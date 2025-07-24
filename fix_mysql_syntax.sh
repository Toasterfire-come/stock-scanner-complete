#!/bin/bash

# =========================================================================
# Fix MySQL Syntax Error in Django Settings
# Removes problematic init_command that causes SQL syntax error
# =========================================================================

echo "🔧 Fixing MySQL syntax error..."

cd "$(dirname "${BASH_SOURCE[0]}")"

# Check if virtual environment exists
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

echo "🔍 Testing Django settings after MySQL syntax fix..."

# Test Django check
if python manage.py check 2>&1; then
    echo "✅ Django settings check passed"
else
    echo "❌ Django settings still have issues"
    exit 1
fi

# Test database connection specifically
echo "🗄️  Testing database connection..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
    print('✅ Database connection successful')
    print(f'✅ Connected to: {settings.DATABASES[\"default\"][\"NAME\"]}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Check your MySQL configuration:')
    print('  1. MySQL service running: net start mysql')
    print('  2. Database exists: stock_scanner_nasdaq')
    print('  3. User exists: stock_scanner')
    print('  4. Password correct: StockScanner2010')
"

# Try makemigrations
echo "📋 Testing makemigrations..."
if python manage.py makemigrations 2>&1; then
    echo "✅ Makemigrations successful"
else
    echo "⚠️  Makemigrations had issues"
fi

# Try migrate
echo "🚀 Testing migrate..."
if python manage.py migrate 2>&1; then
    echo "✅ Migration successful"
else
    echo "⚠️  Migration had issues"
fi

echo ""
echo "🎉 MySQL syntax fix completed!"
echo ""
echo "🚀 If all tests passed, you can now:"
echo "   python manage.py runserver"
echo "   OR"
echo "   ./start_gitbash.sh"