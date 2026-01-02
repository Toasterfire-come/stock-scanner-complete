# Scanner Scheduler Setup Guide

This guide explains how to set up automated scheduling for the daily and intraday stock scanners.

## Quick Start (Recommended)

The easiest way to run both scanners is using the **unified controller script** (`run_all_scanners.sh` or `run_all_scanners.bat`). This single script intelligently runs:
- **Daily scanner:** Starts at 12:00 AM, runs for ~5 hours (off market hours)
- **Intraday scanner:** Starts at 9:30 AM, runs continuously until market close (4:00 PM EST)
  - The intraday scanner manages its own 1-minute update loop internally
  - It automatically exits when market closes - no need to repeatedly trigger it

**Key Difference:** You only schedule each scanner to start ONCE per day - they manage their own execution internally.

## Scanner Overview

### 1. Daily Scanner (realtime_daily_with_proxies.py)
- **Purpose:** Complete daily scan of all tickers with comprehensive metrics
- **Schedule:** Daily at 12:00 AM (midnight)
- **Duration:** ~5 hours (8,782 tickers at 0.488 t/s)
- **Configuration:**
  - Proxies: **ENABLED** (distributes load across proxies)
  - Rate Limit: 0.488 tickers/second (~2.05s per request)
  - Thread Count: 20
  - Total Requests: ~800 spread over 5 hours

### 2. Intraday Scanner (scanner_1min_hybrid.py)
- **Purpose:** Real-time price and volume updates via WebSocket
- **Schedule:** Starts at 9:30 AM, runs continuously until 4:00 PM EST
- **Update Frequency:** Every 1 minute (self-managed loop)
- **Duration:** Each update cycle takes <60 seconds
- **Configuration:**
  - WebSocket streaming (NO rate limits)
  - Updates: current_price, price_change, price_change_percent, volume
  - Market hours detection: Automatically exits at 4:00 PM EST or on weekends

---

## Unified Controller Script (Recommended)

The unified controller script simplifies setup by combining both scanners into a single script.

### Linux Setup

1. **Make script executable:**
   ```bash
   chmod +x /path/to/backend/stock_retrieval/run_all_scanners.sh
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add the following lines:**
   ```bash
   # Daily scanner at midnight (runs for ~5 hours)
   0 0 * * * /path/to/backend/stock_retrieval/run_all_scanners.sh --daily >> /path/to/backend/logs/daily_scanner.log 2>&1

   # Intraday scanner at market open (runs continuously until 4 PM EST)
   30 9 * * 1-5 /path/to/backend/stock_retrieval/run_all_scanners.sh --intraday >> /path/to/backend/logs/intraday_scanner.log 2>&1
   ```

**Important:** The intraday scanner only needs to be scheduled ONCE at 9:30 AM. It will run continuously and exit automatically at 4:00 PM.

### Windows Setup

1. **Open Task Scheduler** (Win + R, type `taskschd.msc`)

2. **Create Task 1 - Daily Scanner:**
   - Name: `Daily Scanner (Midnight)`
   - Trigger: Daily at 12:00 AM
   - Action: Start a program
   - Program: `C:\...\run_all_scanners.bat`
   - Arguments: `--daily`
   - Settings: Stop task if runs longer than 8 hours

3. **Create Task 2 - Intraday Scanner:**
   - Name: `Intraday Scanner (Market Hours)`
   - Trigger: Daily at 9:30 AM (weekdays only: Mon-Fri)
   - **DO NOT** set "Repeat every 1 minute" - the scanner handles this internally
   - Action: Start a program
   - Program: `C:\...\run_all_scanners.bat`
   - Arguments: `--intraday`
   - Settings: Stop task if runs longer than 7 hours (safety limit)

**Important:** The intraday scanner only needs to be triggered ONCE at 9:30 AM. It manages its own 1-minute loop and exits automatically at 4:00 PM.

### Usage

The unified script supports multiple modes:

```bash
# Auto mode (determines what to run based on time)
./run_all_scanners.sh

