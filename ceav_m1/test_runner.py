"""Allowlisted suites with real unittest discovery and explicit missing coverage."""

from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import re
import runpy
import time
import unittest

from . import V2_MODEL_VERSION, V3_MODEL_VERSION
from .output import ROOT, LIMITATIONS, finish_run, new_run, write_json

SUITES = ("reference", "goldens", "v2", "calibration", "incentives", "v3", "robustness", "all", "selected")


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.started = {}

    def startTest(self, test):
        self.started[test.id()] = time.perf_counter()
        super().startTest(test)

    def record(self, test, status, detail=None):
        ids = re.findall(r"_(?:(V2|CAL|INC|V3|ROB)_)?T(\d{2})(?:_|$)", test.id())
        self.records.append({"test_id": (((ids[0][0] + "-") if ids[0][0] else "") + "T" + ids[0][1]) if ids else None, "unittest_id": test.id(),
                             "status": status, "duration_seconds": time.perf_counter() - self.started[test.id()],
                             "assertion_or_error": detail, "evidence": getattr(test, "evidence", None)})

    def addSuccess(self, test):
        self.record(test, "pass")
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.record(test, "fail", self._exc_info_to_string(err, test))
        super().addFailure(test, err)

    def addError(self, test, err):
        self.record(test, "error", self._exc_info_to_string(err, test))
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.record(test, "skipped", reason)
        super().addSkip(test, reason)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.record(test, "fail" if issubclass(err[0], test.failureException) else "error", self._exc_info_to_string(err, test))
        super().addSubTest(test, subtest, err)

    def addExpectedFailure(self, test, err):
        self.record(test, "skipped", "Expected failure: " + self._exc_info_to_string(err, test))
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.record(test, "error", "Unexpected success in expected-failure test")
        super().addUnexpectedSuccess(test)


def discover():
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    tests = list(flatten(suite))
    if loader.errors or not tests:
        raise ValueError("Test discovery failed or discovered zero tests: " + "\n".join(loader.errors))
    return tests


def run_suite(selector, selected=None, injected_fixture=False):
    if selector not in SUITES:
        raise ValueError("Unknown test suite")
    if injected_fixture and selector != "selected":
        raise ValueError("Failure fixture is only available in selected suite")
    log = io.StringIO()
    records = []
    reference_results = None
    started = time.perf_counter()
    if selector == "reference":
        try:
            with redirect_stdout(log), redirect_stderr(log):
                checker = runpy.run_path(str(ROOT / "verification/verify_reference.py"))
                reference_results = checker["serializable"](checker["verify"]())
                print("Reference checker assertions completed; named profiles only.")
            records.append({"test_id": "REF", "unittest_id": None, "status": "pass", "duration_seconds": time.perf_counter() - started})
        except Exception:
            import traceback
            traceback.print_exc(file=log)
            records.append({"test_id": "REF", "status": "error", "assertion_or_error": log.getvalue()})
    else:
        tests = discover()
        registered = json.loads((ROOT / "tests/registry.json").read_text(encoding="utf-8"))
        registered_v2 = json.loads((ROOT / "tests/registry_v2.json").read_text(encoding="utf-8"))
        registered_calibration = json.loads((ROOT / "tests/registry_calibration.json").read_text(encoding="utf-8"))
        registered_incentives = json.loads((ROOT / "tests/registry_incentives.json").read_text(encoding="utf-8"))
        registered_v3 = json.loads((ROOT / "tests/registry_v3.json").read_text(encoding="utf-8"))
        registered_robustness = json.loads((ROOT / "tests/registry_robustness.json").read_text(encoding="utf-8"))
        if set(registered["tests"]) != {f"T{i:02}" for i in range(1, 33)}:
            raise ValueError("Test registry must contain T01-T32")
        if set(registered_v2["tests"]) != {f"V2-T{i:02}" for i in range(1, 16)}:
            raise ValueError("V2 test registry must contain V2-T01 through V2-T15")
        if set(registered_calibration["tests"]) != {f"CAL-T{i:02}" for i in range(1, 9)}:
            raise ValueError("Calibration test registry must contain CAL-T01 through CAL-T08")
        if set(registered_incentives["tests"]) != {f"INC-T{i:02}" for i in range(1, 9)}:
            raise ValueError("Incentive diagnostics registry must contain INC-T01 through INC-T08")
        if set(registered_v3["tests"]) != {f"V3-T{i:02}" for i in range(1, 13)}:
            raise ValueError("V3 test registry must contain V3-T01 through V3-T12")
        if set(registered_robustness["tests"]) != {f"ROB-T{i:02}" for i in range(1, 11)}:
            raise ValueError("Robustness test registry must contain ROB-T01 through ROB-T10")
        available = {test.id(): test for test in tests}
        v1_ids = [f"T{i:02}" for i in range(1, 33)]
        v2_ids = [f"V2-T{i:02}" for i in range(1, 16)]
        calibration_ids = [f"CAL-T{i:02}" for i in range(1, 9)]
        incentive_ids = [f"INC-T{i:02}" for i in range(1, 9)]
        v3_ids = [f"V3-T{i:02}" for i in range(1, 13)]
        robustness_ids = [f"ROB-T{i:02}" for i in range(1, 11)]
        wanted = (v1_ids + v2_ids + calibration_ids + incentive_ids + v3_ids + robustness_ids if selector == "all" else v2_ids if selector == "v2" else calibration_ids if selector == "calibration" else incentive_ids if selector == "incentives" else v3_ids if selector == "v3" else robustness_ids if selector == "robustness" else
                  ["T08", "T09", "T10", "T11"] if selector == "goldens" else list(dict.fromkeys(selected or [])))
        if not wanted and not injected_fixture:
            raise ValueError("No selected test IDs; zero tests cannot pass")
        if any(not re.fullmatch(r"(?:T(?:0[1-9]|[12][0-9]|3[0-2])|V2-T(?:0[1-9]|1[0-5])|CAL-T0[1-8]|INC-T0[1-8]|V3-T(?:0[1-9]|1[0-2])|ROB-T(?:0[1-9]|10))", value) for value in wanted):
            raise ValueError("Only registered V1, V2, CAL, INC, V3 or ROB test IDs are accepted")
        chosen = []
        for test_id in wanted:
            registry = registered_robustness if test_id.startswith("ROB-") else registered_v3 if test_id.startswith("V3-") else registered_incentives if test_id.startswith("INC-") else registered_calibration if test_id.startswith("CAL-") else registered_v2 if test_id.startswith("V2-") else registered
            ids = registry["tests"][test_id]["unittest_ids"]
            if not ids or any(identity not in available for identity in ids):
                records.append({"test_id": test_id, "status": "not_run", "assertion_or_error": "Registered tests missing from real discovery"})
            chosen.extend(available[identity] for identity in ids if identity in available)
        if injected_fixture:
            from tests.failure_fixture import IntentionalFailure
            chosen.append(IntentionalFailure("test_explicit_failure_fixture"))
        if chosen:
            runner = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordedResult)
            with redirect_stdout(log), redirect_stderr(log):
                result = runner.run(unittest.TestSuite(chosen))
            records.extend(result.records)
            executed = result.testsRun
        else:
            executed = 0
        if executed == 0:
            records.append({"test_id": "RUNNER", "status": "error", "assertion_or_error": "Zero tests executed"})
    counts = dict(Counter(r["status"] for r in records))
    passed = bool(records) and counts.get("pass", 0) == len(records)
    return {"suite": selector, "selected_ids": selected or [], "failure_fixture": injected_fixture,
            "status": "passed" if passed else "not_passed", "records": records,
            "counts": {key: counts.get(key, 0) for key in ("pass", "fail", "error", "skipped", "not_run")},
            "duration_seconds": time.perf_counter() - started,
            "browser_acceptance_executed": False, "reference_results": reference_results}, log.getvalue()


