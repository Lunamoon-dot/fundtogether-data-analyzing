import json
from fractions import Fraction as F
import http.client
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from ceav_m1.robustness import (
    ROBUSTNESS_VERSION,
    classify_robustness,
    expand_study,
    forced_all_high_reference,
    gate_equilibrium_summary,
    load_robustness_study,
    pareto_frontier,
    public_signal_reference,
    run_robustness_study,
    summarize_policies,
    validate_robustness_study,
)
from ceav_m1.model import ValidationError, validate_config


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def one_point_study():
    study = load_robustness_study(ROOT / "tests/fixtures/v3_1_robustness_study.json")
    study["policies"] = study["policies"][:1]
    study["uncertainty_axes"] = {
        "pi": ["1/2"],
        "verification_anchor.quality": ["9/10"],
        "judges.high_effort_cost_multiplier": ["1"],
    }
    return study


class RobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load("configs/v3/robustness_base_v3_1.json")
        cls.study = load_robustness_study(ROOT / "tests/fixtures/v3_1_robustness_study.json")
        cls.expected = load("tests/fixtures/v3_1_robustness_expected.json")

    def test_ROB_T01_schema_version_provenance_and_allowlists(self):
        checked = validate_robustness_study(self.study)
        self.assertEqual(checked["analysis_version"], ROBUSTNESS_VERSION)
        self.assertEqual(checked["base_config"], self.base)
        invalid = json.loads(json.dumps(self.study))
        invalid["unknown"] = 1
        with self.assertRaises(ValidationError) as caught:
            validate_robustness_study(invalid)
        self.assertEqual(caught.exception.field, "study.unknown")
        invalid = json.loads(json.dumps(self.study))
        invalid["policies"][0]["overrides"]["reward_budget"] = "7"
        with self.assertRaises(ValidationError) as caught:
            validate_robustness_study(invalid)
        self.assertEqual(caught.exception.field, "study.policies[0].overrides.reward_budget")
        invalid = json.loads(json.dumps(self.study))
        invalid["uncertainty_axes"]["verification_anchor.quality"] = ["1/2"]
        with self.assertRaises(ValidationError) as caught:
            validate_robustness_study(invalid)
        self.assertEqual(caught.exception.field, "study.uncertainty_axes.verification_anchor.quality[0]")

    def test_ROB_T02_cartesian_expansion_and_pseudo_axes(self):
        full = load_robustness_study(ROOT / "configs/v3/robustness_v3_1.json")
        points = expand_study(validate_robustness_study(full))
        self.assertEqual(len(points), 108)
        self.assertEqual(points[0]["point_id"], 0)
        self.assertEqual(points[-1]["point_id"], 107)
        self.assertEqual(points[0]["policy_id"], "v3_r1_baseline")
        self.assertEqual(points[-1]["policy_id"], "hybrid_q60_peer_1_100")
        first = points[0]["config"]
        self.assertEqual(first["pi"], "3/10")
        self.assertEqual(first["verification_anchor"]["sensitivity"], "4/5")
        self.assertEqual(first["verification_anchor"]["specificity"], "4/5")
        self.assertEqual(first["judges"]["B"]["high_effort_cost"], "1/10")
        multiplied = next(point for point in points if point["policy_id"] == "v3_r1_baseline" and point["uncertainty"]["judges.high_effort_cost_multiplier"] == "6/5")
        self.assertEqual(multiplied["config"]["judges"]["A"]["high_effort_cost"], "3/50")
        self.assertEqual(multiplied["config"]["judges"]["B"]["high_effort_cost"], "3/25")
        self.assertEqual(multiplied["config"]["judges"]["C"]["high_effort_cost"], "6/125")

    def test_ROB_T03_real_point_completes_432_search_and_matches_oracle(self):
        result = run_robustness_study(one_point_study())
        self.assertEqual(result["grid"]["total_points"], 1)
        point = result["points"][0]
        self.assertEqual(point["branch_candidate_count"], 432)
        self.assertTrue(point["enumeration_completed"])
        self.assertEqual(point["status"], self.expected["status"])
        self.assertEqual(point["failure_reasons"], self.expected["failure_reasons"])
        for key, value in self.expected["worst"].items():
            self.assertEqual(point["worst"][key], F(value), key)
        self.assertEqual(point["equilibrium_metrics"]["count"], self.expected["equilibrium"]["count"])

    def test_ROB_T04_worst_equilibrium_gates_keep_all_reasons(self):
        summary = {
            "status": "pure_equilibria_evaluated",
            "count": 2,
            "ranges": {
                "accuracy": {"min": F("3/5"), "max": F("9/10")},
                "false_approval_rate": {"min": F("1/10"), "max": F("3/10")},
                "false_rejection_rate": {"min": F("1/10"), "max": F("3/10")},
                "wrong_payout_value": {"min": F("1/20"), "max": F("1/5")},
                "cash_review_cost": {"min": F("3"), "max": F("9/2")},
            },
        }
        reasons, worst = gate_equilibrium_summary(summary, validate_robustness_study(self.study)["gates"])
        self.assertEqual(reasons, ["false_approval_gate", "wrong_payout_gate", "false_rejection_gate", "cash_review_cost_gate"])
        self.assertEqual(worst["accuracy"], F("3/5"))
        self.assertEqual(worst["false_approval_rate"], F("3/10"))
        reasons, worst = gate_equilibrium_summary({"status": "no_pure_equilibrium", "count": 0}, validate_robustness_study(self.study)["gates"])
        self.assertEqual(reasons, ["no_pure_equilibrium"])
        self.assertIsNone(worst)

    def test_ROB_T05_policy_aggregation_and_classification(self):
        policies = [{"policy_id": "p1", "overrides": {}}, {"policy_id": "p2", "overrides": {}}, {"policy_id": "p3", "overrides": {}}]
        safe = {"accuracy": F("4/5"), "false_approval_rate": F("1/10"), "wrong_payout_value": F("1/20"), "false_rejection_rate": F("1/10"), "cash_review_cost": F("2")}
        points = [
            {"point_id": 0, "policy_id": "p1", "status": "pass", "failure_reasons": [], "worst": safe},
            {"point_id": 1, "policy_id": "p1", "status": "pass", "failure_reasons": [], "worst": safe},
            {"point_id": 2, "policy_id": "p2", "status": "pass", "failure_reasons": [], "worst": safe},
            {"point_id": 3, "policy_id": "p3", "status": "fail", "failure_reasons": ["false_approval_gate"], "worst": safe},
            {"point_id": 4, "policy_id": "p3", "status": "pass", "failure_reasons": [], "worst": safe},
        ]
        summaries = summarize_policies(points, policies)
        self.assertEqual([row["robust"] for row in summaries], [True, True, False])
        self.assertEqual(classify_robustness(summaries), "observed_robust_set")
        self.assertEqual(summaries[2]["failure_reason_counts"], {"false_approval_gate": 1})

    def test_ROB_T06_exact_pareto_dominance_and_ties(self):
        def row(identity, values):
            return {"policy_id": identity, "pareto_eligible": True, "worst": dict(zip(("false_approval_rate", "wrong_payout_value", "false_rejection_rate", "cash_review_cost"), map(F, values)))}
        rows = [row("dominant", ("1/10", "1/20", "1/10", "2")), row("dominated", ("1/5", "1/10", "1/5", "3")), row("tie", ("1/10", "1/20", "1/10", "2")), row("tradeoff", ("1/20", "1/20", "1/4", "5/2"))]
        frontier = pareto_frontier(rows)
        self.assertEqual(frontier["policy_ids"], ["dominant", "tie", "tradeoff"])
        self.assertEqual(frontier["dominated_by"]["dominated"], ["dominant", "tie"])

    def test_ROB_T07_references_match_independent_fixture_and_labels(self):
        config = validate_config(self.base, "hybrid_anchor")
        public = public_signal_reference(config)
        forced = forced_all_high_reference(config)
        for key, value in self.expected["public_signal_rule"].items():
            self.assertEqual(public["metrics"][key], F(value), key)
        for key, value in self.expected["forced_all_high"].items():
            self.assertEqual(forced["metrics"][key], F(value), key)
        self.assertEqual(public["status"], "reference_only_not_equal_resources")
        self.assertEqual(forced["status"], "forced_candidate_not_equilibrium_claim")

    def test_ROB_T08_cli_artifacts_freeze_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            study = root / "study.json"
            study.write_text(json.dumps(one_point_study()), encoding="utf-8")
            out = root / "run"
            command = [sys.executable, "-B", "-m", "ceav_m1", "robustness", "--study", str(study), "--out", str(out)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            for name in ("robustness.json", "robustness_points.csv", "policy_summary.csv", "failure_map.json", "pareto_frontier.json", "baseline_comparison.json", "report.md", "manifest.json"):
                self.assertTrue((out / name).is_file(), name)
            manifest = load(Path(out / "manifest.json").relative_to(ROOT)) if out.is_relative_to(ROOT) else json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "succeeded")
            self.assertIn("CEAV_M1_V3_1_ROBUSTNESS_SPEC.md", manifest["documents"])
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(second.returncode, 0)

    def test_ROB_T09_server_validate_and_worker_parity(self):
        from ceav_m1.server import create_server
        with tempfile.TemporaryDirectory() as folder:
            server = create_server(0, Path(folder) / "results")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port, token = server.server_address[1], server.lab.token
                origin = f"http://127.0.0.1:{port}"

                def request(path, body=None):
                    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=90)
                    headers = {"Origin": origin, "X-CEAV-Token": token, "Content-Type": "application/json"}
                    data = json.dumps(body).encode() if body is not None else None
                    connection.request("POST" if data is not None else "GET", path, body=data, headers=headers)
                    response = connection.getresponse()
                    payload = json.loads(response.read())
                    connection.close()
                    return response.status, payload

                payload = {"operation": "robustness", "study": one_point_study()}
                status, checked = request("/api/validate", payload)
                self.assertEqual(status, 200)
                self.assertEqual(checked["grid"]["total_points"], 1)
                status, job = request("/api/runs", payload)
                self.assertEqual(status, 202)
                self.assertTrue(server.lab.jobs[job["job_id"]]["done"].wait(90))
                self.assertEqual(server.lab.snapshot(server.lab.jobs[job["job_id"]])["status"], "succeeded")
                _, artifact = request(f"/api/runs/{job['run_id']}/artifacts/robustness.json")
                self.assertEqual(artifact["grid"]["total_points"], 1)
                self.assertEqual(artifact["points"][0]["branch_candidate_count"], 432)
            finally:
                server.lab.close()
                server.shutdown()
                server.server_close()
                thread.join(5)

    def test_ROB_T10_registry_is_complete_and_discoverable(self):
        from ceav_m1.test_runner import discover
        registry = load("tests/registry_robustness.json")
        self.assertEqual(set(registry["tests"]), {f"ROB-T{i:02}" for i in range(1, 11)})
        available = {test.id() for test in discover()}
        for record in registry["tests"].values():
            self.assertTrue(record["unittest_ids"])
            self.assertTrue(set(record["unittest_ids"]) <= available)


if __name__ == "__main__":
    unittest.main()
