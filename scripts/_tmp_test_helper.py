import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.config import AppConfig
from src.pipelines.get_crypto_data import CryptoDataPipeline
import ccxt

class FakeExchange:
    def __init__(self, opts=None):
        print('FakeExchange created', opts)
        self.opts = opts or {}
    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        print('FakeExchange.fetch_ohlcv', symbol)
        return [[0,1,2,3,4,5]]

class FailingExchange:
    def __init__(self, opts=None):
        print('FailingExchange created', opts)
        self.opts = opts or {}
    def fetch_ohlcv(self, symbol, timeframe, limit=None):
        print('FailingExchange.fetch_ohlcv; raising')
        raise IndexError('simulated')

ccxt.coinbase = lambda opts=None: FailingExchange(opts)
ccxt.binance = lambda opts=None: FakeExchange(opts)

AppConfig.coinbase_api_name = 'classicapikey'
AppConfig.coinbase_private_key = 'classicsecretvalue'

p = CryptoDataPipeline(exchange_id='coinbase')
print('Calling helper directly...')
res = p._attempt_fallback_fetch(['binance', 'kraken'], 'fetch_ohlcv', 'BTC/USDT', '1d', 1)
print('Helper returned:', res)
