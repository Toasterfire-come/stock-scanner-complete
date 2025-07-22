# 📊 Stock Scanner - Complete Business Platform

A comprehensive stock monitoring and membership platform for **retailtradescanner.com** featuring real-time analytics, 4-tier membership system, automatic sales tax collection, and full WordPress integration with 24 professional pages.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Run automated setup
./startup.sh

# 3. Access your application
# Django Admin: http://localhost:8000/admin
# Analytics API: http://localhost:8000/api/analytics/public/
# Stock Data: http://localhost:8000/api/stocks/
```

**For detailed setup instructions, see: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)**

## ✨ Features

### 💰 **Membership System (NEW)**
- **4-Tier Pricing:** Free (15 lookups), Basic ($9.99), Professional ($29.99), Expert ($49.99)
- **Real-time Analytics:** Live member counts, revenue tracking, spending averages
- **Usage Limits:** Automatic enforcement per tier with monthly resets
- **Stripe Integration:** Ready for payment processing with customer tracking
- **Auto-Signup:** New users automatically get free memberships

### 📊 **Real Data Analytics (NEW)**
- **Live Business Intelligence:** Real member counts and revenue calculations
- **Dynamic Statistics:** No fake data - everything calculated from database
- **Admin Dashboard:** WordPress widget showing live analytics
- **Growth Tracking:** Real conversion rates and tier adoption metrics
- **API Endpoints:** `/api/analytics/public/` and `/api/analytics/members/`

### 💳 **Sales Tax System (NEW)**
- **Automatic Collection:** All 50 US states + DC tax rates
- **IP Geolocation:** Detects user location for accurate tax calculation
- **Paid Membership Pro Integration:** Seamless checkout experience
- **Expert Tier:** $49.99/month with automatic tax calculation

### 🖥️ **WordPress Integration (COMPLETE)**
- **24 Professional Pages:** Complete site structure from XML import
- **Live Stock Widgets:** Real-time data from Django backend
- **Modern Design:** Professional CSS with responsive layout
- **Email Signups:** Working backend integration
- **Stock Filtering:** Advanced search and filtering capabilities
- **News Display:** Real-time stock news and important updates

### 📈 **Stock Data & APIs**
- **Real-time stock prices** via yfinance API with rate limiting
- **Advanced Filtering:** Filter by price, volume, market cap, sector
- **Stock Lookup:** Complete company data and financials
- **Market News:** Live news feeds for specific tickers
- **Technical Indicators:** DVAV, DVSA, PE ratios, market cap

### 🗄️ **Database & Models**
- **Membership Model:** Complete user tier tracking with Stripe integration
- **Usage Tracking:** Monthly lookup limits and reset functionality
- **Email Subscriptions:** Category-based with active status tracking
- **Stock Alerts:** Company data with price and volume monitoring
- **SQLite:** Local development database, easily migrated to PostgreSQL

### 🔐 **Security & Production**
- **Domain Ready:** Configured for retailtradescanner.com
- **CORS Setup:** WordPress-Django communication enabled
- **Rate Limiting:** API protection and usage enforcement
- **Sales Tax Compliance:** Automatic collection for US customers
- **Admin Security:** Staff-only access to sensitive analytics

## 📋 System Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **Internet connection** (for stock data)
- **Git** (for cloning repository)
- **Gmail account** (optional, for email notifications)

## 📁 Project Structure

```
stock-scanner-complete/
├── 📄 README.md                          # This file - project overview
├── 📄 requirements.txt                   # Python dependencies (production-ready)
├── 📄 manage.py                          # Django management script
├── 📄 startup.sh                         # Automated setup script
├── 📄 .env.example                       # Environment variables template
├── 📄 QUICK_START_GUIDE.md              # 5-minute setup guide
├── 📄 PRODUCTION_DEPLOYMENT_GUIDE.md    # Complete production deployment
├── 📄 DEVELOPMENT_GUIDE.md              # Development documentation
├── 📄 REAL_DATA_ANALYTICS.md            # Real data analytics system
├── 📄 COMPLETE_SITEMAP.md               # Full site structure (24 pages)
├── 📄 WORDPRESS_DJANGO_CONNECTION.md    # Technical integration guide
├── 📁 stockscanner_django/              # Django project
│   ├── 📄 settings.py                   # Configured for retailtradescanner.com
│   ├── 📄 urls.py                       # URL routing with analytics endpoints
│   ├── 📄 celery.py                     # Celery task queue configuration
│   └── 📄 wsgi.py                       # WSGI configuration
├── 📁 stocks/                           # Stock data & membership app
│   ├── 📄 models.py                     # StockAlert + Membership models
│   ├── 📄 api_views.py                  # Stock APIs with filtering & lookup
│   ├── 📄 analytics_views.py            # 🆕 Real data analytics APIs
│   ├── 📄 admin_dashboard.py            # 🆕 Admin dashboard with live data
│   ├── 📄 admin.py                      # Updated with Membership admin
│   ├── 📄 signals.py                    # 🆕 Auto-create memberships for new users
│   └── 📁 management/commands/          # Django commands
│       └── 📄 setup_memberships.py     # 🆕 Setup memberships for existing users
├── 📁 emails/                          # Email subscription system
│   ├── 📄 models.py                     # EmailSubscription model
│   └── 📄 email_config.py              # Gmail SMTP configuration
├── 📁 core/                            # Core functionality
│   └── 📄 views.py                     # Basic web views
├── 📁 wordpress_plugin/                # Complete WordPress integration
│   └── 📁 stock-scanner-integration/   # Full plugin with 24 pages
│       ├── 📄 stock-scanner-integration.php  # 🆕 With sales tax & analytics widget
│       └── 📁 assets/
│           └── 📄 stock-scanner-frontend.js  # 🆕 Complete frontend integration
├── 📁 wordpress_theme/                 # Professional WordPress theme
│   └── 📁 stock-scanner-theme/         
│       ├── 📄 style.css                # 🆕 Professional modern design
│       ├── 📄 functions.php            # Updated navigation
│       └── 📁 js/theme.js              # Enhanced JavaScript
├── 📁 docs/                           # Documentation
│   └── 📄 SALES_TAX_SETUP.md          # 🆕 Sales tax system guide
├── 📁 tests/                          # Test files
├── 📁 logs_archive/                   # Archived logs
└── 📄 retailtradescanner.WordPress.2025-07-22.xml  # Updated WordPress export (19 pages)
```

## 🛠️ Installation & Setup

### 🚀 Development Setup (Recommended)

**Quick Setup:**
```bash
# Clone and run automated setup
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
./startup.sh
```

**Manual Setup:**
```bash
# 1. Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your settings

