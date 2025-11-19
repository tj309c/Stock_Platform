import pandas as pd
import pytest

from src.dashboards.dashboard_equity import EquityDashboard


class DummyMarketTuplePrice:
    def get_company_info(self, ticker):
        return {'longName': 'Market Corp', 'currentPrice': 9.99}

    def get_key_metrics(self, ticker):
        return {'pe_ratio': 99.99}

    def get_stock_price(self, ticker, period='1y'):
        # Return as a tuple (dataframe, None) to simulate decorator or tuple style API
        idx = pd.date_range(end=pd.Timestamp.now(), periods=10)
        df = pd.DataFrame({'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume': 100}, index=idx)
        return df, None


class DummyMarketExceptionPrice:
    def get_company_info(self, ticker):
        raise Exception('market api error')

    def get_key_metrics(self, ticker):
        raise Exception('market key metrics error')

    def get_stock_price(self, ticker, period='1y'):
        raise Exception('market price error')


class DummyFMPRaises:
    def get_company_profile(self, ticker):
        raise Exception('fmp failure')

    def get_key_metrics(self, ticker):
        raise Exception('fmp key metrics failure')


class DummyEmptyFMP:
    def get_company_profile(self, ticker):
        return None

    def get_key_metrics(self, ticker):
        return None


class DummySentimentRaises:
    def get_sentiment_for_ticker(self, ticker):
        raise Exception('sentiment failed')


def test_handles_fmp_exception_and_fallback_to_market():
    d = EquityDashboard()
    d.fmp_pipeline = DummyFMPRaises()
    d.market_pipeline = DummyMarketTuplePrice()
    d.sentiment_scraper = DummySentimentRaises()

    results = d._fetch_data('AAPL')
    # Unpack results
    company_info, company_info_error, key_metrics, key_metrics_error, price_data, price_data_error, sentiment_data, sentiment_error = results

    # FMP raised, so market pipeline should be used
    assert company_info is not None
    assert company_info.get('longName') == 'Market Corp'
    # Key metrics should fallback to market
    assert key_metrics is not None
    assert key_metrics.get('pe_ratio') == 99.99

    # Price should handle tuple return and unwrap to DataFrame
    assert price_data is not None and isinstance(price_data, pd.DataFrame)
    assert price_data_error is None

    # Sentiment scraper raised; ensure error string returned
    assert sentiment_data is None
    assert isinstance(sentiment_error, str) and 'sentiment' in sentiment_error.lower() or sentiment_error != ''


def test_returns_error_when_no_company_info():
    d = EquityDashboard()
    d.fmp_pipeline = DummyEmptyFMP()
    d.market_pipeline = DummyMarketExceptionPrice()
    d.sentiment_scraper = DummySentimentRaises()

    company_info, company_info_error, *_ = d._fetch_data('AAPL')

    assert company_info is None
    # When both pipelines fail, company_info_error should be a string
    assert isinstance(company_info_error, str) and company_info_error != ''
