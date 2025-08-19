# Comprehensive Stock Scanner API Documentation

## Overview

This API provides a complete stock portfolio and watchlist management system with intelligent news personalization, performance analytics, and alert-based trading ROI tracking. All endpoints use enterprise-grade security with comprehensive input validation and audit logging.

## Base URL

All API endpoints are prefixed with `/api/` (adjustable in your deployment configuration).

## Authentication

All endpoints require user authentication. Include the authentication token in your requests:

```
Authorization: Bearer <your-token>
```

## Response Format

All API responses follow a consistent format:

```json
{
    "success": true|false,
    "data": { ... },
    "message": "Human readable message",
    "error": "Error description (if success is false)",
    "error_code": "SPECIFIC_ERROR_CODE"
}
```

---

# Portfolio Management API

## 1. Create Portfolio

**POST** `/api/portfolio/create/`

Create a new portfolio for the authenticated user.

### Request Body
```json
{
    "name": "My Portfolio",
    "description": "Portfolio description",
    "is_public": false
}
```

### Response
```json
{
    "success": true,
    "data": {
        "portfolio_id": 1,
        "name": "My Portfolio",
        "description": "Portfolio description",
        "is_public": false,
        "created_at": "2025-01-15T10:30:00Z"
    },
    "message": "Portfolio created successfully"
}
```

---

## 2. Add Holding to Portfolio

**POST** `/api/portfolio/add-holding/`

Add a stock holding to an existing portfolio.

### Request Body
```json
{
    "portfolio_id": 1,
    "stock_ticker": "AAPL",
    "shares": 100.0,
    "average_cost": 150.00,
    "current_price": 165.00,
    "alert_id": 123
}
```

### Response
```json
{
    "success": true,
    "data": {
        "holding_id": 456,
        "portfolio_id": 1,
        "stock_ticker": "AAPL",
        "shares": 100.0,
        "average_cost": 150.00,
        "current_price": 165.00,
        "market_value": 16500.00,
        "unrealized_gain_loss": 1500.00,
        "unrealized_gain_loss_percent": 10.00,
        "date_added": "2025-01-15T10:30:00Z"
    },
    "message": "Holding added successfully"
}
```

---

## 3. Sell Holding

**POST** `/api/portfolio/sell-holding/`

Sell shares from a portfolio holding.

### Request Body
```json
{
    "portfolio_id": 1,
    "stock_ticker": "AAPL",
    "shares": 50.0,
    "sale_price": 170.00,
    "fees": 5.00
}
```

### Response
```json
{
    "success": true,
    "data": {
        "transaction_id": 789,
        "portfolio_id": 1,
        "stock_ticker": "AAPL",
        "shares_sold": 50.0,
        "sale_price": 170.00,
        "total_proceeds": 8495.00,
        "cost_basis": 7500.00,
        "realized_gain_loss": 995.00,
        "realized_gain_loss_percent": 13.27,
        "holding_period_days": 45,
        "fees": 5.00
    },
    "message": "Shares sold successfully"
}
```

---

## 4. List User Portfolios

**GET** `/api/portfolio/list/`

Get all portfolios for the authenticated user.

### Response
```json
{
    "success": true,
    "data": {
        "portfolios": [
            {
                "id": 1,
                "name": "Tech Stocks",
                "description": "Technology sector portfolio",
                "is_public": false,
                "total_value": 45000.00,
                "total_cost": 40000.00,
                "total_return": 5000.00,
                "total_return_percent": 12.50,
                "holdings_count": 8,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        ],
        "count": 1
    },
    "message": "Portfolios retrieved successfully"
}
```

---

## 5. Portfolio Performance

**GET** `/api/portfolio/{portfolio_id}/performance/`

Get comprehensive performance metrics for a specific portfolio.

### Response
```json
{
    "success": true,
    "data": {
        "portfolio_id": 1,
        "portfolio_name": "Tech Stocks",
        "total_value": 45000.00,
        "total_cost": 40000.00,
        "total_return": 5000.00,
        "total_return_percent": 12.50,
        "total_holdings": 8,
        "total_transactions": 15,
        "best_performer": {
            "ticker": "NVDA",
            "return_percent": 25.30
        },
        "worst_performer": {
            "ticker": "INTC",
            "return_percent": -8.20
        },
        "sector_breakdown": {
            "Technology": {
                "value": 35000.00,
                "count": 6,
                "percentage": 77.78
            },
            "Healthcare": {
                "value": 10000.00,
                "count": 2,
                "percentage": 22.22
            }
        },
        "alert_performance": {
            "total_alert_transactions": 8,
            "total_manual_transactions": 7,
            "alert_success_rate": 75.00,
            "manual_success_rate": 57.14,
            "categories": {
                "earnings": {
                    "total_transactions": 3,
                    "profitable_trades": 2,
                    "success_rate": 66.67,
                    "average_roi": 850.33
                }
            }
        },
        "last_updated": "2025-01-15T10:30:00Z"
    },
    "message": "Portfolio performance retrieved successfully"
}
```

---

## 6. Import Portfolio from CSV

**POST** `/api/portfolio/import-csv/`

Import portfolio holdings from CSV format.

### Request Body
```json
{
    "portfolio_name": "Imported Portfolio",
    "csv_content": "ticker,shares,average_cost,current_price\nAAPL,100,150.00,165.00\nMSFT,50,200.00,210.00"
}
```

### Response
```json
{
    "success": true,
    "data": {
        "portfolio_id": 2,
        "portfolio_name": "Imported Portfolio",
        "imported_count": 2,
        "error_count": 0,
        "errors": []
    },
    "message": "Portfolio imported successfully"
}
```

---

## 7. Alert ROI Analysis

**GET** `/api/portfolio/alert-roi/`

Get ROI and performance metrics for alert-based trades across all portfolios.

### Response
```json
{
    "success": true,
    "data": {
        "total_alert_transactions": 25,
        "total_manual_transactions": 18,
        "alert_success_rate": 72.00,
        "manual_success_rate": 61.11,
        "categories": {
            "earnings": {
                "total_transactions": 8,
                "profitable_trades": 6,
                "success_rate": 75.00,
                "average_roi": 1245.50
            },
            "analyst": {
                "total_transactions": 5,
                "profitable_trades": 3,
                "success_rate": 60.00,
                "average_roi": 890.25
            }
        },
        "portfolios": [
            {
                "portfolio_id": 1,
                "portfolio_name": "Tech Stocks",
                "performance": { ... }
            }
        ]
    },
    "message": "Alert ROI data retrieved successfully"
}
```

---

## 8. Update Portfolio

**PUT** `/api/portfolio/{portfolio_id}/update/`

Update portfolio information.

### Request Body
```json
{
    "name": "Updated Portfolio Name",
    "description": "Updated description",
    "is_public": true
}
```

---

## 9. Delete Portfolio

**DELETE** `/api/portfolio/{portfolio_id}/`

Delete a portfolio and all its holdings/transactions.

---

# Watchlist Management API

## 1. Create Watchlist

**POST** `/api/watchlist/create/`

Create a new watchlist for the authenticated user.

### Request Body
```json
{
    "name": "Tech Stocks",
    "description": "Technology sector watchlist"
}
```

### Response
```json
{
    "success": true,
    "data": {
        "watchlist_id": 1,
        "name": "Tech Stocks",
        "description": "Technology sector watchlist",
        "created_at": "2025-01-15T10:30:00Z"
    },
    "message": "Watchlist created successfully"
}
```

---

## 2. Add Stock to Watchlist

**POST** `/api/watchlist/add-stock/`

Add a stock to an existing watchlist.

### Request Body
```json
{
    "watchlist_id": 1,
    "stock_ticker": "AAPL",
    "added_price": 150.00,
    "notes": "Good growth potential",
    "target_price": 180.00,
    "stop_loss": 140.00,
    "price_alert_enabled": true,
    "news_alert_enabled": false
}
```

### Response
```json
{
    "success": true,
    "data": {
        "item_id": 123,
        "watchlist_id": 1,
        "stock_ticker": "AAPL",
        "added_price": 150.00,
        "current_price": 165.00,
        "price_change": 15.00,
        "price_change_percent": 10.00,
        "notes": "Good growth potential",
        "target_price": 180.00,
        "stop_loss": 140.00,
        "price_alert_enabled": true,
        "news_alert_enabled": false,
        "added_at": "2025-01-15T10:30:00Z"
    },
    "message": "Stock added to watchlist successfully"
}
```

---

## 3. Remove Stock from Watchlist

