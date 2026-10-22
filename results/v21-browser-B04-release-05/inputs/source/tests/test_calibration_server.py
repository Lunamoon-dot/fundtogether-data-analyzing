import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from ceav_m1.calibration import calibrate_dataset
from ceav_m1.server import create_server
from tests.test_calibration import BASE_CONFIG, DATASET, base_config


class CalibrationServerTests(unittest.TestCase):
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
        payload = response.read()
        content_type = response.getheader("Content-Type", "")
        connection.close()
        return response.status, json.loads(payload) if "json" in content_type else payload

    def request(self, text=None):
        return {"operation": "calibrate", "dataset_csv": text or DATASET.read_text(encoding="utf-8"),
                "source_name": DATASET.name, "provenance_status": "synthetic",
                "base_config": base_config(), "mechanism": "rbts"}

    def test_CAL_T06_api_worker_matches_direct_and_rejects_invalid(self):
        status, sample = self.http("/api/calibration/sample.csv")
        self.assertEqual(status, 200)
        self.assertEqual(sample, DATASET.read_bytes())

        status, job = self.http("/api/runs", self.request())
        self.assertEqual(status, 202)
        internal = self.server.lab.jobs[job["job_id"]]
        self.assertTrue(internal["done"].wait(30))
        self.assertEqual(self.server.lab.snapshot(internal)["status"], "succeeded")
        _, artifact = self.http(f"/api/runs/{job['run_id']}/artifacts/calibration.json")
        direct = calibrate_dataset(DATASET.read_bytes(), base_config(), "rbts", "synthetic", DATASET.name)
        self.assertEqual(artifact["dataset_hash"], direct["dataset_hash"])
        self.assertEqual(artifact["config"], direct["config"])

        invalid = DATASET.read_text(encoding="utf-8").replace("SYN-002", "SYN-001", 1)
        status, error = self.http("/api/runs", self.request(invalid))
        self.assertEqual(status, 422)
        self.assertEqual(error["errors"][0]["field"], "case_id")
        self.assertEqual(error["errors"][0]["row"], 3)


if __name__ == "__main__":
    unittest.main()
