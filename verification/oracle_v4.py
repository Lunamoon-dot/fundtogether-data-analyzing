"""Fixed-fixture V4 reference checks; no production imports or general equilibrium search."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"L0": (0, 0), "L1": (1, 1), "H00": (0, 0),
           "H01": (0, 1), "H10": (1, 0), "H11": (1, 1)}


def _require(condition, message):
    """Keep evidence checks active even when Python is invoked with -O."""
    if not condition:
        raise AssertionError(message)


def realized_score(public, reports, judge, task):
    others = [u for u, z in enumerate(public) if z == public[task] and u != task]
    if not others:
        raise ValueError("insufficient_stratum_support")
    own = reports[judge][task]
    return sum((F(own == reports[j][task])
                - sum(F(own == reports[j][u]) for u in others) / len(others)) / 2
               for j in range(3) if j != judge)


def _rows(z):
    """F01 likelihood enumeration: pi=1/2, public=7/10, private=4/5."""
    rows = []
    for y, *xs in product((0, 1), repeat=4):
        weight = F(7, 10) if y == z else F(3, 10)
        for x in xs:
            weight *= F(4, 5) if x == y else F(1, 5)
        rows.append((weight, y, xs))
    _require(sum(weight for weight, _, _ in rows) == 1, "F01 likelihood mass must equal one")
    return rows


def branch(z, profile, lam=F(1), cost=F(1, 20)):
    """Integrate one F01 stratum using independent task pairs, not a covariance shortcut."""
    rows = [(weight, y, [ACTIONS[action][x] for action, x in zip(profile, xs)])
            for weight, y, xs in _rows(z)]
    scores = []
    for i in range(3):
        same = sum(weight * F(sum(r[i] == r[j] for j in range(3) if j != i), 2)
                   for weight, _, r in rows)
        cross = sum(weight * other_weight * F(sum(r[i] == other_r[j] for j in range(3) if j != i), 2)
                    for weight, _, r in rows for other_weight, _, other_r in rows)
        scores.append(same - cross)
    correct = sum(weight for weight, y, r in rows if (sum(r) >= 2) == y)
    y0 = sum(weight for weight, y, _ in rows if y == 0)
    y1 = 1 - y0
    return {"scores": scores,
            "utilities": [lam * (1 + scores[i]) - (cost if profile[i].startswith("H") else 0)
                          for i in range(3)],
            "accuracy": correct,
            "false_approval_rate": sum(w for w, y, r in rows if y == 0 and sum(r) >= 2) / y0,
            "false_rejection_rate": sum(w for w, y, r in rows if y == 1 and sum(r) < 2) / y1}


def run_checks():
    statewise_checks = 0
    # Every deterministic Low map, both balanced/imbalanced batches, arbitrary focal reports.
    for public in ((0, 0, 1, 1), (0, 0, 1, 1, 1)):
        for low_maps in product(tuple(product((0, 1), repeat=2)), repeat=3):
            for i in range(3):
                for own_reports in product((0, 1), repeat=len(public)):
                    reports = [tuple(g[z] for z in public) for g in low_maps]
                    reports[i] = own_reports
                    for task in range(len(public)):
                        _require(realized_score(public, reports, i, task) == 0,
                                 (public, low_maps, i, own_reports, task))
                        statewise_checks += 1

    certificates = []
    fixtures = {"all_copy_Z": None, "all_H01": "H01", "all_H10": "H10",
                "all_PASS": "L1", "all_FAIL": "L0"}
    metrics = {}
    for name, action in fixtures.items():
        metrics[name] = []
        for z in (0, 1):
            profile = (action or ("L1" if z else "L0"),) * 3
            candidate = branch(z, profile)
            metrics[name].append(candidate)
            for i in range(3):
                values = {}
                for deviation in ACTIONS:
                    changed = list(profile)
                    changed[i] = deviation
                    values[deviation] = branch(z, changed)["utilities"][i]
                gain = max(values.values()) - candidate["utilities"][i]
                _require(gain == 0, (name, z, i, values))
                certificates.append({"fixture": name, "z": z, "judge": "ABC"[i],
                                     "candidate_action": profile[i], "candidate_utility": candidate["utilities"][i],
                                     "deviation_utilities": values, "max_deviation_gain": gain,
                                     "best_actions": [key for key, value in values.items() if value == max(values.values())]})
    for z in (0, 1):
        high, flipped = metrics["all_H01"][z], metrics["all_H10"][z]
        _require(high["scores"] == [F(189, 1250)] * 3, high["scores"])
        _require(high["utilities"] == [F(2753, 2500)] * 3, high["utilities"])
        _require(high["accuracy"] == F(112, 125), high["accuracy"])
        _require(high["false_approval_rate"] == high["false_rejection_rate"] == F(13, 125),
                 (high["false_approval_rate"], high["false_rejection_rate"]))
        _require(high["scores"] == flipped["scores"], (high["scores"], flipped["scores"]))
        _require(flipped["accuracy"] == 1 - high["accuracy"],
                 (flipped["accuracy"], high["accuracy"]))

    return {"status": "passed", "finding": "all_low_persists_without_audit",
            "scope": "finite_statewise_probes_and_F01_six_action_certificates",
            "general_equilibrium_search": False, "engine_certificate": "not_run",
            "proposition_scope": "Universal statement follows from spec proof; finite probes do not prove all parameters.",
            "parameters": {"pi": F(1, 2), "public_quality": F(7, 10), "private_quality": F(4, 5),
                           "cost": F(1, 20), "f": F(0), "lambda_peer": F(1), "reward_budget": F(6)},
            "statewise_checks": statewise_checks, "certificates": certificates, "fixture_metrics": metrics,
            "worst_false_approval_rate": F(1), "worst_false_rejection_rate": F(1),
            "worst_metric_scope": "Global bounds attained by all_PASS/all_FAIL; no general search performed.",
            "limits": ["fixed synthetic F01", "no production engine", "no audit study", "no equilibrium selection guarantee"]}


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"event_type": "independent_reference_oracle_run", "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "implementation_start": False, "preregistered": False, "inputs": []}
    names = ("CEAV_M1_V4_CONDITIONAL_SPEC.md", "CEAV_M1_V4_1_FEASIBILITY.md",
             "references/V4_CONDITIONAL_SCORING_SOURCES.md", "verification/oracle_v4.py",
             "tests/test_v4_research_oracle.py")
    for name in names:
        snapshot = Path("inputs") / name
        target = out / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        manifest["inputs"].append({"source": name, "snapshot": snapshot.as_posix(),
                                   "sha256": sha256(target.read_bytes()).hexdigest()})
    try:
        result = run_checks()
        (out / "oracle.json").write_text(json.dumps(_jsonable(result), indent=2) + "\n", encoding="utf-8")
        (out / "report.md").write_text(
            "# V4.0 independent research closeout\n\n"
            "Finding: `all_low_persists_without_audit`.\n\n"
            f"Statewise finite checks: {result['statewise_checks']}. "
            f"F01 candidate/Judge/branch certificates: {len(result['certificates'])}.\n\n"
            "All-PASS/all-FAIL attain worst FA=1 and FR=1. "
            "H01 and inverted H10 retain equal reward and different decision quality.\n\n"
            "Oracle success verifies these reference checks. It does not certify a full engine, "
            "all equilibria, audit advantage, or production behavior.\n", encoding="utf-8")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {name: sha256((out / name).read_bytes()).hexdigest()
                               for name in ("oracle.json", "report.md")}
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
    print(json.dumps({"finding": record["finding"], "statewise_checks": record["statewise_checks"],
                      "certificates": len(record["certificates"]), "out": str(args.out)}))
