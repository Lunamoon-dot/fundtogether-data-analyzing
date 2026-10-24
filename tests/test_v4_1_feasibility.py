"""Independent checks for the finite V4.1 feasibility certificate."""

import ast
from dataclasses import replace
import importlib
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V41FeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = importlib.import_module("verification.feasibility_v4_1")

    def test_F41_01_has_zero_private_value_for_binary_audit(self):
        fixture = self.module.f41_01()
        self.assertEqual(fixture.anchor_match, (F(43, 50), F(43, 50)))
        self.assertEqual(fixture.high_match, (F(43, 50), F(43, 50)))
        self.assertEqual(fixture.delta, (F(0), F(0)))

    def test_F41_02_has_declared_positive_delta(self):
        fixture = self.module.f41_02()
        self.assertEqual(fixture.anchor_match, (F(33, 50), F(33, 50)))
        self.assertEqual(fixture.high_match, (F(37, 50), F(37, 50)))
        self.assertEqual(fixture.delta, (F(2, 25), F(2, 25)))

    def test_F41_02_entry_boundary_and_strict_deviation(self):
        fixture = self.module.f41_02()
        tie = self.module.analyze(fixture, self.module.Policy(mu=F(1), q=F(5, 8)))
        strict = self.module.analyze(fixture, self.module.Policy(mu=F(1), q=F(3, 4)))
        self.assertEqual(tie["gain_by_judge_z"], [[F(0), F(0)]] * 3)
        self.assertTrue(tie["all_low_persists"])
        self.assertEqual(strict["gain_by_judge_z"], [[F(1, 100), F(1, 100)]] * 3)
        self.assertFalse(strict["all_low_persists"])

    def test_F2_hybrid_and_audit_only_have_same_entry_gain(self):
        fixture = self.module.f41_02()
        audit = self.module.analyze(fixture, self.module.Policy(lambda_peer=F(0), mu=F(1), q=F(3, 4)))
        hybrid = self.module.analyze(fixture, self.module.Policy(lambda_peer=F(1), mu=F(1), q=F(3, 4), budget=F(9)))
        self.assertEqual(audit["gain_by_judge_z"], hybrid["gain_by_judge_z"])
        self.assertTrue(audit["policy_valid"])
        self.assertTrue(hybrid["policy_valid"])

    def test_budget_and_population_cost_are_reported_separately(self):
        fixture = self.module.f41_02()
        audit = self.module.analyze(fixture, self.module.Policy(lambda_peer=F(0), mu=F(1), q=F(5, 8)))
        hybrid = self.module.analyze(fixture, self.module.Policy(lambda_peer=F(1), mu=F(1), q=F(5, 8)))
        self.assertTrue(audit["policy_valid"])
        self.assertFalse(hybrid["policy_valid"])
        self.assertEqual(audit["cost_floor_target_population"], F(99, 80))
        self.assertEqual(hybrid["cost_floor_target_population"], F(339, 80))
        self.assertEqual(audit["cost_floor_batch_average"], audit["cost_floor_target_population"])

    def test_imbalanced_target_and_batch_weights_remain_distinct(self):
        fixture = replace(self.module.f41_02(),
                          anchor_match=(F(33, 50), F(1, 2)),
                          target_weights=(F(3, 4), F(1, 4)),
                          batch_weights=(F(1, 4), F(3, 4)))
        result = self.module.analyze(fixture, self.module.Policy(lambda_peer=F(0), mu=F(1), q=F(1)))
        self.assertEqual(result["cost_floor_target_population"], F(93, 50))
        self.assertEqual(result["cost_floor_batch_average"], F(81, 50))
        self.assertEqual(result["cost_floor_actual_batch"], F(162, 25))

    def test_f41_01_all_low_persists_even_with_maximal_audit_weight(self):
        result = self.module.analyze(self.module.f41_01(), self.module.Policy(mu=F(1), q=F(1)))
        self.assertTrue(result["all_low_persists"])
        self.assertEqual(result["strict_entry_exists"], False)
        self.assertEqual(result["quality_status"], "not_evaluated")

    def test_certificate_is_scoped_and_pins_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "run"
            self.module.write_run(out)
            certificate = json.loads((out / "certificate.json").read_text(encoding="utf-8"))
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(certificate["scope"], "finite_fixture_feasibility_only")
            self.assertFalse(certificate["policy_search"])
            self.assertEqual(certificate["finding"], "finite_feasibility_certificate_only")
            for item in manifest["inputs"]:
                self.assertEqual(sha256((out / item["snapshot"]).read_bytes()).hexdigest(), item["sha256"])
            with self.assertRaises(FileExistsError):
                self.module.write_run(out)

    def test_no_production_math_imports(self):
        source = (ROOT / "verification/feasibility_v4_1.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests") for name in imports))

    def test_optimized_mode_rejects_mutated_fixture_certificate(self):
        command = (
            "import verification.feasibility_v4_1 as oracle; "
            "from fractions import Fraction; "
            "oracle._match_values=lambda *args: (Fraction(0), Fraction(0)); "
            "oracle.run_certificate()"
        )
        process = subprocess.run([sys.executable, "-O", "-c", command], cwd=ROOT,
                                 capture_output=True, text=True)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("AssertionError", process.stderr)


if __name__ == "__main__":
    unittest.main()
