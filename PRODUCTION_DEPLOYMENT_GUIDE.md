# Stock Scanner Production Deployment Guide

## Current State Assessment

You currently have:
- ✅ Django admin console running on localhost:8000
- ✅ NASDAQ data scheduler working (updates every 10 minutes)
- ✅ Virtual environment set up with existing requirements
- ✅ Database migrations completed
- ✅ Basic functionality working

## New Requirements (Add These Only)

Since you already have your environment set up, only add these new packages:

```bash
# Activate your existing virtual environment first
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Add only the new requirements
pip install schedule==1.2.0
pip install python-dotenv==1.0.0
```

## Phase 1: Update Your Local Environment

### Step 1: Update Your Local Files

The following files have been updated with new pricing and features. Update them in your local environment:

#### 1.1 Update Usage Tracker
```bash
# The file wordpress_plugin/stock-scanner-integration/includes/usage-tracker.php
# has been updated with new pricing: Basic ($15), Pro ($30), Enterprise ($100)
# Copy the updated version to your local environment
```

#### 1.2 Update WordPress Plugin
```bash
# The file wordpress_plugin/stock-scanner-integration/stock-scanner-integration.php
# has been updated with correct pricing and 4-tier system
# Copy the updated version to your local environment
```

#### 1.3 Update Environment Template
```bash
# Update your .env file with new pricing structure
# See .env.template for the updated format
```

### Step 2: Test Updated Local Environment

```bash
# Start your Django server (if not already running)
python manage.py runserver

# Verify the following URLs work:
# http://localhost:8000/admin-dashboard/
# http://localhost:8000/wordpress-stocks/
# http://localhost:8000/wordpress-news/
```

### Step 3: Verify NASDAQ Scheduler

Check that your scheduler is working with updated pricing:
```bash
# Check console output for scheduler messages:
# "🚀 Starting NASDAQ data scheduler (every 10 minutes)..."
# "✅ NASDAQ data update completed!"
```

## Phase 2: Prepare Production Environment

### Step 2.1: Server Setup

Choose your production server setup:

#### Option A: VPS/Cloud Server (Recommended)
```bash
# On your production server (Ubuntu/CentOS)
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx mysql-server python3 python3-pip python3-venv
sudo apt install -y php8.1 php8.1-fpm php8.1-mysql php8.1-curl php8.1-zip
sudo apt install -y certbot python3-certbot-nginx
```

#### Option B: Shared Hosting
```bash
# Requirements for shared hosting:
# - PHP 8.1+
# - MySQL 5.7+
# - WordPress support
# - Ability to install plugins
# - SSL certificate
```

### Step 2.2: Domain and SSL Setup

```bash
# Point your domain to your server IP
# Example: stockscanner.yourdomain.com

# Set up SSL certificate (for VPS)
sudo certbot --nginx -d stockscanner.yourdomain.com
```

## Phase 3: Deploy Django Backend

### Step 3.1: Upload Django Code

```bash
# On your production server, create directory
sudo mkdir -p /var/www/stockscanner
sudo chown $USER:$USER /var/www/stockscanner

# Upload your Django project (excluding venv, __pycache__, .git)
# Use rsync, scp, or git clone
rsync -av --exclude='venv' --exclude='__pycache__' \
  --exclude='.git' --exclude='*.pyc' \
  /path/to/your/local/project/ user@server:/var/www/stockscanner/
```

### Step 3.2: Set Up Production Virtual Environment

```bash
# On production server
cd /var/www/stockscanner
python3 -m venv venv
source venv/bin/activate

# Install requirements (same as your local + new ones)
pip install -r requirements.txt
pip install schedule==1.2.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0
```

### Step 3.3: Configure Production Database

```bash
# Create MySQL database and user
sudo mysql -u root -p

CREATE DATABASE stockscanner_production;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON stockscanner_production.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3.4: Create Production Environment File

```bash
# Create /var/www/stockscanner/.env
cat > /var/www/stockscanner/.env << 'EOF'
# Django Settings
DJANGO_SECRET_KEY=your-super-secure-secret-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=stockscanner.yourdomain.com,api.yourdomain.com

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=stockscanner_production
DB_USER=django_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=3306

