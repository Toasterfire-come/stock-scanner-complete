# 🚀 WordPress + Stock Scanner Launch Guide

## 📋 Overview
This guide covers launching your Stock Scanner Django application in production with WordPress integration, including paywall functionality and IONOS hosting.

## 🎯 Launch Phases

### Phase 1: Pre-Launch Preparation (Day 1-2)
### Phase 2: WordPress Integration (Day 3-4)  
### Phase 3: Production Deployment (Day 5-6)
### Phase 4: Testing & Go-Live (Day 7)

---

## 🏗️ **PHASE 1: PRE-LAUNCH PREPARATION**

### 1.1 Server Requirements Check
```bash
# Verify your server meets requirements
python3 --version  # Should be 3.8+
pip3 --version
sqlite3 --version
nginx --version    # Or Apache
```

### 1.2 Domain Setup (IONOS)
Since your domain is already hosted by IONOS:

✅ **DNS Configuration**:
- Main site: `yoursite.com` → WordPress
- API subdomain: `api.yoursite.com` → Django Stock Scanner
- Admin: `admin.yoursite.com` → Django Admin (optional)

### 1.3 SSL Certificate
```bash
# Install Let's Encrypt SSL
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yoursite.com
```

### 1.4 Environment Setup
```bash
# Production environment file
cp .env.sample .env.production
```

**Edit `.env.production`**:
```ini
# Production Settings
DEBUG=False
DJANGO_SECRET_KEY=your-unique-production-secret-key
ALLOWED_HOSTS=api.yoursite.com,yoursite.com

# WordPress Integration
WORDPRESS_SITE_URL=https://yoursite.com
WORDPRESS_API_SECRET=shared-secret-between-wp-and-django
CORS_ALLOWED_ORIGINS=https://yoursite.com,https://www.yoursite.com

# Email (Already configured)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply.retailtradescanner@gmail.com
EMAIL_HOST_PASSWORD=mzqmvhsjqeqrjmjv

# Paid Membership Pro
PMP_API_KEY=your-pmp-api-key
PMP_WEBHOOK_SECRET=webhook-secret-from-pmp
```

---

## 🔗 **PHASE 2: WORDPRESS INTEGRATION**

### 2.1 WordPress Plugin Installation

**Option A: Custom Plugin** (Recommended)
1. Upload `wordpress_plugin/stock-scanner-integration/` to `/wp-content/plugins/`
2. Activate in WordPress Admin → Plugins

**Option B: Theme Integration**
1. Add code to your theme's `functions.php`
2. Use the provided WordPress theme files

### 2.2 Paid Membership Pro Setup

**Install PMP Plugin**:
1. WordPress Admin → Plugins → Add New
2. Search "Paid Membership Pro"
3. Install and activate

**Configure Membership Levels**:
```php
// Add to your theme's functions.php or custom plugin
function setup_stock_scanner_membership_levels() {
    // Free Level (15 stocks/month)
    pmpro_changeMembershipLevel(1, $user_id); // Level 1 = Free
    
    // Premium Level (1000 stocks/month) 
    pmpro_changeMembershipLevel(2, $user_id); // Level 2 = Premium
    
    // Professional Level (10000 stocks/month)
    pmpro_changeMembershipLevel(3, $user_id); // Level 3 = Professional
}
```

### 2.3 WordPress API Authentication

**Add to WordPress `functions.php`**:
```php
// Stock Scanner API Integration
function stock_scanner_api_request($endpoint, $data = []) {
    $api_url = 'https://api.yoursite.com/api/v1/' . $endpoint;
    $secret = 'shared-secret-between-wp-and-django';
    
    $args = [
        'body' => json_encode($data),
        'headers' => [
            'Content-Type' => 'application/json',
            'X-API-Secret' => $secret,
            'X-User-Level' => pmpro_getMembershipLevelForUser(get_current_user_id())->id ?? 0
        ]
    ];
    
    return wp_remote_post($api_url, $args);
}

// Check user stock usage
function check_user_stock_usage($user_id) {
    $response = stock_scanner_api_request('user/usage/', ['user_id' => $user_id]);
    return json_decode(wp_remote_retrieve_body($response), true);
}
```

---

## 🚀 **PHASE 3: PRODUCTION DEPLOYMENT**

### 3.1 Django Production Setup

