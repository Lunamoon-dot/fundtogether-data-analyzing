import json
from fractions import Fraction as F
from pathlib import Path
import tempfile
import sys
import subprocess
import unittest

import ceav_m1
from ceav_m1.model import ValidationError, validate_config
from tests.oracle_v3_3 import all_high_anchor_moments, branch_anchor_by_report


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def v33_raw():
    raw = load("configs/v3/report_sensitive_base_v3_2.json")
    raw["model_version"] = "ceav-m1-v3.3"
    raw["verification_anchor"]["audit_reward_mode"] = "ipw"
    raw["reward_budget"] = "24"
    return raw


def validation_result(raw):
    try:
        return validate_config(raw, "hybrid_anchor")
    except ValidationError as error:
        return error


class V33IPWTests(unittest.TestCase):
    def test_IPW_T01_version_constant_and_schema_round_trip(self):
        self.assertEqual(getattr(ceav_m1, "V33_MODEL_VERSION", None), "ceav-m1-v3.3")
        result = validation_result(v33_raw())
        self.assertEqual(getattr(result, "model_version", None), "ceav-m1-v3.3")
        self.assertEqual(result.raw(), v33_raw())
        self.assertEqual(result.audit_reward_mode, "ipw")
        self.assertEqual(result.audit_probability_by_report, (F(1, 4), F(3, 4)))

    def test_IPW_T02_zero_report_probability_is_rejected(self):
        raw = v33_raw()
        raw["verification_anchor"]["audit_probability_by_report"]["0"] = "0"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "verification_anchor.audit_probability_by_report.0")

    def test_IPW_T03_ipw_cap_is_checked_against_shared_budget(self):
        raw = v33_raw()
        raw["reward_budget"] = "23"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "reward_budget")

    def test_IPW_T04_v3_scalar_audit_input_is_rejected(self):
        raw = v33_raw()
        raw["verification_anchor"]["audit_probability"] = "1/2"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "verification_anchor.audit_probability")

    def test_IPW_T05_distribution_is_64_states_and_normalized(self):
        from ceav_m1.model import enumerate_states
        config = validate_config(v33_raw(), "hybrid_anchor")
        states = enumerate_states(config)
        self.assertEqual(len(states), 64)
        self.assertEqual(sum(state.probability for state in states), F(1))
        self.assertTrue(all(state.audit is None for state in states))

    def test_IPW_T06_expected_anchor_and_audit_cost_match_oracle(self):
        from ceav_m1.evaluate import evaluate
        from ceav_m1.model import enumerate_states
        from ceav_m1.strategies import build_candidate, realized, validate_profile
        raw = v33_raw()
        config = validate_config(raw, "hybrid_anchor")
        candidate = build_candidate(config, validate_profile(load("configs/all_high.json")), rows=enumerate_states(config), mechanism="hybrid_anchor")
        result = evaluate(config, candidate, "hybrid_anchor")
        oracle = all_high_anchor_moments(raw)
        self.assertEqual(result["metrics"]["expected_anchor_reward_total"], sum(oracle["expected_anchor_reward"]))
        self.assertEqual(result["metrics"]["expected_audit_exposure"], oracle["expected_audit_exposure"])
        self.assertEqual(result["metrics"]["expected_audit_cost"], F(raw["verification_anchor"]["cost_per_audit"]) * sum(oracle["expected_audit_exposure"]))
        self.assertEqual(result["metrics"]["anchor_reward_second_moment"], oracle["second_moment"])
        self.assertEqual(result["metrics"]["anchor_reward_variance"], oracle["variance"])
        covariance = result["metrics"]["anchor_reward_covariance"]
        self.assertEqual([covariance[i][i] for i in range(3)], oracle["variance"])
        self.assertEqual(covariance, [list(row) for row in zip(*covariance)])
        q = tuple(F(raw["verification_anchor"]["audit_probability_by_report"][str(report)]) for report in (0, 1))
        cross = [[F(0) for _ in range(3)] for _ in range(3)]
        expected_anchor = [F(0), F(0), F(0)]
        for state in candidate.rows:
            reports, _ = realized(candidate, state)
            for i in range(3):
                if reports[i] == state.verification:
                    expected_anchor[i] += state.probability * F(raw["anchor_weight"])
                for j in range(3):
                    if reports[i] == state.verification and reports[j] == state.verification:
                        cross[i][j] += state.probability * (F(raw["anchor_weight"]) ** 2 / q[reports[i]] if i == j else F(raw["anchor_weight"]) ** 2)
        expected_covariance = [[cross[i][j] - expected_anchor[i] * expected_anchor[j] for j in range(3)] for i in range(3)]
        self.assertEqual(covariance, expected_covariance)

    def test_IPW_T07_expected_anchor_cancels_report_probability(self):
        from ceav_m1.best_response import solve_branch
        from ceav_m1.evaluate import evaluate
        from ceav_m1.model import enumerate_states
        from ceav_m1.strategies import build_candidate, validate_profile
        raw = v33_raw()
        config = validate_config(raw, "hybrid_anchor")
        candidate = build_candidate(config, validate_profile(load("configs/all_high.json")), rows=enumerate_states(config), mechanism="hybrid_anchor")
        direct = evaluate(config, candidate, "hybrid_anchor")
        actual = solve_branch(config, candidate, 0, 0, "hybrid_anchor", direct["conditional"][0][0])
        expected = {key: [value / F(raw["anchor_weight"]) for value in values]
                    for key, values in branch_anchor_by_report(raw, 0, 0).items()}
        for observation in actual["high"]["observations"]:
            self.assertEqual(observation["anchor_by_report"], expected[tuple(observation["observation"])])

    def test_IPW_T08_failure_witness_reconstructs_utility_exactly(self):
        from ceav_m1.equilibria import search_pure
        config = validate_config(v33_raw(), "hybrid_anchor")
        search = search_pure(config, "hybrid_anchor")
        witnesses = [certificate["witness"] for branch in search["branches"].values() for candidate in branch["candidates"]
                     for certificate in candidate["certificates"] if certificate.get("witness")]
        self.assertTrue(witnesses)
        for witness in witnesses[:10]:
            self.assertEqual(witness["reconstruction_error"], F(0))
            self.assertEqual(witness["delta_utility"], witness["delta_peer_reward"] + witness["delta_anchor_reward"] - witness["delta_effort_cost"])

    def test_IPW_T09_study_expands_predeclared_54_points(self):
        try:
            from ceav_m1.ipw import expand_ipw_study, load_ipw_study
        except ImportError as error:
            self.fail(f"V3.3 IPW study module missing: {error}")
        study = load_ipw_study(ROOT / "tests/fixtures/v3_3_ipw_study.json")
        points = expand_ipw_study(study)
        self.assertEqual(len(points), 54)
        self.assertEqual([point["point_id"] for point in points], list(range(54)))
        self.assertTrue(all(point["config"]["model_version"] == "ceav-m1-v3.3" for point in points))

    def test_IPW_T10_study_rejects_non_q_policy_override(self):
        try:
            from ceav_m1.ipw import load_ipw_study, validate_ipw_study
        except ImportError as error:
            self.fail(f"V3.3 IPW study module missing: {error}")
        raw = load_ipw_study(ROOT / "tests/fixtures/v3_3_ipw_study.json")
        raw["policies"][0]["overrides"]["lambda_peer"] = "1/10"
        with self.assertRaises(ValidationError) as caught:
            validate_ipw_study(raw)
        self.assertEqual(caught.exception.field, "study.policies[0].overrides")

    def test_IPW_T11_server_validate_exposes_54_point_grid(self):
        from ceav_m1.ipw import load_ipw_study
        from ceav_m1.server import create_server
        study = load_ipw_study(ROOT / "tests/fixtures/v3_3_ipw_study.json")
        with tempfile.TemporaryDirectory() as folder:
            server = create_server(0, Path(folder) / "api-results")
            try:
                checked = server.lab.validate({"operation": "ipw", "study": study})
                self.assertTrue(checked["valid"])
                self.assertEqual(checked["model_version"], "ceav-m1-v3.3")
                self.assertEqual(checked["grid"]["total_points"], 54)
            finally:
                server.lab.close()
                server.server_close()

    def test_IPW_T12_registry_is_complete_and_discoverable(self):
        from ceav_m1.test_runner import discover
        registry = load("tests/registry_v3_3.json")
        self.assertEqual(set(registry["tests"]), {f"IPW-T{i:02}" for i in range(1, 14)})
        available = {test.id() for test in discover()}
        for record in registry["tests"].values():
            self.assertTrue(record["unittest_ids"])
            self.assertTrue(set(record["unittest_ids"]) <= available)

    def test_IPW_T13_cli_manifest_pins_v33_documents(self):
        from ceav_m1.ipw import load_ipw_study
        study = load_ipw_study(ROOT / "tests/fixtures/v3_3_ipw_study.json")
        study["policies"] = study["policies"][:1]
        study["uncertainty_axes"] = {"pi": ["1/2"], "verification_anchor.quality": ["9/10"], "judges.high_effort_cost_multiplier": ["1"]}
        with tempfile.TemporaryDirectory() as folder:
            study_path = Path(folder) / "study.json"
            out = Path(folder) / "run"
            study_path.write_text(json.dumps(study), encoding="utf-8")
            command = [sys.executable, "-B", "-m", "ceav_m1", "ipw", "--study", str(study_path), "--out", str(out)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["model_version"], "ceav-m1-v3.3")
            self.assertIn("CEAV_M1_V3_3_IPW_SPEC.md", manifest["documents"])
            self.assertTrue((out / "ipw.json").exists())


if __name__ == "__main__":
    unittest.main()
