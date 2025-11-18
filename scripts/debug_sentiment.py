"""
Developer-only debug script: debug_sentiment.py
Purpose: Local debug harness for the SentimentScraper pipeline. To run, set RUN_DEBUG_SCRIPTS=1
"""

from pathlib import Path
import sys
import os
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.core.config import AppConfig
import tempfile

# Simulate tmp_path
import os

if __name__ == '__main__':
    if os.environ.get('RUN_DEBUG_SCRIPTS') != '1':
        print("Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.")
        sys.exit(0)
    tmp = Path(tempfile.mkdtemp())
    AppConfig.DATA_DIR = tmp
    AppConfig.CACHE_DIR = tmp / 'cache'

    s = SentimentScraper()
    print('initial source weights:', s.source_weights)

    # monkeypatch the gather function
    def fake_gather_with_status(self, ticker, sources=None):
        headlines = [
            {'source': 'Finviz', 'title': 'Company beats expectations', 'score': 0.5, 'published': '2025-01-01'},
            {'source': 'Yahoo', 'title': 'Company reports losses and layoffs', 'score': -0.5, 'published': '2025-01-01'},
        ]
        return headlines, {h['source']: {'state': 'ok'} for h in headlines}

    SentimentScraper._gather_headlines_with_status = fake_gather_with_status

    res1 = s.get_sentiment_for_ticker('AAPL')
    print('res1 score:', res1['score'])
    print('res1 per_source:', res1['per_source'])

    # set weights to Finviz only
    weights = {'Finviz': 1.0, 'Yahoo': 0.0, 'SEC': 0.0}
    print('set weights returns:', s.set_weights(weights))
    print('weights after set:', s.get_weights())

    # clear cache and recompute
    s.clear_cache()
    res2 = s.get_sentiment_for_ticker('AAPL')
    print('res2 score:', res2['score'])
    print('res2 per_source:', res2['per_source'])
