"""Complete unilateral optimization with peer behavior frozen."""

from fractions import Fraction as F
from itertools import product

from .model import JUDGES, observe
from .scoring import quadratic
from .strategies import ACTIONS, observation_key, realized


def solve_branch(config, frozen_candidate, judge, z, mechanism="rbts", candidate_payoff=None):
    candidate = frozen_candidate
    if candidate_payoff is None:
        from .evaluate import evaluate
        candidate_payoff = evaluate(config, candidate, mechanism)["conditional"][judge][z]
    rows = [state for state in candidate.rows if state.z == z]
    mass = sum(s.probability for s in rows)
    j, k = (judge + 1) % 3, (judge + 2) % 3
    frozen_rows = [(s, *realized(candidate, s)) for s in rows]
    options = {}
    constant = mechanism == "fixed" or config.multiplier == 0
    for effort in ("L", "H"):
        from .strategies import Profile, build_candidate
        branches = [list(branch) for branch in candidate.profile.branches]
        branches[z][judge] = "L0" if effort == "L" else "H01"
        rebuilt = build_candidate(config, Profile(tuple(tuple(b) for b in branches)), mechanism=mechanism)
        frozen_rows = [(s, *realized(rebuilt, s)) for s in rows]
        groups = {}
        for s, reports, predictions in frozen_rows:
            groups.setdefault(observe(s, judge, effort), []).append((s, reports, predictions))
        observations, information, prediction = [], F(0), F(0)
        for obs, group in groups.items():
            group_mass = sum(s.probability for s, _, _ in group)
            q = sum(s.probability * reports[k] for s, reports, _ in group) / group_mass
            values = []
            for r in (0, 1):
                total = F(0)
                for s, reports, predictions in group:
                    ref = predictions[j]
                    shadow = ref + (2 * r - 1) * min(ref, 1 - ref)
                    total += s.probability / group_mass * quadratic(shadow, reports[k])
                values.append(total)
            best = max(values)
            reports = [r for r in (0, 1) if values[r] == best]
            optimal_prediction_score = 1 - q + q * q
            information += group_mass / mass * best
            prediction += group_mass / mass * optimal_prediction_score
            observations.append({"observation": observation_key(obs), "probability_given_z": group_mass / mass,
                                 "information_by_report": values, "optimal_reports": [0, 1] if constant else reports,
                                 "optimal_prediction": q, "optimal_prediction_score": optimal_prediction_score,
                                 "score_optimal_reports": reports})
        score = information + prediction
        base_reward = config.fixed_reward if mechanism == "fixed" else config.f + config.multiplier * score
        utility = base_reward - (config.costs[judge] if effort == "H" else F(0))
        maps = ["".join(map(str, rs)) for rs in product(*(o["optimal_reports"] for o in observations))]
        options[effort] = {"information_score": information, "prediction_score": prediction, "score": score,
                           "utility": utility, "observations": observations,
                           "optimal_actions": [effort + report_map for report_map in maps]}
    assert options["H"]["score"] >= options["L"]["score"], "Value-of-information invariant failed"
    best = max(option["utility"] for option in options.values())
    efforts = [effort for effort in ("L", "H") if options[effort]["utility"] == best]
    regret = best - candidate_payoff["utility"]
    assert regret >= 0, "Negative regret is a calculation error"
    optimal_actions = [action for action in ACTIONS if action[0] in efforts and action in options[action[0]]["optimal_actions"]]
    witness = None
    if regret > 0:
        action = optimal_actions[0]
        observations = options[action[0]]["observations"]
        witness = {"judge": JUDGES[judge], "z": z, "action": action,
                   "prediction_map": [{"observation": o["observation"], "prediction": o["optimal_prediction"]} for o in observations],
                   "old_utility": candidate_payoff["utility"], "new_utility": best,
                   "conditional_gain": regret, "ex_ante_gain": mass * regret,
                   "peer_predictions_remain_candidate_tables": True}
    return {"judge": JUDGES[judge], "z": z, "branch_probability": mass,
            "reference_judge": JUDGES[j], "scoring_peer_judge": JUDGES[k],
            "candidate_action": candidate.profile.branches[z][judge], "candidate": candidate_payoff,
            "low": options["L"], "high": options["H"], "delta_utility": options["H"]["utility"] - options["L"]["utility"],
            "best_utility": best, "best_efforts": efforts, "optimal_actions": optimal_actions, "regret": regret,
            "report_optimum": "any_admissible_map" if constant else "listed_report_maps",
            "prediction_optimum": "any_in_unit_interval" if constant else "unique_on_reachable_observations",
            "witness": witness,
            "frozen_peer_tables": [{"judge": JUDGES[peer], "table": [{"observation": observation_key(obs), "prediction": p} for obs, p in candidate.predictions[peer]]} for peer in (j, k)]}
