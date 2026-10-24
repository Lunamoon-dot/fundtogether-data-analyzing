"""Test-only mutation probes for the V5.1 quality certificates.

Each mutation runs in a temporary copy of the independent oracle and runner.
Repository sources and immutable artifacts are never modified.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


MUTATIONS = {
    "M01_vote_tie_rule": (
        "sum(votes) >= 2",
        "sum(votes) > 2",
        "majority decision must use the declared two-of-three threshold",
    ),
    "M02_wrong_direct_forecast_target": (
        "p = posterior_t(fixture, judge, z, xs[judge] if high else None)",
        "p = posterior_y(fixture, judge, z, xs[judge] if high else None)",
        "Direct Brier must forecast the audit T, not Y",
    ),
    "M03_wrong_decision_error_side": (
        "F(y == 0 and decision == 1)",
        "F(y == 1 and decision == 1)",
        "false-approval event must use Y=0 and D=1",
    ),
    "M04_wrong_direct_score": (
        "return score(_forecast(fixture, judge, z, action, xs), t)",
        "return score(_forecast(fixture, judge, z, action, xs), t) + F(1, 100)",
        "Brier score expectation must remain exact",
    ),
}


def _run_in_copy(mutation):
    with tempfile.TemporaryDirectory() as folder_name:
        folder = Path(folder_name)
        (folder / "verification").mkdir()
        oracle_source = (ROOT / "verification/oracle_v5_1_quality.py").read_text(encoding="utf-8")
        old, new, _ = mutation
        if old not in oracle_source:
            raise AssertionError(f"mutation target missing: {old}")
        oracle_source = oracle_source.replace(old, new)
        (folder / "verification/oracle_v5_1_quality.py").write_text(oracle_source, encoding="utf-8")
        shutil.copyfile(ROOT / "verification/v5_1_quality_certificates.py",
                        folder / "verification/v5_1_quality_certificates.py")
        command = "from verification.v5_1_quality_certificates import run_certificate; run_certificate()"
        return subprocess.run([sys.executable, "-O", "-c", command], cwd=folder,
                              capture_output=True, text=True)


def run_probes():
    records = []
    for name, mutation in MUTATIONS.items():
        result = _run_in_copy(mutation)
        if result.returncode == 0:
            raise AssertionError((name, "mutation was not rejected"))
        records.append({
            "id": name,
            "status": "rejected",
            "reason": mutation[2],
            "returncode": result.returncode,
        })
    return {"status": "passed", "mutations": records, "scope": "temporary-copy-only"}


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    sources = [
        Path("verification/oracle_v5_1_quality.py"),
        Path("verification/v5_1_quality_certificates.py"),
        Path("verification/mutation_probes_v5_1.py"),
    ]
    manifest = {
        "event_type": "v5.1_phase1.5_quality_mutation_run",
        "status": "running",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": [],
    }
    for source in sources:
        target = out / "inputs" / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({
            "source": source.as_posix(),
            "snapshot": target.relative_to(out).as_posix(),
            "sha256": sha256(target.read_bytes()).hexdigest(),
        })
    try:
        result = run_probes()
        (out / "mutations.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        manifest["status"] = "succeeded"
        manifest["outputs"] = {
            "mutations.json": sha256((out / "mutations.json").read_bytes()).hexdigest()
        }
        return result
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--out":
        print(write_run(sys.argv[2]))
    else:
        print(run_probes())

