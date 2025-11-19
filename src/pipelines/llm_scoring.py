"""
llm_scoring.py
Optional LLM-based headline scoring helper.

This module provides a minimal wrapper to call a configured LLM API to produce a sentiment score
for a single text headline. It supports OpenAI (openai package) and Anthropic (claude package) if
present and configured via `st.secrets` (AppConfig). All calls are optional; the caller should
fall back to VADER/TextBlob when no LLM is available.

Design notes:
- Return value: a float in [-1.0, 1.0] representing sentiment (positive -> bullish)
- Limitations: This is a light wrapper for quick prototyping and not a production-grade LLM client.
"""
from __future__ import annotations

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

try:
    import openai
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except Exception:
    HAS_ANTHROPIC = False

from src.core.config import AppConfig


def _sanitize_response_float(resp: str) -> Optional[float]:
    """Try to parse a numeric float from an LLM response. Returns None on failure."""
    try:
        # Find the first floating number like -0.43, 0.5, 1, -1
        import re
        m = re.search(r"-?\d+\.?\d*", resp)
        if not m:
            return None
        f = float(m.group(0))
        if f > 1:
            # attempt to scale if LLM returned %# or [0,100]
            if f <= 100:
                f = f / 100.0
        # clamp
        return max(min(f, 1.0), -1.0)
    except Exception:
        return None


def score_with_openai(text: str, model: str = 'gpt-4o', max_tokens: int = 16) -> Optional[float]:
    try:
        if not HAS_OPENAI:
            return None
        cfg = AppConfig()
        if not cfg.openai_api_key:
            return None
        openai.api_key = cfg.openai_api_key
        prompt = (
            "You are a sentiment scoring assistant. Given the following headline, return a single numeric sentiment score in JSON format. "
            "Respond with JSON {\"score\": <float in [-1.0, 1.0]>}. Only return JSON.\n"
            f"Headline: {text}\n"
        )
        try:
            # Use chat completion to get structured JSON
            res = openai.ChatCompletion.create(model=model, messages=[{"role":"user","content":prompt}], max_tokens=max_tokens)
            # Support both chat and completion structures
            txt = res['choices'][0].get('message', {}).get('content') or res['choices'][0].get('text')
        except Exception:
            # fallback to completions create
            res = openai.Completion.create(engine=model, prompt=prompt, max_tokens=max_tokens)
            txt = res['choices'][0]['text']
        return _sanitize_response_float(txt)
    except Exception as ex:
        logger.debug("OpenAI scoring failed: %s", ex)
        return None


def score_with_anthropic(text: str, model: str = 'claude-v1') -> Optional[float]:
    try:
        if not HAS_ANTHROPIC:
            return None
        cfg = AppConfig()
        if not cfg.anthropic_api_key:
            return None
        client = Anthropic(api_key=cfg.anthropic_api_key)
        # Anthropic style: ask for JSON only
        prompt = (
            "You are an assistant. Return only JSON with format {\"score\": <float in [-1.0,1.0]>}.\n"
            f"Headline: {text}\n"
        )
        resp = client.completions.create(model=model, prompt=prompt, max_tokens_to_sample=16)
        txt = resp['completion']
        return _sanitize_response_float(txt)
    except Exception as ex:
        logger.debug("Anthropic scoring failed: %s", ex)
        return None


def score_text_with_llm(text: str) -> Optional[float]:
    """Try available LLM providers to score text; returns first non-None result.

    Order: OpenAI -> Anthropic.
    """
    # Try OpenAI first
    val = None
    if HAS_OPENAI:
        val = score_with_openai(text)
        if isinstance(val, float):
            return val
    if HAS_ANTHROPIC:
        val = score_with_anthropic(text)
        if isinstance(val, float):
            return val
    return None


