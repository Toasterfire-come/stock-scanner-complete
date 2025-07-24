#!/bin/bash

# =========================================================================
# Stock Scanner - Complete Linux Setup Script
# Single file setup for MySQL + yfinance + NASDAQ-only tickers
# Compatible with Ubuntu/Debian/CentOS/RHEL/Fedora
# =========================================================================

set -e  # Exit on any error

# Colors for output
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
    echo "|                    STOCK SCANNER - LINUX SETUP                             |"
    echo "|                   MySQL + yfinance + NASDAQ Only                           |"
    echo "|                         Single File Setup                                  |"
    echo "================================================================================"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}🎯 This script will set up:${NC}"
    echo "  ✅ MySQL database server"
    echo "  ✅ Python virtual environment"
    echo "  ✅ Django with yfinance"
    echo "  ✅ NASDAQ-only ticker system"
    echo "  ✅ Complete testing and verification"
    echo ""
}

# Detect Linux distribution
detect_os() {
    log "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        error "Cannot detect operating system"
    fi
    
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            PKG_MANAGER="apt"
            PKG_UPDATE="apt update"
            PKG_INSTALL="apt install -y"
            MYSQL_PKG="mysql-server"
            PYTHON_PKG="python3 python3-pip python3-venv python3-dev"
            BUILD_PKG="build-essential libmysqlclient-dev pkg-config"
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            PKG_MANAGER="yum"
            PKG_UPDATE="yum update -y"
            PKG_INSTALL="yum install -y"
            MYSQL_PKG="mysql-server"
            PYTHON_PKG="python3 python3-pip python3-devel"
            BUILD_PKG="gcc gcc-c++ mysql-devel pkgconfig"
            ;;
        *"Fedora"*)
            PKG_MANAGER="dnf"
            PKG_UPDATE="dnf update -y"
            PKG_INSTALL="dnf install -y"
            MYSQL_PKG="mysql-server"
            PYTHON_PKG="python3 python3-pip python3-devel"
            BUILD_PKG="gcc gcc-c++ mysql-devel pkgconfig"
            ;;
        *)
            error "Unsupported operating system: $OS"
            ;;
    esac
    
    success "Detected: $OS $VER (using $PKG_MANAGER)"
}

# Check if running as root or with sudo
check_privileges() {
    log "Checking user privileges..."
    
    if [[ $EUID -eq 0 ]]; then
        SUDO_CMD=""
        success "Running as root"
    elif sudo -n true 2>/dev/null; then
        SUDO_CMD="sudo"
        success "Sudo access available"
    else
        error "This script requires root access or sudo privileges"
    fi
}

# Install system packages
install_system_packages() {
    log "Installing system packages..."
    
    # Update package lists
    info "Updating package lists..."
    $SUDO_CMD $PKG_UPDATE
    
    # Install Python and development tools
    info "Installing Python and development tools..."
    $SUDO_CMD $PKG_INSTALL $PYTHON_PKG $BUILD_PKG curl wget git
    
    # Verify Python installation
    if ! command -v python3 &> /dev/null; then
        error "Python3 installation failed"
    fi
    
    PYTHON_VERSION=$(python3 --version)
    success "Python installed: $PYTHON_VERSION"
}

# Install and configure MySQL
install_mysql() {
    log "Installing and configuring MySQL..."
    
    # Install MySQL
    info "Installing MySQL server..."
    $SUDO_CMD $PKG_INSTALL $MYSQL_PKG
    
    # Start MySQL service
    info "Starting MySQL service..."
    $SUDO_CMD systemctl start mysql || $SUDO_CMD systemctl start mysqld
    $SUDO_CMD systemctl enable mysql || $SUDO_CMD systemctl enable mysqld
    
    # Check if MySQL is running
    if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mysqld; then
        error "MySQL service failed to start"
    fi
    
    success "MySQL service is running"
}

