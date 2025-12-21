# TradeScanPro Production Deployment Guide

**Date**: December 21, 2025
**Status**: Ready for Production Deployment

---

## 📋 Pre-Deployment Checklist

### Backend Prerequisites
- [x] All migrations created and tested locally
- [x] Django server starts without errors
- [x] All scanners tested and working
- [x] Partner analytics API tested
- [x] Production database credentials ready
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured

### Frontend Prerequisites
- [x] Production build successful (514.92 kB gzipped)
- [x] All routes tested
- [x] Zero build errors/warnings
- [ ] Environment variables configured
- [ ] CDN configured (optional)
- [ ] SSL certificates installed

---

## 🚀 Step 1: Deploy Frontend Build

### Option A: SFTP Deployment (Automated)

**Required Environment Variables**:
```bash
SFTP_HOST=tradescanpro.com
SFTP_PORT=22
SFTP_USER=your_username
SFTP_PASS=your_password
SFTP_REMOTE_DIR=/public_html
```

**Deploy Command**:
```bash
cd frontend
npm run deploy:sftp
```

**What This Does**:
1. Connects to production server via SFTP
2. Clears remote directory (preserves .htaccess)
3. Uploads entire build/ folder
4. Verifies upload completion

---

### Option B: Manual Deployment

**1. Build Frontend**:
```bash
cd frontend
npm run build
```

**2. Upload Build Folder**:
Using FileZilla, WinSCP, or similar:
- Local folder: `frontend/build/*`
- Remote folder: `/public_html/` (or your web root)
- Upload all files and folders

**3. Verify Upload**:
- Check that `index.html` exists in web root
- Check that `static/` folder exists
- Verify `.htaccess` file is present

---

### Frontend Environment Variables

Create `frontend/.env.production`:
```bash
# API Configuration
REACT_APP_API_URL=https://api.tradescanpro.com

# PayPal
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_client_id

# Sentry Error Tracking
REACT_APP_SENTRY_DSN=https://your_sentry_dsn@sentry.io/project

# Analytics (Optional)
REACT_APP_GA_ID=G-XXXXXXXXXX
REACT_APP_MATOMO_URL=https://matomo.yourdomain.com
REACT_APP_CLARITY_ID=your_clarity_id

# Google Search Console (Optional)
REACT_APP_GSC_VERIFICATION=your_gsc_verification_code
```

**Rebuild After Updating**:
```bash
npm run build
```

---

## 🗄️ Step 2: Run Backend Migrations in Production

### Production Database Setup

**1. SSH into Production Server**:
```bash
ssh user@tradescanpro.com
```

**2. Navigate to Backend Directory**:
```bash
cd /path/to/backend
```

**3. Activate Virtual Environment** (if using):
```bash
source venv/bin/activate
```

**4. Check Migration Status**:
```bash
python manage.py showmigrations
```

**5. Run Migrations**:
```bash
python manage.py migrate --skip-checks
```

**Expected Output**:
```
Operations to perform:
  Apply all migrations: stocks, billing, backtesting, education, emails, news, core
Running migrations:
  Applying stocks.0001_initial... OK
  Applying stocks.0002_discount_revenue_tracking... OK
  ...
  Applying stocks.0011_remove_stock_stocks_stoc_symbol_3e1bfd_idx_and_more... OK
```

**6. Verify Database Tables**:
```bash
python manage.py dbshell

# In MySQL shell:
SHOW TABLES;

# Check specific tables:
SELECT COUNT(*) FROM stocks_stock;
SELECT COUNT(*) FROM stocks_referralclickevent;
SELECT COUNT(*) FROM stocks_revenuetracking;

# Exit:
exit;
```

**7. Create Superuser** (if needed):
```bash
python manage.py createsuperuser
```

**8. Collect Static Files**:
```bash
python manage.py collectstatic --noinput
```

---

## ⚙️ Step 3: Configure Environment Variables

### Backend Environment Variables

Create `backend/.env.production`:
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your_very_long_random_secret_key_here
ALLOWED_HOSTS=tradescanpro.com,api.tradescanpro.com,www.tradescanpro.com

# Database Configuration
DB_NAME=stockscanner
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://tradescanpro.com,https://www.tradescanpro.com

