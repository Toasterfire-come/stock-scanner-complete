#!/usr/bin/env python3
"""Batch proxy tester.

Scans the repository for JSON files containing proxy lists (default: *proxies*.json),
extracts the proxy endpoints, and issues 10 test HTTP requests through each proxy.

Usage examples
--------------

    # Test every proxy file using the default target URL (https://httpbin.org/get)
    python3 backend/tools/proxy_tester.py

    # Test a custom list of files and write detailed metrics to JSON
    python3 backend/tools/proxy_tester.py \
        --files backend/working_proxies.json new_proxies.json \
        --target https://api.ipify.org \
        --output proxy_metrics.json

Results are printed as a table and optionally written to JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import requests


DEFAULT_GLOB = "*_proxies*.json"
DEFAULT_TARGET = "https://httpbin.org/get"
DEFAULT_ATTEMPTS = 10
DEFAULT_TIMEOUT = 6.0


@dataclass
class AttemptResult:
    succeeded: bool
    status_code: Optional[int]
    latency_ms: Optional[float]
    error: Optional[str]


@dataclass
class ProxyReport:
    proxy: str
    attempts: List[AttemptResult]

    @property
    def success_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.attempts) - self.success_count

    @property
    def success_rate(self) -> float:
        total = len(self.attempts)
        return (self.success_count / total) * 100.0 if total else 0.0

    @property
    def avg_latency_ms(self) -> Optional[float]:
        latencies = [attempt.latency_ms for attempt in self.attempts if attempt.latency_ms is not None]
        return sum(latencies) / len(latencies) if latencies else None


def discover_proxy_files(root: Path, glob_pattern: str) -> List[Path]:
    return sorted(path for path in root.glob(glob_pattern) if path.is_file())


def load_proxies_from_json(path: Path) -> List[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to read {path}: {exc}") from exc

    proxies: List[str] = []
    if isinstance(payload, list):
        proxies = [str(item).strip() for item in payload if isinstance(item, str) and str(item).strip()]
    elif isinstance(payload, dict):
        for key in ("proxies", "working_proxies", "healthy_proxies"):
            value = payload.get(key)
            if isinstance(value, list):
                proxies.extend(str(item).strip() for item in value if isinstance(item, str) and str(item).strip())
        if not proxies:
            proxies.extend(
                str(value).strip()
                for value in payload.values()
                if isinstance(value, str) and str(value).strip()
            )
    else:
        raise RuntimeError(f"Unsupported JSON structure in {path}")

    normalized: List[str] = []
    seen: Set[str] = set()
    for proxy in proxies:
        value = proxy if "://" in proxy else f"http://{proxy}"
        if value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def test_proxy(proxy: str, target: str, attempts: int, timeout: float) -> ProxyReport:
    results: List[AttemptResult] = []
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    headers = {"User-Agent": "ProxyTester/1.0"}

    for _ in range(attempts):
        start = time.perf_counter()
        try:
            resp = session.get(target, headers=headers, timeout=timeout)
            latency_ms = (time.perf_counter() - start) * 1000.0
            succeeded = resp.ok
            error = None if succeeded else f"HTTP {resp.status_code}"
            results.append(
                AttemptResult(
                    succeeded=succeeded,
                    status_code=resp.status_code,
                    latency_ms=latency_ms,
                    error=error,
                )
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000.0
            results.append(
                AttemptResult(
                    succeeded=False,
                    status_code=None,
                    latency_ms=latency_ms,
                    error=str(exc),
                )
            )
    return ProxyReport(proxy=proxy, attempts=results)


def aggregate_reports(reports: Iterable[ProxyReport]) -> Dict[str, ProxyReport]:
    return {report.proxy: report for report in reports}


def print_summary(file_to_proxies: Dict[Path, List[str]], reports: Dict[str, ProxyReport]) -> None:
    print("\n=== Proxy Test Summary ===")
    for file_path, proxies in file_to_proxies.items():
        if not proxies:
            print(f"{file_path}: no proxies found")
            continue
        print(f"{file_path} ({len(proxies)} proxies)")
        for proxy in proxies:
            report = reports.get(proxy)
            if not report:
                print(f"  {proxy}: not tested")
                continue
            avg_latency = report.avg_latency_ms
            latency_str = f"{avg_latency:.1f} ms" if avg_latency is not None else "n/a"
            print(
                f"  {proxy}: success={report.success_count}/{len(report.attempts)} "
                f"({report.success_rate:.1f}%), avg_latency={latency_str}"
            )


def write_output(path: Path, reports: Dict[str, ProxyReport]) -> None:
    serializable = {proxy: [asdict(attempt) for attempt in report.attempts] for proxy, report in reports.items()}
    path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test proxies by issuing multiple HTTP requests")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to scan for proxy files (default: current working directory)",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default=DEFAULT_GLOB,
        help=f"Glob pattern to find proxy JSON files (default: {DEFAULT_GLOB})",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Explicit proxy JSON files to test (overrides --glob)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=DEFAULT_TARGET,
        help=f"HTTP URL to request via each proxy (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=DEFAULT_ATTEMPTS,
        help=f"Number of requests per proxy (default: {DEFAULT_ATTEMPTS})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds for each request (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON file to write detailed attempt metrics",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    if args.files:
        proxy_files = [Path(file) for file in args.files]
    else:
        proxy_files = discover_proxy_files(args.root, args.glob)

    if not proxy_files:
        print("No proxy JSON files found.")
        return 1

    file_to_proxies: Dict[Path, List[str]] = {}
    all_proxies: Set[str] = set()

    for file_path in proxy_files:
        try:
            proxies = load_proxies_from_json(file_path)
        except Exception as exc:
            print(f"Skipping {file_path}: {exc}")
            continue
        file_to_proxies[file_path] = proxies
        all_proxies.update(proxies)

    if not all_proxies:
        print("No proxies extracted from the selected files.")
        return 1

    reports: Dict[str, ProxyReport] = {}
    for proxy in sorted(all_proxies):
        print(f"Testing proxy {proxy} ...", flush=True)
        reports[proxy] = test_proxy(proxy, args.target, args.attempts, args.timeout)

    print_summary(file_to_proxies, reports)

    if args.output:
        write_output(args.output, reports)
        print(f"Detailed metrics written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

