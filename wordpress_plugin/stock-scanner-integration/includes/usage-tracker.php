<?php
/**
 * Stock Scanner Usage Tracker
 * Tracks API usage, enforces limits, and monitors system resources
 */

if (!defined('ABSPATH')) {
    exit;
}

class StockScannerUsageTracker {
    
    private $table_name;
    private $limits_table;
    private $system_stats_table;
    
    // Usage limits per membership level (per day)
    private $usage_limits = array(
        'free' => array(
            'api_calls' => 50,
            'stock_searches' => 10,
            'news_articles' => 25,
            'concurrent_requests' => 1,
            'priority' => 1,
            'price' => 0
        ),
        'basic' => array(
            'api_calls' => 1000,
            'stock_searches' => 200,
            'news_articles' => 500,
            'concurrent_requests' => 3,
            'priority' => 2,
            'price' => 15
        ),
        'pro' => array(
            'api_calls' => 5000,
            'stock_searches' => 1000,
            'news_articles' => 2500,
            'concurrent_requests' => 7,
            'priority' => 3,
            'price' => 30
        ),
        'enterprise' => array(
            'api_calls' => 20000,
            'stock_searches' => 5000,
            'news_articles' => 10000,
            'concurrent_requests' => 15,
            'priority' => 4,
            'price' => 100
        )
    );
    
    // System resource thresholds
    private $resource_thresholds = array(
        'cpu_warning' => 60,     // 60% CPU usage
        'cpu_critical' => 80,    // 80% CPU usage
        'cpu_emergency' => 95,   // 95% CPU usage - block all but professional
        'memory_warning' => 70,  // 70% memory usage
        'memory_critical' => 85, // 85% memory usage
        'memory_emergency' => 95, // 95% memory usage - block all but professional
        'disk_warning' => 80,    // 80% disk usage
        'disk_critical' => 90,   // 90% disk usage
        'disk_emergency' => 98,  // 98% disk usage - emergency mode
        'api_requests_warning' => 1000,   // 1000 requests per minute
        'api_requests_critical' => 2000,  // 2000 requests per minute
        'api_requests_emergency' => 3000  // 3000 requests per minute
    );
    
    public function __construct() {
        global $wpdb;
        $this->table_name = $wpdb->prefix . 'stock_scanner_usage';
        $this->limits_table = $wpdb->prefix . 'stock_scanner_limits';
        $this->system_stats_table = $wpdb->prefix . 'stock_scanner_system_stats';
        
        add_action('init', array($this, 'init'));
        add_action('wp_ajax_check_usage_limit', array($this, 'ajax_check_usage_limit'));
        add_action('wp_ajax_nopriv_check_usage_limit', array($this, 'ajax_check_usage_limit'));
        
        // System monitoring hooks
        add_action('stock_scanner_monitor_system', array($this, 'monitor_system_resources'));
        add_action('stock_scanner_cleanup_usage', array($this, 'cleanup_old_usage_data'));
        
        // Schedule monitoring tasks
        if (!wp_next_scheduled('stock_scanner_monitor_system')) {
            wp_schedule_event(time(), 'every_minute', 'stock_scanner_monitor_system');
        }
        
        if (!wp_next_scheduled('stock_scanner_cleanup_usage')) {
            wp_schedule_event(time(), 'daily', 'stock_scanner_cleanup_usage');
        }
    }
    
    public function init() {
        $this->create_tables();
        $this->register_cron_intervals();
    }
    
