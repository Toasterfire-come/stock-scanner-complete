@echo off
echo 🚀 Starting Stock Scanner Application
echo ===================================

echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🔧 Installing requirements...
pip install -r requirements.txt

echo.
echo 🔧 Running database migrations...
python manage.py migrate

echo.
echo 🚀 Starting Django development server...
python manage.py runserver

pause
