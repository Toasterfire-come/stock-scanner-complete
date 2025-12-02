"""Logging utilities for the stock retrieval pipeline."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_logging(
    log_dir: Path,
    *,
    log_level: int = logging.INFO,
    log_filename: str = "stock_retrieval.log",
    include_console: bool = True,
) -> None:
    """Configure application logging with shared settings."""

    log_dir.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = []

    file_handler = RotatingFileHandler(
        log_dir / log_filename,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(file_handler)

    if include_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handlers.append(console_handler)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    for handler in handlers:
        root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger instance with the configured root settings."""

    return logging.getLogger(name)


__all__ = ["setup_logging", "get_logger"]
