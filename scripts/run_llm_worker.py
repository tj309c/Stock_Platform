import os
import sys

# Ensure project root is on sys.path when running from the scripts folder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.server.llm_worker import Worker
from src.core.queue_manager import get_global_queue_manager
import logging

if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    qm = get_global_queue_manager()
    parser = argparse.ArgumentParser(description='Run LLM worker')
    parser.add_argument('--once', action='store_true', help='Run a single batch and exit')
    parser.add_argument('--headless-marketwatch', action='store_true', help='Use headless Playwright for MarketWatch scraping')
    parser.add_argument('--max-batch', type=int, default=8, help='Maximum batch size')
    args = parser.parse_args()
    w = Worker(queue_manager=qm, max_batch=args.max_batch)
    try:
        if args.once:
            print('Starting LLM worker in once mode (single batch then exit)')
            if args.headless_marketwatch:
                os.environ['MARKETWATCH_HEADLESS'] = '1'
            w.run(once=True)
        else:
            print('Starting LLM worker (press CTRL+C to exit)')
            if args.headless_marketwatch:
                os.environ['MARKETWATCH_HEADLESS'] = '1'
            w.run()
    except KeyboardInterrupt:
        print('shutting down')
        w.stop()
