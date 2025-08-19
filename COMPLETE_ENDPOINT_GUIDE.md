# Complete Endpoint Guide - Stock Scanner API

## 🎯 **All Working Endpoints**

### **Core Endpoints**
- `GET /` - Homepage with API overview (HTML/JSON)
- `GET /health/` - Health check endpoint
- `GET /api/health/` - WordPress-compatible health check
- `GET /docs/` - API documentation (HTML/JSON)
- `GET /endpoint-status/` - Real-time endpoint status monitoring
- `GET /admin/` - Django admin panel

### **Stock Data API**
- `GET /api/stocks/` - List all stocks with market data
- `GET /api/stock/{ticker}/` - Get specific stock details (e.g., `/api/stock/AAPL/`)
- `GET /api/search/?q={query}` - Search stocks by symbol/name
- `GET /api/trending/` - Get trending stocks
- `GET /api/realtime/{ticker}/` - Real-time stock data
- `GET /api/nasdaq/` - NASDAQ-specific stocks
- `GET /api/filter/` - Filter stocks with parameters
- `GET /api/market-stats/` - Market statistics
- `GET /api/statistics/` - Additional market statistics

### **Portfolio Management**
- `GET /api/portfolio/list/` - List user portfolios
- `POST /api/portfolio/create/` - Create new portfolio
- `POST /api/portfolio/add-holding/` - Add stock to portfolio
- `POST /api/portfolio/sell-holding/` - Sell portfolio holding
- `GET /api/portfolio/{id}/performance/` - Portfolio performance metrics
- `POST /api/portfolio/import-csv/` - Import portfolio from CSV
- `DELETE /api/portfolio/{id}/` - Delete portfolio
- `PUT /api/portfolio/{id}/update/` - Update portfolio
- `GET /api/portfolio/alert-roi/` - ROI alerts

### **Watchlist Management**
- `GET /api/watchlist/list/` - List user watchlists
- `POST /api/watchlist/create/` - Create new watchlist
- `POST /api/watchlist/add-stock/` - Add stock to watchlist
- `POST /api/watchlist/remove-stock/` - Remove stock from watchlist
- `GET /api/watchlist/{id}/performance/` - Watchlist performance
- `PUT /api/watchlist/{id}/` - Update watchlist
- `DELETE /api/watchlist/{id}/delete/` - Delete watchlist
- `GET /api/watchlist/{id}/export/csv/` - Export watchlist as CSV
- `GET /api/watchlist/{id}/export/json/` - Export watchlist as JSON
- `POST /api/watchlist/import/csv/` - Import watchlist from CSV
- `POST /api/watchlist/import/json/` - Import watchlist from JSON

### **News & Personalization**
- `GET /api/news/feed/` - Personalized news feed
- `POST /api/news/mark-read/` - Mark news article as read
- `POST /api/news/mark-clicked/` - Mark news article as clicked
- `POST /api/news/preferences/` - Update news preferences
- `POST /api/news/sync-portfolio/` - Sync portfolio stocks to news
- `GET /api/news/analytics/` - News consumption analytics

### **Alerts & Notifications**
- `POST /api/alerts/create/` - Create price alerts
- Additional alert endpoints available through the system

### **Revenue & Analytics**
- `GET /revenue/revenue-analytics/` - Revenue analytics dashboard (HTML/JSON)
- `GET /revenue/revenue-analytics/{month-year}/` - Monthly revenue analytics
- `POST /revenue/initialize-codes/` - Initialize discount codes
- `POST /revenue/validate-discount/` - Validate discount code
- `POST /revenue/apply-discount/` - Apply discount code
- `POST /revenue/record-payment/` - Record payment transaction
- `GET /revenue/monthly-summary/{month-year}/` - Monthly summary

### **WordPress Integration**
- `POST /api/subscription/` - WordPress subscription management
- All endpoints support WordPress API calls with proper CORS headers
- Automatic JSON responses for WordPress/AJAX requests

### **Authentication**
- `GET /accounts/login/` - Login page
- `POST /accounts/login/` - Login form submission
- `GET /accounts/logout/` - Logout
- All `/accounts/*` Django authentication URLs

## 🔧 **WordPress Integration Features**

### **Automatic Detection**
The system automatically detects WordPress/AJAX requests through:
- `X-Requested-With: XMLHttpRequest` header
- `Accept: application/json` header
- `?format=json` parameter
- API middleware detection

### **Expected WordPress Calls**
```php
// Health Check
wp_remote_get($backend_url . '/api/health/')

// Revenue Analytics
wp_remote_get($backend_url . '/revenue/revenue-analytics/' . $month_year . '/')

// Initialize Discount Codes
wp_remote_post($backend_url . '/revenue/initialize-codes/')
```

### **Response Format**
All API endpoints return standardized JSON:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-08-07T16:30:00Z",
  "endpoint": "/api/stocks/",
  "method": "GET"
}
```

## 🎨 **HTML Interface Features**

### **Dual Response System**
- Browser visits get full HTML pages with interactive elements
- API calls get JSON responses
- All major endpoints support both formats

### **Available HTML Pages**
- `/` - Homepage with feature showcase
- `/docs/` - Interactive API documentation
- `/revenue/revenue-analytics/` - Revenue dashboard with charts
- `/endpoint-status/` - Real-time endpoint monitoring
- `/health/` - System health check
- Custom 404/500 error pages

### **Navigation**
Every page includes consistent navigation:
- Home | API | Analytics | Health | Admin
- Footer links to documentation and status pages

## 🧪 **Testing Endpoints**

### **Manual Testing**
```bash
# Test basic endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/health/
curl http://localhost:8000/api/stocks/
curl http://localhost:8000/api/trending/

# Test with WordPress headers
curl -H "X-Requested-With: XMLHttpRequest" http://localhost:8000/revenue/revenue-analytics/

# Test specific stock
curl http://localhost:8000/api/stock/AAPL/

# Test search
curl "http://localhost:8000/api/search/?q=apple"
```

### **Automated Testing**
Visit `/endpoint-status/` for real-time endpoint monitoring with:
- Response time tracking
- Status code verification
- Error detection
- Success rate calculation

## 🚀 **Performance Features**

### **Optimizations**
- Middleware-based request detection
- Efficient CORS handling
- Database query optimization
- Proper error handling and logging
- Caching support for static content

### **Security**
- CSRF protection
- Secure headers
- Input validation
- Rate limiting ready
- SQL injection protection

## 📱 **Mobile & Responsive**

All HTML interfaces are fully responsive and work on:
- Desktop browsers
- Tablets
- Mobile devices
- API clients
- WordPress admin panels

## 🔗 **Integration Points**

### **WordPress Theme Integration**
- Compatible with existing WordPress theme
- Seamless API data integration
- PayPal payment processing
- User subscription management

### **External Services**
- Yahoo Finance integration
- Email notification system
- News aggregation
- Real-time market data

This system provides comprehensive stock market data API with professional HTML interfaces and seamless WordPress integration.