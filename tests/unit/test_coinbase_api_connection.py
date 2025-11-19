import os
import pytest
import pandas as pd
import ccxt

from src.pipelines.get_crypto_data import CryptoDataPipeline


class FakeExchange:
    def __init__(self, opts=None):
        self.opts = opts or {}
        self.id = 'fake'

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        # simple 2-point dataset: timestamp, open, high, low, close, volume
        return [[1609459200000, 1, 2, 0.5, 1.5, 100], [1609545600000, 2, 3, 1.0, 2.5, 200]]

    def fetch_ticker(self, symbol):
        return {'symbol': symbol, 'last': 100, 'bid': 99, 'ask': 101}


class FailingExchange:
    def __init__(self, opts=None):
        self.opts = opts or {}
        self.id = 'failing'

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        raise IndexError('simulated ccxt parsing error')

    def fetch_ticker(self, symbol):
        raise IndexError('simulated ccxt parsing error')


def test_public_fetch_success(monkeypatch):
    """Test that pipeline works in public mode (no API keys) using a mocked exchange."""
    # Patch get_secret to return no keys
    monkeypatch.setattr('src.pipelines.get_crypto_data.get_secret', lambda k: None, raising=False)

    # Patch ccxt to use our FakeExchange for kraken
    monkeypatch.setattr(ccxt, 'kraken', lambda opts=None: FakeExchange(opts))
    pipeline = CryptoDataPipeline(exchange_id='kraken')

    # Fetch OHLCV data and ticker info
    df = pipeline.get_crypto_price('BTC/USDT', timeframe='1d', limit=2)
    ticker = pipeline.get_ticker_info('BTC/USDT')

    assert df is not None and isinstance(df, pd.DataFrame)
    assert 'Close' in df.columns
    assert ticker.get('last') == 100


def test_pem_private_key_not_passed_to_opts(monkeypatch):
    """Ensure that PEM-style private keys are not passed to ccxt opts as 'secret'."""
    # Make get_secret return a PEM-like private key and other credentials
    def fake_get_secret(key):
        if key == 'KRAKEN_API_KEY' or key == 'KRAKEN_API_NAME':
            return 'abc'
        if key == 'KRAKEN_API_SECRET' or key == 'KRAKEN_PRIVATE_KEY':
            return '-----BEGIN PRIVATE KEY-----\nFAKE-PEM\n-----END PRIVATE KEY-----'
        if key == 'KRAKEN_API_PASSWORD':
            return 'pw'
        return None

    monkeypatch.setattr('src.pipelines.get_crypto_data.get_secret', fake_get_secret, raising=False)

    # Capture opts passed to ccxt.kraken when constructor is invoked
    captured = {}
    def coinbase_constructor(opts=None):
        captured['opts'] = opts or {}
        return FakeExchange(opts)

    monkeypatch.setattr(ccxt, 'kraken', coinbase_constructor)
    pipeline = CryptoDataPipeline(exchange_id='kraken')
    assert 'opts' in captured
    # Validate secret is NOT passed in opts when PEM is provided
    assert 'secret' not in captured['opts'], 'PEM private key should not be passed as secret in opts'
    # Basic sanity: pipeline should initialize and return data from FakeExchange
    df = pipeline.get_crypto_price('BTC/USDT')
    assert df is not None


def test_fallback_on_kraken_indexerror(monkeypatch):
    """If Kraken's fetch raises IndexError, ensure fallback tries another public exchange and returns data."""
    # Provide classic secret so exchange is initialized with creds (if code uses them)
    monkeypatch.setattr('src.pipelines.get_crypto_data.get_secret', lambda k: 'classic' if 'KRAKEN' in k else None, raising=False)

    # Kraken fails; bitstamp returns data
    monkeypatch.setattr(ccxt, 'kraken', lambda opts=None: FailingExchange(opts))
    monkeypatch.setattr(ccxt, 'bitstamp', lambda opts=None: FakeExchange(opts))

    pipeline = CryptoDataPipeline(exchange_id='kraken')
    df = pipeline.get_crypto_price('BTC/USDT', timeframe='1d', limit=1)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[-1]['Close'] == 2.5


@pytest.mark.skipif(not os.getenv('EXCHANGE_INTEGRATION_TEST'), reason='Integration test; set EXCHANGE_INTEGRATION_TEST env var to run')
def test_exchange_integration_live():
    """Integration test template that actually connects to ccxt.kraken using real credentials.
    Run only when `EXCHANGE_INTEGRATION_TEST=1` is set and valid secrets are available.
    """
    # This test intentionally uses real network calls and should be enabled only during manual testing.
    pipeline = CryptoDataPipeline(exchange_id='kraken')
    df = pipeline.get_crypto_price('BTC/USDT', timeframe='1d', limit=5)
    ticker = pipeline.get_ticker_info('BTC/USDT')
    assert df is not None and not df.empty
    assert 'Close' in df.columns
    assert isinstance(ticker.get('last'), (int, float))
