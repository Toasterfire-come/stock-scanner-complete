<?php
/**
 * API Integration Functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get API base URL
 */
function stock_scanner_get_api_url() {
    $api_url = get_option('stock_scanner_api_url', 'http://localhost:8000/api');
    return trailingslashit($api_url);
}

/**
 * Get API key for authentication
 */
function stock_scanner_get_api_key() {
    return get_option('stock_scanner_api_key', '');
}

/**
 * Make authenticated API request
 */
function stock_scanner_api_request($endpoint, $args = array()) {
    $api_url = stock_scanner_get_api_url();
    $api_key = stock_scanner_get_api_key();
    
    $url = $api_url . ltrim($endpoint, '/');
    
    $default_args = array(
        'timeout' => 30,
        'headers' => array(
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ),
    );
    
    // Add API key if available
    if (!empty($api_key)) {
        $default_args['headers']['Authorization'] = 'Bearer ' . $api_key;
    }
    
    $args = wp_parse_args($args, $default_args);
    
    // Check cache first
    $cache_key = 'stock_scanner_' . md5($url . serialize($args));
    $cache_timeout = get_option('stock_scanner_cache_timeout', 300);
    
    $cached_response = get_transient($cache_key);
    if (false !== $cached_response && !isset($args['bypass_cache'])) {
        return $cached_response;
    }
    
    // Make API request
    $response = wp_remote_request($url, $args);
    
    if (is_wp_error($response)) {
        error_log('Stock Scanner API Error: ' . $response->get_error_message());
        return array(
            'success' => false,
            'error' => $response->get_error_message(),
        );
    }
    
    $body = wp_remote_retrieve_body($response);
    $status_code = wp_remote_retrieve_response_code($response);
    
    if ($status_code !== 200) {
        error_log('Stock Scanner API HTTP Error: ' . $status_code . ' - ' . $body);
        return array(
            'success' => false,
            'error' => 'API request failed with status: ' . $status_code,
            'status_code' => $status_code,
        );
    }
    
    $data = json_decode($body, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        error_log('Stock Scanner API JSON Error: ' . json_last_error_msg());
        return array(
            'success' => false,
            'error' => 'Invalid JSON response from API',
        );
    }
    
    // Cache successful responses
    if (isset($data['success']) && $data['success']) {
        set_transient($cache_key, $data, $cache_timeout);
    }
    
    return $data;
}

/**
 * Get stock data for a specific ticker
 */
function stock_scanner_get_stock_data($ticker) {
    if (empty($ticker)) {
        return array(
            'success' => false,
            'error' => 'Ticker symbol is required',
        );
    }
    
    $ticker = sanitize_text_field(strtoupper($ticker));
    return stock_scanner_api_request('stock/' . $ticker . '/');
}

/**
 * Search stocks
 */
function stock_scanner_search_stocks($query, $limit = 50) {
    if (empty($query)) {
        return array(
            'success' => false,
            'error' => 'Search query is required',
        );
    }
    
    $query = sanitize_text_field($query);
    $limit = intval($limit);
    
    return stock_scanner_api_request('search/?q=' . urlencode($query) . '&limit=' . $limit);
}

/**
 * Get market overview data
 */
function stock_scanner_get_market_overview() {
    return stock_scanner_api_request('market-stats/');
}

/**
 * Get trending stocks
 */
function stock_scanner_get_trending_stocks($limit = 20) {
    $limit = intval($limit);
    return stock_scanner_api_request('trending/?limit=' . $limit);
}

/**
 * Get stock list with filtering
 */
function stock_scanner_get_stock_list($filters = array()) {
    $default_filters = array(
        'limit' => 50,
        'category' => '',
        'min_price' => '',
        'max_price' => '',
        'min_volume' => '',
        'exchange' => '',
        'sort_by' => 'last_updated',
        'sort_order' => 'desc',
    );
    
    $filters = wp_parse_args($filters, $default_filters);
    $query_params = array();
    
    foreach ($filters as $key => $value) {
        if (!empty($value)) {
            $query_params[] = urlencode($key) . '=' . urlencode($value);
        }
    }
    
    $query_string = !empty($query_params) ? '?' . implode('&', $query_params) : '';
    
    return stock_scanner_api_request('stocks/' . $query_string);
}

/**
 * Get user portfolio data
 */
function stock_scanner_get_user_portfolio($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'success' => false,
            'error' => 'User not authenticated',
        );
    }
    
    return stock_scanner_api_request('portfolio/', array(
        'method' => 'GET',
        'headers' => array(
            'X-User-ID' => $user_id,
        ),
    ));
}

/**
 * Get user watchlist data
 */
function stock_scanner_get_user_watchlist($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'success' => false,
            'error' => 'User not authenticated',
        );
    }
    
    return stock_scanner_api_request('watchlist/', array(
        'method' => 'GET',
        'headers' => array(
            'X-User-ID' => $user_id,
        ),
    ));
}

/**
 * Create stock alert
 */
function stock_scanner_create_stock_alert($ticker, $target_price, $condition, $user_email) {
    if (empty($ticker) || empty($target_price) || empty($condition) || empty($user_email)) {
        return array(
            'success' => false,
            'error' => 'All fields are required',
        );
    }
    
    $data = array(
        'ticker' => sanitize_text_field(strtoupper($ticker)),
        'target_price' => floatval($target_price),
        'condition' => sanitize_text_field($condition),
        'email' => sanitize_email($user_email),
    );
    
    return stock_scanner_api_request('alerts/create/', array(
        'method' => 'POST',
        'body' => json_encode($data),
    ));
}

