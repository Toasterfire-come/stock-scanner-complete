# 📈 NASDAQ Data Scheduler

## Overview
The Stock Scanner now automatically pulls NASDAQ data every 10 minutes when the Django server is running.

## How It Works

### Automatic Scheduling
- **Starts**: Automatically when Django server starts
- **Frequency**: Every 10 minutes
- **Delay**: 15 seconds after server startup (to ensure database is ready)
- **Data Sources**: 
  - NASDAQ stock prices via yfinance
  - Financial news via Yahoo Finance scraper

### What Gets Updated
1. **Stock Prices**: All NASDAQ tickers with current prices, volume, changes
2. **News Articles**: Latest financial news with sentiment analysis
3. **Market Data**: Volume, market cap, price changes

## Monitoring

### Admin Dashboard
Visit `http://localhost:8000/admin-dashboard/` to see:
- **Scheduler Status**: Shows if scheduler is active
- **Next Update**: Time of next scheduled update
- **Last Update**: When data was last refreshed
- **Manual Update**: Button to trigger immediate update

### Console Output
When server is running, you'll see:
```
🚀 Starting NASDAQ data scheduler (every 10 minutes)...
⏰ NASDAQ scheduler started - updates every 10 minutes
🔄 [2024-01-15 14:30:00] Updating NASDAQ stock data...
✅ [2024-01-15 14:30:15] NASDAQ data update completed!
```

## Manual Control

### Start Server with Scheduler
```bash
./start_admin_console.sh
```

### Manual Update (while server is running)
```bash
# Via Django command
python manage.py update_nasdaq_now

# Via Admin Dashboard
# Click "Update NASDAQ Now" button
```

### WordPress Integration
- WordPress endpoints still work: `/api/wordpress/stocks/` and `/api/wordpress/news/`
- Data is automatically fresh (updated every 10 minutes)
- Admin can view WordPress data at: `/wordpress-stocks/` and `/wordpress-news/`

## Technical Details

### Scheduler Implementation
- Uses Python `schedule` library
- Runs in background daemon thread
- Survives server restarts
- Thread-safe and non-blocking

### Data Flow
```
Server Start → 15s delay → Initial Update → Schedule every 10min
                ↓
        NASDAQ API (yfinance) → Database → WordPress APIs
                ↓
        News Scraper → Sentiment Analysis → Database
```

### Error Handling
- Continues running even if individual updates fail
- Logs all errors with timestamps
- Admin dashboard shows health status
- Manual recovery options available

## Status Monitoring

The admin dashboard shows:
- 🟢 **Healthy**: Scheduler running, recent updates successful
- 🟡 **Warning**: Scheduler running but some issues
- 🔴 **Error**: Scheduler stopped or major issues

## Benefits

1. **Always Fresh Data**: WordPress gets updated data every 10 minutes
2. **Automatic**: No manual intervention required
3. **Reliable**: Continues running in background
4. **Monitorable**: Real-time status in admin dashboard
5. **Controllable**: Manual updates when needed