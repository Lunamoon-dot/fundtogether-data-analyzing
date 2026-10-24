import ast
from fractions import Fraction as F
import importlib
from pathlib import Path
import unittest
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


class V5OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = importlib.import_module("verification.oracle_v5")

    def test_F51_exact_delta_values(self):
        f01 = self.oracle.fixture_metrics("F51-01")
        f02 = self.oracle.fixture_metrics("F51-02")
        self.assertEqual(f01["delta_y"], (F(3249, 708400),) * 2)
        self.assertEqual(f01["delta_t"], (F(3249, 1106875),) * 2)
        self.assertEqual(f02["delta_y"], (F(3969, 58900),) * 2)
        self.assertEqual(f02["delta_t"], (F(15876, 368125),) * 2)

    def test_noise_attenuation_is_exact(self):
        for name in ("F51-01", "F51-02", "V3-HET"):
            metrics = self.oracle.fixture_metrics(name)
            d = metrics["audit_sensitivity"] + metrics["audit_specificity"] - 1
            for y_delta, t_delta in zip(metrics["delta_y_by_judge"], metrics["delta_t_by_judge"]):
                self.assertEqual(t_delta, tuple(d * d * value for value in y_delta))

    def test_strict_propriety_and_zero_coefficient_boundary(self):
        p_true = F(3, 5)
        values = {p: self.oracle.proper_score_expectation(p, p_true) for p in (F(0), F(3, 5), F(1))}
        self.assertGreater(values[F(3, 5)], values[F(0)])
        self.assertGreater(values[F(3, 5)], values[F(1)])
        self.assertEqual(self.oracle.proper_score_expectation(F(0), p_true), F(2, 5))

    def test_v3_het_branch_certificates(self):
        metrics = self.oracle.fixture_metrics("V3-HET")
        self.assertEqual(metrics["delta_t_by_judge"][0], (F(147, 3125), F(392, 5625)))
        self.assertEqual(metrics["delta_t_by_judge"][1], (F(49, 775), F(12544, 202275)))
        self.assertEqual(metrics["delta_t_by_judge"][2], (F(9, 775), F(7, 450)))

    def test_payment_bounds_and_caps(self):
        self.assertEqual(self.oracle.payment_bounds("incremental", F(0), F(1)),
                         {"minimum": F(0), "maximum": F(2), "cap_total": F(6)})
        self.assertEqual(self.oracle.payment_bounds("direct", F(1, 10), F(19, 10)),
                         {"minimum": F(1, 10), "maximum": F(2), "cap_total": F(6)})

    def test_no_production_math_imports(self):
        source = (ROOT / "verification/oracle_v5.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests") for name in imports))


class V5FeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = importlib.import_module("verification.feasibility_v5")

    def test_shifted_incremental_is_infeasible_on_both_public_fixtures(self):
        for name in ("F51-01", "F51-02"):
            result = self.module.analyze(name, self.module.Policy("incremental", mu=F(1), q=F(1)))
            self.assertFalse(result["strict_entry_possible_at_cap"])
            self.assertTrue(result["all_low_persists_at_policy"])

    def test_direct_brier_has_distinct_cap_and_f51_02_candidate(self):
        f01 = self.module.analyze("F51-01", self.module.Policy("direct", mu=F(2), q=F(1)))
        self.assertFalse(f01["strict_entry_possible_at_cap"])
        result = self.module.analyze("F51-02", self.module.Policy("direct", mu=F(2), q=F(3, 5)))
        self.assertEqual(result["mu_max"], F(2))
        self.assertEqual(result["reserve_cap_total"], F(6))
        self.assertTrue(result["strict_entry_exists"])
        self.assertLessEqual(result["cash_floor_target_population"], F(4))

    def test_v3_het_keeps_judge_branch_heterogeneity(self):
        result = self.module.analyze("V3-HET", self.module.Policy("incremental", f=F(1, 10), mu=F(19, 20), q=F(1)))
        self.assertEqual(result["max_gain_at_mu_max_by_judge_z"][0],
                         (F(-83, 15625), F(1823, 112500)))
        self.assertEqual(result["max_gain_at_mu_max_by_judge_z"][1],
                         (F(-619, 15500), F(-83107, 2022750)))
        self.assertEqual(result["max_gain_at_mu_max_by_judge_z"][2],
                         (F(-449, 15500), F(-227, 9000)))

    def test_target_and_batch_cash_weights_are_distinct(self):
        result = self.module.analyze("V3-HET", self.module.Policy("direct", f=F(1, 10), mu=F(19, 10), q=F(1)))
        self.assertNotEqual(result["cash_floor_target_population"], result["cash_floor_batch_average"])
        self.assertEqual(result["cash_floor_actual_batch"], F(4) * result["cash_floor_batch_average"])

    def test_run_certificate_is_bounded(self):
        result = self.module.run_certificate()
        self.assertEqual(result["status"], "passed")
        self.assertIn("direct_brier_requires_separate_screening", result["finding"])
        self.assertEqual(result["f51_01_incremental"]["quality_status"], "not_evaluated")

    def test_mutation_probes_reject_formula_changes(self):
        process = subprocess.run([sys.executable, "verification/mutation_probes_v5.py"], cwd=ROOT,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)


if __name__ == "__main__":
    unittest.main()
