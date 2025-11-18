import pytest
from src.pipelines import get_political_data
import requests


def test_fetch_and_parse(monkeypatch):
    html = "<html><body><ul><li class='recent-trade'>Rep. John Doe bought 100 shares of AAPL</li></ul></body></html>"

    class DummyResp:
        def __init__(self):
            self.status_code = 200
            self.text = html
        def raise_for_status(self):
            return None

    def fake_get(url, timeout=3, headers=None):
        return DummyResp()

    monkeypatch.setattr(requests, 'get', fake_get)
    trades = get_political_data.fetch_housestockwatcher_recent(limit=5)
    assert isinstance(trades, list)
    assert len(trades) >= 1
    parsed = get_political_data.parse_trade_raw(trades[0]['raw'])
    assert parsed['ticker'] == 'AAPL'
