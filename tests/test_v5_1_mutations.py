import importlib
import unittest


class V51MutationTests(unittest.TestCase):
    def test_quality_certificate_mutations_are_rejected(self):
        probes = importlib.import_module("verification.mutation_probes_v5_1")
        result = probes.run_probes()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(len(result["mutations"]), 4)
        self.assertTrue(all(item["status"] == "rejected" for item in result["mutations"]))


if __name__ == "__main__":
    unittest.main()
