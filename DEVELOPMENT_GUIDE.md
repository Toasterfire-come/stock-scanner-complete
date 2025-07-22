# 👨‍💻 Development Guide - Stock Scanner Platform

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Components:**
```
📊 Django Backend (API Server)
├── Real Data Analytics System
├── Membership Management (4 Tiers)
├── Stock Data APIs (yfinance integration)
├── Email Subscription System
└── Sales Tax Calculation

🌐 WordPress Frontend (User Interface)  
├── 24 Professional Pages
├── Live Stock Widgets
├── Email Signup Forms
├── Member Dashboard
└── Analytics Admin Widget

💳 Payment & Tax System
├── Stripe Integration (ready)
├── Paid Membership Pro Plugin
├── Automatic Sales Tax Collection
└── Usage Limit Enforcement
```

---

## 🛠️ **DEVELOPMENT SETUP**

### **Quick Start:**
```bash
# 1. Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Install dependencies
pip install -r requirements.txt

# 3. Database setup
python manage.py migrate
python manage.py setup_memberships
python manage.py createsuperuser

# 4. Start development server
python manage.py runserver
```

### **Access Points:**
- **Django Admin:** http://localhost:8000/admin
- **API Documentation:** http://localhost:8000/api/
- **Analytics API:** http://localhost:8000/api/analytics/public/
- **Membership Admin:** http://localhost:8000/admin/stocks/membership/

---

## 🗃️ **DATABASE MODELS**

### **Membership Model (NEW):**
```python
class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.CharField(choices=['free', 'basic', 'professional', 'expert'])
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    # Stripe Integration
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_status = models.CharField(max_length=20, default='active')
    
    # Usage Tracking
    monthly_lookups_used = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)
    
    # Methods
    def can_make_lookup(self):
        return self.monthly_lookups_used < self.tier_limits
    
    def reset_monthly_usage(self):
        self.monthly_lookups_used = 0
        self.save()
```

### **StockAlert Model:**
```python
class StockAlert(models.Model):
    ticker = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255, blank=True)
    current_price = models.FloatField()
    volume_today = models.BigIntegerField()
    pe_ratio = models.FloatField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    last_update = models.DateTimeField()
    sent = models.BooleanField(default=False)
```

### **EmailSubscription Model:**
```python
class EmailSubscription(models.Model):
    email = models.EmailField()
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('email', 'category')
```

---

## 🔗 **API ENDPOINTS**

### **Analytics APIs (Real Data):**
```python
# Public analytics for website display
GET /api/analytics/public/
{
  "total_members": 47,
  "avg_spending_per_person": 6.97,
  "monthly_revenue": 327.84,
  "email_subscribers": 25,
  "stocks_tracked": 150,
  "platform_status": "active"
}

# Admin analytics (staff only)  
GET /api/analytics/members/
{
  "membership_overview": {
    "total_members": 47,
    "monthly_revenue": 327.84,
    "membership_distribution": {
      "free": 35, "basic": 8, "professional": 3, "expert": 1
    }
  }
}

# Admin dashboard data
GET /api/admin/dashboard/
```

### **Stock Data APIs:**
```python
# Advanced filtering
GET /api/stocks/filter/?min_price=50&max_price=200&sector=technology

# Detailed company lookup
GET /api/stocks/lookup/AAPL/
{
  "basic_info": {"name": "Apple Inc.", "sector": "Technology"},
  "financial_data": {"pe_ratio": 25.4, "market_cap": 2800000000000},
  "technical_indicators": {"moving_avg_50": 145.67},
  "current_price": 150.25
}

# Live news for ticker
GET /api/news/?ticker=AAPL
```

### **Email & Membership APIs:**
```python
# Email signup with backend integration
POST /api/email-signup/
{
  "email": "user@example.com",
  "category": "technology"
}

# WordPress compatibility
POST /api/wordpress/subscribe/
```

---

## 🎨 **WORDPRESS DEVELOPMENT**

### **Plugin Structure:**
```
wordpress_plugin/stock-scanner-integration/
├── stock-scanner-integration.php     # Main plugin file
├── assets/
│   ├── stock-scanner-frontend.js     # Complete frontend integration
│   └── stock-scanner.css             # Plugin styles
└── templates/                        # Page templates
```

### **Theme Structure:**
```
wordpress_theme/stock-scanner-theme/
├── style.css                         # Professional modern design
├── functions.php                     # Theme functions
├── index.php                         # Main template
└── js/
    └── theme.js                      # Enhanced JavaScript
```

### **Live WordPress Features:**
- **24 Pages Created:** Home, Stock Scanner, Premium Plans, Market Analysis, etc.
- **Real-Time Widgets:** Live stock data from Django API
- **Email Forms:** Working backend integration
- **Advanced Filtering:** Stock search and filtering
- **News Display:** Live ticker news feeds
- **Analytics Dashboard:** WordPress admin widget with live data

---

## 💰 **MEMBERSHIP SYSTEM DEVELOPMENT**

### **Automatic Membership Creation:**
```python
# Django signals (stocks/signals.py)
@receiver(post_save, sender=User)
def create_user_membership(sender, instance, created, **kwargs):
    if created:
        Membership.objects.create(
            user=instance,
            tier='free',
            monthly_price=0.00,
            is_active=True
        )
```

### **Usage Limit Enforcement:**
```python
# Check if user can make API call
def can_make_lookup(user):
    membership = user.membership
    if membership.tier == 'expert':
        return True
    return membership.monthly_lookups_used < membership.tier_limits

# Increment usage counter
def increment_usage(user):
    membership = user.membership
    membership.monthly_lookups_used += 1
    membership.save()
```

