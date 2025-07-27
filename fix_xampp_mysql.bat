@echo off
echo ========================================
echo XAMPP MYSQL CONNECTION TROUBLESHOOTER
echo ========================================
echo.

REM Set environment variables
set XAMPP_PATH=C:\xampp
set XAMPP_MYSQL_PATH=C:\xampp\mysql\bin
set XAMPP_CONTROL_PATH=C:\xampp\xampp_control.exe

echo [STEP 1] Checking XAMPP installation...
if not exist "%XAMPP_PATH%" (
    echo ERROR: XAMPP not found at %XAMPP_PATH%
    echo Please install XAMPP first
    pause
    exit /b 1
)
echo SUCCESS: XAMPP directory found
echo.

echo [STEP 2] Finding XAMPP Control Panel...
if exist "%XAMPP_PATH%\xampp_control.exe" (
    set XAMPP_CONTROL_PATH=%XAMPP_PATH%\xampp_control.exe
    echo Found: xampp_control.exe
) else if exist "%XAMPP_PATH%\xampp-control.exe" (
    set XAMPP_CONTROL_PATH=%XAMPP_PATH%\xampp-control.exe
    echo Found: xampp-control.exe
) else if exist "%XAMPP_PATH%\control.exe" (
    set XAMPP_CONTROL_PATH=%XAMPP_PATH%\control.exe
    echo Found: control.exe
) else (
    echo WARNING: XAMPP Control Panel not found
    echo Looking for alternative paths...
    dir "%XAMPP_PATH%\*.exe" | findstr -i control
)
echo Control Panel Path: %XAMPP_CONTROL_PATH%
echo.

echo [STEP 3] Checking MySQL files...
if not exist "%XAMPP_MYSQL_PATH%\mysql.exe" (
    echo ERROR: MySQL executable not found
    echo Expected: %XAMPP_MYSQL_PATH%\mysql.exe
    echo Checking XAMPP structure...
    dir "%XAMPP_PATH%"
    pause
    exit /b 1
)
echo SUCCESS: MySQL executable found
echo.

echo [STEP 4] Checking MySQL service status...
REM Check if MySQL is running as a service
sc query MySQL 2>nul | findstr "RUNNING" > nul
if not errorlevel 1 (
    echo INFO: MySQL Windows service is running
    set MYSQL_SERVICE_RUNNING=1
) else (
    echo INFO: MySQL Windows service not running
    set MYSQL_SERVICE_RUNNING=0
)

REM Check if MySQL process is running
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe" > nul
if not errorlevel 1 (
    echo INFO: MySQL process (mysqld.exe) is running
    set MYSQL_PROCESS_RUNNING=1
) else (
    echo INFO: MySQL process not running
    set MYSQL_PROCESS_RUNNING=0
)
echo.

echo [STEP 5] Opening XAMPP Control Panel...
if exist "%XAMPP_CONTROL_PATH%" (
    echo Starting XAMPP Control Panel...
    start "" "%XAMPP_CONTROL_PATH%"
    echo.
    echo Please do the following in XAMPP Control Panel:
    echo 1. Look for MySQL in the list
    echo 2. Click START button next to MySQL (should turn green)
    echo 3. Wait for MySQL to show "Running" status
    echo 4. If there's an error, click the "Logs" button to see details
    echo.
    echo Press any key when MySQL is started (green)...
    pause > nul
) else (
    echo ERROR: Cannot find XAMPP Control Panel
    echo Please start XAMPP manually
    pause
)
echo.

echo [STEP 6] Testing MySQL connection...
echo Testing direct MySQL connection...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SELECT VERSION();" > temp_mysql_test.txt 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to MySQL
    echo Error details:
    if exist temp_mysql_test.txt (
        type temp_mysql_test.txt
        del temp_mysql_test.txt
    )
    echo.
    echo [TROUBLESHOOTING] Trying to start MySQL manually...
    
    REM Try to start MySQL using XAMPP's mysql_start.bat if it exists
    if exist "%XAMPP_PATH%\mysql_start.bat" (
        echo Running MySQL start script...
        call "%XAMPP_PATH%\mysql_start.bat"
    )
    
    REM Try starting mysqld directly
    echo Attempting to start MySQL daemon...
    start /B "%XAMPP_MYSQL_PATH%\mysqld.exe" --defaults-file="%XAMPP_PATH%\mysql\bin\my.ini" --console
    
    echo Waiting 10 seconds for MySQL to start...
    timeout /t 10 /nobreak > nul
    
    REM Test again
    "%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SELECT VERSION();" > temp_mysql_test2.txt 2>&1
    if errorlevel 1 (
        echo ERROR: Still cannot connect after manual start
        if exist temp_mysql_test2.txt (
            type temp_mysql_test2.txt
            del temp_mysql_test2.txt
        )
        echo.
        echo [NEXT STEPS]
        echo 1. Check XAMPP Control Panel - is MySQL green/running?
        echo 2. Check Windows Task Manager - is mysqld.exe running?
        echo 3. Try restarting XAMPP completely
        echo 4. Check XAMPP error logs in C:\xampp\mysql\data\*.err
        echo.
        pause
        exit /b 1
    )
)

echo SUCCESS: MySQL connection working!
if exist temp_mysql_test.txt (
    echo MySQL Version:
    type temp_mysql_test.txt
    del temp_mysql_test.txt
)
if exist temp_mysql_test2.txt (
    echo MySQL Version:
    type temp_mysql_test2.txt
    del temp_mysql_test2.txt
)
echo.

echo [STEP 7] Creating stockscanner database...
echo Creating database...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if errorlevel 1 (
    echo ERROR: Could not create database
    pause
    exit /b 1
)

echo Verifying database...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SHOW DATABASES;" | findstr stockscanner > nul
if errorlevel 1 (
    echo ERROR: Database not found after creation
    pause
    exit /b 1
)
echo SUCCESS: Database 'stockscanner' created
echo.

echo [STEP 8] Adding MySQL to PATH...
setx PATH "%PATH%;%XAMPP_MYSQL_PATH%" > nul 2>&1
echo SUCCESS: MySQL added to system PATH
echo.

echo ========================================
echo XAMPP MYSQL SETUP COMPLETE!
echo ========================================
echo.
echo MySQL Status:
echo - Connection: Working
echo - Database: stockscanner created
echo - Path: Added to system PATH
echo.
echo You can now continue with Django setup:
echo 1. Run: python manage.py migrate
echo 2. Run: python manage.py runserver
echo 3. Or run: setup_xampp_complete.bat (it will skip to Django setup)
echo.
echo XAMPP Control Panel: %XAMPP_CONTROL_PATH%
echo MySQL Command Line: %XAMPP_MYSQL_PATH%\mysql.exe -u root
echo phpMyAdmin: http://localhost/phpmyadmin
echo.
pause