# 5. Setup database
python manage.py migrate
python manage.py setup_memberships
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

### 🌐 Production Deployment

**For complete production deployment instructions, see:**
- **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Complete production setup
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Quick development setup

**Production highlights:**
- PostgreSQL database configuration
- Nginx reverse proxy with SSL
- Gunicorn application server
- Redis caching
- Automated SSL certificates
- System service configuration

### 🔧 WordPress Plugin Setup

```bash
# 1. Copy plugin to WordPress
cp -r wordpress_plugin/stock-scanner-integration/ /path/to/wordpress/wp-content/plugins/

# 2. Copy theme to WordPress  
cp -r wordpress_theme/stock-scanner-theme/ /path/to/wordpress/wp-content/themes/

# 3. Activate in WordPress admin
# Go to Plugins > Activate "Stock Scanner Integration"
# Go to Appearance > Themes > Activate "Stock Scanner Theme"

# 4. Configure plugin settings
# Go to WordPress Admin > Stock Scanner Settings
# Set Django API URL (e.g., https://api.retailtradescanner.com)
# Test API connection

```

## 🌐 API Endpoints

### 📊 Analytics APIs (NEW)

```bash
# Public analytics (for website display)
GET /api/analytics/public/
{
  "total_members": 47,
  "avg_spending_per_person": 6.97,
  "monthly_revenue": 327.84,
  "email_subscribers": 25,
  "stocks_tracked": 150
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

### 📈 Stock Data APIs

```bash
# List all stocks with pagination
GET /api/stocks/

# Get specific stock details
GET /api/stocks/AAPL/

# Advanced stock filtering (NEW)
GET /api/stocks/filter/?min_price=50&max_price=200&sector=technology&min_volume=1000000

# Detailed stock lookup with financials (NEW)
GET /api/stocks/lookup/AAPL/
{
  "basic_info": {...},
  "financial_data": {...},
  "technical_indicators": {...},
  "market_data": {...}
}

# Stock news for specific ticker (NEW)
GET /api/news/?ticker=AAPL

# Market movers and statistics
GET /api/market-movers/
GET /api/stats/
```

### 📧 Email & Subscriptions

```bash
# Email signup (NEW)
POST /api/email-signup/
{
  "email": "user@example.com",
  "category": "technology"
}

# WordPress subscription compatibility
POST /api/wordpress/subscribe/
```

## 💰 Membership System

### 🎯 Tier Structure

| Tier | Price | Monthly Lookups | Features |
|------|-------|----------------|----------|
| **Free** | $0.00 | 15 | Basic stock data, email alerts |
| **Basic** | $9.99 | 100 | Advanced filtering, news feeds |
| **Professional** | $29.99 | 500 | Portfolio tracking, analytics |
| **Expert** | $49.99 | Unlimited | All features, priority support |

### 🔧 Membership Management

```bash
# Create memberships for existing users
python manage.py setup_memberships

# View membership stats in Django admin
http://localhost:8000/admin/stocks/membership/

# Check user membership in code
user.membership.tier  # 'free', 'basic', 'professional', 'expert'
user.membership.can_make_lookup()  # True/False
user.membership.monthly_lookups_used  # Current usage
```

## 🎨 WordPress Integration

### 📱 24 Complete Pages Created

1. **Home** - Landing page with live stock widgets
2. **About Us** - Company information and team
3. **Stock Scanner** - Main scanning interface
4. **Premium Plans** - Membership tiers and pricing
5. **Stock Alerts** - Real-time alert management
6. **Market Analysis** - Professional analysis tools
7. **Portfolio Tracker** - Investment portfolio management
8. **News & Insights** - Market news and insights
9. **Educational Resources** - Trading education center
10. **Watchlist** - Personal stock watchlists
11. **Technical Analysis** - Advanced charting tools
12. **Fundamentals** - Company fundamental analysis
13. **Screener** - Stock screening tools
14. **Research** - Investment research platform
15. **Earnings Calendar** - Upcoming earnings tracker
16. **Dividend Tracker** - Dividend analysis tools
17. **Options** - Options trading resources
18. **Forex** - Foreign exchange tools
19. **Crypto** - Cryptocurrency tracking
20. **Contact** - Contact form and support
21. **FAQ** - Frequently asked questions
22. **Privacy Policy** - Privacy and data policy
23. **Terms of Service** - Terms and conditions
24. **Member Dashboard** - User account management

### 🔧 Live Features

- **Real-time Stock Data** from Django backend
- **Email Signup Forms** with backend integration
- **Advanced Stock Filtering** and search
- **Live News Feeds** for specific tickers
- **Professional CSS Design** with responsive layout
- **Analytics Dashboard** in WordPress admin
curl "http://localhost:8000/api/stocks/search/?q=apple"
```

### Market Data
```bash
# Market movers
curl "http://localhost:8000/api/market-movers/"

# Market statistics
curl "http://localhost:8000/api/stats/"
```

## 🔧 Configuration Files

### Environment Variables (`.env`)
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database (SQLite)
DB_NAME=stock_scanner.db

