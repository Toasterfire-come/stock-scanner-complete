from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd

from .core import TrendsConfig, compute_latest_values, fetch_interest_over_time, fetch_related_queries


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch and compare Google Trends interest for keywords like 'stock scanner', "
            "'market scanner', and 'trade scanner'."
        )
    )

    parser.add_argument(
        "keywords",
        nargs="*",
        default=["stock scanner", "market scanner", "trade scanner"],
        help="Keywords to compare (default: stock scanner, market scanner, trade scanner)",
    )
    parser.add_argument(
        "--timeframe",
        default="today 5-y",
        help="Timeframe (e.g., 'today 12-m', 'today 5-y', 'now 7-d', 'all')",
    )
    parser.add_argument(
        "--geo",
        default="",
        help="Geographic code (e.g., '', 'US', 'GB', 'IN'). Empty means worldwide",
    )
    parser.add_argument(
        "--gprop",
        default="",
        choices=["", "images", "news", "youtube", "froogle"],
        help="Google property: web (''), images, news, youtube, froogle",
    )
    parser.add_argument(
        "--category",
        type=int,
        default=0,
        help="Google Trends category id (default 0)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional CSV path to save interest over time",
    )
    parser.add_argument(
        "--related",
        action="store_true",
        help="Also print related queries (top and rising) per keyword",
    )

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)

    config = TrendsConfig(
        keywords=args.keywords,
        timeframe=args.timeframe,
        geo=args.geo,
        gprop=args.gprop,
        category=args.category,
    )

    try:
        interest_df = fetch_interest_over_time(config)
    except RuntimeError as dependency_error:
        print(str(dependency_error), file=sys.stderr)
        return 2

    if interest_df.empty:
        print("No trends data returned for the requested parameters.")
        return 0

    # Print latest values snapshot
    latest = compute_latest_values(interest_df)
    print("Latest normalized interest (0-100):")
    for keyword, value in latest:
        print(f"- {keyword}: {value}")

    # Save CSV if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        interest_df.to_csv(out_path)
        print(f"Saved interest over time to {out_path}")

    # Related queries if requested
    if args.related:
        related = fetch_related_queries(config)
        for keyword, sections in related.items():
            print(f"\nRelated queries for: {keyword}")
            for section_name in ("top", "rising"):
                df = sections.get(section_name)
                print(f"  {section_name.title()}:")
                if df is None or df.empty:
                    print("    (none)")
                else:
                    # Show top 10 rows for brevity
                    subset = df.head(10)
                    # Indent lines for readability
                    csv_text = subset.to_csv(index=False).splitlines()
                    for line in csv_text:
                        print("    " + line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

