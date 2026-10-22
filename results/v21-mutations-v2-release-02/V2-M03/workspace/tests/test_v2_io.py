from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ceav_m1.__main__ import execute
from ceav_m1.evaluate import analyze
from ceav_m1.model import ValidationError, validate_config, validate_scenario
from ceav_m1.output import restore_exact, semantic_hash
from ceav_m1.strategies import validate_profile
from tests.test_v2_model import ROOT, raw_profile, raw_v2


def raw_scenario():
    return json.loads((ROOT / "scenarios/sample_campaign/scenario.json").read_text(encoding="utf-8"))


class V2IOTests(unittest.TestCase):
    def test_V2_T08_scenario_validation_and_mathematical_neutrality(self):
        scenario = validate_scenario(raw_scenario())
        self.assertEqual(scenario, raw_scenario())
        invalid = raw_scenario(); invalid["parameter_provenance"]["status"] = "invented"
        with self.assertRaises(ValidationError) as caught:
            validate_scenario(invalid)
        self.assertEqual(caught.exception.field, "scenario.parameter_provenance.status")
        config, profile = validate_config(raw_v2()), validate_profile(raw_profile())
        self.assertEqual(analyze(config, profile), analyze(config, profile))
        with tempfile.TemporaryDirectory() as temporary:
            plain = execute("analyze", raw_v2(), raw_profile(), "rbts", Path(temporary) / "plain")
            contextual = execute("analyze", raw_v2(), raw_profile(), "rbts", Path(temporary) / "context", scenario=raw_scenario())
            self.assertEqual(plain, contextual)

    def test_V2_T09_manifest_certificate_freeze_and_scenario_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "v2-run"
            direct = execute("analyze", raw_v2(), raw_profile(), "rbts", out, scenario=raw_scenario())
            manifest = restore_exact(json.loads((out / "manifest.json").read_text(encoding="utf-8")))
            summary = restore_exact(json.loads((out / "summary.json").read_text(encoding="utf-8")))
            certificate = restore_exact(json.loads((out / "certificate.json").read_text(encoding="utf-8")))
            self.assertEqual(manifest["model_version"], "ceav-m1-v2.0")
            self.assertEqual(manifest["spec"]["revision"], "signal-heterogeneity-r1")
            self.assertEqual(set(manifest["documents"]), {"CEAV_M1_V2_SPEC.md", "ENGINE_DESIGN_V2.md", "VERIFICATION_PLAN_V2.md"})
            self.assertEqual(manifest["scenario_hash"], semantic_hash(raw_scenario()))
            self.assertNotEqual(semantic_hash(raw_v2()), semantic_hash(raw_v2() | {"model_version": "changed-for-hash-check"}))
            self.assertEqual(manifest["scenario"], raw_scenario())
            self.assertTrue((out / "scenario.json").is_file())
            self.assertEqual(certificate["identity"]["scenario_hash"], manifest["scenario_hash"])
            self.assertEqual(summary["signal_diagnostics"], direct["signal_diagnostics"])

    def test_V2_T10_cli_analyze_scenario_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "cli-v2"
            command = [sys.executable, "-B", "-m", "ceav_m1", "analyze", "--config", str(ROOT / "configs/v2/heterogeneous.json"),
                       "--profile", str(ROOT / "configs/all_high.json"), "--scenario", str(ROOT / "scenarios/sample_campaign/scenario.json"),
                       "--mechanism", "rbts", "--out", str(out)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(second.returncode, 0)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["model_version"], "ceav-m1-v2.0")
            self.assertTrue(any(item["name"] == "scenario.json" for item in manifest["artifacts"]))

    def test_V2_T11_nested_sweep_axes_replay_and_invalid_rows(self):
        axes = {"public_signal.specificity": ["3/5", "4/5"], "judges.A.high_effort_cost": ["1/20"], "lambda": ["3/4", "1"]}
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "sweep"
            result = execute("sweep", raw_v2(), raw_profile(), "rbts", out, sweep=axes)
            self.assertEqual(len(result["rows"]), 4)
            self.assertEqual([row["status"] for row in result["rows"]].count("valid"), 2)
            self.assertEqual([row["status"] for row in result["rows"]].count("invalid_budget"), 2)
            valid = next(row for row in result["rows"] if row["status"] == "valid" and row["public_signal.specificity"] == F(4, 5))
            replay_raw = json.loads(valid["config_json"])
            replay = analyze(validate_config(replay_raw), validate_profile(raw_profile()))
            self.assertEqual(replay["metrics"]["wrong_payout_value"], valid["wrong_payout_value"])
            self.assertEqual(replay_raw["judges"]["A"]["high_effort_cost"], "1/20")
            self.assertEqual(raw_v2()["public_signal"]["specificity"], "3/5")


if __name__ == "__main__":
    unittest.main()
