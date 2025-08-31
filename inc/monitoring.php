<?php
/**
 * Production Monitoring & Maintenance
 * System health monitoring, performance tracking, and maintenance features
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Monitoring & Maintenance Class
 */
class RTS_Monitoring {
    
    private $health_checks = array();
    private $performance_metrics = array();
    
    public function __construct() {
        add_action('init', array($this, 'init_monitoring'));
        add_action('wp_ajax_rts_health_check', array($this, 'ajax_health_check'));
        add_action('wp_ajax_rts_performance_metrics', array($this, 'ajax_performance_metrics'));
        
        // Schedule health checks
        if (!wp_next_scheduled('rts_daily_health_check')) {
            wp_schedule_event(time(), 'daily', 'rts_daily_health_check');
        }
        
        add_action('rts_daily_health_check', array($this, 'daily_health_check'));
        
        // Performance monitoring
        add_action('wp_footer', array($this, 'collect_performance_metrics'));
        
        // Database maintenance
        if (!wp_next_scheduled('rts_weekly_maintenance')) {
            wp_schedule_event(time(), 'weekly', 'rts_weekly_maintenance');
        }
        
        add_action('rts_weekly_maintenance', array($this, 'weekly_maintenance'));
        
        // Admin dashboard widgets
        if (is_admin()) {
            add_action('wp_dashboard_setup', array($this, 'add_dashboard_widgets'));
        }
        
        // REST API endpoints
        add_action('rest_api_init', array($this, 'register_rest_endpoints'));
        
        // System status page
        add_action('admin_menu', array($this, 'add_admin_menu'));
    }
    
    /**
     * Initialize monitoring system
     */
    public function init_monitoring() {
        // Register health checks
        $this->register_health_checks();
        
        // Initialize performance tracking
        $this->init_performance_tracking();
        
        // Set up error monitoring
        $this->init_error_monitoring();
        
        // Memory and resource monitoring
        $this->init_resource_monitoring();
    }
    
    /**
     * Register health checks
     */
    private function register_health_checks() {
        $this->health_checks = array(
            'database' => array(
                'name' => __('Database Connection', 'retail-trade-scanner'),
                'callback' => array($this, 'check_database_health'),
                'critical' => true,
            ),
            'filesystem' => array(
                'name' => __('File System', 'retail-trade-scanner'),
                'callback' => array($this, 'check_filesystem_health'),
                'critical' => true,
            ),
            'memory' => array(
                'name' => __('Memory Usage', 'retail-trade-scanner'),
                'callback' => array($this, 'check_memory_health'),
                'critical' => false,
            ),
            'updates' => array(
                'name' => __('Updates Available', 'retail-trade-scanner'),
                'callback' => array($this, 'check_updates_health'),
                'critical' => false,
            ),
            'security' => array(
                'name' => __('Security Status', 'retail-trade-scanner'),
                'callback' => array($this, 'check_security_health'),
                'critical' => true,
            ),
            'performance' => array(
                'name' => __('Site Performance', 'retail-trade-scanner'),
                'callback' => array($this, 'check_performance_health'),
                'critical' => false,
            ),
            'ssl' => array(
                'name' => __('SSL Certificate', 'retail-trade-scanner'),
                'callback' => array($this, 'check_ssl_health'),
                'critical' => true,
            ),
        );
    }
    
