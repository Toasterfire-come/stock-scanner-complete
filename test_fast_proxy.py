#!/usr/bin/env python3
"""
Test Fast Proxy Finder
Simple test to verify fast proxy finder functionality
"""

import sys
import os
import time
import signal

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

def signal_handler(sig, frame):
    print("\n\nINTERRUPTED: Stopping proxy finder...")
    print("Progress saved to fast_working_proxies.json")
    sys.exit(0)

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("TESTING Fast Proxy Finder")
    print("=" * 50)
    print("Press Ctrl+C to stop at any time")
    print()
    
    finder = FastProxyFinder()
    
    try:
        print("1. Testing proxy discovery...")
        start_time = time.time()
        
        working_proxies = finder.find_working_proxies_fast(target_count=None)
        
        elapsed = time.time() - start_time
        print(f"   Found {len(working_proxies)} working proxies in {elapsed:.1f} seconds")
        
        if working_proxies:
            print(f"\n2. Saving {len(working_proxies)} proxies to file...")
            finder.save_proxies(working_proxies)
            print("   SUCCESS: Proxies saved to fast_working_proxies.json")
            
            print(f"\n3. Validating saved proxies...")
            loaded_proxies = finder.load_proxies()
            print(f"   SUCCESS: Loaded {len(loaded_proxies)} proxies from file")
            
            print(f"\nSUCCESS: Fast Proxy Finder test completed!")
            print(f"Working proxies found: {len(working_proxies)}")
            print(f"Time taken: {elapsed:.1f} seconds")
            print(f"Speed: {len(working_proxies)/elapsed:.2f} proxies/second")
        else:
            print("\nWARNING: No working proxies found")
            
    except KeyboardInterrupt:
        print("\n\nINTERRUPTED: Stopping proxy finder...")
        print("Progress saved to fast_working_proxies.json")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()