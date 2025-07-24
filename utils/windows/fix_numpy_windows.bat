@echo off
title Stock Scanner - Fix NumPy Windows Issue
echo 🔧 NumPy Windows Compilation Fix
echo ================================

echo.
echo 🎯 This script fixes the NumPy compilation error on Windows
echo 💡 Uses binary wheels to avoid Microsoft Visual Studio Build Tools requirement
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found!
    echo 💡 Please run setup.bat first
    pause
    exit /b 1
)

echo.
echo 🔧 Step 1: Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Pip upgrade failed, continuing...
)

echo.
echo 🔧 Step 2: Installing NumPy with binary wheel only...
pip install --only-binary=numpy "numpy>=1.24.0,<1.27.0"
if errorlevel 1 (
    echo ⚠️  Binary wheel failed, trying specific version...
    pip install numpy==1.24.4
    if errorlevel 1 (
        echo ❌ NumPy installation failed
        echo.
        echo 💡 Alternative solutions:
        echo    1. Install Microsoft Visual Studio Build Tools
        echo    2. Use Anaconda/Miniconda: conda install numpy
        echo    3. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 🔧 Step 3: Installing Pandas with binary wheel only...
pip install --only-binary=pandas "pandas>=2.0.0,<2.3.0"
if errorlevel 1 (
    echo ⚠️  Binary wheel failed, trying specific version...
    pip install pandas==2.0.3
    if errorlevel 1 (
        echo ❌ Pandas installation failed
        echo ⚠️  Continuing without pandas...
    )
)

echo.
echo 🔧 Step 4: Installing other problematic packages...
pip install --only-binary=lxml "lxml>=4.9.0"
if errorlevel 1 (
    echo ⚠️  lxml binary wheel failed, skipping...
)

pip install --only-binary=cryptography "cryptography>=41.0.0"
if errorlevel 1 (
    echo ⚠️  cryptography binary wheel failed, skipping...
)

echo.
echo 🔧 Step 5: Installing remaining requirements...
python install_windows_safe.py
if errorlevel 1 (
    echo ⚠️  Windows-safe installer failed, trying standard method...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️  Some packages may have failed, continuing...
    )
)

echo.
echo 🔧 Step 6: Testing installations...
python -c "import numpy; print('✅ NumPy version:', numpy.__version__)"
if errorlevel 1 (
    echo ❌ NumPy test failed
) else (
    echo ✅ NumPy working correctly
)

python -c "import pandas; print('✅ Pandas version:', pandas.__version__)"
if errorlevel 1 (
    echo ❌ Pandas test failed
) else (
    echo ✅ Pandas working correctly
)

python -c "import django; print('✅ Django version:', django.__version__)"
if errorlevel 1 (
    echo ❌ Django test failed
) else (
    echo ✅ Django working correctly
)

echo.
echo ========================================
echo 🎉 NumPy Windows Fix Complete!
echo ========================================

echo.
echo 📋 Next Steps:
echo    1. Run: python manage.py migrate
echo    2. Run: python manage.py runserver
echo    3. Open browser to: http://127.0.0.1:8000
echo.

echo 💡 If you still have issues:
echo    1. Install Visual Studio Build Tools: https://aka.ms/vs/17/release/vs_buildtools.exe
echo    2. Use Anaconda instead of pip: https://www.anaconda.com/download
echo    3. Check our troubleshooting guide: WINDOWS_SETUP_GUIDE.md
echo.

pause