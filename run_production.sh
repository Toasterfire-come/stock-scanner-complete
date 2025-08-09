#!/bin/bash
# Stock Scanner - Production Ready Git Bash Script
# Clean, minimal setup for Windows Git Bash environment

set -e  # Exit on any error

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

# Control whether to use virtual environment (default: yes)
USE_VENV=1
if [ "${SKIP_VENV:-0}" = "1" ] || [ "${NO_VENV:-0}" = "1" ]; then
    USE_VENV=0
fi

# Check if running in Git Bash
check_environment() {
    print_step "Checking environment compatibility"
    
    if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" ]]; then
        print_warning "This script is optimized for Git Bash on Windows"
        print_warning "Current environment: $OSTYPE"
    fi
    
    # Check Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Use python3 if available, otherwise python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    print_success "Environment check passed"
}

# Create virtual environment if it doesn't exist
setup_virtual_environment() {
    print_step "Setting up virtual environment"
    
    # Allow skipping venv via flag/env var
    if [ "$USE_VENV" != "1" ]; then
        print_warning "Skipping virtual environment (requested)"
        return 0
    fi
    
    if [ ! -d "venv" ]; then
        print_step "Creating virtual environment"
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment"
    source venv/Scripts/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies"
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install requirements based on platform
    if [ -f "requirements_windows.txt" ]; then
        print_step "Installing Windows-specific requirements"
        pip install -r requirements_windows.txt
    elif [ -f "requirements.txt" ]; then
        print_step "Installing standard requirements"
        pip install -r requirements.txt
    else
        print_error "No requirements file found"
        exit 1
    fi
    
    print_success "Dependencies installed"
}

# Setup environment variables
setup_environment() {
    print_step "Setting up environment variables"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_step "Creating .env from .env.example"
            cp .env.example .env
            print_warning "Please edit .env file with your configuration"
        else
            print_error ".env file not found and no .env.example available"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Run database migrations
run_migrations() {
    print_step "Running database migrations"
    
    python manage.py makemigrations
    python manage.py migrate
    
    print_success "Database migrations completed"
}

# Collect static files for production
collect_static_files() {
    print_step "Collecting static files"
    
    python manage.py collectstatic --noinput
    
    print_success "Static files collected"
}

# Create superuser if needed
create_superuser() {
    print_step "Checking for superuser"
    
    if python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" | grep -q "False"; then
        print_step "Creating superuser"
        echo "Please create a superuser account:"
        python manage.py createsuperuser
    else
        print_success "Superuser already exists"
    fi
}

# Run production readiness check
check_production_readiness() {
    print_step "Running production readiness check"
    
    if [ -f "check_production_ready.py" ]; then
        python check_production_ready.py
    else
        print_warning "Production readiness checker not found"
    fi
}

# Start the Django development server
start_server() {
    print_step "Starting Django development server"
    
    echo -e "\n${GREEN}Server will start at: http://127.0.0.1:8000${NC}"
    echo -e "${GREEN}Admin panel at: http://127.0.0.1:8000/admin${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"
    
    python manage.py runserver 0.0.0.0:8000
}

# Start Cloudflare tunnel and Django server
start_with_tunnel() {
    print_step "Starting Cloudflare tunnel and Django server"

    # Check cloudflared
    if ! command -v cloudflared &> /dev/null; then
        print_error "cloudflared not found. Please install Cloudflare tunnel."
        exit 1
    fi

    # Default tunnel name
    TUNNEL_NAME=${TUNNEL_NAME:-django-api}

    # Verify tunnel exists
    if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
        print_error "Tunnel '$TUNNEL_NAME' not found. Run setup_cloudflare_tunnel_auto.sh first."
        exit 1
    fi

    # Start tunnel in background
    print_step "Starting Cloudflare tunnel: $TUNNEL_NAME"
    cloudflared tunnel run "$TUNNEL_NAME" &
    TUNNEL_PID=$!
    sleep 2

    # Start Django server in background
    print_step "Starting Django server"
    python manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!

    echo -e "\n${GREEN}Services running:${NC}"
    echo -e "  📡 Cloudflare Tunnel (PID: $TUNNEL_PID)"
    echo -e "  🐍 Django Server (PID: $SERVER_PID)"
    echo -e "\n${YELLOW}Press Ctrl+C to stop both services${NC}"

    # Wait on both processes
    wait $TUNNEL_PID $SERVER_PID
}

# Main execution function
main() {
    print_header "Stock Scanner - Production Setup"
    
    # Parse global options and determine command (options can appear anywhere)
    COMMAND=""
    for arg in "$@"; do
        case "$arg" in
            --no-venv)
                USE_VENV=0
                ;;
            -h|--help|help|setup|start|start-tunnel|migrate|static|check)
                # First non-option token is the command
                if [ -z "$COMMAND" ] && [[ "$arg" != --* ]]; then
                    COMMAND="$arg"
                fi
                ;;
            *)
                # If it's not an option (doesn't start with -), and command not set yet
                if [ -z "$COMMAND" ] && [[ "$arg" != -* ]]; then
                    COMMAND="$arg"
                fi
                ;;
        esac
    done
    [ -z "$COMMAND" ] && COMMAND="setup"
    
    # Execute command
    case "$COMMAND" in
        "setup")
            check_environment
            setup_virtual_environment
            install_dependencies
            setup_environment
            run_migrations
            collect_static_files
            create_superuser
            check_production_readiness
            print_success "Setup completed successfully!"
            echo -e "\n${GREEN}To start the server, run: ./run_production.sh start${NC}"
            ;;
        "start")
            check_environment
            setup_virtual_environment
            start_server
            ;;
        "start-tunnel")
            check_environment
            setup_virtual_environment
            start_with_tunnel
            ;;
        "migrate")
            check_environment
            setup_virtual_environment
            run_migrations
            ;;
        "static")
            check_environment
            setup_virtual_environment
            collect_static_files
            ;;
        "check")
            check_environment
            setup_virtual_environment
            check_production_readiness
            ;;
        "help"|"-h"|"--help")
            echo "Stock Scanner - Production Script"
            echo ""
            echo "Usage: ./run_production.sh [command] [options]"
            echo ""
            echo "Commands:"
            echo "  setup         - Full setup (default)"
            echo "  start         - Start the Django server"
            echo "  start-tunnel  - Start Cloudflare tunnel and Django server"
            echo "  migrate       - Run database migrations"
            echo "  static        - Collect static files"
            echo "  check         - Run production readiness check"
            echo "  help          - Show this help message"
            echo ""
            echo "Options:"
            echo "  --no-venv           Skip creating/activating virtual environment"
            echo "                      (or set SKIP_VENV=1 / NO_VENV=1)"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run './run_production.sh help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
