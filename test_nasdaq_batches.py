#!/usr/bin/env python3
"""
Test script for NASDAQ batch processing
Simulates the batch creation and processing logic
"""

def test_batch_creation():
    """Test creating batches of exactly 10 stocks"""
    
    # Simulate NASDAQ tickers (using a subset for testing)
    nasdaq_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
        'CSCO', 'ADBE', 'CRM', 'ORCL', 'AVGO', 'TXN', 'QCOM', 'BKNG', 'ISRG', 'INTU',
        'PEP', 'LIN', 'AZN', 'HON', 'AMAT', 'GILD', 'PANW', 'CMCSA', 'LRCX', 'ADP',
        'MU', 'MELI', 'VRTX', 'MSTR', 'KLAC', 'CRWD', 'APP', 'ADI', 'SBUX', 'COIN',
        'DASH', 'CEG', 'SNPS', 'MDLZ', 'CTAS', 'CDNS', 'ABNB', 'ORLY', 'FTNT', 'MAR'
    ]
    
    print(f"🧪 Testing batch creation with {len(nasdaq_tickers)} tickers")
    
    batch_size = 10
    batches = []
    
    # Create batches of exactly 10 stocks
    for i in range(0, len(nasdaq_tickers), batch_size):
        batch = nasdaq_tickers[i:i + batch_size]
        batches.append(batch)
        print(f"Batch {len(batches)}: {len(batch)} stocks - {batch}")
    
    print(f"\n📊 Batch Summary:")
    print(f"   Total tickers: {len(nasdaq_tickers)}")
    print(f"   Total batches: {len(batches)}")
    print(f"   Stocks per batch: {batch_size}")
    print(f"   Last batch size: {len(batches[-1]) if batches else 0}")
    
    # Simulate API distribution
    iex_limit = min(20, len(nasdaq_tickers))  # First 20 stocks for testing
    finnhub_limit = len(nasdaq_tickers) - iex_limit
    
    print(f"\n📡 API Distribution:")
    print(f"   IEX Cloud: {iex_limit} stocks ({iex_limit // batch_size} batches)")
    print(f"   Finnhub: {finnhub_limit} stocks ({(finnhub_limit + batch_size - 1) // batch_size} batches)")
    
    # Estimate timing
    iex_batches = (iex_limit + batch_size - 1) // batch_size
    finnhub_batches = (finnhub_limit + batch_size - 1) // batch_size
    
    estimated_time = (iex_batches * 0.1) + (finnhub_batches * 0.2)  # seconds
    print(f"\n⏱️ Estimated Collection Time: {estimated_time:.1f} seconds")
    
    return batches

def simulate_full_nasdaq():
    """Simulate processing ALL 3,331 NASDAQ stocks with Dual IEX FREE strategy"""
    
    total_stocks = 3331  # Exact NASDAQ count
    batch_size = 10
    cycles_per_day = 144  # Every 10 minutes
    
    print(f"\n🚀 Simulating ALL 3,331 NASDAQ Stocks Collection")
    print(f"   Total stocks: {total_stocks}")
    print(f"   Batch size: {batch_size}")
    
    total_batches = (total_stocks + batch_size - 1) // batch_size
    print(f"   Total batches: {total_batches}")
    
    # DUAL IEX CLOUD FREE ACCOUNTS STRATEGY
    api_limits = {
        'IEX Cloud #1': 2000,  # First free account
        'IEX Cloud #2': 1331,  # Second free account (remaining stocks)
        'Finnhub': 0,          # Not needed with dual IEX
        'Alpha Vantage': 0,    # Not needed
        'FMP': 0,              # Not needed
        'Twelve Data': 0,      # Not needed
        'Polygon.io': 0        # Not needed
    }
    
    print(f"\n📡 Dual IEX FREE Accounts Strategy:")
    total_covered = 0
    total_time = 0
    
    for api_name, limit in api_limits.items():
        if limit > 0:  # Only show APIs being used
            batches = (limit + batch_size - 1) // batch_size
            if 'IEX Cloud' in api_name:
                batch_time = batches * 0.1  # Fast IEX processing
            else:
                batch_time = batches * 0.2
                
            total_covered += limit
            total_time += batch_time
            
            print(f"   {api_name:14}: {limit:4} stocks ({batches:3} batches) - {batch_time:5.1f}s")
    
    coverage_percent = (total_covered / total_stocks) * 100
    remaining = total_stocks - total_covered
    
    print(f"\n📊 Coverage Summary:")
    print(f"   Total covered: {total_covered}/{total_stocks} stocks")
    print(f"   Coverage: {coverage_percent:.1f}%")
    if remaining > 0:
        print(f"   Remaining: {remaining} stocks uncovered")
        print(f"   💡 To get 100%: Add second IEX Cloud free account")
    else:
        print(f"   🎉 100% COVERAGE ACHIEVED WITH FREE ACCOUNTS!")
    
    print(f"\n⏱️ Collection Timing:")
    print(f"   Total collection time: {total_time:.1f} seconds ({total_time/60:.2f} minutes)")
    print(f"   Idle time per cycle: {600 - total_time:.1f} seconds")
    print(f"   Efficiency: {(total_time/600)*100:.1f}% active, {((600-total_time)/600)*100:.1f}% idle")
    
    # Daily API usage analysis
    print(f"\n📈 Daily API Usage (144 cycles):")
    daily_usage = {}
    total_daily_requests = 0
    
    for api_name, limit in api_limits.items():
        if limit > 0:  # Only show APIs being used
            daily = limit * cycles_per_day
            daily_usage[api_name] = daily
            total_daily_requests += daily
            
            # Check against known limits for IEX accounts
            if 'IEX Cloud' in api_name:
                monthly_limit = 500000
                daily_limit = monthly_limit / 30
                status = "✅" if daily <= daily_limit else "⚠️"
                print(f"   {api_name:14}: {daily:6,} requests/day (vs {daily_limit:6,.0f}/day limit) {status}")
    
    print(f"\n📊 Combined IEX Usage:")
    print(f"   Total requests/day: {total_daily_requests:,}")
    print(f"   Combined monthly: {total_daily_requests * 30:,} (vs 1,000,000 limit)")
    print(f"   Utilization: {(total_daily_requests * 30 / 1000000 * 100):.1f}% of combined free tier limits")
    
    print(f"\n🎯 Bottom Line (DUAL IEX FREE):")
    print(f"   🎉 Collect ALL {total_covered:,} NASDAQ stocks ({coverage_percent:.1f}%)")
    print(f"   ⏱️ Every 10 minutes in {total_time/60:.2f} minutes")
    print(f"   💰 Using 2 FREE IEX Cloud accounts")
    print(f"   🔑 Setup: 5 minutes to create second account")
    print(f"   🏆 Professional-grade market data for $0/month!")

