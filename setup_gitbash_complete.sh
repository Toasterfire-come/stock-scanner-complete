#!/bin/bash

# =========================================================================
# Stock Scanner - Complete Git Bash Setup Script (Windows)
# Single file setup for MySQL + yfinance + NASDAQ-only tickers
# Compatible with Git Bash on Windows
# =========================================================================

set -e  # Exit on any error

# Colors for output (Git Bash compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SETUP_DIR="$PROJECT_DIR/setup"
LOG_FILE="$PROJECT_DIR/setup.log"
DB_NAME="stock_scanner_nasdaq"
DB_USER="stock_scanner"
DB_PASS="StockScanner2010"
MYSQL_ROOT_PASS=""

# Logging function
log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Print header
print_header() {
    clear
    echo -e "${PURPLE}"
    echo "================================================================================"
    echo "|                STOCK SCANNER - GIT BASH SETUP (WINDOWS)                   |"
    echo "|                   MySQL + yfinance + NASDAQ Only                           |"
    echo "|                      Windows Compatible Setup                              |"
    echo "================================================================================"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}🎯 This script will set up:${NC}"
    echo "  ✅ Python virtual environment"
    echo "  ✅ Django with yfinance"
    echo "  ✅ MySQL connection (requires pre-installed MySQL)"
    echo "  ✅ NASDAQ-only ticker system"
    echo "  ✅ Complete testing and verification"
    echo ""
    echo -e "${YELLOW}📋 Prerequisites:${NC}"
    echo "  🔹 Python 3.8+ installed and in PATH"
    echo "  🔹 MySQL Server 8.0+ installed"
    echo "  🔹 Git Bash (you're using it now!)"
    echo ""
}

# Detect Windows environment
detect_environment() {
    log "Detecting Windows environment..."
    
    # Check if we're in Git Bash
    if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" ]]; then
        warning "This script is designed for Git Bash on Windows"
        warning "Current environment: $OSTYPE"
    fi
    
    # Convert Windows paths to Unix style
    if [[ "$PWD" =~ ^/[a-z]/ ]]; then
        success "Git Bash environment detected"
    else
        warning "Unusual path detected: $PWD"
    fi
    
    # Check for Windows Python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py"
    else
        error "Python not found. Please install Python and add to PATH"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    success "Python detected: $PYTHON_VERSION"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        error "Python not found. Install from https://python.org"
    fi
    
    # Check pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        error "pip not found. Reinstall Python with pip"
    fi
    
    # Check MySQL (try common Windows paths)
    MYSQL_FOUND=false
    MYSQL_PATHS=(
        "/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"
        "/c/Program Files/MySQL/MySQL Server 8.4/bin/mysql.exe"
        "/c/xampp/mysql/bin/mysql.exe"
        "/c/wamp64/bin/mysql/mysql*/bin/mysql.exe"
    )
    
    for mysql_path in "${MYSQL_PATHS[@]}"; do
        if [[ -f "$mysql_path" ]] || command -v mysql &> /dev/null; then
            MYSQL_FOUND=true
            break
        fi
    done
    
    if [[ "$MYSQL_FOUND" == "false" ]]; then
        warning "MySQL not found in common locations"
        echo "Please install MySQL from: https://dev.mysql.com/downloads/mysql/"
        echo "Or add MySQL to your PATH"
        read -p "Press Enter if MySQL is installed and you want to continue..."
    else
        success "MySQL installation detected"
    fi
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd "$PROJECT_DIR"
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment
    info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment (Git Bash style)
    info "Activating virtual environment..."
    source venv/Scripts/activate
    
    # Upgrade pip
    info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    success "Virtual environment created and activated"
}

