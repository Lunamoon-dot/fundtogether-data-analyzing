"""Independent V3.3 IPW calculations.

This oracle deliberately imports no ceav_m1 production module.  It only
reconstructs likelihood rows and the IPW anchor expectation/moments needed by
the small red and acceptance fixtures.
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
    private = tuple((F(raw["judges"][judge]["private_signal"]["sensitivity"]),
                     F(raw["judges"][judge]["private_signal"]["specificity"])) for judge in "ABC")
    verification = (F(raw["verification_anchor"]["sensitivity"]), F(raw["verification_anchor"]["specificity"]))
    result = []
    for y, z, xa, xb, xc, t in product((0, 1), repeat=6):
        mass = pi if y else 1 - pi
        mass *= likelihood(z, y, *public)
        for x, pair in zip((xa, xb, xc), private):
            mass *= likelihood(x, y, *pair)
        mass *= likelihood(t, y, *verification)
        result.append((y, z, (xa, xb, xc), t, mass))
    assert len(result) == 64 and sum(row[-1] for row in result) == 1
    return result


def q_by_report(raw):
    values = raw["verification_anchor"]["audit_probability_by_report"]
    return (F(values["0"]), F(values["1"]))


def all_high_anchor_moments(raw):
    q = q_by_report(raw)
    mu = F(raw["anchor_weight"])
    expected = [F(0), F(0), F(0)]
    second = [F(0), F(0), F(0)]
    exposure = [F(0), F(0), F(0)]
    for _y, _z, signals, t, mass in rows(raw):
        for judge, report in enumerate(signals):
            exposure[judge] += mass * q[report]
            if report == t:
                expected[judge] += mass * mu
                second[judge] += mass * mu * mu / q[report]
    variance = [second[i] - expected[i] * expected[i] for i in range(3)]
    return {"expected_anchor_reward": expected, "second_moment": second,
            "variance": variance, "expected_audit_exposure": exposure}


def conditional_anchor_expectation(raw, group, report):
    q = q_by_report(raw)
    mu = F(raw["anchor_weight"])
    mass = sum(row[-1] for row in group)
    return sum(row[-1] / mass * mu * (report == row[3]) for row in group)


def branch_anchor_by_report(raw, judge, z):
    source = [row for row in rows(raw) if row[1] == z]
    groups = {}
    for row in source:
        groups.setdefault((z, row[2][judge]), []).append(row)
    return {observation: [conditional_anchor_expectation(raw, group, report) for report in (0, 1)]
            for observation, group in groups.items()}


def expected_audit_cost(raw, exposure):
    return F(raw["verification_anchor"]["cost_per_audit"]) * sum(exposure)