# Force run daily scanner
./run_all_scanners.sh --daily

# Force run intraday scanner
./run_all_scanners.sh --intraday

# Run both (for testing)
./run_all_scanners.sh --both
```

---

## Individual Scripts (Alternative Setup)

If you prefer to manage each scanner separately, use the individual scripts below.

## Linux Setup (Cron)

### Daily Scanner

1. **Make script executable:**
   ```bash
   chmod +x /path/to/backend/stock_retrieval/run_daily_scanner.sh
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add the following line:**
   ```bash
   0 0 * * * /path/to/backend/stock_retrieval/run_daily_scanner.sh >> /path/to/backend/logs/daily_scanner.log 2>&1
   ```

### Intraday Scanner

1. **Make script executable:**
   ```bash
   chmod +x /path/to/backend/stock_retrieval/run_intraday_scanner.sh
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add the following line:**
   ```bash
   # Run at market open (scanner manages its own loop and exits at 4 PM)
   30 9 * * 1-5 /path/to/backend/stock_retrieval/run_intraday_scanner.sh >> /path/to/backend/logs/intraday_scanner.log 2>&1
   ```

**Important:** Only schedule it ONCE at 9:30 AM. The scanner runs continuously and exits automatically at market close.

---

## Windows Setup (Task Scheduler)

### Daily Scanner

1. **Open Task Scheduler** (Win + R, type `taskschd.msc`)

2. **Create Basic Task:**
   - Name: `Daily Stock Scanner`
   - Description: `Runs comprehensive daily scan at midnight`

3. **Trigger:**
   - Type: Daily
   - Start: 12:00 AM
   - Recur every: 1 day

4. **Action:**
   - Action: Start a program
   - Program: `C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend\stock_retrieval\run_daily_scanner.bat`
   - Start in: `C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend`

5. **Conditions:**
   - Uncheck "Start only if computer is on AC power" (optional)

6. **Settings:**
   - Check "Allow task to be run on demand"
   - Check "Run task as soon as possible after scheduled start is missed"
   - Stop the task if it runs longer than: 8 hours

### Intraday Scanner

1. **Open Task Scheduler**

2. **Create Basic Task:**
   - Name: `Intraday Stock Scanner`
   - Description: `Runs continuously during market hours (9:30 AM - 4:00 PM EST)`

3. **Trigger:**
   - Type: Daily
   - Start time: 9:30 AM
   - Recur every: 1 day
   - Days: Monday, Tuesday, Wednesday, Thursday, Friday
   - **DO NOT** set "Repeat every 1 minute" - the scanner manages this internally

4. **Action:**
   - Action: Start a program
   - Program: `C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend\stock_retrieval\run_intraday_scanner.bat`
   - Start in: `C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend`

5. **Conditions:**
   - Uncheck "Start only if computer is on AC power" (recommended)

6. **Settings:**
   - Check "Allow task to be run on demand"
   - Stop the task if it runs longer than: 7 hours (safety limit - scanner exits at 4 PM)
   - If the running task does not end when requested, force it to stop

**Important:** Schedule it ONCE at 9:30 AM. The scanner runs continuously and automatically exits at 4:00 PM EST.

---

## Scheduler Files

### Unified Controller (Recommended)
- **Linux:** `run_all_scanners.sh`
- **Windows:** `run_all_scanners.bat`
- **Features:** Runs both scanners intelligently based on time

### Individual Scripts (Alternative)

#### Daily Scanner
- **Linux:** `run_daily_scanner.sh`
- **Windows:** `run_daily_scanner.bat`
- **Scanner:** `realtime_daily_with_proxies.py`

#### Intraday Scanner
- **Linux:** `run_intraday_scanner.sh`
- **Windows:** `run_intraday_scanner.bat`
- **Scanner:** `scanner_1min_hybrid.py`

---

## Log Files

Logs are automatically created in `backend/logs/`:

- **Daily Scanner:** `daily_scanner_YYYYMMDD.log`
- **Intraday Scanner:** `intraday_scanner_YYYYMMDD.log`

Example:
```
backend/logs/daily_scanner_20251226.log
backend/logs/intraday_scanner_20251226.log
```

---

## Testing the Setup

### Manual Testing

**Linux:**
```bash
# Test daily scanner
./run_daily_scanner.sh

