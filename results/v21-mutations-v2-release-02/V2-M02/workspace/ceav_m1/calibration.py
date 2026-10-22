"""Exact calibration of V2 signal parameters from a strict labeled CSV."""

from copy import deepcopy
import csv
from dataclasses import dataclass
from fractions import Fraction
from io import StringIO
import json
from pathlib import Path
import shutil

from . import V2_MODEL_VERSION
from .model import JUDGES, ValidationError, rational, validate_config
from .output import ROOT, finish_run, new_run, semantic_hash, sha256, write_json


CALIBRATION_VERSION = "ceav-m1-v2.1-calibration"
DATASET_VERSION = "ceav-calibration-v1"
CALIBRATION_FREEZE = "spec_history/v2.1-calibration-implementation-start-20261022T173242126063Z"
PROVENANCE_STATUSES = ("synthetic", "assumption", "pilot_estimate", "historical_estimate")
REQUIRED_COLUMNS = (
    "case_id", "ground_truth_Y", "public_signal_Z",
    "private_signal_A", "private_signal_B", "private_signal_C",
    "cost_A", "cost_B", "cost_C",
)


class CalibrationError(ValidationError):
    def __init__(self, field, message, row=None):
        self.row = row
        super().__init__(field, message)

    def as_dict(self):
        result = super().as_dict()
        if self.row is not None:
            result["row"] = self.row
        return result


@dataclass(frozen=True, slots=True)
class CalibrationRow:
    case_id: str
    y: int
    z: int
    private_signals: tuple[int, int, int]
    costs: tuple[Fraction, Fraction, Fraction]

    def canonical(self):
        return {
            "case_id": self.case_id,
            "ground_truth_Y": self.y,
            "public_signal_Z": self.z,
            **{f"private_signal_{judge}": self.private_signals[index] for index, judge in enumerate(JUDGES)},
            **{f"cost_{judge}": str(self.costs[index]) for index, judge in enumerate(JUDGES)},
        }


def _binary(value, field, row):
    if value not in ("0", "1"):
        raise CalibrationError(field, "Chỉ nhận 0 hoặc 1.", row)
    return int(value)


def parse_dataset(raw_bytes):
    if not isinstance(raw_bytes, bytes) or not raw_bytes:
        raise CalibrationError("dataset_csv", "Cần file CSV UTF-8 không rỗng.")
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CalibrationError("dataset_csv", "File phải dùng UTF-8 hoặc UTF-8 BOM.") from None
    try:
        reader = csv.DictReader(StringIO(text, newline=""), strict=True)
        header = reader.fieldnames
        if header is None or len(header) != len(set(header)) or tuple(header) != REQUIRED_COLUMNS:
            raise CalibrationError("columns", "Header phải có đúng chín cột theo ceav-calibration-v1 và đúng thứ tự.")
        rows, seen = [], set()
        for number, raw in enumerate(reader, start=2):
            if None in raw or any(value is None for value in raw.values()):
                raise CalibrationError("columns", "Số ô không khớp header.", number)
            values = {key: value.strip() for key, value in raw.items()}
            case_id = values["case_id"]
            if not case_id or case_id in seen:
                raise CalibrationError("case_id", "Phải không rỗng và duy nhất.", number)
            seen.add(case_id)
            y = _binary(values["ground_truth_Y"], "ground_truth_Y", number)
            z = _binary(values["public_signal_Z"], "public_signal_Z", number)
            signals = tuple(_binary(values[f"private_signal_{judge}"], f"private_signal_{judge}", number) for judge in JUDGES)
            costs = []
            for judge in JUDGES:
                field = f"cost_{judge}"
                try:
                    cost = rational(values[field], field)
                except ValidationError as error:
                    raise CalibrationError(field, error.message, number) from None
                if cost < 0:
                    raise CalibrationError(field, "Không được âm.", number)
                costs.append(cost)
            rows.append(CalibrationRow(case_id, y, z, signals, tuple(costs)))
    except csv.Error as error:
        raise CalibrationError("dataset_csv", f"CSV không hợp lệ: {error}.") from None
    if not rows:
        raise CalibrationError("dataset_csv", "Cần ít nhất một data row.")
    classes = {row.y for row in rows}
    if classes != {0, 1}:
        raise CalibrationError("ground_truth_Y", "Dataset phải có cả Y=0 và Y=1.")
    return tuple(rows)


def _rate(numerator, denominator):
    value = Fraction(numerator, denominator)
    return {"numerator": numerator, "denominator": denominator, "value": str(value)}


def _mean(values):
    value = sum(values, Fraction(0)) / len(values)
    return {"numerator": value.numerator, "denominator": value.denominator, "value": str(value)}


