"""
Debug script to test a DCF valuation with a variable, multi-year growth profile.
This is useful for modeling companies whose growth is expected to slow over time.
"""

import sys
from pathlib import Path

# Add the project root to the Python path to allow imports from `src`
sys.path.append(str(Path(__file__).parent.parent))
from src.analysis.valuation_models import ValuationModels

# --- Inputs ---
FCF_INITIAL = 1_000_000_000
WACC = 0.09
TERMINAL_GROWTH_RATE = 0.025

# A list of growth rates, one for each year of the projection
GROWTH_PROFILE = [0.15, 0.12, 0.10, 0.07, 0.05]
PROJECTION_YEARS = len(GROWTH_PROFILE)

print("--- Using Main Valuation Engine ---")

# Use the main valuation model from the application for consistency
dcf_results = ValuationModels.calculate_dcf(
    fcf_initial=FCF_INITIAL,
    growth_rate_5y=0,  # Not used when growth_profile is provided
    growth_rate_terminal=TERMINAL_GROWTH_RATE,
    wacc=WACC,
    shares_outstanding=1, # Set to 1 for easy enterprise value check
    cash=0,
    debt=0,
    years=PROJECTION_YEARS,
    growth_profile=GROWTH_PROFILE
)

print(f"PV of FCFs:              ${dcf_results['pv_fcf_sum']:,.2f}")
print(f"PV of Terminal Value:    ${dcf_results['pv_terminal_value']:,.2f}")
print(f"Calculated Enterprise Value: ${dcf_results['enterprise_value']:,.2f}")
print("-" * 35)
