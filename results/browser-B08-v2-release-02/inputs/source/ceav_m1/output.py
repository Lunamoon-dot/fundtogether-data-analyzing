"""Exact serialization and immutable, pinned run inputs/source/documents."""

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from fractions import Fraction
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys

from . import ENGINE_VERSION, V1_MODEL_VERSION, V2_MODEL_VERSION

ROOT = Path(__file__).resolve().parents[1]
FREEZE = "spec_history/implementation-start-20261022T081942148684Z"
V2_FREEZE = "spec_history/v2-implementation-start-20261022T161522230020Z"
FREEZES = {V1_MODEL_VERSION: FREEZE, V2_MODEL_VERSION: V2_FREEZE}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def exact_payload(value):
    if isinstance(value, Fraction):
        try:
            decimal = float(value)
        except OverflowError:
            decimal = None
        if decimal is not None and not math.isfinite(decimal):
            decimal = None
        result = {"exact": str(value), "decimal": decimal}
        if decimal is None:
            result["decimal_reason"] = "outside_finite_display_range"
        return result
    if is_dataclass(value):
        return exact_payload(asdict(value))
    if isinstance(value, dict):
        return {str(k): exact_payload(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [exact_payload(v) for v in value]
    return value


def restore_exact(value):
    if isinstance(value, dict):
        if {"exact", "decimal"} <= set(value) <= {"exact", "decimal", "decimal_reason"}:
            return Fraction(value["exact"])
        return {key: restore_exact(v) for key, v in value.items()}
    if isinstance(value, list):
        return [restore_exact(v) for v in value]
    return value


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if hasattr(value, "raw"):
        return canonicalize(value.raw())
    if isinstance(value, dict):
        return {str(k): canonicalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonicalize(v) for v in value]
    return value


def semantic_hash(value):
    return sha256(json.dumps(canonicalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(exact_payload(value), ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def documents(root=ROOT, model_version=V1_MODEL_VERSION):
    if model_version not in FREEZES:
        raise ValueError("Unsupported model version for document freeze")
    freeze = FREEZES[model_version]
    folder = root / freeze
    event = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if event["event"] != "analyzer_implementation_start" or event["freeze_status"] != "frozen_at_analyzer_implementation_start":
        raise ValueError("Missing implementation-start freeze event")
    if event.get("model_version", V1_MODEL_VERSION) != model_version:
        raise ValueError("Freeze event model version mismatch")
    if not event["reference_checker_preexisted"] or event["analyzer_existed_before_event"]:
        raise ValueError("Invalid implementation-start provenance")
    for filename, record in event["files"].items():
        if sha256((folder / filename).read_bytes()) != record["sha256"]:
            raise ValueError(f"Pinned document checksum mismatch: {filename}")
    if model_version == V1_MODEL_VERSION:
        parent = root / "spec_history" / event["parent_revision"]
        review = json.loads((parent / "manifest.json").read_text(encoding="utf-8"))
        if sha256((parent / review["file"]).read_bytes()) != event["parent_sha256"] or review["sha256"] != event["parent_sha256"]:
            raise ValueError("Snapshot parent checksum mismatch")
        seen = set()
        while review.get("parent_revision"):
            revision = review["parent_revision"]
            if revision in seen:
                raise ValueError("Cycle in snapshot revision chain")
            seen.add(revision)
            previous_folder = root / "spec_history" / revision
            previous = json.loads((previous_folder / "manifest.json").read_text(encoding="utf-8"))
            if previous["sha256"] != review["parent_sha256"] or sha256((previous_folder / previous["file"]).read_bytes()) != previous["sha256"]:
                raise ValueError("Historical snapshot chain checksum mismatch")
            review = previous
    elif not event.get("v2_oracle_preexisted") or event.get("v2_production_support_existed_before_event"):
        raise ValueError("Invalid V2 implementation-start provenance")
    return event


def source_files(root=ROOT):
    paths = []
    for directory in ("ceav_m1", "web", "tests", "verification", "configs", "scenarios"):
        folder = root / directory
        if folder.exists():
            paths.extend(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".py", ".json", ".html", ".css", ".js"))
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def new_run(out, operation, config=None, profile=None, mechanism=None, request=None, argv=None, publication_owner="cli", scenario=None, model_version=None):
    model_version = config.model_version if config is not None else (model_version or V1_MODEL_VERSION)
    freeze = FREEZES[model_version]
    event = documents(model_version=model_version)
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs = out / "inputs"
    inputs.mkdir()
    for filename in event["files"]:
        shutil.copyfile(ROOT / freeze / filename, inputs / filename)
    shutil.copyfile(ROOT / freeze / "manifest.json", inputs / "freeze_event.json")
    sources = []
    for path in source_files():
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        destination = inputs / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        sources.append({"path": relative.as_posix(), "sha256": sha256(raw)})
    manifest = {"run_id": out.name, "operation": operation, "mechanism": mechanism, "status": "running",
                "model_version": model_version, "engine_version": ENGINE_VERSION,
                "engine_revision": semantic_hash(sources), "source_files": sources,
                "python": sys.version, "platform": platform.platform(), "machine": platform.machine(), "logical_cpu_count": os.cpu_count(),
                "publication_owner": publication_owner,
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "argv": list(argv or sys.argv),
                "randomness": "none", "spec": {"revision": event["spec_revision"],
                "snapshot": freeze + "/" + ("CEAV_M1_SPEC.md" if model_version == V1_MODEL_VERSION else "CEAV_M1_V2_SPEC.md"),
                "sha256": event["files"]["CEAV_M1_SPEC.md" if model_version == V1_MODEL_VERSION else "CEAV_M1_V2_SPEC.md"]["sha256"],
                "freeze_event": freeze + "/manifest.json",
                "freeze_status": event["freeze_status"], "reference_checker_preexisted": True},
                "documents": event["files"], "artifacts": []}
    if config is not None:
        manifest.update(config=canonicalize(config), config_hash=semantic_hash(config))
        write_json(out / "config.json", canonicalize(config))
    if profile is not None:
        manifest.update(profile=canonicalize(profile), profile_hash=semantic_hash(profile))
        write_json(out / "profile.json", canonicalize(profile))
    if request is not None:
        write_json(out / "request.json", request)
        manifest["request_hash"] = semantic_hash(request)
    if scenario is not None:
        manifest.update(scenario=canonicalize(scenario), scenario_hash=semantic_hash(scenario))
        write_json(out / "scenario.json", canonicalize(scenario))
    write_json(out / "manifest.json", manifest)
    return manifest


def write_csv(path, records):
    columns = []
    for row in records:
        for key, value in row.items():
            for column in (key + "_exact", key + "_decimal") if isinstance(value, Fraction) else (key,):
                if column not in columns:
                    columns.append(column)
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in records:
            flattened = {}
            for key, value in row.items():
                if isinstance(value, Fraction):
                    flattened[key + "_exact"] = str(value)
                    flattened[key + "_decimal"] = exact_payload(value)["decimal"]
                else:
                    flattened[key] = value
            writer.writerow(flattened)


def finish_run(out, manifest, status="succeeded", error=None):
    out = Path(out)
    if manifest["status"] in ("succeeded", "failed", "cancelled", "interrupted"):
        raise ValueError("Terminal run state is immutable")
    manifest["status"] = status
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    if error is not None:
        manifest["error"] = str(error)
    report = out / "report.md"
    if not report.exists():
        context = research_context(manifest["config"], manifest.get("profile")) if manifest.get("config") else ""
        report.write_text(f"# CEAV-M1 — {manifest['operation']}\n\nStatus: {status}.\n\n{manifest.get('error', 'Không có kết quả khoa học hoàn chỉnh.')}\n\n" + context, encoding="utf-8", newline="\n")
    if status != "succeeded":
        original = report.read_text(encoding="utf-8")
        report.write_text(f"> Trạng thái run: {status}. Không dùng run này làm certificate hoàn chỉnh.\n\n" + original, encoding="utf-8", newline="\n")
    paths = [path for path in out.iterdir() if path.is_file() and path.name not in ("manifest.json", "manifest.json.tmp")]
    if manifest["operation"] == "compare":
        for name in ("fixed", "rbts"):
            if (out / name).is_dir():
                paths.extend(path for path in (out / name).iterdir() if path.is_file() and not path.name.endswith(".tmp"))
    manifest["artifacts"] = [{"name": path.relative_to(out).as_posix(), "sha256": sha256(path.read_bytes()), "bytes": path.stat().st_size}
                             for path in sorted(paths)]
    write_json(out / "manifest.json", manifest)


LIMITATIONS = "M1: một claim, ba Judge; effort sau public Z; không stake/slashing, không ground-truth reward; chỉ cân bằng thuần, không chứng nhận mixed/coalition hoặc equilibrium selection. Đơn vị nghiên cứu chuẩn hóa, không phải tiền thực. Cân bằng không effort như all-Z có thể cùng tồn tại với high-effort; tăng lambda không tự loại bỏ cân bằng đạt score maximum."


def research_context(config, profile=None, scenario=None):
    version = config.get("model_version", V1_MODEL_VERSION)
    domain = ("0 < pi,a,b < 1; costs, f, lambda, F, B, V, operating_cost >= 0."
              if version == V1_MODEL_VERSION else
              "0 < pi,sensitivity,specificity < 1; cost, f, lambda, F, B, V, operating_cost >= 0.")
    text = f"Model: {version}. Miền tham số: {domain}\n\nCấu hình thực tế của run:\n\n```json\n" + json.dumps(config, ensure_ascii=False, sort_keys=True, indent=2) + "\n```\n\n"
    if profile is not None:
        text += "Candidate effort/report profile:\n\n```json\n" + json.dumps(profile, sort_keys=True, indent=2) + "\n```\n\n"
    if scenario is None:
        text += "Scenario: not_provided.\n\n"
    else:
        text += "Scenario metadata (không tham gia phép tính):\n\n```json\n" + json.dumps(scenario, ensure_ascii=False, sort_keys=True, indent=2) + "\n```\n\n"
    return text + LIMITATIONS + "\n"


def write_analysis(out, result):
    out = Path(out)
    summary = {key: value for key, value in result.items() if key not in ("states", "best_responses", "conditional")}
    write_json(out / "summary.json", summary)
    write_json(out / "best_responses.json", result["best_responses"])
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    identity = {key: manifest[key] for key in ("model_version", "engine_revision", "spec", "documents", "config_hash", "profile_hash", "mechanism")}
    if "scenario_hash" in manifest:
        identity["scenario_hash"] = manifest["scenario_hash"]
    identity["candidate_hash"] = semantic_hash({"config": result["config"], "profile": result["profile"], "predictions": result["predictions"], "mechanism": result["mechanism"]})
    write_json(out / "certificate.json", {"identity": identity, "requires_manifest_status": "succeeded", "analysis": summary | {"best_responses": result["best_responses"]}})
    write_csv(out / "states.csv", result["states"])
    metrics = result["metrics"]
    text = (f"# CEAV-M1 — Phân tích {result['mechanism']}\n\n"
            f"Trạng thái candidate: **{result['equilibrium_status']}**. Max regret: {result['max_regret']}.\n\n"
            f"Accuracy: {metrics['accuracy']}; false approval P(D=1|Y=0): {metrics['false_approval_rate']}; "
            f"giải ngân sai kỳ vọng: {metrics['wrong_payout_value']}.\n\n"
            f"Thực chi reward: {metrics['expected_reward_total']}; maximum reward: {result['reward_cap']}; budget: {result['reward_budget']}.\n\n"
            "Candidate payoff sử dụng candidate thật; best response và witness nằm trong best_responses.json. "
            "Witness giữ prediction của peer tại run gốc; dựng lại Bayesian predictions của một profile mới có thể thay đổi payoff.\n\n"
            "Signal diagnostics nằm trong summary.json; đây là mô tả chất lượng tín hiệu theo prior, không phải decision accuracy hay utility.\n\n"
            + research_context(result["config"], result["profile"], manifest.get("scenario")))
    (out / "report.md").write_text(text, encoding="utf-8", newline="\n")


def write_search(out, result):
    out = Path(out)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    identity = {key: manifest[key] for key in ("model_version", "engine_revision", "spec", "documents", "config_hash", "mechanism")}
    if "scenario_hash" in manifest:
        identity["scenario_hash"] = manifest["scenario_hash"]
    write_json(out / "equilibria.json", result | {"identity": identity, "requires_manifest_status": "succeeded"})
    summary = {key: value for key, value in result.items() if key != "branches"}
    summary["branch_equilibrium_counts"] = {z: b["equilibrium_count"] for z, b in result["branches"].items()}
    write_json(out / "summary.json", summary)
    (out / "report.md").write_text(
        f"# CEAV-M1 — Tìm cân bằng thuần\n\nĐã kiểm tra {result['branch_candidate_count']} candidates; "
        f"số cân bằng theo Z: {summary['branch_equilibrium_counts']}; tổ hợp đầy đủ: {result['full_equilibrium_count']}.\n\n"
        + result["combination_rule"] + "\n\n" + research_context(result["config"], scenario=manifest.get("scenario")), encoding="utf-8", newline="\n")
