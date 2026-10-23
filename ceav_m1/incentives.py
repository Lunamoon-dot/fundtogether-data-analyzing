"""Exact incentive decomposition and pure-equilibrium landscapes for V2."""

from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import shutil

from . import V2_MODEL_VERSION
from .equilibria import search_pure
from .evaluate import analyze
from .model import JUDGES, ValidationError, rational, validate_config, validate_scenario
from .output import ROOT, finish_run, new_run, semantic_hash, sha256, write_csv, write_json
from .strategies import validate_profile


INCENTIVE_VERSION = "ceav-m1-v2.2-incentive-diagnostics"
INCENTIVE_FREEZE = "spec_history/v2.2-incentives-implementation-start-20261022T2025258297100Z"
INCENTIVE_AXES = (
    "pi", "public_signal.sensitivity", "public_signal.specificity",
    "judges.A.private_signal.sensitivity", "judges.A.private_signal.specificity", "judges.A.high_effort_cost",
    "judges.B.private_signal.sensitivity", "judges.B.private_signal.specificity", "judges.B.high_effort_cost",
    "judges.C.private_signal.sensitivity", "judges.C.private_signal.specificity", "judges.C.high_effort_cost",
    "lambda", "reward_budget",
)
HIGH_ACTIONS = ("H00", "H01", "H10", "H11")
DEPENDENT_ACTIONS = frozenset(("H01", "H10"))
IGNORED_ACTIONS = frozenset(("H00", "H11"))
LANDSCAPE_CLASSES = (
    "all_low", "all_high_signal_dependent", "all_high_signal_ignored",
    "all_high_mixed_report", "mixed_effort",
)


def _sign_status(value):
    return "PREFERRED" if value > 0 else "TIED" if value == 0 else "NOT_PREFERRED"


def _threshold(gain, cost, lambda_max):
    if gain > 0:
        value = cost / gain
        return value, "BUDGET_FEASIBLE" if value <= lambda_max else "BUDGET_INFEASIBLE"
    if gain == 0 and cost == 0:
        return F(0), "BUDGET_FEASIBLE"
    return None, "UNATTAINABLE_BY_LAMBDA"


def _high_action_scores(observations):
    scores = {}
    for action in HIGH_ACTIONS:
        score = F(0)
        for observation in observations:
            key = observation["observation"]
            x = int(key[1])
            report = int(action[1 + x])
            score += observation["probability_given_z"] * (
                observation["information_by_report"][report] + observation["optimal_prediction_score"]
            )
        scores[action] = score
    return scores


def decompose_branch(config, certificate):
    """Decompose one peer-frozen best-response certificate."""
    judge = certificate["judge"]
    index = JUDGES.index(judge)
    cost = config.costs[index]
    low_score = certificate["low"]["score"]
    action_scores = _high_action_scores(certificate["high"]["observations"])
    best_high = max(action_scores.values())
    if best_high != certificate["high"]["score"]:
        raise AssertionError("High action scores do not reproduce best-response certificate")
    dependent_high = max(action_scores[action] for action in DEPENDENT_ACTIONS)
    best_actions = [action for action in HIGH_ACTIONS if action_scores[action] == best_high]
    dependent_best_actions = [action for action in DEPENDENT_ACTIONS if action_scores[action] == dependent_high]
    has_dependent = any(action in DEPENDENT_ACTIONS for action in best_actions)
    has_ignored = any(action in IGNORED_ACTIONS for action in best_actions)
    report_status = (
        "TIE_DEPENDENT_AND_IGNORED" if has_dependent and has_ignored else
        "SIGNAL_DEPENDENT_ONLY" if has_dependent else
        "SIGNAL_IGNORED_ONLY"
    )
    gain_best = best_high - low_score
    gain_dependent = dependent_high - low_score
    if gain_best < 0:
        raise AssertionError("Value-of-information invariant failed in diagnostics")
    net_best = config.multiplier * gain_best - cost
    net_dependent = config.multiplier * gain_dependent - cost
    lambda_max = (config.reward_budget - 3 * config.f) / 6
    threshold_best, budget_best = _threshold(gain_best, cost, lambda_max)
    threshold_dependent, budget_dependent = _threshold(gain_dependent, cost, lambda_max)
    if net_best != certificate["high"]["utility"] - certificate["low"]["utility"]:
        raise AssertionError("Net effort incentive does not match best-response utility delta")
    return {
        "judge": judge,
        "z": certificate["z"],
        "candidate_action": certificate["candidate_action"],
        "low_score": low_score,
        "best_high_score": best_high,
        "dependent_high_score": dependent_high,
        "high_action_scores": action_scores,
        "best_high_actions": best_actions,
        "dependent_best_actions": dependent_best_actions,
        "information_gain_best": gain_best,
        "information_gain_dependent": gain_dependent,
        "report_utilization_gap": best_high - dependent_high,
        "effort_cost": cost,
        "lambda": config.multiplier,
        "lambda_max": lambda_max,
        "net_incentive_best": net_best,
        "net_incentive_dependent": net_dependent,
        "lambda_star_best": threshold_best,
        "lambda_star_dependent": threshold_dependent,
        "effort": {"best_high_status": _sign_status(net_best)},
        "dependent_report": {"status": _sign_status(net_dependent)},
        "report": {"status": report_status},
        "budget": {"best_high": budget_best, "dependent_high": budget_dependent},
        "conditional_on_fixed_peer_strategies": True,
    }


