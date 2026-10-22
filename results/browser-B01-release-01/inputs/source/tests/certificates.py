"""Independent certificate replay, using only the test oracle."""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from . import oracle


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_analysis(result):
    require(result["status"] == "succeeded", "Incomplete run cannot certify")
    raw, profile, mechanism = result["config"], result["profile"], result["mechanism"]
    fields = {"model_version", "pi", "a", "b", "costs", "f", "lambda", "fixed_reward", "reward_budget", "payout_value", "operating_cost"}
    require(set(raw) == fields and raw["model_version"] == "ceav-m1-v1.0", "Invalid config schema/version")
    require(all(isinstance(v, str) for key, v in raw.items() if key != "costs"), "Config numbers must be rational strings")
    require(isinstance(raw["costs"], list) and len(raw["costs"]) == 3 and all(isinstance(c, str) for c in raw["costs"]), "Invalid costs")
    p = oracle.parameters(raw)
    require(all(0 < p[k] < 1 for k in ("pi", "a", "b")), "Invalid probability domain")
    require(all(v >= 0 for k, v in p.items() if k not in ("pi", "a", "b", "costs")) and all(c >= 0 for c in p["costs"]), "Negative costs/reward")
    require(mechanism in ("fixed", "rbts"), "Unknown mechanism")
    cap = 3 * p["fixed_reward"] if mechanism == "fixed" else 3 * p["f"] + 6 * p["lambda"]
    require(cap <= p["reward_budget"], "Invalid budget")
    require(set(profile) == {"0", "1"} and all(len(actions) == 3 and all(a in oracle.ACTIONS for a in actions) for actions in profile.values()), "Invalid profile")
    expected = oracle.analyze(raw, profile, mechanism)
    records = result["best_responses"]
    require(len(records) == 6, "Six judge/z records required")
    seen = set()
    constant = mechanism == "fixed" or p["lambda"] == 0
    require(result["prediction_semantics"] == ("arbitrary_reachable_predictions" if constant else "unique_on_reachable_observations"), "Candidate prediction semantics")
    require(len(result["predictions"]) == 3, "Missing candidate prediction table")
    for i, table in enumerate(result["predictions"]):
        require({tuple(item["observation"]): item["prediction"] for item in table} == expected["tables"][i], "Candidate predictions changed")
    for record in records:
        i, z = "ABC".index(record["judge"]), record["z"]
        require((i, z) not in seen, "Duplicate branch")
        seen.add((i, z))
        truth = expected["branches"][2 * i + z]
        require(record["candidate_action"] == profile[str(z)][i], "Candidate action changed")
        require(record["reference_judge"] == "ABC"[(i+1)%3] and record["scoring_peer_judge"] == "ABC"[(i+2)%3], "Cyclic roles changed")
        for key in ("score", "reward", "utility"):
            require(record["candidate"][key] == truth["candidate"][key], f"Candidate {key}")
        mass = sum(w for s, w in oracle.worlds(raw) if s[1] == z)
        require(record["branch_probability"] == mass, "Branch probability")
        require(record["regret"] == truth["regret"], "Regret")
        require(record["delta_utility"] == truth["delta"], "Delta")
        require(record["optimal_actions"] == truth["optimal_actions"], "Action ties")
        require(record["best_utility"] == max(truth["low_utility"], truth["high_utility"]), "Best utility")
        require(record["best_efforts"] == [e for e, value in (("L", truth["low_utility"]), ("H", truth["high_utility"])) if value == record["best_utility"]], "Effort ties")
        require(record["prediction_optimum"] == ("any_in_unit_interval" if constant else "unique_on_reachable_observations"), "Prediction semantics")
        for effort, label in (("L", "low"), ("H", "high")):
            option = record[label]
            trials = [truth["trials"][a] for a in oracle.ACTIONS if a[0] == effort]
            require(option["utility"] == max(t["utility"] for t in trials), "Effort utility")
            require(option["score"] == max(t["score"] for t in trials), "Diagnostic score")
            optimal = [a for a in oracle.ACTIONS if a[0] == effort and truth["trials"][a]["utility"] == option["utility"]]
            require(option["optimal_actions"] == optimal, "Effort report map ties")
            source = trials[0]["predictions"]
            require(len(option["observations"]) == len(source), "Missing observation")
            for obs in option["observations"]:
                key = tuple(obs["observation"])
                require(key in source and obs["optimal_prediction"] == source[key], "Prediction q")
                subset = [(s, w) for s, w in oracle.worlds(raw) if oracle.visible(s, i, effort + ("0" if effort == "L" else "00")) == key]
                require(obs["probability_given_z"] == sum(w for _, w in subset) / mass, "Observation mass")
                information = []
                j, k = (i + 1) % 3, (i + 2) % 3
                for r in (0, 1):
                    total = F(0)
                    for s, w in subset:
                        actions = profile[str(z)]
                        ref = expected["tables"][j][oracle.visible(s, j, actions[j])]
                        shadow = ref + (2 * r - 1) * min(ref, 1 - ref)
                        total += w * (1 - (shadow - oracle.reported(s, k, actions[k])) ** 2)
                    information.append(total / sum(w for _, w in subset))
                require(obs["information_by_report"] == information, "Joint information expectation")
                ties = [0, 1] if constant else [r for r in (0, 1) if information[r] == max(information)]
                require(obs["optimal_reports"] == ties, "Observation report ties")
        for frozen in record["frozen_peer_tables"]:
            peer = "ABC".index(frozen["judge"])
            require(peer in ((i + 1) % 3, (i + 2) % 3), "Wrong peer role")
            require({tuple(item["observation"]): item["prediction"] for item in frozen["table"]} == expected["tables"][peer], "Peer table changed")
        witness = record["witness"]
        if truth["regret"] > 0:
            require(witness is not None, "Missing deviation witness")
            require(witness["judge"] == record["judge"] and witness["z"] == z, "Wrong witness branch")
            require(witness["action"] in truth["optimal_actions"], "Wrong witness action")
            trial = truth["trials"][witness["action"]]
            require({tuple(v["observation"]): v["prediction"] for v in witness["prediction_map"]} == trial["predictions"], "Witness predictions")
            require(witness["old_utility"] == truth["candidate"]["utility"] and witness["new_utility"] == trial["utility"], "Witness utilities")
            require(witness["conditional_gain"] == truth["regret"] and witness["ex_ante_gain"] == mass * truth["regret"], "Witness gain")
        else:
            require(witness is None, "Spurious witness")
    require(seen == {(i, z) for i in range(3) for z in (0, 1)}, "Missing branch")
    for key in ("accuracy", "wrong_payout_value", "false_approval_rate", "false_rejection_rate", "expected_payout"):
        require(result["metrics"][key] == expected[key], f"Metric {key}")
    equilibrium = all(r["regret"] == 0 for r in expected["branches"])
    require(result["equilibrium_status"] == ("exact_pure_equilibrium" if equilibrium else "not_equilibrium"), "Equilibrium verdict")
    return True


