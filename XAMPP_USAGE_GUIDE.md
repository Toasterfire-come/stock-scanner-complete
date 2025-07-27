# XAMPP Integration Guide for Stock Scanner

## Overview
The Stock Scanner now automatically detects and configures for XAMPP MySQL. All Django commands work seamlessly with XAMPP without additional configuration.

## Quick Setup
1. Install XAMPP: `setup_xampp_complete.bat`
2. Use any Django command normally - XAMPP is auto-detected!

## Auto-Detection Features
- Automatically detects XAMPP at `C:\xampp`
- Adds XAMPP MySQL to PATH automatically
- Configures Django settings for XAMPP MySQL (no password)
- Sets up PyMySQL compatibility layer

## Standard Django Commands (All work with XAMPP)

### Server Commands
```bash
# Start development server (auto-detects XAMPP)
python manage.py runserver

# Start on different port
python manage.py runserver 8080

# Using the XAMPP wrapper (optional)
django_xampp.bat runserver
```

### Database Commands
```bash
# Apply migrations (works with XAMPP MySQL)
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations stocks

# Reset migrations and recreate
python manage.py makemigrations --empty stocks
```

### Admin Commands
```bash
# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Stock Scanner Specific Commands
```bash
# Update stock data (XAMPP-compatible)
python manage.py update_stocks_yfinance

# Update specific stocks
python manage.py update_stocks_yfinance --symbols AAPL,GOOGL,TSLA

# Update with limit
python manage.py update_stocks_yfinance --limit 500

# Start scheduler mode
python manage.py update_stocks_yfinance --schedule
```

## XAMPP-Specific Commands

### Using the Django XAMPP Wrapper
```bash
# Wrapper that ensures XAMPP paths are set
django_xampp.bat runserver
django_xampp.bat migrate
django_xampp.bat makemigrations
django_xampp.bat shell
django_xampp.bat createsuperuser
```

### XAMPP Management Commands
```bash
# Start everything with XAMPP-optimized settings
start_server_xampp.bat

# Start stock scheduler with XAMPP
start_scheduler_xampp.bat

# Open database management tools
manage_database_xampp.bat

# Test XAMPP setup
test_xampp_setup.bat
```

## Configuration Details

### Automatic XAMPP Detection
The system automatically detects XAMPP by checking:
- `C:\xampp` directory exists
- `C:\xampp\mysql\bin` directory exists
- Automatically adds XAMPP MySQL to PATH

### Database Configuration
When XAMPP is detected, Django automatically uses:
- **Host:** localhost
- **Port:** 3306  
- **Username:** root
- **Password:** (empty - XAMPP default)
- **Database:** stockscanner

### Manual Environment Override
You can override XAMPP auto-detection using environment variables:
```bash
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_password
set DB_NAME=stockscanner
```

## Web Interfaces

### Django Interfaces
- **Development Server:** http://127.0.0.1:8000/
- **WordPress API:** http://127.0.0.1:8000/api/wordpress/
- **Stock API:** http://127.0.0.1:8000/api/stocks/
- **Django Admin:** http://127.0.0.1:8000/admin/ (admin/admin123)

### XAMPP Interfaces
- **XAMPP Control Panel:** `C:\xampp\xampp-control.exe`
- **phpMyAdmin:** http://localhost/phpmyadmin
- **Apache:** http://localhost

## Troubleshooting

### If Django commands don't work:
1. Ensure XAMPP is installed at `C:\xampp`
2. Start MySQL service in XAMPP Control Panel
3. Use the wrapper: `django_xampp.bat <command>`

### If database connection fails:
1. Check XAMPP Control Panel - MySQL should be green/running
2. Visit phpMyAdmin to verify MySQL is working
3. Ensure `stockscanner` database exists

### If migrations fail:
```bash
# Reset and recreate database
python manage.py flush
python manage.py migrate
```

## Complete Workflow

### Daily Usage
1. **Start XAMPP:** Open XAMPP Control Panel, start Apache and MySQL
2. **Run Server:** `python manage.py runserver` (auto-detects XAMPP)
3. **Update Stocks:** `start_scheduler_xampp.bat` (background updates)
4. **Manage Database:** Visit http://localhost/phpmyadmin

### Development Workflow
1. **Make Model Changes:** Edit models in `stocks/models.py`
2. **Create Migrations:** `python manage.py makemigrations`
3. **Apply Migrations:** `python manage.py migrate`
4. **Test Changes:** `python manage.py runserver`

## Important Notes

- **No virtual environment needed** - all commands work with system Python
- **XAMPP auto-detection** - no manual configuration required
- **All original Django commands work** - no need to change your workflow
- **Fallback support** - works with standard MySQL if XAMPP not detected
- **Always keep XAMPP Control Panel open** when developing

## Quick Reference

| Task | Command |
|------|---------|
| Start server | `python manage.py runserver` |
| Update database | `python manage.py migrate` |
| Create admin user | `python manage.py createsuperuser` |
| Update stocks | `python manage.py update_stocks_yfinance` |
| Start scheduler | `start_scheduler_xampp.bat` |
| Manage database | http://localhost/phpmyadmin |
| XAMPP control | `C:\xampp\xampp-control.exe` |

The system is designed to "just work" with XAMPP - use Django commands normally and XAMPP integration happens automatically!