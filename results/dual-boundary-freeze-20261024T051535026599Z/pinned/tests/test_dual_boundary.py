"""DB01-DB08: paper constants, independent oracle and completeness probes."""

import unittest
from fractions import Fraction as F
from itertools import product

from verification import dual_boundary as subject
from verification import dual_boundary_oracle as oracle


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = {m: subject.build_table(m) for m in ("selective", "uniform")}

    def test_DB01_local_paper_boundaries(self):
        expected = {"selective": (-F(70,633), F(175,1102)),
                    "uniform": (-F(218750,2070709), F(218750,1365587))}
        for mechanism, table in self.tables.items():
            rows = subject.local_boundaries(table)
            self.assertEqual(len(rows), 36)
            for i in range(3):
                lower = max(r["breakpoint"] for r in rows if r["judge"] == i and r["slope"] < 0)
                upper = min(r["breakpoint"] for r in rows if r["judge"] == i and r["slope"] > 0)
                self.assertEqual((lower, upper), expected[mechanism])

    def test_DB02_frozen_calibration(self):
        c = subject.load_config()
        for (z,r), (g0,g1) in oracle.calibration().items():
            self.assertEqual(g0, c["g0_by_z_and_report_sum"][z][sum(r)])
            self.assertEqual(g1, tuple(c["g1_by_z_and_report_sum"][z][sum(r)]))

    def test_DB03_all_profiles_independent_oracle(self):
        for mechanism, table in self.tables.items():
            for z, profile in product((0,1), product(oracle.ACTIONS, repeat=3)):
                self.assertEqual(table[z, profile], oracle.evaluate(z, profile, mechanism), (mechanism,z,profile))

    def test_DB04_closed_intersections(self):
        self.assertEqual(subject.solve_constraints(((F(-1),F(1)),(F(1),F(-1)))), (F(1),F(1)))
        self.assertIsNone(subject.solve_constraints(((F(-2),F(1)),(F(1),F(-1)))))
        self.assertIsNone(subject.solve_constraints(((F(-1),F(0)),)))
        self.assertEqual(subject.solve_constraints(((F(1),F(0)),)), (None,None))

    def test_DB05_neutral_metrics(self):
        expected = {"fa": F(43,1250), "fr": F(481,3125), "wrong_payout": F(43,2500),
                    "loss": F(348,3125), "exposure": F(2557,6250), "cash": F(46957,25000), "reserve": F(6)}
        for mechanism, table in self.tables.items():
            equilibria = subject.full_equilibria(table, (0,0,0))
            self.assertEqual(len(equilibria), 1)
            self.assertEqual(equilibria[0]["interval"], (None,None))
            metric = equilibria[0]["metrics"]
            if mechanism == "selective":
                for k,v in expected.items():
                    self.assertEqual(metric[k],v,k)
            else:
                self.assertEqual(metric["loss"],F(4499061,39062500))

    def test_DB06_all_interval_constraints_and_cells(self):
        for mechanism, table in self.tables.items():
            for vector in subject.load_config()["scenarios"].values():
                equilibria = subject.full_equilibria(table,vector)
                cells = subject.cells(equilibria)
                for cell in cells:
                    b = cell["representative"]
                    active = {e["profile"] for e in equilibria if subject.contains(e["interval"],b)}
                    direct = []
                    for z in (0,1):
                        direct.append([p for p in product(oracle.ACTIONS,repeat=3)
                                       if all(c+b*s >= 0 for c,s in subject.constraints(table,z,p,vector))])
                    self.assertEqual(active,set(product(*direct)))
                    self.assertEqual(cell["pure_count"],len(active))
                    if not active:
                        self.assertFalse(cell["all_gates_pass"])

    def test_DB07_mutations_detected(self):
        for mutation in ("union_payment", "double_audit"):
            self.assertNotEqual(self.tables["selective"][0,("H01",)*3],
                                oracle.evaluate(0,("H01",)*3,"selective",mutation))
        table = self.tables["selective"]
        b = F(1,10)
        # Neutral is strictly dominant, yet symmetric interests admit Low equilibria.
        es = subject.full_equilibria(table,(1,1,1))
        active = [e for e in es if subject.contains(e["interval"],b)]
        self.assertTrue(any(e["profile"] != (("H01",)*3,)*2 for e in active))
        self.assertTrue(any(any(a.startswith("L") for branch in e["profile"] for a in branch) for e in active))
        self.assertTrue(any(e["interval"][0] is not None and subject.contains(e["interval"],e["interval"][0]) for e in es))

    def test_DB08_positions_and_dominated_high_constants(self):
        for table in self.tables.values():
            signatures = []
            for i in range(3):
                vector = tuple(int(i==j) for j in range(3))
                es = subject.full_equilibria(table,vector)
                signatures.append(sorted((str(e["interval"]),str(e["metrics"])) for e in es))
                self.assertTrue(all(a not in ("H00","H11") for e in es for branch in e["profile"] for a in branch))
            self.assertEqual(signatures[0],signatures[1])
            self.assertEqual(signatures[1],signatures[2])


if __name__ == "__main__":
    unittest.main()
