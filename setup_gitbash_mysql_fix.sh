#!/bin/bash

# =========================================================================
# Quick MySQL PATH Fix for Stock Scanner Setup
# Adds MySQL to PATH and runs the main setup
# =========================================================================

echo " Fixing MySQL PATH for Stock Scanner Setup..."

# Common MySQL installation paths
MYSQL_PATHS=(
"/c/Program Files/MySQL/MySQL Server 8.0/bin"
"/c/Program Files/MySQL/MySQL Server 8.4/bin"
"/c/Program Files/MySQL/MySQL Server 5.7/bin"
"/c/Program Files (x86)/MySQL/MySQL Server 8.0/bin"
"/c/Program Files (x86)/MySQL/MySQL Server 8.4/bin"
"/c/xampp/mysql/bin"
"/c/wamp64/bin/mysql/mysql8.0.31/bin"
)

# Find MySQL installation
MYSQL_FOUND=""
for mysql_path in "${MYSQL_PATHS[@]}"; do
if [[ -f "$mysql_path/mysql.exe" ]]; then
MYSQL_FOUND="$mysql_path"
echo " Found MySQL at: $mysql_path"
break
fi
done

# If not found in common paths, search manually
if [[ -z "$MYSQL_FOUND" ]]; then
echo " Searching for MySQL installation..."

# Search in Program Files
MYSQL_SEARCH=$(find "/c/Program Files" -name "mysql.exe" 2>/dev/null | head -1)
if [[ -n "$MYSQL_SEARCH" ]]; then
MYSQL_FOUND=$(dirname "$MYSQL_SEARCH")
echo " Found MySQL at: $MYSQL_FOUND"
fi

# Search in Program Files (x86)
if [[ -z "$MYSQL_FOUND" ]]; then
MYSQL_SEARCH=$(find "/c/Program Files (x86)" -name "mysql.exe" 2>/dev/null | head -1)
if [[ -n "$MYSQL_SEARCH" ]]; then
MYSQL_FOUND=$(dirname "$MYSQL_SEARCH")
echo " Found MySQL at: $MYSQL_FOUND"
fi
fi
fi

if [[ -n "$MYSQL_FOUND" ]]; then
# Add MySQL to PATH for this session
export PATH="$MYSQL_FOUND:$PATH"
echo " MySQL added to PATH temporarily"

# Test MySQL connection
echo " Testing MySQL connection..."
if mysql --version >/dev/null 2>&1; then
echo " MySQL is now accessible!"

# Test with your root password
echo " Testing your root password..."
if mysql -u root -pstockscanner2010 -e "SELECT 1;" >/dev/null 2>&1; then
echo " Root password verified!"
else
echo " Root password may need adjustment"
fi

echo ""
echo " Starting Stock Scanner setup..."
echo "================================================"

# Run the main setup script
chmod +x setup_gitbash_complete.sh
./setup_gitbash_complete.sh

else
echo " MySQL still not accessible"
echo "Please add MySQL to your Windows PATH manually"
fi
else
echo " MySQL not found in common locations"
echo ""
echo " Please locate your MySQL installation and add it to PATH:"
echo "1. Find mysql.exe location (usually in Program Files/MySQL/MySQL Server X.X/bin/)"
echo "2. Add that path to your Windows PATH environment variable"
echo "3. Restart Git Bash and try again"
echo ""
echo "Or run this to search manually:"
echo 'find "/c/Program Files" -name "mysql.exe" 2>/dev/null'
fi