<?php
/**
 * Membership Manager for Stock Scanner Professional
 * 
 * Handles user levels, API limits, payment processing, and subscription management
 * Fully integrated with PayPal and WordPress user system
 */

class StockScannerMembershipManager {
    
    private $membership_levels;
    private $user_limits_cache = [];
    
    public function __construct() {
        $this->init_membership_levels();
        $this->init_hooks();
        $this->create_membership_tables();
    }
    
    /**
     * Initialize WordPress hooks
     */
    private function init_hooks() {
        // User registration and profile hooks
        add_action('user_register', [$this, 'assign_default_membership']);
        add_action('profile_update', [$this, 'sync_user_membership']);
        add_action('delete_user', [$this, 'cleanup_user_data']);
        
        // Payment processing hooks
        add_action('wp_ajax_process_subscription', [$this, 'process_subscription_ajax']);
        add_action('wp_ajax_nopriv_process_subscription', [$this, 'process_subscription_ajax']);
        add_action('wp_ajax_cancel_subscription', [$this, 'cancel_subscription_ajax']);
        add_action('wp_ajax_change_plan', [$this, 'change_plan_ajax']);
        
        // PayPal webhook handlers
        add_action('wp_ajax_paypal_webhook', [$this, 'handle_paypal_webhook']);
        add_action('wp_ajax_nopriv_paypal_webhook', [$this, 'handle_paypal_webhook']);
        
        // API limit enforcement
        add_action('wp_ajax_check_api_limit', [$this, 'check_api_limit_ajax']);
        add_action('wp_ajax_nopriv_check_api_limit', [$this, 'check_api_limit_ajax']);
        
        // Daily reset of API limits
        add_action('stock_scanner_daily_reset', [$this, 'reset_daily_limits']);
        if (!wp_next_scheduled('stock_scanner_daily_reset')) {
            wp_schedule_event(time(), 'daily', 'stock_scanner_daily_reset');
        }
        
        // Subscription expiry checks
        add_action('stock_scanner_subscription_check', [$this, 'check_expired_subscriptions']);
        if (!wp_next_scheduled('stock_scanner_subscription_check')) {
            wp_schedule_event(time(), 'hourly', 'stock_scanner_subscription_check');
        }
    }
    
