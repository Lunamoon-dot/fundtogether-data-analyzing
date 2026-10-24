"""Offline V4.1 equilibrium and quality screening; no production imports."""

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
ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
JUDGES = ("A", "B", "C")
Q_GRID = (F(0), F(1, 4), F(1, 2), F(5, 8), F(3, 4), F(1))
M_GRID = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1), F(5, 4), F(3, 2), F(2))
L_GRID = (F(1, 4), F(1, 2), F(3, 4), F(1))
GATES = {
    "max_false_approval_rate": F(1, 5),
    "max_false_rejection_rate": F(1, 4),
    "max_wrong_payout_value": F(3, 20),
    "max_cash_review_cost": F(4),
}


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


@dataclass(frozen=True)
class Policy:
    lambda_peer: F = F(0)
    mu: F = F(0)
    q: F = F(0)
    budget: F = F(6)

    @property
    def reward_cap(self):
        return 6 * self.lambda_peer + 3 * self.mu


@dataclass(frozen=True)
class Fixture:
    name: str
    pi: F
    public: tuple[F, F]
    private: tuple[tuple[F, F], tuple[F, F], tuple[F, F]]
    audit: tuple[F, F]
    costs: tuple[F, F, F]
    f: F
    payout_value: F
    operating_cost: F
    kappa: F
    target_weights: tuple[F, F]
    batch_weights: tuple[F, F] = (F(1, 2), F(1, 2))
    batch_size: int = 4


def _target_weights(pi, public):
    p_z1 = pi * likelihood(1, 1, *public) + (1 - pi) * likelihood(1, 0, *public)
    return (1 - p_z1, p_z1)


def _make_fixture(name, pi, public, private, audit, costs, f, payout_value=F(1),
                  operating_cost=F(0), kappa=F(0), batch_weights=(F(1, 2), F(1, 2))):
    return Fixture(name=name, pi=pi, public=public, private=private, audit=audit,
                   costs=costs, f=f, payout_value=payout_value,
                   operating_cost=operating_cost, kappa=kappa,
                   target_weights=_target_weights(pi, public), batch_weights=batch_weights)


def f41_01():
    return _make_fixture("F41-01", F(1, 2), (F(19, 20), F(19, 20)),
                         ((F(4, 5), F(4, 5)),) * 3, (F(9, 10), F(9, 10)),
                         (F(1, 20),) * 3, F(0))


def f41_02():
    return _make_fixture("F41-02", F(1, 2), (F(7, 10), F(7, 10)),
                         ((F(4, 5), F(4, 5)),) * 3, (F(9, 10), F(9, 10)),
                         (F(1, 20),) * 3, F(0))


def v3_het():
    return _make_fixture(
        "V3-HET", F(1, 2), (F(4, 5), F(3, 5)),
        ((F(9, 10), F(4, 5)), (F(3, 4), F(19, 20)), (F(13, 20), F(7, 10))),
        (F(9, 10), F(9, 10)), (F(1, 20), F(1, 10), F(1, 25)), F(1, 10),
    )


def report_for(action, x=None):
    return int(action[1]) if action[0] == "L" else int(action[1 + x])


def is_high(action):
    return action[0] == "H"


def classify_actions(actions):
    efforts = tuple(action[0] for action in actions)
    if all(effort == "L" for effort in efforts):
        return "all_low"
    if all(effort == "H" for effort in efforts) and all(action == "H01" for action in actions):
        return "informative_H01"
    if all(effort == "H" for effort in efforts) and all(action == "H10" for action in actions):
        return "inverted_H10"
    if len(set(efforts)) > 1:
        return "asymmetric_effort"
    return "other_pure"


def _joint_rows(fixture):
    rows = []
    for y, z, xa, xb, xc, t in product((0, 1), repeat=6):
        probability = fixture.pi if y else 1 - fixture.pi
        probability *= likelihood(z, y, *fixture.public)
        for x, signal in zip((xa, xb, xc), fixture.private):
            probability *= likelihood(x, y, *signal)
        probability *= likelihood(t, y, *fixture.audit)
        rows.append({"probability": probability, "y": y, "z": z,
                     "signals": (xa, xb, xc), "t": t})
    _require(sum(row["probability"] for row in rows) == 1, "joint mass must equal one")
    return rows


