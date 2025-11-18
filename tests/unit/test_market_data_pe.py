import pandas as pd
import yfinance as yf
from src.pipelines.get_market_data import MarketDataPipeline


def test_get_historical_pe_ratio_basic(monkeypatch):
    pipeline = MarketDataPipeline()

    # Create synthetic price_df to be returned by get_stock_price
    idx = pd.date_range('2025-01-01', periods=3, freq='D')
    price_df = pd.DataFrame({'Close': [100.0, 105.0, 110.0]}, index=idx)
    monkeypatch.setattr(pipeline, 'get_stock_price', lambda ticker, period='1y', interval='1d', start=None, end=None: price_df)

    # Create a fake financials to allow TTM EPS calculation
    class FakeTicker:
        def __init__(self):
            self.info = {'sharesOutstanding': 1_000_000, 'trailingEps': 2.0}
            # quarterly_income_statement with index as 'Net Income' to compute EPS
            self.quarterly_financials = pd.DataFrame({'2024-09-30': [2000000], '2024-06-30': [1500000], '2024-03-31': [1800000], '2023-12-31': [1900000]}, index=['Net Income'])
            self.quarterly_earnings = pd.DataFrame({'Earnings': [2000000, 1500000, 1800000, 1900000]}, index=pd.to_datetime(['2024-09-30','2024-06-30','2024-03-31','2023-12-31']))

    monkeypatch.setattr(yf, 'Ticker', lambda ticker: FakeTicker())

    # Use the pipeline method - should compute peRatio
    pe_df = pipeline.get_historical_pe_ratio('AAPL', period='1mo', interval='1d')
    assert pe_df is not None
    assert isinstance(pe_df, pd.DataFrame)
    assert 'peRatio' in pe_df.columns
    assert pe_df['peRatio'].dropna().shape[0] > 0
