#!/usr/bin/env python3
"""
Real-Time Stock Scanner with Batched Proxy Rotation
====================================================
Scans in batches to avoid curl_cffi segfaults at scale
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import the working scanner
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def load_tickers(limit: int) -> List[str]:
    """Load tickers"""
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        raise FileNotFoundError("No ticker files found")

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS[:limit]
    logger.info(f"Loaded {len(tickers)} total tickers")
    return tickers


def scan_batch(tickers: List[str], batch_num: int, total_batches: int) -> Dict[str, Any]:
    """Scan a batch of tickers using subprocess to avoid memory issues"""
    logger.info(f"Starting batch {batch_num}/{total_batches} ({len(tickers)} tickers)")

    # Create temporary script for this batch
    batch_script = BASE_DIR / f"_temp_batch_{batch_num}.py"
    batch_output = BASE_DIR / f"_temp_batch_{batch_num}_results.json"

    script_content = f'''
import sys
sys.path.insert(0, "{BASE_DIR}")
from realtime_scanner_working_proxy import scan_tickers, SessionPool, ScanConfig, load_proxies
import json

tickers = {tickers!r}
config = ScanConfig(
    max_threads=10,
    target_tickers=len(tickers),
    session_pool_size=20,
    output_json=str({batch_output!r})
)

proxies = load_proxies()
session_pool = SessionPool(proxies, config.session_pool_size, proxy_offset=100)
results = scan_tickers(tickers, session_pool, config)

with open({batch_output!r}, 'w') as f:
    json.dump(results, f, indent=2)
'''

    batch_script.write_text(script_content)

    try:
        # Run batch in subprocess
        import subprocess
        result = subprocess.run(
            [sys.executable, str(batch_script)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            logger.warning(f"Batch {batch_num} returned code {result.returncode}")
            logger.debug(f"stderr: {result.stderr[:500]}")

        # Load results
        if batch_output.exists():
            with open(batch_output, 'r') as f:
                batch_results = json.load(f)
            logger.info(f"Batch {batch_num} complete: {batch_results['scan_info']['successful']}/{len(tickers)} successful")
            return batch_results
        else:
            logger.error(f"Batch {batch_num} failed - no output file")
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"Batch {batch_num} timed out")
        return None
    except Exception as e:
        logger.error(f"Batch {batch_num} error: {e}")
        return None
    finally:
        # Cleanup
        if batch_script.exists():
            batch_script.unlink()
        if batch_output.exists():
            batch_output.unlink()


def aggregate_results(batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate results from multiple batches"""
    all_results = []
    all_failed = []
    total_time = 0.0
    total_successful = 0
    total_failed = 0

    for batch in batch_results:
        if batch:
            all_results.extend(batch['results'])
            all_failed.extend(batch['failed_tickers'])
            total_time += batch['scan_info']['scan_duration_seconds']
            total_successful += batch['scan_info']['successful']
            total_failed += batch['scan_info']['failed']

    total_tickers = total_successful + total_failed
    success_rate = (total_successful / total_tickers * 100) if total_tickers > 0 else 0

    return {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": total_tickers,
            "successful": total_successful,
            "failed": total_failed,
            "success_rate_percent": round(success_rate, 2),
            "scan_duration_seconds": round(total_time, 2),
            "average_rate_per_second": round(total_tickers / total_time, 2) if total_time > 0 else 0,
            "batches": len(batch_results)
        },
        "results": all_results,
        "failed_tickers": all_failed[:100]
    }


def main():
    """Main execution with batching"""
    logger.info("=" * 80)
    logger.info("BATCHED PROXY SCANNER - 2000 TICKERS")
    logger.info("=" * 80)

    # Configuration
    total_tickers = 2000
    batch_size = 500

    # Load all tickers
    all_tickers = load_tickers(total_tickers)

    # Split into batches
    batches = [all_tickers[i:i + batch_size] for i in range(0, len(all_tickers), batch_size)]
    total_batches = len(batches)

    logger.info(f"Scanning {total_tickers} tickers in {total_batches} batches of ~{batch_size}")
    logger.info("-" * 80)

    # Scan each batch
    batch_results = []
    for i, batch_tickers in enumerate(batches, 1):
        result = scan_batch(batch_tickers, i, total_batches)
        if result:
            batch_results.append(result)

        # Small delay between batches
        if i < total_batches:
            logger.info(f"Pausing 5s before next batch...")
            time.sleep(5)

    # Aggregate results
    logger.info("-" * 80)
    logger.info("Aggregating results from all batches...")
    final_results = aggregate_results(batch_results)

    # Save final results
    output_file = BASE_DIR / "realtime_scan_batched_results.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)

    # Print summary
    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total: {final_results['scan_info']['successful']}/{final_results['scan_info']['total_tickers']} "
                f"({final_results['scan_info']['success_rate_percent']:.2f}%)")
    logger.info(f"Batches: {final_results['scan_info']['batches']}")
    logger.info(f"Time: {final_results['scan_info']['scan_duration_seconds']}s")
    logger.info(f"Rate: {final_results['scan_info']['average_rate_per_second']:.2f} tickers/sec")
    logger.info(f"Saved to: {output_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