**DELETE** `/api/watchlist/remove-stock/`

Remove a stock from a watchlist.

### Request Body
```json
{
    "watchlist_id": 1,
    "stock_ticker": "AAPL"
}
```

---

## 4. List User Watchlists

**GET** `/api/watchlist/list/`

Get all watchlists for the authenticated user.

### Response
```json
{
    "success": true,
    "data": {
        "watchlists": [
            {
                "id": 1,
                "name": "Tech Stocks",
                "description": "Technology sector watchlist",
                "total_return_percent": 8.45,
                "best_performer": "NVDA",
                "worst_performer": "INTC",
                "items_count": 12,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        ],
        "count": 1
    },
    "message": "Watchlists retrieved successfully"
}
```

---

## 5. Watchlist Performance

**GET** `/api/watchlist/{watchlist_id}/performance/`

Get comprehensive performance metrics for a specific watchlist.

### Response
```json
{
    "success": true,
    "data": {
        "watchlist_id": 1,
        "watchlist_name": "Tech Stocks",
        "total_items": 12,
        "total_return_percent": 8.45,
        "gains": 8,
        "losses": 4,
        "win_rate": 66.67,
        "best_performer": {
            "ticker": "NVDA",
            "return_percent": 25.30
        },
        "worst_performer": {
            "ticker": "INTC",
            "return_percent": -8.20
        },
        "top_performers": [
            {
                "ticker": "NVDA",
                "return_percent": 25.30,
                "current_price": 875.50,
                "added_price": 700.00
            }
        ],
        "bottom_performers": [
            {
                "ticker": "INTC",
                "return_percent": -8.20,
                "current_price": 27.30,
                "added_price": 29.75
            }
        ],
        "alerts": {
            "items_with_targets": 8,
            "items_with_stop_loss": 6,
            "price_alerts_enabled": 10,
            "news_alerts_enabled": 5,
            "targets_hit": 2,
            "stop_losses_hit": 1
        },
        "last_updated": "2025-01-15T10:30:00Z"
    },
    "message": "Watchlist performance retrieved successfully"
}
```

---

## 6. Export Watchlist to CSV

**GET** `/api/watchlist/{watchlist_id}/export/csv/`

Export watchlist data to CSV format (returns file download).

### Response
Returns a CSV file with headers:
- ticker, company_name, added_at, added_price, current_price, price_change, price_change_percent, notes, target_price, stop_loss, price_alert_enabled, news_alert_enabled

---

## 7. Export Watchlist to JSON

**GET** `/api/watchlist/{watchlist_id}/export/json/`

Export watchlist data to JSON format (returns file download).

---

## 8. Import Watchlist from CSV

**POST** `/api/watchlist/import/csv/`

Import watchlist from CSV format.

### Request Body
```json
{
    "watchlist_name": "Imported Watchlist",
    "csv_content": "ticker,added_price,notes,target_price,stop_loss,price_alert_enabled,news_alert_enabled\nAAPL,150.00,Good stock,180.00,140.00,true,false"
}
```

### Response
```json
{
    "success": true,
    "data": {
        "watchlist_id": 2,
        "watchlist_name": "Imported Watchlist",
        "imported_count": 1,
        "error_count": 0,
        "errors": []
    },
    "message": "Watchlist imported successfully"
}
```

---

## 9. Import Watchlist from JSON

**POST** `/api/watchlist/import/json/`

Import watchlist from JSON format.

### Request Body
```json
{
    "json_content": "{\"watchlist_info\": {\"name\": \"My Watchlist\", \"description\": \"...\"},\"items\": [...]}"
}
```

---

## 10. Update Watchlist

**PUT** `/api/watchlist/{watchlist_id}/`

Update watchlist information.

### Request Body
```json
{
    "name": "Updated Watchlist Name",
    "description": "Updated description"
}
```

---

## 11. Update Watchlist Item

**PUT** `/api/watchlist/item/{item_id}/`

Update a specific watchlist item.

### Request Body
```json
{
    "notes": "Updated notes",
    "target_price": 200.00,
    "stop_loss": 150.00,
    "price_alert_enabled": true,
    "news_alert_enabled": true
}
```

---

## 12. Delete Watchlist

**DELETE** `/api/watchlist/{watchlist_id}/delete/`

Delete a watchlist and all its items.

---

# Data Models

