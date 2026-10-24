"""Test-only mutation probes for the V5 Phase 1 certificate.

Each probe runs a temporary source copy and expects the independent
certificate to reject a changed identity or boundary.  No repository source
is modified.
"""

from pathlib import Path
from hashlib import sha256
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


MUTATIONS = {
    "M01_noise_factor": (
        "d * d * value", "d * value",
        "noise attenuation must use d squared"),
    "M02_effort_cost_sign": (
        "policy.mu * policy.q * deltas[i][z] - fixture.judges[i].cost",
        "policy.mu * policy.q * deltas[i][z] + fixture.judges[i].cost",
        "effort cost must reduce utility"),
    "M03_cap_coefficient": (
        "denominator = F(6) if mechanism == \"incremental\"",
        "denominator = F(3) if mechanism == \"incremental\"",
        "shifted incremental cap must reserve 6 mu"),
    "M04_strict_boundary": (
        "value > 0 for row in gains",
        "value >= 0 for row in gains",
        "equality must retain a tie, not strict entry"),
    "M05_baseline_posterior": (
        '"p_l_t"] == (F(3, 10), F(19, 30))',
        '"p_l_t"] == (F(1, 2), F(1, 2))',
        "baseline posterior must remain model-derived"),
}


def _run_in_copy(replacements):
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        (folder / "verification").mkdir()
        shutil.copyfile(ROOT / "verification/oracle_v5.py", folder / "verification/oracle_v5.py")
        source = (ROOT / "verification/feasibility_v5.py").read_text(encoding="utf-8")
        for old, new, _ in replacements:
            if old not in source:
                raise AssertionError(f"mutation target missing: {old}")
            source = source.replace(old, new, 1)
        (folder / "verification/feasibility_v5.py").write_text(source, encoding="utf-8")
        command = "import verification.feasibility_v5 as m; m.run_certificate()"
        return subprocess.run([sys.executable, "-O", "-c", command], cwd=folder,
                              capture_output=True, text=True)


def run_probes():
    records = []
    for name, mutation in MUTATIONS.items():
        result = _run_in_copy([mutation])
        if result.returncode == 0:
            raise AssertionError((name, "mutation was not rejected"))
        records.append({"id": name, "status": "rejected", "reason": mutation[2]})
    return {"status": "passed", "mutations": records, "scope": "temporary-copy-only"}


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path("verification/oracle_v5.py"), Path("verification/feasibility_v5.py"),
               Path("verification/mutation_probes_v5.py"), Path("tests/test_v5_feasibility.py")]
    manifest = {"event_type": "v5.0_agiis_phase1_mutation_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "inputs": []}
    for source in sources:
        target = out / "inputs" / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({"source": source.as_posix(), "snapshot": target.relative_to(out).as_posix(),
                                    "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        result = run_probes()
        (out / "mutations.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {"mutations.json": sha256((out / "mutations.json").read_bytes()).hexdigest()}
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
