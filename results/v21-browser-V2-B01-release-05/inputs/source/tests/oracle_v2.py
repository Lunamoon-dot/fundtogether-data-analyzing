"""Independent V2 distribution oracle. It never imports production model code."""

from fractions import Fraction as F
from itertools import product

JUDGES = ("A", "B", "C")


def q(value):
    return F(value)


def parsed(raw):
    return {
        "pi": q(raw["pi"]),
        "public": (q(raw["public_signal"]["sensitivity"]), q(raw["public_signal"]["specificity"])),
        "private": tuple((q(raw["judges"][judge]["private_signal"]["sensitivity"]),
                          q(raw["judges"][judge]["private_signal"]["specificity"])) for judge in JUDGES),
        "costs": tuple(q(raw["judges"][judge]["high_effort_cost"]) for judge in JUDGES),
    }


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def worlds(raw):
    p = parsed(raw)
    rows = []
    for state_id, (y, z, xa, xb, xc) in enumerate(product((0, 1), repeat=5)):
        mass = p["pi"] if y else 1 - p["pi"]
        mass *= likelihood(z, y, *p["public"])
        for value, pair in zip((xa, xb, xc), p["private"]):
            mass *= likelihood(value, y, *pair)
        rows.append(((state_id, y, z, xa, xb, xc), mass))
    assert len(rows) == 32
    assert all(mass > 0 for _, mass in rows)
    assert sum(mass for _, mass in rows) == 1
    return tuple(rows)


def diagnostics(raw):
    p = parsed(raw)

    def one(pair):
        sensitivity, specificity = pair
        return {
            "sensitivity": sensitivity,
            "specificity": specificity,
            "false_negative_rate": 1 - sensitivity,
            "false_positive_rate": 1 - specificity,
            "prior_weighted_accuracy": p["pi"] * sensitivity + (1 - p["pi"]) * specificity,
        }

    return {
        "public_signal": one(p["public"]),
        "judges": {judge: {"private_signal": one(pair)} for judge, pair in zip(JUDGES, p["private"])},
    }
