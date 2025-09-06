#!/bin/bash

# Deployment script for Stock Scanner App
# Host: access-5018544625.webspace-host.com
# Protocol: SFTP
# Port: 22

HOST="access-5018544625.webspace-host.com"
PORT="22"
USER="a2565254"
REMOTE_PATH="/public_html"

echo "Preparing deployment..."

# Create deployment package
cd /app/frontend/build
tar -czf /app/stock-scanner-build.tar.gz *

echo "Build package created: stock-scanner-build.tar.gz"

# SFTP deployment using expect (interactive)
echo "Ready to deploy to: $USER@$HOST:$PORT"
echo "Files will be uploaded to: $REMOTE_PATH"
echo "Build package location: /app/stock-scanner-build.tar.gz"

echo "You can now upload the files using SFTP client or the following command:"
echo "sftp -P $PORT $USER@$HOST"
echo "Then use: put /app/stock-scanner-build.tar.gz"