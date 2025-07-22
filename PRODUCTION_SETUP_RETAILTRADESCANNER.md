# 🚀 Production Setup Guide for retailtradescanner.com

## 📋 **Complete Platform Deployment**

This guide provides step-by-step instructions for deploying the complete Stock Scanner platform to **retailtradescanner.com** including:
- **Real Data Analytics System** with live member tracking
- **4-Tier Membership System** (Free, Basic, Professional, Expert)  
- **Automatic Sales Tax Collection** for all US states
- **24 WordPress Pages** with professional design
- **Django Backend** with full REST API integration

---

## ✨ **PLATFORM FEATURES OVERVIEW**

### 💰 **Membership & Revenue System:**
- **Real-Time Analytics:** Live member counts and revenue calculations
- **4 Pricing Tiers:** $0 (Free), $9.99 (Basic), $29.99 (Professional), $49.99 (Expert)
- **Usage Limits:** 15, 100, 500, unlimited API calls per month
- **Automatic Signup:** New users get free memberships via Django signals
- **Stripe Ready:** Customer and subscription tracking integrated

### 💳 **Sales Tax Collection:**
- **Automatic Detection:** IP geolocation for user's state
- **All US States:** 50 states + DC tax rates configured
- **PMP Integration:** Works with Paid Membership Pro checkout
- **Expert Tier:** $49.99 + applicable state tax

### 🖥️ **WordPress Integration:**
- **24 Professional Pages:** Complete site structure
- **Live Widgets:** Real-time stock data from Django
- **Email Signups:** Backend integration working  
- **Stock Filtering:** Advanced search capabilities
- **Modern Design:** Professional responsive CSS
- **Admin Dashboard:** Analytics widget with live data

---

## 🌐 **Domain Architecture**

```
┌─────────────────────────────────┐
│     retailtradescanner.com      │
│    (WordPress Frontend)         │
│                                 │
│  ┌─────────────────────────────┐│
│  │ WordPress Pages (24 total) ││
│  │ • Premium Plans             ││
│  │ • Email Stock Lists         ││
│  │ • Stock Search              ││
│  │ • News Scrapper             ││
│  │ • Membership Pages          ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
            ▼ API Calls
┌─────────────────────────────────┐
│   api.retailtradescanner.com    │
│    (Django Backend API)         │
│                                 │
│  ┌─────────────────────────────┐│
│  │ REST API Endpoints          ││
│  │ • /api/email-signup/        ││
│  │ • /api/stocks/filter/       ││
│  │ • /api/stocks/lookup/       ││
│  │ • /api/news/                ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## 🔧 **1. Domain Configuration**

### **DNS Settings:**
```
# A Records
retailtradescanner.com        → [WordPress Server IP]
www.retailtradescanner.com    → [WordPress Server IP]
api.retailtradescanner.com    → [Django Server IP]

# CNAME (Alternative)
www.retailtradescanner.com    → retailtradescanner.com
api.retailtradescanner.com    → retailtradescanner.com (if same server)
```

### **SSL Certificates:**
```bash
# Using Let's Encrypt (recommended)
certbot --apache -d retailtradescanner.com -d www.retailtradescanner.com -d api.retailtradescanner.com

# Or using Cloudflare SSL (if using Cloudflare)
# Configure Full SSL mode in Cloudflare dashboard
```

---

## 🐍 **2. Django Backend Configuration**

### **Update Django Settings:**
**File:** `stockscanner_django/settings.py`

```python
# Production settings
DEBUG = False

ALLOWED_HOSTS = [
    'api.retailtradescanner.com',
    'retailtradescanner.com',
    'www.retailtradescanner.com',
    '127.0.0.1',
    'localhost'
]

# CORS Configuration for retailtradescanner.com
CORS_ALLOWED_ORIGINS = [
    "https://retailtradescanner.com",
    "https://www.retailtradescanner.com",
    "http://retailtradescanner.com",  # For development/testing
    "http://www.retailtradescanner.com",
]

