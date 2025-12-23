@echo off
REM Proxy Refresh Script for TradeScanPro (Windows)
REM Fetches fresh proxies from free sources
REM Run daily via Windows Task Scheduler at 1:00 AM

setlocal enabledelayedexpansion

set "BACKEND_DIR=%~dp0"
set "BACKEND_DIR=%BACKEND_DIR:~0,-1%"
set "PROXY_FILE=%BACKEND_DIR%\http_proxies.txt"
set "LOG_DIR=%BACKEND_DIR%\logs"
set "LOG_FILE=%LOG_DIR%\proxy_refresh.log"

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%date% %time%] Starting proxy refresh... >> "%LOG_FILE%"

REM Fetch proxies from Geonode API using curl
REM Note: Requires curl to be installed (available in Windows 10+)
curl -s "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&filterUpTime=90&speed=fast&limit=500&protocols=http,https" -o "%TEMP%\proxy_response.json" 2>> "%LOG_FILE%"

REM Parse JSON and extract IP:PORT (requires PowerShell)
powershell -Command "$json = Get-Content '%TEMP%\proxy_response.json' | ConvertFrom-Json; $json.data | ForEach-Object { \"$($_.ip):$($_.port)\" }" > "%PROXY_FILE%.new" 2>> "%LOG_FILE%"

REM Check if we got proxies
for /f %%A in ('type "%PROXY_FILE%.new" ^| find /c /v ""') do set PROXY_COUNT=%%A

if !PROXY_COUNT! GTR 50 (
    move /y "%PROXY_FILE%.new" "%PROXY_FILE%" >nul 2>&1
    echo [%date% %time%] ✓ Proxy refresh successful: !PROXY_COUNT! proxies >> "%LOG_FILE%"
    echo Proxy refresh successful: !PROXY_COUNT! proxies
) else (
    echo [%date% %time%] ⚠ Warning: Only !PROXY_COUNT! proxies fetched, keeping old list >> "%LOG_FILE%"
    echo Warning: Only !PROXY_COUNT! proxies fetched, keeping old list
    del "%PROXY_FILE%.new" 2>nul
)

REM Backup old proxy file
if exist "%PROXY_FILE%" (
    set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set TIMESTAMP=!TIMESTAMP: =0!
    copy "%PROXY_FILE%" "%PROXY_FILE%.backup.!TIMESTAMP!" >nul 2>&1
)

REM Clean up old backups (keep last 7 days)
forfiles /P "%BACKEND_DIR%" /M "http_proxies.txt.backup.*" /D -7 /C "cmd /c del @path" 2>nul

REM Clean up temp file
del "%TEMP%\proxy_response.json" 2>nul

echo [%date% %time%] Proxy refresh complete >> "%LOG_FILE%"
echo Proxy refresh complete
