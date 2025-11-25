# Yahoo Finance Rate Limits Explained

**Last Updated:** November 25, 2025

## 🚨 Important: No Official API

Yahoo Finance **does not provide an official API**. What we call the "Yahoo Finance API" is actually:
- Undocumented web endpoints
- Screen scraping of Yahoo Finance pages
- Reverse-engineered access methods

**This means:** Rate limits are **unofficial, undocumented, and change without notice**.

---

## 📊 Current Rate Limits (2025)

Based on community observations and recent reports:

### Approximate Limits
- **~200-2000 requests per hour per IP** (varies widely)
- **~250-1000 requests per day per IP** (before aggressive blocking)
- **Recent tightening:** Yahoo became more aggressive in 2024

### What Triggers Rate Limiting

| Scenario | Risk Level | When It Happens |
|----------|------------|-----------------|
| 1-50 stocks/day | 🟢 Low | Rarely blocked |
| 100-500 stocks/day | 🟡 Medium | Occasional 429 errors |
| 500-1000 stocks/day | 🟠 High | Frequent blocking |
| 1000+ stocks/day | 🔴 Very High | Almost guaranteed block |
| Rapid loops | 🔴 Very High | Detected as bot activity |

---

## ⏰ When Do Rate Limits Hit?

### Timeline Example (Single IP, No Proxies)

```
Time    | Requests | Status
--------|----------|------------------
0:00    | 0        | ✅ All working
0:10    | 100      | ✅ All working (safe zone)
0:20    | 250      | ⚠️  Starting to see delays
0:30    | 400      | ⚠️  Occasional 429 errors
0:45    | 600      | 🔴 Frequent 429 errors
1:00    | 800      | 🔴 Rate limited
1:30    | 1000     | 🚫 IP temporarily blocked (1-24 hrs)
```

### Error Messages You'll See

```python
# HTTP 429 - Too Many Requests
yfinance.exceptions.YFRateLimitError: Too Many Requests

# Connection errors
HTTPError: 429 Client Error: Too Many Requests for url

# Timeout errors (indirect rate limiting)
ReadTimeout: HTTPSConnectionPool(host='query2.finance.yahoo.com', port=443)
```

---

## 🔄 How Proxies Help

### Without Proxies (Direct Connection)
```
Your IP → Yahoo Finance
   ↓
100 requests from YOUR IP
   ↓
Yahoo sees: "This IP made 100 requests in 10 minutes"
   ↓
🚫 RATE LIMITED
```

### With Proxy Rotation
```
Request 1 → Proxy A → Yahoo Finance
Request 2 → Proxy B → Yahoo Finance
Request 3 → Proxy C → Yahoo Finance
   ↓
Yahoo sees:
- Proxy A: 1 request ✅
- Proxy B: 1 request ✅
- Proxy C: 1 request ✅
   ↓
✅ NO RATE LIMITING (distributed load)
```

---

## 📊 Proxy Types & Their Limits

### 1. No Proxy (Direct Connection)
**Rate Limit:** ~200-1000 requests/hour per IP
```
✅ Best for: <500 stocks/day
✅ Reliability: 98%+
❌ Limited by: Your IP's rate limit
```

### 2. Free Public Proxies
**Rate Limit:** Each proxy has ~200-1000 requests/hour
```
⚠️  Success rate: 0-10% (most are already blocked)
⚠️  Reliability: Very low
⚠️  Many are already rate-limited by Yahoo
❌ Not recommended for production
```

**Why free proxies get rate limited:**
- Shared by thousands of users
- Already made hundreds of requests to Yahoo
- Yahoo has likely already blocked them
- High chance they're on Yahoo's blacklist

### 3. Paid Residential Proxies
**Rate Limit:** Each proxy has ~200-1000 requests/hour
```
✅ Success rate: 95-99%
✅ Pool size: Millions of IPs
✅ Fresh IPs not on blacklists
✅ Geographic distribution
💰 Cost: $50-500/month
```