CORS_ALLOW_CREDENTIALS = True

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database configuration (production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Or MySQL
        'NAME': 'retailtradescanner_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files (production)
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/api.retailtradescanner.com/static/'
```

### **Django Deployment Commands:**
```bash
# Navigate to Django project
cd /path/to/stock-scanner-complete

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Test Django server
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 **3. Web Server Configuration**

### **Apache Virtual Host (Django API):**
**File:** `/etc/apache2/sites-available/api.retailtradescanner.com.conf`

```apache
<VirtualHost *:80>
    ServerName api.retailtradescanner.com
    Redirect permanent / https://api.retailtradescanner.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName api.retailtradescanner.com
    DocumentRoot /var/www/api.retailtradescanner.com
    
    WSGIDaemonProcess retailtradescanner python-path=/path/to/stock-scanner-complete
    WSGIProcessGroup retailtradescanner
    WSGIScriptAlias / /path/to/stock-scanner-complete/stockscanner_django/wsgi.py
    
    <Directory /path/to/stock-scanner-complete/stockscanner_django>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    Alias /static /var/www/api.retailtradescanner.com/static
    <Directory /var/www/api.retailtradescanner.com/static>
        Require all granted
    </Directory>
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/api.retailtradescanner.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/api.retailtradescanner.com/privkey.pem
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains"
</VirtualHost>
```

### **Nginx Configuration (Alternative):**
**File:** `/etc/nginx/sites-available/api.retailtradescanner.com`

```nginx
server {
    listen 80;
    server_name api.retailtradescanner.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.retailtradescanner.com;
    
    ssl_certificate /etc/letsencrypt/live/api.retailtradescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.retailtradescanner.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/api.retailtradescanner.com/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 📱 **4. WordPress Configuration**

### **WordPress Plugin Configuration:**
**File:** WordPress Admin → Settings → Stock Scanner Integration

```php
// Set these options in WordPress admin or wp-config.php
define('STOCK_SCANNER_API_URL', 'https://api.retailtradescanner.com/api/');
define('STOCK_SCANNER_API_SECRET', 'your-production-secret-key');

// Or via WordPress admin:
update_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
update_option('stock_scanner_api_secret', 'your-production-secret-key');
```

### **WordPress Virtual Host:**
**File:** `/etc/apache2/sites-available/retailtradescanner.com.conf`

```apache
<VirtualHost *:80>
    ServerName retailtradescanner.com
    ServerAlias www.retailtradescanner.com
    Redirect permanent / https://retailtradescanner.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName retailtradescanner.com
    ServerAlias www.retailtradescanner.com
    DocumentRoot /var/www/retailtradescanner.com
    
    <Directory /var/www/retailtradescanner.com>
        AllowOverride All
        Require all granted
    </Directory>
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/retailtradescanner.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/retailtradescanner.com/privkey.pem
    
    # WordPress security
    <Files wp-config.php>
        Require all denied
    </Files>
</VirtualHost>
```

---

## 🔐 **5. Security Configuration**

### **Firewall Rules:**
```bash
# UFW (Ubuntu)
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Specific IP restrictions (optional)
ufw allow from [trusted-ip] to any port 22
```

### **Django Security Settings:**
```python
# Additional security for production
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# API rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## 📊 **6. Monitoring & Logging**

### **Django Logging:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/retailtradescanner.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'stocks': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### **System Monitoring:**
```bash
# Install monitoring tools
apt install htop iotop nethogs

# Log monitoring
tail -f /var/log/apache2/access.log
tail -f /var/log/django/retailtradescanner.log

# Performance monitoring
htop  # CPU and memory usage
iotop # Disk I/O
nethogs # Network usage
```

---

## 🚀 **7. Deployment Steps**

### **Step 1: Server Preparation**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install python3 python3-pip python3-venv
apt install apache2 libapache2-mod-wsgi-py3
apt install postgresql postgresql-contrib
apt install certbot python3-certbot-apache
```

### **Step 2: Deploy Django**
```bash
# Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database
sudo -u postgres createdb retailtradescanner_db
sudo -u postgres createuser --interactive

# Run migrations
python manage.py migrate
python manage.py collectstatic
```

### **Step 3: Deploy WordPress**
```bash
# Download WordPress
cd /var/www
wget https://wordpress.org/latest.tar.gz
tar xzf latest.tar.gz
mv wordpress retailtradescanner.com

# Set permissions
chown -R www-data:www-data /var/www/retailtradescanner.com
chmod -R 755 /var/www/retailtradescanner.com

# Install plugin
cp -r /path/to/stock-scanner-complete/wordpress_plugin/* /var/www/retailtradescanner.com/wp-content/plugins/
```

### **Step 4: Configure SSL**
```bash
# Get SSL certificates
certbot --apache -d retailtradescanner.com -d www.retailtradescanner.com -d api.retailtradescanner.com

# Test SSL renewal
certbot renew --dry-run
```

---

## ✅ **8. Testing & Validation**

### **Test Django API:**
```bash
# Test API endpoints
curl https://api.retailtradescanner.com/api/stocks/filter/
curl https://api.retailtradescanner.com/api/news/

# Test CORS
curl -H "Origin: https://retailtradescanner.com" \
     -H "Access-Control-Request-Method: POST" \
     https://api.retailtradescanner.com/api/email-signup/
```

### **Test WordPress Integration:**
```bash
# Check WordPress site
curl -I https://retailtradescanner.com
curl -I https://www.retailtradescanner.com

# Test specific pages
curl https://retailtradescanner.com/premium-plans/
curl https://retailtradescanner.com/stock-search/
```

### **Browser Testing:**
1. **Visit** `https://retailtradescanner.com`
2. **Test email signup** on Email Stock Lists page
3. **Test stock filtering** on Stock Search page
4. **Test stock lookup** with ticker symbols
5. **Test news display** on News Scrapper page
6. **Check browser console** for any JavaScript errors

---

## 🔧 **9. Maintenance & Updates**

### **Regular Maintenance:**
```bash
# Update Django dependencies
pip install --upgrade -r requirements.txt

# Update WordPress core and plugins
wp core update
wp plugin update --all

# Monitor logs
tail -f /var/log/apache2/error.log
tail -f /var/log/django/retailtradescanner.log

# Database backup
pg_dump retailtradescanner_db > backup_$(date +%Y%m%d).sql
```

### **Performance Optimization:**
```bash
# Enable Apache modules
a2enmod expires
a2enmod headers
a2enmod deflate

# WordPress caching
# Install WP Super Cache or W3 Total Cache plugin

# Django caching
# Configure Redis or Memcached in Django settings
```

---

## 📞 **Support & Troubleshooting**

### **Common Issues:**

**CORS Errors:**
- Verify domain in `CORS_ALLOWED_ORIGINS`
- Check SSL certificates
- Ensure proper headers

**API Connection Failures:**
- Check DNS resolution
- Verify firewall rules
- Test API endpoints directly

**WordPress Plugin Issues:**
- Check plugin activation
- Verify API URL setting
- Review JavaScript console

### **Log Locations:**
- **Apache:** `/var/log/apache2/`
- **Django:** `/var/log/django/`
- **WordPress:** `/var/www/retailtradescanner.com/wp-content/debug.log`

---

Your **retailtradescanner.com** site is now configured for production with:
- ✅ **Secure HTTPS** connections
- ✅ **Django API** at `api.retailtradescanner.com`
- ✅ **WordPress frontend** with 24 integrated pages
- ✅ **Real-time stock data** and email management
- ✅ **Professional monitoring** and security

🚀 **Ready for live traffic!**