"""Small independent assertions for V3.3 mutation probes."""
import unittest


class V33MutationAssertions(unittest.TestCase):
    def test_policy_robust_requires_every_point(self):
        from ceav_m1.ipw import summarize_ipw_policies

        points = [
            {"policy_id": "p", "status": "pass", "failure_reasons": [], "worst": {"accuracy": 1, "false_approval_rate": 0, "wrong_payout_value": 0, "false_rejection_rate": 0, "cash_review_cost": 0}},
            {"policy_id": "p", "status": "fail", "failure_reasons": ["cash_review_cost_gate"], "worst": None},
        ]
        summary = summarize_ipw_policies(points, [{"policy_id": "p", "label": "p", "overrides": {}}])[0]
        self.assertEqual(summary["point_count"], 2)
        self.assertEqual(summary["pass_count"], 1)
        self.assertFalse(summary["robust"])

    def test_invalid_budget_point_is_retained_in_policy_summary(self):
        from ceav_m1.ipw import summarize_ipw_policies

        points = [
            {"policy_id": "p", "status": "pass", "failure_reasons": [], "worst": {"accuracy": 1, "false_approval_rate": 0, "wrong_payout_value": 0, "false_rejection_rate": 0, "cash_review_cost": 0}},
            {"policy_id": "p", "status": "fail", "failure_reasons": ["invalid_budget"], "worst": None},
        ]
        summary = summarize_ipw_policies(points, [{"policy_id": "p", "label": "p", "overrides": {}}])[0]
        self.assertEqual(summary["point_count"], 2)
        self.assertEqual(summary["fail_count"], 1)
        self.assertEqual(summary["failure_reason_counts"], {"invalid_budget": 1})


if __name__ == "__main__":
    unittest.main()
