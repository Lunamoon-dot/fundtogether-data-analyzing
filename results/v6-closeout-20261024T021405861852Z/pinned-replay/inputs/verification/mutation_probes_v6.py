"""V6 direct source probes in temporary copies; production bytes stay intact."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TEST = "tests.test_v6_feasibility.V6FeasibilityTests."
PROBES = (
    ("threshold", "threshold = c_fa / (c_fa + c_fr)", "threshold = F(1, 2)",
     "test_T03_majority_noisy_posterior_and_voi"),
    ("future_T_selection", 'q = policy["audit"][z, reports]',
     'q = policy["audit"][z, reports] * _channel(fixture["audit"], 1, y)',
     "test_T05_exposure_uses_realized_reports"),
    ("recalibrate_on_deviation", 'fixed = decisions[z, reports]',
     'fixed = (decision_table(fixture, (policy["c_fa"], policy["c_fr"]), "copyZ") if profile != HIGH else decisions)[z, reports]',
     "tests.test_v6_regressions.V6RegressionTests.test_R01_frozen_calibration_with_external_b_and_deviation"),
    ("peer_adapts", "changed[z][i] = action", "changed[z] = [action]*3",
     "test_T04_policy_and_peers_frozen_under_deviation"),
    ("majority", "initial = int(sum(reports) >= 2)", "initial = int(sum(reports) > 2)",
     "test_T03_majority_noisy_posterior_and_voi"),
    ("frozen_exposure_distribution", "mass = _report_mass(fixture, z, reports, profile[z], y)",
     "mass = _report_mass(fixture, z, reports, HIGH[z], y)",
     "test_T05_exposure_uses_realized_reports"),
    ("FA_denominator", '"final_fa": fa/(1-fixture["pi"])', '"final_fa": fa',
     "test_T08_false_approval_rejection_denominators"),
    ("audit_cost_tripled", 'audit_cost = policy["kappa"]*sum(exposure)',
     'audit_cost = 3*policy["kappa"]*sum(exposure)',
     "test_T09_cash_claim_cost_reserve_and_effort"),
    ("reserve_discounted", 'cap = 3*policy["f"] + 3*policy["mu"]',
     'cap = (3*policy["f"] + 3*policy["mu"])*sum(policy["audit"].values())/16',
     "test_T09_cash_claim_cost_reserve_and_effort"),
    ("effort_cost_omitted", '(fixture["private"][i][2] if effort[z][i] == "H" else F(0))',
     'F(0)', "test_T09_cash_claim_cost_reserve_and_effort"),
    ("ties_dropped", 'if o["utility"] == best', 'if o["utility"] > best',
     "test_T10_exact_ties_and_six_deviations"),
    ("target_replaced_by_batch", '"cash_review_cost": reward+audit_cost+policy["operating_cost"]',
     '"cash_review_cost": sum(payouts[z]+policy["kappa"]*exposure_by_z[z]+policy["operating_cost"] for z in (0,1))/2',
     "test_T12_target_and_batch_weights_separate"),
    ("deviation_omitted", "for action in ACTIONS:", 'for action in ACTIONS[:-1]:',
     "test_T10_exact_ties_and_six_deviations"),
    ("false_stop_GO", 'return "GO_candidate_discovery_only" if meaningful_candidate else "NO-GO"',
     'return "GO_candidate_discovery_only"',
     "test_T11_stop_gates_witnesses_and_non_exhaustive_scope"),
    ("decision_tie_dropped", '"g0": int(posterior >= threshold)',
     '"g0": int(posterior > threshold)',
     "tests.test_v6_regressions.V6RegressionTests.test_R02_bayes_tie_releases"),
)


def run_probes():
    source = (ROOT/"verification/feasibility_v6.py").read_text(encoding="utf-8")
    records = []
    with tempfile.TemporaryDirectory(prefix="ceav-v6-probes-") as tmp:
        for name, old, new, test in PROBES:
            test_id = test if "." in test else TEST+test
            if source.count(old) != 1:
                raise ValueError(f"mutation target {name} must occur exactly once")
            mutated = source.replace(old, new, 1)
            path = Path(tmp)/(name+".py")
            path.write_text(mutated, encoding="utf-8")
            harness = "\n".join([
                "import importlib.util,json,pathlib,sys,unittest",
                f"sys.path.insert(0,{str(ROOT)!r})",
                "import verification",
                f"spec=importlib.util.spec_from_file_location('verification.feasibility_v6',{str(path)!r})",
                "module=importlib.util.module_from_spec(spec)",
                "sys.modules[spec.name]=module; spec.loader.exec_module(module)",
                f"module.ROOT=pathlib.Path({str(ROOT)!r})",
                f"suite=unittest.defaultTestLoader.loadTestsFromName({test_id!r})",
                "result=unittest.TestResult(); suite.run(result)",
                "print(json.dumps({'tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'skipped':len(result.skipped),'details':[text for _,text in result.failures+result.errors]}))",
            ])
            completed = subprocess.run([sys.executable, "-c", harness], capture_output=True, text=True)
            if completed.returncode:
                raise RuntimeError(f"probe harness {name}: {completed.stderr}")
            record = json.loads(completed.stdout)
            record.update(name=name, test_id=test_id, source_sha256=sha256(mutated.encode()).hexdigest())
            record["status"] = "killed_by_assertion" if (record["tests_run"] > 0
                and record["errors"] == 0 and record["failures"] > 0 and record["skipped"] == 0) else "not_killed"
            records.append(record)
    return records


def write_run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    result = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "probes": run_probes()}
    result["status"] = "passed" if all(r["status"] == "killed_by_assertion" for r in result["probes"]) else "failed"
    (out/"mutations.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    (out/"manifest.json").write_text(json.dumps({
        "created_at_utc": result["created_at_utc"], "status": result["status"],
        "source_hashes": {name: sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            "verification/feasibility_v6.py", "verification/mutation_probes_v6.py",
            "tests/test_v6_feasibility.py", "tests/test_v6_mutations.py")},
        "outputs": {"mutations.json": sha256((out/"mutations.json").read_bytes()).hexdigest()},
    }, indent=2)+"\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_run(args.out)
    print(json.dumps({"status": result["status"], "count": len(result["probes"]), "out": str(args.out)}))
    sys.exit(0 if result["status"] == "passed" else 1)