def diagnose_candidate(config, profile, analysis=None):
    if config.model_version != V2_MODEL_VERSION:
        raise ValidationError("model_version", "V2.2 diagnostics chỉ hỗ trợ ceav-m1-v2.0.")
    analysis = analyze(config, profile, "rbts") if analysis is None else analysis
    branches = [decompose_branch(config, certificate) for certificate in analysis["best_responses"]]
    return {
        "feature_version": INCENTIVE_VERSION,
        "model_version": config.model_version,
        "mechanism": "rbts",
        "scope": "conditional_candidate_diagnostics_with_fixed_peer_strategies",
        "config": config.raw(),
        "profile": profile.raw(),
        "candidate_equilibrium_status": analysis["equilibrium_status"],
        "candidate_max_regret": analysis["max_regret"],
        "candidate_metrics": analysis["metrics"],
        "candidate_utility_vector": analysis["metrics"]["expected_judge_utility"],
        "branches": branches,
        "warning": "Conditional thresholds hold only for the pinned peer strategy; they are not global equilibrium guarantees.",
    }


def _classify_actions(actions):
    efforts = {action[0] for action in actions}
    if efforts == {"L"}:
        return "all_low"
    if efforts == {"L", "H"}:
        return "mixed_effort"
    action_set = set(actions)
    if action_set <= DEPENDENT_ACTIONS:
        return "all_high_signal_dependent"
    if action_set <= IGNORED_ACTIONS:
        return "all_high_signal_ignored"
    return "all_high_mixed_report"


def classify_landscape(search):
    if not search.get("enumeration_completed") or search.get("branch_candidate_count") != 432:
        raise ValueError("Landscape requires a completed exhaustive 432-candidate search")
    retained = {}
    branches = {}
    for z in ("0", "1"):
        rows = [row for row in search["branches"][z]["candidates"] if row["accepted"]]
        ids = [row["id"] for row in rows]
        if ids != search["branches"][z]["equilibrium_ids"]:
            raise AssertionError("Retained equilibrium IDs changed before classification")
        counts = {name: 0 for name in LANDSCAPE_CLASSES}
        classified = []
        for row in rows:
            category = _classify_actions(row["actions"])
            counts[category] += 1
            classified.append({"id": row["id"], "actions": row["actions"], "class": category})
        retained[z] = rows
        branches[z] = {"equilibrium_count": len(rows), "equilibrium_ids": ids,
                       "class_counts": counts, "equilibria": classified}
    full_counts = {name: 0 for name in LANDSCAPE_CLASSES}
    for left, right in product(retained["0"], retained["1"]):
        full_counts[_classify_actions([*left["actions"], *right["actions"]])] += 1
    total = sum(full_counts.values())
    if total != search["full_equilibrium_count"]:
        raise AssertionError("Full equilibrium classification does not reproduce solver count")
    low = full_counts["all_low"] > 0
    dependent = full_counts["all_high_signal_dependent"] > 0
    ignored = full_counts["all_high_signal_ignored"] > 0
    return {
        "strategy_scope": search["strategy_scope"],
        "equilibrium_concept": search["equilibrium_concept"],
        "enumeration_completed": True,
        "branch_candidate_count": 432,
        "full_profile_count": search["full_profile_count"],
        "full_equilibrium_count": total,
        "branches": branches,
        "full_class_counts": full_counts,
        "low_effort_exists": low,
        "all_high_signal_dependent_exists": dependent,
        "all_high_signal_ignored_exists": ignored,
        "coexistence_low_and_dependent_high": low and dependent,
        "claims_equilibrium_selection": False,
    }


