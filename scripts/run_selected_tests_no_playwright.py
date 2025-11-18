import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

import pytest

def main():
    args = ['-q',
                'tests/unit/test_llm_worker.py',
                'tests/unit/test_settings_server_status_sources.py',
                'tests/unit/test_get_sec_rss_feeds_clean.py',
                'tests/unit/test_sentiment_scraper_edgecases.py',
                'tests/unit/test_interactive_dcf.py',
                'tests/unit/test_sentiment_status_and_refresh.py']
    if os.environ.get('DEBUG') == '1' or os.environ.get('DEBUG_TESTS') == '1':
        args = ['-vv','-s'] + args
    sys.exit(pytest.main(args))

if __name__ == '__main__':
    main()