def _simple_token_estimate(text: str) -> int:
    # Very rough heuristic: average 4 chars per token -> length / 4
    return max(1, len(text) // 4)


def score_texts_with_llm(texts: List[str], model: str = 'gpt-4o', max_tokens_total: int = 1200) -> List[Optional[float]]:
    """Batch scoring that returns a list of floats or None.
    - It builds a JSON request asking for an array of scores and uses ChatCompletion if available.
    - If prompt would exceed max tokens heuristically, it splits into smaller subrequests.
    """
    if not texts:
        return []
    # Quick estimate of tokens
    est_tokens = sum(_simple_token_estimate(t) for t in texts)
    # if it's estimated too big, chunk
    results: List[Optional[float]] = [None] * len(texts)
    # If server mode configured, attempt to send to server
    try:
        cfg = AppConfig()
        scoring_pref = cfg.secrets.get('LLM_SCORING_MODE', 'auto')
        # Determine whether to use the scoring server explicitly
        if scoring_pref == 'server':
            use_server = True
        elif scoring_pref == 'local':
            use_server = False
        else:
            use_server = getattr(cfg, 'SETTINGS_STORE_TYPE', 'local') == 'server'
        if use_server:
            # send to server endpoint
            import requests
            base = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001'
            try:
                r = requests.post(f"{base}/score", json={'texts': texts}, timeout=10)
                r.raise_for_status()
                data = r.json()
                scores = data.get('scores', [None] * len(texts))
                # validate result
                if isinstance(scores, list) and len(scores) == len(texts):
                    return scores
                if isinstance(scores, dict):
                    # attempt to map by text keys
                    return [scores.get(t) for t in texts]
                return [None] * len(texts)
            except Exception:
                # fallback to local
                pass
        # If explicit queuing is set, attempt to use server async queue
        if scoring_pref == 'server-queue':
            try:
                import requests, time
                base = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001'
                r = requests.post(f"{base}/score/submit", json={'texts': texts}, timeout=5)
                r.raise_for_status()
                job_id = r.json().get('job_id')
                if not job_id:
                    pass
                # poll until complete or timeout
                deadline = time.time() + 10
                while time.time() < deadline:
                    p = requests.get(f"{base}/score/poll/{job_id}")
                    if p.status_code == 200:
                        body = p.json()
                        if body.get('status') == 'complete':
                            return body.get('result', {}).get('scores', [None] * len(texts))
                        if body.get('status') == 'failed':
                            break
                    time.sleep(0.2)
            except Exception:
                pass
    except Exception:
        pass

    if HAS_OPENAI:
        try:
            import openai
            cfg = AppConfig()
            # If an API key is provided, set it; otherwise, allow tests to monkeypatch the
            # ChatCompletion behavior or the environment to supply keys. When no key is present
            # we'll still proceed but real API calls will fail and fall back as expected.
            try:
                if cfg.openai_api_key:
                    openai.api_key = cfg.openai_api_key
            except Exception:
                pass
            # chunk texts if necessary
            i = 0
            while i < len(texts):
                # grow chunk
                accum = 0
                j = i
                while j < len(texts) and accum + _simple_token_estimate(texts[j]) <= max_tokens_total:
                    accum += _simple_token_estimate(texts[j])
                    j += 1
                chunk = texts[i:j]
                # Build prompt asking for JSON array of scores
                items = '\n'.join(f"{idx+1}. {t}" for idx, t in enumerate(chunk, start=i))
                prompt = (
                    "You are a sentiment scoring assistant. Return only JSON object: {\"scores\": [<float>, ...]} corresponding to the input headlines.\n"
                    f"Headlines:\n{items}\n"
                )
                try:
                    res = openai.ChatCompletion.create(model=model, messages=[{"role":"user","content":prompt}], max_tokens=128)
                    txt = res['choices'][0].get('message', {}).get('content') or res['choices'][0].get('text')
                except Exception:
                    # fall back to simple per-text
                    for k in range(i, j):
                        results[k] = score_text_with_llm(texts[k])
                    i = j
                    continue
                # parse JSON robustly
                import json, re
                try:
                    # Some LLMs might wrap JSON in text; extract JSON object or array
                    m = re.search(r"(\{.*?\}|\[.*?\])", txt, re.DOTALL)
                    json_str = m.group(0) if m else txt
                    parsed = json.loads(json_str)
                    # Accept either a dict containing 'scores' or a bare list
                    if isinstance(parsed, dict) and 'scores' in parsed and isinstance(parsed['scores'], list):
                        scs = parsed['scores']
                    elif isinstance(parsed, list):
                        scs = parsed
                    else:
                        scs = None
                    if not scs or not isinstance(scs, list) or len(scs) != len(chunk):
                        # fallback per-item
                        for k in range(i, j):
                            results[k] = score_text_with_llm(texts[k])
                    else:
                        for idx, score in enumerate(scs):
                            try:
                                f = float(score)
                                results[i + idx] = max(min(f, 1.0), -1.0)
                            except Exception:
                                results[i + idx] = None
                except Exception:
                    for k in range(i, j):
                        results[k] = score_text_with_llm(texts[k])
                i = j
            return results
        except Exception:
            # fallback to local per-text
            pass
    # fallback single-text loop
    for idx, t in enumerate(texts):
        results[idx] = score_text_with_llm(t)
    return results


# End of file: only one score_texts_with_llm is implemented above (typed variant)

