# 🚀 Production Deployment Guide - Stock Scanner Platform

This is the **production deployment guide** for the Stock Scanner platform - a comprehensive stock monitoring and membership business platform for **retailtradescanner.com**.

## 📋 **What You're Deploying**

A complete production-ready business platform featuring:
- **Django Backend**: REST APIs, 4-tier membership system, real-time analytics
- **WordPress Frontend**: 24 professional pages with live stock widgets  
- **Business Features**: Sales tax automation, revenue tracking, email marketing
- **Advanced Features**: Regulatory compliance, portfolio analytics, sentiment analysis

## 🎯 **Production Server Requirements**

### **Server Specifications**
- **OS**: Ubuntu 20.04+ LTS or CentOS 8+
- **RAM**: 8GB minimum (16GB recommended for high traffic)
- **Storage**: 100GB SSD (50GB for application, 50GB for database/logs)
- **CPU**: 4 cores minimum (8 cores recommended)
- **Network**: Static IP address with domain pointing to server
- **Domain**: retailtradescanner.com (DNS properly configured)

### **Required Services**
- **Web Server**: Nginx (reverse proxy + static files)
- **Application Server**: Gunicorn (WSGI server for Django)
- **Database**: PostgreSQL 12+ (production database)
- **Cache**: Redis 6+ (session storage + API caching)
- **SSL**: Let's Encrypt (free SSL certificates)
- **Process Manager**: systemd (service management)

## 🚀 **Step-by-Step Production Deployment**

### **Step 1: Initial Server Setup**

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install essential packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget htop ufw

# 3. Install Node.js (for WordPress)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 4. Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# 5. Create application user
sudo adduser stockscanner --disabled-password --gecos ""
sudo usermod -aG sudo stockscanner
sudo usermod -aG www-data stockscanner
```

### **Step 2: PostgreSQL Database Setup**

```bash
# 1. Secure PostgreSQL installation
sudo -u postgres psql

# 2. Create production database (run in PostgreSQL shell)
CREATE DATABASE stockscanner_prod;
CREATE USER stockscanner_user WITH PASSWORD 'your_super_secure_password_here';
ALTER ROLE stockscanner_user SET client_encoding TO 'utf8';
ALTER ROLE stockscanner_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE stockscanner_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE stockscanner_prod TO stockscanner_user;
\q

# 3. Test database connection
psql -h localhost -U stockscanner_user -d stockscanner_prod
# (enter password when prompted, then \q to exit)
```

### **Step 3: Redis Cache Setup**

```bash
# 1. Configure Redis for production
sudo nano /etc/redis/redis.conf

# Update these settings:
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10

# 2. Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# 3. Test Redis
redis-cli ping
# Should return: PONG
```

### **Step 4: Application Deployment**

```bash
# 1. Switch to application user
sudo su - stockscanner

# 2. Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 3. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create production environment file
cp .env.example .env
```

### **Step 5: Production Environment Configuration**

Edit the `.env` file with production values:

```bash
nano .env
```

**Critical Production Environment Variables:**

```env
# ===== CORE DJANGO SETTINGS =====
SECRET_KEY=your_super_secret_production_key_here_minimum_50_characters
DEBUG=False
ALLOWED_HOSTS=retailtradescanner.com,www.retailtradescanner.com,api.retailtradescanner.com

# ===== DATABASE CONFIGURATION =====
DATABASE_URL=postgresql://stockscanner_user:your_super_secure_password_here@localhost:5432/stockscanner_prod

# ===== REDIS CACHE =====
REDIS_URL=redis://localhost:6379/0

# ===== EMAIL CONFIGURATION (PRODUCTION SMTP) =====
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@retailtradescanner.com
EMAIL_HOST_PASSWORD=your_gmail_app_password_here

# ===== API KEYS (PRODUCTION SEPARATED) =====
# Stock Market Data APIs
IEX_API_KEY=pk_live_your_production_iex_cloud_key
FINNHUB_API_KEY=your_production_finnhub_key
ALPHAVANTAGE_API_KEY=your_production_alphavantage_key
TWELVEDATA_API_KEY=your_production_twelvedata_key

