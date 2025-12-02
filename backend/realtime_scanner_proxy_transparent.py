#!/usr/bin/env python3
"""
Real-Time Stock Scanner with Transparent Proxy Rotation
========================================================
Proxies are injected at the HTTP adapter level, invisible to yfinance
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
import requests
from requests.adapters import HTTPAdapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class ScanConfig:
    """Configuration for scanning with transparent proxy rotation"""
    max_threads: int = 50
    timeout: float = 3.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_tickers: int = 2000
    min_success_rate: float = 0.95
    random_delay_range: tuple = (0.01, 0.05)
    output_json: str = "realtime_scan_proxy_results.json"
    proxy_rotation_interval: int = 5  # Optimal: rotate every 5 requests for best success rate


class TransparentProxyAdapter(HTTPAdapter):
    """HTTP adapter that transparently injects proxy into requests"""

    def __init__(self, proxy_manager, *args, **kwargs):
        self.proxy_manager = proxy_manager
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        """Override send to inject proxy transparently"""
        # Get proxy from manager
        proxy = self.proxy_manager.get_proxy()

        if proxy:
            # Set proxy for this request
            kwargs['proxies'] = {
                'http': proxy,
                'https': proxy
            }

        # Use random user agent
        if 'User-Agent' not in request.headers:
            request.headers['User-Agent'] = self.proxy_manager.get_user_agent()

        try:
            return super().send(request, **kwargs)
        except Exception as e:
            # Mark proxy as failed and retry
            if proxy:
                self.proxy_manager.mark_failure(proxy)
            raise


class ProxyManager:
    """Thread-safe proxy manager with transparent rotation"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    ]

    def __init__(self, proxies: List[str], rotation_interval: int = 20):
        self.proxies = proxies if proxies else [None]  # None = direct connection
        self.rotation_interval = rotation_interval
        self.lock = threading.Lock()
        self.current_index = 0
        self.request_count = 0
        self.failures = defaultdict(int)
        self.success_count = defaultdict(int)

        logger.info(f"Initialized ProxyManager with {len(self.proxies)} proxies")
        logger.info(f"Proxy rotation: every {rotation_interval} requests")

    def get_proxy(self) -> Optional[str]:
        """Get current proxy (rotates every N requests)"""
        with self.lock:
            self.request_count += 1

            # Rotate proxy every N requests
            if self.request_count % self.rotation_interval == 0:
                self.current_index = (self.current_index + 1) % len(self.proxies)
                current = self.proxies[self.current_index]
                if current:
                    logger.debug(f"Rotating to proxy: {current}")

            return self.proxies[self.current_index]

    def get_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.USER_AGENTS)

    def mark_failure(self, proxy: str):
        """Mark proxy as failed"""
        if proxy:
            with self.lock:
                self.failures[proxy] += 1

    def mark_success(self, proxy: str):
        """Mark proxy as successful"""
        if proxy:
            with self.lock:
                self.success_count[proxy] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        with self.lock:
            return {
                "total_requests": self.request_count,
                "total_proxies": len(self.proxies),
                "current_proxy": self.proxies[self.current_index],
                "failures": dict(self.failures),
                "successes": dict(self.success_count)
            }


