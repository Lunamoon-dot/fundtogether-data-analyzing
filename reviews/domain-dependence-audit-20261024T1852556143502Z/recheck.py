"""Read-only research replay; write evidence only in this new audit directory."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
paths = [
    "AGENTS.md", "CEAV_M1_DOMAIN_DEPENDENCE_AUDIT.md",
    "CEAV_M1_MANUSCRIPT_V0_2.md", "CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md",
    "CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md",
    "CEAV_M1_NOVELTY_AUDIT_T3_T5.md", "CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md",
    "review-package/CLAIM_EVIDENCE_MAP.md", "review-package/KNOWN_LIMITATIONS.md",
    "review-package/docs/CEAV_M1_MANUSCRIPT_V0_2.md",
    "configs/dual_boundary.json", "review-package/configs/dual_boundary.json",
    "verification/dual_boundary.py", "verification/dual_boundary_oracle.py",
    "verification/dual_boundary_audit.py", "verification/independent_t3_t5_review.py",
    "verification/manuscript_editorial_audit.py", "tests/test_dual_boundary.py",
    "results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json",
    "review-package/frozen-boundary/certificate.json",
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


before = {p: digest(ROOT / p) for p in paths}
for p in paths:
    target = OUT / "inputs" / p
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write((ROOT / p).read_bytes())

commands = [
    ("independent", ROOT, ["-m", "verification.independent_t3_t5_review"]),
    ("metrics", ROOT, ["-m", "verification.manuscript_editorial_audit"]),
    ("focused", ROOT, ["-m", "unittest", "tests.test_dual_boundary", "-v"]),
    ("focused-optimized", ROOT, ["-O", "-m", "unittest", "tests.test_dual_boundary", "-v"]),
    ("package-metrics", ROOT / "review-package", ["-m", "verification.manuscript_editorial_audit"]),
    ("replay", ROOT, ["verification/dual_boundary.py", "--out", str(OUT / "replay")]),
]
runs = []
for name, cwd, args in commands:
    command = [sys.executable, "-X", "utf8", *args]
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    (OUT / (name + ".stdout.txt")).write_text(result.stdout, encoding="utf-8")
    (OUT / (name + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
    runs.append({"name": name, "cwd": str(cwd), "command": command, "exit_code": result.returncode})
    print(name, "exit_code=" + str(result.returncode), flush=True)

after = {p: digest(ROOT / p) for p in paths}
frozen = before["results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json"]
replay = digest(OUT / "replay/certificate.json")
manifest = {"audit_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
            "input_raw_sha256": before, "inputs_unchanged_during_checks": before == after,
            "runs": runs, "replay_raw_sha256": replay, "replay_matches_frozen": replay == frozen,
            "scope": "T3-T5 research replay, not full V1-V6 or browser acceptance"}
with (OUT / "manifest.json").open("x", encoding="utf-8") as stream:
    json.dump(manifest, stream, indent=2)
    stream.write("\n")
print(json.dumps({"runs": len(runs), "all_exit_zero": all(r["exit_code"] == 0 for r in runs),
                  "inputs_unchanged": before == after, "replay_matches_frozen": replay == frozen}))
if any(r["exit_code"] for r in runs) or before != after or replay != frozen:
    raise SystemExit(1)
