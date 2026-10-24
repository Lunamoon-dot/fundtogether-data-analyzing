import ast
from fractions import Fraction as F
import importlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V51QualityCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = importlib.import_module("verification.oracle_v5_1_quality")

    def test_F51_02_direct_and_binary_have_same_decision_quality(self):
        direct = self.oracle.certificate_f51_02()["direct"]
        binary = self.oracle.certificate_f51_02()["binary_audit_only"]
        self.assertEqual(direct["effort_profile"], (("H", "H"), ("H", "H"), ("H", "H")))
        self.assertEqual(binary["effort_profile"], (("H01", "H01"), ("H01", "H01"), ("H01", "H01")))
        for record in (direct, binary):
            self.assertEqual(record["accuracy"], F(112, 125))
            self.assertEqual(record["false_approval_rate"], F(13, 125))
            self.assertEqual(record["false_rejection_rate"], F(13, 125))
            self.assertEqual(record["wrong_payout_value"], F(13, 250))
            self.assertEqual(record["realized_reward_cap"], F(6))
            self.assertEqual(record["decision_rule"], {0: "majority_X", 1: "majority_X"})
        self.assertEqual(binary["expected_cash_cost"], F(111, 50))
        self.assertEqual(direct["expected_cash_cost"], F(434007, 147250))
        self.assertEqual(direct["audit_exposure"], F(3, 5))
        self.assertEqual(binary["audit_exposure"], F(1, 2))

    def test_F51_02_direct_probability_forecasts_are_exact(self):
        record = self.oracle.certificate_f51_02()["direct"]
        self.assertEqual(record["forecast_p_t"], {
            0: {0: F(11, 62), 1: F(23, 38)},
            1: {0: F(15, 38), 1: F(51, 62)},
        })
        self.assertEqual(record["vote_by_z_x"], {
            0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}
        })

    def test_V3_HET_direct_best_responses_and_quality(self):
        record = self.oracle.certificate_v3_het()["direct"]
        self.assertEqual(record["effort_profile"], (("H", "H"), ("L", "L"), ("L", "L")))
        self.assertEqual(record["decision_rule"], {0: "Z", 1: "Z"})
        self.assertEqual(record["accuracy"], F(7, 10))
        self.assertEqual(record["false_approval_rate"], F(2, 5))
        self.assertEqual(record["false_rejection_rate"], F(1, 5))
        self.assertEqual(record["wrong_payout_value"], F(1, 5))
        self.assertEqual(record["expected_cash_cost"], F(4609871, 1171875))

    def test_V3_HET_budget_threshold_and_cheapest_tie_bound(self):
        result = self.oracle.certificate_v3_het()["budget_bound"]
        self.assertEqual(result["s_threshold_B_z0"], F(155, 98))
        self.assertEqual(result["B_z0_best_effort_at_threshold"], ("L", "H"))
        self.assertEqual(result["cheapest_tie_resolution_cost"], F(14998033, 3675000))
        self.assertGreater(result["cheapest_tie_resolution_cost"], F(4))
        self.assertEqual(result["B_high_at_z0_tie_cost"], F(15145033, 3675000))
        self.assertGreater(result["B_high_at_z0_tie_cost"], F(4))

    def test_oracle_has_no_production_imports(self):
        source = (ROOT / "verification/oracle_v5_1_quality.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests", "verification") for name in imports))


if __name__ == "__main__":
    unittest.main()
