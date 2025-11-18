import pytest
from src.pipelines.get_sentiment_scraper import SentimentScraper


def test_multi_source_status_handling(monkeypatch):
    """
    Tests that the scraper correctly reports status for multiple sources,
    including when one source provides no data.
    """
    s = SentimentScraper()
    
    # Patch the internal methods to control their output directly
    monkeypatch.setattr(s, '_get_headlines_from_finviz', lambda ticker: [{'source': 'Finviz', 'title': 'Test Finviz'}]) # noqa
    monkeypatch.setattr(s, '_get_headlines_from_yahoo', lambda ticker: [{'source': 'Yahoo', 'title': 'Yahoo News'}]) # noqa
    monkeypatch.setattr(s, '_get_headlines_from_sec', lambda ticker: []) # Simulate no data for SEC
    
    headlines, status = s.get_headlines_with_status('AAPL', sources=['finviz', 'yahoo', 'sec'])
    
    assert status['Finviz']['state'] == 'ok' # noqa
    assert status['Yahoo']['state'] == 'ok'
    assert status['SEC']['state'] == 'no_data'
    assert isinstance(headlines, list)
    assert len(headlines) >= 2


def test_finviz_and_yahoo_rss_extraction(monkeypatch):
    s = SentimentScraper()
    finviz_html = "<html><body><table class='fullview-news-outer'><tr><td>Nov-17-2025 12:00PM</td><td><a href='https://finviz/article'>Finviz Headline</a></td></tr></table></body></html>"
    yahoo_xml = '<rss><channel><item><title>Yahoo Headline</title><link>https://yahoo/headline</link><pubDate>Mon, 17 Nov 2025 12:30:00 GMT</pubDate></item></channel></rss>'
    
    monkeypatch.setattr(s, '_get_headlines_from_finviz', lambda ticker: s._parse_finviz_html(finviz_html)) # noqa
    monkeypatch.setattr(s, '_get_headlines_from_yahoo', lambda ticker: s._parse_yahoo_rss(yahoo_xml)) # noqa
    
    hh = s.get_headlines('AAPL', sources=['finviz', 'yahoo'])
    assert any(h['source'] == 'Finviz' for h in hh)
    assert any(h['source'] == 'Yahoo' for h in hh)


def test_rate_limiting_throttle(monkeypatch):
    import time
    s = SentimentScraper()
    # set a higher limit for Finviz for test
    s.rate_limits['Finviz'] = 0.5
    # Set last request as now
    s._last_request['Finviz'] = time.time()
    slept = []

    def fake_sleep(d):
        slept.append(d)

    monkeypatch.setattr('time.sleep', fake_sleep)
    s._throttle('Finviz')
    assert len(slept) == 1
    # Should sleep approximately 0.5s
    assert pytest.approx(slept[0], rel=0.05) == 0.5


def test_rate_limits_are_persisted(monkeypatch):
    from src.core.settings_store import set_scope_config
    import time
    conf = {
        'weights': {'Finviz': 0.5, 'Yahoo': 0.5, 'SEC': 0.0}, # noqa
        'scoring_mode': 'auto',
        'enabled_sources': {'Finviz': True, 'Yahoo': True, 'SEC': True},
        'rate_limits': {'Finviz': 0.5, 'Yahoo': 0.1, 'SEC': 0.05} # noqa
    }
    set_scope_config('global', conf)
    s = SentimentScraper()
    assert s.rate_limits.get('Finviz') == 0.5
    # Now verify _throttle respects the persisted value
    s._last_request['Finviz'] = time.time()
    slept = []
    def fake_sleep(d):
        slept.append(d)
    monkeypatch.setattr('time.sleep', fake_sleep)
    s._throttle('Finviz')
    assert len(slept) == 1
    assert pytest.approx(slept[0], rel=0.05) == 0.5


def test_get_headlines_from_sec_uses_cik(monkeypatch):
    """Ensure get_headlines_from_sec resolves CIK and uses it in the EDGAR query URL."""
    from src.pipelines.get_sec_rss_feeds import get_cik_for_ticker
    from src.pipelines.get_sentiment_scraper import SentimentScraper

    # Stub get_cik_for_ticker to return a CIK
    monkeypatch.setattr('src.pipelines.get_sec_rss_feeds.get_cik_for_ticker', lambda t: '320193')
    urls = []

    def fake_get(self, url, *args, **kwargs):
        urls.append(url)
        class R:
            def __init__(self, text):
                self.text = text
                self.status_code = 200
            def raise_for_status(self):
                pass
        return R('<feed></feed>')

    monkeypatch.setattr('requests.sessions.Session.get', fake_get)
    s = SentimentScraper()
    entries = s.get_headlines_from_sec('AAPL')
    # Verify request used the returned CIK
    assert any('CIK=320193' in u for u in urls)
