#!/bin/bash

echo "🚀 Starting Stock Scanner Admin Console..."

# Activate virtual environment
source venv/bin/activate

# Check Django configuration
echo "🔧 Checking Django configuration..."
python manage.py check

# Run migrations (safe to run multiple times)
echo "📊 Applying database migrations..."
python manage.py migrate --run-syncdb

# Start the Django development server
echo "🌐 Starting Django server..."
echo "📱 Admin Dashboard: http://localhost:8000/admin-dashboard/"
echo "📈 WordPress Stocks: http://localhost:8000/wordpress-stocks/"
echo "📰 WordPress News: http://localhost:8000/wordpress-news/"
echo "⚙️ Django Admin: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"

python manage.py runserver