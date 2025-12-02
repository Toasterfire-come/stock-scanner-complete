#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy Scraper - Scrapes proxies from multiple sources

Supports:
- Free proxy list websites
- API endpoints
- Text file lists
- Custom parsers per source
"""

import re
import requests
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ProxyScraper:
    """Scrape proxies from various sources"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_all(self, sources: List[Dict]) -> List[str]:
        """Scrape all sources concurrently"""

        logger.info(f"Scraping {len(sources)} proxy sources...")
        all_proxies = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self.scrape_source, source): source
                for source in sources
            }

            for future in as_completed(futures):
                source = futures[future]
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    logger.info(f"[{source['name']}] Found {len(proxies)} proxies")
                except Exception as e:
                    logger.error(f"[{source['name']}] Failed: {e}")

        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        logger.info(f"Total unique proxies: {len(unique_proxies)}")

        return unique_proxies

    def scrape_source(self, source: Dict) -> List[str]:
        """Scrape a single source"""

        source_type = source.get('type', 'html')

        if source_type == 'html':
            return self._scrape_html(source)
        elif source_type == 'api':
            return self._scrape_api(source)
        elif source_type == 'text':
            return self._scrape_text(source)
        else:
            logger.warning(f"Unknown source type: {source_type}")
            return []

    def _scrape_html(self, source: Dict) -> List[str]:
        """Scrape HTML page for proxies"""

        try:
            response = self.session.get(source['url'], timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            proxies = []

            # Try table parsing (most common)
            if 'table_selector' in source:
                table = soup.select_one(source['table_selector'])
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            proxy = f"http://{ip}:{port}"
                            proxies.append(proxy)

            # Try regex pattern matching
            elif 'pattern' in source:
                pattern = re.compile(source['pattern'])
                matches = pattern.findall(response.text)
                for match in matches:
                    if isinstance(match, tuple):
                        ip, port = match
                        proxy = f"http://{ip}:{port}"
                    else:
                        proxy = f"http://{match}"
                    proxies.append(proxy)

            # Try pre element (some sites use <pre> tags)
            else:
                pre_elements = soup.find_all('pre')
                for pre in pre_elements:
                    text = pre.text
                    # Match IP:PORT format
                    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
                    matches = re.findall(pattern, text)
                    for ip, port in matches:
                        proxy = f"http://{ip}:{port}"
                        proxies.append(proxy)

            return proxies

        except Exception as e:
            logger.debug(f"HTML scrape error for {source['url']}: {e}")
            return []

    def _scrape_api(self, source: Dict) -> List[str]:
        """Scrape API endpoint for proxies"""

        try:
            response = self.session.get(source['url'], timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            proxies = []

            # Handle different API formats
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        ip = item.get('ip') or item.get('host')
                        port = item.get('port')
                        if ip and port:
                            proxy = f"http://{ip}:{port}"
                            proxies.append(proxy)
                    elif isinstance(item, str):
                        if ':' in item:
                            proxy = f"http://{item}"
                            proxies.append(proxy)

            elif isinstance(data, dict):
                proxy_list = data.get('proxies', [])
                for item in proxy_list:
                    if isinstance(item, str):
                        proxy = f"http://{item}"
                        proxies.append(proxy)

            return proxies

        except Exception as e:
            logger.debug(f"API scrape error for {source['url']}: {e}")
            return []

    def _scrape_text(self, source: Dict) -> List[str]:
        """Scrape plain text list of proxies"""

        try:
            response = self.session.get(source['url'], timeout=self.timeout)
            response.raise_for_status()

            proxies = []
            lines = response.text.split('\n')

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Match IP:PORT format
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
                match = re.search(pattern, line)
                if match:
                    ip, port = match.groups()
                    proxy = f"http://{ip}:{port}"
                    proxies.append(proxy)

            return proxies

        except Exception as e:
            logger.debug(f"Text scrape error for {source['url']}: {e}")
            return []


# Default proxy sources (you can add more)
DEFAULT_PROXY_SOURCES = [
    {
        'name': 'Free Proxy List',
        'url': 'https://free-proxy-list.net/',
        'type': 'html',
        'table_selector': 'table.table'
    },
    {
        'name': 'ProxyScrape',
        'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'type': 'text'
    },
    {
        'name': 'Geonode',
        'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
        'type': 'api'
    },
    {
        'name': 'ProxyList Download',
        'url': 'https://www.proxy-list.download/api/v1/get?type=http',
        'type': 'text'
    },
]


def scrape_proxies_from_sources(sources: List[Dict] = None) -> List[str]:
    """
    Scrape proxies from specified sources

    Args:
        sources: List of source configs, or None to use defaults

    Returns:
        List of proxy URLs
    """

    if sources is None:
        sources = DEFAULT_PROXY_SOURCES

    scraper = ProxyScraper()
    proxies = scraper.scrape_all(sources)

    return proxies


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("="*70)
    print("PROXY SCRAPER TEST")
    print("="*70)

    proxies = scrape_proxies_from_sources()

    print(f"\nScraped {len(proxies)} total proxies")
    print(f"\nFirst 10 proxies:")
    for proxy in proxies[:10]:
        print(f"  {proxy}")
