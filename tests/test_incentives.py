import json
from fractions import Fraction as F
import http.client
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import threading
import unittest

from ceav_m1.incentives import (
    classify_landscape,
    decompose_branch,
    diagnose_candidate,
    run_incentive_study,
)
from ceav_m1.model import validate_config
from ceav_m1.output import ROOT, restore_exact
from ceav_m1.server import create_server
from ceav_m1.strategies import validate_profile
from tests.test_v2_model import raw_profile, raw_v2


FIXTURE = ROOT / "tests" / "fixtures" / "incentive_decomposition_expected.json"


def decoded(path):
    return restore_exact(json.loads(Path(path).read_text(encoding="utf-8")))


def fake_branch(data, cost=F(1, 20)):
    observations = [
        {
            "observation": tuple(row["observation"]),
            "probability_given_z": F(row["probability_given_z"]),
            "information_by_report": [F(value) for value in row["information_by_report"]],
            "optimal_prediction_score": F(row["optimal_prediction_score"]),
        }
        for row in data["inputs"]["high_observations"]
    ]
    return {
        "judge": "A",
        "z": 0,
        "candidate_action": "H01",
        "low": {"score": F(data["inputs"]["low_score"]), "utility": F(17, 20), "optimal_actions": ["L0"]},
        "high": {"score": F(6, 5), "utility": F(19, 20), "optimal_actions": ["H00"], "observations": observations},
        "delta_utility": F(1, 10),
    }


def fake_config(cost=F(1, 20)):
    return SimpleNamespace(f=F(1, 10), multiplier=F(3, 4), reward_budget=F(6), costs=(cost, cost, cost))


