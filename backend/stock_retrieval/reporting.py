"""Reporting helpers for stock retrieval summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .logging_utils import get_logger


logger = get_logger(__name__)


def _prepare_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str)
    return value


def write_json_summary(summary: Mapping[str, Any], path: str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(summary, indent=2, default=str))
    logger.info("Summary written to JSON file %s", file_path)


def write_csv_summary(summary: Mapping[str, Any], path: str) -> None:
    import csv

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "value"])
        for key, value in summary.items():
            writer.writerow([key, _prepare_value(value)])

    logger.info("Summary written to CSV file %s", file_path)


__all__ = ["write_json_summary", "write_csv_summary"]
