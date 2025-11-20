#!/bin/bash
# Simple deployment wrapper script
# Uses the Python SFTP deployment script with pre-configured credentials

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy_sftp_complete.py"

# SFTP Configuration (can be overridden by environment variables)
export SFTP_HOST="${SFTP_HOST:-access-5018544625.webspace-host.com}"
export SFTP_PORT="${SFTP_PORT:-22}"
export SFTP_USER="${SFTP_USER:-a1531117}"
export SFTP_PASSWORD="${SFTP_PASSWORD:-C2rt3rK#2010}"
export REMOTE_ROOT="${REMOTE_ROOT:-/}"
export BUILD_DIR="${BUILD_DIR:-frontend/build}"
export KEEP_REMOTE_ITEMS="${KEEP_REMOTE_ITEMS:-.ssh,.htaccess}"

# Check if Python script exists
if [ ! -f "$DEPLOY_SCRIPT" ]; then
    echo "Error: Deployment script not found: $DEPLOY_SCRIPT"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Check if paramiko is installed
if ! python3 -c "import paramiko" 2>/dev/null; then
    echo "Installing required Python packages..."
    pip3 install paramiko
fi

# Run the deployment script
echo "Starting deployment..."
python3 "$DEPLOY_SCRIPT" "$@"
