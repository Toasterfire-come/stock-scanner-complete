"""Concurrent execution utilities for stock retrieval."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from .config import StockRetrievalConfig
from .data_transformer import StockPayload, build_stock_payload
from .logging_utils import get_logger
from .session_factory import ProxyPool
from .yfinance_client import FetchResult, YFinanceFetcher


logger = get_logger(__name__)


@dataclass
class WorkerOutcome:
    symbol: str
    payload: Optional[StockPayload]
    fetch_result: Optional[FetchResult]
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    successes: List[StockPayload] = field(default_factory=list)
    failures: List[Dict[str, object]] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    aborted: bool = False
    metrics: Dict[str, float] = field(default_factory=dict)


def _worker(
    symbol: str,
    fetcher: YFinanceFetcher,
    timestamp: datetime,
    proxy_pool: ProxyPool,
) -> WorkerOutcome:
    proxy = proxy_pool.get_proxy(0)
    try:
        fetch_result = fetcher.fetch(symbol)
        if fetch_result.has_data and fetch_result.current_price is not None:
            payload = build_stock_payload(
                symbol=symbol,
                info=fetch_result.info,
                history=fetch_result.history,
                current_price=fetch_result.current_price,
                timestamp=timestamp,
            )
            return WorkerOutcome(symbol=symbol, payload=payload, fetch_result=fetch_result)

        proxy_pool.mark_failure(proxy)
        next_proxy = proxy_pool.rotate()
        return WorkerOutcome(
            symbol=symbol,
            payload=None,
            fetch_result=fetch_result,
            error="no_data",
        )
    except Exception as exc:  # pragma: no cover - defensive catch
        logger.debug("Worker for %s raised exception: %s", symbol, exc)
        proxy_pool.mark_failure(proxy)
        proxy_pool.rotate()
        return WorkerOutcome(symbol=symbol, payload=None, fetch_result=None, error=str(exc))


def run_executor(
    *,
    tickers: Iterable[str],
    config: StockRetrievalConfig,
    fetcher: YFinanceFetcher,
    proxy_pool: ProxyPool,
) -> ExecutionResult:
    start = time.monotonic()
    timestamp = datetime.now(timezone.utc)

    tickers_list = list(tickers)
    result = ExecutionResult()

    if not tickers_list:
        result.elapsed_seconds = 0.0
        return result

    logger.info(
        "Executing pipeline for %s tickers using %s threads",
        len(tickers_list),
        config.max_threads,
    )

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        future_map = {
            executor.submit(_worker, symbol, fetcher, timestamp, proxy_pool): symbol
            for symbol in tickers_list
        }

    for index, future in enumerate(as_completed(future_map), start=1):
            if result.aborted:
                future.cancel()
                continue

            symbol = future_map[future]

            elapsed = time.monotonic() - start
            if config.max_runtime_seconds and elapsed > config.max_runtime_seconds:
                logger.warning(
                    "Runtime guard exceeded (%.2fs > %ss). Aborting remaining tasks.",
                    elapsed,
                    config.max_runtime_seconds,
                )
                result.aborted = True
                break

            try:
                outcome = future.result()
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("Future for %s raised exception: %s", symbol, exc)
                result.failures.append(
                    {
                        "symbol": symbol,
                        "attempts": 0,
                        "errors": [str(exc)],
                    }
                )
                continue

            if outcome.payload is not None:
                result.successes.append(outcome.payload)
            else:
                attempts = outcome.fetch_result.attempts if outcome.fetch_result else 0
                errors = outcome.fetch_result.errors if outcome.fetch_result else []
                if outcome.error and outcome.error not in errors:
                    errors = list(errors) + [outcome.error]

                result.failures.append(
                    {
                        "symbol": symbol,
                        "attempts": attempts,
                        "errors": errors,
                    }
                )

            if index % 50 == 0 or index == len(tickers_list):
                logger.info(
                    "Executor progress: %s/%s processed (%s successes, %s failures)",
                    index,
                    len(tickers_list),
                    len(result.successes),
                    len(result.failures),
                )

    result.elapsed_seconds = time.monotonic() - start
    result.metrics = {
        "success_count": len(result.successes),
        "failure_count": len(result.failures),
        "elapsed_seconds": result.elapsed_seconds,
        "aborted": 1.0 if result.aborted else 0.0,
    }
    return result


__all__ = ["ExecutionResult", "run_executor"]
