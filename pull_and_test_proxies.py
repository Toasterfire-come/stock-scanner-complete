#!/usr/bin/env python3
"""
Pull and Test Proxies - Comprehensive proxy acquisition and testing
"""

import requests
import json
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_proxies_from_sources():
    """Get proxies from multiple reliable sources"""
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
            'name': 'roosterkid HTTPS',
            'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
            'type': 'text'
        },
        {
            'name': 'ProxyScrape HTTPS',
            'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=https&timeout=5000&country=all&ssl=yes&anonymity=all',
            'type': 'text'
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("PULLING PROXIES FROM SOURCES:")
    print("=" * 40)
    
    for source in sources:
        try:
            print(f"Fetching from {source['name']}...")
            response = requests.get(source['url'], headers=headers, timeout=15)
            
            if response.status_code == 200:
                if source['type'] == 'text':
                    lines = response.text.strip().split('\n')
                    source_proxies = []
                    for line in lines:
                        line = line.strip()
                        # Match IP:PORT pattern
                        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                            if source['name'].lower().startswith('https'):
                                source_proxies.append(f"https://{line}")
                            else:
                                source_proxies.append(f"http://{line}")
                    
                    proxies.extend(source_proxies)
                    print(f"  Found {len(source_proxies)} proxies")
                else:
                    print(f"  Found 0 proxies (unsupported type)")
            else:
                print(f"  Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # Remove duplicates
    unique_proxies = list(set(proxies))
    print(f"\nTotal unique proxies: {len(unique_proxies)}")
    return unique_proxies

def test_proxy(proxy):
    """Test if a proxy is working"""
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
            data = response.json()
            return True, data.get('origin', 'unknown'), 'http'
        return False, None, None
    except requests.exceptions.SSLError:
        # Try HTTPS if HTTP fails
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=8,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('origin', 'unknown'), 'https'
            return False, None, None
        except Exception:
            return False, None, None
    except Exception as e:
        return False, str(e), None

def main():
    print("PULL AND TEST PROXIES")
    print("=" * 50)
    
    # Get fresh proxies
    proxies = get_proxies_from_sources()
    
    if not proxies:
        print("No proxies found from sources!")
        return
    
    # Test proxies with threading
    print(f"\nTESTING {len(proxies)} PROXIES:")
    print("=" * 40)
    
    working_proxies = []
    failed_proxies = []
    
    # Use ThreadPoolExecutor for parallel testing
    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        completed = 0
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            completed += 1
            
            try:
                is_working, ip, protocol = future.result(timeout=15)
                if is_working:
                    working_proxies.append({
                        'proxy': proxy,
                        'ip': ip,
                        'protocol': protocol,
                        'source': 'fresh_pull'
                    })
                    print(f"✅ {proxy} (IP: {ip}, Protocol: {protocol})")
                else:
                    failed_proxies.append(proxy)
                    print(f"❌ {proxy}")
                    
                # Show progress every 25
                if completed % 25 == 0:
                    print(f"Progress: {completed}/{len(proxies)} ({len(working_proxies)} working, {len(failed_proxies)} failed)")
                    
            except Exception as e:
                failed_proxies.append(proxy)
                print(f"❌ {proxy} (Error: {e})")
    
    # Results
    print(f"\nFINAL RESULTS:")
    print("=" * 40)
    print(f"Total tested: {len(proxies)}")
    print(f"Working: {len(working_proxies)}")
    print(f"Failed: {len(failed_proxies)}")
    print(f"Success rate: {len(working_proxies)/len(proxies)*100:.1f}%")
    
    # Save working proxies
    if working_proxies:
        data = {
            'proxies': [p['proxy'] for p in working_proxies],
            'metadata': {
                'total': len(working_proxies),
                'source': 'fresh_pull',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'success_rate': f"{len(working_proxies)/len(proxies)*100:.1f}%",
                'total_tested': len(proxies)
            },
            'detailed_proxies': working_proxies
        }
        
        filename = f'fresh_working_proxies_{int(time.time())}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved {len(working_proxies)} working proxies to {filename}")
        
        # Show first 20 working proxies
        print("\nFirst 20 working proxies:")
        for i, proxy_data in enumerate(working_proxies[:20]):
            print(f"{i+1:2d}. {proxy_data['proxy']} (IP: {proxy_data['ip']}, Protocol: {proxy_data['protocol']})")
        
        if len(working_proxies) > 20:
            print(f"... and {len(working_proxies) - 20} more")
    else:
        print("\nNo working proxies found!")
    
    # Save failed proxies for analysis
    if failed_proxies:
        failed_data = {
            'failed_proxies': failed_proxies,
            'total_failed': len(failed_proxies)
        }
        
        failed_filename = f'failed_proxies_{int(time.time())}.json'
        with open(failed_filename, 'w') as f:
            json.dump(failed_data, f, indent=2)
        
        print(f"\nSaved {len(failed_proxies)} failed proxies to {failed_filename}")

if __name__ == "__main__":
    main()