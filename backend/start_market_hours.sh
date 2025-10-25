#!/bin/bash
# Market Hours Manager Startup Script
# Starts the automated market hours manager for stock scanner components

set -e

# Force UTF-8 to avoid Unicode issues on Windows/Git Bash consoles
export PYTHONIOENCODING="utf-8"
export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "Stock Scanner - Market Hours Manager"

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

# Check if market_hours_manager.py exists
if [ ! -f "market_hours_manager.py" ]; then
    print_error "market_hours_manager.py not found in current directory"
    exit 1
fi

# Check if required packages are installed
print_step "Checking required packages"
$PYTHON_CMD -c "import pytz, psutil, schedule" 2>/dev/null || {
    print_warning "Some required packages may be missing"
    print_step "Installing required packages"
    
    # Try to install missing packages
    if command -v pip3 &> /dev/null; then
        pip3 install pytz psutil schedule
    elif command -v pip &> /dev/null; then
        pip install pytz psutil schedule
    else
        print_error "pip not found. Please install required packages manually:"
        print_error "pip install pytz psutil schedule"
        exit 1
    fi
    
    print_success "Required packages installed"
}

# Check if manage.py exists (Django project)
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Make sure you're in the Django project root directory"
    exit 1
fi

# Check if restart-enabled scripts exist
if [ ! -f "enhanced_stock_retrieval_working.py" ]; then
    print_warning "enhanced_stock_retrieval_working.py not found"
    print_warning "Stock retrieval component will not work"
fi

if [ ! -f "news_scraper_with_restart.py" ]; then
    print_warning "news_scraper_with_restart.py not found"
    print_warning "News scraper component will not work"
fi

if [ ! -f "email_sender_with_restart.py" ]; then
    print_warning "email_sender_with_restart.py not found"
    print_warning "Email sender component will not work"
fi

print_success "Environment checks passed"

# Check if proxy scraper exists
if [ -f "proxy_scraper_validator.py" ]; then
    print_success "Proxy scraper found - daily updates will include proxy refresh"
else
    print_warning "proxy_scraper_validator.py not found"
    print_warning "Proxy updates will not be available"
fi

# Display menu options
echo -e "\n${BLUE}Select Operation Mode:${NC}"
echo "1) Start Market Hours Manager (default)"
echo "2) Start with Daily 9 AM Updates"
echo "3) Update Proxies Only"
echo "4) Run Single Stock Update"
echo "5) Exit"
echo ""
read -t 10 -p "Select option [1-5] (default: 1 in 10s): " -n 1 -r OPTION || OPTION="1"
echo ""

case "${OPTION:-1}" in
    1)
        print_step "Starting Market Hours Manager"
        print_warning "Press Ctrl+C to stop the manager gracefully"
        print_warning "Logs will be written to market_hours_manager.log"
        
        echo -e "\n${YELLOW}Market Hours Schedule:${NC}"
        echo "  Premarket:    4:00 AM - 9:30 AM ET (retrieval, news, emails)"
        echo "  Market:       9:30 AM - 4:00 PM ET (all components + server)"
        echo "  Postmarket:   4:00 PM - 8:00 PM ET (retrieval, news, emails)"
        echo "  After Hours:  8:00 PM - 4:00 AM ET (all components stopped)"
        
        # Start the market hours manager
        exec $PYTHON_CMD market_hours_manager.py
        ;;
    
    2)
        print_step "Starting with Daily 9 AM Updates"
        print_warning "This will update proxies and run full stock update at 9 AM ET daily"
        print_warning "Press Ctrl+C to stop"
        
        echo -e "\n${YELLOW}Daily Update Schedule:${NC}"
        echo "  9:00 AM ET - Proxy refresh + Full stock update"
        echo "  Plus regular 3-minute stock cycles during market hours"
        
        # Start enhanced stock retrieval with daily update mode
        exec $PYTHON_CMD enhanced_stock_retrieval_working.py -daily-update -schedule
        ;;
    
    3)
        print_step "Updating Proxies"
        if [ -f "proxy_scraper_validator.py" ]; then
            $PYTHON_CMD proxy_scraper_validator.py -threads 50 -timeout 5
        else
            print_error "Proxy scraper not found"
            exit 1
        fi
        ;;
    
    4)
        print_step "Running Single Stock Update"
        $PYTHON_CMD enhanced_stock_retrieval_working.py
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