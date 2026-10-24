"""Exact affine boundary study for ONE frozen dual-purpose research point.

No policy optimization, engine integration, floating point, or version change.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
PROFILES = tuple(product(ACTIONS, repeat=3))
HIGH = ("H01",)*3
METRICS = ("fa", "fr", "wrong_payout", "loss", "cash", "exposure", "reserve")


def load_config():
    def convert(x):
        if isinstance(x, dict):
            return {k: convert(v) for k,v in x.items()}
        if isinstance(x, list):
            return tuple(convert(v) for v in x)
        if isinstance(x, str):
            try:
                return F(x)
            except ValueError:
                pass
        return x
    return convert(json.loads((ROOT/"configs/dual_boundary.json").read_text(encoding="utf-8")))


def serial(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)):
        return [serial(v) for v in x]
    return x


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def branch_metrics(c, z, profile, mechanism):
    """Marginalize reports directly; independent oracle retains potential X."""
    result = {k: F(0) for k in ("fa_joint", "fr_joint", "wrong_payout", "loss",
                                "release", "exposure", "reward", "cash")}
    payments = [F(0)]*3
    for y, reports in product((0,1), product((0,1), repeat=3)):
        mass = c["public_accuracy"] if y == z else 1-c["public_accuracy"]
        for action, r in zip(profile, reports):
            if action in ("L0", "L1", "H00", "H11"):
                mass *= int(r == int(action[-1]))
            else:
                accurate = int(action == "H01")
                p = c["private_accuracy"] if accurate else 1-c["private_accuracy"]
                mass *= p if r == y else 1-p
        if not mass:
            continue
        d = c["uniform_d"] if mechanism == "uniform" else c["t"]*int(z == 0 and sum(reports) == 2)
        union = c["a"]+(1-c["a"])*d
        k = sum(reports)
        g0 = c["g0_by_z_and_report_sum"][z][k]
        g1 = c["g1_by_z_and_report_sum"][z][k]
        audit_release = sum((c["audit_accuracy"] if t == y else 1-c["audit_accuracy"])*g1[t] for t in (0,1))
        release = (1-union)*g0+union*audit_release
        result["release"] += mass*release
        result["fa_joint"] += mass*(1-y)*release
        result["fr_joint"] += mass*y*(1-release)
        result["exposure"] += mass*union
        for i,r in enumerate(reports):
            match = c["audit_accuracy"] if r == y else 1-c["audit_accuracy"]
            payments[i] += mass*(c["f"]+c["mu"]*c["a"]*match)
    result["utility"] = tuple(p-c["effort_cost"]*int(a[0] == "H") for p,a in zip(payments,profile))
    result["reward"] = sum(payments)
    result["cash"] = result["reward"]+c["kappa"]*result["exposure"]+c["operating_cost"]
    result["wrong_payout"] = result["fa_joint"]*c["payout_value"]
    result["loss"] = c["c_fa"]*result["fa_joint"]+c["c_fr"]*result["fr_joint"]
    return result


def build_table(mechanism):
    if mechanism not in ("selective", "uniform"):
        raise ValueError("only the two frozen mechanisms")
    c = load_config()
    return {(z,p): branch_metrics(c,z,p,mechanism) for z,p in product((0,1),PROFILES)}


def local_boundaries(table):
    rows = []
    for z,i,action in product((0,1),range(3),ACTIONS):
        changed = list(HIGH)
        changed[i] = action
        base, dev = table[z,HIGH], table[z,tuple(changed)]
        gap = base["utility"][i]-dev["utility"][i]
        slope = dev["release"]-base["release"]
        rows.append({"z":z,"judge":i,"action":action,"neutral_gap":gap,
                     "slope":slope,"breakpoint":gap/slope if slope else None})
    return rows


def pairwise_indifferences(table):
    result = []
    for z,i in product((0,1),range(3)):
        for j,left in enumerate(ACTIONS):
            for right in ACTIONS[j+1:]:
                p,q = list(HIGH),list(HIGH)
                p[i],q[i] = left,right
                l,r = table[z,tuple(p)],table[z,tuple(q)]
                intercept = l["utility"][i]-r["utility"][i]
                slope = l["release"]-r["release"]
                result.append({"z":z,"judge":i,"left":left,"right":right,
                               "intercept_left_minus_right":intercept,"slope_left_minus_right":slope,
                               "breakpoint":-intercept/slope if slope else None,
                               "identical_all_b":intercept == 0 and slope == 0})
    return result


def constraints(table, z, profile, vector):
    base = table[z,profile]
    for i,action in product(range(3),ACTIONS):
        changed = list(profile)
        changed[i] = action
        dev = table[z,tuple(changed)]
        yield (base["utility"][i]-dev["utility"][i],
               vector[i]*(base["release"]-dev["release"]))


def solve_constraints(inequalities):
    """Intersect c+b*s >= 0, with None denoting the appropriate infinity."""
    lo = hi = None
    for intercept,slope in inequalities:
        if slope == 0:
            if intercept < 0:
                return None
        elif slope > 0:
            bound = -intercept/slope
            lo = bound if lo is None else max(lo,bound)
        else:
            bound = -intercept/slope
            hi = bound if hi is None else min(hi,bound)
    return None if lo is not None and hi is not None and lo > hi else (lo,hi)


def contains(interval, b):
    lo,hi = interval
    return (lo is None or b >= lo) and (hi is None or b <= hi)


def combine_metrics(table, profile):
    left,right = (table[z,profile[z]] for z in (0,1))
    # P(Z=0)=P(Z=1)=P(Y=0)=P(Y=1)=1/2 at the frozen point.
    m = {"fa":left["fa_joint"]+right["fa_joint"],
         "fr":left["fr_joint"]+right["fr_joint"]}
    for key in ("wrong_payout", "loss", "cash", "exposure", "reward", "release"):
        m[key] = (left[key]+right[key])/2
    m["reserve"] = F(6)
    return m


def full_equilibria(table, vector):
    branches = []
    for z in (0,1):
        equilibria = []
        for p in PROFILES:
            interval = solve_constraints(constraints(table,z,p,vector))
            if interval is not None:
                equilibria.append((p,interval))
        branches.append(equilibria)
    result = []
    for (p0,i0),(p1,i1) in product(*branches):
        inequalities = []
        for lo,hi in (i0,i1):
            if lo is not None:
                inequalities.append((-lo,F(1)))
            if hi is not None:
                inequalities.append((hi,F(-1)))
        interval = solve_constraints(inequalities)
        if interval is not None:
            profile = (p0,p1)
            metrics = combine_metrics(table,profile)
            gates = {k: metrics[k] <= v for k,v in load_config()["gates"].items()}
            result.append({"id":len(result),"profile":profile,"interval":interval,
                           "metrics":metrics,"gates":gates,"all_gates_pass":all(gates.values())})
    return result


def cells(equilibria):
    endpoints = sorted({b for e in equilibria for b in e["interval"] if b is not None})
    segments = []
    prev = None
    for point in endpoints:
        segments.append(("open",prev,point, point-1 if prev is None else (prev+point)/2))
        segments.append(("point",point,point,point))
        prev = point
    segments.append(("open",prev,None,F(0) if prev is None else prev+1))
    result = []
    for kind,lo,hi,b in segments:
        active = [e for e in equilibria if contains(e["interval"],b)]
        worst = {}
        for key in METRICS:
            if active:
                value = max(e["metrics"][key] for e in active)
                worst[key] = {"value":value,"witnesses":[e["id"] for e in active if e["metrics"][key] == value]}
        result.append({"kind":kind,"lo":lo,"hi":hi,"representative":b,
                       "pure_count":len(active),"equilibrium_ids":[e["id"] for e in active],
                       "existence":"PURE_EXISTS" if active else "NO_PURE_EQUILIBRIUM",
                       "all_gates_pass":bool(active) and all(e["all_gates_pass"] for e in active),
                       "bad_equilibrium_ids":[e["id"] for e in active if not e["all_gates_pass"]],"worst":worst})
    return result


def local_status(table, vector, b):
    inequalities = [pair for z in (0,1) for pair in constraints(table,z,HIGH,vector)]
    if any(c+b*s < 0 for c,s in inequalities):
        return "NOT_EQUILIBRIUM"
    # Self deviations are exactly zero; evaluate the five real alternatives.
    strict = all(c+b*s > 0 for z in (0,1)
                 for j,(c,s) in enumerate(constraints(table,z,HIGH,vector)) if ACTIONS[j%6] != "H01")
    return "STRICT" if strict else "WEAK_WITH_TIES"


def safe_component(partition):
    """Maximal all-gates-pass connected component containing neutral b=0."""
    require(all(c["all_gates_pass"] for c in partition if c["representative"] == 0
                or c["kind"] == "open" and (c["lo"] is None or c["lo"] < 0)
                and (c["hi"] is None or c["hi"] > 0)), "neutral component must pass")
    left = [c for c in partition if c["representative"] < 0 and not c["all_gates_pass"]]
    right = [c for c in partition if c["representative"] > 0 and not c["all_gates_pass"]]
    lo = left[-1]["hi"] if left else None
    hi = right[0]["lo"] if right else None
    def closed(bound):
        return bound is not None and next(c["all_gates_pass"] for c in partition if c["kind"] == "point" and c["lo"] == bound)
    return {"lo":lo,"hi":hi,"lo_included":closed(lo),"hi_included":closed(hi)}


def study():
    config = load_config()
    certificate = {"study":config["study"],"status":"VERIFIED_IN_DECLARED_PURE_CLASS",
                   "verdict":"STRATEGIC_FAILURE", "configuration":config,
                   "scope":{"branch_profiles":216,"full_profiles_per_scenario":46656,
                            "deviations_per_branch_candidate":18,"b_domain":"all real",
                            "mechanisms":2,"scenarios_per_mechanism":5,
                            "completeness":"exact closed half-line intersections and branch product; not mixed equilibrium"},
                   "mechanisms":{}}
    for mechanism in ("selective","uniform"):
        table = build_table(mechanism)
        data = {"local_deviations":local_boundaries(table),
                "all_pairwise_indifferences_against_h01_peers":pairwise_indifferences(table),
                "branch_metrics":[{"z":z,"profile":p,"metrics":table[z,p]} for z,p in product((0,1),PROFILES)],
                "scenarios":{}}
        for name,vector in config["scenarios"].items():
            equilibria = full_equilibria(table,vector)
            partition = cells(equilibria)
            for cell in partition:
                cell["all_h01_status"] = local_status(table,vector,cell["representative"])
            data["scenarios"][name] = {"b_vector_multiplier":vector,"equilibria":equilibria,"cells":partition}
            data["scenarios"][name]["safe_component_containing_zero"] = safe_component(partition)
            data["scenarios"][name]["pure_exists_all_real_b"] = all(cell["pure_count"] > 0 for cell in partition)
            data["scenarios"][name]["all_h01_closed_equilibrium_interval"] = solve_constraints(
                pair for z in (0,1) for pair in constraints(table,z,HIGH,vector))
        certificate["mechanisms"][mechanism] = data
    failure = certificate["mechanisms"]["selective"]["scenarios"]["symmetric"]
    at_tenth = [e for e in failure["equilibria"] if contains(e["interval"],F(1,10))]
    require(len(at_tenth) == 4 and sum(not e["all_gates_pass"] for e in at_tenth) == 3,
            "verdict requires computed strategic failure at b=1/10")
    return certificate


def label_cell(cell):
    def n(x,negative=False):
        return ("-inf" if negative else "+inf") if x is None else str(x)
    return "{"+str(cell["lo"])+"}" if cell["kind"] == "point" else "("+n(cell["lo"],True)+", "+n(cell["hi"])+")"


def render_report(cert):
    lines = ["# Exact pure equilibrium boundary: complete interval tables", "",
             "VERIFIED: all real b in the frozen six-action stationary class. Verdict: **STRATEGIC_FAILURE**.", "",
             "All-H01 local stability and all-equilibrium gate safety are different. Every row below is an exact arrangement cell, not a floating-point sample. At endpoints all ties are retained. NONE means no pure equilibrium; that row fails robustness.", "",
             "Metric maxima can have different witnesses. Full action profiles, their closed equilibrium intervals, all gates, utility/release tables and every maximizing witness ID are in certificate.json. IDs are local to each mechanism/scenario. b has utility units with reward coefficient mu=2.", ""]
    for mechanism,data in cert["mechanisms"].items():
        lines += ["## "+mechanism, "", "### Local deviations against frozen All-H01", "",
                  "All three Judge positions have the following identical values; certificate retains all 36 rows. Deviation gain = -gap + b*slope. A nonzero slope crosses at gap/slope; a crossing need not be the first optimal deviation.", "",
                  "|Z|Action|Neutral gap|Release slope|Indifference b|", "|---|---|---|---|---|"]
        for r in data["local_deviations"]:
            if r["judge"] == 0:
                lines.append(f'|{r["z"]}|{r["action"]}|{r["neutral_gap"]}|{r["slope"]}|{r["breakpoint"]}|')
        for name,scenario in data["scenarios"].items():
            lines += ["", "### "+name+" : b_i = b * "+str(scenario["b_vector_multiplier"]), "",
                      "All-gates-safe component containing zero: "+str(scenario["safe_component_containing_zero"])+". A None endpoint means infinity. Pure existence for all real b: "+str(scenario["pure_exists_all_real_b"])+".", "",
                      "|b cell|All-H01|Pure count|All gates|Worst FA|Worst FR|Wrong payout|Decision loss|Cash|Union exposure|Reserve|Bad IDs|",
                      "|---|---|---:|---|---|---|---|---|---|---|---|---|"]
            for cell in scenario["cells"]:
                vals = [str(cell["worst"][k]["value"]) if cell["worst"] else "NONE" for k in METRICS]
                lines.append("|"+"|".join([label_cell(cell),cell["all_h01_status"],str(cell["pure_count"]),str(cell["all_gates_pass"]),*vals,",".join(map(str,cell["bad_equilibrium_ids"]))])+"|")
            lines += ["", "Closed full-equilibrium intervals and action witnesses (Z=0 / Z=1):", "",
                      "|ID|Z=0 actions|Z=1 actions|Closed b interval|Failed gates|", "|---|---|---|---|---|"]
            for e in scenario["equilibria"]:
                lo,hi=e["interval"]
                lines.append(f'|{e["id"]}|{", ".join(e["profile"][0])}|{", ".join(e["profile"][1])}|[{lo if lo is not None else "-inf"}, {hi if hi is not None else "+inf"}]|{", ".join(k for k,v in e["gates"].items() if not v) or "none"}|')
    return "\n".join(lines)+"\n"


def write_run(out):
    out.mkdir(parents=True,exist_ok=False)
    cert = study()
    (out/"certificate.json").write_text(json.dumps(serial(cert),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"interval-report.md").write_text(render_report(cert),encoding="utf-8")
    paths = ["configs/dual_boundary.json","CEAV_M1_DUAL_BOUNDARY_PROTOCOL.md",
             "verification/dual_boundary.py","verification/dual_boundary_oracle.py","tests/test_dual_boundary.py",
             "tests/__init__.py",
             "CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md"]
    for optional in ("CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md","verification/DUAL_BOUNDARY_INDEPENDENT_REVIEW.md","verification/dual_boundary_mutations.py","verification/dual_boundary_audit.py","verification/dual_boundary_evidence.py"):
        if (ROOT/optional).exists():
            paths.append(optional)
    hashes = {}
    for path in paths:
        data = (ROOT/path).read_bytes()
        hashes[path] = sha256(data).hexdigest()
        dest = out/"pinned"/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
    outputs = {name:sha256((out/name).read_bytes()).hexdigest() for name in ("certificate.json","interval-report.md")}
    (out/"manifest.json").write_text(json.dumps({"utc":datetime.now(timezone.utc).isoformat(),
        "source_raw_sha256":hashes,"outputs_raw_sha256":outputs,
        "config_semantic_sha256":sha256(json.dumps(serial(load_config()),sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "command":"python -X utf8 verification/dual_boundary.py --out NEW_DIRECTORY",
        "frozen_parent_commit":load_config()["parent_commit"],"no_historical_mutation":True},indent=2)+"\n",encoding="utf-8")
    return cert


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"out":str(args.out),"verdict":result["verdict"],"scenarios":10}))