def _conditional_rows(fixture, z):
    rows = [row for row in _joint_rows(fixture) if row["z"] == z]
    mass = sum(row["probability"] for row in rows)
    _require(mass > 0, "public branch has no support")
    return [{**row, "probability": row["probability"] / mass} for row in rows]


class ScreeningModel:
    def __init__(self, fixture):
        self.fixture = fixture
        self.rows_by_z = {z: _conditional_rows(fixture, z) for z in (0, 1)}
        self.global_rows = _joint_rows(fixture)
        self._score_cache = {}
        self._anchor_cache = {}
        self._utility_cache = {}

    def mean_report(self, z, action, judge):
        rows = self.rows_by_z[z]
        return sum(row["probability"] * report_for(action, row["signals"][judge])
                   for row in rows)

    def covariance(self, z, action_i, action_j, judge_i, judge_j):
        key = (z, action_i, action_j, judge_i, judge_j)
        if key not in self._score_cache:
            rows = self.rows_by_z[z]
            mean_i = self.mean_report(z, action_i, judge_i)
            mean_j = self.mean_report(z, action_j, judge_j)
            moment = sum(row["probability"]
                         * report_for(action_i, row["signals"][judge_i])
                         * report_for(action_j, row["signals"][judge_j])
                         for row in rows)
            self._score_cache[key] = moment - mean_i * mean_j
        return self._score_cache[key]

    def anchor_match(self, z, action, judge):
        key = (z, action, judge)
        if key not in self._anchor_cache:
            self._anchor_cache[key] = sum(row["probability"]
                                          * F(report_for(action, row["signals"][judge]) == row["t"])
                                          for row in self.rows_by_z[z])
        return self._anchor_cache[key]

    def profile_stats(self, z, profile):
        scores = []
        anchors = []
        for judge in range(3):
            score = sum(self.covariance(z, profile[judge], profile[peer], judge, peer)
                        for peer in range(3) if peer != judge)
            scores.append(score)
            anchors.append(self.anchor_match(z, profile[judge], judge))
        return tuple(scores), tuple(anchors)

    def branch_utilities(self, z, policy, profile):
        key = (z, policy, tuple(profile))
        if key in self._utility_cache:
            return self._utility_cache[key]
        scores, anchors = self.profile_stats(z, profile)
        utilities = tuple(self.fixture.f + policy.lambda_peer * (1 + scores[judge])
                          + policy.mu * policy.q * anchors[judge]
                          - (self.fixture.costs[judge] if is_high(profile[judge]) else 0)
                          for judge in range(3))
        self._utility_cache[key] = utilities
        return utilities


def covariance_score(fixture, z, profile, judge):
    model = ScreeningModel(fixture)
    return model.profile_stats(z, profile)[0][judge]


def direct_centered_score(fixture, z, profile, judge):
    rows = _conditional_rows(fixture, z)
    total = F(0)
    for peer in range(3):
        if peer == judge:
            continue
        for first in rows:
            own = report_for(profile[judge], first["signals"][judge])
            same_task = F(own == report_for(profile[peer], first["signals"][peer]))
            for second in rows:
                cross_task = F(own == report_for(profile[peer], second["signals"][peer]))
                total += first["probability"] * second["probability"] * (same_task - cross_task) / 2
    return total


def best_response(fixture, policy, z, candidate_profile, judge, model=None):
    model = model or ScreeningModel(fixture)
    peer_actions = tuple(candidate_profile[index] for index in range(3) if index != judge)
    options = {}
    for action in ACTIONS:
        changed = list(candidate_profile)
        changed[judge] = action
        options[action] = model.branch_utilities(z, policy, tuple(changed))[judge]
    candidate_action = candidate_profile[judge]
    candidate_utility = options[candidate_action]
    best_utility = max(options.values())
    return {
        "candidate_action": candidate_action,
        "candidate_utility": candidate_utility,
        "best_utility": best_utility,
        "regret": best_utility - candidate_utility,
        "optimal_actions": [action for action in ACTIONS if options[action] == best_utility],
        "options": options,
        "peer_actions": peer_actions,
    }


