"""Independent potential-state + separate-coin Fraction oracle.

Imports no evaluator, interval analyzer, or parent arithmetic helpers.
"""

from fractions import Fraction as F
from itertools import product


ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")


def calibration():
    table = {}
    for z, reports in product((0, 1), product((0, 1), repeat=3)):
        likelihood = []
        for y in (0, 1):
            p = F(1, 2)*(F(7, 10) if z == y else F(3, 10))
            for r in reports:
                p *= F(4, 5) if r == y else F(1, 5)
            likelihood.append(p)
        g0 = int(likelihood[1] >= 2*likelihood[0])
        g1 = tuple(int(likelihood[1]*(F(9, 10) if t else F(1, 10))
                       >= 2*likelihood[0]*(F(1, 10) if t else F(9, 10)))
                   for t in (0, 1))
        table[z, reports] = (g0, g1)
    return table


def evaluate(z, profile, mechanism, mutation=None):
    """Conditional on Z; actual actions, fixed calibration, no optimization."""
    table = calibration()
    out = {k: F(0) for k in ("fa_joint", "fr_joint", "wrong_payout", "loss",
                             "release", "exposure", "reward", "cash")}
    payments = [F(0)]*3
    for y, xa, xb, xc, t in product((0, 1), repeat=5):
        weight = F(7, 10) if y == z else F(3, 10)
        for bit in (xa, xb, xc):
            weight *= F(4, 5) if bit == y else F(1, 5)
        weight *= F(9, 10) if t == y else F(1, 10)
        reports = tuple(int(action[-1]) if action[0] == "L" else int(action[1+x])
                        for action, x in zip(profile, (xa, xb, xc)))
        d = F(19, 1250) if mechanism == "uniform" else F(1, 6)*int(z == 0 and sum(reports) == 2)
        for ap, ad in product((0, 1), repeat=2):
            mass = weight*(F(2, 5) if ap else F(3, 5))*(d if ad else 1-d)
            union = int(bool(ap or ad))
            g0, g1 = table[z, reports]
            decision = g1[t] if union else g0
            out["fa_joint"] += mass*int(y == 0 and decision == 1)
            out["fr_joint"] += mass*int(y == 1 and decision == 0)
            out["release"] += mass*decision
            out["exposure"] += mass*((ap+ad) if mutation == "double_audit" else union)
            for i, report in enumerate(reports):
                eligible = union if mutation == "union_payment" else ap
                payments[i] += mass*2*eligible*int(report == t)
    out["utility"] = tuple(p-F(1, 20)*int(a[0] == "H") for p, a in zip(payments, profile))
    out["reward"] = sum(payments)
    out["cash"] = out["reward"]+out["exposure"]/4
    out["wrong_payout"] = out["fa_joint"]
    out["loss"] = 2*out["fa_joint"]+out["fr_joint"]
    return out


def best_responses(z, profile, mechanism, interests):
    base = evaluate(z, profile, mechanism)
    choices = []
    for i in range(3):
        utilities = {}
        for action in ACTIONS:
            changed = list(profile)
            changed[i] = action
            m = evaluate(z, changed, mechanism)
            utilities[action] = m["utility"][i]+interests[i]*m["release"]
        optimum = max(utilities.values())
        choices.append(tuple(a for a in ACTIONS if utilities[a] == optimum))
    return tuple(choices)
