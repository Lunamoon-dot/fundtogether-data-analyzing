"""Phase 1 feasibility certificate for CEAV-M1 V5.0.

This module is intentionally smaller than a game engine.  It evaluates exact
posterior/value-of-information bounds and payment accounting for fixed
fixtures; it makes no policy-grid or production-equilibrium claim.
"""

import argparse
from dataclasses import dataclass
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

from verification import oracle_v5 as oracle


MECHANISMS = ("incremental", "direct")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Policy:
    mechanism: str = "incremental"
    f: F = F(0)
    mu: F = F(1)
    q: F = F(1)
    budget: F = F(6)
    kappa: F = F(0)
    operating_cost: F = F(0)


def _as_fraction(value):
    return value if isinstance(value, F) else F(value)


def mu_max(mechanism, budget, f):
    budget = _as_fraction(budget)
    f = _as_fraction(f)
    denominator = F(6) if mechanism == "incremental" else F(3) if mechanism == "direct" else None
    if denominator is None:
        raise KeyError(mechanism)
    numerator = budget - 3 * f
    return numerator / denominator if numerator >= 0 else None


def _validate_policy(policy):
    if policy.mechanism not in MECHANISMS:
        raise ValueError(f"unknown mechanism: {policy.mechanism}")
    for name in ("f", "mu", "budget", "kappa", "operating_cost"):
        _require(getattr(policy, name) >= 0, f"{name} must be non-negative")
    _require(F(0) <= policy.q <= F(1), "q must lie in [0,1]")
    cap = oracle.payment_bounds(policy.mechanism, policy.f, policy.mu)["cap_total"]
    _require(cap <= policy.budget, f"reserve cap {cap} exceeds budget {policy.budget}")


def _threshold(cost, delta, mu):
    if mu <= 0 or delta <= 0:
        return None
    return cost / (mu * delta)


def _branch_reward(fixture, judge, z, policy, high=False):
    if high:
        return oracle.expected_high_reward(fixture, judge, z, policy.mechanism,
                                           policy.f, policy.mu, policy.q)
    return oracle.expected_low_reward(fixture, judge, z, policy.mechanism,
                                      policy.f, policy.mu, policy.q)


def analyze(fixture_name, policy=Policy()):
    """Return exact entry, cap, and cash-floor metrics for one fixture/policy."""
    _validate_policy(policy)
    metrics = oracle.fixture_metrics(fixture_name)
    fixture = metrics["fixture"]
    deltas = metrics["delta_t_by_judge"]
    max_mu = mu_max(policy.mechanism, policy.budget, policy.f)
    gains = tuple(tuple(policy.mu * policy.q * deltas[i][z] - fixture.judges[i].cost
                        for z in (0, 1)) for i in range(3))
    cap_gain = tuple(tuple(max_mu * deltas[i][z] - fixture.judges[i].cost
                          for z in (0, 1)) for i in range(3))
    thresholds = tuple(tuple(_threshold(fixture.judges[i].cost, deltas[i][z], policy.mu)
                             for z in (0, 1)) for i in range(3))
    low_rewards = tuple(tuple(_branch_reward(fixture, i, z, policy)
                              for z in (0, 1)) for i in range(3))
    high_rewards = tuple(tuple(_branch_reward(fixture, i, z, policy, high=True)
                               for z in (0, 1)) for i in range(3))
    cash_low_by_z = tuple(sum(low_rewards[i][z] for i in range(3))
                          + policy.q * policy.kappa + policy.operating_cost
                          for z in (0, 1))
    target_cash_floor = sum(weight * value for weight, value
                            in zip(fixture.target_weights, cash_low_by_z))
    batch_cash_floor = sum(weight * value for weight, value
                           in zip(fixture.batch_weights, cash_low_by_z))
    strict_entry_exists = any(value > 0 for row in gains for value in row)
    strict_entry_possible_at_cap = any(value > 0 for row in cap_gain for value in row)
    return {
        "fixture": fixture_name,
        "mechanism": policy.mechanism,
        "policy": policy,
        "policy_valid": True,
        "mu_max": max_mu,
        "reserve_cap_total": oracle.payment_bounds(policy.mechanism, policy.f, policy.mu)["cap_total"],
        "payment_bounds_per_judge": oracle.payment_bounds(policy.mechanism, policy.f, policy.mu),
        "delta_t_by_judge": deltas,
        "delta_y_by_judge": metrics["delta_y_by_judge"],
        "gain_by_judge_z": gains,
        "max_gain_at_mu_max_by_judge_z": cap_gain,
        "audit_threshold_q_by_judge_z": thresholds,
        "strict_entry_exists": strict_entry_exists,
        "strict_entry_possible_at_cap": strict_entry_possible_at_cap,
        "all_low_persists_at_policy": not strict_entry_exists,
        "low_rewards_by_judge_z": low_rewards,
        "high_rewards_by_judge_z": high_rewards,
        "cash_floor_by_z": cash_low_by_z,
        "cash_floor_target_population": target_cash_floor,
        "cash_floor_batch_average": batch_cash_floor,
        "cash_floor_actual_batch": fixture.batch_size * batch_cash_floor,
        "target_weights": fixture.target_weights,
        "batch_weights": fixture.batch_weights,
        "quality_status": "not_evaluated",
        "scope": "fixed-fixture-feasibility-only",
    }


