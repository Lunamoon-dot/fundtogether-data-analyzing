from fractions import Fraction as F
from itertools import product
from unittest.mock import patch
import unittest

from ceav_m1.equilibria import search_pure
from ceav_m1.evaluate import analyze
from ceav_m1.model import signal_diagnostics, validate_config
from ceav_m1.strategies import ACTIONS, validate_profile
from tests import oracle, oracle_v2
from tests.test_v2_model import raw_profile, raw_v1, raw_v2


def v2_parameters(raw):
    parsed = oracle_v2.parsed(raw)
    return {
        "pi": parsed["pi"],
        "costs": parsed["costs"],
        "f": F(raw["f"]),
        "lambda": F(raw["lambda"]),
        "fixed_reward": F(raw["fixed_reward"]),
        "reward_budget": F(raw["reward_budget"]),
        "payout_value": F(raw["payout_value"]),
        "operating_cost": F(raw.get("operating_cost", "0")),
    }


def independent_analysis(raw, profile, mechanism="rbts"):
    worlds = [(bits[1:], mass) for bits, mass in oracle_v2.worlds(raw)]
    with patch("tests.oracle.worlds", return_value=worlds), patch("tests.oracle.parameters", return_value=v2_parameters(raw)):
        return oracle.analyze(raw, profile, mechanism)


class V2EngineTests(unittest.TestCase):
    def test_V2_T05_candidate_predictions_metrics_and_observations(self):
        raw, raw_p = raw_v2(), raw_profile()
        result = analyze(validate_config(raw), validate_profile(raw_p))
        expected = independent_analysis(raw, raw_p)
        self.assertEqual(result["signal_diagnostics"], signal_diagnostics(validate_config(raw)))
        for i, table in enumerate(result["predictions"]):
            actual = {tuple(item["observation"]): item["prediction"] for item in table}
            self.assertEqual(actual, expected["tables"][i])
        for key in ("accuracy", "false_approval_rate", "false_rejection_rate", "wrong_payout_value", "expected_payout"):
            self.assertEqual(result["metrics"][key], expected[key], key)
        self.assertNotEqual(result["predictions"][0], result["predictions"][1])
        self.assertNotEqual(result["metrics"]["expected_judge_utility"][0], result["metrics"]["expected_judge_utility"][1])

    def test_V2_T06_best_response_matches_independent_six_map_oracle(self):
        raw, raw_p = raw_v2(), raw_profile()
        result = analyze(validate_config(raw), validate_profile(raw_p))
        expected = independent_analysis(raw, raw_p)
        self.assertEqual({(record["judge"], record["z"]) for record in result["best_responses"]},
                         {(judge, z) for judge in "ABC" for z in (0, 1)})
        for record in result["best_responses"]:
            truth = expected["branches"][2 * "ABC".index(record["judge"]) + record["z"]]
            self.assertEqual(record["candidate"]["utility"], truth["candidate"]["utility"])
            self.assertEqual(record["delta_utility"], truth["delta"])
            self.assertEqual(record["regret"], truth["regret"])
            self.assertEqual(record["optimal_actions"], truth["optimal_actions"])
            self.assertTrue(record["frozen_peer_tables"])

    def test_V2_T07_search_direct_oracle_and_complete_branch_space(self):
        v1 = search_pure(validate_config(raw_v1()))
        v2 = search_pure(validate_config(raw_v2("symmetric_g1")))
        self.assertEqual(v2["branch_candidate_count"], 432)
        self.assertEqual(v2["full_profile_count"], 46656)
        for z in ("0", "1"):
            self.assertEqual({tuple(row["actions"]) for row in v2["branches"][z]["candidates"]}, set(product(ACTIONS, repeat=3)))
            self.assertEqual(v1["branches"][z], v2["branches"][z])
        self.assertEqual(v1["full_equilibrium_count"], v2["full_equilibrium_count"])

        raw = raw_v2()
        worlds = [(bits[1:], mass) for bits, mass in oracle_v2.worlds(raw)]
        with patch("tests.oracle.worlds", return_value=worlds), patch("tests.oracle.parameters", return_value=v2_parameters(raw)):
            expected, evidence = oracle.full_profile_enumeration(raw)
        heterogeneous = search_pure(validate_config(raw))
        branches = [heterogeneous["branches"][str(z)] for z in (0, 1)]
        actual = set(product(*(tuple(tuple(row["actions"]) for row in branch["candidates"] if row["accepted"]) for branch in branches)))
        self.assertEqual(evidence["profiles_checked"], 46656)
        self.assertEqual(evidence["full_strategy_deviations_compared"], 46656 * 3 * 36)
        self.assertEqual(expected, actual)
        self.evidence = evidence | {"set_difference": [], "equilibrium_count": len(actual), "fixture": "V2-F01"}


if __name__ == "__main__":
    unittest.main()
