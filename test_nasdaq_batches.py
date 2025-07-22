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
    """Simulate processing all 3,300+ NASDAQ stocks"""
    
    total_stocks = 3331  # Approximate NASDAQ count
    batch_size = 10
    
    print(f"\n🚀 Simulating COMPLETE NASDAQ Collection")
    print(f"   Total stocks: {total_stocks}")
    print(f"   Batch size: {batch_size}")
    
    total_batches = (total_stocks + batch_size - 1) // batch_size
    print(f"   Total batches: {total_batches}")
    
    # API distribution
    iex_limit = 2000
    finnhub_limit = 1300
    covered_stocks = iex_limit + finnhub_limit
    
    iex_batches = (iex_limit + batch_size - 1) // batch_size
    finnhub_batches = (finnhub_limit + batch_size - 1) // batch_size
    
    print(f"\n📡 API Distribution:")
    print(f"   IEX Cloud: {iex_limit} stocks ({iex_batches} batches)")
    print(f"   Finnhub: {finnhub_limit} stocks ({finnhub_batches} batches)")
    print(f"   Coverage: {covered_stocks}/{total_stocks} ({(covered_stocks/total_stocks)*100:.1f}%)")
    
    if covered_stocks < total_stocks:
        remaining = total_stocks - covered_stocks
        print(f"   ⚠️ Remaining: {remaining} stocks (need additional API)")
    
    # Timing estimates
    iex_time = iex_batches * 0.1  # 0.1 seconds per batch
    finnhub_time = finnhub_batches * 0.2  # 0.2 seconds per batch
    total_time = iex_time + finnhub_time
    
    print(f"\n⏱️ Estimated Timing:")
    print(f"   IEX phase: {iex_time:.1f} seconds")
    print(f"   Finnhub phase: {finnhub_time:.1f} seconds")
    print(f"   Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"   Idle time: {600 - total_time:.1f} seconds until next cycle")
    
    # Daily API usage
    cycles_per_day = 144  # Every 10 minutes
    daily_iex = iex_limit * cycles_per_day
    daily_finnhub = finnhub_limit * cycles_per_day
    
    print(f"\n📈 Daily API Usage:")
    print(f"   IEX Cloud: {daily_iex:,} requests/day (limit: 500,000/month)")
    print(f"   Finnhub: {daily_finnhub:,} requests/day (limit: 86,400/day)")
    
    if daily_finnhub > 86400:
        print(f"   ⚠️ Finnhub limit exceeded by {daily_finnhub - 86400:,} requests")
        recommended_finnhub = 86400 // cycles_per_day
        print(f"   💡 Recommended Finnhub limit: {recommended_finnhub} stocks/cycle")

if __name__ == "__main__":
    print("�� NASDAQ Batch Processing Test\n")
    
    # Test with sample data
    test_batch_creation()
    
    # Simulate full NASDAQ
    simulate_full_nasdaq()
    
    print(f"\n✅ Test completed!")
