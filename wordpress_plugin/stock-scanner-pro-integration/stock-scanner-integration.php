<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://retailtradescanner.com
 * Description: Stock scanner with membership integration, anti-bot protection, and advanced analytics
 * Version: 2.1.0
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
define('STOCK_SCANNER_VERSION', '2.1.0');
define('STOCK_SCANNER_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('STOCK_SCANNER_PLUGIN_URL', plugin_dir_url(__FILE__));

/**
 * Main Stock Scanner Integration Class
 */
class Stock_Scanner_Integration {
    
    private static $instance = null;
    private $security_manager;
    
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
        
        // Initialize performance optimizer
        add_action('plugins_loaded', array($this, 'init_performance_optimizer'));
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        try {
            $this->create_tables();
            $this->init_components();
            $this->register_hooks();
            $this->init_security_manager();
        } catch (Exception $e) {
            // Log error but don't break WordPress
            error_log('Stock Scanner Plugin Error: ' . $e->getMessage());
            add_action('admin_notices', array($this, 'show_init_error'));
        }
    }
    
    /**
     * Show initialization error notice
     */
    public function show_init_error() {
        echo '<div class="notice notice-error"><p>';
        echo '<strong>Stock Scanner Plugin Error:</strong> Plugin initialization failed. ';
        echo 'Please check error logs or contact support.';
        echo '</p></div>';
    }
    
    /**
     * Initialize performance optimizer
     */
    public function init_performance_optimizer() {
        // Include the performance optimizer class
        require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-performance-optimizer.php';
        
        // Initialize performance optimizer
        if (class_exists('Stock_Scanner_Performance_Optimizer')) {
            new Stock_Scanner_Performance_Optimizer();
        }
    }
    
    /**
     * Plugin activation
     */
    public function activate() {
        $this->create_tables();
        $this->setup_default_options();
        $this->setup_cron_jobs();
        flush_rewrite_rules();
    }
    
    /**
     * Plugin deactivation
     */
    public function deactivate() {
        $this->clear_cron_jobs();
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
            ip_address varchar(45) NOT NULL,
            user_agent text DEFAULT NULL,
            request_time float NOT NULL,
            response_size int DEFAULT NULL,
            is_suspicious tinyint(1) DEFAULT 0,
            bot_score int DEFAULT 0,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY ip_address (ip_address),
            KEY created_at (created_at),
            KEY is_suspicious (is_suspicious),
            KEY bot_score (bot_score)
        ) $charset_collate;";
        
        // Subscriptions table
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $subscriptions_sql = "CREATE TABLE $subscriptions_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            plan varchar(20) NOT NULL DEFAULT 'free',
            status varchar(20) NOT NULL DEFAULT 'active',
            rate_limit_override int DEFAULT NULL,
            is_banned tinyint(1) DEFAULT 0,
            ban_reason text DEFAULT NULL,
            banned_at datetime DEFAULT NULL,
            banned_by bigint(20) DEFAULT NULL,
            started_at datetime DEFAULT CURRENT_TIMESTAMP,
            expires_at datetime DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY user_id (user_id),
            KEY status (status),
            KEY is_banned (is_banned)
        ) $charset_collate;";
        
        // Security analytics table
        $security_table = $wpdb->prefix . 'stock_scanner_security';
        $security_sql = "CREATE TABLE $security_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) DEFAULT NULL,
            ip_address varchar(45) NOT NULL,
            event_type varchar(50) NOT NULL,
            severity varchar(20) NOT NULL DEFAULT 'low',
            description text NOT NULL,
            data longtext DEFAULT NULL,
            user_agent text DEFAULT NULL,
            referer varchar(500) DEFAULT NULL,
            requests_per_minute int DEFAULT 0,
            requests_per_hour int DEFAULT 0,
            requests_per_day int DEFAULT 0,
            bot_indicators text DEFAULT NULL,
            action_taken varchar(100) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY ip_address (ip_address),
            KEY event_type (event_type),
            KEY severity (severity),
            KEY created_at (created_at)
        ) $charset_collate;";
        
        // Rate limiting table
        $rate_limit_table = $wpdb->prefix . 'stock_scanner_rate_limits';
        $rate_limit_sql = "CREATE TABLE $rate_limit_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) DEFAULT NULL,
            ip_address varchar(45) NOT NULL,
            endpoint varchar(100) NOT NULL,
            requests_count int NOT NULL DEFAULT 1,
            window_start datetime NOT NULL,
            window_end datetime NOT NULL,
            is_blocked tinyint(1) DEFAULT 0,
            block_reason varchar(255) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY unique_limit (ip_address, endpoint, window_start),
            KEY user_id (user_id),
            KEY window_end (window_end),
            KEY is_blocked (is_blocked)
        ) $charset_collate;";
        
        // Notifications table
        $notifications_table = $wpdb->prefix . 'stock_scanner_notifications';
        $notifications_sql = "CREATE TABLE $notifications_table (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            type varchar(50) NOT NULL,
            title varchar(255) NOT NULL,
            message text NOT NULL,
            data text DEFAULT NULL,
            is_read tinyint(1) DEFAULT 0,
            priority varchar(20) DEFAULT 'normal',
            expires_at datetime DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            read_at datetime DEFAULT NULL,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY type (type),
            KEY is_read (is_read),
            KEY priority (priority),
            KEY created_at (created_at)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($usage_sql);
        dbDelta($subscriptions_sql);
        dbDelta($security_sql);
        dbDelta($rate_limit_sql);
        dbDelta($notifications_sql);
    }
    
    /**
     * Setup default options
     */
    private function setup_default_options() {
        add_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        add_option('stock_scanner_version', STOCK_SCANNER_VERSION);
        
        // Payment defaults (PayPal)
        if (!get_option('paypal_mode')) { add_option('paypal_mode', 'sandbox'); }
        if (!get_option('paypal_client_id')) { add_option('paypal_client_id', ''); }
        if (!get_option('paypal_client_secret')) { add_option('paypal_client_secret', ''); }
        if (!get_option('paypal_return_url')) { add_option('paypal_return_url', home_url('/premium-plans')); }
        if (!get_option('paypal_cancel_url')) { add_option('paypal_cancel_url', home_url('/premium-plans')); }
        if (!get_option('paypal_webhook_url')) { add_option('paypal_webhook_url', home_url('/wp-json/stock-scanner/v1/paypal-webhook')); }
        
        // Anti-bot and rate limiting settings (admin discretion only)
        add_option('stock_scanner_rate_limits', json_encode(array(
            'requests_per_minute' => 10,
            'requests_per_hour' => 300,
            'requests_per_day' => 1000,
            'bot_detection_enabled' => true,
            'auto_ban_enabled' => false, // Disabled - admin discretion only
            'auto_rate_limit_enabled' => false, // Disabled - admin discretion only
            'bot_score_threshold' => 75,
            'suspicious_threshold' => 50,
            'alert_threshold' => 60 // Alert admins at this score
        )));
        
        add_option('stock_scanner_bot_patterns', json_encode(array(
            'user_agents' => array(
                'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'requests',
                'urllib', 'httpie', 'postman', 'insomnia', 'selenium', 'phantomjs'
            ),
            'suspicious_patterns' => array(
                'rapid_requests' => 20, // requests per minute
                'identical_timing' => 5, // identical intervals
            )
        )));
    }
    
    /**
     * Setup cron jobs for cleanup and monitoring
     */
    private function setup_cron_jobs() {
        if (!wp_next_scheduled('stock_scanner_cleanup_logs')) {
            wp_schedule_event(time(), 'daily', 'stock_scanner_cleanup_logs');
        }
        
        if (!wp_next_scheduled('stock_scanner_analyze_patterns')) {
            wp_schedule_event(time(), 'hourly', 'stock_scanner_analyze_patterns');
        }
    }
    
    /**
     * Clear cron jobs
     */
    private function clear_cron_jobs() {
        wp_clear_scheduled_hook('stock_scanner_cleanup_logs');
        wp_clear_scheduled_hook('stock_scanner_analyze_patterns');
    }
    
    /**
     * Initialize security manager
     */
    private function init_security_manager() {
        $this->security_manager = new Stock_Scanner_Security_Manager();
    }
    
    /**
     * Initialize components safely
     */
    private function init_components() {
        // Initialize membership manager
        if (!class_exists('Stock_Scanner_Membership_Manager')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-membership-manager.php';
        }
        
        // Initialize security manager
        if (!class_exists('Stock_Scanner_Security_Manager')) {
            $security_manager_file = STOCK_SCANNER_PLUGIN_DIR . 'includes/class-security-manager.php';
            if (file_exists($security_manager_file)) {
                require_once $security_manager_file;
            }
        }
        
        // Initialize other components only if classes don't exist
        $components = array(
            'Stock_Scanner_API' => 'includes/class-stock-api.php',
            'Stock_Scanner_PayPal' => 'includes/class-paypal-integration.php',
            'StockScannerPageManager' => 'includes/class-page-manager.php',
            'StockScannerSitemap' => 'includes/class-seo-sitemap.php',
            'StockScannerSEOOptimizer' => 'includes/class-seo-optimizer.php'
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
        
        // Admin hooks - run after theme to integrate properly
        add_action('admin_menu', array($this, 'add_admin_menu'), 15);
        add_action('admin_enqueue_scripts', array($this, 'admin_enqueue_scripts'));
        
        // User registration hook
        add_action('user_register', array($this, 'setup_new_user_membership'));
        
        // Cron hooks
        add_action('stock_scanner_cleanup_logs', array($this, 'cleanup_old_logs'));
        add_action('stock_scanner_analyze_patterns', array($this, 'analyze_usage_patterns'));
        
        // Request monitoring
        add_action('init', array($this, 'monitor_request'), 1);
    }
    
    /**
     * Add admin menu - integrate with theme menu
     */
    public function add_admin_menu() {
        try {
            // Create a single top-level menu with one Settings submenu
            add_menu_page(
                'Stock Scanner',
                'Stock Scanner',
                'manage_options',
                'stock-scanner-main',
                array($this, 'admin_settings_page'),
                'dashicons-chart-line',
                30
            );
            
            add_submenu_page(
                'stock-scanner-main',
                'Settings',
                'Settings',
                'manage_options',
                'stock-scanner-plugin-settings',
                array($this, 'admin_settings_page')
            );
        } catch (Exception $e) {
            error_log('Stock Scanner Menu Error: ' . $e->getMessage());
        }
    }
    
    /**
     * Enqueue admin scripts
     */
    public function admin_enqueue_scripts($hook) {
        // Check for both possible hook patterns (theme or plugin menu)
        if (strpos($hook, 'stock-scanner') !== false) {
            // Enqueue Chart.js for security analytics charts
            wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
            
            wp_enqueue_script('stock-scanner-admin', STOCK_SCANNER_PLUGIN_URL . 'assets/js/admin.js', array('jquery', 'chart-js'), STOCK_SCANNER_VERSION, true);
            wp_enqueue_style('stock-scanner-admin', STOCK_SCANNER_PLUGIN_URL . 'assets/css/admin.css', array(), STOCK_SCANNER_VERSION);
            
            wp_localize_script('stock-scanner-admin', 'stockScannerAdmin', array(
                'ajax_url' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('stock_scanner_admin_nonce'),
                'strings' => array(
                    'confirm_ban' => 'Are you sure you want to ban this user?',
                    'confirm_unban' => 'Are you sure you want to unban this user?',
                    'loading' => 'Loading...',
                    'error' => 'An error occurred. Please try again.',
                    'success' => 'Operation completed successfully.'
                )
            ));
        }
    }
    
    /**
     * Monitor incoming requests for bot detection
     */
    public function monitor_request() {
        if (is_admin() || wp_doing_cron() || wp_doing_ajax()) {
            return;
        }
        
        $ip = $this->get_client_ip();
        $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        $referer = $_SERVER['HTTP_REFERER'] ?? '';
        
        // Analyze request for bot patterns
        $bot_score = $this->calculate_bot_score($ip, $user_agent, $referer);
        
        if ($bot_score > 50) {
            $this->log_security_event($ip, 'suspicious_request', 'medium', 
                "Suspicious request detected with bot score: $bot_score", array(
                    'user_agent' => $user_agent,
                    'referer' => $referer,
                    'bot_score' => $bot_score
                )
            );
        }
    }
    
    /**
     * Calculate bot score based on various indicators
     */
    private function calculate_bot_score($ip, $user_agent, $referer) {
        $score = 0;
        $patterns = json_decode(get_option('stock_scanner_bot_patterns'), true);
        
        // Check user agent patterns
        foreach ($patterns['user_agents'] as $pattern) {
            if (stripos($user_agent, $pattern) !== false) {
                $score += 20;
            }
        }
        
        // Check for missing JavaScript (would be detected via AJAX calls)
        if (empty($_SERVER['HTTP_X_REQUESTED_WITH'])) {
            $score += 5;
        }
        
        // Check for suspicious headers
        if (empty($_SERVER['HTTP_ACCEPT_LANGUAGE'])) {
            $score += 10;
        }
        
        if (empty($_SERVER['HTTP_ACCEPT_ENCODING'])) {
            $score += 10;
        }
        
        // Check request frequency
        global $wpdb;
        $recent_requests = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE ip_address = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 MINUTE)",
            $ip
        ));
        
        if ($recent_requests > 20) {
            $score += 30;
        } elseif ($recent_requests > 10) {
            $score += 15;
        }
        
        return min(100, $score);
    }
    
    /**
     * Get client IP address
     */
    private function get_client_ip() {
        $ip_keys = array(
            'HTTP_CF_CONNECTING_IP',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_FORWARDED',
            'HTTP_X_CLUSTER_CLIENT_IP',
            'HTTP_FORWARDED_FOR',
            'HTTP_FORWARDED',
            'REMOTE_ADDR'
        );
        
        foreach ($ip_keys as $key) {
            if (!empty($_SERVER[$key])) {
                $ip = $_SERVER[$key];
                if (strpos($ip, ',') !== false) {
                    $ip = trim(explode(',', $ip)[0]);
                }
                if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                    return $ip;
                }
            }
        }
        
        return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    }
    
    /**
     * Log security events
     */
    private function log_security_event($ip, $event_type, $severity, $description, $data = array()) {
        global $wpdb;
        
        $user_id = get_current_user_id();
        $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        $referer = $_SERVER['HTTP_REFERER'] ?? '';
        
        // Calculate request rates
        $rates = $this->calculate_request_rates($ip);
        
        $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_security',
            array(
                'user_id' => $user_id ?: null,
                'ip_address' => $ip,
                'event_type' => $event_type,
                'severity' => $severity,
                'description' => $description,
                'data' => json_encode($data),
                'user_agent' => $user_agent,
                'referer' => $referer,
                'requests_per_minute' => $rates['minute'],
                'requests_per_hour' => $rates['hour'],
                'requests_per_day' => $rates['day'],
                'bot_indicators' => json_encode($this->detect_bot_indicators($user_agent, $data))
            )
        );
    }
    
    /**
     * Calculate request rates for IP
     */
    private function calculate_request_rates($ip) {
        global $wpdb;
        
        $minute = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE ip_address = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 MINUTE)",
            $ip
        ));
        
        $hour = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE ip_address = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)",
            $ip
        ));
        
        $day = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE ip_address = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)",
            $ip
        ));
        
        return array(
            'minute' => intval($minute),
            'hour' => intval($hour),
            'day' => intval($day)
        );
    }
    
    /**
     * Detect bot indicators
     */
    private function detect_bot_indicators($user_agent, $data) {
        $indicators = array();
        
        $bot_patterns = array(
            'automated_tool' => array('curl', 'wget', 'python', 'requests', 'httpie'),
            'browser_automation' => array('selenium', 'phantomjs', 'headless', 'chrome-lighthouse'),
            'scraping_tool' => array('scrapy', 'beautifulsoup', 'mechanize', 'jsoup'),
            'testing_tool' => array('postman', 'insomnia', 'newman', 'artillery')
        );
        
        foreach ($bot_patterns as $category => $patterns) {
            foreach ($patterns as $pattern) {
                if (stripos($user_agent, $pattern) !== false) {
                    $indicators[] = array(
                        'type' => $category,
                        'pattern' => $pattern,
                        'confidence' => 90
                    );
                }
            }
        }
        
        // Check for rapid sequential requests
        if (isset($data['bot_score']) && $data['bot_score'] > 70) {
            $indicators[] = array(
                'type' => 'high_bot_score',
                'value' => $data['bot_score'],
                'confidence' => 85
            );
        }
        
        return $indicators;
    }
    
    /**
     * Check if user/IP is rate limited (admin discretion only)
     */
    private function is_rate_limited($user_id, $ip, $endpoint) {
        global $wpdb;
        
        // Check if user is banned (only if manually banned by admin)
        if ($user_id) {
            $is_banned = $wpdb->get_var($wpdb->prepare(
                "SELECT is_banned FROM {$wpdb->prefix}stock_scanner_subscriptions WHERE user_id = %d",
                $user_id
            ));
            
            if ($is_banned) {
                return array('limited' => true, 'reason' => 'Account banned by administrator', 'type' => 'ban');
            }
        }
        
        // Check if IP is manually blocked by admin
        $is_ip_blocked = $wpdb->get_var($wpdb->prepare(
            "SELECT is_blocked FROM {$wpdb->prefix}stock_scanner_rate_limits 
             WHERE ip_address = %s AND is_blocked = 1 AND window_end > NOW()",
            $ip
        ));
        
        if ($is_ip_blocked) {
            return array('limited' => true, 'reason' => 'IP address blocked by administrator', 'type' => 'ip_block');
        }
        
        // Rate limits are now advisory only - log for admin review but don't block
        $settings = json_decode(get_option('stock_scanner_rate_limits'), true);
        $rates = $this->calculate_request_rates($ip);
        
        // Only alert admin if auto rate limiting is disabled
        if (!$settings['auto_rate_limit_enabled']) {
            if ($rates['minute'] > $settings['requests_per_minute'] || 
                $rates['hour'] > $settings['requests_per_hour'] || 
                $rates['day'] > $settings['requests_per_day']) {
                
                // Log for admin review but don't block
                $this->log_security_event($ip, 'rate_limit_exceeded_advisory', 'medium', 
                    "Rate limits exceeded (advisory): {$rates['minute']}/min, {$rates['hour']}/hr, {$rates['day']}/day");
            }
        }
        
        return array('limited' => false);
    }
    
    /**
     * AJAX handler for stock quotes with enhanced security
     */
    public function ajax_get_stock_quote() {
        $start_time = microtime(true);
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        $ip = $this->get_client_ip();
        $user_id = get_current_user_id();
        
        if (empty($symbol)) {
            wp_send_json_error('Symbol required');
        }
        
        // Check rate limiting
        $rate_check = $this->is_rate_limited($user_id, $ip, 'get_stock_quote');
        if ($rate_check['limited']) {
            $this->log_security_event($ip, 'rate_limit_exceeded', 'high', 
                "Rate limit exceeded: " . $rate_check['reason']);
            
            if ($user_id) {
                $this->send_notification($user_id, 'rate_limit', 'Rate Limit Exceeded', 
                    $rate_check['reason'] . '. Please slow down your requests or upgrade your plan.');
            }
            
            wp_send_json_error(array(
                'message' => $rate_check['reason'],
                'type' => $rate_check['type'],
                'retry_after' => 60
            ));
        }
        
        // Check user limits
        if (!$this->can_make_api_call($user_id)) {
            wp_send_json_error('API limit reached');
        }
        
        // Calculate bot score for this request
        $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        $bot_score = $this->calculate_bot_score($ip, $user_agent, '');
        
        // Log usage with security metrics
        $request_time = microtime(true) - $start_time;
        $this->log_api_usage($user_id, 'stock_quote', $symbol, $ip, $user_agent, $request_time, $bot_score);
        
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
     * Enhanced API usage logging
     */
    private function log_api_usage($user_id, $endpoint, $symbol = null, $ip = null, $user_agent = null, $request_time = 0, $bot_score = 0) {
        global $wpdb;
        
        if (!$ip) {
            $ip = $this->get_client_ip();
        }
        
        if (!$user_agent) {
            $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        }
        
        $is_suspicious = $bot_score > 50 ? 1 : 0;
        
        $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_usage',
            array(
                'user_id' => $user_id,
                'endpoint' => $endpoint,
                'symbol' => $symbol,
                'ip_address' => $ip,
                'user_agent' => $user_agent,
                'request_time' => $request_time,
                'response_size' => strlen(json_encode(array('test' => 'data'))),
                'is_suspicious' => $is_suspicious,
                'bot_score' => $bot_score,
                'created_at' => current_time('mysql')
            )
        );
        
        // Alert admin if bot score is too high (no auto-ban)
        if ($bot_score > 60 && $user_id) {
            $this->alert_admin_suspicious_user($user_id, $bot_score);
        }
    }
    
    /**
     * Alert admin about suspicious user activity (no auto-ban)
     */
    private function alert_admin_suspicious_user($user_id, $bot_score) {
        global $wpdb;
        
        $settings = json_decode(get_option('stock_scanner_rate_limits'), true);
        $alert_threshold = $settings['alert_threshold'] ?? 60;
        
        if ($bot_score < $alert_threshold) {
            return;
        }
        
        // Check if we've already alerted about this user recently (within 24 hours)
        $recent_alert = $wpdb->get_var($wpdb->prepare(
            "SELECT id FROM {$wpdb->prefix}stock_scanner_security 
             WHERE event_type = 'suspicious_user_alert' AND user_id = %d 
             AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)",
            $user_id
        ));
        
        if ($recent_alert) {
            return; // Already alerted recently
        }
        
        $user = get_user_by('ID', $user_id);
        $user_info = $user ? $user->user_login . ' (' . $user->user_email . ')' : 'User ID: ' . $user_id;
        
        $this->log_security_event($this->get_client_ip(), 'suspicious_user_alert', 'high', 
            "Suspicious user activity detected - Bot Score: $bot_score - User: $user_info - Requires admin review", array(
                'user_id' => $user_id,
                'bot_score' => $bot_score,
                'user_login' => $user ? $user->user_login : null,
                'user_email' => $user ? $user->user_email : null,
                'recommendation' => 'Review user activity and consider manual action if necessary'
            )
        );
        
        // Send alert notification to user (informational only)
        $this->send_notification($user_id, 'security_review', 'Account Under Review', 
            "We've detected some unusual activity patterns on your account. Our security team will review this automatically. Please contact support if you have any concerns.");
    }
    
    /**
     * Send notification to user
     */
    private function send_notification($user_id, $type, $title, $message, $data = array()) {
        global $wpdb;
        
        $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_notifications',
            array(
                'user_id' => $user_id,
                'type' => $type,
                'title' => $title,
                'message' => $message,
                'data' => json_encode($data),
                'priority' => in_array($type, array('account_banned', 'rate_limit')) ? 'high' : 'normal'
            )
        );
    }
    
    // Keep existing methods (ensure_user_membership, setup_new_user_membership, ajax_upgrade_membership, ajax_get_usage, can_make_api_call, get_user_usage)
    
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
     * Cleanup old logs (cron job)
     */
    public function cleanup_old_logs() {
        global $wpdb;
        
        // Delete logs older than 30 days
        $wpdb->query(
            "DELETE FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)"
        );
        
        $wpdb->query(
            "DELETE FROM {$wpdb->prefix}stock_scanner_security 
             WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)"
        );
        
        // Delete old rate limit records
        $wpdb->query(
            "DELETE FROM {$wpdb->prefix}stock_scanner_rate_limits 
             WHERE window_end < DATE_SUB(NOW(), INTERVAL 1 DAY)"
        );
        
        // Delete read notifications older than 7 days
        $wpdb->query(
            "DELETE FROM {$wpdb->prefix}stock_scanner_notifications 
             WHERE is_read = 1 AND created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)"
        );
    }
    
    /**
     * Analyze usage patterns (cron job)
     */
    public function analyze_usage_patterns() {
        global $wpdb;
        
        // Find suspicious patterns in the last hour
        $suspicious_ips = $wpdb->get_results(
            "SELECT ip_address, COUNT(*) as request_count, AVG(bot_score) as avg_bot_score
             FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
             GROUP BY ip_address
             HAVING request_count > 50 OR avg_bot_score > 70"
        );
        
        foreach ($suspicious_ips as $ip_data) {
            $this->log_security_event($ip_data->ip_address, 'pattern_analysis', 'medium',
                "Suspicious pattern detected: {$ip_data->request_count} requests, avg bot score: {$ip_data->avg_bot_score}");
        }
    }
    
    /**
     * Admin page methods - delegate to admin interface class
     */
    public function admin_security_page() {
        if (!class_exists('Stock_Scanner_Admin_Interface')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-admin-interface.php';
        }
        $admin_interface = new Stock_Scanner_Admin_Interface($this);
        $admin_interface->security_analytics_page();
    }
    
    public function admin_rate_limits_page() {
        if (!class_exists('Stock_Scanner_Admin_Interface')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-admin-interface.php';
        }
        $admin_interface = new Stock_Scanner_Admin_Interface($this);
        $admin_interface->rate_limits_page();
    }
    
    public function admin_users_page() {
        if (!class_exists('Stock_Scanner_Admin_Interface')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-admin-interface.php';
        }
        $admin_interface = new Stock_Scanner_Admin_Interface($this);
        $admin_interface->user_management_page();
    }
    
    public function admin_settings_page() {
        if (!class_exists('Stock_Scanner_Admin_Interface')) {
            require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/class-admin-interface.php';
        }
        $admin_interface = new Stock_Scanner_Admin_Interface($this);
        $admin_interface->settings_page();
    }
}

/**
 * Security Manager Class
 */
// Note: Security manager full class should live in includes/class-security-manager.php.
// Avoid redefining it here to prevent fatal redeclare errors.
if (!class_exists('Stock_Scanner_Security_Manager')) {
    class Stock_Scanner_Security_Manager {
        public function __construct() {}
        public function detect_automated_behavior($user_id, $ip) { return false; }
        public function apply_rate_limit($user_id, $ip, $action) { return true; }
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