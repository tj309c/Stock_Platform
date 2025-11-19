"""
Debug script: test variations of DCF projection/discount conventions
to see which matches the expected constants in tests/unit/test_valuation_models.py
"""

from math import isclose

EXPECTED = {
    'pv_fcf_sum': 5_888_968_244.83,
    'terminal_value': 31_713_186_445.31,
    'pv_terminal_value': 20_609_910_885.34,
}

fcf_initial = 1_000_000_000
growth_rate_5y = 0.15
wacc = 0.09
terminal_g = 0.025
years = 5

candidates = []

# candidate flags
proj_starts = ['T0', 'T1']  # T0: fcf_initial is t0; fcf_t1 = fcf0*(1+g)
                              # T1: fcf_initial is t1 (no growth applied to get t1)

discounting = ['EoY', 'Mid', 'Front', 'Continuous']  # EoY: discount by t, Mid: t-0.5, Front: t-1, Continuous: exp(-r*t)

# rounding options: none, round fcf to 2 decimals, round PV to 2 decimals, round fcf to int
rounding = ['none', 'round_fcf_2', 'round_pv_2', 'round_fcf_int', 'ceil_fcf', 'floor_fcf', 'round_half_up_2']

for proj_start in proj_starts:
    for disc in discounting:
        for rnd in rounding:
            # generate projection
            proj = []
            if proj_start == 'T0':
                fcf = float(fcf_initial)
                for i in range(1, years + 1):
                    fcf = fcf * (1 + growth_rate_5y)
                    if rnd == 'round_fcf_2':
                        fcf = round(fcf, 2)
                    elif rnd == 'round_fcf_int':
                        fcf = round(fcf)
                    elif rnd == 'ceil_fcf':
                        import math
                        fcf = math.ceil(fcf)
                    elif rnd == 'floor_fcf':
                        import math
                        fcf = math.floor(fcf)
                    elif rnd == 'round_half_up_2':
                        # Round half up to 2 decimals
                        from decimal import Decimal, ROUND_HALF_UP
                        fcf = float(Decimal(str(fcf)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    proj.append(fcf)
            else: # T1
                fcf = float(fcf_initial)
                for i in range(1, years + 1):
                    if i == 1:
                        curr = fcf
                    else:
                        curr = curr * (1 + growth_rate_5y)
                    if rnd == 'round_fcf_2':
                        curr = round(curr, 2)
                    elif rnd == 'round_fcf_int':
                        curr = round(curr)
                    elif rnd == 'ceil_fcf':
                        import math
                        curr = math.ceil(curr)
                    elif rnd == 'floor_fcf':
                        import math
                        curr = math.floor(curr)
                    elif rnd == 'round_half_up_2':
                        from decimal import Decimal, ROUND_HALF_UP
                        curr = float(Decimal(str(curr)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    proj.append(curr)

            # Discounting
            pv_list = []
            for idx, f in enumerate(proj, start=1):
                if disc == 'EoY': exponent = idx
                elif disc == 'Mid': exponent = idx - 0.5
                elif disc == 'Front': exponent = idx - 1
                else:
                    # Continuous discounting
                    import math
                    pv = f * math.exp(-wacc * idx)
                    if rnd == 'round_pv_2': pv = round(pv, 2)
                    pv_list.append(pv)
                    continue
                pv = f / ((1 + wacc) ** exponent)
                if rnd == 'round_pv_2': pv = round(pv, 2)
                pv_list.append(pv)

            pv_sum = sum(pv_list)
            last_fcf = proj[-1]
            # terminal
            fcf_t_plus_1 = last_fcf * (1 + terminal_g)
            if rnd == 'round_fcf_2': fcf_t_plus_1 = round(fcf_t_plus_1, 2)
            terminal_value = fcf_t_plus_1 / (wacc - terminal_g)
            if rnd == 'round_fcf_int': terminal_value = round(terminal_value)
            if disc == 'EoY': exp_term = years
            elif disc == 'Mid': exp_term = years - 0.5
            else: exp_term = years - 1
            pv_terminal = terminal_value / ((1 + wacc) ** exp_term)

            candidates.append({
                'proj_start': proj_start,
                'discounting': disc,
                'rounding': rnd,
                'pv_fcf_sum': pv_sum,
                'terminal_value': terminal_value,
                'pv_terminal': pv_terminal,
                'pv_sum_minus_expected': pv_sum - EXPECTED['pv_fcf_sum'],
                'terminal_minus_expected': terminal_value - EXPECTED['terminal_value'],
                'pv_terminal_minus_expected': pv_terminal - EXPECTED['pv_terminal_value'],
            })

# Print the candidates with smallest absolute differences
candidates.sort(key=lambda x: abs(x['pv_sum_minus_expected']) + abs(x['terminal_minus_expected']) + abs(x['pv_terminal_minus_expected']))

for c in candidates[:20]:
    print('proj_start', c['proj_start'], 'discount', c['discounting'], 'rounding', c['rounding'])
    print(' pv_fcf_sum:', c['pv_fcf_sum'], 'diff', c['pv_sum_minus_expected'])
    print(' terminal_value:', c['terminal_value'], 'diff', c['terminal_minus_expected'])
    print(' pv_terminal:', c['pv_terminal'], 'diff', c['pv_terminal_minus_expected'])
    print('---')

# Also print the top candidate exactly
best = candidates[0]
print('\nBest candidate overall:')
for k,v in best.items():
    print(k, v)

# Quick check: compare our current implementation with end-of-year no rounding, T0 projection
print('\nCurrent baseline (T0, EoY, none)')

fcf_initial = 1_000_000_000
proj = [fcf_initial * (1 + growth_rate_5y)**i for i in range(1, years+1)]
print('proj:', proj)
pv = sum([f/((1+wacc)**i) for i,f in enumerate(proj, start=1)])
print('pv', pv)
last_fcf = proj[-1]
terminal = (last_fcf*(1+terminal_g))/(wacc-terminal_g)
pv_terminal=(terminal)/((1+wacc)**years)
print('terminal', terminal)
print('pv_terminal', pv_terminal)