**Deploy Django App**:
```bash
# Clone your repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
git checkout complete-stock-scanner-v1

# Create production virtual environment
python3 -m venv venv_prod
source venv_prod/bin/activate

# Install dependencies
pip install -r requirements.txt

# Production setup
cp .env.production .env
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 3.2 Nginx Configuration

**Create `/etc/nginx/sites-available/stock-scanner`**:
```nginx
server {
    listen 80;
    server_name api.yoursite.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yoursite.com;

    ssl_certificate /etc/letsencrypt/live/api.yoursite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yoursite.com/privkey.pem;

    location /static/ {
        alias /path/to/stock-scanner-complete/staticfiles/;
    }

    location /media/ {
        alias /path/to/stock-scanner-complete/mediafiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable the site**:
```bash
sudo ln -s /etc/nginx/sites-available/stock-scanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.3 Systemd Service

**Create `/etc/systemd/system/stock-scanner.service`**:
```ini
[Unit]
Description=Stock Scanner Django App
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/stock-scanner-complete
Environment=PATH=/path/to/stock-scanner-complete/venv_prod/bin
EnvironmentFile=/path/to/stock-scanner-complete/.env
ExecStart=/path/to/stock-scanner-complete/venv_prod/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 stockscanner_django.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start the service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-scanner
sudo systemctl start stock-scanner
sudo systemctl status stock-scanner
```

---

## 🧪 **PHASE 4: TESTING & GO-LIVE**

### 4.1 Integration Testing

**Test API Endpoints**:
```bash
# Test basic API
curl -X GET https://api.yoursite.com/api/v1/health/

# Test WordPress integration
curl -X POST https://api.yoursite.com/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -H "X-API-Secret: your-shared-secret" \
  -H "X-User-Level: 1" \
  -d '{"symbol": "AAPL", "user_id": "123"}'
```

**Test WordPress Side**:
```php
// Add to WordPress (temporary testing)
function test_stock_scanner_integration() {
    if (current_user_can('administrator')) {
        $response = stock_scanner_api_request('stocks/', ['symbol' => 'AAPL']);
        echo '<pre>' . print_r($response, true) . '</pre>';
    }
}
add_action('wp_footer', 'test_stock_scanner_integration');
```

### 4.2 Payment Testing

**Stripe Test Mode**:
1. Use Stripe test cards: `4242 4242 4242 4242`
2. Test all membership levels
3. Verify usage limits are enforced

### 4.3 Go-Live Checklist

- [ ] DNS pointing to correct servers
- [ ] SSL certificates installed and working
- [ ] WordPress site loading correctly
- [ ] Django API responding at `api.yoursite.com`
- [ ] PMP membership levels configured
- [ ] Stripe payments working
- [ ] Email notifications sending
- [ ] Usage limits enforcing correctly
- [ ] Logs are being written
- [ ] Backup system in place

---

## 🔧 **POST-LAUNCH MAINTENANCE**

### Daily Tasks
```bash
# Check service status
sudo systemctl status stock-scanner

# View logs
tail -f /path/to/stock-scanner-complete/logs/django.log
tail -f /path/to/stock-scanner-complete/logs/wordpress.log
```

### Weekly Tasks
```bash
# Database backup
python manage.py dbshell
.backup main backup_$(date +%Y%m%d).db

# Update static files if needed
python manage.py collectstatic --noinput
```

### Monthly Tasks
- Review usage analytics
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Renew SSL certificates (automatic with certbot)

---

## 🆘 **TROUBLESHOOTING**

### Common Issues

**1. CORS Errors**
```python
# In Django settings
CORS_ALLOWED_ORIGINS = [
    "https://yoursite.com",
    "https://www.yoursite.com",
]
```

**2. API Authentication Failing**
```php
// Check WordPress headers
$headers = getallheaders();
error_log('API Headers: ' . print_r($headers, true));
```

**3. Stock Limits Not Working**
```python
# Check Django logs
tail -f logs/django.log | grep "usage_limit"
```

### Support Commands
```bash
# Restart everything
sudo systemctl restart stock-scanner
sudo systemctl restart nginx

# Check all services
sudo systemctl status stock-scanner nginx mysql
```

---

## 🎯 **QUICK LAUNCH COMMANDS**

```bash
# 1. Clone and setup
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete && git checkout complete-stock-scanner-v1

# 2. Production setup
python3 -m venv venv_prod && source venv_prod/bin/activate
pip install -r requirements.txt gunicorn

# 3. Configure
cp .env.sample .env
# Edit .env with your production values

# 4. Deploy
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 5. Start
gunicorn --bind 0.0.0.0:8000 stockscanner_django.wsgi:application
```

## 🎉 **YOU'RE LIVE!**

Your Stock Scanner is now integrated with WordPress and ready for production use!

**Next Steps**:
1. Monitor logs for the first week
2. Gather user feedback
3. Scale as needed

**Need Help?** Check the troubleshooting section or review the logs at `/logs/`.