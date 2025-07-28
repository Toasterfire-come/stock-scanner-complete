#!/usr/bin/env python3
"""
Fast Proxy Finder
Quickly finds working proxies from reliable sources
"""

import requests
import time
import random
import threading
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

class FastProxyFinder:
    def __init__(self, timeout=5, max_workers=50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.working_proxies = []
        self.lock = threading.Lock()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def get_fast_proxy_sources(self):
        """Get fast, reliable proxy sources"""
        return [
            # Fast proxy APIs
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all&format=json",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps&anonymityLevel=elite&anonymityLevel=anonymous",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            # Additional fast sources
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        ]
    
    def fetch_proxies_fast(self, source):
        """Fetch proxies from a single source with timeout"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text.strip()
                proxies = []
                
                # Handle JSON responses
                if source.endswith('format=json'):
                    try:
                        data = response.json()
                        if 'proxies' in data:
                            for proxy in data['proxies']:
                                if 'ip' in proxy and 'port' in proxy:
                                    proxies.append(f"http://{proxy['ip']}:{proxy['port']}")
                    except:
                        pass
                
                # Handle text responses
                for line in content.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle different proxy formats
                    if ':' in line:
                        if line.count(':') == 1:  # ip:port
                            proxies.append(f"http://{line}")
                        elif line.count(':') == 2:  # ip:port:protocol
                            parts = line.split(':')
                            if parts[2].lower() in ['http', 'https']:
                                proxies.append(f"{parts[2]}://{parts[0]}:{parts[1]}")
                
                return proxies
        except Exception as e:
            self.logger.debug(f"Failed to fetch from {source}: {e}")
        
        return []
    
    def test_proxy_fast(self, proxy):
        """Test proxy with fast timeout and multiple quick tests"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            # Quick test URLs
            test_urls = [
                'http://httpbin.org/ip',
                'https://httpbin.org/ip',
                'http://ip-api.com/json',
                'https://api.ipify.org?format=json'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(
                        url, 
                        proxies=proxies, 
                        timeout=self.timeout,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def find_working_proxies_fast(self, target_count=100):
        """Find working proxies quickly with optimized methods"""
        self.logger.info(f"FAST PROXY FINDER: Target {target_count} working proxies")
        
        # Fetch from all sources concurrently
        all_proxies = set()
        sources = self.get_fast_proxy_sources()
        
        self.logger.info(f"Fetching from {len(sources)} sources...")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_source = {executor.submit(self.fetch_proxies_fast, source): source for source in sources}
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    proxies = future.result()
                    all_proxies.update(proxies)
                    self.logger.info(f"Fetched {len(proxies)} proxies from {source}")
                except Exception as e:
                    self.logger.debug(f"Failed to fetch from {source}: {e}")
        
        self.logger.info(f"TOTAL: {len(all_proxies)} unique proxies found")
        
        # Test proxies with high concurrency
        working_proxies = []
        proxy_list = list(all_proxies)
        
        # Shuffle to randomize testing order
        random.shuffle(proxy_list)
        
        self.logger.info(f"Testing {len(proxy_list)} proxies with {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {executor.submit(self.test_proxy_fast, proxy): proxy for proxy in proxy_list}
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        with self.lock:
                            working_proxies.append(proxy)
                            self.logger.info(f"WORKING: {proxy} ({len(working_proxies)}/{target_count})")
                            
                            if len(working_proxies) >= target_count:
                                self.logger.info(f"REACHED TARGET: {target_count} working proxies")
                                break
                except Exception as e:
                    self.logger.debug(f"Failed proxy: {proxy}")
        
        return working_proxies
    
    def save_proxies(self, proxies, filename="fast_working_proxies.json"):
        """Save working proxies to file"""
        try:
            data = {
                'proxies': proxies,
                'timestamp': datetime.now().isoformat(),
                'count': len(proxies)
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"SAVED {len(proxies)} proxies to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save proxies: {e}")
    
    def load_proxies(self, filename="fast_working_proxies.json"):
        """Load working proxies from file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                proxies = data.get('proxies', [])
                self.logger.info(f"LOADED {len(proxies)} proxies from {filename}")
                return proxies
                
        except Exception as e:
            self.logger.error(f"Failed to load proxies: {e}")
        
        return []

def main():
    """Test the fast proxy finder"""
    print("FAST PROXY FINDER")
    print("=" * 50)
    
    finder = FastProxyFinder(timeout=3, max_workers=100)
    
    # Try to load existing proxies first
    existing_proxies = finder.load_proxies()
    if existing_proxies:
        print(f"Found {len(existing_proxies)} existing proxies")
        
        # Quick validation of existing proxies
        print("Validating existing proxies...")
        valid_proxies = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_proxy = {executor.submit(finder.test_proxy_fast, proxy): proxy for proxy in existing_proxies}
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                if future.result():
                    valid_proxies.append(proxy)
        
        print(f"Validated {len(valid_proxies)} existing proxies")
        
        if len(valid_proxies) >= 50:
            print("SUFFICIENT existing proxies found!")
            finder.save_proxies(valid_proxies)
            return
    
    # Find new proxies
    print("Finding new working proxies...")
    start_time = time.time()
    
    working_proxies = finder.find_working_proxies_fast(target_count=100)
    
    elapsed = time.time() - start_time
    print(f"FOUND {len(working_proxies)} working proxies in {elapsed:.1f} seconds")
    
    # Save results
    finder.save_proxies(working_proxies)
    
    print("FAST PROXY FINDER COMPLETED!")
    print(f"Working proxies: {len(working_proxies)}")
    print(f"Time taken: {elapsed:.1f} seconds")

if __name__ == "__main__":
    main()