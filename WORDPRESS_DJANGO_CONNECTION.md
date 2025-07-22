# 🔗 WordPress ↔ Django Backend Connection Architecture

## 📋 **Executive Summary**
The WordPress frontend connects to the Django backend through a **multi-layer architecture** using REST APIs, CORS configuration, and JavaScript AJAX calls. Here's the complete technical breakdown:

---

## 🏗️ **Connection Architecture Overview**

```
┌─────────────────┐    HTTPS/HTTP     ┌─────────────────┐
│   WordPress     │ ◄──────────────► │   Django        │
│   Frontend      │    REST API       │   Backend       │
│                 │    Calls          │                 │
├─────────────────┤                   ├─────────────────┤
│ • PHP Plugin    │                   │ • REST APIs     │
│ • JavaScript    │                   │ • Database      │
│ • HTML Forms    │                   │ • yfinance      │
│ • CSS Styling   │                   │ • Stock Data    │
└─────────────────┘                   └─────────────────┘
```

---

## 🔧 **Technical Connection Layers**

### **Layer 1: WordPress Plugin Configuration**
**File:** `wordpress_plugin/stock-scanner-integration/stock-scanner-integration.php`

```php
class StockScannerIntegration {
    private $api_base_url;
    private $api_secret;
    
    public function __construct() {
                 // Django API endpoint configuration
         $this->api_base_url = get_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        $this->api_secret = get_option('stock_scanner_api_secret', '');
    }
    
    public function enqueue_scripts() {
        // Load frontend JavaScript
        wp_enqueue_script('stock-scanner-js', plugin_dir_url(__FILE__) . 'assets/stock-scanner.js');
        
        // Pass WordPress AJAX URL to JavaScript
        wp_localize_script('stock-scanner-js', 'stock_scanner_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ));
    }
}
```

### **Layer 2: Frontend JavaScript API Client**
**File:** `wordpress_plugin/stock-scanner-integration/assets/stock-scanner-frontend.js`

```javascript
class StockScannerFrontend {
    constructor() {
        // Django API base URL
        this.apiBase = '/api/';  // Points to Django backend
        this.init();
    }

    // Email signup API call
    async handleEmailSignup(form) {
        const response = await fetch(`${this.apiBase}email-signup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                email: formData.get('email'),
                category: formData.get('category')
            })
        });
    }

    // Stock filtering API call
    async handleStockFilter() {
        const response = await fetch(`${this.apiBase}stocks/filter/?${params}`);
        const data = await response.json();
    }

    // Stock lookup API call
    async handleStockLookup(ticker) {
        const response = await fetch(`${this.apiBase}stocks/lookup/${ticker}/`);
        const result = await response.json();
    }

    // News API call
    async loadNews() {
        const response = await fetch(`${this.apiBase}news/?${params}`);
        const data = await response.json();
    }
}
```

### **Layer 3: Django Backend API Endpoints**
**File:** `stocks/api_views.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json

