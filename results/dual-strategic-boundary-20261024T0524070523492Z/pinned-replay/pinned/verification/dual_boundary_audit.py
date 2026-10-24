"""Independent certificate completeness audit using the potential-state oracle.

The expected intervals use separately written bound collection, not the
analyzer's solver, constraint generator, cell builder or metric aggregator.
"""

from fractions import Fraction as F
from itertools import product

from verification import dual_boundary_oracle as oracle


def audit(subject):
    checks = 0
    def check(condition, label):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    actions = oracle.ACTIONS
    profiles = tuple(product(actions,repeat=3))
    gates = {"fa":F(1,5),"fr":F(1,4),"wrong_payout":F(3,20),"cash":F(4),"exposure":F(1,2),"reserve":F(6)}
    vectors = ((0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,1))
    for mechanism in ("selective","uniform"):
        expected = {(z,p):oracle.evaluate(z,p,mechanism) for z,p in product((0,1),profiles)}
        table = subject.build_table(mechanism)
        check(table == expected, mechanism+" all864/2 independent branch metrics")
        for vector in vectors:
            branch = []
            for z in (0,1):
                candidates = {}
                for p in profiles:
                    lowers,uppers = [],[]
                    possible = True
                    for i,a in product(range(3),actions):
                        q = tuple(a if j==i else p[j] for j in range(3))
                        c = expected[z,p]["utility"][i]-expected[z,q]["utility"][i]
                        slope = vector[i]*(expected[z,p]["release"]-expected[z,q]["release"])
                        if slope > 0:
                            lowers.append(-c/slope)
                        elif slope < 0:
                            uppers.append(-c/slope)
                        elif c < 0:
                            possible = False
                    lo = max(lowers) if lowers else None
                    hi = min(uppers) if uppers else None
                    if possible and (lo is None or hi is None or lo<=hi):
                        candidates[p] = (lo,hi)
                    actual = subject.solve_constraints(subject.constraints(table,z,p,vector))
                    check(actual == candidates.get(p), "independent candidate interval "+str((mechanism,vector,z,p)))
                branch.append(candidates)
            complete = {}
            for p0,p1 in product(branch[0],branch[1]):
                lo = [v for v in (branch[0][p0][0],branch[1][p1][0]) if v is not None]
                hi = [v for v in (branch[0][p0][1],branch[1][p1][1]) if v is not None]
                lo,hi = (max(lo) if lo else None),(min(hi) if hi else None)
                if lo is None or hi is None or lo<=hi:
                    complete[p0,p1] = (lo,hi)
            es = subject.full_equilibria(table,vector)
            check({e["profile"]:e["interval"] for e in es} == complete,"independent full stationary product")
            oracle_metrics = {}
            for e in es:
                l,r = (expected[z,e["profile"][z]] for z in (0,1))
                metric = {"fa":l["fa_joint"]+r["fa_joint"],"fr":l["fr_joint"]+r["fr_joint"],"reserve":F(6)}
                metric.update({k:(l[k]+r[k])/2 for k in ("wrong_payout","loss","cash","exposure","reward","release")})
                oracle_metrics[e["id"]] = metric
                check(metric == e["metrics"],"full metric weights")
                check({k:metric[k]<=cap for k,cap in gates.items()} == e["gates"],"frozen gates")
            endpoints = sorted({b for pair in complete.values() for b in pair if b is not None})
            partition = subject.cells(es)
            check([(c["lo"],c["kind"]) for c in partition if c["kind"]=="point"] == [(b,"point") for b in endpoints],"all exact endpoints retained")
            check(len(partition) == 2*len(endpoints)+1,"open cells and tails retained")
            for cell in partition:
                b = cell["representative"]
                direct = []
                for z in (0,1):
                    stable = []
                    for p in profiles:
                        utilities = [expected[z,p]["utility"][i]+b*vector[i]*expected[z,p]["release"] for i in range(3)]
                        if all(utilities[i] >= expected[z,tuple(a if j==i else p[j] for j in range(3))]["utility"][i]
                               +b*vector[i]*expected[z,tuple(a if j==i else p[j] for j in range(3))]["release"]
                               for i,a in product(range(3),actions)):
                            stable.append(p)
                    direct.append(stable)
                actual = {es[i]["profile"] for i in cell["equilibrium_ids"]}
                check(actual == set(product(*direct)),"direct best responses in exact cell")
                check(cell["pure_count"] == len(actual),"pure count")
                check(cell["all_gates_pass"] == (bool(actual) and all(es[i]["all_gates_pass"] for i in cell["equilibrium_ids"])),"empty pure set never passes")
                for key in ("fa","fr","wrong_payout","loss","cash","exposure","reserve"):
                    if actual:
                        maximum = max(oracle_metrics[i][key] for i in cell["equilibrium_ids"])
                        witnesses = [i for i in cell["equilibrium_ids"] if oracle_metrics[i][key] == maximum]
                        check(cell["worst"][key] == {"value":maximum,"witnesses":witnesses},"independent worst metric and witness IDs: "+key)
                    else:
                        check(not cell["worst"],"no metrics without pure existence")
                gains = []
                for z,i,a in product((0,1),range(3),actions):
                    if a == "H01":
                        continue
                    p = ("H01",)*3
                    q = tuple(a if j==i else "H01" for j in range(3))
                    gains.append(expected[z,p]["utility"][i]-expected[z,q]["utility"][i]
                                 +b*vector[i]*(expected[z,p]["release"]-expected[z,q]["release"]))
                status = "NOT_EQUILIBRIUM" if min(gains)<0 else "WEAK_WITH_TIES" if min(gains)==0 else "STRICT"
                check(subject.local_status(table,vector,b) == status,"independent All-H01 status")
    return {"checks":checks,"oracle_branch_profiles":864,"branch_candidates":4320,
            "full_profiles_covered":466560,"all_real_b":True,"status":"PASS"}
