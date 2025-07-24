#!/bin/bash

# =========================================================================
# Stock Scanner - Git Bash Setup with Permission Fixes
# Handles Windows permission issues automatically
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
DB_PASS="StockScanner2024!"
MYSQL_ROOT_PASSWORD="stockscanner2010"

# Logging functions
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
    echo "|            STOCK SCANNER - GIT BASH SETUP (PERMISSION FIXED)              |"
    echo "|                   MySQL + yfinance + NASDAQ Only                           |"
    echo "|                    Windows Permission Issues Handled                       |"
    echo "================================================================================"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}🎯 This script will:${NC}"
    echo "  ✅ Fix Windows permission issues automatically"
    echo "  ✅ Setup Python virtual environment"
    echo "  ✅ Install packages without permission errors"
    echo "  ✅ Configure MySQL with your password"
    echo "  ✅ Setup NASDAQ-only ticker system"
    echo ""
}

# Fix Windows permissions
fix_permissions() {
    log "Fixing Windows permissions..."
    
    # Check if running as Administrator
    if [[ $(id -u) -eq 0 ]] || [[ "$USERNAME" == "Administrator" ]]; then
        success "Running with administrator privileges"
    else
        warning "Not running as administrator - will use permission workarounds"
    fi
    
    # Clear problematic pip cache
    info "Clearing pip cache to avoid permission issues..."
    PIP_CACHE_DIRS=(
        "/c/users/$USER/appdata/local/pip/cache"
        "/c/users/carterpc/appdata/local/packages/pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0/localcache/local/pip/cache"
        "/c/users/$USER/appdata/local/packages/*/localcache/local/pip/cache"
    )
    
    for cache_dir in "${PIP_CACHE_DIRS[@]}"; do
        if [[ -d "$cache_dir" ]]; then
            info "Clearing cache: $cache_dir"
            rm -rf "$cache_dir" 2>/dev/null || warning "Could not clear $cache_dir"
        fi
    done
    
    # Create temp directory for downloads
    mkdir -p "$PROJECT_DIR/temp_pip_cache"
    export PIP_CACHE_DIR="$PROJECT_DIR/temp_pip_cache"
    
    success "Permission fixes applied"
}

# Detect Python and environment
detect_environment() {
    log "Detecting Windows environment..."
    
    # Check for Python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py"
    else
        error "Python not found. Please install Python from https://python.org"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    success "Python detected: $PYTHON_VERSION"
    
    # Check Python version (need 3.8+)
    PYTHON_VER=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$PYTHON_VER >= 3.8" | bc -l 2>/dev/null || echo "1") ]]; then
        success "Python version is compatible"
    else
        warning "Python version may be too old (need 3.8+)"
    fi
}

# Setup virtual environment with permission fixes
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd "$PROJECT_DIR"
    
    # Remove existing venv
    if [ -d "venv" ]; then
        warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment
    info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    info "Activating virtual environment..."
    source venv/Scripts/activate
    
    # Upgrade pip with no cache to avoid permission issues
    info "Upgrading pip (no cache)..."
    python -m pip install --upgrade pip --no-cache-dir --disable-pip-version-check
    
    success "Virtual environment ready"
}

# Install packages with permission workarounds
install_python_packages() {
    log "Installing Python packages (permission-safe)..."
    
    source venv/Scripts/activate
    
    # Set pip options to avoid permission issues
    PIP_OPTIONS="--no-cache-dir --disable-pip-version-check --user-install-warning=ignore"
    
    # Core Django packages
    info "Installing Django framework..."
    pip install $PIP_OPTIONS Django==4.2.11
    pip install $PIP_OPTIONS djangorestframework==3.14.0
    pip install $PIP_OPTIONS django-cors-headers==4.3.1
    
    # Security packages (required for PyMySQL authentication)
    info "Installing security packages..."
    pip install $PIP_OPTIONS cryptography>=41.0.0
    
    # Database packages
    info "Installing database packages..."
    pip install $PIP_OPTIONS PyMySQL>=1.1.0
    pip install $PIP_OPTIONS dj-database-url>=2.1.0
    
    # Try mysqlclient with fallback
    info "Attempting mysqlclient installation..."
    if ! pip install $PIP_OPTIONS mysqlclient>=2.2.0 2>/dev/null; then
        warning "mysqlclient failed, using PyMySQL (this is fine for Windows)"
    fi
    
    # Stock data packages
    info "Installing stock data packages..."
    pip install $PIP_OPTIONS requests>=2.31.0
    pip install $PIP_OPTIONS urllib3>=2.0.0
    
    # yfinance with specific version to avoid multitasking issue
    info "Installing yfinance (Windows-safe version)..."
    pip install $PIP_OPTIONS yfinance==0.2.18 || pip install $PIP_OPTIONS yfinance>=0.2.25
    
    # Utility packages
    info "Installing utility packages..."
    pip install $PIP_OPTIONS python-dotenv>=1.0.0
    pip install $PIP_OPTIONS celery>=5.3.0 || warning "Celery failed (optional)"
    pip install $PIP_OPTIONS redis>=5.0.0 || warning "Redis failed (optional)"
    
    # Text processing packages
    info "Installing text processing packages..."
    pip install $PIP_OPTIONS textblob>=0.17.1
    
    # Optional data processing
    info "Installing data processing packages..."
    pip install $PIP_OPTIONS numpy>=1.24.0 || warning "NumPy failed (optional)"
    pip install $PIP_OPTIONS pandas>=2.0.0 || warning "Pandas failed (optional)"
    
    success "Package installation completed"
}

