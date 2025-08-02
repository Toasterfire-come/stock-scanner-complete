<?php
/**
 * PayPal Integration for Stock Scanner
 * 
 * Handles PayPal payment processing, subscriptions, and webhook management
 * 
 * @package StockScannerIntegration
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class StockScannerPayPalIntegration {
    
    /**
     * PayPal API configuration
     */
    private $paypal_mode;
    private $client_id;
    private $client_secret;
    private $api_base_url;
    private $webhook_url;
    private $return_url;
    private $cancel_url;
    
    /**
     * Membership plan prices
     */
    private $plan_prices = [
        'bronze_monthly' => 9.99,
        'bronze_annual' => 95.88,
        'silver_monthly' => 19.99,
        'silver_annual' => 191.88,
        'gold_monthly' => 39.99,
        'gold_annual' => 383.88,
        'platinum_monthly' => 79.99,
        'platinum_annual' => 767.88
    ];
    
    /**
     * Constructor
     */
    public function __construct() {
        $this->init_paypal_config();
        $this->add_hooks();
    }
    
    /**
     * Initialize PayPal configuration
     */
    private function init_paypal_config() {
        $this->paypal_mode = get_option('paypal_mode', 'sandbox');
        $this->client_id = get_option('paypal_client_id', '');
        $this->client_secret = get_option('paypal_client_secret', '');
        $this->webhook_url = get_option('paypal_webhook_url', '');
        $this->return_url = get_option('paypal_return_url', '');
        $this->cancel_url = get_option('paypal_cancel_url', '');
        
        // Set API base URL based on mode
        $this->api_base_url = ($this->paypal_mode === 'live') 
            ? 'https://api-m.paypal.com' 
            : 'https://api-m.sandbox.paypal.com';
    }
    
    /**
     * Add WordPress hooks
     */
    private function add_hooks() {
        add_action('wp_ajax_create_paypal_order', array($this, 'create_paypal_order'));
        add_action('wp_ajax_nopriv_create_paypal_order', array($this, 'create_paypal_order'));
        add_action('wp_ajax_capture_paypal_order', array($this, 'capture_paypal_order'));
        add_action('wp_ajax_nopriv_capture_paypal_order', array($this, 'capture_paypal_order'));
        add_action('wp_ajax_create_paypal_subscription', array($this, 'create_paypal_subscription'));
        add_action('wp_ajax_nopriv_create_paypal_subscription', array($this, 'create_paypal_subscription'));
        
        // Webhook endpoint
        add_action('rest_api_init', array($this, 'register_webhook_endpoint'));
        
        // Admin hooks
        add_action('admin_menu', array($this, 'add_paypal_admin_menu'));
        add_action('admin_init', array($this, 'register_paypal_settings'));
    }
    
    /**
     * Get PayPal access token
     */
    private function get_access_token() {
        $url = $this->api_base_url . '/v1/oauth2/token';
        
        $headers = array(
            'Authorization' => 'Basic ' . base64_encode($this->client_id . ':' . $this->client_secret),
            'Content-Type' => 'application/x-www-form-urlencoded'
        );
        
        $body = array(
            'grant_type' => 'client_credentials'
        );
        
        $response = wp_remote_post($url, array(
            'headers' => $headers,
            'body' => $body,
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            $this->log_error('PayPal token error: ' . $response->get_error_message());
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (isset($data['access_token'])) {
            return $data['access_token'];
        }
        
        $this->log_error('PayPal token response: ' . $body);
        return false;
    }
    
    /**
     * Create PayPal order
     */
    public function create_paypal_order() {
        check_ajax_referer('paypal_nonce', 'nonce');
        
        $plan = sanitize_text_field($_POST['plan']);
        $billing_cycle = sanitize_text_field($_POST['billing_cycle']);
        
        if (!isset($this->plan_prices[$plan . '_' . $billing_cycle])) {
            wp_die('Invalid plan');
        }
        
        $amount = $this->plan_prices[$plan . '_' . $billing_cycle];
        
        $access_token = $this->get_access_token();
        if (!$access_token) {
            wp_die('Failed to get PayPal access token');
        }
        
        $order_data = array(
            'intent' => 'CAPTURE',
            'purchase_units' => array(
                array(
                    'amount' => array(
                        'currency_code' => 'USD',
                        'value' => number_format($amount, 2, '.', '')
                    ),
                    'description' => ucfirst($plan) . ' ' . ucfirst($billing_cycle) . ' Plan - Stock Scanner',
                    'custom_id' => $plan . '_' . $billing_cycle . '_' . get_current_user_id()
                )
            ),
            'application_context' => array(
                'return_url' => $this->return_url,
                'cancel_url' => $this->cancel_url,
                'brand_name' => 'Stock Scanner',
                'user_action' => 'PAY_NOW'
            )
        );
        
        $url = $this->api_base_url . '/v2/checkout/orders';
        
        $response = wp_remote_post($url, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $access_token,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($order_data),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            $this->log_error('PayPal order creation error: ' . $response->get_error_message());
            wp_die('Failed to create PayPal order');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (isset($data['id'])) {
            // Store order details in user meta
            $user_id = get_current_user_id();
            update_user_meta($user_id, 'paypal_order_id', $data['id']);
            update_user_meta($user_id, 'paypal_plan', $plan);
            update_user_meta($user_id, 'paypal_billing_cycle', $billing_cycle);
            
            wp_send_json_success(array(
                'order_id' => $data['id'],
                'approval_url' => $data['links'][1]['href']
            ));
        }
        
        $this->log_error('PayPal order response: ' . $body);
        wp_die('Failed to create PayPal order');
    }
    
    /**
     * Capture PayPal order
     */
    public function capture_paypal_order() {
        check_ajax_referer('paypal_nonce', 'nonce');
        
        $order_id = sanitize_text_field($_POST['order_id']);
        
        $access_token = $this->get_access_token();
        if (!$access_token) {
            wp_die('Failed to get PayPal access token');
        }
        
        $url = $this->api_base_url . '/v2/checkout/orders/' . $order_id . '/capture';
        
        $response = wp_remote_post($url, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $access_token,
                'Content-Type' => 'application/json'
            ),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            $this->log_error('PayPal capture error: ' . $response->get_error_message());
            wp_die('Failed to capture PayPal order');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (isset($data['status']) && $data['status'] === 'COMPLETED') {
            $user_id = get_current_user_id();
            $plan = get_user_meta($user_id, 'paypal_plan', true);
            $billing_cycle = get_user_meta($user_id, 'paypal_billing_cycle', true);
            
            // Update user membership
            $this->update_user_membership($user_id, $plan, $billing_cycle);
            
            // Log successful payment
            $this->log_payment($user_id, $order_id, $data['purchase_units'][0]['amount']['value'], 'completed');
            
            wp_send_json_success(array(
                'status' => 'completed',
                'message' => 'Payment completed successfully'
            ));
        }
        
        $this->log_error('PayPal capture response: ' . $body);
        wp_die('Failed to capture PayPal order');
    }
    
    /**
     * Create PayPal subscription
     */
    public function create_paypal_subscription() {
        check_ajax_referer('paypal_nonce', 'nonce');
        
        $plan = sanitize_text_field($_POST['plan']);
        $billing_cycle = sanitize_text_field($_POST['billing_cycle']);
        
        $access_token = $this->get_access_token();
        if (!$access_token) {
            wp_die('Failed to get PayPal access token');
        }
        
        // Create billing plan
        $plan_id = $this->create_billing_plan($plan, $billing_cycle, $access_token);
        if (!$plan_id) {
            wp_die('Failed to create billing plan');
        }
        
        // Create subscription
        $subscription_data = array(
            'plan_id' => $plan_id,
            'start_time' => date('c'),
            'subscriber' => array(
                'name' => array(
                    'given_name' => get_user_meta(get_current_user_id(), 'first_name', true) ?: 'User',
                    'surname' => get_user_meta(get_current_user_id(), 'last_name', true) ?: 'Account'
                ),
                'email_address' => wp_get_current_user()->user_email
            ),
            'application_context' => array(
                'brand_name' => 'Stock Scanner',
                'return_url' => $this->return_url,
                'cancel_url' => $this->cancel_url
            )
        );
        
        $url = $this->api_base_url . '/v1/billing/subscriptions';
        
        $response = wp_remote_post($url, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $access_token,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($subscription_data),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            $this->log_error('PayPal subscription error: ' . $response->get_error_message());
            wp_die('Failed to create PayPal subscription');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (isset($data['id'])) {
            wp_send_json_success(array(
                'subscription_id' => $data['id'],
                'approval_url' => $data['links'][0]['href']
            ));
        }
        
        $this->log_error('PayPal subscription response: ' . $body);
        wp_die('Failed to create PayPal subscription');
    }
    
    /**
     * Create billing plan
     */
    private function create_billing_plan($plan, $billing_cycle, $access_token) {
        $amount = $this->plan_prices[$plan . '_' . $billing_cycle];
        $frequency = ($billing_cycle === 'annual') ? 'YEAR' : 'MONTH';
        
        $plan_data = array(
            'product_id' => 'PROD-' . strtoupper($plan) . '-' . strtoupper($billing_cycle),
            'name' => ucfirst($plan) . ' ' . ucfirst($billing_cycle) . ' Plan',
            'description' => 'Stock Scanner ' . ucfirst($plan) . ' ' . ucfirst($billing_cycle) . ' Membership',
            'status' => 'ACTIVE',
            'billing_cycles' => array(
                array(
                    'frequency' => array(
                        'interval_unit' => $frequency,
                        'interval_count' => 1
                    ),
                    'tenure_type' => 'REGULAR',
                    'sequence' => 1,
                    'total_cycles' => 0,
                    'pricing_scheme' => array(
                        'fixed_price' => array(
                            'value' => number_format($amount, 2, '.', ''),
                            'currency_code' => 'USD'
                        )
                    )
                )
            ),
            'payment_preferences' => array(
                'auto_bill_outstanding' => true,
                'setup_fee' => array(
                    'value' => '0',
                    'currency_code' => 'USD'
                ),
                'setup_fee_failure_action' => 'CONTINUE',
                'payment_failure_threshold' => 3
            )
        );
        
        $url = $this->api_base_url . '/v1/billing/plans';
        
        $response = wp_remote_post($url, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $access_token,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($plan_data),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        return isset($data['id']) ? $data['id'] : false;
    }
    
    /**
     * Update user membership
     */
    private function update_user_membership($user_id, $plan, $billing_cycle) {
        $membership_levels = array(
            'bronze' => 1,
            'silver' => 2,
            'gold' => 3,
            'platinum' => 4
        );
        
        $level_id = $membership_levels[$plan] ?? 1;
        
        // Update user meta
        update_user_meta($user_id, 'membership_level', $level_id);
        update_user_meta($user_id, 'membership_plan', $plan);
        update_user_meta($user_id, 'billing_cycle', $billing_cycle);
        update_user_meta($user_id, 'membership_start_date', current_time('mysql'));
        update_user_meta($user_id, 'membership_status', 'active');
        
        // Calculate expiration date
        $expiration_date = ($billing_cycle === 'annual') 
            ? date('Y-m-d H:i:s', strtotime('+1 year'))
            : date('Y-m-d H:i:s', strtotime('+1 month'));
        
        update_user_meta($user_id, 'membership_expiration_date', $expiration_date);
    }
    
    /**
     * Register webhook endpoint
     */
    public function register_webhook_endpoint() {
        register_rest_route('stock-scanner/v1', '/paypal-webhook', array(
            'methods' => 'POST',
            'callback' => array($this, 'handle_webhook'),
            'permission_callback' => '__return_true'
        ));
    }
    
    /**
     * Handle PayPal webhook
     */
    public function handle_webhook($request) {
        $body = $request->get_body();
        $data = json_decode($body, true);
        
        $this->log_payment('webhook', 'webhook', json_encode($data), 'webhook_received');
        
        if (isset($data['event_type'])) {
            switch ($data['event_type']) {
                case 'PAYMENT.CAPTURE.COMPLETED':
                    $this->handle_payment_completed($data);
                    break;
                case 'BILLING.SUBSCRIPTION.ACTIVATED':
                    $this->handle_subscription_activated($data);
                    break;
                case 'BILLING.SUBSCRIPTION.CANCELLED':
                    $this->handle_subscription_cancelled($data);
                    break;
                case 'BILLING.SUBSCRIPTION.EXPIRED':
                    $this->handle_subscription_expired($data);
                    break;
            }
        }
        
        return new WP_REST_Response(array('status' => 'success'), 200);
    }
    
    /**
     * Handle payment completed webhook
     */
    private function handle_payment_completed($data) {
        $custom_id = $data['resource']['custom_id'] ?? '';
        $parts = explode('_', $custom_id);
        
        if (count($parts) >= 3) {
            $plan = $parts[0];
            $billing_cycle = $parts[1];
            $user_id = $parts[2];
            
            $this->update_user_membership($user_id, $plan, $billing_cycle);
        }
    }
    
    /**
     * Handle subscription activated webhook
     */
    private function handle_subscription_activated($data) {
        $subscriber_email = $data['resource']['subscriber']['email_address'] ?? '';
        $user = get_user_by('email', $subscriber_email);
        
        if ($user) {
            update_user_meta($user->ID, 'membership_status', 'active');
            update_user_meta($user->ID, 'paypal_subscription_id', $data['resource']['id']);
        }
    }
    
    /**
     * Handle subscription cancelled webhook
     */
    private function handle_subscription_cancelled($data) {
        $subscription_id = $data['resource']['id'] ?? '';
        
        $users = get_users(array(
            'meta_key' => 'paypal_subscription_id',
            'meta_value' => $subscription_id
        ));
        
        foreach ($users as $user) {
            update_user_meta($user->ID, 'membership_status', 'cancelled');
        }
    }
    
    /**
     * Handle subscription expired webhook
     */
    private function handle_subscription_expired($data) {
        $subscription_id = $data['resource']['id'] ?? '';
        
        $users = get_users(array(
            'meta_key' => 'paypal_subscription_id',
            'meta_value' => $subscription_id
        ));
        
        foreach ($users as $user) {
            update_user_meta($user->ID, 'membership_status', 'expired');
        }
    }
    
    /**
     * Add PayPal admin menu
     */
    public function add_paypal_admin_menu() {
        add_submenu_page(
            'stock-scanner-settings',
            'PayPal Settings',
            'PayPal Settings',
            'manage_options',
            'paypal-settings',
            array($this, 'paypal_settings_page')
        );
    }
    
    /**
     * Register PayPal settings
     */
    public function register_paypal_settings() {
        register_setting('paypal_settings', 'paypal_mode');
        register_setting('paypal_settings', 'paypal_client_id');
        register_setting('paypal_settings', 'paypal_client_secret');
        register_setting('paypal_settings', 'paypal_webhook_url');
        register_setting('paypal_settings', 'paypal_return_url');
        register_setting('paypal_settings', 'paypal_cancel_url');
    }
    
    /**
     * PayPal settings page
     */
    public function paypal_settings_page() {
        ?>
        <div class="wrap">
            <h1>PayPal Settings</h1>
            <form method="post" action="options.php">
                <?php settings_fields('paypal_settings'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">PayPal Mode</th>
                        <td>
                            <select name="paypal_mode">
                                <option value="sandbox" <?php selected(get_option('paypal_mode'), 'sandbox'); ?>>Sandbox</option>
                                <option value="live" <?php selected(get_option('paypal_mode'), 'live'); ?>>Live</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Client ID</th>
                        <td>
                            <input type="text" name="paypal_client_id" value="<?php echo esc_attr(get_option('paypal_client_id')); ?>" class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Client Secret</th>
                        <td>
                            <input type="password" name="paypal_client_secret" value="<?php echo esc_attr(get_option('paypal_client_secret')); ?>" class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Webhook URL</th>
                        <td>
                            <input type="url" name="paypal_webhook_url" value="<?php echo esc_attr(get_option('paypal_webhook_url')); ?>" class="regular-text" />
                            <p class="description">Set this URL in your PayPal Developer Dashboard</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Return URL</th>
                        <td>
                            <input type="url" name="paypal_return_url" value="<?php echo esc_attr(get_option('paypal_return_url')); ?>" class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Cancel URL</th>
                        <td>
                            <input type="url" name="paypal_cancel_url" value="<?php echo esc_attr(get_option('paypal_cancel_url')); ?>" class="regular-text" />
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Log payment
     */
    private function log_payment($user_id, $order_id, $amount, $status) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'user_id' => $user_id,
            'order_id' => $order_id,
            'amount' => $amount,
            'status' => $status
        );
        
        $log_file = WP_CONTENT_DIR . '/paypal_payments.log';
        file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
    }
    
    /**
     * Log error
     */
    private function log_error($message) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'error' => $message
        );
        
        $log_file = WP_CONTENT_DIR . '/paypal_errors.log';
        file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
    }
}

// Initialize PayPal integration
new StockScannerPayPalIntegration();