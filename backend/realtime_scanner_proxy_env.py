#!/usr/bin/env python3
"""
Real-Time Stock Scanner with Environment Variable Proxy Rotation
=================================================================
Uses OS-level HTTP_PROXY/HTTPS_PROXY - works with ALL HTTP libraries
"""

import os
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


class ProxyRotator:
    """Thread-safe proxy rotator using environment variables"""

    def __init__(self, proxies: List[str], rotation_interval: int = 5):
        self.proxies = proxies if proxies else []
        self.rotation_interval = rotation_interval
        self.lock = threading.Lock()
        self.current_index = 0
        self.request_count = 0

        if self.proxies:
            # Set initial proxy
            self.set_proxy(self.proxies[0])
            logger.info(f"🔧 Initialized with {len(self.proxies)} proxies, rotating every {rotation_interval} requests")
            logger.info(f"🔧 Starting with proxy: {self.proxies[0]}")
        else:
            logger.warning("No proxies available, using direct connection")

    def set_proxy(self, proxy: str):
        """Set proxy via environment variables"""
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy

    def clear_proxy(self):
        """Remove proxy environment variables"""
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            os.environ.pop(var, None)

    def maybe_rotate(self):
        """Check if we should rotate, and do it"""
        with self.lock:
            self.request_count += 1

            # Log early requests
            if self.request_count <= 10:
                logger.info(f"📊 Request #{self.request_count}, proxy index: {self.current_index}")

            # Rotate every N requests
            if self.proxies and self.request_count % self.rotation_interval == 0:
                old_index = self.current_index
                self.current_index = (self.current_index + 1) % len(self.proxies)
                new_proxy = self.proxies[self.current_index]

                logger.info(f"🔄 ROTATION at request #{self.request_count}: proxy[{old_index}] → proxy[{self.current_index}]")
                logger.info(f"   New proxy: {new_proxy}")

                # Set new proxy
                self.set_proxy(new_proxy)

                # Small pause for handoff
                time.sleep(0.15)


# Global proxy rotator
_proxy_rotator = None


def init_proxy_rotator(proxies: List[str], rotation_interval: int = 5):
    """Initialize global proxy rotator"""
    global _proxy_rotator
    _proxy_rotator = ProxyRotator(proxies, rotation_interval)


# Import yfinance AFTER setting up environment
import yfinance as yf


@dataclass
class ScanConfig:
    """Configuration"""
    max_threads: int = 50
    timeout: float = 3.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 100
    random_delay_range: tuple = (0.01, 0.05)
    output_json: str = "realtime_scan_proxy_env_results.json"
    proxy_rotation_interval: int = 5


def fetch_ticker(ticker: str, config: ScanConfig) -> Optional[Dict[str, Any]]:
    """Fetch ticker data - proxy rotation via environment variables"""

    # Trigger proxy rotation check
    if _proxy_rotator:
        _proxy_rotator.maybe_rotate()

    for attempt in range(config.max_retries):
        try:
            if config.random_delay_range:
                time.sleep(random.uniform(*config.random_delay_range))

            # yfinance will use HTTP_PROXY/HTTPS_PROXY automatically
            stock = yf.Ticker(ticker)
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
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✓ {ticker}: ${data.get('current_price')}")
            return data

        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {str(e)[:100]}")
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay * (2 ** attempt))

    logger.error(f"✗ {ticker}: All attempts failed")
    return None


def scan_tickers(tickers: List[str], config: ScanConfig) -> Dict[str, Any]:
    """Scan tickers with proxy rotation"""
    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info("-" * 80)

    start_time = time.time()
    results = []
    failed_tickers = []
    completed = 0

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {executor.submit(fetch_ticker, ticker, config): ticker for ticker in tickers}

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

    output = {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": len(tickers),
            "successful": len(results),
            "failed": len(failed_tickers),
            "success_rate_percent": round(success_rate, 2),
            "scan_duration_seconds": round(elapsed, 2),
            "average_rate_per_second": round(len(tickers) / elapsed, 2),
            "total_proxy_rotations": _proxy_rotator.request_count // _proxy_rotator.rotation_interval if _proxy_rotator else 0
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
    logger.info("PROXY SCANNER - ENVIRONMENT VARIABLE METHOD")
    logger.info("=" * 80)

    config = ScanConfig()

    # Load and initialize proxy rotator
    proxies = load_proxies()
    init_proxy_rotator(proxies, config.proxy_rotation_interval)

    # Load tickers
    tickers = load_tickers(config.target_tickers)

    # Run scan
    results = scan_tickers(tickers, config)

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
    logger.info(f"Rotations: {results['scan_info']['total_proxy_rotations']}")
    logger.info(f"Time: {results['scan_info']['scan_duration_seconds']}s")
    logger.info(f"Saved to: {output_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
