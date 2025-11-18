import pytest
import requests
from src.pipelines.get_sentiment_scraper import SentimentScraper


def test_status_fields_and_clear_cache(monkeypatch):
    s = SentimentScraper()

    # Monkeypatch network calls to return simple headlines
    html = "<html><body><table class='fullview-news-outer'><tr><td>Nov-17-2025 10:30AM</td><td><a href='https://finviz'>Test</a></td></tr></table></body></html>"
    def fake_get(self, url, *args, **kwargs):
        class R:
            def __init__(self, text):
                self.text = text
                self.status_code = 200
            def raise_for_status(self):
                pass
        return R(html)

    monkeypatch.setattr('requests.sessions.Session.get', fake_get)

    headlines, status = s.get_headlines_with_status('AAPL')
    assert isinstance(status, dict)
    assert 'Finviz' in status
    assert status['Finviz']['state'] in ('ok', 'no_data', 'error')
    # If OK, ensure last_success is set
    if status['Finviz']['state'] == 'ok':
        assert status['Finviz']['last_success'] is not None

    # Test clear_cache does not raise
    s.clear_cache()


def test_status_error_and_message(monkeypatch):
    from src.core.settings_store import set_scope_config
    set_scope_config('global', {'enabled_sources': {'Finviz': True, 'Yahoo': True, 'SEC': True}})
    s = SentimentScraper()

    # Simulate an error by patching one of the scraper methods
    def fake_get(self, ticker):
        raise Exception("Simulated Yahoo failure")

    monkeypatch.setattr(SentimentScraper, 'get_headlines_from_yahoo_rss', fake_get)
    headlines, status = s._gather_headlines_with_status('AAPL')
    assert isinstance(status['Yahoo']['state'], str)
    assert status['Yahoo']['state'] == 'error'
    assert 'Simulated Yahoo failure' in status['Yahoo']['last_error']
