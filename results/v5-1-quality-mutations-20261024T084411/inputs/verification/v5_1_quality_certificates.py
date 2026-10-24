"""Immutable Phase 1.5 decision-quality and baseline certificates.

The finite-state calculations live in oracle_v5_1_quality. This runner only
asserts the declared certificates, snapshots its inputs, and emits an exact
JSON/report pair. It is intentionally not a production engine.
"""

import argparse
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verification import oracle_v5_1_quality as oracle


PARENT_COMMIT = "2835559652b912536439c5b504da30ba68c91436"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _assert_f51(record):
    expected_profile_direct = (("H", "H"),) * 3
    expected_profile_binary = (("H01", "H01"),) * 3
    for label, value, profile in (
        ("direct", record["direct"], expected_profile_direct),
        ("binary_audit_only", record["binary_audit_only"], expected_profile_binary),
    ):
        _require(value["effort_profile"] == profile, f"F51-02 {label} effort profile mismatch")
        _require(value["accuracy"] == F(112, 125), f"F51-02 {label} accuracy mismatch")
        _require(value["false_approval_rate"] == F(13, 125), f"F51-02 {label} FA mismatch")
        _require(value["false_rejection_rate"] == F(13, 125), f"F51-02 {label} FR mismatch")
        _require(value["wrong_payout_value"] == F(13, 250), f"F51-02 {label} wrong payout mismatch")
        _require(value["realized_reward_cap"] == F(6), f"F51-02 {label} cap mismatch")
        _require(value["decision_rule"] == {0: "majority_X", 1: "majority_X"},
                 f"F51-02 {label} decision rule mismatch")
    _require(record["direct"]["response_options"] == ((('H',), ('H',)),) * 3,
             "F51-02 direct response options mismatch")
    _require(record["binary_audit_only"]["response_options"] == ((('H01',), ('H01',)),) * 3,
             "F51-02 binary response options mismatch")
    _require(record["direct"]["expected_cash_cost"] == F(434007, 147250),
             "F51-02 direct cash mismatch")
    _require(record["binary_audit_only"]["expected_cash_cost"] == F(111, 50),
             "F51-02 binary cash mismatch")
    _require(record["direct"]["audit_exposure"] == F(3, 5), "F51-02 direct exposure mismatch")
    _require(record["binary_audit_only"]["audit_exposure"] == F(1, 2),
             "F51-02 binary exposure mismatch")
    _require(record["direct"]["expected_cash_cost"] > record["binary_audit_only"]["expected_cash_cost"],
             "F51-02 direct must be more expensive")
    _require(record["direct"]["audit_exposure"] > record["binary_audit_only"]["audit_exposure"],
             "F51-02 direct must expose more audits")
    direct = record["direct"]
    _require(direct["forecast_p_t"] == {
        0: {0: F(11, 62), 1: F(23, 38)},
        1: {0: F(15, 38), 1: F(51, 62)},
    }, "F51-02 direct forecasts mismatch")
    _require(direct["vote_by_z_x"] == {0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}},
             "F51-02 direct vote map mismatch")
    return {
        "status": "proved",
        "finding": "direct_brier_strictly_dominated_by_binary_audit_only_on_F51_02",
        "same_decision_quality": True,
        "lower_audit_exposure": True,
        "lower_cash_cost": True,
    }


def _assert_v3(record):
    direct = record["direct"]
    _require(direct["effort_profile"] == (("H", "H"), ("L", "L"), ("L", "L")),
             "V3-HET effort profile mismatch")
    _require(direct["response_options"] == ((('H',), ('H',)), (('L',), ('L',)), (('L',), ('L',))),
             "V3-HET response options mismatch")
    _require(direct["decision_rule"] == {0: "Z", 1: "Z"}, "V3-HET decision rule mismatch")
    _require(direct["accuracy"] == F(7, 10), "V3-HET accuracy mismatch")
    _require(direct["false_approval_rate"] == F(2, 5), "V3-HET FA mismatch")
    _require(direct["false_rejection_rate"] == F(1, 5), "V3-HET FR mismatch")
    _require(direct["wrong_payout_value"] == F(1, 5), "V3-HET wrong payout mismatch")
    _require(direct["expected_cash_cost"] == F(4609871, 1171875),
             "V3-HET direct cash mismatch")
    return {
        "status": "proved",
        "finding": "declared_V3_HET_direct_witness_has_D_equals_Z_but_fails_quality_targets",
        "quality_is_not_a_pass": True,
    }


def _assert_bound(record):
    bound = record["budget_bound"]
    _require(bound["s_threshold_B_z0"] == F(155, 98), "B threshold mismatch")
    _require(bound["B_z0_best_effort_at_threshold"] == ("L", "H"),
             "threshold tie must retain both B responses")
    _require(bound["cheapest_tie_resolution_cost"] == F(14998033, 3675000),
             "cheapest tie cost mismatch")
    _require(bound["high_tie_profile_exceeds_cash_gate"], "high tie profile must exceed cash gate")
    _require(bound["cheapest_profile_exceeds_cash_gate"], "cheapest profile must exceed cash gate")
    _require(bound["cheapest_tie_resolution_cost"] > bound["cash_gate"],
             "cheapest threshold profile must exceed cash gate")
    return {
        "status": "proved",
        "finding": "B_high_effort_entry_at_threshold_exceeds_cash_gate_in_fixed_V3_HET",
        "strict_high_requires": bound["strict_high_requires"],
        "scope": "fixed-f=1/10,B=6,kappa=0,V3-HET",
    }


