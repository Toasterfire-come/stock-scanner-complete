"""
Pure selection policy for "best-effort realtime + coverage backfill".

This is intentionally decoupled from Django/yfinance so we can unit test it.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        x = str(x).strip()
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def choose_backfill_tickers(
    *,
    hot_tickers: Sequence[str],
    stale_tickers: Sequence[str],
    max_tickers: int,
) -> List[str]:
    """
    Choose which symbols to backfill via snapshot polling this cycle.

    Priority:
    - hot_tickers first (watchlists / alerts / active scans)
    - then stale_tickers (coverage guarantee)
    """
    max_tickers = int(max_tickers)
    if max_tickers <= 0:
        return []

    merged = dedupe_preserve_order(list(hot_tickers) + list(stale_tickers))
    return merged[:max_tickers]

