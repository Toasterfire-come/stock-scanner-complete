# Scanner Rate Limiting & Configuration Guide

**Last Updated**: December 19, 2025
**Purpose**: Document all three production scanners and their rate limiting configurations

---

## Overview

TradeScanPro uses three scanners to keep stock data up-to-date:

1. **1-Minute Scanner** (`scanner_1min_hybrid.py`) - Real-time prices via WebSocket
2. **10-Minute Scanner** (`scanner_10min_metrics_improved.py`) - Volume & metrics with proxies
3. **Daily Scanner** (`realtime_daily_yfinance.py`) - End-of-day comprehensive update

---

## 1. 1-Minute Scanner (Real-Time Prices)

### File
`scanner_1min_hybrid.py`

### Purpose
Updates current prices in real-time using WebSocket (NO rate limits from Yahoo Finance)

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Update Frequency** | 60 seconds | Continuous scanning every minute |
| **Data Source** | WebSocket | yfinance WebSocket API |
| **Rate Limiting** | **NONE** | WebSocket has no rate limits |
| **Timeout** | 60 seconds | WebSocket listen timeout |
| **Fields Updated** | current_price, price_change, price_change_percent | Price data only |
| **Success Rate** | 70-90%* | During market hours |
| **Performance** | 140 tickers/second | Verified in testing |

\* *Success rate is low (0.05%) when market closed, 70-90% during market hours*

### Rate Limiting Strategy
- **NO rate limiting needed** - WebSocket connections are not throttled
- Runs continuously every 60 seconds
- No proxy rotation required
- Automatic reconnection on failure

### Error Handling
```python
except Exception as e:
    print(f"\n[ERROR] Scan failed: {e}")
    print("Retrying in 60s...")
    await asyncio.sleep(60)
```

### Usage
```bash
# Run continuously
python scanner_1min_hybrid.py

# Expected output:
# [WEBSOCKET] Fetching prices for 8776 tickers...
# Successfully updated: 7900 (90.0%)
# Rate: 140.0 tickers/second
# Next scan in 60s
```

### Best Practices
- Run during market hours (9:30 AM - 4:00 PM ET) for best results
- Monitor WebSocket connection status
- Expect lower success rate after market close
- Use for real-time price updates only (not volume/metrics)

---

## 2. 10-Minute Scanner (Metrics & Volume)

### File
`scanner_10min_metrics_improved.py`

### Purpose
Updates volume, metrics, and metadata using HTTP requests with proxy rotation

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Update Frequency** | 600 seconds (10 min) | Batch updates every 10 minutes |
| **Data Source** | HTTP/yfinance | Standard yfinance API |
| **Batch Size** | 50 tickers | Reduced for reliability |
| **Timeout** | 45 seconds | Per batch timeout |
| **Max Retries** | 3 | Per batch |
| **Backoff Factor** | 2 | Exponential backoff (2s, 4s, 8s) |
| **Delay Between Batches** | 2 seconds | Rate limit protection |
| **Success Rate** | 75-85% | With proxy rotation |
| **Proxy File** | `http_proxies.txt` | HTTP/HTTPS proxies |

### Rate Limiting Strategy

#### Multi-Layer Protection

1. **Proxy Rotation**
   - Cycles through proxies from `http_proxies.txt`
   - Tracks failed proxies in `failed_proxies` set
   - Automatically skips known bad proxies
   - Resets failed proxy tracking when all exhausted

2. **Exponential Backoff**
   ```python
   wait_time = BACKOFF_FACTOR ** attempt  # 2s, 4s, 8s
   time.sleep(wait_time)
   ```

3. **No-Proxy Fallback**
   - If all proxies fail, attempts without proxy
   - Tracks `no_proxy_success` count
   - Useful when proxies are unavailable

4. **Batch Splitting**
   - If batch fails, splits into smaller chunks
   - Recursively retries smaller batches
   - Ensures maximum data retrieval

5. **Inter-Batch Delay**
   ```python
   time.sleep(2)  # 2-second delay between batches
   ```

### Smart Retry Logic

