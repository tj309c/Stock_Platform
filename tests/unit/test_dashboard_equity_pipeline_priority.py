import pandas as pd
import pytest
from src.dashboards.dashboard_equity import EquityDashboard
from src.pipelines.get_market_data import MarketDataPipeline


class DummyFMP:
    def get_company_profile(self, ticker):
        return {'longName': 'FMP Corp', 'currentPrice': 123.45}

    def get_key_metrics(self, ticker):
        return [{'peRatioTTM': 12.34, 'dividendYield': 0.02, 'marketCap': 1_000_000_000}]


class DummyMarket:
    def get_company_info(self, ticker):
        return {'longName': 'Market Corp', 'currentPrice': 9.99}

    def get_key_metrics(self, ticker):
        return {'pe_ratio': 99.99}

    def get_stock_price(self, ticker, period='1y'):
        # generate fake dataframe
        idx = pd.date_range(end=pd.Timestamp.now(), periods=10)
        return pd.DataFrame({'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume': 100}, index=idx)


def test_dashboard_uses_fmp_for_company_info(monkeypatch):
    d = EquityDashboard()
    # Inject fmp and market pipeline dummies
    d.fmp_pipeline = DummyFMP()
    d.market_pipeline = DummyMarket()

    company_info, company_info_error, key_metrics, key_metrics_error, price_data, price_data_error, sentiment_data, sentiment_error = d._fetch_data('AAPL')

    assert company_info is not None
    assert company_info.get('longName') == 'FMP Corp'
    assert key_metrics is not None
    assert key_metrics['pe_ratio'] == 12.34 or key_metrics.get('pe_ratio') == 12.34
    assert price_data is not None


def test_dashboard_falls_back_to_market_pipeline_when_fmp_missing(monkeypatch):
    d = EquityDashboard()
    class EmptyFMP:
        def get_company_profile(self, ticker):
            return None

        def get_key_metrics(self, ticker):
            return None

    d.fmp_pipeline = EmptyFMP()
    d.market_pipeline = DummyMarket()

    company_info, _, key_metrics, _, _, _, _, _ = d._fetch_data('AAPL')
    assert company_info.get('longName') == 'Market Corp'
    assert key_metrics.get('pe_ratio') == 99.99
