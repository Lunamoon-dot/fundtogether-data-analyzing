"""Targeted post-discovery negative witnesses; no exhaustive screening."""

from fractions import Fraction as F
import importlib
import unittest


class V6StopCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = importlib.import_module("verification.v6_phase1_stop")

    def test_S01_all_discovery_candidates_have_exact_bad_NE(self):
        result = self.m.run_certificate()
        self.assertEqual(result["decision"], "NO-GO_declared_phase1_candidates")
        self.assertEqual(len(result["witnesses"]), 4)
        expected = (
            (F(1), F(1,20), F(1,20), F(211,100)),
            (F(1,2), F(1), F(0), F(283,200)),
            (F(1), F(11,250), F(77,500), F(199,100)),
            (F(1,2), F(77,6250), F(2321,3125), F(247,200)),
        )
        for record, values in zip(result["witnesses"], expected):
            self.assertEqual(record["max_regret"], 0)
            self.assertEqual(record["independent_deviation_checks"], 36)
            self.assertFalse(record["gates"]["all_pass"])
            m = record["metrics"]
            self.assertEqual((m["audit_exposure"], m["final_fa"], m["final_fr"], m["cash_review_cost"]), values)
        self.assertEqual(result["equilibrium_count"], "not_computed")

    def test_S02_unverified_or_incomplete_witnesses_cannot_close(self):
        self.assertEqual(self.m.stop_decision([True]*4), "NO-GO_declared_phase1_candidates")
        for evidence in ([], [True]*3, [True, True, True, False]):
            self.assertEqual(self.m.stop_decision(evidence), "UNRESOLVED")


if __name__ == "__main__":
    unittest.main()
