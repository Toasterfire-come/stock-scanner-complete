@echo off
REM ========================================
REM Daily Stock Scanner - Windows Script
REM ========================================
REM Schedule: Daily at 12:00 AM (midnight)
REM
REM Windows Task Scheduler Setup:
REM 1. Open Task Scheduler
REM 2. Create Basic Task -> "Daily Stock Scanner"
REM 3. Trigger: Daily at 12:00 AM
REM 4. Action: Start a program
REM 5. Program: C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend\stock_retrieval\run_daily_scanner.bat
REM 6. Start in: C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
REM

setlocal

REM Get directories
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%.."

REM Create logs directory
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"

REM Set log file with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set "LOG_FILE=%BACKEND_DIR%\logs\daily_scanner_%mydate%.log"

REM Log start
echo ======================================== >> "%LOG_FILE%"
echo Daily Scanner Started: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

REM Change to backend directory
cd /d "%BACKEND_DIR%"

REM Activate virtual environment (if exists)
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\venv\Scripts\activate.bat"
    echo Virtual environment activated >> "%LOG_FILE%"
) else if exist "%BACKEND_DIR%\..\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\..\venv\Scripts\activate.bat"
    echo Virtual environment activated >> "%LOG_FILE%"
)

REM Set PYTHONPATH to include backend directory for Django imports
set "PYTHONPATH=%BACKEND_DIR%;%PYTHONPATH%"

REM Run the daily scanner
python "%SCRIPT_DIR%realtime_daily_with_proxies.py" >> "%LOG_FILE%" 2>&1

REM Log completion
echo. >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Daily Scanner Completed: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

endlocal
