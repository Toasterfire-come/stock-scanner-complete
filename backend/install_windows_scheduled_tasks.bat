@echo off
REM TradeScanPro Windows Scheduled Tasks Installation Script
REM Installs all scanner scheduled tasks automatically using Windows Task Scheduler

setlocal enabledelayedexpansion

set "BACKEND_DIR=%~dp0"
set "BACKEND_DIR=%BACKEND_DIR:~0,-1%"
set "LOG_DIR=%BACKEND_DIR%\logs"

REM Find Python executable
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_BIN=python3"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_BIN=python"
    ) else (
        echo ERROR: Python not found in PATH
        exit /b 1
    )
)

REM Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================================
echo TradeScanPro Windows Scheduled Tasks Installation
echo ============================================================
echo Backend directory: %BACKEND_DIR%
echo Python binary: %PYTHON_BIN%
echo Log directory: %LOG_DIR%
echo ============================================================
echo.

REM Remove existing TradeScanPro tasks if they exist
echo Removing existing TradeScanPro tasks (if any)...
schtasks /Delete /TN "TradeScanPro\RefreshProxies" /F >nul 2>&1
schtasks /Delete /TN "TradeScanPro\DailyScanner" /F >nul 2>&1
schtasks /Delete /TN "TradeScanPro\10MinScanner" /F >nul 2>&1
schtasks /Delete /TN "TradeScanPro\1MinScanner_Start" /F >nul 2>&1
schtasks /Delete /TN "TradeScanPro\1MinScanner_Stop" /F >nul 2>&1
echo.

REM ============================================================
REM Task 1: Refresh Proxies Daily at 1:00 AM
REM ============================================================
echo Creating Task: Refresh Proxies (Daily at 1:00 AM)...
schtasks /Create /TN "TradeScanPro\RefreshProxies" ^
    /TR "\"%BACKEND_DIR%\refresh_proxies.bat\"" ^
    /SC DAILY ^
    /ST 01:00 ^
    /F

if %errorlevel% equ 0 (
    echo   ✓ Refresh Proxies task created successfully
) else (
    echo   ✗ Failed to create Refresh Proxies task
)
echo.

REM ============================================================
REM Task 2: Daily Scanner (12:00 AM - 9:00 AM with Rate Limiting)
REM ============================================================
echo Creating Task: Daily Scanner (12:00 AM start, runs for 9 hours)...
schtasks /Create /TN "TradeScanPro\DailyScanner" ^
    /TR "\"%BACKEND_DIR%\run_daily_scanner.bat\"" ^
    /SC DAILY ^
    /ST 00:00 ^
    /F

if %errorlevel% equ 0 (
    echo   ✓ Daily Scanner task created successfully
    echo   ✓ Runs daily at 12:00 AM with rate-limit protection
) else (
    echo   ✗ Failed to create Daily Scanner task
)
echo.

REM ============================================================
REM Task 3: 10-Minute Scanner (Weekdays during market hours)
REM ============================================================
echo Creating Task: 10-Minute Scanner (Weekdays 9:30 AM - 4:00 PM)...

REM Create base task that runs Monday-Friday using wrapper script
schtasks /Create /TN "TradeScanPro\10MinScanner" ^
    /TR "\"%BACKEND_DIR%\run_10min_scanner.bat\"" ^
    /SC DAILY ^
    /MO 1 ^
    /D MON,TUE,WED,THU,FRI ^
    /ST 09:30 ^
    /RI 10 ^
    /DU 06:30 ^
    /F

if %errorlevel% equ 0 (
    echo   ✓ 10-Minute Scanner task created successfully
    echo   ✓ Runs every 10 minutes from 9:30 AM to 4:00 PM (Mon-Fri)
) else (
    echo   ✗ Failed to create 10-Minute Scanner task
)
echo.

REM ============================================================
REM Task 4: 1-Minute Scanner START (Weekdays at 9:25 AM)
REM ============================================================
echo Creating Task: 1-Minute Scanner Start (Weekdays at 9:25 AM)...
schtasks /Create /TN "TradeScanPro\1MinScanner_Start" ^
    /TR "cmd /c cd /d \"%BACKEND_DIR%\" && start /B %PYTHON_BIN% scanner_1min_hybrid.py >> \"%LOG_DIR%\1min_scanner.log\" 2>&1" ^
    /SC WEEKLY ^
    /D MON,TUE,WED,THU,FRI ^
    /ST 09:25 ^
    /F

if %errorlevel% equ 0 (
    echo   ✓ 1-Minute Scanner Start task created successfully
) else (
    echo   ✗ Failed to create 1-Minute Scanner Start task
)
echo.

REM ============================================================
REM Task 5: 1-Minute Scanner STOP (Weekdays at 4:05 PM)
REM ============================================================
echo Creating Task: 1-Minute Scanner Stop (Weekdays at 4:05 PM)...
schtasks /Create /TN "TradeScanPro\1MinScanner_Stop" ^
    /TR "taskkill /F /IM python.exe /FI \"WINDOWTITLE eq scanner_1min_hybrid.py*\"" ^
    /SC WEEKLY ^
    /D MON,TUE,WED,THU,FRI ^
    /ST 16:05 ^
    /F

if %errorlevel% equ 0 (
    echo   ✓ 1-Minute Scanner Stop task created successfully
) else (
    echo   ✗ Failed to create 1-Minute Scanner Stop task
)
echo.

REM ============================================================
REM Display Summary
REM ============================================================
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Scheduled Tasks Created:
echo ------------------------
schtasks /Query /TN "TradeScanPro\RefreshProxies" /FO LIST 2>nul | findstr "TaskName Next"
schtasks /Query /TN "TradeScanPro\DailyScanner" /FO LIST 2>nul | findstr "TaskName Next"
schtasks /Query /TN "TradeScanPro\10MinScanner" /FO LIST 2>nul | findstr "TaskName Next"
schtasks /Query /TN "TradeScanPro\1MinScanner_Start" /FO LIST 2>nul | findstr "TaskName Next"
schtasks /Query /TN "TradeScanPro\1MinScanner_Stop" /FO LIST 2>nul | findstr "TaskName Next"
echo.
echo ============================================================
echo Useful Commands:
echo ============================================================
echo View all TradeScanPro tasks:
echo   schtasks /Query /TN "TradeScanPro\*"
echo.
echo Run a task manually:
echo   schtasks /Run /TN "TradeScanPro\DailyScanner"
echo.
echo Delete all TradeScanPro tasks:
echo   schtasks /Delete /TN "TradeScanPro\*" /F
echo.
echo View task details:
echo   schtasks /Query /TN "TradeScanPro\DailyScanner" /V /FO LIST
echo.
echo Open Task Scheduler GUI:
echo   taskschd.msc
echo ============================================================
echo.
echo Logs will be written to: %LOG_DIR%
echo.

pause
