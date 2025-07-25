#!/bin/bash
echo "============================================================"
echo " 🚀 Starting Stock Scanner"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run setup first or create venv manually."
    exit 1
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Starting Django development server..."
echo ""
echo "Access points:"
echo " - Main App: http://localhost:8000"
echo " - Admin:    http://localhost:8000/admin"
echo " - API:      http://localhost:8000/api/stocks/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver

echo ""
echo "Server stopped."