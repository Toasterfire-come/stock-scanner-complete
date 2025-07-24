@echo off
title Stock Scanner - Quick Start
color 0A
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █                    🚀 STOCK SCANNER - QUICK START                          █
echo █                       Clean. Organized. Simple.                            █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo 🎯 Choose your setup option:
echo.
echo 1. 🚀 SIMPLE START (Recommended) - One command does everything
echo 2. 🔧 Advanced Setup - Full control over installation  
echo 3. 🗄️  Database Tools - Setup/fix database only
echo 4. 🧪 Test System - Check if everything works
echo 5. 📖 View Documentation
echo 6. 🛠️  Management Tools - Daily operations
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting simple setup...
    echo ⏱️  This will take 15-20 minutes
    echo 💡 Just follow the prompts!
    echo.
    pause
    call setup\SIMPLE_START.bat
if errorlevel 1 (
    echo ❌ Setup step failed
    echo 💡 Check the error message above
    pause
    exit /b 1
)
) else if "%choice%"=="2" (
    echo.
    echo 🔧 Opening advanced setup options...
    call setup\windows\setup.bat
if errorlevel 1 (
    echo ❌ Setup step failed
    echo 💡 Check the error message above
    pause
    exit /b 1
)
) else if "%choice%"=="3" (
    echo.
    echo 🗄️  Opening database management tools...
    call tools\database\setup_database.bat
if errorlevel 1 (
    echo ❌ Setup step failed
    echo 💡 Check the error message above
    pause
    exit /b 1
)
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Running comprehensive system tests...
    call tools\testing\test_system.bat
) else if "%choice%"=="5" (
    echo.
    echo 📖 Opening documentation...
    start docs\README.md
    echo.
    echo 📚 Available Documentation:
    echo    - docs\setup\ - Installation guides
    echo    - docs\production\ - Production deployment  
    echo    - docs\troubleshooting\ - Problem solving
    echo.
    pause
) else if "%choice%"=="6" (
    echo.
    echo 🛠️  Management Tools:
    echo.
    echo    a. Django Management
    echo    b. Database Management
    echo    c. System Testing
    echo    d. Back to main menu
    echo.
    set /p mgmt_choice="Choose management tool (a-d): "
    
    if /i "%mgmt_choice%"=="a" (
        call tools\django\start_app.bat
    ) else if /i "%mgmt_choice%"=="b" (
        call tools\database\setup_database.bat
if errorlevel 1 (
    echo ❌ Setup step failed
    echo 💡 Check the error message above
    pause
    exit /b 1
)
    ) else if /i "%mgmt_choice%"=="c" (
        call tools\testing\test_system.bat
    ) else if /i "%mgmt_choice%"=="d" (
        goto main_menu
    ) else (
        echo Invalid choice.
        pause
    )
) else (
    echo.
    echo ❌ Invalid choice. Please enter 1-6.
    echo.
    pause
    goto main_menu
)

:main_menu
cls
goto start

:start
echo.
echo 🎉 Thanks for using Stock Scanner!
echo.
echo 💡 Quick reminders:
echo    - First time? Choose option 1 (Simple Start)
echo    - Daily use: run start_stock_scanner.bat (created after setup)
echo    - Problems? Choose option 4 (Test System)
echo.
pause
