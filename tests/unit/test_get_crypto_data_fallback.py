import pytest
from pathlib import Path
from src.pipelines.get_crypto_data import CryptoDataPipeline
from src.core.config import AppConfig


class FakeExchange:
    def __init__(self, opts=None):
        self.opts = opts or {}

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        return [[0, 1, 2, 3, 4, 5]]

    def fetch_ticker(self, symbol):
        return {
            'symbol': symbol,
            'last': 100,
            'bid': 99,
            'ask': 101,
            'high': 110,
            'low': 90,
            'quoteVolume': 1000,
            'baseVolume': 10,
            'change': 1,
            'percentage': 1.0,
            'timestamp': 0,
            'datetime': '1970-01-01T00:00:00Z',
        }


class FailingExchange:
    def __init__(self, opts=None):
        self.opts = opts or {}

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        raise IndexError('simulated ECDSA parsing error')

    def fetch_ticker(self, symbol):
        raise IndexError('simulated ECDSA parsing error')


def test_skip_setting_secret_when_pem(monkeypatch):
    # Arrange
    pem_secret = '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBK...'  # truncated
    # Set kraken secrets for pipeline initialization via get_secret lookup
    def fake_get_secret(key):
        if key == 'KRAKEN_API_KEY' or key == 'KRAKEN_API_NAME':
            return 'abc'
        if key == 'KRAKEN_API_SECRET' or key == 'KRAKEN_PRIVATE_KEY':
            return pem_secret
        return None
    monkeypatch.setattr('src.pipelines.get_crypto_data.get_secret', fake_get_secret, raising=False)

    # Patch ccxt.kraken to capture opts
    import ccxt
    monkeypatch.setattr(ccxt, 'kraken', lambda opts=None: FakeExchange(opts))

    pipeline = CryptoDataPipeline(exchange_id='kraken')

    # Act
    exch = pipeline.exchange

    # Assert - opts should not include 'secret' for PEM
    assert not getattr(exch, 'opts', {}).get('secret'), 'PEM secret should not be passed to ccxt exchange opts'


def test_fallback_on_indexerror(monkeypatch):
    # Arrange - set a classic key/secret but ccxt raises IndexError
    monkeypatch.setattr('src.pipelines.get_crypto_data.get_secret', lambda k: 'classicsecretvalue' if 'KRAKEN' in k or 'EXCHANGE_API_KEY' in k else None, raising=False)

    import ccxt
    # Kraken will raise IndexError on fetch_ohlcv
    monkeypatch.setattr(ccxt, 'kraken', lambda opts=None: FailingExchange(opts))
    # Bitstamp will succeed as a public fallback
    monkeypatch.setattr(ccxt, 'bitstamp', lambda opts=None: FakeExchange(opts))

    pipeline = CryptoDataPipeline(exchange_id='kraken')

    # Act
    df = pipeline.get_crypto_price('BTC/USDT', timeframe='1d', limit=1)

    # Assert
    assert df is not None
    assert df.iloc[-1]['Close'] == 4
    
