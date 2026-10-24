"""Independent finite-state oracle for V5 Phase 1.5 certificates.

This file rebuilds the binary signal distributions from primitive likelihoods.
It intentionally imports no CEAV production or Phase 1 evaluator.
"""

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product


JUDGES = ("A", "B", "C")
BINARY_ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")


@dataclass(frozen=True)
class JudgeSpec:
    sensitivity: F
    specificity: F
    cost: F


@dataclass(frozen=True)
class Fixture:
    name: str
    prior: F
    public_sensitivity: F
    public_specificity: F
    judges: tuple[JudgeSpec, JudgeSpec, JudgeSpec]
    audit_sensitivity: F
    audit_specificity: F
    target_weights: tuple[F, F]


@dataclass(frozen=True)
class Policy:
    mechanism: str
    f: F
    mu: F
    q: F
    budget: F = F(6)
    kappa: F = F(0)
    operating_cost: F = F(0)
    payout_value: F = F(1)


def _likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def _fixture(name):
    if name == "F51-02":
        return Fixture(
            name=name, prior=F(1, 2), public_sensitivity=F(7, 10),
            public_specificity=F(7, 10),
            judges=tuple(JudgeSpec(F(4, 5), F(4, 5), F(1, 20)) for _ in JUDGES),
            audit_sensitivity=F(9, 10), audit_specificity=F(9, 10),
            target_weights=(F(1, 2), F(1, 2)))
    if name == "V3-HET":
        return Fixture(
            name=name, prior=F(1, 2), public_sensitivity=F(4, 5),
            public_specificity=F(3, 5), judges=(
                JudgeSpec(F(9, 10), F(4, 5), F(1, 20)),
                JudgeSpec(F(3, 4), F(19, 20), F(1, 10)),
                JudgeSpec(F(13, 20), F(7, 10), F(1, 25)),
            ), audit_sensitivity=F(9, 10), audit_specificity=F(9, 10),
            target_weights=(F(2, 5), F(3, 5)))
    raise KeyError(name)


def _rows(fixture):
    rows = []
    for y, z, xa, xb, xc, t in product((0, 1), repeat=6):
        probability = fixture.prior if y else 1 - fixture.prior
        probability *= _likelihood(z, y, fixture.public_sensitivity, fixture.public_specificity)
        probability *= _likelihood(t, y, fixture.audit_sensitivity, fixture.audit_specificity)
        for x, spec in zip((xa, xb, xc), fixture.judges):
            probability *= _likelihood(x, y, spec.sensitivity, spec.specificity)
        rows.append((probability, y, z, (xa, xb, xc), t))
    if sum(row[0] for row in rows) != 1:
        raise ValueError("joint distribution must sum to one")
    return rows


def _conditional_rows(fixture, z, judge=None, x=None):
    rows = [row for row in _rows(fixture) if row[2] == z]
    if judge is not None and x is not None:
        rows = [row for row in rows if row[3][judge] == x]
    mass = sum(row[0] for row in rows)
    if mass <= 0:
        raise ValueError("conditional event has no mass")
    return [(p / mass, y, z0, xs, t) for p, y, z0, xs, t in rows]


def posterior_y(fixture, judge, z, x=None):
    rows = _conditional_rows(fixture, z, judge, x)
    return sum(p for p, y, _, _, _ in rows if y == 1)


def posterior_t(fixture, judge, z, x=None):
    rows = _conditional_rows(fixture, z, judge, x)
    return sum(p for p, _, _, _, t in rows if t == 1)


def score(p, t):
    return 1 - (p - t) ** 2


def _report(action, x):
    if action == "L0" or action == "H00":
        return 0
    if action == "L1" or action == "H11":
        return 1
    if action == "H01":
        return x
    if action == "H10":
        return 1 - x
    raise KeyError(action)


def _public_mass(fixture, z):
    return sum(p for p, _, z0, _, _ in _rows(fixture) if z0 == z)


def _conditional_expected(fixture, z, function):
    rows = _conditional_rows(fixture, z)
    return sum(p * function(y, xs, t) for p, y, _, xs, t in rows)


def _direct_expected_score(fixture, judge, z, high):
    def value(_, xs, t):
        p = posterior_t(fixture, judge, z, xs[judge] if high else None)
        return score(p, t)
    return _conditional_expected(fixture, z, value)


def _binary_expected_match(fixture, judge, z, action):
    return _conditional_expected(
        fixture, z,
        lambda _, xs, t: F(_report(action, xs[judge]) == t))