def validate_incentive_axes(axes):
    axes = {} if axes is None else axes
    if not isinstance(axes, dict) or set(axes) - set(INCENTIVE_AXES):
        raise ValidationError("axes", "Incentive sweep chứa axis không được hỗ trợ.")
    ordered = [key for key in INCENTIVE_AXES if key in axes]
    for key in ordered:
        if not isinstance(axes[key], list) or not axes[key]:
            raise ValidationError(f"axes.{key}", "Cần danh sách chuỗi hữu tỉ không rỗng.")
        for value in axes[key]:
            rational(value, f"axes.{key}")
    return ordered


def _set_axis(raw, path, value):
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def run_incentive_study(raw_config, raw_profile, axes=None, on_progress=None):
    base = validate_config(raw_config, "rbts")
    if base.model_version != V2_MODEL_VERSION:
        raise ValidationError("model_version", "V2.2 diagnostics chỉ hỗ trợ ceav-m1-v2.0.")
    profile = validate_profile(raw_profile)
    ordered_axes = validate_incentive_axes(axes)
    canonical_axes = {key: list(axes[key]) for key in ordered_axes} if axes else {}
    base_diagnostics = diagnose_candidate(base, profile)
    grid = list(product(*(canonical_axes[key] for key in ordered_axes))) if ordered_axes else [()]
    points = []
    for point_id, values in enumerate(grid):
        raw = deepcopy(base.raw())
        row = {"point_id": point_id}
        for key, value in zip(ordered_axes, values):
            row[key] = rational(value, f"axes.{key}")
            _set_axis(raw, key, value)
        row["config_json"] = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        try:
            config = validate_config(raw, "rbts")
            analysis = analyze(config, profile, "rbts")
            diagnostics = diagnose_candidate(config, profile, analysis)

            def search_progress(progress):
                if on_progress:
                    on_progress({"phase": "incentive_equilibria", "point": point_id + 1,
                                 "points": len(grid), "completed": progress["completed"], "total": progress["total"]})

            landscape = classify_landscape(search_pure(config, "rbts", search_progress))
            row.update(status="valid", config_hash=semantic_hash(config), diagnostics=diagnostics,
                       landscape=landscape, candidate_equilibrium_status=analysis["equilibrium_status"],
                       candidate_max_regret=analysis["max_regret"], candidate_metrics=analysis["metrics"])
        except ValidationError as error:
            row.update(status="invalid_budget" if error.field == "reward_budget" else "invalid_input",
                       error_field=error.field, error=str(error))
        points.append(row)
        if on_progress:
            on_progress({"phase": "incentive_points", "completed": point_id + 1, "total": len(grid)})
    return {
        "feature_version": INCENTIVE_VERSION,
        "model_version": V2_MODEL_VERSION,
        "mechanism": "rbts",
        "config": base.raw(),
        "profile": profile.raw(),
        "axes": canonical_axes,
        "base_diagnostics": base_diagnostics,
        "points": points,
        "scope": "conditional_local_diagnostics_plus_exhaustive_pure_equilibrium_search_per_valid_point",
        "claims_mixed_equilibrium_coverage": False,
        "claims_equilibrium_selection": False,
    }


