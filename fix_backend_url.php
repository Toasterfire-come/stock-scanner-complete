<?php
/**
 * Quick fix script to set the backend URL for Stock Scanner WordPress theme
 * This resolves the "Backend URL not configured" error
 */

// WordPress configuration
require_once('wp-config.php');

// Set the backend URL - CHANGE THIS TO YOUR ACTUAL URL
$backend_url = 'https://api.retailtradescanner.com';  // Your Django server URL

// Alternative URLs for reference:
// $backend_url = 'http://localhost:8000';  // Local development
// $backend_url = 'https://your-tunnel-url.trycloudflare.com';  // Cloudflare tunnel

// Connect to WordPress database
global $wpdb;

// Update the backend URL option
$option_name = 'stock_scanner_backend_url';
$option_value = $backend_url;

// Check if option exists
$existing_value = get_option($option_name);

if ($existing_value === false) {
    // Option doesn't exist, add it
    $result = add_option($option_name, $option_value);
    if ($result) {
        echo "✅ Successfully added backend URL: $option_value\n";
    } else {
        echo "❌ Failed to add backend URL\n";
    }
} else {
    // Option exists, update it
    $result = update_option($option_name, $option_value);
    if ($result || $existing_value === $option_value) {
        echo "✅ Successfully updated backend URL: $option_value\n";
        if ($existing_value === $option_value) {
            echo "   (Value was already correct)\n";
        }
    } else {
        echo "❌ Failed to update backend URL\n";
    }
}

// Verify the setting
$verified_value = get_option($option_name);
echo "\n📋 Current backend URL setting: $verified_value\n";

// Test if the URL is accessible (basic check)
echo "\n🔧 Testing connection to backend...\n";
$test_url = rtrim($backend_url, '/') . '/api/stocks/';
$response = wp_remote_get($test_url, array('timeout' => 10));

if (is_wp_error($response)) {
    echo "❌ Connection test failed: " . $response->get_error_message() . "\n";
    echo "   Make sure your Django server is running and accessible\n";
} else {
    $status_code = wp_remote_retrieve_response_code($response);
    if ($status_code === 200) {
        echo "✅ Connection test successful! Backend is accessible\n";
    } else {
        echo "⚠️  Connection test returned status code: $status_code\n";
        echo "   Check if your Django server is running properly\n";
    }
}

echo "\n🎯 Next steps:\n";
echo "1. Make sure your Django server is running (python manage.py runserver)\n";
echo "2. If using Cloudflare tunnel, make sure it's active\n";
echo "3. Update the \$backend_url variable in this script if needed\n";
echo "4. Test the revenue analytics page in WordPress admin\n";
?>