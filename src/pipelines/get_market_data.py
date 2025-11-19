"""
Market Data Pipeline for Analysis Master
Fetches stock market data using yfinance (free baseline data source).
Provides OHLCV data, fundamentals, options chains, and basic company information.
"""

import yfinance as yf
import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import streamlit as st
import requests
from requests.exceptions import RequestException
import json
from json import JSONDecodeError
from src.utils.helpers import retry_on_exception
from src.core.cache_manager import CacheManager
from src.core.config import AppConfig


class MarketDataPipeline:
    """
    Main pipeline for fetching market data using yfinance.
    Serves as the free-tier baseline for all market data needs.
    """

    def __init__(self):
        pass  # No instance variables needed

    @CacheManager.cache_market_data
    def get_stock_price(
        _self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for a stock.

        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                st.warning(f"No data found for ticker: {ticker}")
                return None

            return df

        except Exception as e:
            st.error(f"Error fetching price data for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_current_price(_self, ticker: str) -> Optional[float]:
        """
        Get the current/latest price for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Current price as float or None
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="1m")

            if data.empty:
                # Fallback to daily data
                data = stock.history(period="5d")

            if not data.empty:
                return float(data['Close'].iloc[-1])

            return None

        except Exception as e:
            st.error(f"Error fetching current price for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_multiple_tickers_current_price(_self, tickers: List[str]) -> Dict[str, Optional[float]]:
        """
        Get the current price for a list of tickers.

        Args:
            tickers: List of stock ticker symbols

        Returns:
            Dictionary mapping ticker to its current price.
        """
        prices = {}
        # yfinance doesn't have a great batch current price method, so we iterate.
        # Caching at the get_current_price level makes this efficient.
        for ticker in tickers:
            prices[ticker] = _self.get_current_price(ticker)
        return prices

    @CacheManager.cache_fundamentals
    def get_company_info(_self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to get company info via yfinance and falls back to FMP if Yahoo returns a non-JSON response
        or other transient errors occur. The yfinance call is retried with exponential backoff.
        """
        # Inner function that performs the actual yfinance fetch. It's decorated with the retry decorator
        # so transient errors like JSONDecodeError and RequestException will be retried.
        @retry_on_exception(exceptions=(JSONDecodeError, RequestException, ValueError), tries=3, delay=1.0, backoff=2.0)
        def _fetch_yf_info(local_ticker: str):
            stock = yf.Ticker(local_ticker)
            # Accessing .info may raise JSONDecodeError on malformed responses
            try:
                return stock.info
            except JSONDecodeError as jde:
                logger = logging.getLogger(__name__)
                logger.debug("yfinance JSONDecodeError for %s: %s", local_ticker, jde)
                raise

        try:
            info = _fetch_yf_info(ticker)
        except (JSONDecodeError, RequestException, ValueError) as e:
            # Final failure after retries — attempt to fallback to FMP if configured
            logger = getattr(__import__('logging'), 'getLogger')(__name__)
            logger.debug("Final failure fetching using yfinance for %s: %s", ticker, e)
            if AppConfig().fmp_api_key:
                from src.pipelines.get_fmp_data import FMPDataPipeline
                fmp = FMPDataPipeline()
                profile = fmp.get_company_profile(ticker)
                if profile:
                    return profile
            # Show user-facing error only on final failure
            st.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None

        # If retries were suppressed by the decorator, _fetch_yf_info may return None.
        if info is None:
            # Attempt fallback to FMP if configured
            if AppConfig().fmp_api_key:
                from src.pipelines.get_fmp_data import FMPDataPipeline
                fmp = FMPDataPipeline()
                profile = fmp.get_company_profile(ticker)
                if profile:
                    return profile
            st.error(f"Error fetching company info for {ticker}: yfinance failed and no fallback available.")
            return None

        if not info or len(info) == 0:
            st.warning(f"No company info found for ticker: {ticker}")
            return None

        return info


    @CacheManager.cache_fundamentals
    def get_financials(_self, ticker: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Get financial statements (Income Statement, Balance Sheet, Cash Flow).

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary containing financial DataFrames or None
        """
        try:
            stock = yf.Ticker(ticker)

            financials = {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
                'quarterly_income_statement': stock.quarterly_financials,
                'quarterly_balance_sheet': stock.quarterly_balance_sheet,
                'quarterly_cash_flow': stock.quarterly_cashflow,
            }

            return financials

        except Exception as e:
            st.error(f"Error fetching financials for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_options_data
    def get_options_chain(_self, ticker: str, expiration: Optional[str] = None) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Get options chain data for a specific expiration date.

        Args:
            ticker: Stock ticker symbol
            expiration: Expiration date (YYYY-MM-DD). If None, uses nearest expiration.

        Returns:
            Dictionary with 'calls' and 'puts' DataFrames or None
        """
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options

            if not expirations or len(expirations) == 0:
                st.warning(f"No options available for {ticker}")
                return None

            # Use provided expiration or default to first available
            exp_date = expiration if expiration else expirations[0]

            if exp_date not in expirations:
                st.warning(f"Expiration {exp_date} not available. Using {expirations[0]}")
                exp_date = expirations[0]

            # Get the options chain
            opt = stock.option_chain(exp_date)

            return {
                'calls': opt.calls,
                'puts': opt.puts,
                'expiration': exp_date,
                'available_expirations': list(expirations)
            }

        except Exception as e:
            st.error(f"Error fetching options chain for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_fundamentals
    def get_key_metrics(_self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Extract key financial metrics from company info.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary of key metrics or None
        """
        try:
            info = _self.get_company_info(ticker)

            if not info:
                return None

            # Extract key metrics with safe fallbacks
            metrics = {
                # Valuation Metrics
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'ev_to_ebitda': info.get('enterpriseToEbitda'),
                'ev_to_revenue': info.get('enterpriseToRevenue'),

                # Profitability Metrics
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),

                # Growth Metrics
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),

                # Financial Health
                'current_ratio': info.get('currentRatio'),
                'debt_to_equity': info.get('debtToEquity'),
                'quick_ratio': info.get('quickRatio'),

                # Dividend Metrics
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),

                # Other
                'beta': info.get('beta'),
                '52week_high': info.get('fiftyTwoWeekHigh'),
                '52week_low': info.get('fiftyTwoWeekLow'),
                'shares_outstanding': info.get('sharesOutstanding'),
            }

            return metrics

        except Exception as e:
            st.error(f"Error extracting key metrics for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_fundamentals
    def get_earnings_dates(_self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Get upcoming and historical earnings dates.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with earnings dates or None
        """
        try:
            stock = yf.Ticker(ticker)
            earnings_dates = stock.earnings_dates

            if earnings_dates is None or earnings_dates.empty:
                st.warning(f"No earnings dates found for {ticker}")
                return None

            return earnings_dates

        except Exception as e:
            st.error(f"Error fetching earnings dates for {ticker}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_multiple_tickers_historical_data(
        _self,
        tickers: List[str],
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple tickers at once.

        Args:
            tickers: List of ticker symbols
            period: Data period
            interval: Data interval

        Returns:
            Dictionary mapping tickers to their DataFrames
        """
        results = {}

        for ticker in tickers:
            data = _self.get_stock_price(ticker, period=period, interval=interval)
            if data is not None:
                results[ticker] = data

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
            window: Rolling window size in days

        Returns:
            DataFrame with volatility metrics
        """
        df = self.calculate_returns(price_data)

        # Annualized volatility (252 trading days)
        df['Volatility'] = df['Daily_Return'].rolling(window=window).std() * np.sqrt(252)

        return df

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """
        Validate if a ticker exists and has data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Check if we got valid info back
            if info and 'regularMarketPrice' in info or 'currentPrice' in info:
                return True

            # Alternative check using history
            hist = stock.history(period="5d")
            return not hist.empty

        except:
            return False


# Convenience functions for quick access
def get_stock_price(ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Quick function to get stock price data."""
    pipeline = MarketDataPipeline()
    return pipeline.get_stock_price(ticker, period, interval)


def get_current_price(ticker: str) -> Optional[float]:
    """Quick function to get current price."""
    pipeline = MarketDataPipeline()
    return pipeline.get_current_price(ticker)


def get_company_info(ticker: str) -> Optional[Dict[str, Any]]:
    """Quick function to get company info."""
    pipeline = MarketDataPipeline()
    return pipeline.get_company_info(ticker)


def validate_ticker(ticker: str) -> bool:
    """Quick function to validate a ticker."""
    return MarketDataPipeline.validate_ticker(ticker)
