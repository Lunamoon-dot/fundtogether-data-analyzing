import hashlib
import json
from pathlib import Path
import unittest

from ceav_m1.output import ROOT


def manifest_sources_match(manifest, prefixes):
    selected = [item for item in manifest["source_files"] if item["path"].startswith(prefixes)]
    return bool(selected) and all((ROOT / item["path"]).is_file() and hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in selected)


def latest_browser(scenario):
    matches = []
    for path in (ROOT / "results").glob("*/browser_results.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("scenario") != scenario or result.get("status") != "passed":
            continue
        manifest = json.loads((path.parent / "manifest.json").read_text(encoding="utf-8"))
        flow = "verification/browser_flows_v2.js" if scenario.startswith("V2-") else "verification/browser_flows.js"
        flow_record = next((item for item in manifest["source_files"] if item["path"] == flow), None)
        flow_matches = bool(flow_record and hashlib.sha256((ROOT / flow).read_bytes()).hexdigest() == flow_record["sha256"])
        if manifest.get("status") == "succeeded" and manifest_sources_match(manifest, ("ceav_m1/", "web/", "configs/")) and flow_matches:
            matches.append((manifest["created_at_utc"], path.parent, result, manifest))
    return max(matches, default=None, key=lambda item: item[0])


class V2ReleaseTests(unittest.TestCase):
    def test_V2_T14_current_source_full_v1_regression(self):
        folder = ROOT / "results" / "v2-v1-regression-release-02"
        result = json.loads((folder / "test_results.json").read_text(encoding="utf-8"))
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(result["status"], "passed")
        self.assertEqual({record["test_id"] for record in result["records"]}, {f"T{i:02}" for i in range(1, 33)})
        self.assertEqual(result["counts"]["fail"] + result["counts"]["error"] + result["counts"]["skipped"] + result["counts"]["not_run"], 0)
        self.assertTrue(manifest_sources_match(manifest, ("ceav_m1/", "web/", "tests/", "configs/", "verification/")))
        self.evidence = {"run_id": folder.name, "counts": result["counts"], "source_matches": True}

    def test_V2_T15_registry_browser_and_mutation_evidence(self):
        registry = json.loads((ROOT / "tests" / "registry_v2.json").read_text(encoding="utf-8"))
        self.assertEqual(set(registry["tests"]), {f"V2-T{i:02}" for i in range(1, 16)})

        browser = {}
        for scenario in [f"B{i:02}" for i in range(1, 10)] + [f"V2-B{i:02}" for i in range(1, 7)]:
            match = latest_browser(scenario)
            self.assertIsNotNone(match, f"Missing passed current-source browser evidence: {scenario}")
            _, folder, result, _ = match
            self.assertTrue(all(step["status"] == "pass" for step in result["steps"]), scenario)
            browser[scenario] = folder.name

        folder = ROOT / "results" / "v2-mutations-release-04"
        mutations = json.loads((folder / "mutation_results.json").read_text(encoding="utf-8"))
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual({record["mutation_id"] for record in mutations["records"]}, {f"V2-M{i:02}" for i in range(1, 10)})
        self.assertTrue(all(record["status"] == "killed" for record in mutations["records"]))
        self.assertTrue(mutations["production_bytes_unchanged"])
        self.assertTrue(manifest_sources_match(manifest, ("ceav_m1/", "web/", "tests/", "configs/", "scenarios/", "verification/")))
        self.evidence = {"registry_ids": sorted(registry["tests"]), "browser_runs": browser, "mutation_run": folder.name}


if __name__ == "__main__":
    unittest.main()
