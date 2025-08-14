#!/usr/bin/env python3
"""
Setup script for external Django API access
"""

import os
import sys
import subprocess
import socket
import requests
import shutil
import re
from datetime import datetime

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def update_django_settings():
    """Update Django settings for external access with backup and robust parsing"""
    settings_file = "stockscanner_django/settings.py"
    
    if not os.path.exists(settings_file):
        print("ERROR: Django settings file not found!")
        return False
    
    # Create backup with timestamp
    backup_file = f"{settings_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(settings_file, backup_file)
        print(f"SUCCESS: Created backup at {backup_file}")
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"Your local IP: {local_ip}")
    
    # Use regex to find and update ALLOWED_HOSTS more robustly
    allowed_hosts_pattern = r'ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]'
    match = re.search(allowed_hosts_pattern, content)
    
    if not match:
        print("ERROR: Could not find ALLOWED_HOSTS in settings.py")
        return False
    
    current_hosts = match.group(1)
    required_hosts = ['localhost', '127.0.0.1', local_ip, '0.0.0.0']
    
    # Check if all required hosts are already present
    hosts_present = all(host in current_hosts for host in required_hosts)
    
    if not hosts_present:
        # Build new ALLOWED_HOSTS list
        new_hosts_str = ', '.join([f"'{host}'" for host in required_hosts])
        new_line = f"ALLOWED_HOSTS = [{new_hosts_str}]"
        
        # Replace the ALLOWED_HOSTS line
        updated_content = re.sub(allowed_hosts_pattern, new_line, content)
        
        # Write back to file
        with open(settings_file, 'w') as f:
            f.write(updated_content)
        
        print("SUCCESS: Updated ALLOWED_HOSTS for external access")
    else:
        print("SUCCESS: ALLOWED_HOSTS already configured for external access")
    
    return True

def test_api_access():
    """Test if API is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/simple/stocks/", timeout=5)
        if response.status_code == 200:
            print("SUCCESS: API is accessible locally")
            return True
        else:
            print(f"ERROR: API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API not accessible: {e}")
        return False

def start_django_server():
    """Start Django server for external access"""
    print("\nStarting Django server for external access...")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start Django on all interfaces
        subprocess.run([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")

def main():
    """Main setup function"""
    print("Django API External Access Setup")
    print("=" * 40)
    
    # Step 1: Update settings
    print("\n1. Updating Django settings...")
    if not update_django_settings():
        return
    
    # Step 2: Check if Django is running
    print("\n2. Testing API access...")
    if not test_api_access():
        print("\nStarting Django server...")
        start_django_server()
        return
    
    # Step 3: Get connection info
    local_ip = get_local_ip()
    print(f"\n3. Connection Information:")
    print(f"   Local API URL: http://localhost:8000/api")
    print(f"   External API URL: http://{local_ip}:8000/api")
    print(f"   WordPress Plugin URL: http://{local_ip}:8000/api")
    
    # Step 4: Instructions
    print(f"\n4. Next Steps:")
    print(f"   Update WordPress plugin settings:")
    print(f"      API URL: http://{local_ip}:8000/api")
    print(f"   Configure router port forwarding:")
    print(f"      External Port: 8000")
    print(f"      Internal IP: {local_ip}")
    print(f"      Internal Port: 8000")
    print(f"   Test connection in WordPress admin")
    
    # Step 5: Start server
    print(f"\n5. Starting server for external access...")
    start_django_server()

if __name__ == "__main__":
    main()