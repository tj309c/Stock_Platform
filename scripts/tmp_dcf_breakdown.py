from pprint import pprint
fcf_initial=1000000000
gr=0.15
r=0.09
projection=[fcf_initial*(1+gr)**i for i in range(1,6)]
print('Year FCFs:')
for i,f in enumerate(projection, start=1):
    pv=f/((1+r)**i)
    print(i, f, pv)
print('pv sum', sum(f/((1+r)**i) for i,f in enumerate(projection, start=1)))
# Terminal
last_fcf=projection[-1]
terminal_value=(last_fcf*(1+0.025))/(r-0.025)
pv_terminal=terminal_value/((1+r)**5)
print('last_fcf', last_fcf)
print('terminal_value', terminal_value)
print('pv_terminal', pv_terminal)