def incentive_documents():
    folder = ROOT / INCENTIVE_FREEZE
    event = json.loads((folder / "manifest.json").read_text(encoding="utf-8-sig"))
    if event.get("event") != "implementation_start" or event.get("feature") != INCENTIVE_VERSION:
        raise ValueError("Invalid incentive diagnostics implementation-start freeze")
    if event.get("production_module_existed_before_event") is not False or not event.get("fixture_preexisted"):
        raise ValueError("Invalid V2.2 implementation-start provenance")
    for record in event["files"]:
        if sha256((folder / record["snapshot"]).read_bytes()) != record["sha256"]:
            raise ValueError("Incentive diagnostics freeze checksum mismatch: " + record["snapshot"])
    return event


def _diagnostic_csv_rows(diagnostics):
    rows = []
    for item in diagnostics["branches"]:
        rows.append({
            "judge": item["judge"], "z": item["z"], "candidate_action": item["candidate_action"],
            "low_score": item["low_score"], "best_high_score": item["best_high_score"],
            "dependent_high_score": item["dependent_high_score"],
            "information_gain_best": item["information_gain_best"],
            "information_gain_dependent": item["information_gain_dependent"],
            "report_utilization_gap": item["report_utilization_gap"], "effort_cost": item["effort_cost"],
            "net_incentive_best": item["net_incentive_best"],
            "net_incentive_dependent": item["net_incentive_dependent"],
            "lambda_star_best": item["lambda_star_best"] if item["lambda_star_best"] is not None else "UNATTAINABLE_BY_LAMBDA",
            "lambda_star_dependent": item["lambda_star_dependent"] if item["lambda_star_dependent"] is not None else "UNATTAINABLE_BY_LAMBDA",
            "lambda_max": item["lambda_max"], "effort_status": item["effort"]["best_high_status"],
            "dependent_status": item["dependent_report"]["status"], "report_status": item["report"]["status"],
            "budget_best": item["budget"]["best_high"], "budget_dependent": item["budget"]["dependent_high"],
        })
    return rows


def _sweep_csv_rows(study):
    rows = []
    for point in study["points"]:
        row = {"point_id": point["point_id"], "status": point["status"], "config_json": point["config_json"]}
        for axis in study["axes"]:
            row[axis] = point[axis]
        if point["status"] == "valid":
            landscape = point["landscape"]
            row.update(config_hash=point["config_hash"], candidate_equilibrium_status=point["candidate_equilibrium_status"],
                       candidate_max_regret=point["candidate_max_regret"], branch_candidate_count=landscape["branch_candidate_count"],
                       full_equilibrium_count=landscape["full_equilibrium_count"], low_effort_exists=landscape["low_effort_exists"],
                       all_high_signal_dependent_exists=landscape["all_high_signal_dependent_exists"],
                       all_high_signal_ignored_exists=landscape["all_high_signal_ignored_exists"],
                       coexistence_low_and_dependent_high=landscape["coexistence_low_and_dependent_high"])
        else:
            row.update(error_field=point.get("error_field"), error=point.get("error"))
        rows.append(row)
    return rows


