"""Targeted semantic mutations, isolated copies; production is never patched."""

import argparse
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ceav_m1.output import finish_run, new_run, sha256, source_files, write_json


def replacement(path, before, after):
    return (path, before, after)


PROBES = {
    "M01": {"tests": ["tests.test_core.CoreTests.test_T12_peer_freeze_numeric_counterexample"], "target": "T12/F04 peer payoff must stay at original candidate tables", "edits": [replacement("ceav_m1/best_response.py", '    for effort in ("L", "H"):\n', '    for effort in ("L", "H"):\n        from .strategies import Profile, build_candidate\n        branches = [list(branch) for branch in candidate.profile.branches]\n        branches[z][judge] = "L0" if effort == "L" else "H01"\n        rebuilt = build_candidate(config, Profile(tuple(tuple(b) for b in branches)), mechanism=mechanism)\n        frozen_rows = [(s, *realized(rebuilt, s)) for s in rows]\n')]},
    "M02": {"tests": ["tests.test_core.CoreTests.test_T11_G4_post_signal_effort"], "target": "T11/F08 must reject averaged positive Delta", "edits": [replacement("ceav_m1/evaluate.py", '    maximum = max(c["regret"] for c in certificates)', '    maximum = F(0) if all(sum(c["branch_probability"] * c["delta_utility"] for c in certificates if c["judge"] == label) >= 0 for label in JUDGES) else max(c["regret"] for c in certificates)')]},
    "M03": {"tests": ["tests.test_core.CoreTests.test_T13_joint_expectation"], "target": "T13 independent state oracle must distinguish joint and product marginals", "edits": [replacement("ceav_m1/best_response.py", '                for s, reports, predictions in group:\n                    ref = predictions[j]\n                    shadow = ref + (2 * r - 1) * min(ref, 1 - ref)\n                    total += s.probability / group_mass * quadratic(shadow, reports[k])', '                for s, _, predictions in group:\n                    ref = predictions[j]\n                    shadow = ref + (2 * r - 1) * min(ref, 1 - ref)\n                    for other, reports, _ in group:\n                        total += s.probability * other.probability / group_mass**2 * quadratic(shadow, reports[k])')]},
    "M04": {"tests": ["tests.test_core.CoreTests.test_T05_H_constants_keep_private_prediction"], "target": "T05/F13 H constant reports still observe private signal", "edits": [replacement("ceav_m1/strategies.py", '            own = observe(state, i, actions[i][0])', '            own = LowObservation(state.z) if actions[i] in ("H00", "H11") else observe(state, i, actions[i][0])')]},
    "M05": {"tests": ["tests.test_core.CoreTests.test_T04_roles"], "target": "T04/F02 reference and scoring peer have distinct cyclic roles", "edits": [replacement("ceav_m1/scoring.py", '    j, k = (judge + 1) % 3, (judge + 2) % 3', '    j, k = (judge + 2) % 3, (judge + 1) % 3')]},
    "M06": {"tests": ["tests.test_core.CoreTests.test_T05_predictions_and_exact_loss"], "target": "T05/F11 production quadratic path must preserve tiny rational differences", "edits": [replacement("ceav_m1/scoring.py", '    return 2 * p - p * p if report else 1 - p * p', '    return F(float(2 * p - p * p if report else 1 - p * p))')]},
    "M07": {"tests": ["tests.test_core.CoreTests.test_T09_G1_all_judges_and_branches"], "target": "T09/F05 retain both optimal low reports", "edits": [replacement("ceav_m1/best_response.py", '            reports = [r for r in (0, 1) if values[r] == best]', '            reports = [r for r in (0, 1) if values[r] == best][:1]')]},
    "M08": {"tests": ["tests.test_core.CoreTests.test_T05_predictions_and_exact_loss"], "target": "T05/F06 prediction must target constant peer report, not Y", "edits": [replacement("ceav_m1/strategies.py", '        tables.append(tuple((key, ones / mass) for key, (mass, ones) in groups.items()))', '        tables.append(tuple((key, sum(s.probability * s.y for s in rows if observe(s, i, profile.branches[s.z][i][0]) == key) / mass) for key, (mass, ones) in groups.items()))')]},
    "M09": {"tests": ["tests.test_core.CoreTests.test_T06_fixed_constant_and_zero_costs"], "target": "T06/F09 different judge costs must be preserved", "edits": [replacement("ceav_m1/best_response.py", 'config.costs[judge]', 'config.costs[0]'), replacement("ceav_m1/evaluate.py", 'config.costs[i]', 'config.costs[0]')]},
    "M10": {"tests": ["tests.test_search.SearchTests.test_T18_binary_and_cyclic_relabel"], "target": "T18 false approval denominator is P(Y=0)", "edits": [replacement("ceav_m1/evaluate.py", '"false_approval_rate": fp / (1 - config.pi)', '"false_approval_rate": fp / config.pi')]},
    "M11": {"tests": ["tests.test_core.CoreTests.test_T06_fixed_constant_and_zero_costs"], "target": "T06/T19 constant reward predictions form a continuum", "edits": [replacement("ceav_m1/strategies.py", 'else "arbitrary_reachable_predictions"', 'else "unique_on_reachable_observations"')]},
    "M12": {"tests": ["tests.test_server.ServerTests.test_T30_duplicate_submit_immutable_snapshot_cancel"], "target": "T30 handshake proves cancel must stop the owned worker tree before terminal state", "edits": [replacement("ceav_m1/server.py", '        if process is not None:\n            terminate_tree(process)\n        job["done"].wait(5)', '        if process is not None:\n            job["status"] = "cancelled"\n            return self.snapshot(job)\n        job["done"].wait(5)')]},
    "M13": {"tests": ["tests.test_io.IOTests.test_T29_runner_actual_failure_and_missing_ids"], "target": "T29 zero discovery and missing IDs cannot pass", "edits": [replacement("ceav_m1/test_runner.py", '        if executed == 0:', '        if False:'), replacement("ceav_m1/test_runner.py", '    passed = bool(records) and counts.get("pass", 0) == len(records)', '    passed = counts.get("fail", 0) == 0 and counts.get("error", 0) == 0')]},
}