def write_test_run(out, selector, selected=None, injected_fixture=False, argv=None, defer_publication=False):
    out = Path(out)
    model_version = (V3_MODEL_VERSION if selector in ("v3", "robustness", "all") or any(value.startswith(("V3-", "ROB-")) for value in (selected or [])) else
                     V2_MODEL_VERSION if selector in ("v2", "calibration", "incentives") or any(value.startswith(("V2-", "CAL-", "INC-")) for value in (selected or [])) else None)
    manifest = new_run(out, "tests", request={"suite": selector, "test_ids": selected or [], "failure_fixture": injected_fixture}, argv=argv, publication_owner="local_server" if defer_publication else "cli", model_version=model_version)
    try:
        result, log = run_suite(selector, selected, injected_fixture)
        write_json(out / "test_results.json", result)
        if result["reference_results"] is not None:
            write_json(out / "reference_results.json", result["reference_results"])
        (out / "test_log.txt").write_text(log, encoding="utf-8", newline="\n")
        (out / "report.md").write_text(f"# CEAV-M1 — Tests\n\nSuite: {selector}; result: {result['status']}; counts: {result['counts']}.\n\nBrowser acceptance được thu riêng; unittest không tự xác nhận V1 B01–B09, V2-B01–B06, CAL-B01, INC-B01, V3-B01 hoặc ROB-B01.\n\n" + LIMITATIONS + "\n", encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest, "succeeded" if result["status"] == "passed" else "failed")
        return result
    except BaseException as error:
        import traceback
        log = traceback.format_exc()
        (out / "test_log.txt").write_text(log, encoding="utf-8", newline="\n")
        write_json(out / "test_results.json", {"suite": selector, "status": "not_passed", "browser_acceptance_executed": False,
                   "selected_ids": selected or [], "failure_fixture": injected_fixture, "duration_seconds": None,
                   "records": [{"test_id": "RUNNER", "status": "error", "assertion_or_error": log}],
                   "counts": {"pass": 0, "fail": 0, "error": 1, "skipped": 0, "not_run": 0}})
        (out / "report.md").write_text(f"# CEAV-M1 — Runner error\n\n{error}\n\nKhông có test pass được suy ra từ runner crash; xem test_log.txt thật.\n", encoding="utf-8", newline="\n")
        if not defer_publication:
            finish_run(out, manifest, "failed", error)
        raise