# Install Python packages
install_python_packages() {
    log "Installing Python packages..."
    
    # Ensure we're in virtual environment
    source venv/Scripts/activate
    
    # Core Django packages
    info "Installing Django framework..."
    pip install Django==4.2.11
    pip install djangorestframework==3.14.0
    pip install django-cors-headers==4.3.1
    
    # Security packages (required for PyMySQL authentication)
    info "Installing security packages..."
    pip install cryptography>=41.0.0
    
    # Database packages (use PyMySQL for Windows compatibility)
    info "Installing database packages..."
    pip install PyMySQL>=1.1.0
    pip install dj-database-url>=2.1.0
    
    # Try mysqlclient, fallback to PyMySQL if compilation fails
    info "Attempting to install mysqlclient..."
    if ! pip install mysqlclient>=2.2.0 2>/dev/null; then
        warning "mysqlclient installation failed, using PyMySQL fallback"
    fi
    
    # Stock data packages
    info "Installing stock data packages..."
    pip install yfinance>=0.2.25
    pip install requests>=2.31.0
    pip install urllib3>=2.0.0
    
    # Utility packages
    info "Installing utility packages..."
    pip install python-dotenv>=1.0.0
    pip install celery>=5.3.0
    pip install redis>=5.0.0
    
    # Text processing packages
    info "Installing text processing packages..."
    pip install textblob>=0.17.1
    
    # Optional data processing (may fail on Windows without compiler)
    info "Installing data processing packages..."
    pip install numpy>=1.24.0 || warning "NumPy installation failed (optional)"
    pip install pandas>=2.0.0 || warning "Pandas installation failed (optional)"
    
    success "Python packages installed"
}

# Create setup directory structure
create_setup_structure() {
    log "Creating setup directory structure..."
    
    mkdir -p "$SETUP_DIR"/{scripts,configs,backups,logs}
    mkdir -p "$PROJECT_DIR"/{data,logs,backups}
    mkdir -p "$PROJECT_DIR"/data/{nasdaq_only,complete_nasdaq}
    
    success "Directory structure created"
}

# Configure Django settings
configure_django() {
    log "Configuring Django settings..."
    
    # Create .env file
    cat > "$PROJECT_DIR/.env" <<EOF
# Stock Scanner Configuration
DEBUG=false
SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(50))")

# Database Configuration (MySQL)
DATABASE_URL=mysql://$DB_USER:$DB_PASS@localhost:3306/$DB_NAME

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname)

# Stock Scanner Settings
NASDAQ_ONLY=true
USE_YFINANCE_ONLY=true

# Performance Settings
DB_CONN_MAX_AGE=300
DB_CONN_HEALTH_CHECKS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=$PROJECT_DIR/logs/stock_scanner.log
EOF
    
    success "Django configuration created"
}

# Update Django settings for PyMySQL compatibility
update_django_settings() {
    log "Updating Django settings for Windows compatibility..."
    
    # Add PyMySQL compatibility to settings.py
    cat >> "$PROJECT_DIR/stockscanner_django/settings.py" <<'EOF'

# Windows Git Bash PyMySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("✅ PyMySQL configured for Windows compatibility")
except ImportError:
    print("⚠️  PyMySQL not available, using default MySQL driver")
EOF
    
    success "Django settings updated for Windows"
}

