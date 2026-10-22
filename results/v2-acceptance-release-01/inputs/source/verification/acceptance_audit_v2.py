"""Aggregate final V2 tests, browser flows, mutations and benchmark evidence."""

import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ceav_m1 import V2_MODEL_VERSION
from ceav_m1.output import finish_run, new_run, sha256, write_json
from tests.test_v2_release import latest_browser


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit(out, tests_folder, v1_folder, mutations_folder):
    out, tests_folder, v1_folder, mutations_folder = map(Path, (out, tests_folder, v1_folder, mutations_folder))
    manifest = new_run(out, "v2_acceptance_audit", request={"tests": str(tests_folder), "v1_regression": str(v1_folder), "mutations": str(mutations_folder)}, model_version=V2_MODEL_VERSION)
    checks = []
    def record(requirement, condition, evidence):
        checks.append({"requirement": requirement, "status": "pass" if condition else "fail", "evidence": evidence})
    try:
        tests, tests_manifest = read(tests_folder / "test_results.json"), read(tests_folder / "manifest.json")
        v1, v1_manifest = read(v1_folder / "test_results.json"), read(v1_folder / "manifest.json")
        mutations, mutation_manifest = read(mutations_folder / "mutation_results.json"), read(mutations_folder / "manifest.json")
        record("V2-T01 through V2-T15 executed", tests["status"] == "passed" and {r["test_id"] for r in tests["records"]} == {f"V2-T{i:02}" for i in range(1, 16)} and all(r["status"] == "pass" for r in tests["records"]), {"run": tests_folder.name, "counts": tests["counts"]})
        record("V1 T01 through T32 regression", v1["status"] == "passed" and {r["test_id"] for r in v1["records"]} == {f"T{i:02}" for i in range(1, 33)} and all(r["status"] == "pass" for r in v1["records"]), {"run": v1_folder.name, "counts": v1["counts"]})
        for scenario in [f"B{i:02}" for i in range(1, 10)] + [f"V2-B{i:02}" for i in range(1, 7)]:
            match = latest_browser(scenario)
            record(scenario + " current-source browser acceptance", bool(match and all(step["status"] == "pass" for step in match[2]["steps"])), {"run": match[1].name if match else None})
        for mutation_id in [f"V2-M{i:02}" for i in range(1, 10)]:
            item = next((row for row in mutations["records"] if row["mutation_id"] == mutation_id), None)
            valid = bool(item and item["status"] == "killed" and item["exit_code"] != 0 and sha256((mutations_folder / mutation_id / "mutation.patch").read_bytes()) == item["patch_sha256"])
            record(mutation_id + " targeted mutation killed", valid, item)
        t07 = next(recorded for recorded in tests["records"] if recorded["test_id"] == "V2-T07")
        benchmark = {"command": "V2 direct oracle plus production search", "duration_seconds": t07["duration_seconds"], "evidence": t07["evidence"], "python": tests_manifest["python"], "platform": tests_manifest["platform"], "machine": tests_manifest["machine"], "logical_cpu_count": tests_manifest["logical_cpu_count"], "source_hash": tests_manifest["engine_revision"]}
        write_json(out / "benchmark.json", benchmark)
        for name in ("test_results.json", "test_log.txt"):
            shutil.copyfile(tests_folder / name, out / name)
        passed = all(check["status"] == "pass" for check in checks)
        acceptance = {"model_version": V2_MODEL_VERSION, "status": "passed" if passed else "failed", "checks": checks, "inputs": {"v2_tests_manifest_sha256": sha256((tests_folder / "manifest.json").read_bytes()), "v1_regression_manifest_sha256": sha256((v1_folder / "manifest.json").read_bytes()), "mutation_manifest_sha256": sha256((mutations_folder / "manifest.json").read_bytes())}}
        write_json(out / "acceptance.json", acceptance)
        (out / "report.md").write_text("# CEAV-M1 V2 — Acceptance\n\n" + f"Status: {acceptance['status']}.\n\n" + "\n".join(f"- {item['requirement']}: {item['status']}" for item in checks) + "\n", encoding="utf-8", newline="\n")
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
    parser.add_argument("--mutations", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if audit(args.out, args.tests, args.v1, args.mutations) else 1)
