"""Named-instance exact arithmetic for the research memo; no model or grid.

Independent primitive-state/event sums; imports no CEAV evaluator/oracle.
The sole new design point was derived on paper before this file existed.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
HIGH = (("H01",)*3,)*2
CHECKS = 0


def require(condition, label):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(label)


def fractions(x):
    if isinstance(x, dict):
        return {k: fractions(v) for k, v in x.items()}
    if isinstance(x, list):
        return tuple(fractions(v) for v in x)
    if isinstance(x, str):
        try:
            return F(x)
        except ValueError:
            pass
    return x


def serial(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [serial(v) for v in x]
    return x


def primitive_rows(fixture):
    rows = []
    for y, z, xa, xb, xc, t in product((0, 1), repeat=6):
        mass = fixture["pi"] if y else 1-fixture["pi"]
        for bit, channel in zip((z, xa, xb, xc, t),
                                (fixture["public"], *fixture["private"], fixture["audit"])):
            p1 = channel[0] if y else 1-channel[1]
            mass *= p1 if bit else 1-p1
        rows.append((y, z, (xa, xb, xc), t, mass))
    require(sum(r[-1] for r in rows) == 1, "primitive normalization")
    return tuple(rows)


def frozen_decisions(rows):
    # Calibrated H01 report vector equals the three potential private signals.
    table = {}
    for z, r in product((0, 1), tuple(product((0, 1), repeat=3))):
        group = [row for row in rows if row[1:3] == (z, r)]
        mass = sum(row[-1] for row in group)
        y1 = sum(row[-1] for row in group if row[0] == 1)
        g0 = int(y1/mass >= F(2, 3))
        g1 = []
        after_loss = F(0)
        for t in (0, 1):
            sub = [row for row in group if row[3] == t]
            m = sum(row[-1] for row in sub)
            truth1 = sum(row[-1] for row in sub if row[0])
            g1.append(int(truth1/m >= F(2, 3)))
            after_loss += min(2*(m-truth1), truth1)/mass
        voi = min(2*(mass-y1), y1)/mass-after_loss
        require(voi >= 0, "conditional value of information")
        table[z, r] = {"g0": g0, "g1": tuple(g1), "mass": mass,
                       "posterior": y1/mass, "voi": voi}
    require(sum(v["mass"] for v in table.values()) == 1, "observation normalization")
    return table


def event_lottery(route, z, reports):
    # Selection reads only locked observables, before the loop uses T.
    if route.startswith("v6_"):
        q = F(len(set(reports)) != 1) if route == "v6_Q1" else F(z == 1)
        return ((0, 0, 1-q), (1, 1, q))
    a = F(2, 5)
    if route == "dual_selective":
        d = F(1, 6) if z == 0 and sum(reports) == 2 else F(0)
    elif route == "dual_uniform":
        d = F(19, 1250)
    elif route == "pay_only":
        d = F(0)
    else:
        raise ValueError("only named paper comparisons are supported")
    return tuple((ap, ad, (a if ap else 1-a)*(d if ad else 1-d))
                 for ap, ad in product((0, 1), repeat=2))


def named_metrics(fixture, rows, decisions, profile, route):
    mu = F(1) if route.startswith("v6_") else F(2)
    fa = fr = accuracy0 = exposure = reward = release = F(0)
    by_z = [F(0), F(0)]
    rewards = [[F(0)]*3 for _ in (0, 1)]
    release_z = [F(0), F(0)]
    pay_rate = F(0)
    for y, z, xs, t, mass in rows:
        reports = tuple(int(action[-1]) if action[0] == "L" else int(action[1+x])
                        for action, x in zip(profile[z], xs))
        accuracy0 += mass*(int(sum(reports) >= 2) == y)
        by_z[z] += mass
        for ap, ad, coin_mass in event_lottery(route, z, reports):
            weight = mass*coin_mass
            audited = bool(ap or ad)
            fixed = decisions[z, reports]
            decision = fixed["g1"][t] if audited else fixed["g0"]
            fa += weight*(1-y)*decision
            fr += weight*y*(1-decision)
            release += weight*decision
            release_z[z] += weight*decision
            exposure += weight*audited
            pay_rate += weight*ap
            for i, r in enumerate(reports):
                payment = fixture["f"]+mu*ap*(r == t)
                rewards[z][i] += weight*payment
                reward += weight*payment
    utility = tuple(tuple(rewards[z][i]/by_z[z]
                          -(fixture["private"][i][2] if profile[z][i][0] == "H" else 0)
                          for i in range(3)) for z in (0, 1))
    return {"preliminary_accuracy": accuracy0, "accuracy": 1-fa-fr,
            "fa": fa/(1-fixture["pi"]), "fr": fr/fixture["pi"],
            "wrong_payout_value": fa, "loss": 2*fa+fr, "exposure": exposure,
            "pay_eligibility": pay_rate, "reward": reward,
            "audit_cost": exposure/4, "cash": reward+exposure/4,
            "reserve": 3*fixture["f"]+3*mu,
            "utility_by_z": utility, "release": release,
            "release_by_z": tuple(release_z[z]/by_z[z] for z in (0, 1))}


def effort_bounds(fixtures):
    expected = {
        "F51-01": (((F(0), F(0)),)*3),
        "F51-02": (((F(2, 25), F(2, 25)),)*3),
        "V3-HET": ((F(3, 50), F(4, 25)), (F(3, 25), F(3, 25)), (F(0), F(0))),
    }
    result = {}
    for fx in fixtures:
        rows = primitive_rows(fx)
        branches = []
        for i, z in product(range(3), (0, 1)):
            group = [r for r in rows if r[1] == z]
            mass = sum(r[-1] for r in group)
            low = max(sum(r[-1] for r in group if r[3] == v) for v in (0, 1))/mass
            high = sum(max(sum(r[-1] for r in group if r[2][i] == x and r[3] == v)
                           for v in (0, 1)) for x in (0, 1))/mass
            delta = high-low
            require(delta == expected[fx["name"]][i][z], "independent binary entry delta")
            branches.append({"judge": i, "z": z, "low_match": low, "high_match": high,
                             "delta": delta, "s_boundary": fx["private"][i][2]/delta if delta else None})
        result[fx["name"]] = branches
    return result


def run_checks():
    global CHECKS
    CHECKS = 0
    study = fractions(json.loads((ROOT/"configs/v6/rave_phase1.json").read_text()))
    require((study["c_fa"], study["c_fr"], study["budget"], study["kappa"], study["operating_cost"], study["payout_value"])
            == (F(2), F(1), F(6), F(1,4), F(0), F(1)), "unchanged primary loss/budget/cost assumptions")
    bounds = effort_bounds(study["fixtures"])
    het = study["fixtures"][2]
    hr = primitive_rows(het)
    het_profile = (("H01","H01","L0"),("H01","H01","L1"))
    matches = F(0)
    for _, z, xs, t, mass in hr:
        reports = tuple(int(a[-1]) if a[0] == "L" else int(a[1+x])
                        for a, x in zip(het_profile[z], xs))
        matches += mass*sum(r == t for r in reports)
    require(matches == F(111,50), "historical HET useful asymmetric match sum")
    f = study["fixtures"][1]
    rows = primitive_rows(f)
    table = frozen_decisions(rows)
    special = [v for (z, r), v in table.items() if z == 0 and sum(r) == 2]
    require(all(v["posterior"] == F(12, 19) and v["voi"] == F(47, 95) for v in special), "named risk class")
    require(sum(v["mass"] for v in special) == F(57, 625), "target risk mass")
    require(sum(v["mass"]*v["voi"] for v in table.values()) == F(477, 6250), "aggregate VOI")
    require(F(47, 95) > study["kappa"], "decision audit value exceeds primary operating cost")
    for z, r in table:
        events = event_lottery("dual_selective", z, r)
        require(sum(p for _, _, p in events) == 1, "lottery normalization")
        require(sum(p*bool(ap or ad) for ap, ad, p in events) <= F(1, 2), "statewise exposure cap")
        require(sum(p*ap for ap, _, p in events) == F(2, 5), "report-independent eligibility")
    selective = named_metrics(f, rows, table, HIGH, "dual_selective")
    uniform = named_metrics(f, rows, table, HIGH, "dual_uniform")
    pay_only = named_metrics(f, rows, table, HIGH, "pay_only")
    expected = {"fa": F(43,1250), "fr": F(481,3125), "wrong_payout_value": F(43,2500),
                "loss": F(348,3125), "exposure": F(2557,6250), "reward": F(222,125),
                "audit_cost": F(2557,25000), "cash": F(46957,25000), "reserve": F(6)}
    for key, value in expected.items():
        require(selective[key] == value, "paper-derived selective "+key)
    require(uniform["loss"] == F(4499061,39062500), "paper uniform decision loss")
    require(uniform["fa"] == F(328691,9765625), "paper uniform FA")
    require(uniform["fr"] == F(3184297,19531250), "paper uniform FR")
    require(uniform["cash"] == selective["cash"] and uniform["exposure"] == selective["exposure"], "fair matched costs")
    gain = uniform["loss"]-selective["loss"]
    require(gain == F(149061,39062500), "allocation loss reduction")
    economic_gain = pay_only["loss"]+pay_only["cash"]-selective["loss"]-selective["cash"]
    require(economic_gain == F(279,125000), "gain versus no additional decision audit")
    require(selective["fa"] <= F(1,5) and selective["fr"] <= F(1,4)
            and selective["wrong_payout_value"] <= F(3,20) and selective["cash"] <= 4
            and selective["reserve"] <= 6, "preserved quality/cash/reserve gates")
    responses = []
    for z, i, action in product((0, 1), range(3), ACTIONS):
        changed = [list(branch) for branch in HIGH]
        changed[z][i] = action
        sel = named_metrics(f, rows, table, changed, "dual_selective")
        uni = named_metrics(f, rows, table, changed, "dual_uniform")
        pay = named_metrics(f, rows, table, changed, "pay_only")
        require(sel["utility_by_z"] == uni["utility_by_z"] == pay["utility_by_z"], "A_dec does not enter neutral utility")
        gamma = selective["utility_by_z"][z][i]-sel["utility_by_z"][z][i]
        require(gamma == 0 if action == "H01" else gamma >= F(7,500), "all six deviations / strict gap")
        responses.append({"z": z, "judge": i, "action": action, "neutral_loss": gamma,
                          "release_change": sel["release_by_z"][z]-selective["release_by_z"][z]})
    copyz = (("L0",)*3,("L1",)*3)
    original = named_metrics(f, rows, table, copyz, "v6_Q1")
    changed = (("L1","L0","L0"),copyz[1])
    seeking = named_metrics(f, rows, table, changed, "v6_Q1")
    require(seeking["utility_by_z"][0][0]-original["utility_by_z"][0][0] == F(17,50), "P1 audit-seeking exact witness")
    strong = study["fixtures"][0]
    sr = primitive_rows(strong)
    st = frozen_decisions(sr)
    all1 = (("L1",)*3,)*2
    bad = named_metrics(strong, sr, st, all1, "v6_Q2")
    require(bad["fa"] == 1 and bad["exposure"] == F(1,2), "P2 bad quality witness")
    regret = F(0)
    for z, i, action in product((0,1), range(3), ACTIONS):
        profile = [list(branch) for branch in all1]
        profile[z][i] = action
        metric = named_metrics(strong, sr, st, profile, "v6_Q2")
        if z == 0:
            require(metric["utility_by_z"][z][i] == (-F(1,20) if action[0] == "H" else 0), "P2 Low indifference")
        regret = max(regret,metric["utility_by_z"][z][i]-bad["utility_by_z"][z][i])
    require(regret == 0, "P2 full-profile zero regret")
    require(F(1,20)/F(15876,368125) == F(73625,63504) > 1, "Direct Brier exposure impossibility")
    require(F(14998033,3675000) > 4, "historical HET Direct Brier cash bound")
    require(CHECKS > 100, "positive executed check count")
    return {"status": "passed", "checks": CHECKS, "new_policy_grid": False,
            "new_design_points": 1, "new_version": False, "bounded_pure_equilibrium_proof": "strict neutral H01 dominance",
            "binary_effort_bounds": bounds, "dual_selective": selective, "dual_uniform": uniform,
            "pay_only": pay_only, "decision_loss_improvement": gain,
            "economic_improvement_vs_pay_only": economic_gain, "six_action_witnesses": responses,
            "P1_audit_seeking_gain": F(17,50), "P2_bad_NE": bad, "P2_max_regret": regret,
            "external_b_sufficient_bound": "abs(b_i)<7/500",
            "recommendation": "GO_bounded_theory_only_no_implementation_or_grid"}


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    sources = ["CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md",
               "verification/research_synthesis_checks.py", "configs/v6/rave_phase1.json"]
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "running", "inputs": []}
    try:
        for source in sources:
            dest = out/"inputs"/source
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/source, dest)
            manifest["inputs"].append({"source": source, "snapshot": "inputs/"+source,
                                       "sha256": sha256(dest.read_bytes()).hexdigest()})
        result = run_checks()
        (out/"certificate.json").write_text(json.dumps(serial(result),indent=2)+"\n",encoding="utf-8")
        manifest["status"] = "passed"
        manifest["outputs"] = {"certificate.json": sha256((out/"certificate.json").read_bytes()).hexdigest()}
        return result
    except BaseException as error:
        manifest.update(status="failed",error=str(error))
        raise
    finally:
        (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"status": result["status"], "checks": result["checks"], "new_design_points": 1}))
