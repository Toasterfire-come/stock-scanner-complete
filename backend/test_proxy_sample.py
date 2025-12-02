#!/usr/bin/env python3
"""
Test a sample of proxies for practical use
"""
import json
import subprocess
import sys

def main():
    # Load all proxies
    with open('working_proxies.json', 'r') as f:
        data = json.load(f)
        all_proxies = data.get('proxies', [])

    print(f"Total proxies in file: {len(all_proxies)}")
    print()

    # Take first 200 proxies (diverse sample)
    sample_size = 200
    sample_proxies = all_proxies[:sample_size]

    # Save sample
    with open('proxy_sample.json', 'w') as f:
        json.dump({"proxies": sample_proxies}, f, indent=2)

    print(f"Created proxy_sample.json with {sample_size} proxies")
    print(f"Testing sample for Yahoo Finance compatibility...")
    print()

    # Test the sample
    result = subprocess.run([
        'python3', 'proxy_config_helper.py',
        '--test', 'proxy_sample.json',
        '--output', 'tested_http_proxies_sample.json',
        '--timeout', '8',
        '--workers', '40',
        '--min-speed', '10',
        '--yahoo-only'
    ], capture_output=False, text=True)

    if result.returncode == 0:
        print()
        print("✓ Sample test completed successfully")

        # Load results
        try:
            with open('tested_http_proxies_sample.json', 'r') as f:
                tested_data = json.load(f)
                working_proxies = tested_data.get('proxies', [])

            print(f"✓ Found {len(working_proxies)} working Yahoo Finance proxies")
            print()
            print("Sample working proxies:")
            for i, proxy in enumerate(working_proxies[:10], 1):
                print(f"  {i}. {proxy}")

        except Exception as e:
            print(f"Error loading results: {e}")
    else:
        print("✗ Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
