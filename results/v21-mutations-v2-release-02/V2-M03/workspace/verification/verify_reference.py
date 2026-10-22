"""Exact checks for CEAV_M1_SPEC.md; not a general equilibrium analyzer.

Run from the standalone workspace:
    python verification/verify_reference.py --output verification/reference_results.json
Only the Python standard library is required.
"""

import argparse
import json
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path


@dataclass(frozen=True)
class Model:
    pi: F = F(1, 2)
    a: F = F(7, 10)
    b: F = F(4, 5)
    cost: F = F(1, 20)
    multiplier: F = F(1)


def quadratic(p, report):
    return 2 * p - p * p if report else 1 - p * p


def states(model):
    rows = []
    for y, z, xa, xb, xc in product((0, 1), repeat=5):
        weight = (model.pi if y else 1 - model.pi)
        weight *= model.a if z == y else 1 - model.a
        for x in (xa, xb, xc):
            weight *= model.b if x == y else 1 - model.b
        rows.append(((y, z, xa, xb, xc), weight))
    assert len(rows) == 32 and sum(w for _, w in rows) == 1
    return rows


def report(policy, state, judge):
    if policy == "X":
        return state[2 + judge]
    if policy == "Z":
        return state[1]
    if policy == "NOT_Z":
        return 1 - state[1]
    if policy == "PASS":
        return 1
    if policy == "FAIL":
        return 0
    raise ValueError(f"Unknown reference policy: {policy}")


def observation(state, judge, high):
    return (state[1], state[2 + judge]) if high else (state[1],)


def groups(rows, judge, high):
    result = {}
    for state, weight in rows:
        result.setdefault(observation(state, judge, high), []).append((state, weight))
    return result


def predictions(rows, profile):
    tables = []
    for i in range(3):
        table = {}
        for key, group in groups(rows, i, profile[i] == "X").items():
            mass = sum(w for _, w in group)
            table[key] = sum(w * report(profile[(i + 2) % 3], s, (i + 2) % 3)
                             for s, w in group) / mass
        tables.append(table)
    return tables


def best_response(rows, profile, peer_tables, judge, high):
    """Optimize own reports and continuous predictions with peer tables FROZEN."""
    reference, peer = (judge + 1) % 3, (judge + 2) % 3
    information = prediction = F(0)
    rules = []
    for key, group in groups(rows, judge, high).items():
        mass = sum(w for _, w in group)
        q = sum(w * report(profile[peer], s, peer) for s, w in group) / mass
        choices = []
        for own_report in (0, 1):
            total = F(0)
            for state, weight in group:
                p_ref = peer_tables[reference][observation(state, reference, profile[reference] == "X")]
                delta = min(p_ref, 1 - p_ref)
                shadow = p_ref + (2 * own_report - 1) * delta
                assert 0 <= shadow <= 1
                total += weight * quadratic(shadow, report(profile[peer], state, peer))
            choices.append(total)
        information += max(choices)
        prediction += mass * (1 - q + q * q)
        rules.append({"observation": list(key), "optimal_prediction": q,
                      "optimal_reports": [r for r in (0, 1) if choices[r] == max(choices)]})
    return {"information": information, "prediction": prediction,
            "score": information + prediction, "rules": rules}


def direct_score(rows, profile, tables, judge):
    total = F(0)
    reference, peer = (judge + 1) % 3, (judge + 2) % 3
    for state, weight in rows:
        own_p = tables[judge][observation(state, judge, profile[judge] == "X")]
        p_ref = tables[reference][observation(state, reference, profile[reference] == "X")]
        own_r = report(profile[judge], state, judge)
        peer_r = report(profile[peer], state, peer)
        shadow = p_ref + (2 * own_r - 1) * min(p_ref, 1 - p_ref)
        score = quadratic(shadow, peer_r) + quadratic(own_p, peer_r)
        assert 0 <= score <= 2
        total += weight * score
    return total


def analyze(model, policy):
    rows = states(model)
    profile = (policy,) * 3
    frozen_tables = predictions(rows, profile)
    table_snapshot = [dict(t) for t in frozen_tables]
    branches = {}
    for z in (0, 1):
        raw = [(s, w) for s, w in rows if s[1] == z]
        mass = sum(w for _, w in raw)
        conditional = [(s, w / mass) for s, w in raw]
        low = best_response(conditional, profile, frozen_tables, 0, False)
        high = best_response(conditional, profile, frozen_tables, 0, True)
        assert high["score"] >= low["score"]
        candidate_score = direct_score(conditional, profile, frozen_tables, 0)
        candidate_utility = model.multiplier * candidate_score - (model.cost if policy == "X" else 0)
        low_u = model.multiplier * low["score"]
        high_u = model.multiplier * high["score"] - model.cost
        regret = max(low_u, high_u) - candidate_utility
        assert regret >= 0
        branches[str(z)] = {"probability": mass, "low": low, "high": high,
                            "delta_utility": high_u - low_u, "regret": regret,
                            "candidate_score": candidate_score}
    assert frozen_tables == table_snapshot
    low = best_response(rows, profile, frozen_tables, 0, False)
    high = best_response(rows, profile, frozen_tables, 0, True)
    accuracy = wrong = false_rejection_joint = F(0)
    for state, weight in rows:
        decision = int(sum(report(policy, state, i) for i in range(3)) >= 2)
        accuracy += weight * (decision == state[0])
        wrong += weight * (decision == 1 and state[0] == 0)
        false_rejection_joint += weight * (decision == 0 and state[0] == 1)
    # Named reference profiles are symmetric across Judge identities.
    for i in (1, 2):
        assert direct_score(rows, profile, frozen_tables, i) == direct_score(rows, profile, frozen_tables, 0)
    return {"low": low, "high": high, "branches": branches,
            "delta_score": high["score"] - low["score"],
            "delta_utility": model.multiplier * (high["score"] - low["score"]) - model.cost,
            "candidate_is_pure_equilibrium": all(v["regret"] == 0 for v in branches.values()),
            "candidate_expected_score": direct_score(rows, profile, frozen_tables, 0),
            "accuracy": accuracy, "wrong_payout_value_for_V1": wrong,
            "false_approval_rate": wrong / (1 - model.pi),
            "false_rejection_rate": false_rejection_joint / model.pi}


