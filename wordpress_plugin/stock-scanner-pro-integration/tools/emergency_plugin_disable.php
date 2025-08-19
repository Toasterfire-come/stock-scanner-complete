<?php
/**
 * Emergency Plugin Disable Script
 * Use this if Stock Scanner plugin is causing WordPress to crash
 * Place in WordPress root and access via browser
 */

// Include WordPress
require_once('wp-config.php');

echo "<h1>Emergency Plugin Manager</h1>";

// Check current active plugins
$active_plugins = get_option('active_plugins', array());
$stock_scanner_plugin = 'stock-scanner-integration/stock-scanner-integration.php';

echo "<h2>Current Status</h2>";

if (in_array($stock_scanner_plugin, $active_plugins)) {
    echo "❌ Stock Scanner plugin is ACTIVE<br>";
    
    if (isset($_GET['disable']) && $_GET['disable'] === 'confirm') {
        // Remove plugin from active list
        $key = array_search($stock_scanner_plugin, $active_plugins);
        if ($key !== false) {
            unset($active_plugins[$key]);
            update_option('active_plugins', $active_plugins);
            echo "✅ Stock Scanner plugin has been DISABLED<br>";
            echo "<p><strong>The plugin is now deactivated. You can now access WordPress admin safely.</strong></p>";
        }
    } else {
        echo "<p><strong>To disable the Stock Scanner plugin, click the button below:</strong></p>";
        echo "<a href='?disable=confirm' style='background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>DISABLE PLUGIN</a>";
    }
} else {
    echo "✅ Stock Scanner plugin is INACTIVE<br>";
    echo "<p>The plugin is already disabled.</p>";
    
    if (isset($_GET['enable']) && $_GET['enable'] === 'confirm') {
        // Add plugin back to active list
        $active_plugins[] = $stock_scanner_plugin;
        update_option('active_plugins', $active_plugins);
        echo "✅ Stock Scanner plugin has been ENABLED<br>";
        echo "<p><strong>The plugin is now reactivated.</strong></p>";
    } else {
        echo "<p>To re-enable the plugin (only if you've fixed the issues), click below:</p>";
        echo "<a href='?enable=confirm' style='background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>ENABLE PLUGIN</a>";
    }
}

echo "<h2>All Active Plugins</h2>";
echo "<ul>";
foreach ($active_plugins as $plugin) {
    echo "<li>$plugin</li>";
}
echo "</ul>";

echo "<h2>Instructions</h2>";
echo "<ol>";
echo "<li>If WordPress is showing critical errors, disable the Stock Scanner plugin</li>";
echo "<li>Once disabled, you can access WordPress admin normally</li>";
echo "<li>Fix any remaining theme issues</li>";
echo "<li>Re-enable the plugin when ready</li>";
echo "</ol>";
?>