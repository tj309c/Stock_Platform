import pytest
import requests
from src.pipelines.get_sec_rss_feeds import (
    fetch_edgar_feed_by_ticker,
    get_form4_entries,
    get_8k_entries,
    get_edgar_feed_for_ticker,
    get_cik_for_ticker,
)


def test_fetch_edgar_feed_parsing(monkeypatch):
    sample = '''<?xml version="1.0"?>
    <feed>
      <entry>
        <title>Form 4 - Insider Transaction</title>
        <link href="https://www.sec.gov/xyz/form4" />
        <updated>2025-01-01T12:00:00Z</updated>
      </entry>
      <entry>
        <title>8-K - Material Event</title>
        <link href="https://www.sec.gov/xyz/8k" />
        <updated>2025-01-02T12:00:00Z</updated>
      </entry>
    </feed>
    '''

    class R:
        def __init__(self, text):
            self.text = text
            self.status_code = 200

        def raise_for_status(self):
            pass

    def fake_get(url, *args, **kwargs):
        return R(sample)

    monkeypatch.setattr('requests.get', fake_get)
    entries = fetch_edgar_feed_by_ticker('AAPL')
    assert isinstance(entries, list)
    assert len(entries) == 2
    form4 = get_form4_entries('AAPL')
    assert len(form4) == 1
    assert form4[0]['type'] == 'form4'
    k8 = get_8k_entries('AAPL')
    assert len(k8) == 1
    assert k8[0]['type'] == '8-k'


def test_get_edgar_feed_for_ticker(monkeypatch):
    xml = '''<?xml version="1.0"?>
    <feed>
      <entry>
        <title>Form 4 - Insider trading</title>
        <link href="https://www.sec.gov/Archives/edgar/data/000/000/0001.htm"/>
        <updated>2025-11-17T12:00:00Z</updated>
      </entry>
      <entry>
        <title>8-K - Material Event</title>
        <link href="https://www.sec.gov/Archives/edgar/data/000/000/0002.htm"/>
        <updated>2025-11-16T12:00:00Z</updated>
      </entry>
    </feed>'''

    class DummyResp:
        status_code = 200
        text = xml

        def raise_for_status(self):
            return None

    def fake_get(url, timeout=3, headers=None):
        return DummyResp()

    monkeypatch.setattr(requests, 'get', fake_get)
    res = get_edgar_feed_for_ticker('AAPL')
    assert isinstance(res, list)
    assert len(res) == 2
    assert res[0]['source'] == 'SEC'
    assert 'Form 4' in res[0]['title']


def test_get_cik_for_ticker(monkeypatch):
    sample_json = {
        '0': {'cik_str': '320193', 'ticker': 'AAPL', 'title': 'Apple Inc.'},
        '1': {'cik_str': '789019', 'ticker': 'MSFT', 'title': 'Microsoft Corp.'},
    }

    class R:
        def __init__(self, data):
            self._data = data
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self._data

    def fake_get(url, *args, **kwargs):
        return R(sample_json)

    monkeypatch.setattr('requests.get', fake_get)
    cik = get_cik_for_ticker('AAPL')
    assert cik == '320193'
    cik_none = get_cik_for_ticker('ZZZZ')
    assert cik_none is None
