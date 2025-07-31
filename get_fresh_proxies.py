#!/usr/bin/env python3
"""
Get Fresh Proxies - Focus on HTTP proxies with better success rates
"""

import requests
import time
import json
import re

def get_proxies_from_sources():
    """Get proxies from reliable sources"""
    proxies = []
    
    sources = [
        {
            'name': 'ProxyScrape HTTP',
            'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=no&anonymity=all',
            'type': 'text'
        },
        {
            'name': 'TheSpeedX HTTP',
            'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'type': 'text'
        },
        {
            'name': 'clarketm HTTP',
            'url': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'type': 'text'
        },
        {
            'name': 'roosterkid HTTP',
            'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
            'type': 'text'
        }
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for source in sources:
        try:
            print(f"Fetching from {source['name']}...")
            response = requests.get(source['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                if source['type'] == 'text':
                    # Extract IP:PORT patterns
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                            proxies.append(f"http://{line}")
                
                print(f"  Found {len([p for p in proxies if source['name'].lower() in p.lower()])} proxies")
            else:
                print(f"  Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # Remove duplicates
    proxies = list(set(proxies))
    print(f"\nTotal unique proxies: {len(proxies)}")
    return proxies

def test_proxy(proxy):
    """Test if a proxy is working with HTTP"""
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        # Test with HTTP first (more reliable)
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=8,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200:
            return True, response.json().get('origin', 'unknown')
        return False, None
    except Exception as e:
        return False, str(e)

def main():
    print("GET FRESH PROXIES")
    print("=" * 30)
    
    # Get fresh proxies
    proxies = get_proxies_from_sources()
    
    if not proxies:
        print("No proxies found from sources!")
        return
    
    # Test proxies
    print(f"\nTesting {len(proxies)} proxies...")
    working_proxies = []
    
    for i, proxy in enumerate(proxies, 1):
        print(f"  Testing {i}/{len(proxies)}: {proxy}")
        is_working, result = test_proxy(proxy)
        
        if is_working:
            print(f"    SUCCESS: {result}")
            working_proxies.append({
                'proxy': proxy,
                'ip': result,
                'source': 'fresh'
            })
        else:
            print(f"    FAILED: {result}")
        
        # Show progress every 10
        if i % 10 == 0:
            print(f"    Progress: {i}/{len(proxies)} tested, {len(working_proxies)} working")
        
        time.sleep(0.1)  # Small delay
    
    # Save results
    if working_proxies:
        output = {
            'proxies': working_proxies,
            'total': len(working_proxies),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('fresh_working_proxies.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nSUCCESS: Saved {len(working_proxies)} working proxies to fresh_working_proxies.json")
        print(f"Success rate: {len(working_proxies)/len(proxies)*100:.1f}%")
    else:
        print("\nFAILED: No working proxies found")

if __name__ == "__main__":
    main()