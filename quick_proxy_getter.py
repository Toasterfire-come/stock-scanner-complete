#!/usr/bin/env python3
"""
Quick Proxy Getter - Fast and reliable proxy collection
"""

import requests
import time
import json

def get_proxies_from_sources():
    """Get proxies from reliable sources"""
    proxies = []
    
    # Most reliable sources
    sources = [
        {
            'name': 'ProxyScrape API',
            'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'type': 'text'
        },
        {
            'name': 'TheSpeedX GitHub',
            'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'type': 'text'
        },
        {
            'name': 'ClarkeTM GitHub',
            'url': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'type': 'text'
        },
        {
            'name': 'Sunny9577 GitHub',
            'url': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'type': 'text'
        },
        {
            'name': 'ProxyDB API',
            'url': 'https://proxydb.net/api/proxies?protocol=http&protocol=https&limit=100',
            'type': 'json'
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for source in sources:
        try:
            print(f"Fetching from {source['name']}...")
            response = requests.get(source['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                if source['type'] == 'text':
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if ':' in line and line.count('.') == 3:
                            parts = line.split(':')
                            if len(parts) == 2:
                                ip, port = parts
                                try:
                                    # Basic validation
                                    if all(0 <= int(x) <= 255 for x in ip.split('.')) and 1 <= int(port) <= 65535:
                                        proxy = f"http://{ip}:{port}"
                                        proxies.append(proxy)
                                except:
                                    continue
                
                elif source['type'] == 'json':
                    data = response.json()
                    if 'data' in data:
                        for item in data['data']:
                            if 'ip' in item and 'port' in item:
                                protocol = item.get('protocol', 'http').lower()
                                if protocol in ['http', 'https']:
                                    proxy = f"{protocol}://{item['ip']}:{item['port']}"
                                    proxies.append(proxy)
                
                print(f"  Found {len(proxies)} proxies so far")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return list(set(proxies))  # Remove duplicates

def test_proxy(proxy):
    """Quick proxy test"""
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200:
            return True
    except:
        pass
    
    return False

def main():
    """Main function"""
    print("QUICK PROXY GETTER")
    print("=" * 30)
    
    # Get proxies
    print("Collecting proxies from reliable sources...")
    all_proxies = get_proxies_from_sources()
    
    print(f"\nTotal proxies collected: {len(all_proxies)}")
    
    if not all_proxies:
        print("No proxies found. Using backup list...")
        backup_proxies = [
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
            "http://103.149.162.204:80",
            "http://103.149.162.205:80",
            "http://103.149.162.206:80",
            "http://103.149.162.207:80",
            "http://103.149.162.208:80",
        ]
        all_proxies = backup_proxies
        print(f"Using {len(backup_proxies)} backup proxies")
    
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
        if (i + 1) % 20 == 0:
            print(f"Tested {i + 1}/{len(all_proxies)} proxies...")
    
    print(f"\nREACHED TARGET: {len(working_proxies)} working proxies")
    
    # Save to file
    data = {
        'proxies': working_proxies,
        'count': len(working_proxies),
        'source': 'quick_getter',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    filename = "quick_working_proxies.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(working_proxies)} proxies to {filename}")
    
    # Show results
    print(f"\nFirst 10 working proxies:")
    for i, proxy in enumerate(working_proxies[:10], 1):
        print(f"  {i}. {proxy}")
    
    if len(working_proxies) > 10:
        print(f"  ... and {len(working_proxies) - 10} more")

if __name__ == "__main__":
    main()