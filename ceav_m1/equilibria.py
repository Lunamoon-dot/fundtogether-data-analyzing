"""All six effort/report actions per judge, separately for each public branch."""

from itertools import product

from .best_response import solve_branch
from .evaluate import evaluate, scope_for
from .strategies import ACTIONS, Profile, build_candidate, observation_key
from .model import enumerate_states


class CancelledError(Exception):
    pass


EQUILIBRIUM_METRICS = (
    "accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value",
    "expected_reward_total", "expected_effort_cost", "expected_audit_cost", "cash_review_cost",
)


def summarize_equilibrium_metrics(config, search, mechanism="hybrid_anchor"):
    """Evaluate every retained full pure equilibrium without substituting candidate metrics."""
    if not search.get("enumeration_completed") or search.get("branch_candidate_count") != 432:
        raise ValueError("Equilibrium metrics require a completed exhaustive 432-candidate search")
    retained = {}
    for z in ("0", "1"):
        retained[z] = [row for row in search["branches"][z]["candidates"] if row["accepted"]]
    count = len(retained["0"]) * len(retained["1"])
    if count != search["full_equilibrium_count"]:
        raise AssertionError("Retained branch equilibria do not reproduce full equilibrium count")
    if count == 0:
        return {"status": "no_pure_equilibrium", "count": 0}

    rows = enumerate_states(config)
    ranges = {key: {"min": None, "max": None} for key in EQUILIBRIUM_METRICS}
    best = worst = None
    for left, right in product(retained["0"], retained["1"]):
        profile = Profile((tuple(left["actions"]), tuple(right["actions"])))
        metrics = evaluate(config, build_candidate(config, profile, rows=rows, mechanism=mechanism), mechanism)["metrics"]
        selected = {key: metrics[key] for key in EQUILIBRIUM_METRICS}
        record = {"profile": profile.raw(), "metrics": selected}
        profile_key = tuple(profile.branches[0] + profile.branches[1])
        for key, value in selected.items():
            ranges[key]["min"] = value if ranges[key]["min"] is None else min(ranges[key]["min"], value)
            ranges[key]["max"] = value if ranges[key]["max"] is None else max(ranges[key]["max"], value)
        if best is None or selected["accuracy"] > best[0] or (selected["accuracy"] == best[0] and profile_key < best[1]):
            best = (selected["accuracy"], profile_key, record)
        if worst is None or selected["accuracy"] < worst[0] or (selected["accuracy"] == worst[0] and profile_key < worst[1]):
            worst = (selected["accuracy"], profile_key, record)
    return {"status": "pure_equilibria_evaluated", "count": count, "ranges": ranges,
            "best_accuracy": best[2], "worst_accuracy": worst[2]}


def search_pure(config, mechanism="rbts", on_progress=None, is_cancelled=None):
    branches = {}
    completed = 0
    for z in (0, 1):
        candidates, retained = [], []
        for actions in product(ACTIONS, repeat=3):
            if is_cancelled and is_cancelled():
                raise CancelledError("Search cancelled; no exhaustive certificate")
            profile = Profile((actions, actions))
            candidate = build_candidate(config, profile, mechanism=mechanism)
            direct = evaluate(config, candidate, mechanism)
            certificates = [solve_branch(config, candidate, i, z, mechanism, direct["conditional"][i][z]) for i in range(3)]
            accepted = all(cert["regret"] == 0 for cert in certificates)
            identity = f"z{z}:" + ",".join(actions)
            record = {"id": identity, "z": z, "actions": list(actions), "accepted": accepted,
                      "prediction_semantics": candidate.prediction_semantics,
                      "predictions": [[{"observation": observation_key(obs), "prediction": p} for obs, p in table if obs.z == z] for table in candidate.predictions],
                      "certificates": certificates,
                      "witness": next((cert["witness"] for cert in certificates if cert["regret"] > 0), None)}
            candidates.append(record)
            if accepted:
                retained.append(identity)
            completed += 1
            if on_progress:
                on_progress({"phase": "equilibria", "completed": completed, "total": 432, "z": z})
        assert len(candidates) == 216
        branches[str(z)] = {"tested": len(candidates), "equilibrium_count": len(retained),
                            "equilibrium_ids": retained, "candidates": candidates}
    count = branches["0"]["equilibrium_count"] * branches["1"]["equilibrium_count"]
    return {**scope_for(mechanism), "status": "succeeded", "mechanism": mechanism, "config": config.raw(),
            "branches": branches, "full_profile_count": 46656, "full_equilibrium_count": count,
            "branch_candidate_count": completed, "enumeration_completed": True,
            "prediction_semantics": candidate.prediction_semantics,
            "combination_rule": "Cartesian product of retained z=0 and z=1 branch IDs; choose both branches before analyzing metrics."}
