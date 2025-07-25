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
**Example Response**:
```json
{
  "success": true,
  "message": "NASDAQ data loading initiated",
  "stocks_loaded": 3500
}
```

#### `POST /api/admin/update-stocks/`
**Description**: Manually update stock prices using yfinance  
**Authentication**: None  
**Method**: POST  
**Response**: JSON with update results  
**Example Response**:
```json
{
  "success": true,
  "message": "Stock prices updated successfully",
  "stocks_updated": 3450,
  "failed_updates": 50
}
```

#### `POST /api/admin/update-nasdaq-now/`
**Description**: Manually trigger immediate NASDAQ data and news update  
**Authentication**: None  
**Method**: POST  
**Response**: JSON with operation status  
**Example Response**:
```json
{
  "success": true,
  "message": "NASDAQ data update completed",
  "execution_time": 45.2,
  "stocks_updated": 3450,
  "news_updated": 125
}
```

#### `GET /api/admin/api-providers/`
**Description**: Get status of external API providers  
**Authentication**: None  
**Response Format**: JSON  
**Example Response**:
```json
{
  "yahoo_finance": {
    "status": "operational",
    "last_check": "2024-01-15 14:30:00",
    "response_time": 0.45,
    "success_rate": 99.2
  },
  "news_scraper": {
    "status": "operational",
    "last_scrape": "2024-01-15 14:25:00",
    "articles_scraped": 125,
    "success_rate": 97.8
  }
}
```

#### `POST /api/admin/scrape-news/`
**Description**: Manually trigger news scraping  
**Authentication**: None  
**Method**: POST  
**Response**: JSON with scraping results  
**Example Response**:
```json
{
  "success": true,
  "message": "News scraping completed",
  "articles_scraped": 125,
  "new_articles": 45,
  "execution_time": 12.3
}
```

#### `POST /api/admin/send-notifications/`
**Description**: Manually trigger sending pending notifications  
**Authentication**: None  
**Method**: POST  
**Response**: JSON with notification results  
**Example Response**:
```json
{
  "success": true,
  "message": "Notifications sent successfully",
  "notifications_sent": 15,
  "failed_notifications": 2
}
```

#### `POST /api/admin/optimize-db/`
**Description**: Manually trigger database optimization  
**Authentication**: None  
**Method**: POST  
**Response**: JSON with optimization results  
**Example Response**:
```json
{
  "success": true,
  "message": "Database optimization completed",
  "tables_optimized": 8,
  "space_freed": "125 MB",
  "execution_time": 8.7
}
```

### WordPress Integration Endpoints

#### `GET /api/wordpress/stocks/`
**Description**: Get stock data formatted for WordPress consumption  
**Authentication**: None  
**Query Parameters**:
- `limit`: Number of stocks to return (default: 50)
- `sort`: Sort field (volume, price, change)
- `filter`: Filter criteria
**Response Format**: JSON  
**Example Response**:
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.25,
      "price_change": 2.15,
      "price_change_percent": 1.24,
      "volume_today": 45234567,
      "market_cap": 2750000000000,
      "pe_ratio": 28.5,
      "last_updated": "2024-01-15 14:30:00"
    }
  ],
  "total": 3500,
  "page": 1,
  "per_page": 50
}
```

#### `GET /api/wordpress/news/`
**Description**: Get news data formatted for WordPress consumption  
**Authentication**: None  
**Query Parameters**:
- `limit`: Number of articles to return (default: 20)
- `sentiment`: Filter by sentiment grade (A, B, C, D, F)
**Response Format**: JSON  
**Example Response**:
```json
{
  "results": [
    {
      "headline": "Apple Reports Strong Q4 Earnings",
      "url": "https://finance.yahoo.com/news/apple-earnings",
      "content": "Apple Inc. reported strong quarterly earnings...",
      "source": "Yahoo Finance",
      "sentiment_grade": "A",
      "sentiment_score": 85,
      "published_date": "2024-01-15 12:00:00",
      "mentioned_tickers": ["AAPL", "MSFT"]
    }
  ],
  "total": 1250,
  "page": 1,
  "per_page": 20
}
```

### Core Application Endpoints

#### `GET /`
**Description**: Home page redirect  
**Authentication**: None  
**Response**: Redirect to admin dashboard

#### `GET /filter/`
**Description**: Stock filtering interface  
**Authentication**: None  
**Response**: HTML page with stock filtering tools  
**Features**:
- Advanced stock screening
- Real-time filtering
- Export capabilities

#### `GET /wordpress-stocks/`
**Description**: Admin page to view WordPress stock data  
**Authentication**: None  
**Response**: HTML page displaying stock data as consumed by WordPress

#### `GET /wordpress-news/`
**Description**: Admin page to view WordPress news data  
**Authentication**: None  
**Response**: HTML page displaying news data as consumed by WordPress

### Stock Data Endpoints

#### `GET /api/stocks/search/`
**Description**: Search stocks by ticker or company name  
**Authentication**: None  
**Query Parameters**:
- `q`: Search query (ticker or company name)
- `limit`: Number of results (default: 10)
**Response Format**: JSON  
**Example Response**:
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.25,
      "market_cap": 2750000000000
    }
  ]
}
```

