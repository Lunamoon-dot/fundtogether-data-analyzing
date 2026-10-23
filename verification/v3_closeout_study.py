"""Run the pinned V3 robustness and anchor-only versus hybrid closeout study."""

from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ceav_m1.equilibria import search_pure, summarize_equilibrium_metrics
from ceav_m1.evaluate import analyze
from ceav_m1.incentives import classify_landscape
from ceav_m1.model import validate_config
from ceav_m1.output import finish_run, new_run, write_json
from ceav_m1.strategies import validate_profile


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def exact(value):
    return str(value) if isinstance(value, F) else value


def set_path(raw, path, value):
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = str(value)


def run_point(name, group, raw, cached_search=None):
    config = validate_config(raw, "hybrid_anchor")
    search = cached_search or search_pure(config, "hybrid_anchor")
    landscape = classify_landscape(search)
    metrics = summarize_equilibrium_metrics(config, search, "hybrid_anchor")
    result = {
        "name": name,
        "group": group,
        "config": config.raw(),
        "reward_cap": 3 * config.f + 6 * config.multiplier + 3 * config.anchor_weight,
        "landscape": {key: landscape[key] for key in (
            "full_equilibrium_count", "low_effort_exists", "all_high_signal_dependent_exists",
            "all_high_signal_ignored_exists", "coexistence_low_and_dependent_high",
        )},
        "equilibrium_metrics": metrics,
        "search_reused": cached_search is not None,
    }
    print(f"{group}/{name}: equilibria={landscape['full_equilibrium_count']} metrics={metrics['status']}", flush=True)
    return result, search