def run_certificate():
    f51 = oracle.certificate_f51_02()
    v3 = oracle.certificate_v3_het()
    findings = {
        "certificate_1_F51_02": _assert_f51(f51),
        "certificate_2_V3_HET": _assert_v3(v3),
        "certificate_3_budget_bound": _assert_bound(v3),
    }
    return {
        "status": "passed",
        "model_version": "ceav-m1-v5.1-quality-certificates",
        "parent_commit": PARENT_COMMIT,
        "findings": findings,
        "certificates": {"F51-02": f51, "V3-HET": v3},
        "decision": "NO-GO",
        "decision_reason": (
            "F51-02 direct Brier is strictly dominated by binary audit-only on exposure and cash "
            "with identical decision quality; the fixed V3-HET B-entry lower bound exceeds the cash gate."
        ),
        "limits": [
            "finite fixed fixtures only",
            "no global policy optimization",
            "no impossibility claim for other scoring rules or environments",
            "no full engine/API/UI conclusion",
        ],
    }


def _freeze_manifest_path():
    candidates = sorted((ROOT / "spec_history").glob("v5.1-phase1.5-implementation-start-*/MANIFEST.json"))
    if not candidates:
        raise FileNotFoundError("V5.1 freeze manifest is missing")
    return candidates[-1]


def _source_list():
    return [
        Path("CEAV_M1_V5_1_DECISION_QUALITY_CERTIFICATES.md"),
        Path("CEAV_M1_V5_INFORMATION_SCORING_SPEC.md"),
        Path("CEAV_M1_V5_FEASIBILITY.md"),
        Path("verification/oracle_v5_1_quality.py"),
        Path("verification/v5_1_quality_certificates.py"),
        Path("tests/test_v5_1_quality_certificates.py"),
        Path("configs/v3/heterogeneous_anchor.json"),
        _freeze_manifest_path().relative_to(ROOT),
    ]


def _report(result):
    f51 = result["certificates"]["F51-02"]
    v3 = result["certificates"]["V3-HET"]
    bound = v3["budget_bound"]
    return "\n".join([
        "# CEAV-M1 V5.1 — Phase 1.5 certificates",
        "",
        f"Parent commit: {PARENT_COMMIT}",
        "",
        "All values below were computed with exact Fraction arithmetic by the independent finite-state oracle.",
        "",
        "## F51-02 baseline comparison",
        "",
        "| Policy | Equilibrium effort/action | Accuracy | FA | FR | Wrong payout | Cap | Audit exposure | Expected cash |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| Direct Brier | {f51['direct']['effort_profile']} | {f51['direct']['accuracy']} | {f51['direct']['false_approval_rate']} | {f51['direct']['false_rejection_rate']} | {f51['direct']['wrong_payout_value']} | {f51['direct']['realized_reward_cap']} | {f51['direct']['audit_exposure']} | {f51['direct']['expected_cash_cost']} |",
        f"| Binary audit-only | {f51['binary_audit_only']['effort_profile']} | {f51['binary_audit_only']['accuracy']} | {f51['binary_audit_only']['false_approval_rate']} | {f51['binary_audit_only']['false_rejection_rate']} | {f51['binary_audit_only']['wrong_payout_value']} | {f51['binary_audit_only']['realized_reward_cap']} | {f51['binary_audit_only']['audit_exposure']} | {f51['binary_audit_only']['expected_cash_cost']} |",
        "",
        "Finding: Direct Brier is strictly dominated by binary audit-only on the declared exposure and cash metrics, with identical decision quality.",
        "",
        "## V3-HET Direct Brier witness",
        "",
        f"Equilibrium effort: {v3['direct']['effort_profile']}; decision rule: {v3['direct']['decision_rule']}.",
        f"Accuracy {v3['direct']['accuracy']}, FA {v3['direct']['false_approval_rate']}, FR {v3['direct']['false_rejection_rate']}, wrong payout {v3['direct']['wrong_payout_value']}, expected cash {v3['direct']['expected_cash_cost']}.",
        "The witness has D=Z, but its quality values are not a quality-gate pass.",
        "",
        "## Budget-feasibility bound",
        "",
        f"B at Z=0 needs s >= {bound['s_threshold_B_z0']} for weak high-effort optimality; equality is the tie {bound['B_z0_best_effort_at_threshold']} and strict induction needs {bound['strict_high_requires']}.",
        f"Cheapest threshold tie resolution {bound['cheapest_tie_resolution_profile']} costs {bound['cheapest_tie_resolution_cost']} > cash gate {bound['cash_gate']}. Resolving B high at the tie costs {bound['B_high_at_z0_tie_cost']}.",
        "This lower bound is scoped to the fixed V3-HET Direct Brier environment and does not rule out other scoring rules or environments.",
        "",
        "## Decision",
        "",
        "NO-GO for Direct Brier Phase 2. No larger Direct Brier screening study is justified by these certificates; future work would need a different incentive/scoring hypothesis or an explicitly changed environment.",
        "",
    ])


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "event_type": "v5.1_phase1.5_quality_certificate_run",
        "model_version": "ceav-m1-v5.1-quality-certificates",
        "status": "running",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "parent_commit": PARENT_COMMIT,
        "inputs": [],
    }
    for source in _source_list():
        snapshot = Path("inputs") / source
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({
            "source": source.as_posix(),
            "snapshot": snapshot.as_posix(),
            "sha256": sha256(target.read_bytes()).hexdigest(),
        })
    try:
        result = run_certificate()
        (out / "certificate.json").write_text(
            json.dumps(_jsonable(result), indent=2) + "\n", encoding="utf-8"
        )
        (out / "report.md").write_text(_report(result), encoding="utf-8", newline="\n")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {
            name: sha256((out / name).read_bytes()).hexdigest()
            for name in ("certificate.json", "report.md")
        }
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
    print(json.dumps({"status": result["status"], "decision": result["decision"], "out": str(args.out)}))