# PayPal Configuration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=live

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@tradescanpro.com
EMAIL_HOST_PASSWORD=your_email_password

# Sentry Configuration
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project

# Partner Codes
PARTNER_CODE_BY_EMAIL={"hamzashehata3000@gmail.com": "ADAM50"}
```

**Load Environment Variables**:
Add to `.bashrc` or `.bash_profile`:
```bash
export $(cat /path/to/backend/.env.production | xargs)
```

Or use python-dotenv in settings.py:
```python
from dotenv import load_dotenv
load_dotenv('/path/to/.env.production')
```

---

## ⏰ Step 4: Set Up Cron Jobs for Scanners

### Scanner Schedule

**Recommended Schedule**:
- **Daily Scanner**: 2:00 AM (off-peak, minimal throttling)
- **Proxy Refresh**: 1:00 AM (before daily scanner)
- **10-Minute Scanner**: Market hours only (9:30 AM - 4:00 PM ET)
- **1-Minute Scanner**: Market hours only (9:30 AM - 4:00 PM ET)

### Create Cron Jobs

**1. Edit Crontab**:
```bash
crontab -e
```

**2. Add Scanner Jobs**:
```bash
# Refresh proxies daily at 1:00 AM
0 1 * * * /path/to/backend/refresh_proxies.sh >> /var/log/tradescanpro/proxy_refresh.log 2>&1

# Daily scanner at 2:00 AM
0 2 * * * cd /path/to/backend && python realtime_daily_yfinance.py >> /var/log/tradescanpro/daily_scanner.log 2>&1

# 10-minute scanner during market hours (9:30 AM - 4:00 PM ET, every 10 minutes)
30-59/10 9 * * 1-5 cd /path/to/backend && python scanner_10min_metrics_improved.py >> /var/log/tradescanpro/10min_scanner.log 2>&1
*/10 10-15 * * 1-5 cd /path/to/backend && python scanner_10min_metrics_improved.py >> /var/log/tradescanpro/10min_scanner.log 2>&1
0,10,20,30,40,50 16 * * 1-5 cd /path/to/backend && python scanner_10min_metrics_improved.py >> /var/log/tradescanpro/10min_scanner.log 2>&1

# 1-minute scanner during market hours (run as background process)
# Start at 9:30 AM on weekdays
30 9 * * 1-5 cd /path/to/backend && nohup python scanner_1min_hybrid.py >> /var/log/tradescanpro/1min_scanner.log 2>&1 &

# Stop at 4:00 PM on weekdays
0 16 * * 1-5 pkill -f scanner_1min_hybrid.py
```

**3. Create Log Directory**:
```bash
sudo mkdir -p /var/log/tradescanpro
sudo chown your_user:your_group /var/log/tradescanpro
```

**4. Verify Cron Jobs**:
```bash
crontab -l
```

### Alternative: Use Scanner Orchestrator

Instead of individual cron jobs, use the orchestrator:

**Create systemd service** (`/etc/systemd/system/tradescanpro-scanners.service`):
```ini
[Unit]
Description=TradeScanPro Scanner Orchestrator
After=network.target mysql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 /path/to/backend/scanner_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tradescanpro-scanners
sudo systemctl start tradescanpro-scanners
sudo systemctl status tradescanpro-scanners
```

---

## 🔗 Step 5: Create Proxy List for 10-Min Scanner

### Create Proxy Refresh Script

**File**: `backend/refresh_proxies.sh`
```bash
#!/bin/bash

# Proxy Refresh Script for TradeScanPro
# Fetches fresh proxies from free sources
# Run daily via cron at 1:00 AM

BACKEND_DIR="/path/to/backend"
PROXY_FILE="$BACKEND_DIR/http_proxies.txt"
LOG_FILE="/var/log/tradescanpro/proxy_refresh.log"

echo "[$(date)] Starting proxy refresh..." | tee -a "$LOG_FILE"

# Fetch proxies from Geonode API
curl -s "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&filterUpTime=90&speed=fast&limit=500&protocols=http%2Chttps" \
    | jq -r '.data[]? | "\(.ip):\(.port)"' > "$PROXY_FILE.new"

