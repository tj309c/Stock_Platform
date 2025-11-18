"""
Small utility script that computes historical P/E using the MarketDataPipeline (yfinance fallback)
and optionally writes to CSV for inspection. This enables the dashboard to avoid relying on external
fundamental APIs for P/E if they are restricted.

Usage:
    python scripts/compute_historical_pe.py TICKER [--period 1y] [--interval 1d] [--out path.csv]

Examples:
    python scripts/compute_historical_pe.py AAPL --period 2y --interval 1d --out aapl_pe.csv
"""
import argparse
import pandas as pd
from src.pipelines.get_market_data import MarketDataPipeline


def main():
    parser = argparse.ArgumentParser(description='Compute historical P/E using yfinance fallback')
    parser.add_argument('ticker', help='Ticker symbol (e.g., AAPL)')
    parser.add_argument('--period', default='1y', help='Period (1y, 2y, 5y, etc.)')
    parser.add_argument('--interval', default='1d', help='Interval (1d, 1wk, 1mo, etc.)')
    parser.add_argument('--out', default=None, help='Optional path to output CSV')
    args = parser.parse_args()

    pipeline = MarketDataPipeline()
    pe_df = pipeline.get_historical_pe_ratio(args.ticker, period=args.period, interval=args.interval)
    if pe_df is None or pe_df.empty:
        print('No P/E data available for', args.ticker)
        return

    print(pe_df.head())
    if args.out:
        pe_df.to_csv(args.out)
        print('Saved to', args.out)


if __name__ == '__main__':
    main()
