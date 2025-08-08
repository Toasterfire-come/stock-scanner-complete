#!/bin/bash
# Automated Cloudflare Tunnel Setup for Stock Scanner
# This script sets up a secure tunnel to hide your IP address

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_header "Stock Scanner - Cloudflare Tunnel Setup"

# Check if cloudflared is installed
print_step "Checking if cloudflared is installed"
if ! command -v cloudflared &> /dev/null; then
    print_error "cloudflared is not installed"
    echo "Please install cloudflared first:"
    echo ""
    echo "Linux:"
    echo "wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    echo "sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared"
    echo "sudo chmod +x /usr/local/bin/cloudflared"
    echo ""
    echo "macOS:"
    echo "brew install cloudflared"
    echo ""
    echo "Windows:"
    echo "winget install --id Cloudflare.cloudflared"
    exit 1
fi

print_success "cloudflared is installed"

# Get domain name
DOMAIN=${1:-"retailtradescanner.com"}
TUNNEL_NAME="stock-scanner"
API_SUBDOMAIN="api"
CONFIG_DIR="$HOME/.cloudflared"

print_step "Setting up tunnel for domain: $DOMAIN"

# Create config directory
mkdir -p "$CONFIG_DIR"

# Check if already authenticated
if [ ! -f "$CONFIG_DIR/cert.pem" ]; then
    print_step "Authenticating with Cloudflare"
    print_warning "This will open your browser. Please log in and select your domain."
    cloudflared tunnel login
    print_success "Authentication completed"
else
    print_success "Already authenticated with Cloudflare"
fi

# Create tunnel if it doesn't exist
print_step "Creating tunnel: $TUNNEL_NAME"
TUNNEL_ID=$(cloudflared tunnel list --output json 2>/dev/null | jq -r ".[] | select(.name == \"$TUNNEL_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$TUNNEL_ID" ]; then
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list --output json | jq -r ".[] | select(.name == \"$TUNNEL_NAME\") | .id")
    print_success "Created tunnel with ID: $TUNNEL_ID"
else
    print_success "Tunnel already exists with ID: $TUNNEL_ID"
fi

# Create configuration file
print_step "Creating tunnel configuration"
cat > "$CONFIG_DIR/config.yml" << EOF
tunnel: $TUNNEL_NAME
credentials-file: $CONFIG_DIR/$TUNNEL_ID.json