    /**
     * Check database health
     */
    public function check_database_health() {
        global $wpdb;
        
        $result = array(
            'status' => 'good',
            'message' => __('Database connection is healthy', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        // Test database connection
        $test_query = $wpdb->get_var("SELECT 1");
        if ($test_query !== '1') {
            $result['status'] = 'critical';
            $result['message'] = __('Database connection failed', 'retail-trade-scanner');
            return $result;
        }
        
        // Check database size
        $db_size = $wpdb->get_var("
            SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'db_size'
            FROM information_schema.tables
            WHERE table_schema = '" . DB_NAME . "'
        ");
        
        if ($db_size > 1000) { // 1GB
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('Database size is large: %s MB', 'retail-trade-scanner'), $db_size);
        }
        
        $result['details']['size'] = $db_size . ' MB';
        
        // Check for orphaned data
        $orphaned_meta = $wpdb->get_var("
            SELECT COUNT(*) FROM {$wpdb->postmeta} pm
            LEFT JOIN {$wpdb->posts} p ON p.ID = pm.post_id
            WHERE p.ID IS NULL
        ");
        
        if ($orphaned_meta > 100) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('Found %d orphaned meta entries', 'retail-trade-scanner'), $orphaned_meta);
        }
        
        $result['details']['orphaned_meta'] = $orphaned_meta;
        
        return $result;
    }
    
    /**
     * Check filesystem health
     */
    public function check_filesystem_health() {
        $result = array(
            'status' => 'good',
            'message' => __('File system is healthy', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        // Check disk space
        $disk_free = disk_free_space(ABSPATH);
        $disk_total = disk_total_space(ABSPATH);
        $disk_used_percent = (($disk_total - $disk_free) / $disk_total) * 100;
        
        if ($disk_used_percent > 90) {
            $result['status'] = 'critical';
            $result['message'] = sprintf(__('Disk space critically low: %d%% used', 'retail-trade-scanner'), $disk_used_percent);
        } elseif ($disk_used_percent > 80) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('Disk space getting low: %d%% used', 'retail-trade-scanner'), $disk_used_percent);
        }
        
        $result['details']['disk_usage'] = round($disk_used_percent, 1) . '%';
        $result['details']['disk_free'] = size_format($disk_free);
        
        // Check file permissions
        $upload_dir = wp_upload_dir();
        if (!is_writable($upload_dir['basedir'])) {
            $result['status'] = 'critical';
            $result['message'] = __('Upload directory is not writable', 'retail-trade-scanner');
        }
        
        $result['details']['uploads_writable'] = is_writable($upload_dir['basedir']) ? 'Yes' : 'No';
        
        return $result;
    }
    
    /**
     * Check memory health
     */
    public function check_memory_health() {
        $result = array(
            'status' => 'good',
            'message' => __('Memory usage is normal', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        $memory_limit = wp_convert_hr_to_bytes(ini_get('memory_limit'));
        $memory_usage = memory_get_peak_usage(true);
        $memory_percent = ($memory_usage / $memory_limit) * 100;
        
        if ($memory_percent > 90) {
            $result['status'] = 'critical';
            $result['message'] = sprintf(__('Memory usage critically high: %d%%', 'retail-trade-scanner'), $memory_percent);
        } elseif ($memory_percent > 80) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('Memory usage high: %d%%', 'retail-trade-scanner'), $memory_percent);
        }
        
        $result['details']['memory_limit'] = size_format($memory_limit);
        $result['details']['memory_usage'] = size_format($memory_usage);
        $result['details']['memory_percent'] = round($memory_percent, 1) . '%';
        
        return $result;
    }
    
    /**
     * Check updates health
     */
    public function check_updates_health() {
        $result = array(
            'status' => 'good',
            'message' => __('All updates are current', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        // Check WordPress core updates
        $core_updates = get_core_updates();
        if (!empty($core_updates) && $core_updates[0]->response !== 'latest') {
            $result['status'] = 'recommended';
            $result['message'] = __('WordPress core update available', 'retail-trade-scanner');
        }
        
        // Check plugin updates
        $plugin_updates = get_plugin_updates();
        if (!empty($plugin_updates)) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('%d plugin updates available', 'retail-trade-scanner'), count($plugin_updates));
        }
        
        // Check theme updates
        $theme_updates = get_theme_updates();
        if (!empty($theme_updates)) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('%d theme updates available', 'retail-trade-scanner'), count($theme_updates));
        }
        
        $result['details']['core_updates'] = !empty($core_updates) && $core_updates[0]->response !== 'latest' ? 1 : 0;
        $result['details']['plugin_updates'] = count($plugin_updates);
        $result['details']['theme_updates'] = count($theme_updates);
        
