#!/bin/bash
# Stock Scanner Setup Script for Git Bash on Windows
# This script sets up the Stock Scanner application using Git Bash environment

set -e # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE} $1${NC}"
echo -e "${BLUE}============================================================${NC}"
}

print_step() {
echo -e "\n${BLUE}[STEP]${NC} $1"
}

print_success() {
echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Git Bash
check_git_bash() {
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" ]]; then
print_warning "This script is designed for Git Bash on Windows"
print_warning "Current environment: $OSTYPE"
read -p "Continue anyway? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
exit 1
fi
fi
}

# Check Python installation
check_python() {
print_step "Checking Python installation..."

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
print_error "Python is not installed or not in PATH"
print_error "Please install Python from https://python.org"
print_error "Make sure to add Python to PATH during installation"
exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
PYTHON_CMD="python3"
PIP_CMD="pip3"
else
PYTHON_CMD="python"
PIP_CMD="pip"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Found Python: $PYTHON_VERSION"

# Check pip
if ! command -v $PIP_CMD &> /dev/null; then
print_error "pip is not available"
exit 1
fi

print_success "pip is available"
}

# Check MySQL installation
check_mysql() {
print_step "Checking MySQL installation..."

# Check common MySQL locations on Windows
MYSQL_PATHS=(
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"
"/c/Program Files/MySQL/MySQL Server 5.7/bin/mysql.exe"
"/c/Program Files (x86)/MySQL/MySQL Server 8.0/bin/mysql.exe"
"/c/Program Files (x86)/MySQL/MySQL Server 5.7/bin/mysql.exe"
"/c/xampp/mysql/bin/mysql.exe"
"/c/wamp64/bin/mysql/mysql8.0.21/bin/mysql.exe"
)

MYSQL_CMD=""

# First check if mysql is in PATH
if command -v mysql &> /dev/null; then
MYSQL_CMD="mysql"
print_success "MySQL found in PATH"
else
# Check common installation paths
for path in "${MYSQL_PATHS[@]}"; do
if [[ -f "$path" ]]; then
MYSQL_CMD="$path"
print_success "MySQL found at: $path"
break
fi
done
fi

if [[ -z "$MYSQL_CMD" ]]; then
print_error "MySQL not found. Please install MySQL Server:"
print_error "1. Download from: https://dev.mysql.com/downloads/mysql/"
print_error "2. Or install XAMPP: https://www.apachefriends.org/"
print_error "3. Or install WAMP: http://www.wampserver.com/"
exit 1
fi

# Test MySQL connection
print_step "Testing MySQL connection..."
if "$MYSQL_CMD" --version &> /dev/null; then
MYSQL_VERSION=$("$MYSQL_CMD" --version)
print_success "MySQL is working: $MYSQL_VERSION"
else
print_warning "MySQL command found but may not be working properly"
fi
}

# Install Python packages
install_packages() {
print_step "Installing Python packages..."

# Create requirements array
packages=(
"Django==4.2.11"
"djangorestframework==3.14.0"
"django-cors-headers==4.3.1"
"PyMySQL==1.1.0"
"dj-database-url==2.1.0"
"python-dotenv==1.0.0"
"yfinance==0.2.18"
"pandas==2.0.3"
"numpy==1.24.3"
"requests==2.31.0"
)

for package in "${packages[@]}"; do
echo "Installing $package..."
if $PIP_CMD install "$package" --quiet; then
print_success "Installed $package"
else
print_error "Failed to install $package"
exit 1
fi
done
}

# Create .env file
create_env_file() {
print_step "Creating .env configuration file..."

cat > .env << 'EOF'
# Stock Scanner Database Configuration
DATABASE_URL=mysql://stock_scanner:StockScanner2024@localhost:3306/stock_scanner_nasdaq

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-git-bash-setup

# Email Settings (optional - configure these later)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys (optional - add your keys here)
FINNHUB_API_KEY=your-finnhub-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key

# Additional Settings
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
EOF

print_success "Created .env file with MySQL configuration"
}

# Setup MySQL database
setup_mysql_database() {
print_step "Setting up MySQL database..."

echo "Please enter your MySQL root password when prompted..."

# Create SQL commands
cat > temp_setup.sql << 'EOF'
CREATE DATABASE IF NOT EXISTS stock_scanner_nasdaq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'stock_scanner'@'localhost' IDENTIFIED BY 'StockScanner2024';
GRANT ALL PRIVILEGES ON stock_scanner_nasdaq.* TO 'stock_scanner'@'localhost';
FLUSH PRIVILEGES;
SELECT 'Database setup completed successfully' as status;
EOF

# Execute SQL
if "$MYSQL_CMD" -u root -p < temp_setup.sql; then
print_success "MySQL database and user created successfully"
rm -f temp_setup.sql
else
print_error "Failed to create database"
rm -f temp_setup.sql
exit 1
fi
}

# Test database connection
test_database_connection() {
print_step "Testing database connection..."

# Create a simple Python test script
cat > test_db_connection.py << 'EOF'
import os
import sys

# Set environment variable
os.environ['DATABASE_URL'] = 'mysql://stock_scanner:StockScanner2024@localhost:3306/stock_scanner_nasdaq'

try:
import pymysql

connection = pymysql.connect(
host='localhost',
user='stock_scanner',
password='StockScanner2024',
database='stock_scanner_nasdaq',
charset='utf8mb4'
)

with connection.cursor() as cursor:
cursor.execute("SELECT 1")
result = cursor.fetchone()

connection.close()
print("SUCCESS: Database connection test passed")
sys.exit(0)

except Exception as e:
print(f"ERROR: Database connection failed: {e}")
sys.exit(1)
EOF

if $PYTHON_CMD test_db_connection.py; then
print_success "Database connection test successful"
rm -f test_db_connection.py
else
print_error "Database connection test failed"
rm -f test_db_connection.py
exit 1
fi
}

# Clean up unnecessary files
cleanup_files() {
print_step "Cleaning up unnecessary files..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove SQLite database files
rm -f db.sqlite3 db.sqlite3-journal 2>/dev/null || true

# Remove IDE files
rm -rf .vscode .idea 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Remove OS files
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Remove log files
find . -name "*.log" -delete 2>/dev/null || true
rm -rf logs 2>/dev/null || true

# Remove temporary files
rm -rf temp tmp .tmp 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true
find . -name "*.old" -delete 2>/dev/null || true

print_success "Cleaned up unnecessary files"
}

# Run Django migrations
run_migrations() {
print_step "Running Django migrations..."

# Set Django settings
export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"

# Make migrations
echo "Creating migrations..."
if $PYTHON_CMD manage.py makemigrations; then
print_success "Migrations created"
else
print_warning "No new migrations to create"
fi

# Apply migrations
echo "Applying migrations..."
if $PYTHON_CMD manage.py migrate; then
print_success "Migrations applied successfully"
else
print_error "Failed to apply migrations"
exit 1
fi
}

# Create superuser
create_superuser() {
print_step "Creating Django superuser (optional)..."

echo
read -p "Do you want to create a Django admin superuser? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
if $PYTHON_CMD manage.py createsuperuser; then
print_success "Superuser created successfully"
else
print_warning "Superuser creation skipped or failed"
fi
else
print_success "Skipping superuser creation"
fi
}

# Verify installation
verify_installation() {
print_step "Verifying installation..."

export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"

# Check migrations status
echo "Checking migration status..."
$PYTHON_CMD manage.py showmigrations

# Test Django check
echo "Running Django system check..."
if $PYTHON_CMD manage.py check; then
print_success "Django system check passed"
else
print_warning "Django system check had issues"
fi

print_success "Installation verification completed"
}

# Main setup function
main() {
print_header "Stock Scanner Setup for Git Bash"

echo "This script will set up the Stock Scanner application with MySQL database."
echo "Make sure you have MySQL Server installed and running."
echo
read -p "Do you want to proceed with the setup? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
echo "Setup cancelled by user"
exit 0
fi

# Run setup steps
check_git_bash
check_python
check_mysql
install_packages
create_env_file
setup_mysql_database
test_database_connection
cleanup_files
run_migrations
create_superuser
verify_installation

print_header "SETUP COMPLETED SUCCESSFULLY"
echo
echo "Next steps:"
echo "1. Start the Django development server:"
echo " $PYTHON_CMD manage.py runserver"
echo
echo "2. Open your browser to:"
echo " http://localhost:8000"
echo
echo "3. Access the admin panel at:"
echo " http://localhost:8000/admin"
echo
echo "4. To stop the server, press Ctrl+C"
echo
print_success "Stock Scanner is ready to use!"
}

# Run main function
main "$@"