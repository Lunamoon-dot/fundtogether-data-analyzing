import json
from pathlib import Path
import unittest

from ceav_m1.output import ROOT
from tests.test_v2_release import latest_browser, latest_test_evidence, manifest_sources_match


class CalibrationReleaseTests(unittest.TestCase):
    def test_CAL_T07_browser_evidence(self):
        match = latest_browser("CAL-B01")
        self.assertIsNotNone(match, "Missing passed current-source CAL-B01 evidence")
        _, folder, result, manifest = match
        self.assertTrue(all(step["status"] == "pass" for step in result["steps"]))
        self.assertTrue(manifest_sources_match(manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "verification/")))
        self.evidence = {"run_id": folder.name, "steps": len(result["steps"]), "source_matches": True}

    def test_CAL_T08_full_regression_evidence(self):
        evidence = {}
        for label, ids in (("v1", [f"T{i:02}" for i in range(1, 33)]),
                           ("v2", [f"V2-T{i:02}" for i in range(1, 16)])):
            match = latest_test_evidence(ids)
            self.assertIsNotNone(match, f"Missing passed current-source {label.upper()} regression evidence")
            _, folder, result, _ = match
            self.assertEqual(result["counts"]["fail"] + result["counts"]["error"] + result["counts"]["skipped"] + result["counts"]["not_run"], 0)
            evidence[label] = {"run_id": folder.name, "counts": result["counts"]}
        self.evidence = {"runs": evidence, "source_matches": True}


if __name__ == "__main__":
    unittest.main()
