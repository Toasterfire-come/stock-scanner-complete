<?php
/**
 * Security and validation functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Validate and sanitize stock ticker
 */
function stock_scanner_validate_ticker($ticker) {
    if (empty($ticker)) {
        return false;
    }
    
    // Remove whitespace and convert to uppercase
    $ticker = strtoupper(trim(sanitize_text_field($ticker)));
    
    // Validate format: 1-5 letters only
    if (!preg_match('/^[A-Z]{1,5}$/', $ticker)) {
        return false;
    }
    
    // Additional validation against known malicious patterns
    $blacklisted_patterns = array('SCRIPT', 'ALERT', 'EVAL', 'EXEC');
    if (in_array($ticker, $blacklisted_patterns)) {
        return false;
    }
    
    return $ticker;
}

/**
 * Validate price value
 */
function stock_scanner_validate_price($price) {
    if (empty($price) && $price !== '0') {
        return false;
    }
    
    // Remove any non-numeric characters except decimal point
    $price = preg_replace('/[^0-9.]/', '', $price);
    
    if (!is_numeric($price)) {
        return false;
    }
    
    $price = floatval($price);
    
    // Validate reasonable price range (0.01 to 10,000)
    if ($price < 0.01 || $price > 10000) {
        return false;
    }
    
    return $price;
}

/**
 * Validate percentage value
 */
function stock_scanner_validate_percentage($percentage) {
    if (empty($percentage) && $percentage !== '0') {
        return false;
    }
    
    // Remove any non-numeric characters except decimal point and minus sign
    $percentage = preg_replace('/[^0-9.-]/', '', $percentage);
    
    if (!is_numeric($percentage)) {
        return false;
    }
    
    $percentage = floatval($percentage);
    
    // Validate reasonable percentage range (-100% to 1000%)
    if ($percentage < -100 || $percentage > 1000) {
        return false;
    }
    
    return $percentage;
}

/**
 * Validate email for notifications
 */
function stock_scanner_validate_notification_email($email) {
    if (empty($email)) {
        return false;
    }
    
    $email = sanitize_email($email);
    
    if (!is_email($email)) {
        return false;
    }
    
    // Check against disposable email providers
    $disposable_domains = array(
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email', 'temp-mail.org'
    );
    
    $domain = substr(strrchr($email, "@"), 1);
    if (in_array(strtolower($domain), $disposable_domains)) {
        return false;
    }
    
    return $email;
}

/**
 * Rate limit API requests
 */
function stock_scanner_check_rate_limit($action, $user_id = null, $limit = 60) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    // Use IP address for non-logged-in users
    if (!$user_id) {
        $identifier = $_SERVER['REMOTE_ADDR'];
    } else {
        $identifier = 'user_' . $user_id;
    }
    
    $cache_key = "rate_limit_{$action}_{$identifier}";
    $current_count = get_transient($cache_key);
    
    if ($current_count === false) {
        set_transient($cache_key, 1, HOUR_IN_SECONDS);
        return true;
    }
    
    if ($current_count >= $limit) {
        return false;
    }
    
    set_transient($cache_key, $current_count + 1, HOUR_IN_SECONDS);
    return true;
}

/**
 * Sanitize API request data
 */
function stock_scanner_sanitize_request_data($data) {
    if (is_array($data)) {
        return array_map('stock_scanner_sanitize_request_data', $data);
    }
    
    if (is_string($data)) {
        // Remove potential XSS vectors
        $data = strip_tags($data);
        $data = sanitize_text_field($data);
        
        // Additional cleaning for specific patterns
        $data = preg_replace('/[<>"\']/', '', $data);
        
        return $data;
    }
    
    return $data;
}

/**
 * Validate AJAX nonce with rate limiting
 */
function stock_scanner_validate_ajax_request($action) {
    // Check nonce
    if (!check_ajax_referer('stock_scanner_nonce', 'nonce', false)) {
        wp_send_json_error('Invalid security token', 403);
        return false;
    }
    
    // Check rate limit
    if (!stock_scanner_check_rate_limit($action)) {
        wp_send_json_error('Too many requests. Please try again later.', 429);
        return false;
    }
    
    return true;
}

/**
 * Log security events
 */
function stock_scanner_log_security_event($event, $details = array()) {
    $log_entry = array(
        'timestamp' => current_time('mysql'),
        'event' => sanitize_text_field($event),
        'details' => is_array($details) ? $details : array(),
        'ip_address' => $_SERVER['REMOTE_ADDR'],
        'user_agent' => $_SERVER['HTTP_USER_AGENT'],
        'user_id' => get_current_user_id(),
        'request_uri' => $_SERVER['REQUEST_URI'],
    );
    
    // Log to WordPress error log
    error_log('Stock Scanner Security Event: ' . json_encode($log_entry));
    
    // Store in database for admin review
    $security_log = get_option('stock_scanner_security_log', array());
    array_unshift($security_log, $log_entry);
    
    // Keep only last 1000 entries
    $security_log = array_slice($security_log, 0, 1000);
    
    update_option('stock_scanner_security_log', $security_log);
}

/**
 * Check for suspicious activity
 */
