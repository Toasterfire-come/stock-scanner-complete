#!/bin/bash

# Stock Scanner Theme Deployment Script
# This script properly deploys the theme to WordPress

echo "🚀 Deploying Stock Scanner Complete Theme..."

# Create WordPress directory structure if it doesn't exist
mkdir -p wp-content/themes/stock-scanner-complete
mkdir -p wp-content/uploads
mkdir -p wp-content/plugins

# Set proper permissions
echo "📁 Setting proper file permissions..."
find wp-content/themes/stock-scanner-complete -type f -exec chmod 644 {} \;
find wp-content/themes/stock-scanner-complete -type d -exec chmod 755 {} \;

# Verify all required theme files exist
echo "✅ Verifying theme files..."
THEME_DIR="wp-content/themes/stock-scanner-complete"

required_files=(
    "style.css"
    "index.php"
    "functions.php"
    "header.php"
    "footer.php"
    "screenshot.png"
)

for file in "${required_files[@]}"; do
    if [[ -f "$THEME_DIR/$file" ]]; then
        echo "✓ $file - Found"
    else
        echo "✗ $file - Missing (Required)"
    fi
done

# Check asset directories
asset_dirs=(
    "assets/css"
    "assets/js"
    "assets/images"
    "js"
)

for dir in "${asset_dirs[@]}"; do
    if [[ -d "$THEME_DIR/$dir" ]]; then
        echo "✓ $dir/ - Found"
    else
        echo "✗ $dir/ - Missing"
    fi
done

# Verify critical assets
critical_assets=(
    "assets/css/enhanced-styles.css"
    "assets/images/logo.png"
    "js/theme-enhanced.js"
)

for asset in "${critical_assets[@]}"; do
    if [[ -f "$THEME_DIR/$asset" ]]; then
        echo "✓ $asset - Found"
    else
        echo "✗ $asset - Missing (Critical)"
    fi
done

echo ""
echo "📋 Deployment Summary:"
echo "Theme Directory: $THEME_DIR"
echo "Files copied: $(find $THEME_DIR -type f | wc -l)"
echo "Directories: $(find $THEME_DIR -type d | wc -l)"

echo ""
echo "🎯 Next Steps:"
echo "1. Upload this entire directory to your WordPress server"
echo "2. Activate the 'Stock Scanner Complete' theme in WordPress Admin"
echo "3. Configure theme settings in Appearance > Customize"

echo ""
echo "✅ Theme deployment structure ready!"