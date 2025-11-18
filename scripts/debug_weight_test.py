import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from src.pipelines.get_sentiment_scraper import SentimentScraper
import pprint

import os

if os.environ.get('RUN_DEBUG_SCRIPTS') != '1':
    print('Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.')
    sys.exit(0)

s = SentimentScraper()

def fake_gather_with_status(self, ticker, sources=None):
    headlines = [
        {'source': 'Finviz', 'title': 'Company beats expectations', 'score': 0.5},
        {'source': 'Yahoo', 'title': 'Company reports losses and layoffs', 'score': -0.5},
    ]
    return headlines, {h['source']: {'state': 'ok'} for h in headlines}

SentimentScraper._gather_headlines_with_status = fake_gather_with_status

func = s.get_sentiment_for_ticker
while hasattr(func, '__wrapped__'):
    func = func.__wrapped__
res1 = func(s, 'AAPL')
print('default:')
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(res1)

s.set_weights({'Finviz': 1.0, 'Yahoo': 0.0, 'SEC': 0.0})
print('weights after set_weights():', s.source_weights)

s.clear_cache()
res2 = func(s, 'AAPL')
print('after weights:')
pp.pprint(res2)

print('---per_source mapping keys---')
print(list(res2['per_source'].keys()))
