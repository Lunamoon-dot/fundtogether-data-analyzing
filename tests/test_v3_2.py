import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ceav_m1 import V32_MODEL_VERSION
from ceav_m1.best_response import solve_branch
from ceav_m1.equilibria import search_pure
from ceav_m1.evaluate import analyze, evaluate
from ceav_m1.model import ValidationError, enumerate_states, validate_config
from ceav_m1.strategies import build_candidate, validate_profile
from tests.oracle_v3_2 import all_high_metrics, branch_anchor_by_report


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class V32ReportSensitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load("configs/v3/report_sensitive_base_v3_2.json")
        cls.profile_raw = load("configs/all_high.json")

    def test_V32_T01_schema_accepts_q0_q1(self):
        config = validate_config(self.raw, "hybrid_anchor")
        self.assertEqual(config.model_version, V32_MODEL_VERSION)
        self.assertEqual(config.raw(), self.raw)
        self.assertEqual(config.audit_probability_by_report, (F("1/4"), F("3/4")))

    def test_V32_T02_scalar_audit_probability_is_rejected(self):
        invalid = json.loads(json.dumps(self.raw))
        invalid["verification_anchor"]["audit_probability"] = "1/2"
        with self.assertRaises(ValidationError) as caught:
            validate_config(invalid, "hybrid_anchor")
        self.assertEqual(caught.exception.field, "verification_anchor.audit_probability")

    def test_V32_T03_distribution_is_64_states_and_normalized(self):
        config = validate_config(self.raw, "hybrid_anchor")
        rows = enumerate_states(config)
        self.assertEqual(len(rows), 64)
        self.assertEqual(sum(row.probability for row in rows), 1)
        self.assertTrue(all(row.audit is None for row in rows))
        self.assertTrue(all(row.verification in (0, 1) for row in rows))

    def test_V32_T04_candidate_metrics_match_independent_oracle(self):
        config = validate_config(self.raw, "hybrid_anchor")
        result = analyze(config, validate_profile(self.profile_raw), "hybrid_anchor")
        expected = all_high_metrics(self.raw)
        for key, value in expected.items():
            self.assertEqual(result["metrics"][key], value, key)

    def test_V32_T05_audit_cost_sums_three_report_exposures(self):
        config = validate_config(self.raw, "hybrid_anchor")
        result = evaluate(config, build_candidate(config, validate_profile(self.profile_raw), mechanism="hybrid_anchor"), "hybrid_anchor")
        self.assertEqual(result["metrics"]["expected_audit_cost"], all_high_metrics(self.raw)["expected_audit_cost"])

    def test_V32_T06_best_response_uses_report_sensitive_anchor(self):
        config = validate_config(self.raw, "hybrid_anchor")
        profile = validate_profile(self.profile_raw)
        candidate = build_candidate(config, profile, mechanism="hybrid_anchor")
        direct = evaluate(config, candidate, "hybrid_anchor")
        actual = solve_branch(config, candidate, 0, 0, "hybrid_anchor", direct["conditional"][0][0])
        expected = branch_anchor_by_report(self.raw, self.profile_raw, 0, 0, "H")
        for observation in actual["high"]["observations"]:
            self.assertEqual(observation["anchor_by_report"], expected[tuple(observation["observation"])])

    def test_V32_T07_exhaustive_search_keeps_432_branch_candidates(self):
        config = validate_config(self.raw, "hybrid_anchor")
        result = search_pure(config, "hybrid_anchor")
        self.assertTrue(result["enumeration_completed"])
        self.assertEqual(result["branch_candidate_count"], 432)

    def test_V32_T08_study_emits_failure_witnesses(self):
        from ceav_m1.report_sensitive import load_report_sensitive_study, run_report_sensitive_study
        study = load_report_sensitive_study(ROOT / "tests/fixtures/v3_2_report_sensitive_study.json")
        result = run_report_sensitive_study(study)
        self.assertEqual(result["grid"]["total_points"], 3)
        self.assertTrue(all("failure_witnesses" in point for point in result["points"]))

    def test_V32_T09_cli_artifacts_pin_v32_spec(self):
        with tempfile.TemporaryDirectory() as folder:
            study = ROOT / "tests/fixtures/v3_2_report_sensitive_study.json"
            out = Path(folder) / "run"
            command = [sys.executable, "-B", "-m", "ceav_m1", "report-sensitive", "--study", str(study), "--out", str(out)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["model_version"], V32_MODEL_VERSION)
            self.assertIn("CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md", manifest["documents"])
            from ceav_m1.report_sensitive import load_report_sensitive_study
            from ceav_m1.server import create_server
            server = create_server(0, Path(folder) / "api-results")
            try:
                checked = server.lab.validate({"operation": "report_sensitive", "study": load_report_sensitive_study(ROOT / "tests/fixtures/v3_2_report_sensitive_study.json")})
                self.assertEqual(checked["model_version"], V32_MODEL_VERSION)
                self.assertEqual(checked["grid"]["total_points"], 3)
            finally:
                server.lab.close()
                server.server_close()

    def test_V32_T10_registry_is_complete_and_discoverable(self):
        from ceav_m1.test_runner import discover
        registry = load("tests/registry_v3_2.json")
        self.assertEqual(set(registry["tests"]), {f"V32-T{i:02}" for i in range(1, 11)})
        available = {test.id() for test in discover()}
        for record in registry["tests"].values():
            self.assertTrue(record["unittest_ids"])
            self.assertTrue(set(record["unittest_ids"]) <= available)


if __name__ == "__main__":
    unittest.main()
