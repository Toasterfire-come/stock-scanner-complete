# Production Stock Scanner System

## Overview

This production-ready scanner system provides real-time stock data updates during market hours with three concurrent scanners:

1. **1-Minute Scanner** (`scanner_1min_websocket.py`)
   - Real-time price updates via WebSocket
   - Updates: `current_price`, `price_change`, `price_change_percent`
   - NO rate limits (WebSocket streaming)
   - Runs continuously during market hours

2. **10-Minute Scanner** (`scanner_10min_metrics.py`)
   - Volume and metrics updates via proxied batch calls
   - Updates: `volume`, `market_cap`, `pe_ratio`, `dividend_yield`, `highs/lows`, etc.
   - Proxy rotation to bypass rate limits
   - Runs every 10 minutes during market hours

3. **Daily Scanner** (`realtime_daily_yfinance.py`)
   - Full data refresh
   - Runs once per day at 4:30 PM ET (after market close)
   - Best run during off-hours (12 AM - 5 AM) for minimal throttling

## Architecture

```
scanner_orchestrator.py (Master Controller)
│
├── scanner_1min_websocket.py (Real-time prices)
│   └── WebSocket streaming (yfinance AsyncWebSocket)
│
├── scanner_10min_metrics.py (Volume/metrics)
│   └── Batch downloads with proxy rotation
│
└── realtime_daily_yfinance.py (Daily refresh)
    └── Full data fetch (off-hours optimized)
```

## Features

- **Market Hours Detection**: Automatically starts/stops at market open/close (9:30 AM - 4:00 PM ET)
- **Weekday Only**: Only runs Monday-Friday
- **Auto-Recovery**: Restarts crashed scanners automatically
- **Concurrent Execution**: All scanners run in parallel for maximum efficiency
- **Production-Ready**: Error handling, logging, graceful shutdown
- **No Manual Intervention**: Set it and forget it

## Requirements

```bash
pip install yfinance pandas pytz asgiref django
```

## Setup

### 1. Ensure Proxies are Available

Run the proxy harvester to get HTTP/HTTPS proxies:

```bash
python fast_proxy_harvester_enhanced.py
```

This creates `http_proxies.txt` which the 10-minute scanner uses.

### 2. Verify Database Connection

Ensure Django settings are correct:
- `stockscanner_django/settings.py` has correct database credentials
- Stock model exists with all required fields

### 3. Test Individual Scanners (Optional)

Test each scanner individually before running the orchestrator:

**1-Minute Scanner:**
```bash
python scanner_1min_websocket.py
```
Expected: Real-time price updates via WebSocket

**10-Minute Scanner:**
```bash
python scanner_10min_metrics.py
```
Expected: Volume/metrics updates with proxy rotation

**Daily Scanner:**
```bash
python realtime_daily_yfinance.py
```
Expected: Full data refresh

## Running Production System

### Option 1: Batch File (Windows)

Double-click `START_PRODUCTION_SCANNERS.bat`

### Option 2: Command Line

```bash
python scanner_orchestrator.py
```

### Option 3: Background Service (Linux/Production)

Create systemd service:

```ini
[Unit]
Description=Stock Scanner Orchestrator
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 scanner_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stock-scanner
sudo systemctl start stock-scanner
sudo systemctl status stock-scanner
```

## Monitoring

The orchestrator provides status updates:

```
[STATUS] 10:00 AM ET - Scanners: RUNNING
[STATUS] 10:05 AM ET - Scanners: RUNNING
[HEALTH] 1-minute scanner crashed - restarting...
[STATUS] 10:10 AM ET - Scanners: RUNNING
```

### Log Files

Redirect output to log file:

```bash
python scanner_orchestrator.py > scanner.log 2>&1
```

Or use `tee` to see output and save to file:

```bash
python scanner_orchestrator.py 2>&1 | tee scanner.log
```

## Performance Targets

| Scanner | Frequency | Target Time | Fields Updated |
|---------|-----------|-------------|----------------|
| 1-Minute | Continuous (~60s) | <60s | Price, change, change% |
| 10-Minute | Every 10 min | <600s | Volume, market cap, PE, etc. |
| Daily | Once/day (4:30 PM) | <3 hours | All fields (full refresh) |

## Data Fields Updated

### 1-Minute Scanner (Price Data)
- `current_price`
- `price_change`
- `price_change_percent`
- `last_updated`

