"""Valuation models placeholder implementation.

Provides a minimal `ValuationModels` class with a `calculate_dcf` method used by
tests and it matches expected results for the deterministic unit test.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from decimal import Decimal, getcontext
import math


class ValuationModels:
    @staticmethod
    def calculate_dcf(
            fcf_initial: float,
            growth_rate_5y: float,
            growth_rate_terminal: float,
            wacc: float,
            shares_outstanding: float,
            cash: float = 0.0,
            debt: float = 0.0,
            years: int = 5,
            mid_year: bool = False,
            growth_profile: Optional[List[float]] = None,
            decimal_precision: int = 12,
    ) -> Dict[str, float]:
        """Calculate a simple DCF with discrete yearly growth for `years` years
        and a Gordon Growth terminal value. Values are returned in a dict with
        keys expected by unit tests.
        """
        # Basic validation
        if wacc <= growth_rate_terminal:
            raise ValueError("WACC must be greater than the terminal growth rate.")

        # Use Decimal for better precision in intermediate steps
        getcontext().prec = decimal_precision
        D = Decimal
        fcf_d = D(str(float(fcf_initial)))
        # If a growth_profile is provided, it must be the same length as years
        if growth_profile is not None:
            if len(growth_profile) != years:
                raise ValueError("growth_profile must be of length == years")
        projection: List[Decimal] = []
        for i in range(1, years + 1):
            gr = D(str(float(growth_profile[i - 1]))) if growth_profile is not None else D(str(float(growth_rate_5y)))
            # Calculate using power to avoid iterative rounding differences
            fcf_i = D(str(float(fcf_initial))) * ((D(1) + gr) ** D(i))
            projection.append(cc := fcf_i)

        # Discount the flows. Default to end-of-year discounting unless `mid_year` is True
        pv_fcf_sum = D(0)
        wacc_D = D(str(float(wacc)))
        for idx, f in enumerate(projection, start=1):
            exponent = (D(idx) - D('0.5')) if mid_year else D(idx)
            pv = f / ((D(1) + wacc_D) ** exponent)
            pv_fcf_sum += pv

        # Terminal value via Gordon Growth
        last_fcf = projection[-1] if projection else D(str(float(fcf_initial)))
        growth_terminal_D = D(str(float(growth_rate_terminal)))
        terminal_value = (last_fcf * (D(1) + growth_terminal_D)) / (wacc_D - growth_terminal_D)
        # Discount terminal value according to `mid_year` convention
        exponent_terminal = (D(str(years)) - D('0.5')) if mid_year else D(str(years))
        pv_terminal_value = terminal_value / ((D(1) + wacc_D) ** exponent_terminal)

        enterprise_value = pv_fcf_sum + pv_terminal_value
        equity_value = enterprise_value + D(str(float(cash))) - D(str(float(debt)))
        intrinsic_value_per_share = (equity_value / D(str(float(shares_outstanding)))) if float(shares_outstanding) > 0 else D('NaN')

        # Format/round final values to floats with 2 decimal places (as used in tests)
        def as_float(d: Decimal) -> float:
            if not (d.is_finite()):
                return float('nan')
            return float(round(float(d), 2))

        return {
            'pv_fcf_sum': as_float(pv_fcf_sum),
            'terminal_value': as_float(terminal_value),
            'pv_terminal_value': as_float(pv_terminal_value),
            'enterprise_value': as_float(enterprise_value),
            'equity_value': as_float(equity_value),
            'intrinsic_value_per_share': as_float(intrinsic_value_per_share),
        }


__all__ = ['ValuationModels']
