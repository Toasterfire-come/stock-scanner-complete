#!/usr/bin/env python3
"""
Real-Time Stock Scanner with Working Proxy Rotation
===================================================
Uses curl_cffi session pools with per-session proxies
"""

import time
import json
import logging
import random
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict

import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class ScanConfig:
    """Configuration"""
    max_threads: int = 10  # Reduced to avoid overwhelming proxies
    timeout: float = 3.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 2000  # Full production scan
    random_delay_range: tuple = (0.01, 0.05)
    output_json: str = "realtime_scan_2000_results.json"
    session_pool_size: int = 100  # 100 proxies = each used ~20 times for 2K tickers (well under 30 limit)


class SessionPool:
    """Pool of curl_cffi sessions, each with a different proxy"""

    def __init__(self, proxies: List[str], pool_size: int, proxy_offset: int = 0):
        self.lock = threading.Lock()
        self.sessions = []
        self.current_index = 0
        self.request_count = 0
        self.rotation_count = 0

        # Create pool of sessions with different proxies, starting from offset
        available_proxies = proxies[proxy_offset:] if proxy_offset < len(proxies) else proxies
        proxies_to_use = (available_proxies[:pool_size] if len(available_proxies) >= pool_size
                         else available_proxies * (pool_size // len(available_proxies) + 1))[:pool_size]

        logger.info(f"🔧 Creating session pool with {pool_size} sessions...")

        try:
            from curl_cffi import requests as curl_requests

            for i, proxy in enumerate(proxies_to_use):
                session = curl_requests.Session(impersonate="chrome")
                # Set proxy for this session
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

                if i < 5:  # Log first 5
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
        """Get next session using round-robin"""
        with self.lock:
            self.request_count += 1

            # Log first 20 requests
            if self.request_count <= 20:
                logger.info(f"📊 Request #{self.request_count}, using session {self.current_index}")

            # Get current session
            session_info = self.sessions[self.current_index]
            session_info["request_count"] += 1

            # Rotate to next session for next request
            old_index = self.current_index
            self.current_index = (self.current_index + 1) % len(self.sessions)

            # Log rotation
            if self.current_index == 0:  # Completed full rotation
                self.rotation_count += 1
                if self.rotation_count <= 10:
                    logger.info(f"🔄 Completed rotation #{self.rotation_count} through all {len(self.sessions)} sessions")

            # Log every 20 requests
            if self.request_count % 20 == 0:
                logger.info(f"📊 Request #{self.request_count}: session[{old_index}] → session[{self.current_index}]")

            return session_info["session"], session_info["proxy"], session_info["index"]

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        with self.lock:
            return {
                "total_requests": self.request_count,
                "total_sessions": len(self.sessions),
                "completed_rotations": self.rotation_count,
                "requests_per_session": [s["request_count"] for s in self.sessions]
            }


def fetch_ticker(ticker: str, session_pool: SessionPool, config: ScanConfig) -> Optional[Dict[str, Any]]:
    """Fetch ticker data using session from pool"""
    for attempt in range(config.max_retries):
        try:
            if config.random_delay_range:
                time.sleep(random.uniform(*config.random_delay_range))

            # Get session from pool (with proxy already set)
            session, proxy, session_idx = session_pool.get_session()

            # Create Ticker with proxied session
            stock = yf.Ticker(ticker, session=session)
            info = stock.info

            if not info or len(info) < 5:
                return None

            # Extract data
            data = {
                "ticker": ticker,
                "company_name": info.get("longName") or info.get("shortName") or ticker,
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "price_change": info.get("regularMarketChange"),
                "price_change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "timestamp": datetime.now().isoformat(),
                "_session_idx": session_idx  # Track which session was used
            }

            logger.info(f"✓ {ticker}: ${data.get('current_price')} (session {session_idx})")
            return data

        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {str(e)[:100]}")
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay * (2 ** attempt))

    logger.error(f"✗ {ticker}: All attempts failed")
    return None


def scan_tickers(tickers: List[str], session_pool: SessionPool, config: ScanConfig) -> Dict[str, Any]:
    """Scan tickers with session pool proxy rotation"""
    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info("-" * 80)

    start_time = time.time()
    results = []
    failed_tickers = []
    completed = 0

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {executor.submit(fetch_ticker, ticker, session_pool, config): ticker
                  for ticker in tickers}

        for future in as_completed(futures):
            ticker = futures[future]
            completed += 1

            try:
                data = future.result()
                if data:
                    results.append(data)
                else:
                    failed_tickers.append(ticker)
            except Exception as e:
                logger.error(f"Exception for {ticker}: {str(e)[:50]}")
                failed_tickers.append(ticker)

            # Progress every 100 tickers
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                success_rate = (len(results) / completed) * 100
                logger.info(f"Progress: {completed}/{len(tickers)} ({completed/len(tickers)*100:.1f}%) | "
                           f"Success: {success_rate:.1f}% | Rate: {rate:.1f}/sec")

    elapsed = time.time() - start_time
    success_rate = (len(results) / len(tickers)) * 100

    # Get session pool stats
    pool_stats = session_pool.get_stats()

    output = {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": len(tickers),
            "successful": len(results),
            "failed": len(failed_tickers),
            "success_rate_percent": round(success_rate, 2),
            "scan_duration_seconds": round(elapsed, 2),
            "average_rate_per_second": round(len(tickers) / elapsed, 2),
            "session_pool_stats": pool_stats
        },
        "results": results,
        "failed_tickers": failed_tickers[:100]
    }

    return output


def load_proxies() -> List[str]:
    """Load proxies"""
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


def load_tickers(limit: int) -> List[str]:
    """Load tickers"""
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        raise FileNotFoundError("No ticker files found")

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS[:limit]
    logger.info(f"Loaded {len(tickers)} tickers")
    return tickers


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("WORKING PROXY SCANNER - SESSION POOL METHOD")
    logger.info("=" * 80)

    config = ScanConfig()

    # Load proxies
    proxies = load_proxies()
    if not proxies:
        logger.error("No proxies available!")
        return

    # Create session pool (use proxies starting from index 100 to avoid recently-used ones)
    session_pool = SessionPool(proxies, config.session_pool_size, proxy_offset=100)

    # Load tickers
    tickers = load_tickers(config.target_tickers)

    # Run scan
    results = scan_tickers(tickers, session_pool, config)

    # Save results
    output_file = BASE_DIR / config.output_json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Success: {results['scan_info']['successful']}/{results['scan_info']['total_tickers']} "
                f"({results['scan_info']['success_rate_percent']:.2f}%)")
    logger.info(f"Completed rotations: {results['scan_info']['session_pool_stats']['completed_rotations']}")
    logger.info(f"Time: {results['scan_info']['scan_duration_seconds']}s")
    logger.info(f"Saved to: {output_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
