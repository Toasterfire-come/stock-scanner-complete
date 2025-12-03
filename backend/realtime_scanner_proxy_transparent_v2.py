#!/usr/bin/env python3
"""
Real-Time Stock Scanner with TRULY Transparent Proxy Rotation
==============================================================
Patches requests at import time, BEFORE yfinance loads
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

# CRITICAL: Patch requests BEFORE importing yfinance
import requests
from requests.adapters import HTTPAdapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


class ProxyRotator:
    """Global proxy rotator - shared across all requests"""

    def __init__(self, proxies: List[str], rotation_interval: int = 5):
        self.proxies = proxies if proxies else [None]
        self.rotation_interval = rotation_interval
        self.lock = threading.Lock()
        self.current_index = 0
        self.request_count = 0

        logger.info(f"🔧 ProxyRotator initialized with {len(self.proxies)} proxies")
        logger.info(f"🔧 Will rotate every {rotation_interval} requests")

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy with rotation"""
        with self.lock:
            self.request_count += 1

            # Log first 10 requests
            if self.request_count <= 10:
                logger.info(f"📊 Request #{self.request_count}")

            # Rotate every N requests
            if self.request_count % self.rotation_interval == 0:
                old_index = self.current_index
                self.current_index = (self.current_index + 1) % len(self.proxies)
                new_proxy = self.proxies[self.current_index]
                logger.info(f"🔄 ROTATION at request #{self.request_count}: proxy[{old_index}] → proxy[{self.current_index}] = {new_proxy}")
                # Small pause for handoff
                time.sleep(0.1)

            return self.proxies[self.current_index]


# Global proxy rotator instance
_proxy_rotator = None


def init_proxy_rotator(proxies: List[str], rotation_interval: int = 5):
    """Initialize global proxy rotator"""
    global _proxy_rotator
    _proxy_rotator = ProxyRotator(proxies, rotation_interval)


class RotatingProxyAdapter(HTTPAdapter):
    """HTTP adapter that uses global proxy rotator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.send_count = 0

    def send(self, request, **kwargs):
        """Inject proxy from global rotator"""
        self.send_count += 1
        if self.send_count <= 10:
            logger.info(f"🌐 RotatingProxyAdapter.send() call #{self.send_count} for {request.url}")

        if _proxy_rotator:
            proxy = _proxy_rotator.get_next_proxy()
            if proxy:
                kwargs['proxies'] = {
                    'http': proxy,
                    'https': proxy
                }

        return super().send(request, **kwargs)


# Monkey-patch ALL requests.Session instances to use our adapter
_original_session_init = requests.Session.__init__

def _patched_session_init(self, *args, **kwargs):
    _original_session_init(self, *args, **kwargs)
    # Mount our rotating proxy adapter
    adapter = RotatingProxyAdapter(max_retries=3)
    self.mount('http://', adapter)
    self.mount('https://', adapter)

requests.Session.__init__ = _patched_session_init
logger.info("✅ Patched requests.Session globally")

# NOW import yfinance (after patching)
import yfinance as yf


@dataclass
class ScanConfig:
    """Configuration"""
    max_threads: int = 50
    timeout: float = 3.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 50
    random_delay_range: tuple = (0.01, 0.05)
    output_json: str = "realtime_scan_proxy_v2_results.json"
    proxy_rotation_interval: int = 5


def fetch_ticker(ticker: str, config: ScanConfig) -> Optional[Dict[str, Any]]:
    """Fetch ticker data - proxy rotation happens automatically"""
    for attempt in range(config.max_retries):
        try:
            if config.random_delay_range:
                time.sleep(random.uniform(*config.random_delay_range))

            # Use yfinance normally - proxies work transparently
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
    """Scan tickers with transparent proxy rotation"""
    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info("-" * 80)

    start_time = time.time()
    results = []
    failed_tickers = []

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {executor.submit(fetch_ticker, ticker, config): ticker for ticker in tickers}

        for future in as_completed(futures):
            ticker = futures[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
                else:
                    failed_tickers.append(ticker)
            except Exception as e:
                logger.error(f"Exception for {ticker}: {str(e)[:50]}")
                failed_tickers.append(ticker)

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
            "average_rate_per_second": round(len(tickers) / elapsed, 2)
        },
        "results": results,
        "failed_tickers": failed_tickers
    }

    return output


def load_proxies() -> List[str]:
    """Load proxies from filtered list"""
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
    logger.info("TRANSPARENT PROXY SCANNER V2 - EARLY PATCHING")
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
    logger.info(f"Time: {results['scan_info']['scan_duration_seconds']}s")
    logger.info(f"Saved to: {output_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
