@echo off
echo Cloudflare Tunnel Setup - Hide Your Home IP
echo ==============================================
echo.

REM Check if cloudflared is installed
cloudflared --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: cloudflared is not installed
    echo.
    echo Please download cloudflared from:
    echo https://github.com/cloudflare/cloudflared/releases
    echo.
    echo Extract to a folder and add to PATH, then run this script again.
    pause
    exit /b 1
)

echo SUCCESS: cloudflared is installed
echo.

REM Check if Django is running
echo Checking if Django is running...
curl -s http://localhost:8000/api/simple/stocks/ >nul 2>&1
if errorlevel 1 (
    echo WARNING: Django is not running on port 8000
    echo.
    echo Please start Django first:
    echo python manage.py runserver 127.0.0.1:8000
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo SUCCESS: Django is running
echo.

REM Login to Cloudflare
echo Step 1: Logging in to Cloudflare...
echo This will open your browser for authentication.
echo.
cloudflared tunnel login

REM Create tunnel
echo.
echo Step 2: Creating tunnel...
cloudflared tunnel create django-api

REM Get tunnel ID
for /f "tokens=2 delims=:" %%i in ('cloudflared tunnel list ^| findstr django-api') do set TUNNEL_ID=%%i
set TUNNEL_ID=%TUNNEL_ID: =%

echo.
echo SUCCESS: Tunnel created with ID: %TUNNEL_ID%
echo.

REM Create config file
echo Step 3: Creating configuration file...
if not exist "%USERPROFILE%\.cloudflared" mkdir "%USERPROFILE%\.cloudflared"

echo tunnel: %TUNNEL_ID% > "%USERPROFILE%\.cloudflared\config.yml"
echo credentials-file: %USERPROFILE%\.cloudflared\%TUNNEL_ID%.json >> "%USERPROFILE%\.cloudflared\config.yml"
echo. >> "%USERPROFILE%\.cloudflared\config.yml"
echo ingress: >> "%USERPROFILE%\.cloudflared\config.yml"
echo   - hostname: api.yourdomain.com >> "%USERPROFILE%\.cloudflared\config.yml"
echo     service: http://localhost:8000 >> "%USERPROFILE%\.cloudflared\config.yml"
echo   - service: http_status:404 >> "%USERPROFILE%\.cloudflared\config.yml"

echo SUCCESS: Configuration file created
echo.

REM Instructions
echo Step 4: Next Steps
echo ===================
echo.
echo 1. Edit the config file to use your domain:
echo    notepad "%USERPROFILE%\.cloudflared\config.yml"
echo.
echo 2. Replace "api.yourdomain.com" with your actual domain
echo.
echo 3. Start the tunnel:
echo    cloudflared tunnel run django-api
echo.
echo 4. Update WordPress settings with your tunnel URL
echo.

echo Configuration file location: "%USERPROFILE%\.cloudflared\config.yml"
echo.
echo Setup complete! Follow the steps above to finish configuration.
pause