"""Configuration helpers for the stock retrieval pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional


PACKAGE_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PACKAGE_ROOT.parent
DEFAULT_LOG_DIR = Path(
    os.getenv("STOCK_RETRIEVAL_LOG_DIR", BACKEND_ROOT / "logs")
)


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no"}


@dataclass(frozen=True)
class StockRetrievalConfig:
    """Immutable configuration for the stock retrieval workflow."""

    combined_ticker_dir: Path = BACKEND_ROOT / "data" / "combined"
    proxy_file: Path = BACKEND_ROOT / "working_proxies.json"
    log_dir: Path = DEFAULT_LOG_DIR
    request_timeout: float = float(os.getenv("STOCK_RETRIEVAL_TIMEOUT", "8.0"))
    per_symbol_timeout: float = float(os.getenv("STOCK_RETRIEVAL_SYMBOL_TIMEOUT", "12.0"))
    max_threads: int = int(os.getenv("STOCK_RETRIEVAL_THREADS", "24"))
    max_runtime_seconds: int = int(os.getenv("STOCK_RETRIEVAL_MAX_RUNTIME", "180"))
    schedule_interval_minutes: int = int(os.getenv("STOCK_RETRIEVAL_SCHEDULE_MINUTES", "3"))
    min_success_ratio: float = float(os.getenv("STOCK_RETRIEVAL_MIN_SUCCESS", "0.97"))
    quality_required_fields: tuple[str, ...] = (
        "current_price",
        "volume",
        "week_52_low",
        "week_52_high",
    )
    use_proxies: bool = _env_flag("STOCK_RETRIEVAL_USE_PROXIES", True)
    save_to_db: bool = _env_flag("STOCK_RETRIEVAL_SAVE_TO_DB", True)
    dry_run: bool = _env_flag("STOCK_RETRIEVAL_DRY_RUN", False)
    max_tickers: Optional[int] = None

    def ensure_directories(self) -> None:
        """Create required directories (log dir, cache folders, etc.)."""

        self.log_dir.mkdir(parents=True, exist_ok=True)

    def with_overrides(
        self,
        *,
        max_tickers: Optional[int] = None,
        use_proxies: Optional[bool] = None,
        save_to_db: Optional[bool] = None,
        dry_run: Optional[bool] = None,
        max_threads: Optional[int] = None,
        request_timeout: Optional[float] = None,
        per_symbol_timeout: Optional[float] = None,
        max_runtime_seconds: Optional[int] = None,
        schedule_interval_minutes: Optional[int] = None,
        log_dir: Optional[Path] = None,
    ) -> "StockRetrievalConfig":
        """Return a new config with the provided overrides applied."""

        return replace(
            self,
            max_tickers=max_tickers if max_tickers is not None else self.max_tickers,
            use_proxies=self.use_proxies if use_proxies is None else use_proxies,
            save_to_db=self.save_to_db if save_to_db is None else save_to_db,
            dry_run=self.dry_run if dry_run is None else dry_run,
            max_threads=self.max_threads if max_threads is None else max_threads,
            request_timeout=self.request_timeout
            if request_timeout is None
            else request_timeout,
            per_symbol_timeout=self.per_symbol_timeout
            if per_symbol_timeout is None
            else per_symbol_timeout,
            max_runtime_seconds=self.max_runtime_seconds
            if max_runtime_seconds is None
            else max_runtime_seconds,
            schedule_interval_minutes=self.schedule_interval_minutes
            if schedule_interval_minutes is None
            else schedule_interval_minutes,
            log_dir=self.log_dir if log_dir is None else log_dir,
        )


def build_config_from_args(args: Optional[object]) -> StockRetrievalConfig:
    """Construct configuration instance from CLI arguments."""

    base = StockRetrievalConfig()
    if args is None:
        return base

    overrides: dict[str, object] = {}

    if getattr(args, "max_tickers", None) is not None:
        overrides["max_tickers"] = args.max_tickers
    if getattr(args, "threads", None) is not None:
        overrides["max_threads"] = args.threads
    if getattr(args, "timeout", None) is not None:
        overrides["request_timeout"] = float(args.timeout)
    if getattr(args, "symbol_timeout", None) is not None:
        overrides["per_symbol_timeout"] = float(args.symbol_timeout)
    if getattr(args, "max_runtime", None) is not None:
        overrides["max_runtime_seconds"] = int(args.max_runtime)

    if getattr(args, "no_db", False):
        overrides["save_to_db"] = False
        overrides["dry_run"] = True
    if getattr(args, "dry_run", False):
        overrides["dry_run"] = True
    if getattr(args, "no_proxies", False):
        overrides["use_proxies"] = False
    if getattr(args, "interval_minutes", None) is not None:
        overrides["schedule_interval_minutes"] = int(args.interval_minutes)

    return base.with_overrides(**overrides)


__all__ = [
    "StockRetrievalConfig",
    "build_config_from_args",
]
