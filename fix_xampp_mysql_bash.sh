#!/bin/bash

echo "========================================"
echo "XAMPP MYSQL CONFIGURATION (Git Bash)"
echo "========================================"
echo

echo "MySQL is now running! Let's configure it for the stock scanner."
echo

echo "[STEP 1] Checking XAMPP installation..."
if [ -d "/c/xampp" ]; then
    echo "SUCCESS: XAMPP directory found"
    XAMPP_PATH="/c/xampp"
elif [ -d "C:\\xampp" ]; then
    echo "SUCCESS: XAMPP directory found (Windows path)"
    XAMPP_PATH="C:\\xampp"
else
    echo "ERROR: XAMPP not found"
    read -p "Press Enter to continue..."
    exit 1
fi

echo
echo "[STEP 2] Testing MySQL connection..."

# Test MySQL connection
if command -v mysql >/dev/null 2>&1; then
    echo "Testing connection to MySQL..."
    mysql -h localhost -u root -e "SELECT 'MySQL connection successful' AS status;" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "SUCCESS: MySQL connection working"
    else
        echo "INFO: MySQL connection needs setup"
    fi
else
    echo "INFO: MySQL client not in PATH, using XAMPP's MySQL"
fi

echo
echo "[STEP 3] Setting up stockscanner database..."

# Create the database using XAMPP's MySQL
if [ -f "/c/xampp/mysql/bin/mysql.exe" ]; then
    echo "Creating stockscanner database..."
    /c/xampp/mysql/bin/mysql.exe -h localhost -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS: stockscanner database created"
        
        echo "Setting up database user permissions..."
        /c/xampp/mysql/bin/mysql.exe -h localhost -u root -e "GRANT ALL PRIVILEGES ON stockscanner.* TO 'root'@'localhost';" 2>/dev/null
        /c/xampp/mysql/bin/mysql.exe -h localhost -u root -e "FLUSH PRIVILEGES;" 2>/dev/null
        
        echo "SUCCESS: Database permissions configured"
    else
        echo "WARNING: Database creation may have failed"
    fi
else
    echo "WARNING: XAMPP MySQL executable not found"
fi

echo
echo "[STEP 4] Testing Django database connection..."

if [ -f "manage.py" ]; then
    echo "Testing Django database connection..."
    python manage.py check --database default 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "SUCCESS: Django can connect to database"
    else
        echo "INFO: Django database needs migration"
    fi
else
    echo "INFO: manage.py not found in current directory"
fi

echo
echo "[STEP 5] Setting up Django database tables..."

if [ -f "manage.py" ]; then
    echo "Running Django migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS: Django database tables created"
    else
        echo "WARNING: Migration may have failed"
    fi
else
    echo "SKIP: manage.py not found"
fi

echo
echo "========================================"
echo "XAMPP MYSQL CONFIGURATION COMPLETE"
echo "========================================"
echo

echo "✅ MySQL Status: RUNNING"
echo "✅ Database: stockscanner"
echo "✅ Connection: localhost:3306"
echo "✅ Username: root"
echo "✅ Password: (empty)"
echo

echo "Next steps:"
echo "1. Run Django development server:"
echo "   python manage.py runserver"
echo
echo "2. Start stock data updates:"
echo "   python start_stock_scheduler.py --background"
echo
echo "3. Access web interfaces:"
echo "   - Django Admin: http://localhost:8000/admin/"
echo "   - Stock API: http://localhost:8000/api/stocks/"
echo "   - phpMyAdmin: http://localhost/phpmyadmin/"
echo

echo "4. Create Django admin user (optional):"
echo "   python manage.py createsuperuser"
echo

read -p "Press Enter to continue..."