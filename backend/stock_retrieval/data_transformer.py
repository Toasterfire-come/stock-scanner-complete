"""Data transformation helpers for the stock retrieval pipeline."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Mapping, Optional

import pandas as pd


PE_RATIO_FIELDS = (
    "trailingPE",
    "forwardPE",
    "priceToBook",
    "priceToSalesTrailing12Months",
)

DIVIDEND_FIELDS = (
    "dividendYield",
    "fiveYearAvgDividendYield",
    "trailingAnnualDividendYield",
)


def safe_decimal(value: Any) -> Optional[Decimal]:
    """Safely convert value to ``Decimal`` when possible."""

    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, str)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None

    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return Decimal(str(value))

    if pd.isna(value):  # type: ignore[call-arg]
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


def extract_pe_ratio(info: Mapping[str, Any]) -> Optional[float]:
    for field in PE_RATIO_FIELDS:
        value = info.get(field)
        if value is None or pd.isna(value):  # type: ignore[call-arg]
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric != 0:
            return numeric
    return None


def extract_dividend_yield(info: Mapping[str, Any]) -> Optional[float]:
    for field in DIVIDEND_FIELDS:
        value = info.get(field)
        if value is None or pd.isna(value):  # type: ignore[call-arg]
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if 0 < numeric < 1:
            return numeric * 100
        return numeric
    return None


def compute_price_changes(history: Optional[pd.DataFrame]) -> Dict[str, Optional[Decimal]]:
    if history is None or history.empty:
        return {
            "price_change_today": None,
            "price_change_week": None,
            "price_change_month": None,
            "price_change_year": None,
            "change_percent": None,
        }

    close = history.get("Close")
    if close is None or close.empty:
        return {
            "price_change_today": None,
            "price_change_week": None,
            "price_change_month": None,
            "price_change_year": None,
            "change_percent": None,
        }

    result: Dict[str, Optional[Decimal]] = {
        "price_change_today": None,
        "price_change_week": None,
        "price_change_month": None,
        "price_change_year": None,
        "change_percent": None,
    }

    periods = {
        "price_change_today": 1,
        "price_change_week": 5,
        "price_change_month": 21,
        "price_change_year": 252,
    }

    latest = close.iloc[-1]

    for field, steps in periods.items():
        if len(close) <= steps:
            continue
        previous = close.iloc[-(steps + 1)]
        if previous is None or pd.isna(previous):  # type: ignore[call-arg]
            continue
        try:
            diff = float(latest) - float(previous)
            result[field] = safe_decimal(diff)
        except (TypeError, ValueError):
            continue

    if result["price_change_today"] is not None and len(close) > 1:
        previous_close = close.iloc[-2]
        if previous_close is not None and not pd.isna(previous_close):  # type: ignore[call-arg]
            try:
                change_percent = (
                    (float(latest) - float(previous_close)) / float(previous_close)
                ) * 100
                result["change_percent"] = safe_decimal(change_percent)
            except (ZeroDivisionError, TypeError, ValueError):
                pass

    return result


def compute_volume_ratio(volume: Optional[Decimal], average_volume: Optional[Decimal]) -> Optional[Decimal]:
    if not volume or not average_volume:
        return None
    if average_volume == 0:
        return None
    try:
        return safe_decimal(volume / average_volume)
    except (InvalidOperation, ZeroDivisionError, TypeError):
        return None


@dataclass
class StockPayload:
    symbol: str
    data: Dict[str, Any]


def build_stock_payload(
    *,
    symbol: str,
    info: Mapping[str, Any],
    history: Optional[pd.DataFrame],
    current_price: Optional[float],
    timestamp: datetime,
) -> StockPayload:
    info = info or {}
    payload: Dict[str, Any] = {
        "ticker": symbol,
        "symbol": symbol,
        "company_name": info.get("longName") or info.get("shortName") or symbol,
        "current_price": safe_decimal(current_price),
        "days_low": safe_decimal(info.get("dayLow")),
        "days_high": safe_decimal(info.get("dayHigh")),
        "volume": safe_decimal(info.get("volume")),
        "volume_today": safe_decimal(info.get("volume")),
        "avg_volume_3mon": safe_decimal(info.get("averageVolume")),
        "market_cap": safe_decimal(info.get("marketCap")),
        "pe_ratio": safe_decimal(extract_pe_ratio(info)),
        "dividend_yield": safe_decimal(extract_dividend_yield(info)),
        "one_year_target": safe_decimal(info.get("targetMeanPrice")),
        "week_52_low": safe_decimal(info.get("fiftyTwoWeekLow")),
        "week_52_high": safe_decimal(info.get("fiftyTwoWeekHigh")),
        "earnings_per_share": safe_decimal(info.get("trailingEps")),
        "book_value": safe_decimal(info.get("bookValue")),
        "price_to_book": safe_decimal(info.get("priceToBook")),
        "exchange": info.get("exchange"),
        "last_updated": timestamp,
        "created_at": timestamp,
    }

    payload.update(compute_price_changes(history))

    volume_ratio = compute_volume_ratio(payload["volume"], payload["avg_volume_3mon"])
    payload["dvav"] = volume_ratio

    return StockPayload(symbol=symbol, data=payload)


__all__ = [
    "StockPayload",
    "build_stock_payload",
    "compute_price_changes",
    "compute_volume_ratio",
    "extract_dividend_yield",
    "extract_pe_ratio",
    "safe_decimal",
]
