import pytest
from unittest.mock import patch
import json
from src.pipelines.get_market_data import MarketDataPipeline
from src.core.config import AppConfig


@patch.object(AppConfig, '__init__', lambda self: setattr(self, 'fmp_api_key', None))
def test_get_company_info_retry(monkeypatch):
    """Test that get_company_info retries on a JSONDecodeError and succeeds on retry."""

    class MockTicker:
        def __init__(self):
            self._count = 0

        @property
        def info(self):
            self._count += 1
            if self._count == 1:
                raise json.JSONDecodeError('Expecting value', '', 0)
            return {'symbol': 'AAPL', 'longName': 'Apple Inc.'}

    mock_ticker = MockTicker()
    monkeypatch.setattr('yfinance.Ticker', lambda ticker: mock_ticker)
    pipeline = MarketDataPipeline()
    info = pipeline.get_company_info('AAPL')
    assert info is not None
    assert info.get('longName') == 'Apple Inc.'


def test_get_company_info_fallback_to_fmp(monkeypatch):
    """Test that get_company_info falls back to FMP when yfinance keeps failing."""
    # yfinance always raises JSONDecodeError
    class MockTickerAlwaysFail:
        @property
        def info(self):
            raise json.JSONDecodeError('Expecting value', '', 0)

    monkeypatch.setattr('yfinance.Ticker', lambda ticker: MockTickerAlwaysFail())

    # Patch AppConfig to return a fake FMP API key and patch FMPDataPipeline.get_company_profile
    from src.core.config import AppConfig
    from src.pipelines.get_fmp_data import FMPDataPipeline

    monkeypatch.setattr(AppConfig, '__init__', lambda self: setattr(self, 'fmp_api_key', 'TEST_KEY'))
    monkeypatch.setattr(FMPDataPipeline, 'get_company_profile', lambda self, ticker: {'symbol': 'AAPL', 'longName': 'Apple Inc. (FMP)'})

    pipeline = MarketDataPipeline()
    info = pipeline.get_company_info('AAPL')
    assert info is not None
    assert info.get('longName') == 'Apple Inc. (FMP)'