# ===== PAYMENT PROCESSING =====
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# ===== PERFORMANCE SETTINGS =====
API_RATE_LIMIT=120
CACHE_TIMEOUT=600
MAX_STOCKS_PER_REQUEST=100
YFINANCE_RATE_LIMIT=0.5

# ===== SECURITY SETTINGS =====
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### **Step 6: API Keys Setup (Production)**

#### **6.1 Stock Market Data APIs**

**IEX Cloud (Primary) - Production Account:**
1. Go to https://iexcloud.io/pricing
2. Sign up for **Launch Plan** ($9/month for 100K requests)
3. Get your production API key: `pk_live_...`
4. Add to `.env`: `IEX_API_KEY=pk_live_your_production_key`

**Finnhub (Secondary) - Free Tier:**
1. Go to https://finnhub.io/register
2. Get free API key (60 calls/minute)
3. Add to `.env`: `FINNHUB_API_KEY=your_key`

**Alpha Vantage (Backup) - Free Tier:**
1. Go to https://www.alphavantage.co/support/#api-key
2. Get free API key (500 calls/day)
3. Add to `.env`: `ALPHAVANTAGE_API_KEY=your_key`

#### **6.2 Payment Processing**

**Stripe Production Setup:**
1. Go to https://dashboard.stripe.com/register
2. Complete business verification
3. Switch to **Live Mode**
4. Get production keys from https://dashboard.stripe.com/apikeys
5. Set up webhook endpoint: `https://retailtradescanner.com/api/stripe/webhook/`

#### **6.3 Email Service**

**Gmail Business Setup:**
1. Set up Gmail for Business or use existing Gmail
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use app password in `EMAIL_HOST_PASSWORD`

### **Step 7: Django Application Setup**

```bash
# 1. Still as stockscanner user, navigate to app directory
cd /home/stockscanner/stock-scanner-complete
source venv/bin/activate

# 2. Run database migrations
python manage.py migrate

# 3. Create production superuser
python manage.py createsuperuser
# Enter: admin username, email, secure password

# 4. Setup membership system
python manage.py setup_memberships

# 5. Collect static files for production
python manage.py collectstatic --noinput

# 6. Test Django setup
python manage.py check --deploy

# 7. Test database connection
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ Database connected')"
```

### **Step 8: Gunicorn WSGI Server Setup**

```bash
# 1. Test Gunicorn manually first
cd /home/stockscanner/stock-scanner-complete
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 stockscanner_django.wsgi:application

# If successful, stop with Ctrl+C and continue
```

**Create Gunicorn systemd service:**

```bash
# 1. Create Gunicorn socket file
sudo nano /etc/systemd/system/gunicorn.socket
```

**Add this content:**
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

```bash
# 2. Create Gunicorn service file
sudo nano /etc/systemd/system/gunicorn.service
```

**Add this content:**
```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=stockscanner
Group=www-data
WorkingDirectory=/home/stockscanner/stock-scanner-complete
Environment="PATH=/home/stockscanner/stock-scanner-complete/venv/bin"
ExecStart=/home/stockscanner/stock-scanner-complete/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          stockscanner_django.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# 3. Start and enable Gunicorn
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# 4. Check status
sudo systemctl status gunicorn.socket
sudo systemctl status gunicorn

# 5. Test socket activation
curl --unix-socket /run/gunicorn.sock localhost
```

### **Step 9: Nginx Web Server Configuration**

```bash
# 1. Create Nginx site configuration
sudo nano /etc/nginx/sites-available/retailtradescanner
```

