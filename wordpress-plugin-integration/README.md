# WordPress Plugin for Stock Scanner Integration

## 🎯 **Perfect for Hosted WordPress Sites (IONOS, etc.)**

This plugin is specifically designed to work with **hosted WordPress sites** that are separate from your Django backend. It connects to your remote Django API and provides real-time stock data and news.

## 📁 **What to Add to `/wordpress/wp-content/plugins/`**

Copy the entire `stock-scanner-plugin` folder to your WordPress plugins directory:

```bash
cp -r stock-scanner-plugin /wordpress/wp-content/plugins/
```

## ✅ **Plugin Features**

### **🔌 Remote API Integration**
- **Works with any hosted WordPress** (IONOS, GoDaddy, Bluehost, etc.)
- **Connects to remote Django API** via HTTP requests
- **Built-in caching** to reduce API calls
- **Error handling** with fallback data
- **Timeout protection** for slow connections

### **📊 Widgets & Shortcodes**
- **Stock Ticker Widget** - Real-time stock prices
- **News Feed Widget** - Yahoo Finance news with sentiment
- **Market Summary Widget** - Key market indices
- **Customizable shortcodes** for any page/post
- **Responsive design** for all devices

### **⚙️ Admin Features**
- **Settings page** to configure API URL
- **Connection testing** to verify API works
- **Widget management** in WordPress admin
- **Shortcode examples** and documentation

## 🚀 **Installation Steps**

### 1. **Upload Plugin**
```bash
# Copy plugin to WordPress plugins directory
cp -r stock-scanner-plugin /wordpress/wp-content/plugins/
```

### 2. **Activate Plugin**
1. Go to WordPress Admin → Plugins
2. Find "Stock Scanner Integration"
3. Click "Activate"

### 3. **Configure API URL**
1. Go to WordPress Admin → Settings → Stock Scanner
2. Enter your Django API URL (e.g., `http://your-domain.com/api`)
3. Click "Save Changes"
4. Test the connection

### 4. **Add Widgets**
1. Go to WordPress Admin → Appearance → Widgets
2. Drag "Stock Scanner Widget" to any widget area
3. Configure widget settings

## 📋 **Shortcodes Available**

### **Stock Ticker**
```php
[stock_ticker limit="10" category="gainers" show_changes="true"]
```

**Parameters:**
- `limit` - Number of stocks (default: 10)
- `category` - gainers, losers, active (default: "")
- `show_changes` - Show price changes (default: true)
- `auto_refresh` - Auto-refresh data (default: true)
- `refresh_interval` - Refresh time in seconds (default: 30)

### **News Feed**
```php
[stock_news limit="5" show_sentiment="true"]
```

**Parameters:**
- `limit` - Number of news articles (default: 5)
- `show_sentiment` - Show sentiment grades (default: true)
- `auto_refresh` - Auto-refresh data (default: true)
- `refresh_interval` - Refresh time in seconds (default: 60)

### **Market Summary**
```php
[market_summary show_changes="true"]
```

**Parameters:**
- `show_changes` - Show market changes (default: true)
- `auto_refresh` - Auto-refresh data (default: true)
- `refresh_interval` - Refresh time in seconds (default: 60)

## 🔧 **API Configuration**

### **Django API Requirements**
Your Django API must be accessible via HTTP and provide these endpoints:

- `GET /api/wordpress/stocks/` - Stock data
- `GET /api/wordpress/news/` - News data  
- `GET /api/market/stats/` - Market summary

### **CORS Configuration**
Ensure your Django API allows requests from your WordPress domain:

```python
# In Django settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-wordpress-domain.com",
    "http://localhost:8000",  # For testing
]
```

### **API Response Format**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "AAPL",
      "current_price": 175.25,
      "change_percent": 2.34,
      "volume": 45678900
    }
  ]
}
```

## 📱 **Widget Usage**

### **Adding Widgets to Sidebar**
1. Go to WordPress Admin → Appearance → Widgets
2. Drag "Stock Scanner Widget" to sidebar
3. Configure:
   - **Title** - Widget title
   - **Widget Type** - Ticker, News, or Summary
   - **Limit** - Number of items to display

### **Adding Widgets to Pages**
Use shortcodes in any page or post:

```php
<!-- Stock ticker -->
[stock_ticker limit="5" category="gainers"]