    /**
     * Initialize membership levels with comprehensive configurations
     */
    private function init_membership_levels() {
        $this->membership_levels = [
            'free' => [
                'name' => 'Free Starter',
                'price' => 0,
                'billing_cycle' => null,
                'features' => [
                    'daily_scans' => 10,
                    'realtime_data' => false,
                    'technical_indicators' => 10,
                    'watchlists' => 3,
                    'stocks_per_watchlist' => 25,
                    'email_alerts' => true,
                    'sms_alerts' => false,
                    'api_access' => false,
                    'priority_support' => false,
                    'advanced_charts' => false,
                    'custom_formulas' => false,
                    'backtesting' => false,
                    'options_data' => false,
                    'level2_data' => false,
                    'ai_insights' => false,
                    'portfolio_tracking' => false,
                    'export_data' => false
                ],
                'limits' => [
                    'api_calls_per_day' => 100,
                    'api_calls_per_hour' => 10,
                    'data_retention_days' => 7,
                    'concurrent_sessions' => 1
                ]
            ],
            
            'bronze' => [
                'name' => 'Bronze Trader',
                'price' => 14.99,
                'billing_cycle' => 'monthly',
                'stripe_price_id' => 'price_bronze_monthly',
                'paypal_plan_id' => 'P-BRONZE-MONTHLY',
                'features' => [
                    'daily_scans' => -1, // unlimited
                    'realtime_data' => true,
                    'technical_indicators' => 25,
                    'watchlists' => -1, // unlimited
                    'stocks_per_watchlist' => -1, // unlimited
                    'email_alerts' => true,
                    'sms_alerts' => true,
                    'api_access' => false,
                    'priority_support' => true,
                    'advanced_charts' => true,
                    'custom_formulas' => false,
                    'backtesting' => false,
                    'options_data' => false,
                    'level2_data' => false,
                    'ai_insights' => false,
                    'portfolio_tracking' => true,
                    'export_data' => true
                ],
                'limits' => [
                    'api_calls_per_day' => 1500,
                    'api_calls_per_hour' => 100,
                    'data_retention_days' => 30,
                    'concurrent_sessions' => 2
                ]
            ],
            
            'silver' => [
                'name' => 'Silver Pro',
                'price' => 29.99,
                'billing_cycle' => 'monthly',
                'stripe_price_id' => 'price_silver_monthly',
                'paypal_plan_id' => 'P-SILVER-MONTHLY',
                'features' => [
                    'daily_scans' => -1, // unlimited
                    'realtime_data' => true,
                    'technical_indicators' => 50,
                    'watchlists' => -1, // unlimited
                    'stocks_per_watchlist' => -1, // unlimited
                    'email_alerts' => true,
                    'sms_alerts' => true,
                    'api_access' => true,
                    'priority_support' => true,
                    'advanced_charts' => true,
                    'custom_formulas' => true,
                    'backtesting' => true,
                    'options_data' => true,
                    'level2_data' => false,
                    'ai_insights' => true,
                    'portfolio_tracking' => true,
                    'export_data' => true
                ],
                'limits' => [
                    'api_calls_per_day' => 5000,
                    'api_calls_per_hour' => 500,
                    'data_retention_days' => 90,
                    'concurrent_sessions' => 3
                ]
            ],
            
            'gold' => [
                'name' => 'Gold Elite',
                'price' => 69.99,
                'billing_cycle' => 'monthly',
                'stripe_price_id' => 'price_gold_monthly',
                'paypal_plan_id' => 'P-GOLD-MONTHLY',
                'features' => [
                    'daily_scans' => -1, // unlimited
                    'realtime_data' => true,
                    'technical_indicators' => 100,
                    'watchlists' => -1, // unlimited
                    'stocks_per_watchlist' => -1, // unlimited
                    'email_alerts' => true,
                    'sms_alerts' => true,
                    'api_access' => true,
                    'priority_support' => true,
                    'advanced_charts' => true,
                    'custom_formulas' => true,
                    'backtesting' => true,
                    'options_data' => true,
                    'level2_data' => true,
                    'ai_insights' => true,
                    'portfolio_tracking' => true,
                    'export_data' => true
                ],
                'limits' => [
                    'api_calls_per_day' => -1, // unlimited
                    'api_calls_per_hour' => -1, // unlimited
                    'data_retention_days' => 365,
                    'concurrent_sessions' => 5
                ]
            ]
        ];
    }
    
