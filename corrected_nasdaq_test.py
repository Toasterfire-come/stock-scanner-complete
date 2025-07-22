#!/usr/bin/env python3
"""
CORRECTED NASDAQ Collection Test - Realistic API Usage
Shows the actual math for market hours only collection
"""

def calculate_realistic_usage():
    """Calculate realistic API usage with corrected math"""
    
    print("🧮 CORRECTED API Usage Calculation")
    print("=" * 50)
    
    # Market parameters
    total_stocks = 3331
    batch_size = 10
    collection_interval_minutes = 30
    market_hours_per_day = 6.5  # 9:30 AM - 4:00 PM ET
    trading_days_per_month = 22
    
    print(f"📊 Parameters:")
    print(f"   Total NASDAQ stocks: {total_stocks:,}")
    print(f"   Collection interval: {collection_interval_minutes} minutes")
    print(f"   Market hours per day: {market_hours_per_day} hours")
    print(f"   Trading days per month: {trading_days_per_month}")
    
    # Calculate collections per day
    collections_per_hour = 60 / collection_interval_minutes
    collections_per_day = collections_per_hour * market_hours_per_day
    
    print(f"\n⏰ Collection Frequency:")
    print(f"   Collections per hour: {collections_per_hour}")
    print(f"   Collections per day: {collections_per_day}")
    
    # API distribution strategy
    iex_account_1_stocks = 1750
    iex_account_2_stocks = 1581  # Remaining stocks (3331 - 1750)
    
    print(f"\n📡 API Distribution:")
    print(f"   IEX Account #1: {iex_account_1_stocks:,} stocks per collection")
    print(f"   IEX Account #2: {iex_account_2_stocks:,} stocks per collection")
    print(f"   Total coverage: {iex_account_1_stocks + iex_account_2_stocks:,} stocks")
    
    # Calculate daily API usage
    account_1_daily = iex_account_1_stocks * collections_per_day
    account_2_daily = iex_account_2_stocks * collections_per_day
    total_daily = account_1_daily + account_2_daily
    
    print(f"\n📈 Daily API Usage:")
    print(f"   Account #1: {account_1_daily:,.0f} requests/day")
    print(f"   Account #2: {account_2_daily:,.0f} requests/day")
    print(f"   Total daily: {total_daily:,.0f} requests/day")
    
    # Calculate monthly usage
    account_1_monthly = account_1_daily * trading_days_per_month
    account_2_monthly = account_2_daily * trading_days_per_month
    total_monthly = total_daily * trading_days_per_month
    
    print(f"\n📅 Monthly API Usage:")
    print(f"   Account #1: {account_1_monthly:,.0f} requests/month")
    print(f"   Account #2: {account_2_monthly:,.0f} requests/month")
    print(f"   Total monthly: {total_monthly:,.0f} requests/month")
    
    # Check against limits
    iex_monthly_limit = 500000
    combined_limit = iex_monthly_limit * 2
    
    print(f"\n🎯 Limit Compliance:")
    print(f"   IEX free limit per account: {iex_monthly_limit:,}/month")
    print(f"   Combined limit (2 accounts): {combined_limit:,}/month")
    
    account_1_utilization = (account_1_monthly / iex_monthly_limit) * 100
    account_2_utilization = (account_2_monthly / iex_monthly_limit) * 100
    total_utilization = (total_monthly / combined_limit) * 100
    
    account_1_status = "✅" if account_1_utilization <= 100 else "❌"
    account_2_status = "✅" if account_2_utilization <= 100 else "❌"
    total_status = "✅" if total_utilization <= 100 else "❌"
    
    print(f"   Account #1 utilization: {account_1_utilization:.1f}% {account_1_status}")
    print(f"   Account #2 utilization: {account_2_utilization:.1f}% {account_2_status}")
    print(f"   Total utilization: {total_utilization:.1f}% {total_status}")
    
    if total_status == "✅":
        remaining_capacity = combined_limit - total_monthly
        print(f"   💡 Remaining capacity: {remaining_capacity:,.0f} requests/month")
    
    return {
        'daily_usage': total_daily,
        'monthly_usage': total_monthly,
        'within_limits': total_status == "✅",
        'utilization_percent': total_utilization
    }