# WordPress Integration
WORDPRESS_URL=https://yourdomain.com
DJANGO_API_URL=https://api.yourdomain.com

# Stripe (add your actual keys)
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF
```

### Step 3.5: Run Production Migrations

**IMPORTANT**: Use your existing migrations, don't recreate them:

```bash
cd /var/www/stockscanner
source venv/bin/activate

# Copy your existing migration files from local to production
# rsync -av migrations/ user@server:/var/www/stockscanner/stocks/migrations/

# Apply existing migrations (not create new ones)
python manage.py migrate --settings=stockscanner_django.settings_production

# Create superuser for production
python manage.py createsuperuser --settings=stockscanner_django.settings_production

# Load NASDAQ data (same as you did locally)
python manage.py load_nasdaq_only --settings=stockscanner_django.settings_production
```

### Step 3.6: Configure Gunicorn Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/stockscanner.service << 'EOF'
[Unit]
Description=Stock Scanner Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/stockscanner
Environment="PATH=/var/www/stockscanner/venv/bin"
ExecStart=/var/www/stockscanner/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/stockscanner/stockscanner.sock \
    --settings=stockscanner_django.settings_production \
    stockscanner_django.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable stockscanner
sudo systemctl start stockscanner
sudo systemctl status stockscanner
```

### Step 3.7: Configure Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/stockscanner << 'EOF'
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/stockscanner;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/stockscanner/stockscanner.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/stockscanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Phase 4: Deploy WordPress Integration

### Step 4.1: Set Up WordPress

```bash
# Download WordPress
cd /var/www/html
sudo wget https://wordpress.org/latest.tar.gz
sudo tar -xzf latest.tar.gz
sudo mv wordpress/* .
sudo rm -rf wordpress latest.tar.gz

# Set permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

### Step 4.2: Configure WordPress Database

```bash
# Create WordPress database
sudo mysql -u root -p

CREATE DATABASE wordpress_stockscanner;
CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'your-wp-password';
GRANT ALL PRIVILEGES ON wordpress_stockscanner.* TO 'wp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4.3: Install WordPress Theme and Plugin

```bash
# Upload theme
sudo cp -r /path/to/wordpress_theme/stock-scanner-theme/ \
  /var/www/html/wp-content/themes/

# Upload plugin
sudo cp -r /path/to/wordpress_plugin/stock-scanner-integration/ \
  /var/www/html/wp-content/plugins/

# Set permissions
sudo chown -R www-data:www-data /var/www/html/wp-content/
```

### Step 4.4: Complete WordPress Setup

1. Go to `https://yourdomain.com/wp-admin/install.php`
2. Complete WordPress installation
3. Install and activate **Paid Memberships Pro** plugin
4. Activate **Stock Scanner Integration** plugin
5. Activate **Stock Scanner Theme**

### Step 4.5: Configure Membership Levels

```bash
# Option 1: Run setup script via WordPress admin
# Go to WordPress admin > Tools > Stock Scanner Setup
# Click "Run Membership Setup"

# Option 2: Run manually via SSH
cd /var/www/html
sudo -u www-data php -r "
require_once 'wp-config.php';
require_once 'wp-content/plugins/stock-scanner-integration/setup-pmp-levels.php';
run_stock_scanner_pmp_setup();
"
```

### Step 4.6: Configure Stripe in WordPress

1. Go to **Memberships > Payment Settings**
2. Select **Stripe** as gateway
3. Enter your live Stripe keys
4. Set currency to **USD**
5. Configure webhook URL: `https://yourdomain.com/stock-scanner/webhook/stripe/`

## Phase 5: Final Configuration and Testing

### Step 5.1: Configure API Integration

Update WordPress settings to connect to Django:
```bash
# In WordPress admin, go to Settings > Stock Scanner
# Set Django API URL: https://api.yourdomain.com
# Test API connection
```

