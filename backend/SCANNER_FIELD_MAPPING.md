# Scanner Field Mapping - Daily vs 1-Minute

## Database Analysis

Based on the Stock model in `stocks/models.py`, here's the breakdown of fields that should be updated by each scanner:

---

## 1-Minute Scanner (Real-time via WebSocket)

**Purpose:** Ultra-fast real-time updates during market hours

**Update Frequency:** Every 60 seconds during market hours

**Fields to Update:**
- ✅ `current_price` - Current trading price
- ✅ `price_change` - Price change amount from previous close
- ✅ `price_change_percent` - Price change percentage from previous close
- ✅ `volume` - Current day's trading volume
- ✅ `last_updated` - Timestamp of update

**Data Source:** yfinance WebSocket
- Field mapping:
  - `current_price` ← `message.get('price')`
  - `price_change` ← `message.get('change')`
  - `price_change_percent` ← `message.get('change_percent')`
  - `volume` ← `int(message.get('day_volume'))`

**Total Fields:** 5 fields (real-time essentials)

---

## Daily Scanner (Comprehensive via REST API)

**Purpose:** Complete daily update of all market data and metrics

**Update Frequency:** Once daily at midnight (12 AM - 5 AM)

**Fields to Update:**

### Basic Info (if missing)
- `company_name` - Full company name
- `exchange` - Stock exchange

### Current Price Data
- ✅ `current_price` - Current trading price
- ✅ `price_change` - Price change amount
- ✅ `price_change_percent` - Price change percentage
- `price_change_today` - Today's price change
- `price_change_week` - Week's price change
- `price_change_month` - Month's price change
- `price_change_year` - Year's price change
- `change_percent` - Alternative change percent field

### Bid/Ask and Range Data
- ✅ `bid_price` - Current bid price
- ✅ `ask_price` - Current ask price
- `bid_ask_spread` - Spread between bid and ask
- `days_range` - Day's trading range (string)
- ✅ `days_low` - Day's low price
- ✅ `days_high` - Day's high price

### Volume Data
- ✅ `volume` - Current trading volume
- `volume_today` - Today's volume
- `avg_volume_3mon` - 3-month average volume
- `dvav` - Day Volume Over Average Volume ratio
- `shares_available` - Total shares available

### Market Data
- ✅ `market_cap` - Market capitalization
- `market_cap_change_3mon` - 3-month market cap change

### Financial Ratios
- ✅ `pe_ratio` - Price to Earnings ratio
- `pe_change_3mon` - 3-month P/E change
- ✅ `dividend_yield` - Dividend yield percentage

### Target and Predictions
- `one_year_target` - 1-year price target

### 52 Week Range
- ✅ `week_52_low` - 52-week low price
- ✅ `week_52_high` - 52-week high price

### Additional Financial Metrics
- `earnings_per_share` - EPS
- `book_value` - Book value per share
- `price_to_book` - Price to book ratio

### Metadata
- ✅ `last_updated` - Timestamp of update

**Total Fields:** ~30 fields (comprehensive daily update)

---

## Field Comparison

| Field Category | 1-Min Scanner | Daily Scanner |
|----------------|---------------|---------------|
| **Price** | current_price, price_change, price_change_percent | All price fields + historical changes |
| **Volume** | volume (day_volume) | volume + averages + DVAV |
| **Bid/Ask** | ❌ Not available | bid_price, ask_price, spread |
| **Range** | ❌ Not available | days_low, days_high, 52-week range |
| **Market Data** | ❌ Not available | market_cap, P/E ratio, dividend yield |
| **Financial Metrics** | ❌ Not available | EPS, book value, P/B ratio |

---

## yfinance API Field Mapping

### WebSocket Fields (1-Minute Scanner)
```python
# Available in WebSocket messages
{
    'id': 'AAPL',                     # ticker
    'price': 219.27,                  # current_price
    'change': 5.99,                   # price_change
    'change_percent': 2.81,           # price_change_percent
    'day_volume': '62590455',         # volume (string!)
    'time': '1754589807000',          # timestamp
    'exchange': 'NMS',                # exchange
    'last_size': '108'                # last trade size
}
```

