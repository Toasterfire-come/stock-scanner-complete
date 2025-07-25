#!/bin/bash

# =============================================================================
# Stock Scanner Database Setup Script
# =============================================================================
# This script runs the interactive database setup

echo "🔧 Stock Scanner Database Setup"
echo "================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/Scripts/activate || source venv/bin/activate
fi

# Install required packages if needed
echo "📦 Ensuring required packages are installed..."
pip install psycopg2-binary getpass pathlib > /dev/null 2>&1

# Run the interactive setup
echo "🚀 Starting interactive database setup..."
python setup_database_interactive.py

echo ""
echo "✅ Database setup complete!"
echo "🚀 You can now run: python manage.py runserver"