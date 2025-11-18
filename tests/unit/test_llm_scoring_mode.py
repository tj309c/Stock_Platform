import pytest
from src.pipelines import llm_scoring
from src.core.config import AppConfig
import requests


def test_score_texts_with_server_preference(monkeypatch, tmp_path):
    # Monkeypatch AppConfig to set server preference
    def fake_init(self):
        self.DATA_DIR = tmp_path
        self.CACHE_DIR = tmp_path / 'cache'
        self.secrets = {'SETTINGS_SERVER_URL': 'http://localhost:5001', 'LLM_SCORING_MODE': 'server'}
        self.SETTINGS_STORE_TYPE = 'local'
    monkeypatch.setattr(AppConfig, '__init__', fake_init)

    class DummyResp:
        def __init__(self, jsond):
            self._json = jsond
            self.status_code = 200
        def raise_for_status(self):
            return None
        def json(self):
            return self._json

    def fake_post(url, json=None, timeout=3):
        return DummyResp({'scores': [0.1, 0.2]})

    monkeypatch.setattr(requests, 'post', fake_post)
    res = llm_scoring.score_texts_with_llm(['A','B'])
    assert res == [0.1, 0.2]
