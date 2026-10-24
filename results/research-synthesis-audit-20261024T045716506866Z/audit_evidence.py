"""Cross-check new paper arithmetic against historical oracles and identities."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from verification import oracle_v6_feasibility as old_v6
from verification import oracle_v5_1_quality as old_v51
from verification import research_synthesis_checks as current


if __name__ == "__main__":
    result = current.run_checks()
    study = current.fractions(json.loads((ROOT/"configs/v6/rave_phase1.json").read_text()))
    assert subprocess.check_output(["git","show","6fb0f4367187cc9eeefb180d4336f237275e38c5:configs/v6/rave_phase1.json"],cwd=ROOT) == (ROOT/"configs/v6/rave_phase1.json").read_bytes()
    fx = study["fixtures"][1]
    table = old_v6.decision_table(fx, (F(2),F(1)))
    comparisons = []
    for route, e in (("dual_selective",None),("dual_uniform",F(2557,6250))):
        audit = {(z,r): F(2,5)+F(1,10)*int(z==0 and sum(r)==2) if e is None else e
                 for z,r in product((0,1),tuple(product((0,1),repeat=3)))}
        policy = dict(audit=audit,f=F(0),mu=F(0),budget=F(6),kappa=F(1,4),
                      operating_cost=F(0),payout_value=F(1),exposure_limit=F(1,2),c_fa=F(2),c_fr=F(1))
        metrics = old_v6.evaluate(fx,policy,table,current.HIGH)
        for a,b in (("fa","final_fa"),("fr","final_fr"),("loss","expected_decision_loss"),
                    ("wrong_payout_value","wrong_payout_value"),("exposure","audit_exposure")):
            assert result[route][a] == metrics[b], (route,a)
            comparisons.append(route+"/"+a)
    policy = old_v51.Policy("binary",F(0),F(2),F(2,5),kappa=F(0))
    original = old_v51.evaluate_profile("F51-02",policy,(("H01","H01"),)*3)
    assert original["expected_reward_total"] == result["dual_selective"]["reward"]
    assert all(old_v51.best_response_options(old_v51._fixture("F51-02"),policy,i,z)["options"] == ("H01",)
               for i,z in product(range(3),(0,1)))
    dirs = [
        "v3-closeout-study-r2", "v31-robustness-study-release-02", "v32-report-sensitive-final-02",
        "v33-ipw-full-20261024T052707", "v4-research-closeout-20261023T2357325229450Z",
        "v4-1-minimal-screening-curated-20261024T011500", "v4-1-audit-cost-sensitivity-20261024T020000",
        "v5-feasibility-20261024T012908", "v5-1-quality-certificates-20261024T084411",
        "v6-rave-phase1-20261024T021148403371Z",
        "v6-closeout-20261024T021405861852Z/negative-certificates",
    ]
    identities = []
    for name in dirs:
        root = ROOT/"results"/name
        manifest = json.loads((root/"manifest.json").read_text())
        checks = 0
        for row in manifest.get("artifacts",[]):
            assert sha256((root/row["name"]).read_bytes()).hexdigest() == row["sha256"], (name,row["name"])
            checks += 1
        for file,digest in manifest.get("outputs",{}).items():
            assert sha256((root/file).read_bytes()).hexdigest() == digest, (name,file)
            checks += 1
        assert checks>0, name
        identities.append({"manifest":str(root.relative_to(ROOT)/"manifest.json"),
                           "sha256":sha256((root/"manifest.json").read_bytes()).hexdigest(),"artifact_checks":checks})
    output = {"status":"passed","historical_manifest_identities":identities,
              "cross_oracle_decision_comparisons":len(comparisons),"cross_oracle_payoff_and_six_branch_optima":"matched",
              "new_policy_grid":False,"new_design_points":1,"checks_in_new_standalone_calculation":result["checks"]}
    with (Path(__file__).parent/"cross-oracle-and-identity.json").open("x",encoding="utf-8") as stream:
        json.dump(output,stream,indent=2)
        stream.write("\n")
    print(json.dumps(output))