def run_certificate():
    """Run exact Phase 1 checks and return a bounded research certificate."""
    f01 = oracle.fixture_metrics("F51-01")
    f02 = oracle.fixture_metrics("F51-02")
    _require(f01["delta_y"] == (F(3249, 708400),) * 2, "F51-01 Delta_Y mismatch")
    _require(f01["delta_t"] == (F(3249, 1106875),) * 2, "F51-01 Delta_T mismatch")
    _require(f02["delta_y"] == (F(3969, 58900),) * 2, "F51-02 Delta_Y mismatch")
    _require(f02["delta_t"] == (F(15876, 368125),) * 2, "F51-02 Delta_T mismatch")
    for name in ("F51-01", "F51-02", "V3-HET"):
        metrics = oracle.fixture_metrics(name)
        d = metrics["audit_sensitivity"] + metrics["audit_specificity"] - 1
        for y_row, t_row in zip(metrics["delta_y_by_judge"], metrics["delta_t_by_judge"]):
            _require(t_row == tuple(d * d * value for value in y_row),
                     f"noise attenuation mismatch in {name}")

    f01_a = analyze("F51-01", Policy("incremental", mu=F(1), q=F(1)))
    f02_a = analyze("F51-02", Policy("incremental", mu=F(1), q=F(1)))
    _require(not f01_a["strict_entry_possible_at_cap"], "F51-01 should be A-infeasible")
    _require(not f02_a["strict_entry_possible_at_cap"], "F51-02 should be A-infeasible")
    f01_b = analyze("F51-01", Policy("direct", mu=F(2), q=F(1)))
    _require(not f01_b["strict_entry_possible_at_cap"], "F51-01 direct Brier should remain infeasible")
    f02_b = analyze("F51-02", Policy("direct", mu=F(2), q=F(3, 5)))
    _require(f02_b["strict_entry_exists"], "direct Brier F51-02 candidate should be retained")
    _require(f02_b["cash_floor_target_population"] <= 4,
             "direct Brier F51-02 witness should fit the target cash floor")
    het_metrics = oracle.fixture_metrics("V3-HET")
    _require(het_metrics["target_weights"] == (F(2, 5), F(3, 5)),
             "V3-HET target weights must remain population-derived")
    _require(het_metrics["batch_weights"] == (F(1, 2), F(1, 2)),
             "V3-HET batch weights must remain separately declared")
    _require(het_metrics["p_l_t"] == (F(3, 10), F(19, 30)),
             "baseline posterior must be model-defined before reporting")
    boundary_mu = F(19, 10)
    boundary_q = F(1, 20) / (boundary_mu * het_metrics["delta_t_by_judge"][0][1])
    boundary = analyze("V3-HET", Policy("direct", f=F(1, 10), mu=boundary_mu, q=boundary_q))
    _require(boundary["gain_by_judge_z"][0][1] == 0, "boundary gain must be an exact tie")
    _require(not boundary["strict_entry_exists"], "boundary must not count equality as strict entry")
    return {
        "status": "passed",
        "scope": "phase1_exact_feasibility_only",
        "finding": "v5_a_infeasible_on_f51_01_and_f51_02; direct_brier_requires_separate_screening",
        "f51_01_incremental": f01_a,
        "f51_02_incremental": f02_a,
        "f51_01_direct": f01_b,
        "f51_02_direct": f02_b,
        "v3_het_incremental": analyze("V3-HET", Policy("incremental", f=F(1, 10), mu=F(19, 20), q=F(1))),
        "v3_het_direct": analyze("V3-HET", Policy("direct", f=F(1, 10), mu=F(19, 10), q=F(4, 5))),
        "direct_boundary": boundary,
        "limits": ["no decision-quality evaluator", "no equilibrium selection", "no global optimum",
                   "no continuous policy search", "no production conclusion"],
    }


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, Policy):
        return {name: _jsonable(getattr(value, name))
                for name in ("mechanism", "f", "mu", "q", "budget", "kappa", "operating_cost")}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _freeze_manifest_path():
    candidates = sorted((ROOT / "spec_history").glob("v5.0-agiis-phase1-implementation-start-*/MANIFEST.json"))
    if not candidates:
        raise FileNotFoundError("V5 freeze manifest is missing")
    return candidates[-1]


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "event_type": "v5.0_agiis_phase1_feasibility_run",
        "model_version": "ceav-m1-v5.0-agiis",
        "status": "running",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": [],
    }
    sources = [
        Path("CEAV_M1_V5_INFORMATION_SCORING_SPEC.md"),
        Path("CEAV_M1_V5_FEASIBILITY.md"),
        Path("references/V5_INFORMATION_SCORING_SOURCES.md"),
        Path("verification/oracle_v5.py"),
        Path("verification/feasibility_v5.py"),
        Path("tests/test_v5_feasibility.py"),
        Path("configs/v3/heterogeneous_anchor.json"),
        _freeze_manifest_path().relative_to(ROOT),
    ]
    for source in sources:
        snapshot = Path("inputs") / source
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({"source": source.as_posix(), "snapshot": snapshot.as_posix(),
                                    "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        result = run_certificate()
        (out / "certificate.json").write_text(json.dumps(_jsonable(result), indent=2) + "\n", encoding="utf-8")
        report = [
            "# CEAV-M1 V5.0 — Phase 1 feasibility certificate", "",
            "Scope: exact finite-sum feasibility only; no production engine or global policy search.", "",
            "Finding: `v5_a_infeasible_on_f51_01_and_f51_02; direct_brier_requires_separate_screening`.", "",
            "V5.0-A strict high effort is impossible at the reward cap on both public-signal fixtures.",
            "Direct Brier is retained as a separate ablation because its reserve cap is different.", "",
            "| Fixture | Mechanism | mu_max | Strict entry at selected policy | Strict entry possible at cap | Target cash floor | Cash gate |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
        for key in ("f51_01_incremental", "f51_02_incremental", "f51_01_direct", "f51_02_direct", "v3_het_incremental", "v3_het_direct"):
            row = result[key]
            report.append(f"| {row['fixture']} | {row['mechanism']} | {row['mu_max']} | {row['strict_entry_exists']} | {row['strict_entry_possible_at_cap']} | {row['cash_floor_target_population']} | {row['cash_floor_target_population'] <= 4} |")
        report += ["", "Quality metrics are `not_evaluated` in Phase 1; positive effort gain is not a policy pass.", ""]
        (out / "report.md").write_text("\n".join(report), encoding="utf-8", newline="\n")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out / name).read_bytes()).hexdigest()
                                for name in ("certificate.json", "report.md")}
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
    print(json.dumps({"status": result["status"], "finding": result["finding"], "out": str(args.out)}))
