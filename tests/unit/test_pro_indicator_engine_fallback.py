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


def test_manual_vs_pandas_ta_indicator_values(monkeypatch):
    """Compare manual fallback calculations to pandas_ta outputs when pandas_ta is available.

    This test skips if pandas_ta is not installed or doesn't provide `Strategy`.
    """
    pandas_ta = pytest.importorskip('pandas_ta')
    if not hasattr(pandas_ta, 'Strategy'):
        pytest.skip('pandas_ta has no Strategy attribute; skip equality test')

    # Prepare engine and data
    engine = ProIndicatorEngine()
    df = make_price_df(n=200)

    # Compute with pandas-ta Strategy (should be the default path)
    res_strategy = engine.calculate_indicators(df)

    # Now force manual fallback by removing Strategy attribute on the ta module
    monkeypatch.delattr('src.analysis.pro_indicator_engine.ta', 'Strategy', raising=False)
    res_fallback = engine.calculate_indicators(df)

    # helper: compare Series while ignoring NaN at the start
    def equal_series(a, b, tol=1e-6):
        import numpy as _np
        # align indices
        a, b = a.align(b, join='inner')
        mask = ~(_np.isnan(a) | _np.isnan(b))
        if mask.sum() == 0:
            return True
        return _np.allclose(a[mask], b[mask], atol=tol, rtol=0, equal_nan=True)

    # Compare a few indicators numerically
    assert equal_series(res_strategy['RSI_14'], res_fallback['RSI_14'])
    assert equal_series(res_strategy['MACD_12_26_9'], res_fallback['MACD_12_26_9'])
    assert equal_series(res_strategy['MACDh_12_26_9'], res_fallback['MACDh_12_26_9'])
    assert equal_series(res_strategy['STOCHk_14_3_3'], res_fallback['STOCHk_14_3_3'])
    assert equal_series(res_strategy['SMA_50'], res_fallback['SMA_50'])

    # Additional numeric comparisons: EMA, ATR, BBANDS, and Bollinger alias mapping
    assert equal_series(res_strategy['EMA_20'], res_fallback['EMA_20'])
    assert equal_series(res_strategy['ATR_14'], res_fallback['ATR_14'])

    # For Bollinger Bands, pandas-ta may use traditional names like BBU_20_2.0 and BBL_20_2.0
    # while fallback uses `BB_UPPER` and `BB_LOWER`. Try to locate pandas-ta names and compare.
    bbu_cols = [c for c in res_strategy.columns if c.startswith('BBU_')]
    bbl_cols = [c for c in res_strategy.columns if c.startswith('BBL_')]
    if bbu_cols:
        assert 'BB_UPPER' in res_fallback.columns
        assert equal_series(res_strategy[bbu_cols[0]], res_fallback['BB_UPPER'])
    if bbl_cols:
        assert 'BB_LOWER' in res_fallback.columns
        assert equal_series(res_strategy[bbl_cols[0]], res_fallback['BB_LOWER'])

    # Also check the mid band if present
    bbm_cols = [c for c in res_strategy.columns if c.startswith('BBM_') or c.startswith('BB_MIDDLE')]
    if bbm_cols and 'BB_MID' in res_fallback.columns:
        assert equal_series(res_strategy[bbm_cols[0]], res_fallback['BB_MID'])

