"""
Helpers utilities used across dashboards and other modules.
"""
from __future__ import annotations

from typing import Any


def format_large_number(num: Any) -> str:
    """Format numbers with suffixes K/M/B/T for display.

    Accepts ints, floats, strings, or None. Returns 'N/A' for non-numeric inputs.
    """
    if num is None:
        return "N/A"
    try:
        num = float(num)
    except Exception:
        return "N/A"
    if num == 0:
        return "0"
    is_negative = num < 0
    abs_num = abs(num)
    sign = "-" if is_negative else ""
    if abs_num >= 1e12:
        return f"{sign}{abs_num/1e12:.2f}T"
    if abs_num >= 1e9:
        return f"{sign}{abs_num/1e9:.2f}B"
    if abs_num >= 1e6:
        return f"{sign}{abs_num/1e6:.2f}M"
    if abs_num >= 1e3:
        return f"{sign}{abs_num/1e3:.2f}K"
    return f"{sign}{abs_num:.0f}"


__all__ = ["format_large_number"]
