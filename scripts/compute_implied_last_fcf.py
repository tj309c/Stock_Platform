expected_terminal = 31713186445.31
wacc = 0.09
g = 0.025
fcf_t_plus_1 = expected_terminal * (wacc - g)
last_fcf = fcf_t_plus_1 / (1 + g)
print('FCF_T+1 implied:', fcf_t_plus_1)
print('Last FCF implied (T):', last_fcf)
# Compare to our projection
fcf_initial = 1_000_000_000
growth = 0.15
proj = [fcf_initial * (1 + growth) ** i for i in range(1, 6)]
print('Our last FCF:', proj[-1])
print('Difference last FCF:', proj[-1] - last_fcf)