def compare_strategies():
    """Compare different collection strategies"""
    
    print(f"\n🔄 Strategy Comparison")
    print("=" * 50)
    
    strategies = {
        'Original (Wrong)': {
            'interval': 10,
            'schedule': '24/7',
            'hours_per_day': 24,
            'days_per_month': 30
        },
        'Corrected (Realistic)': {
            'interval': 30,
            'schedule': 'Market Hours',
            'hours_per_day': 6.5,
            'days_per_month': 22
        },
        'Aggressive (Risky)': {
            'interval': 15,
            'schedule': 'Market Hours',
            'hours_per_day': 6.5,
            'days_per_month': 22
        }
    }
    
    total_stocks = 3331
    iex_monthly_limit = 500000 * 2  # Two accounts
    
    for strategy_name, config in strategies.items():
        collections_per_hour = 60 / config['interval']
        collections_per_day = collections_per_hour * config['hours_per_day']
        daily_requests = total_stocks * collections_per_day
        monthly_requests = daily_requests * config['days_per_month']
        utilization = (monthly_requests / iex_monthly_limit) * 100
        
        status = "✅" if utilization <= 100 else "❌"
        
        print(f"\n📊 {strategy_name}:")
        print(f"   Interval: {config['interval']} minutes")
        print(f"   Schedule: {config['schedule']}")
        print(f"   Collections/day: {collections_per_day:.1f}")
        print(f"   Monthly requests: {monthly_requests:,.0f}")
        print(f"   Utilization: {utilization:.1f}% {status}")
        
        if utilization > 100:
            overage = monthly_requests - iex_monthly_limit
            print(f"   ⚠️ Overage: {overage:,.0f} requests/month")

def show_market_hours_schedule():
    """Show when collections actually happen"""
    
    print(f"\n⏰ Market Hours Collection Schedule")
    print("=" * 50)
    
    market_open = "09:30"
    market_close = "16:00"
    interval_minutes = 30
    
    print(f"📅 Trading Days: Monday - Friday")
    print(f"🕘 Market Hours: {market_open} - {market_close} ET")
    print(f"⏰ Collection Interval: {interval_minutes} minutes")
    
    # Calculate collection times
    from datetime import datetime, timedelta
    
    start_time = datetime.strptime(market_open, "%H:%M")
    end_time = datetime.strptime(market_close, "%H:%M")
    
    collection_times = []
    current_time = start_time
    
    while current_time <= end_time:
        collection_times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)
    
    print(f"\n🎯 Daily Collection Times ({len(collection_times)} times per day):")
    for i, time_str in enumerate(collection_times, 1):
        print(f"   {i:2d}. {time_str} ET")
    
    print(f"\n📊 Summary:")
    print(f"   Collections per day: {len(collection_times)}")
    print(f"   Collections per week: {len(collection_times) * 5}")
    print(f"   Collections per month: {len(collection_times) * 22}")

if __name__ == "__main__":
    print("🧮 NASDAQ Collection - CORRECTED Math Analysis\n")
    
    # Show realistic usage calculation
    result = calculate_realistic_usage()
    
    # Compare strategies
    compare_strategies()
    
    # Show collection schedule
    show_market_hours_schedule()
    
    print(f"\n🎉 Conclusion:")
    if result['within_limits']:
        print(f"✅ Strategy is viable!")
        print(f"✅ {result['utilization_percent']:.1f}% utilization of free tier limits")
        print(f"✅ Can collect ALL 3,331 NASDAQ stocks for $0/month")
        print(f"✅ Data freshness: Maximum 30 minutes during market hours")
    else:
        print(f"❌ Strategy exceeds free tier limits")
        print(f"❌ {result['utilization_percent']:.1f}% utilization (over 100%)")
        print(f"💡 Consider: Longer intervals, paid tier, or fewer stocks")
    
    print(f"\n💡 Next steps:")
    print(f"   🔧 Update .env with both IEX API keys")
    print(f"   ⏰ Use 30-minute intervals during market hours")
    print(f"   📊 Monitor actual usage in IEX dashboard")
    print(f"   🚀 Deploy with: python manage.py collect_nasdaq_realtime")
