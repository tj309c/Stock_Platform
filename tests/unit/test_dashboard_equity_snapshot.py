import pandas as pd
from src.dashboards.dashboard_equity import EquityDashboard
import pytest


def _make_small_df():
    idx = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
    df = pd.DataFrame({
        'open': range(30),
        'high': range(1, 31),
        'low': range(0, 30),
        'close': range(1, 31),
        'volume': [100] * 30,
        'RSI': [50] * 30,
        'STOCHk': [50] * 30,
        'STOCHd': [45] * 30,
        'MACD_12_26': [0] * 30,
        'MACDh_12_26': [0] * 30,
        'MACDs_12_26': [0] * 30,
    }, index=idx)
    return df


def test_create_price_chart_image_snapshot_or_json():
    d = EquityDashboard()
    df = _make_small_df()
    fig = d._create_price_chart('SNAP', df)

    # Try exporting to image if kaleido is available
    try:
        img_bytes = fig.to_image(format='png')
        assert isinstance(img_bytes, (bytes, bytearray))
        assert len(img_bytes) > 1000
    except Exception as e:
        # If kaleido not available, fall back to JSON export check
        json_text = fig.to_json()
        assert isinstance(json_text, str)
        assert len(json_text) > 1000
