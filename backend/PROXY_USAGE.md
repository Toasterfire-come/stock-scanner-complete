# Proxy Support for Stock Scanner

This scanner now includes intelligent proxy support to help avoid rate limits when fetching stock data from Yahoo Finance.

## Features

- **Automatic Proxy Fetching**: Pulls from multiple free proxy sources (2800+ proxies)
- **Proxy Validation**: Tests proxies before use to ensure they work
- **Smart Rotation**: Automatically rotates through working proxies
- **Fallback Support**: Falls back to direct connection if proxies fail
- **Fast Processing**: Parallel validation and scanning for speed

## Proxy Sources

The system automatically fetches proxies from these trusted sources:

1. **Proxifly** (GitHub): 2800+ proxies, updated every 5 minutes
2. **ProxyScrape**: HTTP/SOCKS proxies, updated every 5 minutes
3. **TheSpeedX PROXY-List**: 45k+ proxies, updated daily

All proxies are validated before use to ensure reliability.

## Quick Start

### Option 1: Using Helper Scripts (Easiest)

```bash
# Refresh proxies and run a test scan
cd backend/scripts
./run_scan_with_proxies.sh --refresh --limit 50

# Full scan with fresh proxies
./run_scan_with_proxies.sh --refresh

# Just refresh the proxy list
./refresh_proxies.sh
```

### Option 2: Using Python Directly

```bash
cd backend

# Step 1: Fetch and validate proxies (recommended first time)
python3 proxy_manager.py --fetch-limit 500 --validate-limit 150

# Step 2: Run scanner with proxies
python3 enhanced_scanner_with_proxies.py

# Or do both in one command:
python3 enhanced_scanner_with_proxies.py --refresh-proxies
```

## Detailed Usage

### Proxy Manager

Fetch and validate proxies:

```bash
# Fetch up to 500 proxies and validate 150 of them
python3 proxy_manager.py --fetch-limit 500 --validate-limit 150

# Test existing proxies
python3 proxy_manager.py --test

# Custom storage directory
python3 proxy_manager.py --storage-dir /path/to/proxies
```

**Outputs:**
- `proxies/proxies_latest.json` - Full proxy metadata
- `proxies/proxies_latest.txt` - Simple list for easy loading
- `proxies/proxies_YYYYMMDD_HHMMSS.*` - Timestamped backups

### Enhanced Scanner

Run the stock scanner with proxy support:

```bash
# Basic scan with proxies
python3 enhanced_scanner_with_proxies.py

# Refresh proxies before scanning
python3 enhanced_scanner_with_proxies.py --refresh-proxies

# Test scan with limited symbols
python3 enhanced_scanner_with_proxies.py --limit 100

# Disable proxies (direct connection)
python3 enhanced_scanner_with_proxies.py --no-proxies

# Custom thread count
python3 enhanced_scanner_with_proxies.py --threads 32

# Custom output file
python3 enhanced_scanner_with_proxies.py --output my_results.csv

# Full example
python3 enhanced_scanner_with_proxies.py \
    --refresh-proxies \
    --fetch-limit 300 \
    --validate-limit 100 \
    --threads 16 \
    --output results.csv
```

## How It Works

### 1. Proxy Fetching

The `ProxyManager` fetches proxies from multiple sources in parallel:

```python
from proxy_manager import ProxyManager

manager = ProxyManager(storage_dir="./proxies")
working_proxies = manager.refresh_proxies(
    fetch_limit=500,      # Fetch up to 500 proxies
    validate_limit=150    # Validate 150 of them
)
```

### 2. Proxy Validation

Each proxy is tested against multiple endpoints:
- http://httpbin.org/ip
- https://api.ipify.org
- http://ip-api.com/json/

Only working proxies are saved and used.

### 3. Smart Rotation

The scanner automatically rotates through proxies:
- Each request uses a different proxy
- Failed proxies are moved to the back of the queue
- Successful proxies are prioritized

### 4. Integration with Existing Scanner

The enhanced scanner integrates seamlessly with the existing `fast_stock_scanner.py`:

```python
from enhanced_scanner_with_proxies import EnhancedStockScanner

scanner = EnhancedStockScanner(
    use_proxies=True,
    threads=16
)

symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
results = scanner.scan_stocks(symbols)
```

## Performance Tips

### 1. Balance Fetch vs Validate

Fetching 500 proxies but only validating 100-150 gives a good balance of speed vs quality:

```bash
python3 proxy_manager.py --fetch-limit 500 --validate-limit 150
```

### 2. Thread Count

