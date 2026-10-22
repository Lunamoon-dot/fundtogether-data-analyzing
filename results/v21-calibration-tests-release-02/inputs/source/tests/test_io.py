from fractions import Fraction as F
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from ceav_m1.__main__ import execute
from ceav_m1.output import FREEZE, ROOT, documents, exact_payload, restore_exact, semantic_hash
from ceav_m1.test_runner import run_suite
from tests.test_core import config, profile


class IOTests(unittest.TestCase):
    def test_T20_exact_roundtrip_budget_accounting(self):
        values = [F(1, 2), F(1, 2) + F(1, 10**18), F(1, 2) - F(1, 10**18)]
        self.assertEqual(restore_exact(json.loads(json.dumps(exact_payload(values)))), values)
        self.assertNotEqual(exact_payload(values)[0]["exact"], exact_payload(values)[1]["exact"])
        huge = exact_payload(F(10**1000))
        self.assertIsNone(huge["decimal"])
        self.assertEqual(huge["decimal_reason"], "outside_finite_display_range")
        self.assertEqual(restore_exact(huge), F(10**1000))
        from ceav_m1.evaluate import analyze
        result = analyze(config(), profile())
        self.assertLess(result["metrics"]["expected_reward_total"], result["reward_cap"])
        self.assertEqual(sum(result["metrics"]["expected_judge_utility"]), result["metrics"]["expected_reward_total"] - result["metrics"]["expected_effort_cost"])

    def test_T21_semantic_hash_snapshot_provenance(self):
        self.assertEqual(semantic_hash(config(pi="0.5")), semantic_hash(config(pi="1/2")))
        self.assertNotEqual(semantic_hash(config(pi="0.51")), semantic_hash(config()))
        event = documents()
        self.assertTrue(event["reference_checker_preexisted"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "spec_history", root / "spec_history")
            self.assertEqual(documents(root), event)
            path = root / FREEZE / "ENGINE_DESIGN.md"
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                documents(root)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "spec_history", root / "spec_history")
            path = root / "spec_history/html-ui-r1/CEAV_M1_SPEC.md"
            path.write_bytes(path.read_bytes() + b"tamper ancestor")
            with self.assertRaises(ValueError):
                documents(root)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "spec_history", root / "spec_history")
            path = root / FREEZE / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["freeze_status"] = "not_frozen_for_analyzer_implementation"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                documents(root)

    def test_T21_deterministic_numeric_output_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = (Path(temporary) / name for name in ("first", "second"))
            for folder in (first, second):
                execute("analyze", config().raw(), profile().raw(), "rbts", folder)
            for name in ("summary.json", "states.csv", "best_responses.json", "config.json", "profile.json"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            before = (first / "manifest.json").read_bytes()
            with self.assertRaises(FileExistsError):
                execute("analyze", config().raw(), profile().raw(), "rbts", first)
            self.assertEqual((first / "manifest.json").read_bytes(), before)
            self.assertEqual((first / "inputs/CEAV_M1_SPEC.md").read_bytes(), (ROOT / FREEZE / "CEAV_M1_SPEC.md").read_bytes())
            manifest = json.loads(before)
            self.assertEqual(manifest["engine_revision"], semantic_hash(manifest["source_files"]))

    def test_T22_cli_real_subprocess_artifacts_and_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cfg = ROOT / "configs/golden_g1.json"
            pr = ROOT / "configs/all_high.json"
            operations = (("analyze", cfg, ("summary.json", "best_responses.json", "states.csv")),
                          ("equilibria", cfg, ("summary.json", "equilibria.json")),
                          ("sweep", ROOT / "configs/sweep.json", ("sweep.csv", "sweep.json")),
                          ("compare", cfg, ("summary.json", "fixed/summary.json", "rbts/summary.json")))
            for operation, path, artifacts in operations:
                out = root / operation
                argv = [sys.executable, "-B", "-m", "ceav_m1", operation, "--config", str(path), "--out", str(out)]
                if operation != "equilibria":
                    argv += ["--profile", str(pr)]
                process = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                for name in ("manifest.json", "report.md", *artifacts):
                    self.assertTrue((out / name).is_file(), name)
                report = (out / "report.md").read_text(encoding="utf-8")
                self.assertIn("0 < pi,a,b < 1", report, "Research reports must state the parameter domain")
                self.assertIn('"model_version": "ceav-m1-v1.0"', report, "Report must include actual pinned config")
                duplicate = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(duplicate.returncode, 0)
            bad = root / "bad.json"
            bad.write_text(json.dumps(config().raw() | {"pi": 0.5}), encoding="utf-8")
            invalid = subprocess.run([sys.executable, "-B", "-m", "ceav_m1", "analyze", "--config", str(bad), "--profile", str(pr), "--out", str(root / "bad")], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("pi", invalid.stderr)
            self.assertFalse((root / "bad").exists())
            failed = root / "invalid-sweep-after-start"
            with self.assertRaises(ValueError):
                execute("sweep", config().raw(), profile().raw(), "rbts", failed, sweep={"typo": ["1"]})
            self.assertEqual(json.loads((failed / "manifest.json").read_text(encoding="utf-8"))["status"], "failed")
            self.assertTrue((failed / "report.md").is_file(), "Failed commands must preserve a report")

    def test_T21_cross_cwd_numeric_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = [root / "from-root", root / "from-other-cwd"]
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(ROOT)
            for cwd, out in zip((ROOT, root), outputs):
                process = subprocess.run([sys.executable, "-B", "-m", "ceav_m1", "analyze", "--config", str(ROOT / "configs/golden_g4.json"), "--profile", str(ROOT / "configs/all_high.json"), "--out", str(out)], cwd=cwd, env=environment, capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
            for name in ("summary.json", "best_responses.json", "states.csv"):
                self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes())

    def test_T15_artifact_certificate_identity_and_cancelled_rejection(self):
        from tests.certificates import verify_run
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "certificate"
            execute("analyze", config("golden_g4").raw(), profile().raw(), "rbts", out)
            self.assertTrue(verify_run(out))
            path = out / "certificate.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            original["identity"]["config_hash"] = "tampered"
            path.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_run(out)
            # Restore the actual certificate, then reject a cancelled manifest.
            original["identity"]["config_hash"] = semantic_hash(config("golden_g4"))
            path.write_text(json.dumps(original), encoding="utf-8")
            manifest_path = out / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["status"] = "cancelled"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_run(out)

    def test_T28_sweep_invalid_rows_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = execute("sweep", config().raw(), profile().raw(), "rbts", Path(temporary) / "sweep", sweep={"lambda": ["0", "1", "2"]})
            self.assertEqual([r["status"] for r in result["rows"]], ["valid", "valid", "invalid_budget"])
            self.assertEqual(result["rows"][1]["config_hash"], semantic_hash(config()))

    def test_T29_runner_actual_failure_and_missing_ids(self):
        reference, _ = run_suite("reference")
        self.assertEqual(reference["reference_results"]["G1"]["accuracy"]["exact"], "112/125")
        result, log = run_suite("selected", ["T01"])
        self.assertEqual(result["counts"]["pass"], 1)
        self.assertEqual(result["status"], "passed")
        result, log = run_suite("selected", [], injected_fixture=True)
        self.assertEqual(result["counts"]["fail"], 1)
        self.assertEqual(result["status"], "not_passed")
        self.assertIn("Explicit failure fixture", log)
        # A valid ID with zero discovered methods must not become a pass.
        from unittest.mock import patch
        with patch("ceav_m1.test_runner.discover", return_value=[]):
            result, _ = run_suite("selected", ["T01"])
            self.assertEqual(result["counts"]["not_run"], 1)
            self.assertEqual(result["counts"]["error"], 1)
            self.evidence = {"missing_discovery_fixture": result, "production_engine_unchanged": True}
        with self.assertRaises(ValueError):
            run_suite("selected", [])
        with self.assertRaises(ValueError):
            run_suite("selected", ["os.system"])
        from ceav_m1.test_runner import write_test_run
        with tempfile.TemporaryDirectory() as temporary:
            failed = Path(temporary) / "discovery-crash"
            with patch("ceav_m1.test_runner.discover", side_effect=ValueError("fixture discovery failed")):
                with self.assertRaises(ValueError):
                    write_test_run(failed, "selected", ["T01"])
            self.assertTrue((failed / "report.md").is_file(), "Runner crash must preserve report")
            self.assertTrue((failed / "test_log.txt").is_file(), "Runner crash must preserve actual traceback")
            record = json.loads((failed / "test_results.json").read_text(encoding="utf-8"))
            self.assertEqual(record["counts"]["error"], 1)
            self.assertIn("fixture discovery failed", (failed / "test_log.txt").read_text(encoding="utf-8"))

    def test_T30_comparison_equal_cap_actual_spend(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = execute("compare", config().raw(), profile().raw(), "rbts", Path(temporary) / "compare")
            self.assertEqual(result["reward_cap"], F(6))
            self.assertNotEqual(result["mechanisms"]["fixed"]["metrics"]["expected_reward_total"], result["mechanisms"]["rbts"]["metrics"]["expected_reward_total"])
            self.assertEqual(result["mechanisms"]["fixed"]["metrics"]["accuracy"], result["mechanisms"]["rbts"]["metrics"]["accuracy"])
            manifest = json.loads((Path(temporary) / "compare/manifest.json").read_text(encoding="utf-8"))
            self.assertIn("fixed/certificate.json", [a["name"] for a in manifest["artifacts"]])
            self.assertIn("rbts/states.csv", [a["name"] for a in manifest["artifacts"]])
            from tests.certificates import verify_run
            self.assertTrue(verify_run(Path(temporary) / "compare/fixed"))
            self.assertTrue(verify_run(Path(temporary) / "compare/rbts"))
            with self.assertRaises(ValueError):
                execute("compare", config(fixed_reward="1").raw(), profile().raw(), "rbts", Path(temporary) / "invalid")


if __name__ == "__main__":
    unittest.main()
