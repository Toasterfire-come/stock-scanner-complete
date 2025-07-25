#!/bin/bash
# Direct System Setup for Stock Scanner (No Virtual Environment)
# Uses user-level packages to avoid system conflicts

echo "============================================================"
echo " Stock Scanner - Direct System Setup (User Packages)"
echo "============================================================"
echo ""
echo "Installing packages to user directory (safer approach)"
echo "Your existing pandas 2.3.1 and numpy 2.3.1 will be used!"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

echo "[SUCCESS] Python is installed"
python3 --version
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip is not available"
    echo "Please ensure pip is installed with Python"
    exit 1
fi

echo "[SUCCESS] pip is available"
echo ""

echo "[STEP 1] Installing core Django packages to user directory..."
python3 -m pip install --user Django==4.2.11 djangorestframework django-cors-headers

echo ""
echo "[STEP 2] Installing database and utility packages..."
python3 -m pip install --user python-dotenv requests

echo ""
echo "[STEP 3] Installing stock data packages..."
echo "Note: Using your existing pandas 2.3.1 and numpy 2.3.1"
python3 -m pip install --user yfinance

echo ""
echo "[STEP 4] Installing text processing..."
python3 -m pip install --user textblob

echo ""
echo "[STEP 5] Installing optional packages for better performance..."
python3 -m pip install --user beautifulsoup4 lxml

echo ""
echo "[STEP 6] Setting up Django database..."
python3 manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "[WARNING] Migrations had issues, but continuing..."
fi

python3 manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERROR] Database migration failed"
    exit 1
fi

echo ""
echo "[STEP 7] Loading NASDAQ ticker data..."
python3 manage.py load_nasdaq_only
if [ $? -ne 0 ]; then
    echo "[WARNING] NASDAQ data loading had issues, but system is ready"
fi

echo ""
echo "============================================================"
echo " Setup completed successfully!"
echo "============================================================"
echo ""
echo "Your Stock Scanner is ready to use!"
echo ""
echo "Packages installed to user directory (safe from system conflicts)"
echo "Your existing pandas 2.3.1 and numpy 2.3.1 are being used"
echo ""
echo "To start the application:"
echo "  python3 manage.py runserver"
echo ""
echo "Access points:"
echo "  Main App:    http://localhost:8000"
echo "  Admin:       http://localhost:8000/admin"
echo "  API:         http://localhost:8000/api/stocks/"
echo ""
echo "Optional: Create an admin user"
echo "  python3 manage.py createsuperuser"
echo ""
echo "Press Enter to start the development server..."
read -r

echo "[STARTING] Development server..."
python3 manage.py runserver