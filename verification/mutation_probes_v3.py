"""V3 hybrid-anchor mutations executed only in isolated workspace copies."""

import argparse
import difflib
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ceav_m1 import V3_MODEL_VERSION
from ceav_m1.output import finish_run, new_run, sha256, source_files, write_json


def replacement(path, before, after):
    return path, before, after


PROBES = {
    "V3-M01": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T03_observation_never_contains_audit_or_verification"], "target": "Strategy cannot observe post-report verification", "edits": [
        replacement("ceav_m1/model.py", "class HighObservation:\n    z: int\n    x: int\n", "class HighObservation:\n    z: int\n    x: int\n    verification: int | None = None\n"),
        replacement("ceav_m1/model.py", "return LowObservation(state.z) if effort == \"L\" else HighObservation(state.z, state.signals[judge])\n", "return LowObservation(state.z) if effort == \"L\" else HighObservation(state.z, state.signals[judge], state.verification)\n")
    ]},
    "V3-M02": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T04_candidate_accounting_matches_independent_fixture"], "target": "Anchor score uses verification T, never ground truth Y", "edits": [
        replacement("ceav_m1/evaluate.py", "anchor = anchor_score(reports[i], state.audit, state.verification) if hybrid else F(0)\n", "anchor = anchor_score(reports[i], state.audit, state.y) if hybrid else F(0)\n")
    ]},
    "V3-M03": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T04_candidate_accounting_matches_independent_fixture"], "target": "No anchor reward when audit A=0", "edits": [
        replacement("ceav_m1/scoring.py", "return F(audit and report == verification)\n", "return F(report == verification)\n")
    ]},
    "V3-M04": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T08_worst_case_budget_does_not_multiply_by_q"], "target": "Worst-case budget cap does not multiply anchor by audit probability", "edits": [
        replacement("ceav_m1/model.py", "cap = 3 * config.f + 6 * config.multiplier + 3 * config.anchor_weight\n", "cap = 3 * config.f + 6 * config.multiplier + 3 * config.anchor_weight * config.audit_probability\n")
    ]},
    "V3-M05": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T02_exact_distribution_and_support"], "target": "Audit draw is independent of Y/report", "edits": [
        replacement("ceav_m1/signals.py", "audit_mass = config.audit_probability if audit else 1 - config.audit_probability\n", "audit_mass = config.audit_probability if audit == y else 1 - config.audit_probability\n")
    ]},
    "V3-M06": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T04_candidate_accounting_matches_independent_fixture"], "target": "Hybrid utility subtracts High Effort cost", "edits": [
        replacement("ceav_m1/evaluate.py", "cost = config.costs[i] if action[0] == \"H\" else F(0)\n", "cost = F(0) if hybrid else (config.costs[i] if action[0] == \"H\" else F(0))\n")
    ]},
    "V3-M07": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T05_best_responses_match_independent_fixture"], "target": "Best-response report optimization includes anchor payoff", "edits": [
        replacement("ceav_m1/best_response.py", "combined = [config.multiplier * values[r] + config.anchor_weight * anchors[r] for r in (0, 1)]\n", "combined = [config.multiplier * values[r] for r in (0, 1)]\n")
    ]},
    "V3-M08": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T05_best_responses_match_independent_fixture"], "target": "Peer prediction tables remain frozen during deviation", "edits": [
        replacement("ceav_m1/best_response.py", "    for effort in (\"L\", \"H\"):\n        groups = {}\n", "    for effort in (\"L\", \"H\"):\n        from .strategies import Profile, build_candidate\n        branches = [list(branch) for branch in candidate.profile.branches]\n        branches[z][judge] = \"L0\" if effort == \"L\" else \"H01\"\n        rebuilt = build_candidate(config, Profile(tuple(tuple(branch) for branch in branches)), mechanism=mechanism)\n        frozen_rows = [(state, *realized(rebuilt, state)) for state in rows]\n        groups = {}\n")
    ]},
    "V3-M09": {"tests": ["tests.test_v3.V3EngineTests.test_V3_T06_zero_anchor_reduces_to_v2"], "target": "Zero anchor reduces exactly to V2 RBTS", "edits": [
        replacement("ceav_m1/scoring.py", "return config.f + config.multiplier * score + config.anchor_weight * anchor\n", "return 2 * config.f + config.multiplier * score + config.anchor_weight * anchor\n")
    ]},
    "V3-M10": {"browser": True, "target": "UI displays the exact anchor total from the artifact", "edits": [
        replacement("web/app.js", "numeric(m.expected_anchor_reward_total)", "numeric(m.expected_peer_reward_total)")
    ]},
}


