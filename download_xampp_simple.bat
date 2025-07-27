@echo off
echo ========================================
echo SIMPLE XAMPP DOWNLOADER
echo ========================================
echo.
echo This script will help you download XAMPP manually if the
echo automatic PowerShell download fails.
echo.

echo [OPTION 1] Download XAMPP manually:
echo.
echo 1. Open your web browser
echo 2. Go to: https://www.apachefriends.org/download.html
echo 3. Download: XAMPP for Windows (PHP 8.2.x)
echo 4. Save the file as: xampp-installer.exe
echo 5. Place it in this directory: %cd%
echo 6. Then run: setup_xampp_complete.bat
echo.

echo [OPTION 2] Direct download links:
echo.
echo Primary: https://sourceforge.net/projects/xampp/files/XAMPP%%20Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download
echo Alternative: https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe
echo.

echo [OPTION 3] Try alternative download method:
echo.
echo Using curl (if available):
curl -L -o xampp-installer.exe "https://sourceforge.net/projects/xampp/files/XAMPP Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download"
if exist "xampp-installer.exe" (
    echo SUCCESS: XAMPP downloaded with curl
    echo You can now run: setup_xampp_complete.bat
) else (
    echo Curl download failed or not available
)
echo.

echo [OPTION 4] Check if XAMPP is already installed:
if exist "C:\xampp\xampp-control.exe" (
    echo SUCCESS: XAMPP is already installed at C:\xampp
    echo You can skip the download and run the configuration part:
    echo Just run: setup_xampp_complete.bat
    echo It will detect existing XAMPP and configure it
) else (
    echo XAMPP not found at C:\xampp
)
echo.

echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo After you have xampp-installer.exe in this folder:
echo 1. Run: setup_xampp_complete.bat
echo 2. Follow the installation prompts
echo 3. Use the stock scanner with XAMPP
echo.
echo The setup script will:
echo - Install XAMPP if needed
echo - Configure MySQL for the stock scanner
echo - Create the stockscanner database
echo - Set up all the Django tables
echo - Add sample stock data
echo.
pause