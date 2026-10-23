"""Exact multi-parameter robustness analysis for the unchanged V3 game."""

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

from . import V3_MODEL_VERSION
from .equilibria import search_pure, summarize_equilibrium_metrics
from .evaluate import evaluate
from .incentives import classify_landscape
from .model import JUDGES, ValidationError, rational, validate_config
from .output import FREEZES, finish_run, new_run, semantic_hash, write_csv, write_json
from .strategies import Profile, build_candidate


ROBUSTNESS_VERSION = "ceav-m1-v3.1-robustness"
POLICY_PATHS = (
    "verification_anchor.audit_probability",
    "lambda_peer",
    "anchor_weight",
)
UNCERTAINTY_PATHS = (
    "pi",
    "public_signal.sensitivity",
    "public_signal.specificity",
    "judges.A.private_signal.sensitivity",
    "judges.A.private_signal.specificity",
    "judges.A.high_effort_cost",
    "judges.B.private_signal.sensitivity",
    "judges.B.private_signal.specificity",
    "judges.B.high_effort_cost",
    "judges.C.private_signal.sensitivity",
    "judges.C.private_signal.specificity",
    "judges.C.high_effort_cost",
    "verification_anchor.sensitivity",
    "verification_anchor.specificity",
    "verification_anchor.cost_per_audit",
    "payout_value",
    "operating_cost",
    "verification_anchor.quality",
    "judges.high_effort_cost_multiplier",
)
GATE_FIELDS = (
    "max_false_approval_rate",
    "max_wrong_payout_value",
    "max_false_rejection_rate",
    "max_cash_review_cost",
)
RISK_METRICS = (
    "false_approval_rate",
    "wrong_payout_value",
    "false_rejection_rate",
    "cash_review_cost",
)
PROVENANCE_STATUSES = ("assumption", "pilot_estimate", "historical_estimate")
FORCED_ALL_HIGH = Profile((("H01", "H01", "H01"), ("H01", "H01", "H01")))