# Check if we got proxies
PROXY_COUNT=$(wc -l < "$PROXY_FILE.new")

if [ "$PROXY_COUNT" -gt 50 ]; then
    mv "$PROXY_FILE.new" "$PROXY_FILE"
    echo "[$(date)] ✅ Proxy refresh successful: $PROXY_COUNT proxies" | tee -a "$LOG_FILE"
else
    echo "[$(date)] ⚠️  Warning: Only $PROXY_COUNT proxies fetched, keeping old list" | tee -a "$LOG_FILE"
    rm -f "$PROXY_FILE.new"
fi

# Backup old proxy file
cp "$PROXY_FILE" "$PROXY_FILE.backup.$(date +%s)"

# Clean up old backups (keep last 7 days)
find "$BACKEND_DIR" -name "http_proxies.txt.backup.*" -mtime +7 -delete

echo "[$(date)] Proxy refresh complete" | tee -a "$LOG_FILE"
```

**Make Executable**:
```bash
chmod +x /path/to/backend/refresh_proxies.sh
```

**Test Manually**:
```bash
cd /path/to/backend
./refresh_proxies.sh
```

**Verify Proxies**:
```bash
wc -l http_proxies.txt
head -10 http_proxies.txt
```

**Expected Output**:
```
200 http_proxies.txt

1.2.3.4:8080
5.6.7.8:3128
9.10.11.12:80
...
```

### Alternative Proxy Sources

**1. ProxyScrape API**:
```bash
curl "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all" \
    -o http_proxies.txt
```

**2. Free-Proxy-List.net** (web scraping):
```bash
curl "https://free-proxy-list.net/" | grep -oP '\d+\.\d+\.\d+\.\d+:\d+' > http_proxies.txt
```

**3. Paid Proxy Services** (Recommended for Production):
- **Bright Data**: https://brightdata.com/
- **Smartproxy**: https://smartproxy.com/
- **Oxylabs**: https://oxylabs.io/

**Configuration for Paid Proxies**:
Update `scanner_10min_metrics_improved.py`:
```python
# Use authentication
PROXY_USER = os.getenv('PROXY_USER')
PROXY_PASS = os.getenv('PROXY_PASS')

def get_next_proxy(self):
    proxy_host = self.proxies[self.current_proxy_index]
    if PROXY_USER and PROXY_PASS:
        proxy_url = f'http://{PROXY_USER}:{PROXY_PASS}@{proxy_host}'
    else:
        proxy_url = f'http://{proxy_host}'
    return {'http': proxy_url, 'https': proxy_url}
```

---

## 🧪 Step 6: Test in Production Environment

### Frontend Testing

**1. Verify Homepage**:
```bash
curl -I https://tradescanpro.com
```

**Expected Response**:
```
HTTP/2 200
content-type: text/html
...
```

**2. Check Static Assets**:
```bash
curl -I https://tradescanpro.com/static/js/main.ca066d00.js
```

**3. Test Routes**:
- Homepage: https://tradescanpro.com/
- Features: https://tradescanpro.com/features
- Pricing: https://tradescanpro.com/pricing
- Sign In: https://tradescanpro.com/auth/sign-in
- Sign Up: https://tradescanpro.com/auth/sign-up

**4. Test Authentication**:
- Create test account
- Verify email verification email sent
- Login with test account
- Access protected routes

**5. Test PWA Install**:
- Visit on mobile device
- Check for install prompt
- Verify manifest loads
- Test offline functionality

---

### Backend Testing

**1. Health Check**:
```bash
curl https://api.tradescanpro.com/health/
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "2.0"
}
```

**2. API Endpoints**:
```bash
# Stock list (requires auth)
curl -H "Authorization: Token YOUR_TOKEN" https://api.tradescanpro.com/api/stocks/

# Market stats
curl https://api.tradescanpro.com/api/status/
```

**3. Database Connection**:
```bash
cd /path/to/backend
python manage.py dbshell

