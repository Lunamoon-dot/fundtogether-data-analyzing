"""Direct state/six-map oracle. Deliberately imports no production modules.

Q uses squared error; deviations enumerate whole report maps rather than
production's per-observation maximization. Fractions remain exact throughout.
"""

from fractions import Fraction as F
from itertools import product

ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")


def parameters(raw):
    return {k: tuple(map(F, v)) if k == "costs" else F(v)
            for k, v in raw.items() if k != "model_version"}


def worlds(raw):
    p = parameters(raw)
    result = []
    for bits in product((0, 1), repeat=5):
        y, z, *signals = bits
        mass = p["pi"] if y == 1 else 1 - p["pi"]
        mass *= p["a"] if z == y else 1 - p["a"]
        for x in signals:
            mass *= p["b"] if x == y else 1 - p["b"]
        result.append((bits, mass))
    return result


def visible(bits, judge, action):
    return (bits[1], bits[2 + judge]) if action[0] == "H" else (bits[1],)


def reported(bits, judge, action):
    return int(action[1 + bits[2 + judge]]) if action[0] == "H" else int(action[1])


def forecasts(rows, profile):
    tables = []
    for i in range(3):
        masses, ones = {}, {}
        for bits, mass in rows:
            actions = profile[str(bits[1])]
            key = visible(bits, i, actions[i])
            masses[key] = masses.get(key, F(0)) + mass
            ones[key] = ones.get(key, F(0)) + mass * reported(bits, (i + 2) % 3, actions[(i + 2) % 3])
        tables.append({key: ones[key] / mass for key, mass in masses.items()})
    return tables


def payoff(raw, profile, tables, judge, z, trial=None, trial_predictions=None, mechanism="rbts"):
    """Use original peer tables even when trial changes focal action."""
    p = parameters(raw)
    rows = [(s, w) for s, w in worlds(raw) if s[1] == z]
    mass = sum(w for _, w in rows)
    action = trial or profile[str(z)][judge]
    if trial_predictions is None:
        if trial is None:
            trial_predictions = tables[judge]
        else:
            partitions = {}
            for s, w in rows:
                key = visible(s, judge, action)
                partitions.setdefault(key, []).append((s, w))
            k = (judge + 2) % 3
            trial_predictions = {
                key: sum(w * reported(s, k, profile[str(z)][k]) for s, w in group) / sum(w for _, w in group)
                for key, group in partitions.items()
            }
    information = prediction = F(0)
    j, k = (judge + 1) % 3, (judge + 2) % 3
    for s, w in rows:
        actions = profile[str(z)]
        ref = tables[j][visible(s, j, actions[j])]
        rk = reported(s, k, actions[k])
        r = reported(s, judge, action)
        shadow = ref + (2 * r - 1) * min(ref, 1 - ref)
        own = trial_predictions[visible(s, judge, action)]
        information += w / mass * (1 - (shadow - rk) ** 2)
        prediction += w / mass * (1 - (own - rk) ** 2)
    score = information + prediction
    reward = p["fixed_reward"] if mechanism == "fixed" else p["f"] + p["lambda"] * score
    cost = p["costs"][judge] if action[0] == "H" else F(0)
    return {"information": information, "prediction": prediction, "score": score,
            "reward": reward, "cost": cost, "utility": reward - cost,
            "predictions": trial_predictions}


def analyze(raw, profile, mechanism="rbts"):
    rows = worlds(raw)
    tables = forecasts(rows, profile)
    records = []
    for i in range(3):
        for z in (0, 1):
            trials = {a: payoff(raw, profile, tables, i, z, a, mechanism=mechanism) for a in ACTIONS}
            candidate = payoff(raw, profile, tables, i, z, mechanism=mechanism)
            low = max(trials[a]["utility"] for a in ACTIONS[:2])
            high = max(trials[a]["utility"] for a in ACTIONS[2:])
            best = max(low, high)
            records.append({"judge": i, "z": z, "candidate": candidate, "trials": trials,
                            "low_utility": low, "high_utility": high, "delta": high - low,
                            "regret": best - candidate["utility"],
                            "optimal_actions": [a for a in ACTIONS if trials[a]["utility"] == best]})
    correct = fp = fn = approvals = F(0)
    for s, w in rows:
        decision = int(sum(reported(s, i, profile[str(s[1])][i]) for i in range(3)) >= 2)
        correct += w * (decision == s[0])
        fp += w * (s[0] == 0 and decision == 1)
        fn += w * (s[0] == 1 and decision == 0)
        approvals += w * decision
    p = parameters(raw)
    return {"tables": tables, "branches": records, "accuracy": correct,
            "wrong_payout_value": p["payout_value"] * fp,
            "false_approval_rate": fp / (1 - p["pi"]), "false_rejection_rate": fn / p["pi"],
            "expected_payout": p["payout_value"] * approvals}


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def branch_payoff_table(raw, z, actions, mechanism="rbts"):
    """Cached *payoffs*, never equilibrium flags. Full config/action keys owned by caller."""
    profile = {"0": list(actions), "1": list(actions)}
    rows = [(s, w) for s, w in worlds(raw) if s[1] == z]
    tables = forecasts(rows, profile)
    return tuple(tuple(payoff(raw, profile, tables, i, z, action, mechanism=mechanism)["utility"]
                       for action in ACTIONS) for i in range(3))


def full_profile_enumeration(raw, mechanism="rbts", on_progress=None):
    """T17: compare all 36 deviations/judge for all 46,656 full candidates.

    Caches exact state-integrated payoffs conditional on a full branch action
    tuple. No branch equilibrium solver/flags or product of equilibrium sets.
    Converts common-denominator payoff vectors to integers before repeated
    ex-ante comparisons, preserving exact ordering and ties.
    """
    from math import lcm

    tuples = tuple(product(ACTIONS, repeat=3))
    probabilities = [sum(w for s, w in worlds(raw) if s[1] == z) for z in (0, 1)]
    table = {}
    for z in (0, 1):
        for actions in tuples:
            values = branch_payoff_table(raw, z, actions, mechanism)
            table[z, actions] = tuple(tuple(probabilities[z] * u for u in row) for row in values)
        if on_progress:
            on_progress({"phase": "oracle_payoffs", "completed": (z + 1) * 216, "total": 432})
    # A global denominator is only a lossless arithmetic representation.
    denominator = lcm(*(u.denominator for values in table.values() for row in values for u in row))
    integers = {key: tuple(tuple(int(u * denominator) for u in row) for row in values) for key, values in table.items()}
    retained = set()
    comparisons = 0
    for branch0 in tuples:
        for branch1 in tuples:
            equilibrium = True
            for i in range(3):
                low = integers[0, branch0][i]
                high = integers[1, branch1][i]
                own = low[ACTIONS.index(branch0[i])] + high[ACTIONS.index(branch1[i])]
                for action0, action1 in product(range(6), repeat=2):
                    comparisons += 1
                    if low[action0] + high[action1] > own:
                        equilibrium = False
            if equilibrium:
                retained.add((branch0, branch1))
    return retained, {"profiles_checked": 46656, "full_strategy_deviations_compared": comparisons,
                      "conditional_payoffs_integrated": 2 * 216 * 3 * 6,
                      "payoff_cache_keys": "full raw config, mechanism, z, branch tuple, judge, trial action",
                      "common_denominator": str(denominator), "arithmetic": "exact_integer_ratios"}
