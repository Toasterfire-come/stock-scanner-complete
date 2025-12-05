#!/usr/bin/env python3
"""
Historical Data Scanner for Backtesting
========================================
Fetches maximum historical data across multiple timeframes for all tickers
Timeframes: 1min, 5min, 15min, 30min, 1hr, 4hr, 1day

Features:
- 200 proxies for better load distribution
- 20 threads for optimal stability
- Smart retry logic (avoids same proxy on auth failures)
- Multiple timeframe support
- Maximum historical period per timeframe
- Data stored in organized format for backtesting
"""

import os
import sys
import time
import json
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from collections import defaultdict

import yfinance as yf
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class HistoricalConfig:
    """Configuration for historical data scanning"""
    max_threads: int = 20  # Optimal for curl_cffi stability
    timeout: float = 10.0  # Longer timeout for large historical requests
    max_retries: int = 3  # More retries for historical data
    retry_delay: float = 0.2
    session_pool_size: int = 200  # 200 proxies for better load distribution
    output_dir: str = "historical_data"  # Directory to store historical data

    # Timeframe configurations (interval: max_period)
    # yfinance limits: 1m=7d, 5m=60d, 15m=60d, 30m=60d, 1h=730d, 4h/1d=unlimited
    timeframes: Dict[str, str] = None

    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = {
                "1m": "7d",      # 1-minute: max 7 days
                "5m": "60d",     # 5-minute: max 60 days
                "15m": "60d",    # 15-minute: max 60 days
                "30m": "60d",    # 30-minute: max 60 days
                "1h": "730d",    # 1-hour: max 730 days (2 years)
                "4h": "max",     # 4-hour: maximum available
                "1d": "max",     # 1-day: maximum available
            }


class SessionPool:
    """Pool of curl_cffi sessions, each with a different proxy"""

    def __init__(self, proxies: List[str], pool_size: int):
        self.lock = threading.Lock()
        self.sessions = []
        self.current_index = 0
        self.request_count = 0
        self.failed_sessions = set()
        self.session_failures = defaultdict(int)

        # Limit proxies to pool_size
        proxies_to_use = proxies[:pool_size] if len(proxies) > pool_size else proxies

        logger.info(f"🔧 Creating session pool with {len(proxies_to_use)} sessions...")

        try:
            from curl_cffi import requests as curl_requests

            for i, proxy in enumerate(proxies_to_use):
                session = curl_requests.Session(impersonate="chrome")
                session.proxies = {"http": proxy, "https": proxy}
                self.sessions.append({
                    "session": session,
                    "proxy": proxy,
                    "index": i,
                    "request_count": 0
                })

            logger.info(f"✅ Created {len(self.sessions)} sessions with proxies")

        except ImportError:
            logger.warning("curl_cffi not available, falling back to standard requests")
            import requests as std_requests
            for i, proxy in enumerate(proxies_to_use):
                session = std_requests.Session()
                session.proxies = {"http": proxy, "https": proxy}
                self.sessions.append({
                    "session": session,
                    "proxy": proxy,
                    "index": i,
                    "request_count": 0
                })

    def get_session(self, exclude_index: int = None):
        """Get next session using round-robin rotation"""
        with self.lock:
            self.request_count += 1

            # Skip failed sessions
            attempts = 0
            while attempts < len(self.sessions):
                if self.current_index not in self.failed_sessions and self.current_index != exclude_index:
                    break
                self.current_index = (self.current_index + 1) % len(self.sessions)
                attempts += 1

            if attempts >= len(self.sessions):
                logger.warning("All sessions failed, resetting")
                self.failed_sessions.clear()
                self.current_index = 0

            session_info = self.sessions[self.current_index]
            session_info["request_count"] += 1

            old_index = self.current_index
            self.current_index = (self.current_index + 1) % len(self.sessions)

            # Skip failed sessions in rotation
            while self.current_index in self.failed_sessions and len(self.failed_sessions) < len(self.sessions):
                self.current_index = (self.current_index + 1) % len(self.sessions)

            if self.request_count % 100 == 0:
                healthy = len(self.sessions) - len(self.failed_sessions)
                logger.info(f"📊 Request #{self.request_count} | Healthy: {healthy}/{len(self.sessions)}")

            return session_info["session"], session_info["proxy"], session_info["index"]

    def mark_session_failed(self, session_index: int, reason: str = ""):
        """Mark session as failed"""
        with self.lock:
            self.session_failures[session_index] += 1
            if "401" in reason or "Unauthorized" in reason or self.session_failures[session_index] >= 3:
                self.failed_sessions.add(session_index)
                logger.warning(f"🚫 Session {session_index} failed: {reason[:50]}")

    def get_stats(self):
        """Get session pool statistics"""
        with self.lock:
            return {
                "total_requests": self.request_count,
                "total_sessions": len(self.sessions),
                "failed_sessions": len(self.failed_sessions),
                "healthy_sessions": len(self.sessions) - len(self.failed_sessions),
            }


def load_proxies() -> List[str]:
    """Load working proxies"""
    proxy_file = BASE_DIR / "working_proxies.json"
    if proxy_file.exists():
        with open(proxy_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "proxies" in data:
                proxies = data["proxies"]
            elif isinstance(data, list):
                proxies = data
            else:
                proxies = []

        logger.info(f"Loaded {len(proxies)} proxies")
        return list(dict.fromkeys(proxies))

    logger.warning("No proxies found")
    return []


def fetch_historical_data(
    ticker: str,
    interval: str,
    period: str,
    session_pool: SessionPool,
    config: HistoricalConfig
) -> Optional[pd.DataFrame]:
    """Fetch historical data for a single ticker and timeframe"""
    session, proxy, session_idx = session_pool.get_session()
    failed_session_idx = None

    for attempt in range(config.max_retries):
        try:
            stock = yf.Ticker(ticker, session=session)

            # Fetch historical data
            hist = stock.history(period=period, interval=interval)

            if hist.empty:
                logger.debug(f"No data for {ticker} ({interval})")
                return None

            # Add ticker column
            hist['ticker'] = ticker

            logger.info(f"✓ {ticker} ({interval}): {len(hist)} bars | Period: {period}")
            return hist

        except Exception as e:
            error_msg = str(e)
            is_auth_failure = "401" in error_msg or "Unauthorized" in error_msg

            if is_auth_failure:
                session_pool.mark_session_failed(session_idx, error_msg[:100])
                failed_session_idx = session_idx
                logger.debug(f"Auth failure for {ticker} on session {session_idx}")

                if attempt < config.max_retries - 1:
                    session, proxy, session_idx = session_pool.get_session(exclude_index=failed_session_idx)
            else:
                logger.debug(f"Attempt {attempt + 1} failed for {ticker} ({interval}): {error_msg[:100]}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay * (attempt + 1))

    logger.warning(f"❌ Failed all retries for {ticker} ({interval})")
    return None


def process_ticker_all_timeframes(
    ticker: str,
    session_pool: SessionPool,
    config: HistoricalConfig
) -> Dict[str, Optional[pd.DataFrame]]:
    """Fetch historical data for all timeframes for a single ticker"""
    results = {}

    for interval, period in config.timeframes.items():
        df = fetch_historical_data(ticker, interval, period, session_pool, config)
        results[interval] = df

        # Small delay between timeframe requests for same ticker
        time.sleep(0.1)

    return results


def save_historical_data(ticker: str, timeframe_data: Dict[str, pd.DataFrame], config: HistoricalConfig):
    """Save historical data to organized directory structure"""
    output_base = BASE_DIR / config.output_dir
    output_base.mkdir(exist_ok=True)

    for interval, df in timeframe_data.items():
        if df is not None and not df.empty:
            # Create timeframe directory
            interval_dir = output_base / interval
            interval_dir.mkdir(exist_ok=True)

            # Save as CSV (more portable for backtesting)
            filename = interval_dir / f"{ticker.replace('/', '_').replace('^', 'IDX_')}.csv"
            df.to_csv(filename)

            # Also save as parquet (more efficient)
            parquet_filename = interval_dir / f"{ticker.replace('/', '_').replace('^', 'IDX_')}.parquet"
            df.to_parquet(parquet_filename)


def scan_historical_data(tickers: List[str], session_pool: SessionPool, config: HistoricalConfig):
    """Scan all tickers for historical data across all timeframes"""
    total_tickers = len(tickers)
    completed = 0
    successful = 0
    failed = 0
    start_time = time.time()

    logger.info(f"Starting historical data scan for {total_tickers} tickers...")
    logger.info(f"Timeframes: {', '.join(config.timeframes.keys())}")
    logger.info("-" * 80)

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {
            executor.submit(process_ticker_all_timeframes, ticker, session_pool, config): ticker
            for ticker in tickers
        }

        for future in as_completed(futures):
            ticker = futures[future]
            completed += 1

            try:
                timeframe_data = future.result()

                # Check if we got any data
                has_data = any(df is not None and not df.empty for df in timeframe_data.values())

                if has_data:
                    successful += 1
                    # Save the data
                    save_historical_data(ticker, timeframe_data, config)
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)[:100]}")
                failed += 1

            # Progress update
            if completed % 50 == 0 or completed == total_tickers:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                success_rate = (successful / completed * 100) if completed > 0 else 0
                eta_seconds = (total_tickers - completed) / rate if rate > 0 else 0

                logger.info(
                    f"Progress: {completed}/{total_tickers} ({completed/total_tickers*100:.1f}%) | "
                    f"Success: {success_rate:.1f}% | Rate: {rate:.2f}/sec | ETA: {eta_seconds/60:.1f} min"
                )

    duration = time.time() - start_time

    # Final summary
    logger.info("=" * 80)
    logger.info("HISTORICAL DATA SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total tickers: {total_tickers}")
    logger.info(f"Successful: {successful} ({successful/total_tickers*100:.1f}%)")
    logger.info(f"Failed: {failed} ({failed/total_tickers*100:.1f}%)")
    logger.info(f"Duration: {duration/60:.1f} minutes ({duration:.1f} seconds)")
    logger.info(f"Average rate: {total_tickers/duration:.2f} tickers/sec")
    logger.info(f"Data saved to: {BASE_DIR / config.output_dir}")

    # Session stats
    pool_stats = session_pool.get_stats()
    logger.info("-" * 80)
    logger.info(f"Session pool stats:")
    logger.info(f"  Total requests: {pool_stats['total_requests']}")
    logger.info(f"  Healthy sessions: {pool_stats['healthy_sessions']}/{pool_stats['total_sessions']}")
    logger.info("=" * 80)


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("HISTORICAL DATA SCANNER FOR BACKTESTING")
    logger.info("=" * 80)

    # Load configuration
    config = HistoricalConfig()

    # Load proxies
    proxies = load_proxies()
    if not proxies:
        logger.error("No proxies available! Running without proxies may be very slow.")
        # Create a dummy session pool without proxies
        proxies = [None]

    # Create session pool
    session_pool = SessionPool(proxies, config.session_pool_size)

    # Load tickers
    from historical_tickers_list import get_all_historical_tickers
    tickers = get_all_historical_tickers()

    logger.info(f"Total tickers to process: {len(tickers)}")
    logger.info(f"Timeframes: {list(config.timeframes.keys())}")
    logger.info(f"Max threads: {config.max_threads}")
    logger.info(f"Session pool size: {config.session_pool_size}")
    logger.info("-" * 80)

    # Scan historical data
    scan_historical_data(tickers, session_pool, config)


if __name__ == "__main__":
    main()
