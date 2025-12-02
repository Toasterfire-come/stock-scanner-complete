#!/usr/bin/env python3
"""
Real-Time Scanner - 2K Tickers Standalone (No Django)
======================================================
Scans 2,000 tickers and outputs results to JSON file
No database dependency - pure yfinance + JSON output
"""

import time
import random
import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import threading
from datetime import datetime

# Import yfinance
import yfinance as yf

# Try to import curl_cffi for better TLS fingerprinting
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    import requests
    curl_requests = None
    CURL_CFFI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class ScanConfig:
    """Configuration for 2K ticker scanning"""
    max_threads: int = 200
    timeout: float = 3.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 2000
    min_success_rate: float = 0.95
    use_socks5h: bool = True
    rotate_per_request: bool = True
    random_delay_range: tuple = (0.01, 0.05)
    output_json: str = "realtime_scan_results.json"


class ProxyRotator:
    """Thread-safe proxy rotator"""

    def __init__(self, proxies: List[str], use_socks5h: bool = True):
        self.proxies = proxies
        self.use_socks5h = use_socks5h
        self.current_index = 0
        self.lock = threading.Lock()
        self.failures = {}
        self.successes = {}

        logger.info(f"Initialized ProxyRotator with {len(proxies)} proxies")

    def get_next_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None

        with self.lock:
            available = [p for p in self.proxies if self.failures.get(p, 0) < 5]
            if not available:
                self.failures.clear()
                available = self.proxies

            proxy = available[self.current_index % len(available)]
            self.current_index = (self.current_index + 1) % len(available)
            return proxy

    def mark_success(self, proxy: str):
        with self.lock:
            self.successes[proxy] = self.successes.get(proxy, 0) + 1
            if proxy in self.failures and self.failures[proxy] > 0:
                self.failures[proxy] -= 1

    def mark_failure(self, proxy: str, reason: str = ""):
        with self.lock:
            self.failures[proxy] = self.failures.get(proxy, 0) + 1

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_successes = sum(self.successes.values())
            total_failures = sum(self.failures.values())
            return {
                "total_proxies": len(self.proxies),
                "total_successes": total_successes,
                "total_failures": total_failures,
                "success_rate": total_successes / (total_successes + total_failures) if (total_successes + total_failures) > 0 else 0,
                "healthy_proxies": len([p for p in self.proxies if self.failures.get(p, 0) < 5])
            }


