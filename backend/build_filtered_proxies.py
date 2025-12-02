#!/usr/bin/env python3
"""
Build optimized proxy list from large sample
"""
import json
import subprocess
import sys

def test_proxy_batches(total_proxies=1000, batch_size=200):
    """Test proxies in batches to build optimized list"""

    # Load all proxies
    with open('working_proxies.json', 'r') as f:
        data = json.load(f)
        all_proxies = data.get('proxies', [])

    print(f"Total proxies available: {len(all_proxies)}")
    print(f"Testing {total_proxies} proxies in batches of {batch_size}...")
    print()

    all_working = []

    for batch_num in range(0, total_proxies, batch_size):
        start_idx = batch_num
        end_idx = min(batch_num + batch_size, total_proxies)

        print(f"{'='*80}")
        print(f"BATCH {batch_num//batch_size + 1}: Testing proxies {start_idx} to {end_idx}")
        print(f"{'='*80}")

        # Extract batch
        batch_proxies = all_proxies[start_idx:end_idx]

        # Save batch
        with open(f'proxy_batch_{batch_num}.json', 'w') as f:
            json.dump({"proxies": batch_proxies}, f, indent=2)

        # Test batch
        print(f"Testing {len(batch_proxies)} proxies...")
        result = subprocess.run([
            'python3', 'proxy_config_helper.py',
            '--test', f'proxy_batch_{batch_num}.json',
            '--output', f'tested_batch_{batch_num}.json',
            '--timeout', '8',
            '--workers', '50',
            '--min-speed', '10',
            '--yahoo-only'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            # Load working proxies from this batch
            try:
                with open(f'tested_batch_{batch_num}.json', 'r') as f:
                    tested_data = json.load(f)
                    working = tested_data.get('proxies', [])
                    all_working.extend(working)
                    print(f"✓ Batch complete: {len(working)} working proxies")
            except Exception as e:
                print(f"✗ Error loading batch results: {e}")
        else:
            print(f"✗ Batch test failed")

        print()

    # Save combined working proxies
    unique_working = list(set(all_working))

    print(f"{'='*80}")
    print(f"FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Total tested: {total_proxies}")
    print(f"Working proxies: {len(unique_working)}")
    print(f"Success rate: {len(unique_working)/total_proxies*100:.1f}%")
    print()

    # Save to optimized list
    with open('filtered_working_proxies.json', 'w') as f:
        json.dump({"proxies": unique_working}, f, indent=2)

    print(f"✓ Saved {len(unique_working)} working proxies to filtered_working_proxies.json")
    print()
    print("Sample working proxies:")
    for i, proxy in enumerate(unique_working[:10], 1):
        print(f"  {i}. {proxy}")

if __name__ == "__main__":
    test_proxy_batches(total_proxies=1000, batch_size=200)
