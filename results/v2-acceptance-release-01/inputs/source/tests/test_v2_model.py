from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import unittest

from ceav_m1.model import ValidationError, enumerate_states, signal_diagnostics, validate_config
from ceav_m1.evaluate import analyze
from ceav_m1.strategies import build_candidate, validate_profile
from tests import oracle_v2

ROOT = Path(__file__).resolve().parents[1]


def raw_v2(name="heterogeneous"):
    return json.loads((ROOT / f"configs/v2/{name}.json").read_text(encoding="utf-8"))


def raw_v1(name="golden_g1"):
    return json.loads((ROOT / f"configs/{name}.json").read_text(encoding="utf-8"))


def raw_profile(name="all_high"):
    return json.loads((ROOT / f"configs/{name}.json").read_text(encoding="utf-8"))


class V2ModelTests(unittest.TestCase):
    def test_V2_T01_nested_schema_dispatch_and_errors(self):
        config = validate_config(raw_v2())
        self.assertEqual(config.model_version, "ceav-m1-v2.0")
        self.assertEqual(config.costs, (F(1, 20), F(1, 10), F(1, 25)))
        self.assertEqual(config.raw(), raw_v2())
        self.assertEqual(validate_config(raw_v1()).model_version, "ceav-m1-v1.0")
        reordered = raw_v2(); reordered["judges"] = {key: reordered["judges"][key] for key in ("C", "A", "B")}
        reordered_config = validate_config(reordered)
        self.assertEqual(reordered_config.costs, (F(1, 20), F(1, 10), F(1, 25)))
        self.assertEqual(enumerate_states(reordered_config), enumerate_states(config))

        invalids = []
        missing = raw_v2(); del missing["judges"]["B"]
        invalids.append((missing, "judges"))
        typo = raw_v2(); typo["judges"]["A"]["private_signal"]["specificty"] = typo["judges"]["A"]["private_signal"].pop("specificity")
        invalids.append((typo, "judges.A.private_signal.specificty"))
        missing_specificity = raw_v2(); del missing_specificity["public_signal"]["specificity"]
        invalids.append((missing_specificity, "public_signal"))
        mixed = raw_v2(); mixed["a"] = "7/10"
        invalids.append((mixed, "a"))
        endpoint = raw_v2(); endpoint["public_signal"]["sensitivity"] = "1"
        invalids.append((endpoint, "public_signal.sensitivity"))
        number = raw_v2(); number["judges"]["C"]["high_effort_cost"] = 0.04
        invalids.append((number, "judges.C.high_effort_cost"))
        for raw, field in invalids:
            with self.subTest(field=field), self.assertRaises(ValidationError) as caught:
                validate_config(raw)
            self.assertEqual(caught.exception.field, field)

    def test_V2_T02_distribution_matches_independent_oracle(self):
        raw = raw_v2()
        rows = enumerate_states(validate_config(raw))
        expected = oracle_v2.worlds(raw)
        actual = tuple(((row.state_id, row.y, row.z, *row.signals), row.probability) for row in rows)
        self.assertEqual(actual, expected)
        self.assertEqual(rows[0].probability, F(399, 2500))
        self.assertEqual(rows[-1].probability, F(351, 2000))

        changed = deepcopy(raw)
        changed["judges"]["A"]["private_signal"]["sensitivity"] = "4/5"
        original_rows = enumerate_states(validate_config(raw))
        changed_rows = enumerate_states(validate_config(changed))
        self.assertTrue(all(a.probability == b.probability for a, b in zip(original_rows, changed_rows) if a.y == 0))
        self.assertTrue(any(a.probability != b.probability for a, b in zip(original_rows, changed_rows) if a.y == 1))

        below = enumerate_states(validate_config(raw_v2("below_half")))
        self.assertEqual(len(below), 32)
        self.assertEqual(sum(row.probability for row in below), 1)

    def test_V2_T03_signal_diagnostics_exact(self):
        raw = raw_v2("below_half")
        actual = signal_diagnostics(validate_config(raw))
        self.assertEqual(actual, oracle_v2.diagnostics(raw))
        self.assertEqual(actual["public_signal"]["false_negative_rate"], F(3, 5))
        self.assertEqual(actual["public_signal"]["prior_weighted_accuracy"], F(31, 60))

    def test_V2_T04_v1_reduction_states_predictions_and_analysis(self):
        v1 = validate_config(raw_v1())
        v2 = validate_config(raw_v2("symmetric_g1"))
        self.assertEqual(enumerate_states(v1), enumerate_states(v2))
        profile = validate_profile(raw_profile())
        c1, c2 = build_candidate(v1, profile), build_candidate(v2, profile)
        self.assertEqual(c1.rows, c2.rows)
        self.assertEqual(c1.predictions, c2.predictions)
        r1, r2 = analyze(v1, profile), analyze(v2, profile)
        for key in ("metrics", "judges", "conditional", "states", "branch_masses", "reward_cap", "reward_budget",
                    "predictions", "best_responses", "max_regret", "equilibrium_status"):
            self.assertEqual(r1[key], r2[key], key)


if __name__ == "__main__":
    unittest.main()
