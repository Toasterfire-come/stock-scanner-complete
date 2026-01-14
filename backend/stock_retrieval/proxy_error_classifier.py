"""
Heuristics for identifying "hard" proxy failures.

These errors should trigger immediate quarantine because retrying the same proxy
is almost always wasted time (CONNECT not supported, proxy blocked, unreachable, etc).
"""

from __future__ import annotations

import re
from typing import Optional


_CONNECT_STATUS_RE = re.compile(r"\bCONNECT\b.*\b(400|401|403|407|429|502|503|504)\b", re.IGNORECASE)
_STATUS_CONNECT_RE = re.compile(r"\b(400|401|403|407|429|502|503|504)\b.*\bCONNECT\b", re.IGNORECASE)


def is_hard_proxy_failure(error: Optional[str]) -> bool:
    """
    Returns True for failures that strongly indicate the proxy is unusable for HTTPS Yahoo/yfinance.

    Examples:
    - "CONNECT tunnel failed, response 502"
    - "Received HTTP code 400 from proxy after CONNECT"
    - "Proxy Authentication Required (407)"
    - Connection refused / no route / timed out at proxy level
    """
    if not error:
        return False

    e = str(error).strip()
    if not e:
        return False

    if _CONNECT_STATUS_RE.search(e):
        return True
    if _STATUS_CONNECT_RE.search(e):
        return True

    low = e.lower()

    # Common "tunnel" phrasing across requests/urllib3/curl-like errors
    if "tunnel connection failed" in low:
        return True
    if "proxy error" in low and ("connect" in low or "tunnel" in low):
        return True

    # Proxy is there but won't accept/connect
    hard_markers = (
        "connection refused",
        "no route to host",
        "network is unreachable",
        "connection reset",
        "timed out",
        "timeout",
        "unable to connect to proxy",
        "cannot connect to proxy",
        "proxy connection failed",
    )
    return any(m in low for m in hard_markers)

