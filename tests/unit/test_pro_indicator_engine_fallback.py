import pandas as pd
import numpy as np
import pytest
from src.analysis.pro_indicator_engine import ProIndicatorEngine, ta


def make_price_df(n=60):
    # generate a simple random walk for price
    np.random.seed(0)
    base = 100 + np.cumsum(np.random.normal(0, 1, size=n))
    high = base + np.abs(np.random.normal(0, 1, size=n))
    low = base - np.abs(np.random.normal(0, 1, size=n))
    open_ = base + np.random.normal(0, 0.5, size=n)
    close = base + np.random.normal(0, 0.5, size=n)
    volume = np.random.randint(1, 1000, size=n)
    df = pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
    })
    df.index = pd.date_range(end=pd.Timestamp.now(), periods=n)
    return df


def test_pro_indicator_engine_fallback_computes_indicators(monkeypatch):
    """Ensure fallback path computes RSI, MACD, and Stochastic and alias columns are present.

    The test monkeypatches the imported `ta.Strategy` attribute so the code paths run the manual
    fallback (non-Strategy) calculation code in `ProIndicatorEngine`.
    """
    # Ensure the Strategy attribute is unavailable to trigger fallback path
    monkeypatch.delattr('src.analysis.pro_indicator_engine.ta', 'Strategy', raising=False)

    engine = ProIndicatorEngine()
    df = make_price_df(n=60)

    res = engine.calculate_indicators(df)

    # Columns we expect to exist from the fallback path
    expected_cols = [
        'RSI_14',
        'MACD_12_26_9',
        'MACDh_12_26_9',
        'MACDs_12_26_9',
        'STOCHk_14_3_3',
        'STOCHd_14_3_3',
        'SMA_50',
        'EMA_20',
    ]

    for col in expected_cols:
        assert col in res.columns, f"Expected indicator column '{col}' present in DataFrame"

    # Simple sanity checks for indicator value ranges
    assert res['RSI_14'].min() >= 0
    assert res['RSI_14'].max() <= 100
    assert res['STOCHk_14_3_3'].min() >= 0
    assert res['STOCHk_14_3_3'].max() <= 100

    # MACD columns should be finite and not all NaN
    assert res['MACD_12_26_9'].notna().any()
    assert res['MACDh_12_26_9'].notna().any()
    assert res['MACDs_12_26_9'].notna().any()


if __name__ == '__main__':
    pytest.main([__file__])
