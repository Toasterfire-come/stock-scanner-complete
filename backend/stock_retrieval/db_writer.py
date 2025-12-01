"""Database persistence helpers for stock retrieval payloads."""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

import django
from django.db import transaction

from .logging_utils import get_logger


logger = get_logger(__name__)

DJANGO_READY = False
Stock = None
StockPrice = None


def _ensure_django_ready() -> None:
    global DJANGO_READY, Stock, StockPrice

    if DJANGO_READY:
        return

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
    django.setup()

    from stocks.models import Stock as StockModel, StockPrice as StockPriceModel  # type: ignore

    Stock = StockModel
    StockPrice = StockPriceModel
    DJANGO_READY = True
    logger.info("Django environment initialized for persistence.")


def _coerce_int(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass
class PersistenceSummary:
    saved: int = 0
    price_records: int = 0
    errors: List[str] = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def persist_payloads(payloads: Iterable["StockPayload"]) -> PersistenceSummary:
    from .data_transformer import StockPayload  # local import to avoid circular refs

    _ensure_django_ready()

    summary = PersistenceSummary()

    integer_fields = {
        "volume",
        "volume_today",
        "avg_volume_3mon",
        "shares_available",
        "market_cap",
    }

    for payload in payloads:
        data = dict(payload.data)

        for field in integer_fields:
            data[field] = _coerce_int(data.get(field))

        try:
            with transaction.atomic():
                stock_obj, _ = Stock.objects.update_or_create(
                    ticker=payload.symbol,
                    defaults=data,
                )

                if data.get("current_price") is not None:
                    StockPrice.objects.create(
                        stock=stock_obj,
                        price=data["current_price"],
                    )
                    summary.price_records += 1

                summary.saved += 1
        except Exception as exc:  # pragma: no cover - database failure path
            logger.error("Failed to persist payload for %s: %s", payload.symbol, exc)
            summary.errors.append(f"{payload.symbol}:{exc}")

    return summary


__all__ = ["persist_payloads", "PersistenceSummary"]