- **16 threads**: Good balance for most systems
- **32 threads**: Faster but may cause instability
- **8 threads**: More stable, slower

### 3. When to Use Proxies

**Use proxies when:**
- Scanning large numbers of stocks (1000+)
- Running frequent scans
- Getting rate limited by Yahoo Finance

**Don't use proxies when:**
- Scanning small batches (<100 stocks)
- One-off scans
- Proxies are causing more errors than helping

### 4. Refresh Frequency

- **Daily**: For production use
- **Before each scan**: For maximum reliability
- **Weekly**: For occasional use

## Troubleshooting

### No Working Proxies Found

```bash
# Try increasing validation limit
python3 proxy_manager.py --fetch-limit 1000 --validate-limit 300

# Or run without proxies
python3 enhanced_scanner_with_proxies.py --no-proxies
```

### Proxies Causing 401 Errors

Some proxies may cause authentication errors with Yahoo Finance. The scanner will:
1. Mark failed proxies and rotate to next one
2. Retry with different proxy
3. Fall back to direct connection if needed

To disable proxies entirely:
```bash
python3 enhanced_scanner_with_proxies.py --no-proxies
```

### Slow Validation

Validation runs in parallel but can still take time. Options:

```bash
# Validate fewer proxies
python3 proxy_manager.py --validate-limit 50

# Or just test existing proxies
python3 proxy_manager.py --test
```

## Architecture

```
┌─────────────────────┐
│   Proxy Sources     │
│ - Proxifly          │
│ - ProxyScrape       │
│ - TheSpeedX         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Proxy Fetcher      │
│ - Parallel fetch    │
│ - Deduplication     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Proxy Validator    │
│ - Test endpoints    │
│ - Response time     │
│ - Success rate      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Proxy Storage      │
│ - JSON format       │
│ - Text list         │
│ - Timestamped       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Enhanced Scanner   │
│ - Load proxies      │
│ - Smart rotation    │
│ - Fallback logic    │
└─────────────────────┘
```

## API Reference

### ProxyManager

```python
class ProxyManager:
    def __init__(self, storage_dir: Path)
    def refresh_proxies(
        self,
        fetch_limit: Optional[int] = 500,
        validate_limit: Optional[int] = None
    ) -> List[ProxyInfo]
    def load_latest_proxies(self) -> List[str]
```

### EnhancedStockScanner

```python
class EnhancedStockScanner:
    def __init__(
        self,
        use_proxies: bool = True,
        proxy_dir: str = "./proxies",
        threads: int = 16,
        timeout: int = 12
    )
    def refresh_proxies(
        self,
        fetch_limit: int = 300,
        validate_limit: int = 100
    ) -> int
    def scan_stocks(
        self,
        symbols: List[str],
        csv_output: Optional[str] = None
    ) -> Dict[str, Any]
```

## Examples

### Example 1: Quick Test Scan

```bash
# Fetch 100 proxies, validate 30, scan 50 stocks
python3 enhanced_scanner_with_proxies.py \
    --refresh-proxies \
    --fetch-limit 100 \
    --validate-limit 30 \
    --limit 50
```

### Example 2: Production Scan

```bash
# Fetch 500 proxies, validate 150, scan all stocks
python3 enhanced_scanner_with_proxies.py \
    --refresh-proxies \
    --fetch-limit 500 \
    --validate-limit 150 \
    --threads 16 \
    --output production_scan_$(date +%Y%m%d).csv
```

### Example 3: Scheduled Daily Scan

```bash
#!/bin/bash
# Add to crontab: 0 2 * * * /path/to/daily_scan.sh

cd /path/to/backend

# Refresh proxies
python3 proxy_manager.py --fetch-limit 500 --validate-limit 150

# Run scan
python3 enhanced_scanner_with_proxies.py \
    --output daily_scan_$(date +%Y%m%d).csv

# Clean old proxy files (keep last 7 days)
find proxies/ -name "proxies_*.json" -mtime +7 -delete
```

## Notes

- Free proxies can be unreliable - expect 5-20% success rate
- Validation helps filter out dead proxies
- The scanner will automatically fall back to direct connection if proxies fail
- Yahoo Finance API is for personal use only
- Respect rate limits even with proxies

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for specific error messages
3. Try running without proxies first (`--no-proxies`)
4. Ensure dependencies are installed: `pip install requests`

## Sources

This proxy system uses the following free proxy sources:
- [Proxifly Free Proxy List](https://github.com/proxifly/free-proxy-list)
- [ProxyScrape](https://proxyscrape.com/free-proxy-list)
- [TheSpeedX PROXY-List](https://github.com/TheSpeedX/PROXY-List)