### 10-Minute Scanner (Metrics)
- `volume`
- `days_high`
- `days_low`
- `market_cap`
- `pe_ratio`
- `dividend_yield`
- `week_52_high`
- `week_52_low`
- `avg_volume_3mon`
- `bid_price`
- `ask_price`
- `earnings_per_share`
- `book_value`
- `last_updated`

### Daily Scanner (Complete Refresh)
All fields above + any additional fields in the Stock model

## Troubleshooting

### Scanners Not Starting

**Check market hours:**
- Only runs 9:30 AM - 4:00 PM ET on weekdays
- Check current time: orchestrator displays current time in ET

**Check files exist:**
```bash
ls scanner_1min_websocket.py
ls scanner_10min_metrics.py
ls realtime_daily_yfinance.py
```

### Low Success Rate

**1-Minute Scanner:**
- WebSocket may not receive updates for all tickers immediately
- Normal to see 70-80% success in first minute
- Success rate improves over time as updates arrive

**10-Minute Scanner:**
- Check proxy file exists: `http_proxies.txt`
- Run proxy harvester if missing
- Low-quality proxies can reduce success rate
- Consider running proxy harvester more frequently

**Daily Scanner:**
- Best run during off-hours (12 AM - 5 AM)
- Running during peak hours may hit rate limits
- No proxies needed during off-hours

### Proxy Issues

**Run fresh proxy harvest:**
```bash
python fast_proxy_harvester_enhanced.py
```

**Check proxy count:**
```bash
wc -l http_proxies.txt  # Linux/Mac
find /c http_proxies.txt  # Windows
```

Should have 100+ proxies for good rotation.

### Database Connection Issues

**Check Django settings:**
```bash
python -c "import django; django.setup(); from stocks.models import Stock; print(Stock.objects.count())"
```

Should print ticker count without errors.

### WebSocket Issues

**Check yfinance version:**
```bash
pip show yfinance
```

Ensure version supports AsyncWebSocket (v0.2.28+)

**Test WebSocket manually:**
```bash
python test_websocket_scanner_small.py
```

Should connect and receive updates for 20 tickers.

## Stopping the System

### Graceful Shutdown

Press `Ctrl+C` in the terminal running the orchestrator.

The orchestrator will:
1. Stop all running scanners
2. Wait for graceful shutdown (10s timeout)
3. Force-kill if necessary
4. Exit cleanly

### Emergency Stop (Windows)

```cmd
taskkill /F /IM python.exe
```

### Emergency Stop (Linux/Mac)

```bash
pkill -f scanner_orchestrator.py
```

## Production Deployment Checklist

- [ ] Database configured correctly
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Proxies harvested (`http_proxies.txt` exists with 100+ proxies)
- [ ] Individual scanners tested successfully
- [ ] System time synchronized (for market hours detection)
- [ ] Logging configured (redirect to file or logging service)
- [ ] Monitoring set up (optional: Prometheus, Grafana, etc.)
- [ ] Auto-restart configured (systemd or Windows Task Scheduler)
- [ ] Backup database strategy in place

## Advanced Configuration

### Adjust Scanner Frequencies

Edit scanner files:

**1-Minute Scanner:**
```python
# scanner_1min_websocket.py
self.listen_duration = 60  # Change to desired seconds
```

**10-Minute Scanner:**
```python
# scanner_10min_metrics.py
SCAN_INTERVAL = 600  # Change to desired seconds
```

### Adjust Market Hours

Edit orchestrator:

```python
# scanner_orchestrator.py
MARKET_OPEN = dt_time(9, 30)   # Change to desired time
MARKET_CLOSE = dt_time(16, 0)  # Change to desired time
```

### Adjust Thread Counts

**10-Minute Scanner:**
```python
# scanner_10min_metrics.py
BATCH_SIZE = 100  # Tickers per batch
```

**Daily Scanner:**
```python
# realtime_daily_yfinance.py
MAX_THREADS = 50  # Worker threads
```

### Add Email Alerts (Optional)

Add email alerts for crashes:

```python
# scanner_orchestrator.py
def restart_scanner(self, name: str, script_path: Path):
    print(f"[RESTART] Restarting {name}...")
    # Add email alert here
    send_email(f"Scanner {name} crashed and was restarted")
    self.stop_scanner(name)
    self.start_scanner(name, script_path)
```

## System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 1 GB free
- Network: Stable internet connection

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 10+ GB free (for logs)
- Network: High-speed, reliable connection

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review scanner logs for errors
3. Test individual scanners to isolate issues
4. Verify database connection and schema

## License

Production-ready stock scanner system.