# Test query
SELECT COUNT(*) FROM stocks_stock;
exit;
```

**4. Admin Panel**:
- Visit: https://api.tradescanpro.com/admin/
- Login with superuser credentials
- Verify all models accessible

---

### Scanner Testing

**1. Test Daily Scanner Manually**:
```bash
cd /path/to/backend
python realtime_daily_yfinance.py
```

**Expected Output**:
```
[INFO] ===== Daily Stock Data Scanner =====
[INFO] Total tickers to scan: 8776
[INFO] Threads: 50
[INFO] Starting scan at 2025-12-21 02:00:00
...
[INFO] Progress: 500/8776 (5.7%) | Success: 475 (95.0%)
...
[INFO] Scan complete!
[INFO] Successful: 8345 (95.1%)
[INFO] Total time: 575.3s (9.6 minutes)
```

**2. Test 10-Minute Scanner**:
```bash
cd /path/to/backend
python scanner_10min_metrics_improved.py
```

**Expected Output**:
```
[INFO] Loaded 200 proxies from http_proxies.txt
[BATCH 1/176] Processing 50 tickers...
[PROGRESS] 1/176 batches (0.6%) | Success: 42/50 (84.0%)
...
Successful: 7465 (85.0%)
Proxy failures: 23
Time: 540.0s (9.0 minutes)
```

**3. Test 1-Minute Scanner**:
```bash
cd /path/to/backend
python scanner_1min_hybrid.py
```

**Expected Output**:
```
[WEBSOCKET] Fetching prices for 8776 tickers...
Successfully updated: 7900 (90.0%)
Rate: 140.0 tickers/second
Next scan in 60s
```

**4. Monitor Scanner Logs**:
```bash
tail -f /var/log/tradescanpro/daily_scanner.log
tail -f /var/log/tradescanpro/10min_scanner.log
tail -f /var/log/tradescanpro/1min_scanner.log
```

---

### Partner Analytics Testing

**1. Create Test Data**:
```bash
cd /path/to/backend
python create_partner_test_data.py
```

**2. Login as Partner**:
- Email: hamzashehata3000@gmail.com
- Visit: https://tradescanpro.com/partner/analytics

**3. Verify Dashboard**:
- ✅ Summary statistics load
- ✅ Charts render correctly
- ✅ Recent referrals table shows data
- ✅ Date range filtering works
- ✅ CSV export downloads

---

### Load Testing (Optional)

**1. Install Apache Bench**:
```bash
sudo apt-get install apache2-utils
```

**2. Test Homepage**:
```bash
ab -n 1000 -c 10 https://tradescanpro.com/
```

**3. Test API Endpoint**:
```bash
ab -n 1000 -c 10 -H "Authorization: Token YOUR_TOKEN" https://api.tradescanpro.com/api/stocks/
```

**4. Analyze Results**:
- Requests per second
- Time per request
- Failed requests (should be 0)
- Connection times

---

## 🔍 Monitoring & Maintenance

### Error Monitoring

**1. Sentry Setup**:
- Verify DSN configured in frontend and backend
- Test error reporting: Trigger test error
- Check Sentry dashboard for error

**2. Log Monitoring**:
```bash
# Watch Django logs
tail -f /var/log/tradescanpro/django.log