function stock_scanner_detect_suspicious_activity($request_data) {
    $suspicious_patterns = array(
        // SQL Injection patterns
        '/(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)/i',
        // XSS patterns
        '/<script|javascript:|vbscript:|onload=|onerror=/i',
        // Path traversal
        '/\.\.\/|\.\.\\\\/',
        // Command injection
        '/[;&|`$()]/',
    );
    
    $request_string = json_encode($request_data);
    
    foreach ($suspicious_patterns as $pattern) {
        if (preg_match($pattern, $request_string)) {
            stock_scanner_log_security_event('suspicious_request', array(
                'pattern' => $pattern,
                'data' => $request_data,
            ));
            return true;
        }
    }
    
    return false;
}

/**
 * Secure file upload validation
 */
function stock_scanner_validate_file_upload($file) {
    if (!is_array($file) || !isset($file['tmp_name'])) {
        return array('error' => 'Invalid file upload');
    }
    
    // Check file size (max 5MB)
    if ($file['size'] > 5 * 1024 * 1024) {
        return array('error' => 'File too large (max 5MB)');
    }
    
    // Validate file extension
    $allowed_extensions = array('jpg', 'jpeg', 'png', 'gif', 'pdf', 'csv', 'xlsx');
    $file_extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    
    if (!in_array($file_extension, $allowed_extensions)) {
        return array('error' => 'File type not allowed');
    }
    
    // Validate MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    $allowed_mime_types = array(
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    
    if (!in_array($mime_type, $allowed_mime_types)) {
        return array('error' => 'Invalid file type detected');
    }
    
    return array('success' => true, 'file' => $file);
}

/**
 * Generate secure token
 */
function stock_scanner_generate_secure_token($length = 32) {
    return wp_generate_password($length, false, false);
}

/**
 * Encrypt sensitive data
 */
function stock_scanner_encrypt_data($data, $key = null) {
    if (!$key) {
        $key = defined('AUTH_KEY') ? AUTH_KEY : 'default_key';
    }
    
    $method = 'AES-256-CBC';
    $iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length($method));
    $encrypted = openssl_encrypt($data, $method, $key, 0, $iv);
    
    return base64_encode($iv . $encrypted);
}

/**
 * Decrypt sensitive data
 */
function stock_scanner_decrypt_data($encrypted_data, $key = null) {
    if (!$key) {
        $key = defined('AUTH_KEY') ? AUTH_KEY : 'default_key';
    }
    
    $data = base64_decode($encrypted_data);
    $method = 'AES-256-CBC';
    $iv_length = openssl_cipher_iv_length($method);
    $iv = substr($data, 0, $iv_length);
    $encrypted = substr($data, $iv_length);
    
    return openssl_decrypt($encrypted, $method, $key, 0, $iv);
}

/**
 * Clean and validate search queries
 */
function stock_scanner_sanitize_search_query($query) {
    if (empty($query)) {
        return '';
    }
    
    // Remove potential XSS and injection attempts
    $query = strip_tags($query);
    $query = preg_replace('/[<>"\']/', '', $query);
    
    // Limit length
    $query = substr($query, 0, 100);
    
    // Remove excessive whitespace
    $query = preg_replace('/\s+/', ' ', trim($query));
    
    return sanitize_text_field($query);
}

/**
 * Validate user permissions for actions
 */
function stock_scanner_check_user_permissions($action, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $user = get_user_by('ID', $user_id);
    if (!$user) {
        return false;
    }
    
    // Define action permissions
    $permissions = array(
        'manage_portfolio' => array('subscriber', 'contributor', 'author', 'editor', 'administrator'),
        'create_alerts' => array('subscriber', 'contributor', 'author', 'editor', 'administrator'),
        'export_data' => array('contributor', 'author', 'editor', 'administrator'),
        'api_access' => array('author', 'editor', 'administrator'),
        'admin_access' => array('administrator'),
    );
    
    if (!isset($permissions[$action])) {
        return false;
    }
    
    $user_roles = $user->roles;
    $required_roles = $permissions[$action];
    
    return !empty(array_intersect($user_roles, $required_roles));
}

/**
 * Sanitize output for display
 */
function stock_scanner_safe_output($data, $context = 'html') {
    switch ($context) {
        case 'html':
            return wp_kses_post($data);
        
        case 'attribute':
            return esc_attr($data);
        
        case 'url':
            return esc_url($data);
        
        case 'js':
            return wp_json_encode($data);
        
        case 'css':
            return esc_attr($data);
        
        default:
            return sanitize_text_field($data);
    }
}

/**
 * Content Security Policy header
 */
function stock_scanner_set_csp_header() {
    $csp = "default-src 'self'; ";
    $csp .= "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; ";
    $csp .= "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; ";
    $csp .= "font-src 'self' https://fonts.gstatic.com; ";
    $csp .= "img-src 'self' data: https:; ";
    $csp .= "connect-src 'self' " . stock_scanner_get_api_url() . "; ";
    $csp .= "frame-src 'none'; ";
    $csp .= "object-src 'none'; ";
    $csp .= "base-uri 'self'; ";
    
    if (!is_admin()) {
        header("Content-Security-Policy: " . $csp);
    }
}

// Apply CSP header on frontend
add_action('template_redirect', 'stock_scanner_set_csp_header');

/**
 * Disable XML-RPC if not needed
 */
if (!defined('STOCK_SCANNER_ENABLE_XMLRPC') || !STOCK_SCANNER_ENABLE_XMLRPC) {
    add_filter('xmlrpc_enabled', '__return_false');
}

/**
 * Hide WordPress version
 */
function stock_scanner_remove_wp_version() {
    return '';
}
add_filter('the_generator', 'stock_scanner_remove_wp_version');

/**
 * Disable file editing in admin
 */
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}