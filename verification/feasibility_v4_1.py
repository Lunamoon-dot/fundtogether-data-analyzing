"""Finite V4.1 feasibility certificate; no production imports or policy search."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


@dataclass(frozen=True)
class Policy:
    f: F = F(0)
    lambda_peer: F = F(0)
    mu: F = F(1)
    q: F = F(0)
    budget: F = F(6)
    kappa: F = F(0)
    operating_cost: F = F(0)


@dataclass(frozen=True)
class Fixture:
    name: str
    public_quality: F
    private_quality: F
    audit_quality: F
    anchor_match: tuple[F, F]
    high_match: tuple[F, F]
    delta: tuple[F, F]
    costs: tuple[F, F, F] = (F(1, 20),) * 3
    target_weights: tuple[F, F] = (F(1, 2), F(1, 2))
    batch_weights: tuple[F, F] = (F(1, 2), F(1, 2))
    batch_size: int = 4


def _conditional_rows(public_quality, private_quality, audit_quality, z):
    rows = []
    for y, x, t in product((0, 1), repeat=3):
        p_y = F(1, 2)
        p_z = public_quality if z == y else 1 - public_quality
        p_x = private_quality if x == y else 1 - private_quality
        p_t = audit_quality if t == y else 1 - audit_quality
        rows.append((p_y * p_z * p_x * p_t, y, x, t))
    mass = sum(weight for weight, _, _, _ in rows)
    _require(mass > 0, "conditional row mass must be positive")
    return [(weight / mass, y, x, t) for weight, y, x, t in rows]


def _match_values(public_quality, private_quality, audit_quality, z):
    rows = _conditional_rows(public_quality, private_quality, audit_quality, z)
    anchor = max(sum(weight for weight, _, _, t in rows if t == report)
                 for report in (0, 1))
    high = sum(max(sum(weight for weight, _, x_value, t in rows
                        if x_value == x and t == report)
                   for report in (0, 1))
               for x in (0, 1))
    return anchor, high


def _fixture(name, public_quality):
    anchor = []
    high = []
    for z in (0, 1):
        a_z, h_z = _match_values(public_quality, F(4, 5), F(9, 10), z)
        anchor.append(a_z)
        high.append(h_z)
    return Fixture(name=name, public_quality=public_quality,
                   private_quality=F(4, 5), audit_quality=F(9, 10),
                   anchor_match=tuple(anchor), high_match=tuple(high),
                   delta=tuple(h - a for h, a in zip(high, anchor)))


def f41_01():
    """Public quality 19/20: private X has zero binary-audit value."""
    return _fixture("F41-01", F(19, 20))


def f41_02():
    """V4-F01 public quality 7/10 with audit quality 9/10."""
    return _fixture("F41-02", F(7, 10))


def _validate_policy(policy):
    for name in ("f", "lambda_peer", "mu", "kappa", "operating_cost"):
        _require(getattr(policy, name) >= 0, f"{name} must be non-negative")
    _require(F(0) <= policy.q <= F(1), "q must lie in [0,1]")
    _require(policy.budget >= 0, "budget must be non-negative")


def _policy_dict(policy):
    return {name: getattr(policy, name)
            for name in ("f", "lambda_peer", "mu", "q", "budget", "kappa", "operating_cost")}


def analyze(fixture, policy):
    """Evaluate only F1 entry, cap and F3 cost conditions for one fixed fixture."""
    _validate_policy(policy)
    gains = [[policy.mu * policy.q * fixture.delta[z] - cost
              for z in (0, 1)] for cost in fixture.costs]
    reward_cap = 3 * policy.f + 6 * policy.lambda_peer + 3 * policy.mu
    lb_by_z = [3 * (policy.f + policy.lambda_peer)
               + 3 * policy.mu * policy.q * fixture.anchor_match[z]
               + policy.q * policy.kappa + policy.operating_cost
               for z in (0, 1)]
    target_cost = sum(weight * value for weight, value
                      in zip(fixture.target_weights, lb_by_z))
    batch_cost = sum(weight * value for weight, value
                     in zip(fixture.batch_weights, lb_by_z))
    positive_deltas = [(cost, fixture.delta[z])
                       for cost in fixture.costs for z in (0, 1)
                       if fixture.delta[z] > 0 and policy.mu > 0]
    entry_boundary = (min(cost / (policy.mu * delta)
                          for cost, delta in positive_deltas)
                      if positive_deltas else None)
    return {
        "fixture": fixture.name,
        "policy": _policy_dict(policy),
        "reward_cap_per_claim": reward_cap,
        "policy_valid": reward_cap <= policy.budget,
        "mu_max": (policy.budget - 3 * policy.f - 6 * policy.lambda_peer) / 3,
        "gain_by_judge_z": gains,
        "entry_boundary_q": entry_boundary,
        "all_low_persists": all(gain <= 0 for row in gains for gain in row),
        "strict_entry_exists": any(gain > 0 for row in gains for gain in row),
        "cost_floor_by_z": lb_by_z,
        "cost_floor_target_population": target_cost,
        "cost_floor_batch_average": batch_cost,
        "cost_floor_actual_batch": fixture.batch_size * batch_cost,
        "cash_gate": F(4),
        "cash_floor_passes": target_cost <= F(4),
        "quality_status": "not_evaluated",
        "scope": "finite_fixture_feasibility_only",
    }


def _comparison_rows():
    policies = (
        ("audit-only", Policy(lambda_peer=F(0), mu=F(1), q=F(1), budget=F(6))),
        ("hybrid", Policy(lambda_peer=F(1), mu=F(1), q=F(1), budget=F(6))),
        ("audit-only-boundary", Policy(lambda_peer=F(0), mu=F(1), q=F(5, 8), budget=F(6))),
        ("hybrid-boundary", Policy(lambda_peer=F(1), mu=F(1), q=F(5, 8), budget=F(6))),
    )
    rows = []
    for fixture in (f41_01(), f41_02()):
        for label, policy in policies:
            result = analyze(fixture, policy)
            result["policy_label"] = label
            rows.append(result)
        for q in (F(5, 8), F(3, 4)):
            audit = analyze(fixture, Policy(lambda_peer=F(0), mu=F(1), q=q, budget=F(9)))
            hybrid = analyze(fixture, Policy(lambda_peer=F(1), mu=F(1), q=q, budget=F(9)))
            rows.append({
                "fixture": fixture.name,
                "comparison": "same_budget_same_audit_parameters",
                "q": q,
                "audit_only_gain": audit["gain_by_judge_z"],
                "hybrid_gain": hybrid["gain_by_judge_z"],
                "entry_gain_equal": audit["gain_by_judge_z"] == hybrid["gain_by_judge_z"],
                "audit_only_policy_valid": audit["policy_valid"],
                "hybrid_policy_valid": hybrid["policy_valid"],
            })
    return rows


def run_certificate():
    f41_01_fixture = f41_01()
    f41_02_fixture = f41_02()
    _require(f41_01_fixture.anchor_match == (F(43, 50), F(43, 50)), "F41-01 anchor mismatch")
    _require(f41_01_fixture.high_match == (F(43, 50), F(43, 50)), "F41-01 high mismatch")
    _require(f41_01_fixture.delta == (F(0), F(0)), "F41-01 delta mismatch")
    _require(f41_02_fixture.anchor_match == (F(33, 50), F(33, 50)), "F41-02 anchor mismatch")
    _require(f41_02_fixture.high_match == (F(37, 50), F(37, 50)), "F41-02 high mismatch")
    _require(f41_02_fixture.delta == (F(2, 25), F(2, 25)), "F41-02 delta mismatch")
    fixtures = {fixture.name: {
        "public_quality": fixture.public_quality,
        "private_quality": fixture.private_quality,
        "audit_quality": fixture.audit_quality,
        "anchor_match": fixture.anchor_match,
        "high_match": fixture.high_match,
        "delta": fixture.delta,
    } for fixture in (f41_01_fixture, f41_02_fixture)}
    return {
        "status": "passed",
        "finding": "finite_feasibility_certificate_only",
        "scope": "finite_fixture_feasibility_only",
        "policy_search": False,
        "fixtures": fixtures,
        "matrix": _comparison_rows(),
        "limits": [
            "no policy grid",
            "no exhaustive equilibrium search",
            "quality metrics not evaluated",
            "no production engine or UI",
        ],
    }


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _latest_freeze_manifest():
    candidates = sorted((ROOT / "spec_history").glob(
        "v4.1-feasibility-analyzer-implementation-start-*/manifest.json"))
    _require(candidates, "V4.1 feasibility analyzer freeze is missing")
    return candidates[-1]


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"event_type": "v4.1_finite_feasibility_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "implementation_start": False, "preregistered": False, "inputs": []}
    sources = [
        Path("CEAV_M1_V4_CONDITIONAL_SPEC.md"),
        Path("CEAV_M1_V4_1_FEASIBILITY.md"),
        Path("references/V4_CONDITIONAL_SCORING_SOURCES.md"),
        Path("verification/feasibility_v4_1.py"),
        Path("tests/test_v4_1_feasibility.py"),
        _latest_freeze_manifest().relative_to(ROOT),
    ]
    for source in sources:
        snapshot = Path("inputs") / source
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({"source": source.as_posix(), "snapshot": snapshot.as_posix(),
                                   "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        certificate = run_certificate()
        (out / "certificate.json").write_text(
            json.dumps(_jsonable(certificate), indent=2) + "\n", encoding="utf-8")
        (out / "report.md").write_text(
            "# V4.1 finite feasibility certificate\n\n"
            "Scope: F41-01/F41-02 entry, budget and necessary cost conditions.\n\n"
            "F41-01 has `delta=0`, so no `mu,q` can create a strict effort entry while peers stay Low.\n\n"
            "F41-02 has `delta=2/25`; the entry boundary is `q=5/8` at `mu=1,c=1/20`, "
            "with equality retaining all-Low. At `q=3/4`, audit-only has positive entry gain; "
            "the hybrid gain is algebraically identical when parameters are otherwise shared.\n\n"
            "The primary B=6 matrix also records that `lambda_peer=1,mu=1` violates the hybrid "
            "reward cap. Quality gates are not evaluated and no policy search or engine certificate "
            "is claimed.\n", encoding="utf-8")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out / name).read_bytes()).hexdigest()
                               for name in ("certificate.json", "report.md")}
        return certificate
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = write_run(args.out)
    print(json.dumps({"finding": record["finding"], "scope": record["scope"],
                      "out": str(args.out)}))
