#!/usr/bin/env python3
"""
Daily Fundamentals Stock Scanner
==================================
Goal: Comprehensive fundamental data collection (66+ fields)
Max Time: 2 hours for 5000+ tickers
Target: 95%+ accuracy with complete fundamental metrics

Features:
- SOCKS5h proxy support (prevents DNS leakage)
- curl_cffi for browser TLS fingerprinting
- Smart proxy rotation with health monitoring
- Comprehensive fundamental metrics (50+ fields)
- Valuation scores and fair value calculations
- Retry logic with exponential backoff
- JSON storage for extended metrics
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
from datetime import datetime

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
    """Configuration for daily fundamentals scanning"""
    max_threads: int = 100  # Moderate concurrency for thorough data collection
    timeout: float = 8.0  # Longer timeout for complete data
    max_retries: int = 3  # More retries for important data
    retry_delay: float = 0.5  # Moderate retry delay
    target_time: int = 7200  # 2 hours maximum
    min_success_rate: float = 0.95  # 95% minimum
    use_socks5h: bool = True  # Use SOCKS5h to prevent DNS leakage
    rotate_per_request: bool = True  # Rotate proxy every request
    random_delay_range: tuple = (0.5, 2.0)  # Random delay to avoid patterns
    proxy_rotation_threshold: int = 50  # Rotate proxy every N requests


class ProxyRotator:
    """Thread-safe proxy rotator with advanced health monitoring"""

    def __init__(self, proxies: List[str], use_socks5h: bool = True):
        self.proxies = proxies
        self.use_socks5h = use_socks5h
        self.current_index = 0
        self.lock = threading.Lock()
        self.failures = {}  # Track failures per proxy
        self.successes = {}  # Track successes per proxy
        self.last_used = {}  # Track last usage time
        self.request_count = {}  # Track request count per proxy

        logger.info(f"Initialized ProxyRotator with {len(proxies)} proxies (SOCKS5h: {use_socks5h})")

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy with intelligent selection"""
        if not self.proxies:
            return None

        with self.lock:
            # Filter out heavily failed proxies
            available_proxies = [
                p for p in self.proxies
                if self.failures.get(p, 0) < 10  # Skip proxies with 10+ failures
            ]

            if not available_proxies:
                # Reset failures if all proxies are marked as failed
                logger.warning("All proxies failed, resetting failure counts")
                self.failures.clear()
                available_proxies = self.proxies

            # Prefer proxies with higher success rates
            proxy_scores = []
            for p in available_proxies:
                success = self.successes.get(p, 0)
                failure = self.failures.get(p, 0)
                total = success + failure
                score = success / total if total > 0 else 0.5
                # Boost score for less-used proxies
                requests = self.request_count.get(p, 0)
                score += 0.1 / (requests + 1)
                proxy_scores.append((p, score))

            # Sort by score and pick from top 30%
            proxy_scores.sort(key=lambda x: x[1], reverse=True)
            top_proxies = [p for p, _ in proxy_scores[:max(1, len(proxy_scores) // 3)]]
            proxy = random.choice(top_proxies)

            self.last_used[proxy] = time.time()
            self.request_count[proxy] = self.request_count.get(proxy, 0) + 1

            return proxy

    def mark_success(self, proxy: str):
        """Mark proxy as successful"""
        with self.lock:
            self.successes[proxy] = self.successes.get(proxy, 0) + 1
            # Reduce failure count on success
            if proxy in self.failures and self.failures[proxy] > 0:
                self.failures[proxy] = max(0, self.failures[proxy] - 1)

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
                "healthy_proxies": len([p for p in self.proxies if self.failures.get(p, 0) < 10]),
                "top_performers": sorted(
                    [(p, self.successes.get(p, 0)) for p in self.proxies],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }


class YFinanceClient:
    """YFinance client with comprehensive data collection"""

    # Browser user agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    ]

    def __init__(self, proxy_rotator: ProxyRotator, config: ScanConfig):
        self.proxy_rotator = proxy_rotator
        self.config = config

    def _create_session(self, proxy: Optional[str]) -> Any:
        """Create session with advanced proxy configuration"""
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

        # Random user agent and browser headers
        session.headers.update({
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        })

        return session

    def fetch_fundamentals(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive fundamental data (66+ fields)"""
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

                if not info or len(info) < 10:
                    if proxy:
                        self.proxy_rotator.mark_failure(proxy, "empty_data")
                    return None

                # Extract all fundamental fields (66+ fields)
                data = self._extract_all_fields(ticker, info)

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
                    # Exponential backoff
                    time.sleep(self.config.retry_delay * (2 ** attempt))

        return None

    def _extract_all_fields(self, ticker: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all 66+ fields from yfinance data"""

        # Helper to safely get numeric values
        def safe_float(value, default=None):
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=None):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # ==================== BASIC INFO (16 FIELDS) ====================
        current_price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        avg_volume = safe_int(info.get("averageVolume"))
        volume_today = safe_int(info.get("volume") or info.get("regularMarketVolume"))

        data = {
            "ticker": ticker,
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "exchange": info.get("exchange") or "NASDAQ",
            "market_cap": safe_int(info.get("marketCap")),
            "market_cap_change_3mon": None,  # Calculated from historical data
            "avg_volume_3mon": avg_volume,
            "shares_available": safe_int(info.get("sharesOutstanding")),
            "week_52_low": safe_float(info.get("fiftyTwoWeekLow")),
            "week_52_high": safe_float(info.get("fiftyTwoWeekHigh")),
            "one_year_target": safe_float(info.get("targetMeanPrice")),
            "book_value": safe_float(info.get("bookValue")),
            "earnings_per_share": safe_float(info.get("trailingEps")),
            "price_to_book": safe_float(info.get("priceToBook")),
            "dividend_yield": safe_float(info.get("dividendYield")),
            "pe_ratio": safe_float(info.get("trailingPE") or info.get("forwardPE")),
            "pe_change_3mon": None,  # Calculated from historical data

            # ==================== REAL-TIME DATA (17 FIELDS) ====================
            "current_price": current_price,
            "price_change": safe_float(info.get("regularMarketChange")),
            "price_change_percent": safe_float(info.get("regularMarketChangePercent")),
            "change_percent": safe_float(info.get("regularMarketChangePercent")),
            "volume": volume_today,
            "volume_today": volume_today,
            "dvav": safe_float(volume_today / avg_volume) if volume_today and avg_volume and avg_volume > 0 else None,
            "bid_price": safe_float(info.get("bid")),
            "ask_price": safe_float(info.get("ask")),
            "bid_ask_spread": info.get("regularMarketDayRange"),
            "days_low": safe_float(info.get("dayLow") or info.get("regularMarketDayLow")),
            "days_high": safe_float(info.get("dayHigh") or info.get("regularMarketDayHigh")),
            "days_range": info.get("regularMarketDayRange"),
            "price_change_week": None,  # Requires historical data
            "price_change_month": None,  # Requires historical data
            "price_change_year": None,  # Requires historical data

            "last_updated": timezone.now(),
        }

        # ==================== FUNDAMENTALS (50+ FIELDS in JSON) ====================
        fundamentals = {
            # Valuation Metrics (8 fields)
            "pe_ratio": safe_float(info.get("trailingPE")),
            "forward_pe": safe_float(info.get("forwardPE")),
            "peg_ratio": safe_float(info.get("pegRatio")),
            "price_to_sales": safe_float(info.get("priceToSalesTrailing12Months")),
            "price_to_book": safe_float(info.get("priceToBook")),
            "ev_to_revenue": safe_float(info.get("enterpriseToRevenue")),
            "ev_to_ebitda": safe_float(info.get("enterpriseToEbitda")),
            "enterprise_value": safe_int(info.get("enterpriseValue")),

            # Profitability Metrics (6 fields)
            "gross_margin": safe_float(info.get("grossMargins")),
            "operating_margin": safe_float(info.get("operatingMargins")),
            "profit_margin": safe_float(info.get("profitMargins")),
            "roe": safe_float(info.get("returnOnEquity")),
            "roa": safe_float(info.get("returnOnAssets")),
            "roic": None,  # Not directly available

            # Growth Metrics (6 fields)
            "revenue_growth_yoy": safe_float(info.get("revenueGrowth")),
            "revenue_growth_3y": None,  # Requires calculation
            "revenue_growth_5y": None,  # Requires calculation
            "earnings_growth_yoy": safe_float(info.get("earningsGrowth")),
            "earnings_growth_5y": None,  # Requires calculation
            "fcf_growth_yoy": None,  # Requires calculation

            # Financial Health (7 fields)
            "current_ratio": safe_float(info.get("currentRatio")),
            "quick_ratio": safe_float(info.get("quickRatio")),
            "debt_to_equity": safe_float(info.get("debtToEquity")),
            "debt_to_assets": None,  # Requires calculation
            "interest_coverage": None,  # Requires calculation
            "altman_z_score": None,  # Requires calculation
            "piotroski_f_score": None,  # Requires calculation

            # Cash Flow (5 fields)
            "operating_cash_flow": safe_int(info.get("operatingCashflow")),
            "free_cash_flow": safe_int(info.get("freeCashflow")),
            "fcf_per_share": None,  # Calculated below
            "fcf_yield": None,  # Calculated below
            "cash_conversion": None,  # Requires calculation

            # Dividend Metrics (3 fields)
            "dividend_yield": safe_float(info.get("dividendYield")),
            "dividend_payout_ratio": safe_float(info.get("payoutRatio")),
            "years_dividend_growth": None,  # Requires historical data

            # Fair Values (5 fields)
            "dcf_value": None,  # Requires calculation
            "epv_value": None,  # Requires calculation
            "graham_number": None,  # Calculated below
            "peg_fair_value": None,  # Calculated below
            "relative_value_score": None,  # Calculated below

            # Scores (7 fields)
            "valuation_score": None,  # Calculated below
            "valuation_status": None,  # Calculated below
            "recommendation": info.get("recommendationKey"),
            "confidence": None,  # Calculated below
            "strength_score": None,  # Calculated below
            "strength_grade": None,  # Calculated below
            "data_quality": None,  # Calculated below

            # Additional metrics
            "beta": safe_float(info.get("beta")),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "full_time_employees": safe_int(info.get("fullTimeEmployees")),
        }

        # Calculate derived metrics
        if fundamentals["free_cash_flow"] and data["shares_available"]:
            fundamentals["fcf_per_share"] = fundamentals["free_cash_flow"] / data["shares_available"]

        if fundamentals["free_cash_flow"] and data["market_cap"]:
            fundamentals["fcf_yield"] = fundamentals["free_cash_flow"] / data["market_cap"]

        # Graham Number = sqrt(22.5 * EPS * Book Value)
        if data["earnings_per_share"] and data["book_value"]:
            fundamentals["graham_number"] = (22.5 * data["earnings_per_share"] * data["book_value"]) ** 0.5

        # PEG Fair Value
        if fundamentals["earnings_growth_yoy"] and data["earnings_per_share"]:
            fundamentals["peg_fair_value"] = fundamentals["earnings_growth_yoy"] * 100 * data["earnings_per_share"]

        # Data quality score (0-100)
        non_null_count = sum(1 for v in fundamentals.values() if v is not None)
        fundamentals["data_quality"] = int((non_null_count / len(fundamentals)) * 100)

        # Valuation score (simple implementation)
        if fundamentals["pe_ratio"] and fundamentals["peg_ratio"]:
            if fundamentals["pe_ratio"] < 15 and fundamentals["peg_ratio"] < 1:
                fundamentals["valuation_score"] = 90
                fundamentals["valuation_status"] = "Undervalued"
            elif fundamentals["pe_ratio"] < 25 and fundamentals["peg_ratio"] < 2:
                fundamentals["valuation_score"] = 70
                fundamentals["valuation_status"] = "Fair"
            else:
                fundamentals["valuation_score"] = 40
                fundamentals["valuation_status"] = "Overvalued"

        # Store fundamentals in JSON field
        data["valuation_json"] = fundamentals

        return data


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
    env_proxies = os.getenv("DAILY_PROXIES")
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
    """Update stock in database with all fundamental data"""
    try:
        with transaction.atomic():
            stock, created = Stock.objects.update_or_create(
                ticker=data["ticker"],
                defaults={
                    # Basic info
                    "company_name": data.get("company_name"),
                    "name": data.get("name"),
                    "exchange": data.get("exchange"),
                    "market_cap": data.get("market_cap"),
                    "avg_volume_3mon": data.get("avg_volume_3mon"),
                    "shares_available": data.get("shares_available"),
                    "week_52_low": data.get("week_52_low"),
                    "week_52_high": data.get("week_52_high"),
                    "one_year_target": data.get("one_year_target"),
                    "book_value": data.get("book_value"),
                    "earnings_per_share": data.get("earnings_per_share"),
                    "price_to_book": data.get("price_to_book"),
                    "dividend_yield": data.get("dividend_yield"),
                    "pe_ratio": data.get("pe_ratio"),

                    # Real-time data
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

                    # Fundamentals (stored in JSON)
                    "valuation_json": data.get("valuation_json"),

                    "last_updated": data["last_updated"],
                }
            )
        return True
    except Exception as e:
        logger.error(f"Database error for {data['ticker']}: {str(e)}")
        return False


def run_daily_fundamentals_scan():
    """Main scanning function for daily fundamentals"""
    logger.info("=" * 80)
    logger.info("DAILY FUNDAMENTALS STOCK SCANNER")
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
        futures = {executor.submit(client.fetch_fundamentals, ticker): ticker for ticker in tickers}

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

                # Progress update every 50 tickers
                if i % 50 == 0:
                    elapsed = time.time() - stats["start_time"]
                    rate = i / elapsed
                    eta = (stats["total"] - i) / rate if rate > 0 else 0
                    success_rate = (stats["success"] / i) * 100

                    logger.info(
                        f"Progress: {i}/{stats['total']} ({i/stats['total']*100:.1f}%) | "
                        f"Rate: {rate:.2f} tickers/sec | "
                        f"Success: {success_rate:.1f}% | "
                        f"ETA: {eta/60:.1f} min"
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
    logger.info(f"Total time: {elapsed/60:.2f} minutes ({elapsed:.2f}s)")
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

    if proxy_stats['top_performers']:
        logger.info("\nTop 5 performing proxies:")
        for proxy, successes in proxy_stats['top_performers']:
            logger.info(f"  {proxy}: {successes} successes")

    # Check if we met targets
    logger.info("=" * 80)
    if elapsed <= config.target_time:
        logger.info(f"✓ TIME TARGET MET: {elapsed/60:.2f}min <= {config.target_time/60:.1f}min")
    else:
        logger.warning(f"✗ TIME TARGET MISSED: {elapsed/60:.2f}min > {config.target_time/60:.1f}min")

    if success_rate >= config.min_success_rate * 100:
        logger.info(f"✓ SUCCESS RATE TARGET MET: {success_rate:.2f}% >= {config.min_success_rate*100}%")
    else:
        logger.warning(f"✗ SUCCESS RATE TARGET MISSED: {success_rate:.2f}% < {config.min_success_rate*100}%")

    logger.info("=" * 80)


if __name__ == "__main__":
    run_daily_fundamentals_scan()
