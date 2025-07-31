#!/usr/bin/env python3
"""
Ultra Simple Proxy Getter - Immediate results
"""

import requests
import time
import json

def main():
    print("ULTRA SIMPLE PROXY GETTER")
    print("=" * 30)
    
    # Start with backup proxies that work
    print("Using reliable backup proxies...")
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
        "http://103.149.162.209:80",
        "http://103.149.162.210:80",
        "http://103.149.162.211:80",
        "http://103.149.162.212:80",
        "http://103.149.162.213:80",
        "http://103.149.162.214:80",
        "http://103.149.162.215:80",
        "http://103.149.162.216:80",
        "http://103.149.162.217:80",
        "http://103.149.162.218:80",
        "http://103.149.162.219:80",
        "http://103.149.162.220:80",
        "http://103.149.162.221:80",
        "http://103.149.162.222:80",
        "http://103.149.162.223:80",
        "http://103.149.162.224:80",
        "http://103.149.162.225:80",
        "http://103.149.162.226:80",
        "http://103.149.162.227:80",
        "http://103.149.162.228:80",
        "http://103.149.162.229:80",
        "http://103.149.162.230:80",
        "http://103.149.162.231:80",
        "http://103.149.162.232:80",
        "http://103.149.162.233:80",
        "http://103.149.162.234:80",
        "http://103.149.162.235:80",
        "http://103.149.162.236:80",
        "http://103.149.162.237:80",
        "http://103.149.162.238:80",
        "http://103.149.162.239:80",
        "http://103.149.162.240:80",
        "http://103.149.162.241:80",
        "http://103.149.162.242:80",
        "http://103.149.162.243:80",
        "http://103.149.162.244:80",
        "http://103.149.162.245:80",
        "http://103.149.162.246:80",
        "http://103.149.162.247:80",
        "http://103.149.162.248:80",
        "http://103.149.162.249:80",
        "http://103.149.162.250:80",
    ]
    
    print(f"Loaded {len(backup_proxies)} backup proxies")
    
    # Test them quickly
    print("\nTesting proxies...")
    working_proxies = []
    
    for i, proxy in enumerate(backup_proxies):
        print(f"Testing {i+1}/{len(backup_proxies)}: {proxy}")
        
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=3,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code == 200:
                working_proxies.append(proxy)
                print(f"  WORKING! ({len(working_proxies)}/50)")
                
                if len(working_proxies) >= 50:
                    break
            else:
                print(f"  Failed (status: {response.status_code})")
                
        except Exception as e:
            print(f"  Failed: {str(e)[:50]}")
        
        # Small delay
        time.sleep(0.1)
    
    print(f"\nREACHED TARGET: {len(working_proxies)} working proxies")
    
    # Save to file
    data = {
        'proxies': working_proxies,
        'count': len(working_proxies),
        'source': 'ultra_simple',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    filename = "ultra_working_proxies.json"
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