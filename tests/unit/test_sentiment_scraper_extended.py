import pytest
import requests
from src.pipelines.get_sentiment_scraper import SentimentScraper


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()


def test_finviz_parsing(monkeypatch):
    html = """
    <html><body>
    <table class='fullview-news-outer'>
      <tr>
        <td>Nov-17-2025 10:30AM</td>
        <td><a href='https://finviz.com/story1'>Apple beats EPS</a></td>
      </tr>
    </table>
    </body></html>
    """

    s = SentimentScraper()

    def fake_get(self, url, *args, **kwargs):
        return MockResponse(html)

    monkeypatch.setattr(requests.Session, 'get', fake_get)
    res = s.get_headlines_from_finviz('AAPL')
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]['source'] == 'Finviz'
    assert 'beats' in res[0]['title'].lower()
    assert 'published' in res[0] and res[0]['published']
    # ensure published is parseable
    import pandas as pd
    assert pd.to_datetime(res[0]['published'], errors='coerce') is not pd.NaT


def test_yahoo_rss_parsing(monkeypatch):
    xml = """
    <?xml version='1.0'?>
    <rss>
      <channel>
        <item>
          <title>Apple posts profit increase</title>
          <link>https://finance.yahoo.com/article</link>
        </item>
      </channel>
    </rss>
    """

    s = SentimentScraper()

    def fake_get(self, url, *args, **kwargs):
        return MockResponse(xml)

    monkeypatch.setattr(requests.Session, 'get', fake_get)
    res = s.get_headlines_from_yahoo_rss('AAPL')
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]['source'] == 'Yahoo'
    assert 'profit' in res[0]['title'].lower()
    assert 'published' in res[0] and res[0]['published']
    import pandas as pd
    assert pd.to_datetime(res[0]['published'], errors='coerce') is not pd.NaT


def test_sec_parsing_and_sentiment(monkeypatch):
    xml = """
    <?xml version='1.0'?>
    <feed>
      <entry>
        <title>FORM 4 - John Doe</title>
        <link href='https://www.sec.gov/filing1' />
        <updated>2025-11-17T10:00:00-05:00</updated>
      </entry>
      <entry>
        <title>8-K: Material Event</title>
        <link href='https://www.sec.gov/filing2' />
        <updated>2025-11-17T11:00:00-05:00</updated>
      </entry>
    </feed>
    """

    s = SentimentScraper()

    def fake_get(self, url, *args, **kwargs):
        if 'sec.gov' in url:
            return MockResponse(xml)
        if 'finviz.com' in url:
            return MockResponse("<table class='fullview-news-outer'><tr><td><a>Apple beats</a></td></tr></table>")
        if 'finance.yahoo.com' in url:
            return MockResponse("<?xml version='1.0'?><rss><channel><item><title>Apple misses</title><link>https://finance.yahoo.com</link></item></channel></rss>")
        return MockResponse("")

    monkeypatch.setattr(requests.Session, 'get', fake_get)

    # Ensure SEC parsing works
    sec_headlines = s.get_headlines_from_sec('AAPL')
    assert len(sec_headlines) == 2
    assert all(h['source'] == 'SEC' for h in sec_headlines)
    assert all('published' in h and h['published'] for h in sec_headlines)
    import pandas as pd
    for h in sec_headlines:
      assert pd.to_datetime(h['published'], errors='coerce') is not pd.NaT

    # Full aggregation and sentiment scoring
    combined, status = s._gather_headlines_with_status('AAPL')
    # For the supplied fake responses: we expect at least 4 headlines
    assert isinstance(combined, list) and combined is not None
    assert len(combined) >= 4
    assert isinstance(status, dict)
    assert status.get('SEC')['state'] == 'ok'

    sentiment, err = s.get_sentiment_for_ticker('AAPL')
    assert err is None
    assert 'score' in sentiment
    assert 'num_headlines' in sentiment
    assert 'per_source' in sentiment
    assert 'source_status' in sentiment
    # check that SEC & Finviz were present (due to our fake_get), and statuses are ok
    assert sentiment['source_status'].get('SEC')['state'] == 'ok'
    assert sentiment['source_status'].get('Finviz')['state'] == 'ok'
