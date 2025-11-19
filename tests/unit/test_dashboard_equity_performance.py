import pandas as pd
import numpy as np
import time
from src.dashboards.dashboard_equity import EquityDashboard


def _make_large_df(n=1000):
    idx = pd.date_range(end=pd.Timestamp.now(), periods=n, freq='D')
    close = np.linspace(100, 200, n)
    open_ = close - np.random.normal(1, 0.5, n)
    high = np.maximum(open_, close) + np.random.random(n)
    low = np.minimum(open_, close) - np.random.random(n)
    volume = np.random.randint(1000, 10000, n)
    rsi = np.clip(50 + np.sin(np.linspace(0, 10, n)) * 20, 0, 100)
    stoch_k = np.clip(50 + np.cos(np.linspace(0, 6, n)) * 40, 0, 100)
    stoch_d = np.clip(stoch_k + np.random.normal(0, 3, n), 0, 100)
    macd_line = np.linspace(0, 2, n)
    macd_hist = (macd_line - 1) * 0.2
    macd_signal = np.linspace(-0.1, 1.9, n)

    df = pd.DataFrame({
        'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume,
        'RSI': rsi, 'STOCHk': stoch_k, 'STOCHd': stoch_d,
        'MACD_12_26': macd_line, 'MACDh_12_26': macd_hist, 'MACDs_12_26': macd_signal,
    }, index=idx)
    return df


def test_create_price_chart_speed_threshold():
    d = EquityDashboard()
    df = _make_large_df(1000)
    start = time.perf_counter()
    fig = d._create_price_chart('LARGE', df)
    end = time.perf_counter()
    elapsed = end - start
    # Assert that creation time is reasonable; allow generous threshold for CI
    assert elapsed < 1.5, f"Chart creation took too long: {elapsed:.3f}s"
    assert fig is not None
