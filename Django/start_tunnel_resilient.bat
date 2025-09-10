@echo off
setlocal enabledelayedexpansion

REM ===============================================
REM   Stock Scanner with Cloudflare Tunnel
REM   Windows Resilient Version
REM ===============================================

echo.
echo ===============================================
echo     Stock Scanner with Cloudflare Tunnel
echo     Windows Resilient Version
echo ===============================================
echo.

REM Configuration
set TUNNEL_NAME=django-api
set MAX_RETRIES=10
set RETRY_DELAY=5
set LOG_DIR=%cd%\logs
set CLOUDFLARED_EXE=cloudflared.exe

REM Create log directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Initialize counters
set /a TOTAL_RESTARTS=0
set /a CONSECUTIVE_ERRORS=0

REM Get timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

echo [%timestamp%] Starting Stock Scanner Tunnel - Windows Resilient Version >> "%LOG_DIR%\tunnel_windows.log"

REM ===============================================
REM Prevent Windows from sleeping
REM ===============================================
echo Preventing Windows from sleeping...
powercfg -change -monitor-timeout-ac 0
powercfg -change -disk-timeout-ac 0
powercfg -change -standby-timeout-ac 0
powercfg -change -hibernate-timeout-ac 0

REM Keep system awake using PowerShell
start /b powershell -WindowStyle Hidden -Command "while($true){[System.Windows.Forms.SendKeys]::SendWait('{SCROLLLOCK}');[System.Windows.Forms.SendKeys]::SendWait('{SCROLLLOCK}');Start-Sleep -Seconds 60}" > nul 2>&1

echo Sleep prevention activated

REM ===============================================
REM Fix DNS Settings
REM ===============================================
:FixDNS
echo Configuring DNS for reliability...

REM Flush DNS cache
ipconfig /flushdns > nul 2>&1

REM Set Cloudflare DNS for all network adapters
for /f "skip=2 tokens=3*" %%i in ('netsh interface show interface') do (
    if "%%j" NEQ "" (
        netsh interface ip set dns "%%j" static 1.1.1.1 primary > nul 2>&1
        netsh interface ip add dns "%%j" 8.8.8.8 index=2 > nul 2>&1
    )
)

echo DNS configured with Cloudflare and Google servers

REM Test DNS
nslookup cloudflare.com > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: DNS resolution may have issues
) else (
    echo DNS resolution working
)

REM ===============================================
REM Check for cloudflared.exe
REM ===============================================
:CheckCloudflared
if exist "%CLOUDFLARED_EXE%" (
    echo Found cloudflared.exe in current directory
) else if exist "%cd%\cloudflared.exe" (
    set CLOUDFLARED_EXE=%cd%\cloudflared.exe
    echo Found cloudflared.exe
) else (
    where cloudflared.exe > nul 2>&1
    if !errorlevel! equ 0 (
        set CLOUDFLARED_EXE=cloudflared.exe
        echo Found cloudflared.exe in PATH
    ) else (
        echo ERROR: cloudflared.exe not found!
        echo Please download from: https://github.com/cloudflare/cloudflared/releases/latest
        echo Place cloudflared.exe in the current directory
        pause
        exit /b 1
    )
)

REM ===============================================
REM Check if tunnel exists
REM ===============================================
:CheckTunnel
echo Checking tunnel configuration...
"%CLOUDFLARED_EXE%" tunnel list 2>nul | findstr /C:"%TUNNEL_NAME%" > nul
if %errorlevel% neq 0 (
    echo ERROR: Tunnel '%TUNNEL_NAME%' not found!
    echo Please run setup_cloudflare_tunnel.bat first
    pause
    exit /b 1
)
echo Tunnel configuration verified

REM ===============================================
REM Kill existing processes
REM ===============================================
:KillExisting
echo Stopping any existing services...

REM Kill cloudflared processes
taskkill /F /IM cloudflared.exe > nul 2>&1

REM Kill Python/Django processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a > nul 2>&1
)

timeout /t 2 /nobreak > nul

REM ===============================================
REM Start Cloudflare Tunnel
REM ===============================================
:StartTunnel
set /a RETRY_COUNT=0

:TunnelRetryLoop
if !RETRY_COUNT! geq %MAX_RETRIES% (
    echo ERROR: Failed to start tunnel after %MAX_RETRIES% attempts
    goto :Cleanup
)

set /a RETRY_COUNT+=1
echo.
echo Starting Cloudflare tunnel [Attempt !RETRY_COUNT!/%MAX_RETRIES%]...

REM Start tunnel with resilient settings
start /b "%CLOUDFLARED_EXE%" tunnel ^
    --loglevel info ^
    --transport-loglevel warn ^
    --metrics localhost:2000 ^
    --grace-period 30s ^
    --compression-quality 0 ^
    --no-autoupdate ^
    --protocol quic ^
    --edge-ip-version auto ^
    --heartbeat-interval 30s ^
    --heartbeat-count 5 ^
    --retries 10 ^
    run "%TUNNEL_NAME%" >> "%LOG_DIR%\cloudflared_windows.log" 2>&1

