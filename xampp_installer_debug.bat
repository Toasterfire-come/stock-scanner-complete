@echo off
echo ========================================
echo XAMPP INSTALLER WITH DEBUG
echo ========================================
echo.

echo [DEBUG] Current directory: %CD%
echo [DEBUG] User: %USERNAME%
echo [DEBUG] Admin check...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [DEBUG] Running as Administrator
) else (
    echo [DEBUG] NOT running as Administrator
    echo [WARNING] Some operations may fail without admin rights
)
echo.

echo [STEP 1] Checking existing files...
if exist "xampp-installer.exe" (
    echo Found existing installer file
    echo File size:
    dir xampp-installer.exe | find "xampp-installer.exe"
    echo.
    set /p cleanup="Delete existing installer and download fresh? (y/n): "
    if /i "%cleanup%"=="y" (
        del "xampp-installer.exe"
        echo Deleted existing installer
    )
    echo.
)

echo [STEP 2] Testing download methods...
echo.

REM Method 1: PowerShell with progress
echo Testing Method 1: PowerShell download...
powershell -Command "& {try { Write-Host 'Starting PowerShell download...'; $ProgressPreference = 'SilentlyContinue'; $uri = 'https://sourceforge.net/projects/xampp/files/XAMPP Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download'; $output = 'xampp-installer.exe'; Write-Host 'Downloading from:' $uri; Invoke-WebRequest -Uri $uri -OutFile $output -TimeoutSec 300; if (Test-Path $output) { $size = (Get-Item $output).Length; Write-Host 'SUCCESS: Downloaded' $size 'bytes' } else { Write-Host 'FAILED: File not created' } } catch { Write-Host 'ERROR:' $_.Exception.Message }}"

if exist "xampp-installer.exe" (
    echo SUCCESS: PowerShell download completed
    goto :verify_installer
) else (
    echo PowerShell download failed, trying alternative...
)

REM Method 2: Direct URL with curl
echo.
echo Testing Method 2: Curl download...
curl --version >nul 2>&1
if %errorLevel% == 0 (
    echo Curl is available, downloading...
    curl -L --progress-bar -o xampp-installer.exe "https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe"
    if exist "xampp-installer.exe" (
        echo SUCCESS: Curl download completed
        goto :verify_installer
    ) else (
        echo Curl download failed
    )
) else (
    echo Curl not available, skipping...
)

REM Method 3: Alternative PowerShell approach
echo.
echo Testing Method 3: Alternative PowerShell...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe', 'xampp-installer.exe')"

if exist "xampp-installer.exe" (
    echo SUCCESS: Alternative PowerShell download completed
    goto :verify_installer
) else (
    echo All automatic downloads failed
    goto :manual_download
)

:verify_installer
echo.
echo [STEP 3] Verifying installer...
echo.
if exist "xampp-installer.exe" (
    echo File exists: xampp-installer.exe
    dir xampp-installer.exe | find "xampp-installer.exe"
    
    REM Check file size (should be around 150-200 MB)
    for %%A in (xampp-installer.exe) do (
        echo File size: %%~zA bytes
        if %%~zA LSS 50000000 (
            echo WARNING: File seems too small, might be corrupted
            echo Expected size: ~150MB+
            set /p continue="Continue anyway? (y/n): "
            if /i not "%continue%"=="y" goto :manual_download
        ) else (
            echo File size looks good
        )
    )
    echo.
    goto :install_xampp
) else (
    echo ERROR: No installer file found
    goto :manual_download
)

:install_xampp
echo [STEP 4] Installing XAMPP...
echo.
echo INSTALLATION INSTRUCTIONS:
echo 1. Choose installation directory: C:\xampp (default)
echo 2. Select components: Apache, MySQL, phpMyAdmin (minimum)
echo 3. Allow Windows Firewall access when prompted
echo 4. Start services after installation
echo.
echo Starting installer...
echo (This window will close during installation - this is normal)
echo.

REM Try different execution methods
echo Method 1: Direct execution...
xampp-installer.exe
if %errorLevel% neq 0 (
    echo Direct execution failed (Error: %errorLevel%)
    echo.
    
    echo Method 2: Using start command...
    start /wait xampp-installer.exe
    if %errorLevel% neq 0 (
        echo Start command failed (Error: %errorLevel%)
        echo.
        
        echo Method 3: As Administrator...
        powershell -Command "Start-Process -FilePath '.\xampp-installer.exe' -Verb RunAs -Wait"
        if %errorLevel% neq 0 (
            echo Administrator execution failed
            goto :manual_install
        )
    )
)