class IncentiveDiagnosticsTests(unittest.TestCase):
    def test_INC_T01_hand_computed_exact_decomposition(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        result = decompose_branch(fake_config(), fake_branch(fixture))
        expected = fixture["expected"]
        self.assertEqual(result["high_action_scores"], {key: F(value) for key, value in expected["high_action_scores"].items()})
        for key in (
            "best_high_score", "dependent_high_score", "information_gain_best",
            "information_gain_dependent", "report_utilization_gap", "net_incentive_best",
            "net_incentive_dependent", "lambda_star_best", "lambda_star_dependent", "lambda_max",
        ):
            self.assertEqual(result[key], F(expected[key]), key)
        self.assertEqual(result["report"]["status"], "SIGNAL_IGNORED_ONLY")

    def test_INC_T02_threshold_budget_and_hierarchical_statuses(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        branch = fake_branch(fixture)
        for observation in branch["high"]["observations"]:
            observation["information_by_report"] = [F(1, 2), F(1, 2)]
            observation["optimal_prediction_score"] = F(1, 2)
        branch["high"].update(score=F(1), utility=F(4, 5), optimal_actions=["H00", "H01", "H10", "H11"])
        branch["delta_utility"] = F(-1, 20)
        result = decompose_branch(fake_config(), branch)
        self.assertIsNone(result["lambda_star_best"])
        self.assertEqual(result["budget"]["best_high"], "UNATTAINABLE_BY_LAMBDA")
        self.assertEqual(result["effort"]["best_high_status"], "NOT_PREFERRED")
        self.assertEqual(result["report"]["status"], "TIE_DEPENDENT_AND_IGNORED")

        branch["high"]["utility"] = branch["low"]["utility"]
        branch["delta_utility"] = F(0)
        tied = decompose_branch(fake_config(F(0)), branch)
        self.assertEqual(tied["lambda_star_best"], F(0))
        self.assertEqual(tied["effort"]["best_high_status"], "TIED")
        self.assertEqual(tied["budget"]["best_high"], "BUDGET_FEASIBLE")

    def test_INC_T03_synthetic_candidate_has_six_peer_fixed_diagnostics(self):
        config = validate_config(raw_v2())
        profile = validate_profile(raw_profile())
        result = diagnose_candidate(config, profile)
        self.assertEqual(len(result["branches"]), 6)
        self.assertEqual({(row["judge"], row["z"]) for row in result["branches"]}, {(judge, z) for judge in "ABC" for z in (0, 1)})
        preferred = [(row["judge"], row["z"]) for row in result["branches"] if row["effort"]["best_high_status"] == "PREFERRED"]
        self.assertEqual(preferred, [("C", 1)])
        for row in result["branches"]:
            index = "ABC".index(row["judge"])
            self.assertEqual(row["net_incentive_best"], config.multiplier * row["information_gain_best"] - config.costs[index])
            self.assertGreaterEqual(row["information_gain_best"], 0)
            self.assertTrue(row["conditional_on_fixed_peer_strategies"])
        by_branch = {(row["judge"], row["z"]): row for row in result["branches"]}
        self.assertEqual(by_branch[("A", 0)]["report"]["status"], "SIGNAL_IGNORED_ONLY")
        self.assertEqual(by_branch[("C", 1)]["report"]["status"], "SIGNAL_DEPENDENT_ONLY")

    def test_INC_T04_landscape_classification_preserves_exhaustive_sets(self):
        from ceav_m1.equilibria import search_pure

        heterogeneous = search_pure(validate_config(raw_v2()))
        landscape = classify_landscape(heterogeneous)
        self.assertEqual(landscape["branch_candidate_count"], 432)
        self.assertTrue(landscape["enumeration_completed"])
        self.assertEqual(landscape["full_equilibrium_count"], heterogeneous["full_equilibrium_count"])
        self.assertTrue(landscape["low_effort_exists"])
        self.assertFalse(landscape["all_high_signal_dependent_exists"])
        for z in ("0", "1"):
            self.assertEqual(landscape["branches"][z]["equilibrium_ids"], heterogeneous["branches"][z]["equilibrium_ids"])
            self.assertEqual(landscape["branches"][z]["class_counts"]["all_low"], 8)

        g1 = json.loads((ROOT / "configs" / "v2" / "symmetric_g1.json").read_text(encoding="utf-8"))
        coexistence = classify_landscape(search_pure(validate_config(g1)))
        self.assertTrue(coexistence["low_effort_exists"])
        self.assertTrue(coexistence["all_high_signal_dependent_exists"])
        self.assertTrue(coexistence["coexistence_low_and_dependent_high"])
        for z in ("0", "1"):
            self.assertEqual(coexistence["branches"][z]["class_counts"]["all_low"], 8)
            self.assertEqual(coexistence["branches"][z]["class_counts"]["all_high_signal_dependent"], 2)

    def test_INC_T05_global_sweep_searches_every_valid_point_and_keeps_invalid(self):
        raw = raw_v2()
        before = json.loads(json.dumps(raw))
        result = run_incentive_study(raw, raw_profile(), {"lambda": ["3/4", "1"]})
        self.assertEqual(raw, before)
        self.assertEqual([row["status"] for row in result["points"]], ["valid", "invalid_budget"])
        valid = result["points"][0]
        self.assertEqual(valid["landscape"]["branch_candidate_count"], 432)
        self.assertTrue(valid["landscape"]["enumeration_completed"])
        self.assertEqual(len(valid["diagnostics"]["branches"]), 6)
        self.assertNotIn("landscape", result["points"][1])

    def test_INC_T06_cli_artifacts_freeze_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "incentives"
            command = [sys.executable, "-B", "-m", "ceav_m1", "incentives",
                       "--config", str(ROOT / "configs" / "v2" / "heterogeneous.json"),
                       "--profile", str(ROOT / "configs" / "all_high.json"), "--out", str(out)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(second.returncode, 0)
            for name in ("incentive_diagnostics.json", "incentive_diagnostics.csv", "incentive_sweep.json",
                         "incentive_sweep.csv", "equilibrium_landscape.json", "summary.json", "report.md", "manifest.json"):
                self.assertTrue((out / name).is_file(), name)
            manifest = decoded(out / "manifest.json")
            self.assertEqual(manifest["status"], "succeeded")
            self.assertEqual(manifest["operation"], "incentives")
            self.assertEqual(manifest["model_version"], "ceav-m1-v2.0")
            self.assertEqual(manifest["incentive_diagnostics"]["feature_version"], "ceav-m1-v2.2-incentive-diagnostics")
            self.assertTrue((out / "inputs" / "incentives" / "freeze_event.json").is_file())


class IncentiveServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.server = create_server(0, Path(self.temporary.name) / "results")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.origin = f"http://127.0.0.1:{self.port}"
        self.token = self.server.lab.token

    def tearDown(self):
        self.server.lab.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)
        self.temporary.cleanup()

    def http(self, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=90)
        headers = {"Origin": self.origin, "X-CEAV-Token": self.token, "Content-Type": "application/json"}
        data = json.dumps(body).encode() if body is not None else None
        connection.request("POST" if data is not None else "GET", path, body=data, headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def test_INC_T07_api_worker_history_and_direct_parity(self):
        request = {"operation": "incentives", "config": raw_v2(), "profile": raw_profile(), "mechanism": "rbts", "axes": {}}
        status, checked = self.http("/api/validate", request)
        self.assertEqual(status, 200)
        self.assertEqual(checked["operation"], "incentives")
        status, job = self.http("/api/runs", request)
        self.assertEqual(status, 202)
        internal = self.server.lab.jobs[job["job_id"]]
        self.assertTrue(internal["done"].wait(90))
        snapshot = self.server.lab.snapshot(internal)
        self.assertEqual(snapshot["status"], "succeeded", snapshot)
        _, artifact = self.http(f"/api/runs/{job['run_id']}/artifacts/incentive_sweep.json")
        direct = run_incentive_study(raw_v2(), raw_profile(), {})
        self.assertEqual(artifact["points"][0]["landscape"]["branches"], direct["points"][0]["landscape"]["branches"])
        self.assertEqual(artifact["points"][0]["landscape"]["full_class_counts"], direct["points"][0]["landscape"]["full_class_counts"])
        _, history = self.http("/api/runs")
        record = next(row for row in history["runs"] if row["run_id"] == job["run_id"])
        self.assertEqual(record["operation"], "incentives")


class IncentiveBrowserEvidenceTests(unittest.TestCase):
    def test_INC_T08_current_source_browser_evidence(self):
        from tests.test_v2_release import latest_browser, manifest_sources_match

        match = latest_browser("INC-B01")
        self.assertIsNotNone(match, "Missing passed current-source INC-B01 evidence")
        _, folder, result, manifest = match
        self.assertTrue(all(step["status"] == "pass" for step in result["steps"]))
        self.assertTrue(manifest_sources_match(manifest, ("ceav_m1/", "web/", "tests/", "configs/", "verification/")))
        self.evidence = {"run_id": folder.name, "steps": len(result["steps"]), "source_matches": True}


if __name__ == "__main__":
    unittest.main()
