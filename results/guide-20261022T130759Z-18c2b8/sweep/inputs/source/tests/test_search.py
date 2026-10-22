from fractions import Fraction as F
from itertools import product
import unittest

from ceav_m1.equilibria import CancelledError, search_pure
from ceav_m1.strategies import ACTIONS
from tests import oracle
from tests.test_core import config, profile
from ceav_m1.evaluate import analyze


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g1 = search_pure(config())

    def test_T16_complete_six_action_search(self):
        result = self.g1
        self.assertEqual(result["branch_candidate_count"], 432)
        self.assertEqual(result["full_profile_count"], 46656)
        for z in ("0", "1"):
            branch = result["branches"][z]
            self.assertEqual({tuple(r["actions"]) for r in branch["candidates"]}, set(product(ACTIONS, repeat=3)))
            for record in branch["candidates"]:
                self.assertEqual(len(record["certificates"]), 3)
                if not record["accepted"]:
                    self.assertIsNotNone(record["witness"])
                for certificate in record["certificates"]:
                    self.assertGreaterEqual(certificate["regret"], 0)
            self.assertIn(f"z{z}:H01,H01,H01", branch["equilibrium_ids"])
        self.assertEqual(result["full_equilibrium_count"], result["branches"]["0"]["equilibrium_count"] * result["branches"]["1"]["equilibrium_count"])

    def test_T16_constant_rewards_continuum_counts(self):
        for m in (0, 1, 3):
            c = config(costs=["0"] * m + ["1/20"] * (3-m), **{"lambda": "0"})
            for mechanism in ("rbts", "fixed"):
                result = search_pure(c, mechanism)
                count = 2**(3-m) * 6**m
                self.assertEqual([b["equilibrium_count"] for b in result["branches"].values()], [count, count])
                self.assertEqual(result["full_equilibrium_count"], count**2)
                self.assertEqual(result["prediction_semantics"], "arbitrary_reachable_predictions")

    def test_T17_full_profile_set_equality(self):
        expected, evidence = oracle.full_profile_enumeration(config().raw())
        branches = [self.g1["branches"][str(z)] for z in (0, 1)]
        actual = set(product(*(tuple(tuple(r["actions"]) for r in b["candidates"] if r["accepted"]) for b in branches)))
        self.assertEqual(evidence["profiles_checked"], 46656)
        self.assertEqual(evidence["full_strategy_deviations_compared"], 46656 * 3 * 36)
        self.assertEqual(expected - actual, set())
        self.assertEqual(actual - expected, set())
        # Recorded by the evidence runner through this public test attribute.
        self.evidence = evidence | {"set_difference": [], "equilibrium_count": len(actual),
                                    "retained_full_profile_ids": [{"0": list(a), "1": list(b)} for a, b in sorted(actual)]}

    def test_T18_binary_and_cyclic_relabel(self):
        c, p = config("asymmetric"), profile("asymmetric_profile")
        original = analyze(c, p)
        binary = {"L0": "L1", "L1": "L0", "H00": "H11", "H11": "H00", "H01": "H01", "H10": "H10"}
        transformed = {str(1-z): [binary[a] for a in p.branches[z]] for z in (0, 1)}
        from ceav_m1.model import validate_config
        from ceav_m1.strategies import validate_profile
        flipped = analyze(validate_config(c.raw() | {"pi": str(1-c.pi)}), validate_profile(transformed))
        self.assertEqual(flipped["metrics"]["accuracy"], original["metrics"]["accuracy"])
        self.assertEqual(flipped["metrics"]["false_approval_rate"], original["metrics"]["false_rejection_rate"])
        self.assertEqual(flipped["metrics"]["false_rejection_rate"], original["metrics"]["false_approval_rate"])
        self.assertEqual(flipped["metrics"]["expected_judge_utility"], original["metrics"]["expected_judge_utility"])
        rotated = {str(z): list(p.branches[z][1:] + p.branches[z][:1]) for z in (0, 1)}
        costs = list(map(str, c.costs[1:] + c.costs[:1]))
        shifted = analyze(validate_config(c.raw() | {"costs": costs}), validate_profile(rotated))
        values = original["metrics"]["expected_judge_utility"]
        self.assertEqual(shifted["metrics"]["expected_judge_utility"], values[1:] + values[:1])

    def test_T30_search_cancellation_no_certificate(self):
        progress = []
        with self.assertRaises(CancelledError):
            search_pure(config(), on_progress=progress.append, is_cancelled=lambda: len(progress) == 2)
        self.assertEqual(progress[-1]["completed"], 2)


if __name__ == "__main__":
    unittest.main()
