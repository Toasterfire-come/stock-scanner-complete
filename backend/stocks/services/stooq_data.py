from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests


@dataclass(frozen=True)
class StooqSourceConfig:
    """
    Stooq market-data configuration.

    - STOOQ_COMBINED_CSV: Optional path to a combined CSV produced by scripts/stooq_combine.py
      Expected columns (case-insensitive):
        - symbol
        - datetime (or date + time)
        - open, high, low, close
        - volume (optional)
        - interval (optional; e.g. 5, 60, 'D')
    - STOOQ_BASE_URL: Optional override for remote CSV endpoint.
    """

    combined_csv: Optional[str]
    base_url: str

    @staticmethod
    def from_env() -> "StooqSourceConfig":
        return StooqSourceConfig(
            combined_csv=os.environ.get("STOOQ_COMBINED_CSV") or None,
            base_url=os.environ.get("STOOQ_BASE_URL") or "https://stooq.com",
        )


def _normalize_ohlcv_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a Stooq/yfinance-like dataframe into our backtester schema:
      Date, Open, High, Low, Close, Volume
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Accept either Date column or Date index
    if "Date" not in df.columns:
        if getattr(df.index, "name", None) == "Date":
            df = df.reset_index()
        elif isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index().rename(columns={"index": "Date"})

    # Standardize column names (Stooq is usually capitalized already)
    rename = {}
    for col in df.columns:
        c = str(col).strip()
        rename[c] = c[0].upper() + c[1:] if c and c[0].islower() else c
    df = df.rename(columns=rename)

    required = ["Date", "Open", "High", "Low", "Close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return pd.DataFrame()

    if "Volume" not in df.columns:
        df["Volume"] = 0

    out = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out = out.dropna(subset=["Date"])
    out = out.sort_values("Date")
    return out.reset_index(drop=True)


def fetch_stooq_remote_daily(symbol: str, start_date, end_date, *, cfg: StooqSourceConfig) -> pd.DataFrame:
    """
    Fetch daily OHLCV from Stooq's public CSV endpoint.

    Endpoint pattern (documented by Stooq):
      /q/d/l/?s=<symbol>&i=d
    """
    sym = (symbol or "").strip()
    if not sym:
        return pd.DataFrame()

    url = f"{cfg.base_url.rstrip('/')}/q/d/l/"
    try:
        r = requests.get(url, params={"s": sym.lower(), "i": "d"}, timeout=15)
        r.raise_for_status()
        from io import StringIO

        df = pd.read_csv(StringIO(r.text))
    except Exception:
        return pd.DataFrame()

    df = _normalize_ohlcv_df(df)
    if df.empty:
        return df

    # Filter date range (inclusive)
    start_dt = pd.to_datetime(start_date, errors="coerce")
    end_dt = pd.to_datetime(end_date, errors="coerce")
    if pd.notna(start_dt):
        df = df[df["Date"] >= start_dt]
    if pd.notna(end_dt):
        df = df[df["Date"] <= end_dt]
    return df.reset_index(drop=True)


def fetch_stooq_from_combined_csv(
    symbol: str,
    start_date,
    end_date,
    *,
    cfg: StooqSourceConfig,
    interval: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load OHLCV for a symbol from a locally combined Stooq CSV.
    Designed to support hourly/5m as well as daily if you combine those zips too.
    """
    if not cfg.combined_csv:
        return pd.DataFrame()

    try:
        df = pd.read_csv(cfg.combined_csv)
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    # Case-insensitive column mapping
    cols = {str(c).strip().lower(): c for c in df.columns}
    sym_col = cols.get("symbol")
    dt_col = cols.get("datetime") or cols.get("date")
    if not sym_col or not dt_col:
        return pd.DataFrame()

    # Filter symbol
    sym = (symbol or "").strip().upper()
    df = df[df[sym_col].astype(str).str.upper() == sym]

    # Optional interval filtering
    if interval is not None and "interval" in cols:
        df = df[df[cols["interval"]].astype(str) == str(interval)]

    # Parse datetime
    df = df.copy()
    df["Date"] = pd.to_datetime(df[dt_col], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Map OHLCV
    for want in ("open", "high", "low", "close"):
        if want not in cols:
            return pd.DataFrame()

    df["Open"] = pd.to_numeric(df[cols["open"]], errors="coerce")
    df["High"] = pd.to_numeric(df[cols["high"]], errors="coerce")
    df["Low"] = pd.to_numeric(df[cols["low"]], errors="coerce")
    df["Close"] = pd.to_numeric(df[cols["close"]], errors="coerce")
    if "volume" in cols:
        df["Volume"] = pd.to_numeric(df[cols["volume"]], errors="coerce").fillna(0)
    else:
        df["Volume"] = 0

    df = df.dropna(subset=["Open", "High", "Low", "Close"])

    start_dt = pd.to_datetime(start_date, errors="coerce")
    end_dt = pd.to_datetime(end_date, errors="coerce")
    if pd.notna(start_dt):
        df = df[df["Date"] >= start_dt]
    if pd.notna(end_dt):
        df = df[df["Date"] <= end_dt]

    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].sort_values("Date").reset_index(drop=True)

