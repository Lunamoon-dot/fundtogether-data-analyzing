"""Explicit UI/runner failure demonstration; excluded from normal discovery."""

import unittest


class IntentionalFailure(unittest.TestCase):
    def test_explicit_failure_fixture(self):
        self.assertEqual("intentional fixture actual", "intentional fixture expected", "Explicit failure fixture; production engine is untouched")
