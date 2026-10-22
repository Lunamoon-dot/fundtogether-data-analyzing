"""T32 consumes real recorded keyboard/mobile/contrast evidence, never HTTP200."""

import hashlib
import json
import unittest

from ceav_m1.output import ROOT


class BrowserEvidenceTests(unittest.TestCase):
    def test_T32_current_source_desktop_mobile_browser_evidence(self):
        matching = []
        for path in (ROOT / "results").glob("*/browser_results.json"):
            result = json.loads(path.read_text(encoding="utf-8"))
            if result.get("scenario") != "B09" or result.get("status") != "passed":
                continue
            manifest = json.loads((path.parent / "manifest.json").read_text(encoding="utf-8"))
            sources = [item for item in manifest["source_files"] if item["path"].startswith(("ceav_m1/", "web/", "configs/"))]
            if sources and all(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in sources):
                matching.append((manifest["created_at_utc"], path.parent, result, manifest))
        self.assertTrue(matching, "No real B09 evidence for current engine/web source; browser acceptance must run first")
        _, folder, result, manifest = sorted(matching, key=lambda item: item[0])[-1]
        flow = next(s for s in result["steps"] if s["step"] == "Desktop/mobile keyboard flows")
        self.assertEqual(flow["observed"]["viewports"], [{"width": 1366, "height": 768}, {"width": 390, "height": 844}])
        contrast = next(s for s in result["steps"] if s["step"].startswith("Measured visible text contrast"))
        self.assertEqual(contrast["observed"]["failures"], [])
        self.assertGreater(len(contrast["observed"]["samples"]), 0)
        for name in ("desktop-analysis.png", "mobile-analysis.png", "desktop-history.png", "mobile-history.png"):
            item = next(a for a in manifest["artifacts"] if a["name"] == name)
            self.assertEqual(hashlib.sha256((folder / name).read_bytes()).hexdigest(), item["sha256"])
        self.assertTrue(all(step["status"] == "pass" for step in result["steps"]))
        self.evidence = {"browser_scenario": "B09", "run_id": folder.name, "browser": result["browser"],
                         "source_matches": True, "scope": "Recorded browser interactions; not inferred from unittest or HTTP200"}
