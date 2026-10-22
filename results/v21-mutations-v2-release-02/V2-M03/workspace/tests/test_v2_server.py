import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from ceav_m1.evaluate import analyze
from ceav_m1.model import validate_config
from ceav_m1.server import create_server
from ceav_m1.strategies import validate_profile
from tests.test_v2_io import raw_scenario
from tests.test_v2_model import ROOT, raw_profile, raw_v1, raw_v2


class V2ServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.server = create_server(0, Path(self.temporary.name) / "results")
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

    def http(self, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=20)
        headers = {"Origin": self.origin, "X-CEAV-Token": self.token, "Content-Type": "application/json"}
        data = json.dumps(body).encode() if body is not None else None
        connection.request("POST" if data is not None else "GET", path, body=data, headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def terminal(self, job_id):
        job = self.server.lab.jobs[job_id]
        self.assertTrue(job["done"].wait(20))
        return self.server.lab.snapshot(job)

    def request(self, config=None, scenario=None):
        payload = {"operation": "analyze", "config": config or raw_v2(), "profile": raw_profile(), "mechanism": "rbts"}
        if scenario is not None:
            payload["scenario"] = scenario
        return payload

    def test_V2_T12_status_validate_run_and_direct_parity(self):
        status, metadata = self.http("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(metadata["default_model_version"], "ceav-m1-v2.0")
        self.assertEqual(metadata["supported_model_versions"], ["ceav-m1-v1.0", "ceav-m1-v2.0"])
        self.assertEqual(set(metadata["freezes"]), {"ceav-m1-v1.0", "ceav-m1-v2.0"})
        self.assertEqual(metadata["v2_presets"]["heterogeneous"], raw_v2())

        status, checked = self.http("/api/validate", self.request(scenario=raw_scenario()))
        self.assertEqual(status, 200)
        self.assertEqual(checked["config"], raw_v2())
        self.assertEqual(checked["scenario"], raw_scenario())
        self.assertEqual(checked["signal_diagnostics"]["judges"]["A"]["private_signal"]["sensitivity"]["exact"], "9/10")

        status, job = self.http("/api/runs", self.request(scenario=raw_scenario()))
        self.assertEqual(status, 202)
        self.assertEqual(self.terminal(job["job_id"])["status"], "succeeded")
        _, summary = self.http(f"/api/runs/{job['run_id']}/artifacts/summary.json")
        direct = analyze(validate_config(raw_v2()), validate_profile(raw_profile()))
        self.assertEqual(summary["metrics"]["wrong_payout_value"]["exact"], str(direct["metrics"]["wrong_payout_value"]))

    def test_V2_T13_history_version_scenario_and_round_trip(self):
        jobs = []
        for config, scenario in ((raw_v1(), None), (raw_v2(), raw_scenario())):
            status, job = self.http("/api/runs", self.request(config, scenario))
            self.assertEqual(status, 202)
            self.assertEqual(self.terminal(job["job_id"])["status"], "succeeded")
            jobs.append(job)

        _, history = self.http("/api/runs")
        records = {record["run_id"]: record for record in history["runs"]}
        self.assertEqual(records[jobs[0]["run_id"]]["model_version"], "ceav-m1-v1.0")
        self.assertIsNone(records[jobs[0]["run_id"]]["scenario_hash"])
        self.assertEqual(records[jobs[1]["run_id"]]["model_version"], "ceav-m1-v2.0")
        self.assertIsNotNone(records[jobs[1]["run_id"]]["scenario_hash"])

        _, manifest = self.http(f"/api/runs/{jobs[1]['run_id']}")
        self.assertEqual(manifest["config"], raw_v2())
        self.assertEqual(manifest["scenario"], raw_scenario())
        bad = raw_v2(); bad["a"] = "3/4"
        status, error = self.http("/api/validate", self.request(bad))
        self.assertEqual(status, 422)
        self.assertEqual(error["errors"][0]["field"], "a")


if __name__ == "__main__":
    unittest.main()
