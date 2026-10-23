"""Command line entry point, using the same engine as the local JSON API."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import time

from .calibration import PROVENANCE_STATUSES, write_calibration_run
from .equilibria import CancelledError, search_pure, summarize_equilibrium_metrics
from .evaluate import analyze
from .incentives import classify_landscape, validate_incentive_axes, write_incentive_run
from .ipw import load_ipw_study, write_ipw_run
from .model import ValidationError, rational, validate_config, validate_scenario
from .output import finish_run, new_run, research_context, semantic_hash, write_analysis, write_csv, write_json, write_search
from .report_sensitive import load_report_sensitive_study, write_report_sensitive_run
from .robustness import load_robustness_study, write_robustness_run
from .strategies import validate_profile


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def compare_config(raw):
    config = validate_config(raw, "rbts")
    validate_config(raw, "fixed")
    if config.fixed_reward != config.f + 2 * config.multiplier:
        raise ValidationError("fixed_reward", "Comparison cần F=f+2*lambda; không tự thay input.")
    return config


V1_SWEEP_AXES = ("pi", "a", "b", "c", "lambda")
V2_SWEEP_AXES = (
    "pi", "public_signal.sensitivity", "public_signal.specificity",
    "judges.A.private_signal.sensitivity", "judges.A.private_signal.specificity", "judges.A.high_effort_cost",
    "judges.B.private_signal.sensitivity", "judges.B.private_signal.specificity", "judges.B.high_effort_cost",
    "judges.C.private_signal.sensitivity", "judges.C.private_signal.specificity", "judges.C.high_effort_cost", "lambda",
)
V3_SWEEP_AXES = (
    "pi", "public_signal.sensitivity", "public_signal.specificity",
    "judges.A.private_signal.sensitivity", "judges.A.private_signal.specificity", "judges.A.high_effort_cost",
    "judges.B.private_signal.sensitivity", "judges.B.private_signal.specificity", "judges.B.high_effort_cost",
    "judges.C.private_signal.sensitivity", "judges.C.private_signal.specificity", "judges.C.high_effort_cost",
    "verification_anchor.audit_probability", "verification_anchor.sensitivity", "verification_anchor.specificity",
    "verification_anchor.cost_per_audit",
    "lambda_peer", "anchor_weight",
)


def validate_sweep_axes(sweep, model_version):
    allowed = (V1_SWEEP_AXES if model_version == "ceav-m1-v1.0" else
               V2_SWEEP_AXES if model_version == "ceav-m1-v2.0" else V3_SWEEP_AXES)
    if not isinstance(sweep, dict) or not sweep or set(sweep) - set(allowed):
        raise ValidationError("axes", "Sweep chứa axis không được hỗ trợ cho model version này.")
    axes = [key for key in allowed if key in sweep]
    for key in axes:
        if not isinstance(sweep[key], list) or not sweep[key]:
            raise ValidationError(f"axes.{key}", "Cần danh sách chuỗi hữu tỉ không rỗng.")
        for value in sweep[key]:
            rational(value, f"axes.{key}")
    return axes


def set_axis(raw, path, value):
    if path == "c":
        raw["costs"] = [value] * 3
        return
    target = raw
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def execute(operation, raw_config, raw_profile, mechanism, out, on_progress=None, sweep=None, argv=None, defer_publication=False, scenario=None):
    """Only fixed operation names enter this function; no shell expressions."""
    profile = None if operation == "equilibria" else validate_profile(raw_profile)
    config = compare_config(raw_config) if operation == "compare" else validate_config(raw_config, mechanism)
    scenario = validate_scenario(scenario) if scenario is not None else None
    out = Path(out)
    request = {"operation": operation, "config": raw_config, "profile": raw_profile, "mechanism": mechanism}
    if sweep is not None:
        request["axes"] = sweep
    if scenario is not None:
        request["scenario"] = scenario
    manifest = new_run(out, operation, config, profile, mechanism, request=request, argv=argv, publication_owner="local_server" if defer_publication else "cli", scenario=scenario)
    started = time.perf_counter()
    try:
        if operation == "analyze":
            result = analyze(config, profile, mechanism)
            write_analysis(out, result)
        elif operation == "equilibria":
            result = search_pure(config, mechanism, on_progress)
            write_search(out, result)
        elif operation == "compare":
            results = {name: execute("analyze", raw_config, raw_profile, name, out / name, on_progress, argv=argv, scenario=scenario) for name in ("fixed", "rbts")}
            result = {"comparison_scope": "fixed_candidate_equal_cap", "equal_cap": True,
                      "reward_cap": 3 * config.fixed_reward, "config_hash": semantic_hash(config), "profile_hash": semantic_hash(profile),
                      "mechanisms": {name: {key: value for key, value in r.items() if key in ("metrics", "reward_cap", "equilibrium_status", "max_regret")} for name, r in results.items()}}
            write_json(out / "summary.json", result)
            (out / "report.md").write_text(f"# CEAV-M1 — Comparison\n\nCùng config/profile và maximum reward {3*config.fixed_reward}. "
                f"Actual spend fixed={results['fixed']['metrics']['expected_reward_total']}, RBTS={results['rbts']['metrics']['expected_reward_total']}.\n\n"
                "Đây là so sánh candidate cố định, không phải toàn bộ equilibria.\n\n" + research_context(config.raw(), profile.raw(), scenario), encoding="utf-8", newline="\n")
        elif operation == "sweep":
            from itertools import product
            axes = validate_sweep_axes(sweep, config.model_version)
            exhaustive_landscape = config.model_version == "ceav-m1-v3.0"
            rows = []
            grid = list(product(*(sweep[key] for key in axes)))
            for index, point in enumerate(grid):
                raw = deepcopy(config.raw())
                row = {"point_id": index, "mechanism": mechanism, "profile_hash": semantic_hash(profile)}
                for key, value in zip(axes, point):
                    row[key] = rational(value, key)
                    set_axis(raw, key, value)
                row["config_json"] = json.dumps(raw, sort_keys=True)
                try:
                    point_config = validate_config(raw, mechanism)
                    analyzed = analyze(point_config, profile, mechanism)
                    row.update(status="valid", config_hash=semantic_hash(point_config), equilibrium_status=analyzed["equilibrium_status"])
                    row.update({key: value for key, value in analyzed["metrics"].items() if not isinstance(value, list)})
                    for branch in analyzed["best_responses"]:
                        for key in ("delta_utility", "regret"):
                            row[f"{branch['judge']}_z{branch['z']}_{key}"] = branch[key]
                    if exhaustive_landscape:
                        def search_progress(progress):
                            if on_progress:
                                on_progress({**progress, "point": index + 1, "points_total": len(grid)})
                        search = search_pure(point_config, mechanism, search_progress)
                        landscape = classify_landscape(search)
                        landscape["equilibrium_metrics"] = summarize_equilibrium_metrics(point_config, search, mechanism)
                        row["landscape"] = landscape
                        for key in ("branch_candidate_count", "full_equilibrium_count", "low_effort_exists",
                                    "all_high_signal_dependent_exists", "all_high_signal_ignored_exists",
                                    "coexistence_low_and_dependent_high"):
                            row[key] = landscape[key]
                        equilibrium_metrics = landscape["equilibrium_metrics"]
                        row["equilibrium_metrics_status"] = equilibrium_metrics["status"]
                        if equilibrium_metrics["status"] == "pure_equilibria_evaluated":
                            for metric, values in equilibrium_metrics["ranges"].items():
                                row[f"equilibrium_{metric}_min"] = values["min"]
                                row[f"equilibrium_{metric}_max"] = values["max"]
                except ValidationError as error:
                    row.update(status="invalid_budget" if error.field == "reward_budget" else "invalid_input", error=str(error))
                rows.append(row)
                if on_progress:
                    on_progress({"phase": "sweep", "completed": index + 1, "total": len(grid)})
            scope = ("candidate_analysis_plus_exhaustive_pure_equilibrium_landscape" if exhaustive_landscape
                     else "fixed_candidate_analysis_only")
            result = {"rows": rows, "axes": sweep, "scope": scope}
            write_csv(out / "sweep.csv", [{key: value for key, value in row.items() if key != "landscape"} for row in rows])
            write_json(out / "sweep.json", result)
            scope_text = ("Mỗi điểm V3 hợp lệ gồm candidate diagnostics và exhaustive pure-equilibrium landscape."
                          if exhaustive_landscape else "Các điểm chỉ phân tích candidate cố định; không phải bản đồ mọi cân bằng.")
            (out / "report.md").write_text(f"# CEAV-M1 — Sweep\n\n{len(rows)} điểm. {scope_text} "
                f"Hàng lỗi được giữ: {sum(r['status'] != 'valid' for r in rows)}.\n\nAxes:\n\n```json\n" + json.dumps(sweep, sort_keys=True, indent=2) + "\n```\n\n" + research_context(config.raw(), profile.raw(), scenario), encoding="utf-8", newline="\n")
        else:
            raise ValueError("Unknown operation")
        manifest["duration_seconds"] = time.perf_counter() - started
        if not defer_publication:
            finish_run(out, manifest)
        else:
            write_json(out / "manifest.json", manifest)
        return result
    except BaseException as error:
        import traceback
        (out / "error_log.txt").write_text(traceback.format_exc(), encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest, "cancelled" if isinstance(error, (CancelledError, KeyboardInterrupt)) else "failed", error)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="CEAV-M1 exact research laboratory")
    commands = parser.add_subparsers(dest="operation", required=True)
    for name in ("analyze", "equilibria", "sweep", "compare"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        if name != "equilibria":
            command.add_argument("--profile", type=Path, required=True)
        if name != "compare":
            command.add_argument("--mechanism", choices=("fixed", "rbts", "hybrid_anchor"), default="rbts")
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--scenario", type=Path)
        command.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
        command.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
        command.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    tests = commands.add_parser("tests")
    tests.add_argument("--suite", choices=("reference", "goldens", "v2", "calibration", "incentives", "v3", "robustness", "v3_2", "v3_3", "all", "selected"), required=True)
    tests.add_argument("--test-id", action="append", default=[])
    tests.add_argument("--failure-fixture", action="store_true")
    tests.add_argument("--out", type=Path, required=True)
    tests.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    tests.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    calibrate = commands.add_parser("calibrate")
    calibrate.add_argument("--dataset", type=Path, required=True)
    calibrate.add_argument("--source-name")
    calibrate.add_argument("--base-config", type=Path, required=True)
    calibrate.add_argument("--mechanism", choices=("fixed", "rbts"), default="rbts")
    calibrate.add_argument("--provenance-status", choices=PROVENANCE_STATUSES, required=True)
    calibrate.add_argument("--out", type=Path, required=True)
    calibrate.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    calibrate.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    incentives = commands.add_parser("incentives")
    incentives.add_argument("--config", type=Path, required=True)
    incentives.add_argument("--profile", type=Path, required=True)
    incentives.add_argument("--mechanism", choices=("rbts",), default="rbts")
    incentives.add_argument("--axes", type=Path)
    incentives.add_argument("--out", type=Path, required=True)
    incentives.add_argument("--scenario", type=Path)
    incentives.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
    incentives.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    incentives.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    robustness = commands.add_parser("robustness")
    robustness.add_argument("--study", type=Path, required=True)
    robustness.add_argument("--out", type=Path, required=True)
    robustness.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
    robustness.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    robustness.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    report_sensitive = commands.add_parser("report-sensitive", aliases=("report_sensitive",))
    report_sensitive.add_argument("--study", type=Path, required=True)
    report_sensitive.add_argument("--out", type=Path, required=True)
    report_sensitive.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
    report_sensitive.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    report_sensitive.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    ipw = commands.add_parser("ipw")
    ipw.add_argument("--study", type=Path, required=True)
    ipw.add_argument("--out", type=Path, required=True)
    ipw.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
    ipw.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    ipw.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if getattr(args, "parent_pid", None):
        from .runtime import watch_parent
        watch_parent(args.parent_pid, args.out)
    try:
        if args.operation == "serve":
            from .server import serve_local
            serve_local(args.port)
            return 0
        if args.operation == "tests":
            from .test_runner import write_test_run
            result = write_test_run(args.out, args.suite, args.test_id, args.failure_fixture, defer_publication=args.defer_publication)
            print(json.dumps(result["counts"]))
            return 0 if result["status"] == "passed" else 1
        if args.operation == "calibrate":
            write_calibration_run(args.dataset.read_bytes(), read_json(args.base_config), args.mechanism,
                                  args.provenance_status, args.out, args.source_name or args.dataset.name,
                                  defer_publication=args.defer_publication)
            print(f"Completed calibrate: {args.out.resolve()}")
            return 0
        if args.operation == "incentives":
            axes = read_json(args.axes) if args.axes else {}
            validate_incentive_axes(axes)
            def incentive_progress(value):
                if args.progress_json:
                    print(json.dumps({"progress": value}), flush=True)
            write_incentive_run(read_json(args.config), read_json(args.profile), args.out, axes,
                                read_json(args.scenario) if args.scenario else None,
                                defer_publication=args.defer_publication, on_progress=incentive_progress)
            print(f"Completed incentives: {args.out.resolve()}")
            return 0
        if args.operation == "robustness":
            def robustness_progress(value):
                if args.progress_json:
                    print(json.dumps({"progress": value}), flush=True)
            write_robustness_run(load_robustness_study(args.study), args.out,
                                 defer_publication=args.defer_publication, on_progress=robustness_progress)
            print(f"Completed robustness: {args.out.resolve()}")
            return 0
        if args.operation in ("report-sensitive", "report_sensitive"):
            def report_sensitive_progress(value):
                if args.progress_json:
                    print(json.dumps({"progress": value}), flush=True)
            write_report_sensitive_run(load_report_sensitive_study(args.study), args.out,
                                       defer_publication=args.defer_publication, on_progress=report_sensitive_progress)
            print(f"Completed report-sensitive: {args.out.resolve()}")
            return 0
        if args.operation == "ipw":
            def ipw_progress(value):
                if args.progress_json:
                    print(json.dumps({"progress": value}), flush=True)
            write_ipw_run(load_ipw_study(args.study), args.out,
                          defer_publication=args.defer_publication, on_progress=ipw_progress)
            print(f"Completed ipw: {args.out.resolve()}")
            return 0
        raw_config = read_json(args.config)
        raw_profile = read_json(args.profile) if args.operation != "equilibria" else None
        sweep = None
        if args.operation == "sweep":
            if set(raw_config) != {"base_config", "axes"}:
                raise ValidationError("sweep", "Cần đúng base_config và axes.")
            sweep = raw_config["axes"]
            base = args.config.resolve().parent / raw_config["base_config"]
            raw_config = read_json(base)
        def progress(value):
            if args.progress_json:
                print(json.dumps({"progress": value}), flush=True)
        scenario = read_json(args.scenario) if args.scenario else None
        execute(args.operation, raw_config, raw_profile, getattr(args, "mechanism", "rbts"), args.out, progress, sweep, defer_publication=args.defer_publication, scenario=scenario)
        print(f"Completed {args.operation}: {args.out.resolve()}")
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
