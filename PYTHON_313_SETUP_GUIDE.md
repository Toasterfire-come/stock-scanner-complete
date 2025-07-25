# 🐍 Python 3.13 Windows Setup Guide

## Your Current Situation
You're running Python 3.13 on Windows and encountered a pandas compilation error. The good news is you already have pandas 2.3.1 installed, which is compatible with Python 3.13!

## Quick Fix - Manual Setup

Since you already have pandas and numpy installed, follow these steps:

### Step 1: Create Virtual Environment
```bash
# In Git Bash or Command Prompt
python -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
# In Git Bash
source venv/Scripts/activate

# In Command Prompt
venv\Scripts\activate.bat
```

### Step 3: Install Core Packages (Skip pandas/numpy)
```bash
pip install Django>=4.2.11 djangorestframework>=3.14.0 django-cors-headers>=4.3.1
pip install PyMySQL>=1.1.0 dj-database-url>=2.1.0 python-dotenv>=1.0.0
pip install yfinance>=0.2.25 requests>=2.31.0
pip install textblob>=0.17.1 cryptography>=41.0.0
```

### Step 4: Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Load NASDAQ Data
```bash
python manage.py load_nasdaq_only
```

### Step 7: Start the Server
```bash
python manage.py runserver
```

## Alternative: Use the New Setup Script

Run the new Python 3.13 compatible setup script:
```bash
windows_setup_python313.bat
```

## Accessing the Application

- **Main Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/stocks/

## Package Compatibility Notes

✅ **Working with Python 3.13**:
- pandas 2.3.1 (you already have this)
- numpy 2.3.1 (you already have this)
- Django 4.2+
- yfinance 0.2.25+

❌ **Not Compatible**:
- pandas 2.0.3 (causes compilation errors)
- numpy 1.24.x (too old)

## Troubleshooting

### If yfinance fails to install:
```bash
pip install yfinance --no-cache-dir
```

### If MySQL connection fails:
The project uses SQLite by default for development, so MySQL is not required initially.

### If pandas errors persist:
Your system pandas 2.3.1 should work fine. The error was from trying to install an older incompatible version.

## Next Steps

1. **Test the Application**: Visit http://localhost:8000
2. **Load Sample Data**: The NASDAQ loader will populate your database
3. **Explore the API**: Try http://localhost:8000/api/stocks/
4. **Admin Interface**: Create a superuser and explore http://localhost:8000/admin

## Development Workflow

```bash
# Activate environment (do this each time)
source venv/Scripts/activate  # Git Bash
# or
venv\Scripts\activate.bat     # Command Prompt

# Start development server
python manage.py runserver

# Run migrations (when models change)
python manage.py makemigrations
python manage.py migrate

# Update stock data
python manage.py load_nasdaq_only --update-existing
```