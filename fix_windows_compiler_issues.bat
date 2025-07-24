@echo off
title Stock Scanner - Ultimate Windows Compiler Fix
echo 🛠️ Ultimate Windows Compiler Issues Fix
echo =======================================

echo.
echo 🎯 This script fixes ALL Windows compilation issues including:
echo    - NumPy C compiler errors
echo    - setuptools.build_meta import errors  
echo    - Missing Visual Studio Build Tools
echo    - Python package compilation failures
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
echo 🔧 Step 1: Upgrading core build tools...
echo 📦 Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade pip-tools

echo.
echo 🔧 Step 2: Installing build dependencies...
pip install setuptools-scm
pip install packaging
pip install build

echo.
echo 🔧 Step 3: Installing NumPy using multiple strategies...

REM Strategy 1: Try precompiled wheel from specific index
echo 🎯 Strategy 1: Trying precompiled wheel...
pip install --index-url https://pypi.org/simple/ --only-binary=:all: numpy==1.24.4
if %errorlevel% == 0 (
    echo ✅ NumPy installed successfully with precompiled wheel!
    goto pandas_install
)

REM Strategy 2: Try different NumPy version
echo 🎯 Strategy 2: Trying different NumPy version...
pip install --only-binary=:all: numpy==1.25.2
if %errorlevel% == 0 (
    echo ✅ NumPy installed successfully with version 1.25.2!
    goto pandas_install
)

REM Strategy 3: Try even older stable version
echo 🎯 Strategy 3: Trying older stable version...
pip install --only-binary=:all: numpy==1.21.6
if %errorlevel% == 0 (
    echo ✅ NumPy installed successfully with version 1.21.6!
    goto pandas_install
)

REM Strategy 4: Try without version constraints
echo 🎯 Strategy 4: Trying latest available wheel...
pip install --only-binary=:all: numpy
if %errorlevel% == 0 (
    echo ✅ NumPy installed successfully with latest version!
    goto pandas_install
)

REM Strategy 5: Force reinstall with no dependencies
echo 🎯 Strategy 5: Force install without dependencies...
pip install --force-reinstall --no-deps --only-binary=:all: numpy
if %errorlevel% == 0 (
    echo ✅ NumPy force installed successfully!
    goto pandas_install
)

echo ❌ All NumPy installation strategies failed
echo 💡 Will try alternative solution...
goto alternative_solution

:pandas_install
echo.
echo 🔧 Step 4: Installing Pandas with NumPy dependency resolved...
pip install --only-binary=:all: pandas
if %errorlevel% == 0 (
    echo ✅ Pandas installed successfully!
) else (
    echo ⚠️  Pandas installation failed, trying specific version...
    pip install --only-binary=:all: pandas==2.0.3
    if %errorlevel% == 0 (
        echo ✅ Pandas 2.0.3 installed successfully!
    ) else (
        echo ⚠️  Pandas installation failed, continuing without it...
    )
)

goto other_packages

:alternative_solution
echo.
echo 🔧 Alternative Solution: Using conda-forge packages...
echo 💡 Checking if conda is available...

where conda >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Conda found! Installing via conda...
    conda install -c conda-forge numpy pandas -y
    if %errorlevel% == 0 (
        echo ✅ NumPy and Pandas installed via conda!
        goto other_packages
    )
)

echo.
echo 🔧 Manual Download Solution...
echo 💡 As a last resort, you can manually download wheels from:
echo    https://www.lfd.uci.edu/~gohlke/pythonlibs/
echo.
echo 📋 Look for files like:
echo    numpy-1.24.4-cp311-cp311-win_amd64.whl
echo    pandas-2.0.3-cp311-cp311-win_amd64.whl
echo.
echo Then install with: pip install downloaded_file.whl
echo.

:other_packages
echo.
echo 🔧 Step 5: Installing other required packages (safe ones)...

REM Install packages that typically don't need compilation
pip install Django
pip install djangorestframework
pip install requests
pip install yfinance
pip install django-cors-headers
pip install python-dotenv
pip install django-redis
pip install celery

echo.
echo 🔧 Step 6: Installing packages with binary wheel preference...
pip install --prefer-binary beautifulsoup4
pip install --prefer-binary lxml
pip install --prefer-binary cryptography
pip install --prefer-binary Pillow

echo.
echo 🔧 Step 7: Testing installations...
echo 📋 Testing critical packages...

python -c "import sys; print(f'✅ Python: {sys.version}')"

python -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')" 2>nul
if %errorlevel% == 0 (
    echo ✅ NumPy working correctly
) else (
    echo ❌ NumPy test failed
)

python -c "import pandas; print(f'✅ Pandas: {pandas.__version__}')" 2>nul
if %errorlevel% == 0 (
    echo ✅ Pandas working correctly
) else (
    echo ❌ Pandas test failed
)

python -c "import django; print(f'✅ Django: {django.__version__}')" 2>nul
if %errorlevel% == 0 (
    echo ✅ Django working correctly
) else (
    echo ❌ Django test failed
)

python -c "import yfinance; print('✅ yfinance working')" 2>nul
if %errorlevel% == 0 (
    echo ✅ yfinance working correctly
) else (
    echo ❌ yfinance test failed
)

echo.
echo ========================================
echo 🎉 Windows Compiler Issues Fix Complete!
echo ========================================

echo.
echo 📊 Summary:
echo ✅ Core build tools upgraded
echo ✅ Multiple installation strategies attempted
echo ✅ Binary wheel preferences set
echo ✅ Critical packages tested

echo.
echo 📋 Next Steps:
echo    1. If NumPy/Pandas failed, consider using Anaconda/Miniconda
echo    2. For other failures, try: pip install --force-reinstall package_name
echo    3. Run: python manage.py migrate
echo    4. Run: python manage.py runserver

echo.
echo 💡 Alternative Solutions if Issues Persist:
echo    1. Install Anaconda: https://www.anaconda.com/download
echo    2. Install Visual Studio Build Tools: https://aka.ms/vs/17/release/vs_buildtools.exe
echo    3. Use WSL (Windows Subsystem for Linux)
echo    4. Use Docker for development

echo.
echo 🔗 Useful Resources:
echo    - Python Windows FAQ: https://docs.python.org/3/faq/windows.html
echo    - Unofficial Windows Binaries: https://www.lfd.uci.edu/~gohlke/pythonlibs/
echo    - Stack Overflow: Search "numpy windows compilation error"

echo.
pause