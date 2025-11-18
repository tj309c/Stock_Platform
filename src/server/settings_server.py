"""
Simple Flask server providing Settings endpoints for per-scope configs.

Endpoints:
- GET /settings -> returns all settings
- GET /settings/<scope> -> returns scope config (dict)
- POST /settings/<scope> -> set scope config (JSON body)

This is a minimal, single-file server for dev and local multi-user testing. It stores data in
`data/config/server_settings.json`.
"""
from flask import Flask, jsonify, request
try:
    from flask_cors import CORS
except Exception:
    CORS = lambda app: None
from pathlib import Path
import json
from typing import List
from src.core.queue_manager import get_global_queue_manager
from src.core.config import AppConfig
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.pipelines.get_sec_rss_feeds import get_cik_for_ticker

import src.pipelines.llm_scoring as llm_scoring

app = Flask(__name__)
CORS(app)

DATA_FILE = Path(__file__).parent.parent / 'data' / 'config' / 'server_settings.json'
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
LLM_CACHE_FILE = Path(__file__).parent.parent / 'data' / 'cache' / 'llm_cache.json'
LLM_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_llm_cache() -> dict:
    if not LLM_CACHE_FILE.exists():
        return {}
    try:
        with open(LLM_CACHE_FILE, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_llm_cache(cache: dict):
    with open(LLM_CACHE_FILE, 'w', encoding='utf-8') as fh:
        json.dump(cache, fh, indent=2)

def read_data():
    if not DATA_FILE.exists():
        return {"version": 1, "scopes": {}}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {"version": 1, "scopes": {}}

def write_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2)


@app.route('/settings', methods=['GET'])
def get_settings():
    return jsonify(read_data())


@app.route('/settings/<scope>', methods=['GET'])
def get_scope(scope):
    data = read_data()
    return jsonify(data.get('scopes', {}).get(scope, {}))


@app.route('/settings/<scope>', methods=['POST'])
def set_scope(scope):
    data = read_data()
    payload = request.get_json() or {}
    if 'scopes' not in data:
        data['scopes'] = {}
    data['scopes'][scope] = payload
    write_data(data)
    return jsonify({'status': 'ok', 'scope': scope})


@app.route('/score', methods=['POST'])
def score_texts():
    payload = request.get_json() or {}
    texts: List[str] = payload.get('texts', [])
    if not texts:
        return jsonify({'scores': []})
    # load cache
    cache = _load_llm_cache()
    results = [None] * len(texts)
    to_score_indices = []
    to_score_texts = []
    for idx, t in enumerate(texts):
        if t in cache:
            results[idx] = cache[t]
        else:
            to_score_indices.append(idx)
            to_score_texts.append(t)
    # batch score remaining
    if to_score_texts:
        scored = llm_scoring.score_texts_with_llm(to_score_texts)
        for i, val in enumerate(scored):
            idx = to_score_indices[i]
            results[idx] = val
            if val is not None:
                cache[to_score_texts[i]] = val
    # persist cache
    try:
        _save_llm_cache(cache)
    except Exception:
        pass
    return jsonify({'scores': results})


@app.route('/score/submit', methods=['POST'])
def submit_score_job():
    cfg = AppConfig()
    # API key optional in dev
    required_key = cfg.secrets.get('SETTINGS_SERVER_API_KEY')
    if required_key:
        key = request.headers.get('X-API-KEY')
        if key != required_key:
            return jsonify({'error': 'unauthorized'}), 401
    payload = request.get_json() or {}
    texts = payload.get('texts') or payload.get('text')
    if isinstance(texts, str):
        texts = [texts]
    if not texts or not isinstance(texts, list):
        return jsonify({'error': 'no texts provided'}), 400
    qm = get_global_queue_manager()
    job_id = qm.enqueue({'texts': texts})
    return jsonify({'job_id': job_id})


@app.route('/score/poll/<job_id>', methods=['GET'])
def poll_score_job(job_id: str):
    qm = get_global_queue_manager()
    job = qm.get_job(job_id)
    if not job:
        return jsonify({'error': 'job not found'}), 404
    return jsonify({'job_id': job_id, 'status': job.get('status'), 'result': job.get('result')})


@app.route('/status/sources', methods=['GET'])
def status_sources():
    cfg = AppConfig()
    required_key = cfg.secrets.get('SETTINGS_SERVER_API_KEY')
    if required_key:
        key = request.headers.get('X-API-KEY')
        if key != required_key:
            return jsonify({'error': 'unauthorized'}), 401
    ticker = request.args.get('ticker') or request.args.get('q')
    if not ticker:
        return jsonify({'error': 'ticker parameter required'}), 400
    s = SentimentScraper()
    headlines, status = s.get_headlines_with_status(ticker.upper())
    # Add a resolved CIK to the SEC source status for easier debugging
    try:
        if 'SEC' in status and status['SEC'] is not None:
            status['SEC']['cik'] = get_cik_for_ticker(ticker.upper())
    except Exception:
        pass
    return jsonify({'ticker': ticker.upper(), 'source_status': status, 'num_headlines': len(headlines)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
