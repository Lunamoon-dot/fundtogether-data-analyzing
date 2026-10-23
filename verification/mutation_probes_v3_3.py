"""V3.3 IPW mutation probes in isolated copies only."""
import argparse, difflib, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ceav_m1 import V33_MODEL_VERSION
from ceav_m1.output import finish_run,new_run,sha256,source_files,write_json

PROBES={
 "IPW-M01":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T06_expected_anchor_and_audit_cost_match_oracle"],"target":"IPW denominator is retained","edits":[("ceav_m1/evaluate.py","state.probability * config.anchor_weight * config.anchor_weight / audit_probability","state.probability * config.anchor_weight * config.anchor_weight")]},
 "IPW-M02":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T02_zero_report_probability_is_rejected"],"target":"q0 and q1 must be strictly positive","edits":[("ceav_m1/model.py","if not 0 < value <= 1:","if not 0 <= value <= 1:")]},
 "IPW-M03":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T03_ipw_cap_is_checked_against_shared_budget"],"target":"IPW worst-case cap uses q_min","edits":[("ceav_m1/model.py","3 * config.anchor_weight / min(config.audit_probability_by_report)","3 * config.anchor_weight")]},
 "IPW-M04":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T06_expected_anchor_and_audit_cost_match_oracle"],"target":"audit operating cost remains q-weighted","edits":[("ceav_m1/evaluate.py","sum(audit_exposure) * config.audit_cost_per_audit","sum(audit_exposure) * config.anchor_weight")]},
 "IPW-M05":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T06_expected_anchor_and_audit_cost_match_oracle"],"target":"shared T drives covariance matrix","edits":[("ceav_m1/evaluate.py","if i == j else config.anchor_weight * config.anchor_weight","if i == j else config.anchor_weight * config.anchor_weight / audit_probability")]},
 "IPW-M06":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T08_failure_witness_reconstructs_utility_exactly"],"target":"witness decomposes utility gain","edits":[("ceav_m1/best_response.py","delta_anchor_reward = new_option[\"anchor_reward\"] - candidate_payoff.get(\"anchor_reward\", F(0))","delta_anchor_reward = F(0)")]},
 "IPW-M07":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T10_study_rejects_non_q_policy_override"],"target":"study policy allowlist is q-only","edits":[("ceav_m1/ipw.py","if not isinstance(overrides, dict) or set(overrides) != set(POLICY_PATHS):","if False:")]},
 "IPW-M08":{"tests":["tests.test_v3_3.V33IPWTests.test_IPW_T03_ipw_cap_is_checked_against_shared_budget"],"target":"budget is not silently inflated","edits":[("ceav_m1/model.py","if cap > config.reward_budget:","if cap > config.reward_budget * 2:")]},
}

def copy_workspace(dest):
    for d in ("ceav_m1","tests","configs","scenarios","datasets","verification","spec_history","web"):
        src=ROOT/d
        if src.exists(): shutil.copytree(src,dest/d,ignore=shutil.ignore_patterns("__pycache__"))

def run(out,ids):
    out=Path(out).resolve(); manifest=new_run(out,"v3_3_mutations",request={"ids":ids,"scope":"test-only temporary copies"},model_version=V33_MODEL_VERSION)
    baseline_hashes={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()) for p in source_files()}
    tests=sorted({t for name in ids for t in PROBES[name]["tests"]})
    baseline=subprocess.run([sys.executable,"-B","-m","unittest",*tests,"-v"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
    (out/"baseline_log.txt").write_text(baseline.stdout+baseline.stderr,encoding="utf-8")
    if baseline.returncode: raise ValueError("V3.3 mutation baseline failed")
    records=[]
    for name in ids:
        probe=PROBES[name]; folder=out/name; folder.mkdir(); mutant=folder/"workspace"; mutant.mkdir(); copy_workspace(mutant); patches=[]
        for path,before,after in probe["edits"]:
            file=mutant/path; old=file.read_text(encoding="utf-8")
            if old.count(before)!=1: raise ValueError(f"{name}: mutation anchor count for {path} is {old.count(before)}")
            changed=old.replace(before,after,1); patches.extend(difflib.unified_diff(old.splitlines(keepends=True),changed.splitlines(keepends=True),fromfile=path,tofile=path)); file.write_text(changed,encoding="utf-8",newline="\n")
        patch="".join(patches); (folder/"mutation.patch").write_text(patch,encoding="utf-8",newline="\n")
        command=[sys.executable,"-B","-m","unittest",*probe["tests"],"-v"]
        process=subprocess.run(command,cwd=mutant,capture_output=True,text=True,encoding="utf-8",errors="replace")
        log=process.stdout+process.stderr; (folder/"test_log.txt").write_text(log,encoding="utf-8",newline="\n")
        invalid=any(marker in log for marker in ("SyntaxError","ImportError:","ModuleNotFoundError","Ran 0 tests"))
        status="invalid" if invalid else ("killed" if process.returncode else "survived")
        records.append({"mutation_id":name,"status":status,"expected_failure":probe["target"],"test_ids":probe["tests"],"argv":command,"exit_code":process.returncode,"patch_sha256":sha256(patch.encode()),"assertion_log":f"{name}/test_log.txt"})
        print(name,status,flush=True)
    after_hashes={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()) for p in source_files()}
    if baseline_hashes!=after_hashes: raise ValueError("Production changed during mutation probes")
    write_json(out/"mutation_results.json",{"baseline_exit_code":baseline.returncode,"production_bytes_unchanged":True,"records":records})
    (out/"report.md").write_text("# CEAV-M1 V3.3 — Mutation probes\n\n"+"\n".join(f"- {r['mutation_id']}: {r['status']} — {r['expected_failure']}" for r in records)+"\n",encoding="utf-8",newline="\n")
    passed=all(r["status"]=="killed" for r in records); finish_run(out,manifest,"succeeded" if passed else "failed"); return passed

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); ap.add_argument("--ids",nargs="+",choices=list(PROBES),default=list(PROBES)); a=ap.parse_args(); raise SystemExit(0 if run(a.out,a.ids) else 1)