# Watch nginx logs (if using nginx)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Watch scanner logs
tail -f /var/log/tradescanpro/*.log
```

**3. Database Monitoring**:
```bash
# Check database size
mysql -e "SELECT table_schema AS 'Database',
           ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
           FROM information_schema.tables
           WHERE table_schema = 'stockscanner'
           GROUP BY table_schema;"

# Check table counts
mysql stockscanner -e "SELECT 'stocks_stock', COUNT(*) FROM stocks_stock
                       UNION ALL SELECT 'stocks_revenuetracking', COUNT(*) FROM stocks_revenuetracking;"
```

### Performance Monitoring

**1. Server Resources**:
```bash
# CPU usage
top

# Memory usage
free -m

# Disk usage
df -h
```

**2. Application Performance**:
```bash
# Django slow queries (if DEBUG_TOOLBAR enabled)
# Check admin panel: Django Debug Toolbar

# Database slow query log
# Check MySQL slow query log
```

### Backup Strategy

**1. Database Backups**:
```bash
# Daily database backup (add to cron)
0 3 * * * mysqldump -u your_user -p'your_password' stockscanner | gzip > /backups/stockscanner_$(date +\%Y\%m\%d).sql.gz
```

**2. Code Backups**:
```bash
# Git commit and push regularly
cd /path/to/backend
git add .
git commit -m "Production update $(date)"
git push origin main
```

**3. Retention Policy**:
- Keep daily backups for 7 days
- Keep weekly backups for 1 month
- Keep monthly backups for 1 year

```bash
# Clean old backups (add to cron)
0 4 * * * find /backups -name "stockscanner_*.sql.gz" -mtime +7 -delete
```

---

## 🚨 Troubleshooting

### Frontend Issues

**Issue**: Static files not loading (404 errors)
**Solution**:
1. Check .htaccess file in web root
2. Verify static/ folder uploaded correctly
3. Check file permissions (755 for directories, 644 for files)

**Issue**: API calls failing (CORS errors)
**Solution**:
1. Check CORS_ALLOWED_ORIGINS in backend settings
2. Verify API URL in frontend .env.production
3. Check browser console for exact error

**Issue**: PWA install not working
**Solution**:
1. Verify manifest.json accessible
2. Check HTTPS enabled
3. Verify service worker registered

---

### Backend Issues

**Issue**: 500 Internal Server Error
**Solution**:
1. Check Django logs: `tail -100 /var/log/tradescanpro/django.log`
2. Verify DEBUG=False in production
3. Check database connection
4. Run `python manage.py check --deploy`

**Issue**: Database migrations failing
**Solution**:
1. Check database credentials
2. Verify database exists
3. Run `python manage.py migrate --fake-initial` if needed
4. Check migration files for errors

**Issue**: Static files not serving
**Solution**:
1. Run `python manage.py collectstatic --noinput`
2. Check STATIC_ROOT and STATIC_URL settings
3. Verify web server configuration

---

### Scanner Issues

**Issue**: Daily scanner throttled
**Solution**:
1. Reschedule to off-peak hours (12 AM - 5 AM)
2. Reduce MAX_THREADS from 50 to 25
3. Add delays between requests

**Issue**: 10-min scanner high proxy failures
**Solution**:
1. Refresh proxy list: `./refresh_proxies.sh`
2. Remove dead proxies from list
3. Consider paid proxy service

**Issue**: 1-min scanner WebSocket disconnects
**Solution**:
1. Check internet connection stability
2. Verify Yahoo Finance WebSocket endpoint
3. Add reconnection logic (already implemented)

---

## ✅ Post-Deployment Checklist

### Immediate (Day 1)

- [ ] Frontend deployed and accessible
- [ ] Backend migrations run successfully
- [ ] Admin panel accessible
- [ ] Test account created and working
- [ ] All environment variables configured
- [ ] SSL certificates installed and working
- [ ] Scanners scheduled via cron
- [ ] Proxy list created and tested
- [ ] Error monitoring configured (Sentry)
- [ ] Basic functionality tested

### Short-term (Week 1)

- [ ] Monitor error logs daily
- [ ] Check scanner success rates
- [ ] Verify database growing correctly
- [ ] Test all major features
- [ ] Monitor server resources
- [ ] Set up automated backups
- [ ] Configure alerting for critical errors
- [ ] Performance testing completed

### Medium-term (Month 1)

- [ ] Analyze user behavior (analytics)
- [ ] Optimize slow queries
- [ ] Review and optimize scanner configs
- [ ] Implement additional monitoring
- [ ] Update documentation
- [ ] Plan feature enhancements
- [ ] Review security audit results
- [ ] Optimize bundle sizes if needed

---

## 📞 Support & Contacts

**Developer**: carter.kiefer2010@outlook.com
**Partner**: hamzashehata3000@gmail.com
**Production URL**: https://tradescanpro.com
**API URL**: https://api.tradescanpro.com

---

## 📚 Additional Resources

- [Backend Production Readiness](PRODUCTION_READY_FINAL.md)
- [Frontend Audit Report](FRONTEND_AUDIT_REPORT.md)
- [Scanner Rate Limiting Guide](backend/SCANNER_RATE_LIMITING_GUIDE.md)
- [Partner Analytics Documentation](PARTNER_ANALYTICS_COMPLETE.md)

---

**Last Updated**: December 21, 2025
**Deployment Version**: v2.0
**Status**: Ready for Production
