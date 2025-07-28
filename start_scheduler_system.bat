@echo off
echo ========================================
echo Stock Scanner (System Python)
echo ========================================
echo.

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

REM Run the scheduler using system Python
"C:\Users\Carterpc\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" start_stock_scheduler.py

pause
