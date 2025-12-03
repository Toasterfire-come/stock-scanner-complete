# Daily Update Items - Complete List

This document provides a comprehensive list of all data items that are updated **once per day** (typically after market close at 5:00 PM ET) versus items that are updated **real-time via the frontend/browser**.

---

## ✅ Items Updated ONCE PER DAY (Backend)

### 1. Stock Fundamentals (50+ Fields)

#### Valuation Metrics (8 fields)
- [ ] PE Ratio (Price to Earnings)
- [ ] Forward PE Ratio
- [ ] PEG Ratio (Price/Earnings to Growth)
- [ ] Price to Sales Ratio
- [ ] Price to Book Ratio
- [ ] EV to Revenue (Enterprise Value to Revenue)
- [ ] EV to EBITDA (Enterprise Value to EBITDA)
- [ ] Enterprise Value

#### Profitability Metrics (6 fields)
- [ ] Gross Margin
- [ ] Operating Margin
- [ ] Net Profit Margin
- [ ] ROE (Return on Equity)
- [ ] ROA (Return on Assets)
- [ ] ROIC (Return on Invested Capital)

#### Growth Metrics (6 fields)
- [ ] Revenue Growth YoY (Year over Year)
- [ ] Revenue Growth 3-Year CAGR
- [ ] Revenue Growth 5-Year CAGR
- [ ] Earnings Growth YoY
- [ ] Earnings Growth 5-Year CAGR
- [ ] Free Cash Flow Growth YoY

#### Financial Health Metrics (7 fields)
- [ ] Current Ratio
- [ ] Quick Ratio
- [ ] Debt to Equity Ratio
- [ ] Debt to Assets Ratio
- [ ] Interest Coverage Ratio
- [ ] Altman Z-Score (bankruptcy risk)
- [ ] Piotroski F-Score (0-9)

#### Cash Flow Metrics (5 fields)
- [ ] Operating Cash Flow
- [ ] Free Cash Flow
- [ ] Free Cash Flow per Share
- [ ] Free Cash Flow Yield
- [ ] Cash Conversion Ratio

#### Dividend Metrics (3 fields)
- [ ] Dividend Yield
- [ ] Dividend Payout Ratio
- [ ] Years of Dividend Growth

---

### 2. Calculated Valuations (5 fields)

- [ ] **DCF Value** - Discounted Cash Flow fair value per share
- [ ] **EPV Value** - Earnings Power Value (no-growth valuation)
- [ ] **Graham Number** - Benjamin Graham's fair value formula
- [ ] **PEG Fair Value** - Growth-adjusted fair value
- [ ] **Relative Value Score** - Comparison vs sector medians (0-2.0 scale)

---

### 3. Composite Scores & Recommendations (6 fields)

- [ ] **Valuation Score** (0-100) - Weighted composite of all valuation models
- [ ] **Valuation Status** - Classification:
  - Significantly Undervalued (70+)
  - Undervalued (55-69)
  - Fair Value (45-54)
  - Overvalued (30-44)
  - Significantly Overvalued (<30)
- [ ] **Recommendation** - Investment recommendation:
  - STRONG BUY
  - BUY
  - HOLD
  - SELL
  - STRONG SELL
- [ ] **Confidence Level** - High, Medium, Low (based on data coverage)
- [ ] **Strength Score** (0-100) - Overall financial strength
- [ ] **Strength Grade** - Letter grade: A, B, C, D, F

---

### 4. Basic Stock Information (Low Frequency)

- [ ] Company Name
- [ ] Sector
- [ ] Industry
- [ ] Exchange
- [ ] Market Capitalization
- [ ] Shares Outstanding
- [ ] 52-Week High
- [ ] 52-Week Low
- [ ] Average Volume (3-month)
- [ ] One Year Target Price (analyst consensus)
- [ ] Book Value per Share
- [ ] Earnings per Share (EPS)

---

### 5. Technical Indicators (Daily Timeframe)

