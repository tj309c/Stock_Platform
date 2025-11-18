import types
import json
from src.pipelines import llm_scoring
import streamlit as st


def test_score_texts_server_queue(monkeypatch):
    # configure secrets for server queue mode
    st.secrets['LLM_SCORING_MODE'] = 'server-queue'
    st.secrets['SETTINGS_SERVER_URL'] = 'http://localhost:5001'

    # fake server responses: first POST -> job_id, then GET /poll -> complete
    class DummyResp:
        def __init__(self, status_code, jsond):
            self.status_code = status_code
            self._json = jsond
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception('http error')
            return None
        def json(self):
            return self._json

    def fake_post(url, json=None, timeout=3):
        return DummyResp(200, {'job_id': 'job-1234'})

    def fake_get(url):
        return DummyResp(200, {'job_id': 'job-1234', 'status': 'complete', 'result': {'scores': [0.5, -0.1]}})

    import requests
    monkeypatch.setattr(requests, 'post', fake_post)
    monkeypatch.setattr(requests, 'get', fake_get)

    out = llm_scoring.score_texts_with_llm(['hello', 'world'])
    assert isinstance(out, list)
    assert out == [0.5, -0.1]
