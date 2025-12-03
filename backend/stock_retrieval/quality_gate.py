"""Payload quality validation utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .config import StockRetrievalConfig
from .logging_utils import get_logger


logger = get_logger(__name__)


@dataclass
class QualityIssue:
    symbol: str
    reasons: List[str] = field(default_factory=list)


@dataclass
class QualityStats:
    total: int = 0
    passed: int = 0
    failed: int = 0
    issues: List[QualityIssue] = field(default_factory=list)

    @property
    def success_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total

    def record_pass(self) -> None:
        self.total += 1
        self.passed += 1

    def record_fail(self, issue: QualityIssue) -> None:
        self.total += 1
        self.failed += 1
        self.issues.append(issue)


class QualityGate:
    def __init__(self, config: StockRetrievalConfig) -> None:
        self.config = config
        self.stats = QualityStats()

    def evaluate(self, payload: Dict[str, object]) -> bool:
        issue = QualityIssue(symbol=str(payload.get("symbol")))

        for field in self.config.quality_required_fields:
            if payload.get(field) in (None, ""):
                issue.reasons.append(f"missing_required_field:{field}")

        timestamp = payload.get("last_updated")
        if timestamp:
            try:
                if isinstance(timestamp, datetime):
                    ts = timestamp
                else:
                    ts = datetime.fromisoformat(str(timestamp))
                age_seconds = (datetime.now(timezone.utc) - ts).total_seconds()
                if age_seconds > 300:
                    issue.reasons.append("stale_timestamp")
            except Exception:
                issue.reasons.append("invalid_timestamp")
        else:
            issue.reasons.append("missing_timestamp")

        volume = payload.get("volume")
        if volume in (None, 0):
            issue.reasons.append("invalid_volume")

        if issue.reasons:
            self.stats.record_fail(issue)
            logger.debug(
                "Quality gate failed for %s due to %s",
                issue.symbol,
                ",".join(issue.reasons),
            )
            return False

        self.stats.record_pass()
        return True


__all__ = ["QualityGate", "QualityStats", "QualityIssue"]