def find_branch_equilibria(fixture, policy, z, model=None):
    model = model or ScreeningModel(fixture)
    retained = []
    for profile in product(ACTIONS, repeat=3):
        utilities = model.branch_utilities(z, policy, profile)
        responses = [best_response(fixture, policy, z, profile, judge, model=model) for judge in range(3)]
        if all(response["regret"] == 0 for response in responses):
            retained.append({
                "z": z,
                "actions": profile,
                "classification": classify_actions(profile),
                "utilities": utilities,
                "best_responses": responses,
            })
    return retained


def evaluate_profile(fixture, policy, profile_by_z, model=None):
    model = model or ScreeningModel(fixture)
    accuracy = false_approval_joint = false_rejection_joint = approvals = F(0)
    for row in model.global_rows:
        profile = profile_by_z[str(row["z"])]
        reports = tuple(report_for(action, row["signals"][judge]) for judge, action in enumerate(profile))
        decision = int(sum(reports) >= 2)
        probability = row["probability"]
        accuracy += probability * F(decision == row["y"])
        false_approval_joint += probability * F(row["y"] == 0 and decision == 1)
        false_rejection_joint += probability * F(row["y"] == 1 and decision == 0)
        approvals += probability * decision

    conditional = {}
    for z in (0, 1):
        scores, anchors = model.profile_stats(z, profile_by_z[str(z)])
        rewards = tuple(fixture.f + policy.lambda_peer * (1 + scores[judge])
                        + policy.mu * policy.q * anchors[judge] for judge in range(3))
        effort = sum(fixture.costs[judge] if is_high(profile_by_z[str(z)][judge]) else F(0)
                     for judge in range(3))
        conditional[z] = {"scores": scores, "anchors": anchors, "rewards": rewards,
                          "reward_total": sum(rewards), "effort_cost": effort,
                          "cash_cost": sum(rewards) + policy.q * fixture.kappa + fixture.operating_cost}

    reward_total = sum(fixture.target_weights[z] * conditional[z]["reward_total"] for z in (0, 1))
    effort_total = sum(fixture.target_weights[z] * conditional[z]["effort_cost"] for z in (0, 1))
    cash_target = sum(fixture.target_weights[z] * conditional[z]["cash_cost"] for z in (0, 1))
    cash_batch = sum(fixture.batch_weights[z] * conditional[z]["cash_cost"] for z in (0, 1))
    return {
        "metrics": {
            "accuracy": accuracy,
            "false_approval_rate": false_approval_joint / (1 - fixture.pi),
            "false_rejection_rate": false_rejection_joint / fixture.pi,
            "wrong_payout_probability": false_approval_joint,
            "wrong_payout_value": fixture.payout_value * false_approval_joint,
            "expected_approval_rate": approvals,
            "expected_reward_total": reward_total,
            "expected_effort_cost": effort_total,
            "expected_audit_cost": policy.q * fixture.kappa,
            "cash_review_cost": cash_target,
            "cash_review_cost_batch_average": cash_batch,
            "cash_review_cost_actual_batch": fixture.batch_size * cash_batch,
        },
        "conditional": conditional,
    }


def _full_classification(left, right):
    left_kind, right_kind = left["classification"], right["classification"]
    if left_kind == right_kind == "all_low":
        return "all_low"
    if left_kind == right_kind == "informative_H01":
        return "informative_H01"
    if left_kind == right_kind == "inverted_H10":
        return "inverted_H10"
    if "asymmetric_effort" in (left_kind, right_kind) or left_kind != right_kind:
        return "asymmetric_effort"
    return "other_pure"


def _worst_metrics(equilibria):
    if not equilibria:
        return {"status": "no_pure_equilibrium", "robust": False}
    keys = ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value", "cash_review_cost")
    worst = {
        "accuracy": min(record["metrics"]["accuracy"] for record in equilibria),
        "false_approval_rate": max(record["metrics"]["false_approval_rate"] for record in equilibria),
        "false_rejection_rate": max(record["metrics"]["false_rejection_rate"] for record in equilibria),
        "wrong_payout_value": max(record["metrics"]["wrong_payout_value"] for record in equilibria),
        "cash_review_cost": max(record["metrics"]["cash_review_cost"] for record in equilibria),
    }
    witnesses = {}
    for key in keys:
        target = worst[key]
        witnesses[key] = next(record["profile"] for record in equilibria
                              if record["metrics"][key] == target)
    robust = (worst["false_approval_rate"] <= GATES["max_false_approval_rate"]
              and worst["false_rejection_rate"] <= GATES["max_false_rejection_rate"]
              and worst["wrong_payout_value"] <= GATES["max_wrong_payout_value"]
              and worst["cash_review_cost"] <= GATES["max_cash_review_cost"])
    return {"status": "pure_equilibria_evaluated", "count": len(equilibria),
            **worst, "witnesses": witnesses, "robust": robust}


