# WebSocket Data Sources with Volume Information

## Overview

This document lists alternative WebSocket data sources that provide real-time volume information for stocks, along with implementation details for each.

---

## Current Implementation: yfinance WebSocket

### Volume Fields Available

The yfinance WebSocket already provides volume data in its messages:

**Volume Fields:**
- `day_volume`: Cumulative trading volume for the day (string, e.g., '62590455')
- `last_size`: Size of the most recent trade (string, e.g., '108')

**Complete Message Example:**
```python
{
    'id': 'AAPL',
    'price': 219.2684,
    'time': '1754589807000',
    'exchange': 'NMS',
    'quote_type': 8,
    'market_hours': 1,
    'change_percent': 2.8101785,
    'day_volume': '62590455',      # ← VOLUME DATA
    'change': 5.993408,
    'last_size': '108',             # ← TRADE SIZE
    'price_hint': '2'
}
```

### Fix for Current Scanner

**The 1-minute scanner already has volume support added!** The code now extracts `volume` from WebSocket messages:

```python
# scanner_1min_hybrid.py (already updated)
def websocket_message_handler(self, message):
    ticker = message.get('id', '')
    if ticker:
        self.websocket_updates[ticker] = {
            'current_price': message.get('price'),
            'price_change': message.get('change'),
            'price_change_percent': message.get('change_percent'),
            'volume': message.get('volume'),  # ✅ Already added
            'timestamp': datetime.now()
        }
```

**To properly extract volume from yfinance WebSocket:**

Update the field mapping to use the correct field name:
```python
# Change from:
'volume': message.get('volume')

# To:
'volume': int(message.get('day_volume', 0)) if message.get('day_volume') else None
```

---

## Alternative WebSocket Sources

### 1. Finnhub (FREE TIER AVAILABLE) ⭐ RECOMMENDED

**Features:**
- Free API key with 60 API calls/minute
- WebSocket support for real-time trades
- Volume field included in every message
- Good documentation and Python support

**Volume Field:** `v` (integer representing trade volume)

**Message Format:**
```json
{
    "data": [
        {
            "s": "AAPL",      // Symbol
            "p": 219.27,      // Last price
            "t": 1754589807,  // Timestamp
            "v": 100,         // Volume (shares in this trade)
            "c": ["12"]       // Trade conditions
        }
    ],
    "type": "trade"
}
```

**Python Implementation:**
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    for trade in data.get('data', []):
        symbol = trade['s']
        price = trade['p']
        volume = trade['v']        # Volume field
        timestamp = trade['t']
        print(f"{symbol}: ${price}, Vol: {volume}")

def on_open(ws):
    # Subscribe to tickers
    ws.send(json.dumps({'type': 'subscribe', 'symbol': 'AAPL'}))
    ws.send(json.dumps({'type': 'subscribe', 'symbol': 'MSFT'}))

# Connect
api_key = "YOUR_API_KEY"
ws = websocket.WebSocketApp(
    f"wss://ws.finnhub.io?token={api_key}",
    on_message=on_message,
    on_open=on_open
)
ws.run_forever()
```

**Pros:**
- Free tier available
- Easy to implement
- Good documentation
- Volume included in every trade message

**Cons:**
- Rate limited on free tier (60 calls/min)
- Only US market on free tier
- May need paid plan for 8,782 stocks

**Sign up:** [https://finnhub.io](https://finnhub.io/docs/api/websocket-trades)

---

### 2. Polygon.io (FREE TIER: 5 API calls/min)

**Features:**
- Free tier available (limited)
- Real-time and historical data
- WebSocket streaming
- Professional-grade quality

**Volume Field:** `v` (size of the trade)

**Message Format:**
```json
{
    "ev": "T",           // Event type (T = trade)
    "sym": "AAPL",       // Symbol
    "x": 4,              // Exchange ID
    "p": 219.27,         // Price
    "s": 100,            // Trade size (volume)
    "t": 1754589807000,  // Timestamp
    "c": [14, 41]        // Trade conditions
}
```

**Python Implementation:**
```python
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage

def on_message(msgs):
    for m in msgs:
        if m.event_type == 'T':  # Trade
            print(f"{m.symbol}: ${m.price}, Vol: {m.size}")

