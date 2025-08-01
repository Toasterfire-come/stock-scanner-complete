#!/usr/bin/env python3
"""
Quick Proxy Tester - Test existing proxies without hanging
"""

import json
import requests
import time

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
            timeout=5,  # Short timeout
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200:
            return True, response.json().get('origin', 'unknown')
        return False, None
    except Exception as e:
        return False, str(e)

def main():
    print("QUICK PROXY TESTER")
    print("=" * 30)
    
    # Test working_proxies.json
    print("\nTesting working_proxies.json...")
    proxies = load_proxies_from_file('working_proxies.json')
    print(f"Found {len(proxies)} proxies")
    
    if proxies:
        print("Testing first 10 proxies...")
        working = 0
        for i, proxy in enumerate(proxies[:10]):
            print(f"  Testing {i+1}/10: {proxy}")
            is_working, result = test_proxy(proxy)
            if is_working:
                print(f"    SUCCESS: {result}")
                working += 1
            else:
                print(f"    FAILED: {result}")
            time.sleep(0.1)  # Small delay
        
        print(f"\nResults: {working}/10 working")
    
    # Test fast_working_proxies.json
    print("\nTesting fast_working_proxies.json...")
    proxies = load_proxies_from_file('fast_working_proxies.json')
    print(f"Found {len(proxies)} proxies")
    
    if proxies:
        print("Testing first 10 proxies...")
        working = 0
        for i, proxy in enumerate(proxies[:10]):
            print(f"  Testing {i+1}/10: {proxy}")
            is_working, result = test_proxy(proxy)
            if is_working:
                print(f"    SUCCESS: {result}")
                working += 1
            else:
                print(f"    FAILED: {result}")
            time.sleep(0.1)  # Small delay
        
        print(f"\nResults: {working}/10 working")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()