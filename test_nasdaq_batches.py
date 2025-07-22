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
    """Simulate processing ALL 3,331 NASDAQ stocks with 6 APIs"""
    
    total_stocks = 3331  # Exact NASDAQ count
    batch_size = 10
    cycles_per_day = 144  # Every 10 minutes
    
    print(f"\n🚀 Simulating ALL 3,331 NASDAQ Stocks Collection")
    print(f"   Total stocks: {total_stocks}")
    print(f"   Batch size: {batch_size}")
    
    total_batches = (total_stocks + batch_size - 1) // batch_size
    print(f"   Total batches: {total_batches}")
    
    # AGGRESSIVE MULTI-API STRATEGY
    api_limits = {
        'IEX Cloud': 2000,  # Primary
        'Finnhub': 600,     # Secondary (respects daily limit)
        'Alpha Vantage': 3, # 500/day ÷ 144 cycles
        'FMP': 1,           # 250/day ÷ 144 cycles  
        'Twelve Data': 5,   # 800/day ÷ 144 cycles
        'Polygon.io': 5     # 720/day ÷ 144 cycles
    }
    
    print(f"\n📡 6-API Distribution Strategy:")
    total_covered = 0
    total_time = 0
    
    for api_name, limit in api_limits.items():
        batches = (limit + batch_size - 1) // batch_size
        if api_name == 'IEX Cloud':
            batch_time = batches * 0.1
        elif api_name == 'Finnhub':  
            batch_time = batches * 0.2
        elif api_name == 'Polygon.io':
            batch_time = batches * 12  # 5 per minute limit
        else:
            batch_time = batches * 1.0
            
        total_covered += limit
        total_time += batch_time
        
        print(f"   {api_name:12}: {limit:4} stocks ({batches:3} batches) - {batch_time:5.1f}s")
    
    coverage_percent = (total_covered / total_stocks) * 100
    remaining = total_stocks - total_covered
    
    print(f"\n📊 Coverage Summary:")
    print(f"   Total covered: {total_covered}/{total_stocks} stocks")
    print(f"   Coverage: {coverage_percent:.1f}%")
    if remaining > 0:
        print(f"   Remaining: {remaining} stocks uncovered")
        print(f"   💡 To get 100%: Upgrade Finnhub ($39/month) or add more free APIs")
    else:
        print(f"   🎉 100% COVERAGE ACHIEVED!")
    
    print(f"\n⏱️ Collection Timing:")
    print(f"   Total collection time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"   Idle time per cycle: {600 - total_time:.1f} seconds")
    print(f"   Efficiency: {(total_time/600)*100:.1f}% active, {((600-total_time)/600)*100:.1f}% idle")
    
    # Daily API usage analysis
    print(f"\n📈 Daily API Usage (144 cycles):")
    daily_usage = {}
    for api_name, limit in api_limits.items():
        daily = limit * cycles_per_day
        daily_usage[api_name] = daily
        
        # Check against known limits
        if api_name == 'IEX Cloud':
            monthly_limit = 500000
            daily_limit = monthly_limit / 30
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,.0f}/day limit) {status}")
        elif api_name == 'Finnhub':
            daily_limit = 86400
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,}/day limit) {status}")
        elif api_name == 'Alpha Vantage':
            daily_limit = 500
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,}/day limit) {status}")
        elif api_name == 'FMP':
            daily_limit = 250
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,}/day limit) {status}")
        elif api_name == 'Twelve Data':
            daily_limit = 800
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,}/day limit) {status}")
        elif api_name == 'Polygon.io':
            daily_limit = 720  # 5 per minute
            status = "✅" if daily <= daily_limit else "⚠️"
            print(f"   {api_name:12}: {daily:6,} requests/day (vs {daily_limit:6,}/day limit) {status}")
    
    print(f"\n🎯 Bottom Line:")
    print(f"   📊 Collect {total_covered:,} out of {total_stocks:,} NASDAQ stocks ({coverage_percent:.1f}%)")
    print(f"   ⏱️ Every 10 minutes in {total_time/60:.1f} minutes")
    print(f"   💰 Using 100% FREE API tiers")
    print(f"   🏆 Professional-grade market data for $0/month!")

if __name__ == "__main__":
    print("�� NASDAQ Batch Processing Test\n")
    
    # Test with sample data
    test_batch_creation()
    
    # Simulate full NASDAQ
    simulate_full_nasdaq()
    
    print(f"\n✅ Test completed!")
