"""Aggregate V3.1 tests, browser, mutations and the predeclared full study."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ceav_m1 import V3_MODEL_VERSION
from ceav_m1.output import documents, finish_run, new_run, sha256, write_json
from tests.test_v2_release import manifest_sources_match


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def latest_robustness_browser():
    matches = []
    for path in (ROOT / "results").glob("*/browser_results.json"):
        result = read(path)
        if result.get("scenario") != "ROB-B01" or result.get("status") != "passed":
            continue
        browser_manifest = read(path.parent / "manifest.json")
        pinned = {item["path"]: item["sha256"] for item in browser_manifest.get("source_files", [])}
        flow = "verification/browser_flows_robustness.js"
        harness = "verification/browser_acceptance.py"
        if (browser_manifest.get("status") == "succeeded" and
                manifest_sources_match(browser_manifest, ("ceav_m1/", "web/", "configs/")) and
                pinned.get(flow) == sha256((ROOT / flow).read_bytes()) and
                pinned.get(harness) == sha256((ROOT / harness).read_bytes())):
            matches.append((browser_manifest["created_at_utc"], path.parent, result, browser_manifest))
    return max(matches, default=None, key=lambda item: item[0])


def audit(out, tests_folder, mutations_folder, study_folder):
    out, tests_folder, mutations_folder, study_folder = map(Path, (out, tests_folder, mutations_folder, study_folder))
    manifest = new_run(out, "robustness_acceptance_audit", request={
        "tests": str(tests_folder), "mutations": str(mutations_folder), "study": str(study_folder),
    }, model_version=V3_MODEL_VERSION)
    checks = []

    def record(requirement, condition, evidence):
        checks.append({"requirement": requirement, "status": "pass" if condition else "fail", "evidence": evidence})

    try:
        tests = read(tests_folder / "test_results.json")
        tests_manifest = read(tests_folder / "manifest.json")
        records = tests.get("records", [])
        robustness_records = [item for item in records if str(item.get("test_id", "")).startswith("ROB-")]
        expected_tests = {f"ROB-T{i:02}" for i in range(1, 11)}
        record("ROB-T01 through ROB-T10 executed and passed",
               {item.get("test_id") for item in robustness_records} == expected_tests and all(item.get("status") == "pass" for item in robustness_records),
               {"ids": sorted(item.get("test_id") for item in robustness_records), "counts": tests.get("counts")})
        record("Full V1 through V3.1 regression passed",
               tests.get("suite") == "all" and tests.get("status") == "passed" and
               all(tests.get("counts", {}).get(key, 0) == 0 for key in ("fail", "error", "skipped", "not_run")),
               {"suite": tests.get("suite"), "counts": tests.get("counts")})
        record("Test evidence matches current executable source",
               tests_manifest.get("status") == "succeeded" and manifest_sources_match(
                   tests_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/")),
               {"run": tests_folder.name, "source_hash": tests_manifest.get("engine_revision")})

        browser = latest_robustness_browser()
        record("ROB-B01 current-source browser acceptance passed",
               bool(browser and browser[2].get("status") == "passed" and all(step.get("status") == "pass" for step in browser[2].get("steps", []))),
               {"run": browser[1].name if browser else None, "steps": len(browser[2].get("steps", [])) if browser else 0})

        mutations = read(mutations_folder / "mutation_results.json")
        mutation_manifest = read(mutations_folder / "manifest.json")
        mutation_records = mutations.get("records", [])
        expected_mutations = {f"ROB-M{i:02}" for i in range(1, 7)}
        mutation_hashes = all(sha256((mutations_folder / item["mutation_id"] / "mutation.patch").read_bytes()) == item["patch_sha256"] for item in mutation_records)
        record("ROB-M01 through ROB-M06 killed in isolated copies",
               {item.get("mutation_id") for item in mutation_records} == expected_mutations and
               all(item.get("status") == "killed" for item in mutation_records) and
               mutations.get("production_bytes_unchanged") is True and mutation_hashes,
               {"run": mutations_folder.name, "ids": sorted(item.get("mutation_id") for item in mutation_records)})
        record("Mutation evidence matches current engine, UI, tests and configs",
               mutation_manifest.get("status") == "succeeded" and manifest_sources_match(
                   mutation_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/")),
               {"source_hash": mutation_manifest.get("engine_revision")})

        freeze = documents(model_version=V3_MODEL_VERSION)
        record("V3.1 revision-start freeze remains intact",
               freeze.get("analysis_version") == "ceav-m1-v3.1-robustness" and
               freeze.get("event") == "analyzer_revision_implementation_start" and
               freeze.get("v3_1_oracle_preexisted") is True and
               freeze.get("v3_1_robustness_support_existed_before_event") is False,
               {"spec_revision": freeze.get("spec_revision"), "files": sorted(freeze.get("files", {}))})

        study = read(study_folder / "robustness.json")
        study_manifest = read(study_folder / "manifest.json")
        complete = (study.get("status") == "succeeded" and study.get("grid", {}).get("total_points") == 108 and
                    len(study.get("points", [])) == 108 and all(
                        point.get("branch_candidate_count") == 432 and point.get("enumeration_completed") is True
                        for point in study.get("points", [])))
        record("Predeclared 108-point study completed without partial search", complete,
               {"run": study_folder.name, "grid": study.get("grid"), "classification": study.get("classification")})
        record("Study evidence matches current engine, UI, tests and configs",
               study_manifest.get("status") == "succeeded" and manifest_sources_match(
                   study_manifest, ("ceav_m1/", "web/", "tests/", "configs/", "datasets/")),
               {"source_hash": study_manifest.get("engine_revision")})
        record("Study preserves declared interpretation limits",
               study.get("baseline_comparison", {}).get("latency_comparison") == "latency_not_modeled" and
               study.get("grid", {}).get("grid_only_no_interpolation") is True and
               "pure_strategies_only" in study.get("limitations", []),
               {"limitations": study.get("limitations"), "baseline_scope": study.get("baseline_comparison", {}).get("latency_comparison")})

        passed = all(item["status"] == "pass" for item in checks)
        result = {"analysis_version": "ceav-m1-v3.1-robustness", "model_version": V3_MODEL_VERSION,
                  "status": "passed" if passed else "failed", "checks": checks,
                  "study_result": {"classification": study.get("classification"),
                                   "robust_policy_ids": study.get("robust_policy_ids"),
                                   "pareto_policy_ids": study.get("pareto_frontier", {}).get("policy_ids")},
                  "inputs": {"tests_manifest_sha256": sha256((tests_folder / "manifest.json").read_bytes()),
                             "mutation_manifest_sha256": sha256((mutations_folder / "manifest.json").read_bytes()),
                             "study_manifest_sha256": sha256((study_folder / "manifest.json").read_bytes())}}
        write_json(out / "acceptance.json", result)
        (out / "report.md").write_text("# CEAV-M1 V3.1 — Acceptance\n\n" + f"Status: {result['status']}.\n\n" +
            "\n".join(f"- {item['requirement']}: {item['status']}" for item in checks) + "\n",
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
    parser.add_argument("--mutations", type=Path, required=True)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if audit(args.out, args.tests, args.mutations, args.study) else 1)
