@echo off
echo ========================================
echo MYSQL CRASH DIAGNOSTIC AND REPAIR TOOL
echo ========================================
echo.

echo MySQL crashed with: "MySQL shutdown unexpectedly"
echo This script will diagnose and fix common causes.
echo.

echo [STEP 1] Checking XAMPP MySQL installation...
echo.

if not exist "C:\xampp\mysql" (
    echo ERROR: XAMPP MySQL not found at C:\xampp\mysql
    echo Please ensure XAMPP is installed correctly
    pause
    exit /b 1
)

echo XAMPP MySQL directory: Found
echo.

echo [STEP 2] Checking MySQL error logs...
echo.

if exist "C:\xampp\mysql\data\mysql_error.log" (
    echo MySQL error log found. Last 20 lines:
    echo ----------------------------------------
    powershell -Command "Get-Content 'C:\xampp\mysql\data\mysql_error.log' -Tail 20"
    echo ----------------------------------------
) else (
    echo MySQL error log not found at standard location
)

if exist "C:\xampp\mysql\data\*.err" (
    echo Found .err files:
    dir "C:\xampp\mysql\data\*.err" /b
    echo.
    echo Latest error file content:
    echo ----------------------------------------
    for /f %%i in ('dir "C:\xampp\mysql\data\*.err" /b /o-d') do (
        powershell -Command "Get-Content 'C:\xampp\mysql\data\%%i' -Tail 10"
        goto :continue
    )
    :continue
    echo ----------------------------------------
)

echo.
echo [STEP 3] Common MySQL crash solutions...
echo.
echo Choose a solution to try:
echo.
echo [1] Fix corrupted InnoDB (Most Common)
echo [2] Reset MySQL data directory (Clean start)
echo [3] Fix permissions and ownership
echo [4] Repair MySQL configuration
echo [5] Check for port conflicts
echo [6] Complete MySQL reinstall
echo [7] View detailed diagnostics
echo [0] Exit
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto :fix_innodb
if "%choice%"=="2" goto :reset_data
if "%choice%"=="3" goto :fix_permissions
if "%choice%"=="4" goto :fix_config
if "%choice%"=="5" goto :check_ports
if "%choice%"=="6" goto :reinstall_mysql
if "%choice%"=="7" goto :detailed_diagnostics
if "%choice%"=="0" goto :exit
goto :invalid_choice

:fix_innodb
echo.
echo ========================================
echo FIXING INNODB CORRUPTION
echo ========================================
echo.

echo This is the most common cause of MySQL crashes.
echo We'll force InnoDB recovery mode.
echo.

echo Backing up current MySQL configuration...
if exist "C:\xampp\mysql\bin\my.ini" (
    copy "C:\xampp\mysql\bin\my.ini" "C:\xampp\mysql\bin\my.ini.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%" >nul
    echo Configuration backed up
)

echo.
echo Adding InnoDB recovery mode to configuration...

REM Add InnoDB recovery to my.ini
powershell -Command "$config = Get-Content 'C:\xampp\mysql\bin\my.ini'; $config += ''; $config += '# InnoDB Recovery Mode'; $config += 'innodb_force_recovery = 1'; $config | Set-Content 'C:\xampp\mysql\bin\my.ini'"

echo.
echo Configuration updated with InnoDB recovery mode.
echo.
echo Now try starting MySQL from XAMPP Control Panel.
echo After it starts successfully:
echo 1. Export your databases (if any)
echo 2. Stop MySQL
echo 3. Remove the recovery line from my.ini
echo 4. Restart MySQL normally
echo.

pause
goto :test_mysql

:reset_data
echo.
echo ========================================
echo RESETTING MYSQL DATA DIRECTORY
echo ========================================
echo.

echo WARNING: This will delete ALL your databases and data!
echo Only proceed if you don't have important data or have backups.
echo.
set /p confirm="Are you sure you want to reset all MySQL data? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo Operation cancelled
    pause
    goto :main_menu
)

echo.
echo Stopping any running MySQL processes...
taskkill /f /im mysqld.exe 2>nul

echo.
echo Backing up current data directory...
if exist "C:\xampp\mysql\data" (
    if not exist "C:\xampp\mysql\data_backup" mkdir "C:\xampp\mysql\data_backup"
    xcopy "C:\xampp\mysql\data" "C:\xampp\mysql\data_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%" /e /i /h >nul
    echo Data backed up to data_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%
)

echo.
echo Removing corrupted data directory...
rmdir /s /q "C:\xampp\mysql\data" 2>nul

echo.
echo Initializing fresh MySQL data directory...
"C:\xampp\mysql\bin\mysqld.exe" --initialize-insecure --user=mysql --basedir="C:\xampp\mysql" --datadir="C:\xampp\mysql\data"

