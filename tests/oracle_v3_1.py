"""Independent exact helpers for V3.1 robustness acceptance fixtures."""

from copy import deepcopy
from fractions import Fraction as F

from tests import oracle_v3


METRICS = (
    "accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value",
    "expected_reward_total", "expected_effort_cost", "expected_audit_cost", "cash_review_cost",
)


def set_path(raw, path, value):
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = str(value)


def apply_point(base, overrides, uncertainty):
    raw = deepcopy(base)
    for path, value in overrides.items():
        set_path(raw, path, value)
    for path, value in uncertainty.items():
        if path == "verification_anchor.quality":
            raw["verification_anchor"]["sensitivity"] = str(value)
            raw["verification_anchor"]["specificity"] = str(value)
        elif path == "judges.high_effort_cost_multiplier":
            multiplier = F(value)
            for judge in "ABC":
                raw["judges"][judge]["high_effort_cost"] = str(F(base["judges"][judge]["high_effort_cost"]) * multiplier)
        else:
            set_path(raw, path, value)
    return raw


def public_signal_reference(raw):
    pi = F(raw["pi"])
    sensitivity = F(raw["public_signal"]["sensitivity"])
    specificity = F(raw["public_signal"]["specificity"])
    payout = F(raw["payout_value"])
    false_approval = 1 - specificity
    false_rejection = 1 - sensitivity
    return {
        "accuracy": pi * sensitivity + (1 - pi) * specificity,
        "false_approval_rate": false_approval,
        "false_rejection_rate": false_rejection,
        "wrong_payout_value": payout * (1 - pi) * false_approval,
    }


def point_fixture(raw, gates):
    equilibrium = oracle_v3.equilibrium_summary(raw)
    if equilibrium["status"] != "pure_equilibria_evaluated":
        return {"status": "fail", "failure_reasons": ["no_pure_equilibrium"], "equilibrium": equilibrium}
    worst = {
        "accuracy": equilibrium["ranges"]["accuracy"]["min"],
        "false_approval_rate": equilibrium["ranges"]["false_approval_rate"]["max"],
        "false_rejection_rate": equilibrium["ranges"]["false_rejection_rate"]["max"],
        "wrong_payout_value": equilibrium["ranges"]["wrong_payout_value"]["max"],
        "cash_review_cost": equilibrium["ranges"]["cash_review_cost"]["max"],
    }
    checks = (
        ("false_approval_gate", "false_approval_rate", "max_false_approval_rate"),
        ("wrong_payout_gate", "wrong_payout_value", "max_wrong_payout_value"),
        ("false_rejection_gate", "false_rejection_rate", "max_false_rejection_rate"),
        ("cash_review_cost_gate", "cash_review_cost", "max_cash_review_cost"),
    )
    reasons = [reason for reason, metric, gate in checks if worst[metric] > F(gates[gate])]
    all_high = oracle_v3.evaluate(raw, {"0": ["H01"] * 3, "1": ["H01"] * 3})["metrics"]
    return {
        "status": "pass" if not reasons else "fail",
        "failure_reasons": reasons,
        "equilibrium": equilibrium,
        "worst": worst,
        "public_signal_rule": public_signal_reference(raw),
        "forced_all_high": {key: all_high[key] for key in (
            "accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value", "cash_review_cost"
        )},
    }


def pareto_ids(records):
    keys = ("false_approval_rate", "wrong_payout_value", "false_rejection_rate", "cash_review_cost")
    result = []
    for candidate in records:
        dominated = False
        for other in records:
            if other["policy_id"] == candidate["policy_id"]:
                continue
            weak = all(other["worst"][key] <= candidate["worst"][key] for key in keys)
            strict = any(other["worst"][key] < candidate["worst"][key] for key in keys)
            if weak and strict:
                dominated = True
                break
        if not dominated:
            result.append(candidate["policy_id"])
    return result


def serializable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serializable(item) for item in value]
    return value
