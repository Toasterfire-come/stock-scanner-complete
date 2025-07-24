@echo off
echo 🚀 Stock Scanner MySQL Setup for Windows
echo ==========================================

echo.
echo 🔧 Starting MySQL service...
net start mysql
if errorlevel 1 (
    echo ⚠️  Trying alternative service names...
    net start mysql80
    if errorlevel 1 net start mysql84
)

echo.
echo 🔧 Configuring MySQL database...
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'StockScannerPass2024';"
mysql -u root -e "FLUSH PRIVILEGES;"
mysql -u root -pStockScannerPass2024 -e "CREATE DATABASE IF NOT EXISTS stock_scanner_db;"
mysql -u root -pStockScannerPass2024 -e "CREATE USER IF NOT EXISTS 'stock_scanner_user'@'localhost' IDENTIFIED BY 'StockScannerPass2024';"
mysql -u root -pStockScannerPass2024 -e "GRANT ALL PRIVILEGES ON stock_scanner_db.* TO 'stock_scanner_user'@'localhost';"
mysql -u root -pStockScannerPass2024 -e "FLUSH PRIVILEGES;"

echo.
echo ✅ MySQL setup complete!
echo.
echo 📋 Database Information:
echo   Database: stock_scanner_db
echo   User: stock_scanner_user
echo   Password: StockScannerPass2024
echo   Host: localhost
echo   Port: 3306
echo.
echo 🚀 Next steps:
echo   1. venv\Scripts\activate
echo   2. pip install -r requirements.txt
echo   3. python manage.py migrate
echo   4. python manage.py createsuperuser
echo   5. python manage.py runserver
echo.
pause
