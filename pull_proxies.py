#!/usr/bin/env python3
"""
Standalone proxy puller and tester
Pulls working proxies without requiring database connection
"""

import time
import requests
from proxy_manager import ProxyManager

def main():
    print("🔍 PROXY PULLER & TESTER")
    print("=" * 50)
    
    # Initialize proxy manager
    print("\n📡 Initializing proxy manager...")
    try:
        proxy_manager = ProxyManager()
        initial_stats = proxy_manager.get_proxy_stats()
        print(f"✅ Loaded {initial_stats['total_working']} existing proxies")
    except Exception as e:
        print(f"❌ Failed to load existing proxies: {e}")
        proxy_manager = None
    
    # Pull fresh proxies
    print("\n🔄 Pulling fresh proxies...")
    try:
        if proxy_manager:
            count = proxy_manager.refresh_proxy_pool(force=True)
            if count > 0:
                stats = proxy_manager.get_proxy_stats()
                print(f"✅ SUCCESS: Pulled {count} working proxies")
                print(f"📊 Total working: {stats['total_working']}")
                print(f"📊 Available: {stats['available']}")
                print(f"📊 Last refresh: {stats['last_refresh']}")
                
                # Show first 5 proxies
                print(f"\n🔍 First 5 working proxies:")
                for i, proxy in enumerate(proxy_manager.working_proxies[:5], 1):
                    print(f"  {i}. {proxy}")
                
                if len(proxy_manager.working_proxies) > 5:
                    print(f"  ... and {len(proxy_manager.working_proxies) - 5} more")
                
            else:
                print("❌ Failed to pull any working proxies")
        else:
            print("❌ Proxy manager not available")
            
    except Exception as e:
        print(f"❌ Error pulling proxies: {e}")
    
    # Test a few proxies
    print(f"\n🧪 Testing proxy connectivity...")
    if proxy_manager and proxy_manager.working_proxies:
        test_proxies = proxy_manager.working_proxies[:3]  # Test first 3
        working_count = 0
        
        for i, proxy in enumerate(test_proxies, 1):
            print(f"  Testing {i}/3: {proxy}")
            try:
                session = requests.Session()
                session.proxies = {
                    'http': proxy,
                    'https': proxy
                }
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Test with a simple request
                response = session.get('https://httpbin.org/ip', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Working - IP: {data.get('origin', 'Unknown')}")
                    working_count += 1
                else:
                    print(f"    ❌ Failed - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:50]}")
        
        print(f"\n📊 Test Results: {working_count}/3 proxies working")
    
    print(f"\n🎯 Proxy pulling completed!")
    print(f"💡 Proxies are saved to 'working_proxies.json'")

if __name__ == "__main__":
    main()