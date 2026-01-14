"""
Proxy pool utilities for yfinance/Yahoo scraping.

Design goals:
- Production-ish behavior even with unreliable free proxies:
  - score + quarantine bad proxies quickly
  - prefer recently-successful, low-latency proxies
  - persist pool state to disk between runs
- Keep this module pure-Python and testable (no network in unit tests).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def normalize_hostport(raw: str) -> Optional[str]:
    s = str(raw).strip()
    if not s or s.startswith("#"):
        return None
    # Strip scheme if present
    if s.startswith("http://"):
        s = s[len("http://") :]
    elif s.startswith("https://"):
        s = s[len("https://") :]
    # Basic check
    if ":" not in s:
        return None
    return s


def candidate_proxy_urls(hostport_or_url: str) -> List[str]:
    """
    Given either:
    - host:port
    - http://host:port
    - https://host:port
    return URL candidates to try (http/https).
    """
    s = str(hostport_or_url).strip()
    if not s:
        return []
    if s.startswith("http://") or s.startswith("https://"):
        return [s]
    hostport = normalize_hostport(s)
    if not hostport:
        return []
    return [f"http://{hostport}", f"https://{hostport}"]


@dataclass
class ProxyStats:
    proxy_url: str
    # Metadata / capabilities (best-effort; populated by verifier pipeline)
    first_seen_ts: Optional[float] = None
    last_verified_ts: Optional[float] = None
    supports_https_connect: Optional[bool] = None
    example_ok: Optional[bool] = None
    yahoo_ok: Optional[bool] = None
    yfinance_ok: Optional[bool] = None

    successes: int = 0
    failures: int = 0
    last_success_ts: Optional[float] = None
    last_failure_ts: Optional[float] = None
    last_error: Optional[str] = None
    avg_latency_ms: Optional[float] = None
    quarantined_until_ts: Optional[float] = None

    def is_quarantined(self, now_ts: Optional[float] = None) -> bool:
        now = time.time() if now_ts is None else now_ts
        return self.quarantined_until_ts is not None and self.quarantined_until_ts > now

    def record_success(self, latency_ms: Optional[float] = None, now_ts: Optional[float] = None) -> None:
        now = time.time() if now_ts is None else now_ts
        self.successes += 1
        self.last_success_ts = now
        self.last_error = None
        self.quarantined_until_ts = None
        if latency_ms is not None:
            if self.avg_latency_ms is None:
                self.avg_latency_ms = float(latency_ms)
            else:
                # EMA-ish
                self.avg_latency_ms = (self.avg_latency_ms * 0.8) + (float(latency_ms) * 0.2)

    def record_failure(
        self,
        error: str,
        *,
        quarantine_seconds: Optional[int],
        now_ts: Optional[float] = None,
    ) -> None:
        now = time.time() if now_ts is None else now_ts
        self.failures += 1
        self.last_failure_ts = now
        self.last_error = error[:500] if error else "unknown"
        if quarantine_seconds:
            self.quarantined_until_ts = now + int(quarantine_seconds)


class ProxyPool:
    """
    Maintains proxy stats and selection.
    """

    def __init__(
        self,
        *,
        quarantine_seconds: int = 30 * 60,
        failure_quarantine_threshold: int = 1,
        min_successes_to_prefer: int = 1,
    ):
        self.quarantine_seconds = int(quarantine_seconds)
        self.failure_quarantine_threshold = int(failure_quarantine_threshold)
        self.min_successes_to_prefer = int(min_successes_to_prefer)
        self._stats: Dict[str, ProxyStats] = {}

    @property
    def proxies(self) -> List[str]:
        return list(self._stats.keys())

    def upsert(self, proxy_url: str) -> ProxyStats:
        if proxy_url not in self._stats:
            self._stats[proxy_url] = ProxyStats(proxy_url=proxy_url)
        return self._stats[proxy_url]

    def add_many(self, proxy_urls: Iterable[str]) -> None:
        for p in proxy_urls:
            p = str(p).strip()
            if not p:
                continue
            self.upsert(p)

    def record_success(self, proxy_url: str, latency_ms: Optional[float] = None) -> None:
        self.upsert(proxy_url).record_success(latency_ms=latency_ms)

    def record_failure(self, proxy_url: str, error: str) -> None:
        self.record_failure_ex(proxy_url, error, force_quarantine=False)

    def record_failure_ex(self, proxy_url: str, error: str, *, force_quarantine: bool) -> None:
        """
        Record a failure and optionally quarantine immediately (even if threshold > 1).

        Use force_quarantine for hard proxy failures like:
        - CONNECT 400/502/503
        - repeated timeouts
        """
        stats = self.upsert(proxy_url)
        should_quarantine = force_quarantine or (stats.failures + 1 >= self.failure_quarantine_threshold)
        quarantine = self.quarantine_seconds if should_quarantine else None
        stats.record_failure(error, quarantine_seconds=quarantine)

    def choose(self, *, now_ts: Optional[float] = None) -> Optional[str]:
        """
        Select a proxy with:
        - not quarantined
        - prefer proxies with successes
        - prefer lower avg latency
        """
        now = time.time() if now_ts is None else now_ts
        candidates: List[ProxyStats] = [s for s in self._stats.values() if not s.is_quarantined(now)]
        if not candidates:
            return None

        # Partition by whether they've ever worked
        proven = [s for s in candidates if s.successes >= self.min_successes_to_prefer]
        pool = proven if proven else candidates

        def score(s: ProxyStats) -> Tuple[int, float, float]:
            # Higher successes first, then lower latency, then more recent success
            lat = s.avg_latency_ms if s.avg_latency_ms is not None else 10**9
            rec = -(s.last_success_ts or 0.0)
            return (-s.successes, float(lat), float(rec))

        pool.sort(key=score)
        return pool[0].proxy_url

    def to_json(self) -> Dict:
        return {
            "version": 1,
            "generated_at": time.time(),
            "config": {
                "quarantine_seconds": self.quarantine_seconds,
                "failure_quarantine_threshold": self.failure_quarantine_threshold,
                "min_successes_to_prefer": self.min_successes_to_prefer,
            },
            "proxies": [asdict(s) for s in self._stats.values()],
        }

    @classmethod
    def from_json(cls, payload: Dict) -> "ProxyPool":
        cfg = payload.get("config") or {}
        pool = cls(
            quarantine_seconds=int(cfg.get("quarantine_seconds", 30 * 60)),
            failure_quarantine_threshold=int(cfg.get("failure_quarantine_threshold", 1)),
            min_successes_to_prefer=int(cfg.get("min_successes_to_prefer", 1)),
        )
        for item in payload.get("proxies") or []:
            try:
                s = ProxyStats(**item)
                pool._stats[s.proxy_url] = s
            except Exception:
                continue
        return pool

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_json(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ProxyPool":
        if not path.exists():
            return cls()
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_json(payload)