def _exact_object(value, allowed, field):
    if not isinstance(value, dict):
        raise ValidationError(field, "Cần JSON object.")
    unknown = set(value) - set(allowed)
    missing = set(allowed) - set(value)
    if unknown:
        key = sorted(unknown)[0]
        raise ValidationError(f"{field}.{key}", "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(field, "Thiếu field bắt buộc.")
    return value


def load_robustness_study(path):
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(raw.get("base_config"), str):
        base = (path.resolve().parent / raw["base_config"]).resolve()
        raw["base_config"] = json.loads(base.read_text(encoding="utf-8-sig"))
    return raw


def validate_robustness_study(raw):
    study = _exact_object(raw, ("analysis_version", "base_config", "policies", "uncertainty_axes", "gates", "provenance"), "study")
    if study["analysis_version"] != ROBUSTNESS_VERSION:
        raise ValidationError("study.analysis_version", f"Cần {ROBUSTNESS_VERSION}.")
    if not isinstance(study["base_config"], dict):
        raise ValidationError("study.base_config", "Cần full V3 config object; CLI có thể resolve relative path trước validation.")
    base = validate_config(study["base_config"], "hybrid_anchor")
    if base.model_version != V3_MODEL_VERSION:
        raise ValidationError("study.base_config.model_version", "V3.1 chỉ hỗ trợ ceav-m1-v3.0.")

    policies = study["policies"]
    if not isinstance(policies, list) or not policies:
        raise ValidationError("study.policies", "Cần danh sách policy không rỗng.")
    seen = set()
    for index, value in enumerate(policies):
        policy = _exact_object(value, ("policy_id", "overrides"), f"study.policies[{index}]")
        identity = policy["policy_id"]
        if not isinstance(identity, str) or not identity or identity in seen:
            raise ValidationError(f"study.policies[{index}].policy_id", "Cần ID chuỗi không rỗng và duy nhất.")
        seen.add(identity)
        overrides = policy["overrides"]
        if not isinstance(overrides, dict) or not overrides:
            raise ValidationError(f"study.policies[{index}].overrides", "Cần object override không rỗng.")
        unknown = set(overrides) - set(POLICY_PATHS)
        if unknown:
            key = sorted(unknown)[0]
            raise ValidationError(f"study.policies[{index}].overrides.{key}", "Policy path không được hỗ trợ.")
        for path, value in overrides.items():
            rational(value, f"study.policies[{index}].overrides.{path}")

    axes = study["uncertainty_axes"]
    if not isinstance(axes, dict) or not axes:
        raise ValidationError("study.uncertainty_axes", "Cần ít nhất một uncertainty axis.")
    unknown = set(axes) - set(UNCERTAINTY_PATHS)
    if unknown:
        key = sorted(unknown)[0]
        raise ValidationError(f"study.uncertainty_axes.{key}", "Uncertainty path không được hỗ trợ.")
    for path in (key for key in UNCERTAINTY_PATHS if key in axes):
        values = axes[path]
        if not isinstance(values, list) or not values:
            raise ValidationError(f"study.uncertainty_axes.{path}", "Cần danh sách chuỗi hữu tỉ không rỗng.")
        for index, value in enumerate(values):
            number = rational(value, f"study.uncertainty_axes.{path}[{index}]")
            if path == "verification_anchor.quality" and not F(1, 2) < number <= 1:
                raise ValidationError(f"study.uncertainty_axes.{path}[{index}]", "Phải lớn hơn 1/2 và không vượt 1.")
            if path == "judges.high_effort_cost_multiplier" and number < 0:
                raise ValidationError(f"study.uncertainty_axes.{path}[{index}]", "Không được âm.")

    gates = _exact_object(study["gates"], GATE_FIELDS, "study.gates")
    for field in GATE_FIELDS:
        value = gates[field] if isinstance(gates[field], F) else rational(gates[field], f"study.gates.{field}")
        if value < 0 or field in ("max_false_approval_rate", "max_false_rejection_rate") and value > 1:
            raise ValidationError(f"study.gates.{field}", "Gate nằm ngoài miền hợp lệ.")

    provenance = _exact_object(study["provenance"], ("status", "notes"), "study.provenance")
    if provenance["status"] not in PROVENANCE_STATUSES:
        raise ValidationError("study.provenance.status", "Cần assumption, pilot_estimate hoặc historical_estimate.")
    if not isinstance(provenance["notes"], str) or not provenance["notes"].strip():
        raise ValidationError("study.provenance.notes", "Cần ghi chú không rỗng.")

    normalized = deepcopy(study)
    normalized["base_config"] = base.raw()
    normalized["gates"] = {key: gates[key] if isinstance(gates[key], F) else rational(gates[key], f"study.gates.{key}")
                           for key in GATE_FIELDS}
    return normalized


def _set_path(raw, path, value):
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = str(value)


def expand_study(study):
    study = validate_robustness_study(study)
    axes = [path for path in UNCERTAINTY_PATHS if path in study["uncertainty_axes"]]
    combinations = list(product(*(study["uncertainty_axes"][path] for path in axes)))
    points = []
    for policy_index, policy in enumerate(study["policies"]):
        for scenario_index, values in enumerate(combinations):
            raw = deepcopy(study["base_config"])
            for path in POLICY_PATHS:
                if path in policy["overrides"]:
                    _set_path(raw, path, policy["overrides"][path])
            uncertainty = dict(zip(axes, values))
            for path in axes:
                value = uncertainty[path]
                if path == "verification_anchor.quality":
                    raw["verification_anchor"]["sensitivity"] = str(value)
                    raw["verification_anchor"]["specificity"] = str(value)
                elif path == "judges.high_effort_cost_multiplier":
                    multiplier = rational(value, path)
                    for judge in JUDGES:
                        raw["judges"][judge]["high_effort_cost"] = str(
                            F(study["base_config"]["judges"][judge]["high_effort_cost"]) * multiplier
                        )
                else:
                    _set_path(raw, path, value)
            points.append({
                "point_id": len(points),
                "policy_index": policy_index,
                "scenario_index": scenario_index,
                "policy_id": policy["policy_id"],
                "policy_overrides": deepcopy(policy["overrides"]),
                "uncertainty": uncertainty,
                "config": raw,
            })
    return points


def gate_equilibrium_summary(summary, gates):
    if summary.get("status") != "pure_equilibria_evaluated":
        return ["no_pure_equilibrium"], None
    worst = {
        "accuracy": summary["ranges"]["accuracy"]["min"],
        "false_approval_rate": summary["ranges"]["false_approval_rate"]["max"],
        "wrong_payout_value": summary["ranges"]["wrong_payout_value"]["max"],
        "false_rejection_rate": summary["ranges"]["false_rejection_rate"]["max"],
        "cash_review_cost": summary["ranges"]["cash_review_cost"]["max"],
    }
    checks = (
        ("false_approval_gate", "false_approval_rate", "max_false_approval_rate"),
        ("wrong_payout_gate", "wrong_payout_value", "max_wrong_payout_value"),
        ("false_rejection_gate", "false_rejection_rate", "max_false_rejection_rate"),
        ("cash_review_cost_gate", "cash_review_cost", "max_cash_review_cost"),
    )
    reasons = [reason for reason, metric, gate in checks if worst[metric] > gates[gate]]
    return reasons, worst


def public_signal_reference(config):
    false_approval = 1 - config.public_specificity
    false_rejection = 1 - config.public_sensitivity
    return {
        "status": "reference_only_not_equal_resources",
        "rule": "D=Z",
        "metrics": {
            "accuracy": config.pi * config.public_sensitivity + (1 - config.pi) * config.public_specificity,
            "false_approval_rate": false_approval,
            "false_rejection_rate": false_rejection,
            "wrong_payout_value": config.payout_value * (1 - config.pi) * false_approval,
        },
    }


def forced_all_high_reference(config):
    result = evaluate(config, build_candidate(config, FORCED_ALL_HIGH, mechanism="hybrid_anchor"), "hybrid_anchor")
    return {
        "status": "forced_candidate_not_equilibrium_claim",
        "profile": FORCED_ALL_HIGH.raw(),
        "metrics": {key: result["metrics"][key] for key in (
            "accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value", "cash_review_cost"
        )},
    }


def _run_point(point, gates, on_progress=None, points_total=None):
    result = {key: deepcopy(point[key]) for key in (
        "point_id", "policy_index", "scenario_index", "policy_id", "policy_overrides", "uncertainty", "config"
    )}
    try:
        config = validate_config(point["config"], "hybrid_anchor")
        result["config_hash"] = semantic_hash(config)

        def progress(value):
            if on_progress:
                on_progress({**value, "phase": "robustness_equilibria", "point": point["point_id"] + 1,
                             "points_total": points_total, "policy": point["policy_index"] + 1})

        search = search_pure(config, "hybrid_anchor", progress)
        result.update(
            branch_candidate_count=search["branch_candidate_count"],
            enumeration_completed=search["enumeration_completed"],
            full_equilibrium_count=search["full_equilibrium_count"],
            branch_equilibrium_ids={z: branch["equilibrium_ids"] for z, branch in search["branches"].items()},
            landscape={key: value for key, value in classify_landscape(search).items() if key != "candidates"},
        )
        if not search["enumeration_completed"] or search["branch_candidate_count"] != 432:
            result.update(status="fail", failure_reasons=["incomplete_search"], worst=None)
            return result
        equilibrium = summarize_equilibrium_metrics(config, search, "hybrid_anchor")
        reasons, worst = gate_equilibrium_summary(equilibrium, gates)
        result.update(
            status="pass" if not reasons else "fail",
            failure_reasons=reasons,
            worst=worst,
            equilibrium_metrics=equilibrium,
            references={
                "public_signal_rule": public_signal_reference(config),
                "forced_all_high": forced_all_high_reference(config),
            },
        )
        return result
    except ValidationError as error:
        reason = "invalid_budget" if error.field == "reward_budget" else "invalid_input"
        result.update(status="fail", failure_reasons=[reason], worst=None, error=str(error),
                      branch_candidate_count=0, enumeration_completed=False, full_equilibrium_count=None)
        return result


def _run_point_task(payload):
    point, gates, points_total = payload
    return _run_point(point, gates, on_progress=None, points_total=points_total)


def summarize_policies(points, policies):
    summaries = []
    for policy in policies:
        selected = [point for point in points if point["policy_id"] == policy["policy_id"]]
        failures = Counter(reason for point in selected for reason in point["failure_reasons"])
        eligible = bool(selected) and all(point.get("worst") is not None for point in selected)
        worst = witnesses = None
        if eligible:
            worst, witnesses = {}, {}
            for metric in ("accuracy", *RISK_METRICS):
                chooser = min if metric == "accuracy" else max
                value = chooser(point["worst"][metric] for point in selected)
                witness = next(point for point in selected if point["worst"][metric] == value)
                worst[metric] = value
                witnesses[metric] = witness["point_id"]
        summaries.append({
            "policy_id": policy["policy_id"],
            "overrides": deepcopy(policy["overrides"]),
            "point_count": len(selected),
            "pass_count": sum(point["status"] == "pass" for point in selected),
            "fail_count": sum(point["status"] != "pass" for point in selected),
            "robust": bool(selected) and all(point["status"] == "pass" for point in selected),
            "pareto_eligible": eligible,
            "failure_reason_counts": dict(sorted(failures.items())),
            "worst": worst,
            "witness_point_ids": witnesses,
        })
    return summaries


def classify_robustness(policy_summaries):
    count = sum(policy["robust"] for policy in policy_summaries)
    return "no_robust_policy" if count == 0 else "isolated_robust_point" if count == 1 else "observed_robust_set"


def pareto_frontier(policy_summaries):
    eligible = [policy for policy in policy_summaries if policy.get("pareto_eligible")]
    frontier, dominated_by = [], {}
    for candidate in eligible:
        dominators = []
        for other in eligible:
            if other["policy_id"] == candidate["policy_id"]:
                continue
            weak = all(other["worst"][metric] <= candidate["worst"][metric] for metric in RISK_METRICS)
            strict = any(other["worst"][metric] < candidate["worst"][metric] for metric in RISK_METRICS)
            if weak and strict:
                dominators.append(other["policy_id"])
        if dominators:
            dominated_by[candidate["policy_id"]] = dominators
        else:
            frontier.append(candidate["policy_id"])
    return {"metrics": list(RISK_METRICS), "policy_ids": frontier, "dominated_by": dominated_by,
            "scope": "complete_pure_equilibrium_policy_worst_cases"}


def _baseline_summary(points):
    rows = []
    for policy_id in dict.fromkeys(point["policy_id"] for point in points):
        selected = [point for point in points if point["policy_id"] == policy_id and "references" in point]
        if not selected:
            continue
        record = {"policy_id": policy_id, "scenario_count": len(selected)}
        for reference in ("public_signal_rule", "forced_all_high"):
            metrics = selected[0]["references"][reference]["metrics"]
            record[reference] = {
                key: (min(point["references"][reference]["metrics"][key] for point in selected)
                      if key == "accuracy" else max(point["references"][reference]["metrics"][key] for point in selected))
                for key in metrics
            }
            record[reference]["status"] = selected[0]["references"][reference]["status"]
        rows.append(record)
    return {"policies": rows, "equal_reward_budget_across_policies": True, "judge_count": 3,
            "latency_comparison": "latency_not_modeled", "grid_only_no_interpolation": True}


def run_robustness_study(raw_study, on_progress=None):
    study = validate_robustness_study(raw_study)
    expanded = expand_study(study)
    points = []
    if len(expanded) == 1:
        points.append(_run_point(expanded[0], study["gates"], on_progress, len(expanded)))
        if on_progress:
            on_progress({"phase": "robustness", "completed": 1, "total": 1,
                         "policy": expanded[0]["policy_index"] + 1, "policies_total": len(study["policies"])})
    else:
        workers = min(4, len(expanded))
        payloads = [(point, study["gates"], len(expanded)) for point in expanded]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_run_point_task, payload) for payload in payloads]
            for index, future in enumerate(as_completed(futures), start=1):
                points.append(future.result())
                if on_progress:
                    on_progress({"phase": "robustness", "completed": index, "total": len(expanded),
                                 "policy": None, "policies_total": len(study["policies"])})
        points.sort(key=lambda point: point["point_id"])
    policies = summarize_policies(points, study["policies"])
    classification = classify_robustness(policies)
    failures = Counter(reason for point in points for reason in point["failure_reasons"])
    pareto = pareto_frontier(policies)
    baselines = _baseline_summary(points)
    scenario_count = len(points) // len(study["policies"])
    return {
        "analysis_version": ROBUSTNESS_VERSION,
        "model_version": V3_MODEL_VERSION,
        "status": "succeeded",
        "scope": "declared_grid_exact_pure_equilibrium_worst_case",
        "grid": {
            "policy_count": len(study["policies"]),
            "scenario_count_per_policy": scenario_count,
            "total_points": len(points),
            "uncertainty_axes": deepcopy(study["uncertainty_axes"]),
            "grid_only_no_interpolation": True,
        },
        "gates": deepcopy(study["gates"]),
        "provenance": deepcopy(study["provenance"]),
        "classification": classification,
        "robust_policy_ids": [policy["policy_id"] for policy in policies if policy["robust"]],
        "policies": policies,
        "points": points,
        "failure_map": {"reason_counts": dict(sorted(failures.items())),
                        "failed_point_ids": [point["point_id"] for point in points if point["status"] != "pass"]},
        "pareto_frontier": pareto,
        "baseline_comparison": baselines,
        "limitations": [
            "synthetic_or_assumption_ranges_are_not_confidence_intervals",
            "pure_strategies_only",
            "conditional_independence_unchanged",
            "no_participation_collusion_sybil_or_stake",
            "latency_not_modeled",
            "verification_anchor_does_not_change_decision_or_payout",
        ],
    }


