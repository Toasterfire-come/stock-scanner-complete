# 🚀 Stock Scanner Backend - Complete Frontend Integration Guide

## 📋 Table of Contents
1. [Base Configuration](#base-configuration)
2. [Authentication System](#authentication-system)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Data Models & Response Formats](#data-models--response-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting & Usage Tracking](#rate-limiting--usage-tracking)
7. [Code Examples](#code-examples)
8. [Best Practices](#best-practices)

---

## 🔧 Base Configuration

### Backend URL
```javascript
const BASE_URL = "http://localhost:8001"; // Development
// const BASE_URL = "https://api.retailtradescanner.com"; // Production
```

### CORS Settings
The backend is configured to accept requests from:
- `http://localhost:3000` (React dev server)
- `http://127.0.0.1:3000`
- `http://localhost:8000`
- `http://127.0.0.1:8000`

### Required Headers
```javascript
const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};
```

---

## 🔐 Authentication System

### Token-Based Authentication
The backend uses **API tokens** for authentication, not cookies or sessions.

#### 1. User Registration
```javascript
// Register new user
const registerUser = async (userData) => {
    const response = await fetch(`${BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: defaultHeaders,
        body: JSON.stringify({
            username: userData.username,
            email: userData.email,
            password: userData.password,
            first_name: userData.firstName,
            last_name: userData.lastName
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Store token in localStorage
        localStorage.setItem('rts_token', data.data.api_token);
        localStorage.setItem('user_data', JSON.stringify(data.data));
        return data.data;
    }
    
    throw new Error(data.error);
};
```

#### 2. User Login
```javascript
// Login existing user
const loginUser = async (credentials) => {
    const response = await fetch(`${BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: defaultHeaders,
        body: JSON.stringify({
            username: credentials.username,
            password: credentials.password
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        localStorage.setItem('rts_token', data.data.api_token);
        localStorage.setItem('user_data', JSON.stringify(data.data));
        return data.data;
    }
    
    throw new Error(data.error);
};
```

#### 3. Authenticated Requests
```javascript
// Get stored token
const getAuthToken = () => localStorage.getItem('rts_token');

// Authenticated request headers
const getAuthHeaders = () => ({
    ...defaultHeaders,
    'Authorization': `Bearer ${getAuthToken()}`
});

// Example authenticated request
const getUserProfile = async () => {
    const response = await fetch(`${BASE_URL}/api/user/profile/`, {
        method: 'GET',
        headers: getAuthHeaders()
    });
    
    return await response.json();
};
```

#### 4. Authentication State Management
```javascript
// Check if user is authenticated
const isAuthenticated = () => {
    const token = getAuthToken();
    const userData = localStorage.getItem('user_data');
    return token && userData;
};

// Logout user
const logout = () => {
    localStorage.removeItem('rts_token');
    localStorage.removeItem('user_data');
    // Redirect to login page
};

// Get current user data
const getCurrentUser = () => {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
};
```

---

## 📡 API Endpoints Reference

### 🏠 **Public Endpoints (No Authentication Required)**

#### 1. Homepage & Health
```javascript
// Homepage
GET ${BASE_URL}/
// Response: HTML page

// Health check
GET ${BASE_URL}/health/
// Response: {"status": "healthy"}

// API index
GET ${BASE_URL}/api/
// Response: API information
```

#### 2. Platform Statistics
```javascript
// Get platform statistics
const getPlatformStats = async () => {
    const response = await fetch(`${BASE_URL}/api/platform-stats/`);
    return await response.json();
};

// Response format:
{
    "success": true,
    "nyse_stocks": 0,
    "nasdaq_stocks": 5,
    "total_stocks": 5,
    "total_indicators": 14,
    "scanner_combinations": 70,
    "platform_stats": {
        "total_users": 3,
        "premium_users": 0,
        "recent_stock_updates": 5,
        "api_calls_today": 0
    },
    "market_stats": {
        "exchanges_supported": ["NYSE", "NASDAQ"],
        "data_sources": ["yfinance", "real-time feeds"],
        "update_frequency": "Real-time"
    },
    "timestamp": "2025-09-05T21:53:27.506986+00:00"
}
```

#### 3. Usage Statistics (Public)
```javascript
// Get general usage stats
const getUsageStats = async () => {
    const response = await fetch(`${BASE_URL}/api/usage/`);
    return await response.json();
};

// Response format:
{
    "success": true,
    "usage": {
        "plan": "free",
        "monthly_used": 0,
        "monthly_limit": 15,
        "daily_used": 0,
        "daily_limit": 15
    },
    "rate_limits": {
        "requests_this_minute": 0,
        "requests_this_hour": 0,
        "requests_this_day": 0,
        "rate_limited": false
    }
}
```

### 📈 **Stock Data Endpoints (Public)**

#### 1. Stock List with Filtering
```javascript
// Get stocks with filters
const getStocks = async (filters = {}) => {
    const params = new URLSearchParams();
    
    // Add filters
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category); // gainers, losers, high_volume, large_cap, small_cap
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.min_volume) params.append('min_volume', filters.min_volume);
    if (filters.exchange) params.append('exchange', filters.exchange); // NASDAQ, NYSE
    if (filters.sort_by) params.append('sort_by', filters.sort_by); // price, volume, market_cap, change_percent
    if (filters.sort_order) params.append('sort_order', filters.sort_order); // asc, desc
    
    const response = await fetch(`${BASE_URL}/api/stocks/?${params}`);
    return await response.json();
};

// Example usage:
const topGainers = await getStocks({
    category: 'gainers',
    limit: 10,
    sort_by: 'change_percent',
    sort_order: 'desc'
});
```

#### 2. Individual Stock Details
```javascript
// Get detailed stock information
const getStockDetails = async (ticker) => {
    const response = await fetch(`${BASE_URL}/api/stocks/${ticker.toUpperCase()}/`);
    return await response.json();
};

// Example:
const appleStock = await getStockDetails('AAPL');
```

#### 3. Stock Quotes
```javascript
// Get real-time stock quote
const getStockQuote = async (symbol) => {
    const response = await fetch(`${BASE_URL}/api/stocks/${symbol.toUpperCase()}/quote/`);
    return await response.json();
};

// Response format:
{
    "success": true,
    "symbol": "AAPL",
    "price": 239.67,
    "change": 0.27,
    "change_percent": 0.11,
    "volume": 931731,
    "timestamp": "2025-09-05T21:47:24.449322+00:00",
    "rate_limit_warning": false,
    "source": "yfinance",
    "market_data": {
        "open": 239.40,
        "high": 239.71,
        "low": 239.32,
        "previous_close": 239.78,
        "market_cap": 3557095374848,
        "pe_ratio": 36.37
    },
    "cached": true
}
```

#### 4. Real-time Data
```javascript
// Get comprehensive real-time data
const getRealTimeData = async (ticker) => {
    const response = await fetch(`${BASE_URL}/api/realtime/${ticker.toUpperCase()}/`);
    return await response.json();
};

// Response includes: current_price, volume, market_cap, pe_ratio, dividend_yield, etc.
```

#### 5. Stock Search
```javascript
// Search stocks by ticker or company name
const searchStocks = async (query) => {
    const response = await fetch(`${BASE_URL}/api/stocks/search/?q=${encodeURIComponent(query)}`);
    return await response.json();
};

// Example:
const searchResults = await searchStocks('Apple');
```

#### 6. NASDAQ Stocks
```javascript
// Get NASDAQ-listed stocks
const getNasdaqStocks = async (limit = 500) => {
    const response = await fetch(`${BASE_URL}/api/stocks/nasdaq/?limit=${limit}`);
    return await response.json();
};
```

#### 7. Market Statistics
```javascript
// Get market overview statistics
const getMarketStats = async () => {
    const response = await fetch(`${BASE_URL}/api/market/stats/`);
    return await response.json();
};
```

#### 8. Trending Stocks
```javascript
// Get trending stocks
const getTrendingStocks = async () => {
    const response = await fetch(`${BASE_URL}/api/trending/`);
    return await response.json();
};

// Response includes: high_volume, top_gainers, most_active arrays
```

#### 9. Filter Stocks
```javascript
// Filter stocks with advanced criteria
const filterStocks = async (filters) => {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${BASE_URL}/api/market/filter/?${params}`);
    return await response.json();
};

// Example:
const filteredStocks = await filterStocks({
    min_price: 100,
    max_price: 500,
    min_volume: 1000000,
    exchange: 'NASDAQ'
});
```

### 🔐 **Authenticated Endpoints (Require Token)**

#### 1. User Profile Management
```javascript
// Get user profile
const getUserProfile = async () => {
    const response = await fetch(`${BASE_URL}/api/user/profile/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};

// Update user profile
const updateUserProfile = async (profileData) => {
    const response = await fetch(`${BASE_URL}/api/user/profile/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(profileData)
    });
    return await response.json();
};

// Change password
const changePassword = async (passwordData) => {
    const response = await fetch(`${BASE_URL}/api/user/change-password/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            current_password: passwordData.currentPassword,
            new_password: passwordData.newPassword
        })
    });
    return await response.json();
};
```

#### 2. Billing & Subscription Management
```javascript
// Get current plan
const getCurrentPlan = async () => {
    const response = await fetch(`${BASE_URL}/api/billing/current-plan/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};

// Create PayPal order (Note: Currently has CSRF issues)
const createPayPalOrder = async (planData) => {
    const response = await fetch(`${BASE_URL}/api/billing/create-paypal-order/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            plan_type: planData.planType, // bronze, silver, gold
            billing_cycle: planData.billingCycle, // monthly, annual
            discount_code: planData.discountCode || null
        })
    });
    return await response.json();
};

// Get billing history
const getBillingHistory = async () => {
    const response = await fetch(`${BASE_URL}/api/billing/history/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};

// Get billing statistics
const getBillingStats = async () => {
    const response = await fetch(`${BASE_URL}/api/billing/stats/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};
```

#### 3. Usage Tracking
```javascript
// Track API usage
const trackUsage = async (endpointInfo) => {
    const response = await fetch(`${BASE_URL}/api/usage/track/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            endpoint: endpointInfo.endpoint,
            // Additional tracking data
        })
    });
    return await response.json();
};

// Get usage history
const getUsageHistory = async () => {
    const response = await fetch(`${BASE_URL}/api/usage/history/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};
```

#### 4. Portfolio & Watchlist
```javascript
// Get portfolio
const getPortfolio = async () => {
    const response = await fetch(`${BASE_URL}/api/portfolio/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};

// Add to portfolio
const addToPortfolio = async (symbol) => {
    const response = await fetch(`${BASE_URL}/api/portfolio/add/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ symbol })
    });
    return await response.json();
};

// Get watchlist
const getWatchlist = async () => {
    const response = await fetch(`${BASE_URL}/api/watchlist/`, {
        headers: getAuthHeaders()
    });
    return await response.json();
};

// Add to watchlist
const addToWatchlist = async (symbol) => {
    const response = await fetch(`${BASE_URL}/api/watchlist/add/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ symbol })
    });
    return await response.json();
};
```

#### 5. Alerts Management
```javascript
// Create stock alert
const createAlert = async (alertData) => {
    const response = await fetch(`${BASE_URL}/api/alerts/create/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            symbol: alertData.symbol,
            condition: alertData.condition, // price_above, price_below
            value: alertData.value,
            email: alertData.email
        })
    });
    return await response.json();
};
```

### 🔌 **WordPress Integration Endpoints (Public)**

```javascript
// WordPress stock data
const getWordPressStocks = async () => {
    const response = await fetch(`${BASE_URL}/api/wordpress/`);
    return await response.json();
};

// WordPress news
const getWordPressNews = async () => {
    const response = await fetch(`${BASE_URL}/api/wordpress/news/`);
    return await response.json();
};

// Simple APIs (no database required)
const getSimpleStocks = async () => {
    const response = await fetch(`${BASE_URL}/api/simple/stocks/`);
    return await response.json();
};
```

---

## 📋 Data Models & Response Formats

### User Data Model
```javascript
{
    "user_id": 3,
    "username": "testuser456",
    "email": "test456@example.com",
    "first_name": "Test",
    "last_name": "User",
    "plan": "free", // free, bronze, silver, gold
    "api_token": "51db5598-8e5c-45ee-a370-5039649c4a52",
    "is_premium": false,
    "limits": {
        "monthly": 15,
        "daily": 15
    },
    "usage": {
        "monthly_calls": 2,
        "daily_calls": 2,
        "last_call": "2025-09-05T21:51:03.847934+00:00"
    },
    "subscription": {
        "active": false,
        "end_date": null,
        "trial_used": false
    }
}
```

### Stock Data Model
```javascript
{
    "ticker": "AAPL",
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "name": "Apple Inc.",
    "exchange": "NASDAQ",
    
    // Price data
    "current_price": 239.67,
    "price_change_today": 0.27,
    "price_change_week": -2.15,
    "price_change_month": 5.32,
    "price_change_year": 45.67,
    "change_percent": 0.11,
    
    // Bid/Ask and Range
    "bid_price": 239.65,
    "ask_price": 239.70,
    "bid_ask_spread": 0.05,
    "days_range": "239.32 - 239.71",
    "days_low": 239.32,
    "days_high": 239.71,
    
    // Volume data
    "volume": 931731,
    "volume_today": 931731,
    "avg_volume_3mon": 54449941,
    "dvav": 0.017,
    "shares_available": 15334100992,
    
    // Market data
    "market_cap": 3557095374848,
    "market_cap_change_3mon": 125000000000,
    "formatted_market_cap": "$3.56T",
    
    // Financial ratios
    "pe_ratio": 36.37,
    "pe_change_3mon": 2.5,
    "dividend_yield": 0.43,
    "earnings_per_share": 6.59,
    "book_value": 4.431,
    "price_to_book": 54.09,
    
    // 52-week range
    "week_52_low": 169.21,
    "week_52_high": 260.10,
    
    // Additional metrics
    "one_year_target": 250.00,
    "formatted_price": "$239.67",
    "formatted_change": "+$0.27 (0.11%)",
    "formatted_volume": "931.7K",
    
    // Timestamps
    "last_updated": "2025-09-05T21:47:24.449322+00:00",
    "created_at": "2025-09-05T20:30:15.123456+00:00",
    
    // Calculated fields
    "is_gaining": true,
    "is_losing": false,
    "volume_ratio": 0.017,
    "price_near_52_week_high": false,
    "price_near_52_week_low": false,
    "price_position_52_week": 75.5
}
```

### Standard Response Format
```javascript
// Success Response
{
    "success": true,
    "data": { /* actual data */ },
    "message": "Operation successful", // optional
    "timestamp": "2025-09-05T21:47:24.449322+00:00"
}

// Error Response
{
    "success": false,
    "error": "Error message",
    "details": { /* optional error details */ }
}
```

---

## ⚠️ Error Handling

### Error Types & Status Codes

```javascript
// Error handling utility
const handleApiError = (response, data) => {
    switch (response.status) {
        case 400:
            throw new Error(data.error || 'Bad Request - Check your parameters');
        case 401:
            // Authentication required - redirect to login
            logout();
            throw new Error('Authentication required');
        case 403:
            throw new Error('Access forbidden - Check your permissions');
        case 404:
            throw new Error(data.error || 'Resource not found');
        case 429:
            throw new Error('Rate limit exceeded - Try again later');
        case 500:
            throw new Error('Server error - Please try again later');
        default:
            throw new Error(data.error || 'An unexpected error occurred');
    }
};

// Enhanced API call with error handling
const apiCall = async (url, options = {}) => {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        
        if (!response.ok) {
            handleApiError(response, data);
        }
        
        if (data.success === false) {
            throw new Error(data.error);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
```

### Common Error Scenarios

```javascript
// Rate limiting handling
const handleRateLimitError = (error) => {
    if (error.message.includes('rate limit') || error.message.includes('usage limit')) {
        // Show upgrade prompt or retry timer
        return {
            type: 'RATE_LIMIT',
            message: 'You have reached your API limit. Upgrade your plan for more requests.',
            action: 'UPGRADE_PLAN'
        };
    }
    return null;
};

// Authentication error handling
const handleAuthError = (error) => {
    if (error.message.includes('Authentication required')) {
        logout();
        // Redirect to login page
        window.location.href = '/login';
        return true;
    }
    return false;
};
```

---

## 🚦 Rate Limiting & Usage Tracking

### Plan Limits
```javascript
const PLAN_LIMITS = {
    free: {
        daily: 15,
        monthly: 15,
        features: ['basic_quotes', 'search']
    },
    bronze: {
        daily: 100,
        monthly: 2000,
        features: ['basic_quotes', 'search', 'alerts', 'portfolio']
    },
    silver: {
        daily: 500,
        monthly: 10000,
        features: ['all', 'real_time_data', 'advanced_filters']
    },
    gold: {
        daily: 2000,
        monthly: 50000,
        features: ['all', 'priority_support', 'custom_alerts']
    }
};
```

### Usage Monitoring
```javascript
// Check usage before API calls
const checkUsageBeforeCall = async () => {
    const usage = await getUsageStats();
    
    if (usage.rate_limits.rate_limited) {
        throw new Error('Rate limit exceeded');
    }
    
    if (usage.usage.daily_used >= usage.usage.daily_limit) {
        throw new Error('Daily limit reached');
    }
    
    return usage;
};

// Usage-aware API wrapper
const rateLimitedApiCall = async (url, options = {}) => {
    await checkUsageBeforeCall();
    return await apiCall(url, options);
};
```

---

## 💻 Code Examples

### Complete React Hook Example
```javascript
// useStockData.js - Custom React Hook
import { useState, useEffect, useCallback } from 'react';

const BASE_URL = "http://localhost:8001";

export const useStockData = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const getAuthHeaders = () => ({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('rts_token')}`
    });
    
    const fetchStocks = useCallback(async (filters = {}) => {
        setLoading(true);
        setError(null);
        
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${BASE_URL}/api/stocks/?${params}`);
            const data = await response.json();
            
            if (data.success) {
                setStocks(data.data);
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);
    
    const getStockQuote = useCallback(async (symbol) => {
        try {
            const response = await fetch(`${BASE_URL}/api/stocks/${symbol}/quote/`);
            const data = await response.json();
            
            if (data.success) {
                return data;
            } else {
                throw new Error(data.error);
            }
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, []);
    
    return {
        stocks,
        loading,
        error,
        fetchStocks,
        getStockQuote
    };
};

// Usage in React Component
const StockDashboard = () => {
    const { stocks, loading, error, fetchStocks, getStockQuote } = useStockData();
    
    useEffect(() => {
        fetchStocks({ limit: 50, category: 'gainers' });
    }, [fetchStocks]);
    
    const handleStockClick = async (symbol) => {
        try {
            const quote = await getStockQuote(symbol);
            console.log('Quote:', quote);
        } catch (err) {
            console.error('Failed to get quote:', err);
        }
    };
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            {stocks.map(stock => (
                <div key={stock.ticker} onClick={() => handleStockClick(stock.ticker)}>
                    {stock.ticker} - ${stock.current_price}
                </div>
            ))}
        </div>
    );
};
```

### Authentication Context Example
```javascript
// AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();
const BASE_URL = "http://localhost:8001";

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const token = localStorage.getItem('rts_token');
        const userData = localStorage.getItem('user_data');
        
        if (token && userData) {
            setUser(JSON.parse(userData));
        }
        setLoading(false);
    }, []);
    
    const login = async (credentials) => {
        const response = await fetch(`${BASE_URL}/api/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('rts_token', data.data.api_token);
            localStorage.setItem('user_data', JSON.stringify(data.data));
            setUser(data.data);
            return data.data;
        }
        
        throw new Error(data.error);
    };
    
    const register = async (userData) => {
        const response = await fetch(`${BASE_URL}/api/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('rts_token', data.data.api_token);
            localStorage.setItem('user_data', JSON.stringify(data.data));
            setUser(data.data);
            return data.data;
        }
        
        throw new Error(data.error);
    };
    
    const logout = () => {
        localStorage.removeItem('rts_token');
        localStorage.removeItem('user_data');
        setUser(null);
    };
    
    const value = {
        user,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        loading
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
```

### API Service Class Example
```javascript
// apiService.js - Centralized API service
class StockScannerAPI {
    constructor() {
        this.baseURL = "http://localhost:8001";
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }
    
    getAuthHeaders() {
        const token = localStorage.getItem('rts_token');
        return {
            ...this.defaultHeaders,
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getAuthHeaders(),
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }
    
    // Authentication methods
    async register(userData) {
        return this.request('/api/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
    
    async login(credentials) {
        return this.request('/api/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }
    
    // Stock data methods
    async getStocks(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/api/stocks/?${params}`);
    }
    
    async getStockQuote(symbol) {
        return this.request(`/api/stocks/${symbol}/quote/`);
    }
    
    async getRealTimeData(ticker) {
        return this.request(`/api/realtime/${ticker}/`);
    }
    
    async searchStocks(query) {
        return this.request(`/api/stocks/search/?q=${encodeURIComponent(query)}`);
    }
    
    // Platform methods
    async getPlatformStats() {
        return this.request('/api/platform-stats/');
    }
    
    async getUsageStats() {
        return this.request('/api/usage/');
    }
    
    // User methods (authenticated)
    async getUserProfile() {
        return this.request('/api/user/profile/');
    }
    
    async updateUserProfile(profileData) {
        return this.request('/api/user/profile/', {
            method: 'POST',
            body: JSON.stringify(profileData)
        });
    }
    
    // Billing methods (authenticated)
    async getCurrentPlan() {
        return this.request('/api/billing/current-plan/');
    }
    
    async getBillingHistory() {
        return this.request('/api/billing/history/');
    }
}

