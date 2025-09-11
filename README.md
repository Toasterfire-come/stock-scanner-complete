## CS2 Float Monitor (Safe)

This tool monitors Steam Community Market listings for CS2 skins, fetches float values via a public API, filters by your criteria, and opens matching listings in your signed-in browser for manual purchase.

Important: It does not automate purchases or attempt to bypass Steam rate-limiting or bot detection. Use it responsibly and in accordance with Steam's Terms of Service and API providers' usage policies.

### Features

- Configurable items with `max_float`, `max_price`, and per-item `max_open` limits
- Respectful polling with jitter and retries
- Float lookup via the public CSGOFloat API
- Optional proxy rotation with per-proxy cooldowns (privacy-oriented, not for evasion)
- Opens matching item pages in your browser for quick manual checkout

### Quickstart

1) Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Copy and edit the example config files

```bash
cp config.example.yaml config.yaml
cp proxies.example.json proxies.json  # optional
```

3) Run the monitor

```bash
python -m cs2_float_monitor --config config.yaml --proxies proxies.json
```

Or without proxies:

```bash
python -m cs2_float_monitor --config config.yaml
```

### Configuration

See `config.example.yaml` for a complete example. Minimal fields:

```yaml
polling_interval_seconds: 1.5
country: US
currency: 1  # 1 = USD
items:
  - id: 1
    url: "https://steamcommunity.com/market/listings/730/AK-47%20%7C%20Case%20Hardened%20%28Field-Tested%29"
    max_float: 0.07
    max_price: 50.0
    max_open: 1
  - id: 2
    url: "https://steamcommunity.com/market/listings/730/AWP%20%7C%20Fever%20Dream%20%28Minimal%20Wear%29"
    max_float: 0.15
    max_price: 100.0
    max_open: 2
```

### Proxies (Optional)

Provide a simple JSON file with one or more proxies. Each proxy enforces a cooldown (default 2s) to avoid hammering a single endpoint. This is intended for privacy, not circumvention.

```json
{
  "proxies": [
    {"id": "p1", "http": "http://user:pass@host:port", "https": "http://user:pass@host:port", "cooldown_seconds": 2.0},
    {"id": "p2", "http": "socks5://127.0.0.1:1080", "https": "socks5://127.0.0.1:1080"}
  ]
}
```

Run with:

```bash
python -m cs2_float_monitor --config config.yaml --proxies proxies.json
```

### Notes

- This project respects rate-limits and does not automate purchases. Matches are opened in your browser for manual action.
- CSGOFloat API has its own rate limits. The tool uses retries with backoff and a small concurrency cap.
- Currency is configured via `currency: 1` (USD). If you change it, also adjust your `max_price` numbers accordingly.

# Stock Scanner - Git Bash Complete

**One Command Setup: `./start_django_gitbash.sh`**

## Quick Start (Git Bash)

```bash
# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Run the complete setup and start (single command)
./start_django_gitbash.sh
```

**Access your application:**
- **Main Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Project Structure

```
stock-scanner/
start_django_gitbash.sh # Git Bash setup & launcher (START HERE!)
.env.gitbash # Environment template
manage.py # Django management
requirements.txt # Dependencies

stocks/ # Stock data application
news/ # News scraping & sentiment
core/ # Core Django functionality
emails/ # Email notifications
data/nasdaq_only/ # NASDAQ ticker data
wordpress_plugin/ # WordPress integration
wordpress_theme/ # WordPress theme

API_ENDPOINTS_AND_COMMANDS.md # Complete API reference
GIT_BASH_PRODUCTION_GUIDE.md # Production deployment
GIT_BASH_README.md # Git Bash setup guide
GIT_BASH_SETUP_GUIDE.md # Detailed setup instructions
```

## What This Setup Includes

**Django Framework** - Modern web application backend 
**MySQL Database** - Production-ready MySQL database support 
**yfinance Integration** - Real-time stock data (Yahoo Finance) 
**NASDAQ-Only Tickers** - Focus on NASDAQ securities 
**News Sentiment Analysis** - NLTK-powered sentiment scoring 
**WordPress Integration** - Plugin & theme for WordPress sites 
**Automatic Scheduler** - Updates NASDAQ data every 10 minutes 
**Git Bash Optimized** - Perfect for Windows development 
**Production Ready** - Complete deployment guide included 

