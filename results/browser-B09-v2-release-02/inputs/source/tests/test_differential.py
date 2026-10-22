"""F12 catalog differential checks; deliberately a slow acceptance test."""

from itertools import product
import time
import unittest

from ceav_m1.equilibria import search_pure
from tests import oracle
from tests.test_core import config


class DifferentialTests(unittest.TestCase):
    def test_T14_F12_catalog_all_branch_candidates(self):
        started = time.perf_counter()
        catalog = []
        discrepancies = []
        expected_tables = {}
        parameters = tuple(product(("1/5", "1/2", "4/5"), ("1/3", "1/2", "4/5"), ("1/4", "1/2", "4/5")))
        for pi, a, b in parameters:
            c = config(pi=pi, a=a, b=b, costs=["0", "1/50", "3/20"])
            actual = search_pure(c)
            count = 0
            for z in (0, 1):
                for record in actual["branches"][str(z)]["candidates"]:
                    actions = tuple(record["actions"])
                    # Entire six-action payoffs, calculated directly from states.
                    table = oracle.branch_payoff_table(c.raw(), z, actions)
                    expected_tables[pi, a, b, z, actions] = table
                    raw_profile = {"0": list(actions), "1": list(actions)}
                    forecasts = oracle.forecasts([(s, w) for s, w in oracle.worlds(c.raw()) if s[1] == z], raw_profile)
                    self.assertEqual([{tuple(row["observation"]): row["prediction"] for row in prediction} for prediction in record["predictions"]], forecasts)
                    for i, certificate in enumerate(record["certificates"]):
                        trials = table[i]
                        best = max(trials)
                        candidate = trials[oracle.ACTIONS.index(actions[i])]
                        expected = {"regret": best - candidate,
                                    "delta_utility": max(trials[2:]) - max(trials[:2]),
                                    "optimal_actions": [act for act, utility in zip(oracle.ACTIONS, trials) if utility == best]}
                        got = {key: certificate[key] for key in expected}
                        expected["candidate_utility"] = candidate
                        expected["low_utility"] = max(trials[:2])
                        expected["high_utility"] = max(trials[2:])
                        got.update(candidate_utility=certificate["candidate"]["utility"], low_utility=certificate["low"]["utility"], high_utility=certificate["high"]["utility"])
                        if got != expected:
                            discrepancies.append({"config": c.raw(), "z": z, "actions": actions, "judge": i, "expected": oracle.encode(expected), "observed": oracle.encode(got)})
                        self.assertGreaterEqual(certificate["high"]["score"], certificate["low"]["score"])
                    count += 1
            self.assertEqual(count, 432)
            catalog.append({"config": c.raw(), "branch_candidates_compared": count})
        # Reverse every config, z and candidate, using the already independently
        # integrated numeric payoff vectors (never cached equilibrium flags).
        reversed_checks = 0
        from ceav_m1.best_response import solve_branch
        from ceav_m1.evaluate import evaluate
        from ceav_m1.strategies import Profile, build_candidate
        for pi, a, b in reversed(parameters):
            c = config(pi=pi, a=a, b=b, costs=["0", "1/50", "3/20"])
            for z in (1, 0):
                for actions in reversed(tuple(product(oracle.ACTIONS, repeat=3))):
                    candidate = build_candidate(c, Profile((actions, actions)))
                    direct = evaluate(c, candidate)
                    for i in range(3):
                        cert = solve_branch(c, candidate, i, z, candidate_payoff=direct["conditional"][i][z])
                        trials = expected_tables[pi, a, b, z, actions][i]
                        best = max(trials)
                        self.assertEqual(cert["regret"], best - trials[oracle.ACTIONS.index(actions[i])])
                        self.assertEqual(cert["optimal_actions"], [act for act, value in zip(oracle.ACTIONS, trials) if value == best])
                    reversed_checks += 1
        self.assertEqual(reversed_checks, 27 * 432)
        self.evidence = {"fixture": "F12", "catalog": catalog, "total_branch_candidates": 27 * 432,
                         "candidate_catalog": [{"z": z, "actions": list(actions)} for z in (0, 1) for actions in product(oracle.ACTIONS, repeat=3)],
                         "discrepancies": discrepancies, "reverse_order_branch_candidates": reversed_checks,
                         "cache": "none across candidates", "duration_seconds": time.perf_counter() - started}
        self.assertEqual(discrepancies, [], str(discrepancies[:3]))
