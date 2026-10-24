"""Independent oracle checks for V4.1 finite equilibrium/quality screening."""

import ast
import importlib
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V41ScreeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = importlib.import_module("verification.v4_1_screening")
        cls.oracle = importlib.import_module("verification.oracle_v4_1_screening")

    def test_independent_fixture_oracle_passes_exact_values(self):
        result = self.oracle.run_checks()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["certificates"]["F41-01"]["delta"], F(0))
        self.assertEqual(result["certificates"]["F41-02"]["delta"], F(2, 25))
        self.assertEqual(result["quality_F41_02_H01"]["accuracy"], F(112, 125))

    def test_covariance_identity_matches_direct_finite_score(self):
        fixture = self.module.f41_02()
        profiles = (("L0", "L1", "H01"), ("H01", "H10", "H00"), ("H11", "L0", "L1"))
        for z in (0, 1):
            for profile in profiles:
                for judge in range(3):
                    self.assertEqual(
                        self.module.covariance_score(fixture, z, profile, judge),
                        self.module.direct_centered_score(fixture, z, profile, judge),
                    )

    def test_f41_exact_informative_and_inverted_quality(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(1), mu=F(0), q=F(0))
        h01 = {"0": ("H01",) * 3, "1": ("H01",) * 3}
        h10 = {"0": ("H10",) * 3, "1": ("H10",) * 3}
        h01_metrics = self.module.evaluate_profile(fixture, policy, h01)["metrics"]
        h10_metrics = self.module.evaluate_profile(fixture, policy, h10)["metrics"]
        self.assertEqual(h01_metrics["accuracy"], F(112, 125))
        self.assertEqual(h10_metrics["accuracy"], F(13, 125))
        self.assertEqual(h01_metrics["false_approval_rate"], F(13, 125))
        self.assertEqual(h10_metrics["false_approval_rate"], F(112, 125))

    def test_frozen_peer_deviation_keeps_peer_actions_unchanged(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(1), mu=F(0), q=F(0))
        candidate = ("H01", "H01", "H01")
        deviation = self.module.best_response(fixture, policy, 1, candidate, 0)
        self.assertEqual(deviation["peer_actions"], ("H01", "H01"))
        self.assertEqual(set(deviation["options"]), set(self.module.ACTIONS))
        self.assertEqual(deviation["candidate_action"], "H01")

    def test_frozen_peer_deviation_uses_candidate_action_in_utility(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(1), mu=F(0), q=F(0))
        model = self.module.ScreeningModel(fixture)
        candidate = ("H01", "H01", "H01")
        deviation = self.module.best_response(fixture, policy, 1, candidate, 0, model=model)
        expected = model.branch_utilities(1, policy, ("H10", "H01", "H01"))[0]
        self.assertEqual(deviation["options"]["H10"], expected)

    def test_effort_cost_is_in_utility(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(0), mu=F(0), q=F(0))
        utility = self.module.ScreeningModel(fixture).branch_utilities(0, policy, ("H00", "L0", "L0"))[0]
        self.assertEqual(utility, -F(1, 20))

    def test_branch_search_keeps_all_low_and_label_inversion(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(1), mu=F(0), q=F(0))
        equilibria = self.module.find_branch_equilibria(fixture, policy, 1)
        profiles = {tuple(record["actions"]) for record in equilibria}
        self.assertIn(("L0", "L0", "L0"), profiles)
        self.assertIn(("L1", "L1", "L1"), profiles)
        self.assertIn(("H01", "H01", "H01"), profiles)
        self.assertIn(("H10", "H10", "H10"), profiles)

    def test_tie_boundary_keeps_all_low_equilibrium(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(mu=F(1), q=F(5, 8))
        for z, action in ((0, "L0"), (1, "L1")):
            profiles = {tuple(record["actions"]) for record in self.module.find_branch_equilibria(fixture, policy, z)}
            self.assertIn((action,) * 3, profiles)

    def test_classification_preserves_asymmetric_effort(self):
        self.assertEqual(
            self.module.classify_actions(("L0", "H01", "H10")),
            "asymmetric_effort",
        )
        self.assertEqual(self.module.classify_actions(("H01",) * 3), "informative_H01")
        self.assertEqual(self.module.classify_actions(("H10",) * 3), "inverted_H10")
        self.assertEqual(self.module.classify_actions(("L0",) * 3), "all_low")

    def test_policy_grid_is_finite_and_audit_only_is_fully_enumerated(self):
        fixture = self.module.f41_02()
        audit = self.module.enumerate_policies(fixture, "audit_only")
        conditional = self.module.enumerate_policies(fixture, "conditional_only")
        hybrid = self.module.enumerate_policies(fixture, "hybrid")
        self.assertEqual(len(audit), 48)
        self.assertEqual(len(conditional), 4)
        self.assertGreater(len(hybrid), 0)
        self.assertTrue(all(policy.lambda_peer == 0 for policy in audit))
        self.assertTrue(all(policy.mu == 0 and policy.q == 0 for policy in conditional))
        self.assertTrue(all(policy.reward_cap <= F(6) for policy in hybrid))

    def test_target_population_weights_are_derived_from_public_signal(self):
        fixture = self.module.v3_het()
        self.assertEqual(fixture.target_weights, (F(2, 5), F(3, 5)))
        self.assertNotEqual(fixture.target_weights, fixture.batch_weights)

    def test_screening_separates_feasibility_existence_robustness_selection(self):
        result = self.module.screen_fixture(self.module.f41_02())
        for mechanism in ("audit_only", "conditional_only", "hybrid"):
            record = result["mechanisms"][mechanism]
            self.assertIn("feasible_policy_count", record)
            self.assertIn("pure_equilibrium_policy_count", record)
            self.assertIn("robust_policy_count", record)
            self.assertEqual(record["equilibrium_selection"], "not_modeled")
        self.assertIn("worst_equilibrium_metrics", result["mechanisms"]["audit_only"]["policies"][0])
        comparison = self.module.compare_robust_frontiers(result)
        self.assertFalse(comparison["hybrid_has_incremental_advantage"])

    def test_target_cash_uses_target_weights_separately_from_batch_average(self):
        fixture = self.module.v3_het()
        policy = self.module.Policy(lambda_peer=F(1))
        evaluated = self.module.evaluate_profile(fixture, policy, {"0": ("L0",) * 3, "1": ("H01",) * 3})
        conditional = evaluated["conditional"]
        expected_target = sum(fixture.target_weights[z] * conditional[z]["cash_cost"] for z in (0, 1))
        expected_batch = sum(fixture.batch_weights[z] * conditional[z]["cash_cost"] for z in (0, 1))
        self.assertEqual(evaluated["metrics"]["cash_review_cost"], expected_target)
        self.assertEqual(evaluated["metrics"]["cash_review_cost_batch_average"], expected_batch)
        self.assertNotEqual(expected_target, expected_batch)

    def test_full_screening_retains_asymmetric_effort_equilibria(self):
        fixture = self.module.f41_02()
        policy = self.module.Policy(lambda_peer=F(1, 4), mu=F(1, 4), q=F(5, 8))
        result = self.module.screen_policy(fixture, policy)
        self.assertTrue(any(record["classification"] == "asymmetric_effort" for record in result["equilibria"]))

    def test_failure_witnesses_keep_quality_metrics_and_gates(self):
        result = self.module.screen_fixture(self.module.f41_02())
        policy = result["mechanisms"]["audit_only"]["policies"][0]
        self.assertIn("equilibria", policy)
        self.assertIn("false_approval_rate", policy["worst_equilibrium_metrics"])
        self.assertIn("wrong_payout_value", policy["worst_equilibrium_metrics"])
        self.assertIn("cash_review_cost", policy["worst_equilibrium_metrics"])
        self.assertEqual(policy["gates"], {
            "max_false_approval_rate": F(1, 5),
            "max_false_rejection_rate": F(1, 4),
            "max_wrong_payout_value": F(3, 20),
            "max_cash_review_cost": F(4),
        })

    def test_v3_heterogeneous_fixture_is_screened(self):
        result = self.module.screen_fixture(self.module.v3_het())
        self.assertEqual(result["fixture"], "V3-HET")
        self.assertGreaterEqual(result["mechanisms"]["audit_only"]["policy_count"], 1)
        self.assertGreaterEqual(result["mechanisms"]["hybrid"]["policy_count"], 1)

    def test_artifact_pins_inputs_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "run"
            self.module.write_run(out)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "succeeded")
            self.assertFalse(manifest["preregistered"])
            for item in manifest["inputs"]:
                self.assertEqual(sha256((out / item["snapshot"]).read_bytes()).hexdigest(), item["sha256"])
            with self.assertRaises(FileExistsError):
                self.module.write_run(out)

    def test_no_production_math_imports(self):
        source = (ROOT / "verification/v4_1_screening.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests") for name in imports))


if __name__ == "__main__":
    unittest.main()
