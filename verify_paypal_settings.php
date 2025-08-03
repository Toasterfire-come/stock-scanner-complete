<?php
/**
 * PayPal Settings Verification Script
 * 
 * This script verifies that PayPal settings are properly configured
 * Run this in your WordPress admin or via command line
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    // If running from command line
    if (php_sapi_name() !== 'cli') {
        exit('Direct access not allowed');
    }
}

/**
 * PayPal Settings Verification Class
 */
class PayPalSettingsVerification {
    
    public function __construct() {
        // Load WordPress if running from CLI
        if (php_sapi_name() === 'cli') {
            $this->load_wordpress();
        }
    }
    
    /**
     * Load WordPress for CLI execution
     */
    private function load_wordpress() {
        // Find WordPress root
        $wp_root = dirname(__FILE__);
        while (!file_exists($wp_root . '/wp-config.php')) {
            $wp_root = dirname($wp_root);
            if ($wp_root === '/') {
                die('WordPress not found');
            }
        }
        
        require_once($wp_root . '/wp-config.php');
        require_once(ABSPATH . 'wp-includes/wp-db.php');
        require_once(ABSPATH . 'wp-includes/option.php');
    }
    
    /**
     * Check all PayPal settings
     */
    public function verify_settings() {
        echo "=== PayPal Settings Verification ===\n\n";
        
        $settings = array(
            'paypal_mode' => get_option('paypal_mode'),
            'paypal_client_id' => get_option('paypal_client_id'),
            'paypal_client_secret' => get_option('paypal_client_secret'),
            'paypal_webhook_url' => get_option('paypal_webhook_url'),
            'paypal_return_url' => get_option('paypal_return_url'),
            'paypal_cancel_url' => get_option('paypal_cancel_url')
        );
        
        $all_good = true;
        
        foreach ($settings as $key => $value) {
            if (empty($value)) {
                echo "❌ {$key}: NOT SET\n";
                $all_good = false;
            } else {
                echo "✅ {$key}: SET\n";
            }
        }
        
        echo "\n";
        
        if ($all_good) {
            echo "🎉 SUCCESS: All PayPal settings are configured!\n";
        } else {
            echo "⚠️  WARNING: Some PayPal settings are missing\n";
            echo "Please configure them in WordPress Admin → Settings → Stock Scanner\n";
        }
        
        return $all_good;
    }
    
    /**
     * Check if plugin settings page shows PayPal fields
     */
    public function check_plugin_settings() {
        echo "\n=== Plugin Settings Page Check ===\n\n";
        
        // Check if the plugin class exists
        if (class_exists('StockScannerPlugin')) {
            echo "✅ StockScannerPlugin class exists\n";
        } else {
            echo "❌ StockScannerPlugin class not found\n";
            return false;
        }
        
        // Check if admin_page method exists
        $plugin = new StockScannerPlugin();
        if (method_exists($plugin, 'admin_page')) {
            echo "✅ admin_page method exists\n";
        } else {
            echo "❌ admin_page method not found\n";
            return false;
        }
        
        // Check if PayPal settings are registered
        $paypal_settings = array(
            'paypal_mode',
            'paypal_client_id', 
            'paypal_client_secret',
            'paypal_webhook_url',
            'paypal_return_url',
            'paypal_cancel_url'
        );
        
        foreach ($paypal_settings as $setting) {
            if (get_option($setting) !== false) {
                echo "✅ {$setting} is registered\n";
            } else {
                echo "❌ {$setting} is not registered\n";
            }
        }
        
        return true;
    }
    
    /**
     * Test webhook URL accessibility
     */
    public function test_webhook_url() {
        echo "\n=== Webhook URL Test ===\n\n";
        
        $webhook_url = home_url('/wp-json/stock-scanner/v1/paypal-webhook');
        echo "Webhook URL: {$webhook_url}\n";
        
        // Test if URL is accessible
        $response = wp_remote_get($webhook_url, array(
            'timeout' => 10,
            'user-agent' => 'PayPal-Webhook-Test'
        ));
        
        if (is_wp_error($response)) {
            echo "❌ ERROR: " . $response->get_error_message() . "\n";
            return false;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        echo "Status Code: {$status_code}\n";
        
        if ($status_code === 200) {
            echo "✅ SUCCESS: Webhook endpoint is accessible\n";
            return true;
        } else {
            echo "❌ ERROR: Webhook endpoint returned status {$status_code}\n";
            return false;
        }
    }
    
    /**
     * Display setup instructions
     */
    public function display_instructions() {
        echo "\n=== Setup Instructions ===\n\n";
        
        echo "1. Go to WordPress Admin → Settings → Stock Scanner\n";
        echo "2. You should see two sections:\n";
        echo "   - API Configuration\n";
        echo "   - PayPal Configuration\n";
        echo "3. Fill in all PayPal fields:\n";
        echo "   - PayPal Mode (Sandbox/Live)\n";
        echo "   - Client ID\n";
        echo "   - Client Secret\n";
        echo "   - Webhook URL\n";
        echo "   - Return URL\n";
        echo "   - Cancel URL\n";
        echo "4. Click 'Save Changes'\n";
        echo "5. Test the webhook connection\n\n";
        
        echo "If PayPal settings are not showing:\n";
        echo "1. Deactivate and reactivate the plugin\n";
        echo "2. Clear WordPress cache\n";
        echo "3. Check for JavaScript errors\n";
        echo "4. Verify plugin files are up to date\n";
    }
}

// Run the verification
if (php_sapi_name() === 'cli') {
    // Command line mode
    $verification = new PayPalSettingsVerification();
    
    echo "PayPal Settings Verification\n";
    echo "===========================\n\n";
    
    $verification->verify_settings();
    $verification->check_plugin_settings();
    $verification->test_webhook_url();
    $verification->display_instructions();
    
} else {
    // WordPress admin mode
    if (current_user_can('manage_options')) {
        $verification = new PayPalSettingsVerification();
        
        echo '<div class="wrap">';
        echo '<h1>PayPal Settings Verification</h1>';
        
        echo '<h2>Settings Check</h2>';
        echo '<pre>';
        $verification->verify_settings();
        echo '</pre>';
        
        echo '<h2>Plugin Check</h2>';
        echo '<pre>';
        $verification->check_plugin_settings();
        echo '</pre>';
        
        echo '<h2>Webhook Test</h2>';
        echo '<pre>';
        $verification->test_webhook_url();
        echo '</pre>';
        
        echo '<h2>Instructions</h2>';
        echo '<pre>';
        $verification->display_instructions();
        echo '</pre>';
        
        echo '</div>';
    } else {
        echo '<p>You do not have permission to access this page.</p>';
    }
}