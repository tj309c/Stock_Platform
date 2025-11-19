"""
Helpers utilities used across dashboards and other modules.
"""
from __future__ import annotations

from typing import Any, Callable, Tuple, Type, Optional
import time
import functools
import logging

logger = logging.getLogger(__name__)


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


__all__ = ["format_large_number", "retry_on_exception"]


def retry_on_exception(
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: Optional[float] = None,
    suppress: bool = True,
    return_on_failure: Optional[Any] = None,
):
    """Decorator to retry a function call on specified exceptions.

    Args:
        exceptions: exception types to catch and retry on.
        tries: number of attempts to make.
        delay: initial delay between attempts in seconds.
        backoff: multiplicative backoff factor.
        max_delay: optional cap for backoff delay.
        suppress: if True, returns return_on_failure on final failure instead of raising.
        return_on_failure: value to return if suppress=True and all retries fail.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries = max(1, int(tries))
            _delay = float(delay)
            for attempt in range(1, _tries + 1):
                # Debug print removed in production
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == _tries:
                        # Log with exc_info=True for full stacktrace in debug logs
                        logger.debug(
                            "Function %s failed after %s attempts: %s",
                            getattr(func, '__name__', str(func)),
                            _tries,
                            e,
                            exc_info=True,
                        )
                        if suppress:
                            return return_on_failure
                        raise
                    # log and sleep before retry
                    # Logging handled by logger.debug above.
                    # Provide additional debug info for intermediate retries: include exception repr and function args summary
                    try:
                        arg_preview = f"args={args[:3]}, kwargs_keys={list(kwargs.keys())}"
                    except Exception:
                        arg_preview = "args_preview_unavailable"
                    logger.debug(
                        "Transient error on attempt %s/%s for %s: %s — retrying in %s seconds (%s)",
                        attempt,
                        _tries,
                        getattr(func, '__name__', str(func)),
                        repr(e),
                        _delay,
                        arg_preview,
                    )
                    time.sleep(_delay)
                    _delay *= backoff
                    if max_delay is not None:
                        _delay = min(_delay, max_delay)
            # Should not reach here
            return return_on_failure

        return wrapper

    return decorator