@api_view(['POST'])
@csrf_exempt
def email_signup_api(request):
    """Handle email signups from WordPress frontend"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        category = data.get('category')
        
        # Create email subscription
        subscription = EmailSubscription.objects.create(
            email=email,
            category=category,
            is_active=True
        )
        
        return Response({
            'success': True,
            'message': f'Successfully subscribed to {category} alerts!'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=400)

@api_view(['GET'])
def stock_filter_api(request):
    """Filter stocks based on criteria from WordPress"""
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # ... filtering logic
    
    return Response({
        'success': True,
        'stocks': stock_data,
        'count': len(stock_data)
    })

@api_view(['GET'])
def stock_lookup_api(request, ticker):
    """Get detailed stock data for WordPress"""
    try:
        # Fetch from yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return Response({
            'success': True,
            'data': {
                'ticker': ticker,
                'company_name': info.get('longName'),
                'current_price': info.get('currentPrice'),
                # ... more data
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch data for {ticker}'
        })

@api_view(['GET'])
def stock_news_api(request):
    """Get financial news for WordPress"""
    category = request.GET.get('category', 'market')
    ticker = request.GET.get('ticker')
    
    # Fetch news data
    news_data = get_financial_news(category, ticker)
    
    return Response({
        'success': True,
        'news': news_data,
        'important_stocks': get_important_stocks()
    })
```

### **Layer 4: Django URL Configuration**
**File:** `stocks/urls.py`

```python
from django.urls import path
from . import api_views

urlpatterns = [
    # WordPress Integration Endpoints
    path('api/email-signup/', api_views.email_signup_api, name='email_signup'),
    path('api/stocks/filter/', api_views.stock_filter_api, name='stock_filter'),
    path('api/stocks/lookup/<str:ticker>/', api_views.stock_lookup_api, name='stock_lookup'),
    path('api/news/', api_views.stock_news_api, name='stock_news'),
]
```

### **Layer 5: CORS Configuration**
**File:** `stockscanner_django/settings.py`

```python
# Enable CORS for WordPress communication
INSTALLED_APPS = [
    'corsheaders',  # Enable CORS middleware
    # ... other apps
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware first
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# CORS Configuration for WordPress Integration
 CORS_ALLOWED_ORIGINS = [
     "http://localhost:8000",      # Local development
     "http://127.0.0.1:8000",      # Local development
     "https://retailtradescanner.com", # Production WordPress site
     "https://www.retailtradescanner.com", # Production with www
 ]

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'x-csrftoken',  # Important for Django CSRF protection
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True  # Allow cookies/auth
```

---

## 🔄 **Data Flow Examples**

### **1. Email Signup Flow**
```
WordPress Page → JavaScript Form → Django API → Database → Response → WordPress UI
```

**Detailed Steps:**
1. **User visits** WordPress page (`/email-stock-lists/`)
2. **JavaScript detects** page type and **injects signup form**
3. **User submits** email and category
4. **JavaScript prevents** default form submission
5. **AJAX call** to `POST /api/email-signup/`
6. **Django receives** request with email/category data
7. **Django validates** email format and creates `EmailSubscription`
8. **Django returns** JSON response with success/error
9. **JavaScript displays** confirmation message to user

### **2. Stock Filtering Flow**
```
Filter Form → Real-time Input → Debounced API Call → Django Processing → Filtered Results → Dynamic Display
```

**Detailed Steps:**
1. **User enters** filter criteria (price range, volume, etc.)
2. **JavaScript debounces** input to avoid excessive API calls
3. **AJAX call** to `GET /api/stocks/filter/?min_price=50&max_price=200`
4. **Django queries** database with filters
5. **Django returns** filtered stock data
6. **JavaScript renders** results in professional card layout

### **3. Stock Lookup Flow**
```
Ticker Input → API Request → yfinance Data → Django Processing → Comprehensive Display
```

**Detailed Steps:**
1. **User enters** stock ticker (e.g., "AAPL")
2. **JavaScript calls** `GET /api/stocks/lookup/AAPL/`
3. **Django fetches** real-time data from yfinance
4. **Django processes** and formats financial data
5. **Django returns** comprehensive stock information
6. **JavaScript displays** detailed stock metrics and charts

### **4. News Display Flow**
```
Page Load → News Request → News Aggregation → Important Stocks → Dynamic Content
```

**Detailed Steps:**
1. **Page loads** with news interface
2. **JavaScript calls** `GET /api/news/?category=market`
3. **Django aggregates** financial news from multiple sources
4. **Django identifies** important/trending stocks
5. **Django returns** news articles + important stocks
6. **JavaScript renders** news feed with trending sidebar

---

## 🛡️ **Security & Authentication**

### **CSRF Protection**
```javascript
getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Used in API calls
headers: {
    'X-CSRFToken': this.getCSRFToken()
}
```

### **Rate Limiting** (Django side)
```python
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

def rate_limit_check(request, limit=100, window=3600):
    """Simple rate limiting by IP"""
    ip = request.META.get('REMOTE_ADDR')
    key = f'rate_limit_{ip}'
    current = cache.get(key, 0)
    
    if current >= limit:
        return HttpResponseTooManyRequests("Rate limit exceeded")
    
    cache.set(key, current + 1, window)
    return None
```

---

## 🌐 **Network Configuration**

### **Development Setup:**
- **WordPress:** `http://localhost:80` (or XAMPP/WAMP)
- **Django:** `http://localhost:8000`
- **API Calls:** WordPress → `localhost:8000/api/`

 ### **Production Setup:**
 - **WordPress:** `https://retailtradescanner.com`
 - **Django:** `https://api.retailtradescanner.com` (subdomain)
 - **API Calls:** WordPress → `https://api.retailtradescanner.com/api/`

### **Proxy Configuration** (Optional)
```nginx
# Nginx proxy for seamless integration
location /api/ {
    proxy_pass http://django-backend:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

---

## 🔧 **Configuration Steps**

### **1. WordPress Plugin Configuration**
 ```php
 // In WordPress admin, set these options:
 update_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
 update_option('stock_scanner_api_secret', 'your-secret-key');
 ```

### **2. Django Settings Update**
 ```python
 # Add your WordPress domain to CORS
 CORS_ALLOWED_ORIGINS = [
     "https://retailtradescanner.com",
     "https://www.retailtradescanner.com",
 ]

 # Add to ALLOWED_HOSTS
 ALLOWED_HOSTS = ['api.retailtradescanner.com', 'retailtradescanner.com', 'www.retailtradescanner.com']
 ```

 ### **3. DNS/Domain Setup**
 ```
 # WordPress site
 retailtradescanner.com → WordPress server

 # Django API
 api.retailtradescanner.com → Django server

 # Or subdirectory
 retailtradescanner.com/api/ → Proxy to Django
 ```

---

## 🚀 **Performance Optimizations**

### **Frontend Caching**
```javascript
class StockScannerFrontend {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    async cachedFetch(url) {
        const cached = this.cache.get(url);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }

        const response = await fetch(url);
        const data = await response.json();
        
        this.cache.set(url, {
            data: data,
            timestamp: Date.now()
        });

        return data;
    }
}
```

### **Django API Caching**
```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
@api_view(['GET'])
def stock_data_api(request):
    # Expensive operation cached
    return Response(expensive_stock_calculation())
```

---

## 🔍 **Debugging & Monitoring**

### **WordPress Debug Console**
```javascript
// Enable debug logging
console.log('API Response:', data);
console.error('API Error:', error);

// Network tab in browser dev tools shows:
// - API request URLs
// - Request/response headers
// - Response data
// - Timing information
```

### **Django Logging**
```python
import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def email_signup_api(request):
    logger.info(f"Email signup request from {request.META.get('REMOTE_ADDR')}")
    # ... rest of function
```

---

## ✅ **Connection Verification Checklist**

### **WordPress Side:**
- [ ] Plugin activated and configured
- [ ] JavaScript files loaded properly
- [ ] API base URL set correctly
- [ ] CSRF tokens available
- [ ] Browser console shows no errors

### **Django Side:**
- [ ] CORS properly configured
- [ ] API endpoints responding
- [ ] Database connections working
- [ ] yfinance data accessible
- [ ] No authentication errors

### **Network:**
- [ ] DNS resolution working
- [ ] SSL certificates valid (production)
- [ ] Firewall allowing traffic
- [ ] Rate limiting configured
- [ ] Monitoring active

---

This architecture provides a **robust, secure, and scalable** connection between WordPress and Django, enabling real-time stock data, email management, news aggregation, and advanced filtering capabilities! 🚀✨