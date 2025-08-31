<?php
/**
 * Production Error Handling & Logging
 * Comprehensive error handling, logging, and debugging features
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Error Handling Class
 */
class RTS_Error_Handler {
    
    private $log_file;
    private $max_log_size = 10485760; // 10MB
    private $error_counts = array();
    
    public function __construct() {
        $this->log_file = WP_CONTENT_DIR . '/rts-error.log';
        
        // Set up error handling
        add_action('init', array($this, 'init_error_handling'));
        
        // WordPress error hooks
        add_action('wp_die_handler', array($this, 'custom_wp_die_handler'));
        add_filter('wp_die_ajax_handler', array($this, 'custom_wp_die_ajax_handler'));
        add_filter('wp_die_xmlrpc_handler', array($this, 'custom_wp_die_xmlrpc_handler'));
        
        // Theme-specific error handling
        add_action('wp_ajax_rts_log_js_error', array($this, 'log_javascript_error'));
        add_action('wp_ajax_nopriv_rts_log_js_error', array($this, 'log_javascript_error'));
        
        // Database error handling
        add_action('shutdown', array($this, 'catch_fatal_errors'));
        
        // Admin notices for errors
        if (is_admin()) {
            add_action('admin_notices', array($this, 'show_error_notices'));
            add_action('wp_ajax_rts_dismiss_error_notice', array($this, 'dismiss_error_notice'));
        }
        
        // Error reporting based on environment
        $this->configure_error_reporting();
    }
    
    /**
     * Initialize error handling
     */
    public function init_error_handling() {
        // Set custom error handler
        set_error_handler(array($this, 'custom_error_handler'));
        set_exception_handler(array($this, 'custom_exception_handler'));
        
        // Register shutdown function to catch fatal errors
        register_shutdown_function(array($this, 'catch_fatal_errors'));
        
        // Create error log directory if it doesn't exist
        $log_dir = dirname($this->log_file);
        if (!file_exists($log_dir)) {
            wp_mkdir_p($log_dir);
        }
        
        // Rotate log files if they get too large
        $this->rotate_log_files();
    }
    
    /**
     * Configure error reporting based on environment
     */
    private function configure_error_reporting() {
        if (WP_DEBUG) {
            // Development environment
            error_reporting(E_ALL);
            ini_set('display_errors', 1);
            ini_set('log_errors', 1);
            ini_set('error_log', $this->log_file);
        } else {
            // Production environment
            error_reporting(E_ALL & ~E_NOTICE & ~E_STRICT & ~E_DEPRECATED);
            ini_set('display_errors', 0);
            ini_set('log_errors', 1);
            ini_set('error_log', $this->log_file);
        }
    }
    
    /**
     * Custom error handler
     */
    public function custom_error_handler($severity, $message, $filename, $lineno) {
        // Don't log suppressed errors
        if (!(error_reporting() & $severity)) {
            return false;
        }
        
        $error_type = $this->get_error_type($severity);
        
        $error_data = array(
            'type' => $error_type,
            'message' => $message,
            'file' => $filename,
            'line' => $lineno,
            'severity' => $severity,
            'timestamp' => current_time('mysql'),
            'url' => isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : 'CLI',
            'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : 'Unknown',
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id(),
            'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 5)
        );
        
        $this->log_error($error_data);
        
        // Track error frequency
        $this->track_error_frequency($error_type, $message);
        
        // Send alerts for critical errors
        if ($severity === E_ERROR || $severity === E_CORE_ERROR || $severity === E_COMPILE_ERROR) {
            $this->send_error_alert($error_data);
        }
        
        // Don't execute PHP internal error handler
        return true;
    }
    
    /**
     * Custom exception handler
     */
    public function custom_exception_handler($exception) {
        $error_data = array(
            'type' => 'EXCEPTION',
            'message' => $exception->getMessage(),
            'file' => $exception->getFile(),
            'line' => $exception->getLine(),
            'severity' => E_ERROR,
            'timestamp' => current_time('mysql'),
            'url' => isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : 'CLI',
            'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : 'Unknown',
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id(),
            'trace' => $exception->getTrace()
        );
        
        $this->log_error($error_data);
        $this->send_error_alert($error_data);
        
        // Display user-friendly error page
        if (!WP_DEBUG) {
            $this->display_error_page();
        }
    }
    
