<?php
/**
 * Security Functions for Production
 * @package RetailTradeScanner
 */

if (!defined('ABSPATH')) { exit; }

/**
 * Enhanced security measures for production
 */
class RTS_Security {
    
    public function __construct() {
        add_action('init', [$this, 'init_security']);
        add_action('wp_enqueue_scripts', [$this, 'add_security_headers']);
        add_filter('wp_headers', [$this, 'add_security_headers_filter']);
        add_action('wp_head', [$this, 'add_security_meta_tags']);
    }
    
    /**
     * Initialize security measures
     */
    public function init_security() {
        // Remove WordPress version from head and feeds
        remove_action('wp_head', 'wp_generator');
        add_filter('the_generator', '__return_empty_string');
        
        // Remove RSD link
        remove_action('wp_head', 'rsd_link');
        
        // Remove wlwmanifest link
        remove_action('wp_head', 'wlwmanifest_link');
        
        // Remove shortlink
        remove_action('wp_head', 'wp_shortlink_wp_head');
        
        // Disable XML-RPC if not needed
        if (!defined('RTS_ENABLE_XMLRPC') || !RTS_ENABLE_XMLRPC) {
            add_filter('xmlrpc_enabled', '__return_false');
        }
        
        // Remove admin bar for non-admins
        if (!current_user_can('administrator')) {
            show_admin_bar(false);
        }
        
        // Prevent information disclosure
        add_filter('login_errors', [$this, 'generic_login_errors']);
        
        // Secure file uploads
        add_filter('upload_mimes', [$this, 'secure_upload_mimes']);
        add_filter('wp_handle_upload_prefilter', [$this, 'secure_file_upload']);
    }
    
    /**
     * Add security headers via wp_enqueue_scripts
     */
    public function add_security_headers() {
        if (!is_admin()) {
            // Content Security Policy
            $csp = "default-src 'self'; ";
            $csp .= "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://www.google-analytics.com https://www.googletagmanager.com; ";
            $csp .= "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; ";
            $csp .= "font-src 'self' https://fonts.gstatic.com; ";
            $csp .= "img-src 'self' data: https:; ";
            $csp .= "connect-src 'self' https://www.google-analytics.com; ";
            $csp .= "frame-ancestors 'self';";
            
            header("Content-Security-Policy: " . $csp);
        }
    }
    
    /**
     * Add security headers via wp_headers filter
     */
    public function add_security_headers_filter($headers) {
        if (!is_admin()) {
            $headers['X-Content-Type-Options'] = 'nosniff';
            $headers['X-Frame-Options'] = 'SAMEORIGIN';
            $headers['X-XSS-Protection'] = '1; mode=block';
            $headers['Referrer-Policy'] = 'strict-origin-when-cross-origin';
            $headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()';
        }
        return $headers;
    }
    
    /**
     * Add security meta tags
     */
    public function add_security_meta_tags() {
        if (!is_admin()) {
            echo '<meta name="referrer" content="strict-origin-when-cross-origin">' . "\n";
            echo '<meta http-equiv="X-Content-Type-Options" content="nosniff">' . "\n";
        }
    }
    
    /**
     * Generic login error messages
     */
    public function generic_login_errors($error) {
        return __('Invalid login credentials.', 'retail-trade-scanner');
    }
    
    /**
     * Secure file upload types
     */
    public function secure_upload_mimes($mimes) {
        // Remove potentially dangerous file types
        unset($mimes['exe'], $mimes['bat'], $mimes['cmd'], $mimes['com'], $mimes['pif'], $mimes['scr'], $mimes['vbs'], $mimes['jsp']);
        
        // Add safe types if needed
        $mimes['webp'] = 'image/webp';
        $mimes['svg'] = 'image/svg+xml';
        
        return $mimes;
    }
    
    /**
     * Secure file upload validation
     */
    public function secure_file_upload($file) {
        // Check file size (limit to 10MB)
        if ($file['size'] > 10485760) {
            $file['error'] = __('File size exceeds 10MB limit.', 'retail-trade-scanner');
            return $file;
        }
        
        // Validate file extension
        $allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx'];
        $file_extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        
        if (!in_array($file_extension, $allowed_extensions)) {
            $file['error'] = __('File type not allowed.', 'retail-trade-scanner');
            return $file;
        }
        
        return $file;
    }
    
    /**
     * Sanitize input data
     */
    public static function sanitize_input($data, $type = 'text') {
        switch ($type) {
            case 'email':
                return sanitize_email($data);
            case 'url':
                return esc_url_raw($data);
            case 'int':
                return intval($data);
            case 'float':
                return floatval($data);
            case 'html':
                return wp_kses_post($data);
            case 'textarea':
                return sanitize_textarea_field($data);
            default:
                return sanitize_text_field($data);
        }
    }
    
    /**
     * Verify nonce for AJAX requests
     */
    public static function verify_nonce($nonce, $action = 'rts_nonce') {
        if (!wp_verify_nonce($nonce, $action)) {
            wp_die(__('Security check failed.', 'retail-trade-scanner'), 403);
        }
    }
}

// Initialize security
new RTS_Security();

/**
 * Newsletter subscription with security
 */
function rts_handle_newsletter_subscription() {
    // Verify nonce
    RTS_Security::verify_nonce($_POST['rts_subscribe_nonce'] ?? '', 'rts_subscribe');
    
    // Sanitize email
    $email = RTS_Security::sanitize_input($_POST['email'] ?? '', 'email');
    
    if (!is_email($email)) {
        wp_redirect(add_query_arg('subscribed', 'error', wp_get_referer()));
        exit;
    }
    
    // Rate limiting
    $ip = $_SERVER['REMOTE_ADDR'];
    $transient_key = 'rts_subscribe_' . md5($ip);
    
    if (get_transient($transient_key)) {
        wp_redirect(add_query_arg('subscribed', 'rate_limit', wp_get_referer()));
        exit;
    }
    
    // Set rate limit (1 subscription per hour per IP)
    set_transient($transient_key, true, HOUR_IN_SECONDS);
    
    // Store subscription (implement your email service integration here)
    $subscribers = get_option('rts_subscribers', []);
    if (!in_array($email, $subscribers)) {
        $subscribers[] = $email;
        update_option('rts_subscribers', $subscribers);
    }
    
    // Log the subscription
    error_log('RTS Newsletter Subscription: ' . $email . ' from IP: ' . $ip);
    
    wp_redirect(add_query_arg('subscribed', '1', wp_get_referer()));
    exit;
}
add_action('admin_post_rts_subscribe', 'rts_handle_newsletter_subscription');
add_action('admin_post_nopriv_rts_subscribe', 'rts_handle_newsletter_subscription');

/**
 * Honeypot field for forms (anti-spam)
 */
function rts_honeypot_field() {
    echo '<div style="position: absolute; left: -9999px; opacity: 0;">';
    echo '<label for="rts_honeypot">Leave this field empty</label>';
    echo '<input type="text" id="rts_honeypot" name="rts_honeypot" tabindex="-1" autocomplete="off">';
    echo '</div>';
}

/**
 * Check honeypot field
 */
function rts_check_honeypot() {
    if (!empty($_POST['rts_honeypot'])) {
        wp_die(__('Spam detected.', 'retail-trade-scanner'), 403);
    }
}