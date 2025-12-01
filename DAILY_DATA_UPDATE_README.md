# Daily Data Update System

## Overview

This system manages **daily updates** for stock fundamentals, technicals, and valuation data. Real-time data (price, volume, intraday charts) is handled separately by the frontend.

---

## What Gets Updated Daily?

### 1. **Stock Fundamentals** (50+ metrics)
- **Valuation Metrics**: PE ratio, PEG ratio, Price to Book, Enterprise Value, EV/EBITDA
- **Profitability**: Gross margin, Operating margin, Net margin, ROE, ROA, ROIC
- **Growth**: Revenue growth (YoY, 3Y, 5Y), Earnings growth
- **Financial Health**: Current ratio, Quick ratio, Debt ratios, Altman Z-Score
- **Cash Flow**: Free cash flow, Operating cash flow, FCF yield, Cash conversion
- **Dividends**: Yield, Payout ratio, Dividend growth rates

### 2. **Valuation Models**
- **DCF Value**: Discounted Cash Flow fair value
- **EPV Value**: Earnings Power Value
- **Graham Number**: Benjamin Graham's fair value formula
- **PEG Fair Value**: Growth-adjusted valuation
- **Relative Value Score**: Comparison vs sector medians

### 3. **Composite Scores**
- **Valuation Score** (0-100): Weighted composite of all valuation models
- **Valuation Status**: Significantly undervalued, undervalued, fair value, overvalued, etc.
- **Recommendation**: STRONG BUY, BUY, HOLD, SELL, STRONG SELL
- **Strength Score** (0-100): Financial strength rating
- **Strength Grade**: A, B, C, D, F

### 4. **Basic Stock Info** (low frequency changes)
- Market cap
- 52-week high/low
- Average volume (3-month)
- Shares outstanding
- One year target price
- Book value, Earnings per share

### 5. **Technical Indicators** (daily timeframe)
- Daily Moving Averages (SMA, EMA)
- Daily RSI, MACD, Bollinger Bands
- Other daily technical indicators

---

## What is NOT Updated Daily?

### Real-time Data (Updated via Frontend)
- Current price and price changes
- Bid/Ask prices
- Day's range (high/low)
- Current volume
- Intraday charts (1m, 5m, 15m, 30m, 1H)

---

## Running the Daily Update

### Option 1: Manual Execution

```bash
# Update all stocks
python manage.py update_daily_data

# Update first 100 stocks (for testing)
python manage.py update_daily_data --limit 100

# Update specific tickers
python manage.py update_daily_data --ticker AAPL MSFT GOOGL
```

### Option 2: Cron Job (Recommended)

```bash
# Setup cron job (runs daily at 5:00 PM ET)
cd /app/backend
bash setup_daily_cron.sh

# View cron jobs
crontab -l

# Check cron logs
tail -f logs/daily_update_cron.log
```

### Option 3: Scheduler Daemon

```bash
# Run as background daemon
python daily_data_scheduler.py &

# Run once (no daemon)
python daily_data_scheduler.py --once

# View scheduler logs
tail -f logs/daily_update.log
```

---

## Scheduling Recommendations

### Best Time to Run
- **5:00 PM ET (17:00)**: After US market close
- **6:00 PM ET (18:00)**: If yfinance data is delayed
- **Weekdays only**: Markets are closed on weekends

### Frequency
- **Once per day**: After market close
- **Do NOT run multiple times per day**: Wastes API calls and resources

### Cron Examples

```bash
# Daily at 5:00 PM ET
0 17 * * * cd /app/backend && python manage.py update_daily_data

# Weekdays only at 5:00 PM ET
0 17 * * 1-5 cd /app/backend && python manage.py update_daily_data

# Daily at 6:00 PM ET with logging
0 18 * * * cd /app/backend && python manage.py update_daily_data >> logs/daily_update.log 2>&1
```

---

## API Endpoints

### Valuation Endpoints

```bash
# Get comprehensive valuation analysis
GET /api/valuation/{ticker}/

# Get quick valuation summary
GET /api/valuation/{ticker}/quick/

# Get undervalued stocks screener
GET /api/screener/undervalued/?min_score=60&min_market_cap=1&limit=20
```

### Chart Endpoints (Real-time)

```bash
# Get chart data
GET /api/chart/{ticker}/?timeframe=1d&chart_type=candlestick

# Get technical indicators
GET /api/chart/{ticker}/indicators/?indicators=sma_20,ema_50,rsi,macd
```

---

## Performance Considerations

### Update Duration
- **Single stock**: ~2-5 seconds
- **100 stocks**: ~3-8 minutes
- **1000 stocks**: ~30-80 minutes

### Rate Limiting
- yfinance has rate limits
- Recommended: Update in batches with delays
- Use caching to avoid redundant API calls

### Database Impact
- Updates are atomic (transaction-based)
- Indexes on key fields for fast queries
- Old data is overwritten, not duplicated

---

## Monitoring

### Check Update Status

```python
from stocks.models import StockFundamentals
from django.utils import timezone
from datetime import timedelta

# Check recently updated stocks
recent = StockFundamentals.objects.filter(
    last_updated__gte=timezone.now() - timedelta(hours=24)
).count()

print(f"Stocks updated in last 24 hours: {recent}")
```

### View Logs

```bash
# Cron logs
tail -f /app/backend/logs/daily_update_cron.log

# Scheduler logs
tail -f /app/backend/logs/daily_update.log

# Django logs
tail -f /var/log/supervisor/backend.err.log
```

---

## Troubleshooting

### Common Issues

1. **yfinance rate limits**
   - Solution: Add delays between requests
   - Use smaller batches (--limit 100)

2. **Timeout errors**
   - Solution: Increase request timeout
   - Skip problematic tickers

3. **Memory usage**
   - Solution: Process in smaller batches
   - Clear cache periodically

4. **Missing data**
   - Solution: Check yfinance API status
   - Verify ticker symbols are correct

### Debug Mode

```bash
# Run with verbose logging
python manage.py update_daily_data --ticker AAPL --verbosity 2
```

---

## Integration with Frontend

### Frontend Data Flow

1. **Table Data** (from daily updates):
   ```javascript
   // Fetch valuation data
   fetch(`/api/valuation/${ticker}/`)
   ```

2. **Chart Data** (real-time):
   ```javascript
   // Fetch intraday chart data
   fetch(`/api/chart/${ticker}/?timeframe=15m`)
   ```

3. **Technical Indicators** (mix):
   - Daily indicators: From daily updates
   - Intraday indicators: Calculated on-demand

---

## Next Steps

1. ✅ Daily update service implemented
2. ✅ Management command created
3. ✅ Scheduler scripts ready
4. ⏳ Set up cron job in production
5. ⏳ Monitor first few daily updates
6. ⏳ Adjust batch sizes based on performance
7. ⏳ Add alerting for failed updates

---

## Support

For issues or questions:
- Check logs in `/app/backend/logs/`
- Review Django admin for data status
- Test with `--ticker` flag for single stocks
- Monitor API rate limits

---

**Last Updated**: December 2024
