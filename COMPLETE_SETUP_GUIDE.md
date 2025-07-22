# 🚀 Complete Setup Guide - Stock Scanner Platform

This is the **complete setup guide** for the Stock Scanner platform. This guide consolidates all setup documentation into one comprehensive resource covering development, production, and WordPress integration.

## 📋 **What You're Building**

A comprehensive stock monitoring and membership business platform featuring:
- **Django Backend**: REST APIs, 4-tier membership system, real-time analytics
- **WordPress Frontend**: 24 professional pages with live stock widgets  
- **Business Features**: Sales tax automation, revenue tracking, email marketing
- **Advanced Features**: Regulatory compliance, portfolio analytics, sentiment analysis

## 🎯 **Quick Start (5 Minutes)**

### Prerequisites
- Python 3.8+ installed
- Git installed
- Internet connection

### Automated Setup (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Run automated setup script
./startup.sh

# 3. Access your application
# Django Admin: http://localhost:8000/admin
# Analytics API: http://localhost:8000/api/analytics/public/
# Stock API: http://localhost:8000/api/stocks/
```

### Manual Setup
```bash
# 1. Clone and navigate
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your settings (optional for development)

# 5. Setup database
python manage.py migrate
python manage.py setup_memberships
python manage.py createsuperuser

# 6. Start the server
python manage.py runserver
```

## 🧪 **Verify Installation**

### Test Django Admin
- Visit: http://localhost:8000/admin
- Login with superuser credentials
- Check: Stocks → Memberships (should see user memberships)

### Test APIs
```bash
# Analytics API
curl http://localhost:8000/api/analytics/public/

# Stock Data API  
curl http://localhost:8000/api/stocks/

# Comprehensive test
python test_setup.py
```

## 🔧 **Configuration**

### Environment Variables (.env)
```bash
# Core Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,retailtradescanner.com

# Database
DATABASE_URL=sqlite:///stock_scanner.db

# Email Configuration (Gmail recommended)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# API Settings
API_RATE_LIMIT=60
CACHE_TIMEOUT=300
STOCK_API_RATE_LIMIT=1.0
```

### Gmail Setup for Email Notifications
1. Go to Google Account settings
2. Enable 2-Factor Authentication  
3. Generate an App Password
4. Use App Password in EMAIL_HOST_PASSWORD

## 🗄️ **Database Management**

### Development (SQLite)
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py setup_memberships
python manage.py createsuperuser
```

### Production (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE stockscanner_prod;
CREATE USER stockscanner_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE stockscanner_prod TO stockscanner_user;
\q

# Update .env
DATABASE_URL=postgresql://stockscanner_user:secure_password@localhost/stockscanner_prod

# Migrate
python manage.py migrate
python manage.py setup_memberships
```

## 🌐 **Production Deployment**

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 50GB SSD
- **CPU**: 2 cores minimum
- **Domain**: retailtradescanner.com (DNS configured)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget

# Install Node.js (for WordPress)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
sudo adduser stockscanner
sudo usermod -aG sudo stockscanner
```

### Step 2: Application Deployment
```bash
# Switch to application user
sudo su - stockscanner

# Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
# Edit .env with production settings

# Setup database
python manage.py migrate
python manage.py setup_memberships
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 3: Gunicorn Configuration
```bash
# Create Gunicorn socket
sudo nano /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```bash
# Create Gunicorn service
sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=stockscanner
Group=www-data
WorkingDirectory=/home/stockscanner/stock-scanner-complete
ExecStart=/home/stockscanner/stock-scanner-complete/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          stockscanner_django.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable services
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Step 4: Nginx Configuration
```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/retailtradescanner

