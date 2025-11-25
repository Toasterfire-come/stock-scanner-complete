#!/usr/bin/env python3
"""
Rate Limit Calculator - Shows when you'll hit Yahoo Finance rate limits
"""

import sys


class RateLimitCalculator:
    """Calculate when you'll hit rate limits based on your usage"""

    # Conservative estimates based on community reports
    HOURLY_LIMIT_LOW = 200   # Conservative limit
    HOURLY_LIMIT_HIGH = 1000  # Optimistic limit
    DAILY_LIMIT_LOW = 500
    DAILY_LIMIT_HIGH = 2000

    def __init__(self):
        pass

    def analyze_scenario(self, stocks: int, scans_per_day: int = 1):
        """Analyze a specific scanning scenario"""
        print("\n" + "=" * 70)
        print(f"  SCENARIO: {stocks} stocks × {scans_per_day} scan(s) per day")
        print("=" * 70)

        total_daily_requests = stocks * scans_per_day
        requests_per_hour = total_daily_requests / (24 / scans_per_day) if scans_per_day <= 24 else total_daily_requests

        print(f"\n📊 Request Volume:")
        print(f"   Stocks per scan: {stocks:,}")
        print(f"   Scans per day: {scans_per_day}")
        print(f"   Total daily requests: {total_daily_requests:,}")
        print(f"   Requests per hour: ~{int(requests_per_hour):,}")

        # Analyze risk
        print(f"\n⚠️  Rate Limit Risk Analysis:")

        # Hourly risk
        if requests_per_hour < self.HOURLY_LIMIT_LOW:
            hourly_risk = "🟢 LOW"
            hourly_msg = "Well below typical limits"
        elif requests_per_hour < self.HOURLY_LIMIT_HIGH:
            hourly_risk = "🟡 MEDIUM"
            hourly_msg = "May hit limits on conservative networks"
        else:
            hourly_risk = "🔴 HIGH"
            hourly_msg = "Will likely hit hourly limits"

        print(f"   Hourly: {hourly_risk} - {hourly_msg}")
        print(f"           ({int(requests_per_hour):,} req/hr vs {self.HOURLY_LIMIT_LOW}-{self.HOURLY_LIMIT_HIGH} limit)")

        # Daily risk
        if total_daily_requests < self.DAILY_LIMIT_LOW:
            daily_risk = "🟢 LOW"
            daily_msg = "Safe for daily scanning"
        elif total_daily_requests < self.DAILY_LIMIT_HIGH:
            daily_risk = "🟡 MEDIUM"
            daily_msg = "Approaching daily limits"
        else:
            daily_risk = "🔴 HIGH"
            daily_msg = "Will hit daily limits"

        print(f"   Daily:  {daily_risk} - {daily_msg}")
        print(f"           ({total_daily_requests:,} req/day vs {self.DAILY_LIMIT_LOW}-{self.DAILY_LIMIT_HIGH} limit)")

        # Overall risk
        if hourly_risk == "🟢 LOW" and daily_risk == "🟢 LOW":
            overall_risk = "🟢 SAFE"
        elif "🔴 HIGH" in [hourly_risk, daily_risk]:
            overall_risk = "🔴 WILL BE RATE LIMITED"
        else:
            overall_risk = "🟡 MAY HIT LIMITS"

        print(f"\n   Overall: {overall_risk}")

        # Recommendation
        print(f"\n💡 Recommendation:")
        if overall_risk == "🟢 SAFE":
            print("   ✅ Use direct connection (no proxies needed)")
            print("   ✅ Simple, fast, and reliable")
            print(f"   Command: python3 enhanced_scanner_with_proxies.py --no-proxies")

        elif overall_risk == "🟡 MAY HIT LIMITS":
            print("   ⚠️  Start with direct connection, monitor for 429 errors")
            print("   ⚠️  Have backup plan ready (split batches or proxies)")

            # Calculate batch split
            batches_needed = max(2, int(total_daily_requests / self.DAILY_LIMIT_LOW) + 1)
            stocks_per_batch = stocks // batches_needed

            print(f"\n   Alternative: Split into {batches_needed} batches of ~{stocks_per_batch} stocks each")
            print(f"   - Batch 1 (morning):   stocks 0-{stocks_per_batch}")
            for i in range(1, batches_needed - 1):
                start = i * stocks_per_batch
                end = (i + 1) * stocks_per_batch
                print(f"   - Batch {i+1} (midday):    stocks {start}-{end}")
            print(f"   - Batch {batches_needed} (evening):   stocks {(batches_needed-1)*stocks_per_batch}-{stocks}")

        else:  # HIGH risk
            print("   🔴 WILL be rate limited - need proxies or batching")

            # Calculate batch split
            batches_needed = max(3, int(total_daily_requests / self.DAILY_LIMIT_LOW) + 1)
            stocks_per_batch = stocks // batches_needed

            print(f"\n   Option 1: Split into {batches_needed}+ batches across the day")
            print(f"             ~{stocks_per_batch} stocks per batch")

            # Calculate proxies needed
            proxies_needed = max(1, int(total_daily_requests / self.HOURLY_LIMIT_LOW))
            print(f"\n   Option 2: Use proxy rotation")
            print(f"             Need: ~{proxies_needed} working proxies")
            print(f"             Cost: ~${proxies_needed * 2}-${proxies_needed * 5}/month (paid service)")

        # Time to hit limit
        print(f"\n⏱️  Time Until Rate Limited:")
        minutes_to_limit_low = int((self.HOURLY_LIMIT_LOW / requests_per_hour) * 60) if requests_per_hour > 0 else 999
        minutes_to_limit_high = int((self.HOURLY_LIMIT_HIGH / requests_per_hour) * 60) if requests_per_hour > 0 else 999

        if minutes_to_limit_high >= 60:
            print(f"   {minutes_to_limit_low}-{minutes_to_limit_high}+ minutes (safe)")
        elif minutes_to_limit_high >= 30:
            print(f"   {minutes_to_limit_low}-{minutes_to_limit_high} minutes (monitor closely)")
        else:
            print(f"   {minutes_to_limit_low}-{minutes_to_limit_high} minutes (high risk)")

    def show_common_scenarios(self):
        """Show analysis for common scenarios"""
        print("\n" + "=" * 70)
        print("  COMMON SCANNING SCENARIOS")
        print("=" * 70)

        scenarios = [
            (50, 1, "Small daily scan"),
            (100, 1, "Small-medium daily scan"),
            (500, 1, "Medium daily scan"),
            (1000, 1, "Large daily scan"),
            (2000, 1, "Very large daily scan"),
            (5000, 1, "Full market scan"),
            (100, 3, "Multiple daily scans (100 stocks, 3x/day)"),
            (500, 2, "Multiple daily scans (500 stocks, 2x/day)"),
            (100, 24, "Hourly monitoring (100 stocks)"),
        ]

        for stocks, scans, description in scenarios:
            print(f"\n{'─' * 70}")
            print(f"Scenario: {description}")
            self.analyze_scenario(stocks, scans)

    def interactive_calculator(self):
        """Interactive calculator for custom scenarios"""
        print("\n" + "=" * 70)
        print("  CUSTOM RATE LIMIT CALCULATOR")
        print("=" * 70)

        try:
            stocks = int(input("\nHow many stocks do you want to scan? "))
            scans_per_day = int(input("How many times per day? "))

            self.analyze_scenario(stocks, scans_per_day)

        except (ValueError, KeyboardInterrupt):
            print("\nInvalid input or cancelled.")
            return


