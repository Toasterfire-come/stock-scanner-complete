@echo off
echo ========================================
echo MYSQL WORKBENCH CONFLICT RESOLVER
echo ========================================
echo.

echo MySQL Workbench often installs its own MySQL Server service
echo that conflicts with XAMPP MySQL on port 3306.
echo.

echo [STEP 1] Detecting MySQL Workbench and related services...
echo.

REM Check for MySQL Workbench installation
set WORKBENCH_FOUND=0
if exist "C:\Program Files\MySQL\MySQL Workbench*" (
    echo ✅ Found MySQL Workbench in Program Files
    set WORKBENCH_FOUND=1
)

if exist "C:\Program Files (x86)\MySQL\MySQL Workbench*" (
    echo ✅ Found MySQL Workbench in Program Files (x86)
    set WORKBENCH_FOUND=1
)

REM Check for MySQL Server installations
echo.
echo Checking for MySQL Server installations:
if exist "C:\Program Files\MySQL\MySQL Server*" (
    echo ✅ Found MySQL Server in Program Files
    dir "C:\Program Files\MySQL\MySQL Server*" /b
)

if exist "C:\ProgramData\MySQL" (
    echo ✅ Found MySQL data in ProgramData
)

echo.
echo [STEP 2] Checking MySQL services...
echo.

echo All MySQL-related services:
sc query | findstr /i mysql

echo.
echo Currently running MySQL services:
net start | findstr /i mysql

echo.
echo [STEP 3] Checking port 3306 usage...
echo.

echo Processes using port 3306:
netstat -ano | findstr :3306

echo.
echo Process details for port 3306:
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3306') do (
    echo.
    echo Process ID: %%a
    tasklist /fi "pid eq %%a" | findstr /v "INFO:"
)

echo.
echo [STEP 4] Solution options...
echo.

if %WORKBENCH_FOUND%==1 (
    echo MySQL Workbench detected on your system.
    echo.
) else (
    echo MySQL Workbench not found, but other MySQL services may exist.
    echo.
)

echo Choose your preferred solution:
echo.
echo [1] Stop MySQL Workbench services (Keep both, XAMPP priority)
echo [2] Disable MySQL Workbench services permanently  
echo [3] Change XAMPP MySQL to port 3307 (Both can run)
echo [4] Uninstall MySQL Server completely (XAMPP only)
echo [5] Configure MySQL Workbench to use XAMPP's MySQL
echo [0] Exit
echo.

set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto :stop_workbench_services
if "%choice%"=="2" goto :disable_workbench_services  
if "%choice%"=="3" goto :change_xampp_port
if "%choice%"=="4" goto :uninstall_mysql_server
if "%choice%"=="5" goto :configure_workbench_for_xampp
if "%choice%"=="0" goto :exit
goto :invalid_choice

:stop_workbench_services
echo.
echo ========================================
echo STOPPING MYSQL WORKBENCH SERVICES
echo ========================================
echo.

echo Stopping common MySQL Server services...
echo.

net stop MySQL80 2>nul && echo ✅ Stopped MySQL80
net stop MySQL57 2>nul && echo ✅ Stopped MySQL57
net stop MySQL56 2>nul && echo ✅ Stopped MySQL56
net stop MySQL 2>nul && echo ✅ Stopped MySQL
net stop mysqld 2>nul && echo ✅ Stopped mysqld

echo.
echo Checking if port 3306 is now free...
netstat -ano | findstr :3306 >nul
if %errorLevel% == 0 (
    echo ⚠️  Port 3306 still in use - may need to kill processes
    echo.
    echo Would you like to force-kill MySQL processes?
    set /p kill="Kill MySQL processes? (y/n): "
    if /i "%kill%"=="y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3306') do (
            echo Killing process %%a
            taskkill /pid %%a /f 2>nul
        )
    )
) else (
    echo ✅ Port 3306 is now free!
)

echo.
echo Now try starting XAMPP MySQL from the Control Panel.
echo.
goto :test_xampp

:disable_workbench_services
echo.
echo ========================================
echo DISABLING MYSQL WORKBENCH SERVICES
echo ========================================
echo.