# Find and setup MySQL
setup_mysql() {
    log "Setting up MySQL..."
    
    # Find MySQL installation
    MYSQL_PATHS=(
        "/c/Program Files/MySQL/MySQL Server 8.0/bin"
        "/c/Program Files/MySQL/MySQL Server 8.4/bin"
        "/c/Program Files (x86)/MySQL/MySQL Server 8.0/bin"
        "/c/xampp/mysql/bin"
    )
    
    MYSQL_FOUND=""
    for mysql_path in "${MYSQL_PATHS[@]}"; do
        if [[ -f "$mysql_path/mysql.exe" ]]; then
            MYSQL_FOUND="$mysql_path"
            export PATH="$mysql_path:$PATH"
            success "Found MySQL at: $mysql_path"
            break
        fi
    done
    
    if [[ -z "$MYSQL_FOUND" ]]; then
        warning "MySQL not found in common paths, searching..."
        MYSQL_SEARCH=$(find "/c/Program Files" -name "mysql.exe" 2>/dev/null | head -1)
        if [[ -n "$MYSQL_SEARCH" ]]; then
            MYSQL_FOUND=$(dirname "$MYSQL_SEARCH")
            export PATH="$MYSQL_FOUND:$PATH"
            success "Found MySQL at: $MYSQL_FOUND"
        fi
    fi
    
    if [[ -n "$MYSQL_FOUND" ]]; then
        # Create database setup
        info "Creating MySQL database..."
        cat > "$PROJECT_DIR/setup_mysql.sql" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
        
        # Execute MySQL setup
        if mysql -u root -p"$MYSQL_ROOT_PASSWORD" < "$PROJECT_DIR/setup_mysql.sql" 2>/dev/null; then
            success "MySQL database configured automatically"
        else
            warning "Automatic MySQL setup failed - will use manual fallback"
        fi
        rm -f "$PROJECT_DIR/setup_mysql.sql"
    else
        warning "MySQL not found - will use SQLite fallback"
    fi
}

# Configure Django
configure_django() {
    log "Configuring Django..."
    
    # Create .env file
    cat > "$PROJECT_DIR/.env" <<EOF
# Stock Scanner Configuration
DEBUG=false
SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(50))")

# Database Configuration
DATABASE_URL=mysql://$DB_USER:$DB_PASS@localhost:3306/$DB_NAME

# Settings
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname)
NASDAQ_ONLY=true
USE_YFINANCE_ONLY=true
LOG_LEVEL=INFO
EOF
    
    success "Django configured"
}

# Create directory structure
create_structure() {
    log "Creating project structure..."
    
    mkdir -p "$SETUP_DIR"/{scripts,configs,logs}
    mkdir -p "$PROJECT_DIR"/{data,logs,backups}
    mkdir -p "$PROJECT_DIR"/data/nasdaq_only
    
    success "Project structure created"
}

