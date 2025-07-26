# Stock Scanner API Endpoints & Management Commands

## Overview

This document provides a complete reference for all API endpoints and Django management commands in the Stock Scanner system.

**📈 NEW: Enhanced Stock APIs with comprehensive data and advanced filtering!**

---

## 🆕 Enhanced Stock API Endpoints

### Core Stock Data Endpoints

#### `GET /api/stocks/`
**Description**: Get comprehensive list of stocks with full data and advanced filtering
**Authentication**: None (public access)
**Parameters**:
- `limit`: Number of stocks to return (default: 50, max: 1000)
- `search`: Search by ticker or company name
- `category`: Filter by category (`gainers`, `losers`, `high_volume`, `large_cap`, `small_cap`)
- `min_price`: Minimum price filter (decimal)
- `max_price`: Maximum price filter (decimal)
- `min_volume`: Minimum volume filter (integer)
- `min_market_cap`: Minimum market cap filter (integer)
- `max_market_cap`: Maximum market cap filter (integer)
- `min_pe`: Minimum P/E ratio filter (decimal)
- `max_pe`: Maximum P/E ratio filter (decimal)
- `exchange`: Filter by exchange (default: NASDAQ)
- `sort_by`: Sort field (`price`, `volume`, `market_cap`, `change_percent`, `pe_ratio`)
- `sort_order`: Sort order (`asc`, `desc`) default: desc

**Example Request**:
```
GET /api/stocks/?category=gainers&min_price=50&max_price=500&limit=100&sort_by=change_percent
```

**Example Response**:
```json
{
  "success": true,
  "count": 25,
  "total_available": 156,
  "filters_applied": {
    "category": "gainers",
    "min_price": "50",
    "max_price": "500",
    "sort_by": "change_percent",
    "sort_order": "desc"
  },
  "data": [
    {
      "ticker": "AAPL",
      "symbol": "AAPL",
      "company_name": "Apple Inc.",
      "exchange": "NASDAQ",
      "current_price": 175.25,
      "price_change_today": 5.30,
      "price_change_week": 12.50,
      "price_change_month": 25.80,
      "price_change_year": 45.60,
      "change_percent": 3.12,
      "bid_price": 175.20,
      "ask_price": 175.30,
      "days_low": 172.50,
      "days_high": 176.80,
      "volume": 89543210,
      "avg_volume_3mon": 67890123,
      "market_cap": 2850000000000,
      "pe_ratio": 28.45,
      "dividend_yield": 0.52,
      "week_52_low": 125.30,
      "week_52_high": 198.45,
      "earnings_per_share": 6.15,
      "book_value": 4.25,
      "price_to_book": 41.23,
      "one_year_target": 195.00,
      "formatted_price": "$175.25",
      "formatted_change": "+3.12%",
      "formatted_volume": "89,543,210",
      "formatted_market_cap": "$2.85T",
      "last_updated": "2025-01-27T10:30:00Z",
      "is_gaining": true,
      "is_losing": false,
      "volume_ratio": 1.32,
      "wordpress_url": "/stock/aapl/"
    }
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### `GET /api/stocks/{ticker}/`
**Description**: Get comprehensive detailed information for a specific stock
**Authentication**: None
**Parameters**: None (ticker in URL)

**Example Request**: `GET /api/stocks/AAPL/`

**Example Response**:
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "current_price": 175.25,
    "price_change_today": 5.30,
    "change_percent": 3.12,
    "volume": 89543210,
    "market_cap": 2850000000000,
    "pe_ratio": 28.45,
    "dividend_yield": 0.52,
    "week_52_low": 125.30,
    "week_52_high": 198.45,
    "price_near_52_week_high": false,
    "price_near_52_week_low": false,
    "price_position_52_week": 68.5,
    "price_history": [
      {
        "price": 175.25,
        "timestamp": "2025-01-27T10:30:00Z"
      }
    ],
    "data_quality": {
      "has_price": true,
      "has_volume": true,
      "has_market_cap": true,
      "has_pe_ratio": true,
      "last_update_age_minutes": 2.5
    }
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### `GET /api/stocks/nasdaq/`
**Description**: Get all NASDAQ-listed stocks with comprehensive data
**Authentication**: None
**Parameters**:
- `limit`: Number of stocks to return (default: 500, max: 1000)

**Example Response**:
```json
{
  "success": true,
  "exchange": "NASDAQ",
  "count": 146,
  "total_nasdaq_tickers": 146,
  "data": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.25,
      "price_change_today": 5.30,
      "change_percent": 3.12,
      "volume": 89543210,
      "market_cap": 2850000000000,
      "pe_ratio": 28.45,
      "formatted_price": "$175.25",
      "formatted_change": "+3.12%",
      "formatted_market_cap": "$2.85T",
      "last_updated": "2025-01-27T10:30:00Z",
      "is_gaining": true
    }
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### `GET /api/stocks/search/`
**Description**: Advanced stock search with multiple criteria
**Authentication**: None
**Parameters**:
- `q`: Search query (required) - searches ticker, symbol, and company name

**Example Request**: `GET /api/stocks/search/?q=Apple`

