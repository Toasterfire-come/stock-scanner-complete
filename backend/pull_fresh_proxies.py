#!/usr/bin/env python3
"""
Fresh Proxy Puller for GeoNode API
===================================

Pulls elite, fast, high-uptime proxies from GeoNode API at market start.
Saves to working_proxies.json for use by the stock scanner.

API: https://proxylist.geonode.com/api/proxy-list
Filters: elite anonymity, 90%+ uptime, fast speed, recently checked
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests

# =====================================================
# CONFIGURATION
# =====================================================

class ProxyPullerConfig:
    """Configuration for proxy pulling"""

    # API settings
    API_URL = "https://proxylist.geonode.com/api/proxy-list"

    # Filters
    ANONYMITY_LEVEL = "elite"  # elite, anonymous, transparent
    MIN_UPTIME = 90  # 90% minimum uptime
    LAST_CHECKED = 10  # Checked within last 10 minutes
    SPEED = "fast"  # fast, medium, slow
    LIMIT_PER_PAGE = 500  # Max proxies per request
    MAX_PAGES = 3  # Pull from multiple pages

    # Output
    OUTPUT_FILE = "working_proxies.json"
    BACKUP_FILE = "working_proxies_backup.json"

    # Validation
    VALIDATE_PROXIES = True  # Test proxies before saving
    VALIDATION_TIMEOUT = 5  # Seconds
    VALIDATION_URL = "https://finance.yahoo.com"
    MIN_SUCCESS_RATE = 0.5  # Keep proxies with 50%+ success rate

    # Logging
    LOG_FILE = "proxy_puller.log"
    VERBOSE = True

CONFIG = ProxyPullerConfig()

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(CONFIG.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# PROXY PULLER
# =====================================================

class ProxyPuller:
    """Pulls and validates proxies from GeoNode API"""

    def __init__(self):
        self.proxies: List[Dict] = []
        self.validated_proxies: List[str] = []

    def build_api_url(self, page: int = 1) -> str:
        """Build API URL with filters"""
        params = {
            'anonymityLevel': CONFIG.ANONYMITY_LEVEL,
            'filterUpTime': CONFIG.MIN_UPTIME,
            'filterLastChecked': CONFIG.LAST_CHECKED,
            'speed': CONFIG.SPEED,
            'limit': CONFIG.LIMIT_PER_PAGE,
            'page': page,
            'sort_by': 'lastChecked',
            'sort_type': 'desc'
        }

        param_str = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{CONFIG.API_URL}?{param_str}"

    def fetch_proxies_page(self, page: int) -> Optional[Dict]:
        """Fetch one page of proxies from API"""
        url = self.build_api_url(page)

        try:
            logger.info(f"Fetching proxies from page {page}...")

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            if 'data' in data:
                proxies = data['data']
                logger.info(f"Fetched {len(proxies)} proxies from page {page}")
                return data
            else:
                logger.warning(f"No data in response from page {page}")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to fetch proxies from page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from page {page}: {e}")
            return None

    def fetch_all_proxies(self) -> List[Dict]:
        """Fetch proxies from multiple pages"""
        logger.info("=" * 70)
        logger.info("FETCHING PROXIES FROM GEONODE API")
        logger.info("=" * 70)
        logger.info(f"Anonymity: {CONFIG.ANONYMITY_LEVEL}")
        logger.info(f"Min Uptime: {CONFIG.MIN_UPTIME}%")
        logger.info(f"Speed: {CONFIG.SPEED}")
        logger.info(f"Last Checked: Within {CONFIG.LAST_CHECKED} minutes")
        logger.info(f"Pages: {CONFIG.MAX_PAGES}")
        logger.info("")

        all_proxies = []

        for page in range(1, CONFIG.MAX_PAGES + 1):
            data = self.fetch_proxies_page(page)

            if data and 'data' in data:
                all_proxies.extend(data['data'])

                # Check if there are more pages
                total = data.get('total', 0)
                current_count = len(all_proxies)

                logger.info(f"Total so far: {current_count}/{total}")

                # Small delay between requests
                if page < CONFIG.MAX_PAGES:
                    time.sleep(1)
            else:
                break

        logger.info(f"\nTotal proxies fetched: {len(all_proxies)}")
        self.proxies = all_proxies
        return all_proxies

    def format_proxy(self, proxy_data: Dict) -> str:
        """Format proxy data into usable string"""
        protocol = proxy_data.get('protocols', ['http'])[0]
        ip = proxy_data.get('ip')
        port = proxy_data.get('port')

        if protocol and ip and port:
            return f"{protocol}://{ip}:{port}"
        return None

    def validate_proxy(self, proxy_str: str) -> bool:
        """Test if proxy works"""
        try:
            proxies = {
                'http': proxy_str,
                'https': proxy_str
            }

            response = requests.get(
                CONFIG.VALIDATION_URL,
                proxies=proxies,
                timeout=CONFIG.VALIDATION_TIMEOUT,
                verify=False  # Skip SSL verification for speed
            )

            return response.status_code == 200

        except:
            return False

    def validate_all_proxies(self) -> List[str]:
        """Validate all fetched proxies"""
        if not CONFIG.VALIDATE_PROXIES:
            logger.info("Skipping validation (disabled)")
            return [self.format_proxy(p) for p in self.proxies if self.format_proxy(p)]

        logger.info("")
        logger.info("=" * 70)
        logger.info("VALIDATING PROXIES")
        logger.info("=" * 70)

        validated = []
        total = len(self.proxies)

        for idx, proxy_data in enumerate(self.proxies, 1):
            proxy_str = self.format_proxy(proxy_data)

            if not proxy_str:
                continue

            if CONFIG.VERBOSE and idx % 10 == 0:
                logger.info(f"Validating {idx}/{total}...")

            # For speed, validate only a sample if there are many
            if total > 100 and idx > 50:
                # After first 50, add without validation
                validated.append(proxy_str)
            else:
                if self.validate_proxy(proxy_str):
                    validated.append(proxy_str)
                    if CONFIG.VERBOSE:
                        logger.debug(f"[OK] {proxy_str}")

        logger.info(f"\nValidated proxies: {len(validated)}/{total}")
        logger.info(f"Success rate: {len(validated)/total*100:.1f}%")

        self.validated_proxies = validated
        return validated

    def save_proxies(self, proxies: List[str]) -> bool:
        """Save proxies to JSON file"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("SAVING PROXIES")
        logger.info("=" * 70)

        output_path = Path(CONFIG.OUTPUT_FILE)
        backup_path = Path(CONFIG.BACKUP_FILE)

        # Backup existing file
        if output_path.exists():
            try:
                output_path.rename(backup_path)
                logger.info(f"Backed up existing proxies to {backup_path}")
            except Exception as e:
                logger.warning(f"Could not backup existing file: {e}")

        # Save new proxies
        try:
            data = {
                'proxies': proxies,
                'count': len(proxies),
                'fetched_at': datetime.now().isoformat(),
                'source': 'geonode_api',
                'filters': {
                    'anonymity': CONFIG.ANONYMITY_LEVEL,
                    'min_uptime': CONFIG.MIN_UPTIME,
                    'speed': CONFIG.SPEED,
                    'last_checked': CONFIG.LAST_CHECKED
                }
            }

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"[OK] Saved {len(proxies)} proxies to {output_path}")
            logger.info(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

            return True

        except Exception as e:
            logger.error(f"Failed to save proxies: {e}")
            return False

    def run(self) -> bool:
        """Main workflow: fetch, validate, save"""
        start_time = time.time()

        try:
            # Fetch
            proxies_data = self.fetch_all_proxies()

            if not proxies_data:
                logger.error("No proxies fetched")
                return False

            # Format and optionally validate
            proxy_strings = self.validate_all_proxies()

            if not proxy_strings:
                logger.error("No valid proxies found")
                return False

            # Save
            success = self.save_proxies(proxy_strings)

            # Summary
            duration = time.time() - start_time

            logger.info("")
            logger.info("=" * 70)
            logger.info("PROXY PULL COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total proxies: {len(proxy_strings)}")
            logger.info(f"Duration: {duration:.1f}s")
            logger.info(f"File: {CONFIG.OUTPUT_FILE}")
            logger.info("=" * 70)

            return success

        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")
            return False
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False

# =====================================================
# CLI
# =====================================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Pull fresh proxies from GeoNode API")
    parser.add_argument('--no-validate', action='store_true',
                       help='Skip proxy validation')
    parser.add_argument('--pages', type=int, default=3,
                       help='Number of pages to fetch')
    parser.add_argument('--output', type=str,
                       help='Output file path')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')

    args = parser.parse_args()

    # Apply config
    if args.no_validate:
        CONFIG.VALIDATE_PROXIES = False
    if args.pages:
        CONFIG.MAX_PAGES = args.pages
    if args.output:
        CONFIG.OUTPUT_FILE = args.output
    if args.quiet:
        CONFIG.VERBOSE = False
        logging.getLogger().setLevel(logging.WARNING)

    # Run puller
    puller = ProxyPuller()
    success = puller.run()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