**Paid proxy providers:**
- BrightData (formerly Luminati)
- Smartproxy
- Oxylabs
- SOAX
- NetNut

### 4. Paid Datacenter Proxies
**Rate Limit:** Each proxy has ~200-1000 requests/hour
```
✅ Success rate: 80-95%
✅ Faster than residential
⚠️  More easily detected
💰 Cost: $30-200/month
```

---

## 🎯 When Do YOU Need Proxies?

### Scenario Analysis

#### Scenario 1: Small Daily Scan
```
Stocks: 100
Frequency: Once per day
Requests: ~100/day

Rate Limit Risk: 🟢 NONE
Recommendation: ✅ Direct connection (no proxies)
Why: Well below rate limits
```

#### Scenario 2: Medium Daily Scan
```
Stocks: 500
Frequency: Once per day
Requests: ~500/day

Rate Limit Risk: 🟡 LOW
Recommendation: ✅ Direct connection, monitor for 429 errors
Why: Near rate limit boundary
```

#### Scenario 3: Large Daily Scan
```
Stocks: 2,000
Frequency: Once per day
Requests: ~2,000/day

Rate Limit Risk: 🔴 HIGH
Recommendation: ⚠️  Need proxies OR split into batches
Why: Exceeds typical rate limits
```

#### Scenario 4: Multiple Daily Scans
```
Stocks: 1,000
Frequency: 3x per day (morning, noon, close)
Requests: ~3,000/day

Rate Limit Risk: 🔴 VERY HIGH
Recommendation: 🔴 Definitely need paid proxies
Why: Far exceeds rate limits
```

#### Scenario 5: Real-Time Monitoring
```
Stocks: 100
Frequency: Every 5 minutes
Requests: ~28,800/day (100 stocks × 288 times)

Rate Limit Risk: 🔴 GUARANTEED BLOCK
Recommendation: 🔴 Need paid proxies + streaming data alternative
Why: Massive request volume
```

---

## 💡 Smart Strategies to Avoid Rate Limits

### 1. Batch Processing (No Proxies Needed)
```python
# Instead of scanning all stocks at once:
# BAD: 5000 stocks in 10 minutes → BLOCKED
scan_stocks(all_5000_stocks)

# GOOD: Split into batches across the day → NO BLOCKING
morning:   scan_stocks(stocks[0:1000])      # 8 AM
midday:    scan_stocks(stocks[1000:2000])   # 12 PM
afternoon: scan_stocks(stocks[2000:3000])   # 3 PM
evening:   scan_stocks(stocks[3000:5000])   # 6 PM
```

### 2. Rate Limiting Your Requests
```python
import time

for stock in stocks:
    fetch_stock_data(stock)
    time.sleep(0.5)  # 500ms delay = max 120 requests/min
```

### 3. Caching Results
```python
# Cache results for X hours
if cached_data_age < 4_hours:
    return cached_data
else:
    return fetch_fresh_data()
```

### 4. Efficient API Usage
```python
# BAD: 1 request per stock
for stock in ['AAPL', 'GOOGL', 'MSFT']:
    ticker = yf.Ticker(stock)
    data = ticker.history()

# BETTER: Bulk download (1 request for multiple stocks)
data = yf.download(['AAPL', 'GOOGL', 'MSFT'], period='1d')
```

---

## 🔍 Testing Your Rate Limits

Here's a script to test your personal rate limits:

```python
import yfinance as yf
import time

def test_rate_limit():
    """Test how many requests before getting rate limited"""
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

    for i in range(1, 1000):
        symbol = test_symbols[i % len(test_symbols)]

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            print(f"✅ Request {i}: {symbol} - Success")

        except Exception as e:
            if '429' in str(e) or 'Too Many Requests' in str(e):
                print(f"🚫 RATE LIMITED at request {i}")
                print(f"Your limit: ~{i} requests")
                return i
            else:
                print(f"⚠️  Request {i}: Error - {e}")

        time.sleep(0.1)  # Small delay

    return None

# Run test
limit = test_rate_limit()
print(f"\nYour IP was rate limited after {limit} requests")
```

