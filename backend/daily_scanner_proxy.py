#!/usr/bin/env python3
"""
Daily Stock Scanner with Working Proxy Rotation
================================================
Collects end-of-day historical data using proven SessionPool approach
Runs from 12:00 AM to market open (9:30 AM ET) on weekdays
"""

import time
import json
import logging
import random
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict
import pytz

import yfinance as yf
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class ScanConfig:
    """Configuration for daily scanner"""
    max_threads: int = 15  # Increased for better performance
    timeout: float = 5.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 5000  # Scan all tickers (will load from combined list)
    random_delay_range: tuple = (0.005, 0.02)  # Reduced delay for faster scanning
    output_json: str = "daily_scan_results.json"
    session_pool_size: int = 100  # 100 proxies = each used ~50 times (still under limit)
    history_period: str = "5d"  # Last 5 days for trend analysis
    # Market timing (Eastern Time)
    daily_start_hour: int = 0  # 12:00 AM ET
    daily_end_hour: int = 9  # 9:00 AM ET (before market open at 9:30 AM)
    daily_end_minute: int = 30  # Market opens at 9:30 AM


class SessionPool:
    """Pool of curl_cffi sessions, each with a different proxy"""

    def __init__(self, proxies: List[str], pool_size: int, proxy_offset: int = 0):
        self.lock = threading.Lock()
        self.sessions = []
        self.current_index = 0
        self.request_count = 0
        self.rotation_count = 0

        # Create pool of sessions with different proxies
        available_proxies = proxies[proxy_offset:] if proxy_offset < len(proxies) else proxies
        proxies_to_use = (available_proxies[:pool_size] if len(available_proxies) >= pool_size
                         else available_proxies * (pool_size // len(available_proxies) + 1))[:pool_size]

        logger.info(f"🔧 Creating session pool with {pool_size} sessions...")

        try:
            from curl_cffi import requests as curl_requests

            for i, proxy in enumerate(proxies_to_use):
                session = curl_requests.Session(impersonate="chrome")
                session.proxies = {
                    "http": proxy,
                    "https": proxy
                }
                self.sessions.append({
                    "session": session,
                    "proxy": proxy,
                    "index": i,
                    "request_count": 0
                })

                if i < 5:
                    logger.info(f"   Session {i}: {proxy}")

            logger.info(f"✅ Created {len(self.sessions)} sessions with proxies")

        except ImportError:
            logger.error("curl_cffi not available, falling back to standard requests")
            import requests as std_requests
            for i, proxy in enumerate(proxies_to_use):
                session = std_requests.Session()
                session.proxies = {
                    "http": proxy,
                    "https": proxy
                }
                self.sessions.append({
                    "session": session,
                    "proxy": proxy,
                    "index": i,
                    "request_count": 0
                })

    def get_session(self):
        """Get next session using round-robin rotation"""
        with self.lock:
            self.request_count += 1

            session_info = self.sessions[self.current_index]
            session_info["request_count"] += 1

            old_index = self.current_index
            old_proxy = self.sessions[old_index]["proxy"]
            self.current_index = (self.current_index + 1) % len(self.sessions)
            new_proxy = self.sessions[self.current_index]["proxy"]

            if self.current_index == 0:
                self.rotation_count += 1
                logger.info(f"🔄 Completed rotation #{self.rotation_count} through all {len(self.sessions)} sessions")

            # Log every 50 requests with proxy details
            if self.request_count % 50 == 0:
                logger.info(f"📊 Request #{self.request_count}: session[{old_index}] ({old_proxy}) → session[{self.current_index}] ({new_proxy})")

            # Log at key milestones with full stats
            if self.request_count in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
                logger.warning(f"🎯 MILESTONE {self.request_count}: Using session {old_index} with proxy {old_proxy}")

            return session_info["session"], session_info["proxy"], session_info["index"]

    def get_stats(self):
        """Get session pool statistics"""
        with self.lock:
            return {
                "total_requests": self.request_count,
                "total_sessions": len(self.sessions),
                "completed_rotations": self.rotation_count,
                "requests_per_session": [s["request_count"] for s in self.sessions]
            }


def load_proxies() -> List[str]:
    """Load working proxies from filtered list"""
    filtered_file = BASE_DIR / "filtered_working_proxies.json"
    if filtered_file.exists():
        with open(filtered_file, 'r') as f:
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


def load_tickers(limit: int = None) -> List[str]:
    """Load tickers from combined list"""
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        raise FileNotFoundError("No ticker files found")

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS if limit is None else module.COMBINED_TICKERS[:limit]
    logger.info(f"Loaded {len(tickers)} tickers (limit: {limit or 'none'})")
    return tickers


def calculate_daily_metrics(hist_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate daily metrics from historical data"""
    if hist_df.empty or len(hist_df) < 2:
        return {}

    try:
        latest = hist_df.iloc[-1]
        previous = hist_df.iloc[-2] if len(hist_df) >= 2 else latest

        # Basic OHLCV
        metrics = {
            "date": latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
            "open": round(float(latest['Open']), 2),
            "high": round(float(latest['High']), 2),
            "low": round(float(latest['Low']), 2),
            "close": round(float(latest['Close']), 2),
            "volume": int(latest['Volume']),
            "daily_change": round(float(latest['Close'] - previous['Close']), 2),
            "daily_change_percent": round(float((latest['Close'] - previous['Close']) / previous['Close'] * 100), 2),
        }

        # Average volume (5-day)
        if len(hist_df) >= 5:
            metrics["avg_volume_5d"] = int(hist_df['Volume'].tail(5).mean())
            metrics["volume_ratio"] = round(float(latest['Volume'] / metrics["avg_volume_5d"]), 2)

        # Price range
        metrics["day_range"] = round(float(latest['High'] - latest['Low']), 2)
        metrics["day_range_percent"] = round(float((latest['High'] - latest['Low']) / latest['Low'] * 100), 2)

        # 5-day high/low
        if len(hist_df) >= 5:
            metrics["high_5d"] = round(float(hist_df['High'].tail(5).max()), 2)
            metrics["low_5d"] = round(float(hist_df['Low'].tail(5).min()), 2)

        return metrics

    except Exception as e:
        logger.debug(f"Error calculating metrics: {e}")
        return {}


def fetch_daily_data(ticker: str, session_pool: SessionPool, config: ScanConfig) -> Optional[Dict[str, Any]]:
    """Fetch daily historical data for a ticker"""
    session, proxy, session_idx = session_pool.get_session()
    request_num = session_pool.request_count  # Capture current request number

    for attempt in range(config.max_retries):
        try:
            stock = yf.Ticker(ticker, session=session)

            # Fetch historical data
            hist = stock.history(period=config.history_period)

            if hist.empty:
                logger.debug(f"No data for {ticker}")
                return None

            # Get company info (with fallback)
            try:
                info = stock.info
                company_name = info.get('longName') or info.get('shortName') or ticker
                sector = info.get('sector', 'Unknown')
                industry = info.get('industry', 'Unknown')
                market_cap = info.get('marketCap')
            except:
                company_name = ticker
                sector = 'Unknown'
                industry = 'Unknown'
                market_cap = None

            # Calculate daily metrics
            daily_metrics = calculate_daily_metrics(hist)

            if not daily_metrics:
                return None

            result = {
                "ticker": ticker,
                "company_name": company_name,
                "sector": sector,
                "industry": industry,
                "market_cap": market_cap,
                **daily_metrics,
                "timestamp": datetime.now().isoformat(),
                "_session_idx": session_idx,
                "_request_num": request_num
            }

            logger.info(f"✓ {ticker}: ${daily_metrics.get('close', 'N/A')} "
                       f"({daily_metrics.get('daily_change_percent', 0):+.2f}%) (session {session_idx})")

            return result

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                logger.error(f"❌ [Request #{request_num}] HTTP 401 for {ticker} on session {session_idx} ({proxy}): {error_msg[:100]}")
            else:
                logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {error_msg[:100]}")

            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay * (attempt + 1))
            continue

    logger.warning(f"❌ [Request #{request_num}] Failed all retries for {ticker} on session {session_idx}")
    return None


def scan_tickers(tickers: List[str], session_pool: SessionPool, config: ScanConfig) -> Dict[str, Any]:
    """Scan tickers with daily data collection"""
    results = []
    failed_tickers = []
    start_time = time.time()

    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info("-" * 80)

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {
            executor.submit(fetch_daily_data, ticker, session_pool, config): ticker
            for ticker in tickers
        }

        completed = 0
        for future in as_completed(futures):
            ticker = futures[future]
            completed += 1

            try:
                result = future.result()
                if result:
                    results.append(result)
                else:
                    failed_tickers.append(ticker)
            except Exception as e:
                logger.error(f"✗ {ticker}: {str(e)[:100]}")
                failed_tickers.append(ticker)

            # Progress update
            if completed % 100 == 0 or completed == len(tickers):
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                success_rate = len(results) / completed * 100 if completed > 0 else 0
                logger.info(f"Progress: {completed}/{len(tickers)} ({completed/len(tickers)*100:.1f}%) | "
                          f"Success: {success_rate:.1f}% | Rate: {rate:.1f}/sec")

            # Random delay
            if config.random_delay_range:
                time.sleep(random.uniform(*config.random_delay_range))

    duration = time.time() - start_time
    success_count = len(results)
    fail_count = len(failed_tickers)
    total = success_count + fail_count
    success_rate = (success_count / total * 100) if total > 0 else 0

    # Get session stats
    pool_stats = session_pool.get_stats()

    scan_info = {
        "timestamp": datetime.now().isoformat(),
        "total_tickers": total,
        "successful": success_count,
        "failed": fail_count,
        "success_rate_percent": round(success_rate, 2),
        "scan_duration_seconds": round(duration, 2),
        "average_rate_per_second": round(total / duration, 2) if duration > 0 else 0,
        "session_pool_stats": pool_stats
    }

    return {
        "scan_info": scan_info,
        "results": sorted(results, key=lambda x: x.get('ticker', '')),
        "failed_tickers": failed_tickers[:100]
    }


def is_daily_scan_allowed(config: ScanConfig) -> bool:
    """Check if daily scan is allowed based on time window (12 AM - 9:30 AM ET)"""
    eastern_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(eastern_tz)

    # Check if it's a weekday (Monday=0, Sunday=6)
    if now_et.weekday() >= 5:
        logger.warning(f"Daily scan not allowed on weekends. Today is {now_et.strftime('%A')}")
        return False

    current_hour = now_et.hour
    current_minute = now_et.minute

    # Check if we're in the allowed window: 12:00 AM (00:00) to 9:30 AM (09:30)
    if current_hour < config.daily_start_hour:
        logger.warning(f"Daily scan not allowed yet. Current time: {now_et.strftime('%H:%M')} ET")
        return False

    if current_hour > config.daily_end_hour or (current_hour == config.daily_end_hour and current_minute >= config.daily_end_minute):
        logger.warning(f"Daily scan window closed. Current time: {now_et.strftime('%H:%M')} ET (window: 00:00-09:30 ET)")
        return False

    logger.info(f"Daily scan allowed. Current time: {now_et.strftime('%H:%M')} ET (window: 00:00-09:30 ET)")
    return True


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("DAILY STOCK SCANNER - WITH PROXY ROTATION")
    logger.info("=" * 80)

    config = ScanConfig()

    # Check if we're in the allowed time window
    if not is_daily_scan_allowed(config):
        logger.error("Daily scan can only run from 12:00 AM to 9:30 AM ET on weekdays")
        logger.info("Exiting...")
        return

    # Load proxies
    proxies = load_proxies()
    if not proxies:
        logger.error("No proxies available!")
        return

    # Create session pool (offset 100 to use different proxies than real-time scanner)
    session_pool = SessionPool(proxies, config.session_pool_size, proxy_offset=100)

    # Load tickers (None = all tickers if target >= 5000)
    ticker_limit = None if config.target_tickers >= 5000 else config.target_tickers
    tickers = load_tickers(ticker_limit)
    if not tickers:
        logger.error("No tickers loaded!")
        return

    # Scan
    results = scan_tickers(tickers, session_pool, config)

    # Save results
    output_path = BASE_DIR / config.output_json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Success: {results['scan_info']['successful']}/{results['scan_info']['total_tickers']} "
                f"({results['scan_info']['success_rate_percent']:.2f}%)")
    logger.info(f"Completed rotations: {results['scan_info']['session_pool_stats']['completed_rotations']}")
    logger.info(f"Time: {results['scan_info']['scan_duration_seconds']}s")
    logger.info(f"Saved to: {output_path}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
