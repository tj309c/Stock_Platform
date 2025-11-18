"""
get_political_data.py
Utilities to fetch recent congressional trades (placeholder scraper).
"""
from __future__ import annotations
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_housestockwatcher_recent(limit: int = 10) -> List[Dict]:
    """Fetch recent congressional trades from housestockwatcher.com (scrape simple HTML). Returns list of trades.
    This is a naive scraper and should be replaced with API integration if available.
    """
    url = 'https://housestockwatcher.com/recent'  # placeholder path
    trades: List[Dict] = []
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "AnalysisMaster/0.1"})
        r.raise_for_status()
    except Exception as ex:
        logger.debug('Failed to fetch housestockwatcher: %s', ex)
        return trades
    soup = BeautifulSoup(r.text, 'html.parser')
    # Try to find the table or list items; fallback to text parsing
    try:
        for item in soup.select('li.recent-trade')[:limit]:
            txt = item.text.strip()
            trades.append({'raw': txt})
    except Exception:
        pass
    # Fallback: look for paragraphs containing trade-like text
    if not trades:
        for p in soup.find_all('p'):
            txt = p.text.strip()
            if 'bought' in txt.lower() or 'sold' in txt.lower():
                trades.append({'raw': txt})
                if len(trades) >= limit:
                    break
    return trades


def parse_trade_raw(raw: str) -> Optional[Dict]:
    """Parse a raw text line into a structured trade if possible.
    Example format: 'Rep. John Doe (R) bought 100 shares of AAPL on 2025-11-17'
    """
    try:
        # very naive parsing
        parts = raw.split()
        # find ticker token which is typically uppercase 1-5 chars
        ticker = None
        for tok in parts:
            if tok.isupper() and 1 <= len(tok) <= 5:
                ticker = tok
                break
        return {'raw': raw, 'ticker': ticker}
    except Exception as ex:
        logger.debug('Failed parse trade: %s', ex)
        return None