    /**
     * Create database tables for usage tracking
     */
    private function create_tables() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        // Usage tracking table
        $usage_sql = "CREATE TABLE IF NOT EXISTS {$this->table_name} (
            id int(11) NOT NULL AUTO_INCREMENT,
            user_id int(11) NOT NULL,
            membership_level varchar(50) NOT NULL,
            action_type varchar(100) NOT NULL,
            endpoint varchar(255) NOT NULL,
            ip_address varchar(45) NOT NULL,
            user_agent text,
            request_time datetime NOT NULL,
            response_time float DEFAULT 0,
            status_code int(11) DEFAULT 200,
            data_size int(11) DEFAULT 0,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY membership_level (membership_level),
            KEY action_type (action_type),
            KEY request_time (request_time),
            KEY ip_address (ip_address)
        ) $charset_collate;";
        
        // Rate limiting table
        $limits_sql = "CREATE TABLE IF NOT EXISTS {$this->limits_table} (
            id int(11) NOT NULL AUTO_INCREMENT,
            user_id int(11) NOT NULL,
            ip_address varchar(45) NOT NULL,
            membership_level varchar(50) NOT NULL,
            daily_api_calls int(11) DEFAULT 0,
            daily_searches int(11) DEFAULT 0,
            daily_news_requests int(11) DEFAULT 0,
            concurrent_requests int(11) DEFAULT 0,
            last_request datetime NOT NULL,
            date_created date NOT NULL,
            is_blocked tinyint(1) DEFAULT 0,
            block_reason varchar(255),
            block_until datetime,
            PRIMARY KEY (id),
            UNIQUE KEY user_date (user_id, date_created),
            KEY ip_address (ip_address),
            KEY membership_level (membership_level),
            KEY is_blocked (is_blocked)
        ) $charset_collate;";
        
        // System stats table
        $system_sql = "CREATE TABLE IF NOT EXISTS {$this->system_stats_table} (
            id int(11) NOT NULL AUTO_INCREMENT,
            timestamp datetime NOT NULL,
            cpu_usage float DEFAULT 0,
            memory_usage float DEFAULT 0,
            disk_usage float DEFAULT 0,
            active_connections int(11) DEFAULT 0,
            api_requests_per_minute int(11) DEFAULT 0,
            system_status varchar(50) DEFAULT 'normal',
            alert_level varchar(20) DEFAULT 'none',
            PRIMARY KEY (id),
            KEY timestamp (timestamp),
            KEY system_status (system_status),
            KEY alert_level (alert_level)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($usage_sql);
        dbDelta($limits_sql);
        dbDelta($system_sql);
    }
    
    /**
     * Register custom cron intervals
     */
    private function register_cron_intervals() {
        add_filter('cron_schedules', function($schedules) {
            $schedules['every_minute'] = array(
                'interval' => 60,
                'display' => __('Every Minute')
            );
            $schedules['every_five_minutes'] = array(
                'interval' => 300,
                'display' => __('Every 5 Minutes')
            );
            return $schedules;
        });
    }
    
    /**
     * Track API usage for a user
     */
    public function track_usage($user_id, $action_type, $endpoint, $response_time = 0, $data_size = 0) {
        global $wpdb;
        
        $membership_level = $this->get_user_membership_level($user_id);
        $ip_address = $this->get_client_ip();
        $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        
        // Insert usage record
        $wpdb->insert(
            $this->table_name,
            array(
                'user_id' => $user_id,
                'membership_level' => $membership_level,
                'action_type' => $action_type,
                'endpoint' => $endpoint,
                'ip_address' => $ip_address,
                'user_agent' => $user_agent,
                'request_time' => current_time('mysql'),
                'response_time' => $response_time,
                'data_size' => $data_size
            ),
            array('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%f', '%d')
        );
        
        // Update daily limits
        $this->update_daily_limits($user_id, $action_type, $membership_level);
        
        return $wpdb->insert_id;
    }
    
    /**
     * Check if user can make a request based on limits and system resources
     */
    public function can_make_request($user_id, $action_type) {
        // Check if user is blocked
        if ($this->is_user_blocked($user_id)) {
            return array(
                'allowed' => false,
                'reason' => 'user_blocked',
                'message' => 'Your account has been temporarily blocked. Please contact support.',
                'retry_after' => $this->get_block_expiry($user_id)
            );
        }
        
        // Check system resources first
        $system_status = $this->get_current_system_status();
        if ($system_status['alert_level'] !== 'none') {
            return $this->handle_resource_constraint($user_id, $action_type, $system_status);
        }
        
        // Check usage limits
        $usage_check = $this->check_usage_limits($user_id, $action_type);
        if (!$usage_check['allowed']) {
            return $usage_check;
        }
        
        // Check concurrent requests
        $concurrent_check = $this->check_concurrent_requests($user_id);
        if (!$concurrent_check['allowed']) {
            return $concurrent_check;
        }
        
        return array(
            'allowed' => true,
            'remaining' => $usage_check['remaining'],
            'reset_time' => $usage_check['reset_time']
        );
    }
    
            /**
         * Handle resource constraints based on user membership level with progressive scaling
         */
        private function handle_resource_constraint($user_id, $action_type, $system_status) {
            $membership_level = $this->get_user_membership_level($user_id);
            $priority = $this->usage_limits[$membership_level]['priority'];
            $alert_level = $system_status['alert_level'];
            
                    // Emergency system state - only allow Enterprise users
        if ($alert_level === 'emergency') {
            if ($membership_level !== 'enterprise') {
                    $block_message = $this->get_emergency_block_message($membership_level);
                    return array(
                        'allowed' => false,
                        'reason' => 'system_emergency',
                        'message' => $block_message['message'],
                        'retry_after' => $block_message['retry_after'],
                        'upgrade_url' => '/premium-plans/',
                        'system_status' => $system_status,
                        'emergency_mode' => true
                    );
                }
            }
            
            // Critical system state - progressive blocking
            if ($alert_level === 'critical') {
                $block_chance = $this->get_critical_block_chance($membership_level);
                
                if ($membership_level === 'free' || rand(1, 100) <= $block_chance) {
                    $block_message = $this->get_critical_block_message($membership_level);
                    return array(
                        'allowed' => false,
                        'reason' => 'system_overload',
                        'message' => $block_message['message'],
                        'retry_after' => $block_message['retry_after'],
                        'upgrade_url' => '/premium-plans/',
                        'system_status' => $system_status
                    );
                }
            }
            
            // Warning system state - throttle lower tiers
            if ($alert_level === 'warning') {
                $throttle_chance = $this->get_warning_throttle_chance($membership_level);
                
                if (rand(1, 100) <= $throttle_chance) {
                    $throttle_message = $this->get_warning_throttle_message($membership_level);
                    return array(
                        'allowed' => false,
                        'reason' => 'system_busy',
                        'message' => $throttle_message['message'],
                        'retry_after' => $throttle_message['retry_after'],
                        'upgrade_url' => '/premium-plans/',
                        'system_status' => $system_status
                    );
                }
            }
            
            return array('allowed' => true);
        }
        
        /**
         * Get emergency block message based on membership level
         */
        private function get_emergency_block_message($membership_level) {
            $messages = array(
                'free' => array(
                    'message' => 'System is in emergency mode due to extreme load. Only Enterprise subscribers ($100/month) have access during emergencies. Please upgrade or try again in 30 minutes.',
                    'retry_after' => 1800 // 30 minutes
                ),
                'basic' => array(
                    'message' => 'System emergency: Only Enterprise subscribers have priority access. Basic plan users are temporarily blocked. Upgrade to Enterprise ($100/month) for guaranteed access.',
                    'retry_after' => 900 // 15 minutes
                ),
                'pro' => array(
                    'message' => 'System emergency: Even Pro users are temporarily restricted due to extreme load. Enterprise subscribers ($100/month) have priority access during emergencies.',
                    'retry_after' => 600 // 10 minutes
                )
            );
            
            return $messages[$membership_level] ?? $messages['free'];
        }
        
        /**
         * Get critical block chance based on membership level
         */
        private function get_critical_block_chance($membership_level) {
            $chances = array(
                'free' => 100,        // Always block free users
                'basic' => 80,        // Block 80% of basic users
                'pro' => 40,          // Block 40% of pro users
                'enterprise' => 10    // Block 10% of enterprise users
            );
            
            return $chances[$membership_level] ?? 100;
        }
        
        /**
         * Get critical block message based on membership level
         */
        private function get_critical_block_message($membership_level) {
            $messages = array(
                'free' => array(
                    'message' => 'System overload: Free users are blocked during high load. Upgrade to Basic ($15/month) for priority access, or try again in 10 minutes.',
                    'retry_after' => 600
                ),
                'basic' => array(
                    'message' => 'High system load: Basic users may be temporarily restricted. Upgrade to Pro ($30/month) for better access during peak times.',
                    'retry_after' => 300
                ),
                'pro' => array(
                    'message' => 'System under heavy load: Even Pro users may experience restrictions. Enterprise users ($100/month) have guaranteed access.',
                    'retry_after' => 120
                ),
                'enterprise' => array(
                    'message' => 'System under heavy load: Enterprise users have priority access but may experience delays.',
                    'retry_after' => 60
                )
            );
            
            return $messages[$membership_level] ?? $messages['free'];
        }
        
        /**
         * Get warning throttle chance based on membership level
         */
        private function get_warning_throttle_chance($membership_level) {
            $chances = array(
                'free' => 60,         // Throttle 60% of free users
                'basic' => 30,        // Throttle 30% of basic users
                'pro' => 10,          // Throttle 10% of pro users
                'enterprise' => 0     // Never throttle enterprise users
            );
            
            return $chances[$membership_level] ?? 60;
        }
        
        /**
         * Get warning throttle message based on membership level
         */
        private function get_warning_throttle_message($membership_level) {
            $messages = array(
                'free' => array(
                    'message' => 'System is busy. Free users may experience delays. Upgrade to Basic ($15/month) for better performance.',
                    'retry_after' => 180
                ),
                'basic' => array(
                    'message' => 'System busy: Basic users may experience occasional delays. Upgrade to Pro ($30/month) for priority access.',
                    'retry_after' => 90
                ),
                'pro' => array(
                    'message' => 'System busy: Pro users have priority but may experience minor delays during peak times.',
                    'retry_after' => 30
                )
            );
            
            return $messages[$membership_level] ?? $messages['free'];
        }
    
    /**
     * Check usage limits for a user
     */
    private function check_usage_limits($user_id, $action_type) {
        global $wpdb;
        
        $membership_level = $this->get_user_membership_level($user_id);
        $limits = $this->usage_limits[$membership_level];
        $today = current_time('Y-m-d');
        
        // Get current usage
        $current_usage = $wpdb->get_row($wpdb->prepare(
            "SELECT * FROM {$this->limits_table} WHERE user_id = %d AND date_created = %s",
            $user_id, $today
        ));
        
        if (!$current_usage) {
            // Create new record for today
            $wpdb->insert(
                $this->limits_table,
                array(
                    'user_id' => $user_id,
                    'ip_address' => $this->get_client_ip(),
                    'membership_level' => $membership_level,
                    'last_request' => current_time('mysql'),
                    'date_created' => $today
                ),
                array('%d', '%s', '%s', '%s', '%s')
            );
            
            return array(
                'allowed' => true,
                'remaining' => $limits['api_calls'],
                'reset_time' => strtotime('tomorrow 00:00:00')
            );
        }
        
        // Check specific action limits
        $field_map = array(
            'api_call' => 'daily_api_calls',
            'stock_search' => 'daily_searches',
            'news_request' => 'daily_news_requests'
        );
        
        $usage_field = $field_map[$action_type] ?? 'daily_api_calls';
        $limit_key = array(
            'daily_api_calls' => 'api_calls',
            'daily_searches' => 'stock_searches',
            'daily_news_requests' => 'news_articles'
        )[$usage_field] ?? 'api_calls';
        
        $current_count = (int)$current_usage->$usage_field;
        $limit = $limits[$limit_key];
        
        if ($current_count >= $limit) {
            return array(
                'allowed' => false,
                'reason' => 'limit_exceeded',
                'message' => "Daily {$action_type} limit exceeded ({$current_count}/{$limit}). Upgrade for higher limits.",
                'current_usage' => $current_count,
                'limit' => $limit,
                'reset_time' => strtotime('tomorrow 00:00:00'),
                'upgrade_url' => '/premium-plans/'
            );
        }
        
        return array(
            'allowed' => true,
            'remaining' => $limit - $current_count,
            'reset_time' => strtotime('tomorrow 00:00:00')
        );
    }
    
    /**
     * Check concurrent requests for a user
     */
    private function check_concurrent_requests($user_id) {
        global $wpdb;
        
        $membership_level = $this->get_user_membership_level($user_id);
        $max_concurrent = $this->usage_limits[$membership_level]['concurrent_requests'];
        
        // Count active requests (last 30 seconds)
        $active_requests = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$this->table_name} 
             WHERE user_id = %d 
             AND request_time > DATE_SUB(NOW(), INTERVAL 30 SECOND)
             AND (response_time = 0 OR response_time IS NULL)",
            $user_id
        ));
        
        if ($active_requests >= $max_concurrent) {
            return array(
                'allowed' => false,
                'reason' => 'concurrent_limit',
                'message' => "Too many concurrent requests ({$active_requests}/{$max_concurrent}). Please wait for current requests to complete.",
                'retry_after' => 30
            );
        }
        
        return array('allowed' => true);
    }
    
    /**
     * Update daily usage limits
     */
    private function update_daily_limits($user_id, $action_type, $membership_level) {
        global $wpdb;
        
        $today = current_time('Y-m-d');
        $ip_address = $this->get_client_ip();
        
        $field_map = array(
            'api_call' => 'daily_api_calls',
            'stock_search' => 'daily_searches',
            'news_request' => 'daily_news_requests'
        );
        
        $field = $field_map[$action_type] ?? 'daily_api_calls';
        
        $wpdb->query($wpdb->prepare(
            "INSERT INTO {$this->limits_table} 
             (user_id, ip_address, membership_level, {$field}, last_request, date_created) 
             VALUES (%d, %s, %s, 1, %s, %s)
             ON DUPLICATE KEY UPDATE 
             {$field} = {$field} + 1, 
             last_request = %s",
            $user_id, $ip_address, $membership_level, current_time('mysql'), $today, current_time('mysql')
        ));
    }
    
    /**
     * Monitor system resources
     */
    public function monitor_system_resources() {
        $stats = $this->get_system_stats();
        $this->log_system_stats($stats);
        
        // Check for alerts
        $alert_level = $this->determine_alert_level($stats);
        $this->handle_system_alerts($alert_level, $stats);
        
        return $stats;
    }
    
    /**
     * Get current system statistics
     */
    private function get_system_stats() {
        $stats = array(
            'timestamp' => current_time('mysql'),
            'cpu_usage' => $this->get_cpu_usage(),
            'memory_usage' => $this->get_memory_usage(),
            'disk_usage' => $this->get_disk_usage(),
            'active_connections' => $this->get_active_connections(),
            'api_requests_per_minute' => $this->get_api_requests_per_minute()
        );
        
        return $stats;
    }
    
    /**
     * Get CPU usage percentage
     */
    private function get_cpu_usage() {
        if (function_exists('sys_getloadavg')) {
            $load = sys_getloadavg();
            $cpu_count = $this->get_cpu_count();
            return min(100, ($load[0] / $cpu_count) * 100);
        }
        
        // Fallback method for systems without sys_getloadavg
        if (is_readable('/proc/loadavg')) {
            $load = file_get_contents('/proc/loadavg');
            $load_avg = explode(' ', $load)[0];
            $cpu_count = $this->get_cpu_count();
            return min(100, ($load_avg / $cpu_count) * 100);
        }
        
        return 0;
    }
    
    /**
     * Get memory usage percentage
     */
    private function get_memory_usage() {
        if (is_readable('/proc/meminfo')) {
            $meminfo = file_get_contents('/proc/meminfo');
            preg_match('/MemTotal:\s+(\d+)/', $meminfo, $total_match);
            preg_match('/MemAvailable:\s+(\d+)/', $meminfo, $available_match);
            
            if ($total_match && $available_match) {
                $total = $total_match[1];
                $available = $available_match[1];
                $used = $total - $available;
                return ($used / $total) * 100;
            }
        }
        
        // Fallback to PHP memory usage
        $memory_limit = $this->parse_size(ini_get('memory_limit'));
        $memory_used = memory_get_usage(true);
        
        if ($memory_limit > 0) {
            return ($memory_used / $memory_limit) * 100;
        }
        
        return 0;
    }
    
    /**
     * Get disk usage percentage
     */
    private function get_disk_usage() {
        $total_space = disk_total_space('/');
        $free_space = disk_free_space('/');
        
        if ($total_space && $free_space) {
            $used_space = $total_space - $free_space;
            return ($used_space / $total_space) * 100;
        }
        
        return 0;
    }
    
    /**
     * Get number of active database connections
     */
    private function get_active_connections() {
        global $wpdb;
        
        $connections = $wpdb->get_var("SHOW STATUS LIKE 'Threads_connected'");
        return (int)$connections;
    }
    
    /**
     * Get API requests per minute
     */
    private function get_api_requests_per_minute() {
        global $wpdb;
        
        $count = $wpdb->get_var(
            "SELECT COUNT(*) FROM {$this->table_name} 
             WHERE request_time > DATE_SUB(NOW(), INTERVAL 1 MINUTE)"
        );
        
        return (int)$count;
    }
    
    /**
     * Determine system alert level with emergency thresholds
     */
    private function determine_alert_level($stats) {
        $cpu = $stats['cpu_usage'];
        $memory = $stats['memory_usage'];
        $disk = $stats['disk_usage'];
        $api_requests = $stats['api_requests_per_minute'] ?? 0;
        
        // Emergency level - extreme resource usage
        if ($cpu >= $this->resource_thresholds['cpu_emergency'] ||
            $memory >= $this->resource_thresholds['memory_emergency'] ||
            $disk >= $this->resource_thresholds['disk_emergency'] ||
            $api_requests >= $this->resource_thresholds['api_requests_emergency']) {
            return 'emergency';
        }
        
        // Critical level
        if ($cpu >= $this->resource_thresholds['cpu_critical'] ||
            $memory >= $this->resource_thresholds['memory_critical'] ||
            $disk >= $this->resource_thresholds['disk_critical'] ||
            $api_requests >= $this->resource_thresholds['api_requests_critical']) {
            return 'critical';
        }
        
        // Warning level
        if ($cpu >= $this->resource_thresholds['cpu_warning'] ||
            $memory >= $this->resource_thresholds['memory_warning'] ||
            $disk >= $this->resource_thresholds['disk_warning'] ||
            $api_requests >= $this->resource_thresholds['api_requests_warning']) {
            return 'warning';
        }
        
        return 'none';
    }
    
    /**
     * Handle system alerts
     */
    private function handle_system_alerts($alert_level, $stats) {
        if ($alert_level === 'none') {
            return;
        }
        
        // Log alert
        error_log("Stock Scanner System Alert [{$alert_level}]: " . json_encode($stats));
        
        // Send notifications for critical and emergency alerts
        if ($alert_level === 'critical' || $alert_level === 'emergency') {
            $this->send_admin_alert($alert_level, $stats);
        }
        
        // Send immediate emergency notifications
        if ($alert_level === 'emergency') {
            $this->send_emergency_notifications($stats);
        }
        
        // Update system status
        $this->update_system_status($alert_level, $stats);
    }
    
    /**
     * Send admin alert notification
     */
    private function send_admin_alert($alert_level, $stats) {
        $admin_email = get_option('admin_email');
        $urgency = $alert_level === 'emergency' ? 'URGENT' : 'ALERT';
        $subject = "Stock Scanner System {$urgency}: {$alert_level}";
        
        $message = "System resource alert detected:\n\n";
        $message .= "Alert Level: {$alert_level}\n";
        $message .= "CPU Usage: {$stats['cpu_usage']}%\n";
        $message .= "Memory Usage: {$stats['memory_usage']}%\n";
        $message .= "Disk Usage: {$stats['disk_usage']}%\n";
        $message .= "Active Connections: {$stats['active_connections']}\n";
        $message .= "API Requests/min: {$stats['api_requests_per_minute']}\n";
        $message .= "Timestamp: {$stats['timestamp']}\n\n";
        
        if ($alert_level === 'emergency') {
            $message .= "EMERGENCY: Only Enterprise users have access. All other users are blocked.\n";
            $message .= "Immediate action required to restore service.\n\n";
        }
        
        $message .= "Please check system resources immediately.";
        
        wp_mail($admin_email, $subject, $message);
    }
    
    /**
     * Send emergency notifications via multiple channels
     */
    private function send_emergency_notifications($stats) {
        // Log emergency to WordPress error log
        error_log("EMERGENCY: Stock Scanner system in emergency mode - only Enterprise users allowed");
        
        // Try to send Slack notification if webhook is configured
        $slack_webhook = get_option('stock_scanner_slack_webhook');
        if ($slack_webhook) {
            $this->send_slack_emergency_alert($slack_webhook, $stats);
        }
        
        // Try to send Discord notification if webhook is configured
        $discord_webhook = get_option('stock_scanner_discord_webhook');
        if ($discord_webhook) {
            $this->send_discord_emergency_alert($discord_webhook, $stats);
        }
        
        // Set emergency flag in database
        update_option('stock_scanner_emergency_mode', array(
            'active' => true,
            'started' => current_time('mysql'),
            'stats' => $stats
        ));
    }
    
    /**
     * Send Slack emergency alert
     */
    private function send_slack_emergency_alert($webhook_url, $stats) {
                    $payload = array(
                'text' => '🚨 STOCK SCANNER EMERGENCY 🚨',
                'attachments' => array(
                    array(
                        'color' => 'danger',
                        'title' => 'System Emergency - Only Enterprise Users Allowed',
                    'fields' => array(
                        array('title' => 'CPU Usage', 'value' => $stats['cpu_usage'] . '%', 'short' => true),
                        array('title' => 'Memory Usage', 'value' => $stats['memory_usage'] . '%', 'short' => true),
                        array('title' => 'Disk Usage', 'value' => $stats['disk_usage'] . '%', 'short' => true),
                        array('title' => 'API Requests/min', 'value' => $stats['api_requests_per_minute'], 'short' => true)
                    ),
                    'footer' => 'Stock Scanner Monitoring',
                    'ts' => time()
                )
            )
        );
        
        wp_remote_post($webhook_url, array(
            'body' => json_encode($payload),
            'headers' => array('Content-Type' => 'application/json')
        ));
    }
    
    /**
     * Send Discord emergency alert
     */
    private function send_discord_emergency_alert($webhook_url, $stats) {
                    $payload = array(
                'content' => '🚨 **STOCK SCANNER EMERGENCY** 🚨',
                'embeds' => array(
                    array(
                        'title' => 'System Emergency - Only Enterprise Users Allowed',
                    'color' => 15158332, // Red color
                    'fields' => array(
                        array('name' => 'CPU Usage', 'value' => $stats['cpu_usage'] . '%', 'inline' => true),
                        array('name' => 'Memory Usage', 'value' => $stats['memory_usage'] . '%', 'inline' => true),
                        array('name' => 'Disk Usage', 'value' => $stats['disk_usage'] . '%', 'inline' => true),
                        array('name' => 'API Requests/min', 'value' => $stats['api_requests_per_minute'], 'inline' => true)
                    ),
                    'timestamp' => date('c'),
                    'footer' => array('text' => 'Stock Scanner Monitoring')
                )
            )
        );
        
        wp_remote_post($webhook_url, array(
            'body' => json_encode($payload),
            'headers' => array('Content-Type' => 'application/json')
        ));
    }
    
    /**
     * Log system statistics
     */
    private function log_system_stats($stats) {
        global $wpdb;
        
        $alert_level = $this->determine_alert_level($stats);
        $system_status = 'normal';
        
        switch ($alert_level) {
            case 'emergency':
                $system_status = 'emergency';
                break;
            case 'critical':
                $system_status = 'overloaded';
                break;
            case 'warning':
                $system_status = 'busy';
                break;
            default:
                $system_status = 'normal';
        }
        
        $wpdb->insert(
            $this->system_stats_table,
            array(
                'timestamp' => $stats['timestamp'],
                'cpu_usage' => $stats['cpu_usage'],
                'memory_usage' => $stats['memory_usage'],
                'disk_usage' => $stats['disk_usage'],
                'active_connections' => $stats['active_connections'],
                'api_requests_per_minute' => $stats['api_requests_per_minute'],
                'system_status' => $system_status,
                'alert_level' => $alert_level
            ),
            array('%s', '%f', '%f', '%f', '%d', '%d', '%s', '%s')
        );
    }
    
    /**
     * Get current system status
     */
    private function get_current_system_status() {
        global $wpdb;
        
        $status = $wpdb->get_row(
            "SELECT * FROM {$this->system_stats_table} 
             ORDER BY timestamp DESC LIMIT 1"
        );
        
        if (!$status) {
            return array(
                'system_status' => 'normal',
                'alert_level' => 'none',
                'cpu_usage' => 0,
                'memory_usage' => 0,
                'disk_usage' => 0
            );
        }
        
        return array(
            'system_status' => $status->system_status,
            'alert_level' => $status->alert_level,
            'cpu_usage' => $status->cpu_usage,
            'memory_usage' => $status->memory_usage,
            'disk_usage' => $status->disk_usage,
            'active_connections' => $status->active_connections,
            'api_requests_per_minute' => $status->api_requests_per_minute
        );
    }
    
    /**
     * Update system status
     */
    private function update_system_status($alert_level, $stats) {
        update_option('stock_scanner_system_status', array(
            'alert_level' => $alert_level,
            'last_update' => current_time('mysql'),
            'stats' => $stats
        ));
    }
    
    /**
     * Check if user is blocked
     */
    private function is_user_blocked($user_id) {
        global $wpdb;
        
        $block = $wpdb->get_row($wpdb->prepare(
            "SELECT * FROM {$this->limits_table} 
             WHERE user_id = %d 
             AND is_blocked = 1 
             AND (block_until IS NULL OR block_until > NOW())",
            $user_id
        ));
        
        return $block !== null;
    }
    
    /**
     * Get block expiry time
     */
    private function get_block_expiry($user_id) {
        global $wpdb;
        
        $block_until = $wpdb->get_var($wpdb->prepare(
            "SELECT block_until FROM {$this->limits_table} 
             WHERE user_id = %d AND is_blocked = 1",
            $user_id
        ));
        
        return $block_until ? strtotime($block_until) : null;
    }
    
    /**
     * Block a user
     */
    public function block_user($user_id, $reason, $duration_minutes = 60) {
        global $wpdb;
        
        $block_until = date('Y-m-d H:i:s', time() + ($duration_minutes * 60));
        
        $wpdb->update(
            $this->limits_table,
            array(
                'is_blocked' => 1,
                'block_reason' => $reason,
                'block_until' => $block_until
            ),
            array('user_id' => $user_id, 'date_created' => current_time('Y-m-d')),
            array('%d', '%s', '%s'),
            array('%d', '%s')
        );
    }
    
    /**
     * Unblock a user
     */
    public function unblock_user($user_id) {
        global $wpdb;
        
        $wpdb->update(
            $this->limits_table,
            array(
                'is_blocked' => 0,
                'block_reason' => null,
                'block_until' => null
            ),
            array('user_id' => $user_id),
            array('%d', '%s', '%s'),
            array('%d')
        );
    }
    
    /**
     * Get user membership level
     */
    private function get_user_membership_level($user_id) {
        if (function_exists('pmpro_getMembershipLevelForUser')) {
            $level = pmpro_getMembershipLevelForUser($user_id);
            if ($level && $level->id) {
                switch ($level->id) {
                    case 1: return 'free';
                    case 2: return 'premium';
                    case 3: return 'professional';
                    default: return 'free';
                }
            }
        }
        
        return $user_id > 0 ? 'free' : 'free';
    }
    
    /**
     * Get client IP address
     */
    private function get_client_ip() {
        $ip_keys = array('HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR');
        
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
        
        return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    }
    
    /**
     * Get CPU count
     */
    private function get_cpu_count() {
        if (is_readable('/proc/cpuinfo')) {
            $cpuinfo = file_get_contents('/proc/cpuinfo');
            return substr_count($cpuinfo, 'processor');
        }
        
        return 1; // Default fallback
    }
    
    /**
     * Parse size string to bytes
     */
    private function parse_size($size) {
        $unit = preg_replace('/[^bkmgtpezy]/i', '', $size);
        $size = preg_replace('/[^0-9\.]/', '', $size);
        
        if ($unit) {
            return round($size * pow(1024, stripos('bkmgtpezy', $unit[0])));
        }
        
        return round($size);
    }
    
    /**
     * Cleanup old usage data
     */
    public function cleanup_old_usage_data() {
        global $wpdb;
        
        // Keep usage data for 30 days
        $wpdb->query(
            "DELETE FROM {$this->table_name} 
             WHERE request_time < DATE_SUB(NOW(), INTERVAL 30 DAY)"
        );
        
        // Keep limits data for 7 days
        $wpdb->query(
            "DELETE FROM {$this->limits_table} 
             WHERE date_created < DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        );
        
        // Keep system stats for 7 days
        $wpdb->query(
            "DELETE FROM {$this->system_stats_table} 
             WHERE timestamp < DATE_SUB(NOW(), INTERVAL 7 DAY)"
        );
    }
    
    /**
     * AJAX handler for checking usage limits
     */
    public function ajax_check_usage_limit() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        $action_type = sanitize_text_field($_POST['action_type'] ?? 'api_call');
        
        $result = $this->can_make_request($user_id, $action_type);
        
        wp_send_json($result);
    }
    
    /**
     * Get usage statistics for admin dashboard
     */
    public function get_usage_statistics($days = 7) {
        global $wpdb;
        
        $stats = array();
        
        // Usage by membership level
        $usage_by_level = $wpdb->get_results(
            "SELECT membership_level, COUNT(*) as requests, 
                    AVG(response_time) as avg_response_time,
                    COUNT(DISTINCT user_id) as unique_users
             FROM {$this->table_name} 
             WHERE request_time > DATE_SUB(NOW(), INTERVAL {$days} DAY)
             GROUP BY membership_level"
        );
        
        $stats['usage_by_level'] = $usage_by_level;
        
        // Top endpoints
        $top_endpoints = $wpdb->get_results(
            "SELECT endpoint, COUNT(*) as requests, AVG(response_time) as avg_response_time
             FROM {$this->table_name} 
             WHERE request_time > DATE_SUB(NOW(), INTERVAL {$days} DAY)
             GROUP BY endpoint 
             ORDER BY requests DESC 
             LIMIT 10"
        );
        
        $stats['top_endpoints'] = $top_endpoints;
        
        // System performance
        $system_performance = $wpdb->get_results(
            "SELECT DATE(timestamp) as date,
                    AVG(cpu_usage) as avg_cpu,
                    AVG(memory_usage) as avg_memory,
                    AVG(api_requests_per_minute) as avg_requests_per_min,
                    COUNT(CASE WHEN alert_level != 'none' THEN 1 END) as alerts
             FROM {$this->system_stats_table}
             WHERE timestamp > DATE_SUB(NOW(), INTERVAL {$days} DAY)
             GROUP BY DATE(timestamp)
             ORDER BY date DESC"
        );
        
        $stats['system_performance'] = $system_performance;
        
        // Current system status
        $stats['current_status'] = $this->get_current_system_status();
        
        return $stats;
    }
}

// Initialize the usage tracker
global $stock_scanner_usage_tracker;
$stock_scanner_usage_tracker = new StockScannerUsageTracker();