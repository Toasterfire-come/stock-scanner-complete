#!/usr/bin/env python3
"""
Test Scanner - No Proxies (Direct Connection)
==============================================
Quick test to verify yfinance data extraction works without proxies
"""

import time
import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, Dict, Any, List

import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def fetch_ticker_data(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch data for a single ticker without proxy"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) < 5:
            logger.warning(f"{ticker}: Empty data")
            return None

        # Extract key fields
        data = {
            "ticker": ticker,
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "price_change": info.get("regularMarketChange"),
            "price_change_percent": info.get("regularMarketChangePercent"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✓ {ticker}: ${data.get('current_price')} - {data.get('company_name')}")
        return data

    except Exception as e:
        logger.error(f"✗ {ticker}: {str(e)[:100]}")
        return None


def run_test(num_tickers: int = 50):
    """Test scanner with small sample"""
    logger.info("=" * 80)
    logger.info(f"TEST SCANNER - {num_tickers} TICKERS (NO PROXY)")
    logger.info("=" * 80)

    # Load tickers
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        logger.error("No ticker files found")
        return

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tickers = module.COMBINED_TICKERS[:num_tickers]
    logger.info(f"Testing {len(tickers)} tickers: {', '.join(tickers[:10])}...")
    logger.info("-" * 80)

    start_time = time.time()
    results = []
    failed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_ticker_data, ticker): ticker for ticker in tickers}

        for future in as_completed(futures):
            data = future.result()
            if data:
                results.append(data)
            else:
                failed += 1

    elapsed = time.time() - start_time
    success_rate = (len(results) / len(tickers)) * 100

    # Save results
    output = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "total_tickers": len(tickers),
            "successful": len(results),
            "failed": failed,
            "success_rate_percent": round(success_rate, 2),
            "duration_seconds": round(elapsed, 2),
            "mode": "no_proxy_direct_connection"
        },
        "results": results
    }

    output_file = BASE_DIR / "test_scan_no_proxy.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info("=" * 80)
    logger.info("TEST COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total time: {elapsed:.2f}s")
    logger.info(f"Success: {len(results)}/{len(tickers)} ({success_rate:.2f}%)")
    logger.info(f"Failed: {failed}")
    logger.info(f"Results saved to: {output_file}")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_test(num_tickers=50)
