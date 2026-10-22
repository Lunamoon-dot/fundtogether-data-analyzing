"""All six effort/report actions per judge, separately for each public branch."""

from itertools import product

from .best_response import solve_branch
from .evaluate import SCOPE, evaluate
from .strategies import ACTIONS, Profile, build_candidate, observation_key


class CancelledError(Exception):
    pass


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
    return {**SCOPE, "status": "succeeded", "mechanism": mechanism, "config": config.raw(),
            "branches": branches, "full_profile_count": 46656, "full_equilibrium_count": count,
            "branch_candidate_count": completed, "enumeration_completed": True,
            "prediction_semantics": candidate.prediction_semantics,
            "combination_rule": "Cartesian product of retained z=0 and z=1 branch IDs; choose both branches before analyzing metrics."}