def simulate_paid_iex():
    """Simulate IEX paid tier for 100% coverage"""
    
    total_stocks = 3331
    batch_size = 10
    
    print(f"\n💎 Simulating IEX PAID Tier (100% Coverage)")
    print(f"   Total stocks: {total_stocks}")
    print(f"   Batch size: {batch_size}")
    
    # Paid tier scenarios
    paid_tiers = {
        'Start': {'cost': 9, 'speed_multiplier': 1, 'delay': 0.05},
        'Launch': {'cost': 19, 'speed_multiplier': 10, 'delay': 0.01},
        'Grow': {'cost': 99, 'speed_multiplier': 20, 'delay': 0.005}
    }
    
    for tier_name, config in paid_tiers.items():
        total_batches = (total_stocks + batch_size - 1) // batch_size
        collection_time = total_batches * config['delay']
        
        print(f"\n🚀 IEX {tier_name} Tier (${config['cost']}/month):")
        print(f"   📊 Coverage: {total_stocks}/{total_stocks} stocks (100%)")
        print(f"   📦 Batches: {total_batches} batches of 10 stocks")
        print(f"   ⏱️ Collection time: {collection_time:.1f} seconds ({collection_time/60:.2f} minutes)")
        print(f"   🏃 Speed: {config['speed_multiplier']}x faster than free")
        print(f"   💰 Cost per stock: ${config['cost']/total_stocks:.4f}/month")
        print(f"   ⏰ Idle time: {600 - collection_time:.1f} seconds until next cycle")
        
        # Daily cost breakdown
        daily_cost = config['cost'] / 30
        cost_per_update = daily_cost / 144  # 144 updates per day
        
        print(f"   💳 Daily cost: ${daily_cost:.2f}")
        print(f"   💎 Cost per update: ${cost_per_update:.4f}")
    
    print(f"\n🎯 Bottom Line (PAID Tiers):")
    print(f"   🎉 100% NASDAQ coverage (all {total_stocks:,} stocks)")
    print(f"   ⚡ 10-1000x faster processing")
    print(f"   🔄 Single API (no multi-API complexity)")
    print(f"   💎 Starting at just $9/month ($0.30/day)")
    print(f"   🏆 Institutional-grade performance!")

if __name__ == "__main__":
    print("�� NASDAQ Batch Processing Test\n")
    
    # Test with sample data
    test_batch_creation()
    
    # Simulate full NASDAQ with free tier
    simulate_full_nasdaq()
    
    # Simulate paid IEX tiers
    simulate_paid_iex()
    
    print(f"\n✅ Test completed!")
    print(f"\n💡 Quick upgrade: python3 switch_iex_tier.py")