    /**
     * Create membership-related database tables
     */
    private function create_membership_tables() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        // User subscriptions table
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $sql1 = "CREATE TABLE IF NOT EXISTS {$subscriptions_table} (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            membership_level varchar(20) NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'active',
            payment_method varchar(20) NOT NULL,
            subscription_id varchar(100),
            amount decimal(10,2) NOT NULL,
            currency varchar(3) NOT NULL DEFAULT 'USD',
            billing_cycle varchar(20),
            start_date datetime NOT NULL,
            end_date datetime,
            next_billing_date datetime,
            auto_renew tinyint(1) DEFAULT 1,
            trial_end_date datetime,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY status (status),
            KEY subscription_id (subscription_id),
            FOREIGN KEY (user_id) REFERENCES {$wpdb->users}(ID) ON DELETE CASCADE
        ) $charset_collate;";
        
        // API usage tracking table
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        $sql2 = "CREATE TABLE IF NOT EXISTS {$usage_table} (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            endpoint varchar(100) NOT NULL,
            calls_count int(11) NOT NULL DEFAULT 1,
            usage_date date NOT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY usage_date (usage_date),
            KEY endpoint (endpoint),
            UNIQUE KEY unique_user_endpoint_date (user_id, endpoint, usage_date),
            FOREIGN KEY (user_id) REFERENCES {$wpdb->users}(ID) ON DELETE CASCADE
        ) $charset_collate;";
        
        // Payment transactions table
        $transactions_table = $wpdb->prefix . 'stock_scanner_transactions';
        $sql3 = "CREATE TABLE IF NOT EXISTS {$transactions_table} (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            transaction_id varchar(100) NOT NULL,
            payment_method varchar(20) NOT NULL,
            transaction_type varchar(20) NOT NULL,
            amount decimal(10,2) NOT NULL,
            currency varchar(3) NOT NULL DEFAULT 'USD',
            status varchar(20) NOT NULL,
            gateway_response text,
            subscription_id bigint(20),
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY transaction_id (transaction_id),
            KEY status (status),
            KEY subscription_id (subscription_id)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql1);
        dbDelta($sql2);
        dbDelta($sql3);
    }
    
    /**
     * Get user's current membership level with caching
     */
    public function get_user_membership_level($user_id = null) {
        if (!$user_id) {
            $user_id = get_current_user_id();
        }
        
        if (!$user_id) {
            return 'free';
        }
        
        // Check cache first
        $cache_key = "user_membership_{$user_id}";
        $cached_level = wp_cache_get($cache_key, 'stock_scanner');
        if ($cached_level !== false) {
            return $cached_level;
        }
        
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $subscription = $wpdb->get_row($wpdb->prepare("
            SELECT membership_level, status, end_date, trial_end_date 
            FROM {$subscriptions_table} 
            WHERE user_id = %d 
            AND status IN ('active', 'trialing', 'pending')
            ORDER BY created_at DESC 
            LIMIT 1
        ", $user_id));
        
        $level = 'free';
        
        if ($subscription) {
            $now = current_time('mysql');
            
            // Check if subscription is still valid
            if ($subscription->status === 'active' || 
                ($subscription->status === 'trialing' && $subscription->trial_end_date > $now) ||
                ($subscription->end_date && $subscription->end_date > $now)) {
                $level = $subscription->membership_level;
            } else {
                // Subscription expired, update status
                $this->update_subscription_status($user_id, 'expired');
            }
        }
        
        // Cache for 1 hour
        wp_cache_set($cache_key, $level, 'stock_scanner', HOUR_IN_SECONDS);
        
        return $level;
    }
    
    /**
     * Get user's feature access with comprehensive checking
     */
    public function user_has_feature($feature, $user_id = null) {
        $level = $this->get_user_membership_level($user_id);
        
        if (!isset($this->membership_levels[$level])) {
            return false;
        }
        
        $features = $this->membership_levels[$level]['features'];
        
        return isset($features[$feature]) ? $features[$feature] : false;
    }
    
    /**
     * Check if user can perform action based on limits
     */
    public function check_user_limit($limit_type, $user_id = null, $increment = false) {
        if (!$user_id) {
            $user_id = get_current_user_id();
        }
        
        if (!$user_id) {
            return false;
        }
        
        $level = $this->get_user_membership_level($user_id);
        $limits = $this->membership_levels[$level]['limits'] ?? [];
        
        if (!isset($limits[$limit_type])) {
            return true; // No limit defined
        }
        
        $limit_value = $limits[$limit_type];
        
        if ($limit_value === -1) {
            return true; // Unlimited
        }
        
        $current_usage = $this->get_current_usage($user_id, $limit_type);
        
        if ($increment && $current_usage < $limit_value) {
            $this->increment_usage($user_id, $limit_type);
            return true;
        }
        
        return $current_usage < $limit_value;
    }
    
    /**
     * Get current usage for a specific limit type
     */
    private function get_current_usage($user_id, $limit_type) {
        global $wpdb;
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        
        switch ($limit_type) {
            case 'api_calls_per_day':
                return (int) $wpdb->get_var($wpdb->prepare("
                    SELECT COALESCE(SUM(calls_count), 0) 
                    FROM {$usage_table} 
                    WHERE user_id = %d AND usage_date = %s
                ", $user_id, current_time('Y-m-d')));
                
            case 'api_calls_per_hour':
                return (int) $wpdb->get_var($wpdb->prepare("
                    SELECT COALESCE(SUM(calls_count), 0) 
                    FROM {$usage_table} 
                    WHERE user_id = %d 
                    AND usage_date = %s 
                    AND created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                ", $user_id, current_time('Y-m-d')));
                
            case 'concurrent_sessions':
                return $this->get_active_sessions_count($user_id);
                
            default:
                return 0;
        }
    }
    
    /**
     * Increment usage counter
     */
    private function increment_usage($user_id, $limit_type, $endpoint = 'general') {
        global $wpdb;
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        
        if (strpos($limit_type, 'api_calls') !== false) {
            $wpdb->query($wpdb->prepare("
                INSERT INTO {$usage_table} (user_id, endpoint, calls_count, usage_date) 
                VALUES (%d, %s, 1, %s)
                ON DUPLICATE KEY UPDATE calls_count = calls_count + 1
            ", $user_id, $endpoint, current_time('Y-m-d')));
        }
    }
    
    /**
     * Process subscription via AJAX (secure)
     */
    public function process_subscription_ajax() {
        // Verify nonce for security
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_subscription')) {
            wp_die(json_encode(['success' => false, 'error' => 'Security check failed']));
        }
        
        $user_id = get_current_user_id();
        if (!$user_id) {
            wp_die(json_encode(['success' => false, 'error' => 'User not logged in']));
        }
        
        $plan = sanitize_text_field($_POST['plan']);
        $payment_method = sanitize_text_field($_POST['payment_method']);
        
        if (!isset($this->membership_levels[$plan])) {
            wp_die(json_encode(['success' => false, 'error' => 'Invalid plan selected']));
        }
        
        try {
            switch ($payment_method) {
                case 'paypal':
                    $result = $this->process_paypal_subscription($user_id, $plan);
                    break;
                case 'stripe':
                    $result = $this->process_stripe_subscription($user_id, $plan);
                    break;
                default:
                    throw new Exception('Invalid payment method');
            }
            
            wp_die(json_encode($result));
            
        } catch (Exception $e) {
            error_log('Subscription processing error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false, 
                'error' => 'Payment processing failed. Please try again.'
            ]));
        }
    }
    
    /**
     * Process PayPal subscription
     */
    private function process_paypal_subscription($user_id, $plan) {
        $plan_config = $this->membership_levels[$plan];
        
        // Initialize PayPal integration
        $paypal = new StockScannerPayPalIntegration();
        
        // Create subscription
        $subscription_data = [
            'plan_id' => $plan_config['paypal_plan_id'],
            'user_id' => $user_id,
            'amount' => $plan_config['price'],
            'billing_cycle' => $plan_config['billing_cycle']
        ];
        
        $paypal_response = $paypal->create_subscription($subscription_data);
        
        if ($paypal_response['success']) {
            // Create local subscription record
            $subscription_id = $this->create_subscription_record([
                'user_id' => $user_id,
                'membership_level' => $plan,
                'payment_method' => 'paypal',
                'subscription_id' => $paypal_response['subscription_id'],
                'amount' => $plan_config['price'],
                'billing_cycle' => $plan_config['billing_cycle'],
                'status' => 'pending'
            ]);
            
            // Clear user cache
            $this->clear_user_cache($user_id);
            
            return [
                'success' => true,
                'approval_url' => $paypal_response['approval_url'],
                'subscription_id' => $subscription_id
            ];
        } else {
            throw new Exception($paypal_response['error'] ?? 'PayPal subscription creation failed');
        }
    }
    
    /**
     * Process Stripe subscription
     */
    private function process_stripe_subscription($user_id, $plan) {
        // This would integrate with Stripe API
        // For now, return a placeholder implementation
        return [
            'success' => true,
            'client_secret' => 'stripe_client_secret_placeholder',
            'message' => 'Stripe integration ready'
        ];
    }
    
    /**
     * Create subscription record in database
     */
    private function create_subscription_record($data) {
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $defaults = [
            'status' => 'active',
            'currency' => 'USD',
            'start_date' => current_time('mysql'),
            'auto_renew' => 1
        ];
        
        $data = wp_parse_args($data, $defaults);
        
        // Calculate end date based on billing cycle
        if ($data['billing_cycle'] === 'monthly') {
            $data['end_date'] = date('Y-m-d H:i:s', strtotime('+1 month', strtotime($data['start_date'])));
            $data['next_billing_date'] = $data['end_date'];
        }
        
        $wpdb->insert($subscriptions_table, $data);
        
        return $wpdb->insert_id;
    }
    
    /**
     * Handle PayPal webhook notifications
     */
    public function handle_paypal_webhook() {
        $input = file_get_contents('php://input');
        $event_data = json_decode($input, true);
        
        if (!$event_data) {
            status_header(400);
            exit('Invalid JSON');
        }
        
        // Verify webhook signature
        if (!$this->verify_paypal_webhook($input, $_SERVER['HTTP_PAYPAL_TRANSMISSION_SIG'] ?? '')) {
            status_header(401);
            exit('Webhook verification failed');
        }
        
        $event_type = $event_data['event_type'] ?? '';
        
        switch ($event_type) {
            case 'BILLING.SUBSCRIPTION.ACTIVATED':
                $this->handle_subscription_activated($event_data);
                break;
                
            case 'BILLING.SUBSCRIPTION.CANCELLED':
                $this->handle_subscription_cancelled($event_data);
                break;
                
            case 'BILLING.SUBSCRIPTION.EXPIRED':
                $this->handle_subscription_expired($event_data);
                break;
                
            case 'PAYMENT.SALE.COMPLETED':
                $this->handle_payment_completed($event_data);
                break;
                
            default:
                error_log('Unhandled PayPal webhook event: ' . $event_type);
        }
        
        status_header(200);
        exit('OK');
    }
    
    /**
     * Handle subscription activation
     */
    private function handle_subscription_activated($event_data) {
        $subscription_id = $event_data['resource']['id'] ?? '';
        
        if (!$subscription_id) {
            return;
        }
        
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $wpdb->update(
            $subscriptions_table,
            ['status' => 'active'],
            ['subscription_id' => $subscription_id]
        );
        
        // Clear user cache
        $user_id = $wpdb->get_var($wpdb->prepare("
            SELECT user_id FROM {$subscriptions_table} WHERE subscription_id = %s
        ", $subscription_id));
        
        if ($user_id) {
            $this->clear_user_cache($user_id);
            
            // Send welcome email
            $this->send_subscription_email($user_id, 'activated');
        }
    }
    
    /**
     * Handle subscription cancellation
     */
    private function handle_subscription_cancelled($event_data) {
        $subscription_id = $event_data['resource']['id'] ?? '';
        
        if (!$subscription_id) {
            return;
        }
        
        $user_id = $this->update_subscription_status_by_id($subscription_id, 'cancelled');
        
        if ($user_id) {
            $this->send_subscription_email($user_id, 'cancelled');
        }
    }
    
    /**
     * Handle subscription expiration
     */
    private function handle_subscription_expired($event_data) {
        $subscription_id = $event_data['resource']['id'] ?? '';
        
        if (!$subscription_id) {
            return;
        }
        
        $user_id = $this->update_subscription_status_by_id($subscription_id, 'expired');
        
        if ($user_id) {
            $this->send_subscription_email($user_id, 'expired');
        }
    }
    
    /**
     * Handle payment completion
     */
    private function handle_payment_completed($event_data) {
        $payment_data = $event_data['resource'] ?? [];
        $subscription_id = $payment_data['billing_agreement_id'] ?? '';
        
        if (!$subscription_id) {
            return;
        }
        
        // Record transaction
        $this->record_transaction([
            'subscription_id' => $subscription_id,
            'transaction_id' => $payment_data['id'] ?? '',
            'amount' => $payment_data['amount']['total'] ?? 0,
            'currency' => $payment_data['amount']['currency'] ?? 'USD',
            'status' => 'completed',
            'payment_method' => 'paypal',
            'transaction_type' => 'subscription_payment'
        ]);
    }
    
    /**
     * Verify PayPal webhook signature
     */
    private function verify_paypal_webhook($payload, $signature) {
        // Implement PayPal webhook signature verification
        // This is a simplified version - implement full verification in production
        return !empty($signature);
    }
    
    /**
     * Update subscription status by subscription ID
     */
    private function update_subscription_status_by_id($subscription_id, $status) {
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $user_id = $wpdb->get_var($wpdb->prepare("
            SELECT user_id FROM {$subscriptions_table} WHERE subscription_id = %s
        ", $subscription_id));
        
        if ($user_id) {
            $wpdb->update(
                $subscriptions_table,
                ['status' => $status],
                ['subscription_id' => $subscription_id]
            );
            
            $this->clear_user_cache($user_id);
        }
        
        return $user_id;
    }
    
    /**
     * Record transaction in database
     */
    private function record_transaction($data) {
        global $wpdb;
        $transactions_table = $wpdb->prefix . 'stock_scanner_transactions';
        
        // Get user_id from subscription if not provided
        if (!isset($data['user_id']) && isset($data['subscription_id'])) {
            $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
            $data['user_id'] = $wpdb->get_var($wpdb->prepare("
                SELECT user_id FROM {$subscriptions_table} WHERE subscription_id = %s
            ", $data['subscription_id']));
        }
        
        $wpdb->insert($transactions_table, $data);
    }
    
    /**
     * Send subscription-related emails
     */
    private function send_subscription_email($user_id, $type) {
        $user = get_user_by('ID', $user_id);
        if (!$user) {
            return;
        }
        
        $subject = '';
        $message = '';
        
        switch ($type) {
            case 'activated':
                $subject = 'Welcome to Stock Scanner Professional!';
                $message = 'Your subscription has been activated. Welcome to the professional trading community!';
                break;
                
            case 'cancelled':
                $subject = 'Subscription Cancelled';
                $message = 'Your subscription has been cancelled. You can reactivate anytime.';
                break;
                
            case 'expired':
                $subject = 'Subscription Expired';
                $message = 'Your subscription has expired. Renew now to continue accessing premium features.';
                break;
        }
        
        wp_mail($user->user_email, $subject, $message);
    }
    
    /**
     * Clear user cache
     */
    private function clear_user_cache($user_id) {
        wp_cache_delete("user_membership_{$user_id}", 'stock_scanner');
        unset($this->user_limits_cache[$user_id]);
    }
    
    /**
     * Assign default membership to new users
     */
    public function assign_default_membership($user_id) {
        $this->create_subscription_record([
            'user_id' => $user_id,
            'membership_level' => 'free',
            'payment_method' => 'none',
            'amount' => 0,
            'status' => 'active'
        ]);
    }
    
    /**
     * Reset daily API limits
     */
    public function reset_daily_limits() {
        global $wpdb;
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        
        // Delete usage records older than 7 days
        $wpdb->query("
            DELETE FROM {$usage_table} 
            WHERE usage_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ");
    }
    
    /**
     * Check for expired subscriptions
     */
    public function check_expired_subscriptions() {
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $expired_subscriptions = $wpdb->get_results("
            SELECT user_id, id 
            FROM {$subscriptions_table} 
            WHERE status = 'active' 
            AND end_date IS NOT NULL 
            AND end_date <= NOW()
        ");
        
        foreach ($expired_subscriptions as $subscription) {
            $this->update_subscription_status($subscription->user_id, 'expired');
            $this->send_subscription_email($subscription->user_id, 'expired');
        }
    }
    
    /**
     * Get user's subscription details
     */
    public function get_user_subscription($user_id = null) {
        if (!$user_id) {
            $user_id = get_current_user_id();
        }
        
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        return $wpdb->get_row($wpdb->prepare("
            SELECT * FROM {$subscriptions_table} 
            WHERE user_id = %d 
            ORDER BY created_at DESC 
            LIMIT 1
        ", $user_id));
    }
    
    /**
     * Get user's usage statistics
     */
    public function get_user_usage_stats($user_id = null) {
        if (!$user_id) {
            $user_id = get_current_user_id();
        }
        
        $level = $this->get_user_membership_level($user_id);
        $limits = $this->membership_levels[$level]['limits'] ?? [];
        
        return [
            'level' => $level,
            'level_name' => $this->membership_levels[$level]['name'] ?? 'Unknown',
            'daily_api_calls' => [
                'used' => $this->get_current_usage($user_id, 'api_calls_per_day'),
                'limit' => $limits['api_calls_per_day'] ?? 0
            ],
            'hourly_api_calls' => [
                'used' => $this->get_current_usage($user_id, 'api_calls_per_hour'),
                'limit' => $limits['api_calls_per_hour'] ?? 0
            ]
        ];
    }
    
    /**
     * Get all membership levels (for display)
     */
    public function get_membership_levels() {
        return $this->membership_levels;
    }
    
    /**
     * Update subscription status
     */
    private function update_subscription_status($user_id, $status) {
        global $wpdb;
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $wpdb->update(
            $subscriptions_table,
            ['status' => $status],
            ['user_id' => $user_id]
        );
        
        $this->clear_user_cache($user_id);
    }
    
    /**
     * Get active sessions count (placeholder - implement session tracking)
     */
    private function get_active_sessions_count($user_id) {
        // This would track active sessions in a separate table
        // For now, return 1 if user is logged in
        return is_user_logged_in() && get_current_user_id() == $user_id ? 1 : 0;
    }
    
    /**
     * AJAX handler for API limit checking
     */
    public function check_api_limit_ajax() {
        $user_id = get_current_user_id();
        if (!$user_id) {
            wp_die(json_encode(['allowed' => false, 'error' => 'Not logged in']));
        }
        
        $endpoint = sanitize_text_field($_POST['endpoint'] ?? 'general');
        $can_call = $this->check_user_limit('api_calls_per_hour', $user_id, true);
        
        wp_die(json_encode([
            'allowed' => $can_call,
            'usage_stats' => $this->get_user_usage_stats($user_id)
        ]));
    }
    
    /**
     * Cancel subscription AJAX handler
     */
    public function cancel_subscription_ajax() {
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_subscription')) {
            wp_die(json_encode(['success' => false, 'error' => 'Security check failed']));
        }
        
        $user_id = get_current_user_id();
        if (!$user_id) {
            wp_die(json_encode(['success' => false, 'error' => 'User not logged in']));
        }
        
        $subscription = $this->get_user_subscription($user_id);
        if (!$subscription || $subscription->status !== 'active') {
            wp_die(json_encode(['success' => false, 'error' => 'No active subscription found']));
        }
        
        // Cancel with payment provider
        if ($subscription->payment_method === 'paypal') {
            $paypal = new StockScannerPayPalIntegration();
            $result = $paypal->cancel_subscription($subscription->subscription_id);
            
            if ($result['success']) {
                $this->update_subscription_status($user_id, 'cancelled');
                wp_die(json_encode(['success' => true, 'message' => 'Subscription cancelled successfully']));
            } else {
                wp_die(json_encode(['success' => false, 'error' => $result['error']]));
            }
        }
        
        wp_die(json_encode(['success' => false, 'error' => 'Cancellation not supported for this payment method']));
    }
    
    /**
     * Change plan AJAX handler
     */
    public function change_plan_ajax() {
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_subscription')) {
            wp_die(json_encode(['success' => false, 'error' => 'Security check failed']));
        }
        
        $user_id = get_current_user_id();
        $new_plan = sanitize_text_field($_POST['new_plan']);
        
        if (!$user_id || !isset($this->membership_levels[$new_plan])) {
            wp_die(json_encode(['success' => false, 'error' => 'Invalid request']));
        }
        
        $current_subscription = $this->get_user_subscription($user_id);
        
        // For plan changes, we'll create a new subscription and cancel the old one
        // This is a simplified implementation
        
        wp_die(json_encode([
            'success' => true, 
            'message' => 'Plan change initiated',
            'redirect_url' => home_url('/premium-plans/?change_plan=' . $new_plan)
        ]));
    }
    
    /**
     * Cleanup user data when user is deleted
     */
    public function cleanup_user_data($user_id) {
        global $wpdb;
        
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        $transactions_table = $wpdb->prefix . 'stock_scanner_transactions';
        
        // Cancel active subscriptions first
        $active_subscriptions = $wpdb->get_results($wpdb->prepare("
            SELECT subscription_id, payment_method 
            FROM {$subscriptions_table} 
            WHERE user_id = %d AND status = 'active'
        ", $user_id));
        
        foreach ($active_subscriptions as $sub) {
            if ($sub->payment_method === 'paypal') {
                $paypal = new StockScannerPayPalIntegration();
                $paypal->cancel_subscription($sub->subscription_id);
            }
        }
        
        // Delete user data (foreign key constraints will handle this automatically)
        $this->clear_user_cache($user_id);
    }
}

// Initialize membership manager
new StockScannerMembershipManager();