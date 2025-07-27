@echo off
echo ========================================
echo MANUAL MYSQL SETUP GUIDE
echo ========================================
echo.
echo MySQL Server is not installed on your system.
echo.
echo OPTION 1: Run the automatic installer
echo   install_mysql_and_setup.bat
echo.
echo OPTION 2: Manual installation (follow these steps)
echo.
echo [STEP 1] Download MySQL Server
echo   Go to: https://dev.mysql.com/downloads/installer/
echo   Download: mysql-installer-community-8.0.39.0.msi
echo.
echo [STEP 2] Install MySQL Server
echo   1. Run the downloaded mysql-installer.msi
echo   2. Choose "Server only" or "Developer Default"
echo   3. Set root password to: stockscanner123
echo   4. Complete the installation
echo   5. Ensure MySQL service is started
echo.
echo [STEP 3] Add MySQL to PATH (if needed)
echo   Add this to your PATH environment variable:
echo   C:\Program Files\MySQL\MySQL Server 8.0\bin
echo.
echo [STEP 4] Run database setup
echo   After MySQL is installed, run:
echo   setup_database_complete.bat
echo.
echo ========================================
echo.
echo Alternative: Use XAMPP (includes MySQL)
echo   1. Download XAMPP from: https://www.apachefriends.org/
echo   2. Install XAMPP
echo   3. Start MySQL service from XAMPP Control Panel
echo   4. Run: setup_database_complete.bat
echo.
echo ========================================
echo.
echo Quick Commands to Test MySQL:
echo   mysql --version
echo   mysql -u root -p
echo.
echo Once MySQL is working, your database will have:
echo - All required tables (stocks_stock, stocks_stockalert, etc.)
echo - All required fields (ticker, name, current_price, etc.)
echo - Sample stock data (AAPL, GOOGL, TSLA, MSFT, AMZN)
echo - Admin user (admin/admin123)
echo.
echo Press any key to continue...
pause > nul