## System Requirements

- **Windows**: Git Bash installed
- **Python**: 3.8+ (accessible from Git Bash)
- **Database**: MySQL with user 'stockscanner' and password 'StockScaner2010'
- **Memory**: 2GB+ RAM recommended

## Key Features

### Stock Data Management
- Real-time NASDAQ stock prices via Yahoo Finance
- Historical price tracking and analysis
- Volume, market cap, and P/E ratio monitoring
- Automated data updates every 10 minutes

### News Integration
- Automated news scraping from multiple sources
- Sentiment analysis using NLTK
- Stock ticker extraction from articles
- Sentiment scoring (A-F grades)

### Alert System
- Price-based stock alerts
- Email notifications
- User-customizable alert conditions
- Real-time monitoring

### WordPress Integration
- Complete WordPress plugin for stock data display
- Custom WordPress theme
- API endpoints for external integration
- SEO-optimized pages

### Admin Dashboard
- Comprehensive system status monitoring
- Manual data update controls
- User management interface
- API health monitoring

## Available Scripts

### Development Scripts
- `./start_django_gitbash.sh` - Complete setup and start
- `python manage.py runserver` - Start Django development server

### Management Commands
- `python manage.py load_nasdaq_only` - Load NASDAQ ticker data
- `python manage.py update_stocks_yfinance` - Update stock prices
- `python manage.py update_nasdaq_now` - Full data update
- `python manage.py scrape_news` - Scrape and analyze news
- `python manage.py send_notifications` - Send pending alerts
- `python manage.py optimize_database` - Database optimization

### Git Bash Setup Scripts
- `./setup_git_bash.sh` - Initial Git Bash environment setup
- `./setup_gitbash_complete.sh` - Complete Git Bash setup with MySQL
- `./git_bash_commands.sh` - Common Git Bash commands

## Production Deployment

For production deployment, follow the comprehensive guide:

** [Git Bash Production Guide](GIT_BASH_PRODUCTION_GUIDE.md)**

Key production features:
- Nginx + Gunicorn setup
- SSL certificate automation
- Systemd service configuration
- MySQL production database
- Automated backup strategy
- Monitoring and logging

Environment variables for production hardening:

- `DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production`
- `SECRET_KEY=your-strong-secret`
- `PRIMARY_DOMAIN=api.retailtradescanner.com`
- `PRIMARY_ORIGIN=https://api.retailtradescanner.com`
- `FRONTEND_URL=https://your-frontend.example`
- `WORDPRESS_URL=https://your-wordpress.example`
- `THROTTLE_RATE_ANON=200/hour`
- `THROTTLE_RATE_USER=2000/hour`
- `LOG_LEVEL=INFO`

Run with Gunicorn:

```bash
pip install gunicorn
DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production \
gunicorn stockscanner_django.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Documentation

- **[API Endpoints & Commands](API_ENDPOINTS_AND_COMMANDS.md)** - Complete API reference
- **[Git Bash Setup Guide](GIT_BASH_SETUP_GUIDE.md)** - Detailed setup instructions
- **[Git Bash README](GIT_BASH_README.md)** - Git Bash specific information
- **[Production Guide](GIT_BASH_PRODUCTION_GUIDE.md)** - Production deployment
- **[Security Checklist](SECURITY_CHECKLIST.md)** - Security best practices

## Environment Configuration

Copy the environment template and customize:

```bash
cp .env.gitbash .env
# Edit .env with your specific settings
```

Key environment variables:
- `DEBUG` - Development/production mode
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection string
- `EMAIL_*` - Email configuration for alerts
- `NASDAQ_UPDATE_INTERVAL` - Data update frequency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test with `./start_django_gitbash.sh`
4. Commit changes: `git commit -m "Add new feature"`
5. Push to branch: `git push origin feature/new-feature`
6. Submit a pull request

## Support

If you encounter issues:

1. Check the **[Git Bash Setup Guide](GIT_BASH_SETUP_GUIDE.md)**
2. Review the **[API Documentation](API_ENDPOINTS_AND_COMMANDS.md)**
3. Check Django logs: `python manage.py check`
4. Verify environment: `echo $DEBUG` in Git Bash

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

** Ready to start? Run: `./start_django_gitbash.sh`**
