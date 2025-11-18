import sys
from pathlib import Path

# Add project root to the Python path to allow imports from `src`
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import types
import pandas as pd

# Minimal fake streamlit for tests that only need `secrets.get` and cache_data behavior
streamlit = types.ModuleType('streamlit')

class _Secrets(dict):
    def get(self, key, default=None):
        return super().get(key, default)

streamlit.secrets = _Secrets()

# Simple cache_data decorator stub and clear function to mimic Streamlit's API
class _CacheData:
    def __init__(self):
        self._store = {}
    def __call__(self, ttl=None, show_spinner=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # naive in-memory cache by key
                # make args/kwargs hashable by converting lists to tuples, sets/dicts appropriately
                def make_hashable(x):
                    if isinstance(x, (list, tuple)):
                        return tuple(make_hashable(v) for v in x)
                    if isinstance(x, dict):
                        return tuple(sorted((k, make_hashable(v)) for k, v in x.items()))
                    if isinstance(x, set):
                        return tuple(sorted(make_hashable(v) for v in x))
                    try:
                        hash(x)
                        return x
                    except Exception:
                        return repr(x)

                key = (func.__name__, make_hashable(args), make_hashable(kwargs))
                if key in self._store:
                    return self._store[key]
                val = func(*args, **kwargs)
                self._store[key] = val
                return val
            return wrapper
        return decorator
    def clear(self):
        self._store.clear()

streamlit.cache_data = _CacheData()
sys.modules['streamlit'] = streamlit

def _streamlit_mock_function(*args, **kwargs):
    """A no-op function to mock Streamlit UI calls."""
    pass

streamlit.error = _streamlit_mock_function
streamlit.warning = _streamlit_mock_function
streamlit.info = _streamlit_mock_function
streamlit.success = _streamlit_mock_function

# Minimal fake yfinance module to avoid heavy dependency during unit tests
# Tests don't need full yfinance behavior for these unit tests; provide a minimal stub
def _ticker_history_stub(*args, **kwargs):
    # return a simple DataFrame with 'Close' column
    return pd.DataFrame({'Close': [100.0, 101.0]}, index=pd.to_datetime(['2025-01-01','2025-01-02']))

class _Ticker:
    def __init__(self, symbol):
        self.symbol = symbol
    def history(self, *args, **kwargs):
        return _ticker_history_stub()


yfinance = types.ModuleType('yfinance')
yfinance.Ticker = _Ticker
sys.modules['yfinance'] = yfinance

# Minimal fake openai module for unit tests that want to patch ChatCompletion.create
try:
    import openai
except Exception:
    openai = types.ModuleType('openai')
    class _ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            raise Exception('OpenAI stub not configured')
    openai.ChatCompletion = _ChatCompletion
    sys.modules['openai'] = openai

# Minimal fake playwright module: add sync_playwright() context function if e2e tests run
# For unit tests, not necessary, but present to avoid import errors if e2e run erroneously
try:
    # If Playwright is installed, do nothing and use the real one
    import importlib
    importlib.import_module('playwright')
except Exception:
    # Provide a minimal stub implementation to avoid errors when Playwright is not available.
    # This stub implements only the methods used by tests/e2e/test_settings_flow.py
    class DummyPage:
        def goto(self, url):
            return None
        def is_visible(self, selector):
            return False
        def click(self, selector):
            return None
        def select_option(self, selector, value=None):
            return None
        def wait_for_selector(self, selector, timeout=None):
            return None

    class DummyBrowser:
        def new_page(self):
            return DummyPage()
        def close(self):
            return None

    class DummyChromium:
        def launch(self, headless=True):
            return DummyBrowser()

    class _SyncPlaywrightContext:
        def __enter__(self):
            return types.SimpleNamespace(chromium=DummyChromium())
        def __exit__(self, exc_type, exc, tb):
            return False

    playwright = types.ModuleType('playwright')
    playwright.sync_api = types.ModuleType('playwright.sync_api')
    playwright.sync_api.sync_playwright = lambda: _SyncPlaywrightContext()
    sys.modules['playwright'] = playwright
    sys.modules['playwright.sync_api'] = playwright.sync_api
