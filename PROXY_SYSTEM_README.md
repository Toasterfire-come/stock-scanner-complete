# 🚀 Proxy Support Added to Stock Scanner

Your stock scanner now includes intelligent proxy support to help avoid rate limits and improve scanning reliability!

## What's New

✅ **Automatic Proxy Fetching** - Pulls from 3 major free proxy sources (2800+ proxies)
✅ **Smart Validation** - Tests proxies before use to ensure reliability
✅ **Intelligent Rotation** - Automatically cycles through working proxies
✅ **Fallback Support** - Falls back to direct connection if proxies fail
✅ **Easy Integration** - Works with your existing scanner code

## Quick Start

### Option 1: One-Line Quick Test

```bash
cd backend
python3 enhanced_scanner_with_proxies.py --refresh-proxies --limit 50
```

This will:
1. Fetch fresh proxies from multiple sources
2. Validate them to ensure they work
3. Scan 50 stocks using the working proxies

### Option 2: Using Helper Scripts

```bash
cd backend/scripts

# Refresh proxies first
./refresh_proxies.sh

# Then run the scanner
./run_scan_with_proxies.sh

# Or do both at once:
./run_scan_with_proxies.sh --refresh --limit 100
```

### Option 3: Manual Control

```bash
cd backend

# Step 1: Fetch and validate proxies
python3 proxy_manager.py --fetch-limit 500 --validate-limit 150

# Step 2: Run the scanner with proxies
python3 enhanced_scanner_with_proxies.py

# Or run without proxies
python3 enhanced_scanner_with_proxies.py --no-proxies
```

## Key Files

- `backend/proxy_manager.py` - Fetches and validates proxies
- `backend/enhanced_scanner_with_proxies.py` - Enhanced scanner with proxy support
- `backend/scripts/refresh_proxies.sh` - Quick proxy refresh script
- `backend/scripts/run_scan_with_proxies.sh` - Quick scan script
- `backend/PROXY_USAGE.md` - Detailed documentation

## How It Helps

### Rate Limit Avoidance

Yahoo Finance may rate limit requests from a single IP. Proxies help by:
- Distributing requests across multiple IPs
- Reducing the chance of being blocked
- Allowing faster scanning with more parallel requests

### Sources Used

The system automatically fetches proxies from:
1. **Proxifly** - 2800+ proxies, updated every 5 minutes
2. **ProxyScrape** - Free HTTP/SOCKS proxies
3. **TheSpeedX** - 45k+ proxy list, updated daily

All proxies are validated before use!

## Performance Tips

### When to Use Proxies

✅ **Good for:**
- Large batch scans (1000+ stocks)
- Frequent scanning
- When experiencing rate limits

❌ **May not need for:**
- Small batches (<100 stocks)
- One-off scans
- Already getting good success rates

### Recommended Settings

```bash
# For testing (fast)
python3 enhanced_scanner_with_proxies.py \
    --refresh-proxies \
    --fetch-limit 100 \
    --validate-limit 30 \
    --limit 50

# For production (reliable)
python3 enhanced_scanner_with_proxies.py \
    --refresh-proxies \
    --fetch-limit 500 \
    --validate-limit 150
```

## Example Output

```
================================
PROXY REFRESH STARTED
================================
Fetching proxies from proxifly_http...
Fetched 847 proxies from proxifly_http
Fetching proxies from proxyscrape_http...
Fetched 312 proxies from proxyscrape_http
Total unique proxies fetched: 1523

Validating 150 proxies with 50 workers...
Progress: 50/150 tested, 12 working
Progress: 100/150 tested, 23 working
Validation complete: 35/150 proxies working (23.3%)

Saved 35 proxies to proxies/proxies_20251125_143022.json
================================
PROXY REFRESH COMPLETE - 35 working proxies
================================

Starting scan of 50 symbols...
Success rate: 96.0%
Scan completed in 12.45s
Output saved to: stock_scan_20251125_143045.csv
```

## Troubleshooting

### "No working proxies found"

Try fetching more:
```bash
python3 proxy_manager.py --fetch-limit 1000 --validate-limit 300
```

Or just run without proxies:
```bash
python3 enhanced_scanner_with_proxies.py --no-proxies
```

### Proxies causing errors

The scanner automatically handles this by:
1. Rotating to next proxy on failure
2. Retrying with different proxy
3. Falling back to direct connection

To disable proxies:
```bash
python3 enhanced_scanner_with_proxies.py --no-proxies
```

### Slow validation

Reduce validation count:
```bash
python3 proxy_manager.py --validate-limit 50
```

## Advanced Usage

See `backend/PROXY_USAGE.md` for:
- Detailed API reference
- Integration with existing code
- Scheduled scanning setup
- Performance optimization
- Architecture details

## Notes

⚠️ **Important:**
- Free proxies can be unreliable (expect 10-30% success rate)
- Validation helps filter bad proxies
- Scanner falls back to direct connection if needed
- Yahoo Finance API is for personal use only

## Integration with Existing Scanner

The proxy system integrates seamlessly with your current `fast_stock_scanner.py`:

```python
from enhanced_scanner_with_proxies import EnhancedStockScanner

# Create scanner with proxies
scanner = EnhancedStockScanner(use_proxies=True, threads=16)

# Refresh proxies if needed
scanner.refresh_proxies(fetch_limit=300, validate_limit=100)

# Scan stocks
symbols = ['AAPL', 'GOOGL', 'MSFT']
results = scanner.scan_stocks(symbols)
```

## Support

For detailed documentation, see:
- `backend/PROXY_USAGE.md` - Complete usage guide
- `backend/proxy_manager.py` - Source code with inline docs
- `backend/enhanced_scanner_with_proxies.py` - Scanner implementation

Happy scanning! 🎯