#### Moving Averages
- [ ] SMA 20-day (Simple Moving Average)
- [ ] SMA 50-day
- [ ] SMA 100-day
- [ ] SMA 200-day
- [ ] EMA 12-day (Exponential Moving Average)
- [ ] EMA 26-day
- [ ] EMA 50-day
- [ ] EMA 200-day

#### Momentum Indicators
- [ ] RSI (Relative Strength Index) - daily
- [ ] MACD (Moving Average Convergence Divergence) - daily
  - MACD Line
  - Signal Line
  - Histogram
- [ ] Stochastic Oscillator (daily)
  - %K Line
  - %D Line

#### Volatility Indicators
- [ ] Bollinger Bands (daily)
  - Upper Band
  - Middle Band (20-day SMA)
  - Lower Band
- [ ] ATR (Average True Range) - daily

#### Volume Indicators
- [ ] VWAP (Volume Weighted Average Price) - daily
- [ ] Volume Profile - daily aggregation

---

### 6. Analyst Data

- [ ] Analyst Target Price (mean)
- [ ] Analyst Target Price (high)
- [ ] Analyst Target Price (low)
- [ ] Number of Analysts Following
- [ ] Analyst Recommendation Consensus (buy/hold/sell)

---

### 7. Sector & Industry Data

- [ ] Sector Median PE Ratio
- [ ] Sector Median Price to Book
- [ ] Sector Median EV/EBITDA
- [ ] Sector Median Price to Sales
- [ ] Industry Classification
- [ ] Sector Performance

---

### 8. Historical Data (Daily Aggregates)

- [ ] Daily Open Price
- [ ] Daily High Price
- [ ] Daily Low Price
- [ ] Daily Close Price
- [ ] Daily Volume
- [ ] Daily Price Change
- [ ] Daily Price Change Percentage

---

## 🔄 Items Updated REAL-TIME (Frontend/Browser)

### 1. Intraday Price Data
- [ ] Current Price (live)
- [ ] Price Change (from previous close)
- [ ] Price Change Percentage
- [ ] Bid Price
- [ ] Ask Price
- [ ] Bid-Ask Spread
- [ ] Last Trade Time

### 2. Intraday Volume & Range
- [ ] Current Volume (intraday)
- [ ] Today's High
- [ ] Today's Low
- [ ] Today's Range (high - low)
- [ ] Volume Change vs Average

### 3. Intraday Charts
- [ ] 1-minute charts
- [ ] 5-minute charts
- [ ] 15-minute charts
- [ ] 30-minute charts
- [ ] 1-hour charts
- [ ] 4-hour charts (intraday aggregation)

### 4. Intraday Technical Indicators
- [ ] Intraday Moving Averages (1m, 5m, 15m timeframes)
- [ ] Intraday RSI
- [ ] Intraday MACD
- [ ] Intraday Bollinger Bands
- [ ] Intraday VWAP

### 5. Order Book & Market Depth
- [ ] Level 2 Data (if available)
- [ ] Market Maker Activity
- [ ] Large Orders

### 6. News & Events (Real-time)
- [ ] Breaking news alerts
- [ ] Social media sentiment (real-time)
- [ ] Insider trading activity (real-time filings)

---

## 📊 Update Schedule Summary

| Category | Update Frequency | Update Method | Cache Duration |
|----------|------------------|---------------|----------------|
| Fundamentals | Daily (5 PM ET) | Backend scheduled task | 10 minutes |
| Valuation Scores | Daily (5 PM ET) | Backend scheduled task | 10 minutes |
| Daily Technicals | Daily (5 PM ET) | Backend scheduled task | 15 minutes |
| Intraday Price | Real-time | Frontend API calls | 30 seconds |
| Intraday Charts | Real-time | Frontend API calls | 1-5 minutes |
| Intraday Technicals | On-demand | Frontend API calls | 1-5 minutes |
| News | Real-time | Frontend polling/websocket | No cache |

