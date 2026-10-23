import json
from fractions import Fraction as F
import http.client
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from ceav_m1 import V3_MODEL_VERSION
from ceav_m1.best_response import solve_branch
from ceav_m1.equilibria import search_pure, summarize_equilibrium_metrics
from ceav_m1.evaluate import analyze, evaluate
from ceav_m1.model import HighObservation, LowObservation, ValidationError, enumerate_states, observe, validate_config
from ceav_m1.strategies import build_candidate, validate_profile


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class V3EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load("configs/v3/heterogeneous_anchor.json")
        cls.profile_raw = load("configs/all_high.json")
        cls.expected = load("tests/fixtures/v3_anchor_expected.json")
        cls.closeout_expected = load("tests/fixtures/v3_closeout_expected.json")

    def test_V3_T01_schema_and_mechanism_dispatch(self):
        config = validate_config(self.raw, "hybrid_anchor")
        self.assertEqual(config.model_version, V3_MODEL_VERSION)
        self.assertEqual(config.raw(), self.raw)
        for mechanism in ("fixed", "rbts"):
            with self.assertRaises(ValidationError):
                validate_config(self.raw, mechanism)
        invalid = json.loads(json.dumps(self.raw))
        invalid["lambda"] = invalid.pop("lambda_peer")
        with self.assertRaises(ValidationError) as caught:
            validate_config(invalid, "hybrid_anchor")
        self.assertEqual(caught.exception.field, "lambda")
        invalid = json.loads(json.dumps(self.raw))
        invalid["verification_anchor"]["sensitivity"] = "1/2"
        with self.assertRaises(ValidationError) as caught:
            validate_config(invalid, "hybrid_anchor")
        self.assertEqual(caught.exception.field, "verification_anchor.sensitivity")
        invalid = json.loads(json.dumps(self.raw))
        invalid["verification_anchor"]["cost_per_audit"] = "-1/10"
        with self.assertRaises(ValidationError) as caught:
            validate_config(invalid, "hybrid_anchor")
        self.assertEqual(caught.exception.field, "verification_anchor.cost_per_audit")

    def test_V3_T02_exact_distribution_and_support(self):
        config = validate_config(self.raw, "hybrid_anchor")
        rows = enumerate_states(config)
        self.assertEqual(len(rows), 128)
        self.assertEqual(sum(row.probability for row in rows), 1)
        self.assertEqual(sum(row.probability > 0 for row in rows), self.expected["support_size"])
        for state_id, mass in self.expected["selected_state_masses"].items():
            self.assertEqual(rows[int(state_id)].probability, F(mass))

    def test_V3_T03_observation_never_contains_audit_or_verification(self):
        config = validate_config(self.raw, "hybrid_anchor")
        state = enumerate_states(config)[127]
        low, high = observe(state, 0, "L"), observe(state, 0, "H")
        self.assertEqual(low, LowObservation(state.z))
        self.assertEqual(high, HighObservation(state.z, state.signals[0]))
        self.assertFalse(hasattr(low, "audit"))
        self.assertFalse(hasattr(high, "verification"))

    def test_V3_T04_candidate_accounting_matches_independent_fixture(self):
        config = validate_config(self.raw, "hybrid_anchor")
        profile = validate_profile(self.profile_raw)
        result = analyze(config, profile, "hybrid_anchor")
        for key, value in self.expected["candidate_metrics"].items():
            self.assertEqual(result["metrics"][key], F(value), key)
        for actual, expected in zip(result["judges"], self.expected["candidate_totals"]):
            for key, value in expected.items():
                self.assertEqual(actual[key], F(value), key)
        self.assertEqual(result["state_support_size"], 128)
        audit_raw = load("configs/v3/anchor_dominant_q50.json")
        audit_raw["verification_anchor"]["cost_per_audit"] = self.closeout_expected["audit_cost_case"]["cost_per_audit"]
        audit_profile = validate_profile(self.closeout_expected["equilibrium_metrics"]["best_accuracy"]["profile"])
        audit_result = analyze(validate_config(audit_raw, "hybrid_anchor"), audit_profile, "hybrid_anchor")
        self.assertEqual(audit_result["metrics"]["expected_audit_cost"], F(self.closeout_expected["audit_cost_case"]["expected_audit_cost"]))
        self.assertEqual(audit_result["metrics"]["cash_review_cost"], F(self.closeout_expected["audit_cost_case"]["cash_review_cost"]))

    def test_V3_T05_best_responses_match_independent_fixture(self):
        config = validate_config(self.raw, "hybrid_anchor")
        profile = validate_profile(self.profile_raw)
        candidate = build_candidate(config, profile, mechanism="hybrid_anchor")
        direct = evaluate(config, candidate, "hybrid_anchor")
        for judge, label in enumerate("ABC"):
            for z in (0, 1):
                expected = self.expected["best_responses"][f"{label}-z{z}"]
                actual = solve_branch(config, candidate, judge, z, "hybrid_anchor", direct["conditional"][judge][z])
                self.assertEqual(actual["candidate_action"], expected["candidate_action"])
                self.assertEqual(actual["best_utility"], F(expected["best_utility"]))
                self.assertEqual(actual["regret"], F(expected["regret"]))
                self.assertEqual(actual["optimal_actions"], expected["optimal_actions"])

    def test_V3_T06_zero_anchor_reduces_to_v2(self):
        v2_raw = load("configs/v2/heterogeneous.json")
        v3_raw = json.loads(json.dumps(self.raw))
        v3_raw["f"] = v2_raw["f"]
        v3_raw["lambda_peer"] = v2_raw["lambda"]
        v3_raw["anchor_weight"] = "0"
        v3_raw["reward_budget"] = v2_raw["reward_budget"]
        v2 = validate_config(v2_raw, "rbts")
        v3 = validate_config(v3_raw, "hybrid_anchor")
        v2_rows, v3_rows = enumerate_states(v2), enumerate_states(v3)
        marginal = {}
        for row in v3_rows:
            key = (row.y, row.z, *row.signals)
            marginal[key] = marginal.get(key, F(0)) + row.probability
        self.assertEqual([row.probability for row in v2_rows], [marginal[(row.y, row.z, *row.signals)] for row in v2_rows])
        profile = validate_profile(self.profile_raw)
        old, new = analyze(v2, profile, "rbts"), analyze(v3, profile, "hybrid_anchor")
        for key in ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_probability", "expected_reward_total", "expected_effort_cost"):
            self.assertEqual(old["metrics"][key], new["metrics"][key], key)
        self.assertEqual(old["predictions"], new["predictions"])
        self.assertEqual([item["regret"] for item in old["best_responses"]], [item["regret"] for item in new["best_responses"]])

    def test_V3_T07_exhaustive_search_matches_independent_fixture(self):
        config = validate_config(self.raw, "hybrid_anchor")
        result = search_pure(config, "hybrid_anchor")
        self.assertTrue(result["enumeration_completed"])
        self.assertEqual(result["branch_candidate_count"], 432)
        for z in (0, 1):
            self.assertEqual(result["branches"][str(z)]["equilibrium_ids"], self.expected["branch_equilibria"][str(z)])

    def test_V3_T08_worst_case_budget_does_not_multiply_by_q(self):
        config = validate_config(self.raw, "hybrid_anchor")
        expected = 3 * config.f + 6 * config.multiplier + 3 * config.anchor_weight
        self.assertEqual(expected, F("57/10"))
        invalid = json.loads(json.dumps(self.raw))
        invalid["reward_budget"] = "569/100"
        with self.assertRaises(ValidationError) as caught:
            validate_config(invalid, "hybrid_anchor")
        self.assertEqual(caught.exception.field, "reward_budget")

    def test_V3_T09_cli_artifacts_freeze_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "run"
            command = [sys.executable, "-B", "-m", "ceav_m1", "analyze", "--config",
                       str(ROOT / "configs/v3/heterogeneous_anchor.json"), "--profile",
                       str(ROOT / "configs/all_high.json"), "--mechanism", "hybrid_anchor", "--out", str(out)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "succeeded")
            self.assertEqual(manifest["model_version"], V3_MODEL_VERSION)
            self.assertEqual(manifest["mechanism"], "hybrid_anchor")
            self.assertEqual(set(manifest["documents"]), {
                "CEAV_M1_V3_ANCHOR_SPEC.md", "ENGINE_DESIGN_V3_ANCHOR.md", "VERIFICATION_PLAN_V3_ANCHOR.md",
                "CEAV_M1_V3_1_ROBUSTNESS_SPEC.md", "ENGINE_DESIGN_V3_1_ROBUSTNESS.md", "VERIFICATION_PLAN_V3_1_ROBUSTNESS.md",
            })
            self.assertTrue((out / "inputs/freeze_event.json").is_file())
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)

    def test_V3_T10_server_status_validate_and_worker_parity(self):
        from ceav_m1.server import create_server
        with tempfile.TemporaryDirectory() as folder:
            server = create_server(0, Path(folder) / "results")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port, token = server.server_address[1], server.lab.token
                origin = f"http://127.0.0.1:{port}"

                def request(path, body=None):
                    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
                    headers = {"Origin": origin, "X-CEAV-Token": token, "Content-Type": "application/json"}
                    data = json.dumps(body).encode() if body is not None else None
                    connection.request("POST" if data is not None else "GET", path, body=data, headers=headers)
                    response = connection.getresponse()
                    payload = json.loads(response.read())
                    connection.close()
                    return response.status, payload

                status, metadata = request("/api/status")
                self.assertEqual(status, 200)
                self.assertEqual(metadata["default_model_version"], V3_MODEL_VERSION)
                self.assertEqual(metadata["v3_presets"]["heterogeneous_anchor"], self.raw)
                experimental = metadata["v3_presets"]["anchor_dominant_q50"]
                self.assertEqual(experimental["verification_anchor"]["audit_probability"], "1/2")
                self.assertEqual(experimental["lambda_peer"], "0")
                self.assertEqual(experimental["anchor_weight"], "19/10")
                payload = {"operation": "analyze", "config": self.raw, "profile": self.profile_raw, "mechanism": "hybrid_anchor"}
                status, checked = request("/api/validate", payload)
                self.assertEqual(status, 200)
                self.assertEqual(checked["config"], self.raw)
                status, job = request("/api/runs", payload)
                self.assertEqual(status, 202)
                self.assertTrue(server.lab.jobs[job["job_id"]]["done"].wait(30))
                self.assertEqual(server.lab.snapshot(server.lab.jobs[job["job_id"]])["status"], "succeeded")
                _, summary = request(f"/api/runs/{job['run_id']}/artifacts/summary.json")
                self.assertEqual(summary["metrics"]["expected_anchor_reward_total"]["exact"], self.expected["candidate_metrics"]["expected_anchor_reward_total"])
            finally:
                server.lab.close()
                server.shutdown()
                server.server_close()
                thread.join(5)

    def test_V3_T11_sweep_preserves_valid_and_invalid_points(self):
        from ceav_m1.__main__ import execute
        with tempfile.TemporaryDirectory() as folder:
            experimental = load("configs/v3/anchor_dominant_q50.json")
            result = execute("sweep", experimental, self.profile_raw, "hybrid_anchor", Path(folder) / "sweep",
                             sweep={"anchor_weight": ["19/10", "2"]})
            self.assertEqual(result["scope"], "candidate_analysis_plus_exhaustive_pure_equilibrium_landscape")
            self.assertEqual([row["status"] for row in result["rows"]], ["valid", "invalid_budget"])
            self.assertEqual(result["rows"][0]["anchor_weight"], F("19/10"))
            self.assertEqual(json.loads(result["rows"][0]["config_json"])["anchor_weight"], "19/10")
            landscape = result["rows"][0]["landscape"]
            self.assertTrue(landscape["enumeration_completed"])
            self.assertEqual(landscape["branch_candidate_count"], 432)
            self.assertEqual(landscape["full_equilibrium_count"], 1)
            metrics = landscape["equilibrium_metrics"]
            self.assertEqual(metrics["status"], "pure_equilibria_evaluated")
            self.assertEqual(metrics["count"], 1)
            for key, expected in self.closeout_expected["equilibrium_metrics"]["ranges"].items():
                self.assertEqual(metrics["ranges"][key]["min"], F(expected["min"]), key)
                self.assertEqual(metrics["ranges"][key]["max"], F(expected["max"]), key)
            self.assertEqual(metrics["best_accuracy"]["profile"], self.closeout_expected["equilibrium_metrics"]["best_accuracy"]["profile"])
            direct = summarize_equilibrium_metrics(validate_config(experimental, "hybrid_anchor"), search_pure(validate_config(experimental, "hybrid_anchor"), "hybrid_anchor"), "hybrid_anchor")
            self.assertEqual(metrics, direct)
            self.assertNotIn("landscape", result["rows"][1])

    def test_V3_T12_registry_is_complete_and_discoverable(self):
        from ceav_m1.test_runner import discover
        registry = load("tests/registry_v3.json")
        self.assertEqual(set(registry["tests"]), {f"V3-T{i:02}" for i in range(1, 13)})
        available = {test.id() for test in discover()}
        for record in registry["tests"].values():
            self.assertTrue(record["unittest_ids"])
            self.assertTrue(set(record["unittest_ids"]) <= available)


if __name__ == "__main__":
    unittest.main()
