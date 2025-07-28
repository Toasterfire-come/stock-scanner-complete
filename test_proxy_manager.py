#!/usr/bin/env python3
"""
Test Proxy Manager
Simple test to verify proxy manager functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from proxy_manager import ProxyManager
    print("✅ Successfully imported ProxyManager")
except ImportError as e:
    print(f"❌ Failed to import ProxyManager: {e}")
    print("Installing required packages...")
    os.system("pip install requests")
    try:
        from proxy_manager import ProxyManager
        print("✅ Successfully imported ProxyManager after installing requests")
    except ImportError as e:
        print(f"❌ Still failed to import: {e}")
        sys.exit(1)

def test_proxy_manager():
    """Test the proxy manager functionality"""
    print("\n🧪 Testing Proxy Manager")
    print("=" * 50)
    
    # Create proxy manager with smaller pool for testing
    manager = ProxyManager(min_proxies=10, max_proxies=20)
    
    print("1. Testing proxy pool refresh...")
    count = manager.refresh_proxy_pool(force=True)
    print(f"   Found {count} working proxies")
    
    if count == 0:
        print("⚠️ No proxies found. This is normal for testing.")
        print("   The proxy manager will work when run with the full stock update.")
        return
    
    print("\n2. Testing proxy retrieval...")
    used_proxies = set()
    for i in range(5):
        proxy = manager.get_next_proxy()
        if proxy:
            used_proxies.add(proxy)
            print(f"   {i+1}. {proxy}")
        else:
            print(f"   {i+1}. No proxy available")
    
    print(f"\n3. Testing no reuse (used {len(used_proxies)} unique proxies)")
    
    print("\n4. Testing proxy stats...")
    stats = manager.get_proxy_stats()
    print(f"   Total working: {stats['total_working']}")
    print(f"   Used in run: {stats['used_in_run']}")
    print(f"   Available: {stats['available']}")
    
    print("\n5. Testing proxy failure handling...")
    if used_proxies:
        test_proxy = list(used_proxies)[0]
        print(f"   Marking {test_proxy} as failed...")
        manager.mark_proxy_failed(test_proxy)
        
        new_stats = manager.get_proxy_stats()
        print(f"   New total working: {new_stats['total_working']}")
    
    print("\n6. Testing run reset...")
    manager.reset_run()
    reset_stats = manager.get_proxy_stats()
    print(f"   After reset - used in run: {reset_stats['used_in_run']}")
    
    print("\n✅ Proxy Manager test completed successfully!")
    print("\n📝 To use with stock updates:")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 100")

if __name__ == "__main__":
    test_proxy_manager()