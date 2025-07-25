# 🌐 WordPress Integration Guide

This guide shows you how to integrate the Stock Scanner API with your WordPress site.

## ✅ **API Status: WORKING**

Your Stock Scanner backend is running and the API endpoints are functional!

**Test URL**: http://127.0.0.1:8000/api/simple/status/

---

## 🔗 **Available API Endpoints**

### **1. System Status**
```
GET /api/simple/status/
```
**Purpose**: Check if the API is running  
**Response**: System status and available endpoints

### **2. Stock Data**
```
GET /api/simple/stocks/
GET /api/simple/stocks/?search=AAPL
GET /api/simple/stocks/?limit=10
```
**Purpose**: Get stock data with optional filtering  
**Response**: Array of stock objects with prices, changes, volume

### **3. Individual Stock**
```
GET /api/simple/stocks/AAPL/
GET /api/simple/stocks/MSFT/
```
**Purpose**: Get detailed data for a specific stock  
**Response**: Single stock object with full details

### **4. News Data**
```
GET /api/simple/news/
GET /api/simple/news/?sentiment=A
GET /api/simple/news/?ticker=AAPL
```
**Purpose**: Get news articles with sentiment analysis  
**Response**: Array of news articles with sentiment scores

---

## 📋 **WordPress Integration Examples**

### **PHP Example - Get Stock Data**

```php
<?php
// WordPress function to fetch stock data
function get_stock_scanner_data($ticker = '') {
    $api_url = 'http://127.0.0.1:8000/api/simple/stocks/';
    
    if (!empty($ticker)) {
        $api_url .= $ticker . '/';
    }
    
    $response = wp_remote_get($api_url);
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if ($data['success']) {
        return $data['data'];
    }
    
    return false;
}

// Usage in WordPress
$stocks = get_stock_scanner_data();
$apple_stock = get_stock_scanner_data('AAPL');
?>
```

### **JavaScript Example - Display Stock Widget**

```javascript
// Fetch and display stock data
async function displayStockWidget() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/simple/stocks/?limit=5');
        const data = await response.json();
        
        if (data.success) {
            const stocksHtml = data.data.map(stock => `
                <div class="stock-item">
                    <h4>${stock.ticker} - ${stock.company_name}</h4>
                    <p>Price: ${stock.formatted_price}</p>
                    <p>Change: ${stock.formatted_change}</p>
                    <p>Volume: ${stock.formatted_volume}</p>
                </div>
            `).join('');
            
            document.getElementById('stock-widget').innerHTML = stocksHtml;
        }
    } catch (error) {
        console.error('Error fetching stock data:', error);
    }
}

// Call the function
displayStockWidget();
```

### **WordPress Shortcode Example**

```php
<?php
// Add to your theme's functions.php
function stock_scanner_shortcode($atts) {
    $atts = shortcode_atts(array(
        'ticker' => '',
        'limit' => 5,
        'type' => 'stocks'
    ), $atts);
    
    $api_url = 'http://127.0.0.1:8000/api/simple/' . $atts['type'] . '/';
    
    if (!empty($atts['ticker'])) {
        $api_url .= $atts['ticker'] . '/';
    } else {
        $api_url .= '?limit=' . $atts['limit'];
    }
    
    $response = wp_remote_get($api_url);
    
    if (is_wp_error($response)) {
        return '<p>Error loading stock data</p>';
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (!$data['success']) {
        return '<p>No stock data available</p>';
    }
    
    $output = '<div class="stock-scanner-widget">';
    
    if ($atts['type'] === 'stocks') {
        $stocks = isset($data['data'][0]) ? $data['data'] : [$data['data']];
        
        foreach ($stocks as $stock) {
            $output .= '<div class="stock-item">';
            $output .= '<h4>' . $stock['ticker'] . ' - ' . $stock['company_name'] . '</h4>';
            $output .= '<p><strong>Price:</strong> ' . $stock['formatted_price'] . '</p>';
            $output .= '<p><strong>Change:</strong> ' . $stock['formatted_change'] . '</p>';
            $output .= '<p><strong>Volume:</strong> ' . $stock['formatted_volume'] . '</p>';
            $output .= '</div>';
        }
    }
    
    $output .= '</div>';
    
    return $output;
}

add_shortcode('stock_scanner', 'stock_scanner_shortcode');
?>
```

**Usage in WordPress posts/pages:**
```
[stock_scanner ticker="AAPL"]
[stock_scanner limit="10"]
[stock_scanner type="news" limit="5"]
```

