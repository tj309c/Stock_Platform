from decimal import Decimal, getcontext
getcontext().prec = 28
fcf_initial = Decimal('1000000000')
growth = Decimal('0.15')
wacc = Decimal('0.09')
terminal_g = Decimal('0.025')
years=5

proj = []
val=fcf_initial
for i in range(1, years+1):
    val = val * (1 + growth)
    proj.append(val)

pv_sum = Decimal('0')
for i, f in enumerate(proj, start=1):
    pv = f / ((1 + wacc) ** i)
    pv_sum += pv
    print(i, f, pv)

last_fcf = proj[-1]
terminal = (last_fcf*(1+terminal_g)) / (wacc - terminal_g)
pv_term = terminal / ((1 + wacc) ** years)

print('\nPV sum:', pv_sum)
print('Terminal:', terminal)
print('PV terminal:', pv_term)
print('Enterprise:', pv_sum + pv_term)