echo This will disable MySQL services so they don't start automatically.
echo You can still use MySQL Workbench by connecting to XAMPP's MySQL.
echo.

echo Disabling MySQL services...
echo.

sc config MySQL80 start= disabled 2>nul && echo ✅ Disabled MySQL80
sc config MySQL57 start= disabled 2>nul && echo ✅ Disabled MySQL57
sc config MySQL56 start= disabled 2>nul && echo ✅ Disabled MySQL56
sc config MySQL start= disabled 2>nul && echo ✅ Disabled MySQL

echo.
echo Stopping any currently running services...
net stop MySQL80 2>nul
net stop MySQL57 2>nul  
net stop MySQL56 2>nul
net stop MySQL 2>nul

echo.
echo MySQL Workbench services are now disabled.
echo They won't start automatically with Windows.
echo.
echo To use MySQL Workbench with XAMPP:
echo 1. Start XAMPP MySQL first
echo 2. Connect Workbench to localhost:3306
echo 3. Username: root, Password: (empty)
echo.
goto :test_xampp

:change_xampp_port
echo.
echo ========================================
echo CHANGING XAMPP MYSQL TO PORT 3307
echo ========================================
echo.

echo This allows both MySQL Workbench and XAMPP to run simultaneously.
echo.

if not exist "C:\xampp\mysql\bin\my.ini" (
    echo ERROR: XAMPP MySQL configuration not found
    pause
    goto :main_menu
)

echo Backing up XAMPP MySQL configuration...
copy "C:\xampp\mysql\bin\my.ini" "C:\xampp\mysql\bin\my.ini.backup.workbench" >nul

echo.
echo Changing XAMPP MySQL to port 3307...
powershell -Command "(Get-Content 'C:\xampp\mysql\bin\my.ini') -replace 'port=3306', 'port=3307' | Set-Content 'C:\xampp\mysql\bin\my.ini'"

echo.
echo Updating Django settings for port 3307...
if exist "stockscanner_django\settings.py" (
    powershell -Command "(Get-Content 'stockscanner_django\settings.py') -replace \"'PORT': '3306'\", \"'PORT': '3307'\" | Set-Content 'stockscanner_django\settings.py'"
    echo Django settings updated
)

echo.
echo ========================================
echo CONFIGURATION COMPLETE
echo ========================================
echo.
echo XAMPP MySQL now uses port 3307
echo MySQL Workbench can use port 3306
echo.
echo Connection details for Django/XAMPP:
echo - Host: localhost
echo - Port: 3307
echo - Username: root  
echo - Password: (empty)
echo.
echo Connection details for MySQL Workbench:
echo - Host: localhost
echo - Port: 3306 (default)
echo - Your existing credentials
echo.
goto :test_xampp

:uninstall_mysql_server
echo.
echo ========================================
echo UNINSTALL MYSQL SERVER COMPLETELY
echo ========================================
echo.

echo ⚠️  WARNING: This will completely remove MySQL Server from your system.
echo MySQL Workbench will no longer have a local server to connect to.
echo You'll need to use XAMPP's MySQL for everything.
echo.

set /p confirm="Are you sure you want to uninstall MySQL Server? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo Operation cancelled
    pause
    goto :main_menu
)

echo.
echo Stopping MySQL services...
net stop MySQL80 2>nul
net stop MySQL57 2>nul
net stop MySQL56 2>nul
net stop MySQL 2>nul

echo.
echo Removing MySQL services...
sc delete MySQL80 2>nul && echo Removed MySQL80 service
sc delete MySQL57 2>nul && echo Removed MySQL57 service  
sc delete MySQL56 2>nul && echo Removed MySQL56 service
sc delete MySQL 2>nul && echo Removed MySQL service

