"""V3.2 finite study for report-contingent per-Judge spot checks."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

from . import V32_MODEL_VERSION
from .equilibria import search_pure, summarize_equilibrium_metrics
from .incentives import classify_landscape
from .model import JUDGES, ValidationError, rational, validate_config
from .output import FREEZES, finish_run, new_run, semantic_hash, write_csv, write_json


REPORT_SENSITIVE_VERSION = "ceav-m1-v3.2-report-sensitive"
POLICY_PATHS = (
    "verification_anchor.audit_probability_by_report",
    "lambda_peer",
    "anchor_weight",
)
UNCERTAINTY_PATHS = (
    "pi",
    "verification_anchor.quality",
    "judges.high_effort_cost_multiplier",
)
GATE_FIELDS = ("max_false_approval_rate", "max_wrong_payout_value", "max_false_rejection_rate", "max_cash_review_cost")
RISK_METRICS = ("false_approval_rate", "wrong_payout_value", "false_rejection_rate", "cash_review_cost")
PROVENANCE_STATUSES = ("assumption", "pilot_estimate", "historical_estimate")


def _exact_object(value, allowed, field):
    if not isinstance(value, dict):
        raise ValidationError(field, "Cần JSON object.")
    unknown = set(value) - set(allowed)
    missing = set(allowed) - set(value)
    if unknown:
        key = sorted(unknown)[0]
        raise ValidationError(f"{field}.{key}" if field else key, "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(field, "Thiếu field bắt buộc.")
    return value


def load_report_sensitive_study(path):
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(raw.get("base_config"), str):
        base = (path.resolve().parent / raw["base_config"]).resolve()
        raw["base_config"] = json.loads(base.read_text(encoding="utf-8-sig"))
    return raw


def validate_report_sensitive_study(raw):
    study = _exact_object(raw, ("analysis_version", "base_config", "policies", "uncertainty_axes", "gates", "baseline_policy_id", "provenance"), "study")
    if study["analysis_version"] != REPORT_SENSITIVE_VERSION:
        raise ValidationError("study.analysis_version", f"Cần {REPORT_SENSITIVE_VERSION}.")
    base = validate_config(study["base_config"], "hybrid_anchor")
    if base.model_version != V32_MODEL_VERSION:
        raise ValidationError("study.base_config.model_version", "V3.2 study yêu cầu ceav-m1-v3.2.")
    policies = study["policies"]
    if not isinstance(policies, list) or not policies:
        raise ValidationError("study.policies", "Cần danh sách policy không rỗng.")
    seen = set()
    for index, policy in enumerate(policies):
        policy = _exact_object(policy, ("policy_id", "label", "overrides"), f"study.policies[{index}]")
        identity = policy["policy_id"]
        if not isinstance(identity, str) or not identity or identity in seen:
            raise ValidationError(f"study.policies[{index}].policy_id", "Cần ID duy nhất.")
        seen.add(identity)
        overrides = policy["overrides"]
        if not isinstance(overrides, dict) or not overrides:
            raise ValidationError(f"study.policies[{index}].overrides", "Cần object override không rỗng.")
        unknown = set(overrides) - set(POLICY_PATHS)
        if unknown:
            key = sorted(unknown)[0]
            raise ValidationError(f"study.policies[{index}].overrides.{key}", "Policy path không được hỗ trợ.")
        if "verification_anchor.audit_probability_by_report" in overrides:
            q = _exact_object(overrides["verification_anchor.audit_probability_by_report"], ("0", "1"), f"study.policies[{index}].overrides.verification_anchor.audit_probability_by_report")
            for report in ("0", "1"):
                value = rational(q[report], f"study.policies[{index}].overrides.verification_anchor.audit_probability_by_report.{report}")
                if not 0 <= value <= 1:
                    raise ValidationError(f"study.policies[{index}].overrides.verification_anchor.audit_probability_by_report.{report}", "Phải thuộc [0,1].")
        for path, value in overrides.items():
            if path != "verification_anchor.audit_probability_by_report":
                rational(value, f"study.policies[{index}].overrides.{path}")
    axes = _exact_object(study["uncertainty_axes"], UNCERTAINTY_PATHS, "study.uncertainty_axes")
    for path, values in axes.items():
        if not isinstance(values, list) or not values:
            raise ValidationError(f"study.uncertainty_axes.{path}", "Cần danh sách không rỗng.")
        for index, value in enumerate(values):
            number = rational(value, f"study.uncertainty_axes.{path}[{index}]")
            if path == "pi" and not 0 < number < 1:
                raise ValidationError(f"study.uncertainty_axes.{path}[{index}]", "pi phải thuộc (0,1).")
            if path == "verification_anchor.quality" and not F(1, 2) < number <= 1:
                raise ValidationError(f"study.uncertainty_axes.{path}[{index}]", "Chất lượng phải thuộc (1/2,1].")
            if path == "judges.high_effort_cost_multiplier" and number < 0:
                raise ValidationError(f"study.uncertainty_axes.{path}[{index}]", "Multiplier không được âm.")
    gates = _exact_object(study["gates"], GATE_FIELDS, "study.gates")
    normalized_gates = {}
    for field in GATE_FIELDS:
        value = gates[field] if isinstance(gates[field], F) else rational(gates[field], f"study.gates.{field}")
        if value < 0 or field in ("max_false_approval_rate", "max_false_rejection_rate") and value > 1:
            raise ValidationError(f"study.gates.{field}", "Gate nằm ngoài miền hợp lệ.")
        normalized_gates[field] = value
    provenance = _exact_object(study["provenance"], ("status", "notes"), "study.provenance")
    if provenance["status"] not in PROVENANCE_STATUSES or not isinstance(provenance["notes"], str) or not provenance["notes"].strip():
        raise ValidationError("study.provenance", "Cần provenance status và notes hợp lệ.")
    normalized = deepcopy(study)
    normalized["base_config"] = base.raw()
    normalized["gates"] = normalized_gates
    return normalized


def _apply_path(raw, path, value):
    if path == "verification_anchor.audit_probability_by_report":
        raw["verification_anchor"]["audit_probability_by_report"] = {"0": str(value["0"]), "1": str(value["1"])}
        return
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = str(value)


def expand_report_sensitive_study(study):
    study = validate_report_sensitive_study(study)
    axes = list(study["uncertainty_axes"])
    combinations = list(product(*(study["uncertainty_axes"][path] for path in axes)))
    points = []
    for policy_index, policy in enumerate(study["policies"]):
        for scenario_index, values in enumerate(combinations):
            raw = deepcopy(study["base_config"])
            for path, value in policy["overrides"].items():
                _apply_path(raw, path, value)
            uncertainty = dict(zip(axes, values))
            for path, value in uncertainty.items():
                if path == "verification_anchor.quality":
                    raw["verification_anchor"]["sensitivity"] = str(value)
                    raw["verification_anchor"]["specificity"] = str(value)
                elif path == "judges.high_effort_cost_multiplier":
                    multiplier = rational(value, path)
                    for judge in JUDGES:
                        raw["judges"][judge]["high_effort_cost"] = str(F(study["base_config"]["judges"][judge]["high_effort_cost"]) * multiplier)
                else:
                    _apply_path(raw, path, value)
            points.append({"point_id": len(points), "policy_index": policy_index, "scenario_index": scenario_index,
                           "policy_id": policy["policy_id"], "policy_overrides": deepcopy(policy["overrides"]),
                           "uncertainty": uncertainty, "config": raw})
    return points


def _failure_witnesses(search, point_id):
    witnesses = []
    for z, branch in search["branches"].items():
        for candidate in branch["candidates"]:
            for certificate in candidate["certificates"]:
                if certificate.get("witness") is not None:
                    witness = certificate["witness"]
                    old_action = witness.get("old_action", certificate.get("candidate_action"))
                    new_action = witness.get("action")
                    if old_action and new_action and old_action[0] != new_action[0]:
                        failure_type = "effort_cost"
                    elif old_action and new_action and old_action != new_action:
                        failure_type = "report_sensitive_anchor"
                    else:
                        failure_type = "peer_score"
                    witnesses.append({"point_id": point_id, "branch_candidate": candidate["id"], "z": int(z),
                                      "judge": certificate["judge"], "failure_type": failure_type, "witness": witness})
    return witnesses


def _gate_summary(summary, gates):
    if summary.get("status") != "pure_equilibria_evaluated":
        return ["no_pure_equilibrium"], None
    worst = {"accuracy": summary["ranges"]["accuracy"]["min"],
             "false_approval_rate": summary["ranges"]["false_approval_rate"]["max"],
             "wrong_payout_value": summary["ranges"]["wrong_payout_value"]["max"],
             "false_rejection_rate": summary["ranges"]["false_rejection_rate"]["max"],
             "cash_review_cost": summary["ranges"]["cash_review_cost"]["max"]}
    checks = (("false_approval_gate", "false_approval_rate", "max_false_approval_rate"),
              ("wrong_payout_gate", "wrong_payout_value", "max_wrong_payout_value"),
              ("false_rejection_gate", "false_rejection_rate", "max_false_rejection_rate"),
              ("cash_review_cost_gate", "cash_review_cost", "max_cash_review_cost"))
    return [reason for reason, metric, gate in checks if worst[metric] > gates[gate]], worst


def _run_point(point, gates):
    result = {key: deepcopy(point[key]) for key in ("point_id", "policy_index", "scenario_index", "policy_id", "policy_overrides", "uncertainty", "config")}
    try:
        config = validate_config(point["config"], "hybrid_anchor")
        result["config_hash"] = semantic_hash(config)
        search = search_pure(config, "hybrid_anchor")
        witnesses = _failure_witnesses(search, point["point_id"])
        result.update(branch_candidate_count=search["branch_candidate_count"], enumeration_completed=search["enumeration_completed"],
                      full_equilibrium_count=search["full_equilibrium_count"],
                      branch_equilibrium_ids={z: branch["equilibrium_ids"] for z, branch in search["branches"].items()},
                      landscape={key: value for key, value in classify_landscape(search).items() if key != "candidates"},
                      failure_witnesses=witnesses,
                      failure_decomposition=dict(sorted(Counter(witness["failure_type"] for witness in witnesses).items())))
        if not search["enumeration_completed"] or search["branch_candidate_count"] != 432:
            result.update(status="fail", failure_reasons=["incomplete_search"], worst=None, equilibrium_metrics=None)
            return result
        equilibrium = summarize_equilibrium_metrics(config, search, "hybrid_anchor")
        reasons, worst = _gate_summary(equilibrium, gates)
        result.update(status="pass" if not reasons else "fail", failure_reasons=reasons, worst=worst, equilibrium_metrics=equilibrium)
        return result
    except ValidationError as error:
        result.update(status="fail", failure_reasons=["invalid_budget" if error.field == "reward_budget" else "invalid_input"],
                      worst=None, error=str(error), branch_candidate_count=0, enumeration_completed=False,
                      full_equilibrium_count=None, failure_witnesses=[], failure_decomposition={})
        return result


def summarize_report_sensitive_policies(points, policies):
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
        summaries.append({"policy_id": policy["policy_id"], "label": policy["label"], "overrides": deepcopy(policy["overrides"]),
                          "point_count": len(selected), "pass_count": sum(point["status"] == "pass" for point in selected),
                          "fail_count": sum(point["status"] != "pass" for point in selected), "robust": bool(selected) and all(point["status"] == "pass" for point in selected),
                          "pareto_eligible": eligible, "failure_reason_counts": dict(sorted(failures.items())), "worst": worst,
                          "witness_point_ids": witnesses})
    return summaries


def run_report_sensitive_study(raw_study, on_progress=None):
    study = validate_report_sensitive_study(raw_study)
    expanded = expand_report_sensitive_study(study)
    points = []
    for index, point in enumerate(expanded, start=1):
        points.append(_run_point(point, study["gates"]))
        if on_progress:
            on_progress({"phase": "report_sensitive", "completed": index, "total": len(expanded), "policy": point["policy_index"] + 1})
    policies = summarize_report_sensitive_policies(points, study["policies"])
    return {"analysis_version": REPORT_SENSITIVE_VERSION, "model_version": V32_MODEL_VERSION, "status": "succeeded",
            "scope": "declared_grid_exact_pure_equilibrium_worst_case", "grid": {"policy_count": len(study["policies"]),
            "scenario_count_per_policy": len(points) // len(study["policies"]), "total_points": len(points),
            "uncertainty_axes": deepcopy(study["uncertainty_axes"]), "grid_only_no_interpolation": True},
            "gates": deepcopy(study["gates"]), "provenance": deepcopy(study["provenance"]), "policies": policies,
            "robust_policy_ids": [policy["policy_id"] for policy in policies if policy["robust"]], "points": points,
            "failure_map": {"reason_counts": dict(sorted(Counter(reason for point in points for reason in point["failure_reasons"]).items())),
                            "failed_point_ids": [point["point_id"] for point in points if point["status"] != "pass"]},
            "limitations": ["q0_q1_are_per_judge_audits", "assumption_ranges_are_not_confidence_intervals", "pure_strategies_only",
                            "no_participation_collusion_sybil_or_stake", "audit_does_not_change_decision_or_payout"]}


def _point_csv(point):
    row = {"point_id": point["point_id"], "policy_id": point["policy_id"], "scenario_index": point["scenario_index"],
           "status": point["status"], "failure_reasons": ";".join(point["failure_reasons"]), "config_hash": point.get("config_hash"),
           "branch_candidate_count": point.get("branch_candidate_count"), "enumeration_completed": point.get("enumeration_completed"),
           "full_equilibrium_count": point.get("full_equilibrium_count")}
    row.update({f"uncertainty:{key}": F(value) for key, value in point["uncertainty"].items()})
    if point.get("worst"):
        row.update({f"worst_{key}": value for key, value in point["worst"].items()})
    return row


def write_report_sensitive_run(raw_study, out, argv=None, defer_publication=False, on_progress=None):
    study = validate_report_sensitive_study(raw_study)
    base = validate_config(study["base_config"], "hybrid_anchor")
    request = {**deepcopy(study), "gates": {key: str(value) for key, value in study["gates"].items()}}
    manifest = new_run(out, "report_sensitive", base, mechanism="hybrid_anchor", request=request, argv=argv,
                       publication_owner="local_server" if defer_publication else "cli")
    manifest["analysis"] = {"version": REPORT_SENSITIVE_VERSION, "revision": "report-sensitive-spot-check-r1",
                             "snapshot": FREEZES[V32_MODEL_VERSION] + "/CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md", "grid_only_no_interpolation": True}
    write_json(Path(out) / "manifest.json", manifest)
    try:
        result = run_report_sensitive_study(study, on_progress)
        out = Path(out)
        write_json(out / "report_sensitive.json", result)
        write_csv(out / "report_sensitive_points.csv", [_point_csv(point) for point in result["points"]])
        write_json(out / "failure_map.json", result["failure_map"])
        lines = ["# CEAV-M1 V3.2 — Report-sensitive spot-checking", "", f"Đã hoàn tất {result['grid']['total_points']} point.", "",
                 "Failure witnesses được lưu trong report_sensitive.json; mỗi q0/q1 là audit riêng cho một Judge.", ""]
        for policy in result["policies"]:
            worst = policy["worst"] or {}
            lines.append(f"- {policy['policy_id']}: robust={policy['robust']} pass={policy['pass_count']}/{policy['point_count']} worst_FA={worst.get('false_approval_rate', '—')} witnesses={policy['witness_point_ids'] or '—'}")
        (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest)
        return result
    except BaseException as error:
        if not defer_publication:
            finish_run(out, manifest, "failed", error)
        raise