def _best_options(values):
    maximum = max(values.values())
    return tuple(key for key in values if values[key] == maximum)


def best_response_options(fixture, policy, judge, z):
    s = policy.mu * policy.q
    cost = fixture.judges[judge].cost
    if policy.mechanism == "direct":
        values = {
            "L": s * _direct_expected_score(fixture, judge, z, False),
            "H": s * _direct_expected_score(fixture, judge, z, True) - cost,
        }
    elif policy.mechanism == "binary":
        values = {}
        for action in BINARY_ACTIONS:
            values[action] = s * _binary_expected_match(fixture, judge, z, action)
            if action.startswith("H"):
                values[action] -= cost
    else:
        raise KeyError(policy.mechanism)
    return {"options": _best_options(values), "utilities": values}


def _response_options(fixture, policy):
    return tuple(tuple(best_response_options(fixture, policy, judge, z)["options"]
                       for z in (0, 1)) for judge in range(3))


def _profile_product(options):
    choices = []
    for judge in range(3):
        for z in (0, 1):
            choices.append(options[judge][z])
    for flat in product(*choices):
        yield tuple((flat[judge * 2], flat[judge * 2 + 1]) for judge in range(3))


def _vote(fixture, judge, z, action, xs):
    if fixture.name == "V3-HET" or fixture.name == "F51-02":
        if action in BINARY_ACTIONS:
            return _report(action, xs[judge])
        x = xs[judge] if action == "H" else None
        return int(posterior_y(fixture, judge, z, x) >= F(1, 2))
    raise KeyError(fixture.name)


def _forecast(fixture, judge, z, action, xs):
    if action in BINARY_ACTIONS:
        return None
    return posterior_t(fixture, judge, z, xs[judge] if action == "H" else None)


def _score_for_action(fixture, judge, z, action, xs, t):
    if action in BINARY_ACTIONS:
        return F(_report(action, xs[judge]) == t)
    return score(_forecast(fixture, judge, z, action, xs), t)


def _decision_label(fixture, profile):
    decisions = {}
    for z in (0, 1):
        rows = _conditional_rows(fixture, z)
        if all((sum(_vote(fixture, j, z, profile[j][z], xs) for j in range(3)) >= 2)
               == bool(z) for _, _, _, xs, _ in rows):
            decisions[z] = "Z"
        elif all((sum(_vote(fixture, j, z, profile[j][z], xs) for j in range(3)) >= 2)
                 == (sum(xs) >= 2) for _, _, _, xs, _ in rows):
            decisions[z] = "majority_X"
        else:
            decisions[z] = "profile_dependent"
    return decisions


def evaluate_profile(fixture_name, policy, profile):
    fixture = _fixture(fixture_name)
    rows = _rows(fixture)
    expected_reward = F(0)
    expected_effort_cost = F(0)
    accuracy = false_approval_joint = false_rejection_joint = F(0)
    decisions = []
    for probability, y, z, xs, t in rows:
        votes = tuple(_vote(fixture, j, z, profile[j][z], xs) for j in range(3))
        decision = int(sum(votes) >= 2)
        decisions.append((z, xs, decision))
        expected_reward += probability * sum(
            policy.f + policy.mu * policy.q * _score_for_action(fixture, j, z, profile[j][z], xs, t)
            for j in range(3))
        expected_effort_cost += probability * sum(
            fixture.judges[j].cost * F(profile[j][z] == "H" or profile[j][z] in ("H00", "H01", "H10", "H11"))
            for j in range(3))
        accuracy += probability * F(decision == y)
        false_approval_joint += probability * F(y == 0 and decision == 1)
        false_rejection_joint += probability * F(y == 1 and decision == 0)
    fa = false_approval_joint / (1 - fixture.prior)
    fr = false_rejection_joint / fixture.prior
    return {
        "fixture": fixture_name,
        "mechanism": policy.mechanism,
        "policy": policy,
        "effort_profile": profile,
        "response_options": _response_options(fixture, policy),
        "accuracy": accuracy,
        "false_approval_rate": fa,
        "false_rejection_rate": fr,
        "wrong_payout_probability": false_approval_joint,
        "wrong_payout_value": policy.payout_value * false_approval_joint,
        "expected_reward_total": expected_reward,
        "expected_cash_cost": expected_reward + policy.q * policy.kappa + policy.operating_cost,
        "expected_effort_cost": expected_effort_cost,
        "realized_reward_cap": 3 * policy.f + 3 * policy.mu,
        "audit_exposure": policy.q,
        "decision_rule": _decision_label(fixture, profile),
        "decisions": tuple(decisions),
        "target_weights": fixture.target_weights,
    }