```python
# Strategy 1: Try with proxies (3 attempts)
for attempt in range(MAX_RETRIES):
    proxy_dict = self.get_next_proxy()
    batch_results = self.fetch_price_data_only(tickers, proxy_dict)
    success_rate = success_count / len(tickers)

    if success_rate > 0.5:  # At least 50% success
        break
    else:
        # Mark proxy as failed, try next one
        self.failed_proxies.add(proxy_str)
        time.sleep(BACKOFF_FACTOR ** attempt)

# Strategy 2: Try without proxy (fallback)
if not results and self.no_proxy_fallback:
    results = self.fetch_price_data_only(tickers, proxies=None)

# Strategy 3: Split batch and retry
if not results and len(tickers) > 10:
    results = self.fetch_batch_with_retry(tickers[:mid])
    results.update(self.fetch_batch_with_retry(tickers[mid:]))
```

### Proxy Management

**Proxy File Format** (`http_proxies.txt`):
```
1.2.3.4:8080
5.6.7.8:3128
9.10.11.12:80
```

**Proxy Selection**:
```python
def get_next_proxy(self, skip_failed: bool = True):
    """Get next proxy in rotation, skipping known failures"""
    while attempts < max_attempts:
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

        if skip_failed and proxy in self.failed_proxies:
            continue  # Skip known bad proxies

        return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
```

### Error Handling

```python
try:
    batch_results = self.fetch_price_data_only(tickers, proxy_dict)
except Exception as e:
    # Mark proxy as failed
    self.failed_proxies.add(proxy_str)
    self.stats['proxy_failures'] += 1
    # Exponential backoff before retry
    time.sleep(BACKOFF_FACTOR ** attempt)
```

### Usage

```bash
# Run continuously
python scanner_10min_metrics_improved.py

# Expected output:
# [INFO] Loaded 500 proxies from http_proxies.txt
# [BATCH 1/176] Processing 50 tickers...
# [PROGRESS] 1/176 batches (0.6%) | Success: 42/50 (84.0%)
# ...
# Successful: 7465 (85.0%)
# Proxy failures: 23
# No-proxy successes: 156
# Time: 540.0s (9.0 minutes)
# Next scan in 600s (10 minutes)
```

### Best Practices

1. **Maintain Fresh Proxy List**
   - Update `http_proxies.txt` daily
   - Remove dead proxies regularly
   - Aim for 200-500 working proxies

2. **Monitor Proxy Success Rate**
   - Track `proxy_failures` count
   - If > 50%, refresh proxy list
   - Consider paid proxies for production

3. **Adjust Batch Size**
   - Reduce if seeing high failure rates
   - Increase if proxies are reliable
   - Current: 50 tickers (balanced)

4. **Schedule Wisely**
   - Run every 10 minutes during market hours
   - Less frequent after hours (30-60 min)
   - Pause overnight if not needed

---

## 3. Daily Scanner (End-of-Day Update)

### File
`realtime_daily_yfinance.py`

### Purpose
Comprehensive end-of-day update for all tickers (prices, volume, fundamentals)

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Update Frequency** | Daily | Once per day after market close |
| **Recommended Time** | 12:00 AM - 5:00 AM | Off-peak hours for minimal throttling |
| **Data Source** | HTTP/yfinance | Standard yfinance API |
| **Max Threads** | 50 | Conservative threading |
| **Batch Size** | 100 | Database batch updates |
| **Timeout** | 15 seconds | Per ticker timeout |
| **Fields Updated** | ALL | Prices, volume, fundamentals, metadata |

### Rate Limiting Strategy

#### Time-Based Throttling Avoidance

1. **Off-Peak Schedule**
   ```python
   current_hour = datetime.now().hour
   if not (0 <= current_hour <= 5):
       logger.warning("⚠️  WARNING: Running outside recommended hours (12am-5am)")
       logger.warning("⚠️  May experience higher throttling rates")
   ```

2. **Conservative Threading**
   - MAX_THREADS = 50 (not aggressive)
   - ThreadPoolExecutor manages concurrency
   - Prevents overwhelming Yahoo Finance

