# 🔧 Scripts Directory

This directory contains organized utility scripts for the Stock Scanner project.

## 📁 Directory Structure

```
scripts/
├── setup/          # Installation and setup scripts
├── testing/        # Testing and validation scripts
├── utils/          # Utility and maintenance scripts
└── README.md       # This file
```

## 🚀 Quick Reference

### Setup Scripts
```bash
# Windows installation with fixes
python scripts/setup/windows_fix_install.py

# Database migrations
python scripts/setup/run_migrations.py

# Redis setup for Windows
python scripts/setup/setup_redis_windows.py
```

### Testing Scripts
```bash
# Django startup test
python scripts/testing/test_django_startup.py

# YFinance API test
python scripts/testing/test_yfinance_system.py

# Redis dependency test
python scripts/testing/test_redis_fix.py
```

### Utility Scripts
```bash
# Rate limit optimizer (⭐ FEATURED)
python scripts/utils/yahoo_rate_limit_optimizer.py

# Enable Celery Beat
python scripts/utils/enable_celery_beat.py

# Check code syntax
python scripts/utils/check_syntax.py
```

## 📚 Documentation

- [Project Structure Guide](../docs/PROJECT_STRUCTURE.md)
- [Rate Limit Optimizer Guide](../docs/YFINANCE_RATE_LIMIT_GUIDE.md)
- [Windows Setup Guide](../WINDOWS_SETUP_GUIDE.md)