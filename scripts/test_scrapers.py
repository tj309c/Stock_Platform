"""Simple script to test the sentiment scrapers for a list of tickers.
Run this from the project root with the project venv activated:
    .\.venv\Scripts\python.exe scripts\test_scrapers.py
"""
import os, sys
# Ensure project root is in sys.path so imports like `src.*` work when script is run from scripts/ dir
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from src.pipelines.get_sentiment_scraper import SentimentScraper
import json
import sys

def run_tests(tickers=None):
    tickers = tickers or ['AAPL', 'MSFT', 'TSLA', 'AMD']
    s = SentimentScraper()
    for t in tickers:
        print('---', t, '---')
        try:
            headlines, status = s.get_headlines_with_status(t)
            print('Headlines total:', len(headlines))
            print('Status:')
            print(json.dumps(status, indent=2))
            if headlines:
                for h in headlines[:3]:
                    print('-', h['source'], '|', h['published'], '|', h['title'])
        except Exception as e:
            print('Exception while testing', t, e)
        print('\n')

if __name__ == '__main__':
    ticks = sys.argv[1:] if len(sys.argv) > 1 else None
    run_tests(ticks)
