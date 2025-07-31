#!/usr/bin/env python3
"""
Test Existing Proxies - Test proxies already in the repo
"""

import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_proxies_from_file(filename):
    """Load proxies from JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('proxies', [])
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

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
            return True, proxy
    except Exception as e:
        pass
    
    return False, proxy

def test_proxy_list(proxies, filename, max_workers=10):
    """Test a list of proxies"""
    print(f"\nTesting {len(proxies)} proxies from {filename}...")
    
    working_proxies = []
    failed_proxies = []
    
    # Use ThreadPoolExecutor for parallel testing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        completed = 0
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            completed += 1
            
            try:
                is_working, proxy_url = future.result(timeout=10)
                if is_working:
                    working_proxies.append(proxy_url)
                    print(f"WORKING: {proxy_url} ({len(working_proxies)} working)")
                else:
                    failed_proxies.append(proxy_url)
                
                # Progress update
                if completed % 20 == 0 or completed == len(proxies):
                    print(f"Progress: {completed}/{len(proxies)} tested ({len(working_proxies)} working)")
                    
            except Exception as e:
                failed_proxies.append(proxy)
                print(f"Error testing {proxy}: {e}")
    
    return working_proxies, failed_proxies

def main():
    print("TEST EXISTING PROXIES")
    print("=" * 40)
    
    # Load proxies from both files
    working_proxies = load_proxies_from_file('working_proxies.json')
    fast_proxies = load_proxies_from_file('fast_working_proxies.json')
    
    print(f"Found {len(working_proxies)} proxies in working_proxies.json")
    print(f"Found {len(fast_proxies)} proxies in fast_working_proxies.json")
    
    # Combine and remove duplicates
    all_proxies = list(set(working_proxies + fast_proxies))
    print(f"Total unique proxies: {len(all_proxies)}")
    
    if not all_proxies:
        print("No proxies found in the repo!")
        return
    
    # Test all proxies
    working, failed = test_proxy_list(all_proxies, "combined proxies")
    
    print(f"\nTEST RESULTS:")
    print(f"Total tested: {len(all_proxies)}")
    print(f"Working: {len(working)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {(len(working)/len(all_proxies)*100):.1f}%")
    
    # Save working proxies
    if working:
        data = {
            'proxies': working,
            'count': len(working),
            'source': 'tested_existing',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tested': len(all_proxies),
            'success_rate': f"{(len(working)/len(all_proxies)*100):.1f}%"
        }
        
        filename = "tested_working_proxies.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved {len(working)} working proxies to {filename}")
        
        # Show first 20 working proxies
        print(f"\nFirst 20 working proxies:")
        for i, proxy in enumerate(working[:20], 1):
            print(f"  {i}. {proxy}")
        
        if len(working) > 20:
            print(f"  ... and {len(working) - 20} more")
    
    # Show some failed proxies for debugging
    if failed:
        print(f"\nFirst 10 failed proxies:")
        for i, proxy in enumerate(failed[:10], 1):
            print(f"  {i}. {proxy}")
        
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

if __name__ == "__main__":
    main()