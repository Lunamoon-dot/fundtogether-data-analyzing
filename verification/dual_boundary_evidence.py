"""Fresh immutable evidence bundle; run as a module from the repository root."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from verification import dual_boundary as subject
from verification.dual_boundary_audit import audit
from verification.dual_boundary_mutations import run_probes


def run(out):
    out = out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    checks = []
    for name,flags,modules in (
        ("focused",[],["tests.test_dual_boundary"]),
        ("optimized",["-O"],["tests.test_dual_boundary"]),
        ("historical-v6",[],["tests.test_v6_feasibility","tests.test_v6_regressions","tests.test_v6_mutations","tests.test_v6_stop_certificates"]),
    ):
        command = [sys.executable,"-X","utf8",*flags,"-m","unittest",*modules,"-v"]
        completed = subprocess.run(command,cwd=subject.ROOT,capture_output=True,text=True,encoding="utf-8")
        text = completed.stdout+completed.stderr
        (out/(name+".log")).write_text(text,encoding="utf-8")
        count = 10 if name != "historical-v6" else 24
        subject.require(completed.returncode == 0 and f"Ran {count} tests" in text and "\nOK\n" in text and "skipped=" not in text,
                        "tests unavailable, skipped or failed: "+name)
        checks.append({"name":name,"tests_executed":count,"exit_code":completed.returncode,"command":command})
        print(name+": "+str(count)+" tests PASS",flush=True)
    independent = audit(subject)
    (out/"independent-audit.json").write_text(json.dumps(independent,indent=2)+"\n",encoding="utf-8")
    mutations = run_probes()
    (out/"mutation-probes.json").write_text(json.dumps(mutations,indent=2)+"\n",encoding="utf-8")
    subject.write_run(out/"analysis")
    pinned = out/"analysis/pinned"
    command = [sys.executable,"-X","utf8",str(pinned/"verification/dual_boundary.py"),"--out",str(out/"pinned-replay")]
    replay = subprocess.run(command,cwd=pinned,capture_output=True,text=True,encoding="utf-8")
    (out/"pinned-replay.log").write_text(replay.stdout+replay.stderr,encoding="utf-8")
    subject.require(replay.returncode == 0,"pinned replay failed")
    for name in ("certificate.json","interval-report.md"):
        subject.require((out/"analysis"/name).read_bytes() == (out/"pinned-replay"/name).read_bytes(),"pinned replay differs: "+name)
    # Refusal is tested against the completed output: no existing bytes change.
    before = (out/"analysis/certificate.json").read_bytes()
    try:
        subject.write_run(out/"analysis")
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing analysis was overwritten")
    subject.require(before == (out/"analysis/certificate.json").read_bytes(),"refusal changed certificate")
    # Historical manifests and their immutable outputs are checked, not rewritten.
    history = []
    for path in (subject.ROOT/"results").glob("v6-*/manifest.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        history.append({"path":str(path.relative_to(subject.ROOT)),"raw_sha256":sha256(path.read_bytes()).hexdigest(),"role":"historical identity only"})
    tracked = subprocess.check_output(["git","diff","--name-only","HEAD"],cwd=subject.ROOT,text=True).splitlines()
    subject.require(not tracked,"pre-existing tracked research files changed: "+str(tracked))
    identity = {"historical_manifests":history,"tracked_diff_from_parent":tracked,"pinned_certificate_and_report_identical":True,"existing_output_refused":True}
    (out/"identity-and-replay.json").write_text(json.dumps(identity,indent=2)+"\n",encoding="utf-8")
    files = {str(p.relative_to(out)).replace("\\","/"):sha256(p.read_bytes()).hexdigest()
             for p in sorted(out.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    manifest = {"utc":datetime.now(timezone.utc).isoformat(),"status":"VERIFIED","verdict":"STRATEGIC_FAILURE",
                "parent_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=subject.ROOT,text=True).strip(),
                "command":"python -X utf8 -m verification.dual_boundary_evidence --out NEW_DIRECTORY",
                "test_runs":checks,"independent_audit":independent,"mutants_detected":len(mutations),
                "raw_sha256":files,"source_hash_manifest":"analysis/manifest.json",
                "history_identity_scope":"all tracked parent bytes unchanged; V6 manifest identities recorded; historical correctness separately covered by 24 regressions"}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"out":str(out),"verdict":"STRATEGIC_FAILURE","independent_checks":independent["checks"],"mutants_detected":len(mutations)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    run(parser.parse_args().out)
