#!/bin/bash

# =============================================================================
# Stock Scanner Django Quick Start Script
# =============================================================================
# This script helps you quickly start the Django application for development

echo "🚀 Starting Stock Scanner Django Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    if [ -f ".env.production" ]; then
        cp .env.production .env
        echo "📝 Please edit .env file with your settings"
        echo "🔑 Generate a secret key with: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    else
        echo "🔧 Creating basic .env file..."
        cat > .env << EOF
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SCHEDULER_ENABLED=True
NASDAQ_UPDATE_INTERVAL=10
EOF
    fi
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Check if superuser exists, if not prompt to create one
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one:')
    exit(1)
" 2>/dev/null || {
    echo "🔐 Creating superuser..."
    python manage.py createsuperuser
}

# Load initial data if needed
echo "📊 Loading initial NASDAQ data (if needed)..."
python manage.py shell -c "
from stocks.models import Stock
if Stock.objects.count() == 0:
    print('Loading NASDAQ data...')
    from django.core.management import call_command
    call_command('load_nasdaq_only')
else:
    print(f'Found {Stock.objects.count()} stocks in database')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Django development server..."
echo "📱 Access the application at: http://127.0.0.1:8000/"
echo "🔧 Admin panel at: http://127.0.0.1:8000/admin/"
echo "📊 API status at: http://127.0.0.1:8000/api/admin/status/"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the development server
python manage.py runserver 0.0.0.0:8000