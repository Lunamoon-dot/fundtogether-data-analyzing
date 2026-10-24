"""Additional test coverage found by mutation/review; primary freeze unchanged."""

from fractions import Fraction as F
from itertools import product
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from verification import feasibility_v6 as checker
from verification import oracle_v6_feasibility as oracle


class V6RegressionTests(unittest.TestCase):
    def test_R01_frozen_calibration_with_external_b_and_deviation(self):
        study = checker.load_study()
        for fixture in study["fixtures"]:
            decisions = checker.decision_table(fixture, (F(2), F(1)))
            policy = dict({k: study[k] for k in ("mu", "budget", "kappa", "operating_cost",
                "payout_value", "exposure_limit", "c_fa", "c_fr")}, f=fixture["f"],
                audit=checker.audit_table("disagreement", (F(1), F(0))))
            for z, i, action in product((0, 1), range(3), checker.ACTIONS):
                profile = [list(branch) for branch in checker.HIGH]
                profile[z][i] = action
                expected = oracle.evaluate(fixture, policy, decisions, profile, (F(1, 10),)*3)
                actual = checker.evaluate(fixture, policy, decisions, profile, (F(1, 10),)*3)
                self.assertEqual(actual, expected, (fixture["name"], z, i, action))

    def test_R02_bayes_tie_releases(self):
        fixture = checker.load_study()["fixtures"][1]
        # For z=0,r=100 posterior=3/31; choose loss ratio with that threshold.
        decisions = checker.decision_table(fixture, (F(3), F(28)))
        self.assertEqual(decisions[0, (1, 0, 0)]["posterior"], F(3, 31))
        self.assertEqual(decisions[0, (1, 0, 0)]["g0"], 1)
        self.assertEqual(decisions, oracle.decision_table(fixture, (F(3), F(28))))

    def test_R03_T_conditionally_independent(self):
        for fixture in checker.load_study()["fixtures"]:
            rows = tuple(oracle._potential_states(fixture))
            self.assertEqual(sum(row[-1] for row in rows), 1)
            for y, z, xa, xb, xc in product((0, 1), repeat=5):
                selected = [row for row in rows if row[:3] == (y, z, (xa, xb, xc))]
                positive = sum(row[-1] for row in selected if row[3] == 1)
                expected = fixture["audit"][0] if y else 1-fixture["audit"][1]
                self.assertEqual(positive/sum(row[-1] for row in selected), expected)

    def test_R04_run_contains_complete_replayable_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"run"
            with patch.object(checker, "run_certificate", return_value={
                    "phase2_decision": "NO-GO", "fixtures": []}):
                checker.write_run(out)
            with patch.object(checker, "ROOT", out/"inputs"):
                checker.verify_freeze()


if __name__ == "__main__":
    unittest.main()
