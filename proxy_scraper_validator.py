#!/usr/bin/env python3
"""
Proxy Scraper and Validator
Scrapes proxies from multiple sources and validates them
Uses similar methods to enhanced_stock_retrieval_working.py
"""

import os
import sys
import time
import json
import argparse
import requests
import logging
import signal
import threading
import random
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import schedule
import subprocess
from logging.handlers import RotatingFileHandler

# Setup logging with rotation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'proxy_scraper_validator.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False

# Global flag for graceful shutdown
shutdown_flag = False

# Proxy validation tracking with thread safety
proxy_validation_results = defaultdict(lambda: {"successes": 0, "failures": 0, "last_check": None, "response_time": None})
proxy_validation_lock = threading.Lock()

# Test URLs for validation
TEST_URLS = [
    "http://httpbin.org/ip",
    "http://ipinfo.io/json",
    "http://api.ipify.org?format=json",
    "https://www.google.com",
    "https://www.yahoo.com"
]

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    logger.info("Received interrupt signal. Shutting down gracefully...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Proxy Scraper and Validator')
    parser.add_argument('-threads', type=int, default=50, help='Number of threads for validation (default: 50)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-output', type=str, default='working_proxies.json', help='Output file for working proxies')
    parser.add_argument('-all-output', type=str, default='all_scraped_proxies.json', help='Output file for all scraped proxies')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 30 minutes)')
    parser.add_argument('-validate-only', type=str, help='Validate proxies from existing file')
    parser.add_argument('-scrape-only', action='store_true', help='Only scrape proxies without validation')
    parser.add_argument('-min-success-rate', type=float, default=0.6, help='Minimum success rate for proxy (default: 0.6)')
    parser.add_argument('-max-response-time', type=float, default=5.0, help='Maximum response time in seconds (default: 5.0)')
    parser.add_argument('-github-repos', action='store_true', help='Include GitHub repository scraping')
    return parser.parse_args()

def normalize_proxy_string(proxy_str: str) -> Optional[str]:
    """Normalize and validate proxy string format"""
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    
    p = proxy_str.strip()
    if not p:
        return None
    
    # Remove any whitespace and common separators
    p = re.sub(r'\s+', '', p)
    
    # Check if it's a valid IP:PORT format
    ip_port_pattern = r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    if re.match(ip_port_pattern, p):
        # Add http:// prefix if not present
        return f"http://{p}"
    
    # Check if it already has a scheme
    if '://' in p:
        # Validate the URL format
        try:
            parsed = urlparse(p)
            if parsed.scheme in ['http', 'https', 'socks4', 'socks5'] and parsed.netloc:
                return p
        except:
            pass
    
    return None

def extract_proxies_from_text(text: str) -> Set[str]:
    """Extract proxy addresses from text using regex patterns"""
    proxies = set()
    
    # Pattern for IP:PORT
    ip_port_pattern = r'\b(\d{1,3}\.){3}\d{1,3}:\d{1,5}\b'
    matches = re.findall(ip_port_pattern, text)
    
    for match in matches:
        proxy = normalize_proxy_string(match)
        if proxy:
            proxies.add(proxy)
    
    return proxies

def scrape_free_proxy_list() -> List[str]:
    """Scrape proxies from free-proxy-list.net"""
    proxies = []
    try:
        logger.info("Scraping free-proxy-list.net...")
        url = "https://free-proxy-list.net/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the proxy table
        table = soup.find('table', {'class': 'table-striped'})
        if not table:
            table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    if ip and port:
                        proxy = normalize_proxy_string(f"{ip}:{port}")
                        if proxy:
                            proxies.append(proxy)
        
        # Also extract from any script tags that might contain proxy data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                extracted = extract_proxies_from_text(script.string)
                for proxy in extracted:
                    if proxy not in proxies:
                        proxies.append(proxy)
        
        logger.info(f"Scraped {len(proxies)} proxies from free-proxy-list.net")
    except Exception as e:
        logger.error(f"Error scraping free-proxy-list.net: {e}")
    
    return proxies

