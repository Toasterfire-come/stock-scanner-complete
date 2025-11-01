"""Session and proxy management for stock retrieval."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional
import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import StockRetrievalConfig
from .logging_utils import get_logger


logger = get_logger(__name__)

try:  # Prefer curl_cffi sessions for Yahoo compatibility when available
    from curl_cffi import requests as curl_requests  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    curl_requests = None


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
    failures: List[str] = field(default_factory=list)
    rotation_index: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    @classmethod
    def from_config(cls, config: StockRetrievalConfig) -> "ProxyPool":
        if not config.use_proxies:
            logger.info("Proxy usage disabled via configuration.")
            return cls(proxies=[], enabled=False)

        def _load(path: Path) -> List[str]:
            if not path.exists():
                return []
            try:
                with path.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
            except json.JSONDecodeError as exc:
                logger.error("Failed to parse proxy file %s: %s", path, exc)
                return []

            proxies = _flatten_proxy_payload(payload)
            return list(dict.fromkeys(proxy.strip() for proxy in proxies if proxy))

        primary_path = Path(config.proxy_file)
        proxies = _load(primary_path)

        if not proxies:
            repo_root = config.combined_ticker_dir.parent.parent
            fallback_path = repo_root / "healthy_proxies.json"
            proxies = _load(fallback_path)
            if proxies:
                logger.info(
                    "Loaded %s proxies from fallback %s",
                    len(proxies),
                    fallback_path.name,
                )

        if not proxies:
            logger.warning(
                "Proxy file not found or empty at %s; continuing without proxies.",
                primary_path,
            )
            return cls(proxies=[], enabled=False)

        logger.info("Loaded %s proxies for rotation", len(proxies))
        return cls(proxies=proxies, enabled=bool(proxies))

    def get_proxy(self, worker_index: int) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        with self._lock:
            index = (self.rotation_index + worker_index) % len(self.proxies)
            return self.proxies[index]

    def acquire(self) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        with self._lock:
            proxy = self.proxies[self.rotation_index % len(self.proxies)]
            self.rotation_index = (self.rotation_index + 1) % len(self.proxies)
            return proxy

    def mark_failure(self, proxy: Optional[str]) -> None:
        if proxy is None or not self.enabled or proxy not in self.proxies:
            return
        with self._lock:
            self.failures.append(proxy)
            idx = self.proxies.index(proxy)
            failed = self.proxies.pop(idx)
            self.proxies.append(failed)
            if self.rotation_index >= len(self.proxies):
                self.rotation_index = 0
            logger.debug("Marked proxy %s as unhealthy; moved to rotation tail", proxy)

    def record_success(self, proxy: Optional[str]) -> None:
        if proxy is None:
            return
        with self._lock:
            if proxy in self.failures:
                self.failures = [p for p in self.failures if p != proxy]

    def rotate(self) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        with self._lock:
            self.rotation_index = (self.rotation_index + 1) % len(self.proxies)
            proxy = self.proxies[self.rotation_index]
            logger.debug("Rotated proxy to %s", proxy)
            return proxy


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
    if curl_requests is not None and proxy:
        session = curl_requests.Session()
    else:
        session = requests.Session()

    adapter = HTTPAdapter(max_retries=_build_retry(timeout))
    if hasattr(session, "mount"):
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    else:
        logger.debug("Session type %s does not support mount(); skipping adapter install", type(session))

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
