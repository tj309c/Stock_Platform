expected_terminal = 31713186445.31
wacc = 0.09
g=0.025
ftp1 = expected_terminal * (wacc - g)
print('FCF T+1 expected:', ftp1)
print('last fcf expected:', ftp1/(1+g))
