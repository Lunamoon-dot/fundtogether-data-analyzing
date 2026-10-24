"""Exact V6 Phase-1 feasibility; no general equilibrium engine or runtime API."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
REPORTS = tuple(product((0, 1), repeat=3))
HIGH = (("H01",) * 3,) * 2
PROFILES = {
    "all_H01": HIGH,
    "copy_Z": (("L0",) * 3, ("L1",) * 3),
    "all_0": (("L0",) * 3,) * 2,
    "all_1": (("L1",) * 3,) * 2,
    "split_copy_Z": (("L0", "L0", "L1"), ("L1", "L1", "L0")),
}


def _fractions(value):
    if isinstance(value, dict):
        return {key: _fractions(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(_fractions(item) for item in value)
    if isinstance(value, str):
        try:
            return F(value)
        except ValueError:
            pass
    return value


def load_study():
    return _fractions(json.loads((ROOT / "configs/v6/rave_phase1.json").read_text()))


def _channel(channel, bit, y):
    positive = channel[0] if y == 1 else 1 - channel[1]
    return positive if bit == 1 else 1 - positive


def _report_chance(channel, action, r, y):
    if action not in ACTIONS:
        raise ValueError("unknown action")
    if action[0] == "L":
        return F(r == int(action[1]))
    return sum(_channel(channel, x, y) for x in (0, 1) if int(action[x+1]) == r)


def _report_mass(fixture, z, reports, branch, y):
    mass = (fixture["pi"] if y else 1 - fixture["pi"]) * _channel(fixture["public"], z, y)
    for channel, action, r in zip(fixture["private"], branch, reports):
        mass *= _report_chance(channel, action, r, y)
    return mass


def decision_table(fixture, losses, calibration="H01"):
    if calibration not in ("H01", "copyZ"):
        raise ValueError("unknown calibration")
    c_fa, c_fr = losses
    if min(c_fa, c_fr) <= 0:
        raise ValueError("losses must be positive")
    threshold = c_fa / (c_fa + c_fr)
    table = {}
    for z, reports in product((0, 1), REPORTS):
        branch = ("H01",) * 3 if calibration == "H01" else (f"L{z}",) * 3
        weights = [_report_mass(fixture, z, reports, branch, y) for y in (0, 1)]
        state_mass = sum(weights)
        if not state_mass:
            if calibration != "copyZ":
                raise ValueError("unsupported H01 report state")
            weights = [(fixture["pi"] if y else 1-fixture["pi"])
                       * _channel(fixture["public"], z, y) for y in (0, 1)]
        normalizer = sum(weights)
        posterior = weights[1] / normalizer
        after = [tuple(weights[y]*_channel(fixture["audit"], t, y) for y in (0, 1))
                 for t in (0, 1)]
        table[z, reports] = {
            "posterior": posterior,
            "g0": int(posterior >= threshold),
            "g1": tuple(int(row[1]/sum(row) >= threshold) for row in after),
            "mass": state_mass,
            "voi": min(c_fa*weights[0], c_fr*weights[1])/normalizer
            - sum(min(c_fa*row[0], c_fr*row[1]) for row in after)/normalizer,
        }
    return table


def audit_table(kind, params):
    if kind not in ("uniform", "disagreement", "public"):
        raise ValueError("unknown audit allocation")
    if len(params) != (1 if kind == "uniform" else 2) or any(not 0 <= q <= 1 for q in params):
        raise ValueError("audit probabilities must lie in [0,1]")
    return {(z, r): params[0] if kind == "uniform" else params[z] if kind == "public"
            else params[int(len(set(r)) == 1)] for z, r in product((0, 1), REPORTS)}


def evaluate(fixture, policy, decisions, profile, b=(0, 0, 0)):
    if len(profile) != 2 or any(len(branch) != 3 for branch in profile) or len(b) != 3:
        raise ValueError("three Judges and two public branches required")
    if any(not 0 <= q <= 1 for q in policy["audit"].values()):
        raise ValueError("audit probabilities must lie in [0,1]")
    if min(policy[k] for k in ("f", "mu", "budget", "kappa", "operating_cost", "payout_value")) < 0:
        raise ValueError("negative payment/cost")
    cap = 3*policy["f"] + 3*policy["mu"]
    if cap > policy["budget"]:
        raise ValueError("reward reserve exceeds budget")
    accuracy0 = accuracy = fa0 = fr0 = fa = fr = F(0)
    public_mass = [F(0), F(0)]
    exposure = [F(0), F(0)]
    release = [F(0), F(0)]
    audit_truth = [F(0), F(0)]
    rewards = [[F(0)] * 3 for _ in (0, 1)]
    for z, reports, y in product((0, 1), REPORTS, (0, 1)):
        mass = _report_mass(fixture, z, reports, profile[z], y)
        q = policy["audit"][z, reports]
        fixed = decisions[z, reports]
        audited_release = sum(_channel(fixture["audit"], t, y)*fixed["g1"][t] for t in (0, 1))
        final = (1-q)*fixed["g0"] + q*audited_release
        initial = int(sum(reports) >= 2)
        accuracy0 += mass*(initial == y)
        accuracy += mass*(final if y else 1-final)
        fa0 += mass*initial*(1-y)
        fr0 += mass*(1-initial)*y
        fa += mass*final*(1-y)
        fr += mass*(1-final)*y
        public_mass[z] += mass
        exposure[z] += mass*q
        audit_truth[y] += mass*q
        release[z] += mass*final
        for i, r in enumerate(reports):
            rewards[z][i] += mass*(policy["f"] + policy["mu"]*q*_channel(fixture["audit"], r, y))
    reward_by_z = tuple(tuple(value/public_mass[z] for value in row) for z, row in enumerate(rewards))
    payouts = tuple(sum(row) for row in reward_by_z)
    exposure_by_z = tuple(exposure[z]/public_mass[z] for z in (0, 1))
    release_by_z = tuple(release[z]/public_mass[z] for z in (0, 1))
    effort = tuple(tuple(action[0] for action in branch) for branch in profile)
    utilities = tuple(tuple(reward_by_z[z][i]+b[i]*release_by_z[z]
                            - (fixture["private"][i][2] if effort[z][i] == "H" else F(0))
                            for i in range(3)) for z in (0, 1))
    reward = sum(sum(row) for row in rewards)
    audit_cost = policy["kappa"]*sum(exposure)
    return {
        "preliminary_accuracy": accuracy0, "final_accuracy": accuracy,
        "preliminary_fa": fa0/(1-fixture["pi"]), "preliminary_fr": fr0/fixture["pi"],
        "final_fa": fa/(1-fixture["pi"]), "final_fr": fr/fixture["pi"],
        "wrong_payout_value": fa*policy["payout_value"],
        "expected_decision_loss": policy["c_fa"]*fa+policy["c_fr"]*fr,
        "audit_exposure": sum(exposure),
        "audit_given_y": (audit_truth[0]/(1-fixture["pi"]), audit_truth[1]/fixture["pi"]),
        "expected_reviewer_payout": reward, "expected_audit_cost": audit_cost,
        "cash_review_cost": reward+audit_cost+policy["operating_cost"],
        "reward_cap": cap, "release_probability": sum(release),
        "utility_by_z": utilities, "reward_by_z": reward_by_z,
        "release_by_z": release_by_z, "reviewer_payout_by_z": payouts,
        "exposure_by_z": exposure_by_z,
        "batch_cash_review_cost": sum(payouts[z]+policy["kappa"]*exposure_by_z[z]
                                      + policy["operating_cost"] for z in (0, 1))/2,
        "effort_by_z": effort,
    }


def deviations(fixture, policy, decisions, profile, b=(0, 0, 0)):
    candidate = evaluate(fixture, policy, decisions, profile, b)
    branches = []
    for z in (0, 1):
        judges = []
        for i in range(3):
            options = []
            for action in ACTIONS:
                changed = [list(branch) for branch in profile]
                changed[z][i] = action
                new = evaluate(fixture, policy, decisions, changed, b)
                value = new["utility_by_z"][z][i]
                options.append({"action": action, "utility": value,
                    "gain": value-candidate["utility_by_z"][z][i],
                    "audit_exposure": new["exposure_by_z"][z],
                    "delta_exposure": new["exposure_by_z"][z]-candidate["exposure_by_z"][z],
                    "delta_release": new["release_by_z"][z]-candidate["release_by_z"][z],
                    "delta_reward": new["reward_by_z"][z][i]-candidate["reward_by_z"][z][i]})
            best = max(option["utility"] for option in options)
            judges.append({"judge": i, "candidate_action": profile[z][i],
                "candidate_utility": candidate["utility_by_z"][z][i],
                "best_actions": [o["action"] for o in options if o["utility"] == best],
                "regret": best-candidate["utility_by_z"][z][i], "actions": options})
        branches.append(tuple(judges))
    max_regret = max(rec["regret"] for branch in branches for rec in branch)
    return {"by_z": tuple(branches), "max_regret": max_regret,
            "is_equilibrium": max_regret == 0, "scope": "targeted_profile_only"}


def gates(metrics, cap, exposure_limit):
    result = {"fa": metrics["final_fa"] <= F(1, 5),
              "fr": metrics["final_fr"] <= F(1, 4),
              "wrong_payout": metrics["wrong_payout_value"] <= F(3, 20),
              "cash": metrics["cash_review_cost"] <= 4,
              "reserve": cap <= 6, "exposure": metrics["audit_exposure"] <= exposure_limit}
    return dict(result, all_pass=all(result.values()))


def witness_summary(records):
    names = ("final_fa", "final_fr", "wrong_payout_value", "expected_decision_loss",
             "cash_review_cost", "audit_exposure", "final_accuracy")
    worst = {}
    for name in names:
        if records:
            record = (min if name == "final_accuracy" else max)(records, key=lambda r: r["metrics"][name])
            worst[name] = {"value": record["metrics"][name], "profile_id": record["profile_id"]}
    return {"witnessed_equilibrium_count": len(records), "worst_metrics": worst or None,
            "total_equilibrium_count": "not_computed_phase1",
            "worst_equilibrium_metrics": "not_computed_phase1", "robust_pass": False}


def phase2_decision(meaningful_candidate):
    return "GO_candidate_discovery_only" if meaningful_candidate else "NO-GO"


def _policy(study, fixture, audit):
    names = ("mu", "budget", "kappa", "operating_cost", "payout_value", "exposure_limit", "c_fa", "c_fr")
    return dict({key: study[key] for key in names}, f=fixture["f"], audit=audit)


def _majority_table(table):
    return {key: dict(row, g0=int(sum(key[1]) >= 2), g1=(int(sum(key[1]) >= 2),)*2)
            for key, row in table.items()}


def _public_reference(fixture, study):
    fa = fr = F(0)
    for z in (0, 1):
        m = [(fixture["pi"] if y else 1-fixture["pi"])*_channel(fixture["public"], z, y) for y in (0, 1)]
        d = int(study["c_fr"]*m[1] >= study["c_fa"]*m[0])
        fa += m[0]*d
        fr += m[1]*(1-d)
    return {"status": "diagnostic_reference_only", "accuracy": 1-fa-fr,
            "fa": fa/(1-fixture["pi"]), "fr": fr/fixture["pi"],
            "wrong_payout_value": fa*study["payout_value"],
            "expected_decision_loss": study["c_fa"]*fa+study["c_fr"]*fr,
            "cash_review_cost": F(0), "audit_exposure": F(0)}


def run_certificate():
    study = load_study()
    fixtures = []
    for fixture in study["fixtures"]:
        table = decision_table(fixture, (study["c_fa"], study["c_fr"]))
        p0 = _policy(study, fixture, audit_table("uniform", (F(0),)))
        majority = _majority_table(table)
        bayes0 = evaluate(fixture, p0, table, HIGH)
        majority0 = evaluate(fixture, p0, majority, HIGH)
        comparisons = []
        for allocation in study["allocations"]:
            p = _policy(study, fixture, audit_table(allocation["kind"], allocation["params"]))
            selective = evaluate(fixture, p, table, HIGH)
            e = selective["audit_exposure"]
            uniform_policy = dict(p, audit=audit_table("uniform", (e,)))
            uniform = evaluate(fixture, uniform_policy, table, HIGH)
            improvement = uniform["expected_decision_loss"]-selective["expected_decision_loss"]
            status = gates(selective, selective["reward_cap"], study["exposure_limit"])
            meaningful = improvement > 0 and selective["cash_review_cost"] <= uniform["cash_review_cost"] and status["all_pass"]
            strategic = []
            # Neutral utility records always precede external-preference diagnostics.
            for label, b in (("neutral_primary", (F(0),)*3),
                             ("external_b_diagnostic", (study["external_b_diagnostic"],)*3)):
                policies = []
                for policy_id, policy in (("selective", p), ("matched_uniform", uniform_policy)):
                    witnesses = []
                    profiles = []
                    for profile_id, profile in PROFILES.items():
                        metrics = evaluate(fixture, policy, table, profile, b)
                        response = deviations(fixture, policy, table, profile, b)
                        record = {"profile_id": profile_id, "profile": profile, "metrics": metrics, "deviations": response}
                        profiles.append(record)
                        if response["is_equilibrium"]:
                            witnesses.append(record)
                    policies.append({"policy_id": policy_id, "profiles": profiles,
                                     "equilibria": witness_summary(witnesses)})
                strategic.append({"study": label, "b": b, "policies": policies})
            comparisons.append({"allocation": allocation, "audit_policy": p["audit"],
                "selective": selective, "optimized_uniform_at_matched_exposure": uniform,
                "decision_loss_improvement": improvement,
                "economic_loss_plus_cash_improvement": uniform["expected_decision_loss"]+uniform["cash_review_cost"]
                - selective["expected_decision_loss"]-selective["cash_review_cost"],
                "gates_at_exogenous_H01": status, "meaningful_candidate": meaningful,
                "same_allocation_majority_B0": evaluate(fixture, p, majority, HIGH),
                "strategy_witnesses": strategic,
                "calibration_stress_copyZ": evaluate(fixture, p,
                    decision_table(fixture, (study["c_fa"], study["c_fr"]), "copyZ"), HIGH)})
        fixtures.append({"fixture": fixture, "calibration_assumptions": "all_H01_fixed_before_deviation",
            "decision_table": table, "B0_no_audit_majority": majority0,
            "no_audit_bayes": bayes0,
            "aggregation_rule_loss_improvement": majority0["expected_decision_loss"]-bayes0["expected_decision_loss"],
            "uniform_full_audit": evaluate(fixture, dict(p0, audit=audit_table("uniform", (F(1),))), table, HIGH),
            "B3_public_signal_only": _public_reference(fixture, study),
            "B4_oracle": {"status": "non_deployable_oracle", "accuracy": F(1), "expected_decision_loss": F(0)},
            "comparisons": comparisons})
    candidate = any(c["meaningful_candidate"] for fx in fixtures for c in fx["comparisons"])
    return {"status": "succeeded", "model_version": study["model_version"],
            "scope": "phase01_exact_feasibility_and_targeted_deviations",
            "Gate_A": "formal_model_and_counterexample", "Gate_B": candidate,
            "Gate_C": "not_run_phase2", "Gate_D": "not_run_phase2",
            "phase2_decision": phase2_decision(candidate), "fixtures": fixtures,
            "limits": ["synthetic assumptions", "fixed truthful calibration", "targeted profiles only",
                       "no exhaustive equilibrium count or worst-equilibrium certificate",
                       "no mixed/coalition/bribery resistance", "no production acceptance"]}


def freeze_path():
    paths = sorted((ROOT / "spec_history").glob("v6.0-rave-pre-checker-freeze-*/manifest.json"))
    if len(paths) != 1:
        raise ValueError("one explicit V6 primary freeze required")
    return paths[0]


def verify_freeze():
    path = freeze_path()
    manifest = json.loads(path.read_text())
    for row in manifest["inputs"]:
        if sha256((path.parent / row["snapshot"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("frozen bytes changed: " + row["source"])
        if sha256((ROOT / row["source"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("current primary input differs from freeze: " + row["source"])
    return manifest


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _report(result):
    rows = ["# V6 RAVE Phase 0–1 — exact feasibility", "",
            "Synthetic assumptions; exogenous H01 discovery is not equilibrium success.",
            f"Phase 2: **{result['phase2_decision']}**. C/D remain not run.", "",
            "## Matched-exposure comparison", "",
            "| Fixture | Allocation | Exposure | Selective loss | Uniform loss | Selective cash | Uniform cash | Gates at H01 | Candidate |",
            "|---|---|---:|---:|---:|---:|---:|---|---|"]
    for fx in result["fixtures"]:
        for c in fx["comparisons"]:
            s, u = c["selective"], c["optimized_uniform_at_matched_exposure"]
            rows.append(f"| {fx['fixture']['name']} | {c['allocation']['name']} | {s['audit_exposure']} | {s['expected_decision_loss']} | {u['expected_decision_loss']} | {s['cash_review_cost']} | {u['cash_review_cost']} | {c['gates_at_exogenous_H01']['all_pass']} | {c['meaningful_candidate']} |")
    rows += ["", "## Required Phase-1 answers", "",
        "1. **Equal exposure:** see exact table and decision_loss_improvement in certificate; positive values are allocation benefits under calibrated exogenous reports only.",
        "2. **Attribution:** no_audit_bayes vs B0_no_audit_majority isolates aggregation-rule benefit. Selective vs matched uniform uses identical g0/g1; their difference isolates allocation.",
        "3. **Noisy T:** posterior odds multiply by sens_T/(1-spec_T) when T=1, or (1-sens_T)/spec_T when T=0 (here 9 or 1/9). Decisions change only when this crosses threshold 2/3. Unanimous evidence can rationally override T.",
        "4. **Manipulation:** disagreement-only auditing with all-copy-Z has a profitable Low contrarian deviation. F51-02 gain=17/50 at mu=1,b=0; F51-01=7/50. This seeks an audit. Exposure changes for every six-action deviation are preserved.",
        "5. **Copy-Z:** Q1-zero has exposure zero and retains unanimous-but-wrong cases (F51-02 FA=FR=3/10). It is not a neutral equilibrium there because dissent earns bonus. Its failure as an equilibrium does not remove the reporting-distortion concern; uniform/Q2 copy-Z witnesses are checked separately.",
        "6. **Reporting bias:** paying only audited agreement can reward dissent even without private information. Certificates keep actual candidate utility and all deviations, rather than calling H01 truthful in equilibrium.",
        "7. **Cash/payment:** costs include all reviewer bonuses and one kappa charge per claim audit, with undiscounted 3f+3mu reserve. Table reports positive/negative economic outcomes separately. Incentive-adjusted economic viability remains unproved.",
        "8. **Candidate:** a candidate requires lower decision loss, no higher cash and all declared H01 gates; see meaningful_candidate fields. This is the sole Gate-B rule, fixed before output.",
        "9. **Residual risks:** real auditor provenance/correlated error/capture, distribution estimation, strategic Creator evidence, reviewer participation, latency, coordinated/mixed/history strategies and calibration fixed points are not modeled. The labelled b=1/10 and copyZ-calibration diagnostics are not a robustness sweep.",
        f"10. **Decision:** {result['phase2_decision']}; a future request may open only the justified strategic study. No Phase 2 ran here. The finite decision comparison and audit-seeking counterexample are reproducible in certificate.json.",
        "", "## Strategic scope and failure witnesses", "",
        "Each allocation and its matched uniform baseline has 5 targeted profiles, each checked against all 6 deviations for each Judge/Z (36 options/profile), first b=0 then the separate b=1/10 diagnostic. This is not 216-profile exhaustive search. Worst metrics/counts are explicitly limited to witnessed equilibria; overall equilibrium count and worst-equilibrium gates are not computed.", ""]
    for fx in result["fixtures"]:
        rows.append(f"- {fx['fixture']['name']}: no-audit majority loss {fx['B0_no_audit_majority']['expected_decision_loss']}; no-audit Bayes loss {fx['no_audit_bayes']['expected_decision_loss']}; aggregation improvement {fx['aggregation_rule_loss_improvement']}.")
        for c in fx["comparisons"]:
            for policy in c["strategy_witnesses"][0]["policies"]:
                eq = policy["equilibria"]
                rows.append(f"  - {c['allocation']['name']} / {policy['policy_id']}: {eq['witnessed_equilibrium_count']} witnessed equilibria; total count not computed.")
    return "\n".join(rows) + "\n"


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"event_type": "v6_phase01_feasibility_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "inputs": []}
    try:
        frozen = verify_freeze()
        manifest["config_semantic_sha256"] = frozen["config_semantic_sha256"]
        sources = [row["source"] for row in frozen["inputs"]] + [
            "verification/feasibility_v6.py", "verification/mutation_probes_v6.py",
            "tests/test_v6_regressions.py", "tests/test_v6_mutations.py",
            freeze_path().relative_to(ROOT).as_posix()]
        sources += [(freeze_path().parent / row["snapshot"]).relative_to(ROOT).as_posix()
                    for row in frozen["inputs"]]
        for source in sources:
            dst = out / "inputs" / source
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/source, dst)
            manifest["inputs"].append({"source": source, "snapshot": "inputs/"+source,
                                       "sha256": sha256(dst.read_bytes()).hexdigest()})
        result = run_certificate()
        (out / "certificate.json").write_text(json.dumps(_jsonable(result), indent=2)+"\n", encoding="utf-8")
        (out / "report.md").write_text(_report(result), encoding="utf-8")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out/name).read_bytes()).hexdigest() for name in ("certificate.json", "report.md")}
        return result
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"status": result["status"], "phase2_decision": result["phase2_decision"], "out": str(args.out)}))
