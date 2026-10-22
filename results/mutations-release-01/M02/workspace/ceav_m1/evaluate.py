"""State-level accounting, separate from focal optimization."""

from fractions import Fraction as F

from .model import JUDGES
from .scoring import reward, score_judge
from .strategies import build_candidate, observation_key, realized

SCOPE = {"strategy_scope": "pure_effort_report_with_continuous_optimal_predictions",
         "equilibrium_concept": "pure_strategy_nash_in_reduced_normal_form", "scoring_rule": "rbts_eq8",
         "effort_timing": "after_public_signal", "arithmetic": "rational_exact",
         "peer_tables_frozen_on_deviation": True, "claims_mixed_equilibrium_coverage": False,
         "claims_equilibrium_selection": False}


def evaluate(config, candidate, mechanism="rbts"):
    states, totals = [], [{key: F(0) for key in ("score", "reward", "effort_cost", "utility")} for _ in range(3)]
    branch_mass = [sum(s.probability for s in candidate.rows if s.z == z) for z in (0, 1)]
    conditional = [[{key: F(0) for key in ("score", "reward", "effort_cost", "utility")} for _ in range(2)] for _ in range(3)]
    accuracy = fp = fn = approvals = F(0)
    for state in candidate.rows:
        reports, predictions = realized(candidate, state)
        decision = int(sum(reports) >= 2)
        record = {"state_id": state.state_id, "y": state.y, "z": state.z,
                  "x_A": state.signals[0], "x_B": state.signals[1], "x_C": state.signals[2],
                  "probability": state.probability, "decision": decision,
                  "wrong_payout_contribution": config.payout_value * state.probability * (state.y == 0 and decision == 1)}
        for i, label in enumerate(JUDGES):
            score = score_judge(reports, predictions, i)
            action = candidate.profile.branches[state.z][i]
            paid = reward(score["total_score"], mechanism, config)
            cost = config.costs[i] if action[0] == "H" else F(0)
            values = {"score": score["total_score"], "reward": paid, "effort_cost": cost, "utility": paid - cost}
            for key, value in values.items():
                totals[i][key] += state.probability * value
                conditional[i][state.z][key] += state.probability / branch_mass[state.z] * value
            record.update({f"{label}_action": action, f"{label}_report": reports[i], f"{label}_prediction": predictions[i]})
            record.update({f"{label}_{key}": value for key, value in score.items()})
            record.update({f"{label}_{key}": value for key, value in values.items()})
        states.append(record)
        accuracy += state.probability * (decision == state.y)
        fp += state.probability * (state.y == 0 and decision == 1)
        fn += state.probability * (state.y == 1 and decision == 0)
        approvals += state.probability * decision
    reward_total = sum(row["reward"] for row in totals)
    effort_cost = sum(row["effort_cost"] for row in totals)
    metrics = {"accuracy": accuracy, "false_approval_rate": fp / (1 - config.pi), "false_rejection_rate": fn / config.pi,
               "wrong_payout_probability": fp, "wrong_payout_value": config.payout_value * fp,
               "expected_payout": config.payout_value * approvals, "expected_reward_total": reward_total,
               "expected_effort_cost": effort_cost, "expected_judge_utility": [row["utility"] for row in totals],
               "operating_cost": config.operating_cost, "cash_review_cost": reward_total + config.operating_cost}
    cap = 3 * config.fixed_reward if mechanism == "fixed" else 3 * config.f + 6 * config.multiplier
    assert reward_total <= cap <= config.reward_budget
    return {"metrics": metrics, "judges": totals, "conditional": conditional, "states": states,
            "branch_masses": branch_mass, "reward_cap": cap, "reward_budget": config.reward_budget}


def analyze(config, profile, mechanism="rbts"):
    from .best_response import solve_branch

    candidate = build_candidate(config, profile, mechanism=mechanism)
    result = evaluate(config, candidate, mechanism)
    certificates = [solve_branch(config, candidate, i, z, mechanism, result["conditional"][i][z])
                    for i in range(3) for z in (0, 1)]
    maximum = F(0) if all(sum(c["branch_probability"] * c["delta_utility"] for c in certificates if c["judge"] == label) >= 0 for label in JUDGES) else max(c["regret"] for c in certificates)
    return {**SCOPE, **result, "mechanism": mechanism, "config": config.raw(), "profile": profile.raw(),
            "prediction_semantics": candidate.prediction_semantics,
            "predictions": [[{"observation": observation_key(obs), "prediction": p} for obs, p in table] for table in candidate.predictions],
            "best_responses": certificates, "max_regret": maximum,
            "equilibrium_status": "exact_pure_equilibrium" if maximum == 0 else "not_equilibrium",
            "status": "succeeded"}
