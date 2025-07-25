# 🚀 Stock Scanner - Git Bash Complete

**One Command Setup: `./start_django_gitbash.sh`**

## 🎯 Quick Start (Git Bash)

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
- **Login**: admin / admin123

## 📁 Project Structure

```
stock-scanner/
├── 🚀 start_django_gitbash.sh      # Git Bash setup & launcher (START HERE!)
├── ⚙️ .env.gitbash                 # Environment template
├── 📊 manage.py                    # Django management
├── 📋 requirements.txt             # Dependencies
│
├── 📂 stocks/                      # Stock data application
├── 📂 news/                        # News scraping & sentiment
├── 📂 core/                        # Core Django functionality
├── 📂 emails/                      # Email notifications
├── 📂 data/nasdaq_only/            # NASDAQ ticker data
├── 📂 wordpress_plugin/            # WordPress integration
├── 📂 wordpress_theme/             # WordPress theme
│
├── 📚 API_ENDPOINTS_AND_COMMANDS.md        # Complete API reference
├── 📚 GIT_BASH_PRODUCTION_GUIDE.md        # Production deployment
├── 📚 GIT_BASH_README.md                  # Git Bash setup guide
└── 📚 GIT_BASH_SETUP_GUIDE.md             # Detailed setup instructions
```

## 🎯 What This Setup Includes

✅ **Django Framework** - Modern web application backend  
✅ **MySQL/SQLite Database** - Flexible database support  
✅ **yfinance Integration** - Real-time stock data (Yahoo Finance)  
✅ **NASDAQ-Only Tickers** - Focus on NASDAQ securities  
✅ **News Sentiment Analysis** - NLTK-powered sentiment scoring  
✅ **WordPress Integration** - Plugin & theme for WordPress sites  
✅ **Automatic Scheduler** - Updates NASDAQ data every 10 minutes  
✅ **Git Bash Optimized** - Perfect for Windows development  
✅ **Production Ready** - Complete deployment guide included  

## 🛠️ System Requirements

- **Windows**: Git Bash installed
- **Python**: 3.8+ (accessible from Git Bash)
- **Database**: SQLite (development) or MySQL (production)
- **Memory**: 2GB+ RAM recommended

## 🌟 Key Features

### 📊 Stock Data Management
- Real-time NASDAQ stock prices via Yahoo Finance
- Historical price tracking and analysis
- Volume, market cap, and P/E ratio monitoring
- Automated data updates every 10 minutes

### 📰 News Integration
- Automated news scraping from multiple sources
- Sentiment analysis using NLTK
- Stock ticker extraction from articles
- Sentiment scoring (A-F grades)

### 🔔 Alert System
- Price-based stock alerts
- Email notifications
- User-customizable alert conditions
- Real-time monitoring

### 🌐 WordPress Integration
- Complete WordPress plugin for stock data display
- Custom WordPress theme
- API endpoints for external integration
- SEO-optimized pages

### 🔧 Admin Dashboard
- Comprehensive system status monitoring
- Manual data update controls
- User management interface
- API health monitoring

## 📋 Available Scripts

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

## 🚀 Production Deployment

For production deployment, follow the comprehensive guide:

**📚 [Git Bash Production Guide](GIT_BASH_PRODUCTION_GUIDE.md)**

Key production features:
- Nginx + Gunicorn setup
- SSL certificate automation
- Systemd service configuration
- MySQL production database
- Automated backup strategy
- Monitoring and logging

## 📖 Documentation

- **[API Endpoints & Commands](API_ENDPOINTS_AND_COMMANDS.md)** - Complete API reference
- **[Git Bash Setup Guide](GIT_BASH_SETUP_GUIDE.md)** - Detailed setup instructions
- **[Git Bash README](GIT_BASH_README.md)** - Git Bash specific information
- **[Production Guide](GIT_BASH_PRODUCTION_GUIDE.md)** - Production deployment
- **[Security Checklist](SECURITY_CHECKLIST.md)** - Security best practices

## 🔧 Environment Configuration

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

## 📞 Support

If you encounter issues:

1. Check the **[Git Bash Setup Guide](GIT_BASH_SETUP_GUIDE.md)**
2. Review the **[API Documentation](API_ENDPOINTS_AND_COMMANDS.md)**
3. Check Django logs: `python manage.py check`
4. Verify environment: `echo $DEBUG` in Git Bash

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 Ready to start? Run: `./start_django_gitbash.sh`**