echo.
echo ========================================
echo MANUAL CLEANUP REQUIRED
echo ========================================
echo.
echo To complete the uninstallation:
echo.
echo 1. Open Control Panel > Programs and Features
echo 2. Uninstall "MySQL Server" entries
echo 3. Delete folders:
echo    - C:\Program Files\MySQL
echo    - C:\Program Files (x86)\MySQL  
echo    - C:\ProgramData\MySQL
echo.
echo 4. Configure MySQL Workbench to connect to XAMPP:
echo    - Host: localhost
echo    - Port: 3306
echo    - Username: root
echo    - Password: (empty)
echo.

start appwiz.cpl
echo Programs and Features opened for manual uninstallation.
echo.
goto :test_xampp

:configure_workbench_for_xampp
echo.
echo ========================================
echo CONFIGURE WORKBENCH FOR XAMPP
echo ========================================
echo.

echo This will help you set up MySQL Workbench to use XAMPP's MySQL
echo instead of its own MySQL Server.
echo.

echo First, let's stop any conflicting MySQL services:
net stop MySQL80 2>nul
net stop MySQL57 2>nul
net stop MySQL56 2>nul
net stop MySQL 2>nul

echo.
echo ========================================
echo WORKBENCH CONNECTION SETUP
echo ========================================
echo.
echo 1. Start XAMPP MySQL first (if not already running)
echo 2. Open MySQL Workbench
echo 3. Create a new connection with these settings:
echo.
echo    Connection Name: XAMPP Local
echo    Hostname: localhost (or 127.0.0.1)
echo    Port: 3306
echo    Username: root
echo    Password: (leave empty)
echo.
echo 4. Test the connection
echo 5. Use this connection for all your database work
echo.

set /p openworkbench="Open MySQL Workbench now? (y/n): "
if /i "%openworkbench%"=="y" (
    echo Opening MySQL Workbench...
    start "MySQL Workbench" "C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" 2>nul
    if %errorLevel% neq 0 (
        start "MySQL Workbench" "C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" 2>nul
        if %errorLevel% neq 0 (
            echo Could not find MySQL Workbench executable
            echo Please open it manually from Start Menu
        )
    )
)

echo.
goto :test_xampp

:test_xampp
echo.
echo ========================================
echo TESTING XAMPP MYSQL
echo ========================================
echo.

echo Please try starting XAMPP MySQL now:
echo.
echo 1. Open XAMPP Control Panel
echo 2. Click START next to MySQL
echo 3. Look for green "Running" status
echo.

set /p success="Did XAMPP MySQL start successfully? (y/n): "

if /i "%success%"=="y" (
    echo.
    echo ✅ SUCCESS! XAMPP MySQL is now running.
    echo.
    echo Next steps:
    echo 1. Configure database: fix_xampp_mysql.bat
    echo 2. Set up Django: python manage.py migrate  
    echo 3. Start development: python manage.py runserver
    echo.
    echo If using MySQL Workbench:
    echo - Connect to localhost:3306 (or 3307 if changed)
    echo - Username: root
    echo - Password: (empty)
    echo.
) else (
    echo.
    echo ❌ XAMPP MySQL still not starting.
    echo.
    echo Additional steps to try:
    echo 1. Restart your computer
    echo 2. Run this script again
    echo 3. Try: quick_fix_mysql_crash.bat
    echo 4. Check XAMPP Control Panel logs
    echo.
)

pause
goto :exit

:invalid_choice
echo Invalid choice. Please enter a number between 0-5.
pause
goto :main_menu

:main_menu
cls
echo Choose your preferred solution:
echo.
echo [1] Stop MySQL Workbench services (Keep both, XAMPP priority)
echo [2] Disable MySQL Workbench services permanently  
echo [3] Change XAMPP MySQL to port 3307 (Both can run)
echo [4] Uninstall MySQL Server completely (XAMPP only)
echo [5] Configure MySQL Workbench to use XAMPP's MySQL
echo [0] Exit
echo.

set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto :stop_workbench_services
if "%choice%"=="2" goto :disable_workbench_services  
if "%choice%"=="3" goto :change_xampp_port
if "%choice%"=="4" goto :uninstall_mysql_server
if "%choice%"=="5" goto :configure_workbench_for_xampp
if "%choice%"=="0" goto :exit
goto :invalid_choice

:exit
echo.
echo Press any key to exit...
pause >nul