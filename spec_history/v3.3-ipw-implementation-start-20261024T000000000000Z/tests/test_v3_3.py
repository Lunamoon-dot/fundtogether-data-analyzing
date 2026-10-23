import json
from fractions import Fraction as F
from pathlib import Path
import unittest

import ceav_m1
from ceav_m1.model import ValidationError, validate_config


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def v33_raw():
    raw = load("configs/v3/report_sensitive_base_v3_2.json")
    raw["model_version"] = "ceav-m1-v3.3"
    raw["verification_anchor"]["audit_reward_mode"] = "ipw"
    raw["reward_budget"] = "24"
    return raw


def validation_result(raw):
    try:
        return validate_config(raw, "hybrid_anchor")
    except ValidationError as error:
        return error


class V33IPWTests(unittest.TestCase):
    def test_IPW_T01_version_constant_and_schema_round_trip(self):
        self.assertEqual(getattr(ceav_m1, "V33_MODEL_VERSION", None), "ceav-m1-v3.3")
        result = validation_result(v33_raw())
        self.assertEqual(getattr(result, "model_version", None), "ceav-m1-v3.3")
        self.assertEqual(result.raw(), v33_raw())
        self.assertEqual(result.audit_reward_mode, "ipw")
        self.assertEqual(result.audit_probability_by_report, (F(1, 4), F(3, 4)))

    def test_IPW_T02_zero_report_probability_is_rejected(self):
        raw = v33_raw()
        raw["verification_anchor"]["audit_probability_by_report"]["0"] = "0"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "verification_anchor.audit_probability_by_report.0")

    def test_IPW_T03_ipw_cap_is_checked_against_shared_budget(self):
        raw = v33_raw()
        raw["reward_budget"] = "23"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "reward_budget")

    def test_IPW_T04_v3_scalar_audit_input_is_rejected(self):
        raw = v33_raw()
        raw["verification_anchor"]["audit_probability"] = "1/2"
        result = validation_result(raw)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.field, "verification_anchor.audit_probability")


if __name__ == "__main__":
    unittest.main()
