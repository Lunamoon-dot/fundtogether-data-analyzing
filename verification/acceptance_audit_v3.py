"""Aggregate final V3 tests, browser and mutation evidence on current source."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ceav_m1 import V3_MODEL_VERSION
from ceav_m1.output import documents, finish_run, new_run, sha256, write_json
from tests.test_v2_release import latest_browser, manifest_sources_match


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit(out, tests_folder, mutations_folder):
    out, tests_folder, mutations_folder = map(Path, (out, tests_folder, mutations_folder))
    manifest = new_run(out, "v3_acceptance_audit", request={"tests": str(tests_folder), "mutations": str(mutations_folder)}, model_version=V3_MODEL_VERSION)
    checks = []

    def record(requirement, condition, evidence):
        checks.append({"requirement": requirement, "status": "pass" if condition else "fail", "evidence": evidence})

    try:
        tests = read(tests_folder / "test_results.json")
        tests_manifest = read(tests_folder / "manifest.json")
        mutations = read(mutations_folder / "mutation_results.json")
        mutation_manifest = read(mutations_folder / "manifest.json")
        records = tests.get("records", [])
        v3 = [item for item in records if str(item.get("test_id", "")).startswith("V3-")]
        expected_v3 = {f"V3-T{i:02}" for i in range(1, 13)}
        record("V3-T01 through V3-T12 executed and passed", {item.get("test_id") for item in v3} == expected_v3 and all(item.get("status") == "pass" for item in v3), {"counts": tests.get("counts"), "ids": sorted(item.get("test_id") for item in v3)})
        record("Full V1/V2/V2.1/V2.2/V3 regression passed", tests.get("status") == "passed" and all(tests.get("counts", {}).get(key, 0) == 0 for key in ("fail", "error", "skipped", "not_run")), {"suite": tests.get("suite"), "counts": tests.get("counts")})
        record("Test evidence matches current source", tests_manifest.get("status") == "succeeded" and manifest_sources_match(tests_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "verification/")), {"run": tests_folder.name, "source_hash": tests_manifest.get("engine_revision")})

        browser = latest_browser("V3-B01")
        record("V3-B01 current-source browser acceptance passed", bool(browser and all(step.get("status") == "pass" for step in browser[2].get("steps", []))), {"run": browser[1].name if browser else None, "steps": len(browser[2]["steps"]) if browser else 0})

        expected_mutations = {f"V3-M{i:02}" for i in range(1, 11)}
        mutation_records = mutations.get("records", [])
        mutation_hashes = all(sha256((mutations_folder / item["mutation_id"] / "mutation.patch").read_bytes()) == item["patch_sha256"] for item in mutation_records)
        record("V3-M01 through V3-M10 killed in isolated copies", {item.get("mutation_id") for item in mutation_records} == expected_mutations and all(item.get("status") == "killed" for item in mutation_records) and mutations.get("production_bytes_unchanged") is True and mutation_hashes, {"run": mutations_folder.name, "ids": sorted(item.get("mutation_id") for item in mutation_records)})
        record("Mutation evidence matches current source", mutation_manifest.get("status") == "succeeded" and manifest_sources_match(mutation_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/", "scenarios/", "verification/")), {"source_hash": mutation_manifest.get("engine_revision")})

        freeze = documents(model_version=V3_MODEL_VERSION)
        record("V3 r2 revision-start freeze remains intact", freeze.get("model_version") == V3_MODEL_VERSION and freeze.get("event") == "analyzer_revision_implementation_start" and freeze.get("v3_oracle_preexisted") is True and freeze.get("v3_production_support_existed_before_event") is True and freeze.get("v3_r2_closeout_support_existed_before_event") is False, {"spec_revision": freeze.get("spec_revision"), "files": sorted(freeze.get("files", {}))})

        passed = all(item["status"] == "pass" for item in checks)
        result = {"model_version": V3_MODEL_VERSION, "status": "passed" if passed else "failed", "checks": checks,
                  "inputs": {"tests_manifest_sha256": sha256((tests_folder / "manifest.json").read_bytes()), "mutation_manifest_sha256": sha256((mutations_folder / "manifest.json").read_bytes())}}
        write_json(out / "acceptance.json", result)
        (out / "report.md").write_text("# CEAV-M1 V3 — Acceptance\n\n" + f"Status: {result['status']}.\n\n" + "\n".join(f"- {item['requirement']}: {item['status']}" for item in checks) + "\n", encoding="utf-8", newline="\n")
        finish_run(out, manifest, "succeeded" if passed else "failed")
        return passed
    except BaseException as error:
        finish_run(out, manifest, "failed", error)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--mutations", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if audit(args.out, args.tests, args.mutations) else 1)
