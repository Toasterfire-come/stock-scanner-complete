#!/usr/bin/env python3
"""
Batched Real-Time Stock Scanner - 5000+ Tickers
================================================
Handles large NYSE+NASDAQ scans in manageable batches
"""

import time
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

def run_batch(start_idx: int, end_idx: int, batch_num: int, total_batches: int):
    """Run a single batch scan"""
    print(f"\n{'='*80}")
    print(f"BATCH {batch_num}/{total_batches}: Tickers {start_idx}-{end_idx}")
    print(f"{'='*80}\n")

    # Create batch-specific scanner config
    batch_script = f"""
import sys
sys.path.insert(0, '{BASE_DIR}')
from realtime_scanner_working_proxy import (
    SessionPool, ScanConfig, load_proxies, scan_tickers, load_tickers
)
import json

# Load all tickers and slice for this batch
all_tickers = load_tickers(10000)  # Load max
batch_tickers = all_tickers[{start_idx}:{end_idx}]

print(f"Batch {batch_num}: Scanning {{len(batch_tickers)}} tickers...")

config = ScanConfig(
    max_threads=20,
    timeout=3.0,
    target_tickers=len(batch_tickers),
    session_pool_size=20,  # 20 proxies - proven stable
    output_json="batch_{batch_num}_results.json"
)

proxies = load_proxies()
session_pool = SessionPool(proxies, config.session_pool_size, proxy_offset=0)
results = scan_tickers(batch_tickers, session_pool, config)

with open('{BASE_DIR}/batch_{batch_num}_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\\nBatch {batch_num} complete: {{results['scan_info']['successful']}}/{{results['scan_info']['total_tickers']}} successful")
"""

    # Run batch
    result = subprocess.run(
        [sys.executable, "-c", batch_script],
        capture_output=True,
        text=True,
        timeout=180  # 3 minutes max per batch
    )

    if result.returncode != 0:
        print(f"⚠️  Batch {batch_num} had issues:")
        print(result.stderr[-500:] if result.stderr else "No error output")

    print(result.stdout)
    return result.returncode == 0

def aggregate_batches(num_batches: int):
    """Combine all batch results"""
    print(f"\n{'='*80}")
    print("AGGREGATING ALL BATCHES")
    print(f"{'='*80}\n")

    all_results = []
    total_successful = 0
    total_failed = 0
    total_time = 0

    for i in range(1, num_batches + 1):
        batch_file = BASE_DIR / f"batch_{i}_results.json"
        if not batch_file.exists():
            print(f"⚠️  Missing: batch_{i}_results.json")
            continue

        with open(batch_file, 'r') as f:
            batch_data = json.load(f)

        all_results.extend(batch_data['results'])
        total_successful += batch_data['scan_info']['successful']
        total_failed += batch_data['scan_info']['failed']
        total_time += batch_data['scan_info']['scan_duration_seconds']

        print(f"Batch {i}: {batch_data['scan_info']['successful']}/{batch_data['scan_info']['total_tickers']} "
              f"({batch_data['scan_info']['success_rate_percent']:.1f}%)")

    # Create combined results
    total_tickers = total_successful + total_failed
    success_rate = (total_successful / total_tickers * 100) if total_tickers > 0 else 0

    combined = {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": total_tickers,
            "successful": total_successful,
            "failed": total_failed,
            "success_rate_percent": round(success_rate, 2),
            "total_scan_duration_seconds": round(total_time, 2),
            "num_batches": num_batches,
            "average_rate_per_second": round(total_tickers / total_time, 2) if total_time > 0 else 0
        },
        "results": sorted(all_results, key=lambda x: x.get('ticker', ''))
    }

    output_file = BASE_DIR / "realtime_scan_full_results.json"
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n{'='*80}")
    print(f"FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Total: {total_successful}/{total_tickers} ({success_rate:.2f}%)")
    print(f"Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Rate: {total_tickers/total_time:.1f} tickers/sec")
    print(f"Saved: {output_file}")
    print(f"{'='*80}\n")

def main():
    """Run full 5130-ticker scan in batches"""
    total_tickers = 5130  # Full NYSE + NASDAQ
    batch_size = 500  # 20 proxies × 25 requests = 500 tickers per batch

    batches = []
    for start in range(0, total_tickers, batch_size):
        end = min(start + batch_size, total_tickers)
        batches.append((start, end))

    print(f"\n{'='*80}")
    print(f"BATCHED SCANNER: {total_tickers} Tickers in {len(batches)} Batches")
    print(f"{'='*80}")
    print(f"Batch size: {batch_size} tickers")
    print(f"Proxies per batch: 20")
    print(f"Requests per proxy: ~{batch_size/20:.0f}")
    print(f"Cooldown between batches: 30s")
    print(f"Est. total time: ~{len(batches) * 50 / 60:.1f} minutes")
    print(f"{'='*80}\n")

    start_time = time.time()

    for i, (start_idx, end_idx) in enumerate(batches, 1):
        success = run_batch(start_idx, end_idx, i, len(batches))

        if not success:
            print(f"⚠️  Batch {i} failed, continuing...")

        # Cooldown between batches (except last)
        if i < len(batches):
            cooldown = 30
            print(f"\n💤 Cooldown {cooldown}s before next batch...")
            time.sleep(cooldown)

    total_duration = time.time() - start_time

    # Aggregate all results
    aggregate_batches(len(batches))

    print(f"Total execution time: {total_duration:.1f}s ({total_duration/60:.1f} min)\n")

if __name__ == "__main__":
    main()
