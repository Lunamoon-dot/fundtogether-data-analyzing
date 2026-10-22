from copy import deepcopy
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from itertools import product
import inspect
import hashlib
import json
from pathlib import Path
import unittest

from ceav_m1.best_response import solve_branch
from ceav_m1.evaluate import analyze, evaluate
from ceav_m1.model import HighObservation, LowObservation, ValidationError, enumerate_states, observe, validate_config
from ceav_m1.scoring import quadratic, score_judge
from ceav_m1.strategies import ACTIONS, build_candidate, report_for, validate_profile
from tests import oracle
from tests.certificates import verify_analysis

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads((ROOT / "tests/fixtures/reference.json").read_text(encoding="utf-8"))


def config(name="golden_g1", **updates):
    raw = json.loads((ROOT / "configs" / f"{name}.json").read_text(encoding="utf-8"))
    raw.update(updates)
    return validate_config(raw)


def profile(name="all_high"):
    return validate_profile(json.loads((ROOT / "configs" / f"{name}.json").read_text(encoding="utf-8")))


class CoreTests(unittest.TestCase):
    def test_T01_distribution(self):
        c = config(pi="1/2", a="1/2", b="1/2")
        rows = enumerate_states(c)
        self.assertEqual(len({(s.y, s.z, s.signals) for s in rows}), 32)
        self.assertEqual([s.probability for s in rows], [F(1, 32)] * 32)
        for s, (bits, mass) in zip(rows, oracle.worlds(c.raw())):
            self.assertEqual((s.y, s.z, *s.signals), bits)
            self.assertEqual(s.probability, mass)
        result = analyze(c, profile())
        self.assertEqual(result["judges"][0]["score"], F(5, 4))

    def test_T02_information_boundaries(self):
        self.assertEqual(list(inspect.signature(report_for).parameters), ["action", "observation"])
        self.assertEqual(list(inspect.signature(score_judge).parameters), ["reports", "predictions", "judge"])
        rows = enumerate_states(config())
        for action in ACTIONS:
            outputs = {}
            for row in rows:
                obs = observe(row, 0, action[0])
                self.assertFalse(hasattr(obs, "y"))
                self.assertFalse(hasattr(obs, "signals"))
                if action[0] == "L":
                    self.assertFalse(hasattr(obs, "x"))
                value = report_for(action, obs)
                self.assertEqual(outputs.setdefault(obs, value), value)
        with self.assertRaises(TypeError):
            report_for("H00", LowObservation(0))
        with self.assertRaises(FrozenInstanceError):
            LowObservation(0).z = 1

    def test_T03_bounds_endpoints(self):
        for p, r in product((F(0), F(1, 5), F(1, 2), F(1)), (0, 1)):
            self.assertEqual(quadratic(p, r), 1 - (p - r) ** 2)
        for reports in product((0, 1), repeat=3):
            for ps in product((F(0), F(1, 2), F(1)), repeat=3):
                for i in range(3):
                    row = score_judge(reports, ps, i)
                    self.assertTrue(0 <= row["shadow"] <= 1)
                    self.assertTrue(0 <= row["total_score"] <= 2)

    def test_T04_roles(self):
        fixture = FIXTURES["F02"]
        ps = tuple(map(F, fixture["predictions"]))
        for i in range(3):
            row = score_judge(fixture["reports"], ps, i)
            self.assertEqual(row["total_score"], F(fixture["scores"][i]))
            self.assertEqual((row["reference_id"], row["peer_id"]), ((i + 1) % 3, (i + 2) % 3))

    def test_T05_predictions_and_exact_loss(self):
        points = (F(0), F(1, 3), F(1, 2), F(1, 2) + F(1, 10**18), F(1))
        for q, p in product(points, repeat=2):
            expected = lambda v: q * quadratic(v, 1) + (1 - q) * quadratic(v, 0)
            self.assertEqual(expected(q) - expected(p), (p - q) ** 2)
        for name in ("all_pass", "all_fail"):
            candidate = build_candidate(config(), profile(name))
            self.assertEqual({p for table in candidate.predictions for _, p in table}, {F(name == "all_pass")})

    def test_T05_H_constants_keep_private_prediction(self):
        c = config()
        for action in ("H00", "H11"):
            raw = {str(z): [action, "H01", "H01"] for z in (0, 1)}
            candidate = build_candidate(c, validate_profile(raw))
            values = [p for _, p in candidate.predictions[0]]
            self.assertEqual(values, list(map(F, FIXTURES["F05"]["predictions"])))
            result = analyze(c, validate_profile(raw))
            high = sum(b["branch_probability"] * b["high"]["prediction_score"] for b in result["best_responses"] if b["judge"] == "A")
            low = sum(b["branch_probability"] * b["low"]["prediction_score"] for b in result["best_responses"] if b["judge"] == "A")
            self.assertEqual(high, F(FIXTURES["F13"]["high_prediction"]))
            self.assertEqual(low, F(FIXTURES["F13"]["low_prediction"]))
            self.assertEqual(high - low, F(FIXTURES["F13"]["prediction_gain"]))

    def test_T06_fixed_constant_and_zero_costs(self):
        for mechanism in ("fixed", "rbts"):
            c = config(costs=["0", "1/50", "3/20"], **{"lambda": "0"})
            result = analyze(c, profile(), mechanism)
            self.assertEqual(result["prediction_semantics"], "arbitrary_reachable_predictions")
            for b in result["best_responses"]:
                i = "ABC".index(b["judge"])
                self.assertEqual(b["regret"], c.costs[i])
                self.assertEqual(b["best_efforts"], ["L", "H"] if i == 0 else ["L"])
                self.assertEqual(b["prediction_optimum"], "any_in_unit_interval")
                self.assertEqual(b["report_optimum"], "any_admissible_map")
            self.assertTrue(verify_analysis(result))

    def test_T07_uninformative_private_signal(self):
        result = analyze(config(b="1/2"), profile())
        for b in result["best_responses"]:
            self.assertEqual(b["high"]["score"], b["low"]["score"])
            self.assertEqual(b["delta_utility"], -F(1, 20))

    def test_T08_low_effort_maximum_profiles(self):
        for name in ("all_z", "all_not_z", "all_pass", "all_fail"):
            result = analyze(config(), profile(name))
            self.assertEqual(result["equilibrium_status"], "exact_pure_equilibrium")
            for state in result["states"]:
                for judge in "ABC":
                    self.assertEqual(state[f"{judge}_score"], 2)
            for b in result["best_responses"]:
                self.assertEqual(b["regret"], 0)
                self.assertEqual(b["delta_utility"], -F(1, 20))
                self.assertEqual(b["low"]["observations"][0]["optimal_reports"], [0, 1])
            self.assertTrue(verify_analysis(result))

    def test_T09_G1_all_judges_and_branches(self):
        result = analyze(config(), profile())
        expected = FIXTURES["F05"]
        self.assertEqual(result["equilibrium_status"], "exact_pure_equilibrium")
        for branch in result["best_responses"]:
            self.assertEqual(branch["low"]["score"], F(expected["low"]))
            self.assertEqual(branch["high"]["score"], F(expected["high"]))
            self.assertEqual(branch["delta_utility"], F(expected["delta_utility"]))
            self.assertEqual(branch["regret"], 0)
            self.assertEqual(branch["low"]["observations"][0]["optimal_reports"], [0, 1])
            for obs in branch["high"]["observations"]:
                z, x = obs["observation"]
                self.assertEqual(obs["optimal_reports"], [x])
                self.assertEqual(obs["information_by_report"][x] - obs["information_by_report"][1 - x], F(expected["report_margins"][2*z+x]))
        self.assertEqual(result["metrics"]["accuracy"], F(expected["accuracy"]))
        self.assertEqual(result["metrics"]["wrong_payout_value"], F(expected["wrong_payout"]))
        low = analyze(config(), profile("all_z"))
        self.assertTrue(all(l > h for l, h in zip(low["metrics"]["expected_judge_utility"], result["metrics"]["expected_judge_utility"])))
        self.assertTrue(verify_analysis(result))

    def test_T10_G3_negative_result(self):
        result = analyze(config("golden_g3"), profile())
        for b in result["best_responses"]:
            self.assertEqual(b["low"]["score"], F(149, 100))
            self.assertEqual(b["high"]["score"], F(23833, 15680))
            self.assertEqual(b["delta_utility"], -F(1571, 78400))
        self.assertEqual(result["equilibrium_status"], "not_equilibrium")
        self.assertEqual(result["metrics"]["accuracy"], F(27, 32))
        self.assertTrue(verify_analysis(result))

    def test_T11_G4_post_signal_effort(self):
        result = analyze(config("golden_g4"), profile())
        self.assertEqual(result["equilibrium_status"], "not_equilibrium")
        for b in result["best_responses"]:
            self.assertEqual(b["delta_utility"], F(FIXTURES["F08"][f"delta_z{b['z']}"]))
            if b["z"] == 1:
                self.assertGreater(b["regret"], 0)
                self.assertEqual(b["witness"]["action"][0], "L")
                self.assertEqual(b["witness"]["ex_ante_gain"], F(31, 50) * b["regret"])
        self.assertGreater(sum(b["branch_probability"] * b["delta_utility"] for b in result["best_responses"] if b["judge"] == "A"), 0)
        self.assertTrue(verify_analysis(result))

    def test_T12_peer_freeze_numeric_counterexample(self):
        c, p = config(), profile()
        candidate = build_candidate(c, p)
        before = candidate.predictions
        result = solve_branch(c, candidate, 0, 0)
        self.assertEqual(candidate.predictions, before)
        self.assertEqual(result["low"]["score"], F(3611, 2500))
        # Independently rebuild the wrong peer response to establish this is discriminating.
        raw = {str(z): ["L0", "H01", "H01"] for z in (0, 1)}
        rebuilt = oracle.forecasts(oracle.worlds(c.raw()), raw)
        changed = oracle.payoff(c.raw(), raw, rebuilt, 0, 0)
        self.assertEqual(changed["score"], F(3461, 2500))
        self.assertNotEqual(result["low"]["score"], changed["score"])

    def test_T13_joint_expectation(self):
        outcomes = ((F(1, 4), 0), (F(3, 4), 1))
        for r in (0, 1):
            joint = sum(quadratic(p + (2*r-1)*min(p, 1-p), k) for p, k in outcomes) / 2
            independent = sum(quadratic(p + (2*r-1)*min(p, 1-p), k) for p, _ in outcomes for _, k in outcomes) / 4
            self.assertEqual(joint, F(7, 8))
            self.assertEqual(independent, F(5, 8))
        self.assertTrue(verify_analysis(analyze(config("asymmetric"), profile("asymmetric_profile"))))
        self.assertTrue(verify_analysis(analyze(config(), profile())))

    def test_T14_information_variance_identity(self):
        for name in ("golden_g1", "golden_g4", "asymmetric"):
            result = analyze(config(name), profile("asymmetric_profile") if name == "asymmetric" else profile())
            for b in result["best_responses"]:
                self.assertGreaterEqual(b["high"]["score"], b["low"]["score"])
                qlow = b["low"]["observations"][0]["optimal_prediction"]
                variance = sum(o["probability_given_z"] * (o["optimal_prediction"] - qlow) ** 2 for o in b["high"]["observations"])
                self.assertEqual(b["high"]["prediction_score"] - b["low"]["prediction_score"], variance)

    def test_T15_asymmetric_certificate_and_tamper(self):
        stored = json.loads((ROOT / "tests/fixtures/asymmetric_oracle.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256((ROOT / "tests/fixtures/oracle_preproduction.py").read_bytes()).hexdigest(), stored["oracle_sha256"])
        independent = oracle.analyze(stored["config"], stored["profile"])
        self.assertEqual(oracle.encode(independent), stored["expected"])
        result = analyze(config("asymmetric"), profile("asymmetric_profile"))
        self.assertTrue(verify_analysis(result))
        changes = (
            lambda r: r["best_responses"].pop(),
            lambda r: r["best_responses"][0]["low"]["observations"][0].update(optimal_prediction=F(1, 123)),
            lambda r: r["best_responses"][1]["witness"].update(conditional_gain=F(99)),
            lambda r: r["best_responses"][1]["witness"].update(action="L0"),
            lambda r: r.update(status="cancelled"),
            lambda r: r["best_responses"][0].update(regret=F(1)),
            lambda r: r["best_responses"][0].update(reference_judge="C"),
        )
        for change in changes:
            altered = deepcopy(result)
            change(altered)
            with self.assertRaises(ValueError):
                verify_analysis(altered)

    def test_T19_threshold_and_reward_shift(self):
        threshold = F(FIXTURES["F05"]["lambda_threshold"])
        for scale, efforts in ((F(1, 2), ["L"]), (F(1), ["L", "H"]), (F(2), ["H"])):
            result = analyze(config(reward_budget="12", **{"lambda": str(scale * threshold)}), profile())
            self.assertTrue(all(b["best_efforts"] == efforts for b in result["best_responses"]))
        old = analyze(config(), profile())
        new = analyze(config(f="1/3", reward_budget="7"), profile())
        for a, b in zip(old["best_responses"], new["best_responses"]):
            self.assertEqual(a["regret"], b["regret"])
            self.assertEqual(b["candidate"]["utility"] - a["candidate"]["utility"], F(1, 3))

    def test_T20_input_validation(self):
        base = config().raw()
        cases = [{"pi": 0.5}, {"pi": True}, {"pi": "0"}, {"a": "1"}, {"b": "NaN"},
                 {"pi": "1/0"}, {"f": "-1"}, {"costs": ["0"]}, {"costs": ["0", "-1", "0"]},
                 {"typo": "1"}, {"model_version": "v2"}, {"reward_budget": "5"}]
        for update in cases:
            with self.assertRaises(ValidationError, msg=str(update)):
                validate_config(base | update)
        for raw in ({}, {"0": ["L0"] * 3}, {"0": ["bad"] * 3, "1": ["L0"] * 3}):
            with self.assertRaises(ValidationError):
                validate_profile(raw)
        for key in base.keys() - {"operating_cost"}:
            missing = dict(base)
            del missing[key]
            with self.assertRaises(ValidationError):
                validate_config(missing)


if __name__ == "__main__":
    unittest.main()
