<?php
/**
 * PayPal Webhook Setup Helper
 * 
 * This script helps you set up PayPal webhooks for the Stock Scanner plugin
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
 * PayPal Webhook Setup Helper Class
 */
class PayPalWebhookSetup {
    
    private $webhook_url;
    private $paypal_mode;
    
    public function __construct() {
        $this->webhook_url = home_url('/wp-json/stock-scanner/v1/paypal-webhook');
        $this->paypal_mode = get_option('paypal_mode', 'sandbox');
    }
    
    /**
     * Display webhook setup information
     */
    public function display_setup_info() {
        echo "=== PayPal Webhook Setup Information ===\n\n";
        
        echo "1. WEBHOOK URL:\n";
        echo "   " . $this->webhook_url . "\n\n";
        
        echo "2. PAYPAL MODE:\n";
        echo "   " . ucfirst($this->paypal_mode) . "\n\n";
        
        echo "3. REQUIRED EVENTS:\n";
        echo "   - PAYMENT.CAPTURE.COMPLETED\n";
        echo "   - BILLING.SUBSCRIPTION.ACTIVATED\n";
        echo "   - BILLING.SUBSCRIPTION.CANCELLED\n";
        echo "   - BILLING.SUBSCRIPTION.EXPIRED\n";
        echo "   - BILLING.SUBSCRIPTION.SUSPENDED\n\n";
        
        echo "4. PAYPAL DASHBOARD URL:\n";
        if ($this->paypal_mode === 'sandbox') {
            echo "   https://developer.paypal.com/apps/ (Sandbox tab)\n";
        } else {
            echo "   https://developer.paypal.com/apps/ (Live tab)\n";
        }
        echo "\n";
        
        echo "5. SETUP STEPS:\n";
        echo "   1. Go to PayPal Developer Dashboard\n";
        echo "   2. Click '" . ucfirst($this->paypal_mode) . "' tab\n";
        echo "   3. Go to 'Webhooks' in left menu\n";
        echo "   4. Click 'Add Webhook'\n";
        echo "   5. Enter webhook URL: " . $this->webhook_url . "\n";
        echo "   6. Select all required events\n";
        echo "   7. Save webhook\n";
        echo "   8. Test webhook delivery\n\n";
        
        echo "6. TESTING:\n";
        echo "   - Use PayPal sandbox accounts for testing\n";
        echo "   - Make test payments\n";
        echo "   - Check logs: wp-content/paypal_payments.log\n";
        echo "   - Monitor: wp-content/paypal_errors.log\n\n";
        
        echo "7. TROUBLESHOOTING:\n";
        echo "   - Verify webhook URL is accessible\n";
        echo "   - Check HTTPS is enabled\n";
        echo "   - Ensure all events are selected\n";
        echo "   - Test webhook delivery in PayPal Dashboard\n\n";
    }
    
    /**
     * Test webhook endpoint
     */
    public function test_webhook_endpoint() {
        echo "Testing webhook endpoint...\n";
        
        $response = wp_remote_post($this->webhook_url, array(
            'headers' => array(
                'Content-Type' => 'application/json',
                'User-Agent' => 'PayPal-Webhook-Test'
            ),
            'body' => json_encode(array(
                'event_type' => 'TEST.WEBHOOK',
                'test' => true
            )),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            echo "ERROR: " . $response->get_error_message() . "\n";
            return false;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        echo "Status Code: " . $status_code . "\n";
        
        if ($status_code === 200) {
            echo "SUCCESS: Webhook endpoint is accessible\n";
            return true;
        } else {
            echo "ERROR: Webhook endpoint returned status " . $status_code . "\n";
            return false;
        }
    }
    
    /**
     * Check PayPal settings
     */
    public function check_paypal_settings() {
        echo "Checking PayPal settings...\n\n";
        
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
                echo "WARNING: {$key} is not set\n";
                $all_good = false;
            } else {
                echo "OK: {$key} is configured\n";
            }
        }
        
        if ($all_good) {
            echo "\nSUCCESS: All PayPal settings are configured\n";
        } else {
            echo "\nWARNING: Some PayPal settings are missing\n";
            echo "Please configure them in WordPress Admin → Settings → Stock Scanner\n";
        }
        
        return $all_good;
    }
    
    /**
     * Generate webhook test data
     */
    public function generate_test_data() {
        echo "Generating webhook test data...\n\n";
        
        $test_data = array(
            'PAYMENT.CAPTURE.COMPLETED' => array(
                'id' => 'TEST_PAYMENT_' . time(),
                'status' => 'COMPLETED',
                'amount' => array(
                    'currency_code' => 'USD',
                    'value' => '14.99'
                ),
                'custom_id' => 'test_user_123'
            ),
            'BILLING.SUBSCRIPTION.ACTIVATED' => array(
                'id' => 'TEST_SUBSCRIPTION_' . time(),
                'status' => 'ACTIVE',
                'plan_id' => 'bronze_monthly',
                'subscriber' => array(
                    'email_address' => 'test@example.com'
                )
            )
        );
        
        echo "Test data for webhook testing:\n\n";
        
        foreach ($test_data as $event_type => $data) {
            echo "Event: {$event_type}\n";
            echo "Data: " . json_encode($data, JSON_PRETTY_PRINT) . "\n\n";
        }
        
        return $test_data;
    }
}

// Run the setup helper
if (php_sapi_name() === 'cli') {
    // Command line mode
    $setup = new PayPalWebhookSetup();
    
    echo "PayPal Webhook Setup Helper\n";
    echo "===========================\n\n";
    
    $setup->display_setup_info();
    
    echo "Checking settings...\n";
    $setup->check_paypal_settings();
    
    echo "\nTesting webhook endpoint...\n";
    $setup->test_webhook_endpoint();
    
    echo "\nGenerating test data...\n";
    $setup->generate_test_data();
    
} else {
    // WordPress admin mode
    if (current_user_can('manage_options')) {
        $setup = new PayPalWebhookSetup();
        
        echo '<div class="wrap">';
        echo '<h1>PayPal Webhook Setup Helper</h1>';
        
        echo '<h2>Setup Information</h2>';
        echo '<pre>';
        $setup->display_setup_info();
        echo '</pre>';
        
        echo '<h2>Settings Check</h2>';
        echo '<pre>';
        $setup->check_paypal_settings();
        echo '</pre>';
        
        echo '<h2>Webhook Test</h2>';
        echo '<pre>';
        $setup->test_webhook_endpoint();
        echo '</pre>';
        
        echo '</div>';
    } else {
        echo '<p>You do not have permission to access this page.</p>';
    }
}