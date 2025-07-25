#!/bin/bash
# Git Bash Helper Commands for Stock Scanner
# Source this file to get helpful aliases and functions
# Usage: source git_bash_commands.sh

# Colors for output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Determine Python command
if command -v python3 &> /dev/null; then
    export PYTHON_CMD="python3"
    export PIP_CMD="pip3"
else
    export PYTHON_CMD="python"
    export PIP_CMD="pip"
fi

# =============================================================================
# SETUP COMMANDS
# =============================================================================

# Main setup command
alias setup='bash setup_git_bash.sh'

# Quick setup for experienced users
quick_setup() {
    print_info "Running quick setup..."
    $PIP_CMD install Django==4.2.11 PyMySQL python-dotenv dj-database-url djangorestframework django-cors-headers
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py migrate
    print_success "Quick setup completed. Run 'start' to launch the server."
}

# Install only Python dependencies
install_deps() {
    print_info "Installing Python dependencies..."
    if [[ -f "requirements_windows.txt" ]]; then
        $PIP_CMD install -r requirements_windows.txt
    elif [[ -f "requirements.txt" ]]; then
        $PIP_CMD install -r requirements.txt
    else
        print_error "No requirements file found"
        return 1
    fi
    print_success "Dependencies installed"
}

# =============================================================================
# DATABASE COMMANDS
# =============================================================================

# Create database (requires MySQL root password)
create_db() {
    print_info "Creating MySQL database..."
    cat > temp_create_db.sql << 'EOF'
CREATE DATABASE IF NOT EXISTS stock_scanner_nasdaq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'stock_scanner'@'localhost' IDENTIFIED BY 'StockScanner2024';
GRANT ALL PRIVILEGES ON stock_scanner_nasdaq.* TO 'stock_scanner'@'localhost';
FLUSH PRIVILEGES;
SELECT 'Database created successfully' as result;
EOF
    
    if mysql -u root -p < temp_create_db.sql; then
        rm -f temp_create_db.sql
        print_success "Database created successfully"
    else
        rm -f temp_create_db.sql
        print_error "Failed to create database"
    fi
}

# Test database connection
test_db() {
    print_info "Testing database connection..."
    $PYTHON_CMD -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='stock_scanner', password='StockScanner2024', database='stock_scanner_nasdaq')
    conn.close()
    print('SUCCESS: Database connection working')
except Exception as e:
    print(f'ERROR: Database connection failed: {e}')
"
}

# Reset database (WARNING: This will delete all data!)
reset_db() {
    print_warning "This will delete ALL data in the database!"
    read -p "Are you sure? Type 'yes' to continue: " confirm
    if [[ "$confirm" == "yes" ]]; then
        print_info "Resetting database..."
        mysql -u root -p -e "DROP DATABASE IF EXISTS stock_scanner_nasdaq; CREATE DATABASE stock_scanner_nasdaq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
        $PYTHON_CMD manage.py migrate
        print_success "Database reset completed"
    else
        print_info "Database reset cancelled"
    fi
}

# =============================================================================
# DJANGO COMMANDS
# =============================================================================

# Start Django development server
alias start='export DJANGO_SETTINGS_MODULE="stockscanner_django.settings" && $PYTHON_CMD manage.py runserver'

# Start on specific port
start_port() {
    local port=${1:-8000}
    print_info "Starting server on port $port..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py runserver "0.0.0.0:$port"
}

# Run Django migrations
migrate() {
    print_info "Running Django migrations..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py makemigrations
    $PYTHON_CMD manage.py migrate
    print_success "Migrations completed"
}

# Create Django superuser
create_admin() {
    print_info "Creating Django superuser..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py createsuperuser
}

# Django shell
alias shell='export DJANGO_SETTINGS_MODULE="stockscanner_django.settings" && $PYTHON_CMD manage.py shell'

# Django system check
check_django() {
    print_info "Running Django system check..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py check
}

# Show migration status
show_migrations() {
    print_info "Showing migration status..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py showmigrations
}

# Collect static files
collect_static() {
    print_info "Collecting static files..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    $PYTHON_CMD manage.py collectstatic --noinput
}

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

