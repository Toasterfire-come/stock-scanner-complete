"""Session and proxy management for stock retrieval."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import StockRetrievalConfig
from .logging_utils import get_logger


logger = get_logger(__name__)


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _flatten_proxy_payload(payload: object) -> List[str]:
    if isinstance(payload, list):
        return [str(item) for item in payload if item]
    if isinstance(payload, dict):
        values: List[str] = []
        for value in payload.values():
            if isinstance(value, (list, tuple)):
                values.extend(str(item) for item in value if item)
            elif value:
                values.append(str(value))
        return values
    return []


@dataclass
class ProxyPool:
    proxies: List[str]
    enabled: bool = True

    @classmethod
    def from_config(cls, config: StockRetrievalConfig) -> "ProxyPool":
        if not config.use_proxies:
            logger.info("Proxy usage disabled via configuration.")
            return cls(proxies=[], enabled=False)

        path = Path(config.proxy_file)
        if not path.exists():
            logger.warning("Proxy file not found at %s; continuing without proxies.", path)
            return cls(proxies=[], enabled=False)

        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse proxy file %s: %s", path, exc)
            return cls(proxies=[], enabled=False)

        proxies = _flatten_proxy_payload(payload)
        unique = list(dict.fromkeys(proxy.strip() for proxy in proxies if proxy))

        logger.info("Loaded %s proxies from %s", len(unique), path.name)
        return cls(proxies=unique, enabled=bool(unique))

    def get_proxy(self, worker_index: int) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        return self.proxies[worker_index % len(self.proxies)]


def _build_retry(timeout_seconds: float) -> Retry:
    return Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )


def create_requests_session(
    *,
    proxy: Optional[str],
    timeout: float,
) -> requests.Session:
    session = requests.Session()

    adapter = HTTPAdapter(max_retries=_build_retry(timeout))
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({"User-Agent": USER_AGENT})

    if proxy:
        session.proxies = {
            "http": proxy,
            "https": proxy,
        }
        logger.debug("Session configured with proxy %s", proxy)

    session.request = _wrap_timeout(session.request, timeout)
    return session


def _wrap_timeout(original_request, timeout: float):
    def wrapped(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return original_request(method, url, **kwargs)

    return wrapped


def configure_yfinance_session(session: requests.Session) -> None:
    try:
        import yfinance.shared  # type: ignore

        yfinance.shared._requests = session
        logger.info("Patched yfinance shared session for proxy-aware requests.")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Unable to patch yfinance session: %s", exc)


__all__ = [
    "ProxyPool",
    "create_requests_session",
    "configure_yfinance_session",
]
