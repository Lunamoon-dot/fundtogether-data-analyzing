"""Aggregate V2.1 calibration tests, regression and browser evidence."""

import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ceav_m1 import V2_MODEL_VERSION
from ceav_m1.calibration import CALIBRATION_VERSION, calibration_documents
from ceav_m1.output import finish_run, new_run, sha256, write_json
from tests.test_v2_release import latest_browser, manifest_sources_match


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit(out, tests_folder, v1_folder, v2_folder):
    out, tests_folder, v1_folder, v2_folder = map(Path, (out, tests_folder, v1_folder, v2_folder))
    manifest = new_run(out, "calibration_acceptance", request={"tests": str(tests_folder), "v1": str(v1_folder), "v2": str(v2_folder)}, model_version=V2_MODEL_VERSION)
    checks = []

    def record(requirement, condition, evidence):
        checks.append({"requirement": requirement, "status": "pass" if condition else "fail", "evidence": evidence})

    try:
        tests, tests_manifest = read(tests_folder / "test_results.json"), read(tests_folder / "manifest.json")
        v1, v1_manifest = read(v1_folder / "test_results.json"), read(v1_folder / "manifest.json")
        v2, v2_manifest = read(v2_folder / "test_results.json"), read(v2_folder / "manifest.json")
        cal_ids = {f"CAL-T{i:02}" for i in range(1, 9)}
        v1_ids = {f"T{i:02}" for i in range(1, 33)}
        v2_ids = {f"V2-T{i:02}" for i in range(1, 16)}
        record("CAL-T01 through CAL-T08 executed", tests["status"] == "passed" and {r["test_id"] for r in tests["records"]} == cal_ids and all(r["status"] == "pass" for r in tests["records"]), {"run": tests_folder.name, "counts": tests["counts"]})
        record("V1 regression executed", v1["status"] == "passed" and {r["test_id"] for r in v1["records"]} == v1_ids and all(r["status"] == "pass" for r in v1["records"]), {"run": v1_folder.name, "counts": v1["counts"]})
        record("V2 regression executed", v2["status"] == "passed" and {r["test_id"] for r in v2["records"]} == v2_ids and all(r["status"] == "pass" for r in v2["records"]), {"run": v2_folder.name, "counts": v2["counts"]})
        record("Calibration tests use current source", manifest_sources_match(tests_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "verification/")), tests_manifest["engine_revision"])
        record("V1 regression uses current source", manifest_sources_match(v1_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "verification/")), v1_manifest["engine_revision"])
        record("V2 regression uses current source", manifest_sources_match(v2_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "verification/")), v2_manifest["engine_revision"])
        browser = latest_browser("CAL-B01")
        record("CAL-B01 current-source browser acceptance", bool(browser and all(step["status"] == "pass" for step in browser[2]["steps"])), {"run": browser[1].name if browser else None})
        freeze = calibration_documents()
        record("Calibration implementation-start freeze is intact", freeze["feature"] == CALIBRATION_VERSION, {"freeze": CALIBRATION_VERSION, "files": len(freeze["files"])})
        raw = ROOT / "datasets/synthetic_v2_calibration.csv"
        record("Synthetic fixture is pinned and labeled", raw.is_file() and read(ROOT / "datasets/synthetic_v2_calibration.metadata.json")["provenance_status"] == "synthetic", {"sha256": sha256(raw.read_bytes())})
        passed = all(item["status"] == "pass" for item in checks)
        acceptance = {"feature_version": CALIBRATION_VERSION, "model_version": V2_MODEL_VERSION,
                      "status": "passed" if passed else "failed", "checks": checks,
                      "inputs": {"calibration_tests_manifest_sha256": sha256((tests_folder / "manifest.json").read_bytes()),
                                 "v1_manifest_sha256": sha256((v1_folder / "manifest.json").read_bytes()),
                                 "v2_manifest_sha256": sha256((v2_folder / "manifest.json").read_bytes())}}
        write_json(out / "acceptance.json", acceptance)
        for name in ("test_results.json", "test_log.txt"):
            shutil.copyfile(tests_folder / name, out / name)
        (out / "report.md").write_text("# CEAV-M1 V2.1 — Calibration acceptance\n\n" +
            f"Status: {acceptance['status']}.\n\n" + "\n".join(f"- {item['requirement']}: {item['status']}" for item in checks) + "\n",
            encoding="utf-8", newline="\n")
        finish_run(out, manifest, "succeeded" if passed else "failed")
        return passed
    except BaseException as error:
        finish_run(out, manifest, "failed", error)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--v1", type=Path, required=True)
    parser.add_argument("--v2", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if audit(args.out, args.tests, args.v1, args.v2) else 1)