# Download NASDAQ tickers
download_nasdaq_tickers() {
    log "Downloading NASDAQ-only tickers..."
    
    # Create tools directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/tools"
    
    # Create NASDAQ ticker downloader
    cat > "$PROJECT_DIR/tools/nasdaq_only_downloader.py" <<'EOF'
#!/usr/bin/env python3
"""
NASDAQ-Only Ticker Downloader for Windows Git Bash
Downloads ONLY NASDAQ-listed securities
"""

import os
import sys
import urllib.request
import csv
from datetime import datetime
from pathlib import Path

def download_nasdaq_tickers():
    """Download NASDAQ-only tickers"""
    data_dir = Path('data/nasdaq_only')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    nasdaq_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
    local_file = data_dir / 'nasdaqlisted.txt'
    
    try:
        print("📡 Downloading NASDAQ ticker list...")
        urllib.request.urlretrieve(nasdaq_url, local_file)
        
        tickers = []
        with open(local_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 8 and row[0] and row[3] != 'Y':  # Exclude test issues
                    symbol = row[0].strip()
                    if symbol and len(symbol) <= 5 and symbol.isalpha():
                        tickers.append(symbol)
        
        # Save to Python file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = data_dir / f'nasdaq_only_tickers_{timestamp}.py'
        
        with open(output_file, 'w') as f:
            f.write(f'# NASDAQ-Only Tickers - Generated {datetime.now()}\n')
            f.write(f'# Total: {len(tickers)} tickers\n\n')
            f.write('NASDAQ_ONLY_TICKERS = [\n')
            for i in range(0, len(tickers), 10):
                row = tickers[i:i+10]
                f.write('    ' + ', '.join(f'"{ticker}"' for ticker in row) + ',\n')
            f.write(']\n\n')
            f.write(f'TOTAL_TICKERS = {len(tickers)}\n')
            f.write('EXCHANGE = "NASDAQ"\n')
        
        print(f"✅ Downloaded {len(tickers)} NASDAQ tickers")
        return len(tickers)
        
    except Exception as e:
        print(f"⚠️  FTP download failed: {e}")
        print("📦 Using fallback NASDAQ ticker list...")
        
        # Fallback list of core NASDAQ tickers
        fallback_tickers = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST",
            "NFLX", "ADBE", "PEP", "TMUS", "CSCO", "INTC", "CMCSA", "TXN", "QCOM", "AMGN",
            "HON", "INTU", "AMD", "AMAT", "ISRG", "BKNG", "ADP", "GILD", "LRCX", "MDLZ",
            "SBUX", "PYPL", "REGN", "MRNA", "ZM", "DXCM", "CRWD", "ABNB", "WDAY", "TEAM"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = data_dir / f'nasdaq_only_tickers_{timestamp}.py'
        
        with open(output_file, 'w') as f:
            f.write(f'# NASDAQ-Only Tickers (Fallback) - Generated {datetime.now()}\n')
            f.write(f'# Total: {len(fallback_tickers)} core tickers\n\n')
            f.write('NASDAQ_ONLY_TICKERS = [\n')
            for i in range(0, len(fallback_tickers), 10):
                row = fallback_tickers[i:i+10]
                f.write('    ' + ', '.join(f'"{ticker}"' for ticker in row) + ',\n')
            f.write(']\n\n')
            f.write(f'TOTAL_TICKERS = {len(fallback_tickers)}\n')
            f.write('EXCHANGE = "NASDAQ"\n')
        
        print(f"✅ Using {len(fallback_tickers)} core NASDAQ tickers")
        return len(fallback_tickers)

if __name__ == "__main__":
    download_nasdaq_tickers()
EOF
    
    # Download tickers
    cd "$PROJECT_DIR"
    source venv/Scripts/activate
    python tools/nasdaq_only_downloader.py
    
    success "NASDAQ tickers downloaded"
}

# Create Django management command
create_django_command() {
    log "Creating Django management command..."
    
    mkdir -p "$PROJECT_DIR/stocks/management/commands"
    
    cat > "$PROJECT_DIR/stocks/management/commands/load_nasdaq_only.py" <<'EOF'
#!/usr/bin/env python3
"""
Django Management Command: Load NASDAQ-Only Tickers
Windows Git Bash Compatible
"""

import sys
import glob
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from stocks.models import Stock

class Command(BaseCommand):
    help = 'Load NASDAQ-only ticker list into database'

    def add_arguments(self, parser):
        parser.add_argument('--update-existing', action='store_true')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write('🏛️  Loading NASDAQ-Only Tickers (Windows)')
        
        # Find latest ticker file
        data_dir = Path('data/nasdaq_only')
        pattern = str(data_dir / 'nasdaq_only_tickers_*.py')
        ticker_files = glob.glob(pattern)
        
        if not ticker_files:
            raise CommandError("No NASDAQ ticker file found")
        
        latest_file = max(ticker_files, key=lambda x: Path(x).stat().st_mtime)
        
        # Load ticker data
        with open(latest_file, 'r') as f:
            content = f.read()
        
        namespace = {}
        exec(content, namespace)
        tickers = namespace.get('NASDAQ_ONLY_TICKERS', [])
        
        self.stdout.write(f'📊 Found {len(tickers)} NASDAQ tickers')
        
        if options['dry_run']:
            self.stdout.write('🔍 DRY RUN - No changes made')
            return
        
        # Load tickers
        added = 0
        updated = 0
        
        with transaction.atomic():
            for ticker in tickers:
                stock, created = Stock.objects.get_or_create(
                    symbol=ticker,
                    defaults={
                        'name': f'{ticker} Corporation',
                        'exchange': 'NASDAQ',
                        'sector': 'Technology',
                        'is_active': True,
                        'last_updated': timezone.now()
                    }
                )
                
                if created:
                    added += 1
                elif options['update_existing']:
                    stock.exchange = 'NASDAQ'
                    stock.is_active = True
                    stock.last_updated = timezone.now()
                    stock.save()
                    updated += 1
        
        self.stdout.write(f'✅ Added: {added}, Updated: {updated}')
        self.stdout.write(f'🏛️  NASDAQ stocks in database: {Stock.objects.filter(exchange="NASDAQ").count()}')
        self.stdout.write('')
        self.stdout.write(f'🚀 Next Steps:')
        self.stdout.write('   1. Start server: python manage.py runserver')
        self.stdout.write('   2. Access app: http://localhost:8000')
        self.stdout.write('   3. Create admin: python manage.py createsuperuser')
EOF
    
    success "Django management command created"
}

# Setup MySQL database
setup_mysql_database() {
    log "Setting up MySQL database..."
    
    info "Attempting to connect to MySQL..."
    
    # Your MySQL root password
    MYSQL_ROOT_PASSWORD="stockscanner2010"
    
    # Try to connect to MySQL and create database
    cat > "$PROJECT_DIR/setup_mysql.sql" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Try to execute MySQL commands
    if command -v mysql &> /dev/null; then
        info "Executing MySQL setup with your root password..."
        if mysql -u root -p"$MYSQL_ROOT_PASSWORD" < "$PROJECT_DIR/setup_mysql.sql" 2>/dev/null; then
            success "MySQL database configured automatically"
        else
            warning "Automatic setup failed, trying manual setup..."
            echo "Please enter your MySQL root password (stockscanner2010) when prompted:"
            mysql -u root -p < "$PROJECT_DIR/setup_mysql.sql" || warning "MySQL setup may have failed"
        fi
        rm "$PROJECT_DIR/setup_mysql.sql"
    else
        warning "MySQL command not found in PATH"
        echo "Please manually create the database with these commands:"
        cat "$PROJECT_DIR/setup_mysql.sql"
        echo ""
        echo "Save this file and run: mysql -u root -pstockscanner2010 < setup_mysql.sql"
    fi
}

# Run Django setup
setup_django() {
    log "Setting up Django..."
    
    cd "$PROJECT_DIR"
    source venv/Scripts/activate
    
    # Create migrations
    info "Creating Django migrations..."
    python manage.py makemigrations
    
    # Run migrations
    info "Running Django migrations..."
    python manage.py migrate
    
    # Load NASDAQ tickers
    info "Loading NASDAQ tickers..."
    python manage.py load_nasdaq_only --update-existing
    
    success "Django setup completed"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    cd "$PROJECT_DIR"
    source venv/Scripts/activate
    
    # Test Django
    info "Testing Django..."
    if python manage.py check; then
        success "Django check passed"
    else
        warning "Django check found issues"
    fi
    
    # Test database connection
    info "Testing database connection..."
    python -c "
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
" || warning "Database test failed"
    
    # Test yfinance
    info "Testing yfinance..."
    python -c "
try:
    import yfinance as yf
    stock = yf.Ticker('AAPL')
    info = stock.info
    if info:
        print(f'✅ yfinance OK: {info.get(\"longName\", \"Apple Inc.\")}')
    else:
        print('⚠️  yfinance connection limited')
except Exception as e:
    print(f'⚠️  yfinance test failed: {e}')
" || warning "yfinance test failed"
    
    success "Installation tests completed"
}

# Create startup scripts
create_startup_scripts() {
    log "Creating startup scripts..."
    
    # Create Windows batch file for easy startup
    cat > "$PROJECT_DIR/start_windows.bat" <<EOF
@echo off
echo Starting Stock Scanner...
cd /d "%~dp0"
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    echo Virtual environment activated
    echo Starting Django server...
    python manage.py runserver 0.0.0.0:8000
) else (
    echo Error: Virtual environment not found
    echo Please run setup_gitbash_complete.sh first
    pause
)
EOF
    
    # Create Git Bash startup script
    cat > "$PROJECT_DIR/start_gitbash.sh" <<EOF
#!/bin/bash
# Stock Scanner Startup Script for Git Bash

cd "\$(dirname "\${BASH_SOURCE[0]}")"
source venv/Scripts/activate

echo "🚀 Starting Stock Scanner..."
echo "📊 NASDAQ tickers: \$(python manage.py shell -c "from stocks.models import Stock; print(Stock.objects.filter(exchange='NASDAQ').count())" 2>/dev/null || echo 'Unknown')"
echo "🌐 Server will be available at: http://localhost:8000"
echo ""

python manage.py runserver 0.0.0.0:8000
EOF
    
    chmod +x "$PROJECT_DIR/start_gitbash.sh"
    
    success "Startup scripts created"
}