---

## 🎨 **CSS Styling Example**

```css
.stock-scanner-widget {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    background: #f9f9f9;
}

.stock-item {
    border-bottom: 1px solid #eee;
    padding: 15px 0;
    margin-bottom: 15px;
}

.stock-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.stock-item h4 {
    margin: 0 0 10px 0;
    color: #333;
}

.stock-item p {
    margin: 5px 0;
    color: #666;
}
```

---

## 🔧 **WordPress Plugin Structure**

Create a simple WordPress plugin:

**File: `wp-content/plugins/stock-scanner/stock-scanner.php`**

```php
<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Description: Integrates with Stock Scanner Django API
 * Version: 1.0
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class StockScannerPlugin {
    
    private $api_base = 'http://127.0.0.1:8000/api/simple/';
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_shortcode('stock_scanner', array($this, 'shortcode'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
    }
    
    public function init() {
        // Plugin initialization
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('stock-scanner-js', plugin_dir_url(__FILE__) . 'stock-scanner.js', array('jquery'), '1.0', true);
        wp_enqueue_style('stock-scanner-css', plugin_dir_url(__FILE__) . 'stock-scanner.css', array(), '1.0');
        
        // Pass API URL to JavaScript
        wp_localize_script('stock-scanner-js', 'stockScannerAjax', array(
            'api_url' => $this->api_base
        ));
    }
    
    public function shortcode($atts) {
        // Shortcode implementation (from example above)
        return $this->render_stock_widget($atts);
    }
    
    private function render_stock_widget($atts) {
        // Widget rendering logic
    }
}

// Initialize the plugin
new StockScannerPlugin();
?>
```

---

## 🚀 **Testing Your Integration**

### **1. Test API Connection**
```bash
curl http://127.0.0.1:8000/api/simple/status/
```

### **2. Test in WordPress**
Add this to a WordPress page to test:
```php
<?php
$response = wp_remote_get('http://127.0.0.1:8000/api/simple/stocks/?limit=3');
$body = wp_remote_retrieve_body($response);
$data = json_decode($body, true);

if ($data['success']) {
    echo '<pre>' . print_r($data['data'], true) . '</pre>';
} else {
    echo 'API connection failed';
}
?>
```

### **3. Check WordPress Admin**
- Go to your WordPress admin
- Add the shortcode `[stock_scanner limit="5"]` to any post/page
- View the page to see stock data

---

## 📊 **API Response Format**

### **Stock Data Response**
```json
{
    "success": true,
    "data": [
        {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "current_price": 175.43,
            "price_change": 2.15,
            "price_change_percent": 1.24,
            "volume": 52847392,
            "formatted_price": "$175.43",
            "formatted_change": "+1.24%",
            "formatted_volume": "52,847,392",
            "last_updated": "2025-07-25T19:12:06.539305+00:00"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_stocks": 5
    },
    "meta": {
        "api_version": "1.0"
    }
}
```

### **News Data Response**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "title": "Apple Reports Strong Q4 Earnings",
            "summary": "Apple Inc. reported quarterly earnings...",
            "url": "https://example.com/apple-earnings",
            "source": "Financial News",
            "sentiment_grade": "A",
            "sentiment_color": "green",
            "mentioned_tickers": ["AAPL"],
            "formatted_date": "July 25, 2025"
        }
    ]
}
```

---

## ✅ **Verification Checklist**

- [ ] ✅ **Django Server Running**: http://127.0.0.1:8000/
- [ ] ✅ **API Status Working**: http://127.0.0.1:8000/api/simple/status/
- [ ] ✅ **Stock Data Available**: http://127.0.0.1:8000/api/simple/stocks/
- [ ] ✅ **News Data Available**: http://127.0.0.1:8000/api/simple/news/
- [ ] ⏳ **WordPress Integration**: Add shortcode to WordPress
- [ ] ⏳ **Custom Styling**: Add CSS for better appearance
- [ ] ⏳ **Production Setup**: Follow production deployment guide

---

## 🎉 **Your Stock Scanner is Ready!**

**Backend Status**: ✅ **WORKING**  
**API Status**: ✅ **FUNCTIONAL**  
**WordPress Ready**: ✅ **YES**

You can now:
1. **Use the API endpoints** in your WordPress site
2. **Create custom widgets** with stock data
3. **Display real-time stock information** 
4. **Show news with sentiment analysis**
5. **Build custom dashboards** for your users

**Next Steps**: Follow the production deployment guide when ready to go live!