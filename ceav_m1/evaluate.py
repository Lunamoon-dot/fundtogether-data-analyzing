"""State-level accounting, separate from focal optimization."""

from fractions import Fraction as F

from . import V32_MODEL_VERSION, V33_MODEL_VERSION
from .model import JUDGES, signal_diagnostics
from .signals import audit_probability_for_report
from .scoring import anchor_score, reward, score_judge
from .strategies import build_candidate, observation_key, realized

SCOPE = {"strategy_scope": "pure_effort_report_with_continuous_optimal_predictions",
         "equilibrium_concept": "pure_strategy_nash_in_reduced_normal_form", "scoring_rule": "rbts_eq8",
         "effort_timing": "after_public_signal", "arithmetic": "rational_exact",
         "peer_tables_frozen_on_deviation": True, "claims_mixed_equilibrium_coverage": False,
         "claims_equilibrium_selection": False}


def scope_for(mechanism):
    if mechanism != "hybrid_anchor":
        return SCOPE
    return {**SCOPE, "scoring_rule": "hybrid_rbts_plus_verification_anchor",
            "verification_timing": "after_reports_locked", "ground_truth_used_for_reward": False}


def evaluate(config, candidate, mechanism="rbts"):
    hybrid = mechanism == "hybrid_anchor"
    total_keys = ("score", "peer_score", "anchor_score", "peer_reward", "anchor_reward", "reward", "effort_cost", "utility") if hybrid else ("score", "reward", "effort_cost", "utility")
    states, totals = [], [{key: F(0) for key in total_keys} for _ in range(3)]
    branch_mass = [sum(s.probability for s in candidate.rows if s.z == z) for z in (0, 1)]
    conditional = [[{key: F(0) for key in total_keys} for _ in range(2)] for _ in range(3)]
    verification_matches = [F(0), F(0), F(0)]
    audit_exposure = [F(0), F(0), F(0)]
    report_sensitive = config.model_version in (V32_MODEL_VERSION, V33_MODEL_VERSION)
    ipw = config.model_version == V33_MODEL_VERSION
    anchor_second_moment = [F(0), F(0), F(0)]
    anchor_cross_moment = [[F(0) for _ in range(3)] for _ in range(3)]
    report_one_rate = [F(0), F(0), F(0)]
    report_one_by_y = [[F(0), F(0)] for _ in range(3)]
    accuracy = fp = fn = approvals = F(0)
    for state in candidate.rows:
        reports, predictions = realized(candidate, state)
        decision = int(sum(reports) >= 2)
        record = {"state_id": state.state_id, "y": state.y, "z": state.z,
                  "x_A": state.signals[0], "x_B": state.signals[1], "x_C": state.signals[2],
                  "probability": state.probability, "decision": decision,
                  "wrong_payout_contribution": config.payout_value * state.probability * (state.y == 0 and decision == 1)}
        if hybrid:
            record.update(audit=state.audit, verification=state.verification)
        for i, label in enumerate(JUDGES):
            score = score_judge(reports, predictions, i)
            action = candidate.profile.branches[state.z][i]
            audit_probability = audit_probability_for_report(config, reports[i]) if hybrid else F(0)
            anchor = ((reports[i] == state.verification) if ipw else audit_probability * (reports[i] == state.verification) if report_sensitive else
                      anchor_score(reports[i], state.audit, state.verification) if hybrid else F(0))
            paid = reward(score["total_score"], mechanism, config, anchor)
            cost = config.costs[i] if action[0] == "H" else F(0)
            values = {"score": score["total_score"], "reward": paid, "effort_cost": cost, "utility": paid - cost}
            if hybrid:
                peer_reward = config.f + config.multiplier * score["total_score"]
                values.update(peer_score=score["total_score"], anchor_score=anchor, peer_reward=peer_reward,
                              anchor_reward=config.anchor_weight * anchor)
                verification_matches[i] += state.probability * (anchor if report_sensitive else (reports[i] == state.verification))
                audit_exposure[i] += state.probability * audit_probability
                if ipw and reports[i] == state.verification:
                    anchor_second_moment[i] += state.probability * config.anchor_weight * config.anchor_weight / audit_probability
                if ipw:
                    for j in range(3):
                        if reports[i] == state.verification and reports[j] == state.verification:
                            factor = (config.anchor_weight * config.anchor_weight / audit_probability
                                      if i == j else config.anchor_weight * config.anchor_weight)
                            anchor_cross_moment[i][j] += state.probability * factor
            for key, value in values.items():
                totals[i][key] += state.probability * value
                conditional[i][state.z][key] += state.probability / branch_mass[state.z] * value
            record.update({f"{label}_action": action, f"{label}_report": reports[i], f"{label}_prediction": predictions[i]})
            record.update({f"{label}_{key}": value for key, value in score.items()})
            record.update({f"{label}_{key}": value for key, value in values.items()})
            if report_sensitive:
                record[f"{label}_audit_probability"] = audit_probability
        states.append(record)
        accuracy += state.probability * (decision == state.y)
        fp += state.probability * (state.y == 0 and decision == 1)
        fn += state.probability * (state.y == 1 and decision == 0)
        approvals += state.probability * decision
        for i, report in enumerate(reports):
            report_one_rate[i] += state.probability * report
            report_one_by_y[i][state.y] += state.probability * report
    reward_total = sum(row["reward"] for row in totals)
    effort_cost = sum(row["effort_cost"] for row in totals)
    metrics = {"accuracy": accuracy, "false_approval_rate": fp / (1 - config.pi), "false_rejection_rate": fn / config.pi,
               "wrong_payout_probability": fp, "wrong_payout_value": config.payout_value * fp,
               "expected_payout": config.payout_value * approvals, "expected_reward_total": reward_total,
               "expected_effort_cost": effort_cost, "expected_judge_utility": [row["utility"] for row in totals],
               "operating_cost": config.operating_cost, "cash_review_cost": reward_total + config.operating_cost}
    metrics.update(report_one_rate=report_one_rate,
                   report_one_rate_by_y=[[values[0] / (1 - config.pi), values[1] / config.pi] for values in report_one_by_y])
    if hybrid:
        expected_audit_cost = ((sum(audit_exposure) * config.audit_cost_per_audit) if report_sensitive else
                               config.audit_probability * config.audit_cost_per_audit)
        metrics.update(expected_peer_reward_total=sum(row["peer_reward"] for row in totals),
                       expected_anchor_reward_total=sum(row["anchor_reward"] for row in totals),
                       verification_agreement=verification_matches,
                       expected_audit_cost=expected_audit_cost,
                       cash_review_cost=reward_total + config.operating_cost + expected_audit_cost)
        if ipw:
            metrics.update(anchor_reward_second_moment=anchor_second_moment,
                           anchor_reward_variance=[anchor_second_moment[i] - totals[i]["anchor_reward"] ** 2 for i in range(3)],
                           anchor_reward_covariance=[[anchor_cross_moment[i][j] - totals[i]["anchor_reward"] * totals[j]["anchor_reward"] for j in range(3)] for i in range(3)],
                           max_realized_anchor_payment=config.anchor_weight / min(config.audit_probability_by_report),
                           payment_cap_ratio=(config.anchor_weight / min(config.audit_probability_by_report)) / config.reward_budget)
    cap = (3 * config.fixed_reward if mechanism == "fixed" else
           3 * config.f + 6 * config.multiplier +
           (3 * config.anchor_weight / min(config.audit_probability_by_report) if ipw else
            3 * config.anchor_weight if hybrid else 0))
    assert reward_total <= cap <= config.reward_budget
    if report_sensitive:
        metrics["expected_audit_exposure"] = audit_exposure
    return {"metrics": metrics, "judges": totals, "conditional": conditional, "states": states,
            "branch_masses": branch_mass, "reward_cap": cap, "reward_budget": config.reward_budget,
            "state_support_size": sum(state.probability > 0 for state in candidate.rows)}


def analyze(config, profile, mechanism="rbts"):
    from .best_response import solve_branch

    candidate = build_candidate(config, profile, mechanism=mechanism)
    result = evaluate(config, candidate, mechanism)
    certificates = [solve_branch(config, candidate, i, z, mechanism, result["conditional"][i][z])
                    for i in range(3) for z in (0, 1)]
    maximum = max(c["regret"] for c in certificates)
    return {**scope_for(mechanism), **result, "mechanism": mechanism, "config": config.raw(), "profile": profile.raw(),
            "signal_diagnostics": signal_diagnostics(config),
            "prediction_semantics": candidate.prediction_semantics,
            "predictions": [[{"observation": observation_key(obs), "prediction": p} for obs, p in table] for table in candidate.predictions],
            "best_responses": certificates, "max_regret": maximum,
            "equilibrium_status": "exact_pure_equilibrium" if maximum == 0 else "not_equilibrium",
            "status": "succeeded"}
