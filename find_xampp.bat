@echo off
echo ========================================
echo XAMPP INSTALLATION DETECTOR
echo ========================================
echo.

echo [STEP 1] Searching for XAMPP installation...
echo.

REM Check common XAMPP installation paths
set XAMPP_FOUND=0

echo Checking common XAMPP locations:
echo.

if exist "C:\xampp" (
    echo ✅ Found XAMPP at: C:\xampp
    set XAMPP_PATH=C:\xampp
    set XAMPP_FOUND=1
) else (
    echo ❌ Not found at: C:\xampp
)

if exist "D:\xampp" (
    echo ✅ Found XAMPP at: D:\xampp
    set XAMPP_PATH=D:\xampp
    set XAMPP_FOUND=1
) else (
    echo ❌ Not found at: D:\xampp
)

if exist "C:\Program Files\xampp" (
    echo ✅ Found XAMPP at: C:\Program Files\xampp
    set XAMPP_PATH=C:\Program Files\xampp
    set XAMPP_FOUND=1
) else (
    echo ❌ Not found at: C:\Program Files\xampp
)

if exist "C:\Program Files (x86)\xampp" (
    echo ✅ Found XAMPP at: C:\Program Files (x86)\xampp
    set XAMPP_PATH=C:\Program Files (x86)\xampp
    set XAMPP_FOUND=1
) else (
    echo ❌ Not found at: C:\Program Files (x86)\xampp
)

echo.

REM Search for XAMPP in other locations
echo Searching entire C: drive for XAMPP (this may take a moment)...
for /f "delims=" %%i in ('dir /s /b /ad C:\xampp 2^>nul') do (
    if exist "%%i\xampp_control.exe" (
        echo ✅ Found XAMPP at: %%i
        set XAMPP_PATH=%%i
        set XAMPP_FOUND=1
    )
)

echo.

if %XAMPP_FOUND%==1 (
    echo ========================================
    echo XAMPP FOUND!
    echo ========================================
    echo Location: %XAMPP_PATH%
    echo.
    
    echo Checking XAMPP components:
    if exist "%XAMPP_PATH%\xampp_control.exe" (
        echo ✅ XAMPP Control Panel found
    ) else if exist "%XAMPP_PATH%\xampp-control.exe" (
        echo ✅ XAMPP Control Panel found (xampp-control.exe)
    ) else (
        echo ❌ XAMPP Control Panel not found
    )
    
    if exist "%XAMPP_PATH%\mysql\bin\mysql.exe" (
        echo ✅ MySQL found
    ) else (
        echo ❌ MySQL not found
    )
    
    if exist "%XAMPP_PATH%\apache\bin\httpd.exe" (
        echo ✅ Apache found
    ) else (
        echo ❌ Apache not found
    )
    
    echo.
    echo [NEXT STEPS]
    echo 1. Update the XAMPP path in scripts
    echo 2. Or create a symbolic link to C:\xampp
    echo 3. Or move XAMPP to C:\xampp
    echo.
    
    echo Would you like to:
    echo [1] Create symbolic link to C:\xampp (Recommended)
    echo [2] Open XAMPP Control Panel
    echo [3] Continue manually
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        echo Creating symbolic link...
        mklink /D "C:\xampp" "%XAMPP_PATH%"
        if errorlevel 1 (
            echo ERROR: Could not create symbolic link
            echo Please run as Administrator or move XAMPP manually
        ) else (
            echo SUCCESS: Symbolic link created
            echo XAMPP is now accessible at C:\xampp
        )
    ) else if "%choice%"=="2" (
        if exist "%XAMPP_PATH%\xampp_control.exe" (
            start "" "%XAMPP_PATH%\xampp_control.exe"
        ) else if exist "%XAMPP_PATH%\xampp-control.exe" (
            start "" "%XAMPP_PATH%\xampp-control.exe"
        )
    )
    
) else (
    echo ========================================
    echo XAMPP NOT FOUND
    echo ========================================
    echo.
    echo XAMPP is not installed on this system.
    echo.
    echo [INSTALLATION OPTIONS]
    echo.
    echo Option 1: Download XAMPP manually
    echo 1. Go to: https://www.apachefriends.org/download.html
    echo 2. Download XAMPP for Windows
    echo 3. Install to C:\xampp (recommended)
    echo.
    echo Option 2: Use our download script
    echo 1. Run: download_xampp_simple.bat
    echo 2. Follow the download instructions
    echo.
    echo Option 3: Auto-download and install
    echo 1. Run: setup_xampp_complete.bat
    echo 2. It will download and install XAMPP automatically
    echo.
    echo ========================================
    echo.
    
    echo Would you like to:
    echo [1] Download XAMPP manually (opens browser)
    echo [2] Run download helper script
    echo [3] Exit and install manually
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        start https://www.apachefriends.org/download.html
        echo Browser opened. Download XAMPP and install to C:\xampp
    ) else if "%choice%"=="2" (
        if exist "download_xampp_simple.bat" (
            call download_xampp_simple.bat
        ) else (
            echo download_xampp_simple.bat not found
            echo Please run: setup_xampp_complete.bat
        )
    )
)

echo.
echo Press any key to continue...
pause > nul