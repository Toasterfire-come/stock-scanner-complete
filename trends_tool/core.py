from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class TrendsConfig:
    """Configuration for Google Trends queries."""

    keywords: List[str]
    timeframe: str = "today 5-y"
    geo: str = ""
    gprop: str = ""
    category: int = 0
    language: str = "en-US"
    timezone_minutes: int = 360
    retries: int = 2
    backoff_factor: float = 0.2
    connect_timeout_seconds: int = 10
    read_timeout_seconds: int = 25


def _create_trends_client(config: TrendsConfig):
    """Create and return a configured pytrends client lazily.

    Imported lazily so that help/usage can run without dependencies installed.
    """

    try:
        from pytrends.request import TrendReq  # type: ignore
    except Exception as import_error:
        raise RuntimeError(
            "pytrends is required. Install dependencies with: pip install -r requirements.txt"
        ) from import_error

    return TrendReq(
        hl=config.language,
        tz=config.timezone_minutes,
        retries=config.retries,
        backoff_factor=config.backoff_factor,
        timeout=(config.connect_timeout_seconds, config.read_timeout_seconds),
    )


def fetch_interest_over_time(config: TrendsConfig) -> pd.DataFrame:
    """Fetch interest over time for the provided keywords.

    Returns a DataFrame with a datetime index and one column per keyword.
    """

    if not config.keywords or not any(k.strip() for k in config.keywords):
        raise ValueError("At least one non-empty keyword must be provided")

    client = _create_trends_client(config)
    client.build_payload(
        kw_list=[k.strip() for k in config.keywords if k.strip()],
        cat=config.category,
        timeframe=config.timeframe,
        geo=config.geo,
        gprop=config.gprop,
    )

    data = client.interest_over_time()
    if data is None or data.empty:
        return pd.DataFrame()

    cleaned = data.drop(columns=[c for c in data.columns if c.lower() == "ispartial"], errors="ignore")
    cleaned.index.name = "date"
    return cleaned


def fetch_related_queries(
    config: TrendsConfig,
) -> Dict[str, Dict[str, Optional[pd.DataFrame]]]:
    """Fetch related queries for each keyword.

    Returns a mapping keyword -> {"top": DataFrame | None, "rising": DataFrame | None}
    """

    client = _create_trends_client(config)
    client.build_payload(
        kw_list=[k.strip() for k in config.keywords if k.strip()],
        cat=config.category,
        timeframe=config.timeframe,
        geo=config.geo,
        gprop=config.gprop,
    )

    related = client.related_queries() or {}
    # Ensure dictionaries exist for all keywords
    ensured: Dict[str, Dict[str, Optional[pd.DataFrame]]] = {}
    for keyword in config.keywords:
        keyword_stripped = keyword.strip()
        if not keyword_stripped:
            continue
        krel = related.get(keyword_stripped) or {}
        ensured[keyword_stripped] = {
            "top": krel.get("top"),
            "rising": krel.get("rising"),
        }
    return ensured


def compute_latest_values(interest_df: pd.DataFrame) -> List[Tuple[str, Optional[int]]]:
    """Return the latest non-null values per keyword column.

    Values are integers on a 0-100 scale or None if no data.
    """

    if interest_df is None or interest_df.empty:
        return []

    latest_row = interest_df.tail(1)
    results: List[Tuple[str, Optional[int]]] = []
    for column_name in interest_df.columns:
        value = latest_row[column_name].iloc[0]
        results.append((column_name, int(value) if pd.notna(value) else None))
    return results

