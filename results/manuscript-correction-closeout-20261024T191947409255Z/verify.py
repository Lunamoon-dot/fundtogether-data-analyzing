"""Run only the existing numerical/focused checks and scoped corrections."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
if not OUT.is_relative_to(ROOT):
    raise RuntimeError("Evidence directory must remain inside workspace")
env = os.environ.copy()
env.pop("PYTHONPATH", None)
runs = []


def run(name, cwd, args, expected_tests=None):
    command = [sys.executable, "-B", "-X", "utf8", *args]
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")
    for suffix, value in (("stdout", result.stdout), ("stderr", result.stderr)):
        with (OUT / f"{name}.{suffix}.txt").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
    row = {"name": name, "cwd": str(cwd), "command": command, "exit_code": result.returncode}
    if expected_tests is not None:
        match = re.search(r"Ran (\d+) tests", result.stderr)
        row["tests_executed"] = int(match[1]) if match else 0
        if row["tests_executed"] != expected_tests or not result.stderr.rstrip().endswith("OK"):
            raise RuntimeError(name + ": test discovery/result mismatch")
    runs.append(row)
    print(name, "exit=" + str(result.returncode), flush=True)
    if result.returncode:
        raise RuntimeError(name + " failed; preserve logs")
    return result.stdout


for relative in (
    "CEAV_M1_MANUSCRIPT_V0_3.md", "CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md",
    "CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md", "verification/manuscript_correction_checks.py",
    "verification/dual_boundary_oracle.py", "verification/independent_t3_t5_review.py",
    "verification/manuscript_editorial_audit.py", "tests/test_dual_boundary.py",
):
    target = OUT / "corrected-inputs" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write((ROOT / relative).read_bytes())

run("root-metrics", ROOT, ["-m", "verification.manuscript_editorial_audit"])
independent = json.loads(run("root-independent", ROOT, ["-m", "verification.independent_t3_t5_review"]))
run("root-focused", ROOT, ["-m", "unittest", "tests.test_dual_boundary", "-v"], 10)
run("root-focused-optimized", ROOT, ["-O", "-m", "unittest", "tests.test_dual_boundary", "-v"], 10)
correction = json.loads(run("root-correction", ROOT, ["-m", "verification.manuscript_correction_checks"]))
run("root-correction-optimized", ROOT, ["-O", "-m", "verification.manuscript_correction_checks"])

# The temporary package is contained in this workspace; its commands cannot
# resolve the parent checkout through cwd or PYTHONPATH.
with tempfile.TemporaryDirectory(prefix="standalone-", dir=OUT) as temporary:
    standalone = Path(temporary) / "review-package"
    shutil.copytree(ROOT / "review-package", standalone, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    run("package-origins", standalone, ["-c", "from pathlib import Path; import verification.dual_boundary as d; import tests.test_dual_boundary as t; root=Path.cwd(); print(d.__file__); print(t.__file__); assert Path(d.__file__).is_relative_to(root); assert Path(t.__file__).is_relative_to(root)"])
    run("package-metrics", standalone, ["-m", "verification.manuscript_editorial_audit"])
    run("package-independent", standalone, ["-m", "verification.independent_t3_t5_review"])
    run("package-focused", standalone, ["-m", "unittest", "tests.test_dual_boundary", "-v"], 10)
    run("package-correction", standalone, ["-m", "verification.manuscript_correction_checks"])
    run("package-summary", standalone, ["-m", "verification.review_summary"])

before = json.loads((OUT / "before.json").read_text(encoding="utf-8"))
changed = [p for p, digest in before["protected_raw_sha256"].items()
           if sha256((ROOT / p).read_bytes()).hexdigest() != digest]
if changed:
    raise RuntimeError("Historical/source bytes changed: " + str(changed))
manifest = {"utc": datetime.now(timezone.utc).isoformat(), "baseline_commit": before["baseline_commit"],
            "python": sys.version, "runs": runs, "protected_files_unchanged": len(before["protected_raw_sha256"]),
            "independent_audit": independent["T5"]["independent_audit"],
            "correction_checks": correction["checks"], "local_boundary_cases": len(correction["boundary_cases"]),
            "root_package_synchronized": correction["root_package_synchronized"],
            "scope": "limited manuscript corrections; no certificate regeneration or equilibrium expansion"}
with (OUT / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, indent=2)
    stream.write("\n")
print(json.dumps({"commands": len(runs), "all_exit_zero": True, "checks": correction["checks"],
                  "protected_files_unchanged": manifest["protected_files_unchanged"]}), flush=True)