        return $result;
    }
    
    /**
     * Check security health
     */
    public function check_security_health() {
        $result = array(
            'status' => 'good',
            'message' => __('Security status is good', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        $issues = array();
        
        // Check if admin user exists
        $admin_user = get_user_by('login', 'admin');
        if ($admin_user) {
            $issues[] = __('Default "admin" user exists', 'retail-trade-scanner');
        }
        
        // Check file permissions
        if (is_writable(ABSPATH . 'wp-config.php')) {
            $issues[] = __('wp-config.php is writable', 'retail-trade-scanner');
        }
        
        // Check if debug mode is enabled in production
        if (WP_DEBUG && !WP_DEBUG_LOG) {
            $issues[] = __('Debug mode enabled without logging', 'retail-trade-scanner');
        }
        
        // Check for failed login attempts
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_login_attempts';
        if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($table_name))) === $table_name) {
            $recent_attempts = $wpdb->get_var($wpdb->prepare(
                "SELECT COUNT(*) FROM $table_name WHERE attempt_time > %s",
                date('Y-m-d H:i:s', strtotime('-24 hours'))
            ));
            
            if ($recent_attempts > 50) {
                $issues[] = sprintf(__('%d failed login attempts in last 24 hours', 'retail-trade-scanner'), $recent_attempts);
            }
            
            $result['details']['failed_logins'] = $recent_attempts;
        }
        
        if (!empty($issues)) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('%d security recommendations', 'retail-trade-scanner'), count($issues));
            $result['details']['issues'] = $issues;
        }
        
        return $result;
    }
    
    /**
     * Check performance health
     */
    public function check_performance_health() {
        $result = array(
            'status' => 'good',
            'message' => __('Performance is optimal', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        // Check for object caching
        if (!wp_using_ext_object_cache()) {
            $result['status'] = 'recommended';
            $result['message'] = __('Object caching not enabled', 'retail-trade-scanner');
        }
        
        // Check database query count
        global $wpdb;
        if ($wpdb->num_queries > 50) {
            $result['status'] = 'recommended';
            $result['message'] = sprintf(__('High database query count: %d', 'retail-trade-scanner'), $wpdb->num_queries);
        }
        
        $result['details']['db_queries'] = $wpdb->num_queries;
        $result['details']['object_cache'] = wp_using_ext_object_cache() ? 'Enabled' : 'Disabled';
        
        // Check for optimization plugins
        $optimization_plugins = array(
            'wp-rocket/wp-rocket.php',
            'w3-total-cache/w3-total-cache.php',
            'wp-super-cache/wp-cache.php',
        );
        
        $has_cache_plugin = false;
        foreach ($optimization_plugins as $plugin) {
            if (is_plugin_active($plugin)) {
                $has_cache_plugin = true;
                break;
            }
        }
        
        $result['details']['cache_plugin'] = $has_cache_plugin ? 'Yes' : 'No';
        
        return $result;
    }
    
    /**
     * Check SSL health
     */
    public function check_ssl_health() {
        $result = array(
            'status' => 'good',
            'message' => __('SSL certificate is valid', 'retail-trade-scanner'),
            'details' => array(),
        );
        
        if (!is_ssl()) {
            $result['status'] = 'critical';
            $result['message'] = __('SSL not enabled', 'retail-trade-scanner');
            return $result;
        }
        
        // Check SSL certificate expiration (if possible)
        $site_url = home_url();
        $parsed_url = parse_url($site_url);
        
        if ($parsed_url['scheme'] === 'https') {
            $context = stream_context_create(array(
                'ssl' => array(
                    'capture_peer_cert' => true,
                    'verify_peer' => false,
                    'verify_peer_name' => false,
                ),
            ));
            
            $stream = @stream_socket_client(
                'ssl://' . $parsed_url['host'] . ':' . (isset($parsed_url['port']) ? $parsed_url['port'] : 443),
                $errno,
                $errstr,
                30,
                STREAM_CLIENT_CONNECT,
                $context
            );
            
            if ($stream) {
                $params = stream_context_get_params($stream);
                $cert = openssl_x509_parse($params['options']['ssl']['peer_certificate']);
                
                if ($cert) {
                    $expires = $cert['validTo_time_t'];
                    $days_until_expiry = ($expires - time()) / (60 * 60 * 24);
                    
                    if ($days_until_expiry < 30) {
                        $result['status'] = 'recommended';
                        $result['message'] = sprintf(__('SSL certificate expires in %d days', 'retail-trade-scanner'), $days_until_expiry);
                    }
                    
                    $result['details']['expires'] = date('Y-m-d', $expires);
                    $result['details']['days_remaining'] = round($days_until_expiry);
                }
                
                fclose($stream);
            }
        }
        
        return $result;
    }
    
    /**
     * AJAX health check
     */
    public function ajax_health_check() {
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $check = sanitize_text_field($_POST['check'] ?? 'all');
        
        if ($check === 'all') {
            $results = array();
            foreach ($this->health_checks as $key => $config) {
                $results[$key] = call_user_func($config['callback']);
                $results[$key]['name'] = $config['name'];
                $results[$key]['critical'] = $config['critical'];
            }
            wp_send_json_success($results);
        } else {
            if (isset($this->health_checks[$check])) {
                $result = call_user_func($this->health_checks[$check]['callback']);
                $result['name'] = $this->health_checks[$check]['name'];
                $result['critical'] = $this->health_checks[$check]['critical'];
                wp_send_json_success($result);
            } else {
                wp_send_json_error('Invalid check');
            }
        }
    }
    
    /**
     * Daily health check
     */
    public function daily_health_check() {
        $critical_issues = array();
        
        foreach ($this->health_checks as $key => $config) {
            if ($config['critical']) {
                $result = call_user_func($config['callback']);
                if ($result['status'] === 'critical') {
                    $critical_issues[] = $config['name'] . ': ' . $result['message'];
                }
            }
        }
        
        if (!empty($critical_issues)) {
            $admin_email = get_option('admin_email');
            $subject = sprintf('[%s] Critical Health Issues Detected', get_bloginfo('name'));
            $message = "The following critical issues were detected during the daily health check:\n\n";
            $message .= implode("\n", $critical_issues);
            $message .= "\n\nPlease address these issues as soon as possible.";
            
            wp_mail($admin_email, $subject, $message);
        }
    }
    
    /**
     * Initialize performance tracking
     */
    private function init_performance_tracking() {
        if (!defined('WP_DEBUG') || !WP_DEBUG) {
            return;
        }
        
        // Track page load times
        add_action('wp_footer', array($this, 'track_page_load_time'));
        
        // Track database queries
        add_action('shutdown', array($this, 'track_database_queries'));
    }
    
    /**
     * Track page load time
     */
    public function track_page_load_time() {
        $load_time = timer_stop(0, 3);
        
        // Store in transient for dashboard widget
        $recent_loads = get_transient('rts_recent_load_times') ?: array();
        $recent_loads[] = array(
            'url' => $_SERVER['REQUEST_URI'],
            'time' => $load_time,
            'timestamp' => time(),
        );
        
        // Keep only last 50 loads
        $recent_loads = array_slice($recent_loads, -50);
        set_transient('rts_recent_load_times', $recent_loads, DAY_IN_SECONDS);
        
        // Alert if load time is too high
        if ($load_time > 3.0) {
            error_log("RTS: Slow page load detected - {$_SERVER['REQUEST_URI']} took {$load_time}s");
        }
    }
    
    /**
     * Track database queries
     */
    public function track_database_queries() {
        global $wpdb;
        
        if ($wpdb->num_queries > 100) {
            error_log("RTS: High query count detected - {$wpdb->num_queries} queries on {$_SERVER['REQUEST_URI']}");
        }
    }
    
    /**
     * Initialize error monitoring
     */
    private function init_error_monitoring() {
        // Error monitoring is handled by the error handling class
    }
    
    /**
     * Initialize resource monitoring
     */
    private function init_resource_monitoring() {
        add_action('shutdown', array($this, 'monitor_resources'));
    }
    
    /**
     * Monitor system resources
     */
    public function monitor_resources() {
        $memory_usage = memory_get_peak_usage(true);
        $memory_limit = wp_convert_hr_to_bytes(ini_get('memory_limit'));
        $memory_percent = ($memory_usage / $memory_limit) * 100;
        
        if ($memory_percent > 90) {
            error_log("RTS: High memory usage detected - {$memory_percent}% on {$_SERVER['REQUEST_URI']}");
        }
    }
    
    /**
     * Weekly maintenance tasks
     */
    public function weekly_maintenance() {
        // Clean up old error logs
        global $wpdb;
        $error_table = $wpdb->prefix . 'rts_error_log';
        if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($error_table))) === $error_table) {
            $wpdb->query($wpdb->prepare(
                "DELETE FROM $error_table WHERE created_at < %s",
                date('Y-m-d H:i:s', strtotime('-30 days'))
            ));
        }
        
        // Clean up old login attempts
        $login_table = $wpdb->prefix . 'rts_login_attempts';
        if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($login_table))) === $login_table) {
            $wpdb->query($wpdb->prepare(
                "DELETE FROM $login_table WHERE attempt_time < %s",
                date('Y-m-d H:i:s', strtotime('-7 days'))
            ));
        }
        
        // Clean up orphaned post meta
        $wpdb->query("
            DELETE pm FROM {$wpdb->postmeta} pm
            LEFT JOIN {$wpdb->posts} p ON p.ID = pm.post_id
            WHERE p.ID IS NULL
        ");
        
        // Optimize database tables
        $tables = $wpdb->get_results("SHOW TABLES", ARRAY_N);
        foreach ($tables as $table) {
            $wpdb->query("OPTIMIZE TABLE {$table[0]}");
        }
        
        // Clear expired transients
        $wpdb->query("
            DELETE a, b FROM {$wpdb->options} a, {$wpdb->options} b
            WHERE a.option_name LIKE '_transient_%'
            AND a.option_name NOT LIKE '_transient_timeout_%'
            AND b.option_name = CONCAT('_transient_timeout_', SUBSTRING(a.option_name, 12))
            AND b.option_value < UNIX_TIMESTAMP()
        ");
        
        // Generate maintenance report
        $this->generate_maintenance_report();
    }
    
    /**
     * Generate maintenance report
     */
    private function generate_maintenance_report() {
        global $wpdb;
        
        $report = array(
            'timestamp' => current_time('mysql'),
            'database_size' => $wpdb->get_var("
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1)
                FROM information_schema.tables
                WHERE table_schema = '" . DB_NAME . "'
            "),
            'post_count' => wp_count_posts()->publish,
            'user_count' => count_users()['total_users'],
            'plugin_count' => count(get_plugins()),
            'theme_count' => count(wp_get_themes()),
        );
        
        update_option('rts_last_maintenance_report', $report);
    }
    
    /**
     * Add dashboard widgets
     */
    public function add_dashboard_widgets() {
        wp_add_dashboard_widget(
            'rts_health_status',
            __('Site Health Status', 'retail-trade-scanner'),
            array($this, 'dashboard_health_widget')
        );
        
        wp_add_dashboard_widget(
            'rts_performance_metrics',
            __('Performance Metrics', 'retail-trade-scanner'),
            array($this, 'dashboard_performance_widget')
        );
    }
    
    /**
     * Dashboard health widget
     */
    public function dashboard_health_widget() {
        ?>
        <div id="rts-health-widget">
            <p><?php esc_html_e('Loading health status...', 'retail-trade-scanner'); ?></p>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $.post(ajaxurl, {
                action: 'rts_health_check',
                check: 'all'
            }, function(response) {
                if (response.success) {
                    var html = '<div class="rts-health-grid">';
                    $.each(response.data, function(key, check) {
                        var statusClass = check.status === 'good' ? 'green' : 
                                        check.status === 'recommended' ? 'orange' : 'red';
                        html += '<div class="rts-health-item">';
                        html += '<span class="status-dot ' + statusClass + '"></span>';
                        html += '<strong>' + check.name + '</strong><br>';
                        html += '<small>' + check.message + '</small>';
                        html += '</div>';
                    });
                    html += '</div>';
                    $('#rts-health-widget').html(html);
                }
            });
        });
        </script>
        
        <style>
        .rts-health-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .rts-health-item {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-dot.green { background: #46b450; }
        .status-dot.orange { background: #ffb900; }
        .status-dot.red { background: #dc3232; }
        </style>
        <?php
    }
    
    /**
     * Dashboard performance widget
     */
    public function dashboard_performance_widget() {
        $recent_loads = get_transient('rts_recent_load_times') ?: array();
        $avg_load_time = 0;
        
        if (!empty($recent_loads)) {
            $total_time = array_sum(array_column($recent_loads, 'time'));
            $avg_load_time = $total_time / count($recent_loads);
        }
        
        global $wpdb;
        $db_size = $wpdb->get_var("
            SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1)
            FROM information_schema.tables
            WHERE table_schema = '" . DB_NAME . "'
        ");
        
        ?>
        <div class="rts-performance-metrics">
            <div class="metric">
                <strong><?php esc_html_e('Average Load Time', 'retail-trade-scanner'); ?></strong><br>
                <span class="metric-value"><?php echo number_format($avg_load_time, 2); ?>s</span>
            </div>
            <div class="metric">
                <strong><?php esc_html_e('Database Size', 'retail-trade-scanner'); ?></strong><br>
                <span class="metric-value"><?php echo $db_size; ?> MB</span>
            </div>
            <div class="metric">
                <strong><?php esc_html_e('Memory Usage', 'retail-trade-scanner'); ?></strong><br>
                <span class="metric-value"><?php echo size_format(memory_get_peak_usage(true)); ?></span>
            </div>
            <div class="metric">
                <strong><?php esc_html_e('Object Cache', 'retail-trade-scanner'); ?></strong><br>
                <span class="metric-value"><?php echo wp_using_ext_object_cache() ? 'Enabled' : 'Disabled'; ?></span>
            </div>
        </div>
        
        <style>
        .rts-performance-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .metric {
            text-align: center;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .metric-value {
            font-size: 18px;
            color: #0073aa;
            font-weight: bold;
        }
        </style>
        <?php
    }
    
    /**
     * Register REST API endpoints
     */
    public function register_rest_endpoints() {
        register_rest_route('rts/v1', '/health', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_health_check'),
            'permission_callback' => array($this, 'rest_permission_check'),
        ));
        
        register_rest_route('rts/v1', '/performance', array(
            'methods' => 'GET',
            'callback' => array($this, 'rest_performance_metrics'),
            'permission_callback' => array($this, 'rest_permission_check'),
        ));
    }
    
    /**
     * REST API permission check
     */
    public function rest_permission_check() {
        return current_user_can('manage_options');
    }
    
    /**
     * REST API health check
     */
    public function rest_health_check($request) {
        $results = array();
        
        foreach ($this->health_checks as $key => $config) {
            $results[$key] = call_user_func($config['callback']);
            $results[$key]['name'] = $config['name'];
            $results[$key]['critical'] = $config['critical'];
        }
        
        return rest_ensure_response($results);
    }
    
    /**
     * REST API performance metrics
     */
    public function rest_performance_metrics($request) {
        $recent_loads = get_transient('rts_recent_load_times') ?: array();
        $metrics = array(
            'average_load_time' => 0,
            'recent_loads' => count($recent_loads),
            'memory_usage' => memory_get_peak_usage(true),
            'memory_limit' => wp_convert_hr_to_bytes(ini_get('memory_limit')),
        );
        
        if (!empty($recent_loads)) {
            $total_time = array_sum(array_column($recent_loads, 'time'));
            $metrics['average_load_time'] = $total_time / count($recent_loads);
        }
        
        return rest_ensure_response($metrics);
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_management_page(
            __('System Status', 'retail-trade-scanner'),
            __('System Status', 'retail-trade-scanner'),
            'manage_options',
            'rts-system-status',
            array($this, 'system_status_page')
        );
    }
    
    /**
     * System status page
     */
    public function system_status_page() {
        ?>
        <div class="wrap">
            <h1><?php esc_html_e('System Status', 'retail-trade-scanner'); ?></h1>
            
            <div id="rts-system-status">
                <div class="rts-status-section">
                    <h2><?php esc_html_e('Health Checks', 'retail-trade-scanner'); ?></h2>
                    <div id="health-checks-container">
                        <p><?php esc_html_e('Loading...', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
                
                <div class="rts-status-section">
                    <h2><?php esc_html_e('System Information', 'retail-trade-scanner'); ?></h2>
                    <table class="widefat">
                        <tbody>
                            <tr>
                                <td><strong><?php esc_html_e('WordPress Version', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php echo get_bloginfo('version'); ?></td>
                            </tr>
                            <tr>
                                <td><strong><?php esc_html_e('PHP Version', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php echo PHP_VERSION; ?></td>
                            </tr>
                            <tr>
                                <td><strong><?php esc_html_e('MySQL Version', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php global $wpdb; echo $wpdb->db_version(); ?></td>
                            </tr>
                            <tr>
                                <td><strong><?php esc_html_e('Server Software', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></td>
                            </tr>
                            <tr>
                                <td><strong><?php esc_html_e('Memory Limit', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php echo ini_get('memory_limit'); ?></td>
                            </tr>
                            <tr>
                                <td><strong><?php esc_html_e('Max Execution Time', 'retail-trade-scanner'); ?></strong></td>
                                <td><?php echo ini_get('max_execution_time'); ?>s</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="rts-status-section">
                    <h2><?php esc_html_e('Maintenance Actions', 'retail-trade-scanner'); ?></h2>
                    <p>
                        <button class="button button-primary" onclick="rtsTriggerMaintenance()">
                            <?php esc_html_e('Run Weekly Maintenance', 'retail-trade-scanner'); ?>
                        </button>
                        <button class="button" onclick="rtsClearCache()">
                            <?php esc_html_e('Clear Theme Cache', 'retail-trade-scanner'); ?>
                        </button>
                    </p>
                </div>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            // Load health checks
            $.post(ajaxurl, {
                action: 'rts_health_check',
                check: 'all'
            }, function(response) {
                if (response.success) {
                    var html = '<div class="rts-health-checks">';
                    $.each(response.data, function(key, check) {
                        var statusClass = check.status === 'good' ? 'notice-success' : 
                                        check.status === 'recommended' ? 'notice-warning' : 'notice-error';
                        html += '<div class="notice ' + statusClass + ' inline">';
                        html += '<p><strong>' + check.name + '</strong>: ' + check.message + '</p>';
                        if (check.details && Object.keys(check.details).length > 0) {
                            html += '<ul>';
                            $.each(check.details, function(key, value) {
                                html += '<li>' + key + ': ' + value + '</li>';
                            });
                            html += '</ul>';
                        }
                        html += '</div>';
                    });
                    html += '</div>';
                    $('#health-checks-container').html(html);
                }
            });
        });
        
        function rtsTriggerMaintenance() {
            if (confirm('<?php esc_html_e('This will run database optimization and cleanup tasks. Continue?', 'retail-trade-scanner'); ?>')) {
                jQuery.post(ajaxurl, {
                    action: 'rts_trigger_maintenance'
                }, function(response) {
                    alert('<?php esc_html_e('Maintenance completed successfully.', 'retail-trade-scanner'); ?>');
                });
            }
        }
        
        function rtsClearCache() {
            jQuery.post(ajaxurl, {
                action: 'rts_clear_cache'
            }, function(response) {
                alert('<?php esc_html_e('Cache cleared successfully.', 'retail-trade-scanner'); ?>');
            });
        }
        </script>
        
        <style>
        .rts-status-section {
            margin-bottom: 30px;
        }
        .rts-health-checks .notice {
            margin: 10px 0;
        }
        </style>
        <?php
    }
}

// Initialize monitoring
new RTS_Monitoring();

/**
 * Manual maintenance trigger
 */
add_action('wp_ajax_rts_trigger_maintenance', function() {
    if (!current_user_can('manage_options')) {
        wp_die('Unauthorized');
    }
    
    $monitoring = new RTS_Monitoring();
    $monitoring->weekly_maintenance();
    
    wp_send_json_success('Maintenance completed');
});

/**
 * Utility functions for monitoring
 */

/**
 * Get system health score
 */
function rts_get_health_score() {
    $monitoring = new RTS_Monitoring();
    $checks = array(
        'database' => $monitoring->check_database_health(),
        'filesystem' => $monitoring->check_filesystem_health(),
        'memory' => $monitoring->check_memory_health(),
        'security' => $monitoring->check_security_health(),
        'performance' => $monitoring->check_performance_health(),
        'ssl' => $monitoring->check_ssl_health(),
    );
    
    $total_checks = count($checks);
    $good_checks = 0;
    
    foreach ($checks as $check) {
        if ($check['status'] === 'good') {
            $good_checks++;
        }
    }
    
    return round(($good_checks / $total_checks) * 100);
}

/**
 * Log system event
 */
function rts_log_system_event($event, $details = array()) {
    $log_entry = array(
        'timestamp' => current_time('mysql'),
        'event' => $event,
        'details' => $details,
        'user_id' => get_current_user_id(),
        'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0',
    );
    
    $system_log = get_option('rts_system_log', array());
    $system_log[] = $log_entry;
    
    // Keep only last 100 entries
    $system_log = array_slice($system_log, -100);
    
    update_option('rts_system_log', $system_log);
}