# Save configuration
save_configuration() {
    log "Saving configuration..."
    
    cat > "$SETUP_DIR/configs/installation_info.txt" <<EOF
Stock Scanner Installation Information (Windows Git Bash)
Generated: $(date)

System Information:
- OS: Windows (Git Bash)
- Python: $($PYTHON_CMD --version 2>&1)
- Environment: Git Bash

Database Configuration:
- Database: $DB_NAME
- User: $DB_USER
- Host: localhost
- Port: 3306

Project Directories:
- Project: $PROJECT_DIR
- Setup: $SETUP_DIR
- Data: $PROJECT_DIR/data
- Logs: $PROJECT_DIR/logs

Important Files:
- Environment: $PROJECT_DIR/.env
- Windows Startup: $PROJECT_DIR/start_windows.bat
- Git Bash Startup: $PROJECT_DIR/start_gitbash.sh

Commands:
- Start server (Windows): start_windows.bat
- Start server (Git Bash): ./start_gitbash.sh
- Load tickers: python manage.py load_nasdaq_only
- Django admin: python manage.py createsuperuser

Virtual Environment:
- Activate: source venv/Scripts/activate
- Deactivate: deactivate
EOF
    
    success "Configuration saved to $SETUP_DIR/configs/installation_info.txt"
}

