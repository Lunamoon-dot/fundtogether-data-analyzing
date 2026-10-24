"""Test-only mutants; production and frozen artifacts are never edited."""

from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace

from verification import dual_boundary as subject
from verification import dual_boundary_oracle as oracle
from verification.dual_boundary_audit import audit


def run_probes():
    results = []
    baseline = subject.build_table("selective")
    for mutation in ("union_payment","double_audit"):
        detected = baseline[0,("H01",)*3] != oracle.evaluate(0,("H01",)*3,"selective",mutation)
        subject.require(detected,mutation+" escaped")
        results.append({"mutation":mutation,"detected":detected,"detector":"DB03 separate-coin identity"})
    # With all L1, reports carry no Y information; recalibrating at that profile
    # would replace the frozen z=0 table by g0=0,g1=(0,1).
    original_calibration = oracle.calibration
    def recalibrated():
        table = original_calibration()
        table[0,(1,1,1)] = (0,(0,1))
        return table
    try:
        oracle.calibration = recalibrated
        detected = oracle.evaluate(0,("L1",)*3,"selective") != baseline[0,("L1",)*3]
    finally:
        oracle.calibration = original_calibration
    subject.require(detected,"recalibration escaped")
    results.append({"mutation":"recalibrate_actual_reports","detected":detected,"detector":"DB02 frozen calibration"})
    path = Path(subject.__file__)
    source = path.read_text(encoding="utf-8")
    replacements = {
        "discard_exact_ties":("b >= lo", "b > lo"),
        "omit_low_profiles":("PROFILES = tuple(product(ACTIONS, repeat=3))", "PROFILES = tuple(product(ACTIONS[2:], repeat=3))"),
        "omit_asymmetric_profiles":("PROFILES = tuple(product(ACTIONS, repeat=3))", "PROFILES = tuple((a,a,a) for a in ACTIONS)"),
        "reverse_external_slope":("vector[i]*(base[\"release\"]-dev[\"release\"])", "vector[i]*(dev[\"release\"]-base[\"release\"] )"),
        "change_peers_on_deviation":("changed[i] = action\n        dev = table[z,tuple(changed)]", "changed = [action]*3\n        dev = table[z,tuple(changed)]"),
        "report_minimum_as_worst":("value = max(e[\"metrics\"][key] for e in active)", "value = min(e[\"metrics\"][key] for e in active)"),
    }
    for name,(old,new) in replacements.items():
        subject.require(old in source,"mutation anchor missing: "+name)
        namespace = {"__file__":str(path),"__name__":"test_only_mutant"}
        # In-memory test copy; compiling this string cannot alter source bytes.
        exec(compile(source.replace(old,new),"<test-only-"+name+">","exec"),namespace)
        mutant = SimpleNamespace(**namespace)
        try:
            audit(mutant)
        except (AssertionError, KeyError) as error:
            results.append({"mutation":name,"detected":True,"detector":str(error)})
        else:
            raise AssertionError(name+" escaped independent audit")
    return results


if __name__ == "__main__":
    import json
    print(json.dumps(run_probes(),indent=2))
