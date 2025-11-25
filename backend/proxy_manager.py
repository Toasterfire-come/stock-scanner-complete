#!/usr/bin/env python3
"""
Advanced Proxy Manager - Fetches, validates, and manages free proxies
for stock data retrieval to avoid rate limits.

Sources:
- Proxifly (GitHub): 2800+ proxies, updated every 5 minutes
- ProxyScrape: HTTP/SOCKS5 proxies, updated every 5 minutes
- TheSpeedX PROXY-List: 45k+ proxies, updated daily
- Free-Proxy-List.net: Curated list of working proxies
"""

import os
import sys
import json
import time
import logging
import requests
import concurrent.futures
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """Information about a proxy server"""
    address: str
    protocol: str = "http"
    country: str = ""
    response_time: float = 0.0
    success_rate: float = 0.0
    last_checked: str = ""
    is_working: bool = False


class ProxyFetcher:
    """Fetches proxies from multiple free sources"""

    # Free proxy source URLs
    SOURCES = {
        'proxifly_http': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json',
        'proxifly_socks4': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.json',
        'proxifly_socks5': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.json',
        'thespeedx_http': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'thespeedx_socks4': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'thespeedx_socks5': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'proxyscrape_http': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'proxyscrape_socks4': 'https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=10000&country=all',
        'proxyscrape_socks5': 'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all',
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_from_source(self, name: str, url: str) -> List[ProxyInfo]:
        """Fetch proxies from a single source"""
        proxies = []
        protocol = 'http'

        if 'socks4' in name:
            protocol = 'socks4'
        elif 'socks5' in name:
            protocol = 'socks5'

        try:
            logger.info(f"Fetching proxies from {name}...")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse based on format
            if url.endswith('.json'):
                # JSON format (Proxifly)
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            ip = item.get('ip', '')
                            port = item.get('port', '')
                            if ip and port:
                                proxy_addr = f"{protocol}://{ip}:{port}"
                                proxies.append(ProxyInfo(
                                    address=proxy_addr,
                                    protocol=protocol,
                                    country=item.get('country', ''),
                                ))
                        elif isinstance(item, str) and ':' in item:
                            proxy_addr = f"{protocol}://{item}"
                            proxies.append(ProxyInfo(address=proxy_addr, protocol=protocol))
            else:
                # Text format (TheSpeedX, ProxyScrape)
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#'):
                        # Format: IP:PORT
                        proxy_addr = f"{protocol}://{line}"
                        proxies.append(ProxyInfo(address=proxy_addr, protocol=protocol))

            logger.info(f"Fetched {len(proxies)} proxies from {name}")
            return proxies

        except Exception as e:
            logger.error(f"Error fetching from {name}: {e}")
            return []

    def fetch_all(self, limit: Optional[int] = None) -> List[ProxyInfo]:
        """Fetch proxies from all sources in parallel"""
        all_proxies = []
        seen = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.fetch_from_source, name, url): name
                for name, url in self.SOURCES.items()
            }

            for future in concurrent.futures.as_completed(futures):
                try:
                    proxies = future.result()
                    # Deduplicate
                    for proxy in proxies:
                        if proxy.address not in seen:
                            seen.add(proxy.address)
                            all_proxies.append(proxy)
                            if limit and len(all_proxies) >= limit:
                                break
                except Exception as e:
                    logger.error(f"Error processing future: {e}")

                if limit and len(all_proxies) >= limit:
                    break

        logger.info(f"Total unique proxies fetched: {len(all_proxies)}")
        return all_proxies[:limit] if limit else all_proxies