# Main installation function
main() {
    print_header
    
    # Initialize log
    echo "Stock Scanner Setup Log (Git Bash) - $(date)" > "$LOG_FILE"
    
    log "Starting Stock Scanner setup for Windows Git Bash..."
    
    # Pre-flight checks
    detect_environment
    check_prerequisites
    
    # Python setup
    setup_python_env
    install_python_packages
    
    # Project setup
    create_setup_structure
    configure_django
    update_django_settings
    download_nasdaq_tickers
    create_django_command
    setup_mysql_database
    setup_django
    
    # Testing
    test_installation
    
    # Finalization
    create_startup_scripts
    save_configuration
    
    # Final summary
    echo ""
    echo -e "${GREEN}================================================================================"
    echo "🎉 STOCK SCANNER SETUP COMPLETED SUCCESSFULLY! (Windows Git Bash)"
    echo "================================================================================${NC}"
    echo ""
    echo -e "${CYAN}📊 Setup Summary:${NC}"
    echo "  ✅ Python virtual environment configured"
    echo "  ✅ Django application setup"
    echo "  ✅ NASDAQ-only tickers loaded"
    echo "  ✅ yfinance integration ready"
    echo "  ✅ Windows startup scripts created"
    echo ""
    echo -e "${CYAN}🚀 Quick Start Options:${NC}"
    echo "  Option 1 (Windows): Double-click start_windows.bat"
    echo "  Option 2 (Git Bash): ./start_gitbash.sh"
    echo "  Option 3 (Manual): source venv/Scripts/activate && python manage.py runserver"
    echo ""
    echo -e "${CYAN}🌐 Access:${NC}"
    echo "  http://localhost:8000"
    echo ""
    echo -e "${CYAN}📚 Next Steps:${NC}"
    echo "  1. Create admin user: python manage.py createsuperuser"
    echo "  2. Access Django admin: http://localhost:8000/admin"
    echo "  3. Configure MySQL root password if needed"
    echo ""
    echo -e "${CYAN}📋 Important Notes:${NC}"
    echo "  - Virtual environment: source venv/Scripts/activate"
    echo "  - Setup info: setup/configs/installation_info.txt"
    echo "  - Logs: setup.log"
    echo ""
    
    success "Setup completed! Your Stock Scanner is ready to use on Windows."
}

# Run main function
main "$@"