def verify():
    base = Model()
    g1 = analyze(base, "X")
    assert g1["low"]["score"] == F(3611, 2500)
    assert g1["high"]["score"] == F(334433762, 216825625)
    assert g1["delta_score"] == F(85003317, 867302500)
    assert g1["candidate_is_pure_equilibrium"]
    assert g1["accuracy"] == F(112, 125)
    assert g1["wrong_payout_value_for_V1"] == F(13, 250)
    assert all(r["optimal_reports"] == [r["observation"][1]] for r in g1["high"]["rules"])
    assert all(r["optimal_reports"] == [0, 1] for r in g1["low"]["rules"])
    expected_forecasts = {(0, 0): F(8, 31), (0, 1): F(11, 19),
                          (1, 0): F(8, 19), (1, 1): F(23, 31)}
    assert {tuple(r["observation"]): r["optimal_prediction"] for r in g1["high"]["rules"]} == expected_forecasts

    g2 = {p: analyze(base, p) for p in ("Z", "NOT_Z", "PASS", "FAIL")}
    for result in g2.values():
        assert result["candidate_expected_score"] == 2
        assert result["candidate_is_pure_equilibrium"]
        assert result["delta_utility"] == -base.cost
    assert g2["Z"]["accuracy"] == F(7, 10)
    assert g2["Z"]["wrong_payout_value_for_V1"] == F(3, 20)

    g3 = analyze(replace(base, a=F(9, 10), b=F(3, 4)), "X")
    assert g3["low"]["score"] == F(149, 100)
    assert g3["high"]["score"] == F(23833, 15680)
    assert g3["delta_score"] == F(2349, 78400)
    assert not g3["candidate_is_pure_equilibrium"]
    assert g3["accuracy"] == F(27, 32)

    g4 = analyze(replace(base, pi=F(4, 5)), "X")
    assert g4["delta_utility"] > 0
    assert g4["branches"]["0"]["delta_utility"] > 0
    assert g4["branches"]["1"]["delta_utility"] < 0
    assert not g4["candidate_is_pure_equilibrium"]
    assert analyze(replace(base, b=F(1, 2)), "X")["delta_score"] == 0
    assert analyze(replace(base, multiplier=F(0)), "X")["delta_utility"] == -base.cost

    for q, p in product((F(0), F(1, 3), F(1)), repeat=2):
        expected_q = q * quadratic(q, 1) + (1 - q) * quadratic(q, 0)
        expected_p = q * quadratic(p, 1) + (1 - q) * quadratic(p, 0)
        assert expected_q - expected_p == (p - q) ** 2
    for cost in (F(0), F(1, 20)):
        fixed_low, fixed_high = F(2), F(2) - cost
        assert fixed_low - fixed_high == cost

    return {"spec_version": "ceav-m1-v1.0", "arithmetic": "fractions.Fraction",
            "scope": "Named-profile reference checks only; no exhaustive equilibrium search",
            "configurations": {
                "G1_and_G2": vars(base),
                "G3": vars(replace(base, a=F(9, 10), b=F(3, 4))),
                "G4": vars(replace(base, pi=F(4, 5))),
                "shared": {"f": F(0), "fixed_reward": F(2),
                           "reward_budget": F(6), "payout_value": F(1)},
            },
            "G1": g1, "G2": g2, "G3": g3, "G4": g4,
            "G1_lambda_threshold": base.cost / g1["delta_score"]}


def serializable(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serializable(item) for item in value]
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write reproducible reference JSON")
    args = parser.parse_args()
    results = verify()
    encoded = json.dumps(serializable(results), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
        print(f"Reference checks passed; wrote {args.output.resolve()}")
    else:
        print(encoded, end="")
    print("G1 delta utility:", float(results["G1"]["delta_utility"]))
    print("G3 delta utility:", float(results["G3"]["delta_utility"]))
    print("G4 rejects all-H despite positive aggregate effort gain.")
