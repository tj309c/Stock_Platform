import json
import pytest
from src.core import settings_store
from src.core.config import AppConfig
from src.server import settings_server


class DummyResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception('HTTP error')


def test_server_store_get_set(monkeypatch, tmp_path):
    # Start with a fresh AppConfig pointing to local server URL
    def fake_init(self):
        self.DATA_DIR = tmp_path
        self.CACHE_DIR = tmp_path / 'cache'
        self.secrets = {'SETTINGS_SERVER_URL': 'http://localhost:5001'}
        self.SETTINGS_STORE_TYPE = 'server'
    monkeypatch.setattr(AppConfig, '__init__', fake_init)

    client = settings_server.app.test_client()

    # Monkeypatch requests.get/post to call the Flask test client instead
    import requests

    def fake_get(url, timeout=3):
        # path is after base
        path = url.replace('http://localhost:5001', '')
        r = client.get(path)
        data = json.loads(r.get_data(as_text=True)) if r.get_data() else {}
        return DummyResponse(r.status_code, data)

    def fake_post(url, json=None, timeout=3):
        path = url.replace('http://localhost:5001', '')
        r = client.post(path, json=json)
        data = json.loads(r.get_data(as_text=True)) if r.get_data() else {}
        return DummyResponse(r.status_code, data)

    monkeypatch.setattr('requests.get', fake_get)
    monkeypatch.setattr('requests.post', fake_post)

    # set scope config
    conf = {'weights': {'Finviz': 0.5, 'Yahoo': 0.5, 'SEC': 0.0}, 'scoring_mode': 'vader'}
    ok = settings_store.set_scope_config('equity', conf)
    assert ok
    loaded = settings_store.get_scope_config('equity')
    assert loaded['scoring_mode'] == 'vader'
    assert loaded['weights']['Finviz'] == 0.5
