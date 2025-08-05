<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://retailtradescanner.com
 * Description: Stock scanner with membership integration and API functionality
 * Version: 2.0.0
 * Author: Stock Scanner Team
 * License: GPL v2 or later
 * Text Domain: stock-scanner
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('STOCK_SCANNER_VERSION', '2.0.0');
define('STOCK_SCANNER_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('STOCK_SCANNER_PLUGIN_URL', plugin_dir_url(__FILE__));

/**
 * Main Stock Scanner Integration Class
 */
class Stock_Scanner_Integration {
    
    private static $instance = null;
    
    /**
     * Get singleton instance
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Constructor
     */
    private function __construct() {
        add_action('init', array($this, 'init'));
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        $this->create_tables();
        $this->init_components();
        $this->register_hooks();
    }
    
    /**
     * Plugin activation
     */
    public function activate() {
        $this->create_tables();
        $this->setup_default_options();
        flush_rewrite_rules();
    }
    
    /**
     * Plugin deactivation
     */
    public function deactivate() {
        flush_rewrite_rules();
    }
    
    /**
     * Create database tables
     */
    private function create_tables() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        // Usage tracking table
        $usage_table = $wpdb->prefix . 'stock_scanner_usage';
        $usage_sql = "CREATE TABLE $usage_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            endpoint varchar(100) NOT NULL,
            symbol varchar(20) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY created_at (created_at)
        ) $charset_collate;";
        
        // Subscriptions table
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $subscriptions_sql = "CREATE TABLE $subscriptions_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            plan varchar(20) NOT NULL DEFAULT 'free',
            status varchar(20) NOT NULL DEFAULT 'active',
            started_at datetime DEFAULT CURRENT_TIMESTAMP,
            expires_at datetime DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY user_id (user_id)
        ) $charset_collate;";
        
        // Analytics table
        $analytics_table = $wpdb->prefix . 'stock_scanner_analytics';
        $analytics_sql = "CREATE TABLE $analytics_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) DEFAULT NULL,
            action varchar(100) NOT NULL,
            data text DEFAULT NULL,
            ip_address varchar(45) DEFAULT NULL,
            user_agent text DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY action (action),
            KEY created_at (created_at)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($usage_sql);
        dbDelta($subscriptions_sql);
        dbDelta($analytics_sql);
    }
    
    /**
     * Setup default options
     */
    private function setup_default_options() {
        add_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        add_option('stock_scanner_version', STOCK_SCANNER_VERSION);
    }
    
    /**
     * Initialize components safely
     */
    private function init_components() {
        // Initialize membership manager
        if (!class_exists('Stock_Scanner_Membership_Manager')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-membership-manager.php';
        }
        
        // Initialize other components only if classes don't exist
        $components = array(
            'Stock_Scanner_API' => 'includes/class-stock-api.php',
            'Stock_Scanner_PayPal' => 'includes/class-paypal-integration.php'
        );
        
        foreach ($components as $class => $file) {
            if (!class_exists($class)) {
                $file_path = STOCK_SCANNER_PLUGIN_DIR . $file;
                if (file_exists($file_path)) {
                    require_once $file_path;
                }
            }
        }
        
        // Ensure user membership setup
        add_action('wp_loaded', array($this, 'ensure_user_membership'));
    }
    
    /**
     * Register WordPress hooks
     */
    private function register_hooks() {
        // AJAX hooks for frontend functionality
        add_action('wp_ajax_stock_scanner_get_quote', array($this, 'ajax_get_stock_quote'));
        add_action('wp_ajax_nopriv_stock_scanner_get_quote', array($this, 'ajax_get_stock_quote'));
        
        add_action('wp_ajax_stock_scanner_upgrade', array($this, 'ajax_upgrade_membership'));
        add_action('wp_ajax_stock_scanner_usage', array($this, 'ajax_get_usage'));
        
        // User registration hook
        add_action('user_register', array($this, 'setup_new_user_membership'));
    }
    
    /**
     * Ensure user has membership record
     */
    public function ensure_user_membership() {
        if (is_user_logged_in()) {
            $user_id = get_current_user_id();
            $membership_level = get_user_meta($user_id, 'membership_level', true);
            
            if (empty($membership_level)) {
                update_user_meta($user_id, 'membership_level', 'free');
                
                // Create subscription record
                global $wpdb;
                $table = $wpdb->prefix . 'stock_scanner_subscriptions';
                
                $existing = $wpdb->get_var($wpdb->prepare(
                    "SELECT id FROM $table WHERE user_id = %d",
                    $user_id
                ));
                
                if (!$existing) {
                    $wpdb->insert($table, array(
                        'user_id' => $user_id,
                        'plan' => 'free',
                        'status' => 'active'
                    ));
                }
            }
        }
    }
    
    /**
     * Setup membership for new user
     */
    public function setup_new_user_membership($user_id) {
        update_user_meta($user_id, 'membership_level', 'free');
        
        global $wpdb;
        $table = $wpdb->prefix . 'stock_scanner_subscriptions';
        
        $wpdb->insert($table, array(
            'user_id' => $user_id,
            'plan' => 'free',
            'status' => 'active'
        ));
    }
    
    /**
     * AJAX handler for stock quotes
     */
    public function ajax_get_stock_quote() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        if (empty($symbol)) {
            wp_send_json_error('Symbol required');
        }
        
        // Check user limits
        $user_id = get_current_user_id();
        if (!$this->can_make_api_call($user_id)) {
            wp_send_json_error('API limit reached');
        }
        
        // Log usage
        $this->log_api_usage($user_id, 'stock_quote', $symbol);
        
        // Mock stock data (replace with real API)
        $data = array(
            'symbol' => strtoupper($symbol),
            'price' => number_format(rand(10, 500) + (rand(0, 99) / 100), 2),
            'change' => number_format((rand(-10, 10) + (rand(0, 99) / 100)), 2),
            'change_percent' => number_format((rand(-5, 5) + (rand(0, 99) / 100)), 2),
            'volume' => number_format(rand(100000, 10000000)),
            'timestamp' => current_time('mysql')
        );
        
        wp_send_json_success($data);
    }
    
    /**
     * AJAX handler for membership upgrade
     */
    public function ajax_upgrade_membership() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        if (!$user_id) {
            wp_send_json_error('Not logged in');
        }
        
        $plan = sanitize_text_field($_POST['plan'] ?? '');
        $price = floatval($_POST['price'] ?? 0);
        
        if (!in_array($plan, array('bronze', 'silver', 'gold'))) {
            wp_send_json_error('Invalid plan');
        }
        
        // Return PayPal URL (implement actual PayPal integration)
        wp_send_json_success(array(
            'payment_url' => 'https://www.paypal.com/cgi-bin/webscr',
            'plan' => $plan,
            'price' => $price
        ));
    }
    
    /**
     * AJAX handler for usage stats
     */
    public function ajax_get_usage() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        if (!$user_id) {
            wp_send_json_error('Not logged in');
        }
        
        $usage = $this->get_user_usage($user_id);
        wp_send_json_success($usage);
    }
    
    /**
     * Check if user can make API call
     */
    private function can_make_api_call($user_id) {
        if (!$user_id) return false;
        
        $usage = $this->get_user_usage($user_id);
        $level = get_user_meta($user_id, 'membership_level', true) ?: 'free';
        
        $limits = array(
            'free' => array('monthly' => 15, 'daily' => 5, 'hourly' => 2),
            'bronze' => array('monthly' => 1500, 'daily' => 50, 'hourly' => 10),
            'silver' => array('monthly' => 5000, 'daily' => 200, 'hourly' => 25),
            'gold' => array('monthly' => -1, 'daily' => -1, 'hourly' => -1)
        );
        
        $user_limits = $limits[$level] ?? $limits['free'];
        
        if ($user_limits['monthly'] === -1) return true; // Unlimited
        
        return $usage['monthly_calls'] < $user_limits['monthly'] &&
               $usage['daily_calls'] < $user_limits['daily'] &&
               $usage['hourly_calls'] < $user_limits['hourly'];
    }
    
    /**
     * Get user usage statistics
     */
    private function get_user_usage($user_id) {
        global $wpdb;
        $table = $wpdb->prefix . 'stock_scanner_usage';
        
        $current_month = date('Y-m');
        $current_date = date('Y-m-d');
        $current_hour = date('Y-m-d H:00:00');
        
        $monthly_calls = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table WHERE user_id = %d AND DATE_FORMAT(created_at, '%%Y-%%m') = %s",
            $user_id, $current_month
        ));
        
        $daily_calls = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table WHERE user_id = %d AND DATE(created_at) = %s",
            $user_id, $current_date
        ));
        
        $hourly_calls = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table WHERE user_id = %d AND created_at >= %s",
            $user_id, $current_hour
        ));
        
        return array(
            'monthly_calls' => intval($monthly_calls),
            'daily_calls' => intval($daily_calls),
            'hourly_calls' => intval($hourly_calls)
        );
    }
    
    /**
     * Log API usage
     */
    private function log_api_usage($user_id, $endpoint, $symbol = null) {
        global $wpdb;
        $table = $wpdb->prefix . 'stock_scanner_usage';
        
        $wpdb->insert($table, array(
            'user_id' => $user_id,
            'endpoint' => $endpoint,
            'symbol' => $symbol,
            'created_at' => current_time('mysql')
        ));
    }
}

// Initialize plugin
function stock_scanner_integration_init() {
    return Stock_Scanner_Integration::get_instance();
}

// Start the plugin
add_action('plugins_loaded', 'stock_scanner_integration_init');

// Enqueue scripts for frontend
function stock_scanner_enqueue_scripts() {
    if (!is_admin()) {
        wp_enqueue_script('jquery');
        wp_localize_script('jquery', 'stock_scanner_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ));
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');