import csv
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ceav_m1.calibration import CalibrationError, calibrate_dataset
from ceav_m1.evaluate import analyze
from ceav_m1.model import validate_config
from ceav_m1.strategies import validate_profile


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets/synthetic_v2_calibration.csv"
BASE_CONFIG = ROOT / "configs/v2/heterogeneous.json"
EXPECTED = ROOT / "tests/fixtures/calibration_expected.json"


def base_config():
    return json.loads(BASE_CONFIG.read_text(encoding="utf-8"))


def dataset_bytes():
    return DATASET.read_bytes()


def mutate_csv(transform):
    rows = list(csv.reader(StringIO(dataset_bytes().decode("utf-8"))))
    transform(rows)
    stream = StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return stream.getvalue().encode()


class CalibrationTests(unittest.TestCase):
    def test_CAL_T01_fixture_matches_manual_expected(self):
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
        result = calibrate_dataset(dataset_bytes(), base_config(), "rbts", "synthetic", DATASET.name)
        self.assertEqual(result["row_count"], expected["row_count"])
        self.assertEqual(result["class_counts"], expected["class_counts"])
        self.assertEqual(result["estimates"]["pi"], expected["pi"])
        self.assertEqual(result["estimates"]["public_signal"], expected["public_signal"])
        for judge in "ABC":
            observed = result["estimates"]["judges"][judge]
            wanted = expected["judges"][judge]
            self.assertEqual(observed["private_signal"]["sensitivity"], wanted["sensitivity"])
            self.assertEqual(observed["private_signal"]["specificity"], wanted["specificity"])
            self.assertEqual(observed["high_effort_cost"], wanted["mean_cost"])

    def test_CAL_T02_strict_dataset_validation(self):
        mutations = [
            (lambda rows: rows[0].pop(), "columns"),
            (lambda rows: rows[0].append("unknown"), "columns"),
            (lambda rows: rows.__setitem__(2, rows[1].copy()), "case_id"),
            (lambda rows: rows[1].__setitem__(2, "yes"), "public_signal_Z"),
            (lambda rows: rows[1].__setitem__(6, "-1/20"), "cost_A"),
            (lambda rows: [row.__setitem__(1, "1") for row in rows[1:]], "ground_truth_Y"),
        ]
        for transform, field in mutations:
            with self.subTest(field=field):
                with self.assertRaises(CalibrationError) as caught:
                    calibrate_dataset(mutate_csv(transform), base_config(), "rbts", "synthetic", "bad.csv")
                self.assertEqual(caught.exception.field, field)

        degenerate = mutate_csv(lambda rows: [row.__setitem__(2, row[1]) for row in rows[1:]])
        with self.assertRaises(CalibrationError) as caught:
            calibrate_dataset(degenerate, base_config(), "rbts", "synthetic", "degenerate.csv")
        self.assertEqual(caught.exception.field, "public_signal.sensitivity")

    def test_CAL_T03_semantic_and_raw_hashes(self):
        original = calibrate_dataset(dataset_bytes(), base_config(), "rbts", "synthetic", DATASET.name)
        lines = dataset_bytes().decode().splitlines()
        reordered = ("\r\n".join([lines[0], *reversed(lines[1:])]) + "\r\n").encode()
        changed = calibrate_dataset(reordered, base_config(), "rbts", "synthetic", "reordered.csv")
        self.assertEqual(original["dataset_hash"], changed["dataset_hash"])
        self.assertNotEqual(original["raw_sha256"], changed["raw_sha256"])
        self.assertEqual(original["config"], changed["config"])

    def test_CAL_T04_generated_config_preserves_economics_and_runs(self):
        base = base_config()
        result = calibrate_dataset(dataset_bytes(), base, "rbts", "synthetic", DATASET.name)
        for key in ("f", "lambda", "fixed_reward", "reward_budget", "payout_value", "operating_cost"):
            self.assertEqual(result["config"][key], base[key])
        config = validate_config(result["config"], "rbts")
        profile = validate_profile(json.loads((ROOT / "configs/all_high.json").read_text(encoding="utf-8")))
        analyzed = analyze(config, profile, "rbts")
        self.assertEqual(len(analyzed["states"]), 32)

    def test_CAL_T05_cli_artifacts_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "calibration-run"
            command = [sys.executable, "-B", "-m", "ceav_m1", "calibrate", "--dataset", str(DATASET),
                       "--base-config", str(BASE_CONFIG), "--mechanism", "rbts",
                       "--provenance-status", "synthetic", "--out", str(out)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual((out / "dataset.csv").read_bytes(), DATASET.read_bytes())
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "succeeded")
            self.assertEqual(manifest["operation"], "calibrate")
            self.assertEqual(manifest["calibration"]["revision"], "ceav-m1-v2.1-calibration")
            self.assertTrue((out / "calibration.json").is_file())
            self.assertTrue((out / "config.json").is_file())


if __name__ == "__main__":
    unittest.main()
