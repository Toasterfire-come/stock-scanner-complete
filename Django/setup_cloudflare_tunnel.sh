#!/bin/bash

echo "Cloudflare Tunnel Setup - Hide Your Home IP"
echo "============================================"
echo

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "ERROR: cloudflared is not installed"
    echo
    echo "Please download cloudflared from:"
    echo "https://github.com/cloudflare/cloudflared/releases"
    echo
    echo "Extract to a folder and add to PATH, then run this script again."
    exit 1
fi

echo "SUCCESS: cloudflared is installed"
echo

# Check if Django is running
echo "Checking if Django is running..."
if command -v curl &> /dev/null; then
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/simple/stocks/)
    if [ "$response" != "200" ]; then
        echo "WARNING: Django is not running on port 8000"
        echo
        echo "Please start Django first:"
        echo "python3 manage.py runserver 127.0.0.1:8000"
        echo
        echo "Then run this script again."
        exit 1
    fi
else
    echo "WARNING: curl not available, skipping Django check"
fi

echo "SUCCESS: Django is running"
echo

# Login to Cloudflare
echo "Step 1: Logging in to Cloudflare..."
echo "This will open your browser for authentication."
echo
cloudflared tunnel login

# Create tunnel
echo
echo "Step 2: Creating tunnel..."
cloudflared tunnel create django-api

# Get tunnel ID
tunnel_id=$(cloudflared tunnel list | grep django-api | awk '{print $1}')

if [ -z "$tunnel_id" ]; then
    echo "ERROR: Failed to get tunnel ID"
    exit 1
fi

echo
echo "SUCCESS: Tunnel created with ID: $tunnel_id"
echo

# Create config directory
config_dir="$HOME/.cloudflared"
mkdir -p "$config_dir"

# Create config file
echo "Step 3: Creating configuration file..."
cat > "$config_dir/config.yml" << EOF
tunnel: $tunnel_id
credentials-file: $config_dir/$tunnel_id.json

ingress:
  # Your Django API
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  
  # Catch-all rule
  - service: http_status:404
EOF

echo "SUCCESS: Configuration file created"
echo

# Instructions
echo "Step 4: Next Steps"
echo "==================="
echo
echo "1. Edit the config file to use your domain:"
echo "   notepad \"$config_dir/config.yml\""
echo
echo "2. Replace \"api.yourdomain.com\" with your actual domain"
echo
echo "3. Start the tunnel:"
echo "   cloudflared tunnel run django-api"
echo
echo "4. Update WordPress settings with your tunnel URL"
echo

echo "Configuration file location: $config_dir/config.yml"
echo
echo "Setup complete! Follow the steps above to finish configuration."