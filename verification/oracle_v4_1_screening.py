"""Independent finite checks for the V4.1 screening fixtures.

This module intentionally enumerates the signal distribution itself.  It does
not import the screening analyzer, so a changed analyzer cannot manufacture
its own expected fixture values.
"""

from fractions import Fraction as F
from itertools import product


def _likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


FIXTURES = {
    "F41-01": {
        "pi": F(1, 2), "public": (F(19, 20), F(19, 20)),
        "private": (F(4, 5), F(4, 5)), "audit": (F(9, 10), F(9, 10)),
    },
    "F41-02": {
        "pi": F(1, 2), "public": (F(7, 10), F(7, 10)),
        "private": (F(4, 5), F(4, 5)), "audit": (F(9, 10), F(9, 10)),
    },
}


def _rows(fixture, z=None):
    rows = []
    for y, public, xa, xb, xc, truth in product((0, 1), repeat=6):
        probability = fixture["pi"] if y else 1 - fixture["pi"]
        probability *= _likelihood(public, y, *fixture["public"])
        for signal in (xa, xb, xc):
            probability *= _likelihood(signal, y, *fixture["private"])
        probability *= _likelihood(truth, y, *fixture["audit"])
        if z is None or public == z:
            rows.append((probability, y, public, (xa, xb, xc), truth))
    if z is not None:
        mass = sum(row[0] for row in rows)
        rows = [(probability / mass, y, public, signals, truth)
                for probability, y, public, signals, truth in rows]
    return rows


def report(action, signal):
    if action == "L0" or action == "H00":
        return 0
    if action == "L1" or action == "H11":
        return 1
    return signal if action == "H01" else 1 - signal


def conditional_match(fixture, z, action, judge=0):
    return sum(probability * F(report(action, signals[judge]) == truth)
               for probability, _, _, signals, truth in _rows(fixture, z))


def best_high_match(fixture, z, judge=0):
    candidates = {action: conditional_match(fixture, z, action, judge)
                  for action in ("H00", "H01", "H10", "H11")}
    action = max(candidates, key=candidates.get)
    return action, candidates[action]


def centered_pair_score(fixture, z, own_action, peer_action, own_judge=0, peer_judge=1):
    rows = _rows(fixture, z)
    own_mean = sum(p * report(own_action, signals[own_judge]) for p, _, _, signals, _ in rows)
    peer_mean = sum(p * report(peer_action, signals[peer_judge]) for p, _, _, signals, _ in rows)
    joint = sum(p * report(own_action, signals[own_judge]) * report(peer_action, signals[peer_judge])
                for p, _, _, signals, _ in rows)
    return joint - own_mean * peer_mean


def quality(fixture, profile_by_z):
    accuracy = fa = fr = F(0)
    rows = _rows(fixture)
    for probability, y, z, signals, _ in rows:
        profile = profile_by_z[z]
        decision = sum(report(action, signals[judge]) for judge, action in enumerate(profile)) >= 2
        accuracy += probability * F(decision == bool(y))
        fa += probability * F(y == 0 and decision)
        fr += probability * F(y == 1 and not decision)
    return {"accuracy": accuracy,
            "false_approval_rate": fa / (1 - fixture["pi"]),
            "false_rejection_rate": fr / fixture["pi"]}


def run_checks():
    expected = {
        "F41-01": (F(43, 50), F(43, 50), F(0)),
        "F41-02": (F(33, 50), F(37, 50), F(2, 25)),
    }
    certificates = {}
    for name, fixture in FIXTURES.items():
        low_matches = []
        high_matches = []
        for z in (0, 1):
            low_action = "L0" if z == 0 else "L1"
            low_matches.append(conditional_match(fixture, z, low_action))
            high_matches.append(best_high_match(fixture, z)[1])
        values = (low_matches[0], high_matches[0], high_matches[0] - low_matches[0])
        if values != expected[name] or tuple(low_matches) != (expected[name][0],) * 2 \
                or tuple(high_matches) != (expected[name][1],) * 2:
            raise AssertionError((name, low_matches, high_matches))
        certificates[name] = {"low_match": low_matches, "high_match": high_matches,
                              "delta": high_matches[0] - low_matches[0]}

    fixture = FIXTURES["F41-02"]
    for z in (0, 1):
        score = centered_pair_score(fixture, z, "H01", "H01")
        direct = sum(
            p * q * (F(report("H01", signals[0]) == report("H01", other[1]))
                     - F(report("H01", signals[0]) == report("H01", signals[1])))
            for p, _, _, signals, _ in _rows(fixture, z)
            for q, _, _, other, _ in _rows(fixture, z)
        )
        # The direct pair expression is the negative of covariance's
        # agreement ordering; normalize it before comparing.
        if score != -direct / 2:
            raise AssertionError((z, score, direct))

    quality_result = quality(fixture, {0: ("H01",) * 3, 1: ("H01",) * 3})
    if quality_result["accuracy"] != F(112, 125):
        raise AssertionError(quality_result)
    return {"status": "passed", "certificates": certificates,
            "quality_F41_02_H01": quality_result,
            "scope": "independent finite fixture checks only"}


if __name__ == "__main__":
    print(run_checks())
