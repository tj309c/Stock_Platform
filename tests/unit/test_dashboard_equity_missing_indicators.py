import pandas as pd
from src.dashboards.dashboard_equity import EquityDashboard


def _make_df_without_macd_or_stoch():
    idx = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
    df = pd.DataFrame({
        'open': range(30),
        'high': range(1, 31),
        'low': range(0, 30),
        'close': range(1, 31),
        'volume': [100] * 30,
        # No RSI or MACD or STOCH - verify only price and volume traces are present
    }, index=idx)
    return df


def test_create_price_chart_without_macd_or_stoch():
    d = EquityDashboard()
    df = _make_df_without_macd_or_stoch()
    fig = d._create_price_chart('NOIND', df)

    trace_names = [getattr(t, 'name', '') for t in fig.data]
    # Expect Price & Volume at a minimum
    assert 'Price' in trace_names
    assert 'Volume' in trace_names
    # There should be no MACD traces
    assert not any('MACD' in (name or '') for name in trace_names)
    # No Stochastic or RSI
    assert not any('%K' in (name or '') for name in trace_names)
    assert not any('STOCH' in (name or '') for name in trace_names)
