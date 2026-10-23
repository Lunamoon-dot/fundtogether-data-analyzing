"""Independent V3 oracle. It deliberately imports no ceav_m1 production module."""

from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path


ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
JUDGES = ("A", "B", "C")


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def parsed(raw):
    return {
        "pi": F(raw["pi"]),
        "public": tuple(F(raw["public_signal"][key]) for key in ("sensitivity", "specificity")),
        "private": tuple(tuple(F(raw["judges"][judge]["private_signal"][key]) for key in ("sensitivity", "specificity")) for judge in JUDGES),
        "costs": tuple(F(raw["judges"][judge]["high_effort_cost"]) for judge in JUDGES),
        "q": F(raw["verification_anchor"]["audit_probability"]),
        "verification": tuple(F(raw["verification_anchor"][key]) for key in ("sensitivity", "specificity")),
        "audit_cost": F(raw["verification_anchor"]["cost_per_audit"]),
        "f": F(raw["f"]),
        "lambda": F(raw["lambda_peer"]),
        "mu": F(raw["anchor_weight"]),
        "payout": F(raw["payout_value"]),
    }


def enumerate_states(raw):
    cfg = parsed(raw)
    rows = []
    for state_id, bits in enumerate(product((0, 1), repeat=7)):
        y, z, xa, xb, xc, audit, verification = bits
        mass = cfg["pi"] if y else 1 - cfg["pi"]
        mass *= likelihood(z, y, *cfg["public"])
        for value, pair in zip((xa, xb, xc), cfg["private"]):
            mass *= likelihood(value, y, *pair)
        mass *= cfg["q"] if audit else 1 - cfg["q"]
        mass *= likelihood(verification, y, *cfg["verification"])
        rows.append({"state_id": state_id, "y": y, "z": z, "signals": (xa, xb, xc),
                     "audit": audit, "verification": verification, "probability": mass})
    assert len(rows) == 128 and sum(row["probability"] for row in rows) == 1
    return rows


def report_for(action, x=None):
    return int(action[1]) if action[0] == "L" else int(action[1 + x])


def observation(row, judge, effort):
    return (row["z"],) if effort == "L" else (row["z"], row["signals"][judge])


def predictions(profile, rows):
    tables = []
    for judge in range(3):
        groups = {}
        peer = (judge + 2) % 3
        for row in rows:
            actions = profile[str(row["z"])]
            own_obs = observation(row, judge, actions[judge][0])
            peer_report = report_for(actions[peer], row["signals"][peer] if actions[peer][0] == "H" else None)
            mass, ones = groups.get(own_obs, (F(0), F(0)))
            groups[own_obs] = (mass + row["probability"], ones + row["probability"] * peer_report)
        tables.append({key: ones / mass for key, (mass, ones) in groups.items() if mass})
    return tables


def quadratic(p, report):
    return 2 * p - p * p if report else 1 - p * p


def peer_score(reports, forecasts, judge):
    reference, peer = (judge + 1) % 3, (judge + 2) % 3
    p_ref = forecasts[reference]
    shadow = p_ref + (2 * reports[judge] - 1) * min(p_ref, 1 - p_ref)
    return quadratic(shadow, reports[peer]) + quadratic(forecasts[judge], reports[peer])


