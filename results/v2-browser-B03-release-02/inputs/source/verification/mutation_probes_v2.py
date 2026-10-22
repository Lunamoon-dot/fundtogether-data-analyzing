"""V2 signal/scenario mutations executed only in isolated workspace copies."""

import argparse
import difflib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ceav_m1 import V2_MODEL_VERSION
from ceav_m1.output import finish_run, new_run, sha256, source_files, write_json


def replacement(path, before, after):
    return path, before, after


PROBES = {
    "V2-M01": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T02_distribution_matches_independent_oracle"], "target": "Y=0 uses specificity", "edits": [replacement("ceav_m1/signals.py", "    return specificity if not value else 1 - specificity\n", "    return sensitivity if not value else 1 - sensitivity\n")]},
    "V2-M02": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T02_distribution_matches_independent_oracle"], "target": "Y=1 uses sensitivity", "edits": [replacement("ceav_m1/signals.py", "        return sensitivity if value else 1 - sensitivity\n", "        return specificity if value else 1 - specificity\n")]},
    "V2-M03": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T02_distribution_matches_independent_oracle", "tests.test_v2_engine.V2EngineTests.test_V2_T05_candidate_predictions_metrics_and_observations"], "target": "B/C retain their own channels", "edits": [replacement("ceav_m1/signals.py", "        private = tuple(zip(config.private_sensitivities, config.private_specificities))\n", "        private = ((config.private_sensitivities[0], config.private_specificities[0]),) * 3\n")]},
    "V2-M04": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T01_nested_schema_dispatch_and_errors"], "target": "Judge names, not JSON order, determine positions", "edits": [replacement("ceav_m1/model.py", "    judges = _exact_object(raw[\"judges\"], JUDGES, \"judges\")\n    sensitivities, specificities, costs = [], [], []\n    for judge in JUDGES:\n", "    judges = _exact_object(raw[\"judges\"], JUDGES, \"judges\")\n    sensitivities, specificities, costs = [], [], []\n    for judge in judges:\n")]},
    "V2-M05": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T01_nested_schema_dispatch_and_errors"], "target": "Missing specificity is rejected", "edits": [replacement("ceav_m1/model.py", "    public = _exact_object(raw[\"public_signal\"], (\"sensitivity\", \"specificity\"), \"public_signal\")\n", "    if \"specificity\" not in raw[\"public_signal\"]:\n        raw[\"public_signal\"][\"specificity\"] = raw[\"public_signal\"][\"sensitivity\"]\n    public = _exact_object(raw[\"public_signal\"], (\"sensitivity\", \"specificity\"), \"public_signal\")\n")]},
    "V2-M06": {"tests": ["tests.test_v2_io.V2IOTests.test_V2_T09_manifest_certificate_freeze_and_scenario_identity"], "target": "Semantic hash includes model_version", "edits": [replacement("ceav_m1/output.py", "        return {str(k): canonicalize(v) for k, v in value.items()}\n", "        return {str(k): canonicalize(v) for k, v in value.items() if str(k) != \"model_version\"}\n")]},
    "V2-M07": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T03_signal_diagnostics_exact"], "target": "Signal accuracy is prior weighted", "edits": [replacement("ceav_m1/signals.py", '            "prior_weighted_accuracy": config.pi * sensitivity + (1 - config.pi) * specificity,\n', '            "prior_weighted_accuracy": (sensitivity + specificity) / 2,\n')]},
    "V2-M08": {"tests": ["tests.test_v2_io.V2IOTests.test_V2_T08_scenario_validation_and_mathematical_neutrality"], "target": "Scenario cannot alter mathematics", "edits": [replacement("ceav_m1/__main__.py", "    scenario = validate_scenario(scenario) if scenario is not None else None\n", "    scenario = validate_scenario(scenario) if scenario is not None else None\n    if scenario is not None:\n        config = validate_config(raw_config | {\"pi\": \"2/3\"}, mechanism)\n")]},
    "V2-M09": {"tests": ["tests.test_v2_model.V2ModelTests.test_V2_T04_v1_reduction_states_predictions_and_analysis"], "target": "V1 state generator semantics remain unchanged", "edits": [replacement("ceav_m1/signals.py", "        return (config.a, config.a), ((config.b, config.b),) * 3\n", "        return (config.a, config.a), ((config.a, config.a),) * 3\n")]},
}


def run(out, ids):
    out = Path(out).resolve()
    manifest = new_run(out, "v2_mutations", request={"ids": ids, "scope": "test-only temporary copies"}, model_version=V2_MODEL_VERSION)
    baseline_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
    try:
        tests = sorted({test for name in ids for test in PROBES[name]["tests"]})
        baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests, "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (out / "baseline_log.txt").write_text(baseline.stdout + baseline.stderr, encoding="utf-8")
        if baseline.returncode:
            raise ValueError("V2 mutation baseline is not passing")
        records = []
        for name in ids:
            probe, folder = PROBES[name], out / name
            folder.mkdir()
            mutant = folder / "workspace"
            mutant.mkdir()
            for directory in ("ceav_m1", "tests", "configs", "scenarios", "verification", "spec_history"):
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
            invalid = any(marker in log for marker in ("SyntaxError", "ImportError:", "ModuleNotFoundError", "Ran 0 tests"))
            status = "invalid" if invalid else ("killed" if process.returncode and ("FAIL:" in log or "ERROR:" in log) else "survived")
            records.append({"mutation_id": name, "status": status, "expected_failure": probe["target"], "test_ids": probe["tests"], "argv": command, "exit_code": process.returncode, "patch_sha256": sha256(patch.encode()), "baseline_source_hash": manifest["engine_revision"], "assertion_log": f"{name}/test_log.txt"})
            print(name, status, flush=True)
        after_hashes = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()) for path in source_files()}
        if baseline_hashes != after_hashes:
            raise ValueError("Production or fixtures changed during V2 mutation probes")
        write_json(out / "mutation_results.json", {"baseline_exit_code": baseline.returncode, "production_bytes_unchanged": True, "records": records})
        (out / "report.md").write_text("# CEAV-M1 V2 — Mutation probes\n\n" + "\n".join(f"- {record['mutation_id']}: {record['status']} — {record['expected_failure']}" for record in records) + "\n", encoding="utf-8", newline="\n")
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
