"""Analytically derived checks for the small V4 research oracle, not an engine suite."""

import ast
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


class V4ResearchOracleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "verification/oracle_v4.py").exists(), "V4 reference oracle is not implemented")
        self.oracle = importlib.import_module("verification.oracle_v4")

    def test_V4_O01_finite_score_uses_only_other_tasks_in_same_stratum(self):
        public = (0, 0, 1, 1, 1)
        reports = ((0, 1, 0, 1, 1), (0, 0, 0, 0, 1), (1, 1, 1, 0, 1))
        self.assertEqual([self.oracle.realized_score(public, reports, 0, t) for t in (2, 3, 4)],
                         [F(0), F(-3, 4), F(3, 4)])
        with self.assertRaisesRegex(ValueError, "insufficient_stratum_support"):
            self.oracle.realized_score((0, 1), ((0, 1),) * 3, 0, 0)

    def test_V4_O02_all_low_centered_score_and_high_cost(self):
        for z in (0, 1):
            low = ("L1",) * 3 if z else ("L0",) * 3
            for action in self.oracle.ACTIONS:
                profile = (action, *low[1:])
                result = self.oracle.branch(z, profile)
                self.assertEqual(result["scores"][0], F(0))
                self.assertEqual(result["utilities"][0], F(1) - (F(1, 20) if action.startswith("H") else 0))

    def test_V4_O03_F01_all_six_deviations_against_informative_peers(self):
        expected = dict(zip(self.oracle.ACTIONS, (F(0), F(0), F(0), F(189, 1250), F(-189, 1250), F(0))))
        for z in (0, 1):
            for action, score in expected.items():
                self.assertEqual(self.oracle.branch(z, (action, "H01", "H01"))["scores"][0], score)
            high = self.oracle.branch(z, ("H01",) * 3)
            self.assertEqual(high["utilities"], [F(2753, 2500)] * 3)
            self.assertEqual(high["accuracy"], F(112, 125))
            self.assertEqual(high["false_approval_rate"], F(13, 125))
            self.assertEqual(high["false_rejection_rate"], F(13, 125))

    def test_V4_O04_label_inversion_preserves_reward_and_reverses_quality(self):
        for z in (0, 1):
            high = self.oracle.branch(z, ("H01",) * 3)
            flipped = self.oracle.branch(z, ("H10",) * 3)
            self.assertEqual(high["utilities"], flipped["utilities"])
            for metric in ("accuracy", "false_approval_rate", "false_rejection_rate"):
                self.assertEqual(flipped[metric], 1 - high[metric])

    def test_V4_O05_zero_lambda_and_zero_cost_preserve_ties(self):
        for z in (0, 1):
            for action in self.oracle.ACTIONS:
                result = self.oracle.branch(z, (action, "L0", "L1"), lam=F(0), cost=F(0))
                self.assertEqual(result["utilities"][0], F(0))

    def test_V4_O06_result_is_a_negative_finding_with_explicit_scope(self):
        result = self.oracle.run_checks()
        self.assertEqual(result["finding"], "all_low_persists_without_audit")
        self.assertEqual(result["status"], "passed")
        self.assertFalse(result["general_equilibrium_search"])
        self.assertEqual(result["worst_false_approval_rate"], F(1))
        self.assertEqual(result["worst_false_rejection_rate"], F(1))
        self.assertGreater(result["statewise_checks"], 0)
        self.assertTrue(all(row["max_deviation_gain"] == 0 for row in result["certificates"]))

    def test_V4_O07_run_refuses_overwrite_and_pins_actual_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "run"
            self.oracle.write_run(out)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            for item in manifest["inputs"]:
                self.assertEqual(sha256((out / item["snapshot"]).read_bytes()).hexdigest(), item["sha256"])
            original = (out / "oracle.json").read_bytes()
            with self.assertRaises(FileExistsError):
                self.oracle.write_run(out)
            self.assertEqual((out / "oracle.json").read_bytes(), original)

    def test_V4_O08_imports_no_production_math(self):
        source = (ROOT / "verification/oracle_v4.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertFalse(any(name and name.split(".")[0] in ("ceav_m1", "tests") for name in imports))

    def test_V4_O09_optimized_mode_keeps_oracle_checks_active(self):
        command = (
            "import json; "
            "from verification.oracle_v4 import run_checks, _jsonable; "
            "print(json.dumps(_jsonable(run_checks())))"
        )
        process = subprocess.run([sys.executable, "-O", "-c", command], cwd=ROOT,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["finding"], "all_low_persists_without_audit")
        self.assertGreater(result["statewise_checks"], 0)

        mutation = (
            "import verification.oracle_v4 as oracle; "
            "from fractions import Fraction; "
            "oracle.realized_score=lambda *args: Fraction(1); "
            "oracle.run_checks()"
        )
        rejected = subprocess.run([sys.executable, "-O", "-c", mutation], cwd=ROOT,
                                  capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("AssertionError", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
