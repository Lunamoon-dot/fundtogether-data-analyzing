"""V6-T16: actual temporary source mutations must fail assertions."""

import importlib
import unittest


class V6MutationTests(unittest.TestCase):
    def test_T16_mutations_execute_and_are_killed(self):
        module = importlib.import_module("verification.mutation_probes_v6")
        records = module.run_probes()
        self.assertGreaterEqual(len(records), 13)
        self.assertTrue(all(row["status"] == "killed_by_assertion" for row in records), records)
        self.assertTrue(all(row["tests_run"] > 0 and row["errors"] == 0 for row in records))


if __name__ == "__main__":
    unittest.main()
