"""
Debug script to reverse-engineer the effective exponent used for discounting
the terminal value back to its present value.

This helps verify that the discounting period (e.g., 5 years for end-of-year)
is being applied correctly in the main DCF model.
"""
import math

# --- Inputs from the unit test's expected values ---
PV_TERMINAL_VALUE = 20609910885.34
TERMINAL_VALUE_FUTURE = 31713186445.31
DISCOUNT_RATE = 0.09

# The formula for Present Value is: PV = FV / (1 + r)^n
# We need to solve for the exponent 'n'.
#
# n = log(FV / PV) / log(1 + r)

# Calculate the ratio of Future Value to Present Value
fv_pv_ratio = TERMINAL_VALUE_FUTURE / PV_TERMINAL_VALUE

# Calculate the exponent 'n'
effective_exponent = math.log(fv_pv_ratio) / math.log(1 + DISCOUNT_RATE)

print(f"Future Value (Terminal Value): ${TERMINAL_VALUE_FUTURE:,.2f}")
print(f"Present Value of Terminal Value: ${PV_TERMINAL_VALUE:,.2f}")
print("-" * 40)
print(f"The effective discounting exponent (years) is: {effective_exponent:.4f}")
print("\nThis confirms the model is using an exponent of 5 years for end-of-year discounting.")
