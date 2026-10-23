"""Independent V3.2 calculations for the red and acceptance tests.

This file intentionally does not import the production model, evaluator, or
report-sensitive study.  It reconstructs only the finite likelihood sums used
by the fixture.
"""

from fractions import Fraction as F
from itertools import product


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def rows(raw):
    pi = F(raw["pi"])
    public = (F(raw["public_signal"]["sensitivity"]), F(raw["public_signal"]["specificity"]))
    private = tuple((F(raw["judges"][j]["private_signal"]["sensitivity"]),
                     F(raw["judges"][j]["private_signal"]["specificity"])) for j in "ABC")
    verification = (F(raw["verification_anchor"]["sensitivity"]), F(raw["verification_anchor"]["specificity"]))
    result = []
    for y, z, xa, xb, xc, t in product((0, 1), repeat=6):
        mass = pi if y else 1 - pi
        mass *= likelihood(z, y, *public)
        for x, pair in zip((xa, xb, xc), private):
            mass *= likelihood(x, y, *pair)
        mass *= likelihood(t, y, *verification)
        result.append((y, z, (xa, xb, xc), t, mass))
    assert sum(row[-1] for row in result) == 1
    return result


def q_by_report(raw):
    values = raw["verification_anchor"]["audit_probability_by_report"]
    return (F(values["0"]), F(values["1"]))


def all_high_metrics(raw):
    q = q_by_report(raw)
    payout = F(raw["payout_value"])
    mu = F(raw["anchor_weight"])
    kappa = F(raw["verification_anchor"]["cost_per_audit"])
    accuracy = false_approval = false_rejection = audit_exposure = anchor_total = F(0)
    for y, _z, signals, t, mass in rows(raw):
        reports = signals
        decision = int(sum(reports) >= 2)
        accuracy += mass * (decision == y)
        false_approval += mass * (y == 0 and decision == 1)
        false_rejection += mass * (y == 1 and decision == 0)
        for report in reports:
            audit_exposure += mass * q[report]
            anchor_total += mass * q[report] * (report == t)
    return {
        "accuracy": accuracy,
        "false_approval_rate": false_approval / (1 - F(raw["pi"])),
        "false_rejection_rate": false_rejection / F(raw["pi"]),
        "expected_anchor_reward_total": mu * anchor_total,
        "expected_audit_cost": kappa * audit_exposure,
        "wrong_payout_value": payout * false_approval,
    }


def branch_anchor_by_report(raw, profile, judge, z, effort):
    q = q_by_report(raw)
    source = rows(raw)
    selected = [row for row in source if row[1] == z]
    groups = {}
    for row in selected:
        observation = (z, row[2][judge]) if effort == "H" else (z,)
        groups.setdefault(observation, []).append(row)
    result = {}
    for observation, group in groups.items():
        mass = sum(row[-1] for row in group)
        result[observation] = [sum(row[-1] / mass * q[report] * (report == row[3]) for row in group) for report in (0, 1)]
    return result
