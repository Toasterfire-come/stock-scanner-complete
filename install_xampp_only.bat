@echo off
echo ========================================
echo XAMPP INSTALLER ONLY
echo ========================================
echo.
echo This script will download and install XAMPP to C:\xampp
echo.

echo [STEP 1] Checking if XAMPP is already installed...
if exist "C:\xampp\xampp_control.exe" (
    echo SUCCESS: XAMPP is already installed at C:\xampp
    echo Opening XAMPP Control Panel...
    start "" "C:\xampp\xampp_control.exe"
    echo.
    echo You can now run: fix_xampp_mysql.bat
    pause
    exit /b 0
)

if exist "C:\xampp" (
    echo WARNING: C:\xampp directory exists but XAMPP may not be complete
    echo Continuing with installation...
    echo.
)

echo [STEP 2] Downloading XAMPP installer...
echo.

REM Try different download methods
set DOWNLOAD_SUCCESS=0

echo Method 1: Using PowerShell...
powershell -Command "try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://sourceforge.net/projects/xampp/files/XAMPP Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download' -OutFile 'xampp-installer.exe'; Write-Host 'SUCCESS: Downloaded with PowerShell' } catch { Write-Host 'PowerShell download failed' }"

if exist "xampp-installer.exe" (
    set DOWNLOAD_SUCCESS=1
    echo SUCCESS: XAMPP installer downloaded with PowerShell
) else (
    echo PowerShell download failed, trying curl...
    curl -L -o xampp-installer.exe "https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe"
    
    if exist "xampp-installer.exe" (
        set DOWNLOAD_SUCCESS=1
        echo SUCCESS: XAMPP installer downloaded with curl
    ) else (
        echo Both download methods failed
        set DOWNLOAD_SUCCESS=0
    )
)

if %DOWNLOAD_SUCCESS%==0 (
    echo.
    echo ========================================
    echo DOWNLOAD FAILED - MANUAL DOWNLOAD REQUIRED
    echo ========================================
    echo.
    echo Please download XAMPP manually:
    echo 1. Go to: https://www.apachefriends.org/download.html
    echo 2. Download: XAMPP for Windows (PHP 8.2.x)
    echo 3. Save as: xampp-installer.exe in this folder
    echo 4. Run this script again
    echo.
    start https://www.apachefriends.org/download.html
    echo Browser opened for manual download
    pause
    exit /b 1
)

echo.
echo [STEP 3] Installing XAMPP...
echo.
echo IMPORTANT INSTALLATION NOTES:
echo - Install to: C:\xampp (default location)
echo - Select: Apache, MySQL, phpMyAdmin (minimum)
echo - Allow firewall access when prompted
echo - Choose to start services after installation
echo.
echo Starting XAMPP installer...
echo (This may take 5-15 minutes depending on your system)
echo.

start /wait xampp-installer.exe

echo.
echo [STEP 4] Verifying installation...
if exist "C:\xampp\xampp_control.exe" (
    echo SUCCESS: XAMPP installed successfully!
    
    echo Opening XAMPP Control Panel...
    start "" "C:\xampp\xampp_control.exe"
    
    echo.
    echo ========================================
    echo XAMPP INSTALLATION COMPLETE!
    echo ========================================
    echo.
    echo Installation Location: C:\xampp
    echo Control Panel: C:\xampp\xampp_control.exe
    echo.
    echo NEXT STEPS:
    echo 1. In XAMPP Control Panel, click START for:
    echo    - Apache (web server)
    echo    - MySQL (database)
    echo 2. Wait for both to show green "Running" status
    echo 3. Run: fix_xampp_mysql.bat to configure for stock scanner
    echo.
    echo Web Interfaces:
    echo - XAMPP Dashboard: http://localhost
    echo - phpMyAdmin: http://localhost/phpmyadmin
    echo.
    
) else if exist "C:\xampp" (
    echo WARNING: XAMPP directory exists but installation may be incomplete
    echo.
    echo Checking for alternative control panel names...
    if exist "C:\xampp\xampp-control.exe" (
        echo Found xampp-control.exe
        start "" "C:\xampp\xampp-control.exe"
    ) else if exist "C:\xampp\control.exe" (
        echo Found control.exe
        start "" "C:\xampp\control.exe"
    ) else (
        echo ERROR: No XAMPP control panel found
        echo Installation may have failed
        echo.
        echo Please try:
        echo 1. Reinstalling XAMPP manually
        echo 2. Checking Windows Add/Remove Programs
        echo 3. Looking for XAMPP in Start Menu
    )
    
) else (
    echo ERROR: XAMPP installation failed
    echo C:\xampp directory not found
    echo.
    echo Please try:
    echo 1. Running the installer again
    echo 2. Installing manually from: https://www.apachefriends.org/
    echo 3. Checking if antivirus blocked the installation
    echo 4. Running as Administrator
)

echo.
echo Cleaning up installer file...
if exist "xampp-installer.exe" del "xampp-installer.exe"

echo.
echo Press any key to continue...
pause > nul