@echo off
echo ========================================
echo QUICK MYSQL SERVICE STOPPER
echo ========================================
echo.
echo Stopping common MySQL services that conflict with XAMPP...
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
    echo ⚠️  WARNING: Port 3306 is still in use
    echo Run: fix_mysql_port_conflict.bat for more options
) else (
    echo ✅ SUCCESS: Port 3306 is now free!
    echo.
    echo 📋 Next steps:
    echo 1. Go to XAMPP Control Panel
    echo 2. Click START next to MySQL
    echo 3. Wait for green "Running" status
    echo 4. Run: fix_xampp_mysql.bat
)

echo.
echo 💡 To prevent auto-startup:
echo 1. Press Win+R, type: services.msc
echo 2. Find MySQL services
echo 3. Set Startup Type to "Manual"
echo.
pause