# Email (Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stock API
STOCK_API_RATE_LIMIT=1.0
```

### Database Settings (`database_settings_local.py`)
- SQLite configuration
- Performance optimizations
- Backup utilities
- Health monitoring

### Email Settings (`emails/email_config.py`)
- Gmail SMTP configuration
- Rate limiting for email sending
- Template management
- Queue processing

## 🐛 Troubleshooting

### Common Issues

#### Database Issues
```bash
# Test database
python3 test_database_setup.py

# Reset database
rm stock_scanner.db
python manage.py migrate
```

#### Email Issues
```bash
# Test email configuration
python3 -c "from emails.email_config import test_email_connection; print(test_email_connection())"
```

#### Stock Data Issues
```bash
# Test yfinance connection
python3 -c "from stocks.yfinance_config import test_yfinance_connection; print(test_yfinance_connection())"
```

## 📚 Documentation

- **[Complete Setup Guide](COMPLETE_SETUP_GUIDE.md)** - Detailed installation instructions
- **[Security Configuration](security_hardening.py)** - Production security settings
- **[Database Management](database_settings_local.py)** - SQLite utilities
- **[Email Configuration](emails/email_config.py)** - Gmail SMTP setup

## 🎯 Key Features in Detail

### Stock Data Management
- **Automatic fetching** from Yahoo Finance
- **Rate limiting** to prevent API blocking
- **Caching** for improved performance
- **Error handling** and retry logic

### Email System
- **Gmail SMTP** with app password security
- **Bulk email processing** with queues
- **Template-based** HTML and text emails
- **Subscription management** by category

### WordPress Integration
The plugin automatically creates pages from your XML export:

**Main Trading Pages:**
- Premium Plans - Gold/Silver/Free plan comparison with live stock widgets
- Email Stock Lists - Subscribe to stock alert lists
- All Stock Alerts - Complete collection of stock lists
- Popular Stock Lists - Most subscribed lists
- Stock Search - Advanced stock search tools
- Personalized Stock Finder - AI-powered recommendations
- News Scrapper - Financial news aggregation
- Filter and Scrapper Pages - Advanced filtering tools

**Membership & Account Pages:**
- Membership Account - User account management
- Membership Billing - Payment and billing history
- Membership Cancel - Subscription cancellation
- Membership Checkout - Purchase process
- Membership Confirmation - Purchase confirmation
- Membership Orders - Order history
- Membership Levels - Plan comparison
- Login - User authentication
- Your Profile - User profile management

**Legal Pages:**
- Terms and Conditions
- Privacy Policy

**Additional Features:**
- Stock widgets on every page with live data
- Responsive design matching your brand
- Membership paywall integration
- Navigation menu with all pages

### Database
- **SQLite** for simplicity and portability
- **Automatic backups** before major operations
- **Performance optimization** with indexes
- **Health monitoring** and maintenance tools

### Security
- **Production-ready** Django settings
- **CSRF protection** and security headers
- **Rate limiting** on API endpoints
- **Custom middleware** for additional protection

## 🚀 Production Deployment

### Security Hardening
```bash
# Generate production configuration
python3 security_hardening.py

# Review generated files:
# - production_settings.py
# - .env (with secure defaults)
# - deploy_secure.sh
```

### Deployment Script
```bash
# Automated deployment with:
./deploy_secure.sh

# Includes:
# - System package installation
# - Virtual environment setup
# - Database initialization
# - Nginx configuration
# - SSL certificate setup
# - Firewall configuration
```

## 🤝 Contributing

This is a complete, ready-to-use stock scanning application. Feel free to:

1. **Fork** the project
2. **Add features** or improvements
3. **Test thoroughly** using the provided test scripts
4. **Update documentation** as needed

## 📄 License

This project is provided as-is for educational and commercial use. 

## 🆘 Support

For setup issues:

1. **Read** the [Complete Setup Guide](COMPLETE_SETUP_GUIDE.md)
2. **Run** the diagnostic script: `python3 test_database_setup.py`
3. **Check** the troubleshooting section above
4. **Verify** your `.env` configuration

---

**Built with ❤️ using Django, SQLite, and yfinance**

*Ready to monitor stocks like a pro!* 📈✨