**Add this content:**
```nginx
server {
    listen 80;
    server_name retailtradescanner.com www.retailtradescanner.com api.retailtradescanner.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Django static files
    location /static/ {
        root /home/stockscanner/stock-scanner-complete;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django media files
    location /media/ {
        root /home/stockscanner/stock-scanner-complete;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django admin
    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        client_max_body_size 50M;
    }

    # Django API endpoints
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        client_max_body_size 10M;
        
        # API rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # WordPress frontend (if on same server)
    location / {
        try_files $uri $uri/ /index.php?$args;
        index index.php index.html index.htm;
        root /var/www/retailtradescanner;
    }

    # PHP processing for WordPress
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        client_max_body_size 50M;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ ~$ {
        deny all;
    }

    # Rate limiting setup
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
}
```

```bash
# 2. Enable the site
sudo ln -s /etc/nginx/sites-available/retailtradescanner /etc/nginx/sites-enabled/

# 3. Remove default site
sudo rm /etc/nginx/sites-enabled/default

# 4. Test Nginx configuration
sudo nginx -t

# 5. Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# 6. Check status
sudo systemctl status nginx
```
### **Step 10: SSL Certificate Setup (Let's Encrypt)**

```bash
# 1. Install Certbot
sudo apt install certbot python3-certbot-nginx

# 2. Obtain SSL certificates
sudo certbot --nginx -d retailtradescanner.com -d www.retailtradescanner.com -d api.retailtradescanner.com

# 3. Test automatic renewal
sudo certbot renew --dry-run

# 4. Set up automatic renewal (already configured, but verify)
sudo systemctl status certbot.timer

# 5. Check SSL configuration
curl -I https://retailtradescanner.com
```

### **Step 11: WordPress Installation & Integration**

```bash
# 1. Install PHP and required extensions
sudo apt install php8.1-fpm php8.1-mysql php8.1-curl php8.1-gd php8.1-intl php8.1-mbstring php8.1-soap php8.1-xml php8.1-xmlrpc php8.1-zip

# 2. Create WordPress directory
sudo mkdir -p /var/www/retailtradescanner
cd /var/www

# 3. Download and extract WordPress
sudo wget https://wordpress.org/latest.tar.gz
sudo tar xzf latest.tar.gz
sudo mv wordpress/* retailtradescanner/
sudo rm -rf wordpress latest.tar.gz

# 4. Set proper permissions
sudo chown -R www-data:www-data /var/www/retailtradescanner
sudo chmod -R 755 /var/www/retailtradescanner

# 5. Install Stock Scanner WordPress plugin
sudo cp -r /home/stockscanner/stock-scanner-complete/wordpress_plugin/stock-scanner-integration/ /var/www/retailtradescanner/wp-content/plugins/

# 6. Install Stock Scanner theme
sudo cp -r /home/stockscanner/stock-scanner-complete/wordpress_theme/stock-scanner-theme/ /var/www/retailtradescanner/wp-content/themes/

# 7. Set permissions for plugin and theme
sudo chown -R www-data:www-data /var/www/retailtradescanner/wp-content/
```

### **Step 12: WordPress Configuration**

1. **Complete WordPress Setup:**
   - Visit: https://retailtradescanner.com
   - Follow WordPress installation wizard
   - Create admin user and database connection

2. **Configure Stock Scanner Plugin:**
   - Go to WordPress Admin → Plugins
   - Activate "Stock Scanner Integration"
   - Go to Settings → Stock Scanner Settings
   - Configure:
     ```
     Django API URL: https://api.retailtradescanner.com/api/
     API Secret: (optional for security)
     Cache Timeout: 600 seconds
     Max Stocks Per Widget: 20
     ```

3. **Activate Theme:**
   - Go to Appearance → Themes
   - Activate "Stock Scanner Theme"

4. **Import Pages:**
   - Go to Tools → Import
   - Upload: `retailtradescanner.WordPress.2025-07-22.xml`
   - Import all 24 pages

### **Step 13: Final Production Testing**