def main(out):
    out = Path(out)
    baseline_raw = load("configs/v3/heterogeneous_anchor.json")
    base_raw = load("configs/v3/anchor_dominant_q50.json")
    all_high = validate_profile(load("configs/all_high.json"))
    base_config = validate_config(base_raw, "hybrid_anchor")
    manifest = new_run(out, "v3_closeout_study", base_config, all_high, "hybrid_anchor",
                       request={"study": "robustness_and_anchor_only_vs_hybrid", "arithmetic": "exact"})
    try:
        points = []
        baseline, _ = run_point("v3_r1_baseline", "comparison", baseline_raw)
        points.append(baseline)
        base, base_search = run_point("anchor_dominant_q50", "comparison", base_raw)
        points.append(base)

        for q in (F(2, 5), F(11, 25), F(3, 5)):
            raw = deepcopy(base_raw)
            set_path(raw, "verification_anchor.audit_probability", q)
            point, _ = run_point(f"q_{q}", "audit_probability", raw)
            points.append(point)

        for quality in (F(4, 5), F(19, 20)):
            raw = deepcopy(base_raw)
            set_path(raw, "verification_anchor.sensitivity", quality)
            set_path(raw, "verification_anchor.specificity", quality)
            point, _ = run_point(f"anchor_quality_{quality}", "anchor_quality", raw)
            points.append(point)

        for multiplier in (F(4, 5), F(6, 5)):
            raw = deepcopy(base_raw)
            for judge in "ABC":
                raw["judges"][judge]["high_effort_cost"] = str(F(raw["judges"][judge]["high_effort_cost"]) * multiplier)
            point, _ = run_point(f"judge_costs_x_{multiplier}", "judge_costs", raw)
            points.append(point)

        for prior in (F(3, 10), F(7, 10)):
            raw = deepcopy(base_raw)
            raw["pi"] = str(prior)
            point, _ = run_point(f"prior_{prior}", "prior", raw)
            points.append(point)

        for peer_weight in (F(1, 100), F(1, 20), F(1, 10)):
            raw = deepcopy(base_raw)
            raw["lambda_peer"] = str(peer_weight)
            raw["anchor_weight"] = str(F(19, 10) - 2 * peer_weight)
            point, _ = run_point(f"lambda_{peer_weight}", "peer_allocation", raw)
            points.append(point)

        for audit_cost in (F(1, 10), F(1, 5), F(1, 2)):
            raw = deepcopy(base_raw)
            set_path(raw, "verification_anchor.cost_per_audit", audit_cost)
            point, _ = run_point(f"audit_cost_{audit_cost}", "audit_cost", raw, base_search)
            points.append(point)

        baseline_metrics = baseline["equilibrium_metrics"]["best_accuracy"]["metrics"]
        improved_metrics = base["equilibrium_metrics"]["best_accuracy"]["metrics"]
        forced = analyze(validate_config(baseline_raw, "hybrid_anchor"), all_high, "hybrid_anchor")["metrics"]
        comparison = {
            "baseline_equilibrium": baseline_metrics,
            "forced_all_high_candidate": {key: forced[key] for key in ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value")},
            "experimental_equilibrium": improved_metrics,
            "accuracy_gain_vs_baseline_equilibrium": improved_metrics["accuracy"] - baseline_metrics["accuracy"],
            "accuracy_gain_vs_forced_all_high_candidate": improved_metrics["accuracy"] - forced["accuracy"],
            "false_approval_change_vs_baseline": improved_metrics["false_approval_rate"] - baseline_metrics["false_approval_rate"],
            "false_rejection_change_vs_baseline": improved_metrics["false_rejection_rate"] - baseline_metrics["false_rejection_rate"],
        }
        robust = [point for point in points if point["group"] not in ("comparison", "audit_cost")]
        robustness = {
            "points": len(robust),
            "with_pure_equilibrium": sum(point["equilibrium_metrics"]["status"] == "pure_equilibria_evaluated" for point in robust),
            "unique_pure_equilibrium": sum(point["landscape"]["full_equilibrium_count"] == 1 for point in robust),
            "without_all_low_equilibrium": sum(not point["landscape"]["low_effort_exists"] for point in robust),
        }
        result = {"study": "v3_closeout_r2", "comparison": comparison, "robustness": robustness, "points": points,
                  "limitations": ["synthetic parameters", "pure strategies only", "one-factor-at-a-time robustness", "no production auditor provenance"]}
        write_json(out / "study.json", result)

        def pct(value):
            return f"{float(value) * 100:.2f}%"

        lines = [
            "# CEAV-M1 V3 — Closeout study",
            "",
            "## Accuracy improvement",
            "",
            f"- Baseline equilibrium accuracy: `{exact(baseline_metrics['accuracy'])}` ({pct(baseline_metrics['accuracy'])}).",
            f"- Experimental equilibrium accuracy: `{exact(improved_metrics['accuracy'])}` ({pct(improved_metrics['accuracy'])}).",
            f"- Gain: `{exact(comparison['accuracy_gain_vs_baseline_equilibrium'])}` ({pct(comparison['accuracy_gain_vs_baseline_equilibrium'])} points).",
            f"- Gain versus forced all-High candidate: `{exact(comparison['accuracy_gain_vs_forced_all_high_candidate'])}` ({pct(comparison['accuracy_gain_vs_forced_all_high_candidate'])} points).",
            "",
            "## Robustness points",
            "",
            "| Group | Point | Pure eq | All-Low exists | Accuracy range |",
            "| --- | --- | ---: | --- | --- |",
        ]
        for point in points:
            summary = point["equilibrium_metrics"]
            accuracy = "—" if summary["status"] != "pure_equilibria_evaluated" else f"{exact(summary['ranges']['accuracy']['min'])} .. {exact(summary['ranges']['accuracy']['max'])}"
            lines.append(f"| {point['group']} | {point['name']} | {point['landscape']['full_equilibrium_count']} | {point['landscape']['low_effort_exists']} | {accuracy} |")
        lines += ["", "Synthetic evidence only; no production auditor, mixed-equilibrium, collusion or Sybil claim.", ""]
        (out / "report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        finish_run(out, manifest)
        return 0
    except BaseException as error:
        finish_run(out, manifest, "failed", error)
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().out))
