"""Ticker loading utilities for the stock retrieval pipeline."""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable, List

from .config import StockRetrievalConfig
from .logging_utils import get_logger


logger = get_logger(__name__)

_TICKER_PATTERN = re.compile(r"^[A-Z0-9.=-]{1,8}$")


@dataclass(frozen=True)
class TickerLoadResult:
    tickers: List[str]
    source: Path


def _find_latest_module(directory: Path) -> Path:
    candidates = sorted(
        directory.glob("combined_tickers_*.py"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No combined ticker modules found in {directory}."
        )
    return candidates[0]


def _load_module_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalize_tickers(raw_tickers: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()

    for ticker in raw_tickers:
        if not ticker:
            continue

        candidate = ticker.strip().upper()
        if candidate in seen:
            continue

        if not _TICKER_PATTERN.match(candidate):
            logger.debug("Skipping ticker %s due to validation failure.", ticker)
            continue

        seen.add(candidate)
        normalized.append(candidate)

    return normalized


def load_combined_tickers(config: StockRetrievalConfig) -> TickerLoadResult:
    directory = config.combined_ticker_dir
    module_path = _find_latest_module(directory)
    logger.info("Loading combined tickers from %s", module_path.name)

    module = _load_module_from_path(module_path)
    tickers = getattr(module, "COMBINED_TICKERS", None)
    if tickers is None:
        raise AttributeError(
            f"Module {module_path} does not define COMBINED_TICKERS."
        )

    normalized = _normalize_tickers(tickers)
    logger.info("Loaded %s tickers from %s", len(normalized), module_path.name)

    if config.max_tickers:
        sliced = normalized[: config.max_tickers]
        logger.info(
            "Applying max_tickers=%s override (from %s to %s).",
            config.max_tickers,
            len(normalized),
            len(sliced),
        )
        normalized = sliced

    return TickerLoadResult(tickers=normalized, source=module_path)


__all__ = ["TickerLoadResult", "load_combined_tickers"]