```bash
# 1. Test Django API endpoints
curl https://api.retailtradescanner.com/api/analytics/public/
curl https://api.retailtradescanner.com/api/stocks/

# 2. Test WordPress frontend
curl -I https://retailtradescanner.com

# 3. Test Django admin
curl -I https://retailtradescanner.com/admin/

# 4. Check all services are running
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status postgresql
sudo systemctl status redis-server

# 5. Check SSL grades
curl -I https://retailtradescanner.com | grep "HTTP/"

# 6. Test database connectivity
cd /home/stockscanner/stock-scanner-complete
source venv/bin/activate
python manage.py shell -c "
from stocks.models import Membership, StockAlert
from django.contrib.auth.models import User
print(f'Users: {User.objects.count()}')
print(f'Memberships: {Membership.objects.count()}')
print(f'Stocks: {StockAlert.objects.count()}')
print('✅ Production database operational')
"
```

## 🎯 **Production Monitoring & Maintenance**

### **Daily Monitoring Commands**

```bash
# Check service status
sudo systemctl status nginx gunicorn postgresql redis-server

# Check disk space
df -h

# Check memory usage
free -h

# Check latest logs
sudo journalctl -u gunicorn --since today
sudo tail -f /var/log/nginx/access.log

# Check SSL certificate expiry
sudo certbot certificates
```

### **Performance Optimization**

```bash
# 1. Enable Nginx compression
sudo nano /etc/nginx/nginx.conf
# Add in http block:
# gzip on;
# gzip_vary on;
# gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

# 2. Configure PostgreSQL for production
sudo nano /etc/postgresql/12/main/postgresql.conf
# Adjust: shared_buffers, effective_cache_size, maintenance_work_mem

# 3. Configure Redis memory policy
sudo nano /etc/redis/redis.conf
# Set: maxmemory-policy allkeys-lru
```

## 🎉 **Production Deployment Complete!**

Your Stock Scanner platform is now fully deployed and production-ready with:

### **✅ What's Now Live:**
- **🌐 Frontend**: https://retailtradescanner.com (WordPress with 24 pages)
- **⚙️ Backend API**: https://api.retailtradescanner.com/api/
- **👨‍💼 Admin Panel**: https://retailtradescanner.com/admin/
- **📊 Analytics**: https://api.retailtradescanner.com/api/analytics/public/
- **🔒 SSL Security**: A+ grade SSL certificates
- **💾 Database**: PostgreSQL with Redis caching
- **📈 Performance**: Nginx + Gunicorn production stack

### **✅ Business Features Active:**
- **4-Tier Membership System**: $0, $9.99, $29.99, $49.99/month
- **Real-Time Stock Data**: Live market prices and analytics
- **Payment Processing**: Stripe integration ready
- **Email Marketing**: Automated subscriber management
- **Sales Tax**: Automatic calculation for all US states
- **WordPress Integration**: 24 professional pages with live widgets

### **💼 Monthly Operating Costs:**
- **Server Hosting**: $20-50/month (DigitalOcean/Linode)
- **IEX Cloud API**: $9/month (100K requests)
- **SSL Certificates**: $0/month (Let's Encrypt)
- **Domain**: $12/year
- **Total**: ~$30-60/month for complete operation

### **📈 Revenue Potential:**
- **100 Basic Members**: $999/month revenue
- **50 Professional**: $1,499/month revenue  
- **10 Expert**: $499/month revenue
- **Total Potential**: $2,997/month from just 160 members

**ROI**: 5,000%+ return on $60/month operating costs

## 🚀 **Your Stock Scanning Business is Live!**

**Next Steps:**
1. **Marketing**: Drive traffic to retailtradescanner.com
2. **Content**: Publish stock analysis and market insights
3. **SEO**: Optimize for stock trading keywords
4. **Social Media**: Build trading community presence
5. **Email Campaigns**: Convert visitors to paid members

**Support Resources:**
- Monitor logs: `sudo journalctl -u gunicorn --since today`
- Check performance: `sudo systemctl status nginx gunicorn postgresql redis-server`
- Update stocks: `python manage.py update_stocks --popular`
- Backup database: `pg_dump stockscanner_prod > backup.sql`

**Ready to generate revenue from day one!** 💰

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