<!-- News feed -->
[stock_news limit="3" show_sentiment="true"]

<!-- Market summary -->
[market_summary show_changes="true"]
```

## 🎨 **Customization**

### **Styling**
The plugin includes modern, responsive CSS that works with most themes. You can customize by adding CSS to your theme:

```css
/* Custom stock ticker colors */
.ticker-item.positive {
    border-left-color: #your-color;
}

/* Custom news sentiment colors */
.news-item.sentiment-excellent {
    border-left-color: #your-color;
}
```

### **JavaScript Events**
The plugin triggers custom events you can hook into:

```javascript
// Listen for stock data updates
$(document).on('stockDataLoaded', function(event, data) {
    console.log('Stock data updated:', data);
});

// Listen for news data updates
$(document).on('newsDataLoaded', function(event, data) {
    console.log('News data updated:', data);
});
```

## 🔒 **Security Features**

### **WordPress Security**
- **Nonce verification** for all AJAX requests
- **Input sanitization** for all parameters
- **Output escaping** for all displayed data
- **Capability checks** for admin functions

### **API Security**
- **Timeout protection** (10 seconds)
- **Error handling** with graceful fallbacks
- **Caching** to reduce server load
- **User-Agent** identification for requests

## 📊 **Performance Features**

### **Caching**
- **5-minute cache** for API responses
- **Transient storage** using WordPress cache
- **Automatic cache invalidation**
- **Fallback data** when API is unavailable

### **Optimization**
- **Lazy loading** of widgets
- **Minified CSS/JS** files
- **Efficient DOM updates**
- **Memory management**

## 🛠 **Troubleshooting**

### **Common Issues**

1. **"API connection failed"**
   - Check Django server is running
   - Verify API URL in settings
   - Test API endpoints directly
   - Check CORS configuration

2. **"Widget not loading"**
   - Check browser console for errors
   - Verify plugin is activated
   - Check widget placement
   - Test with different theme

3. **"No data displayed"**
   - Check API response format
   - Verify shortcode parameters
   - Test with sample data
   - Check cache settings

### **Debug Mode**
Enable WordPress debug mode in `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

### **API Testing**
Test your Django API directly:
```bash
curl -X GET "http://your-domain.com/api/wordpress/stocks/?limit=1"
```

## 📈 **Monitoring & Analytics**

### **Plugin Health**
- **Connection status** in admin panel
- **Error logging** for debugging
- **Performance metrics** for optimization
- **Usage statistics** for insights

### **API Monitoring**
- **Response times** tracking
- **Error rates** monitoring
- **Cache hit rates** analysis
- **User engagement** metrics

## 🔄 **Updates & Maintenance**

### **Plugin Updates**
- **Automatic update checks**
- **Backward compatibility**
- **Migration scripts** for data
- **Version control** tracking

### **API Compatibility**
- **Version detection** for API
- **Feature flags** for capabilities
- **Graceful degradation** for missing features
- **Migration support** for API changes

## 📞 **Support**

### **Getting Help**
1. Check the troubleshooting section
2. Review WordPress error logs
3. Test API endpoints directly
4. Check browser console for errors

### **Customization**
- Modify `stock-scanner-plugin.php` for core changes
- Edit `css/stock-scanner-plugin.css` for styling
- Update `js/stock-scanner-plugin.js` for functionality

## 🎉 **Ready for Production!**

The plugin is fully functional and ready for production use on any hosted WordPress site. It provides:

**✅ Remote API Integration**
- Works with any hosted WordPress
- Connects to remote Django API
- Built-in error handling
- Automatic caching

**✅ User-Friendly Features**
- Easy admin configuration
- Drag-and-drop widgets
- Simple shortcodes
- Responsive design

**✅ Performance Optimized**
- Efficient caching
- Minimal server load
- Fast loading times
- Memory efficient

**✅ Security Compliant**
- WordPress security standards
- Input validation
- Output sanitization
- Nonce protection

The plugin will work perfectly with your IONOS hosted WordPress site and connect to your Django API! 🚀