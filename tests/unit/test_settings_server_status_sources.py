import json
from src.server import settings_server

def test_status_sources_endpoint(monkeypatch):
    # Monkeypatch SentimentScraper.get_headlines_with_status to return predictable output
    fake_status = ({}, {'Finviz': {'state': 'ok', 'last_success': '2025-01-01T00:00:00', 'last_error': None}})
    class FakeSS:
        def get_headlines_with_status(self, ticker):
            return fake_status

    monkeypatch.setattr('src.server.settings_server.SentimentScraper', lambda: FakeSS())
    app = settings_server.app
    client = app.test_client()
    rv = client.get('/status/sources?ticker=AAPL')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['ticker'] == 'AAPL'
    assert 'source_status' in data
    assert data['source_status']['Finviz']['state'] == 'ok'
    # If SEC status is present, its 'cik' key should be present (may be None)
    if 'SEC' in data['source_status']:
        assert 'cik' in data['source_status']['SEC']
