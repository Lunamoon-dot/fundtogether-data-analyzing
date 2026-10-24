"""Four targeted negative V6 certificates; no general equilibrium search."""

import argparse
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
from verification import feasibility_v6 as checker
from verification import oracle_v6_feasibility as oracle


PRIMARY = Path("results/v6-rave-phase1-20261024T021148403371Z")
WITNESSES = (
    ("F51-01", "Q1-zero", (("L0", "L0", "L1"), ("L1", "L1", "L0"))),
    ("F51-01", "Q2-z1", (("L1",) * 3,) * 2),
    ("F51-02", "Q1-zero", (("L0", "L1", "H01"),) * 2),
    ("F51-02", "Q2-z0", (("H01",) * 3, ("L0",) * 3)),
)


def stop_decision(certified_failures):
    return "NO-GO_declared_phase1_candidates" if len(certified_failures) == 4 and all(certified_failures) else "UNRESOLVED"


def run_certificate():
    study = checker.load_study()
    primary = json.loads((ROOT/PRIMARY/"certificate.json").read_text())
    candidate_ids = {(fx["fixture"]["name"], c["allocation"]["name"])
                     for fx in primary["fixtures"] for c in fx["comparisons"] if c["meaningful_candidate"]}
    if candidate_ids != {(f, a) for f, a, _ in WITNESSES}:
        raise ValueError("targeted witnesses do not cover the original candidate set")
    records = []
    for name, allocation_name, profile in WITNESSES:
        fx = next(f for f in study["fixtures"] if f["name"] == name)
        allocation = next(a for a in study["allocations"] if a["name"] == allocation_name)
        table = checker.decision_table(fx, (study["c_fa"], study["c_fr"]))
        independent_table = oracle.decision_table(fx, (study["c_fa"], study["c_fr"]))
        if table != independent_table:
            raise AssertionError("posterior/decision mismatch")
        policy = dict({k: study[k] for k in ("mu", "budget", "kappa", "operating_cost",
            "payout_value", "exposure_limit", "c_fa", "c_fr")}, f=fx["f"],
            audit=checker.audit_table(allocation["kind"], allocation["params"]))
        metrics = checker.evaluate(fx, policy, table, profile)
        if metrics != oracle.evaluate(fx, policy, independent_table, profile):
            raise AssertionError("independent metric mismatch")
        response = checker.deviations(fx, policy, table, profile)
        count = 0
        maximum = F(0)
        for z in (0, 1):
            for i in range(3):
                values = {}
                for action in ("L0", "L1", "H00", "H01", "H10", "H11"):
                    changed = [list(branch) for branch in profile]
                    changed[z][i] = action
                    value = oracle.evaluate(fx, policy, independent_table, changed)["utility_by_z"][z][i]
                    values[action] = value
                    recorded = next(o for o in response["by_z"][z][i]["actions"] if o["action"] == action)
                    if recorded["utility"] != value:
                        raise AssertionError("independent deviation mismatch")
                    count += 1
                best = max(values.values())
                maximum = max(maximum, best-metrics["utility_by_z"][z][i])
                if set(response["by_z"][z][i]["best_actions"]) != {a for a, v in values.items() if v == best}:
                    raise AssertionError("best response/tie mismatch")
        if maximum != response["max_regret"]:
            raise AssertionError("max regret mismatch")
        gates = checker.gates(metrics, metrics["reward_cap"], study["exposure_limit"])
        records.append({"fixture": name, "allocation": allocation_name, "profile": profile,
            "b": (F(0),)*3, "metrics": metrics, "max_regret": maximum,
            "best_responses": response, "independent_deviation_checks": count, "gates": gates,
            "finding": "strategic_failure" if maximum == 0 and not gates["all_pass"] else "unresolved"})
    decision = stop_decision([r["finding"] == "strategic_failure" for r in records])
    closed = decision == "NO-GO_declared_phase1_candidates"
    return {"status": "verified" if closed else "unresolved", "scope": "post_discovery_four_targeted_counterexamples",
        "preregistered_before_discovery": False, "game_policy_gates_changed": False,
        "decision": decision,
        "Gate_B": "positive_exogenous_only", "Gate_C": "universal_requirement_refuted_by_witnesses" if closed else "not_certified",
        "Gate_D": "no_robust_improving_candidate_in_declared_discovery_set" if closed else "not_certified",
        "equilibrium_count": "not_computed", "phase2_executed": False,
        "witnesses": records, "supersedes_recommendation_only": str(PRIMARY/"certificate.json")}


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "running", "inputs": []}
    try:
        freezes = list((ROOT/"spec_history").glob("v6.0-rave-negative-witness-check-*/manifest.json"))
        if len(freezes) != 1:
            raise ValueError("one negative-witness declaration required")
        freeze = freezes[0]
        frozen = json.loads(freeze.read_text())
        for row in frozen["inputs"]:
            for path in (ROOT/row["source"], freeze.parent/row["snapshot"]):
                if sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                    raise ValueError("negative-witness frozen input changed")
        primary_manifest = json.loads((ROOT/PRIMARY/"manifest.json").read_text())
        if sha256((ROOT/PRIMARY/"certificate.json").read_bytes()).hexdigest() != primary_manifest["outputs"]["certificate.json"]:
            raise ValueError("primary certificate identity mismatch")
        sources = [row["source"] for row in frozen["inputs"]] + [
            (PRIMARY/"certificate.json").as_posix(), "verification/v6_phase1_stop.py",
            freeze.relative_to(ROOT).as_posix()]
        sources += [(freeze.parent/row["snapshot"]).relative_to(ROOT).as_posix() for row in frozen["inputs"]]
        for source in sources:
            dst = out/"inputs"/source
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/source, dst)
            manifest["inputs"].append({"source": source, "snapshot": "inputs/"+source,
                                       "sha256": sha256(dst.read_bytes()).hexdigest()})
        result = run_certificate()
        (out/"certificate.json").write_text(json.dumps(checker._jsonable(result), indent=2)+"\n", encoding="utf-8")
        closed = result["decision"] == "NO-GO_declared_phase1_candidates"
        lines = ["# V6 Phase 1 — final negative certificates", "",
                 f"**{result['decision']}**", "",
                 "Four exogenous Gate-B winners each have a certified bad pure equilibrium." if closed
                 else "UNRESOLVED: targeted evidence is insufficient to close every candidate.",
                 "These are post-discovery targeted counterexamples; no exhaustive search ran.", "",
                 "| Fixture | Policy | Maximum regret | Exposure | FA | FR | Cash | Failure |",
                 "|---|---|---:|---:|---:|---:|---:|---|"]
        for row in result["witnesses"]:
            m = row["metrics"]
            fail = ", ".join(k for k, passed in row["gates"].items() if not passed and k != "all_pass")
            lines.append(f"| {row['fixture']} | {row['allocation']} | {row['max_regret']} | {m['audit_exposure']} | {m['final_fa']} | {m['final_fr']} | {m['cash_review_cost']} | {fail} |")
        lines += ["", "Each witness checks 36 unilateral actions with frozen peers/policy and the independent potential-state oracle. One bad NE refutes an all-NE requirement; it does not determine the total equilibrium count or worst metric over the whole class.", "",
                  "The primary GO_candidate_discovery_only remains a truthful decision-feasibility result. "
                  + ("This negative certificate supersedes its recommendation for further screening. " if closed else "No final stop decision is certified. ")
                  + "No game/policy/gate was tuned, no historical artifact was changed, and no general RAVE impossibility is claimed.", ""]
        (out/"report.md").write_text("\n".join(lines), encoding="utf-8")
        manifest["status"] = "succeeded"
        manifest["outputs"] = {n: sha256((out/n).read_bytes()).hexdigest() for n in ("certificate.json", "report.md")}
        return result
    except BaseException as error:
        manifest.update(status="failed", error=str(error))
        raise
    finally:
        (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"decision": result["decision"], "witnesses": len(result["witnesses"])}))