3. **No Proxy Rotation**
   - Runs during off-peak hours
   - Direct connection sufficient
   - Throttling is minimal at night

4. **Generous Timeout**
   - TIMEOUT = 15.0 seconds
   - Allows slower responses
   - Prevents premature failures

### Progress Monitoring

```python
if i % 500 == 0:  # Every 500 tickers
    elapsed = time.time() - start_time
    rate = i / elapsed
    success_rate = (success_count / i) * 100
    eta = remaining / rate if rate > 0 else 0

    logger.info(
        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) | "
        f"Success: {success_count} ({success_rate:.1f}%) | "
        f"Rate: {rate:.1f} t/s | "
        f"ETA: {eta/60:.1f} min"
    )
```

### Error Handling

```python
try:
    data = yf.Ticker(ticker).info
    if 'regularMarketPrice' in data:
        success_count += 1
    else:
        failed_count += 1
except Exception as e:
    failed_count += 1
    logger.debug(f"Failed to fetch {ticker}: {e}")
```

### Usage

```bash
# Run once (recommended: schedule with cron/Task Scheduler)
python realtime_daily_yfinance.py

# Expected output:
# [INFO] ===== Daily Stock Data Scanner =====
# [INFO] Total tickers to scan: 8776
# [INFO] Threads: 50
# [INFO] Batch size: 100
# [INFO] Starting scan at 2025-12-19 02:00:00
# [INFO] Recommended hours: 12am-5am ET (minimal throttling)
# ...
# [INFO] Progress: 500/8776 (5.7%) | Success: 475 (95.0%) | Rate: 15.2 t/s | ETA: 9.1 min
# ...
# [INFO] Scan complete!
# [INFO] Successful: 8345 (95.1%)
# [INFO] Failed: 431 (4.9%)
# [INFO] Total time: 575.3s (9.6 minutes)
# [INFO] Average rate: 15.3 tickers/second
```

### Best Practices

1. **Schedule During Off-Peak**
   - Best: 12:00 AM - 5:00 AM ET
   - Good: 6:00 AM - 8:00 AM ET
   - Avoid: 9:30 AM - 4:00 PM ET (market hours)

2. **Monitor Success Rate**
   - Target: > 90%
   - If < 80%, check for API changes
   - Consider adding proxy rotation if needed

3. **Database Performance**
   - BATCH_SIZE = 100 works well
   - Increase if database can handle it
   - Decrease if seeing timeouts

4. **Automation**

   **Linux/Mac (crontab)**:
   ```bash
   # Run daily at 2:00 AM
   0 2 * * * cd /path/to/backend && python realtime_daily_yfinance.py >> logs/daily_scanner.log 2>&1
   ```

   **Windows (Task Scheduler)**:
   - Create task to run daily at 2:00 AM
   - Action: `python realtime_daily_yfinance.py`
   - Start in: `C:\path\to\backend`
   - Run whether user is logged on or not

---

## Rate Limiting Comparison

| Scanner | Frequency | Rate Limits | Strategy | Success Rate |
|---------|-----------|-------------|----------|--------------|
| **1-Min** | Every 60s | **None** (WebSocket) | Direct connection | 70-90% (market hours) |
| **10-Min** | Every 10min | **Yes** (HTTP) | Proxy rotation + backoff | 75-85% |
| **Daily** | Once/day | **Minimal** (off-peak) | Off-peak + threading | 90-95% |

---

## Combined Usage Strategy

### Market Hours (9:30 AM - 4:00 PM ET)
```
1-Min Scanner:  Running continuously (real-time prices)
10-Min Scanner: Running every 10 minutes (volume/metrics)
Daily Scanner:  Paused (wait for market close)
```

### After Hours (4:00 PM - 12:00 AM ET)
```
1-Min Scanner:  Paused or reduced frequency (30-60 min)
10-Min Scanner: Reduced frequency (30-60 min)
Daily Scanner:  Paused (wait for off-peak)
```

### Off-Peak (12:00 AM - 9:30 AM ET)
```
1-Min Scanner:  Paused
10-Min Scanner: Paused
Daily Scanner:  **Run at 2:00 AM** (comprehensive update)
```

