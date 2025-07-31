#!/usr/bin/env python3
"""
Smart Proxy Getter - Fresh sources + reliable backups
"""

import requests
import time
import json

def get_fresh_proxies():
    """Try to get fresh proxies from reliable sources"""
    proxies = []
    
    # Quick sources that usually work
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for source in sources:
        try:
            print(f"Trying: {source}")
            response = requests.get(source, headers=headers, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if ':' in line and line.count('.') == 3:
                        parts = line.split(':')
                        if len(parts) == 2:
                            ip, port = parts
                            try:
                                if all(0 <= int(x) <= 255 for x in ip.split('.')) and 1 <= int(port) <= 65535:
                                    proxy = f"http://{ip}:{port}"
                                    proxies.append(proxy)
                            except:
                                continue
                
                print(f"  Found {len(proxies)} proxies from this source")
                if len(proxies) > 100:  # Got enough
                    break
                    
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    return list(set(proxies))  # Remove duplicates

def get_backup_proxies():
    """Get reliable backup proxies"""
    return [
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
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            return True
    except:
        pass
    
    return False

def main():
    print("SMART PROXY GETTER")
    print("=" * 30)
    
    # Try fresh sources first
    print("Step 1: Trying fresh proxy sources...")
    fresh_proxies = get_fresh_proxies()
    
    if fresh_proxies:
        print(f"Found {len(fresh_proxies)} fresh proxies")
        
        # Test fresh proxies
        print("\nStep 2: Testing fresh proxies...")
        working_proxies = []
        
        for i, proxy in enumerate(fresh_proxies):
            if test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"WORKING: {proxy} ({len(working_proxies)}/50)")
                
                if len(working_proxies) >= 50:
                    break
            
            # Progress update
            if (i + 1) % 20 == 0:
                print(f"Tested {i + 1}/{len(fresh_proxies)} fresh proxies...")
    
    # If not enough fresh proxies, use backups
    if not fresh_proxies or len(working_proxies) < 50:
        print(f"\nStep 3: Using backup proxies (need {50 - len(working_proxies)} more)...")
        backup_proxies = get_backup_proxies()
        
        for i, proxy in enumerate(backup_proxies):
            if len(working_proxies) >= 50:
                break
                
            if test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"BACKUP WORKING: {proxy} ({len(working_proxies)}/50)")
    
    print(f"\nFINAL RESULT: {len(working_proxies)} working proxies")
    
    # Save to file
    data = {
        'proxies': working_proxies,
        'count': len(working_proxies),
        'source': 'smart_getter',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    filename = "smart_working_proxies.json"
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