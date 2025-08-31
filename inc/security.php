<?php
/**
 * Production Security Features
 * Comprehensive security enhancements for the Retail Trade Scanner theme
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Security Class - Handles all security features
 */
class RTS_Security {
    
    public function __construct() {
        add_action('init', array($this, 'init_security_features'));
        add_action('wp_head', array($this, 'add_security_headers'));
        add_filter('wp_headers', array($this, 'add_security_response_headers'));
        add_action('wp_login_failed', array($this, 'log_failed_login'));
        add_action('wp_authenticate_user', array($this, 'check_login_attempts'), 10, 2);
        add_filter('xmlrpc_enabled', '__return_false'); // Disable XML-RPC
        
        // Input sanitization and validation
        add_action('wp_ajax_nopriv_rts_subscribe', array($this, 'secure_rts_subscribe'));
        add_action('wp_ajax_rts_subscribe', array($this, 'secure_rts_subscribe'));
        add_action('wp_ajax_nopriv_rts_contact', array($this, 'secure_rts_contact'));
        add_action('wp_ajax_rts_contact', array($this, 'secure_rts_contact'));
    }
    
    /**
     * Initialize security features
     */
    public function init_security_features() {
        // Remove WordPress version from header
        remove_action('wp_head', 'wp_generator');
        
        // Remove WP version from RSS feeds
        add_filter('the_generator', '__return_empty_string');
        
        // Hide WP version from scripts and styles
        add_filter('script_loader_src', array($this, 'remove_version_from_assets'), 15, 1);
        add_filter('style_loader_src', array($this, 'remove_version_from_assets'), 15, 1);
        
        // Disable file editing in admin
        if (!defined('DISALLOW_FILE_EDIT')) {
            define('DISALLOW_FILE_EDIT', true);
        }
        
        // Limit login attempts
        $this->init_login_security();
        
        // Content Security Policy
        $this->init_content_security_policy();
        
        // Rate limiting
        $this->init_rate_limiting();
    }
    
    /**
     * Add security headers
     */
    public function add_security_headers() {
        if (!headers_sent()) {
            // Content Security Policy
            $csp = "default-src 'self'; ";
            $csp .= "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://www.google-analytics.com https://www.googletagmanager.com; ";
            $csp .= "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; ";
            $csp .= "font-src 'self' https://fonts.gstatic.com; ";
            $csp .= "img-src 'self' data: https:; ";
            $csp .= "connect-src 'self' https://www.google-analytics.com; ";
            $csp .= "frame-ancestors 'none'; ";
            $csp .= "base-uri 'self'; ";
            $csp .= "form-action 'self';";
            
            header("Content-Security-Policy: " . $csp);
        }
        
        // Add nonce to inline scripts
        echo '<meta name="csp-nonce" content="' . esc_attr(wp_create_nonce('csp_nonce')) . '">';
    }
    
    /**
     * Add security response headers
     */
    public function add_security_response_headers($headers) {
        $headers['X-Frame-Options'] = 'DENY';
        $headers['X-XSS-Protection'] = '1; mode=block';
        $headers['X-Content-Type-Options'] = 'nosniff';
        $headers['Referrer-Policy'] = 'strict-origin-when-cross-origin';
        $headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()';
        $headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains';
        
        return $headers;
    }
    
    /**
     * Remove version numbers from assets
     */
    public function remove_version_from_assets($src) {
        if (strpos($src, 'ver=')) {
            $src = remove_query_arg('ver', $src);
        }
        return $src;
    }
    
    /**
     * Initialize login security
     */
    private function init_login_security() {
        // Create failed login attempts table
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_login_attempts';
        
        $charset_collate = $wpdb->get_charset_collate();
        $sql = "CREATE TABLE IF NOT EXISTS $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            ip_address varchar(45) NOT NULL,
            attempt_time datetime DEFAULT CURRENT_TIMESTAMP,
            username varchar(60) NOT NULL,
            PRIMARY KEY (id),
            KEY ip_time (ip_address, attempt_time)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
    
    /**
     * Log failed login attempts
     */
    public function log_failed_login($username) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_login_attempts';
        $ip = $this->get_client_ip();
        
        $wpdb->insert(
            $table_name,
            array(
                'ip_address' => $ip,
                'username' => sanitize_user($username),
                'attempt_time' => current_time('mysql')
            ),
            array('%s', '%s', '%s')
        );
        
        // Clean up old attempts (older than 24 hours)
        $wpdb->query($wpdb->prepare(
            "DELETE FROM $table_name WHERE attempt_time < %s",
            date('Y-m-d H:i:s', strtotime('-24 hours'))
        ));
    }
    
