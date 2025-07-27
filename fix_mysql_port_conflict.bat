@echo off
echo ========================================
echo MYSQL PORT 3306 CONFLICT RESOLVER
echo ========================================
echo.

echo The error indicates another MySQL service is using port 3306.
echo This script will help identify and resolve the conflict.
echo.

echo [STEP 1] Checking what's using port 3306...
echo.

REM Check what's using port 3306
echo Finding process using port 3306:
netstat -ano | findstr :3306
echo.

echo Detailed port information:
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3306') do (
    echo Process ID: %%a
    tasklist /fi "pid eq %%a" 2>nul | findstr /v "INFO:"
)
echo.

echo [STEP 2] Checking for MySQL services...
echo.

echo Installed MySQL services:
sc query | findstr /i mysql
echo.

echo MySQL service status:
net start | findstr /i mysql
echo.

echo [STEP 3] Solutions Available...
echo.
echo Choose your preferred solution:
echo.
echo [1] Stop conflicting MySQL services (Recommended)
echo [2] Change XAMPP MySQL port to 3307
echo [3] Uninstall conflicting MySQL services
echo [4] Kill processes using port 3306 (Advanced)
echo [5] View detailed diagnosis
echo [0] Exit
echo.

set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto :stop_mysql_services
if "%choice%"=="2" goto :change_xampp_port
if "%choice%"=="3" goto :uninstall_mysql
if "%choice%"=="4" goto :kill_processes
if "%choice%"=="5" goto :detailed_diagnosis
if "%choice%"=="0" goto :exit
goto :invalid_choice

:stop_mysql_services
echo.
echo ========================================
echo STOPPING MYSQL SERVICES
echo ========================================
echo.

echo Attempting to stop MySQL services...
echo.

REM Common MySQL service names
net stop MySQL80 2>nul && echo SUCCESS: Stopped MySQL80
net stop MySQL57 2>nul && echo SUCCESS: Stopped MySQL57
net stop MySQL56 2>nul && echo SUCCESS: Stopped MySQL56
net stop MySQL 2>nul && echo SUCCESS: Stopped MySQL
net stop mysqld 2>nul && echo SUCCESS: Stopped mysqld

echo.
echo Checking if port 3306 is now free...
netstat -ano | findstr :3306
if %errorLevel% == 0 (
    echo WARNING: Port 3306 is still in use
    echo You may need to kill specific processes or reboot
) else (
    echo SUCCESS: Port 3306 is now free!
    echo.
    echo Now try starting XAMPP MySQL:
    echo 1. Open XAMPP Control Panel
    echo 2. Click START next to MySQL
    echo 3. Wait for green "Running" status
)

echo.
echo To prevent services from starting automatically:
echo 1. Open Services (services.msc)
echo 2. Find MySQL services
echo 3. Set Startup Type to "Manual" or "Disabled"
echo.

pause
goto :restart_test

:change_xampp_port
echo.
echo ========================================
echo CHANGING XAMPP MYSQL PORT TO 3307
echo ========================================
echo.

if not exist "C:\xampp\mysql\bin\my.ini" (
    echo ERROR: XAMPP MySQL configuration not found
    echo Make sure XAMPP is installed at C:\xampp
    pause
    goto :main_menu
)

echo Backing up original configuration...
copy "C:\xampp\mysql\bin\my.ini" "C:\xampp\mysql\bin\my.ini.backup" >nul
echo Backup created: my.ini.backup

echo.
echo Modifying MySQL configuration to use port 3307...

REM Create new configuration with port 3307
powershell -Command "(Get-Content 'C:\xampp\mysql\bin\my.ini') -replace 'port=3306', 'port=3307' | Set-Content 'C:\xampp\mysql\bin\my.ini'"

echo.
echo Updating Django settings for port 3307...

if exist "stockscanner_django\settings.py" (
    powershell -Command "(Get-Content 'stockscanner_django\settings.py') -replace \"'PORT': '3306'\", \"'PORT': '3307'\" | Set-Content 'stockscanner_django\settings.py'"
    echo Django settings updated for port 3307
)

echo.
echo ========================================
echo CONFIGURATION COMPLETE
echo ========================================
echo.
echo Changes made:
echo - XAMPP MySQL now uses port 3307
echo - Django configured for port 3307
echo - Original config backed up as my.ini.backup
echo.
echo Next steps:
echo 1. Restart XAMPP Control Panel
echo 2. Start MySQL (should work on port 3307)
echo 3. Update any other applications to use port 3307
echo.
echo Connection details for other apps:
echo - Host: localhost
echo - Port: 3307
echo - Username: root
echo - Password: (empty by default)
echo.