    /**
     * Catch fatal errors
     */
    public function catch_fatal_errors() {
        $error = error_get_last();
        
        if ($error && in_array($error['type'], array(E_ERROR, E_CORE_ERROR, E_COMPILE_ERROR, E_PARSE))) {
            $error_data = array(
                'type' => 'FATAL',
                'message' => $error['message'],
                'file' => $error['file'],
                'line' => $error['line'],
                'severity' => $error['type'],
                'timestamp' => current_time('mysql'),
                'url' => isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : 'CLI',
                'user_agent' => isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : 'Unknown',
                'ip_address' => $this->get_client_ip(),
                'user_id' => get_current_user_id(),
                'trace' => array()
            );
            
            $this->log_error($error_data);
            $this->send_error_alert($error_data);
        }
    }
    
    /**
     * Log JavaScript errors
     */
    public function log_javascript_error() {
        // Verify nonce for security
        if (!wp_verify_nonce($_POST['nonce'] ?? '', 'rts_js_error_nonce')) {
            wp_die('Security check failed');
        }
        
        $error_data = array(
            'type' => 'JAVASCRIPT',
            'message' => sanitize_text_field($_POST['message'] ?? ''),
            'file' => sanitize_text_field($_POST['filename'] ?? ''),
            'line' => intval($_POST['lineno'] ?? 0),
            'column' => intval($_POST['colno'] ?? 0),
            'stack' => sanitize_textarea_field($_POST['stack'] ?? ''),
            'url' => sanitize_text_field($_POST['url'] ?? ''),
            'user_agent' => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
            'timestamp' => current_time('mysql'),
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id()
        );
        
        $this->log_error($error_data);
        
        wp_send_json_success();
    }
    
    /**
     * Log error to file and database
     */
    private function log_error($error_data) {
        // Format error message
        $log_message = sprintf(
            "[%s] %s: %s in %s on line %d\n",
            $error_data['timestamp'],
            $error_data['type'],
            $error_data['message'],
            $error_data['file'],
            $error_data['line']
        );
        
        // Add context information
        $log_message .= sprintf(
            "URL: %s\nIP: %s\nUser ID: %d\nUser Agent: %s\n",
            $error_data['url'],
            $error_data['ip_address'],
            $error_data['user_id'],
            $error_data['user_agent']
        );
        
        // Add stack trace for debugging
        if (!empty($error_data['trace'])) {
            $log_message .= "Stack trace:\n";
            foreach ($error_data['trace'] as $i => $trace) {
                $log_message .= sprintf(
                    "#%d %s(%d): %s%s%s()\n",
                    $i,
                    $trace['file'] ?? '[internal function]',
                    $trace['line'] ?? 0,
                    $trace['class'] ?? '',
                    $trace['type'] ?? '',
                    $trace['function'] ?? ''
                );
            }
        }
        
        $log_message .= str_repeat('-', 80) . "\n";
        
        // Write to log file
        error_log($log_message, 3, $this->log_file);
        
        // Store in database for admin interface
        $this->store_error_in_database($error_data);
        
        // Clean up old errors
        $this->cleanup_old_errors();
    }
    
    /**
     * Store error in database
     */
    private function store_error_in_database($error_data) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'rts_error_log';
        
        // Create table if it doesn't exist
        $this->create_error_log_table();
        
