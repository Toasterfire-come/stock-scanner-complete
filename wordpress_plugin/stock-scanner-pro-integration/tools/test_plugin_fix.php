<?php
/**
 * Test script to verify Stock Scanner plugin fixes
 * Place this in your WordPress root and access via browser
 */

// Include WordPress
require_once('wp-config.php');
require_once('wp-admin/includes/admin.php');

echo "<h1>Stock Scanner Plugin Test</h1>";

// Test 1: Check if both theme and plugin are loaded
echo "<h2>Test 1: Components Check</h2>";

// Check if theme class exists
$theme_class = 'Stock_Scanner_Admin_Settings';
if (class_exists($theme_class)) {
    echo "✅ Theme admin class loaded<br>";
} else {
    echo "❌ Theme admin class NOT loaded<br>";
}

// Check if plugin class exists
$plugin_class = 'Stock_Scanner_Integration';
if (class_exists($plugin_class)) {
    echo "✅ Plugin class loaded<br>";
} else {
    echo "❌ Plugin class NOT loaded<br>";
}

// Test 2: Check menu hooks
echo "<h2>Test 2: Menu Hooks Check</h2>";
global $admin_page_hooks;

if (isset($admin_page_hooks['stock-scanner-settings'])) {
    echo "✅ Theme menu registered<br>";
} else {
    echo "❌ Theme menu NOT registered<br>";
}

// Test 3: Check for conflicts
echo "<h2>Test 3: Conflict Detection</h2>";
$stock_scanner_menus = 0;
foreach ($admin_page_hooks as $hook => $title) {
    if (strpos($hook, 'stock-scanner') !== false || strpos($title, 'Stock Scanner') !== false) {
        $stock_scanner_menus++;
        echo "Found menu: $hook -> $title<br>";
    }
}

if ($stock_scanner_menus > 1) {
    echo "⚠️ Multiple Stock Scanner menus detected ($stock_scanner_menus)<br>";
} else {
    echo "✅ Single Stock Scanner menu detected<br>";
}

// Test 4: Database tables
echo "<h2>Test 4: Database Tables</h2>";
global $wpdb;

$tables_to_check = [
    $wpdb->prefix . 'stock_scanner_usage',
    $wpdb->prefix . 'stock_scanner_memberships',
    $wpdb->prefix . 'stock_scanner_bot_patterns'
];

foreach ($tables_to_check as $table) {
    $exists = $wpdb->get_var("SHOW TABLES LIKE '$table'") == $table;
    if ($exists) {
        echo "✅ Table $table exists<br>";
    } else {
        echo "❌ Table $table missing<br>";
    }
}

echo "<h2>Test Results</h2>";
echo "<p>If you see mostly green checkmarks (✅), the plugin is working correctly.</p>";
echo "<p>If you see red X marks (❌) or warnings (⚠️), there may still be issues.</p>";
?>