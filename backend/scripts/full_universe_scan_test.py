#!/usr/bin/env python3
"""Run a full NYSE+NASDAQ batch scan and report field-level completeness metrics.

This script exercises `StockScanner.scan_batch` across the combined ticker universe
without persisting to the database or writing CSV output. It calculates failure
percentages for each payload field and prints summary SLO indicators so the run
can be validated against the 97% completeness / 5% failure / sub-180s targets.

Usage examples
--------------
    python3 scripts/full_universe_scan_test.py --max-tickers 500
    python3 scripts/full_universe_scan_test.py --use-proxies --threads 40 \
        --chunk-size 250 --timeout 8 --print-json

Environment overrides of interest
---------------------------------
    SCANNER_REQUIRED_COMPLETENESS   -> required completeness ratio (default 0.97)
    SCANNER_MAX_FAILURE_RATIO       -> max acceptable failure ratio (default 0.05)
    SCANNER_RUNTIME_TARGET_SEC      -> runtime target in seconds (default 180)

The script forces `SCANNER_INCLUDE_PAYLOADS=1` so that raw payloads are returned
from `scan_batch` for analysis. No external side effects (file writes / DB writes)
occur.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fast_stock_scanner import StockScanner, load_combined_tickers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exercise the batch scanner across the NYSE+NASDAQ universe and report field completeness metrics."
    )
    parser.add_argument("--threads", type=int, default=40, help="Thread pool size for network work (default: 40)")
    parser.add_argument("--timeout", type=int, default=8, help="Per-request timeout in seconds (default: 8)")
    parser.add_argument("--chunk-size", type=int, default=250, help="Batch chunk size passed to scan_batch (default: 250)")
    parser.add_argument("--max-tickers", type=int, default=None, help="Optional cap on number of tickers to evaluate (for smoke tests)")
    parser.add_argument("--use-proxies", action="store_true", help="Enable proxy usage (reads proxies from --proxy-file)")
    parser.add_argument("--proxy-file", default="working_proxies.json", help="Proxy JSON file path (default: working_proxies.json)")
    parser.add_argument("--disable-denylist", action="store_true", help="Disable auto denylist filtering during the run")
    parser.add_argument(
        "--fields",
        nargs="*",
        default=None,
        help="Specific payload fields to analyse. Defaults to all non-internal fields returned by the scanner.",
    )
    parser.add_argument("--print-json", action="store_true", help="Print metrics as JSON instead of human-readable text")
    parser.add_argument("--show-top-failures", type=int, default=25, help="How many failing symbols to display (default: 25)")
    return parser.parse_args()


def normalise_env(args: argparse.Namespace) -> None:
    """Set runtime environment knobs before instantiating the scanner."""

    os.environ.setdefault("SCANNER_INCLUDE_PAYLOADS", "1")
    os.environ["SCANNER_BATCH_CHUNK"] = str(max(1, args.chunk_size))
    # Ensure we do not persist results in any way
    os.environ.setdefault("SCANNER_ENRICH_FASTINFO", "1")
    if args.disable_denylist:
        os.environ["SCANNER_USE_DENYLIST"] = "0"


def build_field_list(payloads: Dict[str, Dict[str, Any]], explicit_fields: Iterable[str] | None) -> List[str]:
    if explicit_fields:
        return [f.strip() for f in explicit_fields if f and f.strip()]
    field_names = set()
    for payload in payloads.values():
        for key in payload.keys():
            if not key or key.startswith("_"):
                continue
            field_names.add(str(key))
    return sorted(field_names)


def compute_field_failures(
    symbols: List[str],
    payloads: Dict[str, Dict[str, Any]],
    fields: List[str],
) -> Dict[str, Dict[str, Any]]:
    totals = len(symbols)
    failures: Dict[str, Dict[str, Any]] = {}
    for field in fields:
        missing = 0
        present = 0
        for sym in symbols:
            payload = payloads.get(sym)
            value = None if payload is None else payload.get(field)
            if value is None:
                missing += 1
            else:
                present += 1
        pct_missing = (missing / totals * 100.0) if totals else 0.0
        pct_present = (present / totals * 100.0) if totals else 0.0
        failures[field] = {
            "missing": missing,
            "missing_pct": pct_missing,
            "present": present,
            "present_pct": pct_present,
        }
    return failures


def safe_json_dump(data: Dict[str, Any]) -> str:
    def _default(obj: Any) -> Any:
        try:
            import decimal
            import datetime
        except Exception:  # pragma: no cover
            decimal = None  # type: ignore
            datetime = None  # type: ignore

        if decimal and isinstance(obj, decimal.Decimal):
            return float(obj)
        if datetime:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if isinstance(obj, datetime.date):
                return obj.isoformat()
        return str(obj)

    return json.dumps(data, default=_default, indent=2, sort_keys=True)


def main() -> int:
    args = parse_args()
    normalise_env(args)

    scanner = StockScanner(
        threads=args.threads,
        timeout=args.timeout,
        proxy_file=args.proxy_file,
        use_proxies=args.use_proxies,
        db_enabled=False,
    )

    symbols = load_combined_tickers()
    if args.max_tickers is not None:
        symbols = symbols[: max(0, args.max_tickers)]

    if not symbols:
        print("No symbols available for scanning.", file=sys.stderr)
        return 1

    run_start = time.time()
    stats = scanner.scan_batch(symbols, csv_out=None, chunk_size=args.chunk_size)
    elapsed = time.time() - run_start

    payloads = stats.get("payloads")
    if payloads is None:
        print("scan_batch did not return payloads; ensure SCANNER_INCLUDE_PAYLOADS=1", file=sys.stderr)
        return 2

    fields = build_field_list(payloads, args.fields)
    field_failures = compute_field_failures(symbols, payloads, fields)

    report = {
        "total_tickers": len(symbols),
        "success": stats.get("success"),
        "failed": stats.get("failed"),
        "failure_ratio": stats.get("failure_ratio"),
        "completeness_ratio": stats.get("completeness_ratio"),
        "duration_sec": stats.get("duration_sec"),
        "measured_duration_sec": round(elapsed, 2),
        "rate_per_sec": stats.get("rate_per_sec"),
        "runtime_target_sec": stats.get("runtime_target_sec"),
        "runtime_target_met": stats.get("runtime_target_met"),
        "required_completeness_ratio": stats.get("required_completeness_ratio"),
        "completeness_target_met": stats.get("completeness_target_met"),
        "max_failure_ratio": stats.get("max_failure_ratio"),
        "failure_ratio_target_met": stats.get("failure_ratio_target_met"),
        "proxies_available": stats.get("proxies_available"),
        "skipped_from_denylist": stats.get("skipped_from_denylist"),
        "rate_limited_chunks": stats.get("rate_limited_chunks"),
        "proxy_rotations": stats.get("proxy_rotations"),
        "batch_quote_results": stats.get("batch_quote_results"),
        "fallback_recovered": stats.get("fallback_recovered"),
        "field_failures": field_failures,
        "failed_symbols_sample": stats.get("failed_symbols_sample", []),
        "missing_symbols_sample": stats.get("missing_symbols_sample", []),
    }

    if args.print_json:
        # Remove heavy payload data before serialising
        return_payloads = safe_json_dump(report)
        print(return_payloads)
    else:
        print("=== Full Universe Batch Scan Test ===")
        print(f"Total tickers evaluated: {report['total_tickers']}")
        print(
            "Overall success: {success}/{total} ({ratio:.2%}) | Failures: {failed} ({fail_ratio:.2%})".format(
                success=report.get("success", 0),
                total=report["total_tickers"],
                ratio=report.get("completeness_ratio", 0.0) if report.get("completeness_ratio") is not None else 0.0,
                failed=report.get("failed", 0),
                fail_ratio=report.get("failure_ratio", 0.0) if report.get("failure_ratio") is not None else 0.0,
            )
        )
        print(
            "Runtime: {dur}s (measured {measured}s) | Target {target}s -> {met}".format(
                dur=report.get("duration_sec", "?"),
                measured=report.get("measured_duration_sec", "?"),
                target=report.get("runtime_target_sec", "?"),
                met="OK" if report.get("runtime_target_met") else "NOT MET",
            )
        )
        print(
            "Completeness target {req:.2%}: {met}".format(
                req=report.get("required_completeness_ratio", 0.0) if report.get("required_completeness_ratio") is not None else 0.0,
                met="OK" if report.get("completeness_target_met") else "NOT MET",
            )
        )
        print(
            "Failure ratio target {max_fail:.2%}: {met}".format(
                max_fail=report.get("max_failure_ratio", 0.0) if report.get("max_failure_ratio") is not None else 0.0,
                met="OK" if report.get("failure_ratio_target_met") else "NOT MET",
            )
        )
        print(f"Proxies available: {report.get('proxies_available', 0)} | Rate limited chunks: {report.get('rate_limited_chunks', 0)} | Proxy rotations: {report.get('proxy_rotations', 0)}")
        if report.get("skipped_from_denylist"):
            print(f"Skipped from denylist: {report['skipped_from_denylist']}")
        print("\nField completeness (sorted by highest missing %):")
        sorted_fields = sorted(field_failures.items(), key=lambda item: item[1]["missing_pct"], reverse=True)
        for field, metrics in sorted_fields:
            print(
                "  {field:25s} missing {missing:6d} ({missing_pct:6.2f}%) | present {present:6d} ({present_pct:6.2f}%)".format(
                    field=field,
                    missing=metrics["missing"],
                    missing_pct=metrics["missing_pct"],
                    present=metrics["present"],
                    present_pct=metrics["present_pct"],
                )
            )
        top_fail = report.get("failed_symbols_sample", [])[: max(0, args.show_top_failures)]
        if top_fail:
            print("\nSample failing tickers:")
            print(", ".join(top_fail))
        missing_sample = report.get("missing_symbols_sample", [])[: max(0, args.show_top_failures)]
        if missing_sample:
            print("\nSymbols missing after both passes (sample):")
            print(", ".join(missing_sample))

    return 0


if __name__ == "__main__":
    sys.exit(main())