def calibrate_dataset(raw_bytes, base_config_raw, mechanism="rbts", provenance_status="assumption", source_name="dataset.csv"):
    if provenance_status not in PROVENANCE_STATUSES:
        raise CalibrationError("provenance_status", "Cần synthetic, assumption, pilot_estimate hoặc historical_estimate.")
    if not isinstance(source_name, str) or not source_name.strip():
        raise CalibrationError("source_name", "Cần tên nguồn không rỗng.")
    try:
        base = validate_config(base_config_raw, mechanism)
    except ValidationError as error:
        raise CalibrationError(f"base_config.{error.field}", error.message) from None
    if base.model_version != V2_MODEL_VERSION:
        raise CalibrationError("base_config.model_version", "Calibration chỉ sinh config ceav-m1-v2.0.")
    rows = parse_dataset(raw_bytes)
    positives = [row for row in rows if row.y == 1]
    negatives = [row for row in rows if row.y == 0]
    estimates = {
        "pi": _rate(len(positives), len(rows)),
        "public_signal": {
            "sensitivity": _rate(sum(row.z == 1 for row in positives), len(positives)),
            "specificity": _rate(sum(row.z == 0 for row in negatives), len(negatives)),
        },
        "judges": {},
    }
    for index, judge in enumerate(JUDGES):
        estimates["judges"][judge] = {
            "private_signal": {
                "sensitivity": _rate(sum(row.private_signals[index] == 1 for row in positives), len(positives)),
                "specificity": _rate(sum(row.private_signals[index] == 0 for row in negatives), len(negatives)),
            },
            "high_effort_cost": _mean([row.costs[index] for row in rows]),
        }
    config = deepcopy(base.raw())
    config["pi"] = estimates["pi"]["value"]
    config["public_signal"] = {key: value["value"] for key, value in estimates["public_signal"].items()}
    for judge in JUDGES:
        config["judges"][judge] = {
            "private_signal": {key: value["value"] for key, value in estimates["judges"][judge]["private_signal"].items()},
            "high_effort_cost": estimates["judges"][judge]["high_effort_cost"]["value"],
        }
    try:
        config = validate_config(config, mechanism).raw()
    except ValidationError as error:
        raise CalibrationError(error.field, "Estimate không tạo được config V2 hợp lệ: " + error.message) from None
    canonical_rows = [row.canonical() for row in sorted(rows, key=lambda item: item.case_id)]
    warnings = ["Dataset synthetic chỉ kiểm tra pipeline; không phải bằng chứng về hiệu năng Judge."] if provenance_status == "synthetic" else [
        "Point estimates chưa chứng minh tính đại diện, ground-truth quality hoặc absence of selection bias."
    ]
    return {
        "calibration_version": CALIBRATION_VERSION,
        "dataset_version": DATASET_VERSION,
        "model_version": V2_MODEL_VERSION,
        "source_name": Path(source_name).name,
        "provenance_status": provenance_status,
        "raw_sha256": sha256(raw_bytes),
        "dataset_hash": semantic_hash(canonical_rows),
        "row_count": len(rows),
        "class_counts": {"0": len(negatives), "1": len(positives)},
        "estimates": estimates,
        "config": config,
        "warnings": warnings,
    }


def calibration_documents():
    folder = ROOT / CALIBRATION_FREEZE
    event = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if event.get("event") != "implementation_start" or event.get("feature") != CALIBRATION_VERSION:
        raise ValueError("Invalid calibration implementation-start freeze")
    for record in event["files"]:
        if sha256((folder / record["snapshot"]).read_bytes()) != record["sha256"]:
            raise ValueError("Calibration freeze checksum mismatch: " + record["snapshot"])
    return event


def write_calibration_run(raw_bytes, base_config_raw, mechanism, provenance_status, out, source_name="dataset.csv", argv=None, defer_publication=False):
    result = calibrate_dataset(raw_bytes, base_config_raw, mechanism, provenance_status, source_name)
    config = validate_config(result["config"], mechanism)
    request = {"operation": "calibrate", "source_name": result["source_name"], "provenance_status": provenance_status,
               "mechanism": mechanism, "raw_sha256": result["raw_sha256"], "dataset_hash": result["dataset_hash"],
               "base_config": validate_config(base_config_raw, mechanism).raw()}
    out = Path(out)
    manifest = new_run(out, "calibrate", config, mechanism=mechanism, request=request, argv=argv,
                       publication_owner="local_server" if defer_publication else "cli")
    try:
        raw_path = out / "dataset.csv"
        raw_path.write_bytes(raw_bytes)
        write_json(out / "calibration.json", result)
        write_json(out / "base_config.json", request["base_config"])
        event = calibration_documents()
        pinned = out / "inputs" / "calibration"
        pinned.mkdir()
        freeze = ROOT / CALIBRATION_FREEZE
        for record in event["files"]:
            shutil.copyfile(freeze / record["snapshot"], pinned / record["snapshot"])
        shutil.copyfile(freeze / "manifest.json", pinned / "freeze_event.json")
        manifest["calibration"] = {"revision": CALIBRATION_VERSION, "schema": DATASET_VERSION,
                                   "freeze": CALIBRATION_FREEZE, "freeze_created_at_utc": event["created_at_utc"],
                                   "documents": event["files"], "dataset_hash": result["dataset_hash"],
                                   "raw_sha256": result["raw_sha256"], "provenance_status": provenance_status}
        (out / "report.md").write_text(
            "# CEAV-M1 V2.1 — Calibration\n\n"
            f"Status: {'running' if defer_publication else 'succeeded'}; source: `{result['source_name']}`; provenance: `{provenance_status}`.\n\n"
            f"Rows: {result['row_count']}; Y=0: {result['class_counts']['0']}; Y=1: {result['class_counts']['1']}.\n\n"
            f"Dataset semantic hash: `{result['dataset_hash']}`. Raw SHA-256: `{result['raw_sha256']}`.\n\n"
            "Config V2 được ước lượng bằng exact counts, không smoothing. Xem `calibration.json` để biết numerator/denominator. "
            "Calibration không tự chạy analyzer. Synthetic data không phải evidence thực nghiệm.\n",
            encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest)
        else:
            write_json(out / "manifest.json", manifest)
        return result
    except BaseException as error:
        if not defer_publication:
            finish_run(out, manifest, "failed", error)
        raise