def evaluate(raw, profile):
    cfg, rows = parsed(raw), enumerate_states(raw)
    tables = predictions(profile, rows)
    totals = [{key: F(0) for key in ("peer_score", "anchor_score", "peer_reward", "anchor_reward", "reward", "effort_cost", "utility")} for _ in range(3)]
    conditional = [[{key: F(0) for key in totals[0]} for _ in range(2)] for _ in range(3)]
    branch_mass = [sum(row["probability"] for row in rows if row["z"] == z) for z in (0, 1)]
    accuracy = false_approval = false_rejection = approvals = F(0)
    for row in rows:
        actions = profile[str(row["z"])]
        reports = tuple(report_for(action, row["signals"][i] if action[0] == "H" else None) for i, action in enumerate(actions))
        forecasts = tuple(tables[i][observation(row, i, actions[i][0])] for i in range(3))
        decision = int(sum(reports) >= 2)
        accuracy += row["probability"] * (decision == row["y"])
        false_approval += row["probability"] * (row["y"] == 0 and decision == 1)
        false_rejection += row["probability"] * (row["y"] == 1 and decision == 0)
        approvals += row["probability"] * decision
        for judge, action in enumerate(actions):
            peer = peer_score(reports, forecasts, judge)
            anchor = F(row["audit"] and reports[judge] == row["verification"])
            peer_reward = cfg["f"] + cfg["lambda"] * peer
            anchor_reward = cfg["mu"] * anchor
            cost = cfg["costs"][judge] if action[0] == "H" else F(0)
            values = {"peer_score": peer, "anchor_score": anchor, "peer_reward": peer_reward,
                      "anchor_reward": anchor_reward, "reward": peer_reward + anchor_reward,
                      "effort_cost": cost, "utility": peer_reward + anchor_reward - cost}
            for key, value in values.items():
                totals[judge][key] += row["probability"] * value
                conditional[judge][row["z"]][key] += row["probability"] / branch_mass[row["z"]] * value
    metrics = {"accuracy": accuracy, "false_approval_rate": false_approval / (1 - cfg["pi"]),
               "false_rejection_rate": false_rejection / cfg["pi"], "wrong_payout_probability": false_approval,
               "wrong_payout_value": cfg["payout"] * false_approval, "expected_payout": cfg["payout"] * approvals,
               "expected_peer_reward_total": sum(row["peer_reward"] for row in totals),
               "expected_anchor_reward_total": sum(row["anchor_reward"] for row in totals),
               "expected_reward_total": sum(row["reward"] for row in totals),
               "expected_effort_cost": sum(row["effort_cost"] for row in totals),
               "expected_audit_cost": cfg["q"] * cfg["audit_cost"]}
    metrics["operating_cost"] = F(raw.get("operating_cost", "0"))
    metrics["cash_review_cost"] = (metrics["expected_reward_total"] + metrics["operating_cost"]
                                   + metrics["expected_audit_cost"])
    return {"rows": rows, "predictions": tables, "totals": totals, "conditional": conditional,
            "branch_mass": branch_mass, "metrics": metrics}


def best_response(raw, profile, judge, z, evaluated=None):
    cfg, result = parsed(raw), evaluated or evaluate(raw, profile)
    rows, tables = result["rows"], result["predictions"]
    branch = [row for row in rows if row["z"] == z]
    mass = sum(row["probability"] for row in branch)
    reference, peer = (judge + 1) % 3, (judge + 2) % 3
    options = {}
    for action in ACTIONS:
        groups = {}
        for row in branch:
            groups.setdefault(observation(row, judge, action[0]), []).append(row)
        expected_peer = expected_anchor = F(0)
        for own_obs, group in groups.items():
            group_mass = sum(row["probability"] for row in group)
            q_peer = F(0)
            for row in group:
                actions = profile[str(z)]
                peer_action = actions[peer]
                q_peer += row["probability"] / group_mass * report_for(peer_action, row["signals"][peer] if peer_action[0] == "H" else None)
            own_prediction = q_peer if cfg["lambda"] else F(0)
            report = report_for(action, own_obs[1] if action[0] == "H" else None)
            for row in group:
                weight = row["probability"] / mass
                actions = profile[str(z)]
                reports = [report_for(a, row["signals"][i] if a[0] == "H" else None) for i, a in enumerate(actions)]
                reports[judge] = report
                forecasts = [tables[i][observation(row, i, actions[i][0])] for i in range(3)]
                forecasts[judge] = own_prediction
                expected_peer += weight * peer_score(tuple(reports), tuple(forecasts), judge)
                expected_anchor += weight * F(row["audit"] and report == row["verification"])
        peer_reward = cfg["f"] + cfg["lambda"] * expected_peer
        anchor_reward = cfg["mu"] * expected_anchor
        cost = cfg["costs"][judge] if action[0] == "H" else F(0)
        options[action] = {"peer_score": expected_peer, "anchor_score": expected_anchor,
                           "peer_reward": peer_reward, "anchor_reward": anchor_reward,
                           "utility": peer_reward + anchor_reward - cost}
    best = max(item["utility"] for item in options.values())
    optimal = [action for action in ACTIONS if options[action]["utility"] == best]
    candidate_action = profile[str(z)][judge]
    candidate_utility = result["conditional"][judge][z]["utility"]
    return {"candidate_action": candidate_action, "candidate_utility": candidate_utility,
            "best_utility": best, "regret": best - candidate_utility, "optimal_actions": optimal,
            "options": options}


