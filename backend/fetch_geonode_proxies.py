#!/usr/bin/env python3
"""
Fetch SOCKS5 proxies from GeoNode API
"""
import requests
import json
import sys

def fetch_geonode_proxies():
    """Fetch elite SOCKS5 proxies from GeoNode API"""

    # GeoNode API endpoint with filters
    url = (
        "https://proxylist.geonode.com/api/proxy-list"
        "?anonymityLevel=elite"
        "&filterUpTime=90"
        "&filterLastChecked=10"
        "&speed=fast"
        "&limit=500"
        "&page=1"
        "&sort_by=lastChecked"
        "&sort_type=desc"
        "&protocols=socks5"  # Filter for SOCKS5 only
    )

    print(f"Fetching proxies from GeoNode API...")
    print(f"URL: {url}")
    print()

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'data' not in data:
            print("Error: No 'data' field in response")
            return []

        proxies = []
        for proxy in data['data']:
            # Build SOCKS5 proxy URL
            ip = proxy.get('ip')
            port = proxy.get('port')
            protocols = proxy.get('protocols', [])

            if not ip or not port:
                continue

            # Check if it supports SOCKS5
            if 'socks5' in protocols:
                proxy_url = f"socks5://{ip}:{port}"
                proxies.append({
                    "url": proxy_url,
                    "country": proxy.get('country'),
                    "uptime": proxy.get('upTime'),
                    "speed": proxy.get('speed'),
                    "anonymity": proxy.get('anonymityLevel'),
                    "last_checked": proxy.get('lastChecked')
                })

        print(f"✓ Successfully fetched {len(proxies)} SOCKS5 proxies")
        print()
        print("Sample proxies:")
        for p in proxies[:5]:
            print(f"  - {p['url']} ({p['country']}) - Uptime: {p['uptime']}%, Speed: {p['speed']}ms")

        return proxies

    except Exception as e:
        print(f"Error fetching proxies: {str(e)}")
        return []

def save_proxies(proxies, filename):
    """Save proxies to JSON file"""
    # Extract just the URLs
    proxy_urls = [p['url'] for p in proxies]

    data = {
        "proxies": proxy_urls,
        "metadata": {
            "source": "GeoNode API",
            "total": len(proxies),
            "filters": {
                "anonymity": "elite",
                "uptime": "90%+",
                "last_checked": "10 min",
                "speed": "fast",
                "protocol": "socks5"
            },
            "details": proxies  # Keep full details for reference
        }
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Saved {len(proxy_urls)} proxies to {filename}")

if __name__ == "__main__":
    proxies = fetch_geonode_proxies()

    if proxies:
        save_proxies(proxies, "geonode_socks5_proxies.json")
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Total SOCKS5 proxies fetched: {len(proxies)}")

        # Country distribution
        countries = {}
        for p in proxies:
            country = p.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1

        print(f"\nCountry distribution (top 10):")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {country}: {count}")

        # Speed distribution
        speeds = [p.get('speed', 0) for p in proxies if p.get('speed')]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            print(f"\nAverage speed: {avg_speed:.0f}ms")
            print(f"Fastest: {min(speeds)}ms")
            print(f"Slowest: {max(speeds)}ms")

        sys.exit(0)
    else:
        print("Failed to fetch proxies")
        sys.exit(1)