---

## 🔧 Implementation Details

### Backend Daily Update
**Script**: `/app/backend/stocks/management/commands/update_daily_data.py`

**Updates**:
1. All fundamental metrics from yfinance
2. Calculate all valuation models (DCF, EPV, Graham, PEG, Relative)
3. Calculate composite scores and recommendations
4. Update daily technical indicators
5. Store in database (Stock & StockFundamentals models)

**Duration**: 
- Single stock: ~2-5 seconds
- 100 stocks: ~3-8 minutes
- 1000 stocks: ~30-80 minutes

### Frontend Real-time Updates
**Method**: API calls on-demand

**Endpoints**:
- `/api/chart/{ticker}/` - Intraday chart data
- `/api/chart/{ticker}/indicators/` - Intraday indicators
- Real-time price feeds (websockets or polling)

**Frequency**:
- Price: Every 1-5 seconds during market hours
- Charts: On user request or every 1-5 minutes
- Indicators: On user request

---

## 📈 Data Flow Diagram

```
Daily (5 PM ET) - Backend Scheduler
    ↓
yfinance API
    ↓
DailyUpdateService
    ↓
Calculate Valuations (DCF, EPV, Graham, etc.)
    ↓
Calculate Scores (Valuation Score, Strength Score)
    ↓
Database (Stock & StockFundamentals tables)
    ↓
Cached API Responses (10-15 min TTL)
    ↓
Frontend Tables & Screeners


Real-time - Frontend
    ↓
API Calls (on-demand or polling)
    ↓
/api/chart/{ticker}/ endpoint
    ↓
yfinance API (directly or cached 1-5 min)
    ↓
Frontend Charts & Live Price Display
```

---

## ✅ Checklist for Daily Updates

### Daily (Automated via Cron)
- [ ] Run at 5:00 PM ET (after market close)
- [ ] Update all stocks (or batches)
- [ ] Log results to `/app/backend/logs/daily_update.log`
- [ ] Check for errors and retry failed stocks
- [ ] Monitor API rate limits

### Real-time (Frontend)
- [ ] Poll for price updates every 1-5 seconds during market hours
- [ ] Refresh charts on user request
- [ ] Calculate intraday indicators on-demand
- [ ] Display last update timestamp

---

## 🚀 Production Setup

### Cron Job (Recommended)
```bash
# Run daily at 5:00 PM ET (weekdays only)
0 17 * * 1-5 cd /app/backend && python manage.py update_daily_data >> logs/daily_update.log 2>&1
```

### Monitoring
```bash
# Check cron logs
tail -f /app/backend/logs/daily_update_cron.log

# Check update status
python manage.py shell
>>> from stocks.models import StockFundamentals
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> recent = StockFundamentals.objects.filter(
...     last_updated__gte=timezone.now() - timedelta(hours=24)
... ).count()
>>> print(f"Stocks updated in last 24 hours: {recent}")
```

---

## 📝 Notes

1. **API Rate Limits**: yfinance has rate limits. Daily updates help avoid hitting these limits during trading hours.

2. **Cache Strategy**: Cached data serves most requests. Real-time data only fetched when explicitly needed.

3. **Performance**: Separating daily and real-time updates significantly improves frontend performance.

4. **Cost Efficiency**: Reduces API calls and database queries by caching low-frequency data.

5. **Data Freshness**: 
   - Fundamentals: Updated once daily (sufficient for long-term analysis)
   - Price: Real-time during market hours
   - Charts: On-demand with short cache

---

## 🔗 Related Documentation

- **Daily Update System**: `/app/DAILY_DATA_UPDATE_README.md`
- **MVP Status**: `/app/MVP.md`
- **Implementation Summary**: `/app/PHASE_2_3_IMPLEMENTATION_SUMMARY.md`
- **API Endpoints**: See `/app/backend/stocks/valuation_api.py` and `/app/backend/stocks/charting_api.py`

---

**Last Updated**: December 2024