def copy_workspace(destination):
    for directory in ("ceav_m1", "tests", "configs", "scenarios", "datasets", "verification", "spec_history", "web"):
        source = ROOT / directory
        if source.exists():
            shutil.copytree(source, destination / directory, ignore=shutil.ignore_patterns("__pycache__"))


def run_browser_mutant(mutant, folder):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    log_path = folder / "server_log.txt"
    with log_path.open("w", encoding="utf-8") as stream:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        server = subprocess.Popen([sys.executable, "-B", "-m", "ceav_m1", "serve", "--port", str(port)], cwd=mutant, stdout=stream, stderr=subprocess.STDOUT, creationflags=flags)
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if server.poll() is not None:
                    raise ValueError("Mutant browser server terminated")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/api/status", timeout=1):
                        break
                except OSError:
                    time.sleep(0.1)
            else:
                raise ValueError("Mutant browser server did not become ready")
            command = [sys.executable, "-B", "verification/browser_acceptance.py", "--scenario", "V3-B01", "--base", f"http://127.0.0.1:{port}", "--out", str(folder / "browser-evidence")]
            process = subprocess.run(command, cwd=mutant, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            return command, process
        finally:
            if server.poll() is None:
                server.terminate()
                server.wait(timeout=10)


def run(out, ids):
    out = Path(out).resolve()
    manifest = new_run(out, "v3_mutations", request={"ids": ids, "scope": "test-only temporary copies"}, model_version=V3_MODEL_VERSION)
    baseline_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
    try:
        tests = sorted({test for name in ids for test in PROBES[name].get("tests", [])})
        baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests, "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (out / "baseline_log.txt").write_text(baseline.stdout + baseline.stderr, encoding="utf-8")
        if baseline.returncode:
            raise ValueError("V3 mutation baseline is not passing")
        records = []
        for name in ids:
            probe, folder = PROBES[name], out / name
            folder.mkdir()
            mutant = folder / "workspace"
            mutant.mkdir()
            copy_workspace(mutant)
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
            if probe.get("browser"):
                command, process = run_browser_mutant(mutant, folder)
            else:
                command = [sys.executable, "-B", "-m", "unittest", *probe["tests"], "-v"]
                process = subprocess.run(command, cwd=mutant, capture_output=True, text=True, encoding="utf-8", errors="replace")
            log = process.stdout + process.stderr
            (folder / "test_log.txt").write_text(log, encoding="utf-8", newline="\n")
            invalid = any(marker in log for marker in ("SyntaxError", "ImportError:", "ModuleNotFoundError", "Ran 0 tests"))
            status = "invalid" if invalid else ("killed" if process.returncode else "survived")
            records.append({"mutation_id": name, "status": status, "expected_failure": probe["target"], "test_ids": probe.get("tests", ["V3-B01"]), "argv": command, "exit_code": process.returncode, "patch_sha256": sha256(patch.encode()), "baseline_source_hash": manifest["engine_revision"], "assertion_log": f"{name}/test_log.txt"})
            print(name, status, flush=True)
        after_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
        if baseline_hashes != after_hashes:
            raise ValueError("Production or fixtures changed during V3 mutation probes")
        write_json(out / "mutation_results.json", {"baseline_exit_code": baseline.returncode, "production_bytes_unchanged": True, "records": records})
        (out / "report.md").write_text("# CEAV-M1 V3 — Mutation probes\n\n" + "\n".join(f"- {record['mutation_id']}: {record['status']} — {record['expected_failure']}" for record in records) + "\n", encoding="utf-8", newline="\n")
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