def _policy_valid(fixture, policy):
    cap = 3 * fixture.f + 6 * policy.lambda_peer + 3 * policy.mu
    return policy.lambda_peer >= 0 and policy.mu >= 0 and F(0) <= policy.q <= F(1) and cap <= policy.budget


def enumerate_policies(fixture, mechanism):
    policies = []
    if mechanism == "audit_only":
        candidates = (Policy(lambda_peer=F(0), mu=mu, q=q) for mu in M_GRID for q in Q_GRID)
    elif mechanism == "conditional_only":
        candidates = (Policy(lambda_peer=lam, mu=F(0), q=F(0)) for lam in L_GRID)
    elif mechanism == "hybrid":
        candidates = (Policy(lambda_peer=lam, mu=mu, q=q)
                      for lam in L_GRID for mu in M_GRID if mu > 0 for q in Q_GRID)
    else:
        raise ValueError(f"unknown mechanism: {mechanism}")
    for policy in candidates:
        if _policy_valid(fixture, policy):
            policies.append(policy)
    return policies


def screen_policy(fixture, policy):
    model = ScreeningModel(fixture)
    branches = {z: find_branch_equilibria(fixture, policy, z, model=model) for z in (0, 1)}
    equilibria = []
    for left, right in product(branches[0], branches[1]):
        profile = {"0": left["actions"], "1": right["actions"]}
        evaluated = evaluate_profile(fixture, policy, profile, model=model)
        metrics = evaluated["metrics"]
        equilibria.append({
            "profile": profile,
            "classification": _full_classification(left, right),
            "branch_classification": {"0": left["classification"], "1": right["classification"]},
            "utilities_by_branch": {"0": left["utilities"], "1": right["utilities"]},
            "metrics": metrics,
        })
    worst = _worst_metrics(equilibria)
    return {
        "policy": policy,
        "reward_cap": 3 * fixture.f + 6 * policy.lambda_peer + 3 * policy.mu,
        "policy_valid": _policy_valid(fixture, policy),
        "branch_equilibria": {str(z): branches[z] for z in (0, 1)},
        "equilibria": equilibria,
        "equilibrium_count": len(equilibria),
        "pure_equilibrium_exists": bool(equilibria),
        "worst_equilibrium_metrics": worst,
        "gates": GATES,
        "equilibrium_selection": "not_modeled",
    }


def _select_robust_policy(records):
    robust = [record for record in records if record["worst_equilibrium_metrics"].get("robust")]
    if not robust:
        return None
    selected = min(robust, key=lambda record: (record["worst_equilibrium_metrics"]["cash_review_cost"],
                                               record["policy"].mu, record["policy"].q))
    return selected["policy"]


def screen_fixture(fixture):
    mechanisms = {}
    for mechanism in ("audit_only", "conditional_only", "hybrid"):
        policies = [screen_policy(fixture, policy) for policy in enumerate_policies(fixture, mechanism)]
        selected = _select_robust_policy(policies)
        mechanisms[mechanism] = {
            "policy_count": len(policies),
            "feasible_policy_count": sum(record["policy_valid"] for record in policies),
            "pure_equilibrium_policy_count": sum(record["pure_equilibrium_exists"] for record in policies),
            "robust_policy_count": sum(record["worst_equilibrium_metrics"].get("robust", False) for record in policies),
            "selected_robust_policy": selected,
            "policy_selection_rule": "minimum worst-equilibrium cash among robust policies; null if none",
            "equilibrium_selection": "not_modeled",
            "policies": policies,
        }
    return {"fixture": fixture.name, "target_weights": fixture.target_weights,
            "batch_weights": fixture.batch_weights, "mechanisms": mechanisms,
            "gates": GATES, "finite_grid": {"Q": Q_GRID, "M": M_GRID, "L": L_GRID},
            "scope": "finite_declared_grid_only"}


