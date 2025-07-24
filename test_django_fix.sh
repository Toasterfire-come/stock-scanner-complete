#!/bin/bash

echo "🔧 Testing Django after indentation fix..."

cd "$(dirname "${BASH_SOURCE[0]}")"

# Activate virtual environment
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Test Django settings
echo "🔍 Testing Django settings..."
if python manage.py check 2>&1; then
    echo "✅ Django settings are valid"
else
    echo "❌ Django settings have issues"
    exit 1
fi

# Try to make migrations
echo "📋 Creating migrations..."
if python manage.py makemigrations 2>&1; then
    echo "✅ Migrations created successfully"
else
    echo "⚠️  Migration creation had issues"
fi

# Try to migrate
echo "🗄️  Running migrations..."
if python manage.py migrate 2>&1; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️  Migration had issues"
fi

# Test server startup (just check, don't start)
echo "🌐 Testing server startup..."
if timeout 5s python manage.py runserver --dry-run 2>/dev/null || python manage.py check --deploy 2>/dev/null; then
    echo "✅ Server startup test passed"
else
    echo "⚠️  Server startup test had issues"
fi

echo ""
echo "🎉 Django fix test completed!"
echo ""
echo "🚀 If all tests passed, you can now start the server:"
echo "   ./start_gitbash.sh"
echo "   OR"
echo "   source venv/Scripts/activate && python manage.py runserver"