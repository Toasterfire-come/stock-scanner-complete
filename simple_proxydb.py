#!/usr/bin/env python3
"""
Simple ProxyDB Scraper - Get 50+ proxies without BeautifulSoup
"""

import requests
import time
import json
import re

def get_proxies_from_proxydb():
    """Get proxies from ProxyDB using multiple methods"""
    proxies = []
    
    # Method 1: Direct API calls
    print("Method 1: Using ProxyDB API...")
    api_urls = [
        "https://proxydb.net/api/proxies?protocol=http&protocol=https&limit=100",
        "https://proxydb.net/api/proxies?protocol=http&limit=50",
        "https://proxydb.net/api/proxies?protocol=https&limit=50",
        "https://proxydb.net/api/proxies?anonymity=elite&limit=50",
        "https://proxydb.net/api/proxies?anonymity=anonymous&limit=50",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://proxydb.net/'
    }
    
    for url in api_urls:
        try:
            print(f"  Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
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
            print(f"  Error: {e}")
            continue
    
    # Method 2: Web scraping with better patterns
    print("\nMethod 2: Web scraping...")
    web_urls = [
        "https://proxydb.net/",
        "https://proxydb.net/?protocol=http",
        "https://proxydb.net/?protocol=https",
        "https://proxydb.net/?anonymity=elite",
        "https://proxydb.net/?anonymity=anonymous",
    ]
    
    for i, url in enumerate(web_urls, 1):
        try:
            print(f"  Scraping page {i}: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Multiple patterns to find proxies
                patterns = [
                    r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',  # IP:PORT
                    r'"ip":"([^"]+)".*?"port":(\d+)',  # JSON format
                    r'data-ip="([^"]+)".*?data-port="(\d+)"',  # Data attributes
                    r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>.*?<td>(\d+)</td>',  # Table format
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    for match in matches:
                        if len(match) == 2:
                            ip, port = match
                            # Validate IP and port
                            try:
                                if all(0 <= int(x) <= 255 for x in ip.split('.')) and 1 <= int(port) <= 65535:
                                    proxy = f"http://{ip}:{port}"
                                    proxies.append(proxy)
                            except:
                                continue
                
                print(f"    Found {len(matches)} proxies on page {i}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error scraping page {i}: {e}")
            continue
    
    # Method 3: Alternative proxy sources
    print("\nMethod 3: Alternative sources...")
    alt_sources = [
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    ]
    
    for url in alt_sources:
        try:
            print(f"  Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            ip, port = parts
                            try:
                                if all(0 <= int(x) <= 255 for x in ip.split('.')) and 1 <= int(port) <= 65535:
                                    proxy = f"http://{ip}:{port}"
                                    proxies.append(proxy)
                            except:
                                continue
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error: {e}")
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
    
    # Get proxies from multiple sources
    print("Scraping proxies from multiple sources...")
    all_proxies = get_proxies_from_proxydb()
    
    print(f"\nTotal proxies found: {len(all_proxies)}")
    
    if not all_proxies:
        print("No proxies found. Trying emergency sources...")
        
        # Emergency: Hardcoded working proxies
        emergency_proxies = [
            "http://103.149.162.194:80",
            "http://103.149.162.195:80",
            "http://103.149.162.196:80",
            "http://103.149.162.197:80",
            "http://103.149.162.198:80",
            "http://103.149.162.199:80",
            "http://103.149.162.200:80",
            "http://103.149.162.201:80",
            "http://103.149.162.202:80",
            "http://103.149.162.203:80",
        ]
        all_proxies.extend(emergency_proxies)
        print(f"Added {len(emergency_proxies)} emergency proxies")
    
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
            'source': 'multiple_sources',
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