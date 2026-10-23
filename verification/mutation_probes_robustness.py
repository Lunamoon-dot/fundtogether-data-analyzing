"""V3.1 robustness mutations executed only in isolated workspace copies."""

import argparse
import difflib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ceav_m1 import V3_MODEL_VERSION
from ceav_m1.output import finish_run, new_run, sha256, source_files, write_json


PROBES = {
    "ROB-M01": ("tests.test_robustness.RobustnessTests.test_ROB_T04_worst_equilibrium_gates_keep_all_reasons",
                '"false_approval_rate": summary["ranges"]["false_approval_rate"]["max"],',
                '"false_approval_rate": summary["ranges"]["false_approval_rate"]["min"],',
                "Worst equilibrium uses max false approval"),
    "ROB-M02": ("tests.test_robustness.RobustnessTests.test_ROB_T04_worst_equilibrium_gates_keep_all_reasons",
                'return ["no_pure_equilibrium"], None', 'return [], None', "No-pure point fails closed"),
    "ROB-M03": ("tests.test_robustness.RobustnessTests.test_ROB_T05_policy_aggregation_and_classification",
                'all(point["status"] == "pass" for point in selected)',
                'any(point["status"] == "pass" for point in selected)', "Every scenario must pass"),
    "ROB-M04": ("tests.test_robustness.RobustnessTests.test_ROB_T07_references_match_independent_fixture_and_labels",
                'config.payout_value * (1 - config.pi) * false_approval',
                'config.payout_value * false_approval', "Wrong payout includes fake-claim prevalence"),
    "ROB-M05": ("tests.test_robustness.RobustnessTests.test_ROB_T06_exact_pareto_dominance_and_ties",
                'strict = any(other["worst"][metric] < candidate["worst"][metric] for metric in RISK_METRICS)',
                'strict = weak', "Pareto equality is not strict dominance"),
    "ROB-M06": ("tests.test_robustness.RobustnessTests.test_ROB_T02_cartesian_expansion_and_pseudo_axes",
                'for judge in JUDGES:', 'for judge in ("A",):', "Cost multiplier applies to all Judges"),
}


def copy_workspace(destination):
    for directory in ("ceav_m1", "tests", "configs", "scenarios", "datasets", "verification", "spec_history", "web"):
        source = ROOT / directory
        if source.exists():
            shutil.copytree(source, destination / directory, ignore=shutil.ignore_patterns("__pycache__"))


def run(out, ids):
    out = Path(out).resolve()
    manifest = new_run(out, "robustness_mutations", request={"ids": ids, "scope": "test-only temporary copies"}, model_version=V3_MODEL_VERSION)
    baseline_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
    try:
        tests = sorted({PROBES[name][0] for name in ids})
        baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests, "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (out / "baseline_log.txt").write_text(baseline.stdout + baseline.stderr, encoding="utf-8", newline="\n")
        if baseline.returncode:
            raise ValueError("Robustness mutation baseline is not passing")
        records = []
        for name in ids:
            test, before, after, target = PROBES[name]
            folder = out / name
            folder.mkdir()
            mutant = folder / "workspace"
            mutant.mkdir()
            copy_workspace(mutant)
            file = mutant / "ceav_m1/robustness.py"
            old = file.read_text(encoding="utf-8")
            if old.count(before) != 1:
                raise ValueError(f"{name}: mutation anchor must match once")
            changed = old.replace(before, after, 1)
            patch = "".join(difflib.unified_diff(old.splitlines(keepends=True), changed.splitlines(keepends=True), fromfile="ceav_m1/robustness.py", tofile="ceav_m1/robustness.py"))
            file.write_text(changed, encoding="utf-8", newline="\n")
            (folder / "mutation.patch").write_text(patch, encoding="utf-8", newline="\n")
            command = [sys.executable, "-B", "-m", "unittest", test, "-v"]
            process = subprocess.run(command, cwd=mutant, capture_output=True, text=True, encoding="utf-8", errors="replace")
            log = process.stdout + process.stderr
            (folder / "test_log.txt").write_text(log, encoding="utf-8", newline="\n")
            invalid = any(marker in log for marker in ("SyntaxError", "ImportError:", "ModuleNotFoundError", "Ran 0 tests"))
            status = "invalid" if invalid else ("killed" if process.returncode else "survived")
            records.append({"mutation_id": name, "status": status, "expected_failure": target, "test_ids": [test],
                            "argv": command, "exit_code": process.returncode, "patch_sha256": sha256(patch.encode()),
                            "baseline_source_hash": manifest["engine_revision"], "assertion_log": f"{name}/test_log.txt"})
            print(name, status, flush=True)
        after_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
        if baseline_hashes != after_hashes:
            raise ValueError("Production or fixtures changed during robustness mutation probes")
        write_json(out / "mutation_results.json", {"baseline_exit_code": baseline.returncode,
                   "production_bytes_unchanged": True, "records": records})
        (out / "report.md").write_text("# CEAV-M1 V3.1 — Mutation probes\n\n" + "\n".join(
            f"- {record['mutation_id']}: {record['status']} — {record['expected_failure']}" for record in records) + "\n",
            encoding="utf-8", newline="\n")
        passed = all(record["status"] == "killed" for record in records)
        finish_run(out, manifest, "succeeded" if passed else "failed")
        return passed
    except BaseException as error:
        finish_run(out, manifest, "failed", error)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", choices=list(PROBES), default=list(PROBES))
    args = parser.parse_args()
    raise SystemExit(0 if run(args.out, args.ids) else 1)
