#!/bin/bash

# Deploy script for Trade Scan Pro
echo "🚀 Starting deployment to webspace..."

# Configuration
SFTP_HOST="access-5018544625.webspace-host.com"
SFTP_PORT="22"
SFTP_USER="a2565254"
SFTP_PASS="C2rt3rK#2010"
BUILD_DIR="/workspace/frontend/build"
REMOTE_DIR="/html"  # Adjust if needed

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Please run the build first."
    exit 1
fi

echo "📦 Preparing to upload build files..."

# Create SFTP batch file
cat > /tmp/sftp_batch.txt << EOF
cd $REMOTE_DIR
put -r $BUILD_DIR/* .
bye
EOF

# Use sshpass for automated SFTP deployment
echo "📤 Uploading files to webspace..."
sshpass -p "$SFTP_PASS" sftp -P $SFTP_PORT -oBatchMode=no -oStrictHostKeyChecking=no -b /tmp/sftp_batch.txt $SFTP_USER@$SFTP_HOST

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your site should be live at your webspace URL"
else
    echo "❌ Deployment failed. Please check credentials and try again."
    exit 1
fi

# Clean up
rm -f /tmp/sftp_batch.txt

echo "🎉 Deployment complete!"