#!/usr/bin/env python3
"""
Simple ProxyDB Scraper - Get 50+ proxies without BeautifulSoup
"""

import requests
import time
import json
import re

def get_proxies_from_proxydb():
    """Get proxies from ProxyDB using simple regex"""
    proxies = []
    
    # ProxyDB URLs to scrape
    urls = [
        "https://proxydb.net/?protocol=http&protocol=https",
        "https://proxydb.net/?protocol=http&protocol=https&offset=20",
        "https://proxydb.net/?protocol=http&protocol=https&offset=40",
        "https://proxydb.net/?protocol=http&protocol=https&offset=60",
        "https://proxydb.net/?protocol=http&protocol=https&offset=80",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"Scraping page {i}: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Use regex to find IP:PORT patterns
                content = response.text
                
                # Find IP:PORT patterns
                ip_port_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
                matches = re.findall(ip_port_pattern, content)
                
                for ip, port in matches:
                    # Validate IP and port
                    if all(0 <= int(x) <= 255 for x in ip.split('.')) and 1 <= int(port) <= 65535:
                        proxy = f"http://{ip}:{port}"
                        proxies.append(proxy)
                
                print(f"Found {len(matches)} proxies on page {i}")
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"Error scraping page {i}: {e}")
            continue
    
    return list(set(proxies))  # Remove duplicates

def test_proxy(proxy):
    """Test if a proxy is working"""
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=8,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200:
            return True
    except:
        pass
    
    return False

def main():
    """Main function"""
    print("SIMPLE PROXYDB SCRAPER")
    print("=" * 40)
    
    # Get proxies from ProxyDB
    print("Scraping proxies from ProxyDB...")
    all_proxies = get_proxies_from_proxydb()
    
    print(f"\nTotal proxies found: {len(all_proxies)}")
    
    if not all_proxies:
        print("No proxies found. Trying alternative sources...")
        
        # Alternative: Use ProxyDB API
        try:
            api_url = "https://proxydb.net/api/proxies?protocol=http&protocol=https&limit=100"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        if 'ip' in item and 'port' in item:
                            proxy = f"http://{item['ip']}:{item['port']}"
                            all_proxies.append(proxy)
            
            print(f"API fetched {len(all_proxies)} proxies")
        except Exception as e:
            print(f"API failed: {e}")
    
    if all_proxies:
        # Test proxies
        print(f"\nTesting {len(all_proxies)} proxies...")
        working_proxies = []
        
        for i, proxy in enumerate(all_proxies):
            if test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"WORKING: {proxy} ({len(working_proxies)}/50)")
                
                if len(working_proxies) >= 50:
                    break
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"Tested {i + 1}/{len(all_proxies)} proxies...")
        
        print(f"\nREACHED TARGET: {len(working_proxies)} working proxies")
        
        # Save to file
        data = {
            'proxies': working_proxies,
            'count': len(working_proxies),
            'source': 'proxydb.net',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        filename = "proxydb_working_proxies.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(working_proxies)} proxies to {filename}")
        
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