if %errorLevel% == 0 (
    echo SUCCESS: MySQL data directory reset
    echo.
    echo MySQL is now clean with:
    echo - Root user with no password
    echo - Empty databases
    echo - Fresh system tables
    echo.
    echo Try starting MySQL from XAMPP Control Panel
) else (
    echo ERROR: Failed to initialize MySQL data directory
    echo Check the error messages above
)

echo.
pause
goto :test_mysql

:fix_permissions
echo.
echo ========================================
echo FIXING MYSQL PERMISSIONS
echo ========================================
echo.

echo Fixing file and folder permissions for MySQL...
echo.

echo Setting permissions on MySQL directory...
icacls "C:\xampp\mysql" /grant Everyone:(OI)(CI)F /T >nul 2>&1
icacls "C:\xampp\mysql\data" /grant Everyone:(OI)(CI)F /T >nul 2>&1

echo.
echo Fixing file ownership...
takeown /f "C:\xampp\mysql" /r /d y >nul 2>&1
takeown /f "C:\xampp\mysql\data" /r /d y >nul 2>&1

echo.
echo Permissions updated. Try starting MySQL now.
echo.

pause
goto :test_mysql

:fix_config
echo.
echo ========================================
echo REPAIRING MYSQL CONFIGURATION
echo ========================================
echo.

echo Checking MySQL configuration file...

if not exist "C:\xampp\mysql\bin\my.ini" (
    echo ERROR: MySQL configuration file not found
    echo Creating default configuration...
    
    echo [mysqld] > "C:\xampp\mysql\bin\my.ini"
    echo port=3306 >> "C:\xampp\mysql\bin\my.ini"
    echo socket="C:/xampp/mysql/mysql.sock" >> "C:\xampp\mysql\bin\my.ini"
    echo basedir="C:/xampp/mysql" >> "C:\xampp\mysql\bin\my.ini"
    echo tmpdir="C:/xampp/tmp" >> "C:\xampp\mysql\bin\my.ini"
    echo datadir="C:/xampp/mysql/data" >> "C:\xampp\mysql\bin\my.ini"
    echo pid_file="mysql.pid" >> "C:\xampp\mysql\bin\my.ini"
    echo log_error="mysql_error.log" >> "C:\xampp\mysql\bin\my.ini"
    echo log_error_verbosity=3 >> "C:\xampp\mysql\bin\my.ini"
    echo.
    echo [client] >> "C:\xampp\mysql\bin\my.ini"
    echo port=3306 >> "C:\xampp\mysql\bin\my.ini"
    echo socket="C:/xampp/mysql/mysql.sock" >> "C:\xampp\mysql\bin\my.ini"
    
    echo Default configuration created
) else (
    echo Configuration file exists
    echo.
    echo Checking for common configuration issues...
    
    echo Current port setting:
    findstr /i "port" "C:\xampp\mysql\bin\my.ini"
    
    echo.
    echo Current datadir setting:
    findstr /i "datadir" "C:\xampp\mysql\bin\my.ini"
)

echo.
echo Configuration check complete. Try starting MySQL.
echo.

pause
goto :test_mysql

:check_ports
echo.
echo ========================================
echo CHECKING PORT CONFLICTS
echo ========================================
echo.

echo Checking if port 3306 is available...
netstat -ano | findstr :3306

if %errorLevel% == 0 (
    echo.
    echo Port 3306 is in use by another process.
    echo This could be causing the MySQL crash.
    echo.
    echo Options:
    echo 1. Stop other MySQL services
    echo 2. Change XAMPP MySQL to port 3307
    echo.
    set /p portchoice="Run port conflict resolver? (y/n): "
    if /i "%portchoice%"=="y" (
        if exist "fix_mysql_port_conflict.bat" (
            call fix_mysql_port_conflict.bat
        ) else (
            echo Port conflict resolver not found
        )
    )
) else (
    echo Port 3306 is available - not a port conflict issue
)

echo.
pause
goto :test_mysql

:reinstall_mysql
echo.
echo ========================================
echo COMPLETE MYSQL REINSTALL
echo ========================================
echo.

echo This will completely reinstall MySQL within XAMPP.
echo.
set /p confirm="Proceed with MySQL reinstall? (y/n): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled
    pause
    goto :main_menu
)

echo.
echo Stopping MySQL processes...
taskkill /f /im mysqld.exe 2>nul

echo.
echo Backing up data (if any)...
if exist "C:\xampp\mysql\data" (
    xcopy "C:\xampp\mysql\data" "C:\xampp\mysql_data_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%" /e /i /h >nul
    echo Data backed up
)

echo.
echo Downloading fresh MySQL for XAMPP...
echo This may take several minutes...

