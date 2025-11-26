# Proxy Scraper & Validator for YFinance

A comprehensive Python script that scrapes free proxies from multiple sources and validates them against the yfinance library.

## Features

- **30+ Proxy Sources**: Fetches proxies from multiple free proxy list providers
- **YFinance Validation**: Tests each proxy specifically with yfinance library
- **Concurrent Testing**: Uses ThreadPoolExecutor for fast validation (30 workers)
- **Smart Deduplication**: Combines with existing proxies and removes duplicates
- **Multiple Output Formats**: Saves as both JSON (detailed) and TXT (simple list)
- **Progress Tracking**: Real-time progress updates with ETA
- **Error Handling**: Robust error handling for network issues

## Installation

Required dependencies:
```bash
pip install requests yfinance
```

## Usage

Simply run the script:

```bash
python proxy_scraper_validator.py
```

Or make it executable:

```bash
chmod +x proxy_scraper_validator.py
./proxy_scraper_validator.py
```

## Output Files

The script creates two files:

1. **yfinance_working_proxies.json** - Detailed JSON format with metadata
   ```json
   {
     "proxies": ["1.2.3.4:8080", "5.6.7.8:3128"],
     "total_count": 150,
     "new_proxies_added": 50,
     "existing_proxies": 100,
     "last_updated": "2025-11-26 10:30:00",
     "validation_method": "yfinance",
     "note": "These proxies have been validated to work with yfinance library"
   }
   ```

2. **yfinance_working_proxies.txt** - Simple text file (one proxy per line)
   ```
   1.2.3.4:8080
   5.6.7.8:3128
   9.10.11.12:80
   ```

## How It Works

### Step 1: Fetch Proxies
- Scrapes 30+ free proxy list sources
- Collects HTTP, HTTPS, SOCKS4, and SOCKS5 proxies
- Deduplicates and cleans the proxy list

### Step 2: Validate with YFinance
- Tests each proxy by fetching real stock data
- Uses random stock symbols (AAPL, MSFT, GOOGL, etc.)
- Verifies actual data is returned (not just HTTP 200)
- Rotates user agents to avoid detection
- Concurrent testing with 30 workers for speed

### Step 3: Save Results
- Saves working proxies to JSON and TXT files
- Merges with existing proxies if file exists
- Provides detailed statistics and summary

## Proxy Sources

The script fetches from 30+ sources including:
- ProxyScrape API
- Proxy-List Download API
- GitHub proxy repositories (TheSpeedX, monosans, jetkai, etc.)
- Community-maintained proxy lists

## Configuration

You can customize the script by editing these variables:

```python
# Number of concurrent workers for testing
max_workers = 30

# Batch size for testing
batch_size = 100

# Timeout for proxy testing
timeout = 8

# Stop after finding N working proxies
if len(working_proxies) >= 1000:
    break
```

## Performance

Typical performance:
- **Fetching**: 1-2 minutes for all sources
- **Testing**: Varies based on proxy quality
  - ~30 proxies/second with 30 workers
  - 1000 proxies ≈ 30-40 seconds
  - 5000 proxies ≈ 3-4 minutes

## Success Rates

Success rates vary widely based on:
- Time of day
- Yahoo Finance rate limiting
- Proxy source quality
- Geographic location

Typical success rates: **1-10%** of fetched proxies work with yfinance

## Usage in Your Code

### Using JSON file:
```python
import json

# Load proxies
with open('yfinance_working_proxies.json', 'r') as f:
    data = json.load(f)
    proxies = data['proxies']

# Use with yfinance
import yfinance as yf
import requests

session = requests.Session()
session.proxies = {
    'http': f'http://{proxies[0]}',
    'https': f'http://{proxies[0]}'
}

ticker = yf.Ticker('AAPL', session=session)
info = ticker.info
```

### Using TXT file:
```python
# Load proxies
with open('yfinance_working_proxies.txt', 'r') as f:
    proxies = [line.strip() for line in f if line.strip()]

# Rotate through proxies
import random
proxy = random.choice(proxies)
```

## Troubleshooting

### No working proxies found
- Yahoo Finance may be rate limiting
- Try running at a different time
- Check your internet connection
- Some proxy sources may be temporarily down

### Low success rate
- Normal! Free proxies are often unreliable
- Run the script multiple times
- The script merges with existing working proxies

### Script is slow
- Increase `max_workers` (but may hit rate limits)
- Decrease `batch_size` for more frequent updates
- Reduce timeout value (but may miss slow-but-working proxies)

## Comparison with Other Scripts

This repository has several proxy scripts:

| Script | Purpose | Speed | Validation |
|--------|---------|-------|------------|
| `proxy_scraper_validator.py` | **Comprehensive yfinance validation** | Medium | **yfinance library** |
| `fetch_fresh_proxies.py` | Yahoo Finance API validation | Medium | Yahoo Finance API |
| `test_proxy_connectivity.py` | Two-phase testing | Fast | Connectivity + Yahoo |
| `quick_proxy_fetch.py` | Quick fetch & test | Fast | Yahoo Finance API |
| `fetch_1000_proxies.py` | Bulk fetch | Fast | Minimal |

**Use this script (`proxy_scraper_validator.py`)** when you need proxies specifically tested with the yfinance library for maximum compatibility.

## License

This script is for educational purposes. Respect the terms of service of proxy providers and Yahoo Finance.

## Notes

- Free proxies are inherently unreliable
- Proxies may stop working at any time
- Always have a fallback to direct connection
- Respect rate limits and terms of service
- Use proxies responsibly and ethically
