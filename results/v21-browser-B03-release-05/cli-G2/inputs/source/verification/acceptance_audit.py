"""Audit current implementation against every CEAV-M1 acceptance gate.

Consumes immutable real suite/browser/mutation artifacts. Registration, HTTP200,
hashes alone, zero tests, partial work and stale production sources never pass.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ceav_m1.output import documents, finish_run, new_run, sha256, source_files, write_json
from tests.certificates import verify_run


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_matches(manifest, prefixes=None):
    files = [item for item in manifest["source_files"] if prefixes is None or item["path"].startswith(prefixes)]
    if not files:
        return False
    if not all((ROOT / item["path"]).is_file() and sha256((ROOT / item["path"]).read_bytes()) == item["sha256"] for item in files):
        return False
    if prefixes is None:
        return {item["path"] for item in files} == {path.relative_to(ROOT).as_posix() for path in source_files()}
    return True


def audit(out, mutation_folder):
    out, mutation_folder = Path(out), Path(mutation_folder)
    manifest = new_run(out, "acceptance_audit", request={"mutation_run": str(mutation_folder)})
    checks = []
    def record(name, condition, evidence):
        checks.append({"requirement": name, "status": "pass" if condition else "fail", "evidence": evidence})
    try:
        event = documents()
        record("GATE-0 frozen raw documents, parent chain and reference preexistence", event["reference_checker_preexisted"] and not event["analyzer_existed_before_event"], event)
        oracle = read(ROOT / "tests/fixtures/asymmetric_oracle.json")
        record("F09 oracle raw bytes reproduce recorded pre-production identity", sha256((ROOT / "tests/fixtures/oracle_preproduction.py").read_bytes()) == oracle["oracle_sha256"], read(ROOT / "tests/fixtures/oracle_recovery.json"))
        browser = {}
        for path in (ROOT / "results").glob("*/browser_results.json"):
            result, pinned = read(path), read(path.parent / "manifest.json")
            scenario = result["scenario"]
            if scenario not in browser or pinned["created_at_utc"] > browser[scenario][1]["created_at_utc"]:
                browser[scenario] = (path.parent, pinned, result)
        for i in range(1, 10):
            key = f"B{i:02}"
            entry = browser.get(key)
            valid = bool(entry and entry[1]["status"] == "succeeded" and entry[2]["status"] == "passed" and source_matches(entry[1], ("ceav_m1/", "web/", "configs/")) and all(step["status"] == "pass" for step in entry[2]["steps"]))
            record(key + " real browser scenario on current engine/web", valid, {"run": str(entry[0]) if entry else None})
        b06 = browser.get("B06")
        suite_folder = ROOT / "results" / b06[2]["all_run"] if b06 and b06[2].get("all_run") else None
        suite = read(suite_folder / "test_results.json") if suite_folder else {"records": [], "status": "missing", "suite": None}
        suite_manifest = read(suite_folder / "manifest.json") if suite_folder else None
        record("Complete all-suite is succeeded and pins current full source", bool(suite_manifest and suite_manifest["status"] == "succeeded" and suite["status"] == "passed" and suite["suite"] == "all" and source_matches(suite_manifest)), {"run": str(suite_folder), "counts": suite.get("counts")})
        registry = read(ROOT / "tests/registry.json")
        by_method = {r["unittest_id"]: r for r in suite["records"] if r.get("unittest_id")}
        test_status = {}
        for i in range(1, 33):
            key = f"T{i:02}"
            expected = registry["tests"][key]["unittest_ids"]
            passed = bool(expected) and all(name in by_method and by_method[name]["status"] == "pass" for name in expected)
            test_status[key] = passed
            record(key + " all registered assertions actually executed", passed, {"unittest_ids": expected, "run": str(suite_folder)})
        expected_methods = {name for row in registry["tests"].values() for name in row["unittest_ids"]}
        record("All-suite has no omitted/unregistered/skipped/zero tests", set(by_method) == expected_methods and bool(by_method) and all(r["status"] == "pass" for r in suite["records"]), {"registered_methods": len(expected_methods), "actual_methods": len(by_method)})
        f12 = next((r.get("evidence") for r in suite["records"] if "F12_catalog" in r.get("unittest_id", "")), None)
        record("F12 forward/reverse catalog exact differential", bool(f12 and f12["total_branch_candidates"] == 11664 and f12["reverse_order_branch_candidates"] == 11664 and len(f12["catalog"]) == 27 and len(f12["candidate_catalog"]) == 432 and not f12["discrepancies"]), f12)
        t17 = next((r.get("evidence") for r in suite["records"] if "T17_full_profile" in r.get("unittest_id", "")), None)
        record("T17 direct full-profile exact set equality", bool(t17 and t17["profiles_checked"] == 46656 and t17["full_strategy_deviations_compared"] == 5038848 and t17["set_difference"] == [] and len(t17["retained_full_profile_ids"]) == t17["equilibrium_count"]), t17)
        mutations = read(mutation_folder / "mutation_results.json")
        mutation_manifest = read(mutation_folder / "manifest.json")
        current_mutation_source = source_matches(mutation_manifest, ("ceav_m1/", "web/", "tests/", "configs/"))
        record("Mutation baseline and relevant production/test sources", mutations["baseline_exit_code"] == 0 and mutations["production_bytes_unchanged"] and current_mutation_source, {"run": str(mutation_folder), "source_matches_engine_web_tests": current_mutation_source})
        mutation_status = {}
        for i in range(1, 14):
            key = f"M{i:02}"
            item = next((r for r in mutations["records"] if r["mutation_id"] == key), None)
            passed = bool(item and item["status"] == "killed" and item["exit_code"] != 0)
            if item:
                patch = mutation_folder / key / "mutation.patch"
                log = (mutation_folder / item["assertion_log"]).read_text(encoding="utf-8")
                passed = passed and sha256(patch.read_bytes()) == item["patch_sha256"] and ("FAIL:" in log or "ERROR:" in log) and not any(text in log for text in ("SyntaxError", "ModuleNotFoundError", "Ran 0 tests"))
            mutation_status[key] = bool(passed)
            record(key + " targeted semantic mutant killed", passed, item)
        benchmark = []
        if "B03" in browser:
            golden = next((s["observed"] for s in browser["B03"][2]["steps"] if s["step"] == "Golden run identities"), [])
            parity = read(browser["B03"][0] / "cli_parity.json") if (browser["B03"][0] / "cli_parity.json").exists() else []
            record("Actual CLI/API byte equality G1-G4", len(parity) == 4 and all(p["numeric_artifacts_byte_equal"] and p["cli_exit_code"] == 0 for p in parity), parity)
            for item in golden:
                folder = ROOT / "results" / item["run_id"]
                valid = verify_run(folder)
                record(item["golden"] + " standalone certificate independently replayed", valid, {"run": str(folder)})
                pinned = read(folder / "manifest.json")
                benchmark.append({"command": "analyze", "golden": item["golden"], "run_id": item["run_id"], "duration_seconds": pinned["duration_seconds"], "python": pinned["python"], "platform": pinned["platform"], "machine": pinned["machine"], "logical_cpu_count": pinned["logical_cpu_count"], "source_hash": pinned["engine_revision"], "config_hash": pinned["config_hash"]})
        if "B04" in browser:
            identities = next((s["observed"] for s in browser["B04"][2]["steps"] if s["step"] == "Search and full analysis IDs"), None)
            if identities:
                folder = ROOT / "results" / identities["search"]
                pinned, search = read(folder / "manifest.json"), read(folder / "equilibria.json")
                benchmark.append({"command": "equilibria", "run_id": identities["search"], "duration_seconds": pinned["duration_seconds"], "python": pinned["python"], "platform": pinned["platform"], "machine": pinned["machine"], "logical_cpu_count": pinned["logical_cpu_count"], "source_hash": pinned["engine_revision"], "config_hash": pinned["config_hash"], "branch_candidates": search["branch_candidate_count"], "full_equilibria": search["full_equilibrium_count"]})
        if "B05" in browser:
            comparison = next((s["observed"] for s in browser["B05"][2]["steps"] if s["step"] == "Comparison artifact source"), None)
            valid = False
            if comparison:
                folder = ROOT / "results" / comparison["run_id"]
                summaries = {name: read(folder / name / "summary.json") for name in ("fixed", "rbts")}
                valid = verify_run(folder / "fixed") and verify_run(folder / "rbts")
                valid = valid and summaries["fixed"]["reward_cap"]["exact"] == summaries["rbts"]["reward_cap"]["exact"] and summaries["fixed"]["metrics"]["expected_reward_total"]["exact"] != summaries["rbts"]["metrics"]["expected_reward_total"]["exact"]
                for name in ("fixed/states.csv", "rbts/states.csv"):
                    expected = next(item["sha256"] for item in comparison["manifest"]["artifacts"] if item["name"] == name)
                    valid = valid and sha256((browser["B05"][0] / name.replace("/", "-")).read_bytes()) == expected
            record("Equal-cap comparison, independent sub-certificates and nested downloads", valid, comparison)
        record("Measured analyze and exhaustive pure-search benchmarks", any(b["command"] == "analyze" for b in benchmark) and any(b["command"] == "equilibria" and b["branch_candidates"] == 432 for b in benchmark), benchmark)
        write_json(out / "benchmark.json", {"timed_scope": "engine and artifact generation, excluding input/source pinning", "runs": benchmark})
        gate_ranges = {"GATE-1": range(1, 6), "GATE-2": range(6, 16), "GATE-3": range(16, 20), "GATE-4": range(20, 23), "GATE-5": range(23, 33)}
        gate_mutations = {"GATE-2": [1,2,3,5,7,8,9,10], "GATE-3": [4,11], "GATE-4": [6], "GATE-5": [12,13]}
        gates = {"GATE-0": all(c["status"] == "pass" for c in checks[:2])}
        for gate, ids in gate_ranges.items():
            gates[gate] = all(test_status[f"T{i:02}"] for i in ids) and all(mutation_status[f"M{i:02}"] for i in gate_mutations.get(gate, []))
        # Every explicit ancillary check is also mandatory, not just gate counts.
        passed = all(c["status"] == "pass" for c in checks) and all(gates.values())
        write_json(out / "acceptance.json", {"status": "passed" if passed else "failed", "gates": gates, "checks": checks,
                   "all_suite_run": str(suite_folder), "browser_runs": {key: str(value[0]) for key, value in browser.items()},
                   "mutation_run": str(mutation_folder), "claims_production_or_user_study": False})
        (out / "report.md").write_text("# CEAV-M1 — Acceptance audit\n\n" + ("PASS" if passed else "FAIL") + "\n\n" + "\n".join(f"- {key}: {'pass' if value else 'fail'}" for key, value in gates.items()) + "\n\n" + "\n".join(f"- {c['status']}: {c['requirement']}" for c in checks) + "\n\nScope remains pure equilibrium in CEAV-M1; no mixed/coalition/selection, human behavior or production claim.\n", encoding="utf-8", newline="\n")
        finish_run(out, manifest, "succeeded" if passed else "failed")
        print(json.dumps({"status": "passed" if passed else "failed", "gates": gates, "failed_requirements": [c["requirement"] for c in checks if c["status"] != "pass"]}))
        return passed
    except BaseException as error:
        (out / "report.md").write_text(f"# Acceptance audit failed\n\n{error}\n", encoding="utf-8")
        finish_run(out, manifest, "failed", error)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mutations", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if audit(args.out, args.mutations) else 1)