#### `GET /api/stocks/alerts/`
**Description**: Get stock alerts for authenticated users  
**Authentication**: Required  
**Response Format**: JSON  
**Example Response**:
```json
{
  "alerts": [
    {
      "id": 1,
      "ticker": "AAPL",
      "alert_type": "price_above",
      "target_price": 180.00,
      "current_price": 175.25,
      "is_active": true,
      "created_date": "2024-01-10 10:00:00"
    }
  ]
}
```

### News Endpoints

#### `GET /api/news/recent/`
**Description**: Get recent news articles  
**Authentication**: None  
**Query Parameters**:
- `limit`: Number of articles (default: 20)
- `sentiment`: Filter by sentiment
- `ticker`: Filter by mentioned ticker
**Response Format**: JSON

### Paywall & Membership Endpoints

#### `POST /api/paywall/check-access/`
**Description**: Check user access permissions  
**Authentication**: Required  
**Request Body**:
```json
{
  "user_id": 123,
  "requested_resource": "advanced_analytics",
  "action": "view"
}
```
**Response**:
```json
{
  "access_granted": true,
  "membership_level": "pro",
  "remaining_quota": 4500,
  "upgrade_url": "/membership-checkout/?level=3"
}
```

#### `GET /api/membership/status/`
**Description**: Get user membership status  
**Authentication**: Required  
**Response**:
```json
{
  "membership_level": "pro",
  "expires_at": "2024-02-15 00:00:00",
  "usage_today": {
    "api_calls": 245,
    "stock_searches": 12,
    "news_articles": 67
  },
  "limits": {
    "api_calls": 5000,
    "stock_searches": 1000,
    "news_articles": 2500
  }
}
```

### System Health Endpoints

