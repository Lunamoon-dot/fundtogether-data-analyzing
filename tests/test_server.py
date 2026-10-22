from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from ceav_m1.server import Laboratory, create_server
from ceav_m1.output import ROOT
from tests.test_core import config, profile


def request(operation="analyze"):
    result = {"operation": operation, "config": config().raw(), "profile": profile().raw(), "mechanism": "rbts"}
    if operation == "equilibria":
        del result["profile"]
    return result


def wait_until(predicate, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.02)
    raise AssertionError("Timed out waiting for explicit worker handshake/state")


class BarrierLab(Laboratory):
    mode = "barrier"

    def worker_command(self, job):
        return [sys.executable, "-B", str(ROOT / "tests/worker_fixture.py"), str(job["staged"]), str(self.results / job["run_id"]), self.mode, str(os.getpid())]


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.results = Path(self.temporary.name) / "results"
        self.server = create_server(0, self.results)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.origin = f"http://127.0.0.1:{self.port}"
        self.token = self.server.lab.token

    def tearDown(self):
        self.server.lab.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)
        self.temporary.cleanup()

    def http(self, path, body=None, headers=None, method=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        base = {"Origin": self.origin, "X-CEAV-Token": self.token, "Content-Type": "application/json"}
        if headers:
            base.update(headers)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        connection.request(method or ("POST" if data is not None else "GET"), path, body=data, headers=base)
        response = connection.getresponse()
        raw = response.read()
        status = response.status
        content_type = response.getheader("Content-Type", "")
        connection.close()
        return status, json.loads(raw) if "application/json" in content_type else raw

    def terminal(self, identity):
        job = self.server.lab.jobs[identity]
        self.assertTrue(job["done"].wait(15))
        return self.server.lab.snapshot(job)

    def install_barrier_lab(self, mode="barrier"):
        self.server.lab.__class__ = BarrierLab
        self.server.lab.mode = mode

    def test_T23_offline_assets_capabilities_port_conflict(self):
        for path in ("/", "/styles.css", "/app.js"):
            status, body = self.http(path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
        _, data = self.http("/api/status")
        self.assertTrue(all(data["capabilities"].values()))
        self.assertEqual(data["token"], self.token)
        process = subprocess.run([sys.executable, "-B", "-m", "ceav_m1", "serve", "--port", str(self.port)], cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(process.stderr)
        self.assertIn(str(self.port), process.stderr)
        self.assertIn("--port", process.stderr)
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_T24_validation_fields_fraction_profile_presets(self):
        status, result = self.http("/api/validate", request())
        self.assertEqual(status, 200)
        self.assertEqual(result["config"]["pi"], "1/2")
        self.assertEqual(result["comparison_fixed_reward"], "2")
        invalid = request()
        invalid["config"]["pi"] = 0.5
        status, result = self.http("/api/validate", invalid)
        self.assertEqual(status, 422)
        self.assertEqual(result["errors"][0]["field"], "pi")
        _, status = self.http("/api/status")
        self.assertEqual(status["presets"]["golden_g4"]["pi"], "4/5")
        self.assertEqual(status["presets"]["all_inverted"], {"0": ["H10"] * 3, "1": ["H10"] * 3})
        bad_mechanism = request("compare") | {"mechanism": "typo"}
        self.assertEqual(self.http("/api/validate", bad_mechanism)[0], 422)
        unused_field = request() | {"suite": "reference"}
        self.assertEqual(self.http("/api/validate", unused_field)[0], 422)

    def test_T25_API_CLI_exact_parity_G1_G4(self):
        from ceav_m1.evaluate import analyze
        for name in ("golden_g1", "golden_g2", "golden_g3", "golden_g4"):
            payload = request()
            payload["config"] = config(name).raw()
            payload["profile"] = profile("all_z" if name == "golden_g2" else "all_high").raw()
            status, job = self.http("/api/runs", payload)
            self.assertEqual(status, 202)
            finished = self.terminal(job["job_id"])
            self.assertEqual(finished["status"], "succeeded", finished)
            _, output = self.http(f"/api/runs/{job['run_id']}/artifacts/summary.json")
            direct = analyze(config(name), profile("all_z" if name == "golden_g2" else "all_high"))
            self.assertEqual(output["metrics"]["accuracy"]["exact"], str(direct["metrics"]["accuracy"]))
            self.assertEqual(output["equilibrium_status"], direct["equilibrium_status"])

    def test_T26_witness_artifact_all_six_branches(self):
        payload = request(); payload["config"] = config("golden_g4").raw()
        _, job = self.http("/api/runs", payload)
        self.assertEqual(self.terminal(job["job_id"])["status"], "succeeded")
        _, certificates = self.http(f"/api/runs/{job['run_id']}/artifacts/best_responses.json")
        self.assertEqual({(b["judge"], b["z"]) for b in certificates}, {(i, z) for i in "ABC" for z in (0, 1)})
        self.assertTrue(all(b["witness"] for b in certificates if b["z"] == 1))

    def test_T27_search_progress_and_certificate_artifact(self):
        _, job = self.http("/api/runs", request("equilibria"))
        final = self.terminal(job["job_id"])
        self.assertEqual(final["status"], "succeeded", final)
        self.assertEqual(final["progress"]["completed"], 432)
        _, search = self.http(f"/api/runs/{job['run_id']}/artifacts/equilibria.json")
        self.assertEqual(search["branch_candidate_count"], 432)
        self.assertTrue(search["branches"]["0"]["equilibrium_ids"])

    def test_T29_API_failure_fixture_and_missing_group(self):
        payload = {"operation": "tests", "suite": "selected", "test_ids": [], "failure_fixture": True}
        _, job = self.http("/api/runs", payload)
        self.assertEqual(self.terminal(job["job_id"])["status"], "failed")
        _, result = self.http(f"/api/runs/{job['run_id']}/artifacts/test_results.json")
        self.assertEqual(result["counts"]["fail"], 1)
        _, log = self.http(f"/api/runs/{job['run_id']}/artifacts/test_log.txt")
        self.assertIn(b"Explicit failure fixture", log)
        status, _ = self.http("/api/runs", {"operation": "tests", "suite": "selected", "test_ids": ["os.system"]})
        self.assertEqual(status, 422)

    def test_T30_duplicate_submit_immutable_snapshot_cancel(self):
        self.install_barrier_lab("child")
        barrier = threading.Barrier(2)
        def submit():
            barrier.wait()
            return self.http("/api/runs", request())
        with ThreadPoolExecutor(2) as pool:
            responses = list(pool.map(lambda _: submit(), range(2)))
        self.assertEqual(sorted(status for status, _ in responses), [202, 409])
        job = next(body for status, body in responses if status == 202)
        internal = self.server.lab.jobs[job["job_id"]]
        wait_until(lambda: (internal["staged"] / "started.json").exists())
        handshake = json.loads((internal["staged"] / "started.json").read_text(encoding="utf-8"))
        snapshot = json.loads((internal["staged"] / "request.json").read_text(encoding="utf-8"))
        self.assertEqual(snapshot["config"]["pi"], "1/2")
        process = internal["process"]
        status, cancelled = self.http(f"/api/jobs/{job['job_id']}/cancel", {})
        self.assertEqual(status, 200)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertIsNotNone(process.poll())
        from ceav_m1.runtime import process_alive
        self.assertFalse(process_alive(handshake["child_pid"]))
        _, manifest = self.http(f"/api/runs/{job['run_id']}")
        self.assertEqual(manifest["status"], "cancelled")
        again = self.http(f"/api/jobs/{job['job_id']}/cancel", {})[1]
        self.assertEqual(again["status"], "cancelled")

    def test_T30_cancel_before_worker_launch(self):
        gate = threading.Event()
        lab = self.server.lab
        original_worker = lab.worker
        def delayed_worker(job):
            gate.wait(10)
            original_worker(job)
        lab.worker = delayed_worker
        _, job = self.http("/api/runs", request())
        internal = lab.jobs[job["job_id"]]
        with ThreadPoolExecutor(1) as pool:
            cancel = pool.submit(lambda: self.http(f"/api/jobs/{job['job_id']}/cancel", {}))
            wait_until(lambda: internal["cancel_requested"])
            gate.set()
            status, cancelled = cancel.result(timeout=10)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertIsNone(internal["process"])
        self.assertFalse((lab.results / job["run_id"] / "summary.json").exists())

    def test_T30_partial_output_before_manifest_is_preserved_and_finalized(self):
        out = self.results / "run-partial-output"
        (out / "inputs").mkdir(parents=True)
        (out / "inputs" / "copied-before-cancel.txt").write_text("partial", encoding="utf-8")
        manifest = self.server.lab.prepare_terminal_run(out, request())
        self.assertEqual(manifest["run_id"], "run-partial-output")
        self.assertTrue((out / "manifest.json").is_file())
        preserved = self.results / ".jobs" / "run-partial-output" / "partial-output-before-terminal-publication" / "inputs" / "copied-before-cancel.txt"
        self.assertEqual(preserved.read_text(encoding="utf-8"), "partial")

    def test_T30_success_before_cancel_and_worker_crash(self):
        self.install_barrier_lab()
        for mode, expected in (("barrier", "succeeded"), ("crash", "failed")):
            self.server.lab.mode = mode
            _, job = self.http("/api/runs", request())
            internal = self.server.lab.jobs[job["job_id"]]
            wait_until(lambda: (internal["staged"] / "started.json").exists())
            (internal["staged"] / "release").touch()
            self.assertEqual(self.terminal(job["job_id"])["status"], expected)
            status, response = self.http(f"/api/jobs/{job['job_id']}/cancel", {})
            self.assertEqual(response["status"], expected)

    def test_T31_history_path_origin_allowlist(self):
        _, job = self.http("/api/runs", request())
        self.terminal(job["job_id"])
        identity = job["run_id"]
        for path in (f"/api/runs/../artifacts/manifest.json", f"/api/runs/%2e%2e/artifacts/manifest.json", f"/api/runs/%252e%252e/artifacts/manifest.json", f"/api/runs/{identity}/artifacts/../../AGENTS.md", f"/api/runs/{identity}/artifacts/C:%5CWindows%5Cwin.ini", f"/api/runs/{identity}/artifacts/%5C%5Cserver%5Cshare", f"/api/runs/{identity}/artifacts/request.json.tmp"):
            self.assertNotEqual(self.http(path)[0], 200, path)
        for headers in ({"Origin": "https://evil.example"}, {"Origin": ""}, {"X-CEAV-Token": ""}, {"X-CEAV-Token": "wrong"}):
            self.assertEqual(self.http("/api/runs", request(), headers)[0], 403)
        status, history = self.http("/api/runs")
        self.assertTrue(any(r["run_id"] == identity for r in history["runs"]))
        self.assertEqual(self.http("/api/status", headers={"Host": f"attacker.example:{self.port}"})[0], 403)

    def test_T31_restart_interrupted_run_and_completed_history(self):
        _, completed = self.http("/api/runs", request())
        self.assertEqual(self.terminal(completed["job_id"])["status"], "succeeded")
        completed_manifest = self.server.lab.run_folder(completed["run_id"])[1]
        self.install_barrier_lab()
        _, job = self.http("/api/runs", request())
        internal = self.server.lab.jobs[job["job_id"]]
        wait_until(lambda: (internal["staged"] / "started.json").exists())
        self.server.lab.close()
        self.assertIsNotNone(internal["process"].poll())
        restarted = Laboratory(self.results)
        _, manifest = restarted.run_folder(job["run_id"])
        self.assertEqual(manifest["status"], "interrupted")
        previous = manifest.copy()
        Laboratory(self.results)
        self.assertEqual(restarted.run_folder(job["run_id"])[1], previous)
        self.assertEqual(restarted.run_folder(completed["run_id"])[1], completed_manifest)

    def test_T31_abrupt_parent_exit_kills_worker_tree(self):
        from ceav_m1.runtime import process_alive
        folder = Path(self.temporary.name) / "abrupt"
        folder.mkdir()
        process = subprocess.Popen([sys.executable, "-B", str(ROOT / "tests/server_fixture.py"), str(folder)], cwd=ROOT,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            ready = folder / "server.json"
            wait_until(ready.exists)
            metadata = json.loads(ready.read_text(encoding="utf-8"))
            port = metadata["port"]
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("POST", "/api/runs", body=json.dumps(request()), headers={"Origin": f"http://127.0.0.1:{port}", "Content-Type": "application/json", "X-CEAV-Token": metadata["token"]})
            response = connection.getresponse()
            self.assertEqual(response.status, 202)
            job = json.loads(response.read())
            connection.close()
            staged = folder / "results/.jobs" / job["run_id"]
            wait_until(lambda: (staged / "started.json").exists())
            handshake = json.loads((staged / "started.json").read_text(encoding="utf-8"))
            self.assertTrue(process_alive(handshake["pid"]))
            self.assertTrue(process_alive(handshake["child_pid"]))
            process.kill()  # Intentionally stop only the owned server process.
            process.wait(timeout=5)
            wait_until(lambda: not process_alive(handshake["pid"]))
            wait_until(lambda: not process_alive(handshake["child_pid"]))
            restarted = Laboratory(folder / "results")
            manifest = restarted.run_folder(job["run_id"])[1]
            self.assertEqual(manifest["status"], "interrupted")
            self.evidence = {"server_pid": process.pid, "worker_pid": handshake["pid"], "child_pid": handshake["child_pid"], "worker_alive_after_parent_exit": False, "child_alive_after_parent_exit": False, "manifest_status": manifest["status"]}
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdout.close()

    def test_T31_symlink_junction_and_prefix_sibling_confinement(self):
        from ceav_m1.server import confined
        outside = Path(self.temporary.name) / "results-sibling"
        outside.mkdir()
        (outside / "manifest.json").write_text('{"run_id":"escape"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            confined(self.results, outside / "manifest.json")
        alias = self.results / "escape"
        kind = "symlink"
        try:
            alias.symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(outside)], capture_output=True, text=True)
            if result.returncode:
                self.skipTest("Cannot create symlink or junction fixture: " + result.stderr)
            kind = "junction"
        self.assertTrue(alias.exists())
        with self.assertRaises(ValueError):
            self.server.lab.run_folder("escape")
        self.assertNotEqual(self.http("/api/runs/escape")[0], 200)
        self.evidence = {"fixture": kind, "target_outside_results_rejected": True, "prefix_sibling_rejected": True}


if __name__ == "__main__":
    unittest.main()