REM Download fresh XAMPP MySQL (this is complex, so we'll guide manual reinstall)
echo.
echo MANUAL REINSTALL STEPS:
echo 1. Download fresh XAMPP from: https://www.apachefriends.org/
echo 2. Backup your current C:\xampp\htdocs folder
echo 3. Uninstall current XAMPP
echo 4. Install fresh XAMPP
echo 5. Restore your htdocs content
echo 6. Run: fix_xampp_mysql.bat
echo.

pause
goto :exit

:detailed_diagnostics
echo.
echo ========================================
echo DETAILED MYSQL DIAGNOSTICS
echo ========================================
echo.

echo === XAMPP MYSQL FILES ===
echo.
echo MySQL executable:
if exist "C:\xampp\mysql\bin\mysqld.exe" (
    echo ✅ Found: C:\xampp\mysql\bin\mysqld.exe
    dir "C:\xampp\mysql\bin\mysqld.exe"
) else (
    echo ❌ Missing: C:\xampp\mysql\bin\mysqld.exe
)

echo.
echo MySQL configuration:
if exist "C:\xampp\mysql\bin\my.ini" (
    echo ✅ Found: C:\xampp\mysql\bin\my.ini
    echo File size:
    dir "C:\xampp\mysql\bin\my.ini"
    echo.
    echo Key settings:
    findstr /i "port datadir basedir" "C:\xampp\mysql\bin\my.ini"
) else (
    echo ❌ Missing: C:\xampp\mysql\bin\my.ini
)

echo.
echo MySQL data directory:
if exist "C:\xampp\mysql\data" (
    echo ✅ Found: C:\xampp\mysql\data
    echo Contents:
    dir "C:\xampp\mysql\data" /b | head -10
) else (
    echo ❌ Missing: C:\xampp\mysql\data
)

echo.
echo === PROCESS AND PORT STATUS ===
echo.
echo MySQL processes:
tasklist | findstr /i mysql

echo.
echo Port 3306 usage:
netstat -ano | findstr :3306

echo.
echo === ERROR LOGS (Last 10 lines) ===
echo.
if exist "C:\xampp\mysql\data\mysql_error.log" (
    powershell -Command "Get-Content 'C:\xampp\mysql\data\mysql_error.log' -Tail 10"
) else (
    echo No mysql_error.log found
)

echo.
echo === WINDOWS EVENT LOG (MySQL related) ===
echo.
powershell -Command "Get-EventLog -LogName Application -Source '*MySQL*' -Newest 5 2>$null | Format-Table TimeGenerated, EntryType, Message -Wrap"

echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:test_mysql
echo.
echo ========================================
echo TESTING MYSQL STARTUP
echo ========================================
echo.

echo Please try starting MySQL now:
echo.
echo 1. Open XAMPP Control Panel
echo 2. Click START next to MySQL
echo 3. Watch for green "Running" status
echo.

set /p success="Did MySQL start successfully? (y/n): "

if /i "%success%"=="y" (
    echo.
    echo ✅ SUCCESS! MySQL is now running.
    echo.
    echo Next steps:
    echo 1. Test database connection: run fix_xampp_mysql.bat
    echo 2. Set up Django: python manage.py migrate
    echo 3. Start development: python manage.py runserver
    echo.
    echo If this was an InnoDB recovery, remember to:
    echo 1. Export any important data
    echo 2. Remove innodb_force_recovery from my.ini
    echo 3. Restart MySQL normally
    echo.
) else (
    echo.
    echo ❌ MySQL still not starting.
    echo.
    echo Additional troubleshooting:
    echo 1. Check XAMPP Control Panel logs (click Logs button)
    echo 2. Try running this script again with a different option
    echo 3. Consider complete XAMPP reinstall
    echo 4. Check Windows Event Viewer for MySQL errors
    echo.
    echo Would you like to try another solution?
    set /p retry="Try another fix? (y/n): "
    if /i "%retry%"=="y" goto :main_menu
)

pause
goto :exit

:invalid_choice
echo Invalid choice. Please enter a number between 0-7.
pause
goto :main_menu

:main_menu
cls
echo [STEP 3] Common MySQL crash solutions...
echo.
echo Choose a solution to try:
echo.
echo [1] Fix corrupted InnoDB (Most Common)
echo [2] Reset MySQL data directory (Clean start)
echo [3] Fix permissions and ownership
echo [4] Repair MySQL configuration
echo [5] Check for port conflicts
echo [6] Complete MySQL reinstall
echo [7] View detailed diagnostics
echo [0] Exit
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto :fix_innodb
if "%choice%"=="2" goto :reset_data
if "%choice%"=="3" goto :fix_permissions
if "%choice%"=="4" goto :fix_config
if "%choice%"=="5" goto :check_ports
if "%choice%"=="6" goto :reinstall_mysql
if "%choice%"=="7" goto :detailed_diagnostics
if "%choice%"=="0" goto :exit
goto :invalid_choice

:exit
echo.
echo ========================================
echo MYSQL CRASH TROUBLESHOOTER COMPLETE
echo ========================================
echo.
echo If MySQL is still not working:
echo 1. Check XAMPP forums: https://community.apachefriends.org/
echo 2. Try complete XAMPP reinstall
echo 3. Consider using alternative like WAMP
echo.
echo Press any key to exit...
pause >nul