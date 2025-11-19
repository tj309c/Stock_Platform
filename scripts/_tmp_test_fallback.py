import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.config import AppConfig
from src.pipelines.get_crypto_data import CryptoDataPipeline

class FakeExchange:
    def __init__(self, opts=None):
        print('FakeExchange created with opts', opts)
        self.opts = opts or {}

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        print('FakeExchange.fetch_ohlcv called for', symbol)
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
        print('FailingExchange created with opts', opts)
        self.opts = opts or {}

    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        print('FailingExchange.fetch_ohlcv called; raising IndexError')
        raise IndexError('simulated ECDSA parsing error')

    def fetch_ticker(self, symbol):
        raise IndexError('simulated ECDSA parsing error')

# Monkeypatch
import ccxt
ccxt.coinbase = lambda opts=None: FailingExchange(opts)
ccxt.binance = lambda opts=None: FakeExchange(opts)

# Setup config
AppConfig.coinbase_api_name = 'classicapikey'
AppConfig.coinbase_private_key = 'classicsecretvalue'

p = CryptoDataPipeline(exchange_id='coinbase')
print('Requesting ohlcv...')
df = p.get_crypto_price('BTC/USDT', timeframe='1d', limit=1)
print('Result DF:', df)

# Directly test the helper fallback method to ensure it invokes binance fallback
print('Testing _attempt_fallback_fetch directly')
res = p._attempt_fallback_fetch(['binance'], 'fetch_ohlcv', 'BTC/USDT', '1d', 1)
print('Direct attempt_fallback_fetch res:', res)