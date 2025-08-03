# WordPress Theme Integration for Stock Scanner

## 📁 What to Add to `/wordpress/wp-content/themes/`

Copy the entire `stock-scanner-theme` folder to your WordPress themes directory:

```bash
cp -r stock-scanner-theme /wordpress/wp-content/themes/
```

## 🎯 Theme Features

### ✅ **Complete WordPress Integration**
- **Live Stock Ticker** - Real-time stock data scrolling in header
- **Stock Widgets** - Display stock data anywhere with shortcodes
- **News Feed** - Yahoo Finance news with sentiment analysis
- **Market Summary** - Key market indices in footer
- **Responsive Design** - Works on all devices
- **AJAX Integration** - Seamless API communication

### 📊 **Shortcodes Available**

#### Stock Ticker Shortcode
```php
[stock_ticker limit="10" category="gainers" show_changes="true"]
```

**Parameters:**
- `limit` - Number of stocks to display (default: 10)
- `category` - Filter by category: gainers, losers, active (default: "")
- `show_changes` - Show price changes (default: true)

#### News Feed Shortcode
```php
[stock_news limit="5" show_sentiment="true"]
```

**Parameters:**
- `limit` - Number of news articles (default: 5)
- `show_sentiment` - Show sentiment grades (default: true)

### 🔧 **API Integration**

The theme automatically connects to your Django API at:
- **Stock Data**: `http://127.0.0.1:8000/api/wordpress/stocks/`
- **News Data**: `http://127.0.0.1:8000/api/wordpress/news/`

### 📱 **Responsive Features**
- Mobile-optimized ticker
- Responsive grid layouts
- Touch-friendly navigation
- Adaptive content sizing

## 🚀 **Installation Steps**

### 1. **Copy Theme Files**
```bash
# Copy the theme to WordPress themes directory
cp -r stock-scanner-theme /wordpress/wp-content/themes/
```

### 2. **Activate Theme**
1. Go to WordPress Admin → Appearance → Themes
2. Find "Stock Scanner" theme
3. Click "Activate"

### 3. **Configure API URL**
Edit `functions.php` and update the API URL:
```php
'api_url' => 'http://your-domain.com/api', // Change to your Django server URL
```

### 4. **Test Integration**
1. Visit your WordPress site
2. Check the live ticker in the header
3. Test shortcodes on any page/post

## 📋 **File Structure**

```
stock-scanner-theme/
├── style.css              # Theme information
├── functions.php          # Theme functions and API integration
├── index.php             # Main template
├── header.php            # Header template with ticker
├── footer.php            # Footer with market summary
├── css/
│   └── stock-scanner.css # Main stylesheet
└── js/
    └── stock-scanner.js  # JavaScript functionality
```

## 🎨 **Customization Options**

### **Colors**
The theme uses a modern color scheme:
- Primary: `#3498db` (Blue)
- Success: `#27ae60` (Green)
- Warning: `#f39c12` (Orange)
- Danger: `#e74c3c` (Red)
- Dark: `#2c3e50` (Dark Blue)

### **Layout**
- **Header**: Gradient background with live ticker
- **Content**: Clean white cards with shadows
- **Footer**: Dark background with market summary

### **Typography**
- Font: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- Responsive font sizing
- Clear hierarchy with different weights

## 🔌 **API Endpoints Used**

### **Stock Data**
- `GET /api/wordpress/stocks/` - Get stock list
- Parameters: `limit`, `category`, `search`

### **News Data**
- `GET /api/wordpress/news/` - Get news articles
- Parameters: `limit`, `show_sentiment`

### **Response Format**
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

## 📱 **Mobile Features**

### **Responsive Design**
- Mobile-first approach
- Touch-friendly buttons
- Optimized ticker for small screens
- Collapsible navigation

### **Performance**
- Lazy loading of content
- Cached API responses
- Optimized images
- Minified CSS/JS

## 🛠 **Troubleshooting**

### **Common Issues**

1. **API Connection Failed**
   - Check Django server is running
   - Verify API URL in `functions.php`
   - Test API endpoints directly

2. **Ticker Not Loading**
   - Check browser console for errors
   - Verify AJAX nonce is working
   - Test with simple API endpoint

3. **Styling Issues**
   - Clear browser cache
   - Check CSS file paths
   - Verify theme activation

### **Debug Mode**
Enable WordPress debug mode in `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

## 📈 **Performance Tips**

### **Optimization**
- Use caching plugins (WP Rocket, W3 Total Cache)
- Optimize images
- Minify CSS/JS
- Use CDN for static assets

### **API Optimization**
- Cache API responses
- Use pagination for large datasets
- Implement rate limiting
- Monitor API performance

## 🔒 **Security**

### **WordPress Security**
- Keep WordPress updated
- Use strong passwords
- Install security plugins
- Regular backups

### **API Security**
- Use HTTPS for production
- Implement API authentication
- Rate limit API requests
- Validate all inputs

## 📞 **Support**

### **Getting Help**
1. Check the troubleshooting section
2. Review WordPress error logs
3. Test API endpoints directly
4. Check browser console for errors

### **Customization**
- Modify `functions.php` for API changes
- Edit `css/stock-scanner.css` for styling
- Update `js/stock-scanner.js` for functionality

## 🎉 **Ready to Use!**

The theme is fully functional and ready for production use. Simply copy the files to your WordPress themes directory and activate the theme. The integration with your Django API will provide real-time stock data and news to your WordPress site!

**Key Benefits:**
- ✅ Real-time stock data
- ✅ Live news feed with sentiment analysis
- ✅ Responsive design
- ✅ Easy customization
- ✅ SEO optimized
- ✅ Performance optimized