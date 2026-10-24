"""Fixed-pair V3-HET audit-cost sensitivity checks."""

import ast
import importlib
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V41AuditCostSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = importlib.import_module("verification.v4_1_audit_cost_sensitivity")

    def test_exact_pair_and_crossover(self):
        result = self.module.run_study()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["baseline_cash"]["audit_only"], F(381, 160))
        self.assertEqual(result["baseline_cash"]["hybrid"], F(14551, 6000))
        self.assertEqual(result["kappa_star"], F(527, 1500))
        self.assertEqual(result["audit_gate_kappa_max"], F(259, 100))
        self.assertEqual(result["hybrid_gate_kappa_max"], F(9449, 3000))

    def test_crossover_and_gate_intervals_are_classified_exactly(self):
        result = self.module.run_study()
        points = {point["kappa"]: point for point in result["points"]}
        self.assertEqual(points[F(0)]["cheaper"], "audit_only")
        self.assertEqual(points[result["kappa_star"]]["cheaper"], "tie")
        self.assertEqual(points[F(3, 8)]["cheaper"], "hybrid")
        self.assertTrue(points[F(3, 8)]["hybrid"]["robust_under_declared_gates"])
        self.assertTrue(points[result["hybrid_gate_kappa_max"]]["hybrid"]["cash_gate_pass"])
        self.assertFalse(points[result["hybrid_gate_kappa_max"]]["audit_only"]["cash_gate_pass"])

    def test_quality_tradeoff_is_preserved(self):
        result = self.module.run_study()
        audit = result["points"][0]["audit_only"]["quality"]
        hybrid = result["points"][0]["hybrid"]["quality"]
        self.assertLess(hybrid["accuracy"], audit["accuracy"])
        self.assertGreater(hybrid["false_rejection_rate"], audit["false_rejection_rate"])
        self.assertTrue(result["points"][3]["hybrid"]["quality_gate_pass"])

    def test_run_pins_inputs_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "run"
            self.module.write_run(out)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "succeeded")
            for item in manifest["inputs"]:
                self.assertEqual(sha256((out / item["snapshot"]).read_bytes()).hexdigest(), item["sha256"])
            with self.assertRaises(FileExistsError):
                self.module.write_run(out)

    def test_no_production_math_imports(self):
        source = (ROOT / "verification/v4_1_audit_cost_sensitivity.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests") for name in imports))


if __name__ == "__main__":
    unittest.main()
