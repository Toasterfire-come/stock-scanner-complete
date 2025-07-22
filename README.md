# 📊 Stock Scanner - Django Application

A powerful, real-time stock monitoring and analysis application built with Django, featuring Gmail SMTP integration, local SQLite database, and WordPress API compatibility.

## 🚀 Quick Start

```bash
# 1. Download and extract the project
# 2. Run the automated setup
python3 setup_local.py

# 3. Start the application
source venv/bin/activate
python manage.py runserver

# 4. Visit http://localhost:8000
```

## ✨ Features

### 📈 **Stock Data**
- **Real-time stock prices** via yfinance API
- **Market movers** and statistics
- **Technical indicators** (DVAV, DVSA, PE ratios)
- **Rate-limited requests** to prevent blocking
- **Caching system** for better performance

### 📧 **Email Notifications**
- **Gmail SMTP integration** with app passwords
- **Automated stock alerts** based on price changes
- **Category-based subscriptions** (technology, healthcare, etc.)
- **Rate limiting** to respect Gmail quotas

### 🗄️ **Database**
- **Local SQLite database** - no passwords required
- **Automatic backups** with timestamps
- **Health monitoring** and optimization
- **Django ORM** for easy data management

### 🌐 **API & Integration**
- **REST API** for external integrations
- **WordPress compatibility** with CORS support
- **JSON data export** for filtering systems
- **Admin dashboard** for management

### 🔐 **Security**
- **Production-ready security** settings
- **HTTPS enforcement** for production
- **Rate limiting** and monitoring
- **Custom security middleware**

## 📋 System Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **Internet connection** (for stock data)
- **Gmail account** (for email notifications)

## 📁 Project Structure

```
stock-scanner/
├── 📄 README.md                          # This file
├── 📄 COMPLETE_SETUP_GUIDE.md           # Detailed setup instructions
├── 📄 requirements_secure.txt            # Python dependencies
├── 📄 manage.py                          # Django management script
├── 🔧 setup_local.py                     # Automated setup script
├── 🧪 test_database_setup.py            # Database test script
├── 🗄️ database_settings_local.py        # SQLite configuration
├── 🔐 security_hardening.py             # Security configuration
├── 📁 stockscanner_django/              # Django project
│   ├── 📄 settings.py                   # Django settings
│   ├── 📄 urls.py                       # URL routing
│   └── 📄 wsgi.py                       # WSGI configuration
├── 📁 stocks/                           # Stock data app
│   ├── 📄 models.py                     # Database models
│   ├── 📄 api_views.py                  # REST API views
│   ├── 📄 yfinance_config.py           # Stock data configuration
│   └── 📁 management/commands/          # Django commands
├── 📁 emails/                          # Email system
│   ├── 📄 models.py                     # Email models
│   ├── 📄 email_config.py              # Gmail SMTP configuration
│   ├── 📄 tasks.py                     # Email tasks
│   └── 📁 templates/                   # Email templates
├── 📁 core/                            # Core functionality
│   ├── 📄 views.py                     # Web views
│   └── 📁 templates/                   # HTML templates
├── 📁 wordpress_plugin/                # WordPress plugin (auto-creates pages)
│   └── 📁 stock-scanner-integration/   # Complete plugin with paywall
├── 📁 wordpress_theme/                 # WordPress theme
│   └── 📁 stock-scanner-theme/         # Modern responsive theme
├── 📄 retailtradescanner.WordPress.2025-07-22.xml  # WordPress content export
└── 📁 static/                          # Static files (CSS, JS, images)
```

## 🛠️ Installation Options

### 🚀 Complete WordPress Installation (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
git checkout complete-stock-scanner-v1

# 2. One-command Django setup
python3 setup_local.py

# 3. WordPress Integration
# Copy wordpress_plugin/stock-scanner-integration/ to /wp-content/plugins/
# Copy wordpress_theme/stock-scanner-theme/ to /wp-content/themes/
# Activate both in WordPress admin

# 4. Your complete stock scanner is ready!
# Django API: http://localhost:8000
# WordPress: http://your-site.com
```

### Option 2: Django Only (Manual Setup)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Option 3: Production Deployment
```bash
# Run security hardening
python3 security_hardening.py

# Deploy with generated script
./deploy_secure.sh
```

## 📧 Gmail Configuration

1. **Enable 2-Factor Authentication** in your Google account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → App passwords
   - Generate password for "Mail" application
3. **Update .env file** with your Gmail credentials

## 🌐 API Usage

### Get Stock Data
```bash
# List all stocks
curl "http://localhost:8000/api/stocks/"

# Get specific stock
curl "http://localhost:8000/api/stocks/AAPL/"

# Search stocks
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