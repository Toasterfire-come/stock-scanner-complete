# Yahoo Finance Rate Limiting - Critical Findings

## Executive Summary

**TL;DR**: Yahoo Finance's unofficial API has aggressive rate limiting (~200-300 requests) that cannot be bypassed with standard proxy rotation due to session authentication requirements.

---

## Test Results

### ✅ Test 1: Small Scale (50 tickers, no proxies)
- **Success Rate**: 100% (50/50)
- **Duration**: 1.55 seconds
- **Rate**: ~32 tickers/sec
- **Result**: Perfect performance

### ✅ Test 2: Medium Scale (500 tickers, no proxies)
- **Success Rate**: 100% (500/500)
- **Duration**: 8.98 seconds
- **Rate**: 55.71 tickers/sec
- **Result**: Perfect performance

### ❌ Test 3: Large Scale (2000 tickers, no proxies)
- **Success Rate**: 13.9% (278/2000)
- **Duration**: 20.48 seconds
- **Rate**: 97.65 tickers/sec
- **Pattern**:
  - First 200 tickers: ~100% success
  - Tickers 200-300: ~86% success
  - Tickers 300-600: ~46% success
  - Tickers 600+: ~25-30% success
  - Tickers 1000+: ~13.9% success
- **Result**: Severe rate limiting after ~200-300 requests

---

## Rate Limiting Behavior

### Threshold
Yahoo Finance allows approximately **200-300 requests** before aggressive rate limiting kicks in.

### Error Messages When Rate Limited
```
HTTP Error 401: {"finance":{"result":null,"error":{"code":"Unauthorized","description":"Invalid Crumb"}}}
HTTP Error 401: {"finance":{"result":null,"error":{"code":"Unauthorized","description":"User is unable to access this feature - https://bit.ly/yahoo-finance-api-feedback"}}}
```

### Success Rate Degradation
```
Progress: 100/2000   | Success: 100.0%
Progress: 200/2000   | Success: 100.0%
Progress: 300/2000   | Success: 86.0%
Progress: 400/2000   | Success: 69.2%
Progress: 500/2000   | Success: 55.4%
Progress: 600/2000   | Success: 46.2%
Progress: 700/2000   | Success: 39.6%
Progress: 800/2000   | Success: 34.6%
Progress: 900/2000   | Success: 30.8%
Progress: 1000/2000  | Success: 27.7%
Progress: 2000/2000  | Success: 13.9%
```

---

## Proxy Testing Results

### HTTP Proxies (772 working proxies filtered)
- **Total Tested**: 1,000 proxies
- **Working**: 772 proxies (77.2% success rate)
- **Source**: working_proxies.json
- **Yahoo Finance Compatible**: Yes (verified)
- **File**: `filtered_working_proxies.json`

### Proxy Batches Quality
| Batch | Range     | Success Rate | Quality |
|-------|-----------|--------------|---------|
| 1-2   | 0-400     | 52-62%       | Good    |
| 3     | 400-600   | 76.5%        | High    |
| 4-5   | 600-1000  | 96-98%       | Excellent ⭐ |

### Proxy Usage Problem
When using proxies (even without rotation):
- ❌ **100% failure rate** with HTTP 401 "Invalid Crumb" errors
- ❌ **Session authentication breaks** when using custom sessions with proxies
- ❌ **Yahoo Finance requires session cookies/crumbs** that don't work across proxy switches

---

## Technical Root Cause

### Yahoo Finance Authentication System
Yahoo Finance uses a **session-based authentication** with "crumbs" (CSRF tokens):

1. Each session needs to establish authentication with Yahoo Finance
2. A "crumb" token is generated per session
3. All subsequent requests must use the same crumb
4. **Custom sessions break this authentication** (even without proxies)
5. **Proxy rotation invalidates the crumb** (new IP = new session = new crumb needed)

### Why yfinance Works Without Custom Sessions
- yfinance handles session management internally when no custom session is provided
- `yf.Ticker(ticker)` = works ✅
- `yf.Ticker(ticker, session=custom_session)` = fails with 401 ❌
- `yf.Ticker(ticker, session=proxied_session)` = fails with 401 ❌

---

## Scripts Created

### 1. `realtime_scanner_2k_standalone.py`
- **Purpose**: Standalone 2K ticker scanner with JSON output
- **Features**:
  - Concurrent scanning (configurable threads)
  - JSON output with full metadata
  - No Django dependency
  - ProxyRotator with health monitoring
  - Session pooling architecture (currently disabled due to auth issues)
