"""V4.1 mutation probes in isolated temporary copies only."""

import argparse
import difflib
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]

PROBES = {
    "V41-M01": {
        "target": "effort cost remains in utility",
        "edits": [("verification/v4_1_screening.py",
                   "- (self.fixture.costs[judge] if is_high(profile[judge]) else 0)",
                   "- F(0)")],
        "tests": ["tests.test_v4_1_screening.V41ScreeningTests.test_effort_cost_is_in_utility"],
    },
    "V41-M02": {
        "target": "centered covariance subtracts independent means",
        "edits": [("verification/v4_1_screening.py",
                   "self._score_cache[key] = moment - mean_i * mean_j",
                   "self._score_cache[key] = moment + mean_i * mean_j")],
        "tests": ["tests.test_v4_1_screening.V41ScreeningTests.test_covariance_identity_matches_direct_finite_score"],
    },
    "V41-M03": {
        "target": "frozen-peer deviation changes only the focal action",
        "edits": [("verification/v4_1_screening.py",
                   "changed = list(candidate_profile)\n        changed[judge] = action",
                   "changed = [action, action, action]")],
        "tests": ["tests.test_v4_1_screening.V41ScreeningTests.test_frozen_peer_deviation_uses_candidate_action_in_utility"],
    },
    "V41-M04": {
        "target": "target cash gate uses target population weights",
        "edits": [("verification/v4_1_screening.py",
                   "cash_target = sum(fixture.target_weights[z] * conditional[z][\"cash_cost\"] for z in (0, 1))",
                   "cash_target = sum(fixture.batch_weights[z] * conditional[z][\"cash_cost\"] for z in (0, 1))")],
        "tests": ["tests.test_v4_1_screening.V41ScreeningTests.test_target_cash_uses_target_weights_separately_from_batch_average"],
    },
    "V41-M05": {
        "target": "zero-regret tie profiles remain equilibria",
        "edits": [("verification/v4_1_screening.py",
                   "if all(response[\"regret\"] == 0 for response in responses):",
                   "if all(response[\"regret\"] > 0 for response in responses):")],
        "tests": ["tests.test_v4_1_screening.V41ScreeningTests.test_tie_boundary_keeps_all_low_equilibrium"],
    },
    "V41-M06": {
        "target": "all-low, inverted and asymmetric pure equilibria are retained",
        "edits": [("verification/v4_1_screening.py",
                   "if all(response[\"regret\"] == 0 for response in responses):",
                   "if all(response[\"regret\"] == 0 for response in responses) and classify_actions(profile) not in (\"all_low\", \"inverted_H10\", \"asymmetric_effort\"):")],
        "tests": [
            "tests.test_v4_1_screening.V41ScreeningTests.test_branch_search_keeps_all_low_and_label_inversion",
            "tests.test_v4_1_screening.V41ScreeningTests.test_full_screening_retains_asymmetric_effort_equilibria",
        ],
    },
}


SOURCE_FILES = (Path("verification/v4_1_screening.py"),
                Path("verification/oracle_v4_1_screening.py"),
                Path("tests/test_v4_1_screening.py"))


def _hashes(root):
    return {path.as_posix(): sha256((root / path).read_bytes()).hexdigest() for path in SOURCE_FILES}


def _copy_workspace(dest):
    for relative in SOURCE_FILES:
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)


def run(out, ids):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "event_type": "v4.1_screening_mutation_probes",
        "status": "running",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "temporary test-only copies",
        "ids": ids,
    }
    baseline_tests = sorted({test for probe_id in ids for test in PROBES[probe_id]["tests"]})
    baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", *baseline_tests, "-v"],
                              cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (out / "baseline.log").write_text(baseline.stdout + baseline.stderr, encoding="utf-8", newline="\n")
    if baseline.returncode:
        manifest.update(status="failed", error="baseline_tests_failed")
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError("V4.1 mutation baseline failed")

    before = _hashes(ROOT)
    records = []
    with tempfile.TemporaryDirectory(prefix="ceav-v41-mutants-") as temporary:
        temporary = Path(temporary)
        for probe_id in ids:
            probe = PROBES[probe_id]
            folder = out / probe_id
            folder.mkdir()
            mutant = temporary / probe_id
            _copy_workspace(mutant)
            patches = []
            for relative, old, new in probe["edits"]:
                file = mutant / relative
                original = file.read_text(encoding="utf-8")
                if original.count(old) != 1:
                    raise ValueError(f"{probe_id}: mutation anchor count for {relative} is {original.count(old)}")
                changed = original.replace(old, new, 1)
                patches.extend(difflib.unified_diff(original.splitlines(keepends=True), changed.splitlines(keepends=True),
                                                    fromfile=relative, tofile=relative))
                file.write_text(changed, encoding="utf-8", newline="\n")
            (folder / "mutation.patch").write_text("".join(patches), encoding="utf-8", newline="\n")
            command = [sys.executable, "-B", "-m", "unittest", *probe["tests"], "-v"]
            process = subprocess.run(command, cwd=mutant, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace")
            log = process.stdout + process.stderr
            (folder / "test.log").write_text(log, encoding="utf-8", newline="\n")
            invalid = any(marker in log for marker in ("SyntaxError", "ImportError:", "ModuleNotFoundError", "Ran 0 tests"))
            status = "invalid" if invalid else ("killed" if process.returncode else "survived")
            records.append({"mutation_id": probe_id, "status": status, "target": probe["target"],
                            "tests": probe["tests"], "exit_code": process.returncode,
                            "assertion_log": f"{probe_id}/test.log",
                            "patch_sha256": sha256("".join(patches).encode()).hexdigest()})

    if _hashes(ROOT) != before:
        raise RuntimeError("production bytes changed during mutation probes")
    (out / "mutation_results.json").write_text(json.dumps({"production_bytes_unchanged": True, "records": records},
                                                            indent=2) + "\n", encoding="utf-8")
    (out / "report.md").write_text("# CEAV-M1 V4.1 — Mutation probes\n\n" +
                                   "\n".join(f"- {record['mutation_id']}: {record['status']} — {record['target']}"
                                             for record in records) + "\n", encoding="utf-8", newline="\n")
    manifest.update(status="succeeded" if all(record["status"] == "killed" for record in records) else "failed",
                    records=records)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest["status"] == "succeeded"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", choices=sorted(PROBES), default=sorted(PROBES))
    args = parser.parse_args()
    raise SystemExit(0 if run(args.out, args.ids) else 1)
