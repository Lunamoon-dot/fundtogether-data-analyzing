"""Loopback HTTP interface and one subprocess job, with parent-owned publication."""

from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
from urllib.parse import unquote, urlsplit

from . import DEFAULT_MODEL_VERSION, ENGINE_VERSION, SUPPORTED_MODEL_VERSIONS, V1_MODEL_VERSION, V2_MODEL_VERSION, V3_MODEL_VERSION, V33_MODEL_VERSION
from .__main__ import compare_config, validate_sweep_axes
from .calibration import PROVENANCE_STATUSES, calibrate_dataset
from .incentives import validate_incentive_axes
from .model import ValidationError, signal_diagnostics, validate_config, validate_scenario
from .output import FREEZES, ROOT, documents, exact_payload, finish_run, new_run, sha256, write_json
from .robustness import expand_study, load_robustness_study, validate_robustness_study
from .report_sensitive import expand_report_sensitive_study, load_report_sensitive_study, validate_report_sensitive_study
from .ipw import expand_ipw_study, load_ipw_study, validate_ipw_study
from .strategies import ACTIONS, validate_profile
from .test_runner import SUITES

TERMINAL = ("succeeded", "failed", "cancelled", "interrupted")
OPERATIONS = ("analyze", "equilibria", "sweep", "compare", "tests", "calibrate", "incentives", "robustness", "report_sensitive", "ipw")
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")


class BusyError(ValueError):
    pass


def confined(root, path):
    root, path = Path(root).resolve(), Path(path).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path outside allowed root")
    return path


def terminate_tree(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=5)


class Laboratory:
    def __init__(self, results_dir=None):
        self.results = Path(results_dir or ROOT / "results").resolve()
        self.results.mkdir(parents=True, exist_ok=True)
        self.staging = self.results / ".jobs"
        self.staging.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)
        self.jobs = {}
        self.active = None
        self.recover()

    def recover(self):
        for folder in self.results.iterdir():
            if folder.name.startswith(".") or not folder.is_dir():
                continue
            try:
                folder = confined(self.results, folder)
                manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
                if manifest["status"] in ("queued", "running") and manifest.get("publication_owner") == "local_server":
                    finish_run(folder, manifest, "interrupted", "Server restarted before terminal publication")
            except (OSError, ValueError, KeyError):
                continue
        for staged in self.staging.iterdir():
            try:
                staged = confined(self.staging, staged)
                job = json.loads((staged / "job.json").read_text(encoding="utf-8"))
                if job["status"] not in TERMINAL and not (self.results / job["run_id"] / "manifest.json").exists():
                    out = self.results / job["run_id"]
                    manifest = self.prepare_terminal_run(out, job["request"])
                    finish_run(out, manifest, "interrupted", "Server stopped before worker created artifacts")
            except (OSError, ValueError, KeyError):
                continue

    def validate(self, request):
        if not isinstance(request, dict):
            raise ValidationError("request", "Cần JSON object.")
        allowed = {"operation", "config", "profile", "mechanism", "axes", "suite", "test_ids", "failure_fixture", "scenario",
                   "dataset_csv", "source_name", "provenance_status", "base_config", "study"}
        if set(request) - allowed:
            raise ValidationError(sorted(set(request) - allowed)[0], "Field không được hỗ trợ.")
        operation = request.get("operation", "analyze")
        if operation not in OPERATIONS:
            raise ValidationError("operation", "Operation không được hỗ trợ.")
        if operation == "robustness":
            if set(request) != {"operation", "study"}:
                extra = set(request) - {"operation", "study"}
                raise ValidationError(sorted(extra)[0] if extra else "study", "Robustness cần đúng operation và study.")
            study = validate_robustness_study(request["study"])
            points = expand_study(study)
            return {"valid": True, "operation": operation, "analysis_version": study["analysis_version"],
                    "model_version": V3_MODEL_VERSION, "grid": {"policy_count": len(study["policies"]),
                    "scenario_count_per_policy": len(points) // len(study["policies"]), "total_points": len(points)},
                    "gates": study["gates"]}
        if operation == "report_sensitive":
            if set(request) != {"operation", "study"}:
                extra = set(request) - {"operation", "study"}
                raise ValidationError(sorted(extra)[0] if extra else "study", "Report-sensitive cần đúng operation và study.")
            study = validate_report_sensitive_study(request["study"])
            points = expand_report_sensitive_study(study)
            return {"valid": True, "operation": operation, "analysis_version": study["analysis_version"],
                    "model_version": study["base_config"]["model_version"],
                    "grid": {"policy_count": len(study["policies"]),
                              "scenario_count_per_policy": len(points) // len(study["policies"]), "total_points": len(points)},
                    "gates": study["gates"]}
        if operation == "ipw":
            if set(request) != {"operation", "study"}:
                extra = set(request) - {"operation", "study"}
                raise ValidationError(sorted(extra)[0] if extra else "study", "IPW cần đúng operation và study.")
            study = validate_ipw_study(request["study"])
            points = expand_ipw_study(study)
            return {"valid": True, "operation": operation, "analysis_version": study["analysis_version"],
                    "model_version": V33_MODEL_VERSION,
                    "grid": {"policy_count": len(study["policies"]),
                              "scenario_count_per_policy": len(points) // len(study["policies"]), "total_points": len(points)},
                    "gates": study["gates"]}
        if operation == "calibrate":
            fields = {"operation", "dataset_csv", "source_name", "provenance_status", "base_config", "mechanism"}
            if set(request) - fields:
                raise ValidationError(sorted(set(request) - fields)[0], "Field không được hỗ trợ cho calibration.")
            missing = fields - set(request)
            if missing:
                raise ValidationError(sorted(missing)[0], "Thiếu field bắt buộc.")
            if not isinstance(request["dataset_csv"], str):
                raise ValidationError("dataset_csv", "Cần nội dung CSV dạng text.")
            result = calibrate_dataset(request["dataset_csv"].encode("utf-8"), request["base_config"], request["mechanism"],
                                       request["provenance_status"], request["source_name"])
            return {"valid": True, "operation": operation, "dataset_hash": result["dataset_hash"],
                    "row_count": result["row_count"], "config": result["config"]}
        operation_fields = {"operation", "suite", "test_ids", "failure_fixture"} if operation == "tests" else {"operation", "config", "mechanism"}
        if operation != "tests":
            operation_fields.add("scenario")
        if operation not in ("tests", "equilibria"):
            operation_fields.add("profile")
        if operation in ("sweep", "incentives"):
            operation_fields.add("axes")
        if set(request) - operation_fields:
            raise ValidationError(sorted(set(request) - operation_fields)[0], "Field không được hỗ trợ cho operation này.")
        if operation == "tests":
            suite = request.get("suite")
            if suite not in SUITES:
                raise ValidationError("suite", "Suite không được hỗ trợ.")
            selected = request.get("test_ids", [])
            if not isinstance(selected, list) or any(not isinstance(i, str) or not re.fullmatch(r"(?:T(?:0[1-9]|[12][0-9]|3[0-2])|V2-T(?:0[1-9]|1[0-5])|CAL-T0[1-8]|INC-T0[1-8]|V3-T(?:0[1-9]|1[0-2])|ROB-T(?:0[1-9]|10)|V32-T(?:0[1-9]|10)|IPW-T(?:0[1-9]|1[0-3]))", i) for i in selected):
                raise ValidationError("test_ids", "Chỉ nhận IDs đã đăng ký V1, V2, CAL, INC, V3, ROB, V32 hoặc IPW.")
            if type(request.get("failure_fixture", False)) is not bool:
                raise ValidationError("failure_fixture", "Cần boolean.")
            fixture = request.get("failure_fixture", False)
            if fixture and suite != "selected":
                raise ValidationError("failure_fixture", "Chỉ dùng fixture lỗi trong suite selected.")
            if suite == "selected" and not selected and not fixture:
                raise ValidationError("test_ids", "Chọn ít nhất một test ID.")
            return {"valid": True, "operation": operation}
        mechanism = request.get("mechanism", "rbts")
        if mechanism not in ("fixed", "rbts", "hybrid_anchor"):
            raise ValidationError("mechanism", "Chỉ hỗ trợ fixed, rbts hoặc hybrid_anchor.")
        if operation == "incentives" and mechanism != "rbts":
            raise ValidationError("mechanism", "V2.2 incentive diagnostics chỉ hỗ trợ rbts.")
        config = compare_config(request.get("config")) if operation == "compare" else validate_config(request.get("config"), mechanism)
        profile = validate_profile(request.get("profile")) if operation != "equilibria" else None
        scenario = validate_scenario(request["scenario"]) if request.get("scenario") is not None else None
        if operation == "sweep":
            axes = request.get("axes")
            validate_sweep_axes(axes, config.model_version)
        if operation == "incentives":
            validate_incentive_axes(request.get("axes", {}))
        return {"valid": True, "operation": operation, "config": config.raw(), "profile": profile.raw() if profile else None,
                "scenario": scenario, "signal_diagnostics": signal_diagnostics(config),
                "comparison_fixed_reward": None if mechanism == "hybrid_anchor" else str(config.f + 2 * config.multiplier)}

    def snapshot(self, job):
        return {key: deepcopy(job.get(key)) for key in ("job_id", "run_id", "status", "progress", "error", "cancel_requested", "request", "worker_pid")}

    def submit(self, request):
        request = json.loads(json.dumps(request))
        if isinstance(request, dict):
            request.setdefault("operation", "analyze")
        self.validate(request)
        with self.lock:
            if self.active is not None:
                raise BusyError("Đang có tác vụ; đợi hoàn tất hoặc hủy tác vụ hiện tại.")
            identity = "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(5)
            staged = self.staging / identity
            staged.mkdir(exist_ok=False)
            job = {"job_id": identity, "run_id": identity, "status": "queued", "request": request,
                   "progress": None, "error": None, "cancel_requested": False, "stop_reason": None,
                   "process": None, "done": threading.Event(), "staged": staged}
            self.jobs[identity] = job
            self.active = identity
            write_json(staged / "request.json", request)
            write_json(staged / "job.json", self.snapshot(job))
            thread = threading.Thread(target=self.worker, args=(job,), daemon=True)
            job["thread"] = thread
            thread.start()
            return self.snapshot(job)

    def worker_command(self, job):
        request, staged = job["request"], job["staged"]
        operation = request["operation"]
        command = [sys.executable, "-B", "-m", "ceav_m1", operation, "--out", str(self.results / job["run_id"]), "--defer-publication", "--parent-pid", str(os.getpid())]
        if operation == "tests":
            command += ["--suite", request["suite"]]
            for test_id in request.get("test_ids", []):
                command += ["--test-id", test_id]
            if request.get("failure_fixture"):
                command += ["--failure-fixture"]
            return command
        if operation == "robustness":
            write_json(staged / "robustness_study.json", request["study"])
            command += ["--study", str(staged / "robustness_study.json"), "--progress-json"]
            return command
        if operation == "report_sensitive":
            write_json(staged / "report_sensitive_study.json", request["study"])
            command += ["--study", str(staged / "report_sensitive_study.json"), "--progress-json"]
            return command
        if operation == "ipw":
            write_json(staged / "ipw_study.json", request["study"])
            command += ["--study", str(staged / "ipw_study.json"), "--progress-json"]
            return command
        if operation == "calibrate":
            dataset = staged / "dataset.csv"
            dataset.write_text(request["dataset_csv"], encoding="utf-8", newline="")
            write_json(staged / "base_config.json", request["base_config"])
            command += ["--dataset", str(dataset), "--base-config", str(staged / "base_config.json"),
                        "--source-name", request["source_name"], "--mechanism", request["mechanism"],
                        "--provenance-status", request["provenance_status"]]
            return command
        write_json(staged / "config.json", request["config"])
        config_path = staged / "config.json"
        if operation == "sweep":
            write_json(staged / "sweep.json", {"base_config": "config.json", "axes": request["axes"]})
            config_path = staged / "sweep.json"
        if operation == "incentives" and request.get("axes"):
            write_json(staged / "incentive_axes.json", request["axes"])
            command += ["--axes", str(staged / "incentive_axes.json")]
        command += ["--config", str(config_path), "--progress-json"]
        if request.get("scenario") is not None:
            write_json(staged / "scenario.json", request["scenario"])
            command += ["--scenario", str(staged / "scenario.json")]
        if operation != "equilibria":
            write_json(staged / "profile.json", request["profile"])
            command += ["--profile", str(staged / "profile.json")]
        if operation != "compare":
            command += ["--mechanism", request.get("mechanism", "rbts")]
        return command

    def prepare_terminal_run(self, out, request):
        if (out / "manifest.json").exists():
            return json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        if out.exists():
            partial = self.staging / out.name / "partial-output-before-terminal-publication"
            partial.parent.mkdir(parents=True, exist_ok=True)
            if partial.exists():
                raise ValueError("Partial output snapshot already exists")
            shutil.move(str(out), str(partial))
        operation = request["operation"]
        if operation == "calibrate":
            calibrated = calibrate_dataset(request["dataset_csv"].encode("utf-8"), request["base_config"], request["mechanism"],
                                            request["provenance_status"], request["source_name"])
            return new_run(out, operation, validate_config(calibrated["config"], request["mechanism"]), mechanism=request["mechanism"],
                           request={key: value for key, value in request.items() if key != "dataset_csv"}, publication_owner="local_server")
        if operation == "robustness":
            study = validate_robustness_study(request["study"])
            config = validate_config(study["base_config"], "hybrid_anchor")
            return new_run(out, operation, config, mechanism="hybrid_anchor", request=request,
                           publication_owner="local_server")
        if operation == "report_sensitive":
            study = validate_report_sensitive_study(request["study"])
            config = validate_config(study["base_config"], "hybrid_anchor")
            return new_run(out, operation, config, mechanism="hybrid_anchor", request=request,
                           publication_owner="local_server")
        if operation == "ipw":
            study = validate_ipw_study(request["study"])
            config = validate_config(study["base_config"], "hybrid_anchor")
            return new_run(out, operation, config, mechanism="hybrid_anchor", request=request,
                           publication_owner="local_server")
        config = None if operation == "tests" else (compare_config(request["config"]) if operation == "compare" else validate_config(request["config"], request.get("mechanism", "rbts")))
        profile = validate_profile(request["profile"]) if operation in ("analyze", "compare", "sweep", "incentives") else None
        scenario = validate_scenario(request["scenario"]) if request.get("scenario") is not None else None
        return new_run(out, operation, config, profile, request.get("mechanism"), request=request, publication_owner="local_server", scenario=scenario)

    def worker(self, job):
        process = None
        log = []
        exit_code = None
        try:
            with self.lock:
                if not job["stop_reason"]:
                    command = self.worker_command(job)
                    kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
                    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               text=True, encoding="utf-8", errors="replace", **kwargs)
                    job.update(process=process, worker_pid=process.pid, status="running")
                    write_json(job["staged"] / "job.json", self.snapshot(job))
            if process is not None:
                for line in process.stdout:
                    log.append(line)
                    try:
                        payload = json.loads(line)
                        if "progress" in payload:
                            with self.lock:
                                job["progress"] = payload["progress"]
                    except (ValueError, TypeError):
                        pass
                exit_code = process.wait()
                process.stdout.close()
            with self.lock:
                status = job["stop_reason"] or ("succeeded" if exit_code == 0 else "failed")
                out = self.results / job["run_id"]
                manifest = self.prepare_terminal_run(out, job["request"])
                (out / "worker_log.txt").write_text("".join(log), encoding="utf-8", newline="\n")
                if not (out / "report.md").exists():
                    (out / "report.md").write_text(f"# CEAV-M1 — Tác vụ {status}\n\nChưa có kết quả khoa học hoàn chỉnh; không dùng làm certificate.\n", encoding="utf-8")
                finish_run(out, manifest, status, "".join(log[-12:]) if status == "failed" else None)
                job.update(status=status, error=manifest.get("error"))
        except BaseException as error:
            if process is not None:
                terminate_tree(process)
            with self.lock:
                job.update(status=job["stop_reason"] or "failed", error=str(error))
                try:
                    out = self.results / job["run_id"]
                    manifest = self.prepare_terminal_run(out, job["request"])
                    if manifest["status"] not in TERMINAL:
                        finish_run(out, manifest, job["status"], error)
                except (OSError, ValueError):
                    pass
        finally:
            with self.lock:
                write_json(job["staged"] / "job.json", self.snapshot(job))
                if self.active == job["job_id"]:
                    self.active = None
                job["done"].set()

    def cancel(self, identity, reason="cancelled"):
        with self.lock:
            if identity not in self.jobs:
                raise KeyError("Unknown job")
            job = self.jobs[identity]
            if job["status"] in TERMINAL:
                return self.snapshot(job)
            job.update(cancel_requested=True, stop_reason=reason)
            process = job["process"]
        if process is not None:
            terminate_tree(process)
        job["done"].wait(5)
        with self.lock:
            return self.snapshot(job)

    def close(self):
        with self.lock:
            active = self.active
        if active:
            self.cancel(active, "interrupted")

    def run_folder(self, identity):
        if not SAFE_ID.fullmatch(identity):
            raise ValueError("Invalid run ID")
        folder = confined(self.results, self.results / identity)
        manifest = json.loads(confined(folder, folder / "manifest.json").read_text(encoding="utf-8"))
        if manifest["run_id"] != identity:
            raise ValueError("Run identity mismatch")
        return folder, manifest

    def history(self):
        records = []
        for folder in self.results.iterdir():
            if not folder.is_dir() or not SAFE_ID.fullmatch(folder.name):
                continue
            try:
                _, manifest = self.run_folder(folder.name)
                records.append({key: manifest.get(key) for key in ("run_id", "operation", "mechanism", "status", "created_at_utc", "model_version", "config_hash", "profile_hash", "scenario_hash", "spec", "engine_revision")})
            except (OSError, ValueError, KeyError):
                continue
        return sorted(records, key=lambda r: r["created_at_utc"] or "", reverse=True)

    def artifact(self, identity, name):
        folder, manifest = self.run_folder(identity)
        allowed = {"manifest.json"} | {item["name"] for item in manifest.get("artifacts", [])}
        if name not in allowed or "\\" in name or ":" in name:
            raise ValueError("Artifact not in this run's allowlist")
        return confined(folder, folder / name)

    def browser_evidence(self):
        latest = {}
        for record in self.history():
            if record["operation"] != "browser_acceptance":
                continue
            try:
                folder, manifest = self.run_folder(record["run_id"])
                result = json.loads((folder / "browser_results.json").read_text(encoding="utf-8"))
                scenario = result["scenario"]
                if scenario in latest:
                    continue
                relevant = [item for item in manifest["source_files"] if item["path"].startswith(("ceav_m1/", "web/", "configs/", "datasets/", "verification/"))]
                match = all(sha256((ROOT / item["path"]).read_bytes()) == item["sha256"] for item in relevant)
                latest[scenario] = {"scenario": scenario, "run_id": manifest["run_id"], "status": result["status"],
                                    "browser": result["browser"], "viewport": result["viewport"], "source_matches": match,
                                    "source_comparison_scope": "engine_web_presets_datasets_and_browser_flows", "full_source_hash": manifest["engine_revision"]}
            except (OSError, ValueError, KeyError):
                continue
        required = [f"B{i:02}" for i in range(1, 10)] + [f"V2-B{i:02}" for i in range(1, 7)] + ["CAL-B01", "INC-B01", "V3-B01", "ROB-B01"]
        return {"records": [latest[key] for key in sorted(latest)], "required_scenarios": required}


class LoopbackHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        # Windows SO_REUSEADDR can bind an already-listening address. Exclusive
        # ownership makes port-conflict behavior deterministic on this platform.
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def create_server(port=8765, results_dir=None, laboratory=None):
    lab = laboratory

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def send(self, status, body, content_type="application/json; charset=utf-8", download=None):
            data = body if isinstance(body, bytes) else json.dumps(exact_payload(body), ensure_ascii=False, allow_nan=False).encode("utf-8")
            try:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
                if download:
                    self.send_header("Content-Disposition", f'attachment; filename="{download}"')
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                self.close_connection = True

        def check_host(self):
            port = self.server.server_address[1]
            host = self.headers.get("Host")
            if host not in (f"127.0.0.1:{port}", f"localhost:{port}"):
                raise PermissionError("Host not allowed")
            return host

        def do_GET(self):
            try:
                self.check_host()
                path = unquote(urlsplit(self.path).path)
                if path == "/favicon.ico":
                    self.send(204, b"", "image/x-icon")
                elif path in ("/", "/styles.css", "/app.js"):
                    name = "index.html" if path == "/" else path[1:]
                    asset = confined(ROOT / "web", ROOT / "web" / name)
                    mime = {"index.html": "text/html", "styles.css": "text/css", "app.js": "text/javascript"}[name]
                    self.send(200, asset.read_bytes(), mime + "; charset=utf-8")
                elif path == "/api/status":
                    events = {version: documents(model_version=version) for version in SUPPORTED_MODEL_VERSIONS}
                    with lab.lock:
                        active = lab.snapshot(lab.jobs[lab.active]) if lab.active else None
                    presets = {name: json.loads((ROOT / "configs" / f"{name}.json").read_text(encoding="utf-8")) for name in ("golden_g1", "golden_g2", "golden_g3", "golden_g4", "asymmetric", "all_high", "all_inverted", "all_z", "all_not_z", "all_pass", "all_fail", "asymmetric_profile")}
                    v2_presets = {name: json.loads((ROOT / "configs" / "v2" / f"{name}.json").read_text(encoding="utf-8")) for name in ("symmetric_g1", "heterogeneous", "below_half")}
                    v3_presets = {name: json.loads((ROOT / "configs" / "v3" / f"{name}.json").read_text(encoding="utf-8"))
                                  for name in ("heterogeneous_anchor", "anchor_dominant_q50")}
                    v32_presets = {"report_sensitive_base": json.loads((ROOT / "configs/v3/report_sensitive_base_v3_2.json").read_text(encoding="utf-8"))}
                    v33_presets = {"ipw_base": json.loads((ROOT / "configs/v3/ipw_base_v3_3.json").read_text(encoding="utf-8"))}
                    report_sensitive_acceptance = load_report_sensitive_study(ROOT / "tests/fixtures/v3_2_report_sensitive_study.json")
                    ipw_full = load_ipw_study(ROOT / "tests/fixtures/v3_3_ipw_study.json")
                    ipw_acceptance = deepcopy(ipw_full)
                    ipw_acceptance["policies"] = ipw_acceptance["policies"][:1]
                    ipw_acceptance["uncertainty_axes"] = {"pi": ["1/2"],
                                                            "verification_anchor.quality": ["9/10"],
                                                            "judges.high_effort_cost_multiplier": ["1"]}
                    robustness_full = load_robustness_study(ROOT / "configs/v3/robustness_v3_1.json")
                    robustness_acceptance = load_robustness_study(ROOT / "tests/fixtures/v3_1_robustness_study.json")
                    robustness_acceptance["policies"] = robustness_acceptance["policies"][:1]
                    robustness_acceptance["uncertainty_axes"] = {
                        "pi": ["1/2"], "verification_anchor.quality": ["9/10"],
                        "judges.high_effort_cost_multiplier": ["1"],
                    }
                    self.send(200, {"model_version": DEFAULT_MODEL_VERSION, "default_model_version": DEFAULT_MODEL_VERSION,
                                   "supported_model_versions": list(SUPPORTED_MODEL_VERSIONS), "engine_version": ENGINE_VERSION,
                                   "freeze_status": events[DEFAULT_MODEL_VERSION]["freeze_status"],
                                   "freezes": {version: {"path": FREEZES[version], "status": events[version]["freeze_status"]} for version in SUPPORTED_MODEL_VERSIONS},
                                   "capabilities": {operation: True for operation in OPERATIONS}, "suites": list(SUITES),
                                   "token": lab.token, "active_job": active, "actions": ACTIONS, "presets": presets,
                                   "v2_presets": v2_presets, "v3_presets": v3_presets, "v32_presets": v32_presets,
                                   "v33_presets": v33_presets,
                                   "robustness_studies": {"acceptance": robustness_acceptance, "full": robustness_full},
                                   "report_sensitive_studies": {"acceptance": report_sensitive_acceptance},
                                   "ipw_studies": {"acceptance": ipw_acceptance, "full": ipw_full}})
                elif path == "/api/calibration/sample.csv":
                    sample = ROOT / "datasets" / "synthetic_v2_calibration.csv"
                    self.send(200, sample.read_bytes(), "text/csv; charset=utf-8", sample.name if urlsplit(self.path).query == "download=1" else None)
                elif path == "/api/runs":
                    self.send(200, {"runs": lab.history()})
                elif path == "/api/browser-evidence":
                    self.send(200, lab.browser_evidence())
                elif re.fullmatch(r"/api/jobs/[^/]+", path):
                    identity = path.rsplit("/", 1)[-1]
                    with lab.lock:
                        self.send(200, lab.snapshot(lab.jobs[identity]))
                elif re.fullmatch(r"/api/runs/[^/]+", path):
                    _, manifest = lab.run_folder(path.rsplit("/", 1)[-1])
                    self.send(200, manifest)
                elif re.fullmatch(r"/api/runs/[^/]+/artifacts/.+", path):
                    _, _, _, identity, _, name = path.split("/", 5)
                    file = lab.artifact(identity, name)
                    types = {".json": "application/json", ".csv": "text/csv", ".md": "text/markdown", ".txt": "text/plain"}
                    self.send(200, file.read_bytes(), types.get(file.suffix, "application/octet-stream") + "; charset=utf-8", file.name if urlsplit(self.path).query == "download=1" else None)
                else:
                    self.send(404, {"error": "Not found"})
            except PermissionError as error:
                self.send(403, {"error": str(error)})
            except (OSError, ValueError, KeyError) as error:
                self.send(404, {"error": str(error)})

        def do_POST(self):
            try:
                host = self.check_host()
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2_000_000 or self.headers.get_content_type() != "application/json":
                    raise ValueError("Expected bounded application/json body")
                body = self.rfile.read(length)
                if self.headers.get("Origin") != f"http://{host}" or not secrets.compare_digest(self.headers.get("X-CEAV-Token", ""), lab.token):
                    raise PermissionError("Same-origin and session token required")
                request = json.loads(body)
                path = unquote(urlsplit(self.path).path)
                if path == "/api/validate":
                    self.send(200, lab.validate(request))
                elif path == "/api/runs":
                    self.send(202, lab.submit(request))
                elif re.fullmatch(r"/api/jobs/[^/]+/cancel", path):
                    self.send(200, lab.cancel(path.split("/")[3]))
                else:
                    self.send(404, {"error": "Not found"})
            except PermissionError as error:
                self.send(403, {"error": str(error)})
            except BusyError as error:
                self.send(409, {"error": str(error)})
            except ValidationError as error:
                self.send(422, {"errors": [error.as_dict()]})
            except KeyError as error:
                self.send(404, {"error": str(error)})
            except (OSError, ValueError, TypeError) as error:
                self.send(400, {"error": str(error)})

    # Bind before recovery: a failed second startup must not interrupt the
    # existing server's running artifacts.
    server = LoopbackHTTPServer(("127.0.0.1", port), Handler)
    try:
        lab = lab or Laboratory(results_dir)
    except BaseException:
        server.server_close()
        raise
    server.lab = lab
    return server


def serve_local(port):
    if not 0 <= port <= 65535:
        raise ValueError("--port phải thuộc [0,65535].")
    try:
        server = create_server(port)
    except OSError as error:
        raise OSError(f"Không thể mở 127.0.0.1:{port}; port có thể đang được sử dụng. Chọn port khác bằng --port. {error}") from error
    print(f"CEAV-M1: http://127.0.0.1:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.lab.close()
        server.server_close()