api_key = "YOUR_API_KEY"
client = WebSocketClient(api_key, on_message)
client.subscribe("T.AAPL", "T.MSFT")  # Subscribe to trades
client.run()
```

**Pros:**
- High-quality data
- Professional API
- Good Python library

**Cons:**
- Very limited free tier (5 calls/min)
- Paid plans required for production ($99+/month)

**Sign up:** [https://polygon.io](https://polygon.io/)

---

### 3. Alpha Vantage (FREE TIER AVAILABLE)

**Features:**
- Free API key
- 25 API calls/day on free tier (very limited)
- Good for small-scale projects
- No WebSocket on free tier (REST only)

**Volume Field:** Available in REST API, but WebSocket requires premium

**Pros:**
- Truly free
- Easy to use
- Good documentation

**Cons:**
- No WebSocket on free tier
- Very limited rate (25 calls/day)
- Not suitable for real-time 8,782 stocks

**Sign up:** [https://www.alphavantage.co](https://www.alphavantage.co/)

---

### 4. Twelve Data (PAID: $19+/month for WebSocket)

**Features:**
- WebSocket streaming
- Real-time quotes
- Volume included
- Unlimited requests on paid plans

**Volume Field:** `volume` in quote messages

**Message Format:**
```json
{
    "event": "quote",
    "symbol": "AAPL",
    "price": 219.27,
    "volume": 62590455,
    "timestamp": 1754589807
}
```

**Pros:**
- Affordable ($19/month)
- Unlimited requests
- Good coverage

**Cons:**
- No free WebSocket tier
- Requires payment

**Sign up:** [https://twelvedata.com](https://twelvedata.com/)

---

### 5. IEX Cloud (PAID: $9+/month)

**Features:**
- U.S. market data
- WebSocket streaming
- Transparent pricing
- Good developer experience

**Volume Field:** `volume` in trade messages

**Pros:**
- Reliable data
- Developer-friendly
- Transparent pricing

**Cons:**
- Paid only
- U.S. stocks only

**Sign up:** https://iexcloud.io

---

### 6. yflive (Alternative yfinance WebSocket Library)

**Features:**
- Free Yahoo Finance data
- WebSocket streaming
- Alternative to yfinance
- Volume included

**Python Implementation:**
```python
from yliveticker import YLiveTicker

def on_ticker(data):
    symbol = data['id']
    price = data['price']
    volume = data.get('dayVolume', 0)  # Volume field
    print(f"{symbol}: ${price}, Vol: {volume}")

ticker = YLiveTicker(['AAPL', 'MSFT'])
ticker.on_ticker = on_ticker
ticker.start()
```

**Pros:**
- Free
- Direct Yahoo Finance data
- Easy to implement

**Cons:**
- Unofficial library
- May break if Yahoo changes format
- Rate limiting possible

**GitHub:** [https://github.com/yahoofinancelive/yliveticker](https://github.com/yahoofinancelive/yliveticker)

---

### 7. EODHD (PAID: Real-Time WebSocket)

**Features:**
- Real-time data with <50ms delay
- WebSocket streaming
- 50 tickers simultaneously
- Global coverage

**Volume Field:** Included in real-time messages

**Pros:**
- Low latency
- Good coverage
- WebSocket support

**Cons:**
- Paid subscription required
- Limited concurrent tickers (50)

**Sign up:** [https://eodhd.com/financial-apis/new-real-time-data-api-websockets](https://eodhd.com/financial-apis/new-real-time-data-api-websockets)

---

## Comparison Table

| Source | Free Tier | WebSocket | Volume Field | Rate Limit | Best For |
|--------|-----------|-----------|--------------|------------|----------|
| **yfinance** | ✅ Yes | ✅ Yes | `day_volume` | Unknown | Current solution |
| **Finnhub** | ✅ Yes | ✅ Yes | `v` | 60/min | ⭐ Best free alternative |
| **Polygon** | ⚠️ Limited | ✅ Yes | `s` | 5/min | Professional use |
| **Alpha Vantage** | ✅ Yes | ❌ No | N/A | 25/day | Testing only |
| **Twelve Data** | ❌ No | ✅ Yes | `volume` | Unlimited | Paid option |
| **IEX Cloud** | ❌ No | ✅ Yes | `volume` | Varies | U.S. stocks |
| **yflive** | ✅ Yes | ✅ Yes | `dayVolume` | Unknown | Yahoo backup |
| **EODHD** | ❌ No | ✅ Yes | Included | 50 tickers | Limited use |

---

## Recommendations

### For Your Use Case (8,782 stocks, real-time updates)

#### Option 1: Fix Current yfinance WebSocket ✅ RECOMMENDED

**Action Required:**
Update `scanner_1min_hybrid.py` to properly extract volume:

```python
def websocket_message_handler(self, message):
    """Handle WebSocket messages - store price and volume updates"""
    ticker = message.get('id', '')
    if ticker:
        # Extract volume from the correct field
        day_volume = message.get('day_volume')
        volume = int(day_volume) if day_volume else None

        self.websocket_updates[ticker] = {
            'current_price': message.get('price'),
            'price_change': message.get('change'),
            'price_change_percent': message.get('change_percent'),
            'volume': volume,  # Fixed to use day_volume
            'timestamp': datetime.now()
        }
