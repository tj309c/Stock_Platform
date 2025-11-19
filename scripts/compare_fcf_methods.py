from decimal import Decimal, getcontext
from math import pow

fcf_initial = 1_000_000_000
growth = 0.15

# float iterative
f = float(fcf_initial)
for i in range(1,6):
    f = f*(1+growth)
f_iterative = f

# float power
f_power = float(fcf_initial * ((1+growth)**5))

# Decimal iterative
getcontext().prec = 28
D = Decimal
f = D(str(fcf_initial))
for i in range(1,6):
    f = f*(D(1)+D(str(growth)))
f_dec_iter = f

# Decimal power
f_dec_pow = D(str(fcf_initial)) * (D(1)+D(str(growth)))**D(5)

print('float iterative f5:', f_iterative)
print('float pow f5:      ', f_power)
print('decimal iterative f5:', f_dec_iter)
print('decimal pow f5:      ', f_dec_pow)

# Differences
print('\nDifferences from float iterative:')
print('float pow diff: ', f_power - f_iterative)
print('decimal iter diff:', float(f_dec_iter) - f_iterative)
print('decimal pow diff:  ', float(f_dec_pow) - f_iterative)
