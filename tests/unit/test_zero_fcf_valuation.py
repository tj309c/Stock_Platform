"""
Unit tests for the Zero FCF Valuation models in src/analysis/zero_fcf_valuation.py.
"""

import unittest
from src.analysis.zero_fcf_valuation import ZeroFCFValuation

class TestZeroFCFValuation(unittest.TestCase):
    """
    Test suite for the ZeroFCFValuation class.
    """

    def test_revenue_multiple_valuation(self):
        """
        Test the revenue multiple valuation with a set of known inputs.
        """
        inputs = {
            "latest_revenue": 1_000_000_000,
            "revenue_multiple": 5.0,
            "shares_outstanding": 200_000_000,
            "cash": 100_000_000,
            "debt": 300_000_000,
        }

        results = ZeroFCFValuation.revenue_multiple_valuation(**inputs)

        expected_enterprise_value = 5_000_000_000
        expected_intrinsic_value = 24.00

        self.assertIsInstance(results, dict)
        self.assertAlmostEqual(results['enterprise_value'], expected_enterprise_value, places=2)
        self.assertAlmostEqual(results['intrinsic_value_per_share'], expected_intrinsic_value, places=2)

    def test_rule_of_40(self):
        """
        Test the Rule of 40 calculation and assessments.
        """
        # Healthy scenario
        healthy_results = ZeroFCFValuation.rule_of_40(
            revenue_growth_rate=0.30, profit_margin=0.15
        )
        self.assertAlmostEqual(healthy_results['score'], 0.45)
        self.assertEqual(healthy_results['assessment'], "Healthy")

        # Needs Improvement scenario
        improvement_results = ZeroFCFValuation.rule_of_40(
            revenue_growth_rate=0.20, profit_margin=0.10
        )
        self.assertAlmostEqual(improvement_results['score'], 0.30)
        self.assertEqual(improvement_results['assessment'], "Needs Improvement")

        # Unhealthy scenario
        unhealthy_results = ZeroFCFValuation.rule_of_40(
            revenue_growth_rate=0.05, profit_margin=0.05
        )
        self.assertAlmostEqual(unhealthy_results['score'], 0.10)
        self.assertEqual(unhealthy_results['assessment'], "Unhealthy")

if __name__ == '__main__':
    unittest.main()