ingress:
  # Main Django API
  - hostname: $API_SUBDOMAIN.$DOMAIN
    service: http://localhost:8000
    
  # WordPress integration endpoint
  - hostname: $API_SUBDOMAIN.$DOMAIN
    service: http://localhost:8000
    path: /wp-json/*
    
  # API endpoints
  - hostname: $API_SUBDOMAIN.$DOMAIN
    service: http://localhost:8000
    path: /api/*
    
  # Health check endpoint
  - hostname: $API_SUBDOMAIN.$DOMAIN
    service: http://localhost:8000
    path: /health/*
    
  # Catch-all rule (required)
  - service: http_status:404
EOF

print_success "Configuration file created at $CONFIG_DIR/config.yml"

# Display configuration
print_step "Tunnel Configuration Summary"
echo "Domain: $DOMAIN"
echo "API URL: https://$API_SUBDOMAIN.$DOMAIN"
echo "Tunnel ID: $TUNNEL_ID"
echo "Config file: $CONFIG_DIR/config.yml"

# Create DNS instructions
print_step "DNS Configuration Required"
print_warning "You need to add the following DNS record in your Cloudflare dashboard:"
echo ""
echo "Record Type: CNAME"
echo "Name: $API_SUBDOMAIN"
echo "Target: $TUNNEL_ID.cfargotunnel.com"
echo "Proxy status: Proxied (orange cloud)"
echo ""

# Create environment file updates
print_step "Updating environment configuration"
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    # Backup original
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update URLs
    sed -i.tmp "s|API_BASE_URL=.*|API_BASE_URL=https://$API_SUBDOMAIN.$DOMAIN|g" "$ENV_FILE"
    sed -i.tmp "s|PAYPAL_WEBHOOK_URL=.*|PAYPAL_WEBHOOK_URL=https://$API_SUBDOMAIN.$DOMAIN/wp-json/stock-scanner/v1/paypal-webhook|g" "$ENV_FILE"
    
    # Update CORS origins
    CORS_ORIGINS="https://$DOMAIN,https://$API_SUBDOMAIN.$DOMAIN"
    sed -i.tmp "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=$CORS_ORIGINS|g" "$ENV_FILE"
    
    # Update Django allowed hosts
    ALLOWED_HOSTS="localhost,127.0.0.1,$DOMAIN,$API_SUBDOMAIN.$DOMAIN"
    sed -i.tmp "s|DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS|g" "$ENV_FILE"
    
    rm -f "$ENV_FILE.tmp"
    print_success "Environment file updated"
else
    print_warning "No .env file found. Please update your environment configuration manually."
fi

# Create systemd service file (Linux)
if command -v systemctl &> /dev/null; then
    print_step "Creating systemd service"
    cat > cloudflare-tunnel.service << EOF
[Unit]
Description=Cloudflare Tunnel for Stock Scanner
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
ExecStart=/usr/local/bin/cloudflared tunnel run $TUNNEL_NAME
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Systemd service file created: cloudflare-tunnel.service"
    print_warning "To install the service, run:"
    echo "sudo mv cloudflare-tunnel.service /etc/systemd/system/"
    echo "sudo systemctl enable cloudflare-tunnel"
    echo "sudo systemctl start cloudflare-tunnel"
fi

# Create startup scripts
print_step "Creating startup scripts"

# Linux/macOS startup script
cat > start_tunnel.sh << 'EOF'
#!/bin/bash
# Start Cloudflare Tunnel and Django Server

echo "Starting Cloudflare Tunnel..."
cloudflared tunnel run stock-scanner &
TUNNEL_PID=$!

sleep 5

echo "Starting Django Server..."
python3 manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!

echo "Services started:"
echo "Cloudflare Tunnel PID: $TUNNEL_PID"
echo "Django Server PID: $SERVER_PID"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $TUNNEL_PID $SERVER_PID; exit' INT
wait
EOF

chmod +x start_tunnel.sh

# Windows startup script
cat > start_tunnel.bat << 'EOF'
@echo off
echo Starting Cloudflare Tunnel...
start /B cloudflared tunnel run stock-scanner

timeout /t 5

echo Starting Django Server...
start /B python manage.py runserver 0.0.0.0:8000

echo Services started successfully!
echo Check the Cloudflare dashboard for tunnel status.
pause
EOF

print_success "Startup scripts created: start_tunnel.sh and start_tunnel.bat"

print_header "Setup Complete!"
print_success "Cloudflare tunnel is configured and ready to use"

echo ""
echo "Next Steps:"
echo "1. Add the DNS record in your Cloudflare dashboard (see instructions above)"
echo "2. Test the tunnel: cloudflared tunnel run $TUNNEL_NAME"
echo "3. Start everything together: ./start_tunnel.sh"
echo ""
echo "Your API will be available at: https://$API_SUBDOMAIN.$DOMAIN"
echo "Your IP address will be hidden behind Cloudflare's network"
echo ""
echo "Logs and monitoring:"
echo "- Tunnel logs: cloudflared tunnel run $TUNNEL_NAME --loglevel debug"
echo "- Market hours manager logs: tail -f market_hours_manager.log"

print_header "Security Benefits"
echo "✅ Your real IP address is hidden"
echo "✅ DDoS protection from Cloudflare"  
echo "✅ SSL/TLS encryption automatically enabled"
echo "✅ Geographic load balancing available"
echo "✅ Access logs and analytics in Cloudflare dashboard"