def run(out, ids):
    out = Path(out).resolve()
    manifest = new_run(out, "mutations", request={"ids": ids, "scope": "test-only temporary copies"})
    baseline_hashes = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in source_files()}
    try:
        tests = sorted({test for name in ids for test in PROBES[name]["tests"]})
        baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests, "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (out / "baseline_log.txt").write_text(baseline.stdout + baseline.stderr, encoding="utf-8")
        if baseline.returncode:
            raise ValueError("Mutation baseline is not passing; probes invalid")
        records = []
        for name in ids:
            probe = PROBES[name]
            folder = out / name
            folder.mkdir()
            mutant = folder / "workspace"
            mutant.mkdir()
            for directory in ("ceav_m1", "tests", "configs", "verification", "spec_history"):
                shutil.copytree(ROOT / directory, mutant / directory, ignore=shutil.ignore_patterns("__pycache__"))
            patches = []
            for path, before, after in probe["edits"]:
                file = mutant / path
                old = file.read_text(encoding="utf-8")
                if old.count(before) != 1:
                    raise ValueError(f"{name}: mutation anchor must match once: {path}")
                changed = old.replace(before, after, 1)
                patches.extend(difflib.unified_diff(old.splitlines(keepends=True), changed.splitlines(keepends=True), fromfile=path, tofile=path))
                file.write_text(changed, encoding="utf-8", newline="\n")
            patch = "".join(patches)
            (folder / "mutation.patch").write_text(patch, encoding="utf-8", newline="\n")
            command = [sys.executable, "-B", "-m", "unittest", *probe["tests"], "-v"]
            process = subprocess.run(command, cwd=mutant, capture_output=True, text=True, encoding="utf-8", errors="replace")
            log = process.stdout + process.stderr
            (folder / "test_log.txt").write_text(log, encoding="utf-8", newline="\n")
            invalid = "SyntaxError" in log or "ImportError:" in log or "ModuleNotFoundError" in log or "Ran 0 tests" in log
            status = "invalid" if invalid else ("killed" if process.returncode and ("FAIL:" in log or "ERROR:" in log) else "survived")
            records.append({"mutation_id": name, "status": status, "expected_failure": probe["target"],
                            "test_ids": probe["tests"], "argv": command, "exit_code": process.returncode,
                            "patch_sha256": sha256(patch.encode("utf-8")), "baseline_source_hash": manifest["engine_revision"],
                            "assertion_log": f"{name}/test_log.txt"})
            print(name, status, flush=True)
        after_hashes = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in source_files()}
        if baseline_hashes != after_hashes:
            raise ValueError("Production or fixtures changed during mutation probes")
        write_json(out / "mutation_results.json", {"baseline_exit_code": baseline.returncode, "production_bytes_unchanged": True, "records": records})
        (out / "report.md").write_text("# CEAV-M1 — Mutation probes\n\n" + "\n".join(f"- {r['mutation_id']}: {r['status']} — {r['expected_failure']}" for r in records) + "\n", encoding="utf-8", newline="\n")
        passed = all(r["status"] == "killed" for r in records)
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
