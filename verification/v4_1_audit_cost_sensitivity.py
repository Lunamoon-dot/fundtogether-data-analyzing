"""Fixed-pair V3-HET audit-cost sensitivity; no frontier re-optimization."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "results/v4-1-minimal-screening-curated-20261024T011500"
GATES = {
    "max_false_approval_rate": F(1, 5),
    "max_false_rejection_rate": F(1, 4),
    "max_wrong_payout_value": F(3, 20),
    "max_cash_review_cost": F(4),
}
POLICY_KEYS = ("lambda_peer", "mu", "q")
EXPECTED = {
    "audit_only": {
        "lambda_peer": F(0), "mu": F(3, 2), "q": F(5, 8),
        "cash_review_cost": F(381, 160),
        "accuracy": F(1813, 2000), "false_approval_rate": F(51, 500),
        "false_rejection_rate": F(17, 200), "wrong_payout_value": F(51, 1000),
    },
    "hybrid": {
        "lambda_peer": F(1, 4), "mu": F(5, 4), "q": F(1, 2),
        "cash_review_cost": F(14551, 6000),
        "accuracy": F(421, 500), "false_approval_rate": F(12, 125),
        "false_rejection_rate": F(11, 50), "wrong_payout_value": F(6, 125),
    },
}


def _fraction(value):
    return value if isinstance(value, F) else F(value)


def _load_projection():
    source = CURATED / "pair_projection.json"
    if not source.exists():
        raise FileNotFoundError(source)
    projection = json.loads(source.read_text(encoding="utf-8"))
    if projection.get("fixture") != "V3-HET":
        raise AssertionError("sensitivity requires the pinned V3-HET fixture")
    for mechanism, expected in EXPECTED.items():
        record = projection["policies"][mechanism]
        policy = record["policy"]
        for key in POLICY_KEYS:
            if _fraction(policy[key]) != expected[key]:
                raise AssertionError((mechanism, key, policy[key], expected[key]))
        metrics = record["worst_equilibrium_metrics"]
        if not record["pure_equilibrium_exists"] or not metrics["robust"]:
            raise AssertionError((mechanism, "baseline policy must be robust"))
        for key in ("cash_review_cost", "accuracy", "false_approval_rate",
                    "false_rejection_rate", "wrong_payout_value"):
            if _fraction(metrics[key]) != expected[key]:
                raise AssertionError((mechanism, key, metrics[key], expected[key]))
    return projection


def _quality_passes(expected):
    return (expected["false_approval_rate"] <= GATES["max_false_approval_rate"]
            and expected["false_rejection_rate"] <= GATES["max_false_rejection_rate"]
            and expected["wrong_payout_value"] <= GATES["max_wrong_payout_value"])


def _policy_at_kappa(mechanism, kappa):
    expected = EXPECTED[mechanism]
    cash = expected["cash_review_cost"] + expected["q"] * kappa
    return {
        "policy": {key: expected[key] for key in POLICY_KEYS},
        "kappa": kappa,
        "cash_review_cost": cash,
        "cash_gate_pass": cash <= GATES["max_cash_review_cost"],
        "quality_gate_pass": _quality_passes(expected),
        "robust_under_declared_gates": cash <= GATES["max_cash_review_cost"] and _quality_passes(expected),
        "quality": {key: expected[key] for key in
                     ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value")},
    }


def run_study():
    _load_projection()
    audit = EXPECTED["audit_only"]
    hybrid = EXPECTED["hybrid"]
    kappa_star = (hybrid["cash_review_cost"] - audit["cash_review_cost"]) / (audit["q"] - hybrid["q"])
    audit_gate_max = (GATES["max_cash_review_cost"] - audit["cash_review_cost"]) / audit["q"]
    hybrid_gate_max = (GATES["max_cash_review_cost"] - hybrid["cash_review_cost"]) / hybrid["q"]
    points = (F(0), F(1, 4), kappa_star, F(3, 8), F(1, 2), F(1), hybrid_gate_max)
    point_records = []
    for kappa in points:
        audit_record = _policy_at_kappa("audit_only", kappa)
        hybrid_record = _policy_at_kappa("hybrid", kappa)
        if hybrid_record["cash_review_cost"] < audit_record["cash_review_cost"]:
            cheaper = "hybrid"
        elif hybrid_record["cash_review_cost"] > audit_record["cash_review_cost"]:
            cheaper = "audit_only"
        else:
            cheaper = "tie"
        point_records.append({"kappa": kappa, "audit_only": audit_record,
                              "hybrid": hybrid_record, "cheaper": cheaper,
                              "hybrid_economic_advantage_at_point":
                                  cheaper == "hybrid" and hybrid_record["robust_under_declared_gates"]})
    return {
        "status": "passed",
        "fixture": "V3-HET",
        "study_scope": "fixed_pair_only",
        "policies": {mechanism: {key: EXPECTED[mechanism][key] for key in POLICY_KEYS}
                     for mechanism in ("audit_only", "hybrid")},
        "baseline_cash": {"audit_only": audit["cash_review_cost"], "hybrid": hybrid["cash_review_cost"]},
        "kappa_star": kappa_star,
        "audit_gate_kappa_max": audit_gate_max,
        "hybrid_gate_kappa_max": hybrid_gate_max,
        "hybrid_cheaper_and_gate_feasible_interval": {
            "lower_exclusive": kappa_star,
            "upper_inclusive": hybrid_gate_max,
        },
        "points": point_records,
        "finding": "hybrid_fixed_pair_has_a_positive_audit_cost_tradeoff_but_quality_tradeoff_remains",
        "limits": ["fixed policy pair", "synthetic V3-HET", "no frontier re-optimization",
                   "no human labor calibration", "no global or production conclusion"],
    }


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _freeze_manifest():
    candidates = sorted((ROOT / "spec_history").glob("v4.1-audit-cost-sensitivity-implementation-start-*/manifest.json"))
    if not candidates:
        raise AssertionError("audit-cost sensitivity freeze is missing")
    return candidates[-1]


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"event_type": "v4.1_audit_cost_sensitivity_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "implementation_start": False, "preregistered": False, "inputs": []}
    sources = [Path("CEAV_M1_V4_1_AUDIT_COST_SENSITIVITY_SPEC.md"),
               Path("CEAV_M1_V4_1_SCREENING_SPEC.md"),
               Path("verification/v4_1_audit_cost_sensitivity.py"),
               Path("verification/v4_1_screening.py"),
               Path("verification/oracle_v4_1_screening.py"),
               Path("tests/test_v4_1_audit_cost_sensitivity.py"),
               Path("results/v4-1-minimal-screening-curated-20261024T011500/pair_projection.json"),
               Path("results/v4-1-minimal-screening-curated-20261024T011500/manifest.json"),
               _freeze_manifest().relative_to(ROOT)]
    for source in sources:
        snapshot = Path("inputs") / source
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({"source": source.as_posix(), "snapshot": snapshot.as_posix(),
                                   "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        result = run_study()
        (out / "sensitivity.json").write_text(json.dumps(_jsonable(result), indent=2) + "\n", encoding="utf-8")
        lines = ["# CEAV-M1 V4.1 — Audit-cost sensitivity", "",
                 "Scope: fixed V3-HET pair; no policy re-optimization.", "",
                 f"Crossover: `kappa* = {result['kappa_star']}`.",
                 f"Audit-only cash gate: `kappa <= {result['audit_gate_kappa_max']}`.",
                 f"Hybrid cash gate: `kappa <= {result['hybrid_gate_kappa_max']}`.", "",
                 "Hybrid is cheaper only on the open interval above `kappa*`; equality is a tie.", "",
                 "| kappa | Audit cash | Hybrid cash | Cheaper | Hybrid robust |", "| ---: | ---: | ---: | --- | --- |"]
        for point in result["points"]:
            lines.append(f"| {point['kappa']} | {point['audit_only']['cash_review_cost']} | {point['hybrid']['cash_review_cost']} | {point['cheaper']} | {point['hybrid']['robust_under_declared_gates']} |")
        lines += ["", "Finding: `hybrid_fixed_pair_has_a_positive_audit_cost_tradeoff_but_quality_tradeoff_remains`.",
                  "This does not establish a frontier or production advantage.", ""]
        (out / "report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out / name).read_bytes()).hexdigest()
                                for name in ("sensitivity.json", "report.md")}
        return result
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"status": result["status"], "kappa_star": str(result["kappa_star"]), "out": str(args.out)}))
