"""
Crypto Data Pipeline for Analysis Master
Fetches cryptocurrency market data using ccxt (free exchange data).
Provides OHLCV data, market info, and exchange data for major cryptocurrencies.
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ccxt.base.errors import AuthenticationError
from datetime import datetime, timedelta
import streamlit as st
from src.core.cache_manager import CacheManager
from src.core.config import AppConfig
import logging

logger = logging.getLogger(__name__)


class CryptoDataPipeline:
    """
    Main pipeline for fetching cryptocurrency data using ccxt.
    Supports multiple exchanges with Coinbase as the default.
    """

    def __init__(self, exchange_id: str = 'coinbase'):
        """
        Initialize the crypto data pipeline.

        Args:
            exchange_id: Exchange to use (default: 'coinbase')
        """
        self.exchange_id = exchange_id
        self._exchange = None

    @property
    def exchange(self):
        """Lazy load the exchange connection."""
        if self._exchange is None:
            try:
                exchange_class = getattr(ccxt, self.exchange_id)
                cfg = AppConfig()
                opts = {
                    'enableRateLimit': True,
                    'timeout': 30000,
                }
                # If we have coinbase credentials in AppConfig and the exchange is coinbase, set them
                if self.exchange_id.lower() == 'coinbase':
                    if cfg.coinbase_api_name:
                        opts['apiKey'] = cfg.coinbase_api_name
                    if cfg.coinbase_private_key:
                        sec = cfg.coinbase_private_key
                        if isinstance(sec, str) and ('BEGIN' in sec and 'PRIVATE KEY' in sec): # type: ignore
                            logging.getLogger(__name__).warning(
                                "Coinbase private key appears to be a PEM / Cloud key. Skipping adding it to CCXT opts."
                            )
                        else:
                            opts['secret'] = cfg.coinbase_private_key
                    if cfg.coinbase_api_password:
                        opts['password'] = cfg.coinbase_api_password
                self._exchange = exchange_class(opts)
            except Exception as e:
                st.error(f"Error connecting to {self.exchange_id}: {str(e)}")
                # Fallback to coinbase
                logging.getLogger(__name__).debug("Falling back to coinbase without credentials: %s", e)
                self._exchange = ccxt.coinbase({'enableRateLimit': True})
        return self._exchange

    def _attempt_fallback_fetch(self, fallback_exchanges, func_name: str, *args, **kwargs):
        """
        Attempt a fetch operation (e.g., fetch_ohlcv) across fallback_exchanges. func_name is the method to call.
        Returns result from the first successful fallback or None.
        """
        for ex_id in fallback_exchanges:
            logging.getLogger(__name__).debug("Attempting fallback fetch on '%s' for function '%s'", ex_id, func_name)
            try:
                ex_class = getattr(ccxt, ex_id)
                fallback_ex = ex_class({'enableRateLimit': True})
                func = getattr(fallback_ex, func_name)
                try:
                    res = func(*args, **kwargs)
                    logging.getLogger(__name__).info("Fallback to '%s' succeeded for '%s'", ex_id, func_name)
                    return res
                except Exception as e_fetch:
                    logging.getLogger(__name__).debug("Fallback fetch from '%s' failed for function '%s': %s", ex_id, func_name, e_fetch)
                    continue
            except Exception as e_init:
                logging.getLogger(__name__).debug("Failed to initialize fallback exchange '%s': %s", ex_id, e_init)
                continue
        return None

    @CacheManager.cache_market_data
    def get_crypto_price(
        _self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 365
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candlestick timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data or None if error
        """
        logger.debug(f"get_crypto_price called for {symbol}, timeframe={timeframe}, limit={limit}")
        try:
            # Fetch OHLCV data
            try:
                logger.debug(f"Calling primary exchange '{_self.exchange_id}' to fetch OHLCV for {symbol}")
                ohlcv = _self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            except (AuthenticationError, IndexError) as ae:
                logger.warning(f"Primary exchange '{_self.exchange_id}' failed for {symbol}: {repr(ae)}. Attempting public fallbacks.")
                # Fallback to public exchange if initial exchange requires auth or index error
                fallback_exchanges = ['binance', 'kraken', 'coinbasepro']
                symbol_variants = [symbol]
                if '/USD' in symbol and 'USDT' not in symbol:
                    symbol_variants.append(symbol.replace('/USD', '/USDT'))
                ohlcv = None
                for variant in symbol_variants:
                    logger.debug(f"Attempting fallback fetch for symbol variant '{variant}'")
                    # Correctly call the helper method on the `_self` instance
                    res = CryptoDataPipeline._attempt_fallback_fetch(_self, fallback_exchanges, 'fetch_ohlcv', variant, timeframe, limit=limit)
                    ohlcv = res
                    if ohlcv:
                        st.info(f"Using fallback exchange to fetch ohlcv for {variant}.")
                        symbol = variant
                        break

            if not ohlcv:
                st.warning(f"No data found for {symbol}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            st.error(f"Error fetching price data for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_current_price(_self, symbol: str) -> Optional[float]:
        """
        Get the current price for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Current price as float or None
        """
        try:
            ticker = _self.exchange.fetch_ticker(symbol)
            return ticker.get('last')

        except Exception as e:
            st.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_ticker_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed ticker information for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Dictionary with ticker info or None
        """
        try:
            try:
                ticker = _self.exchange.fetch_ticker(symbol)
            except (AuthenticationError, IndexError) as ae:
                # Authentication errors from ccxt can indicate that the exchange requires API credentials
                msg = str(ae)
                st.error(f"Authentication error fetching ticker for {symbol}: {msg}")
                st.info("If you are using Coinbase (or another exchange with authentication-required endpoints), add COINBASE_API_KEY/COINBASE_API_SECRET to `.streamlit/secrets.toml` or set the keys in the environment.")
                # Attempt to fallback to public exchange to fetch ticker. Try common public exchanges and symbol variants.
                fallback_exchanges = ['binance', 'kraken', 'coinbasepro']
                symbol_variants = [symbol]
                if '/USD' in symbol and 'USDT' not in symbol:
                    symbol_variants.append(symbol.replace('/USD', '/USDT'))
                for variant in symbol_variants:
                    ticker = CryptoDataPipeline._attempt_fallback_fetch(_self, fallback_exchanges, 'fetch_ticker', variant)
                    if ticker:
                        st.info(f"Using fallback exchange to fetch ticker for {variant}.")
                        return {
                            'symbol': ticker.get('symbol'),
                            'last': ticker.get('last'),
                            'bid': ticker.get('bid'),
                            'ask': ticker.get('ask'),
                            'high': ticker.get('high'),
                            'low': ticker.get('low'),
                            'volume': ticker.get('quoteVolume'),
                            'base_volume': ticker.get('baseVolume'),
                            'change': ticker.get('change'),
                            'percentage': ticker.get('percentage'),
                            'timestamp': ticker.get('timestamp'),
                            'datetime': ticker.get('datetime'),
                        }
                return None

            return {
                'symbol': ticker.get('symbol'),
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('quoteVolume'),  # Volume in quote currency
                'base_volume': ticker.get('baseVolume'),  # Volume in base currency
                'change': ticker.get('change'),
                'percentage': ticker.get('percentage'),
                'timestamp': ticker.get('timestamp'),
                'datetime': ticker.get('datetime'),
            }

        except Exception as e:
            # Enhance error message for coinbase auth specifically
            text = str(e)
            if 'apiKey' in text or 'API Key' in text or 'requires "apiKey"' in text:
                st.error(f"Coinbase requires API credentials to access this data. Please add COINBASE_API_KEY/COINBASE_API_SECRET to `.streamlit/secrets.toml` or set the keys as environment variables.")
            else:
                st.error(f"Error fetching ticker info for {symbol}: {text}")
            return None

    @CacheManager.cache_market_data
    def get_orderbook(_self, symbol: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        Get orderbook data for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            limit: Number of levels to fetch

        Returns:
            Dictionary with bids and asks or None
        """
        try:
            orderbook = _self.exchange.fetch_order_book(symbol, limit=limit)

            return {
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp'),
                'datetime': orderbook.get('datetime'),
            }

        except Exception as e:
            st.error(f"Error fetching orderbook for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_market_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get market information and trading limits for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Dictionary with market info or None
        """
        try:
            markets = _self.exchange.load_markets()
            market = markets.get(symbol)

            if not market:
                return None

            return {
                'id': market.get('id'),
                'symbol': market.get('symbol'),
                'base': market.get('base'),
                'quote': market.get('quote'),
                'active': market.get('active'),
                'maker_fee': market.get('maker'),
                'taker_fee': market.get('taker'),
                'limits': market.get('limits'),
                'precision': market.get('precision'),
            }

        except Exception as e:
            st.error(f"Error fetching market info for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_multiple_tickers(
        _self,
        symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch ticker data for multiple cryptocurrencies at once.

        Args:
            symbols: List of trading pairs

        Returns:
            Dictionary mapping symbols to their ticker data
        """
        results = {}

        for symbol in symbols:
            ticker = _self.get_ticker_info(symbol)
            if ticker is not None:
                results[symbol] = ticker

        return results

    def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate various return metrics from price data.

        Args:
            price_data: DataFrame with OHLCV data

        Returns:
            DataFrame with added return columns
        """
        df = price_data.copy()

        # Daily returns
        df['Daily_Return'] = df['Close'].pct_change()

        # Cumulative returns
        df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1

        # Log returns
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))

        return df

    def calculate_volatility(
        self,
        price_data: pd.DataFrame,
        window: int = 30
    ) -> pd.DataFrame:
        """
        Calculate rolling volatility metrics.

        Args:
            price_data: DataFrame with OHLCV data
            window: Rolling window size

        Returns:
            DataFrame with volatility metrics
        """
        df = self.calculate_returns(price_data)

        # Annualized volatility (365 days for crypto, 24/7 market)
        df['Volatility'] = df['Daily_Return'].rolling(window=window).std() * np.sqrt(365)

        return df

    @staticmethod
    def get_available_exchanges() -> List[str]:
        """
        Get list of available exchanges from ccxt.

        Returns:
            List of exchange IDs
        """
        return ccxt.exchanges

    @staticmethod
    def validate_symbol(symbol: str, exchange_id: str = 'coinbase') -> bool:
        """
        Validate if a trading pair exists on an exchange.

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            exchange_id: Exchange to check

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({'enableRateLimit': True})
            markets = exchange.load_markets()
            return symbol in markets
        except:
            return False


# Convenience functions for quick access
def get_crypto_price(symbol: str, timeframe: str = '1d', limit: int = 365) -> Optional[pd.DataFrame]:
    """Quick function to get crypto price data."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_crypto_price(symbol, timeframe, limit)


def get_current_price(symbol: str) -> Optional[float]:
    """Quick function to get current crypto price."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_current_price(symbol)


def get_ticker_info(symbol: str) -> Optional[Dict[str, Any]]:
    """Quick function to get ticker info."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_ticker_info(symbol)


def validate_symbol(symbol: str) -> bool:
    """Quick function to validate a symbol."""
    return CryptoDataPipeline.validate_symbol(symbol)
