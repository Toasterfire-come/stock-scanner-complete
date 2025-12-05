#!/usr/bin/env python3
"""
Ultra-Fast Real-Time Stock Scanner
===================================
Goal: Scan 5130+ tickers in under 160 seconds (95%+ accuracy)
Target: ~0.031s per ticker average

Features:
- SOCKS5h proxy support (prevents DNS leakage)
- curl_cffi for browser TLS fingerprinting
- Per-request proxy rotation
- Aggressive concurrency (200+ threads)
- Real-time metrics only (17 fields)
- Smart retry with exponential backoff
"""

import os
import sys
import time
import random
import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from decimal import Decimal
import threading

# Django setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner.settings")

import django
django.setup()

from django.db import transaction
from stocks.models import Stock
from django.utils import timezone

# Import yfinance after Django setup
import yfinance as yf

# Try to import curl_cffi for better TLS fingerprinting
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    import requests
    curl_requests = None
    CURL_CFFI_AVAILABLE = False

# SOCKS proxy support
try:
    import socks
    from requests.adapters import HTTPAdapter
    from urllib3.contrib.socks import SOCKSProxyManager
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Configuration for ultra-fast scanning"""
    max_threads: int = 200  # Optimized for 5000+ tickers in <160s (~32 tickers/sec needed)
    timeout: float = 3.0  # Slightly longer for reliability
    max_retries: int = 2  # Minimal retries
    retry_delay: float = 0.1  # Fast retry
    target_time: int = 160  # Target completion time (seconds)
    min_success_rate: float = 0.95  # 95% minimum
    use_socks5h: bool = True  # Use SOCKS5h to prevent DNS leakage
    rotate_per_request: bool = True  # Rotate proxy every request
    random_delay_range: tuple = (0.005, 0.02)  # Minimal delay between requests


class ProxyRotator:
    """Thread-safe proxy rotator with health monitoring"""

    def __init__(self, proxies: List[str], use_socks5h: bool = True):
        self.proxies = proxies
        self.use_socks5h = use_socks5h
        self.current_index = 0
        self.lock = threading.Lock()
        self.failures = {}  # Track failures per proxy
        self.successes = {}  # Track successes per proxy
        self.last_used = {}  # Track last usage time

        logger.info(f"Initialized ProxyRotator with {len(proxies)} proxies (SOCKS5h: {use_socks5h})")

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None

        with self.lock:
            # Find least recently used healthy proxy
            available_proxies = [
                p for p in self.proxies
                if self.failures.get(p, 0) < 5  # Skip proxies with 5+ failures
            ]

            if not available_proxies:
                # Reset failures if all proxies are marked as failed
                logger.warning("All proxies failed, resetting failure counts")
                self.failures.clear()
                available_proxies = self.proxies

            # Round-robin selection
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index = (self.current_index + 1) % len(available_proxies)
            self.last_used[proxy] = time.time()

            return proxy

    def mark_success(self, proxy: str):
        """Mark proxy as successful"""
        with self.lock:
            self.successes[proxy] = self.successes.get(proxy, 0) + 1
            # Reduce failure count on success
            if proxy in self.failures and self.failures[proxy] > 0:
                self.failures[proxy] -= 1

    def mark_failure(self, proxy: str, reason: str = ""):
        """Mark proxy as failed"""
        with self.lock:
            self.failures[proxy] = self.failures.get(proxy, 0) + 1
            logger.debug(f"Proxy {proxy} failed ({reason}): {self.failures[proxy]} failures")

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
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
    """YFinance client with advanced proxy support"""

    # Browser user agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, proxy_rotator: ProxyRotator, config: ScanConfig):
        self.proxy_rotator = proxy_rotator
        self.config = config

    def _create_session(self, proxy: Optional[str]) -> Any:
        """Create session with proxy configuration"""
        if CURL_CFFI_AVAILABLE and curl_requests:
            # Use curl_cffi for better TLS fingerprinting
            session = curl_requests.Session()
            if proxy:
                session.proxies = {"http": proxy, "https": proxy}
        else:
            # Fallback to standard requests
            import requests
            session = requests.Session()
            if proxy:
                if self.config.use_socks5h and proxy.startswith("socks5://"):
                    # SOCKS5h proxy (DNS through proxy)
                    session.proxies = {
                        "http": proxy.replace("socks5://", "socks5h://"),
                        "https": proxy.replace("socks5://", "socks5h://")
                    }
                else:
                    session.proxies = {"http": proxy, "https": proxy}

        # Random user agent
        session.headers.update({
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        return session

    def fetch_realtime_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time data for a single ticker (17 fields)"""
        proxy = self.proxy_rotator.get_next_proxy() if self.config.rotate_per_request else None

        for attempt in range(self.config.max_retries):
            try:
                # Random delay to avoid pattern detection
                if self.config.random_delay_range:
                    delay = random.uniform(*self.config.random_delay_range)
                    time.sleep(delay)

                # Create session with proxy
                session = self._create_session(proxy)

                # Fetch data using yfinance
                stock = yf.Ticker(ticker, session=session)
                info = stock.info

                if not info or len(info) < 5:
                    if proxy:
                        self.proxy_rotator.mark_failure(proxy, "empty_data")
                    return None

                # Extract real-time fields (17 fields)
                data = {
                    # Critical Priority (7 fields) - Sub-minute updates
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "price_change": info.get("regularMarketChange"),
                    "price_change_percent": info.get("regularMarketChangePercent"),
                    "change_percent": info.get("regularMarketChangePercent"),  # Duplicate for compatibility
                    "volume": info.get("volume") or info.get("regularMarketVolume"),
                    "volume_today": info.get("regularMarketVolume"),
                    "dvav": None,  # Calculated separately

                    # Medium Priority (6 fields) - Minute updates
                    "bid_price": info.get("bid"),
                    "ask_price": info.get("ask"),
                    "bid_ask_spread": None,  # Calculated separately
                    "days_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                    "days_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                    "days_range": info.get("regularMarketDayRange"),

                    # Low Priority (4 fields) - Hourly updates
                    "price_change_week": None,  # Requires historical data
                    "price_change_month": None,  # Requires historical data
                    "price_change_year": None,  # Requires historical data

                    # Metadata
                    "ticker": ticker,
                    "last_updated": timezone.now()
                }

                # Calculate derived fields
                if data["volume_today"] and info.get("averageVolume"):
                    avg_vol = info.get("averageVolume")
                    if avg_vol and avg_vol > 0:
                        data["dvav"] = float(data["volume_today"]) / float(avg_vol)

                if data["bid_price"] and data["ask_price"]:
                    data["bid_ask_spread"] = f"{data['bid_price']:.2f} - {data['ask_price']:.2f}"

                # Mark proxy as successful
                if proxy:
                    self.proxy_rotator.mark_success(proxy)

                return data

            except Exception as e:
                logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {str(e)[:50]}")
                if proxy:
                    self.proxy_rotator.mark_failure(proxy, str(e)[:30])

                if attempt < self.config.max_retries - 1:
                    # Get new proxy for retry
                    proxy = self.proxy_rotator.get_next_proxy()
                    time.sleep(self.config.retry_delay * (2 ** attempt))

        return None