// Export singleton instance
export const stockAPI = new StockScannerAPI();

// Usage examples:
// const stocks = await stockAPI.getStocks({ limit: 10 });
// const quote = await stockAPI.getStockQuote('AAPL');
// const user = await stockAPI.login({ username: 'user', password: 'pass' });
```

---

## ✅ Best Practices

### 1. **Token Management**
```javascript
// Always check token expiry (if applicable)
const isTokenValid = () => {
    const token = localStorage.getItem('rts_token');
    // Add token expiry logic if needed
    return !!token;
};

// Refresh token on API errors
const handleTokenRefresh = async () => {
    // Implement if backend supports token refresh
};
```

### 2. **Error Boundaries**
```javascript
// React Error Boundary for API errors
class APIErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    
    componentDidCatch(error, errorInfo) {
        console.error('API Error:', error, errorInfo);
    }
    
    render() {
        if (this.state.hasError) {
            return <div>Something went wrong with the API call.</div>;
        }
        
        return this.props.children;
    }
}
```

### 3. **Caching Strategy**
```javascript
// Simple cache implementation
class APICache {
    constructor(ttl = 300000) { // 5 minutes
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    get(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        if (Date.now() - cached.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }
}

const apiCache = new APICache();

// Use cache in API calls
const getCachedStockQuote = async (symbol) => {
    const cacheKey = `quote_${symbol}`;
    const cached = apiCache.get(cacheKey);
    
    if (cached) {
        return cached;
    }
    
    const quote = await stockAPI.getStockQuote(symbol);
    apiCache.set(cacheKey, quote);
    return quote;
};
```

### 4. **Loading States**
```javascript
// Loading state management
const useApiCall = (apiFunction) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const execute = useCallback(async (...args) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await apiFunction(...args);
            setData(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [apiFunction]);
    
    return { data, loading, error, execute };
};
```

### 5. **Rate Limit Handling**
```javascript
// Rate limit aware API wrapper
const rateLimitedAPI = {
    async call(apiFunction, ...args) {
        try {
            return await apiFunction(...args);
        } catch (error) {
            if (error.message.includes('rate limit')) {
                // Show user-friendly message
                throw new Error('You have reached your API limit. Please upgrade your plan or try again later.');
            }
            throw error;
        }
    }
};
```

---

## 🚀 Quick Start Checklist

### 1. **Setup Configuration**
- [ ] Set correct `BASE_URL`
- [ ] Configure CORS if needed
- [ ] Set up error handling

### 2. **Authentication Implementation**
- [ ] Implement login/register functions
- [ ] Set up token storage (localStorage)
- [ ] Create authentication context/hook
- [ ] Handle authentication errors

### 3. **API Integration**
- [ ] Create API service class
- [ ] Implement stock data fetching
- [ ] Set up real-time data polling
- [ ] Add search functionality

### 4. **User Experience**
- [ ] Add loading states
- [ ] Implement error boundaries
- [ ] Set up rate limit handling
- [ ] Cache frequently accessed data

### 5. **Testing**
- [ ] Test all endpoints
- [ ] Verify authentication flow
- [ ] Check error handling
- [ ] Test rate limiting

---

## 📞 Support & Additional Information

For issues with specific endpoints or integration problems:

1. **Check endpoint status** using the testing tools provided
2. **Verify authentication** token is valid and properly formatted
3. **Review rate limits** for your current plan
4. **Check CORS settings** if requests are being blocked

**Current Known Issues:**
- PayPal endpoints have CSRF protection issues (being resolved)
- Some endpoints may hit rate limits during heavy testing
- Real-time data requires yfinance package to be working

This documentation covers all current backend functionality and provides complete integration examples for frontend development.