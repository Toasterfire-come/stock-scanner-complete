"""yfinance wrapper providing resilient data retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
import yfinance as yf

from .logging_utils import get_logger
from .session_factory import ProxyPool, create_requests_session


logger = get_logger(__name__)


HISTORY_PERIODS_DEFAULT: Sequence[str] = ("1d", "5d", "1mo")


@dataclass
class FetchResult:
    symbol: str
    info: Dict[str, Any] = field(default_factory=dict)
    history: Optional[pd.DataFrame] = None
    current_price: Optional[float] = None
    attempts: int = 0
    errors: List[str] = field(default_factory=list)
    proxy: Optional[str] = None

    @property
    def has_data(self) -> bool:
        if self.history is not None and not self.history.empty:
            return True
        return bool(self.info)


class YFinanceFetcher:
    def __init__(
        self,
        *,
        history_periods: Sequence[str] = HISTORY_PERIODS_DEFAULT,
        max_attempts: int = 3,
        proxy_pool: Optional[ProxyPool] = None,
        request_timeout: float = 8.0,
    ) -> None:
        self.history_periods = history_periods
        self.max_attempts = max_attempts
        self.proxy_pool = proxy_pool
        self.request_timeout = request_timeout

    def fetch(self, symbol: str) -> FetchResult:
        result = FetchResult(symbol=symbol)

        for attempt in range(1, self.max_attempts + 1):
            proxy = self._select_proxy()
            session = (
                create_requests_session(proxy=proxy, timeout=self.request_timeout)
                if proxy
                else None
            )
            ticker = yf.Ticker(symbol, session=session) if session else yf.Ticker(symbol)
            result.attempts = attempt
            result.proxy = proxy

            if not result.info:
                try:
                    info = ticker.info
                    if isinstance(info, dict) and info:
                        result.info = info
                except Exception as exc:  # pragma: no cover - network failure path
                    message = f"Attempt {attempt} info error: {exc}"
                    logger.debug("%s", message)
                    result.errors.append(message)
                    reason = "rate_limited" if "Too Many Requests" in message else str(exc)
                    self._handle_failure(proxy, reason=reason)
                    continue

            if result.history is None or result.history.empty:
                history = self._fetch_history(ticker)
                if history is not None and not history.empty:
                    result.history = history
                else:
                    if proxy:
                        self._handle_failure(proxy, reason="empty_history")

            if result.current_price is None:
                result.current_price = self._derive_current_price(ticker, result)

            if result.has_data and result.current_price is not None:
                self._record_success(proxy)
                break
            else:
                self._handle_failure(proxy, reason="no_data")

        if not result.has_data:
            logger.debug("No data retrieved for %s after %s attempts", symbol, result.attempts)

        return result

    def _select_proxy(self) -> Optional[str]:
        if self.proxy_pool is None:
            return None
        proxy = self.proxy_pool.acquire()
        if proxy:
            logger.debug("Using proxy %s", proxy)
        return proxy

    def _handle_failure(self, proxy: Optional[str], *, reason: str | None = None) -> None:
        if self.proxy_pool is None or proxy is None:
            return
        self.proxy_pool.mark_failure(proxy, reason=reason)
        self.proxy_pool.rotate()

    def _record_success(self, proxy: Optional[str]) -> None:
        if self.proxy_pool is None or proxy is None:
            return
        self.proxy_pool.record_success(proxy)

    def _fetch_history(self, ticker: yf.Ticker) -> Optional[pd.DataFrame]:
        for period in self.history_periods:
            try:
                history = ticker.history(period=period)
            except Exception as exc:  # pragma: no cover - network failure path
                logger.debug("History fetch failed for period %s: %s", period, exc)
                continue

            if history is not None and not history.empty:
                return history
        return None

    def _derive_current_price(self, ticker: yf.Ticker, result: FetchResult) -> Optional[float]:
        if result.history is not None and not result.history.empty:
            try:
                return float(result.history["Close"].iloc[-1])
            except Exception:
                pass

        if result.info:
            for key in ("currentPrice", "regularMarketPrice", "regularMarketOpen"):
                value = result.info.get(key)
                if value is not None:
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        continue

        try:
            fast_info = getattr(ticker, "fast_info", None)
            if fast_info:
                for key in ("lastPrice", "last_price", "regularMarketPrice"):
                    value = fast_info.get(key) if isinstance(fast_info, dict) else getattr(fast_info, key, None)
                    if value is not None:
                        try:
                            return float(value)
                        except (TypeError, ValueError):
                            continue
        except Exception as exc:  # pragma: no cover - best-effort path
            logger.debug("fast_info retrieval failed: %s", exc)

        return None


__all__ = ["FetchResult", "YFinanceFetcher"]
