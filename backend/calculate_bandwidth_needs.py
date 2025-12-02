#!/usr/bin/env python3
"""
Calculate bandwidth requirements for Yahoo Finance stock scanning
"""

# Yahoo Finance API Response Sizes (estimated from testing)
RESPONSE_SIZES = {
    'fast_info': 2_000,      # ~2 KB per fast_info response
    'info': 15_000,          # ~15 KB per full info response
    'chart_data': 5_000,     # ~5 KB per chart endpoint
}

# Your requirements
TOTAL_TICKERS = 5193
DAILY_UPDATES = 1  # How many times per day you scan all tickers
MONTHLY_DAYS = 30

# Calculation assumptions
FAST_INFO_SUCCESS_RATE = 0.70  # 70% succeed with fast_info
INFO_FALLBACK_RATE = 0.30      # 30% need full info fallback
OVERHEAD_MULTIPLIER = 1.3      # 30% overhead for HTTP headers, retries, etc.

print("="*70)
print("BANDWIDTH CALCULATION FOR YAHOO FINANCE STOCK SCANNER")
print("="*70)
print()

# Single scan bandwidth
print("SINGLE SCAN (all 5,193 tickers once):")
print("-"*70)

fast_info_requests = TOTAL_TICKERS * FAST_INFO_SUCCESS_RATE
info_requests = TOTAL_TICKERS * INFO_FALLBACK_RATE

fast_info_bandwidth = fast_info_requests * RESPONSE_SIZES['fast_info']
info_bandwidth = info_requests * RESPONSE_SIZES['info']

total_single_scan = (fast_info_bandwidth + info_bandwidth) * OVERHEAD_MULTIPLIER

print(f"Fast_info requests: {fast_info_requests:.0f} × {RESPONSE_SIZES['fast_info']:,} bytes")
print(f"  = {fast_info_bandwidth:,.0f} bytes ({fast_info_bandwidth/1024/1024:.2f} MB)")
print()
print(f"Info fallback requests: {info_requests:.0f} × {RESPONSE_SIZES['info']:,} bytes")
print(f"  = {info_bandwidth:,.0f} bytes ({info_bandwidth/1024/1024:.2f} MB)")
print()
print(f"Subtotal: {(fast_info_bandwidth + info_bandwidth)/1024/1024:.2f} MB")
print(f"With {(OVERHEAD_MULTIPLIER-1)*100:.0f}% overhead: {total_single_scan/1024/1024:.2f} MB per scan")
print()

# Daily bandwidth
print("DAILY BANDWIDTH:")
print("-"*70)
daily_bandwidth = total_single_scan * DAILY_UPDATES
print(f"Single scan: {total_single_scan/1024/1024:.2f} MB")
print(f"Updates per day: {DAILY_UPDATES}")
print(f"Total per day: {daily_bandwidth/1024/1024:.2f} MB")
print()

# Monthly bandwidth
print("MONTHLY BANDWIDTH:")
print("-"*70)
monthly_bandwidth = daily_bandwidth * MONTHLY_DAYS
print(f"Daily: {daily_bandwidth/1024/1024:.2f} MB")
print(f"Days per month: {MONTHLY_DAYS}")
print(f"Total per month: {monthly_bandwidth/1024/1024:.2f} MB ({monthly_bandwidth/1024/1024/1024:.3f} GB)")
print()

# Your available bandwidth
print("YOUR AVAILABLE BANDWIDTH:")
print("-"*70)
accounts = 10
bandwidth_per_account_gb = 1
total_available_gb = accounts * bandwidth_per_account_gb
total_available_bytes = total_available_gb * 1024 * 1024 * 1024

print(f"Accounts: {accounts}")
print(f"Bandwidth per account: {bandwidth_per_account_gb} GB")
print(f"Total available: {total_available_gb} GB ({total_available_bytes:,} bytes)")
print()

# Comparison
print("ANALYSIS:")
print("="*70)
usage_gb = monthly_bandwidth / 1024 / 1024 / 1024
remaining_gb = total_available_gb - usage_gb
usage_percent = (usage_gb / total_available_gb) * 100

print(f"Monthly usage: {usage_gb:.3f} GB")
print(f"Available: {total_available_gb} GB")
print(f"Remaining: {remaining_gb:.3f} GB")
print(f"Usage: {usage_percent:.1f}%")
print()

if usage_gb <= total_available_gb:
    print("✓ SUFFICIENT BANDWIDTH")
    print(f"  You have {remaining_gb:.2f} GB buffer ({(1 - usage_percent/100)*100:.1f}% unused)")

    # Calculate how many scans you could do
    scans_possible = total_available_gb * 1024 / (total_single_scan/1024/1024)
    scans_per_day = scans_possible / MONTHLY_DAYS

    print(f"  Maximum possible scans per month: {scans_possible:.0f}")
    print(f"  Maximum scans per day: {scans_per_day:.1f}")

    if scans_per_day >= 4:
        print(f"  ✓ You can scan every 6 hours (4× daily)")
    elif scans_per_day >= 2:
        print(f"  ✓ You can scan every 12 hours (2× daily)")
    elif scans_per_day >= 1:
        print(f"  ✓ You can scan once daily")
    else:
        print(f"  ⚠ Limited to less than daily scans")
else:
    shortfall_gb = usage_gb - total_available_gb
    print("✗ INSUFFICIENT BANDWIDTH")
    print(f"  Shortfall: {shortfall_gb:.2f} GB")
    print(f"  Need {(usage_gb/total_available_gb):.1f}× more bandwidth")
    print()
    print("  Options:")
    print(f"  1. Reduce scan frequency to {total_available_gb/usage_gb:.1f}× per month")
    print(f"  2. Get {(usage_gb/bandwidth_per_account_gb):.0f} accounts instead of {accounts}")

print()
print("="*70)
print("DIFFERENT SCAN FREQUENCIES:")
print("="*70)

for scans_per_day in [1, 2, 4, 8, 24]:
    daily_usage = total_single_scan * scans_per_day / 1024 / 1024
    monthly_usage = daily_usage * MONTHLY_DAYS / 1024
    fits = "✓" if monthly_usage <= total_available_gb else "✗"
    print(f"{fits} {scans_per_day:2d}× daily: {monthly_usage:6.2f} GB/month ({daily_usage:5.1f} MB/day)")

print()
print("="*70)
print("RECOMMENDATIONS:")
print("="*70)
print()
print("1. Start with 1× daily scans to stay well within limits")
print("2. Monitor actual bandwidth usage (may be lower than estimates)")
print("3. Adjust scan frequency based on real usage")
print("4. Keep 20-30% buffer for retries and failed requests")
print()
