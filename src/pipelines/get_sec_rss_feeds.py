from __future__ import annotations

"""Utilities to fetch and parse SEC EDGAR Atom/ RSS feeds (Form 4, 8-K, etc.)."""

import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)
USER_AGENT = 'AnalysisMaster-EDGAR/1.0'


def _parse_updated_text(updated_text: Optional[str]) -> Optional[str]:
    if not updated_text:
        return None
    try:
        dt = pd.to_datetime(updated_text, errors='coerce')
        if dt is not pd.NaT:
            return dt.isoformat()
    except Exception:
        pass
    return None


def fetch_edgar_feed_by_ticker(ticker: str, session: Optional[requests.Session] = None) -> List[Dict]:
    """Fetch EDGAR feed entries for a ticker and return parsed entries.

    Each entry is a dict: {'title', 'url', 'published'}.
    """
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&owner=include&output=atom"
    try:
        if session is None:
            r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        else:
            r = session.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        r.raise_for_status()
    except Exception as ex:
        logger.debug("EDGAR fetch failed for %s: %s", ticker, ex)
        return []

    try:
        soup = BeautifulSoup(r.text, 'xml')
    except Exception:
        soup = BeautifulSoup(r.text, 'html.parser')

    entries: List[Dict] = []
    try:
        for entry in soup.find_all(lambda t: t.name and t.name.lower() == 'entry'):
            title_el = entry.find('title')
            link_el = entry.find('link')
            updated_el = entry.find('updated')
            title = title_el.text.strip() if title_el and title_el.text else ''
            href = link_el.get('href') if link_el else None
            published = _parse_updated_text(updated_el.text if updated_el else None) or datetime.now().isoformat()
            entries.append({'title': title, 'url': href, 'published': published})
    except Exception as ex:
        logger.debug('EDGAR parse error: %s', ex)
        return []
    return entries


def get_form4_entries(ticker: str, session: Optional[requests.Session] = None) -> List[Dict]:
    entries = fetch_edgar_feed_by_ticker(ticker, session=session)
    return [ {**e, 'type': 'form4'} for e in entries if (e.get('title') or '') and ('form 4' in e.get('title').lower() or 'form4' in e.get('title').lower() or 'form-4' in e.get('title').lower()) ]


def get_8k_entries(ticker: str, session: Optional[requests.Session] = None) -> List[Dict]:
    entries = fetch_edgar_feed_by_ticker(ticker, session=session)
    return [ {**e, 'type': '8-k'} for e in entries if (e.get('title') or '') and ('8-k' in e.get('title').lower() or '8k' in e.get('title').lower() or '8 k' in e.get('title').lower()) ]


def get_edgar_feed_for_ticker(ticker: str, session: Optional[requests.Session] = None) -> List[Dict]:
    entries = fetch_edgar_feed_by_ticker(ticker, session=session)
    return [{**e, 'source': 'SEC'} for e in entries]


_CIK_CACHE = {}


def get_cik_for_ticker(ticker: str, session: Optional[requests.Session] = None) -> Optional[str]:
    """Resolve a ticker symbol to an SEC CIK string using SEC provided mapping.

    The SEC maintains a JSON file of company tickers -> CIKs which we can use to resolve
    a symbol to a CIK. Returns the CIK string (un-padded) or None when a mapping is not found.
    Results are cached in-memory for the duration of the process to reduce requests.
    """
    if not ticker:
        return None
    key = ticker.upper().strip()
    if key in _CIK_CACHE:
        return _CIK_CACHE.get(key)
    url = 'https://www.sec.gov/files/company_tickers.json'
    try:
        if session is None:
            r = requests.get(url, timeout=8, headers={'User-Agent': USER_AGENT})
        else:
            r = session.get(url, timeout=8, headers={'User-Agent': USER_AGENT})
        r.raise_for_status()
    except Exception:
        return None
    try:
        data = r.json()
    except Exception:
        # Older SEC dumps used a list; try a fallback parsing
        try:
            arr = r.json()
            for item in arr:
                if (item.get('ticker') or '').upper() == key:
                    cik = str(item.get('cik_str') or item.get('cik') or '')
                    _CIK_CACHE[key] = cik
                    return cik
        except Exception:
            return None
    # The JSON is expected to be a dict mapping numeric ids to entries. Try to find by ticker
    try:
        for _, v in data.items():
            t = (v.get('ticker') or '').upper()
            if t == key:
                cik = str(v.get('cik_str') or v.get('cik') or '')
                _CIK_CACHE[key] = cik
                return cik
    except Exception:
        pass
    return None
