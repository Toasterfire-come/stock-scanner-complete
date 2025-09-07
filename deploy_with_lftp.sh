#!/bin/bash

# Deploy script using lftp
echo "🚀 Starting deployment to webspace..."

# Configuration
SFTP_HOST="access-5018544625.webspace-host.com"
SFTP_PORT="22"
SFTP_USER="a2565254"
SFTP_PASS="C2rt3rK#2010"
BUILD_DIR="/workspace/frontend/build"
REMOTE_DIR="/html"

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Please run the build first."
    exit 1
fi

echo "📦 Preparing to upload build files..."

# Create a temporary script for lftp
cat > /tmp/lftp_script.txt << EOF
set sftp:auto-confirm yes
set ssl:verify-certificate no
open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST:$SFTP_PORT
cd $REMOTE_DIR
mirror -R --verbose --delete-first $BUILD_DIR/ ./
bye
EOF

# Check if lftp is available
if command -v lftp &> /dev/null; then
    echo "📤 Uploading files using lftp..."
    lftp -f /tmp/lftp_script.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment successful!"
    else
        echo "❌ Deployment failed."
        exit 1
    fi
else
    echo "lftp not found. Creating manual upload instructions..."
    
    # Create manual instructions
    cat > /workspace/DEPLOYMENT_INSTRUCTIONS.txt << EOI
MANUAL DEPLOYMENT INSTRUCTIONS
==============================

Since automated deployment tools are not available, please follow these steps:

1. Use an SFTP client (like FileZilla, Cyberduck, or WinSCP)

2. Connection details:
   - Host: access-5018544625.webspace-host.com
   - Port: 22
   - Protocol: SFTP
   - Username: a2565254
   - Password: C2rt3rK#2010

3. Upload the contents of the 'build' folder:
   - Local folder: /workspace/frontend/build/
   - Remote folder: /html/ (or your webspace root)

4. Make sure to upload ALL files and folders including:
   - index.html
   - static/ folder
   - manifest.json
   - robots.txt
   - All other files in the build directory

5. After upload, your site should be live!

Build files are ready at: /workspace/frontend/build/
EOI

    echo "📝 Manual deployment instructions created at: /workspace/DEPLOYMENT_INSTRUCTIONS.txt"
    echo ""
    echo "Since automated deployment is not available in this environment,"
    echo "please follow the manual instructions to deploy your site."
fi

# Clean up
rm -f /tmp/lftp_script.txt

echo "🎉 Process complete!"