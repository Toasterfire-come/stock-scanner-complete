#!/bin/bash

echo "Django API External Access Setup"
echo "================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python and try again"
    exit 1
fi

# Check if Django project exists
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Function to get local IP
get_local_ip() {
    if command -v ipconfig &> /dev/null; then
        # Windows
        ipconfig | grep "IPv4 Address" | head -1 | awk '{print $NF}'
    else
        # Linux/Mac
        hostname -I | awk '{print $1}'
    fi
}

# Function to update Django settings
update_django_settings() {
    local_ip=$(get_local_ip)
    echo "Your local IP: $local_ip"
    
    settings_file="stockscanner_django/settings.py"
    
    if [ ! -f "$settings_file" ]; then
        echo "ERROR: Django settings file not found!"
        return 1
    fi
    
    # Check if already configured
    if grep -q "0.0.0.0" "$settings_file"; then
        echo "SUCCESS: ALLOWED_HOSTS already configured for external access"
        return 0
    fi
    
    # Update ALLOWED_HOSTS
    sed -i "s/ALLOWED_HOSTS = \[.*\]/ALLOWED_HOSTS = ['localhost', '127.0.0.1', '$local_ip', '0.0.0.0']/" "$settings_file"
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS: Updated ALLOWED_HOSTS for external access"
    else
        echo "ERROR: Failed to update ALLOWED_HOSTS"
        return 1
    fi
}

# Function to test API access
test_api_access() {
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/simple/stocks/)
        if [ "$response" = "200" ]; then
            echo "SUCCESS: API is accessible locally"
            return 0
        else
            echo "ERROR: API returned status code: $response"
            return 1
        fi
    else
        echo "WARNING: curl not available, skipping API test"
        return 1
    fi
}

# Function to start Django server
start_django_server() {
    echo
    echo "Starting Django server for external access..."
    echo "Press Ctrl+C to stop the server"
    echo
    
    python3 manage.py runserver 0.0.0.0:8000
}

# Main execution
echo "1. Updating Django settings..."
if ! update_django_settings; then
    exit 1
fi

echo
echo "2. Testing API access..."
if ! test_api_access; then
    echo
    echo "Starting Django server..."
    start_django_server
    exit 0
fi

# Get connection info
local_ip=$(get_local_ip)
echo
echo "3. Connection Information:"
echo "   Local API URL: http://localhost:8000/api"
echo "   External API URL: http://$local_ip:8000/api"
echo "   WordPress Plugin URL: http://$local_ip:8000/api"

echo
echo "4. Next Steps:"
echo "   Update WordPress plugin settings:"
echo "      API URL: http://$local_ip:8000/api"
echo "   Configure router port forwarding:"
echo "      External Port: 8000"
echo "      Internal IP: $local_ip"
echo "      Internal Port: 8000"
echo "   Test connection in WordPress admin"

echo
echo "5. Starting server for external access..."
start_django_server