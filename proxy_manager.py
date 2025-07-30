#!/usr/bin/env python3
"""
Advanced Proxy Manager for Stock Scanner
Finds, tests, and manages a pool of working proxies
Ensures no proxy is reused during a single run
"""

import requests
import time
import random
import threading
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
from fast_proxy_finder import FastProxyFinder

class ProxyManager:
    def __init__(self, min_proxies=100, max_proxies=200, test_timeout=5):
        self.min_proxies = min_proxies
        self.max_proxies = max_proxies
        self.test_timeout = test_timeout
        self.working_proxies = []
        self.used_proxies = set()  # Track used proxies in current run
        self.lock = threading.Lock()
        self.proxy_file = Path("working_proxies.json")
        self.last_refresh = None
        self.refresh_interval = timedelta(hours=6)  # Refresh every 6 hours
        self.switch_interval = 200  # Switch proxy every 200 tickers
        self.current_proxy = None
        self.ticker_count = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load existing proxies and ensure we have enough
        self.load_proxies()
        self.ensure_sufficient_proxies()
        
    def ensure_sufficient_proxies(self):
        """Ensure we have enough working proxies"""
        if len(self.working_proxies) < self.min_proxies:
            self.logger.info(f"NEED MORE PROXIES: Current: {len(self.working_proxies)}, Required: {self.min_proxies}")
            self.refresh_proxy_pool(force=True)
        
        if len(self.working_proxies) == 0:
            self.logger.warning("WARNING: No working proxies found. Will run without proxies.")
        else:
            self.logger.info(f"READY: {len(self.working_proxies)} working proxies available")
    
    def get_proxy_sources(self):
        """Get list of proxy sources"""
        return [
            # Free proxy APIs
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
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
        ]
    
    def fetch_proxies_from_source(self, source):
        """Fetch proxies from a single source"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(source, headers=headers, timeout=30)
            if response.status_code == 200:
                content = response.text.strip()
                proxies = []
                
                # Parse different formats
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
            self.logger.warning(f"Failed to fetch from {source}: {e}")
        
        return []
    
    def test_proxy(self, proxy):
        """Test if a proxy is working by making a request to Yahoo Finance"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            # Use a Yahoo Finance endpoint for AAPL summary (public, no auth required)
            yfinance_url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=price'
            response = requests.get(
                yfinance_url,
                proxies=proxies,
                timeout=self.test_timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.Timeout:
            self.logger.debug(f"Proxy {proxy} timed out")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.debug(f"Proxy {proxy} connection error")
            return False
        except Exception as e:
            self.logger.debug(f"Proxy {proxy} error: {e}")
            return False
    
    def find_working_proxies(self, target_count=None):
        """Find working proxies using fast proxy finder"""
        if target_count is None:
            target_count = self.min_proxies
            
        self.logger.info(f"FINDING {target_count} working proxies using fast finder...")
        
        # Use fast proxy finder
        fast_finder = FastProxyFinder(timeout=5, max_workers=100)
        working_proxies = fast_finder.find_working_proxies_fast(target_count)
        
        self.logger.info(f"FAST FINDER: Found {len(working_proxies)} working proxies")
        return working_proxies
    
    def refresh_proxy_pool(self, force=False):
        """Refresh the proxy pool if needed"""
        with self.lock:
            current_time = datetime.now()
            
            # Check if refresh is needed
            if (force or 
                len(self.working_proxies) < self.min_proxies or
                self.last_refresh is None or
                current_time - self.last_refresh > self.refresh_interval):
                
                self.logger.info("REFRESHING proxy pool...")
                
                # Find new working proxies
                new_proxies = self.find_working_proxies(self.max_proxies)
                
                # Combine with existing proxies (remove duplicates)
                existing_proxies = set(self.working_proxies)
                new_proxies_set = set(new_proxies)
                
                # Keep existing proxies that are still working
                combined_proxies = list(existing_proxies.union(new_proxies_set))
                
                # Shuffle to randomize order
                random.shuffle(combined_proxies)
                
                self.working_proxies = combined_proxies
                self.last_refresh = current_time
                
                # Save to file
                self.save_proxies()
                
                self.logger.info(f"SUCCESS: Proxy pool refreshed: {len(self.working_proxies)} working proxies")
            
            return len(self.working_proxies)
    
    def get_next_proxy(self):
        """Get next available proxy (not used in current run)"""
        with self.lock:
            # Refresh if needed
            self.refresh_proxy_pool()
            
            # Find unused proxy
            for proxy in self.working_proxies:
                if proxy not in self.used_proxies:
                    self.used_proxies.add(proxy)
                    return proxy
            
            # If all proxies used, clear used list and start over
            if len(self.used_proxies) >= len(self.working_proxies):
                self.logger.warning("WARNING: All proxies used, clearing used list")
                self.used_proxies.clear()
                
                # Try to get first available
                if self.working_proxies:
                    proxy = self.working_proxies[0]
                    self.used_proxies.add(proxy)
                    return proxy
            
            return None
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed and remove from working list"""
        with self.lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.logger.warning(f"REMOVED failed proxy: {proxy}")
                
                # If we're running low, refresh
                if len(self.working_proxies) < self.min_proxies // 2:
                    self.logger.info("RUNNING LOW on proxies, triggering refresh...")
                    threading.Thread(target=self.refresh_proxy_pool, args=(True,)).start()
    
    def get_proxy_stats(self):
        """Get proxy pool statistics"""
        with self.lock:
            return {
                'total_working': len(self.working_proxies),
                'used_in_run': len(self.used_proxies),
                'available': len(self.working_proxies) - len(self.used_proxies),
                'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None
            }
    
    def save_proxies(self):
        """Save working proxies to file"""
        try:
            data = {
                'proxies': self.working_proxies,
                'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.proxy_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"SAVED {len(self.working_proxies)} proxies to {self.proxy_file}")
            
        except Exception as e:
            self.logger.error(f"FAILED to save proxies: {e}")
    
    def load_proxies(self):
        """Load working proxies from file"""
        try:
            if self.proxy_file.exists():
                with open(self.proxy_file, 'r') as f:
                    data = json.load(f)
                
                self.working_proxies = data.get('proxies', [])
                last_refresh_str = data.get('last_refresh')
                if last_refresh_str:
                    self.last_refresh = datetime.fromisoformat(last_refresh_str)
                
                self.logger.info(f"LOADED {len(self.working_proxies)} proxies from {self.proxy_file}")
                
                # Quick validation of first 10 proxies only (to avoid long startup)
                if self.working_proxies:
                    self.logger.info("QUICK VALIDATION of first 10 proxies...")
                    valid_proxies = []
                    test_proxies = self.working_proxies[:10]  # Only test first 10
                    
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        future_to_proxy = {executor.submit(self.test_proxy, proxy): proxy for proxy in test_proxies}
                        
                        for future in as_completed(future_to_proxy):
                            proxy = future_to_proxy[future]
                            try:
                                if future.result(timeout=5):  # 5 second timeout per proxy
                                    valid_proxies.append(proxy)
                            except Exception:
                                pass  # Skip failed proxies
                    
                    # If we have some valid proxies, assume the rest are also valid
                    if valid_proxies:
                        self.logger.info(f"QUICK VALIDATION: {len(valid_proxies)}/10 proxies working - assuming all {len(self.working_proxies)} are valid")
                    else:
                        self.logger.warning("QUICK VALIDATION: No proxies working - will refresh pool")
                        self.working_proxies = []
                
        except Exception as e:
            self.logger.error(f"FAILED to load proxies: {e}")
            self.working_proxies = []
    
    def reset_run(self):
        """Reset used proxies for a new run"""
        with self.lock:
            self.used_proxies.clear()
            self.logger.info("RESET proxy usage for new run")

    def get_proxy_for_ticker(self, ticker_number):
        """Get proxy for a specific ticker number, switching every 200 tickers"""
        if not self.working_proxies:
            return None
            
        with self.lock:
            # Switch proxy every 200 tickers
            if (ticker_number % self.switch_interval == 0 or 
                self.current_proxy is None or 
                self.current_proxy in self.used_proxies):
                
                # Get next available proxy
                proxy = self.get_next_proxy()
                if proxy:
                    self.current_proxy = proxy
                    self.logger.info(f"SWITCHED: Proxy {ticker_number//self.switch_interval + 1}: {proxy}")
                else:
                    self.logger.warning("WARNING: No more proxies available, running without proxy")
                    self.current_proxy = None
            
            return self.current_proxy

def main():
    """Test the proxy manager"""
    print("PROXY MANAGER TEST")
    print("=" * 50)
    
    manager = ProxyManager(min_proxies=50, max_proxies=100)
    
    # Refresh proxy pool
    count = manager.refresh_proxy_pool(force=True)
    print(f"SUCCESS: Found {count} working proxies")
    
    # Test getting proxies
    print("\nTESTING proxy retrieval:")
    for i in range(10):
        proxy = manager.get_next_proxy()
        if proxy:
            print(f"  {i+1}. {proxy}")
        else:
            print(f"  {i+1}. No proxy available")
    
    # Show stats
    stats = manager.get_proxy_stats()
    print(f"\nSTATS: {stats}")
    
    # Reset for new run
    manager.reset_run()
    print("RESET for new run")

if __name__ == "__main__":
    main()