class TransparentProxyScanner:
    """Scanner with transparent proxy injection"""

    def __init__(self, config: ScanConfig, proxy_manager: ProxyManager):
        self.config = config
        self.proxy_manager = proxy_manager

        # Monkey-patch requests Session to use our adapter
        self._patch_requests()

    def _patch_requests(self):
        """Patch requests library to use transparent proxy adapter"""
        original_init = requests.Session.__init__
        proxy_manager = self.proxy_manager

        def patched_init(session_self, *args, **kwargs):
            original_init(session_self, *args, **kwargs)
            # Mount our transparent proxy adapter
            adapter = TransparentProxyAdapter(proxy_manager, max_retries=3)
            session_self.mount('http://', adapter)
            session_self.mount('https://', adapter)

        requests.Session.__init__ = patched_init
        logger.info("Patched requests.Session to use transparent proxy adapter")

    def fetch_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch ticker data - yfinance won't know about proxy"""
        for attempt in range(self.config.max_retries):
            try:
                if self.config.random_delay_range:
                    time.sleep(random.uniform(*self.config.random_delay_range))

                # Use yfinance normally - proxy is transparent!
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

                # Calculate volume ratio
                if data.get("volume") and data.get("average_volume"):
                    data["volume_ratio"] = float(data["volume"]) / float(data["average_volume"])
                else:
                    data["volume_ratio"] = None

                logger.info(f"✓ {ticker}: ${data.get('current_price')}")
                return data

            except Exception as e:
                logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {str(e)[:100]}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))

        logger.error(f"✗ {ticker}: All attempts failed")
        return None

    def scan(self, tickers: List[str]) -> Dict[str, Any]:
        """Scan tickers with transparent proxy rotation"""
        logger.info(f"Starting scan of {len(tickers)} tickers...")
        logger.info("-" * 80)

        start_time = time.time()
        results = []
        failed_tickers = []

        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = {executor.submit(self.fetch_ticker, ticker): ticker for ticker in tickers}

            completed = 0
            for future in as_completed(futures):
                completed += 1
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

                # Progress update every 100 tickers
                if completed % 100 == 0:
                    success_rate = (len(results) / completed) * 100
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (len(tickers) - completed) / rate if rate > 0 else 0
                    logger.info(
                        f"Progress: {completed}/{len(tickers)} ({completed/len(tickers)*100:.1f}%) | "
                        f"Rate: {rate:.2f}/sec | Success: {success_rate:.1f}% | ETA: {int(eta)}s"
                    )

        elapsed = time.time() - start_time
        success_rate = (len(results) / len(tickers)) * 100

        # Build output
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
            "proxy_stats": self.proxy_manager.get_stats(),
            "results": results,
            "failed_tickers": failed_tickers[:100]  # Limit to first 100 failures
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

        logger.info(f"Loaded {len(proxies)} proxies from {filtered_file}")
        return list(dict.fromkeys(proxies))  # Remove duplicates

    logger.warning("No proxies found, using direct connection")
    return []


def load_tickers(limit: int = 2000) -> List[str]:
    """Load tickers from combined ticker file"""
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        raise FileNotFoundError("No ticker files found")

    # Import the most recent ticker file
    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS[:limit]
    logger.info(f"Loaded {len(tickers)} tickers from {ticker_files[-1].name}")
    return tickers


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("REAL-TIME STOCK SCANNER - TRANSPARENT PROXY ROTATION")
    logger.info("=" * 80)

    config = ScanConfig()
    logger.info(f"Config: {config.max_threads} threads, {config.timeout}s timeout")
    logger.info(f"Proxy rotation: every {config.proxy_rotation_interval} requests")

    # Load proxies
    proxies = load_proxies()

    # Load tickers
    tickers = load_tickers(config.target_tickers)

    # Create proxy manager
    proxy_manager = ProxyManager(proxies, rotation_interval=config.proxy_rotation_interval)

    # Create scanner
    scanner = TransparentProxyScanner(config, proxy_manager)

    # Run scan
    results = scanner.scan(tickers)

    # Save results
    output_file = BASE_DIR / config.output_json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total time: {results['scan_info']['scan_duration_seconds']:.2f}s")
    logger.info(f"Average rate: {results['scan_info']['average_rate_per_second']:.2f} tickers/sec")
    logger.info(f"Success: {results['scan_info']['successful']}/{results['scan_info']['total_tickers']} "
                f"({results['scan_info']['success_rate_percent']:.2f}%)")
    logger.info(f"Failed: {results['scan_info']['failed']}")
    logger.info("-" * 80)
    logger.info(f"✓ Results saved to: {output_file}")
    logger.info(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
