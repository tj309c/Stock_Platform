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
    monkeypatch.setattr(AppConfig, 'coinbase_private_key', pem_secret, raising=False)
    monkeypatch.setattr(AppConfig, 'coinbase_api_name', 'dummy_key', raising=False)

    # Patch ccxt.coinbase to capture opts
    import ccxt
    monkeypatch.setattr(ccxt, 'coinbase', lambda opts=None: FakeExchange(opts))

    pipeline = CryptoDataPipeline(exchange_id='coinbase')

    # Act
    exch = pipeline.exchange

    # Assert - opts should not include 'secret' for PEM
    assert not getattr(exch, 'opts', {}).get('secret'), 'PEM secret should not be passed to ccxt exchange opts'


def test_fallback_on_indexerror(monkeypatch):
    # Arrange - set a classic key/secret but ccxt raises IndexError
    monkeypatch.setattr(AppConfig, 'coinbase_private_key', 'classicsecretvalue', raising=False)
    monkeypatch.setattr(AppConfig, 'coinbase_api_name', 'classicapikey', raising=False)

    import ccxt
    # Coinbase will raise IndexError on fetch_ohlcv
    monkeypatch.setattr(ccxt, 'coinbase', lambda opts=None: FailingExchange(opts))
    # Binance will succeed
    monkeypatch.setattr(ccxt, 'binance', lambda opts=None: FakeExchange(opts))

    pipeline = CryptoDataPipeline(exchange_id='coinbase')

    # Act
    df = pipeline.get_crypto_price('BTC/USDT', timeframe='1d', limit=1)

    # Assert
    assert df is not None
    assert df.iloc[-1]['Close'] == 4
    