echo.
echo [STEP 5] Verifying installation...
timeout /t 3 /nobreak >nul

if exist "C:\xampp\xampp_control.exe" (
    echo SUCCESS: XAMPP installed successfully!
    echo Location: C:\xampp
    goto :post_install
) else if exist "C:\xampp\xampp-control.exe" (
    echo SUCCESS: XAMPP installed (xampp-control.exe)
    echo Location: C:\xampp
    goto :post_install
) else if exist "C:\xampp" (
    echo WARNING: C:\xampp exists but control panel not found
    echo Checking directory contents...
    dir C:\xampp
    goto :post_install
) else (
    echo ERROR: XAMPP installation failed or incomplete
    echo C:\xampp directory not found
    goto :troubleshoot
)

:post_install
echo.
echo [STEP 6] Post-installation setup...
echo.
echo Opening XAMPP Control Panel...
if exist "C:\xampp\xampp_control.exe" (
    start "" "C:\xampp\xampp_control.exe"
) else if exist "C:\xampp\xampp-control.exe" (
    start "" "C:\xampp\xampp-control.exe"
) else (
    echo Cannot find XAMPP Control Panel
    echo Please start it manually from Start Menu
)

echo.
echo ========================================
echo POST-INSTALLATION CHECKLIST
echo ========================================
echo.
echo 1. XAMPP Control Panel should be open
echo 2. Click START for Apache (wait for green)
echo 3. Click START for MySQL (wait for green)
echo 4. Both should show "Running" status
echo.
echo After services are running:
echo 5. Run: fix_xampp_mysql.bat
echo 6. Or run: python manage.py migrate
echo.
echo Web interfaces will be available at:
echo - XAMPP Dashboard: http://localhost
echo - phpMyAdmin: http://localhost/phpmyadmin
echo.
goto :cleanup

:manual_download
echo.
echo ========================================
echo MANUAL DOWNLOAD REQUIRED
echo ========================================
echo.
echo Automatic download failed. Please:
echo.
echo 1. Open browser and go to:
echo    https://www.apachefriends.org/download.html
echo.
echo 2. Download: XAMPP for Windows (PHP 8.2.x)
echo    File: xampp-windows-x64-8.2.12-0-VS16-installer.exe
echo.
echo 3. Save the file as: xampp-installer.exe
echo    In this folder: %CD%
echo.
echo 4. Run this script again
echo.
start https://www.apachefriends.org/download.html
echo Browser opened for manual download
goto :cleanup

:manual_install
echo.
echo ========================================
echo MANUAL INSTALLATION REQUIRED
echo ========================================
echo.
echo Automatic installation failed. Please:
echo.
echo 1. Right-click: xampp-installer.exe
echo 2. Select: "Run as administrator"
echo 3. Install to: C:\xampp (default)
echo 4. Select: Apache, MySQL, phpMyAdmin
echo 5. Allow firewall access
echo.
echo After installation:
echo 1. Open XAMPP Control Panel
echo 2. Start Apache and MySQL services
echo 3. Run: fix_xampp_mysql.bat
echo.
goto :cleanup

:troubleshoot
echo.
echo ========================================
echo TROUBLESHOOTING
echo ========================================
echo.
echo Installation may have failed due to:
echo.
echo 1. ANTIVIRUS BLOCKING:
echo    - Temporarily disable antivirus
echo    - Add C:\xampp to exclusions
echo    - Try installing again
echo.
echo 2. PERMISSIONS:
echo    - Run this script as Administrator
echo    - Right-click > Run as administrator
echo.
echo 3. EXISTING INSTALLATIONS:
echo    - Uninstall old XAMPP versions
echo    - Check Add/Remove Programs
echo    - Delete C:\xampp if it exists
echo.
echo 4. WINDOWS DEFENDER:
echo    - Windows may have quarantined the installer
echo    - Check Windows Security notifications
echo.
echo 5. DISK SPACE:
echo    - Ensure 1GB+ free space on C: drive
echo.
echo Try these solutions and run the script again.
echo.

:cleanup
echo.
echo Cleaning up installer file...
if exist "xampp-installer.exe" (
    set /p delete_installer="Delete installer file? (y/n): "
    if /i "%delete_installer%"=="y" (
        del "xampp-installer.exe"
        echo Installer file deleted
    )
)

echo.
echo Press any key to exit...
pause >nul