# Test intraday scanner
./run_intraday_scanner.sh
```

**Windows:**
```cmd
# Test daily scanner
run_daily_scanner.bat

# Test intraday scanner
run_intraday_scanner.bat
```

### Verify Scheduled Tasks

**Linux:**
```bash
# List cron jobs
crontab -l

# View logs
tail -f /path/to/backend/logs/daily_scanner_YYYYMMDD.log
tail -f /path/to/backend/logs/intraday_scanner_YYYYMMDD.log
```

**Windows:**
```powershell
# List scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Scanner*"}

# View logs
Get-Content C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend\logs\daily_scanner_*.log -Tail 50
```

---

## Configuration Changes

### Daily Scanner Settings

Edit `backend/stock_retrieval/realtime_daily_with_proxies.py`:

```python
# Current configuration
TARGET_RATE = 0.488  # tickers/second (5-hour completion)
USE_PROXIES = True   # Proxy rotation enabled
MAX_THREADS = 20     # Thread pool size
```

**To adjust completion time:**
- **Faster (3 hours):** `TARGET_RATE = 0.81`
- **Current (5 hours):** `TARGET_RATE = 0.488`
- **Slower (8 hours):** `TARGET_RATE = 0.305`

Formula: `TARGET_RATE = 8782 tickers / (desired_hours × 3600 seconds)`

### Intraday Scanner Settings

The intraday scanner uses WebSocket streaming with no configurable rate limit (Yahoo Finance handles this).

---

## Troubleshooting

### Daily Scanner Not Running

1. **Check proxy file exists:**
   ```bash
   ls backend/stock_retrieval/http_proxies.txt
   ```

2. **Verify proxies are working:**
   ```bash
   python backend/test_daily_scanner_load.py
   ```

3. **Check logs for errors:**
   ```bash
   tail -50 backend/logs/daily_scanner_YYYYMMDD.log
   ```

### Intraday Scanner Issues

1. **WebSocket connection errors:**
   - Check internet connection
   - Verify yfinance is up to date: `pip install --upgrade yfinance`

2. **Market hours detection:**
   - The script includes timezone checking (EST)
   - Verify system timezone is correct

3. **Check logs:**
   ```bash
   tail -50 backend/logs/intraday_scanner_YYYYMMDD.log
   ```

### Permission Issues (Linux)

```bash
# Make scripts executable
chmod +x backend/stock_retrieval/*.sh

# Check cron permissions
sudo tail -f /var/log/cron
```

---

## Production Deployment

### Recommended Setup

1. **Daily Scanner:** 12:00 AM (midnight) - Runs during off-hours
2. **Intraday Scanner:** Every 1 minute during market hours (9:30 AM - 4:00 PM EST)

### Resource Usage

**Daily Scanner:**
- CPU: Moderate (20 threads)
- Memory: ~200-500 MB
- Network: ~800 requests over 5 hours (very light)
- Duration: 5 hours

**Intraday Scanner:**
- CPU: Low (WebSocket streaming)
- Memory: ~100-200 MB
- Network: Light (WebSocket, no HTTP polling)
- Duration: <60 seconds per run

---

## Summary

| Scanner | Schedule | Duration | Method | Purpose |
|---------|----------|----------|--------|---------|
| Daily | 12:00 AM daily | 5 hours | HTTP + Proxies | Full comprehensive scan |
| Intraday | Every 1 min (market hours) | <60s | WebSocket | Real-time price updates |

**Status:** Production ready - all scripts created and tested.

---

**Generated:** December 26, 2025
**Version:** 1.0