def scrape_spys_one() -> List[str]:
    """Scrape proxies from spys.one"""
    proxies = []
    try:
        logger.info("Scraping spys.one...")
        urls = [
            "https://spys.one/en/free-proxy-list/",
            "https://spys.one/en/anonymous-proxy-list/",
            "https://spys.one/en/https-ssl-proxy/"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Extract proxies from the page
                extracted = extract_proxies_from_text(response.text)
                
                # Also parse HTML for structured data
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for proxy data in various formats
                for tag in soup.find_all(['tr', 'div', 'span']):
                    text = tag.get_text()
                    if ':' in text and '.' in text:
                        extracted.update(extract_proxies_from_text(text))
                
                for proxy in extracted:
                    if proxy not in proxies:
                        proxies.append(proxy)
                
                time.sleep(1)  # Be respectful
            except Exception as e:
                logger.warning(f"Error scraping {url}: {e}")
        
        logger.info(f"Scraped {len(proxies)} proxies from spys.one")
    except Exception as e:
        logger.error(f"Error scraping spys.one: {e}")
    
    return proxies

def scrape_proxyscrape() -> List[str]:
    """Scrape proxies from ProxyScrape API"""
    proxies = []
    try:
        logger.info("Scraping ProxyScrape...")
        
        # ProxyScrape provides direct API endpoints
        api_urls = [
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&format=textplain",
            "https://api.proxyscrape.com/v2/?request=get&protocol=https&timeout=10000&country=all&ssl=yes&anonymity=all&format=textplain",
            "https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=10000&country=all&format=textplain",
            "https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all&format=textplain"
        ]
        
        for url in api_urls:
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                lines = response.text.strip().split('\n')
                for line in lines:
                    proxy = normalize_proxy_string(line.strip())
                    if proxy and proxy not in proxies:
                        proxies.append(proxy)
                
                time.sleep(1)  # Be respectful
            except Exception as e:
                logger.warning(f"Error fetching from ProxyScrape API: {e}")
        
        logger.info(f"Scraped {len(proxies)} proxies from ProxyScrape")
    except Exception as e:
        logger.error(f"Error scraping ProxyScrape: {e}")
    
    return proxies

def scrape_geonode() -> List[str]:
    """Scrape proxies from Geonode"""
    proxies = []
    try:
        logger.info("Scraping Geonode...")
        
        # Geonode API endpoints
        api_urls = [
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=speed&sort_type=asc"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for url in api_urls:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        ip = item.get('ip')
                        port = item.get('port')
                        if ip and port:
                            proxy = normalize_proxy_string(f"{ip}:{port}")
                            if proxy and proxy not in proxies:
                                proxies.append(proxy)
                
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error fetching from Geonode API: {e}")
        
        logger.info(f"Scraped {len(proxies)} proxies from Geonode")
    except Exception as e:
        logger.error(f"Error scraping Geonode: {e}")
    
    return proxies

def scrape_proxynova() -> List[str]:
    """Scrape proxies from ProxyNova"""
    proxies = []
    try:
        logger.info("Scraping ProxyNova...")
        
        base_url = "https://www.proxynova.com"
        countries = ['us', 'uk', 'ca', 'fr', 'de', 'nl', 'jp', 'cn', 'in', 'br']
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for country in countries[:5]:  # Limit to avoid too many requests
            try:
                url = f"{base_url}/proxy-server-list/country-{country}/"
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find proxy table
                table = soup.find('table', {'id': 'tbl_proxy_list'})
                if not table:
                    table = soup.find('table')
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            # ProxyNova often obfuscates IPs with JavaScript
                            ip_elem = cols[0]
                            port_elem = cols[1]
                            
                            # Try to extract IP (might be obfuscated)
                            ip_text = ip_elem.get_text().strip()
                            port_text = port_elem.get_text().strip()
                            
                            # Also check for any script tags that might contain the real IP
                            script = ip_elem.find('script')
                            if script and script.string:
                                # Try to extract IP from JavaScript
                                ip_match = re.search(r'(\d{1,3}\.){3}\d{1,3}', script.string)
                                if ip_match:
                                    ip_text = ip_match.group()
                            
                            if ip_text and port_text and '.' in ip_text:
                                proxy = normalize_proxy_string(f"{ip_text}:{port_text}")
                                if proxy and proxy not in proxies:
                                    proxies.append(proxy)
                
                time.sleep(2)  # Be respectful
            except Exception as e:
                logger.warning(f"Error scraping ProxyNova {country}: {e}")
        
        logger.info(f"Scraped {len(proxies)} proxies from ProxyNova")
    except Exception as e:
        logger.error(f"Error scraping ProxyNova: {e}")
    
    return proxies

def scrape_github_repos() -> List[str]:
    """Scrape proxy lists from GitHub repositories"""
    proxies = []
    try:
        logger.info("Scraping GitHub repositories...")
        
        # Popular proxy list repositories
        github_urls = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for url in github_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                lines = response.text.strip().split('\n')
                for line in lines:
                    proxy = normalize_proxy_string(line.strip())
                    if proxy and proxy not in proxies:
                        # Determine protocol from URL if not specified
                        if 'socks4' in url.lower() and not proxy.startswith('socks'):
                            proxy = proxy.replace('http://', 'socks4://')
                        elif 'socks5' in url.lower() and not proxy.startswith('socks'):
                            proxy = proxy.replace('http://', 'socks5://')
                        
                        proxies.append(proxy)
                
                time.sleep(0.5)  # Be respectful to GitHub
            except Exception as e:
                logger.warning(f"Error fetching from GitHub: {url} - {e}")
        
        logger.info(f"Scraped {len(proxies)} proxies from GitHub repositories")
    except Exception as e:
        logger.error(f"Error scraping GitHub: {e}")
    
    return proxies

def validate_proxy(proxy: str, timeout: int = 10) -> Tuple[bool, float]:
    """Validate a single proxy by testing it against test URLs"""
    if shutdown_flag:
        return False, 0
    
    # Parse proxy format
    proxy_dict = {
        'http': proxy,
        'https': proxy
    }
    
    # Try multiple test URLs
    for test_url in TEST_URLS[:3]:  # Test with first 3 URLs
        try:
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxy_dict,
                timeout=timeout,
                verify=False,
                allow_redirects=False
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 301, 302]:
                return True, response_time
                
        except Exception as e:
            continue
    
    return False, 0

def validate_proxy_batch(proxy: str, timeout: int, max_response_time: float) -> Optional[Dict]:
    """Validate a proxy and return its details if successful"""
    try:
        is_valid, response_time = validate_proxy(proxy, timeout)
        
        if is_valid and response_time <= max_response_time:
            with proxy_validation_lock:
                proxy_validation_results[proxy]["successes"] += 1
                proxy_validation_results[proxy]["response_time"] = response_time
                proxy_validation_results[proxy]["last_check"] = datetime.now().isoformat()
            
            return {
                "proxy": proxy,
                "response_time": response_time,
                "last_validated": datetime.now().isoformat(),
                "success_rate": 1.0
            }
        else:
            with proxy_validation_lock:
                proxy_validation_results[proxy]["failures"] += 1
            return None
            
    except Exception as e:
        logger.debug(f"Error validating {proxy}: {e}")
        with proxy_validation_lock:
            proxy_validation_results[proxy]["failures"] += 1
        return None

def deduplicate_proxies(proxies: List[str]) -> List[str]:
    """Remove duplicate proxies while preserving order"""
    seen = set()
    unique = []
    for proxy in proxies:
        if proxy not in seen:
            seen.add(proxy)
            unique.append(proxy)
    return unique

def scrape_all_sources(include_github: bool = False) -> List[str]:
    """Scrape proxies from all configured sources"""
    all_proxies = []
    
    # Scrape from each source
    sources = [
        ("Free-Proxy-List", scrape_free_proxy_list),
        ("Spys.one", scrape_spys_one),
        ("ProxyScrape", scrape_proxyscrape),
        ("Geonode", scrape_geonode),
        ("ProxyNova", scrape_proxynova)
    ]
    
    if include_github:
        sources.append(("GitHub Repos", scrape_github_repos))
    
    for source_name, scraper_func in sources:
        try:
            logger.info(f"Scraping from {source_name}...")
            proxies = scraper_func()
            all_proxies.extend(proxies)
            logger.info(f"Total proxies so far: {len(all_proxies)}")
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
    
    # Deduplicate
    unique_proxies = deduplicate_proxies(all_proxies)
    logger.info(f"Total unique proxies scraped: {len(unique_proxies)}")
    
    return unique_proxies

def validate_proxies(proxies: List[str], args) -> List[Dict]:
    """Validate a list of proxies using thread pool"""
    logger.info(f"Starting validation of {len(proxies)} proxies...")
    logger.info(f"Using {args.threads} threads, timeout: {args.timeout}s, max response time: {args.max_response_time}s")
    
    working_proxies = []
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_proxy = {}
        
        for proxy in proxies:
            if shutdown_flag:
                break
            future = executor.submit(validate_proxy_batch, proxy, args.timeout, args.max_response_time)
            future_to_proxy[future] = proxy
        
        completed = 0
        for future in as_completed(future_to_proxy):
            if shutdown_flag:
                break
            
            proxy = future_to_proxy[future]
            completed += 1
            
            try:
                result = future.result(timeout=args.timeout + 2)
                if result:
                    working_proxies.append(result)
                    logger.info(f"[{completed}/{len(proxies)}] WORKING: {proxy} (Response: {result['response_time']:.2f}s)")
                else:
                    logger.debug(f"[{completed}/{len(proxies)}] FAILED: {proxy}")
            except TimeoutError:
                logger.debug(f"[{completed}/{len(proxies)}] TIMEOUT: {proxy}")
            except Exception as e:
                logger.debug(f"[{completed}/{len(proxies)}] ERROR: {proxy} - {e}")
            
            # Progress update
            if completed % 50 == 0 or completed == len(proxies):
                success_rate = (len(working_proxies) / completed) * 100 if completed > 0 else 0
                logger.info(f"Progress: {completed}/{len(proxies)} validated, {len(working_proxies)} working ({success_rate:.1f}% success rate)")
    
    # Sort by response time
    working_proxies.sort(key=lambda x: x['response_time'])
    
    return working_proxies

def save_proxies(proxies: List, filename: str, format: str = "list"):
    """Save proxies to file in specified format"""
    try:
        if format == "list":
            # Save as simple list
            proxy_list = [p['proxy'] if isinstance(p, dict) else p for p in proxies]
            with open(filename, 'w') as f:
                json.dump(proxy_list, f, indent=2)
        else:
            # Save with full details
            with open(filename, 'w') as f:
                json.dump(proxies, f, indent=2)
        
        logger.info(f"Saved {len(proxies)} proxies to {filename}")
    except Exception as e:
        logger.error(f"Error saving proxies to {filename}: {e}")

def load_proxies_from_file(filename: str) -> List[str]:
    """Load proxies from a JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        proxies = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    proxy = normalize_proxy_string(item)
                    if proxy:
                        proxies.append(proxy)
                elif isinstance(item, dict) and 'proxy' in item:
                    proxy = normalize_proxy_string(item['proxy'])
                    if proxy:
                        proxies.append(proxy)
        
        logger.info(f"Loaded {len(proxies)} proxies from {filename}")
        return proxies
    except Exception as e:
        logger.error(f"Error loading proxies from {filename}: {e}")
        return []

def run_proxy_update(args):
    """Run a single proxy update cycle"""
    global shutdown_flag
    
    logger.info("="*60)
    logger.info(f"PROXY UPDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    # Scrape or load proxies
    if args.validate_only:
        logger.info(f"Loading proxies from {args.validate_only}...")
        all_proxies = load_proxies_from_file(args.validate_only)
    else:
        logger.info("Scraping proxies from all sources...")
        all_proxies = scrape_all_sources(include_github=args.github_repos)
        
        # Save all scraped proxies
        save_proxies(all_proxies, args.all_output, format="list")
    
    if not all_proxies:
        logger.error("No proxies to process")
        return
    
    # Validate proxies if not in scrape-only mode
    if not args.scrape_only:
        working_proxies = validate_proxies(all_proxies, args)
        
        # Save working proxies
        save_proxies(working_proxies, args.output, format="detailed")
        
        # Also save simple list for compatibility with stock scraper
        simple_list = [p['proxy'] for p in working_proxies]
        save_proxies(simple_list, args.output.replace('.json', '_simple.json'), format="list")
        
        # Summary
        logger.info("="*60)
        logger.info("VALIDATION RESULTS")
        logger.info("="*60)
        logger.info(f"Total Scraped: {len(all_proxies)}")
        logger.info(f"Working: {len(working_proxies)}")
        if len(all_proxies) > 0:
            logger.info(f"Success Rate: {(len(working_proxies)/len(all_proxies)*100):.1f}%")
        
        if working_proxies:
            avg_response_time = sum(p['response_time'] for p in working_proxies) / len(working_proxies)
            logger.info(f"Average Response Time: {avg_response_time:.2f}s")
            logger.info(f"Fastest Proxy: {working_proxies[0]['proxy']} ({working_proxies[0]['response_time']:.2f}s)")
    else:
        logger.info(f"Scrape-only mode: Saved {len(all_proxies)} proxies without validation")
    
    logger.info("="*60)

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    logger.info("PROXY SCRAPER AND VALIDATOR")
    logger.info("="*60)
    logger.info(f"Configuration:")
    logger.info(f"  Threads: {args.threads}")
    logger.info(f"  Timeout: {args.timeout}s")
    logger.info(f"  Max Response Time: {args.max_response_time}s")
    logger.info(f"  Min Success Rate: {args.min_success_rate}")
    logger.info(f"  Output File: {args.output}")
    logger.info(f"  All Proxies File: {args.all_output}")
    logger.info(f"  Include GitHub: {args.github_repos}")
    logger.info(f"  Schedule Mode: {args.schedule}")
    logger.info(f"  Validate Only: {args.validate_only}")
    logger.info(f"  Scrape Only: {args.scrape_only}")
    logger.info("="*60)
    
    if args.schedule:
        logger.info("SCHEDULER MODE: Running proxy update every 30 minutes")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.info("="*60)
        
        # Immediate run
        run_proxy_update(args)
        
        # Schedule subsequent runs
        schedule.every(30).minutes.do(run_proxy_update, args)
        
        try:
            while not shutdown_flag:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update
        run_proxy_update(args)
    
    logger.info("Script completed!")

if __name__ == "__main__":
    main()