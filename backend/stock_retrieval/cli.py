"""Command-line interface for the stock retrieval pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import time
from typing import Any, Dict, Optional

from .config import StockRetrievalConfig, build_config_from_args
from .logging_utils import get_logger, setup_logging
from .pipeline import run_pipeline


logger = get_logger(__name__)
_stop_requested = False


def _signal_handler(signum: int, frame: object) -> None:  # pragma: no cover - signal handling
    global _stop_requested
    logger.warning("Received signal %s, requesting stop after current run.", signum)
    _stop_requested = True


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the stock retrieval pipeline using yfinance.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--max-tickers", type=int, default=None, help="Limit number of tickers processed")
    parser.add_argument("--threads", type=int, default=None, help="Override max worker threads")
    parser.add_argument("--timeout", type=float, default=None, help="HTTP request timeout in seconds")
    parser.add_argument("--symbol-timeout", type=float, default=None, help="Per-symbol execution timeout")
    parser.add_argument("--max-runtime", type=int, default=None, help="Maximum runtime (seconds) before aborting run")

    parser.add_argument("--no-proxies", action="store_true", help="Disable proxy usage even if configured")
    parser.add_argument("--dry-run", action="store_true", help="Skip database writes and capture metrics only")
    parser.add_argument("--no-db", action="store_true", help="Disable database persistence (implies dry-run)")

    parser.add_argument("--schedule", action="store_true", help="Enable continuous scheduler mode")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=None,
        help="Override schedule interval in minutes",
    )

    parser.add_argument(
        "--log-level",
        default=os.getenv("STOCK_RETRIEVAL_LOG_LEVEL", "INFO"),
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument("--json", action="store_true", help="Emit run summary as JSON to stdout")

    parser.add_argument("--version", action="store_true", help="Print package version and exit")

    return parser.parse_args(argv)


def _log_level_from_string(value: str) -> int:
    try:
        return getattr(logging, value.upper())
    except AttributeError as exc:  # pragma: no cover - defensive path
        raise ValueError(f"Invalid log level: {value}") from exc


def configure_environment(args: argparse.Namespace) -> StockRetrievalConfig:
    if args.version:
        from . import __version__

        print(__version__)
        raise SystemExit(0)

    return build_config_from_args(args)


def run_once(config: StockRetrievalConfig, *, emit_json: bool = False) -> Dict[str, Any]:
    result = run_pipeline(config)
    if emit_json:
        print(json.dumps(result, indent=2, default=str))
    return result


def run_scheduler(config: StockRetrievalConfig, *, emit_json: bool = False) -> None:
    interval_seconds = max(60, config.schedule_interval_minutes * 60)
    logger.info(
        "Scheduler initialized with %s-minute interval.",
        config.schedule_interval_minutes,
    )

    while not _stop_requested:
        start = time.monotonic()
        run_once(config, emit_json=emit_json)
        if _stop_requested:
            break

        elapsed = time.monotonic() - start
        sleep_seconds = max(0.0, interval_seconds - elapsed)
        if sleep_seconds > 0:
            logger.info("Sleeping %.2f seconds before next run.", sleep_seconds)
            time.sleep(sleep_seconds)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    config = configure_environment(args)

    log_level = _log_level_from_string(args.log_level)
    setup_logging(config.log_dir, log_level=log_level)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    logger.info("Starting stock retrieval CLI with config: %s", config)

    if args.schedule:
        run_scheduler(config, emit_json=args.json)
    else:
        run_once(config, emit_json=args.json)

    logger.info("Stock retrieval CLI exiting. stop_requested=%s", _stop_requested)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    sys.exit(main())