/**
 * Subscribe to email notifications
 */
function stock_scanner_subscribe_email($email, $category = '') {
    if (empty($email) || !is_email($email)) {
        return array(
            'success' => false,
            'error' => 'Valid email address is required',
        );
    }
    
    $data = array(
        'email' => sanitize_email($email),
        'category' => sanitize_text_field($category),
    );
    
    return stock_scanner_api_request('subscription/', array(
        'method' => 'POST',
        'body' => json_encode($data),
    ));
}

/**
 * Get stock news
 */
function stock_scanner_get_stock_news($ticker = '', $limit = 20) {
    $limit = intval($limit);
    $query_params = array('limit' => $limit);
    
    if (!empty($ticker)) {
        $query_params['ticker'] = sanitize_text_field(strtoupper($ticker));
    }
    
    $query_string = '?' . http_build_query($query_params);
    
    return stock_scanner_api_request('news/' . $query_string);
}

/**
 * Get personalized news for user
 */
function stock_scanner_get_personalized_news($user_id = null, $limit = 20) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return stock_scanner_get_stock_news('', $limit); // Fallback to general news
    }
    
    $limit = intval($limit);
    
    return stock_scanner_api_request('news/personalized/?limit=' . $limit, array(
        'headers' => array(
            'X-User-ID' => $user_id,
        ),
    ));
}

/**
 * Clear API cache
 */
function stock_scanner_clear_api_cache() {
    global $wpdb;
    
    $wpdb->query(
        "DELETE FROM {$wpdb->options} 
         WHERE option_name LIKE '_transient_stock_scanner_%' 
         OR option_name LIKE '_transient_timeout_stock_scanner_%'"
    );
    
    return true;
}

/**
 * Get API health status
 */
function stock_scanner_get_api_health() {
    $health_check = stock_scanner_api_request('health/', array(
        'bypass_cache' => true,
        'timeout' => 10,
    ));
    
    if (!isset($health_check['success']) || !$health_check['success']) {
        return array(
            'status' => 'down',
            'message' => isset($health_check['error']) ? $health_check['error'] : 'API is not responding',
            'timestamp' => current_time('mysql'),
        );
    }
    
    return array(
        'status' => 'up',
        'message' => 'API is running normally',
        'timestamp' => current_time('mysql'),
        'data' => $health_check,
    );
}

/**
 * Format currency values
 */
function stock_scanner_format_currency($value, $decimals = 2) {
    if (!is_numeric($value)) {
        return '$0.00';
    }
    
    return '$' . number_format(floatval($value), $decimals);
}

/**
 * Format percentage values
 */
function stock_scanner_format_percentage($value, $decimals = 2, $show_sign = true) {
    if (!is_numeric($value)) {
        return '0.00%';
    }
    
    $formatted = number_format(floatval($value), $decimals) . '%';
    
    if ($show_sign && $value > 0) {
        $formatted = '+' . $formatted;
    }
    
    return $formatted;
}

/**
 * Get price change class for styling
 */
function stock_scanner_get_price_change_class($change) {
    if (!is_numeric($change)) {
        return 'price-neutral';
    }
    
    $change = floatval($change);
    
    if ($change > 0) {
        return 'price-positive text-success';
    } elseif ($change < 0) {
        return 'price-negative text-danger';
    } else {
        return 'price-neutral text-muted';
    }
}

/**
 * Sanitize API data for output
 */
function stock_scanner_sanitize_api_data($data) {
    if (is_array($data)) {
        return array_map('stock_scanner_sanitize_api_data', $data);
    } elseif (is_string($data)) {
        return sanitize_text_field($data);
    } elseif (is_numeric($data)) {
        return $data;
    } else {
        return $data;
    }
}

/**
 * AJAX handler for real-time stock data
 */
function stock_scanner_ajax_realtime_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $tickers = isset($_POST['tickers']) ? sanitize_text_field($_POST['tickers']) : '';
    
    if (empty($tickers)) {
        wp_send_json_error('No tickers specified');
        return;
    }
    
    $ticker_array = array_map('trim', array_map('strtoupper', explode(',', $tickers)));
    $results = array();
    
    foreach ($ticker_array as $ticker) {
        if (!empty($ticker)) {
            $stock_data = stock_scanner_get_stock_data($ticker);
            if (isset($stock_data['success']) && $stock_data['success']) {
                $results[$ticker] = $stock_data['data'];
            }
        }
    }
    
    wp_send_json_success($results);
}
add_action('wp_ajax_stock_scanner_realtime_data', 'stock_scanner_ajax_realtime_data');
add_action('wp_ajax_nopriv_stock_scanner_realtime_data', 'stock_scanner_ajax_realtime_data');

/**
 * AJAX handler for newsletter signup
 */
function stock_scanner_ajax_newsletter_signup() {
    check_ajax_referer('newsletter_signup', 'newsletter_nonce');
    
    $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
    
    if (empty($email) || !is_email($email)) {
        wp_send_json_error('Valid email address is required');
        return;
    }
    
    $result = stock_scanner_subscribe_email($email);
    
    if (isset($result['success']) && $result['success']) {
        wp_send_json_success('Successfully subscribed to newsletter');
    } else {
        $error_message = isset($result['error']) ? $result['error'] : 'Failed to subscribe';
        wp_send_json_error($error_message);
    }
}
add_action('wp_ajax_newsletter_signup', 'stock_scanner_ajax_newsletter_signup');
add_action('wp_ajax_nopriv_newsletter_signup', 'stock_scanner_ajax_newsletter_signup');