### **Tier Management:**
```python
# Pricing structure
TIER_PRICING = {
    'free': 0.00,
    'basic': 9.99,
    'professional': 29.99,
    'expert': 49.99
}

# Usage limits
TIER_LIMITS = {
    'free': 15,
    'basic': 100,
    'professional': 500,
    'expert': -1  # unlimited
}
```

---

## 📊 **ANALYTICS DEVELOPMENT**

### **Real Data Calculations:**
```python
# analytics_views.py - Real database queries
def get_membership_stats():
    total_members = Membership.objects.filter(is_active=True).count()
    
    # Calculate revenue by tier
    monthly_revenue = 0.00
    for tier_code, price in TIER_PRICING.items():
        tier_count = Membership.objects.filter(tier=tier_code, is_active=True).count()
        monthly_revenue += tier_count * price
    
    # Average spending per person
    avg_spending = monthly_revenue / total_members if total_members > 0 else 0.00
    
    return {
        'total_members': total_members,
        'monthly_revenue': monthly_revenue,
        'avg_spending_per_person': avg_spending
    }
```

### **WordPress Admin Widget:**
```javascript
// WordPress dashboard widget with live data
function loadAnalytics() {
    $.ajax({
        url: 'https://api.retailtradescanner.com/api/analytics/public/',
        success: function(response) {
            $('.total-members').text(response.data.total_members);
            $('.monthly-revenue').text('$' + response.data.monthly_revenue);
            $('.avg-spending').text('$' + response.data.avg_spending_per_person);
        }
    });
}
```

---

## 💳 **SALES TAX DEVELOPMENT**

### **Tax Calculation System:**
```php
// WordPress plugin - PHP tax calculation
public function calculate_sales_tax($tax, $values, $order) {
    $country = $_SESSION['user_country'] ?? 'US';
    $state = $_SESSION['user_state'] ?? '';
    
    if ($country !== 'US') return 0;
    
    $subtotal = floatval($order->subtotal);
    $tax_rate = $this->get_tax_rate_for_state($state);
    
    return $subtotal * ($tax_rate / 100);
}

// State tax rates (all 50 states + DC)
private function get_tax_rate_for_state($state) {
    $tax_rates = [
        'CA' => 7.25, 'NY' => 4.00, 'TX' => 6.25,
        // ... all 50 states + DC
    ];
    return $tax_rates[$state] ?? 6.00; // Default 6%
}
```

### **IP Geolocation:**
```javascript
// Frontend tax detection
async function detectLocationAndShowTax() {
    try {
        const response = await fetch('http://ipapi.co/json/');
        const location = await response.json();
        if (location.country_code === 'US') {
            displayTaxInfo(location.region_code, location.region);
        }
    } catch (error) {
        // Silent failure - tax will use default rate
    }
}
```

---

## 🧪 **TESTING & DEBUGGING**

### **Test Membership System:**
```python
# Django shell testing
python manage.py shell

# Create test users and memberships
from django.contrib.auth.models import User
from stocks.models import Membership

user = User.objects.create_user('testuser', 'test@example.com', 'password')
# Membership automatically created via signals

# Test usage limits
membership = user.membership
print(membership.can_make_lookup())  # True
membership.monthly_lookups_used = 15  # Reach limit
print(membership.can_make_lookup())  # False for free tier
```

### **Test Analytics APIs:**
```bash
# Test public analytics
curl http://localhost:8000/api/analytics/public/

# Test admin analytics (need staff user)
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/analytics/members/

# Test stock filtering
curl "http://localhost:8000/api/stocks/filter/?min_price=50&max_price=200"
```

### **Debug WordPress Integration:**
```php
// WordPress debug mode
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);

// Check API connection in plugin
$response = wp_remote_get('http://localhost:8000/api/analytics/public/');
error_log('API Response: ' . print_r($response, true));
```

---

## 🚀 **DEPLOYMENT WORKFLOW**

### **Development → Staging → Production:**
```bash
# 1. Development (localhost)
python manage.py runserver
# Test all features locally

# 2. Staging (test server)
git push origin staging
# Deploy to staging server for final testing

# 3. Production (retailtradescanner.com)
git push origin master
# Deploy to production with:
# - PostgreSQL database
# - SSL certificates
# - Domain configuration
# - WordPress integration
```

### **Database Migrations:**
```bash
# Create migration for model changes
python manage.py makemigrations stocks

# Apply migrations
python manage.py migrate

# Setup memberships after deployment
python manage.py setup_memberships
```

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Database Optimization:**
```python
# Use select_related for membership queries
users_with_memberships = User.objects.select_related('membership').all()

# Index important fields
class Membership(models.Model):
    tier = models.CharField(max_length=20, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
```

### **API Caching:**
```python
# Cache analytics results
from django.core.cache import cache

def get_analytics_data():
    cache_key = 'analytics_data'
    data = cache.get(cache_key)
    if not data:
        data = calculate_analytics()
        cache.set(cache_key, data, 300)  # 5 minutes
    return data
```

---

## ✅ **DEVELOPMENT CHECKLIST**

### **Backend (Django):**
- [x] Real data analytics system
- [x] Membership model with 4 tiers
- [x] Usage limit enforcement
- [x] Sales tax calculation
- [x] Stock filtering APIs
- [x] Email subscription system
- [x] Admin dashboard integration

### **Frontend (WordPress):**
- [x] 24 professional pages
- [x] Live stock widgets
- [x] Email signup forms
- [x] Modern responsive design
- [x] Analytics admin widget
- [x] Stock filtering interface

### **Integration:**
- [x] Django-WordPress API connection
- [x] CORS configuration
- [x] Real-time data updates
- [x] Sales tax collection
- [x] Membership tier enforcement

Your development environment is fully configured for building and extending the Stock Scanner platform! 🚀