**Example Response**:
```json
{
  "success": true,
  "query": "Apple",
  "count": 1,
  "results": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.25,
      "change_percent": 3.12,
      "market_cap": 2850000000000,
      "exchange": "NASDAQ",
      "match_type": "company",
      "url": "/api/stocks/AAPL/"
    }
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Market Data Endpoints

#### `GET /api/market/stats/`
**Description**: Get comprehensive market statistics and overview
**Authentication**: None
**Response Format**: JSON with market overview, top performers, volume leaders

#### `GET /api/market/filter/`
**Description**: Advanced stock filtering with multiple criteria
**Authentication**: None
**Parameters**: Multiple filtering options (price, volume, market cap, P/E, sector)

### Real-time Data Endpoints

#### `GET /api/realtime/{ticker}/`
**Description**: Get real-time stock data with live yfinance integration
**Authentication**: None
**Response**: Live stock data with real-time prices

#### `GET /api/trending/`
**Description**: Get trending/most active stocks
**Authentication**: None
**Response**: List of high-volume and trending stocks

---

## 🔄 Automated Data Updates

### Enhanced Update System

The system now includes a **5-minute auto-scheduler** that:

- ✅ Updates NASDAQ stocks every 5 minutes automatically
- ✅ Uses multithreaded processing for high performance
- ✅ Focuses on NASDAQ-listed securities only
- ✅ Collects comprehensive data (price, volume, ratios, financials)
- ✅ Starts automatically on system startup
- ✅ Includes error handling and retry logic

### Management Commands

#### `python manage.py update_stocks_yfinance --startup --nasdaq-only`
**Description**: Start the enhanced 5-minute scheduler with NASDAQ focus
**New Features**:
- `--startup`: Runs initial update then starts scheduler
- `--nasdaq-only`: Updates only NASDAQ-listed tickers (default: True)
- `--schedule`: Runs continuous 5-minute updates
- `--threads`: Number of concurrent threads (default: 10)
- `--limit`: Maximum stocks to update (default: 500)

#### `python manage.py load_nasdaq_only`
**Description**: Load NASDAQ-only ticker symbols into database
**Features**:
- Loads 146 curated NASDAQ tickers
- Excludes NYSE, ARCA, BATS exchanges
- Updates existing records with new information

### Startup Integration

#### Auto-Scheduler Startup
```bash
# Start scheduler automatically
python start_stock_scheduler.py

# Create system service (Linux)
python start_stock_scheduler.py --create-service

# Check environment only
python start_stock_scheduler.py --check-only
```

#### Integrated Startup Script
The main startup script (`./start_django_gitbash.sh`) now includes:
- Optional stock scheduler startup
- Background scheduler process management
- Automatic cleanup on exit
- Integrated logging

---

## 🎯 Key Improvements

### API Enhancements
1. **Full Data Model**: All Stock model fields available in APIs
2. **Advanced Filtering**: Price, volume, market cap, P/E ratio filters
3. **Multiple Sorting**: Sort by any field with asc/desc order
4. **Comprehensive Search**: Search across ticker, symbol, and company name
5. **Data Quality Indicators**: Timestamps, data freshness, completeness
6. **Price History**: Recent price movements included
7. **Calculated Metrics**: Price position relative to 52-week range

### Data Collection Improvements
1. **5-Minute Updates**: Frequent automatic updates
2. **NASDAQ Focus**: 146 curated NASDAQ tickers
3. **Multithreaded Processing**: 10 concurrent threads for speed
4. **Comprehensive Data**: 25+ data points per stock
5. **Error Handling**: Robust retry and error recovery
6. **Rate Limiting**: Respectful API usage with delays

### System Integration
1. **Auto-Startup**: Scheduler starts with system
2. **Service Creation**: Systemd/Windows service support
3. **Background Processing**: Non-blocking data updates
4. **Logging**: Comprehensive logging and monitoring
5. **Cleanup**: Proper process management and cleanup

---

## Admin Dashboard Endpoints

#### `GET /admin-dashboard/`
**Description**: Main admin dashboard interface 
**Authentication**: None (public access) 
**Response**: HTML page with admin controls and system overview 
**Features**:
- System status metrics
- NASDAQ scheduler status
- Manual update controls
- Real-time system monitoring

#### `GET /api/admin/status/`
**Description**: Get comprehensive system status information 
**Authentication**: None 
**Response Format**: JSON 
**Example Response**:
```json
{
"total_stocks": 3500,
"unsent_notifications": 12,
"success_rate": 98.5,
"last_update": "2024-01-15 14:30:00",
"total_news": 1250,
"scheduler_status": "running",
"next_run": "2024-01-15 14:40:00",
"system_health": {
"cpu_usage": 45.2,
"memory_usage": 62.1,
"disk_usage": 78.3
}
}
```

#### `POST /api/admin/load-nasdaq/`
**Description**: Manually trigger NASDAQ data loading 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with operation status

#### `POST /api/admin/update-stocks/`
**Description**: Manually update stock prices using yfinance 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with update results

#### `POST /api/admin/update-nasdaq-now/`
**Description**: Manually trigger immediate NASDAQ data and news update 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with operation status

#### `GET /api/admin/api-providers/`
**Description**: Get status of external API providers 
**Authentication**: None 
**Response Format**: JSON

#### `POST /api/admin/scrape-news/`
**Description**: Manually trigger news scraping 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with scraping results

#### `POST /api/admin/send-notifications/`
**Description**: Manually trigger sending pending notifications 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with notification results

#### `POST /api/admin/optimize-db/`
**Description**: Manually trigger database optimization 
**Authentication**: None 
**Method**: POST 
**Response**: JSON with optimization results

### WordPress Integration Endpoints

#### `GET /api/wordpress/stocks/`
**Description**: Get stock data formatted for WordPress consumption 
**Authentication**: None 
**Query Parameters**:
- `limit`: Number of stocks to return (default: 50)
- `sort`: Sort field (volume, price, change)
- `filter`: Filter criteria
**Response Format**: JSON

#### `GET /api/wordpress/news/`
**Description**: Get news data formatted for WordPress consumption 
**Authentication**: None 
**Query Parameters**: