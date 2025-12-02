#!/usr/bin/env python3
"""
Unified Proxy Manager
=====================

Fetches high-quality proxies from Geonode API and manages OS-level proxy redirection
with automatic switching on rate limits or after 500 tickers.
"""

import os
import sys
import time
import json
import logging
import requests
from typing import List, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# =====================================================
# GEONODE PROXY FETCHER
# =====================================================

class GeonodeProxyFetcher:
    """Fetch elite proxies from Geonode API"""

    API_URL = "https://proxylist.geonode.com/api/proxy-list"

    @staticmethod
    def fetch_proxies(limit: int = 500) -> List[Dict]:
        """
        Fetch high-quality proxies from Geonode API

        Filters:
        - anonymityLevel=elite (highest anonymity)
        - filterUpTime=90 (90%+ uptime)
        - filterLastChecked=10 (checked in last 10 minutes)
        - speed=fast (fast proxies only)
        """

        params = {
            'anonymityLevel': 'elite',
            'filterUpTime': 90,
            'filterLastChecked': 10,
            'speed': 'fast',
            'limit': limit,
            'page': 1,
            'sort_by': 'lastChecked',
            'sort_type': 'desc'
        }

        try:
            logger.info(f"Fetching proxies from Geonode API (limit={limit})...")
            response = requests.get(
                GeonodeProxyFetcher.API_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            proxies = data.get('data', [])

            logger.info(f"Successfully fetched {len(proxies)} elite proxies")
            return proxies

        except Exception as e:
            logger.error(f"Failed to fetch proxies from Geonode: {e}")
            return []

    @staticmethod
    def format_proxy(proxy_data: Dict) -> tuple:
        """
        Format proxy data into URL string

        Returns:
            tuple: (proxy_url, is_http) where is_http indicates if it's HTTP/HTTPS
        """
        ip = proxy_data.get('ip')
        port = proxy_data.get('port')
        protocols = proxy_data.get('protocols', ['http'])

        # Prefer HTTP/HTTPS over SOCKS for yfinance compatibility
        protocol = None
        is_http = False

        if 'https' in protocols:
            protocol = 'https'
            is_http = True
        elif 'http' in protocols:
            protocol = 'http'
            is_http = True
        elif 'socks5' in protocols:
            protocol = 'socks5'
        elif 'socks4' in protocols:
            protocol = 'socks4'
        elif protocols:
            protocol = protocols[0]
        else:
            protocol = 'http'

        return (f"{protocol}://{ip}:{port}", is_http)

# =====================================================
# UNIFIED PROXY MANAGER
# =====================================================

class UnifiedProxyManager:
    """
    Manages OS-level proxy redirection with automatic switching

    Features:
    - Fetches proxies from Geonode API at startup
    - Sets OS-level environment variables (http_proxy, https_proxy, etc.)
    - Monitors request count and switches after 500 tickers
    - Detects rate limits and switches immediately
    - Tracks failed proxies to avoid reuse
    """

    def __init__(self, auto_fetch: bool = True):
        self.proxies: List[str] = []
        self.proxy_data: List[Dict] = []
        self.current_proxy: Optional[str] = None
        self.current_index: int = 0
        self.request_count: int = 0
        self.proxy_switches: int = 0
        self.rate_limits_detected: int = 0
        self.failed_proxies: set = set()
        self.last_fetch_time: Optional[datetime] = None

        # Configuration
        self.max_requests_per_proxy = 500  # Switch after 500 tickers
        self.refetch_interval_hours = 1    # Refresh proxy list hourly

        if auto_fetch:
            self.fetch_and_load_proxies()

    def fetch_and_load_proxies(self, limit: int = 500, prefer_http: bool = True) -> bool:
        """
        Fetch proxies from Geonode and load them

        Args:
            limit: Maximum number of proxies to fetch
            prefer_http: If True, prioritize HTTP/HTTPS proxies over SOCKS

        Returns:
            bool: True if proxies were loaded successfully
        """
        try:
            logger.info("=" * 70)
            logger.info("FETCHING PROXIES FROM GEONODE API")
            logger.info("=" * 70)

            self.proxy_data = GeonodeProxyFetcher.fetch_proxies(limit=limit)

            if not self.proxy_data:
                logger.warning("No proxies fetched from Geonode")
                return False

            # Format proxies and separate by type
            http_proxies = []
            socks_proxies = []

            for p in self.proxy_data:
                proxy_url, is_http = GeonodeProxyFetcher.format_proxy(p)

                if is_http:
                    http_proxies.append(proxy_url)
                else:
                    socks_proxies.append(proxy_url)

            # Prioritize HTTP proxies if requested
            if prefer_http:
                self.proxies = http_proxies + socks_proxies
            else:
                self.proxies = socks_proxies + http_proxies

            # Remove failed proxies from previous runs
            self.proxies = [p for p in self.proxies if p not in self.failed_proxies]

            logger.info(f"Loaded {len(self.proxies)} working proxies")
            logger.info(f"  HTTP/HTTPS: {len(http_proxies)}")
            logger.info(f"  SOCKS: {len(socks_proxies)}")
            logger.info(f"Failed proxies excluded: {len(self.failed_proxies)}")

            self.last_fetch_time = datetime.now()

            # Log sample proxies
            if self.proxies:
                logger.info("\nSample proxies:")
                for i, proxy in enumerate(self.proxies[:5]):
                    proxy_type = "HTTP" if proxy in http_proxies else "SOCKS"
                    logger.info(f"  {i+1}. {proxy} ({proxy_type})")
                logger.info("")

            logger.info("=" * 70)
            return True

        except Exception as e:
            logger.error(f"Failed to fetch and load proxies: {e}")
            return False

    def should_refetch_proxies(self) -> bool:
        """Check if we should refetch proxies"""
        if not self.last_fetch_time:
            return True

        elapsed = datetime.now() - self.last_fetch_time
        return elapsed > timedelta(hours=self.refetch_interval_hours)

    def set_proxy(self, proxy_url: Optional[str] = None) -> bool:
        """
        Set OS-level proxy environment variables

        Sets all common proxy environment variable variants to ensure
        all traffic is redirected through the proxy.

        CRITICAL: Sets proxy BEFORE any network calls to ensure yfinance/curl_cffi picks it up
        """
        try:
            if proxy_url:
                # CRITICAL: Set proxy environment variables FIRST, before any imports/calls
                proxy_vars = [
                    'HTTP_PROXY', 'HTTPS_PROXY',
                    'http_proxy', 'https_proxy',
                    'ALL_PROXY', 'all_proxy',
                    'REQUESTS_PROXY', 'requests_proxy'  # Additional for requests compatibility
                ]

                for var in proxy_vars:
                    os.environ[var] = proxy_url

                # Also set NO_PROXY to avoid proxying localhost
                os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
                os.environ['no_proxy'] = 'localhost,127.0.0.1'

                self.current_proxy = proxy_url
                self.request_count = 0  # Reset request counter

                logger.info(f"[PROXY] Set OS-level proxy: {proxy_url}")

                # Force clear any cached curl_cffi sessions
                try:
                    import gc
                    gc.collect()  # Force garbage collection to clear old sessions
                except:
                    pass

                return True
            else:
                # Clear all proxy settings
                proxy_vars = [
                    'HTTP_PROXY', 'HTTPS_PROXY',
                    'http_proxy', 'https_proxy',
                    'ALL_PROXY', 'all_proxy',
                    'REQUESTS_PROXY', 'requests_proxy'
                ]

                for var in proxy_vars:
                    if var in os.environ:
                        del os.environ[var]

                self.current_proxy = None
                self.request_count = 0

                logger.info("[PROXY] Cleared OS-level proxies (direct connection)")

                # Force clear any cached sessions
                try:
                    import gc
                    gc.collect()
                except:
                    pass

                return True

        except Exception as e:
            logger.error(f"Failed to set proxy: {e}")
            return False

    def switch_proxy(self, reason: str = "manual") -> bool:
        """Switch to next available proxy"""
        if not self.proxies:
            logger.warning("No proxies available to switch to")
            return False

        # Mark current proxy as failed if switching due to rate limit
        if reason == "rate_limit" and self.current_proxy:
            self.mark_failed(self.current_proxy, reason)

        # Find next working proxy
        attempts = 0
        max_attempts = len(self.proxies)

        while attempts < max_attempts:
            self.current_index = (self.current_index + 1) % len(self.proxies)
            next_proxy = self.proxies[self.current_index]

            if next_proxy not in self.failed_proxies:
                self.set_proxy(next_proxy)
                self.proxy_switches += 1
                logger.info(f"[PROXY SWITCH] Reason: {reason} | Switch #{self.proxy_switches} | Index: {self.current_index + 1}/{len(self.proxies)}")
                return True

            attempts += 1

        logger.error("All proxies have failed, clearing proxy settings")
        self.set_proxy(None)
        return False

    def mark_failed(self, proxy_url: str, reason: str = "unknown"):
        """Mark a proxy as failed"""
        self.failed_proxies.add(proxy_url)
        logger.warning(f"[PROXY FAILED] {proxy_url} - Reason: {reason} | Total failed: {len(self.failed_proxies)}")

    def increment_request_count(self) -> bool:
        """
        Increment request counter and check if we should switch proxy

        Returns True if proxy was switched
        """
        self.request_count += 1

        # Check if we should switch after reaching limit
        if self.request_count >= self.max_requests_per_proxy:
            logger.info(f"[PROXY] Reached {self.request_count} requests, switching proxy...")
            return self.switch_proxy(reason="request_limit")

        return False

    def handle_rate_limit(self) -> bool:
        """Handle rate limit detection by switching proxy"""
        self.rate_limits_detected += 1
        logger.warning(f"[RATE LIMIT] Detected (#{self.rate_limits_detected})")
        return self.switch_proxy(reason="rate_limit")

    @staticmethod
    def detect_rate_limit(error: Exception) -> bool:
        """Detect if error is a rate limit"""
        error_str = str(error).lower()

        rate_limit_indicators = [
            'rate limit', '429', 'too many requests',
            'invalid crumb', 'user is unable to access',
            '401', 'unauthorized', '403', 'forbidden',
            'quota exceeded', 'throttled'
        ]

        return any(indicator in error_str for indicator in rate_limit_indicators)

    def get_stats(self) -> Dict:
        """Get current proxy manager statistics"""
        return {
            'total_proxies': len(self.proxies),
            'failed_proxies': len(self.failed_proxies),
            'working_proxies': len(self.proxies) - len(self.failed_proxies),
            'current_proxy': self.current_proxy,
            'current_index': self.current_index + 1,
            'request_count': self.request_count,
            'max_requests': self.max_requests_per_proxy,
            'proxy_switches': self.proxy_switches,
            'rate_limits_detected': self.rate_limits_detected,
            'last_fetch': self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }

    def clear(self):
        """Clear all proxy settings"""
        self.set_proxy(None)
        logger.info("[PROXY] Cleared all proxy settings")

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def create_proxy_manager() -> UnifiedProxyManager:
    """Create and initialize proxy manager"""
    manager = UnifiedProxyManager(auto_fetch=True)

    # Set initial proxy if available
    if manager.proxies:
        manager.switch_proxy(reason="initialization")
    else:
        logger.warning("No proxies available, running without proxy")

    return manager

# =====================================================
# MAIN - FOR TESTING
# =====================================================

def main():
    """Test the unified proxy manager"""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    logger.info("=" * 70)
    logger.info("UNIFIED PROXY MANAGER - TEST")
    logger.info("=" * 70)

    # Create manager
    manager = create_proxy_manager()

    # Show stats
    stats = manager.get_stats()
    logger.info("\nProxy Manager Stats:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    # Test proxy switching
    logger.info("\n" + "=" * 70)
    logger.info("Testing proxy switching...")
    logger.info("=" * 70)

    for i in range(3):
        logger.info(f"\nSwitch test {i+1}/3")
        manager.switch_proxy(reason="test")
        time.sleep(1)

    # Test rate limit handling
    logger.info("\n" + "=" * 70)
    logger.info("Testing rate limit handling...")
    logger.info("=" * 70)

    manager.handle_rate_limit()

    # Test request counting
    logger.info("\n" + "=" * 70)
    logger.info("Testing request counting...")
    logger.info("=" * 70)

    # Simulate 505 requests
    logger.info("Simulating 505 requests...")
    for i in range(505):
        switched = manager.increment_request_count()
        if switched:
            logger.info(f"Auto-switched at request {i+1}")

    # Final stats
    logger.info("\n" + "=" * 70)
    logger.info("Final Stats:")
    logger.info("=" * 70)
    stats = manager.get_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    # Cleanup
    manager.clear()

    logger.info("\n" + "=" * 70)
    logger.info("TEST COMPLETE")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
