# Environment Setup Guide

This guide explains how to configure the environment for the Stock Scanner with Market Hours Manager and all enhanced components.

## Quick Setup

### 1. Choose Your Environment File

Choose the appropriate environment file for your setup:

- **`.env.example`** - Comprehensive template with all options
- **`.env.production`** - Ready-to-use production configuration
- **Custom `.env`** - Create your own based on the examples

### 2. Copy and Configure

```bash
# For production (recommended)
cp .env.production .env

# OR for custom setup
cp .env.example .env
```

### 3. Generate Django Secret Key

**IMPORTANT**: Generate a new Django secret key for security:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Replace the `DJANGO_SECRET_KEY` in your `.env` file with the generated key.

### 4. Update Critical Settings

Edit your `.env` file and update these **REQUIRED** settings:

```bash
# Django Security (REQUIRED)
DJANGO_SECRET_KEY=your-generated-secret-key-here

# Database (Currently using XAMPP root with no password)
DB_USER=root
DB_PASSWORD=

# Email (REQUIRED for notifications)
EMAIL_HOST_PASSWORD=your-gmail-app-password

# PayPal (REQUIRED for payments)
PAYPAL_CLIENT_ID=your-live-paypal-client-id
PAYPAL_CLIENT_SECRET=your-live-paypal-client-secret
```

## Updated Settings

### 🔄 New Market Hours Manager Settings

```bash
# Market Hours Configuration
MARKET_PREMARKET_START=04:00
MARKET_OPEN=09:30
MARKET_CLOSE=16:00
MARKET_POSTMARKET_END=20:00

# Component Intervals
STOCK_RETRIEVAL_INTERVAL=3
NEWS_SCRAPER_INTERVAL=5
EMAIL_SENDER_INTERVAL=10

# Manager Settings
MARKET_HOURS_ENABLED=True
WEEKEND_TRADING_ENABLED=False
```

### 💰 Updated Pricing (December 2024)

Simplified 3-tier pricing structure with 10% annual discount:

```bash
# Bronze Plan - Entry Level
BRONZE_MONTHLY_PRICE=24.99
BRONZE_ANNUAL_PRICE=269.89

# Silver Plan - Professional
SILVER_MONTHLY_PRICE=49.99
SILVER_ANNUAL_PRICE=539.89

# Gold Plan - Premium
GOLD_MONTHLY_PRICE=99.99
GOLD_ANNUAL_PRICE=1079.89
```

### 🔒 Enhanced Security Settings

Production-ready security configuration:

```bash
# Security Headers
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
```

## Environment-Specific Configurations

### Production Environment

Use `.env.production` for live deployment:

- **SSL Enabled**: All security headers configured
- **Live PayPal**: Production PayPal credentials
- **Redis Caching**: Redis for cache and Celery
- **Secure Cookies**: Production-safe cookie settings
- **Rate Limiting**: Production-appropriate limits

### Development Environment (Current XAMPP Setup)

Current configuration is already set for XAMPP development:

```bash
# Current XAMPP settings
DB_USER=root
DB_PASSWORD=
DJANGO_DEBUG=False  # Set to True for debugging
PAYPAL_MODE=live    # Change to sandbox for testing
SSL_ENABLED=True    # Can be False for local development
```

## Required External Services

### 1. Redis (Recommended for Production)

Install and configure Redis:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

Update environment:
```bash
CELERY_ENABLED=True
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
```

### 2. MySQL Database

**Current Setup (XAMPP Development):**
```sql
CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Using root user with no password (XAMPP default)
```

**Future Production Setup:**
```sql
CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stockscanner_user'@'localhost' IDENTIFIED BY 'StockScanner2024!SecurePassword#Prod';
GRANT ALL PRIVILEGES ON stockscanner.* TO 'stockscanner_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Gmail App Password

Generate Gmail app password for email notifications:

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings → Security → App Passwords
3. Generate password for "Mail"
4. Use this password as `EMAIL_HOST_PASSWORD`

## Security Checklist

- [ ] Generated new Django secret key
- [ ] Database configured (currently XAMPP root/no password)
- [ ] Configured Gmail app password
- [ ] PayPal credentials configured (currently live)
- [ ] Set secure file permissions: `chmod 600 .env`
- [ ] Consider SSL certificates for production
- [ ] Plan production database security upgrade
- [ ] Configured proper backup settings

## File Permissions

Set proper permissions for security:

```bash
# Environment file (sensitive)
chmod 600 .env

# Log files
chmod 644 *.log

# Scripts
chmod +x *.sh *.py
```

## Verification

Test your configuration:

```bash
# Test Django configuration
python manage.py check

# Test database connection
python manage.py dbshell

# Test market hours manager
python market_hours_manager.py --help

# Test restart-enabled components
python news_scraper_with_restart.py --help
python email_sender_with_restart.py --help
```

## Environment Variables Reference

### Critical Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django security key | `your-50-char-secret-key` |
| `DB_PASSWORD` | Database password | `SecurePassword123!` |
| `EMAIL_HOST_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop` |
| `PAYPAL_CLIENT_ID` | PayPal live client ID | `AQLxJ2PT...` |
| `PAYPAL_CLIENT_SECRET` | PayPal live secret | `EBz7lzVK...` |

### Market Hours Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MARKET_PREMARKET_START` | Premarket start time (ET) | `04:00` |
| `MARKET_OPEN` | Market open time (ET) | `09:30` |
| `MARKET_CLOSE` | Market close time (ET) | `16:00` |
| `MARKET_POSTMARKET_END` | Postmarket end time (ET) | `20:00` |

### Component Intervals

| Variable | Description | Default |
|----------|-------------|---------|
| `STOCK_RETRIEVAL_INTERVAL` | Stock data update interval | `3` minutes |
| `NEWS_SCRAPER_INTERVAL` | News scraping interval | `5` minutes |
| `EMAIL_SENDER_INTERVAL` | Email sending interval | `10` minutes |

## Troubleshooting

### Common Issues

1. **"SECRET_KEY not found"**
   - Generate new secret key and add to `.env`

2. **"Database connection failed"**
   - Check database credentials and ensure MySQL is running

3. **"Redis connection failed"**
   - Install Redis or disable Celery: `CELERY_ENABLED=False`

4. **"Email sending failed"**
   - Verify Gmail app password and 2FA settings

5. **"PayPal API error"**
   - Check PayPal credentials and webhook URLs

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
DJANGO_DEBUG=True
LOG_LEVEL=DEBUG
MARKET_HOURS_LOG_LEVEL=DEBUG
```

**Remember to disable debug mode in production!**

## Next Steps

After environment setup:

1. Run database migrations: `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Test market hours manager: `./start_market_hours.sh`
4. Configure systemd service for production
5. Set up SSL certificates
6. Configure backup strategy

## Support

For additional help:
- Check component logs in respective `.log` files
- Review Django settings: `python manage.py diffsettings`
- Validate environment: `python manage.py check --deploy`