"""Data pipeline for fetching cryptocurrency data using ccxt."""

import streamlit as st
import pandas as pd
import ccxt
import logging
from typing import Dict, Optional
from src.core.config import get_secret

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class CryptoDataPipeline:
    """
    A data pipeline for fetching cryptocurrency data from exchanges using ccxt.
    Handles exchange initialization, data fetching, and basic data processing.
    """

    def __init__(self, exchange_id: str = 'kraken'):
        """
        Initializes the data pipeline with a specific exchange.

        Args:
            exchange_id (str): The ID of the exchange to connect to (e.g., 'coinbase', 'binance').
        """
        self.exchange_id = exchange_id
        self.logger = logging.getLogger(__name__)
        self.exchange = self._get_exchange()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_ticker_info(_self, symbol: str) -> Optional[Dict]:
        """
        Fetches the latest ticker information for a given symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USD').

        Returns:
            dict: A dictionary containing ticker information, or None if an error occurs.
        """
        if not _self.exchange:
            return None
        try:
            ticker = _self.exchange.fetch_ticker(symbol)
            return ticker
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.BadSymbol) as e:
            _self.logger.error(f"Failed to fetch ticker for {symbol}: {e}")
            return None

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_crypto_price(_self, symbol: str, timeframe: str = '1d', limit: int = 365) -> Optional[pd.DataFrame]:
        """
        Fetches historical OHLCV data for a crypto symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USD').
            timeframe (str): The timeframe for the data (e.g., '1h', '1d').
            limit (int): The number of data points to fetch.

        Returns:
            pd.DataFrame: A DataFrame with OHLCV data, or None if an error occurs.
        """
        if not _self.exchange or (not getattr(_self.exchange, 'has', {}).get('fetchOHLCV') and not hasattr(_self.exchange, 'fetch_ohlcv')):
            _self.logger.warning(f"{_self.exchange_id} does not support fetching OHLCV data.")
            return None
        try:
            ohlcv = _self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except IndexError as e:
            # Some exchanges may raise IndexError from within CCXT when parsing keys or the payload
            _self.logger.warning(f"IndexError fetching OHLCV on {getattr(_self.exchange, 'id', _self.exchange_id)}: {e} - trying fallback exchanges")
            # Try fallback exchanges (public CCXT endpoints) — prefer Kraken and other lightweight public exchanges.
            fallback_exchanges = ['kraken', 'bitstamp', 'bitfinex']
            for fex in fallback_exchanges:
                # Skip trying the same exchange as we already attempted above
                if fex == _self.exchange_id:
                    continue
                try:
                    fallback_cls = getattr(ccxt, fex)
                    fallback_exchange = fallback_cls()
                    ohlcv = fallback_exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    return df
                except Exception:
                    # Ignore errors and try next fallback
                    continue
            return None
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.BadSymbol) as e:
            _self.logger.error(f"Failed to fetch OHLCV data for {symbol}: {e}")
            return None

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_market_info(_self, symbol: str) -> Optional[Dict]:
        """
        Fetches market information for a given symbol.

        Args:
            symbol (str): The trading pair symbol.

        Returns:
            dict: Market information, or None if an error occurs.
        """
        if not _self.exchange:
            return None
        try:
            _self.exchange.load_markets()
            market = _self.exchange.market(symbol)
            return market
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.BadSymbol) as e:
            _self.logger.error(f"Failed to fetch market info for {symbol}: {e}")
            return None

    @st.cache_data(ttl=60)  # Cache for 1 minute (more frequent updates)
    def get_orderbook(_self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """
        Fetches the order book for a given symbol.

        Args:
            symbol (str): The trading pair symbol.
            limit (int): The number of bids and asks to retrieve.

        Returns:
            dict: A dictionary with 'bids' and 'asks', or None if an error occurs.
        """
        if not _self.exchange or (not getattr(_self.exchange, 'has', {}).get('fetchOrderBook') and not hasattr(_self.exchange, 'fetch_order_book')):
            _self.logger.warning(f"{_self.exchange_id} does not support fetching order books.")
            return None
        try:
            orderbook = _self.exchange.fetch_order_book(symbol, limit=limit)
            return orderbook
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.BadSymbol) as e:
            _self.logger.error(f"Failed to fetch order book for {symbol}: {e}")
            return None

    def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Calculates daily and cumulative returns."""
        returns_df = price_data.copy()
        returns_df['Daily_Return'] = returns_df['Close'].pct_change()
        returns_df['Cumulative_Return'] = (1 + returns_df['Daily_Return']).cumprod() - 1
        return returns_df

    def calculate_volatility(self, price_data: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """Calculates rolling volatility."""
        volatility_df = price_data.copy()
        returns = volatility_df['Close'].pct_change()
        # Annualize for crypto (365 days)
        volatility_df['Volatility'] = returns.rolling(window=window).std() * (365 ** 0.5)
        return volatility_df

    def _get_exchange(self) -> Optional[ccxt.Exchange]:
        """
        Initializes and returns an exchange instance with API keys if available.
        """
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            
            # Generic mapping for exchange API keys and secrets (Binance, etc.) - prefer explicit exchange-specific secrets
            api_key = get_secret(f"{self.exchange_id.upper()}_API_KEY") or get_secret("EXCHANGE_API_KEY")
            secret = get_secret(f"{self.exchange_id.upper()}_API_SECRET") or get_secret("EXCHANGE_API_SECRET")

            # Do not pass PEM-formatted private keys as 'secret' to CCXT - CCXT expects API secret strings for classic keys
            if api_key and secret:
                # Detect PEM-like secret values (BEGIN ... PRIVATE KEY) and skip including them in opts
                if isinstance(secret, str) and ('BEGIN' in secret and 'PRIVATE KEY' in secret):
                    self.logger.warning("Detected PEM private key in secrets; not passing 'secret' to CCXT opts.")
                    return exchange_class({ 'apiKey': api_key })
                # Normal key/secret pair
                self.logger.info(f"Initializing {self.exchange_id} with API credentials.")
                return exchange_class({
                    'apiKey': api_key,
                    'secret': secret,
                })
            else:
                self.logger.warning(f"API credentials not found for {self.exchange_id}. Initializing in public mode.")
                return exchange_class()
        except AttributeError:
            self.logger.error(f"Exchange '{self.exchange_id}' not found in ccxt.")
            return None
        except Exception as e:
            self.logger.error(f"Failed to initialize exchange {self.exchange_id}: {e}")
            return None
