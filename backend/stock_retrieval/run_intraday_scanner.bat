@echo off
REM ========================================
REM Intraday Stock Scanner - Windows Script
REM ========================================
REM Starts the intraday scanner which runs continuously during market hours
REM The scanner manages its own 1-minute update loop and exits at market close
REM
REM Windows Task Scheduler Setup:
REM 1. Open Task Scheduler
REM 2. Create Basic Task -> "Intraday Stock Scanner"
REM 3. Trigger: Daily at 9:30 AM (weekdays only: Mon-Fri)
REM 4. Action: Start a program
REM 5. Program: C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend\stock_retrieval\run_intraday_scanner.bat
REM 6. Start in: C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
REM 7. Settings: Allow task to be run on demand, Stop task if runs longer than 7 hours (safety limit)
REM

setlocal

REM Get directories
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%.."

REM Create logs directory
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"

REM Set log file with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set "LOG_FILE=%BACKEND_DIR%\logs\intraday_scanner_%mydate%.log"

REM Log start
echo ======================================== >> "%LOG_FILE%"
echo Intraday Scanner Started: %date% %time% >> "%LOG_FILE%"
echo Scanner will run continuously until market close (4:00 PM EST) >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

REM Change to backend directory
cd /d "%BACKEND_DIR%"

REM Activate virtual environment (if exists)
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\venv\Scripts\activate.bat"
) else if exist "%BACKEND_DIR%\..\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\..\venv\Scripts\activate.bat"
)

REM Set PYTHONPATH to include backend directory for Django imports
set "PYTHONPATH=%BACKEND_DIR%;%PYTHONPATH%"

REM Run the intraday scanner (manages its own loop and exits at market close)
python "%SCRIPT_DIR%scanner_1min_hybrid.py" >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Intraday Scanner Completed: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

endlocal
