@echo off
echo ========================================
echo QUICK MYSQL CRASH FIX - INNODB RECOVERY
echo ========================================
echo.

echo MySQL crashed with "shutdown unexpectedly" error.
echo This is usually caused by InnoDB corruption.
echo.
echo This script will:
echo 1. Enable InnoDB recovery mode
echo 2. Allow MySQL to start in safe mode
echo 3. Guide you through the recovery process
echo.

if not exist "C:\xampp\mysql\bin\my.ini" (
    echo ERROR: XAMPP MySQL configuration not found
    echo Please ensure XAMPP is installed at C:\xampp
    pause
    exit /b 1
)

echo [STEP 1] Backing up MySQL configuration...
copy "C:\xampp\mysql\bin\my.ini" "C:\xampp\mysql\bin\my.ini.backup.crash" >nul
echo Configuration backed up as my.ini.backup.crash

echo.
echo [STEP 2] Enabling InnoDB recovery mode...

REM Add InnoDB recovery mode to my.ini
powershell -Command "$content = Get-Content 'C:\xampp\mysql\bin\my.ini'; $content += ''; $content += '# EMERGENCY InnoDB Recovery Mode'; $content += 'innodb_force_recovery = 1'; $content | Set-Content 'C:\xampp\mysql\bin\my.ini'"

echo InnoDB recovery mode enabled

echo.
echo [STEP 3] Try starting MySQL now...
echo.
echo 1. Go to XAMPP Control Panel
echo 2. Click START next to MySQL
echo 3. MySQL should start successfully now
echo.

set /p started="Did MySQL start? (y/n): "

if /i "%started%"=="y" (
    echo.
    echo ✅ SUCCESS! MySQL is running in recovery mode.
    echo.
    echo ⚠️  IMPORTANT RECOVERY STEPS:
    echo.
    echo 1. Export any important databases NOW:
    echo    - Open phpMyAdmin: http://localhost/phpmyadmin
    echo    - Export databases you need to keep
    echo.
    echo 2. After exporting data:
    echo    - Stop MySQL in XAMPP Control Panel
    echo    - Remove the recovery lines from my.ini
    echo    - Restart MySQL normally
    echo.
    echo 3. If you have no important data:
    echo    - Run: fix_mysql_crash.bat
    echo    - Choose option 2 to reset data directory
    echo.
    echo Recovery mode is TEMPORARY - remove it after backup!
    echo.
    
    set /p hasdata="Do you have important databases to backup? (y/n): "
    if /i "%hasdata%"=="y" (
        echo.
        echo Opening phpMyAdmin for data export...
        start http://localhost/phpmyadmin
        echo.
        echo After exporting your data:
        echo 1. Stop MySQL
        echo 2. Edit C:\xampp\mysql\bin\my.ini
        echo 3. Remove these lines:
        echo    # EMERGENCY InnoDB Recovery Mode
        echo    innodb_force_recovery = 1
        echo 4. Restart MySQL
    ) else (
        echo.
        echo Since you have no important data, we can reset MySQL completely.
        set /p reset="Reset MySQL data directory? (y/n): "
        if /i "%reset%"=="y" (
            echo.
            echo Resetting MySQL data directory...
            echo This will give you a fresh, working MySQL installation.
            echo.
            if exist "fix_mysql_crash.bat" (
                echo Run: fix_mysql_crash.bat and choose option 2
            ) else (
                echo Manual reset steps:
                echo 1. Stop MySQL
                echo 2. Delete C:\xampp\mysql\data folder
                echo 3. Run: C:\xampp\mysql\bin\mysqld.exe --initialize-insecure
                echo 4. Start MySQL normally
            )
        )
    )
    
) else (
    echo.
    echo ❌ MySQL still not starting.
    echo.
    echo Try these additional solutions:
    echo.
    echo 1. Check XAMPP Control Panel logs (click Logs button)
    echo 2. Run: fix_mysql_crash.bat for more options
    echo 3. Check for port conflicts: stop_mysql_services.bat
    echo 4. Try running XAMPP as Administrator
    echo.
    echo Common causes:
    echo - Another MySQL service using port 3306
    echo - Corrupted data directory
    echo - Permission issues
    echo - Missing configuration files
    echo.
)

echo.
echo Press any key to exit...
pause >nul