#### `GET /api/health/`
**Description**: Basic health check endpoint  
**Authentication**: None  
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15 14:30:00",
  "version": "1.0.0"
}
```

#### `GET /api/metrics/`
**Description**: System performance metrics  
**Authentication**: Admin required  
**Response**:
```json
{
  "cpu_usage": 45.2,
  "memory_usage": 62.1,
  "disk_usage": 78.3,
  "active_connections": 25,
  "requests_per_minute": 450,
  "alert_level": "none"
}
```

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
**Example**:
```bash
Loading NASDAQ tickers...
✅ Loaded 3,500 NASDAQ stocks
⚠️ Skipped 50 duplicates
✅ NASDAQ data loading completed
```

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
**Output**: Update statistics and any errors  
**Example**:
```bash
Updating stock prices from Yahoo Finance...
✅ Updated 3,450 stocks successfully
⚠️ Failed to update 50 stocks (API errors)
📊 Average update time: 0.25 seconds per stock
✅ Stock price update completed
```

#### `python manage.py update_nasdaq_now`
**Description**: Manually trigger immediate NASDAQ data and news update  
**Usage**: `python manage.py update_nasdaq_now`  
**Function**:
- Calls update_stocks_yfinance command
- Triggers news scraping via news.scraper module
- Provides consolidated progress reporting
- Same functionality as the scheduled updates
**Output**: Combined update results  
**Example**:
```bash
🔄 Starting manual NASDAQ data update...
📈 Updating NASDAQ stock prices...
📰 Updating news data...
✅ NASDAQ data update completed in 45.2 seconds
```

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
**Output**: Scraping statistics and article count  
**Example**:
```bash
🔍 Scraping news articles...
📰 Yahoo Finance: 125 articles scraped
🎯 Sentiment analysis completed
📊 Found 45 new articles
✅ News scraping completed
```

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
**Output**: Notification sending results  
**Example**:
```bash
📧 Checking stock alerts...
🔔 Found 15 triggered alerts
📨 Sent 13 notifications successfully
⚠️ Failed to send 2 notifications
✅ Notification sending completed
```

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
**Output**: Optimization results and space freed  
**Example**:
```bash
🔧 Optimizing database tables...
📊 stocks_stockprice: Optimized, freed 125 MB
📰 news_newsarticle: Cleaned 500 old articles
🗂️ Rebuilt 5 table indexes
✅ Database optimization completed
```

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
**Output**: Cleanup statistics  
**Example**:
```bash
🧹 Cleaning up old data...
📈 Removed 10,000 old stock prices (>90 days)
📰 Removed 500 old news articles (>30 days)
🗑️ Freed 250 MB of storage
✅ Data cleanup completed
```

### User Management Commands

#### `python manage.py create_test_users`
**Description**: Create test users for different membership levels  
**Usage**: `python manage.py create_test_users [--count COUNT]`  
**Options**:
- `--count`: Number of test users per membership level
**Function**:
- Creates users for each membership tier
- Sets up test stock alerts
- Configures test usage data
- Useful for testing and development
**Output**: Created user information  
**Example**:
```bash
👥 Creating test users...
✅ Created 5 Free users
✅ Created 5 Basic users  
✅ Created 5 Pro users
✅ Created 5 Enterprise users
🔔 Set up test alerts for all users
✅ Test user creation completed
```

#### `python manage.py sync_membership_levels`
**Description**: Sync membership levels between WordPress and Django  
**Usage**: `python manage.py sync_membership_levels [--user-id USER_ID]`  
**Options**:
- `--user-id`: Sync specific user only
**Function**:
- Queries WordPress database for membership levels
- Updates Django user membership information
- Syncs usage limits and permissions
- Handles membership changes and cancellations
**Output**: Sync results and any discrepancies  
**Example**:
```bash
🔄 Syncing membership levels...
👤 Updated 15 user memberships
⬆️ 3 users upgraded to Pro
⬇️ 1 user downgraded to Basic
✅ Membership sync completed
```

### Monitoring Commands

#### `python manage.py monitor_system`
**Description**: Monitor system resources and performance  
**Usage**: `python manage.py monitor_system [--alert-threshold PERCENT]`  
**Options**:
- `--alert-threshold`: CPU/Memory threshold for alerts
**Function**:
- Monitors CPU, memory, and disk usage
- Checks API response times
- Monitors database performance
- Sends alerts if thresholds exceeded
- Logs system metrics
**Output**: Current system status and any alerts  
**Example**:
```bash
📊 Monitoring system resources...
💻 CPU Usage: 45.2%
🧠 Memory Usage: 62.1%
💾 Disk Usage: 78.3%
🌐 API Response Time: 0.25s
✅ All systems operating normally
```

#### `python manage.py check_api_health`
**Description**: Check health of external API integrations  
**Usage**: `python manage.py check_api_health [--provider PROVIDER]`  
**Options**:
- `--provider`: Check specific provider only (yahoo, news)
**Function**:
- Tests Yahoo Finance API connectivity
- Checks news scraping endpoints
- Measures response times
- Validates data quality
- Reports any issues or degradations
**Output**: API health status report  
**Example**:
```bash
🔍 Checking API health...
✅ Yahoo Finance: Operational (0.45s response)
✅ News Sources: Operational (1.2s response)
📊 Success Rate: 99.2%
✅ All APIs healthy
```

### Development Commands

#### `python manage.py generate_test_data`
**Description**: Generate test data for development and testing  
**Usage**: `python manage.py generate_test_data [--stocks COUNT] [--news COUNT]`  
**Options**:
- `--stocks`: Number of test stocks to create
- `--news`: Number of test news articles to create
**Function**:
- Creates realistic test stock data
- Generates test news articles with sentiment
- Creates test user alerts and usage data
- Useful for development and testing
**Output**: Generated data statistics  
**Example**:
```bash
🧪 Generating test data...
📈 Created 100 test stocks
📰 Created 50 test news articles
🔔 Created 25 test alerts
✅ Test data generation completed
```

#### `python manage.py export_data`
**Description**: Export system data for backup or analysis  
**Usage**: `python manage.py export_data [--format FORMAT] [--output PATH]`  
**Options**:
- `--format`: Export format (json, csv, xlsx)
- `--output`: Output file path
**Function**:
- Exports stock data and prices
- Exports news articles and sentiment data
- Exports user usage statistics
- Creates comprehensive data backups
**Output**: Export file location and statistics  
**Example**:
```bash
📤 Exporting system data...
📈 Exported 3,500 stocks
📰 Exported 1,250 news articles
👥 Exported user data
✅ Data exported to backup_20240115.json
```

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

### Development/Testing
```bash
# Create test environment
python manage.py create_test_users --count 10
python manage.py generate_test_data --stocks 500 --news 100

# Export data for analysis
python manage.py export_data --format json --output test_data.json
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

This comprehensive reference covers all available API endpoints and management commands in the Stock Scanner system, providing developers and administrators with the information needed to effectively use and maintain the platform.