# Clean up cache and temporary files
cleanup() {
    print_info "Cleaning up cache and temporary files..."
    
    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # Django cache
    rm -f db.sqlite3 db.sqlite3-journal 2>/dev/null || true
    
    # IDE files
    rm -rf .vscode .idea 2>/dev/null || true
    find . -name "*.swp" -delete 2>/dev/null || true
    
    # OS files
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    # Log files
    find . -name "*.log" -delete 2>/dev/null || true
    
    # Temporary files
    rm -rf temp tmp .tmp 2>/dev/null || true
    find . -name "*.bak" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Show project status
status() {
    print_info "Stock Scanner Project Status"
    echo "================================"
    
    # Python version
    echo "Python: $($PYTHON_CMD --version 2>&1)"
    
    # Django version
    if $PYTHON_CMD -c "import django; print('Django:', django.get_version())" 2>/dev/null; then
        :
    else
        print_warning "Django not installed"
    fi
    
    # Database connection
    if $PYTHON_CMD -c "import pymysql; pymysql.connect(host='localhost', user='stock_scanner', password='StockScanner2024', database='stock_scanner_nasdaq').close(); print('Database: Connected')" 2>/dev/null; then
        :
    else
        print_warning "Database: Not connected"
    fi
    
    # Check if server is running
    if curl -s http://localhost:8000 >/dev/null 2>&1; then
        print_success "Server: Running on http://localhost:8000"
    else
        echo "Server: Not running"
    fi
    
    # Git status
    if git status --porcelain >/dev/null 2>&1; then
        local changes=$(git status --porcelain | wc -l)
        if [[ $changes -gt 0 ]]; then
            print_warning "Git: $changes uncommitted changes"
        else
            print_success "Git: Working directory clean"
        fi
    fi
}

# Load stock data
load_stocks() {
    print_info "Loading NASDAQ stock data..."
    export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
    
    if [[ -f "stocks/management/commands/load_nasdaq_only.py" ]]; then
        $PYTHON_CMD manage.py load_nasdaq_only
        print_success "Stock data loaded"
    else
        print_error "Stock loading command not found"
    fi
}

# Show logs
logs() {
    local lines=${1:-50}
    print_info "Showing last $lines lines of logs..."
    
    if [[ -f "django.log" ]]; then
        tail -n "$lines" django.log
    elif [[ -f "logs/django.log" ]]; then
        tail -n "$lines" logs/django.log
    else
        print_warning "No log files found"
    fi
}

# =============================================================================
# GIT COMMANDS
# =============================================================================

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# Quick commit and push
quick_commit() {
    local message=${1:-"Quick update from Git Bash"}
    git add -A
    git commit -m "$message"
    git push origin $(git branch --show-current)
    print_success "Changes committed and pushed"
}

# Pull latest changes and update
update() {
    print_info "Updating project..."
    git pull origin $(git branch --show-current)
    install_deps
    migrate
    print_success "Project updated"
}

# =============================================================================
# HELP COMMANDS
# =============================================================================

# Show available commands
help_commands() {
    echo "Stock Scanner Git Bash Commands"
    echo "==============================="
    echo
    echo "SETUP COMMANDS:"
    echo "  setup              - Run full setup script"
    echo "  quick_setup        - Quick setup for experienced users"
    echo "  install_deps       - Install Python dependencies only"
    echo
    echo "DATABASE COMMANDS:"
    echo "  create_db          - Create MySQL database and user"
    echo "  test_db            - Test database connection"
    echo "  reset_db           - Reset database (WARNING: deletes all data)"
    echo
    echo "DJANGO COMMANDS:"
    echo "  start              - Start Django development server"
    echo "  start_port <port>  - Start server on specific port"
    echo "  migrate            - Run Django migrations"
    echo "  create_admin       - Create Django superuser"
    echo "  shell              - Open Django shell"
    echo "  check_django       - Run Django system check"
    echo "  show_migrations    - Show migration status"
    echo "  collect_static     - Collect static files"
    echo
    echo "UTILITY COMMANDS:"
    echo "  cleanup            - Clean cache and temporary files"
    echo "  status             - Show project status"
    echo "  load_stocks        - Load NASDAQ stock data"
    echo "  logs [lines]       - Show application logs"
    echo
    echo "GIT COMMANDS:"
    echo "  gs, ga, gc, gp, gl - Git shortcuts"
    echo "  quick_commit [msg] - Quick commit and push"
    echo "  update             - Pull changes and update project"
    echo
    echo "HELP:"
    echo "  help_commands      - Show this help"
}

# Show welcome message
print_info "Stock Scanner Git Bash commands loaded!"
print_info "Type 'help_commands' to see all available commands"
print_info "Type 'setup' to run the full setup script"
print_info "Type 'start' to start the Django server"