```

**Pros:**
- Already implemented
- Free
- No API key needed
- Supports all 8,782 stocks

**Cons:**
- Unofficial Yahoo Finance usage
- May be rate limited
- Could break if Yahoo changes format

---

#### Option 2: Switch to Finnhub WebSocket

**Good for:** Reliable free tier, official API

**Requirements:**
1. Sign up for free API key at [Finnhub.io](https://finnhub.io)
2. Rewrite scanner to use Finnhub WebSocket
3. Handle 60 API calls/minute limit

**Implementation Strategy:**
- Subscribe to 60 stocks at a time
- Rotate subscriptions every minute
- Complete coverage in ~146 minutes (8782 / 60)

**Not suitable for 1-minute updates of all stocks.**

---

#### Option 3: Paid Service (Twelve Data or Polygon)

**Good for:** Production reliability, unlimited stocks

**Cost:** $19-99/month

**Benefits:**
- Official support
- No rate limits
- Reliable data
- Professional quality

---

## Implementation: Fix yfinance WebSocket Volume

Here's the complete updated code for `scanner_1min_hybrid.py`:

```python
def websocket_message_handler(self, message):
    """Handle WebSocket messages - store price and volume updates"""
    ticker = message.get('id', '')
    if ticker:
        # Extract volume from day_volume field (Yahoo's field name)
        day_volume_str = message.get('day_volume', '0')
        try:
            volume = int(day_volume_str) if day_volume_str else None
        except (ValueError, TypeError):
            volume = None

        self.websocket_updates[ticker] = {
            'current_price': message.get('price'),
            'price_change': message.get('change'),
            'price_change_percent': message.get('change_percent'),
            'volume': volume,  # Now correctly extracts from day_volume
            'timestamp': datetime.now()
        }
```

---

## Conclusion

**RECOMMENDED SOLUTION:**

Fix the current yfinance WebSocket implementation to properly extract `day_volume`:
1. Update field mapping from `message.get('volume')` to `message.get('day_volume')`
2. Convert string to integer
3. Handle parse errors gracefully

This solution:
- ✅ Free
- ✅ Already implemented
- ✅ Supports all 8,782 stocks
- ✅ Real-time updates
- ✅ Includes volume data

**Alternative if yfinance breaks:** Finnhub (free tier, but limited to 60 stocks/minute)

---

## Sources

- [yfinance WebSocket Documentation](https://ranaroussi.github.io/yfinance/reference/api/yfinance.WebSocket.html)
- [Finnhub WebSocket API](https://finnhub.io/docs/api/websocket-trades)
- [Polygon.io Stock API](https://polygon.io/)
- [Twelve Data - Yahoo Finance Alternatives](https://twelvedata.com/news/10-best-yahoo-finance-alternatives-for-2023)
- [yfinance Alert Manager Tutorial](https://www.marketcalls.in/python/how-to-build-yfinance-alert-manager-using-yfinance-websockets-python-tutorial.html)
- [Finnhub Python Tutorial - Analyzing Alpha](https://analyzingalpha.com/finnhub-api-python-tutorial)
- [yliveticker GitHub](https://github.com/yahoofinancelive/yliveticker)
- [EODHD Real-Time WebSocket API](https://eodhd.com/financial-apis/new-real-time-data-api-websockets)
- [Beyond yFinance: Best Financial Data APIs](https://medium.com/@trading.dude/beyond-yfinance-comparing-the-best-financial-data-apis-for-traders-and-developers-06a3b8bc07e2)
- [Live Data Streaming | DeepWiki](https://deepwiki.com/ranaroussi/yfinance/4.6-live-data-streaming)
