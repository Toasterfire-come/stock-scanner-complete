@echo off
setlocal enabledelayedexpansion

:: Stock Scanner Scheduler Manager for Windows
:: This batch file provides easy access to the PHP scheduler management script

set "SCRIPT_DIR=%~dp0"
set "PHP_SCRIPT=%SCRIPT_DIR%manage_scheduler_windows.php"

:: Check if PHP is available
where php >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PHP is not found in PATH
    echo Please install PHP or add it to your system PATH
    echo Download from: https://www.php.net/downloads
    pause
    exit /b 1
)

:: Check if the PHP script exists
if not exist "%PHP_SCRIPT%" (
    echo Error: Scheduler script not found at %PHP_SCRIPT%
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

:: Show header
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           Stock Scanner Scheduler Manager (Windows)         ║
echo ║                         Batch Launcher                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: If no arguments provided, show interactive menu
if "%~1"=="" (
    goto :interactive_menu
)

:: Execute command directly
php "%PHP_SCRIPT%" %*
goto :end

:interactive_menu
echo Available Commands:
echo.
echo   1. Start Scheduler
echo   2. Stop Scheduler  
echo   3. Restart Scheduler
echo   4. Check Status
echo   5. Test API Connection
echo   6. View Logs
echo   7. System Check
echo   8. Market Status
echo   9. Configure API
echo   0. Exit
echo.

set /p "choice=Enter your choice (0-9): "

if "%choice%"=="1" (
    echo Starting scheduler...
    php "%PHP_SCRIPT%" start
) else if "%choice%"=="2" (
    echo Stopping scheduler...
    php "%PHP_SCRIPT%" stop
) else if "%choice%"=="3" (
    echo Restarting scheduler...
    php "%PHP_SCRIPT%" restart
) else if "%choice%"=="4" (
    php "%PHP_SCRIPT%" status
) else if "%choice%"=="5" (
    php "%PHP_SCRIPT%" test
) else if "%choice%"=="6" (
    php "%PHP_SCRIPT%" logs
) else if "%choice%"=="7" (
    php "%PHP_SCRIPT%" syscheck
) else if "%choice%"=="8" (
    php "%PHP_SCRIPT%" market
) else if "%choice%"=="9" (
    php "%PHP_SCRIPT%" config
) else if "%choice%"=="0" (
    echo Goodbye!
    goto :end
) else (
    echo Invalid choice. Please try again.
)

echo.
echo Press any key to return to menu...
pause >nul
cls
goto :interactive_menu

:end
endlocal