server {
    listen 80;
    server_name retailtradescanner.com www.retailtradescanner.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/stockscanner/stock-scanner-complete;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    # WordPress location (if on same server)
    location / {
        try_files $uri $uri/ /index.php?$args;
        index index.php index.html;
        root /var/www/retailtradescanner;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/retailtradescanner /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d retailtradescanner.com -d www.retailtradescanner.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## 📱 **WordPress Integration**

### Step 1: WordPress Installation
```bash
# Download WordPress
cd /var/www
sudo wget https://wordpress.org/latest.tar.gz
sudo tar xzvf latest.tar.gz
sudo mv wordpress retailtradescanner
sudo chown -R www-data:www-data retailtradescanner
```

### Step 2: Install Plugin and Theme
```bash
# Copy plugin
sudo cp -r /home/stockscanner/stock-scanner-complete/wordpress_plugin/stock-scanner-integration/ /var/www/retailtradescanner/wp-content/plugins/

# Copy theme
sudo cp -r /home/stockscanner/stock-scanner-complete/wordpress_theme/stock-scanner-theme/ /var/www/retailtradescanner/wp-content/themes/

# Set permissions
sudo chown -R www-data:www-data /var/www/retailtradescanner/wp-content/
```

### Step 3: WordPress Configuration
1. **Complete WordPress setup** via web interface
2. **Activate plugin**: Plugins → Stock Scanner Integration → Activate
3. **Activate theme**: Appearance → Themes → Stock Scanner Theme → Activate
4. **Configure plugin**: 
   - Go to Stock Scanner Settings
   - Set Django API URL: `https://retailtradescanner.com/api/`
   - Test API connection
5. **Import pages**: Tools → Import → Upload XML file from project

### Step 4: Plugin Configuration
```bash
# WordPress plugin settings
Stock Scanner Settings:
- Django API URL: https://retailtradescanner.com/api/
- API Secret: (optional, for enhanced security)
- Cache Timeout: 300 seconds
- Max Stocks Per Widget: 10
```

## 💰 **Membership System**

### Tier Structure
| Tier | Price | Monthly Lookups | Features |
|------|-------|----------------|----------|
| **Free** | $0.00 | 15 | Basic stock data, email alerts |
| **Basic** | $9.99 | 100 | Advanced filtering, news feeds |
| **Professional** | $29.99 | 500 | Portfolio tracking, analytics |
| **Expert** | $49.99 | Unlimited | All features, priority support |

### Membership Management
```bash
# Create memberships for existing users
python manage.py setup_memberships

# View membership stats in Django admin
# http://localhost:8000/admin/stocks/membership/

# Check user membership in code
# user.membership.tier  # 'free', 'basic', 'professional', 'expert'
# user.membership.can_make_lookup()  # True/False
# user.membership.monthly_lookups_used  # Current usage
```

## 📊 **API Endpoints Reference**

### Analytics
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
# Returns detailed membership distribution and revenue data

# Admin dashboard data
GET /api/admin/dashboard/
```

### Stock Data
```bash
# List all stocks with pagination
GET /api/stocks/

# Get specific stock details
GET /api/stocks/AAPL/

# Advanced stock filtering
GET /api/stocks/filter/?min_price=50&max_price=200&sector=technology&min_volume=1000000

# Detailed stock lookup with financials
GET /api/stocks/lookup/AAPL/
{
  "basic_info": {...},
  "financial_data": {...},
  "technical_indicators": {...},
  "market_data": {...}
}

# Stock news for specific ticker
GET /api/news/?ticker=AAPL

# Market movers and statistics
GET /api/market-movers/
GET /api/stats/
```

### Email & Subscriptions
```bash
# Email signup
POST /api/email-signup/
{
  "email": "user@example.com",
  "category": "technology"
}

# WordPress subscription compatibility
POST /api/wordpress/subscribe/
```

## 🐛 **Troubleshooting**

### Common Development Issues

**ImportError or ModuleNotFoundError:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Database Errors:**
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py setup_memberships
```

**Permission Errors:**
```bash
# Make startup script executable
chmod +x startup.sh
```

**API Not Working:**
```bash
# Check Django server is running
python manage.py runserver
# Test with curl
curl http://localhost:8000/api/analytics/public/
```

### Production Issues

**Gunicorn not starting:**
```bash
# Check status
sudo systemctl status gunicorn

# Check logs
sudo journalctl -u gunicorn

# Restart service
sudo systemctl restart gunicorn
```

**Nginx errors:**
```bash
# Check Nginx status
sudo systemctl status nginx

# Check configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

**Database connection issues:**
```bash
# Test database connection
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database OK')"

# Check PostgreSQL status
sudo systemctl status postgresql
```

### WordPress Issues

**Plugin not working:**
1. Check WordPress error logs
2. Verify API URL in plugin settings
3. Test API endpoint manually with curl
4. Check CORS settings in Django

**Theme not displaying correctly:**
1. Clear WordPress cache
2. Check theme file permissions
3. Verify CSS/JS files are loading

## 📈 **Performance Optimization**

### Development
```bash
# Enable Django debug toolbar
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS += ['debug_toolbar']
```

### Production
```bash
# Enable Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Optimize database queries
python manage.py check --deploy
```

## 🔐 **Security Checklist**

### Django Security
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Set up proper database permissions
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets

### Server Security
- [ ] Configure firewall (ufw)
- [ ] Regular security updates
- [ ] SSH key authentication
- [ ] Fail2ban for brute force protection
- [ ] Regular backups
- [ ] Monitor logs

## 📚 **Advanced Features**

### Regulatory Compliance
- **GDPR Compliance**: Articles 17 & 20 implementation
- **Security Monitoring**: Threat detection and logging
- **Audit Logging**: Comprehensive user action tracking

### API Usage Analytics
- **Real-time Usage Tracking**: Monitor API performance
- **Usage Optimization**: Performance metrics and suggestions
- **Tier Analytics**: Track usage by membership tier

### Market Sentiment Analysis
- **Multi-source Sentiment Scoring**: Aggregate sentiment data
- **Confidence Levels**: Reliability scoring for sentiment data

### Portfolio Analytics
- **Risk Metrics**: Sharpe ratio, beta, VaR calculations
- **Performance Analysis**: Portfolio optimization suggestions
- **Rebalancing**: Automated rebalancing recommendations

## ✅ **Success Indicators**

You know everything is working when:

1. **Django Admin** loads and shows membership data
2. **Analytics API** returns real member statistics
3. **Stock APIs** return live stock data
4. **WordPress** displays with live widgets
5. **No errors** in logs or terminal
6. **SSL certificate** is properly configured
7. **Email system** sends notifications
8. **Payment system** processes test transactions

## 🎉 **Congratulations!**

Your Stock Scanner platform is now running with:
- ✅ **Complete membership business** with 4-tier pricing
- ✅ **Real-time stock data** and analytics
- ✅ **Professional WordPress frontend** with 24 pages
- ✅ **Production-ready infrastructure** with SSL and security
- ✅ **Business intelligence** with real revenue tracking
- ✅ **Email marketing system** for subscriber growth
- ✅ **Sales tax compliance** for US market

**🚀 You're ready to launch your stock scanning business!**

## 📞 **Support Resources**

- **Project Repository**: https://github.com/Toasterfire-come/stock-scanner-complete
- **Test Scripts**: `test_setup.py` for verification
- **Logs**: Check `logs/` directory for debugging
- **Django Admin**: Monitor system health and user activity

Need help? Run the verification script: `python test_setup.py` and check the logs for specific error messages.