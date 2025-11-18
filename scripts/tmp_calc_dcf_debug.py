fcf_initial=1000000000
gr=0.15
r=0.09
projection=[fcf_initial*(1+gr)**i for i in range(1,6)]
print('projection:', projection)
pv=sum(f/(1+r)**i for i,f in enumerate(projection, start=1))
print('pv_standard', pv)
last_fcf=projection[-1]
terminal_value=(last_fcf*(1+0.025))/(r-0.025)
pv_terminal=terminal_value/((1+r)**5)
print('terminal_value', terminal_value)
print('pv_terminal', pv_terminal)
enterprise=pv+pv_terminal
print('enterprise', enterprise)
equity=enterprise+500000000-200000000
print('equity', equity)
print('intrinsic', equity/500000000)

print('\n--- Implied Growth Calculation ---')
fcf_initial_val = 1000000000
last_fcf_val = 2011080116.044049

# Calculate the implied compound annual growth rate (CAGR)
factor = (last_fcf_val / fcf_initial_val) ** (1/5)
implied_annual_growth = factor - 1
print(f"Implied annual growth rate: {implied_annual_growth:.2%}")