def write_incentive_run(raw_config, raw_profile, out, axes=None, scenario=None, argv=None,
                        defer_publication=False, on_progress=None):
    config = validate_config(raw_config, "rbts")
    if config.model_version != V2_MODEL_VERSION:
        raise ValidationError("model_version", "V2.2 diagnostics chỉ hỗ trợ ceav-m1-v2.0.")
    profile = validate_profile(raw_profile)
    validate_incentive_axes(axes)
    scenario = validate_scenario(scenario) if scenario is not None else None
    request = {"operation": "incentives", "config": config.raw(), "profile": profile.raw(),
               "mechanism": "rbts", "axes": axes or {}}
    if scenario is not None:
        request["scenario"] = scenario
    out = Path(out)
    manifest = new_run(out, "incentives", config, profile, "rbts", request=request, argv=argv,
                       publication_owner="local_server" if defer_publication else "cli", scenario=scenario)
    try:
        event = incentive_documents()
        pinned = out / "inputs" / "incentives"
        pinned.mkdir()
        freeze = ROOT / INCENTIVE_FREEZE
        for record in event["files"]:
            shutil.copyfile(freeze / record["snapshot"], pinned / record["snapshot"])
        shutil.copyfile(freeze / "manifest.json", pinned / "freeze_event.json")
        manifest["incentive_diagnostics"] = {
            "feature_version": INCENTIVE_VERSION,
            "freeze": INCENTIVE_FREEZE,
            "freeze_created_at_utc": event["created_at_utc"],
            "documents": event["files"],
        }
        study = run_incentive_study(config.raw(), profile.raw(), axes or {}, on_progress)
        diagnostics = study["base_diagnostics"]
        landscapes = {"feature_version": INCENTIVE_VERSION, "axes": study["axes"],
                      "points": [{"point_id": point["point_id"], "status": point["status"],
                                  **({"config_hash": point["config_hash"], "landscape": point["landscape"]}
                                     if point["status"] == "valid" else
                                     {"error_field": point.get("error_field"), "error": point.get("error")})}
                                 for point in study["points"]]}
        write_json(out / "incentive_diagnostics.json", diagnostics)
        write_csv(out / "incentive_diagnostics.csv", _diagnostic_csv_rows(diagnostics))
        write_json(out / "incentive_sweep.json", {key: study[key] for key in ("feature_version", "model_version", "mechanism", "axes", "points", "scope", "claims_mixed_equilibrium_coverage", "claims_equilibrium_selection")})
        write_csv(out / "incentive_sweep.csv", _sweep_csv_rows(study))
        write_json(out / "equilibrium_landscape.json", landscapes)
        valid = [point for point in study["points"] if point["status"] == "valid"]
        summary = {
            "feature_version": INCENTIVE_VERSION,
            "model_version": V2_MODEL_VERSION,
            "mechanism": "rbts",
            "axes": study["axes"],
            "point_count": len(study["points"]),
            "valid_point_count": len(valid),
            "invalid_point_count": len(study["points"]) - len(valid),
            "base_candidate_equilibrium_status": diagnostics["candidate_equilibrium_status"],
            "base_candidate_max_regret": diagnostics["candidate_max_regret"],
            "point_summaries": [
                {"point_id": point["point_id"], "status": point["status"],
                 **({"config_hash": point["config_hash"],
                     "full_equilibrium_count": point["landscape"]["full_equilibrium_count"],
                     "low_effort_exists": point["landscape"]["low_effort_exists"],
                     "all_high_signal_dependent_exists": point["landscape"]["all_high_signal_dependent_exists"],
                     "coexistence_low_and_dependent_high": point["landscape"]["coexistence_low_and_dependent_high"]}
                    if point["status"] == "valid" else {"error": point.get("error")})}
                for point in study["points"]
            ],
            "scope": study["scope"],
        }
        write_json(out / "summary.json", summary)
        (out / "report.md").write_text(
            "# CEAV-M1 V2.2 — Incentive diagnostics\n\n"
            f"Candidate: **{diagnostics['candidate_equilibrium_status']}**; max regret: {diagnostics['candidate_max_regret']}.\n\n"
            f"Sweep points: {len(study['points'])}; valid exhaustive landscapes: {len(valid)}. "
            "Mỗi valid point đã kiểm tra 432 branch candidates.\n\n"
            "Threshold trong incentive_diagnostics là conditional trên peer strategy đã pin; "
            "equilibrium_landscape mới là kết quả exhaustive toàn cục trong phạm vi pure strategies.\n\n"
            "H01/H10 chỉ có nghĩa report phụ thuộc X; không tự chứng minh gần ground truth. "
            "Existence không chứng minh equilibrium selection.\n",
            encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest)
        else:
            write_json(out / "manifest.json", manifest)
        return study
    except BaseException as error:
        if not defer_publication:
            finish_run(out, manifest, "failed", error)
        raise
