# Stock Scanner API Endpoints & Management Commands

## Overview

This document provides a complete reference for all API endpoints and Django management commands in the Stock Scanner system.

---

## 🌐 API Endpoints

### Admin Dashboard Endpoints

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
- `limit`: Number of articles to return (default: 20)
- `sentiment`: Filter by sentiment grade (A, B, C, D, F)
**Response Format**: JSON

### Core Application Endpoints

#### `GET /`
**Description**: Home page redirect  
**Authentication**: None  
**Response**: Redirect to admin dashboard

#### `GET /filter/`
**Description**: Stock filtering interface  
**Authentication**: None  
**Response**: HTML page with stock filtering tools

#### `GET /wordpress-stocks/`
**Description**: Admin page to view WordPress stock data  
**Authentication**: None  
**Response**: HTML page displaying stock data as consumed by WordPress

#### `GET /wordpress-news/`
**Description**: Admin page to view WordPress news data  
**Authentication**: None  
**Response**: HTML page displaying news data as consumed by WordPress

---

## 🛠️ Django Management Commands

### Data Loading Commands

#### `python manage.py load_nasdaq_only`
**Description**: Load NASDAQ ticker symbols and company information  
**Usage**: `python manage.py load_nasdaq_only`  
**Function**: 
- Reads NASDAQ ticker data from CSV files
- Creates Stock objects for each ticker
- Updates company names and basic information
- Skips duplicates based on ticker symbol
**Output**: Progress information and count of loaded stocks

#### `python manage.py update_stocks_yfinance`
**Description**: Update stock prices using Yahoo Finance API  
**Usage**: `python manage.py update_stocks_yfinance [--ticker TICKER] [--limit LIMIT]`  
**Options**:
- `--ticker`: Update specific ticker only
- `--limit`: Limit number of stocks to update
**Function**:
- Fetches real-time price data from Yahoo Finance
- Updates current_price, volume, market_cap, pe_ratio
- Calculates price changes and percentages
- Handles API rate limiting and errors

#### `python manage.py update_nasdaq_now`
**Description**: Manually trigger immediate NASDAQ data and news update  
**Usage**: `python manage.py update_nasdaq_now`  
**Function**:
- Calls update_stocks_yfinance command
- Triggers news scraping via news.scraper module
- Provides consolidated progress reporting
- Same functionality as the scheduled updates

### News Management Commands

#### `python manage.py scrape_news`
**Description**: Scrape news articles from configured sources  
**Usage**: `python manage.py scrape_news [--source SOURCE] [--limit LIMIT]`  
**Options**:
- `--source`: Scrape from specific source only
- `--limit`: Limit number of articles to scrape
**Function**:
- Scrapes news from Yahoo Finance and other sources
- Performs sentiment analysis using NLTK
- Extracts mentioned stock tickers
- Saves articles to NewsArticle model

### Notification Commands

#### `python manage.py send_notifications`
**Description**: Send pending stock alert notifications  
**Usage**: `python manage.py send_notifications [--user-id USER_ID] [--alert-type TYPE]`  
**Options**:
- `--user-id`: Send notifications for specific user
- `--alert-type`: Send specific type of alerts only
**Function**:
- Checks all active stock alerts
- Compares current prices with alert conditions
- Sends email notifications for triggered alerts
- Updates alert status and last_sent timestamps

### Database Management Commands

#### `python manage.py optimize_database`
**Description**: Optimize database tables and clean up old data  
**Usage**: `python manage.py optimize_database [--tables TABLE1,TABLE2] [--days DAYS]`  
**Options**:
- `--tables`: Optimize specific tables only
- `--days`: Keep data for specified days (default: 90)
**Function**:
- Optimizes MySQL table indexes
- Removes old stock price history
- Cleans up expired user sessions
- Removes old news articles based on retention policy
- Analyzes table statistics

#### `python manage.py cleanup_old_data`
**Description**: Remove old data based on retention policies  
**Usage**: `python manage.py cleanup_old_data [--dry-run] [--days DAYS]`  
**Options**:
- `--dry-run`: Show what would be deleted without actually deleting
- `--days`: Retention period in days
**Function**:
- Removes stock price data older than retention period
- Cleans up old news articles
- Removes expired user sessions
- Cleans up old API usage logs

---

## 🔧 Command Usage Examples

### Daily Operations
```bash
# Update stock prices (automated via scheduler)
python manage.py update_stocks_yfinance

# Send pending notifications
python manage.py send_notifications

# Clean up old data
python manage.py cleanup_old_data --days 90
```

### Weekly Maintenance
```bash
# Optimize database
python manage.py optimize_database

# Check system health
python manage.py monitor_system
python manage.py check_api_health

# Sync membership levels
python manage.py sync_membership_levels
```

### Emergency Operations
```bash
# Manual data update
python manage.py update_nasdaq_now

# Force database optimization
python manage.py optimize_database --tables stocks_stock,stocks_stockprice

# Check system status
python manage.py monitor_system --alert-threshold 80
```

---

## 📝 Notes

### Authentication Requirements
- **Public Endpoints**: Most admin and WordPress integration endpoints are public
- **User Endpoints**: Paywall and membership endpoints require user authentication
- **Admin Endpoints**: System metrics and sensitive operations may require admin privileges

### Rate Limiting
- External API calls (Yahoo Finance) are rate-limited
- Internal API endpoints have configurable rate limits based on membership level
- Emergency mode affects API access based on membership tier

### Error Handling
- All endpoints return consistent JSON error responses
- Management commands provide detailed error logging
- Failed operations include retry mechanisms where appropriate

### Monitoring
- All API calls are logged for usage tracking
- System metrics are continuously monitored
- Alerts are sent for system issues or threshold breaches

This comprehensive reference covers all available API endpoints and management commands in the Stock Scanner system.