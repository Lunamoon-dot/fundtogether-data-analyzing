"""Independent exact potential-state oracle for the finite V6 RAVE game.

The integration retains all potential private signals and the potential audit
signal, including when effort/audit is absent. No checker or engine is imported.
"""

from fractions import Fraction
from itertools import product


_ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
_BITS = (0, 1)


def _signal_probability(channel, outcome, truth):
    sensitivity, specificity = channel[:2]
    positive = sensitivity if truth else 1 - specificity
    return positive if outcome else 1 - positive


def _potential_states(fixture):
    """Yield all 64 (Y,Z,X_A,X_B,X_C,T) states with their joint mass."""
    pi = fixture["pi"]
    for y, z, xa, xb, xc, t in product(_BITS, repeat=6):
        mass = pi if y else 1 - pi
        mass *= _signal_probability(fixture["public"], z, y)
        private = (xa, xb, xc)
        for channel, x in zip(fixture["private"], private):
            mass *= _signal_probability(channel, x, y)
        mass *= _signal_probability(fixture["audit"], t, y)
        yield y, z, private, t, mass


def decision_table(fixture, losses, calibration="H01"):
    """Construct frozen Bayesian decisions by independent finite-state sums.

    ``mass`` is calibrated P(Z=z,reports=r). Under copyZ calibration,
    off-support rows retain mass zero and use the public posterior fallback.
    """
    if calibration not in ("H01", "copyZ"):
        raise ValueError("calibration must be H01 or copyZ")
    c_fa, c_fr = map(Fraction, losses)
    if c_fa <= 0 or c_fr <= 0:
        raise ValueError("decision losses must be positive")

    keys = tuple(product(_BITS, tuple(product(_BITS, repeat=3))))
    cells = {key: [[Fraction(0) for _ in _BITS] for _ in _BITS]
             for key in keys}
    public_cells = [[[Fraction(0) for _ in _BITS] for _ in _BITS]
                    for _ in _BITS]
    for y, z, private, t, mass in _potential_states(fixture):
        reports = private if calibration == "H01" else (z, z, z)
        cells[z, reports][y][t] += mass
        public_cells[z][y][t] += mass

    threshold = c_fa / (c_fa + c_fr)
    result = {}
    for key in keys:
        weighted = cells[key]
        state_mass = sum((sum(row) for row in weighted), Fraction(0))
        if not state_mass:
            if calibration != "copyZ":
                raise ValueError("H01 calibration requires supported report states")
            weighted = public_cells[key[0]]
        normalizer = sum((sum(row) for row in weighted), Fraction(0))
        if not normalizer:
            raise ValueError("public observation has zero probability")
        posterior = sum(weighted[1]) / normalizer
        unaudited_loss = min(c_fa * (1 - posterior), c_fr * posterior)
        audited_loss = Fraction(0)
        audited_decisions = []
        for t in _BITS:
            audit_mass = weighted[0][t] + weighted[1][t]
            if not audit_mass:
                raise ValueError("audit observation has zero conditional probability")
            audit_posterior = weighted[1][t] / audit_mass
            audited_decisions.append(int(audit_posterior >= threshold))
            audited_loss += min(c_fa * weighted[0][t],
                                c_fr * weighted[1][t]) / normalizer
        result[key] = {
            "posterior": posterior,
            "g0": int(posterior >= threshold),
            "g1": tuple(audited_decisions),
            "mass": state_mass,
            "voi": unaudited_loss - audited_loss,
        }
    return result


def evaluate(fixture, policy, decisions, profile, b=(0, 0, 0)):
    """Sum the 128 potential states, including both actual audit outcomes.

    Returned branch quantities condition on Z; primary metrics weight those
    branches by their actual probability. Effort labels are ``L`` or ``H``.
    """
    if len(profile) != 2 or any(len(branch) != 3 for branch in profile):
        raise ValueError("profile must contain two three-Judge branches")
    if any(action not in _ACTIONS for branch in profile for action in branch):
        raise ValueError("unknown action")
    if len(b) != 3:
        raise ValueError("b must contain three external benefits")
    for z, reports in product(_BITS, tuple(product(_BITS, repeat=3))):
        q = policy["audit"][z, reports]
        if not 0 <= q <= 1:
            raise ValueError("audit probabilities must lie in [0,1]")
        row = decisions[z, reports]
        if row["g0"] not in _BITS or len(row["g1"]) != 2 or any(
                decision not in _BITS for decision in row["g1"]):
            raise ValueError("terminal decisions must be binary")

    zero = Fraction(0)
    totals = {name: zero for name in (
        "preliminary_accuracy", "final_accuracy", "preliminary_fa_joint",
        "preliminary_fr_joint", "final_fa_joint", "final_fr_joint",
        "audit_exposure", "release_probability")}
    truth_mass = [zero, zero]
    audit_truth_mass = [zero, zero]
    public_mass = [zero, zero]
    audit_public_mass = [zero, zero]
    release_public_mass = [zero, zero]
    rewards_public_mass = [[zero for _ in range(3)] for _ in _BITS]

    for y, z, private, t, potential_mass in _potential_states(fixture):
        reports = tuple(int(action[-1]) if action[0] == "L"
                        else int(action[1 + x])
                        for action, x in zip(profile[z], private))
        preliminary = int(sum(reports) >= 2)
        q = policy["audit"][z, reports]
        fixed = decisions[z, reports]
        for a in _BITS:
            mass = potential_mass * (q if a else 1 - q)
            final = fixed["g1"][t] if a else fixed["g0"]
            truth_mass[y] += mass
            public_mass[z] += mass
            totals["preliminary_accuracy"] += mass * (preliminary == y)
            totals["final_accuracy"] += mass * (final == y)
            if not y:
                totals["preliminary_fa_joint"] += mass * preliminary
                totals["final_fa_joint"] += mass * final
            else:
                totals["preliminary_fr_joint"] += mass * (1 - preliminary)
                totals["final_fr_joint"] += mass * (1 - final)
            totals["audit_exposure"] += mass * a
            audit_truth_mass[y] += mass * a
            audit_public_mass[z] += mass * a
            totals["release_probability"] += mass * final
            release_public_mass[z] += mass * final
            for i in range(3):
                reward = policy["f"] + policy["mu"] * a * (reports[i] == t)
                rewards_public_mass[z][i] += mass * reward

    if any(not mass for mass in truth_mass + public_mass):
        raise ValueError("both truth and public branches must have positive mass")
    reward_by_z = tuple(tuple(value / public_mass[z] for value in row)
                        for z, row in enumerate(rewards_public_mass))
    reviewer_payout_by_z = tuple(sum(row) for row in reward_by_z)
    exposure_by_z = tuple(audit_public_mass[z] / public_mass[z] for z in _BITS)
    release_by_z = tuple(release_public_mass[z] / public_mass[z] for z in _BITS)
    effort_by_z = tuple(tuple(action[0] for action in branch) for branch in profile)
    utility_by_z = tuple(tuple(
        reward_by_z[z][i] + b[i] * release_by_z[z]
        - (fixture["private"][i][2] if effort_by_z[z][i] == "H" else zero)
        for i in range(3)) for z in _BITS)
    expected_reward = sum((sum(row) for row in rewards_public_mass), zero)
    expected_audit_cost = policy["kappa"] * totals["audit_exposure"]
    cash = expected_reward + expected_audit_cost + policy["operating_cost"]

    return {
        "preliminary_accuracy": totals["preliminary_accuracy"],
        "final_accuracy": totals["final_accuracy"],
        "preliminary_fa": totals["preliminary_fa_joint"] / truth_mass[0],
        "preliminary_fr": totals["preliminary_fr_joint"] / truth_mass[1],
        "final_fa": totals["final_fa_joint"] / truth_mass[0],
        "final_fr": totals["final_fr_joint"] / truth_mass[1],
        "wrong_payout_value": totals["final_fa_joint"] * policy["payout_value"],
        "expected_decision_loss": policy["c_fa"] * totals["final_fa_joint"]
        + policy["c_fr"] * totals["final_fr_joint"],
        "audit_exposure": totals["audit_exposure"],
        "audit_given_y": tuple(audit_truth_mass[y] / truth_mass[y] for y in _BITS),
        "expected_reviewer_payout": expected_reward,
        "expected_audit_cost": expected_audit_cost,
        "cash_review_cost": cash,
        "reward_cap": 3 * policy["f"] + 3 * policy["mu"],
        "release_probability": totals["release_probability"],
        "utility_by_z": utility_by_z,
        "reward_by_z": reward_by_z,
        "release_by_z": release_by_z,
        "reviewer_payout_by_z": reviewer_payout_by_z,
        "exposure_by_z": exposure_by_z,
        "batch_cash_review_cost": sum((reviewer_payout_by_z[z]
            + policy["kappa"] * exposure_by_z[z] + policy["operating_cost"]
            for z in _BITS), zero) / 2,
        "effort_by_z": effort_by_z,
    }