## Stock Model
```json
{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "current_price": 165.50,
    "change_percent": 2.35,
    "volume": 45678000,
    "market_cap": 2650000000000,
    "pe_ratio": 28.45
}
```

## Portfolio Model
```json
{
    "id": 1,
    "name": "My Portfolio",
    "description": "Investment portfolio",
    "is_public": false,
    "total_value": 45000.00,
    "total_cost": 40000.00,
    "total_return": 5000.00,
    "total_return_percent": 12.50,
    "followers_count": 0,
    "likes_count": 0
}
```

## Watchlist Model
```json
{
    "id": 1,
    "name": "Tech Stocks",
    "description": "Technology watchlist",
    "total_return_percent": 8.45,
    "best_performer": "NVDA",
    "worst_performer": "INTC"
}
```

---

# Error Codes

| Code | Description |
|------|-------------|
| `AUTH_REQUIRED` | Authentication required |
| `VALIDATION_ERROR` | Input validation failed |
| `PORTFOLIO_NOT_FOUND` | Portfolio not found |
| `WATCHLIST_NOT_FOUND` | Watchlist not found |
| `STOCK_NOT_FOUND` | Stock not found |
| `INSUFFICIENT_SHARES` | Not enough shares to sell |
| `IMPORT_ERROR` | CSV/JSON import failed |
| `EXPORT_ERROR` | Export operation failed |
| `INTERNAL_ERROR` | Internal server error |

---

# Rate Limiting

API endpoints are rate-limited based on user tier:
- Free: 100 requests/hour
- Basic: 500 requests/hour  
- Pro: 2000 requests/hour
- Enterprise: Unlimited

---

# Security Features

1. **Authentication**: All endpoints require valid user authentication
2. **Input Validation**: Comprehensive validation with sanitization
3. **SQL Injection Protection**: Parameterized queries and ORM usage
4. **XSS Protection**: Input sanitization removes dangerous content
5. **Rate Limiting**: Prevents abuse and ensures fair usage
6. **Audit Logging**: All API calls are logged for compliance
7. **CSRF Protection**: Cross-site request forgery protection enabled

---

# Usage Examples

## Python Example
```python
import requests

headers = {
    'Authorization': 'Bearer your-token',
    'Content-Type': 'application/json'
}

# Create portfolio
response = requests.post(
    'https://yourapi.com/api/portfolio/create/',
    headers=headers,
    json={
        'name': 'My Tech Portfolio',
        'description': 'Technology stocks',
        'is_public': False
    }
)

portfolio_data = response.json()
portfolio_id = portfolio_data['data']['portfolio_id']

# Add holding
requests.post(
    'https://yourapi.com/api/portfolio/add-holding/',
    headers=headers,
    json={
        'portfolio_id': portfolio_id,
        'stock_ticker': 'AAPL',
        'shares': 100,
        'average_cost': 150.00
    }
)
```

## JavaScript Example
```javascript
const API_BASE = 'https://yourapi.com/api/';
const headers = {
    'Authorization': 'Bearer your-token',
    'Content-Type': 'application/json'
};

// Create watchlist
const response = await fetch(`${API_BASE}watchlist/create/`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        name: 'Growth Stocks',
        description: 'High growth potential stocks'
    })
});

const watchlistData = await response.json();

// Add stock to watchlist
await fetch(`${API_BASE}watchlist/add-stock/`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        watchlist_id: watchlistData.data.watchlist_id,
        stock_ticker: 'TSLA',
        target_price: 300.00,
        price_alert_enabled: true
    })
});
```

---

# Database Schema

The system includes the following database tables:

1. **stocks_userprofile** - Extended user profiles
2. **stocks_userportfolio** - User portfolios
3. **stocks_portfolioholding** - Portfolio holdings
4. **stocks_tradetransaction** - Trade transactions
5. **stocks_userwatchlist** - User watchlists
6. **stocks_watchlistitem** - Watchlist items
7. **stocks_userinterests** - News personalization preferences
8. **stocks_personalizednews** - Personalized news articles
9. **stocks_portfoliofollowing** - Social following relationships

All tables include appropriate indexes for optimal query performance and foreign key constraints for data integrity.

---

This comprehensive API provides enterprise-grade portfolio and watchlist management with advanced features like alert-based ROI tracking, intelligent news personalization, and seamless import/export capabilities.