def load_tickers() -> List[str]:
    """Load tickers from combined ticker file"""
    combined_dir = BASE_DIR / "data" / "combined"

    # Find the latest combined ticker file
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))
    if not ticker_files:
        logger.error("No combined ticker files found")
        return []

    latest_file = ticker_files[-1]
    logger.info(f"Loading tickers from {latest_file.name}")

    # Import the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", latest_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS
    logger.info(f"Loaded {len(tickers)} tickers")
    return tickers


def load_proxies() -> List[str]:
    """Load proxies from configuration files"""
    proxies = []

    # Load from working_proxies.json
    proxy_file = BASE_DIR / "working_proxies.json"
    if proxy_file.exists():
        with open(proxy_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "proxies" in data:
                proxies.extend(data["proxies"])
            elif isinstance(data, list):
                proxies.extend(data)
        logger.info(f"Loaded {len(proxies)} proxies from working_proxies.json")

    # Load from socks5_proxies.json (if exists)
    socks_file = BASE_DIR / "socks5_proxies.json"
    if socks_file.exists():
        with open(socks_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "proxies" in data:
                proxies.extend(data["proxies"])
            elif isinstance(data, list):
                proxies.extend(data)
        logger.info(f"Loaded {len(proxies)} SOCKS5 proxies from socks5_proxies.json")

    # Load from environment variable
    env_proxies = os.getenv("REALTIME_PROXIES")
    if env_proxies:
        proxies.extend([p.strip() for p in env_proxies.split(",") if p.strip()])
        logger.info(f"Loaded {len(env_proxies.split(','))} proxies from environment")

    # Remove duplicates
    proxies = list(dict.fromkeys(proxies))

    if not proxies:
        logger.warning("No proxies loaded! Running without proxy rotation.")
    else:
        logger.info(f"Total unique proxies: {len(proxies)}")

    return proxies


def update_stock_in_db(data: Dict[str, Any]) -> bool:
    """Update stock in database"""
    try:
        with transaction.atomic():
            stock, created = Stock.objects.update_or_create(
                ticker=data["ticker"],
                defaults={
                    "current_price": data.get("current_price"),
                    "price_change": data.get("price_change"),
                    "price_change_percent": data.get("price_change_percent"),
                    "change_percent": data.get("change_percent"),
                    "volume": data.get("volume"),
                    "volume_today": data.get("volume_today"),
                    "dvav": data.get("dvav"),
                    "bid_price": data.get("bid_price"),
                    "ask_price": data.get("ask_price"),
                    "bid_ask_spread": data.get("bid_ask_spread"),
                    "days_low": data.get("days_low"),
                    "days_high": data.get("days_high"),
                    "days_range": data.get("days_range"),
                    "last_updated": data["last_updated"],
                }
            )
        return True
    except Exception as e:
        logger.error(f"Database error for {data['ticker']}: {str(e)}")
        return False


def run_ultra_fast_scan():
    """Main scanning function"""
    logger.info("=" * 80)
    logger.info("ULTRA-FAST REAL-TIME STOCK SCANNER")
    logger.info("=" * 80)

    # Load configuration
    config = ScanConfig()
    logger.info(f"Config: {config.max_threads} threads, {config.timeout}s timeout, {config.max_retries} retries")

    # Load tickers
    tickers = load_tickers()
    if not tickers:
        logger.error("No tickers to scan")
        return

    logger.info(f"Target: {len(tickers)} tickers in {config.target_time}s ({len(tickers)/config.target_time:.2f} tickers/sec)")

    # Load proxies
    proxies = load_proxies()
    proxy_rotator = ProxyRotator(proxies, use_socks5h=config.use_socks5h)

    # Create YFinance client
    client = YFinanceClient(proxy_rotator, config)

    # Statistics
    stats = {
        "total": len(tickers),
        "success": 0,
        "failed": 0,
        "db_updated": 0,
        "db_failed": 0,
        "start_time": time.time()
    }

    logger.info(f"Starting scan at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("-" * 80)

    # Execute concurrent scanning
    with ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        futures = {executor.submit(client.fetch_realtime_data, ticker): ticker for ticker in tickers}

        for i, future in enumerate(as_completed(futures), 1):
            ticker = futures[future]

            try:
                data = future.result()

                if data:
                    stats["success"] += 1
                    # Update database
                    if update_stock_in_db(data):
                        stats["db_updated"] += 1
                    else:
                        stats["db_failed"] += 1
                else:
                    stats["failed"] += 1

                # Progress update every 100 tickers
                if i % 100 == 0:
                    elapsed = time.time() - stats["start_time"]
                    rate = i / elapsed
                    eta = (stats["total"] - i) / rate if rate > 0 else 0
                    success_rate = (stats["success"] / i) * 100

                    logger.info(
                        f"Progress: {i}/{stats['total']} ({i/stats['total']*100:.1f}%) | "
                        f"Rate: {rate:.2f} tickers/sec | "
                        f"Success: {success_rate:.1f}% | "
                        f"ETA: {eta:.0f}s"
                    )

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                stats["failed"] += 1

    # Final statistics
    elapsed = time.time() - stats["start_time"]
    success_rate = (stats["success"] / stats["total"]) * 100

    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total time: {elapsed:.2f}s")
    logger.info(f"Average rate: {stats['total']/elapsed:.2f} tickers/sec")
    logger.info(f"Success: {stats['success']}/{stats['total']} ({success_rate:.2f}%)")
    logger.info(f"Failed: {stats['failed']}/{stats['total']} ({stats['failed']/stats['total']*100:.2f}%)")
    logger.info(f"DB Updated: {stats['db_updated']}")
    logger.info(f"DB Failed: {stats['db_failed']}")

    # Proxy statistics
    proxy_stats = proxy_rotator.get_stats()
    logger.info("-" * 80)
    logger.info("PROXY STATISTICS")
    logger.info("-" * 80)
    logger.info(f"Total proxies: {proxy_stats['total_proxies']}")
    logger.info(f"Healthy proxies: {proxy_stats['healthy_proxies']}")
    logger.info(f"Proxy success rate: {proxy_stats['success_rate']*100:.2f}%")
    logger.info(f"Total proxy successes: {proxy_stats['total_successes']}")
    logger.info(f"Total proxy failures: {proxy_stats['total_failures']}")

    # Check if we met targets
    logger.info("=" * 80)
    if elapsed <= config.target_time:
        logger.info(f"✓ TIME TARGET MET: {elapsed:.2f}s <= {config.target_time}s")
    else:
        logger.warning(f"✗ TIME TARGET MISSED: {elapsed:.2f}s > {config.target_time}s")

    if success_rate >= config.min_success_rate * 100:
        logger.info(f"✓ SUCCESS RATE TARGET MET: {success_rate:.2f}% >= {config.min_success_rate*100}%")
    else:
        logger.warning(f"✗ SUCCESS RATE TARGET MISSED: {success_rate:.2f}% < {config.min_success_rate*100}%")

    logger.info("=" * 80)


if __name__ == "__main__":
    run_ultra_fast_scan()
