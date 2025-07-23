# 📁 Project Structure Guide

This document explains the organized structure of the Stock Scanner Complete project after cleanup and reorganization.

## 🏗️ Directory Structure

```
stock-scanner-complete/
├── 📄 README.md                          # Main project documentation
├── 📄 requirements.txt                   # Python dependencies
├── 📄 requirements-windows.txt           # Windows-specific dependencies
├── 📄 manage.py                          # Django management script
├── 📄 .gitignore                         # Git ignore patterns
├── 📄 WINDOWS_SETUP_GUIDE.md             # Windows setup instructions
│
├── 📁 docs/                              # 📚 Documentation
│   ├── 📄 PROJECT_STRUCTURE.md           # This file - project organization
│   ├── 📄 YFINANCE_RATE_LIMIT_GUIDE.md   # Rate limit optimizer guide
│   ├── 📄 API_DOCUMENTATION.md           # API endpoints documentation
│   └── 📄 DEPLOYMENT_GUIDE.md            # Production deployment guide
│
├── 📁 scripts/                           # 🔧 Utility Scripts
│   ├── 📁 setup/                         # Setup and installation scripts
│   │   ├── 📄 windows_fix_install.py     # Windows installer with fixes
│   │   ├── 📄 setup_redis_windows.py     # Redis setup for Windows
│   │   ├── 📄 install_missing_packages.py # Package installer
│   │   ├── 📄 run_migrations.py          # Database migration runner
│   │   └── 📄 apply_yfinance_migrations.py # YFinance specific migrations
│   ├── 📁 testing/                       # Testing and validation scripts
│   │   ├── 📄 test_django_startup.py     # Django startup test
│   │   ├── 📄 test_yfinance_system.py    # YFinance API test
│   │   ├── 📄 test_imports.py            # Import validation test
│   │   ├── 📄 test_redis_fix.py          # Redis dependency test
│   │   └── 📄 django_minimal_test.py     # Minimal Django test
│   └── 📁 utils/                         # Utility and maintenance scripts
│       ├── 📄 yahoo_rate_limit_optimizer.py # 🌟 Rate limit optimizer
│       ├── 📄 enable_celery_beat.py      # Celery Beat enabler
│       ├── 📄 fix_env_urls.py            # Environment URL fixer
│       └── 📄 check_syntax.py            # Code syntax checker
│
├── 📁 stockscanner_django/               # 🎯 Django Project
│   ├── 📄 settings.py                    # Django configuration
│   ├── 📄 urls.py                        # URL routing
│   ├── 📄 wsgi.py                        # WSGI configuration
│   ├── 📄 asgi.py                        # ASGI configuration
│   ├── 📄 celery.py                      # Celery configuration
│   └── 📄 __init__.py                    # Python package init
│
├── 📁 stocks/                            # 📊 Stock Data App
│   ├── 📄 models.py                      # Database models (StockAlert, Membership)
│   ├── 📄 api_views.py                   # REST API endpoints
│   ├── 📄 analytics_views.py             # Analytics and reporting
│   ├── 📄 admin.py                       # Django admin configuration
│   ├── 📄 admin_dashboard.py             # Admin dashboard
│   ├── 📄 api_manager.py                 # Stock data API management
│   ├── 📄 advanced_features.py           # Advanced analytics features
│   ├── 📄 signals.py                     # Django signals
│   ├── 📄 urls.py                        # Stock app URL patterns
│   ├── 📁 management/commands/           # Django management commands
│   └── 📁 migrations/                    # Database migrations
│
├── 📁 core/                             # 🌐 Core Web App
│   ├── 📄 views.py                       # Core web views
│   ├── 📄 admin_api_views.py             # Admin API endpoints
│   ├── 📄 models.py                      # Core models
│   ├── 📄 urls.py                        # Core URL patterns
│   ├── 📁 templates/                     # HTML templates
│   ├── 📁 static/                        # Static files (CSS, JS)
│   └── 📁 migrations/                    # Database migrations
│
├── 📁 emails/                           # 📧 Email System
│   ├── 📄 models.py                      # Email subscription models
│   ├── 📄 email_config.py               # Email configuration
│   ├── 📄 admin.py                       # Email admin interface
│   └── 📁 migrations/                    # Database migrations
│
├── 📁 news/                             # 📰 News Aggregation
│   ├── 📄 models.py                      # News models
│   ├── 📄 scraper.py                     # News scraping logic
│   ├── 📄 tasks.py                       # Background news tasks
│   └── 📁 migrations/                    # Database migrations
│
├── 📁 wordpress_plugin/                 # 🌐 WordPress Integration
│   └── 📁 stock-scanner-integration/    # Complete WordPress plugin
│       ├── 📄 stock-scanner-integration.php # Main plugin file
│       └── 📁 assets/                    # Plugin assets (JS, CSS)
│
├── 📁 wordpress_theme/                  # 🎨 WordPress Theme
│   └── 📁 stock-scanner-theme/          # Professional theme
│       ├── 📄 style.css                 # Theme styles
│       ├── 📄 functions.php             # Theme functions
│       ├── 📄 index.php                 # Theme template
│       └── 📁 js/                       # Theme JavaScript
│
└── 📁 tests/                           # 🧪 Test Suite
    ├── 📄 test_models.py                # Model tests
    ├── 📄 test_api_views.py             # API endpoint tests
    ├── 📄 test_analytics.py             # Analytics tests
    └── 📄 test_integration.py           # Integration tests
```