---

## 📈 ROI Analysis: Free vs Paid Proxies

### Option 1: Free Proxies
```
Cost: $0/month
Working proxies: 0-5% (0-50 out of 1000 fetched)
Time to validate: 30-60 minutes daily
Reliability: Very poor
Success rate: 0-20%

Total Cost: $0 + wasted time
Recommendation: ❌ Not worth it for production
```

### Option 2: Paid Proxies
```
Cost: $100/month (entry level)
Working proxies: 95%+
Setup time: 5 minutes
Reliability: Excellent
Success rate: 95-99%

For 10,000 stocks/day:
- Without proxies: Impossible (rate limited)
- With paid proxies: Easy and reliable

ROI: ✅ Worth it for >1000 stocks/day
```

### Option 3: No Proxies + Smart Batching
```
Cost: $0/month
Batch into 4 scans/day: 250 stocks each = 1000 total
Reliability: Excellent
Success rate: 98%+

Best for: <1000 stocks/day
Recommendation: ✅ Start here
```

---

## 🎓 Best Practices

### ✅ Do This

1. **Start without proxies** - Test if you hit rate limits
2. **Use bulk downloads** - `yf.download()` is more efficient
3. **Add delays** - 0.5-1 second between requests
4. **Cache results** - Don't re-fetch data you already have
5. **Batch processing** - Spread scans across the day
6. **Monitor 429 errors** - Track when you get rate limited
7. **Use paid proxies** - If you need >1000 stocks/day

### ❌ Don't Do This

1. ❌ Use free proxies for production
2. ❌ Make rapid-fire requests (detected as bot)
3. ❌ Scan 5000+ stocks in one go without proxies
4. ❌ Ignore 429 errors (you'll get IP banned)
5. ❌ Run continuous loops without delays
6. ❌ Fetch same data multiple times per day

---

## 🚀 Recommended Approach by Scale

### Small Scale (<500 stocks/day)
```bash
# No proxies needed
python3 enhanced_scanner_with_proxies.py --no-proxies
```

### Medium Scale (500-1000 stocks/day)
```bash
# Split into 2-3 batches across the day
morning:   python3 scanner.py --limit 500 --no-proxies
afternoon: python3 scanner.py --offset 500 --limit 500 --no-proxies
```

### Large Scale (>1000 stocks/day)
```bash
# Use paid proxy service
# Add paid proxies to proxies/paid_proxies.txt
python3 enhanced_scanner_with_proxies.py
```

---

## 📚 Summary

| Question | Answer |
|----------|--------|
| **Are all proxies rate limited?** | Yes, but each proxy has its own rate limit (~200-1000 req/hr) |
| **When does rate limiting start?** | After ~200-1000 requests/hour from one IP |
| **Do free proxies help?** | Rarely - most are already rate-limited by Yahoo |
| **Do paid proxies help?** | Yes - fresh IPs not on Yahoo's blacklist |
| **When do I need proxies?** | When scanning >1000 stocks/day |
| **Best strategy for <1000 stocks?** | Direct connection with smart batching |
| **Best strategy for >1000 stocks?** | Paid proxies ($100-500/month) |

---

## Sources

Research based on:
- [Stack Overflow: Yahoo Finance API Query Limits](https://stackoverflow.com/questions/9346582/what-is-the-query-limit-on-yahoos-finance-api)
- [Medium: Why yfinance Keeps Getting Blocked](https://medium.com/@trading.dude/why-yfinance-keeps-getting-blocked-and-what-to-use-instead-92d84bb2cc01)
- [GitHub: yfinance Rate Limit Issues](https://github.com/ranaroussi/yfinance/issues/2422)
- [APIpark: Yahoo Finance API Call Limits](https://apipark.com/technews/RZtyppGC.html)
- Community observations from 2024-2025

---

**Bottom Line:** Start without proxies and monitor for rate limits. Only use paid proxies if you're scanning >1000 stocks/day.
