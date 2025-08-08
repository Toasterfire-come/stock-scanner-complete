@echo off
title Stock Scanner with Cloudflare Tunnel

echo ===============================================
echo     Stock Scanner with Cloudflare Tunnel
echo ===============================================
echo.

:: Check if cloudflared is installed
where cloudflared >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: cloudflared not found!
    echo Please install Cloudflare tunnel first:
    echo   Download from: https://github.com/cloudflare/cloudflared/releases
    echo   Or use: winget install --id Cloudflare.cloudflared
    pause
    exit /b 1
)

:: Check if tunnel exists
set TUNNEL_NAME=django-api
cloudflared tunnel list 2>nul | findstr /i "%TUNNEL_NAME%" >nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Tunnel '%TUNNEL_NAME%' not found!
    echo Please run the setup script first:
    echo   setup_cloudflare_tunnel_auto.sh
    pause
    exit /b 1
)

echo 🚀 Starting Cloudflare tunnel...
start /b "" cloudflared tunnel run %TUNNEL_NAME%

:: Wait for tunnel to start
timeout /t 3 /nobreak >nul

echo ✅ Cloudflare tunnel started
echo.

echo 🚀 Starting Django server...
start /b "" python manage.py runserver 0.0.0.0:8000

:: Wait for server to start
timeout /t 3 /nobreak >nul

echo ✅ Django server started
echo.
echo 🌐 Services running:
echo    📡 Cloudflare Tunnel: Active
echo    🐍 Django Server: Active
echo    🔗 Your app is accessible via Cloudflare URL
echo.
echo Press any key to stop all services
pause >nul

echo.
echo 🛑 Shutting down services...

:: Kill all related processes
taskkill /f /im cloudflared.exe >nul 2>nul
taskkill /f /im python.exe >nul 2>nul

echo ✅ All services stopped
pause