"""Pipeline scaffold for the stock retrieval workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from collections import Counter

from .config import StockRetrievalConfig
from .logging_utils import get_logger
from .data_transformer import StockPayload
from .quality_gate import QualityGate
from .session_factory import (
    ProxyPool,
    configure_yfinance_session,
    create_requests_session,
)
from .ticker_loader import load_combined_tickers
from .executor import run_executor
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
    proxy = None
    if proxy_pool.enabled and proxy_pool.proxies:
        proxy = proxy_pool.acquire()
        session = create_requests_session(proxy=proxy, timeout=config.request_timeout)
        configure_yfinance_session(session)

    fetcher = YFinanceFetcher(
        proxy_pool=proxy_pool,
        request_timeout=config.request_timeout,
    )
    exec_result = run_executor(
        tickers=ticker_result.tickers,
        config=config,
        fetcher=fetcher,
        proxy_pool=proxy_pool,
    )

    quality_gate = QualityGate(config)
    quality_passed_payloads: List[StockPayload] = []

    for payload in exec_result.successes:
        if quality_gate.evaluate(payload.data):
            quality_passed_payloads.append(payload)

    meets_threshold = quality_gate.stats.success_ratio >= config.min_success_ratio

    status = "completed"
    if exec_result.aborted:
        status = "aborted"
    elif exec_result.failures or quality_gate.stats.failed:
        status = "incomplete"

    persistence_summary = {
        "saved": 0,
        "price_records": 0,
        "errors": [],
    }

    if config.save_to_db and not config.dry_run and quality_passed_payloads:
        from .db_writer import persist_payloads

        persistence = persist_payloads(quality_passed_payloads)
        persistence_summary = {
            "saved": persistence.saved,
            "price_records": persistence.price_records,
            "errors": persistence.errors,
        }

        if persistence.errors:
            logger.warning(
                "Persistence completed with %s error(s)", len(persistence.errors)
            )

    failure_reasons: Counter[str] = Counter()
    for failure in exec_result.failures:
        for err in failure.get("errors", []) or []:
            failure_reasons[err] += 1

    top_failure_causes = failure_reasons.most_common(5)
    success_ratio = (
        (len(exec_result.successes) / max(1, len(exec_result.successes) + len(exec_result.failures)))
        * 100
    )
    quality_ratio = quality_gate.stats.success_ratio * 100

    logger.info(
        "Run summary: %d processed | %.1f%% success | quality %.1f%% (target %.1f%%) | runtime %.1fs",
        len(exec_result.successes) + len(exec_result.failures),
        success_ratio,
        quality_ratio,
        config.min_success_ratio * 100,
        exec_result.elapsed_seconds,
    )
    if top_failure_causes:
        formatted_causes = "; ".join(f"{err[:80]} ({count})" for err, count in top_failure_causes)
        logger.info("Top failure causes: %s", formatted_causes)
    if not meets_threshold:
        logger.warning(
            "Quality ratio %.2f%% below required %.2f%%; %d payloads queued for retry",
            quality_ratio,
            config.min_success_ratio * 100,
            len(exec_result.failures),
        )

    summary: Dict[str, Any] = {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tickers_loaded": len(ticker_result.tickers),
        "tickers_processed": len(exec_result.successes) + len(exec_result.failures),
        "ticker_source": ticker_result.source.name,
        "max_threads": config.max_threads,
        "max_runtime_seconds": config.max_runtime_seconds,
        "proxy_enabled": proxy_pool.enabled,
        "proxy_in_use": proxy,
        "executor_elapsed_seconds": exec_result.elapsed_seconds,
        "executor_aborted": exec_result.aborted,
        "success_count": len(exec_result.successes),
        "failure_count": len(exec_result.failures),
        "executor_metrics": exec_result.metrics,
        "quality_passed": quality_gate.stats.passed,
        "quality_failed": quality_gate.stats.failed,
        "quality_success_ratio": round(quality_gate.stats.success_ratio, 4),
        "meets_quality_threshold": meets_threshold,
        "dry_run": config.dry_run,
        "ready_for_persistence": len(quality_passed_payloads),
        "persistence_saved": persistence_summary["saved"],
        "persistence_price_records": persistence_summary["price_records"],
        "persistence_errors": persistence_summary["errors"][:5],
        "sample_successes": [payload.symbol for payload in quality_passed_payloads[:5]],
        "sample_failures": exec_result.failures[:5],
        "quality_issues": [
            {"symbol": issue.symbol, "reasons": issue.reasons[:5]}
            for issue in quality_gate.stats.issues[:5]
        ],
        "top_failure_reasons": top_failure_causes,
    }
    logger.info("Pipeline summary: %s", summary)
    return summary


__all__ = ["run_pipeline"]