    /**
     * Check login attempts and block if necessary
     */
    public function check_login_attempts($user, $password) {
        if (is_wp_error($user)) {
            return $user;
        }
        
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_login_attempts';
        $ip = $this->get_client_ip();
        
        // Check attempts in last hour
        $attempts = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table_name WHERE ip_address = %s AND attempt_time > %s",
            $ip,
            date('Y-m-d H:i:s', strtotime('-1 hour'))
        ));
        
        if ($attempts >= 3) {
            return new WP_Error(
                'too_many_attempts',
                __('Too many failed login attempts. Please try again in 1 hour.', 'retail-trade-scanner')
            );
        }
        
        return $user;
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
     * Initialize Content Security Policy
     */
    private function init_content_security_policy() {
        // Add CSP violation reporting endpoint
        add_action('wp_ajax_nopriv_csp_violation', array($this, 'handle_csp_violation'));
        add_action('wp_ajax_csp_violation', array($this, 'handle_csp_violation'));
    }
    
    /**
     * Handle CSP violations
     */
    public function handle_csp_violation() {
        $violation = json_decode(file_get_contents('php://input'), true);
        
        if ($violation && isset($violation['csp-report'])) {
            $report = $violation['csp-report'];
            
            // Log CSP violation
            error_log(sprintf(
                'CSP Violation: %s blocked on %s (source: %s)',
                $report['blocked-uri'] ?? 'unknown',
                $report['document-uri'] ?? 'unknown',
                $report['source-file'] ?? 'inline'
            ));
        }
        
        wp_die('', '', array('response' => 204));
    }
    
    /**
     * Initialize rate limiting
     */
    private function init_rate_limiting() {
        add_action('wp_ajax_nopriv_rts_rate_limit', array($this, 'check_rate_limit'));
        add_action('wp_ajax_rts_rate_limit', array($this, 'check_rate_limit'));
    }
    
    /**
     * Check rate limit for API calls
     */
    public function check_rate_limit($action = 'general', $limit = 60, $window = 3600) {
        $ip = $this->get_client_ip();
        $key = 'rts_rate_limit_' . md5($ip . $action);
        $attempts = get_transient($key);
        
        if ($attempts === false) {
            set_transient($key, 1, $window);
            return true;
        }
        
        if ($attempts >= $limit) {
            wp_die(
                __('Rate limit exceeded. Please try again later.', 'retail-trade-scanner'),
                __('Too Many Requests', 'retail-trade-scanner'),
                array('response' => 429)
            );
        }
        
        set_transient($key, $attempts + 1, $window);
        return true;
    }
    
    /**
     * Secure subscription handler
     */
    public function secure_rts_subscribe() {
        // Rate limiting
        $this->check_rate_limit('subscribe', 10, 3600);
        
        // Verify nonce
        if (!isset($_POST['rts_subscribe_nonce']) || !wp_verify_nonce($_POST['rts_subscribe_nonce'], 'rts_subscribe')) {
            wp_die(__('Security check failed.', 'retail-trade-scanner'), __('Forbidden', 'retail-trade-scanner'), array('response' => 403));
        }
        
        // Sanitize and validate email
        $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
        
        if (!is_email($email)) {
            $this->safe_redirect_back('subscribed', '0');
        }
        
        // Check for disposable email domains
        $disposable_domains = array('10minutemail.com', 'tempmail.org', 'guerrillamail.com');
        $email_domain = substr(strrchr($email, "@"), 1);
        
        if (in_array($email_domain, $disposable_domains)) {
            $this->safe_redirect_back('subscribed', '0');
        }
        
        // Store subscription securely
        $subscription_data = array(
            'email' => $email,
            'ip_address' => $this->get_client_ip(),
            'user_agent' => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
            'timestamp' => current_time('mysql'),
            'opt_in_method' => 'website_footer'
        );
        
        // Save to database or external service
        $this->save_subscription($subscription_data);
        
        // Send confirmation email
        $admin_email = get_option('admin_email');
        $subject = sprintf(__('[%s] New Subscription', 'retail-trade-scanner'), get_bloginfo('name'));
        $message = sprintf(__('New subscription: %s', 'retail-trade-scanner'), $email);
        
        wp_mail($admin_email, $subject, $message);
        
        $this->safe_redirect_back('subscribed', '1');
    }
    
    /**
     * Secure contact form handler
     */
    public function secure_rts_contact() {
        // Rate limiting
        $this->check_rate_limit('contact', 5, 3600);
        
        // Verify nonce
        if (!isset($_POST['rts_contact_nonce']) || !wp_verify_nonce($_POST['rts_contact_nonce'], 'rts_contact')) {
            wp_die(__('Security check failed.', 'retail-trade-scanner'), __('Forbidden', 'retail-trade-scanner'), array('response' => 403));
        }
        
        // Sanitize inputs
        $name = isset($_POST['name']) ? sanitize_text_field($_POST['name']) : '';
        $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
        $message = isset($_POST['message']) ? wp_kses_post($_POST['message']) : '';
        
        // Validate inputs
        if (empty($name) || !is_email($email) || empty($message)) {
            $this->safe_redirect_back('contact', 'invalid');
        }
        
        // Basic spam filtering
        if ($this->is_spam_content($name . ' ' . $message)) {
            $this->safe_redirect_back('contact', 'spam');
        }
        
        // Send email
        $admin_email = get_option('admin_email');
        $subject = sprintf(__('[%s] Contact Form Submission', 'retail-trade-scanner'), get_bloginfo('name'));
        $email_message = sprintf(
            "Name: %s\nEmail: %s\n\nMessage:\n%s\n\n---\nIP: %s\nUser Agent: %s",
            $name,
            $email,
            wp_strip_all_tags($message),
            $this->get_client_ip(),
            sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? '')
        );
        
        $headers = array('Reply-To: ' . $email);
        wp_mail($admin_email, $subject, $email_message, $headers);
        
        $this->safe_redirect_back('contact', 'sent');
    }
    
    /**
     * Safe redirect back with parameters
     */
    private function safe_redirect_back($param, $value) {
        $url = wp_get_referer();
        if (!$url || !wp_validate_redirect($url)) {
            $url = home_url('/');
        }
        
        $url = add_query_arg(array($param => $value), $url);
        wp_safe_redirect($url);
        exit;
    }
    
    /**
     * Basic spam detection
     */
    private function is_spam_content($content) {
        $spam_patterns = array(
            '/\b(viagra|cialis|pharmacy|casino|poker|loan|mortgage)\b/i',
            '/http[s]?:\/\/[^\s]{10,}/i', // Long URLs
            '/\b\d{10,}\b/', // Long numbers
            '/(.)\1{4,}/', // Repeated characters
        );
        
        foreach ($spam_patterns as $pattern) {
            if (preg_match($pattern, $content)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Save subscription securely
     */
    private function save_subscription($data) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'rts_subscriptions';
        
        // Create table if it doesn't exist
        $charset_collate = $wpdb->get_charset_collate();
        $sql = "CREATE TABLE IF NOT EXISTS $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            email varchar(255) NOT NULL,
            ip_address varchar(45) NOT NULL,
            user_agent text,
            opt_in_method varchar(50),
            subscription_date datetime DEFAULT CURRENT_TIMESTAMP,
            status varchar(20) DEFAULT 'active',
            PRIMARY KEY (id),
            UNIQUE KEY email (email),
            KEY status (status)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
        
        // Insert subscription
        $wpdb->replace(
            $table_name,
            array(
                'email' => $data['email'],
                'ip_address' => $data['ip_address'],
                'user_agent' => $data['user_agent'],
                'opt_in_method' => $data['opt_in_method'],
                'subscription_date' => $data['timestamp'],
                'status' => 'active'
            ),
            array('%s', '%s', '%s', '%s', '%s', '%s')
        );
    }
}

// Initialize security features
new RTS_Security();

/**
 * Additional security utilities
 */

/**
 * Secure file upload validation
 */
function rts_validate_file_upload($file) {
    $allowed_types = array('jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx');
    $file_extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    
    // Check file extension
    if (!in_array($file_extension, $allowed_types)) {
        return new WP_Error('invalid_file_type', __('File type not allowed.', 'retail-trade-scanner'));
    }
    
    // Check file size (5MB max)
    if ($file['size'] > 5 * 1024 * 1024) {
        return new WP_Error('file_too_large', __('File size exceeds 5MB limit.', 'retail-trade-scanner'));
    }
    
    // Check MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    $allowed_mimes = array(
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
    
    if (!in_array($mime_type, $allowed_mimes)) {
        return new WP_Error('invalid_mime_type', __('File MIME type not allowed.', 'retail-trade-scanner'));
    }
    
    return true;
}

/**
 * Sanitize user input with context
 */
function rts_sanitize_input($input, $context = 'text') {
    switch ($context) {
        case 'email':
            return sanitize_email($input);
        case 'url':
            return esc_url_raw($input);
        case 'html':
            return wp_kses_post($input);
        case 'textarea':
            return sanitize_textarea_field($input);
        case 'key':
            return sanitize_key($input);
        case 'slug':
            return sanitize_title($input);
        case 'text':
        default:
            return sanitize_text_field($input);
    }
}

/**
 * Generate secure random token
 */
function rts_generate_secure_token($length = 32) {
    if (function_exists('random_bytes')) {
        return bin2hex(random_bytes($length / 2));
    } elseif (function_exists('openssl_random_pseudo_bytes')) {
        return bin2hex(openssl_random_pseudo_bytes($length / 2));
    } else {
        return wp_generate_password($length, false);
    }
}

/**
 * Constant-time string comparison
 */
function rts_hash_equals($known_string, $user_string) {
    if (function_exists('hash_equals')) {
        return hash_equals($known_string, $user_string);
    }
    
    if (strlen($known_string) !== strlen($user_string)) {
        return false;
    }
    
    $result = 0;
    for ($i = 0; $i < strlen($known_string); $i++) {
        $result |= ord($known_string[$i]) ^ ord($user_string[$i]);
    }
    
    return $result === 0;
}