### Step 5.2: Test Complete System

#### Test Django Backend
```bash
# Check these URLs work:
https://api.yourdomain.com/admin-dashboard/
https://api.yourdomain.com/api/admin/status/
https://api.yourdomain.com/api/wordpress/stocks/
https://api.yourdomain.com/api/wordpress/news/
```

#### Test WordPress Frontend
```bash
# Check these work:
https://yourdomain.com/ (theme loads)
https://yourdomain.com/membership-plans/ (pricing displays)
https://yourdomain.com/membership-checkout/?level=1 (Stripe checkout)
```

#### Test Stripe Integration
```bash
# Test checkout process:
1. Go to membership checkout
2. Select Basic plan ($15/month)
3. Complete with test card: 4242 4242 4242 4242
4. Verify membership is assigned
5. Check webhook delivery in Stripe dashboard
```

### Step 5.3: Monitor System Health

```bash
# Check Django service
sudo systemctl status stockscanner

# Check Nginx
sudo systemctl status nginx

# Check Django logs
sudo journalctl -u stockscanner -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Phase 6: Production Optimizations

### Step 6.1: Set Up Monitoring

```bash
# Install monitoring tools
pip install sentry-sdk  # Error tracking
pip install newrelic    # Performance monitoring

# Configure in settings_production.py
```

### Step 6.2: Set Up Backups

```bash
# Create backup script
sudo tee /usr/local/bin/stockscanner-backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/stockscanner"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u django_user -p'password' stockscanner_production > \
  $BACKUP_DIR/django_db_$DATE.sql

mysqldump -u wp_user -p'password' wordpress_stockscanner > \
  $BACKUP_DIR/wordpress_db_$DATE.sql

# Backup files
tar -czf $BACKUP_DIR/django_files_$DATE.tar.gz /var/www/stockscanner
tar -czf $BACKUP_DIR/wordpress_files_$DATE.tar.gz /var/www/html

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

# Make executable and add to cron
sudo chmod +x /usr/local/bin/stockscanner-backup.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/stockscanner-backup.sh
```

### Step 6.3: Configure SSL Auto-Renewal

```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Add to cron (usually already done by certbot)
sudo crontab -l | grep -q certbot || \
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Troubleshooting Common Issues

### Django Issues
```bash
# If Django won't start
sudo systemctl status stockscanner
sudo journalctl -u stockscanner -n 50

# If database connection fails
python manage.py dbshell --settings=stockscanner_django.settings_production

# If static files not loading
python manage.py collectstatic --settings=stockscanner_django.settings_production
```

### WordPress Issues
```bash
# If theme not loading
# Check file permissions: sudo chown -R www-data:www-data /var/www/html

# If plugin not working
# Check error logs: sudo tail -f /var/log/nginx/error.log

# If API connection fails
# Check Django is running and accessible
curl https://api.yourdomain.com/api/admin/status/
```

### Stripe Issues
```bash
# If payments not working
# Check webhook delivery in Stripe dashboard
# Verify webhook endpoint: https://yourdomain.com/stock-scanner/webhook/stripe/
# Check WordPress error logs
```

## Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (UFW or iptables)
- [ ] Database users have minimal permissions
- [ ] WordPress admin secured with strong passwords
- [ ] Django DEBUG=False in production
- [ ] Stripe live keys configured securely
- [ ] Regular backups scheduled
- [ ] Error monitoring configured
- [ ] Server updates automated

## Performance Optimization

### Django Optimizations
```bash
# Add to settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Install Redis
sudo apt install redis-server
pip install redis django-redis
```

### Database Optimizations
```bash
# Optimize MySQL
sudo mysql_secure_installation

# Add to MySQL config (/etc/mysql/mysql.conf.d/mysqld.cnf)
[mysqld]
innodb_buffer_pool_size = 1G
query_cache_size = 256M
tmp_table_size = 64M
max_heap_table_size = 64M
```

This guide takes you from your current working localhost setup to a fully functional production environment without disrupting your existing configuration or requiring you to recreate migrations or virtual environments.