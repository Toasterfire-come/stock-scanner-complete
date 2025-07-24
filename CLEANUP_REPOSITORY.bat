@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Repository Cleanup Script - Stock Scanner
REM Cleans up unnecessary files and organizes the repository structure
REM =========================================================================

echo.
echo ================================================================================
echo ^|                        REPOSITORY CLEANUP SCRIPT                         ^|
echo ^|                         Stock Scanner v5.0                               ^|
echo ================================================================================
echo.
echo 🧹 This script will clean up the repository and make it more organized
echo 📁 Removes unnecessary files and optimizes structure
echo 🔧 Keeps all essential functionality intact
echo.

REM Check if we're in the project directory
if not exist "manage.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo 💡 Make sure you're in the stock-scanner-complete folder
    pause
    exit /b 1
)

echo 🔧 Starting repository cleanup...

REM Remove Python cache files
echo 📁 Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f" 2>nul
echo ✅ Python cache cleaned

REM Remove development files
echo 📁 Cleaning development files...
if exist ".pytest_cache\" rd /s /q ".pytest_cache" 2>nul
if exist ".coverage" del /q ".coverage" 2>nul
if exist "htmlcov\" rd /s /q "htmlcov" 2>nul
if exist ".tox\" rd /s /q ".tox" 2>nul
if exist "build\" rd /s /q "build" 2>nul
if exist "dist\" rd /s /q "dist" 2>nul
if exist "*.egg-info\" rd /s /q "*.egg-info" 2>nul
echo ✅ Development files cleaned

REM Clean up old/duplicate files
echo 📁 Removing duplicate/old files...
if exist "requirements_old.txt" del /q "requirements_old.txt" 2>nul
if exist "requirements_backup.txt" del /q "requirements_backup.txt" 2>nul
if exist "setup_old.py" del /q "setup_old.py" 2>nul

REM Remove old Windows setup files (keeping only the latest)
echo 📁 Organizing Windows setup files...
if exist "WINDOWS_SETUP_FIX.bat" del /q "WINDOWS_SETUP_FIX.bat" 2>nul
echo ✅ Old setup files removed (keeping FIX_WINDOWS_COMPLETE.bat)

REM Clean up database files (optional - comment out if you want to keep data)
REM echo 📁 Cleaning database files...
REM if exist "db.sqlite3" del /q "db.sqlite3" 2>nul
REM echo ✅ Database files cleaned (fresh start)

REM Remove temporary log files
echo 📁 Cleaning log files...
if exist "*.log" del /q "*.log" 2>nul
if exist "logs\" (
    for %%f in (logs\*.log) do del /q "%%f" 2>nul
)
echo ✅ Log files cleaned

REM Clean up IDE files
echo 📁 Cleaning IDE files...
if exist ".vscode\" rd /s /q ".vscode" 2>nul
if exist ".idea\" rd /s /q ".idea" 2>nul
if exist "*.swp" del /q "*.swp" 2>nul
if exist "*.swo" del /q "*.swo" 2>nul
if exist ".DS_Store" del /q ".DS_Store" 2>nul
echo ✅ IDE files cleaned

REM Organize documentation
echo 📁 Organizing documentation...
if not exist "docs\" mkdir docs
if exist "README_*.md" (
    for %%f in (README_*.md) do move "%%f" docs\ 2>nul
)
echo ✅ Documentation organized

REM Create .gitignore if it doesn't exist
echo 📁 Creating/updating .gitignore...
if not exist ".gitignore" (
    echo # Python > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.py[cod] >> .gitignore
    echo *$py.class >> .gitignore
    echo. >> .gitignore
    echo # Django >> .gitignore
    echo *.log >> .gitignore
    echo local_settings.py >> .gitignore
    echo db.sqlite3 >> .gitignore
    echo media/ >> .gitignore
    echo. >> .gitignore
    echo # Virtual Environment >> .gitignore
    echo venv/ >> .gitignore
    echo env/ >> .gitignore
    echo. >> .gitignore
    echo # IDE >> .gitignore
    echo .vscode/ >> .gitignore
    echo .idea/ >> .gitignore
    echo *.swp >> .gitignore
    echo *.swo >> .gitignore
    echo. >> .gitignore
    echo # OS >> .gitignore
    echo .DS_Store >> .gitignore
    echo Thumbs.db >> .gitignore
    echo. >> .gitignore
    echo # Environment >> .gitignore
    echo .env >> .gitignore
    echo .env.local >> .gitignore
    echo ✅ Created .gitignore
) else (
    echo ✅ .gitignore already exists
)

REM Create clean directory structure
echo 📁 Optimizing directory structure...
if not exist "scripts\" mkdir scripts
if not exist "logs\" mkdir logs
if not exist "backups\" mkdir backups

REM Move setup scripts to scripts directory
if exist "FIX_WINDOWS_COMPLETE.bat" (
    if not exist "scripts\FIX_WINDOWS_COMPLETE.bat" copy "FIX_WINDOWS_COMPLETE.bat" scripts\ >nul
)
if exist "LOAD_NASDAQ_ONLY.bat" (
    if not exist "scripts\LOAD_NASDAQ_ONLY.bat" copy "LOAD_NASDAQ_ONLY.bat" scripts\ >nul
)

echo ✅ Directory structure optimized

REM Create a clean requirements summary
echo 📁 Creating clean requirements summary...
echo # Stock Scanner Requirements Summary > REQUIREMENTS_SUMMARY.md
echo. >> REQUIREMENTS_SUMMARY.md
echo ## Main Requirements >> REQUIREMENTS_SUMMARY.md
echo - requirements.txt - Full production requirements >> REQUIREMENTS_SUMMARY.md
echo - requirements_windows.txt - Windows optimized >> REQUIREMENTS_SUMMARY.md
echo - requirements_minimal.txt - Essential only (NO compilation) >> REQUIREMENTS_SUMMARY.md
echo. >> REQUIREMENTS_SUMMARY.md
echo ## Installation Commands >> REQUIREMENTS_SUMMARY.md
echo ```cmd >> REQUIREMENTS_SUMMARY.md
echo # Ultimate Windows fix (RECOMMENDED) >> REQUIREMENTS_SUMMARY.md
echo FIX_WINDOWS_COMPLETE.bat >> REQUIREMENTS_SUMMARY.md
echo. >> REQUIREMENTS_SUMMARY.md
echo # Or manual minimal install >> REQUIREMENTS_SUMMARY.md
echo pip install -r requirements_minimal.txt >> REQUIREMENTS_SUMMARY.md
echo ``` >> REQUIREMENTS_SUMMARY.md

echo ✅ Requirements summary created

REM Show repository status
echo.
echo 📊 Repository cleanup completed!
echo.
echo 📁 Current directory structure:
dir /b | findstr /v /c:"venv" | findstr /v /c:"__pycache__" | findstr /v /c:".pyc"

echo.
echo ✅ Repository is now clean and organized!
echo.
echo 🎯 Key files for users:
echo    📄 FIX_WINDOWS_COMPLETE.bat - Ultimate Windows fix
echo    📄 LOAD_NASDAQ_ONLY.bat - Load NASDAQ tickers
echo    📄 requirements_minimal.txt - Essential packages only
echo    📄 REQUIREMENTS_SUMMARY.md - Installation guide
echo.
echo 🚀 Ready for Git commit:
echo    git add -A
echo    git commit -m "🧹 Repository cleanup and optimization"
echo    git push
echo.

echo Press any key to continue...
pause >nul