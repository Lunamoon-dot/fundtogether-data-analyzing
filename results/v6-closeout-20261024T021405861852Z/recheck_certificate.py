"""Replay a V6 certificate using only its pinned independent potential oracle.

Run: python THIS_FILE --run RUN_DIRECTORY --out NEW_JSON_FILE
Does not import the feasibility checker or use its Bayesian/payoff helpers.
"""

import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path


def fractions(x):
    if isinstance(x, dict):
        return {k: fractions(v) for k, v in x.items()}
    if isinstance(x, list):
        return tuple(fractions(v) for v in x)
    if isinstance(x, str):
        try:
            return F(x)
        except ValueError:
            pass
    return x


def serial(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [serial(v) for v in x]
    return x


def run(root):
    checks = 0

    def check(condition, label):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    manifest = json.loads((root/"manifest.json").read_text())
    for row in manifest["inputs"]:
        check(sha256((root/row["snapshot"]).read_bytes()).hexdigest() == row["sha256"], row["snapshot"])
    for name, digest in manifest["outputs"].items():
        check(sha256((root/name).read_bytes()).hexdigest() == digest, name)
    inputs = root/"inputs"
    freezes = list((inputs/"spec_history").glob("v6.0-rave-*/manifest.json"))
    check(len(freezes) == 1, "one freeze")
    frozen = json.loads(freezes[0].read_text())
    for row in frozen["inputs"]:
        check(sha256((freezes[0].parent/row["snapshot"]).read_bytes()).hexdigest() == row["sha256"], "freeze "+row["source"])
    raw_config = json.loads((inputs/"configs/v6/rave_phase1.json").read_text())
    semantic = sha256(json.dumps(raw_config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    check(semantic == manifest["config_semantic_sha256"] == frozen["config_semantic_sha256"], "semantic hash")
    study = fractions(raw_config)
    spec = importlib.util.spec_from_file_location("pinned_v6_oracle", inputs/"verification/oracle_v6_feasibility.py")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    result = json.loads((root/"certificate.json").read_text())
    profile_count = deviation_count = 0
    candidates = []
    failures = []
    truth_not_equilibrium = []
    for fx_record, fixture in zip(result["fixtures"], study["fixtures"]):
        table = oracle.decision_table(fixture, (study["c_fa"], study["c_fr"]))
        check(serial(table) == fx_record["decision_table"], "posterior/decision table")
        check(len(fx_record["comparisons"]) == 4, "four declared allocations")
        for comparison, allocation in zip(fx_record["comparisons"], study["allocations"]):
            audit = {(z, r): allocation["params"][z] if allocation["kind"] == "public"
                     else allocation["params"][int(len(set(r)) == 1)]
                     for z, r in product((0, 1), tuple(product((0, 1), repeat=3)))}
            check({ast.literal_eval(k): F(v) for k, v in comparison["audit_policy"].items()} == audit, "observable q")
            policy = dict({k: study[k] for k in ("mu", "budget", "kappa", "operating_cost", "payout_value", "exposure_limit", "c_fa", "c_fr")}, f=fixture["f"], audit=audit)
            high = (("H01",)*3,)*2
            selective = oracle.evaluate(fixture, policy, table, high)
            check(serial(selective) == comparison["selective"], "selective exogenous metric record")
            uniform_policy = dict(policy, audit={key: selective["audit_exposure"] for key in audit})
            uniform = oracle.evaluate(fixture, uniform_policy, table, high)
            check(serial(uniform) == comparison["optimized_uniform_at_matched_exposure"], "matched uniform record")
            improvement = uniform["expected_decision_loss"]-selective["expected_decision_loss"]
            check(str(improvement) == comparison["decision_loss_improvement"], "allocation benefit")
            quality = selective["final_fa"] <= F(1, 5) and selective["final_fr"] <= F(1, 4) and selective["wrong_payout_value"] <= F(3, 20)
            passed = quality and selective["cash_review_cost"] <= 4 and selective["reward_cap"] <= 6 and selective["audit_exposure"] <= study["exposure_limit"]
            candidate = improvement > 0 and selective["cash_review_cost"] <= uniform["cash_review_cost"] and passed
            check(candidate == comparison["meaningful_candidate"], "candidate gate")
            if candidate:
                candidates.append([fixture["name"], allocation["name"]])
            for diagnostic in comparison["strategy_witnesses"]:
                b = (F(0),)*3 if diagnostic["study"] == "neutral_primary" else (study["external_b_diagnostic"],)*3
                check(serial(b) == diagnostic["b"], "separate b study")
                for pol_record, p in zip(diagnostic["policies"], (policy, uniform_policy)):
                    equilibrium_records = []
                    check(len(pol_record["profiles"]) == 5, "five targeted profiles")
                    for profile_record in pol_record["profiles"]:
                        profile = tuple(tuple(v) for v in profile_record["profile"])
                        metrics = oracle.evaluate(fixture, p, table, profile, b)
                        profile_count += 1
                        check(serial(metrics) == profile_record["metrics"], "targeted profile metrics")
                        maximum = F(0)
                        for z in (0, 1):
                            for i in range(3):
                                response = profile_record["deviations"]["by_z"][z][i]
                                values = {}
                                check(len(response["actions"]) == 6, "all six actions")
                                for option in response["actions"]:
                                    action = option["action"]
                                    changed = [list(v) for v in profile]
                                    changed[z][i] = action
                                    dev = oracle.evaluate(fixture, p, table, changed, b)
                                    deviation_count += 1
                                    value = dev["utility_by_z"][z][i]
                                    values[action] = value
                                    check(str(value) == option["utility"], "deviation utility")
                                    check(str(value-metrics["utility_by_z"][z][i]) == option["gain"], "deviation gain")
                                    for field, key in (("delta_exposure", "exposure_by_z"), ("delta_release", "release_by_z")):
                                        check(str(dev[key][z]-metrics[key][z]) == option[field], field)
                                best = max(values.values())
                                regret = best-metrics["utility_by_z"][z][i]
                                maximum = max(maximum, regret)
                                check(set(response["best_actions"]) == {a for a, u in values.items() if u == best}, "ties")
                                check(F(response["regret"]) == regret, "branch regret")
                        check(F(profile_record["deviations"]["max_regret"]) == maximum, "max regret")
                        check(profile_record["deviations"]["is_equilibrium"] == (maximum == 0), "witness NE")
                        if maximum == 0:
                            equilibrium_records.append(profile_record)
                            if metrics["audit_exposure"] > study["exposure_limit"]:
                                failures.append({"fixture": fixture["name"], "allocation": allocation["name"], "policy": pol_record["policy_id"], "study": diagnostic["study"], "profile": profile_record["profile_id"], "audit_exposure": str(metrics["audit_exposure"]), "finding": "strategic_failure_witness_exposure"})
                        elif candidate and profile_record["profile_id"] == "all_H01" and pol_record["policy_id"] == "selective" and diagnostic["study"] == "neutral_primary":
                            truth_not_equilibrium.append({"fixture":fixture["name"],"allocation":allocation["name"],"max_regret":str(maximum)})
                    summary = pol_record["equilibria"]
                    check(summary["witnessed_equilibrium_count"] == len(equilibrium_records), "witness count")
                    check(summary["total_equilibrium_count"] == "not_computed_phase1" and not summary["robust_pass"], "non-exhaustive scope")
                    if equilibrium_records:
                        for key, witness in summary["worst_metrics"].items():
                            extremum = (min if key == "final_accuracy" else max)(F(row["metrics"][key]) for row in equilibrium_records)
                            check(F(witness["value"]) == extremum, "worst witnessed metric")
                            check(any(row["profile_id"] == witness["profile_id"] and F(row["metrics"][key]) == extremum for row in equilibrium_records), "worst witness identity")
        print("oracle rechecked", fixture["name"], flush=True)
    check(profile_count == 240 and deviation_count == 8640, "declared coverage")
    check(result["phase2_decision"] == ("GO_candidate_discovery_only" if candidates else "NO-GO"), "stop gate")
    return {"status": "passed", "checks": checks, "targeted_profile_records": profile_count,
            "independent_deviation_records": deviation_count, "meaningful_exogenous_candidates": candidates,
            "truthful_candidates_not_equilibria": truth_not_equilibrium,
            "strategic_failure_witnesses": failures, "source": "pinned independent potential-state oracle",
            "equilibrium_search": "not_run_phase2"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.run)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result))