pause
goto :restart_test

:uninstall_mysql
echo.
echo ========================================
echo UNINSTALL CONFLICTING MYSQL SERVICES
echo ========================================
echo.

echo WARNING: This will permanently remove MySQL services from your system.
echo Only proceed if you want to use XAMPP as your only MySQL installation.
echo.
set /p confirm="Are you sure you want to uninstall MySQL services? (y/n): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled
    pause
    goto :main_menu
)

echo.
echo Stopping and removing MySQL services...
echo.

REM Stop and remove common MySQL services
sc stop MySQL80 2>nul
sc delete MySQL80 2>nul && echo Removed: MySQL80

sc stop MySQL57 2>nul
sc delete MySQL57 2>nul && echo Removed: MySQL57

sc stop MySQL56 2>nul
sc delete MySQL56 2>nul && echo Removed: MySQL56

sc stop MySQL 2>nul
sc delete MySQL 2>nul && echo Removed: MySQL

echo.
echo Services removal complete.
echo You may also want to:
echo 1. Uninstall MySQL from Control Panel > Programs
echo 2. Delete MySQL folders from Program Files
echo 3. Clean registry entries (use CCleaner or similar)
echo.

pause
goto :restart_test

:kill_processes
echo.
echo ========================================
echo KILLING PROCESSES USING PORT 3306
echo ========================================
echo.

echo WARNING: This will forcefully terminate processes using port 3306.
echo This may cause data loss if databases are running.
echo.
set /p confirm="Are you sure you want to kill processes? (y/n): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled
    pause
    goto :main_menu
)

echo.
echo Finding and killing processes on port 3306...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3306') do (
    echo Killing process ID: %%a
    taskkill /pid %%a /f 2>nul
)

echo.
echo Process termination complete.
echo.

pause
goto :restart_test

:detailed_diagnosis
echo.
echo ========================================
echo DETAILED SYSTEM DIAGNOSIS
echo ========================================
echo.

echo === PORT 3306 USAGE ===
netstat -ano | findstr :3306
echo.

echo === MYSQL PROCESSES ===
tasklist | findstr /i mysql
echo.

echo === MYSQL SERVICES ===
sc query | findstr /i mysql
echo.

echo === RUNNING MYSQL SERVICES ===
net start | findstr /i mysql
echo.

echo === XAMPP MYSQL STATUS ===
if exist "C:\xampp\mysql\bin\mysqld.exe" (
    echo XAMPP MySQL binary: Found
) else (
    echo XAMPP MySQL binary: NOT FOUND
)

if exist "C:\xampp\mysql\bin\my.ini" (
    echo XAMPP MySQL config: Found
    echo Config port setting:
    findstr /i "port" "C:\xampp\mysql\bin\my.ini"
) else (
    echo XAMPP MySQL config: NOT FOUND
)
echo.

echo === SYSTEM MYSQL INSTALLATIONS ===
if exist "C:\Program Files\MySQL" (
    echo MySQL installation found in Program Files:
    dir "C:\Program Files\MySQL" /b
)

if exist "C:\Program Files (x86)\MySQL" (
    echo MySQL installation found in Program Files (x86):
    dir "C:\Program Files (x86)\MySQL" /b
)
echo.

echo Press any key to return to main menu...
pause >nul
goto :main_menu

:restart_test
echo.
echo ========================================
echo TESTING XAMPP MYSQL
echo ========================================
echo.

echo Please now try to start XAMPP MySQL:
echo.
echo 1. Open XAMPP Control Panel
echo 2. Click START next to MySQL
echo 3. Check if it shows green "Running" status
echo.

set /p success="Did XAMPP MySQL start successfully? (y/n): "

if /i "%success%"=="y" (
    echo.
    echo SUCCESS! XAMPP MySQL is now running.
    echo.
    echo Next steps:
    echo 1. Run: fix_xampp_mysql.bat
    echo 2. Set up Django: python manage.py migrate
    echo 3. Start server: python manage.py runserver
    echo.
) else (
    echo.
    echo If MySQL still won't start, try:
    echo 1. Restart your computer
    echo 2. Run this script again
    echo 3. Choose option 2 to change port to 3307
    echo 4. Check Windows Event Viewer for MySQL errors
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
goto :start

:exit
echo.
echo Script complete. Press any key to exit...
pause >nul

:start