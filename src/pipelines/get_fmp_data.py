"""
get_fmp_data.py

Client for fetching data from the Financial Modeling Prep (FMP) API.
Requires an FMP_API_KEY in the secrets.toml file.
"""
import requests
import logging
from requests.exceptions import RequestException
import streamlit as st
from typing import List, Dict, Optional

from src.core.config import AppConfig
from src.core.cache_manager import CacheManager
from src.utils.helpers import retry_on_exception

class FMPDataPipeline:
    """
    Provides methods to fetch data from the Financial Modeling Prep API.
    """
    def __init__(self):
        self.api_key = AppConfig().fmp_api_key
        if not self.api_key:
            st.warning("FMP API key not found. FMP data will be unavailable.", icon="⚠️")
        self.base_url = "https://financialmodelingprep.com/api/v3"

    @retry_on_exception(exceptions=(RequestException, ValueError), tries=3, delay=1.0, backoff=2.0)
    def _make_request(_self, endpoint: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """Helper function to make requests to the FMP API."""
        if not _self.api_key:
            return None

        if params is None:
            params = {}
        params['apikey'] = _self.api_key

        try:
            response = requests.get(f"{_self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as nde:
                # JSON decode error - allow retry decorator to capture it so that transient issues are retried.
                # Log debug info with a snippet to help root cause analysis in logs.
                text_snippet = (response.text or '')[:500]
                logger = logging.getLogger(__name__)
                logger.debug("JSON decode error for FMP endpoint '%s': %s. Response preview: %s", endpoint, nde, text_snippet)
                # Only show a Streamlit error message after final failure (handled in decorator or caller).
                raise
            if isinstance(data, dict) and data.get('Error Message'):
                st.error(f"FMP API Error: {data['Error Message']}")
                return None
            return data
        except requests.exceptions.RequestException as re:
            # Let the decorator handle transient network errors and apply retry/backoff.
            logger = logging.getLogger(__name__)
            logger.debug("FMP API request exception for endpoint '%s': %s", endpoint, re, exc_info=True)
            raise

    @CacheManager.cache_fundamentals
    def get_company_profile(_self, ticker: str) -> Optional[Dict]:
        """
        Retrieves the company profile for a given ticker.
        """
        endpoint = f"profile/{ticker.upper()}"
        data = _self._make_request(endpoint)
        return data[0] if data else None

    @CacheManager.cache_analysis
    def get_analyst_consensus(_self, ticker: str) -> Optional[Dict]:
        """
        Retrieves analyst ratings and consensus estimates.
        """
        endpoint = f"analyst-estimates/{ticker.upper()}"
        data = _self._make_request(endpoint)
        return data[0] if data else None

    @CacheManager.cache_fundamentals
    def get_earnings_surprises(_self, ticker: str) -> Optional[List[Dict]]:
        """
        Retrieves historical earnings surprises.
        """
        endpoint = f"earnings-surprises/{ticker.upper()}"
        return _self._make_request(endpoint)

    @CacheManager.cache_fundamentals
    def get_key_metrics(_self, ticker: str, period: str = "annual", limit: int = 10) -> Optional[List[Dict]]:
        """
        Retrieves key financial metrics for a company.
        
        Args:
            ticker (str): The stock ticker.
            period (str): 'annual' or 'quarter'.
            limit (int): Number of periods to retrieve.
        """
        endpoint = f"key-metrics/{ticker.upper()}"
        params = {"period": period, "limit": limit}
        return _self._make_request(endpoint, params)
