#!/usr/bin/env python3
"""
Combine Stooq .txt files (from extracted folders or zip files) into a single normalized CSV.

Supports lines like:
  ACCS.US,60,20240514,220000,10,10.08,9.99,10.08,10776,0

Output columns:
  symbol,datetime,open,high,low,close,volume,interval

Examples (Windows):
  py scripts\\stooq_combine.py ^
    --input "C:\\Users\\Carterpc\\Downloads\\h_us_txt.zip" ^
    --output "C:\\Users\\Carterpc\\Downloads\\stooq_hourly_combined.csv"

  py scripts\\stooq_combine.py ^
    --input "C:\\Users\\Carterpc\\Downloads\\h_us_txt.zip\\data\\hourly\\us\\nyse stocks\\1" ^
    --input "C:\\Users\\Carterpc\\Downloads\\d_us_txt.zip" ^
    --output "C:\\Users\\Carterpc\\Downloads\\stooq_all_combined.csv"
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, Optional, TextIO, Tuple


@dataclass(frozen=True)
class ParsedRow:
    symbol: str
    dt: datetime
    o: float
    h: float
    l: float
    c: float
    v: int
    interval: str  # "D" or minutes like "60"/"5"


def _symbol_from_filename(path: str) -> Optional[str]:
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    if not name:
        return None
    # Common Stooq naming is SYMBOL.txt (already includes .US in the symbol).
    return name.strip().upper()


def _parse_stooq_line(fields: list[str], *, default_symbol: Optional[str]) -> Optional[ParsedRow]:
    """
    Supported shapes:
    - 10 fields (intraday): symbol, interval, yyyymmdd, hhmmss, open, high, low, close, volume, openint
    - 8 fields (daily w/ symbol): symbol, yyyymmdd, open, high, low, close, volume, openint
    - 7 fields (daily no symbol): yyyymmdd, open, high, low, close, volume, openint  (symbol from filename)
    - 6 fields (daily no openint): yyyymmdd, open, high, low, close, volume        (symbol from filename)
    """
    # Trim whitespace
    fields = [f.strip() for f in fields if f is not None]
    if not fields:
        return None

    try:
        if len(fields) == 10:
            sym, interval, ymd, hms, o, h, l, c, v, _oi = fields
            dt = datetime.strptime(f"{ymd}{hms}", "%Y%m%d%H%M%S")
            return ParsedRow(
                symbol=sym.strip().upper(),
                dt=dt,
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
                v=int(float(v)),
                interval=str(interval).strip(),
            )

        if len(fields) == 8:
            sym, ymd, o, h, l, c, v, _oi = fields
            dt = datetime.strptime(ymd, "%Y%m%d")
            return ParsedRow(
                symbol=sym.strip().upper(),
                dt=dt,
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
                v=int(float(v)),
                interval="D",
            )

        if len(fields) == 7:
            if not default_symbol:
                return None
            ymd, o, h, l, c, v, _oi = fields
            dt = datetime.strptime(ymd, "%Y%m%d")
            return ParsedRow(
                symbol=default_symbol,
                dt=dt,
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
                v=int(float(v)),
                interval="D",
            )

        if len(fields) == 6:
            if not default_symbol:
                return None
            ymd, o, h, l, c, v = fields
            dt = datetime.strptime(ymd, "%Y%m%d")
            return ParsedRow(
                symbol=default_symbol,
                dt=dt,
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
                v=int(float(v)),
                interval="D",
            )
    except Exception:
        return None

    return None


def _iter_txt_paths_in_dir(root: str) -> Iterator[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".txt"):
                yield os.path.join(dirpath, fn)


def _iter_txt_members_in_zip(z: zipfile.ZipFile) -> Iterator[str]:
    for name in z.namelist():
        if name.lower().endswith(".txt") and not name.endswith("/"):
            yield name


def _open_input_text(path: str) -> Tuple[str, Iterable[Tuple[str, TextIO]]]:
    """
    Return (kind, iterable) where kind is 'dir' or 'zip', and iterable yields (logical_name, fileobj).
    """
    if os.path.isdir(path):
        def _gen() -> Iterator[Tuple[str, TextIO]]:
            for fp in _iter_txt_paths_in_dir(path):
                yield fp, open(fp, "r", encoding="utf-8", errors="ignore")

        return "dir", _gen()

    if path.lower().endswith(".zip") and os.path.isfile(path):
        zf = zipfile.ZipFile(path)

        def _gen() -> Iterator[Tuple[str, TextIO]]:
            for member in _iter_txt_members_in_zip(zf):
                # ZipExtFile is binary; wrap with TextIOWrapper
                f = zf.open(member, "r")
                import io

                yield member, io.TextIOWrapper(f, encoding="utf-8", errors="ignore")

        return "zip", _gen()

    # Also support passing an extracted path inside a zip "like ...zip\\data\\...".
    # If that folder exists on disk, it will be treated as a dir above. Otherwise error.
    raise FileNotFoundError(f"Input path not found or unsupported: {path}")


def combine(inputs: list[str], output_csv: str, *, interval_filter: Optional[str] = None) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)) or ".", exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
        w = csv.writer(out_f)
        w.writerow(["symbol", "datetime", "open", "high", "low", "close", "volume", "interval"])

        total = 0
        kept = 0

        for inp in inputs:
            kind, iterable = _open_input_text(inp)
            for logical_name, f in iterable:
                default_symbol = _symbol_from_filename(logical_name)
                try:
                    reader = csv.reader(f, delimiter=",")
                    for row in reader:
                        total += 1
                        parsed = _parse_stooq_line(row, default_symbol=default_symbol)
                        if not parsed:
                            continue
                        if interval_filter is not None and str(parsed.interval) != str(interval_filter):
                            continue
                        w.writerow(
                            [
                                parsed.symbol,
                                parsed.dt.strftime("%Y-%m-%d %H:%M:%S"),
                                f"{parsed.o:.6f}",
                                f"{parsed.h:.6f}",
                                f"{parsed.l:.6f}",
                                f"{parsed.c:.6f}",
                                str(parsed.v),
                                str(parsed.interval),
                            ]
                        )
                        kept += 1
                finally:
                    try:
                        f.close()
                    except Exception:
                        pass

        print(f"Done. Read {total} rows, wrote {kept} rows to {output_csv}")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Combine Stooq .txt files into a single CSV.")
    p.add_argument("--input", action="append", required=True, help="Input folder OR .zip file. Can be provided multiple times.")
    p.add_argument("--output", required=True, help="Output CSV path.")
    p.add_argument(
        "--interval",
        default=None,
        help='Optional interval filter. Examples: "60" (hourly), "5" (5-min), "D" (daily).',
    )

    args = p.parse_args(argv)
    combine(args.input, args.output, interval_filter=args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