### REST API Fields (Daily Scanner)
```python
# Available via yf.Ticker(ticker).info
{
    'regularMarketPrice': 219.27,     # current_price
    'bid': 219.25,                    # bid_price
    'ask': 219.30,                    # ask_price
    'dayLow': 215.50,                 # days_low
    'dayHigh': 220.10,                # days_high
    'volume': 62590455,               # volume (integer)
    'averageVolume': 55000000,        # avg_volume_3mon
    'marketCap': 3400000000000,       # market_cap
    'trailingPE': 28.5,               # pe_ratio
    'dividendYield': 0.0045,          # dividend_yield
    'fiftyTwoWeekLow': 180.50,        # week_52_low
    'fiftyTwoWeekHigh': 230.75,       # week_52_high
    'earningsPerShare': 7.50,         # earnings_per_share
    'bookValue': 4.25,                # book_value
    'priceToBook': 51.5,              # price_to_book
    'forwardPE': 25.2,                # forward P/E
    # ... many more fields
}
```

---

## Removed: 10-Minute Scanner

**Reason for Removal:**
1. Redundant with 1-minute scanner (same price/volume data)
2. Load test showed 43-minute actual scan time (not 10 minutes)
3. Without proxies, achieves only 3.4 t/s (not 15 t/s)
4. Adds unnecessary complexity

**Replacement Strategy:**
- 1-Minute scanner provides frequent real-time updates (every 60s)
- Daily scanner provides comprehensive data (once per day)
- Together they cover all use cases without the 10-minute scanner

---

## Scanner Configuration Summary

### 1-Minute Scanner (scanner_1min_hybrid.py)
- **Method:** WebSocket (yfinance AsyncWebSocket)
- **Rate:** Real-time, no rate limits
- **Fields:** 5 fields (price, change, change%, volume, timestamp)
- **Frequency:** Every 60 seconds during market hours
- **Stocks:** ALL 8,782 stocks
- **Time:** <60 seconds per scan
- **Status:** ✅ KEEP - Real-time essentials

### Daily Scanner (realtime_daily_with_proxies.py)
- **Method:** REST API (yfinance Ticker.info)
- **Rate:** 3.5 t/s (realistic, achievable)
- **Fields:** ~30 fields (comprehensive market data)
- **Frequency:** Once daily (12 AM - 5 AM)
- **Stocks:** ALL 8,782 stocks
- **Time:** ~42 minutes per scan (8782 / 3.5 t/s = 2,509s)
- **Status:** ✅ KEEP - Daily comprehensive update

### ~~10-Minute Scanner~~ (REMOVED)
- **Status:** ❌ REMOVE - Redundant and underperforming

---

## Implementation Plan

1. **Remove 10-Minute Scanner Files**
   - Delete `scanner_10min_fast.py`
   - Delete `scanner_10min_priority.py`
   - Delete `run_10min_scanner.bat`
   - Remove from scheduled tasks

2. **Update Daily Scanner**
   - Rename to reflect realistic timing
   - Configure for 3.5 t/s rate (achievable)
   - Disable proxies (adds overhead, no benefit at this rate)
   - Update field extraction to pull all ~30 fields

3. **Update 1-Minute Scanner**
   - Already correctly configured
   - Volume extraction fixed (uses `day_volume`)
   - Keep as-is

4. **Update Scheduled Tasks**
   - Daily: Run at 12 AM (completes by 1 AM)
   - 1-Minute: Run continuously during market hours

---

## Testing Plan

1. **Test Daily Scanner** (5-10 tickers)
   - Verify all ~30 fields are populated
   - Check rate control (~3.5 t/s)
   - Confirm no errors

2. **Test 1-Minute Scanner** (during market hours)
   - Verify 5 fields are updated
   - Check WebSocket connection stability
   - Confirm volume extraction works

3. **Database Verification**
   - Query random stocks to verify field population
   - Check last_updated timestamps
   - Ensure no null values where data should exist