class ProxyValidator:
    """Validates proxies against test endpoints"""

    # Test URLs - use fast, reliable endpoints
    TEST_URLS = [
        'http://httpbin.org/ip',
        'https://api.ipify.org?format=json',
        'http://ip-api.com/json/',
    ]

    def __init__(self, timeout: int = 10, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers

    def test_proxy(self, proxy: ProxyInfo) -> Tuple[ProxyInfo, bool]:
        """Test a single proxy"""
        start_time = time.time()

        # Configure proxy dict for requests
        proxy_dict = {
            'http': proxy.address,
            'https': proxy.address,
        }

        # Try each test URL
        for test_url in self.TEST_URLS:
            try:
                response = requests.get(
                    test_url,
                    proxies=proxy_dict,
                    timeout=self.timeout,
                    verify=False  # Skip SSL verification for speed
                )

                if response.status_code == 200:
                    elapsed = time.time() - start_time
                    proxy.response_time = round(elapsed, 2)
                    proxy.is_working = True
                    proxy.last_checked = datetime.now().isoformat()
                    return proxy, True

            except Exception:
                continue

        # All tests failed
        proxy.is_working = False
        proxy.last_checked = datetime.now().isoformat()
        return proxy, False

    def validate_batch(self, proxies: List[ProxyInfo], show_progress: bool = True) -> List[ProxyInfo]:
        """Validate a batch of proxies in parallel"""
        working_proxies = []
        total = len(proxies)

        logger.info(f"Validating {total} proxies with {self.max_workers} workers...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_proxy, proxy): proxy for proxy in proxies}

            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                try:
                    proxy, is_working = future.result()
                    if is_working:
                        working_proxies.append(proxy)
                        if show_progress and completed % 10 == 0:
                            logger.info(f"Progress: {completed}/{total} tested, {len(working_proxies)} working")
                except Exception as e:
                    logger.debug(f"Validation error: {e}")

        logger.info(f"Validation complete: {len(working_proxies)}/{total} proxies working ({len(working_proxies)/total*100:.1f}%)")

        # Sort by response time
        working_proxies.sort(key=lambda p: p.response_time)

        return working_proxies


class ProxyManager:
    """Complete proxy management system"""

    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.fetcher = ProxyFetcher()
        self.validator = ProxyValidator()

    def refresh_proxies(self, fetch_limit: Optional[int] = 500, validate_limit: Optional[int] = None) -> List[ProxyInfo]:
        """Fetch and validate fresh proxies"""
        logger.info("=" * 70)
        logger.info("PROXY REFRESH STARTED")
        logger.info("=" * 70)

        # Fetch proxies
        proxies = self.fetcher.fetch_all(limit=fetch_limit)

        if not proxies:
            logger.error("No proxies fetched!")
            return []

        # Validate proxies
        if validate_limit and validate_limit < len(proxies):
            logger.info(f"Limiting validation to {validate_limit} proxies")
            proxies = proxies[:validate_limit]

        working_proxies = self.validator.validate_batch(proxies)

        if working_proxies:
            self.save_proxies(working_proxies)

        logger.info("=" * 70)
        logger.info(f"PROXY REFRESH COMPLETE - {len(working_proxies)} working proxies")
        logger.info("=" * 70)

        return working_proxies

    def save_proxies(self, proxies: List[ProxyInfo]) -> None:
        """Save proxies to multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as JSON with metadata
        json_file = self.storage_dir / f"proxies_{timestamp}.json"
        json_data = [asdict(p) for p in proxies]
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"Saved {len(proxies)} proxies to {json_file}")

        # Save as simple text list (for easy loading)
        txt_file = self.storage_dir / f"proxies_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            for proxy in proxies:
                f.write(f"{proxy.address}\n")
        logger.info(f"Saved proxy list to {txt_file}")

        # Also save as 'latest' for easy reference
        latest_json = self.storage_dir / "proxies_latest.json"
        with open(latest_json, 'w') as f:
            json.dump(json_data, f, indent=2)

        latest_txt = self.storage_dir / "proxies_latest.txt"
        with open(latest_txt, 'w') as f:
            for proxy in proxies:
                f.write(f"{proxy.address}\n")

    def load_latest_proxies(self) -> List[str]:
        """Load the most recent proxy list"""
        latest_txt = self.storage_dir / "proxies_latest.txt"

        if not latest_txt.exists():
            logger.warning("No latest proxy file found")
            return []

        with open(latest_txt, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(proxies)} proxies from {latest_txt}")
        return proxies


def main():
    """CLI interface for proxy management"""
    import argparse

    parser = argparse.ArgumentParser(description='Proxy Manager - Fetch and validate free proxies')
    parser.add_argument('--fetch-limit', type=int, default=500,
                       help='Maximum proxies to fetch (default: 500)')
    parser.add_argument('--validate-limit', type=int, default=None,
                       help='Maximum proxies to validate (default: all fetched)')
    parser.add_argument('--storage-dir', type=str, default='./proxies',
                       help='Directory to store proxy lists (default: ./proxies)')
    parser.add_argument('--test', action='store_true',
                       help='Test existing proxies in storage directory')

    args = parser.parse_args()

    # Determine storage directory
    if not os.path.isabs(args.storage_dir):
        # Relative to backend directory
        backend_dir = Path(__file__).parent
        storage_dir = backend_dir / args.storage_dir
    else:
        storage_dir = Path(args.storage_dir)

    manager = ProxyManager(storage_dir)

    if args.test:
        # Test existing proxies
        proxies_list = manager.load_latest_proxies()
        if proxies_list:
            proxy_infos = [ProxyInfo(address=p) for p in proxies_list]
            working = manager.validator.validate_batch(proxy_infos)
            manager.save_proxies(working)
    else:
        # Fetch and validate new proxies
        manager.refresh_proxies(
            fetch_limit=args.fetch_limit,
            validate_limit=args.validate_limit
        )

    return 0


if __name__ == '__main__':
    sys.exit(main())
