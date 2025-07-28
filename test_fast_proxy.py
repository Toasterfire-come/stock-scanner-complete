#!/usr/bin/env python3
"""
Test Fast Proxy Finder
Simple test to verify fast proxy finder functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fast_proxy_finder import FastProxyFinder
    print("SUCCESS: Successfully imported FastProxyFinder")
except ImportError as e:
    print(f"ERROR: Failed to import FastProxyFinder: {e}")
    print("Installing required packages...")
    os.system("pip install requests")
    try:
        from fast_proxy_finder import FastProxyFinder
        print("SUCCESS: Successfully imported FastProxyFinder after installing requests")
    except ImportError as e:
        print(f"ERROR: Still failed to import: {e}")
        sys.exit(1)

def test_fast_proxy_finder():
    """Test the fast proxy finder functionality"""
    print("\nTESTING Fast Proxy Finder")
    print("=" * 50)
    
    # Create fast proxy finder
    finder = FastProxyFinder(timeout=3, max_workers=50)
    
    print("1. Testing proxy discovery...")
    start_time = time.time()
    
    working_proxies = finder.find_working_proxies_fast(target_count=None)
    
    elapsed = time.time() - start_time
    print(f"   Found {len(working_proxies)} working proxies in {elapsed:.1f} seconds")
    
    if len(working_proxies) == 0:
        print("WARNING: No proxies found. This might be due to network issues.")
        return
    
    print("\n2. Testing proxy saving...")
    finder.save_proxies(working_proxies, "test_proxies.json")
    
    print("\n3. Testing proxy loading...")
    loaded_proxies = finder.load_proxies("test_proxies.json")
    print(f"   Loaded {len(loaded_proxies)} proxies")
    
    print("\n4. Testing proxy validation...")
    valid_count = 0
    for proxy in working_proxies[:5]:  # Test first 5
        if finder.test_proxy_fast(proxy):
            valid_count += 1
            print(f"   VALID: {proxy}")
        else:
            print(f"   INVALID: {proxy}")
    
    print(f"\nVALIDATION: {valid_count}/5 proxies still working")
    
    print("\nSUCCESS: Fast Proxy Finder test completed!")
    print(f"Working proxies found: {len(working_proxies)}")
    print(f"Time taken: {elapsed:.1f} seconds")
    print(f"Speed: {len(working_proxies)/elapsed:.1f} proxies/second")

if __name__ == "__main__":
    import time
    test_fast_proxy_finder()