        // Insert error
        $wpdb->insert(
            $table_name,
            array(
                'error_type' => $error_data['type'],
                'message' => $error_data['message'],
                'file' => $error_data['file'],
                'line' => $error_data['line'],
                'url' => $error_data['url'],
                'ip_address' => $error_data['ip_address'],
                'user_id' => $error_data['user_id'],
                'user_agent' => $error_data['user_agent'],
                'stack_trace' => maybe_serialize($error_data['trace'] ?? array()),
                'created_at' => $error_data['timestamp']
            ),
            array('%s', '%s', '%s', '%d', '%s', '%s', '%d', '%s', '%s', '%s')
        );
    }
    
    /**
     * Create error log table
     */
    private function create_error_log_table() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'rts_error_log';
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE IF NOT EXISTS $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            error_type varchar(50) NOT NULL,
            message text NOT NULL,
            file varchar(500) NOT NULL,
            line int(11) NOT NULL,
            url varchar(500) NOT NULL,
            ip_address varchar(45) NOT NULL,
            user_id bigint(20) DEFAULT 0,
            user_agent text,
            stack_trace longtext,
            created_at datetime NOT NULL,
            PRIMARY KEY (id),
            KEY error_type (error_type),
            KEY created_at (created_at),
            KEY user_id (user_id)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
    
    /**
     * Get error type string
     */
    private function get_error_type($severity) {
        $error_types = array(
            E_ERROR => 'ERROR',
            E_WARNING => 'WARNING',
            E_PARSE => 'PARSE',
            E_NOTICE => 'NOTICE',
            E_CORE_ERROR => 'CORE_ERROR',
            E_CORE_WARNING => 'CORE_WARNING',
            E_COMPILE_ERROR => 'COMPILE_ERROR',
            E_COMPILE_WARNING => 'COMPILE_WARNING',
            E_USER_ERROR => 'USER_ERROR',
            E_USER_WARNING => 'USER_WARNING',
            E_USER_NOTICE => 'USER_NOTICE',
            E_STRICT => 'STRICT',
            E_RECOVERABLE_ERROR => 'RECOVERABLE_ERROR',
            E_DEPRECATED => 'DEPRECATED',
            E_USER_DEPRECATED => 'USER_DEPRECATED'
        );
        
        return $error_types[$severity] ?? 'UNKNOWN';
    }
    
    /**
     * Get client IP address
     */
    private function get_client_ip() {
        $ip_keys = array('HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR');
        
        foreach ($ip_keys as $key) {
            if (array_key_exists($key, $_SERVER) === true) {
                $ip = $_SERVER[$key];
                if (strpos($ip, ',') !== false) {
                    $ip = explode(',', $ip)[0];
                }
                $ip = trim($ip);
                if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                    return $ip;
                }
            }
        }
        
        return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '0.0.0.0';
    }
    
    /**
     * Track error frequency
     */
    private function track_error_frequency($type, $message) {
        $key = md5($type . $message);
        
        if (!isset($this->error_counts[$key])) {
            $this->error_counts[$key] = 0;
        }
        
        $this->error_counts[$key]++;
        
        // Alert if error occurs too frequently
        if ($this->error_counts[$key] >= 10) {
            $this->send_frequency_alert($type, $message, $this->error_counts[$key]);
        }
    }
    
    /**
     * Send error alert
     */
    private function send_error_alert($error_data) {
        // Only send alerts in production and for critical errors
        if (WP_DEBUG || !in_array($error_data['type'], array('FATAL', 'ERROR', 'EXCEPTION'))) {
            return;
        }
        
        // Rate limit alerts (max 1 per hour for same error)
        $alert_key = 'rts_error_alert_' . md5($error_data['message'] . $error_data['file']);
        if (get_transient($alert_key)) {
            return;
        }
        
        set_transient($alert_key, true, HOUR_IN_SECONDS);
        
        $admin_email = get_option('admin_email');
        $site_name = get_bloginfo('name');
        
        $subject = sprintf('[%s] Critical Error Alert', $site_name);
        
        $message = sprintf(
            "A critical error has occurred on your website:\n\n" .
            "Error Type: %s\n" .
            "Message: %s\n" .
            "File: %s\n" .
            "Line: %d\n" .
            "URL: %s\n" .
            "Time: %s\n" .
            "User ID: %d\n\n" .
            "Please check your error logs for more details.\n\n" .
            "Website: %s",
            $error_data['type'],
            $error_data['message'],
            $error_data['file'],
            $error_data['line'],
            $error_data['url'],
            $error_data['timestamp'],
            $error_data['user_id'],
            home_url()
        );
        
        wp_mail($admin_email, $subject, $message);
    }
    
    /**
     * Send frequency alert
     */
    private function send_frequency_alert($type, $message, $count) {
        $admin_email = get_option('admin_email');
        $site_name = get_bloginfo('name');
        
        $subject = sprintf('[%s] Frequent Error Alert', $site_name);
        
        $email_message = sprintf(
            "The following error has occurred %d times recently:\n\n" .
            "Error Type: %s\n" .
            "Message: %s\n\n" .
            "This may indicate a serious issue that requires immediate attention.\n\n" .
            "Website: %s",
            $count,
            $type,
            $message,
            home_url()
        );
        
        wp_mail($admin_email, $subject, $email_message);
    }
    
    /**
     * Display user-friendly error page
     */
    private function display_error_page() {
        http_response_code(500);
        
        ?>
        <!DOCTYPE html>
        <html <?php language_attributes(); ?>>
        <head>
            <meta charset="<?php bloginfo('charset'); ?>">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title><?php esc_html_e('Server Error', 'retail-trade-scanner'); ?> - <?php bloginfo('name'); ?></title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: #433e0e;
                    color: #c1bdb3;
                    text-align: center;
                }
                .error-container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: #2a2506;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }
                h1 {
                    color: #e15554;
                    font-size: 2.5em;
                    margin-bottom: 20px;
                    font-weight: 300;
                }
                p {
                    line-height: 1.6;
                    margin-bottom: 20px;
                    font-size: 1.1em;
                }
                .btn {
                    display: inline-block;
                    background: #374a67;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    transition: background 0.3s ease;
                }
                .btn:hover {
                    background: #4a5c7a;
                }
                .error-code {
                    font-size: 0.9em;
                    color: #5f5b6b;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1><?php esc_html_e('Oops! Something went wrong', 'retail-trade-scanner'); ?></h1>
                <p><?php esc_html_e('We\'re experiencing a temporary technical issue. Our team has been notified and is working to resolve this quickly.', 'retail-trade-scanner'); ?></p>
                <p><?php esc_html_e('Please try again in a few minutes, or contact support if the problem persists.', 'retail-trade-scanner'); ?></p>
                <a href="<?php echo esc_url(home_url('/')); ?>" class="btn"><?php esc_html_e('Return to Homepage', 'retail-trade-scanner'); ?></a>
                <div class="error-code">
                    <?php printf(esc_html__('Error ID: %s', 'retail-trade-scanner'), substr(md5(time()), 0, 8)); ?>
                </div>
            </div>
        </body>
        </html>
        <?php
        exit;
    }
    
    /**
     * Show admin error notices
     */
    public function show_error_notices() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_error_log';
        
        // Check if table exists
        if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($table_name))) !== $table_name) {
            return;
        }
        
        // Get recent critical errors
        $recent_errors = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM $table_name 
             WHERE error_type IN ('FATAL', 'ERROR', 'EXCEPTION') 
             AND created_at > %s 
             ORDER BY created_at DESC 
             LIMIT 5",
            date('Y-m-d H:i:s', strtotime('-24 hours'))
        ));
        
        if (!empty($recent_errors)) {
            $dismissed_notices = get_user_meta(get_current_user_id(), 'rts_dismissed_error_notices', true);
            if (!is_array($dismissed_notices)) {
                $dismissed_notices = array();
            }
            
            foreach ($recent_errors as $error) {
                $notice_id = 'error_' . $error->id;
                
                if (!in_array($notice_id, $dismissed_notices)) {
                    ?>
                    <div class="notice notice-error is-dismissible" data-notice-id="<?php echo esc_attr($notice_id); ?>">
                        <p>
                            <strong><?php esc_html_e('Critical Error Detected:', 'retail-trade-scanner'); ?></strong>
                            <br>
                            <?php echo esc_html($error->message); ?>
                            <br>
                            <small>
                                <?php printf(
                                    esc_html__('File: %s, Line: %d, Time: %s', 'retail-trade-scanner'),
                                    esc_html(basename($error->file)),
                                    $error->line,
                                    esc_html($error->created_at)
                                ); ?>
                            </small>
                        </p>
                    </div>
                    <?php
                }
            }
            
            // Add JavaScript for dismissible notices
            ?>
            <script>
            jQuery(document).ready(function($) {
                $('.notice.is-dismissible').on('click', '.notice-dismiss', function() {
                    var noticeId = $(this).parent().data('notice-id');
                    $.post(ajaxurl, {
                        action: 'rts_dismiss_error_notice',
                        notice_id: noticeId,
                        nonce: '<?php echo wp_create_nonce('rts_dismiss_error_nonce'); ?>'
                    });
                });
            });
            </script>
            <?php
        }
    }
    
    /**
     * Dismiss error notice
     */
    public function dismiss_error_notice() {
        if (!wp_verify_nonce($_POST['nonce'], 'rts_dismiss_error_nonce')) {
            wp_die('Security check failed');
        }
        
        $notice_id = sanitize_text_field($_POST['notice_id']);
        $user_id = get_current_user_id();
        
        $dismissed_notices = get_user_meta($user_id, 'rts_dismissed_error_notices', true);
        if (!is_array($dismissed_notices)) {
            $dismissed_notices = array();
        }
        
        $dismissed_notices[] = $notice_id;
        update_user_meta($user_id, 'rts_dismissed_error_notices', $dismissed_notices);
        
        wp_send_json_success();
    }
    
    /**
     * Clean up old errors
     */
    private function cleanup_old_errors() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_error_log';
        
        // Delete errors older than 30 days
        $wpdb->query($wpdb->prepare(
            "DELETE FROM $table_name WHERE created_at < %s",
            date('Y-m-d H:i:s', strtotime('-30 days'))
        ));
    }
    
    /**
     * Rotate log files
     */
    private function rotate_log_files() {
        if (file_exists($this->log_file) && filesize($this->log_file) > $this->max_log_size) {
            $backup_file = $this->log_file . '.' . date('Y-m-d-H-i-s');
            rename($this->log_file, $backup_file);
            
            // Keep only last 5 backup files
            $log_dir = dirname($this->log_file);
            $log_files = glob($log_dir . '/rts-error.log.*');
            
            if (count($log_files) > 5) {
                usort($log_files, function($a, $b) {
                    return filemtime($a) - filemtime($b);
                });
                
                $files_to_delete = array_slice($log_files, 0, count($log_files) - 5);
                foreach ($files_to_delete as $file) {
                    unlink($file);
                }
            }
        }
    }
    
    /**
     * Custom WordPress die handlers
     */
    public function custom_wp_die_handler($function) {
        return array($this, 'wp_die_handler');
    }
    
    public function custom_wp_die_ajax_handler($function) {
        return array($this, 'wp_die_ajax_handler');
    }
    
    public function custom_wp_die_xmlrpc_handler($function) {
        return array($this, 'wp_die_xmlrpc_handler');
    }
    
    public function wp_die_handler($message, $title = '', $args = array()) {
        // Log the wp_die call
        $this->log_error(array(
            'type' => 'WP_DIE',
            'message' => is_string($message) ? $message : 'WP Die called',
            'file' => '',
            'line' => 0,
            'timestamp' => current_time('mysql'),
            'url' => $_SERVER['REQUEST_URI'] ?? '',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id(),
            'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 5)
        ));
        
        // Call default handler
        _default_wp_die_handler($message, $title, $args);
    }
    
    public function wp_die_ajax_handler($message, $title = '', $args = array()) {
        // Log AJAX errors
        $this->log_error(array(
            'type' => 'AJAX_ERROR',
            'message' => is_string($message) ? $message : 'AJAX Error',
            'file' => '',
            'line' => 0,
            'timestamp' => current_time('mysql'),
            'url' => $_SERVER['REQUEST_URI'] ?? '',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id(),
            'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 5)
        ));
        
        // Call default handler
        _ajax_wp_die_handler($message, $title, $args);
    }
    
    public function wp_die_xmlrpc_handler($message, $title = '', $args = array()) {
        // Log XML-RPC errors
        $this->log_error(array(
            'type' => 'XMLRPC_ERROR',
            'message' => is_string($message) ? $message : 'XML-RPC Error',
            'file' => '',
            'line' => 0,
            'timestamp' => current_time('mysql'),
            'url' => $_SERVER['REQUEST_URI'] ?? '',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
            'ip_address' => $this->get_client_ip(),
            'user_id' => get_current_user_id(),
            'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 5)
        ));
        
        // Call default handler
        _xmlrpc_wp_die_handler($message, $title, $args);
    }
}

