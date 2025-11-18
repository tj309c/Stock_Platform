"""
Debug script to calculate the required Year 5 Free Cash Flow (FCF)
to match the expected Present Value (PV) from the unit tests.
This helps diagnose discrepancies in DCF calculations.
"""

# --- Inputs from the unit test ---
EXPECTED_PV_SUM = 5888968244.83
FCF_INITIAL = 1000000000
GROWTH_RATE = 0.15
DISCOUNT_RATE = 0.09

# --- Calculations ---

# 1. Project the Free Cash Flows for 5 years
projection = [FCF_INITIAL * (1 + GROWTH_RATE) ** i for i in range(1, 6)]

# 2. Calculate the Present Value of each projected FCF
pv_values = [fcf / ((1 + DISCOUNT_RATE) ** i) for i, fcf in enumerate(projection, start=1)]

# 3. Work backwards to find the required FCF for year 5
pv_sum_1_to_4 = sum(pv_values[:4])
needed_pv_for_year5 = EXPECTED_PV_SUM - pv_sum_1_to_4
needed_fcf_for_year5 = needed_pv_for_year5 * ((1 + DISCOUNT_RATE) ** 5)

print(f"Sum of PV for years 1-4: {pv_sum_1_to_4:,.2f}")
print(f"Required PV for year 5:   {needed_pv_for_year5:,.2f}")
print(f"Required FCF for year 5:  {needed_fcf_for_year5:,.2f}")
print(f"Our projected FCF for year 5: {projection[-1]:,.2f}")
print(f"Difference (Needed - Ours): {needed_fcf_for_year5 - projection[-1]:,.2f}")