def _dominates(left, right):
    """Return strict all-metric dominance for robust policy records."""
    left_policy, right_policy = left["policy"], right["policy"]
    left_metrics, right_metrics = left["worst_equilibrium_metrics"], right["worst_equilibrium_metrics"]
    weak = (left_policy.q <= right_policy.q
            and left_metrics["cash_review_cost"] <= right_metrics["cash_review_cost"]
            and left_metrics["accuracy"] >= right_metrics["accuracy"]
            and left_metrics["false_approval_rate"] <= right_metrics["false_approval_rate"]
            and left_metrics["false_rejection_rate"] <= right_metrics["false_rejection_rate"]
            and left_metrics["wrong_payout_value"] <= right_metrics["wrong_payout_value"])
    strict = (left_policy.q < right_policy.q
              or left_metrics["cash_review_cost"] < right_metrics["cash_review_cost"]
              or left_metrics["accuracy"] > right_metrics["accuracy"]
              or left_metrics["false_approval_rate"] < right_metrics["false_approval_rate"]
              or left_metrics["false_rejection_rate"] < right_metrics["false_rejection_rate"]
              or left_metrics["wrong_payout_value"] < right_metrics["wrong_payout_value"])
    return weak and strict


def compare_robust_frontiers(result):
    audit = [record for record in result["mechanisms"]["audit_only"]["policies"]
             if record["worst_equilibrium_metrics"].get("robust")]
    hybrid = [record for record in result["mechanisms"]["hybrid"]["policies"]
              if record["worst_equilibrium_metrics"].get("robust")]
    audit_frontier = [record for record in audit
                      if not any(_dominates(other, record) for other in audit if other is not record)]
    witness_count = 0
    first_witness = None
    for hybrid_record in hybrid:
        for audit_record in audit_frontier:
            if _dominates(hybrid_record, audit_record):
                witness_count += 1
                if first_witness is None:
                    first_witness = {"hybrid": hybrid_record["policy"], "audit_only": audit_record["policy"]}
    unmatched_hybrid = [record for record in hybrid
                        if not any(_dominates(audit_record, record) for audit_record in audit)]
    return {
        "audit_only_robust_count": len(audit),
        "audit_only_pareto_frontier_count": len(audit_frontier),
        "hybrid_robust_count": len(hybrid),
        "audit_only_min_worst_cash": min((record["worst_equilibrium_metrics"]["cash_review_cost"] for record in audit), default=None),
        "hybrid_min_worst_cash": min((record["worst_equilibrium_metrics"]["cash_review_cost"] for record in hybrid), default=None),
        "audit_only_min_q": min((record["policy"].q for record in audit), default=None),
        "hybrid_min_q": min((record["policy"].q for record in hybrid), default=None),
        "hybrid_strict_dominance_witness_count": witness_count,
        "hybrid_strict_dominance_witness": first_witness,
        "hybrid_unmatched_tradeoff_count": len(unmatched_hybrid),
        "hybrid_has_incremental_advantage": witness_count > 0,
        "comparison_rule": "Hybrid must strictly dominate an Audit-only Pareto-frontier robust policy on q, worst cash, worst accuracy and all worst error metrics. A lower-q/higher-cash tradeoff is not an incremental advantage.",
    }


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, Policy):
        return _jsonable({"lambda_peer": value.lambda_peer, "mu": value.mu, "q": value.q, "budget": value.budget})
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def run_screening():
    fixture_results = [screen_fixture(fixture) for fixture in (f41_01(), f41_02(), v3_het())]
    comparisons = [{"fixture": result["fixture"], **compare_robust_frontiers(result)}
                   for result in fixture_results]
    advantage = any(item["hybrid_has_incremental_advantage"] for item in comparisons)
    conclusion = ("hybrid_has_incremental_advantage_on_declared_grid"
                  if advantage else "negative_no_incremental_hybrid_advantage_on_declared_grid")
    return {
        "status": "passed",
        "conclusion": conclusion,
        "fixtures": fixture_results,
        "frontier_comparison": comparisons,
        "incremental_advantage_definition": "strict_robust_frontier_dominance",
        "scope": "finite_declared_grid_only",
        "policy_search": "finite_grid_exhaustive_within_declared_grid",
        "equilibrium_selection": "not_modeled",
        "limits": ["synthetic fixtures", "pure stationary strategies only", "no global optimality",
                   "no mixed or coalition equilibrium", "no production CLI/API/UI"],
    }


