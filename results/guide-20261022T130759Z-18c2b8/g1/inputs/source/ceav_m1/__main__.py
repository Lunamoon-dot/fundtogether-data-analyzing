"""Command line entry point, using the same engine as the local JSON API."""

import argparse
import json
from pathlib import Path
import sys
import time

from .equilibria import CancelledError, search_pure
from .evaluate import analyze
from .model import ValidationError, rational, validate_config
from .output import finish_run, new_run, research_context, semantic_hash, write_analysis, write_csv, write_json, write_search
from .strategies import validate_profile


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def compare_config(raw):
    config = validate_config(raw, "rbts")
    validate_config(raw, "fixed")
    if config.fixed_reward != config.f + 2 * config.multiplier:
        raise ValidationError("fixed_reward", "Comparison cần F=f+2*lambda; không tự thay input.")
    return config


def execute(operation, raw_config, raw_profile, mechanism, out, on_progress=None, sweep=None, argv=None, defer_publication=False):
    """Only fixed operation names enter this function; no shell expressions."""
    profile = None if operation == "equilibria" else validate_profile(raw_profile)
    config = compare_config(raw_config) if operation == "compare" else validate_config(raw_config, mechanism)
    out = Path(out)
    request = {"operation": operation, "config": raw_config, "profile": raw_profile, "mechanism": mechanism}
    if sweep is not None:
        request["axes"] = sweep
    manifest = new_run(out, operation, config, profile, mechanism, request=request, argv=argv, publication_owner="local_server" if defer_publication else "cli")
    started = time.perf_counter()
    try:
        if operation == "analyze":
            result = analyze(config, profile, mechanism)
            write_analysis(out, result)
        elif operation == "equilibria":
            result = search_pure(config, mechanism, on_progress)
            write_search(out, result)
        elif operation == "compare":
            results = {name: execute("analyze", raw_config, raw_profile, name, out / name, on_progress, argv=argv) for name in ("fixed", "rbts")}
            result = {"comparison_scope": "fixed_candidate_equal_cap", "equal_cap": True,
                      "reward_cap": 3 * config.fixed_reward, "config_hash": semantic_hash(config), "profile_hash": semantic_hash(profile),
                      "mechanisms": {name: {key: value for key, value in r.items() if key in ("metrics", "reward_cap", "equilibrium_status", "max_regret")} for name, r in results.items()}}
            write_json(out / "summary.json", result)
            (out / "report.md").write_text(f"# CEAV-M1 — Comparison\n\nCùng config/profile và maximum reward {3*config.fixed_reward}. "
                f"Actual spend fixed={results['fixed']['metrics']['expected_reward_total']}, RBTS={results['rbts']['metrics']['expected_reward_total']}.\n\n"
                "Đây là so sánh candidate cố định, không phải toàn bộ equilibria.\n\n" + research_context(config.raw(), profile.raw()), encoding="utf-8", newline="\n")
        elif operation == "sweep":
            from itertools import product
            if not isinstance(sweep, dict) or not sweep or set(sweep) - {"pi", "a", "b", "c", "lambda"}:
                raise ValidationError("axes", "Cần axes pi,a,b,c,lambda được hỗ trợ.")
            axes = [key for key in ("pi", "a", "b", "c", "lambda") if key in sweep]
            for key in axes:
                if not isinstance(sweep[key], list) or not sweep[key]:
                    raise ValidationError(f"axes.{key}", "Cần danh sách chuỗi hữu tỉ không rỗng.")
                for value in sweep[key]:
                    rational(value, f"axes.{key}")
            rows = []
            grid = list(product(*(sweep[key] for key in axes)))
            for index, point in enumerate(grid):
                raw = dict(config.raw())
                row = {"point_id": index, "mechanism": mechanism, "profile_hash": semantic_hash(profile)}
                for key, value in zip(axes, point):
                    row[key] = rational(value, key)
                    raw["costs" if key == "c" else key] = [value] * 3 if key == "c" else value
                row["config_json"] = json.dumps(raw, sort_keys=True)
                try:
                    point_config = validate_config(raw, mechanism)
                    analyzed = analyze(point_config, profile, mechanism)
                    row.update(status="valid", config_hash=semantic_hash(point_config), equilibrium_status=analyzed["equilibrium_status"])
                    row.update({key: value for key, value in analyzed["metrics"].items() if not isinstance(value, list)})
                    for branch in analyzed["best_responses"]:
                        for key in ("delta_utility", "regret"):
                            row[f"{branch['judge']}_z{branch['z']}_{key}"] = branch[key]
                except ValidationError as error:
                    row.update(status="invalid_budget" if error.field == "reward_budget" else "invalid_input", error=str(error))
                rows.append(row)
                if on_progress:
                    on_progress({"phase": "sweep", "completed": index + 1, "total": len(grid)})
            result = {"rows": rows, "axes": sweep, "scope": "fixed_candidate_analysis_only"}
            write_csv(out / "sweep.csv", rows)
            write_json(out / "sweep.json", result)
            (out / "report.md").write_text(f"# CEAV-M1 — Sweep\n\n{len(rows)} điểm trên candidate cố định; không phải bản đồ mọi cân bằng. "
                f"Hàng lỗi được giữ: {sum(r['status'] != 'valid' for r in rows)}.\n\nAxes:\n\n```json\n" + json.dumps(sweep, sort_keys=True, indent=2) + "\n```\n\n" + research_context(config.raw(), profile.raw()), encoding="utf-8", newline="\n")
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
            command.add_argument("--mechanism", choices=("fixed", "rbts"), default="rbts")
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--progress-json", action="store_true", help=argparse.SUPPRESS)
        command.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
        command.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    tests = commands.add_parser("tests")
    tests.add_argument("--suite", choices=("reference", "goldens", "all", "selected"), required=True)
    tests.add_argument("--test-id", action="append", default=[])
    tests.add_argument("--failure-fixture", action="store_true")
    tests.add_argument("--out", type=Path, required=True)
    tests.add_argument("--defer-publication", action="store_true", help=argparse.SUPPRESS)
    tests.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
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
        execute(args.operation, raw_config, raw_profile, getattr(args, "mechanism", "rbts"), args.out, progress, sweep, defer_publication=args.defer_publication)
        print(f"Completed {args.operation}: {args.out.resolve()}")
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
