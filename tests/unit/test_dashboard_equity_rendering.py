import pandas as pd
import numpy as np

from src.dashboards.dashboard_equity import EquityDashboard


def _make_indicators_df(n=30):
    idx = pd.date_range(end=pd.Timestamp.now(), periods=n, freq='D')
    # Simple upward moving price for candlestick
    close = np.linspace(100, 120, n)
    open_ = close - np.random.normal(0.5, 0.5, n)
    high = np.maximum(open_, close) + np.random.random(n)
    low = np.minimum(open_, close) - np.random.random(n)
    volume = np.random.randint(1000, 5000, n)

    # Indicators: RSI, Stochastic %K/%D, MACD (line, hist, signal)
    rsi = np.clip(50 + np.sin(np.linspace(0, 3.14, n)) * 20, 0, 100)
    stoch_k = np.clip(50 + np.cos(np.linspace(0, 3.14, n)) * 40, 0, 100)
    stoch_d = np.clip(stoch_k + np.random.normal(0, 3, n), 0, 100)
    macd_line = np.linspace(0, 2, n)
    macd_hist = (macd_line - 1) * 0.5
    macd_signal = np.linspace(-0.1, 1.8, n)

    df = pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
        'RSI': rsi,
        'STOCHk': stoch_k,
        'STOCHd': stoch_d,
        'MACD_12_26': macd_line,
        'MACDh_12_26': macd_hist,
        'MACDs_12_26': macd_signal,
    }, index=idx)
    return df


def test_create_price_chart_contains_expected_traces_and_axes():
    d = EquityDashboard()
    df = _make_indicators_df(30)
    fig = d._create_price_chart('TEST', df)

    # Basic figure sanity checks
    assert fig is not None
    # Template should exist, avoid versions specifics about internal naming
    assert fig.layout.template is not None
    assert 'TEST' in (fig.layout.title.text if fig.layout.title else '')

    # Collect names/types of traces
    trace_names = [getattr(t, 'name', '') for t in fig.data]

    # Expected traces include: Price (candlestick), Volume(Row 2), RSI(Row 3), %K, %D(Row 4), MACD Hist, MACD Line, Signal (Row5)
    assert 'Price' in trace_names
    assert 'Volume' in trace_names
    assert any('RSI' in (name or '') for name in trace_names)
    assert any('%K' in (name or '') for name in trace_names) or any('STOCHk' in (name or '') for name in trace_names)
    assert any('%D' in (name or '') for name in trace_names) or any('STOCHd' in (name or '') for name in trace_names)
    assert any('MACD Hist' in (name or '') for name in trace_names)
    assert any(name == 'MACD' for name in trace_names) or any(name == 'Signal' for name in trace_names)

    # Check that axes ranges for RSI/Stochastic were set (0-100 range)
    # yaxis3 is RSI; yaxis4 is Stochastic
    assert hasattr(fig.layout, 'yaxis3') and tuple(getattr(fig.layout.yaxis3, 'range', [])) == (0, 100)
    assert hasattr(fig.layout, 'yaxis4') and tuple(getattr(fig.layout.yaxis4, 'range', [])) == (0, 100)

    # Confirm the number of traces aligns with expected series (candlestick + volume + RSI + stoch k+d + macd hist+line+signal = 8)
    assert len(fig.data) >= 7
