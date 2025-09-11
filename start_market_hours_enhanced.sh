#!/bin/bash
# Enhanced Market Hours Manager Startup Script with Integrated Proxy Management
# Starts the automated market hours manager with daily updates at 9 AM

set -e

# Force UTF-8 to avoid Unicode issues
export PYTHONIOENCODING="utf-8"
export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
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

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "Enhanced Stock Scanner - Market Hours Manager"
print_info "With Integrated Proxy Management & Daily 9 AM Updates"

# Check if Python is available
print_step "Checking Python installation"
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

print_success "Python found: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
print_info "Python version: $PYTHON_VERSION"

# Check if required files exist
print_step "Checking required components"

REQUIRED_FILES=(
    "market_hours_manager_enhanced.py"
    "enhanced_stock_retrieval_integrated.py"
    "integrated_proxy_manager.py"
    "daily_market_updater.py"
    "proxy_scraper_validator.py"
    "utils/proxy_utils.py"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
        print_warning "Missing: $file"
    else
        print_success "Found: $file"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    print_error "Missing required files. Please ensure all components are installed."
    print_info "Missing files: ${MISSING_FILES[*]}"
    exit 1
fi

# Check if Django project exists
if [ ! -f "manage.py" ]; then
    print_warning "manage.py not found. Django server component will not work"
    print_info "Make sure you're in the Django project root directory"
fi

# Check and install required packages
print_step "Checking required Python packages"

REQUIRED_PACKAGES=(
    "pytz"
    "psutil"
    "schedule"
    "requests"
    "beautifulsoup4"
    "yfinance"
    "pandas"
)

MISSING_PACKAGES=()
for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! $PYTHON_CMD -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_warning "Missing packages: ${MISSING_PACKAGES[*]}"
    print_step "Installing missing packages"
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install required packages manually:"
        print_error "pip install ${MISSING_PACKAGES[*]}"
        exit 1
    fi
    
    # Install packages
    $PIP_CMD install ${MISSING_PACKAGES[*]}
    
    # Also install from requirements if exists
    if [ -f "requirements_proxy.txt" ]; then
        print_info "Installing from requirements_proxy.txt"
        $PIP_CMD install -r requirements_proxy.txt
    fi
    
    print_success "Required packages installed"
else
    print_success "All required packages are installed"
fi

# Check for existing proxy data
print_step "Checking proxy data"
if [ -f "working_proxies.json" ]; then
    PROXY_AGE=$(( ($(date +%s) - $(stat -c %Y "working_proxies.json" 2>/dev/null || stat -f %m "working_proxies.json" 2>/dev/null)) / 3600 ))
    if [ $PROXY_AGE -gt 24 ]; then
        print_warning "Proxy list is $PROXY_AGE hours old. Will be updated at 8:45 AM ET"
    else
        print_success "Proxy list found (age: $PROXY_AGE hours)"
    fi
else
    print_warning "No proxy list found. Will be created at 8:45 AM ET"
fi

# Display configuration
print_header "Configuration"
echo -e "${MAGENTA}Schedule:${NC}"
echo "  ${CYAN}8:45 AM ET${NC} - Daily proxy update (scrape & validate)"
echo "  ${CYAN}9:00 AM ET${NC} - Daily market update (stocks, news, emails)"
echo ""
echo -e "${MAGENTA}Market Hours (Eastern Time):${NC}"
echo "  ${YELLOW}Premarket:${NC}    4:00 AM - 9:30 AM (retrieval, news, emails)"
echo "  ${GREEN}Market:${NC}       9:30 AM - 4:00 PM (all components + server)"
echo "  ${YELLOW}Postmarket:${NC}   4:00 PM - 8:00 PM (retrieval, news, emails)"
echo "  ${RED}After Hours:${NC}  8:00 PM - 4:00 AM (all components stopped)"
echo ""
echo -e "${MAGENTA}Components:${NC}"
echo "  • Enhanced Stock Retrieval (with integrated proxies)"
echo "  • Proxy Manager (30-minute updates)"
echo "  • News Scraper (5-minute intervals)"
echo "  • Email Sender (10-minute intervals)"
echo "  • Django Server (market hours only)"

# Create log directory if needed
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_info "Created logs directory"
fi

# Offer options
print_header "Startup Options"
echo "1) Start Enhanced Market Hours Manager (recommended)"
echo "2) Run Daily Update Once (test mode)"
echo "3) Update Proxies Only"
echo "4) Check Component Status"
echo "5) Exit"
echo ""
read -p "Select option [1-5]: " -n 1 -r
echo ""

case $REPLY in
    1)
        print_info "Starting Enhanced Market Hours Manager"
        print_warning "Press Ctrl+C to stop the manager gracefully"
        print_warning "Logs will be written to market_hours_manager_enhanced.log"
        
        # Start the enhanced market hours manager
        exec $PYTHON_CMD market_hours_manager_enhanced.py
        ;;
    
    2)
        print_info "Running daily update once (test mode)"
        $PYTHON_CMD daily_market_updater.py -once
        ;;
    
    3)
        print_info "Updating proxies"
        $PYTHON_CMD integrated_proxy_manager.py -github
        ;;
    
    4)
        print_info "Checking component status"
        
        # Check if processes are running
        echo -e "\n${CYAN}Process Status:${NC}"
        
        PROCESSES=(
            "enhanced_stock_retrieval"
            "proxy_scraper"
            "proxy_manager"
            "news_scraper"
            "email_sender"
            "manage.py runserver"
        )
        
        for proc in "${PROCESSES[@]}"; do
            if pgrep -f "$proc" > /dev/null; then
                PID=$(pgrep -f "$proc" | head -1)
                echo -e "  ${GREEN}✓${NC} $proc (PID: $PID)"
            else
                echo -e "  ${RED}✗${NC} $proc"
            fi
        done
        
        # Check proxy stats
        if [ -f "proxy_manager_stats.json" ]; then
            echo -e "\n${CYAN}Proxy Statistics:${NC}"
            $PYTHON_CMD -c "
import json
with open('proxy_manager_stats.json') as f:
    stats = json.load(f)
    print(f'  Last Scrape: {stats.get(\"last_scrape\", \"N/A\")}')
    print(f'  Total Working: {stats.get(\"total_working\", 0)}')
    print(f'  Success Rate: {stats.get(\"validation_history\", [{}])[-1].get(\"success_rate\", 0):.1f}%' if stats.get(\"validation_history\") else '  Success Rate: N/A')
"
        fi
        
        # Check log files
        echo -e "\n${CYAN}Recent Log Activity:${NC}"
        for log in market_hours_manager_enhanced.log daily_market_updater.log proxy_scraper_validator.log; do
            if [ -f "$log" ]; then
                LAST_LINE=$(tail -1 "$log" 2>/dev/null | cut -c1-80)
                echo -e "  $log: $LAST_LINE..."
            fi
        done
        ;;
    
    5)
        print_info "Exiting"
        exit 0
        ;;
    
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac