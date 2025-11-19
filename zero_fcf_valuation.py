"""
src/analysis/zero_fcf_valuation.py

Contains alternative valuation models for companies with zero or negative
Free Cash Flow (FCF), such as high-growth tech or SaaS companies.
"""

from typing import Dict

class ZeroFCFValuation:
    """
    A collection of valuation methods for non-profitable or high-growth firms
    where traditional DCF is not applicable.
    """

    @staticmethod
    def revenue_multiple_valuation(
        latest_revenue: float,
        revenue_multiple: float,
        shares_outstanding: float,
        cash: float = 0.0,
        debt: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculates intrinsic value based on a revenue multiple.

        Args:
            latest_revenue (float): The company's trailing twelve months (TTM) revenue.
            revenue_multiple (float): The industry or peer-based revenue multiple (e.g., 5.0x).
            shares_outstanding (float): The number of shares outstanding.
            cash (float): Total cash and cash equivalents.
            debt (float): Total debt.

        Returns:
            dict: A dictionary containing the calculated enterprise and intrinsic values.
        """
        enterprise_value = latest_revenue * revenue_multiple
        equity_value = enterprise_value - debt + cash
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

        return {
            "enterprise_value": enterprise_value,
            "intrinsic_value_per_share": intrinsic_value_per_share
        }

    @staticmethod
    def rule_of_40(
        revenue_growth_rate: float,
        profit_margin: float
    ) -> Dict[str, float | str]:
        """
        Calculates the Rule of 40 score for a SaaS company.

        The rule states that a healthy SaaS company's revenue growth rate plus
        its profit margin should be 40% or higher.

        Args:
            revenue_growth_rate (float): The company's year-over-year revenue growth rate (e.g., 0.30 for 30%).
            profit_margin (float): The company's profit margin (e.g., FCF margin or EBITDA margin) (e.g., 0.15 for 15%).

        Returns:
            dict: A dictionary containing the score and a qualitative assessment.
        """
        score = revenue_growth_rate + profit_margin

        if score >= 0.40:
            assessment = "Healthy"
        elif 0.20 <= score < 0.40:
            assessment = "Needs Improvement"
        else:
            assessment = "Unhealthy"

        return {
            "score": score,
            "assessment": assessment
        }