def canonical_hash(value):
    def plain(v):
        if isinstance(v, F):
            return str(v)
        if isinstance(v, dict):
            return {str(k): plain(item) for k, item in v.items()}
        if isinstance(v, (tuple, list)):
            return [plain(item) for item in v]
        return v
    return hashlib.sha256(json.dumps(plain(value), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def decode(value):
    if isinstance(value, dict):
        if "exact" in value and "decimal" in value and set(value) <= {"exact", "decimal", "decimal_reason"}:
            return F(value["exact"])
        return {key: decode(v) for key, v in value.items()}
    return [decode(v) for v in value] if isinstance(value, list) else value


def verify_run(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    certificate = decode(json.loads((folder / "certificate.json").read_text(encoding="utf-8")))
    require(manifest["status"] == certificate["requires_manifest_status"] == "succeeded", "Manifest must be terminal succeeded")
    for item in manifest["artifacts"]:
        require(hashlib.sha256((folder / item["name"]).read_bytes()).hexdigest() == item["sha256"], "Artifact bytes changed: " + item["name"])
    identity = certificate["identity"]
    for key in ("model_version", "engine_revision", "spec", "documents", "config_hash", "profile_hash", "mechanism"):
        require(identity[key] == manifest[key], "Certificate identity mismatch: " + key)
    require(identity["config_hash"] == canonical_hash(manifest["config"]), "Config hash mismatch")
    require(identity["profile_hash"] == canonical_hash(manifest["profile"]), "Profile hash mismatch")
    analysis = certificate["analysis"]
    require(analysis["config"] == manifest["config"] and analysis["profile"] == manifest["profile"], "Certificate input mismatch")
    candidate = {key: analysis[key] for key in ("config", "profile", "predictions", "mechanism")}
    require(canonical_hash(candidate) == identity["candidate_hash"], "Candidate hash mismatch")
    event = json.loads((folder / "inputs/freeze_event.json").read_text(encoding="utf-8"))
    require(event["event"] == "analyzer_implementation_start" and event["freeze_status"] == "frozen_at_analyzer_implementation_start", "Invalid freeze event")
    for name, item in manifest["documents"].items():
        require(hashlib.sha256((folder / "inputs" / name).read_bytes()).hexdigest() == item["sha256"] == event["files"][name]["sha256"], "Pinned document bytes changed")
    require(canonical_hash(manifest["source_files"]) == manifest["engine_revision"], "Source manifest hash")
    for item in manifest["source_files"]:
        path = (folder / "inputs/source" / item["path"]).resolve()
        require(path.is_relative_to((folder / "inputs/source").resolve()), "Source path escape")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], "Pinned source bytes changed")
    return verify_analysis(analysis)