def _point_csv(point):
    row = {
        "point_id": point["point_id"], "policy_id": point["policy_id"], "scenario_index": point["scenario_index"],
        "status": point["status"], "failure_reasons": ";".join(point["failure_reasons"]),
        "config_hash": point.get("config_hash"), "branch_candidate_count": point.get("branch_candidate_count"),
        "enumeration_completed": point.get("enumeration_completed"), "full_equilibrium_count": point.get("full_equilibrium_count"),
    }
    row.update({f"uncertainty:{key}": F(value) for key, value in point["uncertainty"].items()})
    if point.get("worst"):
        row.update({f"worst_{key}": value for key, value in point["worst"].items()})
    return row


def _policy_csv(policy):
    row = {key: policy[key] for key in ("policy_id", "point_count", "pass_count", "fail_count", "robust", "pareto_eligible")}
    row["overrides_json"] = json.dumps(policy["overrides"], sort_keys=True)
    row["failure_reasons_json"] = json.dumps(policy["failure_reason_counts"], sort_keys=True)
    if policy["worst"]:
        row.update({f"worst_{key}": value for key, value in policy["worst"].items()})
    return row


def write_robustness_run(raw_study, out, argv=None, defer_publication=False, on_progress=None):
    study = validate_robustness_study(raw_study)
    base = validate_config(study["base_config"], "hybrid_anchor")
    out = Path(out)
    request = {**deepcopy(study), "gates": {key: str(value) for key, value in study["gates"].items()}}
    manifest = new_run(out, "robustness", base, mechanism="hybrid_anchor", request=request, argv=argv,
                       publication_owner="local_server" if defer_publication else "cli")
    freeze = FREEZES[V3_MODEL_VERSION]
    manifest["analysis"] = {
        "version": ROBUSTNESS_VERSION,
        "revision": "robustness-grid-r1",
        "snapshot": freeze + "/CEAV_M1_V3_1_ROBUSTNESS_SPEC.md",
        "grid_only_no_interpolation": True,
    }
    write_json(out / "manifest.json", manifest)
    try:
        result = run_robustness_study(study, on_progress)
        write_json(out / "robustness.json", result)
        write_csv(out / "robustness_points.csv", [_point_csv(point) for point in result["points"]])
        write_csv(out / "policy_summary.csv", [_policy_csv(policy) for policy in result["policies"]])
        write_json(out / "failure_map.json", result["failure_map"])
        write_json(out / "pareto_frontier.json", result["pareto_frontier"])
        write_json(out / "baseline_comparison.json", result["baseline_comparison"])
        lines = [
            "# CEAV-M1 V3.1 — Robustness",
            "",
            f"Classification: **{result['classification']}**.",
            "",
            f"Đã hoàn tất {result['grid']['total_points']} point = {result['grid']['policy_count']} policy × {result['grid']['scenario_count_per_policy']} uncertainty scenarios.",
            "",
            "## Policy worst cases",
            "",
            "| Policy | Robust | Pass/total | Worst false approval | Worst wrongly paid | Worst false rejection | Worst cash cost |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for policy in result["policies"]:
            worst = policy["worst"] or {}
            lines.append(
                f"| {policy['policy_id']} | {policy['robust']} | {policy['pass_count']}/{policy['point_count']} | "
                f"{worst.get('false_approval_rate', '—')} | {worst.get('wrong_payout_value', '—')} | "
                f"{worst.get('false_rejection_rate', '—')} | {worst.get('cash_review_cost', '—')} |"
            )
        lines += [
            "", "## Failure map", "",
            json.dumps(result["failure_map"]["reason_counts"], sort_keys=True),
            "", "## Pareto frontier", "",
            ", ".join(result["pareto_frontier"]["policy_ids"]) or "Không có policy eligible.",
            "", "Ranges trong run này là assumption/pilot/historical theo provenance; không tự trở thành confidence interval.",
            "Latency: `latency_not_modeled`. V3.1 giữ nguyên game V3, pure strategies và conditional independence; không chứng minh production readiness.", "",
        ]
        (out / "report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest)
        return result
    except BaseException as error:
        if not defer_publication:
            finish_run(out, manifest, "failed", error)
        raise
