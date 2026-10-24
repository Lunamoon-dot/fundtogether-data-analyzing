"""V6 Phase-1 tests: hand derivations plus an independent state-space oracle."""

import ast
from copy import deepcopy
from fractions import Fraction as F
import importlib
from itertools import product
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V6FeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = importlib.import_module("verification.feasibility_v6")
        cls.o = importlib.import_module("verification.oracle_v6_feasibility")

    def setUp(self):
        self.study = self.m.load_study()
        self.fx = self.study["fixtures"][1]
        self.high = (("H01",) * 3,) * 2
        self.copyz = (("L0",) * 3, ("L1",) * 3)
        self.table = self.m.decision_table(self.fx, (F(2), F(1)))

    def policy(self, kind="uniform", params=(F(1, 2),), fixture=None):
        fx = fixture or self.fx
        names = ("mu", "budget", "kappa", "operating_cost", "payout_value",
                 "exposure_limit", "c_fa", "c_fr")
        return dict({k: self.study[k] for k in names}, f=fx["f"],
                    audit=self.m.audit_table(kind, params))

    def test_T01_posterior_normalization_independence_and_exact_values(self):
        # z=0, r=111: odds=(3/7)*4^3=192/7; p=192/199.
        state = self.table[(0, (1, 1, 1))]
        self.assertEqual(state["posterior"], F(192, 199))
        # z=0,r=100 odds=(3/7)*(4)*(1/4)^2=3/28.
        self.assertEqual(self.table[(0, (1, 0, 0))]["posterior"], F(3, 31))
        self.assertEqual(sum(row["mass"] for row in self.table.values()), 1)
        for fx in self.study["fixtures"]:
            table = self.m.decision_table(fx, (F(2), F(1)))
            self.assertEqual(table, self.o.decision_table(fx, (F(2), F(1))))
            for row in table.values():
                self.assertGreaterEqual(row["voi"], 0)
                self.assertGreaterEqual(row["posterior"], 0)
                self.assertLessEqual(row["posterior"], 1)

    def test_T02_audit_observable_only_and_bounds(self):
        audit = self.m.audit_table("disagreement", (F(1), F(0)))
        self.assertEqual(len(audit), 16)
        self.assertEqual(audit[(0, (0, 0, 0))], 0)
        self.assertEqual(audit[(1, (1, 0, 1))], 1)
        for q in (F(-1, 10), F(11, 10)):
            with self.assertRaises(ValueError):
                self.m.audit_table("uniform", (q,))
        # API accepts only observable keys, no Y/X/T dimension.
        self.assertTrue(all(len(key) == 2 and len(key[1]) == 3 for key in audit))

    def test_T03_majority_noisy_posterior_and_voi(self):
        state = self.table[(0, (1, 1, 0))]
        # p=12/19; t=1 -> odds=9*12/7 -> p=108/115.
        self.assertEqual(state["posterior"], F(12, 19))
        self.assertEqual(state["g0"], 0)
        self.assertEqual(state["g1"], (0, 1))
        self.assertGreater(state["voi"], 0)
        self.assertEqual(self.table[(0, (1, 1, 1))]["g1"], (1, 1))
        policy = self.policy(params=(F(0),))
        result = self.m.evaluate(self.fx, policy, self.table, self.high)
        self.assertEqual(result["preliminary_accuracy"], F(112, 125))
        self.assertEqual(result["preliminary_fa"], F(13, 125))
        self.assertEqual(result["preliminary_fr"], F(13, 125))

    def test_T04_policy_and_peers_frozen_under_deviation(self):
        table_before = deepcopy(self.table)
        p = self.policy("disagreement", (F(1), F(0)))
        certificate = self.m.deviations(self.fx, p, self.table, self.high)
        self.assertEqual(self.table, table_before)
        rec = certificate["by_z"][0][0]
        self.assertEqual(len(rec["actions"]), 6)
        for action in rec["actions"]:
            changed = ((action["action"], "H01", "H01"), self.high[1])
            expected = self.o.evaluate(self.fx, p, self.table, changed)["utility_by_z"][0][0]
            self.assertEqual(action["utility"], expected)

    def test_T05_exposure_uses_realized_reports(self):
        p = self.policy("disagreement", (F(1), F(0)))
        high = self.m.evaluate(self.fx, p, self.table, self.high)
        low = self.m.evaluate(self.fx, p, self.table, self.copyz)
        self.assertEqual(high["audit_exposure"], F(12, 25))
        self.assertEqual(low["audit_exposure"], 0)
        self.assertEqual(high["audit_given_y"], (F(12, 25), F(12, 25)))

    def test_T06_copyZ_and_audit_seeking_reporting_bias(self):
        p = self.policy("disagreement", (F(1), F(0)))
        cert = self.m.deviations(self.fx, p, self.table, self.copyz)
        self.assertFalse(cert["is_equilibrium"])
        for z in (0, 1):
            for rec in cert["by_z"][z]:
                opposite = next(a for a in rec["actions"] if a["action"] == f"L{1-z}")
                self.assertEqual(opposite["gain"], F(17, 50))
                self.assertEqual(opposite["delta_exposure"], 1)
        metrics = self.m.evaluate(self.fx, p, self.table, self.copyz)
        self.assertEqual(metrics["preliminary_fa"], F(3, 10))
        self.assertEqual(metrics["preliminary_fr"], F(3, 10))
        self.assertEqual(metrics["wrong_payout_value"], F(3, 20))

    def test_T07_uniform_endpoints_and_allocation_attribution(self):
        p = self.policy(params=(F(0),))
        zero = self.m.evaluate(self.fx, p, self.table, self.high)
        p["audit"] = self.m.audit_table("uniform", (F(1),))
        one = self.m.evaluate(self.fx, p, self.table, self.high)
        p["audit"] = self.m.audit_table("uniform", (F(2, 5),))
        mix = self.m.evaluate(self.fx, p, self.table, self.high)
        self.assertEqual(mix["expected_decision_loss"],
                         F(3, 5)*zero["expected_decision_loss"] + F(2, 5)*one["expected_decision_loss"])
        self.assertLessEqual(one["expected_decision_loss"], zero["expected_decision_loss"])
        s = self.policy("disagreement", (F(1), F(0)))
        selective = self.m.evaluate(self.fx, s, self.table, self.high)
        e = selective["audit_exposure"]
        p["audit"] = self.m.audit_table("uniform", (e,))
        uniform = self.m.evaluate(self.fx, p, self.table, self.high)
        improvement = sum(row["mass"]*(s["audit"][key]-e)*row["voi"]
                          for key, row in self.table.items())
        self.assertEqual(uniform["expected_decision_loss"]-selective["expected_decision_loss"], improvement)
        self.assertGreater(improvement, 0)

    def test_T08_false_approval_rejection_denominators(self):
        fx = self.study["fixtures"][2]
        table = self.m.decision_table(fx, (F(2), F(1)))
        majority = {key: dict(row, g0=int(sum(key[1]) >= 2),
                              g1=(int(sum(key[1]) >= 2),)*2) for key, row in table.items()}
        result = self.m.evaluate(fx, self.policy(fixture=fx), majority, self.copyz)
        self.assertEqual(result["final_fa"], F(2, 5))
        self.assertEqual(result["final_fr"], F(1, 5))
        self.assertEqual(result["wrong_payout_value"], F(1, 5))
        self.assertEqual(result["expected_decision_loss"], F(1, 2))

    def test_T09_cash_claim_cost_reserve_and_effort(self):
        p = self.policy()
        result = self.m.evaluate(self.fx, p, self.table, self.high)
        self.assertEqual(result["expected_reviewer_payout"], F(111, 100))
        self.assertEqual(result["expected_audit_cost"], F(1, 8))
        self.assertEqual(result["cash_review_cost"], F(247, 200))
        self.assertEqual(result["reward_cap"], 3)
        self.assertEqual(result["utility_by_z"][0][0], F(8, 25))
        p["mu"] = F(3)
        with self.assertRaises(ValueError):
            self.m.evaluate(self.fx, p, self.table, self.high)

    def test_T10_exact_ties_and_six_deviations(self):
        p = self.policy(params=(F(5, 8),))
        cert = self.m.deviations(self.fx, p, self.table, self.copyz)
        for z in (0, 1):
            for rec in cert["by_z"][z]:
                self.assertEqual(set(rec["best_actions"]), {f"L{z}", "H01"})
                self.assertEqual(rec["regret"], 0)
                self.assertEqual({a["action"] for a in rec["actions"]},
                                 {"L0", "L1", "H00", "H01", "H10", "H11"})
        self.assertTrue(cert["is_equilibrium"])

    def test_T11_stop_gates_witnesses_and_non_exhaustive_scope(self):
        self.assertEqual(self.m.phase2_decision(False), "NO-GO")
        self.assertEqual(self.m.phase2_decision(True), "GO_candidate_discovery_only")
        self.assertIsNone(self.m.witness_summary([])["worst_metrics"])
        records = [dict(profile_id="bad", metrics=dict(final_fa=F(1), final_fr=F(0),
                   expected_decision_loss=F(1), cash_review_cost=F(0), audit_exposure=F(0),
                   wrong_payout_value=F(1, 2), final_accuracy=F(1, 2)))]
        summary = self.m.witness_summary(records)
        self.assertEqual(summary["worst_metrics"]["final_fa"]["profile_id"], "bad")
        self.assertEqual(summary["total_equilibrium_count"], "not_computed_phase1")
        self.assertFalse(self.m.gates(records[0]["metrics"], F(3), F(1, 2))["all_pass"])

    def test_T12_target_and_batch_weights_separate(self):
        fx = self.study["fixtures"][2]
        table = self.m.decision_table(fx, (F(2), F(1)))
        p = self.policy("public", (F(1), F(0)), fx)
        result = self.m.evaluate(fx, p, table, self.copyz)
        self.assertEqual(result["audit_exposure"], F(2, 5))
        self.assertEqual(result["cash_review_cost"], F(31, 25))
        self.assertEqual(result["batch_cash_review_cost"], F(59, 40))
        self.assertNotEqual(result["cash_review_cost"], result["batch_cash_review_cost"])

    def test_T13_independent_oracle_all_declared_profiles(self):
        for fx in self.study["fixtures"]:
            table = self.m.decision_table(fx, (F(2), F(1)))
            profiles = (self.high, self.copyz, (("L0",)*3,)*2,
                        (("L1",)*3,)*2, (("L0", "L0", "L1"), ("L1", "L1", "L0")))
            for allocation in self.study["allocations"]:
                p = self.policy(allocation["kind"], allocation["params"], fx)
                for profile in profiles:
                    for b in ((F(0),)*3, (F(1, 10),)*3):
                        actual = self.m.evaluate(fx, p, table, profile, b)
                        expected = self.o.evaluate(fx, p, table, profile, b)
                        self.assertEqual(actual, expected, (fx["name"], allocation["name"], profile, b))
        tree = ast.parse((ROOT / "verification/oracle_v6_feasibility.py").read_text(encoding="utf-8"))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        self.assertFalse(any(n and n.split(".")[0] in ("verification", "ceav_m1", "tests") for n in imports))

    def test_T14_freeze_and_output_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                self.m.write_run(Path(tmp))
        event = self.m.freeze_path()
        self.assertTrue(event.is_file())
        self.m.verify_freeze()

    def test_T15_misspecification_fixed_not_actual_recalibration(self):
        alternate = self.m.decision_table(self.fx, (F(2), F(1)), "copyZ")
        self.assertEqual(alternate, self.o.decision_table(self.fx, (F(2), F(1)), "copyZ"))
        p = self.policy()
        calibrated = self.m.evaluate(self.fx, p, self.table, self.high)
        stressed = self.m.evaluate(self.fx, p, alternate, self.high)
        self.assertNotEqual(calibrated["expected_decision_loss"], stressed["expected_decision_loss"])


if __name__ == "__main__":
    unittest.main()
