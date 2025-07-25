#!/bin/bash

# =============================================================================
# Stock Scanner Django - Git Bash Startup Script
# =============================================================================
# This script is optimized for Git Bash on Windows

echo " Starting Stock Scanner Django Application (Git Bash)..."

# Check if we're in Git Bash
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$MINGW_PREFIX" ]]; then
echo " Git Bash detected"
else
echo " This script is optimized for Git Bash"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
echo " Creating virtual environment..."
python -m venv venv
fi

# Activate virtual environment (Git Bash style)
echo " Activating virtual environment..."
source venv/Scripts/activate

# Install dependencies
echo " Installing/updating dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
echo " No .env file found. Setting up database configuration..."
echo " Running interactive database setup..."
python setup_database_interactive.py

# Check if setup was successful
if [ ! -f ".env" ]; then
echo " Database setup was cancelled or failed."
echo " Creating basic .env file with SQLite as fallback..."
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-gitbash-development-key-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SCHEDULER_ENABLED=True
NASDAQ_UPDATE_INTERVAL=10
EOF
echo " Using SQLite for development. Run 'python setup_database_interactive.py' to configure PostgreSQL."
fi
fi

# Run migrations
echo " Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Check if superuser exists
echo " Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if User.objects.filter(is_superuser=True).exists():
print(' Superuser already exists')
else:
print(' No superuser found')
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(' Created superuser: admin/admin123')
" 2>/dev/null || {
echo " Creating superuser..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()
from django.contrib.auth.models import User
try:
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(' Created superuser: admin/admin123')
except:
print(' Superuser already exists')
"
}

# Load initial data if needed
echo " Checking NASDAQ data..."
python manage.py shell -c "
from stocks.models import Stock
count = Stock.objects.count()
if count == 0:
print(' Loading NASDAQ data...')
from django.core.management import call_command
call_command('load_nasdaq_only')
print(' NASDAQ data loaded')
else:
print(f' Found {count} stocks in database')
" 2>/dev/null || echo " Will load NASDAQ data on first admin access"

# Collect static files
echo " Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo " Setup complete!"
echo ""
echo " Starting Django development server..."
echo " Access your application at:"
echo " Main Dashboard: http://127.0.0.1:8000/"
echo " Admin Panel: http://127.0.0.1:8000/admin/"
echo " API Status: http://127.0.0.1:8000/api/admin/status/"
echo ""
echo " Login Credentials:"
echo " Username: admin"
echo " Password: admin123"
echo ""
echo " Press Ctrl+C to stop the server"
echo ""

# Start the development server
echo " Starting server..."
python manage.py runserver 127.0.0.1:8000