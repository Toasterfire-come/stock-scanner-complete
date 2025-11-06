#!/usr/bin/env python3
"""Quick health-check runner for the stock retrieval pipeline.

This script executes a dry-run batch against a limited ticker set, prints
progress every few seconds, and reports overall runtime plus quality metrics.
Use it to validate that recent changes still hit the ?180s / ?97% targets.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_TICKERS = 250
LOG_INTERVAL_SEC = 15


def run_health_check(max_tickers: int, threads: int, timeout: float) -> int:
    cmd = [
        sys.executable,
        "-m",
        "stock_retrieval",
        "--max-tickers",
        str(max_tickers),
        "--threads",
        str(threads),
        "--timeout",
        str(timeout),
        "--dry-run",
        "--json",
    ]

    print(f"Running: {' '.join(cmd)}")
    start = time.time()
    process = subprocess.Popen(
        cmd,
        cwd=Path(__file__).resolve().parents[2],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    last_log = start
    output_lines: list[str] = []

    assert process.stdout is not None
    for line in process.stdout:
        output_lines.append(line.rstrip())
        now = time.time()
        if now - last_log >= LOG_INTERVAL_SEC:
            elapsed = now - start
            print(f"[progress] {elapsed:.1f}s elapsed...")
            last_log = now

    process.wait()
    elapsed = time.time() - start
    print(f"Run completed in {elapsed:.1f}s with return code {process.returncode}")

    # Emit captured output
    for line in output_lines:
        print(line)

    return process.returncode or 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run stock retrieval health check")
    parser.add_argument("--max-tickers", type=int, default=DEFAULT_TICKERS)
    parser.add_argument("--threads", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=8.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_health_check(args.max_tickers, args.threads, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
