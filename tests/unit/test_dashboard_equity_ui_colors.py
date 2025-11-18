import pandas as pd
from src.dashboards.dashboard_equity import EquityDashboard


def test_chart_trace_colors_for_overlays_and_subplots():
    ed = EquityDashboard()

    # Build a small dataframe with necessary columns
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])    
    df = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [101, 102, 103],
        'low': [99, 100, 101],
        'close': [100.5, 101.5, 102.5],
        'volume': [1000, 1100, 1050],
        'sma_20': [100, 100.5, 101],
        'ema_50': [99.5, 100, 100.5],
        'rsi_14': [45, 50, 55],
    }, index=idx)

    # Choose overlays and subplots
    overlays = ['SMA 20', 'EMA 50']
    subplots = ['Volume', 'RSI']

    # Call protected _create_advanced_chart and get the plotly figure
    fig = ed._create_advanced_chart(df, overlays=overlays, subplots=subplots)

    # Map of expected colors (must match logic in dashboard code)
    overlay_color_map = {
        'SMA 20': 'orange',
        'SMA 50': 'yellow',
        'EMA 20': 'lightblue',
        'EMA 50': 'cyan',
        'Bollinger Bands': 'gray',
        'Ichimoku Cloud': 'aqua',
    }
    subplot_color_map = {
        'Volume': 'green',
        'RSI': 'purple',
        'MACD': 'blue'
    }

    # Find overlay traces by name and check colors
    overlay_traces = {t.name: t for t in fig.data if t.name in overlays}
    assert 'SMA 20' in overlay_traces
    assert overlay_traces['SMA 20'].line.color == overlay_color_map['SMA 20']
    assert 'EMA 50' in overlay_traces
    assert overlay_traces['EMA 50'].line.color == overlay_color_map['EMA 50']

    # Subplot traces
    subplot_traces = {t.name: t for t in fig.data if t.name in subplots}
    assert 'Volume' in subplot_traces
    # For bar color we check marker colors exist or default
    assert hasattr(subplot_traces['Volume'], 'marker')
    assert 'RSI' in subplot_traces
    assert subplot_traces['RSI'].line.color == subplot_color_map['RSI']