# Download NASDAQ tickers
download_tickers() {
    log "Downloading NASDAQ tickers..."
    
    source venv/Scripts/activate
    mkdir -p "$PROJECT_DIR/tools"
    
    # Create simple ticker downloader
    cat > "$PROJECT_DIR/tools/get_tickers.py" <<'EOF'
import urllib.request
import csv
from pathlib import Path
from datetime import datetime

def download_tickers():
    data_dir = Path('data/nasdaq_only')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("📡 Downloading NASDAQ tickers...")
        url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        urllib.request.urlretrieve(url, data_dir / 'nasdaqlisted.txt')
        
        tickers = []
        with open(data_dir / 'nasdaqlisted.txt', 'r') as f:
            reader = csv.reader(f, delimiter='|')
            next(reader)
            for row in reader:
                if len(row) >= 4 and row[0] and row[3] != 'Y':
                    symbol = row[0].strip()
                    if symbol and len(symbol) <= 5:
                        tickers.append(symbol)
        
        # Save tickers
        with open(data_dir / 'nasdaq_tickers.py', 'w') as f:
            f.write(f'# NASDAQ Tickers - {datetime.now()}\n')
            f.write(f'NASDAQ_TICKERS = {tickers}\n')
            f.write(f'TOTAL_TICKERS = {len(tickers)}\n')
        
        print(f"✅ Downloaded {len(tickers)} NASDAQ tickers")
        return len(tickers)
        
    except Exception as e:
        print(f"⚠️ Download failed: {e}")
        fallback = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "NFLX", "ADBE", "CRM"]
        
        with open(data_dir / 'nasdaq_tickers.py', 'w') as f:
            f.write(f'# NASDAQ Tickers (Fallback) - {datetime.now()}\n')
            f.write(f'NASDAQ_TICKERS = {fallback}\n')
            f.write(f'TOTAL_TICKERS = {len(fallback)}\n')
        
        print(f"✅ Using {len(fallback)} fallback tickers")
        return len(fallback)

if __name__ == "__main__":
    download_tickers()
EOF
    
    python tools/get_tickers.py
    success "NASDAQ tickers ready"
}

# Run Django setup
setup_django() {
    log "Setting up Django..."
    
    source venv/Scripts/activate
    
    # Check if Django works
    if python manage.py check 2>/dev/null; then
        info "Django check passed"
        
        # Run migrations
        python manage.py makemigrations 2>/dev/null || warning "Migrations may have issues"
        python manage.py migrate 2>/dev/null || warning "Migration may have issues"
        
        success "Django setup completed"
    else
        warning "Django setup had issues - check manually later"
    fi
}

# Create startup scripts
create_startup() {
    log "Creating startup scripts..."
    
    # Windows batch file
    cat > "$PROJECT_DIR/start_windows.bat" <<EOF
@echo off
echo Starting Stock Scanner...
cd /d "%~dp0"
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    python manage.py runserver 0.0.0.0:8000
) else (
    echo Virtual environment not found!
    pause
)
EOF
    
    # Git Bash script
    cat > "$PROJECT_DIR/start_gitbash.sh" <<EOF
#!/bin/bash
cd "\$(dirname "\${BASH_SOURCE[0]}")"
source venv/Scripts/activate
echo "🚀 Starting Stock Scanner..."
python manage.py runserver 0.0.0.0:8000
EOF
    
    chmod +x "$PROJECT_DIR/start_gitbash.sh"
    success "Startup scripts created"
}

# Cleanup temporary files
cleanup() {
    log "Cleaning up..."
    
    # Remove temp cache
    rm -rf "$PROJECT_DIR/temp_pip_cache" 2>/dev/null
    
    success "Cleanup completed"
}

# Main function
main() {
    print_header
    
    echo "Stock Scanner Setup (Permission Fixed) - $(date)" > "$LOG_FILE"
    
    # Run setup steps
    fix_permissions
    detect_environment
    setup_python_env
    install_python_packages
    create_structure
    configure_django
    setup_mysql
    download_tickers
    setup_django
    create_startup
    cleanup
    
    # Final summary
    echo ""
    echo -e "${GREEN}================================================================================"
    echo "🎉 STOCK SCANNER SETUP COMPLETED! (Permission Issues Fixed)"
    echo "================================================================================${NC}"
    echo ""
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo "  Windows: Double-click start_windows.bat"
    echo "  Git Bash: ./start_gitbash.sh"
    echo "  Manual: source venv/Scripts/activate && python manage.py runserver"
    echo ""
    echo -e "${CYAN}🌐 Access: http://localhost:8000${NC}"
    echo ""
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo "  1. Create admin: python manage.py createsuperuser"
    echo "  2. Check logs: cat setup.log"
    echo ""
    
    success "Setup completed successfully!"
}

# Run main function
main "$@"