## 🎯 Key Components

### 1. **Setup Scripts (`scripts/setup/`)**

| Script | Purpose | Usage |
|--------|---------|-------|
| `windows_fix_install.py` | 🪟 Windows installation with compatibility fixes | `python scripts/setup/windows_fix_install.py` |
| `setup_redis_windows.py` | 🔧 Redis setup for Windows users | `python scripts/setup/setup_redis_windows.py` |
| `run_migrations.py` | 📊 Database migration runner | `python scripts/setup/run_migrations.py` |

### 2. **Testing Scripts (`scripts/testing/`)**

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_django_startup.py` | ✅ Comprehensive Django startup test | `python scripts/testing/test_django_startup.py` |
| `test_yfinance_system.py` | 📈 YFinance API connectivity test | `python scripts/testing/test_yfinance_system.py` |
| `test_redis_fix.py` | 🔧 Redis dependency validation | `python scripts/testing/test_redis_fix.py` |

### 3. **Utility Scripts (`scripts/utils/`)**

| Script | Purpose | Usage |
|--------|---------|-------|
| `yahoo_rate_limit_optimizer.py` | 🌟 **Rate limit optimizer** | `python scripts/utils/yahoo_rate_limit_optimizer.py` |
| `enable_celery_beat.py` | ⏰ Celery Beat scheduler setup | `python scripts/utils/enable_celery_beat.py` |
| `check_syntax.py` | 🔍 Code syntax validation | `python scripts/utils/check_syntax.py` |

## 🌟 Rate Limit Optimizer Spotlight

### Location
```
scripts/utils/yahoo_rate_limit_optimizer.py
```

### Quick Start
```bash
# Basic optimization test
python scripts/utils/yahoo_rate_limit_optimizer.py

# Advanced configuration
python scripts/utils/yahoo_rate_limit_optimizer.py --comprehensive --save-results
```

### Documentation
📚 **Complete Guide**: [docs/YFINANCE_RATE_LIMIT_GUIDE.md](YFINANCE_RATE_LIMIT_GUIDE.md)

## 🚀 Quick Start Commands

### Setup (Windows)
```cmd
# 1. Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Run Windows installer
python scripts/setup/windows_fix_install.py

# 3. Test startup
python scripts/testing/test_django_startup.py

# 4. Start Django
python manage.py runserver
```

### Setup (Linux/Mac)
```bash
# 1. Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python scripts/setup/run_migrations.py

# 4. Start Django
python manage.py runserver
```

## 📊 Development Workflow

### 1. **Initial Setup**
```bash
# Install and configure
python scripts/setup/windows_fix_install.py  # Windows
# OR
pip install -r requirements.txt  # Linux/Mac

# Test installation
python scripts/testing/test_django_startup.py
```

### 2. **Rate Limit Optimization**
```bash
# Optimize Yahoo Finance API calls
python scripts/utils/yahoo_rate_limit_optimizer.py

# Apply results to production
# (Follow guide in docs/YFINANCE_RATE_LIMIT_GUIDE.md)
```

### 3. **Testing**
```bash
# Test all components
python scripts/testing/test_django_startup.py
python scripts/testing/test_yfinance_system.py
python scripts/testing/test_imports.py
```

### 4. **Development**
```bash
# Start development server
python manage.py runserver

# Access applications
# Main app: http://localhost:8000
# Admin: http://localhost:8000/admin
# API: http://localhost:8000/api/
```

## 🔧 Configuration Files

### Environment Files
- `.env` - Main environment configuration
- `.env.example` - Template for environment variables

### Django Configuration
- `stockscanner_django/settings.py` - Main Django settings
- `stockscanner_django/urls.py` - URL routing

### Requirements
- `requirements.txt` - Python dependencies (Linux/Mac)
- `requirements-windows.txt` - Windows-specific dependencies

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| [README.md](../README.md) | 📖 Main project documentation |
| [WINDOWS_SETUP_GUIDE.md](../WINDOWS_SETUP_GUIDE.md) | 🪟 Windows installation guide |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 📁 This file - project organization |
| [YFINANCE_RATE_LIMIT_GUIDE.md](YFINANCE_RATE_LIMIT_GUIDE.md) | 📊 Rate limit optimizer guide |

## 🤝 Contributing

### Adding New Features
1. **Models**: Add to appropriate app (`stocks/`, `core/`, `emails/`)
2. **APIs**: Add to `*/api_views.py` files
3. **Tests**: Add to `tests/` directory
4. **Scripts**: Add to appropriate `scripts/` subdirectory

### Code Organization Guidelines
- **Setup scripts** → `scripts/setup/`
- **Test scripts** → `scripts/testing/`
- **Utility scripts** → `scripts/utils/`
- **Documentation** → `docs/`
- **Django apps** → Root level directories

## 🎯 Next Steps

1. **📊 Run Rate Limit Optimizer**: Optimize Yahoo Finance API performance
2. **🧪 Run Tests**: Validate all components work correctly
3. **🚀 Deploy**: Follow deployment guide for production
4. **📖 Read Docs**: Explore all documentation for advanced features

---

**📁 Clean, organized, and ready for development!** ✨