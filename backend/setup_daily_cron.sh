#!/bin/bash
"""
Setup script for daily data updates via cron.

This script sets up a cron job to run daily fundamental updates
at 5:00 PM ET (after market close).
"""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

echo "Setting up daily data update cron job..."

# Create the cron command
CRON_CMD="0 17 * * * cd $SCRIPT_DIR && $PYTHON_PATH manage.py update_daily_data >> $SCRIPT_DIR/logs/daily_update_cron.log 2>&1"

# Add to crontab (avoid duplicates)
if ! crontab -l 2>/dev/null | grep -q "update_daily_data"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✓ Cron job added successfully"
    echo "  Schedule: Daily at 5:00 PM ET"
    echo "  Command: python manage.py update_daily_data"
    echo "  Log: $SCRIPT_DIR/logs/daily_update_cron.log"
else
    echo "✓ Cron job already exists"
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron job: crontab -e (then delete the line)"
echo "To run manually: python manage.py update_daily_data"
echo ""
echo "Setup complete!"
