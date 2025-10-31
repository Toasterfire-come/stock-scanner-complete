"""Pipeline scaffold for the stock retrieval workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import StockRetrievalConfig
from .logging_utils import get_logger
from .data_transformer import StockPayload, build_stock_payload
from .session_factory import (
    ProxyPool,
    configure_yfinance_session,
    create_requests_session,
)
from .ticker_loader import load_combined_tickers
from .yfinance_client import YFinanceFetcher


logger = get_logger(__name__)


def run_pipeline(config: StockRetrievalConfig) -> Dict[str, Any]:
    """Execute a single stock retrieval cycle (placeholder implementation)."""

    config.ensure_directories()
    logger.info("Stock retrieval pipeline scaffolding initialized.")
    logger.info(
        "Configuration summary | threads=%s timeout=%s max_runtime=%s",
        config.max_threads,
        config.request_timeout,
        config.max_runtime_seconds,
    )

    ticker_result = load_combined_tickers(config)
    logger.info(
        "Discovered %s tickers from %s", len(ticker_result.tickers), ticker_result.source.name
    )

    proxy_pool = ProxyPool.from_config(config)
    proxy = proxy_pool.get_proxy(0)
    session = create_requests_session(proxy=proxy, timeout=config.request_timeout)
    configure_yfinance_session(session)

    fetcher = YFinanceFetcher()
    processed_payloads: List[StockPayload] = []
    failures: List[Dict[str, Any]] = []

    start_time = datetime.now(timezone.utc)

    for index, symbol in enumerate(ticker_result.tickers, start=1):
        fetch_result = fetcher.fetch(symbol)

        if fetch_result.has_data:
            payload = build_stock_payload(
                symbol=symbol,
                info=fetch_result.info,
                history=fetch_result.history,
                current_price=fetch_result.current_price,
                timestamp=start_time,
            )
            processed_payloads.append(payload)
        else:
            failures.append(
                {
                    "symbol": symbol,
                    "attempts": fetch_result.attempts,
                    "errors": fetch_result.errors,
                }
            )

        if index % 50 == 0:
            logger.info(
                "Progress: %s tickers processed (%s successes, %s failures)",
                index,
                len(processed_payloads),
                len(failures),
            )

    total_processed = len(processed_payloads) + len(failures)

    status = "incomplete" if failures else "completed"

    summary: Dict[str, Any] = {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tickers_loaded": len(ticker_result.tickers),
        "tickers_processed": total_processed,
        "ticker_source": ticker_result.source.name,
        "max_threads": config.max_threads,
        "max_runtime_seconds": config.max_runtime_seconds,
        "proxy_enabled": proxy_pool.enabled,
        "proxy_in_use": proxy,
        "success_count": len(processed_payloads),
        "failure_count": len(failures),
        "sample_successes": [payload.symbol for payload in processed_payloads[:5]],
        "sample_failures": failures[:5],
    }
    logger.info("Pipeline summary: %s", summary)
    return summary


__all__ = ["run_pipeline"]