timeout /t 8 /nobreak > nul

REM Check if tunnel is running
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find /I /N "cloudflared.exe" > nul
if %errorlevel% neq 0 (
    echo Tunnel failed to start, retrying...
    set /a CONSECUTIVE_ERRORS+=1
    
    REM If multiple failures, fix DNS again
    if !CONSECUTIVE_ERRORS! geq 3 (
        echo Multiple failures detected, fixing DNS...
        goto :FixDNS
    )
    
    timeout /t %RETRY_DELAY% /nobreak > nul
    goto :TunnelRetryLoop
)

echo Cloudflare tunnel started successfully
set /a TOTAL_RESTARTS+=1
set /a CONSECUTIVE_ERRORS=0

REM ===============================================
REM Start Django Server
REM ===============================================
:StartDjango
echo Starting Django server...

cd /d "%cd%"
start /b python manage.py runserver 0.0.0.0:8000 >> "%LOG_DIR%\django_windows.log" 2>&1

timeout /t 3 /nobreak > nul

REM Check if Django is running on port 8000
netstat -an | findstr :8000 | findstr LISTENING > nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Django server
    goto :Cleanup
)

echo Django server started successfully

REM ===============================================
REM Start Monitoring Loop
REM ===============================================
:MonitorLoop
echo.
echo ===============================================
echo Services Running:
echo   - Cloudflare Tunnel: ACTIVE
echo   - Django Server: ACTIVE (Port 8000)
echo   - Monitoring: ACTIVE
echo   - Sleep Prevention: ACTIVE
echo.
echo Your app is accessible via Cloudflare URL
echo Logs are saved to: %LOG_DIR%
echo.
echo Press Ctrl+C to stop all services
echo ===============================================
echo.

REM Create a monitoring batch file that runs in background
echo @echo off > "%TEMP%\monitor_services.bat"
echo :Loop >> "%TEMP%\monitor_services.bat"
echo timeout /t 20 /nobreak ^> nul >> "%TEMP%\monitor_services.bat"
echo REM Send keepalive >> "%TEMP%\monitor_services.bat"
echo curl -s http://localhost:8000/health/ ^> nul 2^>^&1 >> "%TEMP%\monitor_services.bat"
echo REM Check tunnel >> "%TEMP%\monitor_services.bat"
echo tasklist /FI "IMAGENAME eq cloudflared.exe" 2^>nul ^| find /I /N "cloudflared.exe" ^> nul >> "%TEMP%\monitor_services.bat"
echo if %%errorlevel%% neq 0 ( >> "%TEMP%\monitor_services.bat"
echo     echo Tunnel died, please restart the script >> "%TEMP%\monitor_services.bat"
echo     exit >> "%TEMP%\monitor_services.bat"
echo ) >> "%TEMP%\monitor_services.bat"
echo REM Check Django >> "%TEMP%\monitor_services.bat"
echo netstat -an ^| findstr :8000 ^| findstr LISTENING ^> nul >> "%TEMP%\monitor_services.bat"
echo if %%errorlevel%% neq 0 ( >> "%TEMP%\monitor_services.bat"
echo     echo Django died, please restart the script >> "%TEMP%\monitor_services.bat"
echo     exit >> "%TEMP%\monitor_services.bat"
echo ) >> "%TEMP%\monitor_services.bat"
echo goto :Loop >> "%TEMP%\monitor_services.bat"

REM Start the monitor in background
start /b /min cmd /c "%TEMP%\monitor_services.bat"

REM Main loop to keep script running and send keepalives
:MainLoop
timeout /t 30 /nobreak > nul

REM Send keepalive request
curl -s http://localhost:8000/health/ > nul 2>&1

REM Check if tunnel is still running
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find /I /N "cloudflared.exe" > nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Tunnel process died, attempting restart...
    goto :StartTunnel
)

REM Check if Django is still running
netstat -an | findstr :8000 | findstr LISTENING > nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Django server died, attempting restart...
    goto :StartDjango
)

goto :MainLoop

REM ===============================================
REM Cleanup on exit
REM ===============================================
:Cleanup
echo.
echo Shutting down services...

REM Kill processes
taskkill /F /IM cloudflared.exe > nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a > nul 2>&1
)

REM Restore power settings
echo Restoring power settings...
powercfg -change -monitor-timeout-ac 30
powercfg -change -disk-timeout-ac 20  
powercfg -change -standby-timeout-ac 30
powercfg -change -hibernate-timeout-ac 180

echo.
echo All services stopped
echo Total restarts during session: %TOTAL_RESTARTS%
pause
exit /b 0