---

## Monitoring & Troubleshooting

### Key Metrics to Track

1. **Success Rate**
   - 1-Min: Should be 70-90% during market hours
   - 10-Min: Should be 75-85% with good proxies
   - Daily: Should be 90-95% during off-peak

2. **Proxy Health** (10-Min Scanner)
   - Monitor `proxy_failures` count
   - High failures (>50%) = refresh proxy list
   - Track `no_proxy_success` for fallback usage

3. **Processing Rate**
   - 1-Min: ~140 tickers/second
   - 10-Min: ~15-20 tickers/second
   - Daily: ~15-20 tickers/second

### Common Issues

#### Issue: Low Success Rate on 1-Min Scanner
**Cause**: Market closed or WebSocket connection issues
**Solution**:
- Check if market is open
- Verify internet connection
- Restart scanner to reconnect WebSocket

#### Issue: High Proxy Failures on 10-Min Scanner
**Cause**: Stale or dead proxies
**Solution**:
- Update `http_proxies.txt` with fresh proxies
- Remove dead proxies from list
- Consider paid proxy service

#### Issue: Daily Scanner Throttled
**Cause**: Running during peak hours
**Solution**:
- Reschedule to 12:00 AM - 5:00 AM
- Reduce MAX_THREADS if needed
- Add delays between batches

---

## Proxy Sources

For the 10-minute scanner, maintain a fresh proxy list:

1. **Free Proxy Lists**
   - https://www.proxy-list.download/
   - https://free-proxy-list.net/
   - https://www.sslproxies.org/

2. **Proxy APIs**
   - https://proxylist.geonode.com/api/proxy-list
   - https://www.proxyscrape.com/

3. **Paid Proxy Services** (Recommended for Production)
   - Bright Data
   - Smartproxy
   - Oxylabs

### Proxy Refresh Script

Create a cron job to refresh proxies daily:

```bash
#!/bin/bash
# refresh_proxies.sh

cd /path/to/backend

# Fetch fresh proxies
curl "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&filterUpTime=90&speed=fast&limit=500" \
    | jq -r '.data[] | "\(.ip):\(.port)"' > http_proxies.txt.new

# Replace old proxy list
mv http_proxies.txt.new http_proxies.txt

echo "Proxies refreshed: $(wc -l < http_proxies.txt) proxies"
```

Schedule with cron:
```bash
# Refresh proxies daily at 1:00 AM
0 1 * * * /path/to/refresh_proxies.sh >> logs/proxy_refresh.log 2>&1
```

---

## Scanner Orchestration

Use `scanner_orchestrator.py` to manage all three scanners automatically:

```python
# Manages:
# - 1-min scanner during market hours
# - 10-min scanner during market hours
# - Daily scanner at configured time
# - Automatic start/stop based on market schedule
```

---

## Testing & Validation

### Test 1-Min Scanner
```bash
# Run for 5 minutes, expect 5 scans
python scanner_1min_hybrid.py
# Watch for "Successfully updated" messages
# Verify rate ~140 tickers/second
```

### Test 10-Min Scanner
```bash
# Run single scan, check proxy rotation
python scanner_10min_metrics_improved.py
# Monitor proxy usage
# Verify success rate 75-85%
```

### Test Daily Scanner
```bash
# Run during off-peak hours
python realtime_daily_yfinance.py
# Expect 90-95% success rate
# Should complete in 10-15 minutes
```

---

## Production Deployment Checklist

- [ ] 1-Min Scanner configured to run during market hours
- [ ] 10-Min Scanner has fresh proxy list (200+ proxies)
- [ ] Daily Scanner scheduled for 2:00 AM
- [ ] Monitoring in place for success rates
- [ ] Logs configured and rotating
- [ ] Database backups scheduled
- [ ] Alert system for failures
- [ ] Proxy refresh automation enabled

---

**Last Updated**: December 19, 2025
**Maintained By**: Development Team
**Contact**: carter.kiefer2010@outlook.com