class YFinanceClient:
    """YFinance client with proxy support"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, proxy_rotator: ProxyRotator, config: ScanConfig):
        self.proxy_rotator = proxy_rotator
        self.config = config

    def _create_session(self, proxy: Optional[str]):
        if CURL_CFFI_AVAILABLE and curl_requests:
            session = curl_requests.Session()
            if proxy:
                session.proxies = {"http": proxy, "https": proxy}
        else:
            import requests
            session = requests.Session()
            if proxy:
                if self.config.use_socks5h and proxy.startswith("socks5://"):
                    session.proxies = {
                        "http": proxy.replace("socks5://", "socks5h://"),
                        "https": proxy.replace("socks5://", "socks5h://")
                    }
                else:
                    session.proxies = {"http": proxy, "https": proxy}

        session.headers.update({
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive"
        })

        return session

    def fetch_realtime_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        proxy = self.proxy_rotator.get_next_proxy() if self.config.rotate_per_request else None

        for attempt in range(self.config.max_retries):
            try:
                if self.config.random_delay_range:
                    time.sleep(random.uniform(*self.config.random_delay_range))

                session = self._create_session(proxy)
                stock = yf.Ticker(ticker, session=session)
                info = stock.info

                if not info or len(info) < 5:
                    if proxy:
                        self.proxy_rotator.mark_failure(proxy, "empty_data")
                    return None

                # Extract real-time fields
                data = {
                    "ticker": ticker,
                    "company_name": info.get("longName") or info.get("shortName") or ticker,
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "price_change": info.get("regularMarketChange"),
                    "price_change_percent": info.get("regularMarketChangePercent"),
                    "volume": info.get("volume") or info.get("regularMarketVolume"),
                    "bid_price": info.get("bid"),
                    "ask_price": info.get("ask"),
                    "days_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                    "days_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "52_week_low": info.get("fiftyTwoWeekLow"),
                    "52_week_high": info.get("fiftyTwoWeekHigh"),
                    "average_volume": info.get("averageVolume"),
                    "timestamp": datetime.now().isoformat()
                }

                # Calculate derived fields
                if data["volume"] and data["average_volume"] and data["average_volume"] > 0:
                    data["volume_ratio"] = float(data["volume"]) / float(data["average_volume"])
                else:
                    data["volume_ratio"] = None

                # Convert None to null for JSON
                data = {k: (v if v is not None else None) for k, v in data.items()}

                if proxy:
                    self.proxy_rotator.mark_success(proxy)

                return data

            except Exception as e:
                logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {str(e)[:50]}")
                if proxy:
                    self.proxy_rotator.mark_failure(proxy, str(e)[:30])

                if attempt < self.config.max_retries - 1:
                    proxy = self.proxy_rotator.get_next_proxy()
                    time.sleep(self.config.retry_delay * (2 ** attempt))

        return None


def load_tickers(limit: int = 2000) -> List[str]:
    """Load tickers from combined ticker file"""
    combined_dir = BASE_DIR / "data" / "combined"

    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))
    if not ticker_files:
        logger.error("No combined ticker files found")
        return []

    latest_file = ticker_files[-1]
    logger.info(f"Loading tickers from {latest_file.name}")

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", latest_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    all_tickers = module.COMBINED_TICKERS
    tickers = all_tickers[:limit]
    logger.info(f"Loaded {len(tickers)} tickers")
    return tickers


def load_proxies() -> List[str]:
    """Load proxies from filtered list"""
    proxies = []

    filtered_file = BASE_DIR / "filtered_working_proxies.json"
    if filtered_file.exists():
        with open(filtered_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "proxies" in data:
                proxies.extend(data["proxies"])
            elif isinstance(data, list):
                proxies.extend(data)
        logger.info(f"Loaded {len(proxies)} proxies from filtered_working_proxies.json")
        return list(dict.fromkeys(proxies))

    logger.warning("No filtered proxies found!")
    return []


def run_scan_2k():
    """Main scanning function"""
    logger.info("=" * 80)
    logger.info("REAL-TIME STOCK SCANNER - 2K TICKERS (STANDALONE)")
    logger.info("=" * 80)

    config = ScanConfig()
    logger.info(f"Config: {config.max_threads} threads, {config.timeout}s timeout")

    tickers = load_tickers(limit=config.target_tickers)
    if not tickers:
        logger.error("No tickers to scan")
        return

    proxies = load_proxies()
    if not proxies:
        logger.error("No proxies loaded!")
        return

    proxy_rotator = ProxyRotator(proxies, use_socks5h=config.use_socks5h)
    client = YFinanceClient(proxy_rotator, config)

    stats = {
        "total": len(tickers),
        "success": 0,
        "failed": 0,
        "start_time": time.time()
    }

    results = []

    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info("-" * 80)

    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {executor.submit(client.fetch_realtime_data, ticker): ticker for ticker in tickers}

        for i, future in enumerate(as_completed(futures), 1):
            ticker = futures[future]

            try:
                data = future.result()

                if data:
                    stats["success"] += 1
                    results.append(data)
                else:
                    stats["failed"] += 1

                if i % 100 == 0:
                    elapsed = time.time() - stats["start_time"]
                    rate = i / elapsed
                    eta = (stats["total"] - i) / rate if rate > 0 else 0
                    success_rate = (stats["success"] / i) * 100

                    logger.info(
                        f"Progress: {i}/{stats['total']} ({i/stats['total']*100:.1f}%) | "
                        f"Rate: {rate:.2f}/sec | Success: {success_rate:.1f}% | ETA: {eta:.0f}s"
                    )

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                stats["failed"] += 1

    elapsed = time.time() - stats["start_time"]
    success_rate = (stats["success"] / stats["total"]) * 100

    # Save results to JSON
    output_data = {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": stats["total"],
            "successful": stats["success"],
            "failed": stats["failed"],
            "success_rate_percent": round(success_rate, 2),
            "scan_duration_seconds": round(elapsed, 2),
            "average_rate_per_second": round(stats["total"] / elapsed, 2)
        },
        "proxy_stats": proxy_rotator.get_stats(),
        "results": results
    }

    output_file = BASE_DIR / config.output_json
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total time: {elapsed:.2f}s")
    logger.info(f"Average rate: {stats['total']/elapsed:.2f} tickers/sec")
    logger.info(f"Success: {stats['success']}/{stats['total']} ({success_rate:.2f}%)")
    logger.info(f"Failed: {stats['failed']}")
    logger.info("-" * 80)
    logger.info(f"✓ Results saved to: {output_file}")
    logger.info(f"  Total results: {len(results)}")
    logger.info(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

    proxy_stats = proxy_rotator.get_stats()
    logger.info("-" * 80)
    logger.info("PROXY STATISTICS")
    logger.info(f"Total proxies: {proxy_stats['total_proxies']}")
    logger.info(f"Healthy proxies: {proxy_stats['healthy_proxies']}")
    logger.info(f"Proxy success rate: {proxy_stats['success_rate']*100:.2f}%")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_scan_2k()
