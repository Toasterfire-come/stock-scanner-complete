#!/bin/bash
# Install systemd services for automated market hours management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Market Hours Manager Services${NC}"
echo "========================================"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run with sudo: sudo $0${NC}"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Workspace directory: $WORKSPACE_DIR${NC}"

# Update service files with correct paths
echo -e "${BLUE}Updating service files with correct paths...${NC}"
sed -i "s|/workspace|$WORKSPACE_DIR|g" *.service
sed -i "s|User=ubuntu|User=$SUDO_USER|g" *.service
sed -i "s|Group=ubuntu|Group=$SUDO_USER|g" *.service

# Copy service files to systemd directory
echo -e "${BLUE}Copying service files...${NC}"
cp -v market-hours-manager.service /etc/systemd/system/
cp -v daily-market-updater.service /etc/systemd/system/
cp -v daily-market-updater.timer /etc/systemd/system/

# Create log directory
echo -e "${BLUE}Creating log directory...${NC}"
mkdir -p /var/log
touch /var/log/market-hours-manager.log
touch /var/log/market-hours-manager.error.log
touch /var/log/daily-market-updater.log
touch /var/log/daily-market-updater.error.log
chown $SUDO_USER:$SUDO_USER /var/log/market-hours-manager*.log
chown $SUDO_USER:$SUDO_USER /var/log/daily-market-updater*.log

# Reload systemd daemon
echo -e "${BLUE}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable services
echo -e "${BLUE}Enabling services...${NC}"
systemctl enable market-hours-manager.service
systemctl enable daily-market-updater.timer

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Available commands:"
echo "  Start market hours manager:  sudo systemctl start market-hours-manager"
echo "  Stop market hours manager:   sudo systemctl stop market-hours-manager"
echo "  Check status:                sudo systemctl status market-hours-manager"
echo "  View logs:                   sudo journalctl -u market-hours-manager -f"
echo ""
echo "  Start daily timer:           sudo systemctl start daily-market-updater.timer"
echo "  Check timer status:          sudo systemctl status daily-market-updater.timer"
echo "  List all timers:             sudo systemctl list-timers"
echo ""
echo "  View market manager logs:    tail -f /var/log/market-hours-manager.log"
echo "  View daily updater logs:     tail -f /var/log/daily-market-updater.log"
echo ""
echo -e "${YELLOW}Note: Services will start automatically on system boot${NC}"

# Ask if user wants to start services now
echo ""
read -p "Do you want to start the services now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting services...${NC}"
    systemctl start market-hours-manager.service
    systemctl start daily-market-updater.timer
    
    sleep 2
    
    echo -e "${GREEN}Services started!${NC}"
    echo ""
    systemctl status market-hours-manager.service --no-pager | head -15
    echo ""
    systemctl status daily-market-updater.timer --no-pager | head -10
fi