def show_proxy_comparison():
    """Show how proxies help with rate limits"""
    print("\n" + "=" * 70)
    print("  HOW PROXIES HELP WITH RATE LIMITS")
    print("=" * 70)

    print("\n📊 WITHOUT PROXIES (Direct Connection)")
    print("   ┌─────────────┐")
    print("   │   Your IP   │")
    print("   └──────┬──────┘")
    print("          │")
    print("          │  All requests from ONE IP")
    print("          │")
    print("   ┌──────▼──────────────────────┐")
    print("   │   Yahoo Finance             │")
    print("   │   Rate Limiter              │")
    print("   │                             │")
    print("   │   Tracking: Your IP         │")
    print("   │   Requests: 1000/hour       │")
    print("   │   Status: 🔴 RATE LIMITED   │")
    print("   └─────────────────────────────┘")

    print("\n📊 WITH PROXY ROTATION")
    print("   ┌─────────────┐")
    print("   │   Your IP   │")
    print("   └──────┬──────┘")
    print("          │")
    print("          ├─→ Proxy A ──→ Request 1, 11, 21...")
    print("          │")
    print("          ├─→ Proxy B ──→ Request 2, 12, 22...")
    print("          │")
    print("          └─→ Proxy C ──→ Request 3, 13, 23...")
    print("                    │")
    print("   ┌────────────────▼─────────────┐")
    print("   │   Yahoo Finance              │")
    print("   │   Rate Limiter               │")
    print("   │                              │")
    print("   │   Tracking: Proxy A (33/hr)  │")
    print("   │   Tracking: Proxy B (33/hr)  │")
    print("   │   Tracking: Proxy C (34/hr)  │")
    print("   │   Status: ✅ ALL UNDER LIMIT │")
    print("   └──────────────────────────────┘")

    print("\n💡 Key Insight:")
    print("   Each proxy has its own rate limit!")
    print("   10 proxies × 200 req/hr = 2,000 req/hr total capacity")
    print("   50 proxies × 200 req/hr = 10,000 req/hr total capacity")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Calculate when you\'ll hit Yahoo Finance rate limits'
    )
    parser.add_argument('--stocks', type=int, help='Number of stocks to scan')
    parser.add_argument('--scans-per-day', type=int, default=1,
                       help='Number of scans per day')
    parser.add_argument('--common', action='store_true',
                       help='Show common scenarios')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive calculator')

    args = parser.parse_args()

    calculator = RateLimitCalculator()

    # Show proxy comparison
    show_proxy_comparison()

    if args.common:
        calculator.show_common_scenarios()

    elif args.interactive:
        calculator.interactive_calculator()

    elif args.stocks:
        calculator.analyze_scenario(args.stocks, args.scans_per_day)

    else:
        # Default: show common scenarios
        calculator.show_common_scenarios()

    print("\n" + "=" * 70)
    print("  For more details, see: backend/RATE_LIMITS_EXPLAINED.md")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