// Initialize error handling
new RTS_Error_Handler();

/**
 * Error Handling Utility Functions
 */

/**
 * Log custom error with context
 */
function rts_log_error($message, $context = array()) {
    $error_data = array(
        'type' => 'CUSTOM',
        'message' => $message,
        'file' => $context['file'] ?? '',
        'line' => $context['line'] ?? 0,
        'timestamp' => current_time('mysql'),
        'url' => $_SERVER['REQUEST_URI'] ?? '',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
        'ip_address' => rts_get_client_ip(),
        'user_id' => get_current_user_id(),
        'trace' => debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 3)
    );
    
    $handler = new RTS_Error_Handler();
    $handler->log_error($error_data);
}

/**
 * Get client IP address
 */
function rts_get_client_ip() {
    $ip_keys = array('HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR');
    
    foreach ($ip_keys as $key) {
        if (array_key_exists($key, $_SERVER) === true) {
            $ip = $_SERVER[$key];
            if (strpos($ip, ',') !== false) {
                $ip = explode(',', $ip)[0];
            }
            $ip = trim($ip);
            if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                return $ip;
            }
        }
    }
    
    return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '0.0.0.0';
}

/**
 * Safe error handling for theme functions
 */
function rts_safe_include($file_path, $required = false) {
    if (!file_exists($file_path)) {
        rts_log_error("File not found: {$file_path}");
        
        if ($required) {
            wp_die("Required file not found: " . basename($file_path));
        }
        
        return false;
    }
    
    try {
        if ($required) {
            require_once $file_path;
        } else {
            include_once $file_path;
        }
        return true;
    } catch (Exception $e) {
        rts_log_error("Error including file {$file_path}: " . $e->getMessage());
        return false;
    }
}

/**
 * Graceful degradation wrapper
 */
function rts_safe_execute($callback, $fallback = null, $context = '') {
    try {
        if (is_callable($callback)) {
            return call_user_func($callback);
        }
    } catch (Exception $e) {
        rts_log_error("Error executing callback in {$context}: " . $e->getMessage());
        
        if (is_callable($fallback)) {
            return call_user_func($fallback);
        }
    }
    
    return $fallback;
}