@echo off
REM ========================================
REM Unified Scanner Controller - Windows
REM ========================================
REM Runs both daily and intraday scanners intelligently:
REM - Daily scanner: Runs once at 12:00 AM (off market hours, ~5 hour runtime)
REM - Intraday scanner: Starts at 9:30 AM and runs continuously until market close (4:00 PM)
REM   * The intraday scanner manages its own 1-minute loop internally
REM   * No need to reschedule - it exits automatically when market closes
REM
REM Windows Task Scheduler Setup:
REM 1. Open Task Scheduler
REM 2. Create Task 1 - Daily Scanner:
REM    Name: "Daily Stock Scanner"
REM    Trigger: Daily at 12:00 AM
REM    Action: run_all_scanners.bat --daily
REM    Stop task if runs longer than: 8 hours
REM 3. Create Task 2 - Intraday Scanner:
REM    Name: "Intraday Stock Scanner"
REM    Trigger: Daily at 9:30 AM (weekdays only: Mon-Fri)
REM    Action: run_all_scanners.bat --intraday
REM    Stop task if runs longer than: 7 hours (auto-exits at 4PM, but safety limit)
REM

setlocal

REM Get directories
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%.."

REM Create logs directory
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"

REM Get mode from command line argument
set "MODE=%1"
if "%MODE%"=="" set "MODE=auto"

REM Get current time
for /f "tokens=1-2 delims=:" %%a in ("%time%") do (
    set hour=%%a
    set minute=%%b
)
REM Remove leading space
set hour=%hour: =%

REM ========================================
REM Daily Scanner Function
REM ========================================
if "%MODE%"=="--daily" goto run_daily
if "%MODE%"=="--both" goto run_daily
if "%MODE%"=="auto" if %hour% EQU 0 goto run_daily
goto check_intraday

:run_daily
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set "LOG_FILE=%BACKEND_DIR%\logs\daily_scanner_%mydate%.log"

echo ======================================== >> "%LOG_FILE%"
echo Daily Scanner Started: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

cd /d "%BACKEND_DIR%"

REM Activate virtual environment
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\venv\Scripts\activate.bat"
) else if exist "%BACKEND_DIR%\..\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\..\venv\Scripts\activate.bat"
)

REM Run the daily scanner
python "%SCRIPT_DIR%realtime_daily_with_proxies.py" >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Daily Scanner Completed: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

if "%MODE%"=="--daily" goto end
if "%MODE%"=="auto" goto end

REM ========================================
REM Intraday Scanner Function
REM ========================================
:check_intraday
if "%MODE%"=="--intraday" goto run_intraday
if "%MODE%"=="--both" goto run_intraday
if "%MODE%"=="auto" (
    if %hour% GEQ 9 if %hour% LEQ 16 goto run_intraday
)
goto end

:run_intraday
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set "LOG_FILE=%BACKEND_DIR%\logs\intraday_scanner_%mydate%.log"

echo ======================================== >> "%LOG_FILE%"
echo Intraday Scanner Started: %date% %time% >> "%LOG_FILE%"
echo Scanner will run continuously until market close (4:00 PM EST) >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

cd /d "%BACKEND_DIR%"

REM Activate virtual environment
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\venv\Scripts\activate.bat"
) else if exist "%BACKEND_DIR%\..\venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\..\venv\Scripts\activate.bat"
)

REM Run the intraday scanner (it will manage its own loop and exit at market close)
python "%SCRIPT_DIR%scanner_1min_hybrid.py" >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Intraday Scanner Completed: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

:end
endlocal
