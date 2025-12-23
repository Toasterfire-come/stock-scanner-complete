# Cron Jobs Setup Guide

## Overview
All scripts required for automated scanning with cron jobs are now present in this repository.

## Required Scripts ✅

All the following scripts are present and ready to use:

1. **install_cron_jobs.sh** - Main installation script for setting up cron jobs
2. **refresh_proxies.sh** - Daily proxy refresh script
3. **realtime_daily_yfinance.py** - Daily comprehensive scanner (runs at 2:00 AM)
4. **scanner_10min_metrics_improved.py** - 10-minute metrics scanner (runs during market hours)
5. **scanner_1min_hybrid.py** - 1-minute price scanner (WebSocket-based)

## Installation

To install all cron jobs automatically:

```bash
cd C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
./install_cron_jobs.sh
```

## Cron Schedule

The installation script will set up the following schedule:

### Daily Jobs
- **1:00 AM** - Refresh proxies (`refresh_proxies.sh`)
- **2:00 AM** - Daily comprehensive scan (`realtime_daily_yfinance.py`)

### Market Hours Jobs (Mon-Fri)
- **9:30 AM - 4:00 PM** - 10-minute metrics scanner (every 10 minutes)
- **9:25 AM** - Start 1-minute price scanner
- **4:05 PM** - Stop 1-minute price scanner

## Log Files

All logs are written to `backend/logs/`:
- `proxy_refresh.log` - Proxy refresh operations
- `daily_scanner.log` - Daily comprehensive scans
- `10min_scanner.log` - 10-minute metrics scans
- `1min_scanner.log` - 1-minute price updates

## Verification

To verify cron jobs are installed:

```bash
crontab -l
```

To view logs in real-time:

```bash
tail -f backend/logs/daily_scanner.log
tail -f backend/logs/10min_scanner.log
tail -f backend/logs/1min_scanner.log
```

## Manual Execution

You can run any scanner manually for testing:

```bash
# Daily scanner
python realtime_daily_yfinance.py

# 10-minute scanner
python scanner_10min_metrics_improved.py

# 1-minute scanner
python scanner_1min_hybrid.py
```

## Scanner Details

### refresh_proxies.sh
- Fetches fresh proxies from Geonode API
- Requires `curl` and `jq` to be installed
- Creates backup of old proxy list
- Only updates if at least 50 proxies are fetched

### realtime_daily_yfinance.py
- Runs during off-hours (12am-5am) for minimal throttling
- Target: Complete all stocks in under 3 hours
- No proxies needed at night
- Updates all stock data comprehensively

### scanner_10min_metrics_improved.py
- Updates volume and metrics every 10 minutes
- Uses proxy rotation with fallback
- Smart retry logic with exponential backoff
- Batch processing for efficiency

### scanner_1min_hybrid.py
- Real-time price updates via WebSocket
- No rate limits (WebSocket streaming)
- Updates: current_price, price_change, price_change_percent
- Fast execution (<60s for all tickers)

## Troubleshooting

If cron jobs aren't running:

1. Check cron service is running: `service cron status`
2. Verify crontab: `crontab -l`
3. Check log files for errors
4. Ensure scripts have execute permissions: `chmod +x *.sh`
5. Verify Python path in install script matches your system

## Notes

- The scripts use relative paths and auto-detect the backend directory
- Python binary is auto-detected (tries `python3` first, then `python`)
- Logs directory is created automatically if it doesn't exist
- Old proxy backups are cleaned up after 7 days
