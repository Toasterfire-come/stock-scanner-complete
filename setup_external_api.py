#!/usr/bin/env python3
"""
Setup script for external Django API access
"""

import os
import sys
import subprocess
import socket
import requests

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
    """Update Django settings for external access"""
    settings_file = "stockscanner_django/settings.py"
    
    if not os.path.exists(settings_file):
        print("❌ Django settings file not found!")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"📍 Your local IP: {local_ip}")
    
    # Update ALLOWED_HOSTS
    if '0.0.0.0' not in content:
        # Find ALLOWED_HOSTS line and update it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'ALLOWED_HOSTS =' in line:
                # Update the line to include external access
                lines[i] = f"ALLOWED_HOSTS = ['localhost', '127.0.0.1', '{local_ip}', '0.0.0.0']"
                break
        
        # Write back to file
        with open(settings_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated ALLOWED_HOSTS for external access")
    else:
        print("✅ ALLOWED_HOSTS already configured for external access")
    
    return True

def test_api_access():
    """Test if API is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/simple/stocks/", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible locally")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API not accessible: {e}")
        return False

def start_django_server():
    """Start Django server for external access"""
    print("\n🚀 Starting Django server for external access...")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start Django on all interfaces
        subprocess.run([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped")

def main():
    """Main setup function"""
    print("🔧 Django API External Access Setup")
    print("=" * 40)
    
    # Step 1: Update settings
    print("\n1️⃣ Updating Django settings...")
    if not update_django_settings():
        return
    
    # Step 2: Check if Django is running
    print("\n2️⃣ Testing API access...")
    if not test_api_access():
        print("\n💡 Starting Django server...")
        start_django_server()
        return
    
    # Step 3: Get connection info
    local_ip = get_local_ip()
    print(f"\n3️⃣ Connection Information:")
    print(f"   Local API URL: http://localhost:8000/api")
    print(f"   External API URL: http://{local_ip}:8000/api")
    print(f"   WordPress Plugin URL: http://{local_ip}:8000/api")
    
    # Step 4: Instructions
    print(f"\n4️⃣ Next Steps:")
    print(f"   📝 Update WordPress plugin settings:")
    print(f"      API URL: http://{local_ip}:8000/api")
    print(f"   🔧 Configure router port forwarding:")
    print(f"      External Port: 8000")
    print(f"      Internal IP: {local_ip}")
    print(f"      Internal Port: 8000")
    print(f"   🧪 Test connection in WordPress admin")
    
    # Step 5: Start server
    print(f"\n5️⃣ Starting server for external access...")
    start_django_server()

if __name__ == "__main__":
    main()