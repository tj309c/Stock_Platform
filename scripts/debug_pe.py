"""
Developer-only debug script: debug_pe.py
Purpose: Quick inspection and debugging of yfinance ticker info, quarterly earnings and financials.
This script is intended for local developer troubleshooting only. To run it, set environment variable:
    RUN_DEBUG_SCRIPTS=1
"""

import os
import sys
import os
import sys
import pandas as pd
import yfinance as yf

def debug_ticker(ticker='AAPL'):
    stock = yf.Ticker(ticker)
    print('info keys present:', 'trailingEps' in stock.info, 'sharesOutstanding' in stock.info)
    print('trailingEps:', stock.info.get('trailingEps'))
    print('sharesOutstanding:', stock.info.get('sharesOutstanding'))
    print('\nquarterly_earnings:')
    print(stock.quarterly_earnings)
    print('\nquarterly_financials:')
    print(stock.quarterly_financials)
    print('\nfinancials:')
    print(stock.financials)
    print('\nearnings:')
    print(stock.earnings)

if __name__ == '__main__':
    if os.environ.get('RUN_DEBUG_SCRIPTS') != '1' and os.environ.get('DEBUG') != '1':
        print("Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.")
        sys.exit(0)
    debug_ticker()