def _latest_freeze_manifest():
    candidates = sorted((ROOT / "spec_history").glob("v4.1-screening-implementation-start-*/manifest.json"))
    _require(candidates, "V4.1 screening freeze is missing")
    return candidates[-1]


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"event_type": "v4.1_minimal_screening_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "implementation_start": False, "preregistered": False, "inputs": []}
    sources = [Path("CEAV_M1_V4_CONDITIONAL_SPEC.md"), Path("CEAV_M1_V4_1_FEASIBILITY.md"),
               Path("CEAV_M1_V4_1_SCREENING_SPEC.md"), Path("CEAV_M1_V3_ANCHOR_SPEC.md"),
               Path("configs/v3/heterogeneous_anchor.json"), Path("references/V4_CONDITIONAL_SCORING_SOURCES.md"),
               Path("verification/oracle_v4_1_screening.py"),
               Path("verification/mutation_probes_v4_1.py"),
               Path("verification/v4_1_screening.py"), Path("tests/test_v4_1_screening.py"),
               _latest_freeze_manifest().relative_to(ROOT)]
    for source in sources:
        snapshot = Path("inputs") / source
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        manifest["inputs"].append({"source": source.as_posix(), "snapshot": snapshot.as_posix(),
                                   "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        result = run_screening()
        (out / "screening.json").write_text(json.dumps(_jsonable(result), indent=2) + "\n", encoding="utf-8")
        lines = ["# CEAV-M1 V4.1 — Minimal screening", "",
                 f"Conclusion on the declared finite grid: `{result['conclusion']}`.", "",
                 "Audit-only was enumerated over all valid `M x Q` policies; Conditional-only and Hybrid were enumerated over all valid policies under `B=6`.", "",
                 "Worst-equilibrium metrics retain all pure equilibria. Equilibrium selection is not modeled. This artifact does not claim global optimality, production readiness or quality outside the pinned fixtures/grid.", ""]
        for fixture in result["fixtures"]:
            lines += [f"## {fixture['fixture']}", "",
                      "| Mechanism | Policies | Pure-eq policies | Robust policies | Selected robust policy |",
                      "| --- | ---: | ---: | ---: | --- |"]
            for mechanism in ("audit_only", "conditional_only", "hybrid"):
                group = fixture["mechanisms"][mechanism]
                lines.append(f"| {mechanism} | {group['policy_count']} | {group['pure_equilibrium_policy_count']} | {group['robust_policy_count']} | {group['selected_robust_policy']} |")
            lines.append("")
        lines += ["## Robust frontier comparison", "",
                  "Hybrid counts as incrementally advantageous only when it strictly dominates an Audit-only Pareto-frontier robust policy on declared audit probability, worst-equilibrium cash, worst-equilibrium accuracy and all worst-equilibrium error metrics. A lower-q/higher-cash tradeoff is not an incremental advantage.", "",
                  "| Fixture | Audit frontier | Audit min worst cash | Hybrid min worst cash | Audit min q | Hybrid min q | Unmatched tradeoffs | Strict dominance |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
        for comparison in result["frontier_comparison"]:
            lines.append(f"| {comparison['fixture']} | {comparison['audit_only_pareto_frontier_count']} | {comparison['audit_only_min_worst_cash']} | {comparison['hybrid_min_worst_cash']} | {comparison['audit_only_min_q']} | {comparison['hybrid_min_q']} | {comparison['hybrid_unmatched_tradeoff_count']} | {comparison['hybrid_has_incremental_advantage']} |")
        lines += ["", f"Incremental conclusion: `{result['conclusion']}`.", ""]
        (out / "report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out / name).read_bytes()).hexdigest()
                               for name in ("screening.json", "report.md")}
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
    record = write_run(args.out)
    print(json.dumps({"status": record["status"], "conclusion": record["conclusion"], "out": str(args.out)}))
