#!/usr/bin/env python3
"""
ProxyDB Scraper - Get 50+ proxies from ProxyDB
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup

class ProxyDBScraper:
    def __init__(self):
        self.base_url = "https://proxydb.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_proxies_from_proxydb(self, limit=100):
        """Get proxies from ProxyDB"""
        proxies = []
        
        # ProxyDB has multiple pages with proxies
        for page in range(1, 6):  # Get first 5 pages
            try:
                url = f"{self.base_url}/?protocol=http&protocol=https&offset={(page-1)*20}"
                print(f"Scraping page {page}: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find proxy table
                    table = soup.find('table', {'class': 'table'})
                    if table:
                        rows = table.find_all('tr')[1:]  # Skip header
                        
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                protocol = cols[2].text.strip().lower() if len(cols) > 2 else 'http'
                                
                                if ip and port and protocol in ['http', 'https']:
                                    proxy = f"{protocol}://{ip}:{port}"
                                    proxies.append(proxy)
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
        
        return proxies[:limit]
    
    def get_proxies_from_api(self, limit=100):
        """Get proxies from ProxyDB API endpoints"""
        proxies = []
        
        # ProxyDB API endpoints
        api_urls = [
            "https://proxydb.net/api/proxies?protocol=http&protocol=https&limit=50",
            "https://proxydb.net/api/proxies?protocol=http&limit=25",
            "https://proxydb.net/api/proxies?protocol=https&limit=25",
        ]
        
        for url in api_urls:
            try:
                print(f"Fetching from API: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data:
                        for item in data['data']:
                            if 'ip' in item and 'port' in item:
                                protocol = item.get('protocol', 'http').lower()
                                if protocol in ['http', 'https']:
                                    proxy = f"{protocol}://{item['ip']}:{item['port']}"
                                    proxies.append(proxy)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching from API: {e}")
                continue
        
        return proxies[:limit]
    
    def test_proxy(self, proxy):
        """Test if a proxy is working"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=10,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return True
        except:
            pass
        
        return False
    
    def find_working_proxies(self, target_count=50):
        """Find working proxies from ProxyDB"""
        print(f"PROXYDB SCRAPER: Target {target_count} working proxies")
        
        # Get proxies from multiple sources
        all_proxies = []
        
        # Method 1: Web scraping
        print("\nMethod 1: Web scraping...")
        scraped_proxies = self.get_proxies_from_proxydb(limit=100)
        all_proxies.extend(scraped_proxies)
        print(f"Scraped {len(scraped_proxies)} proxies")
        
        # Method 2: API
        print("\nMethod 2: API endpoints...")
        api_proxies = self.get_proxies_from_api(limit=100)
        all_proxies.extend(api_proxies)
        print(f"API fetched {len(api_proxies)} proxies")
        
        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        print(f"\nTotal unique proxies: {len(unique_proxies)}")
        
        # Test proxies
        print(f"\nTesting {len(unique_proxies)} proxies...")
        working_proxies = []
        
        for i, proxy in enumerate(unique_proxies):
            if self.test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"WORKING: {proxy} ({len(working_proxies)}/{target_count})")
                
                if len(working_proxies) >= target_count:
                    break
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"Tested {i + 1}/{len(unique_proxies)} proxies...")
        
        print(f"\nREACHED TARGET: {len(working_proxies)} working proxies")
        return working_proxies
    
    def save_proxies(self, proxies, filename="proxydb_working_proxies.json"):
        """Save working proxies to file"""
        data = {
            'proxies': proxies,
            'count': len(proxies),
            'source': 'proxydb.net',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(proxies)} proxies to {filename}")

def main():
    """Main function"""
    print("PROXYDB SCRAPER")
    print("=" * 40)
    
    scraper = ProxyDBScraper()
    
    # Find working proxies
    working_proxies = scraper.find_working_proxies(target_count=50)
    
    if working_proxies:
        # Save to file
        scraper.save_proxies(working_proxies)
        
        # Show first 10
        print(f"\nFirst 10 working proxies:")
        for i, proxy in enumerate(working_proxies[:10], 1):
            print(f"  {i}. {proxy}")
        
        if len(working_proxies) > 10:
            print(f"  ... and {len(working_proxies) - 10} more")
    else:
        print("No working proxies found")

if __name__ == "__main__":
    main()