def branch_equilibria(raw, z):
    retained = []
    for actions in product(ACTIONS, repeat=3):
        profile = {"0": list(actions), "1": list(actions)}
        result = evaluate(raw, profile)
        if all(best_response(raw, profile, judge, z, result)["regret"] == 0 for judge in range(3)):
            retained.append(f"z{z}:" + ",".join(actions))
    return retained


def equilibrium_summary(raw):
    branches = {str(z): branch_equilibria(raw, z) for z in (0, 1)}
    metric_keys = ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value",
                   "expected_reward_total", "expected_effort_cost", "expected_audit_cost", "cash_review_cost")
    records = []
    for left, right in product(branches["0"], branches["1"]):
        profile = {"0": left.split(":", 1)[1].split(","), "1": right.split(":", 1)[1].split(",")}
        metrics = evaluate(raw, profile)["metrics"]
        records.append({"profile": profile, "metrics": {key: metrics[key] for key in metric_keys}})
    if not records:
        return {"status": "no_pure_equilibrium", "count": 0}
    ranges = {key: {"min": min(row["metrics"][key] for row in records),
                    "max": max(row["metrics"][key] for row in records)} for key in metric_keys}
    best_accuracy = max(records, key=lambda row: (row["metrics"]["accuracy"], str(row["profile"])))
    worst_accuracy = min(records, key=lambda row: (row["metrics"]["accuracy"], str(row["profile"])))
    return {"status": "pure_equilibria_evaluated", "count": len(records), "ranges": ranges,
            "best_accuracy": best_accuracy, "worst_accuracy": worst_accuracy}


def fixture(raw, profile):
    result = evaluate(raw, profile)
    selected_ids = (0, 1, 2, 3, 32, 63, 64, 96, 127)
    return {
        "fixture_version": "v3-anchor-oracle-r1",
        "selected_state_masses": {str(i): str(result["rows"][i]["probability"]) for i in selected_ids},
        "support_size": sum(row["probability"] > 0 for row in result["rows"]),
        "candidate_metrics": {key: str(value) for key, value in result["metrics"].items()},
        "candidate_totals": [{key: str(value) for key, value in row.items()} for row in result["totals"]],
        "best_responses": {f"{JUDGES[judge]}-z{z}": {
            "candidate_action": (br := best_response(raw, profile, judge, z, result))["candidate_action"],
            "best_utility": str(br["best_utility"]), "regret": str(br["regret"]),
            "optimal_actions": br["optimal_actions"]
        } for judge in range(3) for z in (0, 1)},
        "branch_equilibria": {str(z): branch_equilibria(raw, z) for z in (0, 1)},
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    raw = json.loads((root / "configs/v3/heterogeneous_anchor.json").read_text(encoding="utf-8"))
    profile = json.loads((root / "configs/all_high.json").read_text(encoding="utf-8"))
    print(json.dumps(fixture(raw, profile), indent=2, sort_keys=True))