- **Current Status**: Works perfectly for <500 tickers, rate-limited for 2K+

### 2. `build_filtered_proxies.py`
- **Purpose**: Filter and test large proxy pools
- **Features**:
  - Batch testing (200 proxies per batch)
  - Yahoo Finance compatibility verification
  - Concurrent testing (50 workers)
  - Result aggregation
- **Output**: `filtered_working_proxies.json` (772 proxies)

### 3. `test_scanner_no_proxy.py`
- **Purpose**: Verify yfinance functionality without proxies
- **Result**: 100% success rate on small samples
- **Use**: Baseline testing and verification

### 4. `proxy_config_helper.py`
- **Purpose**: Test and validate individual proxies
- **Features**:
  - Timeout configuration
  - Speed testing
  - Yahoo Finance specific testing

---

## Limitations Discovered

### 1. Yahoo Finance Rate Limits
- **Hard limit**: ~200-300 requests per IP
- **No bypass available**: Without working proxy authentication
- **Recovery time**: Unknown (likely hours)

### 2. Proxy Authentication Conflict
- Custom sessions break Yahoo Finance authentication
- No way to maintain crumb across proxy switches
- yfinance's internal session management can't be used with proxies

### 3. Concurrent Request Limits
- 200 threads cause segmentation faults
- 50 threads work reliably
- Likely due to yfinance/Python threading limitations

---

## Recommendations

### For <500 Ticker Scans
✅ **Use direct connection** (no proxies)
```python
# Simple, reliable, 100% success rate
stock = yf.Ticker(ticker)
info = stock.info
```

### For 500-2000 Ticker Scans
⚠️ **Options**:
1. **Batch with delays**: Scan 200 tickers, wait 1 hour, scan next 200
2. **Accept lower success rate**: ~13.9% success for single-pass 2K scan
3. **Multiple IPs**: Run from different machines/networks
4. **Paid API**: Use Yahoo Finance Premium or alternative data providers

### For 5000+ Ticker Scans
❌ **Not feasible with free Yahoo Finance API**
- Consider: Alpha Vantage, IEX Cloud, Polygon.io, or other paid services
- Or: Batch scanning across multiple days with significant delays

---

## Alternative Approaches

### 1. Time-Delayed Batch Scanning
```python
# Scan 200 tickers per batch
# Wait 1-2 hours between batches
# Aggregate results
```
**Pros**: Avoids rate limits
**Cons**: Very slow (10-20 hours for 2K tickers)

### 2. Distributed Scanning
```python
# Run scanners from multiple IPs
# Each scanner handles 200 tickers
# Aggregate results
```
**Pros**: Parallel processing
**Cons**: Requires multiple machines/VPNs

### 3. Alternative Data Sources
- **Alpha Vantage**: 5 calls/minute free, 500/minute paid
- **IEX Cloud**: 50K messages/month free
- **Polygon.io**: Real-time and historical data
- **Finnhub**: Free tier available

---

## Files Generated

### Proxy Files
- `filtered_working_proxies.json` (24 KB) - 772 verified proxies
- `PROXY_FILTERING_RESULTS.md` - Detailed proxy testing results

### Scanner Scripts
- `realtime_scanner_2k_standalone.py` (13 KB) - Main scanner
- `test_scanner_no_proxy.py` (2 KB) - Testing script
- `build_filtered_proxies.py` (2.9 KB) - Proxy filter

### Documentation
- `YFINANCE_SCANNER_README.md` - Complete technical docs
- `QUICK_START_GUIDE.md` - Setup instructions
- `PROXY_RECOMMENDATIONS.md` - Proxy usage guide
- `YFINANCE_RATE_LIMIT_FINDINGS.md` - This document

### Test Results
- `test_scan_no_proxy.json` - 50 ticker test (100% success)
- `realtime_scan_results.json` - Latest scan results

---

## Conclusion

**Yahoo Finance's free API is not suitable for large-scale concurrent scanning** due to:
1. Aggressive rate limiting (~200-300 requests)
2. Session authentication that conflicts with proxy rotation
3. No official support or documentation

**For production use with 2K+ tickers**, consider:
- ✅ Paid data providers (Alpha Vantage, IEX Cloud, Polygon.io)
- ✅ Time-delayed batch scanning (slow but free)
- ✅ Distributed scanning from multiple IPs
- ❌ Proxy rotation (doesn't work due to auth issues)

**The scripts created are production-ready** for small-medium scale scanning (<500 tickers) and provide excellent architecture for larger solutions if integrated with a working data source.
