# Stock Scanner Theme - File Organization

## Recent File Organization (Updated: 2025)

This document tracks the recent reorganization of files that were moved from the root directory into the appropriate plugin and theme folders.

## Files Moved to Theme Directory

### JavaScript Files - Enhanced UI Components
- **Location**: `/assets/js/enhanced/`
- **Files Moved**:
  - `enhanced-ui.js` → `/assets/js/enhanced/enhanced-ui.js`
    - Advanced UI components for loading states, animations, charts
    - Skeleton loaders, micro-interactions, dark mode support

### JavaScript Files - Shared Functions  
- **Location**: `/assets/js/shared/`
- **Files Moved**:
  - `shared-functions.js` → `/assets/js/shared/shared-functions.js`
    - Portfolio, watchlist, and news management functions
    - API helpers and utility functions

### JavaScript Files - Core Integration
- **Location**: `/assets/js/`
- **Files Moved**:
  - `plugin-integration.js` → `/assets/js/plugin-integration.js`
    - Main plugin integration and frontend interactions
    - Stock quote lookups, membership management

### Progressive Web App Files
- **Location**: Theme root
- **Files Moved**:
  - `service-worker.js` → `/service-worker.js`
    - PWA functionality and caching

### Templates and Assets
- **Location**: `/templates/`
- **Files Moved**:
  - `stock-news.html` → `/templates/stock-news.html` (removed due to corruption)
  - `stock-news.headers` → `/templates/stock-news.headers`

## Files Moved to Plugin Directory

### Plugin Tools and Utilities
- **Location**: `/wordpress_plugin/stock-scanner-pro-integration/tools/`
- **Files Moved**:
  - `emergency_plugin_disable.php` → Emergency plugin disable script
  - `fix_backend_url.php` → Backend URL configuration utility
  - `test_plugin_fix.php` → Plugin testing script

### Plugin Core Features
- **Location**: `/wordpress_plugin/stock-scanner-pro-integration/includes/`
- **Files Moved**:
  - `setup_paypal_webhooks.php` → PayPal integration setup
  - `verify_paypal_settings.php` → PayPal configuration verification

## Updated File References

The following files have been updated to reflect the new file paths:

1. **Theme Functions** (`/functions.php`):
   - Updated JavaScript enqueue paths for enhanced-ui.js and shared-functions.js
   - Maintained existing plugin-integration.js path (already correct)

2. **Footer Template** (`/footer.php`):
   - Service worker registration path updated

## Benefits of This Organization

1. **Better Structure**: Files are now logically organized by function and type
2. **Easier Maintenance**: Related files are grouped together
3. **Clear Separation**: Plugin vs theme functionality is clearly separated
4. **Scalability**: New files can be easily categorized and placed

## Next Steps

- Test all functionality to ensure paths are working correctly
- Update any hardcoded references in other files
- Consider adding automated tests for file organization