def evaluate_best_profiles(fixture_name, policy):
    fixture = _fixture(fixture_name)
    options = _response_options(fixture, policy)
    return tuple(evaluate_profile(fixture_name, policy, profile)
                 for profile in _profile_product(options))


def _forecast_table(fixture_name, judge=0):
    fixture = _fixture(fixture_name)
    p_t = {z: {x: posterior_t(fixture, judge, z, x) for x in (0, 1)} for z in (0, 1)}
    p_y = {z: {x: posterior_y(fixture, judge, z, x) for x in (0, 1)} for z in (0, 1)}
    votes = {z: {x: int(p_y[z][x] >= F(1, 2)) for x in (0, 1)} for z in (0, 1)}
    return p_t, p_y, votes


def certificate_f51_02():
    direct_policy = Policy("direct", F(0), F(2), F(3, 5))
    binary_policy = Policy("binary", F(0), F(2), F(1, 2))
    direct = evaluate_best_profiles("F51-02", direct_policy)[0]
    binary = evaluate_best_profiles("F51-02", binary_policy)[0]
    fixture = _fixture("F51-02")
    response_details = {
        "direct": tuple(tuple(best_response_options(fixture, direct_policy, j, z)
                               for z in (0, 1)) for j in range(3)),
        "binary": tuple(tuple(best_response_options(fixture, binary_policy, j, z)
                               for z in (0, 1)) for j in range(3)),
    }
    forecast_tables = []
    for judge in range(3):
        p_t, p_y, votes = _forecast_table("F51-02", judge)
        forecast_tables.append({"p_t": p_t, "p_y": p_y, "votes": votes})
    direct["forecast_tables_by_judge"] = tuple(forecast_tables)
    direct["forecast_p_t"] = forecast_tables[0]["p_t"]
    direct["forecast_p_y"] = forecast_tables[0]["p_y"]
    direct["vote_by_z_x"] = forecast_tables[0]["votes"]
    direct["response_details_by_judge"] = response_details["direct"]
    binary["response_details_by_judge"] = response_details["binary"]
    return {"direct": direct, "binary_audit_only": binary}


def _v3_direct_profile():
    policy = Policy("direct", F(1, 10), F(19, 10), F(4, 5))
    return evaluate_best_profiles("V3-HET", policy)[0]


def certificate_v3_het():
    direct_policy = Policy("direct", F(1, 10), F(19, 10), F(4, 5))
    direct = _v3_direct_profile()
    forecast_tables = []
    for judge in range(3):
        p_t, p_y, votes = _forecast_table("V3-HET", judge)
        forecast_tables.append({"p_t": p_t, "p_y": p_y, "votes": votes})
    direct["forecast_tables_by_judge"] = tuple(forecast_tables)

    fixture = _fixture("V3-HET")
    threshold_s = fixture.judges[1].cost / F(49, 775)
    threshold_policy = Policy("direct", F(1, 10), threshold_s, F(1))
    options = _response_options(fixture, threshold_policy)
    cheapest_profile = (("H", "H"), ("L", "L"), ("L", "L"))
    tie_high_profile = (("H", "H"), ("H", "L"), ("L", "L"))
    cheapest = evaluate_profile("V3-HET", threshold_policy, cheapest_profile)
    tie_high = evaluate_profile("V3-HET", threshold_policy, tie_high_profile)
    bound = {
        "s_threshold_B_z0": threshold_s,
        "strict_high_requires": f"s > {threshold_s}",
        "B_z0_best_effort_at_threshold": options[1][0],
        "B_z1_best_effort_at_threshold": options[1][1],
        "A_best_effort_at_threshold": options[0],
        "C_best_effort_at_threshold": options[2],
        "cheapest_tie_resolution_profile": cheapest_profile,
        "cheapest_tie_resolution_cost": cheapest["expected_cash_cost"],
        "B_high_at_z0_tie_profile": tie_high_profile,
        "B_high_at_z0_tie_cost": tie_high["expected_cash_cost"],
        "cash_gate": F(4),
        "cheapest_profile_exceeds_cash_gate": cheapest["expected_cash_cost"] > 4,
        "high_tie_profile_exceeds_cash_gate": tie_high["expected_cash_cost"] > 4,
        "threshold_policy": threshold_policy,
    }
    return {"direct": direct, "budget_bound": bound}