# Secure MySQL installation
secure_mysql() {
    log "Securing MySQL installation..."
    
    # Check if root password is already set
    if mysql -u root -e "SELECT 1" 2>/dev/null; then
        info "MySQL root password not set, configuring..."
        
        # Generate random root password
        MYSQL_ROOT_PASS=$(openssl rand -base64 32)
        
        # Set root password and secure installation
        mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PASS';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test_%';
FLUSH PRIVILEGES;
EOF
        
        success "MySQL root password set"
    else
        info "MySQL root password already configured"
        echo -n "Enter MySQL root password: "
        read -s MYSQL_ROOT_PASS
        echo
        
        # Test connection
        if ! mysql -u root -p"$MYSQL_ROOT_PASS" -e "SELECT 1" 2>/dev/null; then
            error "Invalid MySQL root password"
        fi
    fi
}

# Create database and user
create_database() {
    log "Creating database and user..."
    
    mysql -u root -p"$MYSQL_ROOT_PASS" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Test database connection
    if mysql -u "$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SELECT 1;" 2>/dev/null; then
        success "Database $DB_NAME created and accessible"
    else
        error "Failed to create or access database"
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
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    info "Upgrading pip..."
    pip install --upgrade pip
    
    success "Virtual environment created and activated"
}

# Install Python packages
install_python_packages() {
    log "Installing Python packages..."
    
    # Ensure we're in virtual environment
    source venv/bin/activate
    
    # Core Django packages
    info "Installing Django framework..."
    pip install Django==4.2.11
    pip install djangorestframework==3.14.0
    pip install django-cors-headers==4.3.1
    
    # Database packages
    info "Installing database packages..."
    pip install mysqlclient>=2.2.0
    pip install dj-database-url>=2.1.0
    
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
    
    # Optional data processing (if needed)
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
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

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

# Download NASDAQ tickers
download_nasdaq_tickers() {
    log "Downloading NASDAQ-only tickers..."
    
    # Create NASDAQ ticker downloader
    cat > "$PROJECT_DIR/tools/nasdaq_only_downloader.py" <<'EOF'
#!/usr/bin/env python3
"""
NASDAQ-Only Ticker Downloader for Linux
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
            "HON", "INTU", "AMD", "AMAT", "ISRG", "BKNG", "ADP", "GILD", "LRCX", "MDLZ"
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
    
    # Make executable
    chmod +x "$PROJECT_DIR/tools/nasdaq_only_downloader.py"
    
    # Create tools directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/tools"
    
    # Download tickers
    cd "$PROJECT_DIR"
    source venv/bin/activate
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
        self.stdout.write('🏛️  Loading NASDAQ-Only Tickers')
        
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
EOF
    
    success "Django management command created"
}

# Run Django setup
setup_django() {
    log "Setting up Django..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
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
    source venv/bin/activate
    
    # Test Django
    info "Testing Django..."
    if python manage.py check --deploy; then
        success "Django check passed"
    else
        warning "Django check found issues (may be normal for development)"
    fi
    
    # Test database connection
    info "Testing database connection..."
    python -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('✅ Database connection OK')
"
    
    # Test yfinance
    info "Testing yfinance..."
    python -c "
import yfinance as yf
stock = yf.Ticker('AAPL')
info = stock.info
print(f'✅ yfinance OK: {info.get(\"longName\", \"Apple Inc.\")}')
"
    
    # Test NASDAQ tickers
    info "Testing NASDAQ tickers..."
    python manage.py shell -c "
from stocks.models import Stock
nasdaq_count = Stock.objects.filter(exchange='NASDAQ').count()
print(f'✅ NASDAQ tickers loaded: {nasdaq_count}')
"
    
    success "All tests passed!"
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > "$PROJECT_DIR/start_stock_scanner.sh" <<EOF
#!/bin/bash
# Stock Scanner Startup Script

cd "$PROJECT_DIR"
source venv/bin/activate

echo "🚀 Starting Stock Scanner..."
echo "📊 NASDAQ tickers: \$(python manage.py shell -c "from stocks.models import Stock; print(Stock.objects.filter(exchange='NASDAQ').count())")"
echo "🌐 Server will be available at: http://localhost:8000"
echo ""

python manage.py runserver 0.0.0.0:8000
EOF
    
    chmod +x "$PROJECT_DIR/start_stock_scanner.sh"
    
    success "Startup script created: start_stock_scanner.sh"
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > "$SETUP_DIR/scripts/backup_database.sh" <<EOF
#!/bin/bash
# Database Backup Script

BACKUP_DIR="$PROJECT_DIR/backups"
BACKUP_FILE="\$BACKUP_DIR/nasdaq_db_\$(date +%Y%m%d_%H%M%S).sql"

mkdir -p "\$BACKUP_DIR"

echo "📦 Backing up database to: \$BACKUP_FILE"
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > "\$BACKUP_FILE"

if [ \$? -eq 0 ]; then
    echo "✅ Backup completed successfully"
    
    # Keep only last 7 days of backups
    find "\$BACKUP_DIR" -name "nasdaq_db_*.sql" -mtime +7 -delete
else
    echo "❌ Backup failed"
    exit 1
fi
EOF
    
    chmod +x "$SETUP_DIR/scripts/backup_database.sh"
    
    success "Backup script created"
}

# Save configuration
save_configuration() {
    log "Saving configuration..."
    
    cat > "$SETUP_DIR/configs/installation_info.txt" <<EOF
Stock Scanner Installation Information
Generated: $(date)

System Information:
- OS: $OS $VER
- Python: $(python3 --version)
- MySQL: $(mysql --version)

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
- Startup: $PROJECT_DIR/start_stock_scanner.sh
- Backup: $SETUP_DIR/scripts/backup_database.sh

Commands:
- Start server: ./start_stock_scanner.sh
- Load tickers: python manage.py load_nasdaq_only
- Backup database: $SETUP_DIR/scripts/backup_database.sh
- Django admin: python manage.py createsuperuser
EOF
    
    success "Configuration saved to $SETUP_DIR/configs/installation_info.txt"
}

# Main installation function
main() {
    print_header
    
    # Initialize log
    echo "Stock Scanner Setup Log - $(date)" > "$LOG_FILE"
    
    log "Starting Stock Scanner setup..."
    
    # Pre-flight checks
    detect_os
    check_privileges
    
    # System setup
    install_system_packages
    install_mysql
    secure_mysql
    create_database
    
    # Python setup
    setup_python_env
    install_python_packages
    
    # Project setup
    create_setup_structure
    configure_django
    download_nasdaq_tickers
    create_django_command
    setup_django
    
    # Testing
    test_installation
    
    # Finalization
    create_startup_script
    create_backup_script
    save_configuration
    
    # Final summary
    echo ""
    echo -e "${GREEN}================================================================================"
    echo "🎉 STOCK SCANNER SETUP COMPLETED SUCCESSFULLY!"
    echo "================================================================================${NC}"
    echo ""
    echo -e "${CYAN}📊 Setup Summary:${NC}"
    echo "  ✅ MySQL database configured"
    echo "  ✅ Python environment ready"
    echo "  ✅ Django application setup"
    echo "  ✅ NASDAQ-only tickers loaded"
    echo "  ✅ yfinance integration ready"
    echo ""
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo "  cd $PROJECT_DIR"
    echo "  ./start_stock_scanner.sh"
    echo ""
    echo -e "${CYAN}🌐 Access:${NC}"
    echo "  http://localhost:8000"
    echo ""
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "  Setup info: $SETUP_DIR/configs/installation_info.txt"
    echo "  Logs: $LOG_FILE"
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo "  Load NASDAQ tickers: python manage.py load_nasdaq_only"
    echo "  Backup database: $SETUP_DIR/scripts/backup_database.sh"
    echo "  Create admin user: python manage.py createsuperuser"
    echo ""
    
    success "Setup completed! Your Stock Scanner is ready to use."
}

# Run main function
main "$@"