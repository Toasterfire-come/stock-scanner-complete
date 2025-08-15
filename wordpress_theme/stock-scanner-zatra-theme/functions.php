<?php
/**
 * Stock Scanner Pro - Zatra Edition Functions
 * Professional WordPress theme with Django backend integration
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme setup
 */
function stock_scanner_zatra_setup() {
    // Add theme support for various features
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('automatic-feed-links');
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');
    add_theme_support('wp-block-styles');
    add_theme_support('editor-styles');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner-zatra'),
        'footer' => __('Footer Menu', 'stock-scanner-zatra'),
        'mobile' => __('Mobile Menu', 'stock-scanner-zatra'),
    ));
    
    // Set content width for responsive images
    $GLOBALS['content_width'] = 1200;
}
add_action('after_setup_theme', 'stock_scanner_zatra_setup');

/**
 * Enqueue scripts and styles
 */
function stock_scanner_zatra_scripts() {
    // Theme stylesheet
    wp_enqueue_style('stock-scanner-zatra-style', get_stylesheet_uri(), array(), '1.0.0');
    
    // Font Awesome (local)
    wp_enqueue_style(
        'font-awesome-6',
        get_template_directory_uri() . '/assets/framework/Font-Awesome-6/css/all.min.css',
        array(),
        '6.5.0'
    );
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Main theme JavaScript
    wp_enqueue_script('stock-scanner-zatra-js', get_template_directory_uri() . '/assets/js/theme.js', array('jquery'), '1.0.0', true);
    
    // Advanced AI Assistant
    wp_enqueue_script('stock-scanner-ai-assistant', get_template_directory_uri() . '/assets/js/ai-assistant.js', array('jquery'), '1.0.0', true);
    
    // Advanced Charts System
    wp_enqueue_script('stock-scanner-advanced-charts', get_template_directory_uri() . '/assets/js/advanced-charts.js', array('chart-js'), '1.0.0', true);
    
    // Localize script with AJAX URL and nonce
    wp_localize_script('stock-scanner-zatra-js', 'stockScannerAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'theme_url' => get_template_directory_uri()
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_zatra_scripts');

/**
 * Register block pattern category
 */
function stock_scanner_zatra_block_pattern_category() {
    register_block_pattern_category(
        'stock-scanner-zatra',
        array('label' => __('Stock Scanner Zatra', 'stock-scanner-zatra'))
    );
}
add_action('init', 'stock_scanner_zatra_block_pattern_category');

// =============================================================================
// BACKEND API INTEGRATION (Copied from previous theme)
// =============================================================================

/**
 * Get backend API URL
 */
function get_backend_api_url($endpoint = '') {
    $api_settings = get_option('stock_scanner_api_settings', array());
    $backend_url = $api_settings['backend_url'] ?? 'http://localhost:8000';
    
    if (empty($backend_url)) {
        $backend_url = 'http://localhost:8000';
    }
    
    return rtrim($backend_url, '/') . '/api/' . ltrim($endpoint, '/');
}

/**
 * Make authenticated API request to Django backend
 */
function make_backend_api_request($endpoint, $data = array(), $method = 'GET') {
    $api_settings = get_option('stock_scanner_api_settings', array());
    $backend_url = $api_settings['backend_url'] ?? '';
    
    // Check if backend URL is configured
    if (empty($backend_url)) {
        return new WP_Error('no_backend_url', 'Backend URL not configured. Please configure it in Settings > Stock Scanner.');
    }
    
    $api_url = get_backend_api_url($endpoint);
    $api_key = $api_settings['api_key'] ?? '';
    $timeout = $api_settings['timeout'] ?? 30;
    
    if (!$api_url) {
        return new WP_Error('invalid_api_url', 'Invalid API URL constructed');
    }
    
    $args = array(
        'method' => $method,
        'timeout' => $timeout,
        'headers' => array(
            'Content-Type' => 'application/json',
        )
    );
    
    if (!empty($api_key)) {
        $args['headers']['Authorization'] = 'Bearer ' . $api_key;
    }
    
    if ($method === 'POST' || $method === 'PUT') {
        $args['body'] = json_encode($data);
    } elseif ($method === 'GET' && !empty($data)) {
        $api_url .= '?' . http_build_query($data);
    }
    
    // Log the API request for debugging
    if (defined('WP_DEBUG') && WP_DEBUG) {
        error_log("Stock Scanner API Request: $method $api_url");
        if (!empty($data)) {
            error_log("Stock Scanner API Data: " . json_encode($data));
        }
    }
    
    $response = wp_remote_request($api_url, $args);
    
    if (is_wp_error($response)) {
        // Log the error for debugging
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log("Stock Scanner API Error: " . $response->get_error_message());
        }
        return $response;
    }
    
    $status_code = wp_remote_retrieve_response_code($response);
    $body = wp_remote_retrieve_body($response);
    
    // Log the response for debugging
    if (defined('WP_DEBUG') && WP_DEBUG) {
        error_log("Stock Scanner API Response: Status $status_code, Body: " . substr($body, 0, 200) . "...");
    }
    
    if ($status_code >= 400) {
        $error_message = "API request failed with status $status_code";
        if (!empty($body)) {
            $decoded_body = json_decode($body, true);
            if (isset($decoded_body['error'])) {
                $error_message .= ": " . $decoded_body['error'];
            } elseif (isset($decoded_body['message'])) {
                $error_message .= ": " . $decoded_body['message'];
            } else {
                $error_message .= ": " . $body;
            }
        }
        return new WP_Error('api_error', $error_message);
    }
    
    $decoded_response = json_decode($body, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        return new WP_Error('json_decode_error', 'Invalid JSON response from backend: ' . json_last_error_msg());
    }
    
    return $decoded_response;
}

// =============================================================================
// USER AUTHENTICATION AND SUBSCRIPTION HELPERS
// =============================================================================

/**
 * Check if user is authenticated
 */
function is_user_authenticated() {
    return is_user_logged_in();
}

/**
 * Get user subscription status
 */
function get_user_subscription_status($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return 'guest';
    }
    
    // Get subscription status from user meta or API
    $subscription_status = get_user_meta($user_id, 'subscription_status', true);
    
    if (empty($subscription_status)) {
        $subscription_status = 'free';
    }
    
    return $subscription_status; // 'free', 'pro', 'enterprise'
}

/**
 * Check if user has premium access
 */
function user_has_premium_access($user_id = null) {
    $status = get_user_subscription_status($user_id);
    return in_array($status, ['pro', 'enterprise']);
}

/**
 * Require authentication for page access
 */
function require_authentication() {
    if (!is_user_logged_in()) {
        wp_redirect(wp_login_url(get_permalink()));
        exit;
    }
}

/**
 * Get stock data from backend
 */
function get_stock_data($symbol) {
    return make_backend_api_request('stocks/' . urlencode($symbol));
}

/**
 * Get market overview data
 */
function get_market_overview() {
    return make_backend_api_request('market/overview');
}

/**
 * Get user watchlist
 */
function get_user_watchlist($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    return make_backend_api_request('watchlist/' . $user_id);
}

/**
 * Add custom body classes based on user status
 */
function stock_scanner_zatra_body_classes($classes) {
    if (is_user_logged_in()) {
        $classes[] = 'logged-in-user';
        $subscription_status = get_user_subscription_status();
        $classes[] = 'subscription-' . $subscription_status;
        
        if (user_has_premium_access()) {
            $classes[] = 'premium-user';
        }
    } else {
        $classes[] = 'guest-user';
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_zatra_body_classes');

// Add a global theme marker class for styling hooks
add_filter('body_class', function($classes) {
    $classes[] = 'theme-zatra';
    return $classes;
});

/**
 * Template redirect for protected pages
 */
function stock_scanner_zatra_template_redirect() {
    // List of pages that require authentication
    $protected_pages = array('dashboard', 'portfolio', 'account', 'billing-history', 'user-settings', 'watchlist');
    
    if (is_page($protected_pages) && !is_user_logged_in()) {
        wp_redirect(wp_login_url(get_permalink()));
        exit;
    }
}
add_action('template_redirect', 'stock_scanner_zatra_template_redirect');

// Redirect signed-in users visiting the Home page to the Dashboard (avoid self-redirect loops)
add_action('template_redirect', function() {
    if (!is_user_logged_in()) {
        return;
    }
    if (!(is_front_page() || is_page('home'))) {
        return;
    }
    $dashboard = get_page_by_path('dashboard');
    if (!$dashboard) {
        return;
    }
    $dashboard_url = get_permalink($dashboard->ID);
    // If already on Dashboard or Dashboard is the static front page, do not redirect
    if (is_page($dashboard->ID) || ((int) get_option('page_on_front') === (int) $dashboard->ID)) {
        return;
    }
    wp_safe_redirect($dashboard_url, 302);
    exit;
});

// =============================================================================
// WORDPRESS REST API ENDPOINTS FOR FRONTEND CONNECTIVITY
// =============================================================================

/**
 * Register custom REST API endpoints
 */
function stock_scanner_register_rest_endpoints() {
    // Stock data endpoint
    register_rest_route('stock-scanner/v1', '/stock-data/(?P<symbol>[a-zA-Z0-9]+)', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_stock_data_endpoint',
        'permission_callback' => '__return_true',
        'args' => array(
            'symbol' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param) && preg_match('/^[a-zA-Z0-9]+$/', $param);
                }
            )
        )
    ));

    // Historical data endpoint
    register_rest_route('stock-scanner/v1', '/historical-data/(?P<symbol>[a-zA-Z0-9]+)', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_historical_data_endpoint',
        'permission_callback' => '__return_true',
        'args' => array(
            'symbol' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param) && preg_match('/^[a-zA-Z0-9]+$/', $param);
                }
            ),
            'range' => array(
                'required' => false,
                'default' => '1W',
                'validate_callback' => function($param, $request, $key) {
                    return in_array($param, ['1D', '1W', '1M', '3M', '1Y', '5Y']);
                }
            )
        )
    ));

    // Real-time data endpoint
    register_rest_route('stock-scanner/v1', '/realtime-data/(?P<symbol>[a-zA-Z0-9]+)', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_realtime_data_endpoint',
        'permission_callback' => '__return_true',
        'args' => array(
            'symbol' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param) && preg_match('/^[a-zA-Z0-9]+$/', $param);
                }
            )
        )
    ));

    // Market data endpoint
    register_rest_route('stock-scanner/v1', '/market-data', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_market_data_endpoint',
        'permission_callback' => '__return_true'
    ));

    // User watchlist endpoint
    register_rest_route('stock-scanner/v1', '/watchlist', array(
        array(
            'methods' => 'GET',
            'callback' => 'stock_scanner_get_watchlist_endpoint',
            'permission_callback' => 'is_user_logged_in'
        ),
        array(
            'methods' => 'POST',
            'callback' => 'stock_scanner_add_to_watchlist_endpoint',
            'permission_callback' => 'is_user_logged_in',
            'args' => array(
                'symbol' => array(
                    'required' => true,
                    'validate_callback' => function($param, $request, $key) {
                        return is_string($param) && preg_match('/^[a-zA-Z0-9]+$/', $param);
                    }
                )
            )
        ),
        array(
            'methods' => 'DELETE',
            'callback' => 'stock_scanner_remove_from_watchlist_endpoint',
            'permission_callback' => 'is_user_logged_in',
            'args' => array(
                'symbol' => array(
                    'required' => true,
                    'validate_callback' => function($param, $request, $key) {
                        return is_string($param) && preg_match('/^[a-zA-Z0-9]+$/', $param);
                    }
                )
            )
        )
    ));

    // Portfolio endpoint
    register_rest_route('stock-scanner/v1', '/portfolio', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_portfolio_endpoint',
        'permission_callback' => 'is_user_logged_in'
    ));

    // News endpoint
    register_rest_route('stock-scanner/v1', '/news', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_news_endpoint',
        'permission_callback' => '__return_true',
        'args' => array(
            'category' => array(
                'required' => false,
                'default' => 'general'
            ),
            'limit' => array(
                'required' => false,
                'default' => 20,
                'validate_callback' => function($param, $request, $key) {
                    return is_numeric($param) && $param > 0 && $param <= 100;
                }
            )
        )
    ));
}
add_action('rest_api_init', 'stock_scanner_register_rest_endpoints');

/**
 * Stock data endpoint callback
 */
function stock_scanner_get_stock_data_endpoint($request) {
    $symbol = $request->get_param('symbol');
    
    // Try to get data from backend first
    $backend_data = get_stock_data($symbol);
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data if backend is unavailable
    $mock_data = generate_mock_stock_data($symbol);
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * Historical data endpoint callback
 */
function stock_scanner_get_historical_data_endpoint($request) {
    $symbol = $request->get_param('symbol');
    $range = $request->get_param('range');
    
    // Try to get data from backend first
    $backend_data = make_backend_api_request("historical/{$symbol}", array('range' => $range));
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data
    $mock_data = generate_mock_historical_data($symbol, $range);
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * Real-time data endpoint callback
 */
function stock_scanner_get_realtime_data_endpoint($request) {
    $symbol = $request->get_param('symbol');
    
    // Try to get data from backend first
    $backend_data = make_backend_api_request("realtime/{$symbol}");
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data
    $mock_data = generate_mock_realtime_data($symbol);
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * Market data endpoint callback
 */
function stock_scanner_get_market_data_endpoint($request) {
    // Try to get data from backend first
    $backend_data = get_market_overview();
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data
    $mock_data = generate_mock_market_data();
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * Watchlist endpoints
 */
function stock_scanner_get_watchlist_endpoint($request) {
    $user_id = get_current_user_id();
    
    // Try to get data from backend first
    $backend_data = get_user_watchlist($user_id);
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to WordPress user meta
    $watchlist = get_user_meta($user_id, 'stock_watchlist', true);
    if (!$watchlist) {
        $watchlist = array();
    }
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $watchlist,
        'source' => 'wordpress',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

function stock_scanner_add_to_watchlist_endpoint($request) {
    $user_id = get_current_user_id();
    $symbol = $request->get_param('symbol');
    
    // Try to add to backend first
    $backend_result = make_backend_api_request("watchlist/{$user_id}", array('symbol' => $symbol), 'POST');
    
    if (!is_wp_error($backend_result) && $backend_result) {
        return rest_ensure_response(array(
            'success' => true,
            'message' => 'Added to watchlist',
            'source' => 'backend'
        ));
    }
    
    // Fallback to WordPress user meta
    $watchlist = get_user_meta($user_id, 'stock_watchlist', true);
    if (!$watchlist) {
        $watchlist = array();
    }
    
    if (!in_array($symbol, $watchlist)) {
        $watchlist[] = $symbol;
        update_user_meta($user_id, 'stock_watchlist', $watchlist);
    }
    
    return rest_ensure_response(array(
        'success' => true,
        'message' => 'Added to watchlist',
        'source' => 'wordpress',
        'backend_error' => is_wp_error($backend_result) ? $backend_result->get_error_message() : 'Backend unavailable'
    ));
}

function stock_scanner_remove_from_watchlist_endpoint($request) {
    $user_id = get_current_user_id();
    $symbol = $request->get_param('symbol');
    
    // Try to remove from backend first
    $backend_result = make_backend_api_request("watchlist/{$user_id}/{$symbol}", array(), 'DELETE');
    
    if (!is_wp_error($backend_result)) {
        return rest_ensure_response(array(
            'success' => true,
            'message' => 'Removed from watchlist',
            'source' => 'backend'
        ));
    }
    
    // Fallback to WordPress user meta
    $watchlist = get_user_meta($user_id, 'stock_watchlist', true);
    if (!$watchlist) {
        $watchlist = array();
    }
    
    $watchlist = array_diff($watchlist, array($symbol));
    update_user_meta($user_id, 'stock_watchlist', $watchlist);
    
    return rest_ensure_response(array(
        'success' => true,
        'message' => 'Removed from watchlist',
        'source' => 'wordpress',
        'backend_error' => is_wp_error($backend_result) ? $backend_result->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * Portfolio endpoint callback
 */
function stock_scanner_get_portfolio_endpoint($request) {
    $user_id = get_current_user_id();
    
    // Try to get data from backend first
    $backend_data = make_backend_api_request("portfolio/{$user_id}");
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data
    $mock_data = generate_mock_portfolio_data($user_id);
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

/**
 * News endpoint callback
 */
function stock_scanner_get_news_endpoint($request) {
    $category = $request->get_param('category');
    $limit = $request->get_param('limit');
    
    // Try to get data from backend first
    $backend_data = make_backend_api_request('news', array(
        'category' => $category,
        'limit' => $limit
    ));
    
    if (!is_wp_error($backend_data) && $backend_data) {
        return rest_ensure_response(array(
            'success' => true,
            'data' => $backend_data,
            'source' => 'backend'
        ));
    }
    
    // Fallback to mock data
    $mock_data = generate_mock_news_data($category, $limit);
    
    return rest_ensure_response(array(
        'success' => true,
        'data' => $mock_data,
        'source' => 'mock',
        'backend_error' => is_wp_error($backend_data) ? $backend_data->get_error_message() : 'Backend unavailable'
    ));
}

// =============================================================================
// MOCK DATA GENERATORS FOR FALLBACK WHEN BACKEND IS UNAVAILABLE
// =============================================================================

/**
 * Generate mock stock data
 */
function generate_mock_stock_data($symbol) {
    $base_price = 100 + (crc32($symbol) % 500);
    $change = (mt_rand(-500, 500) / 100);
    $current_price = $base_price + $change;
    
    return array(
        'symbol' => strtoupper($symbol),
        'name' => ucfirst(strtolower($symbol)) . ' Corporation',
        'price' => round($current_price, 2),
        'change' => round($change, 2),
        'change_percent' => round(($change / $base_price) * 100, 2),
        'volume' => mt_rand(1000000, 50000000),
        'market_cap' => round($current_price * mt_rand(100000000, 1000000000), 0),
        'pe_ratio' => round(mt_rand(10, 30) + (mt_rand(0, 99) / 100), 2),
        'high_52w' => round($current_price * (1 + mt_rand(10, 50) / 100), 2),
        'low_52w' => round($current_price * (1 - mt_rand(10, 50) / 100), 2),
        'timestamp' => time()
    );
}

/**
 * Generate mock historical data
 */
function generate_mock_historical_data($symbol, $range) {
    $days_map = array(
        '1D' => 1,
        '1W' => 7,
        '1M' => 30,
        '3M' => 90,
        '1Y' => 365,
        '5Y' => 1825
    );
    
    $days = $days_map[$range] ?? 30;
    $base_price = 100 + (crc32($symbol) % 500);
    
    $labels = array();
    $prices = array();
    $volumes = array();
    $current_price = $base_price;
    
    for ($i = $days; $i >= 0; $i--) {
        $date = date('Y-m-d', strtotime("-{$i} days"));
        $labels[] = $date;
        
        // Simulate price movement
        $volatility = 0.02;
        $change = (mt_rand(-100, 100) / 100) * $volatility * $current_price;
        $current_price += $change;
        $current_price = max($current_price, 1); // Prevent negative prices
        
        $prices[] = round($current_price, 2);
        $volumes[] = mt_rand(1000000, 10000000);
    }
    
    return array(
        'symbol' => strtoupper($symbol),
        'range' => $range,
        'labels' => $labels,
        'prices' => $prices,
        'volumes' => $volumes,
        'trend' => end($prices) > $prices[0] ? 1 : -1,
        'timestamp' => time()
    );
}

/**
 * Generate mock real-time data
 */
function generate_mock_realtime_data($symbol) {
    $base_data = generate_mock_stock_data($symbol);
    
    return array(
        'symbol' => $base_data['symbol'],
        'price' => $base_data['price'],
        'change' => $base_data['change'],
        'change_percent' => $base_data['change_percent'],
        'volume' => $base_data['volume'],
        'timestamp' => date('H:i:s'),
        'market_status' => 'open' // or 'closed', 'pre-market', 'after-hours'
    );
}

/**
 * Generate mock market data
 */
function generate_mock_market_data() {
    $indices = array(
        array(
            'symbol' => 'SPY',
            'name' => 'S&P 500',
            'price' => 450.25,
            'change' => 2.15,
            'change_percent' => 0.48
        ),
        array(
            'symbol' => 'QQQ',
            'name' => 'NASDAQ 100',
            'price' => 375.80,
            'change' => -1.25,
            'change_percent' => -0.33
        ),
        array(
            'symbol' => 'DIA',
            'name' => 'Dow Jones',
            'price' => 340.15,
            'change' => 0.85,
            'change_percent' => 0.25
        )
    );
    
    return array(
        'indices' => $indices,
        'market_status' => 'open',
        'last_updated' => time(),
        'advancing' => mt_rand(1500, 2500),
        'declining' => mt_rand(1000, 2000),
        'unchanged' => mt_rand(200, 500)
    );
}

/**
 * Generate mock portfolio data
 */
function generate_mock_portfolio_data($user_id) {
    $holdings = array(
        array(
            'symbol' => 'AAPL',
            'name' => 'Apple Inc.',
            'shares' => 50,
            'avg_cost' => 150.00,
            'current_price' => 175.25,
            'market_value' => 8762.50,
            'gain_loss' => 1262.50,
            'gain_loss_percent' => 16.83
        ),
        array(
            'symbol' => 'GOOGL',
            'name' => 'Alphabet Inc.',
            'shares' => 25,
            'avg_cost' => 2500.00,
            'current_price' => 2750.80,
            'market_value' => 68770.00,
            'gain_loss' => 6270.00,
            'gain_loss_percent' => 10.03
        )
    );
    
    $total_value = array_sum(array_column($holdings, 'market_value'));
    $total_cost = array_sum(array_map(function($h) { return $h['shares'] * $h['avg_cost']; }, $holdings));
    $total_gain_loss = $total_value - $total_cost;
    
    return array(
        'user_id' => $user_id,
        'total_value' => $total_value,
        'total_cost' => $total_cost,
        'total_gain_loss' => $total_gain_loss,
        'total_gain_loss_percent' => ($total_gain_loss / $total_cost) * 100,
        'holdings' => $holdings,
        'last_updated' => time()
    );
}

/**
 * Generate mock news data
 */
function generate_mock_news_data($category, $limit) {
    $news_items = array(
        array(
            'title' => 'Market Reaches New Highs Amid Economic Optimism',
            'summary' => 'Stock markets continue their upward trajectory as investors remain confident about economic recovery.',
            'source' => 'Financial Times',
            'published_at' => date('Y-m-d H:i:s', strtotime('-2 hours')),
            'url' => '#',
            'category' => 'market'
        ),
        array(
            'title' => 'Tech Stocks Lead Market Rally',
            'summary' => 'Technology companies show strong performance in latest trading session.',
            'source' => 'Reuters',
            'published_at' => date('Y-m-d H:i:s', strtotime('-4 hours')),
            'url' => '#',
            'category' => 'technology'
        ),
        array(
            'title' => 'Federal Reserve Maintains Interest Rates',
            'summary' => 'Central bank keeps rates steady as inflation concerns persist.',
            'source' => 'Bloomberg',
            'published_at' => date('Y-m-d H:i:s', strtotime('-6 hours')),
            'url' => '#',
            'category' => 'economy'
        )
    );
    
    // Filter by category if specified
    if ($category !== 'general') {
        $news_items = array_filter($news_items, function($item) use ($category) {
            return $item['category'] === $category;
        });
    }
    
    // Limit results
    $news_items = array_slice($news_items, 0, $limit);
    
    return array(
        'category' => $category,
        'total' => count($news_items),
        'articles' => $news_items,
        'last_updated' => time()
    );
}

// =============================================================================
// BACKEND CONNECTION HEALTH CHECK
// =============================================================================

/**
 * Check backend connection health
 */
function stock_scanner_check_backend_health() {
    $health_check = make_backend_api_request('health');
    
    if (is_wp_error($health_check)) {
        return array(
            'status' => 'error',
            'message' => $health_check->get_error_message(),
            'timestamp' => time()
        );
    }
    
    return array(
        'status' => 'healthy',
        'data' => $health_check,
        'timestamp' => time()
    );
}

/**
 * Add backend health check to admin dashboard
 */
function stock_scanner_admin_dashboard_widget() {
    wp_add_dashboard_widget(
        'stock_scanner_backend_health',
        'Stock Scanner Backend Status',
        'stock_scanner_backend_health_widget_content'
    );
}
add_action('wp_dashboard_setup', 'stock_scanner_admin_dashboard_widget');

function stock_scanner_backend_health_widget_content() {
    $health = stock_scanner_check_backend_health();
    
    echo '<div class="backend-health-status">';
    if ($health['status'] === 'healthy') {
        echo '<p style="color: green;"><strong>✓ Backend Connected</strong></p>';
        echo '<p>Last checked: ' . date('Y-m-d H:i:s', $health['timestamp']) . '</p>';
    } else {
        echo '<p style="color: red;"><strong>✗ Backend Disconnected</strong></p>';
        echo '<p>Error: ' . esc_html($health['message']) . '</p>';
        echo '<p><em>Using fallback mock data</em></p>';
    }
    echo '</div>';
}

// =============================================================================
// ADMIN SETTINGS PAGE FOR BACKEND CONFIGURATION
// =============================================================================

/**
 * Add admin menu for Stock Scanner settings
 */
function stock_scanner_admin_menu() {
    add_options_page(
        'Stock Scanner Settings',
        'Stock Scanner',
        'manage_options',
        'stock-scanner-settings',
        'stock_scanner_settings_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_menu');

/**
 * Register settings
 */
function stock_scanner_register_settings() {
    register_setting('stock_scanner_settings', 'stock_scanner_api_settings', array(
        'sanitize_callback' => 'stock_scanner_sanitize_api_settings'
    ));
    
    add_settings_section(
        'stock_scanner_api_section',
        'Backend API Configuration',
        'stock_scanner_api_section_callback',
        'stock-scanner-settings'
    );
    
    add_settings_field(
        'backend_url',
        'Backend URL',
        'stock_scanner_backend_url_callback',
        'stock-scanner-settings',
        'stock_scanner_api_section'
    );
    
    add_settings_field(
        'api_key',
        'API Key',
        'stock_scanner_api_key_callback',
        'stock-scanner-settings',
        'stock_scanner_api_section'
    );
    
    add_settings_field(
        'timeout',
        'Request Timeout (seconds)',
        'stock_scanner_timeout_callback',
        'stock-scanner-settings',
        'stock_scanner_api_section'
    );
}
add_action('admin_init', 'stock_scanner_register_settings');

/**
 * Settings page content
 */
function stock_scanner_settings_page() {
    if (isset($_POST['test_connection'])) {
        $health = stock_scanner_check_backend_health();
        if ($health['status'] === 'healthy') {
            echo '<div class="notice notice-success"><p><strong>✓ Backend connection successful!</strong></p></div>';
        } else {
            echo '<div class="notice notice-error"><p><strong>✗ Backend connection failed:</strong> ' . esc_html($health['message']) . '</p></div>';
        }
    }
    
    ?>
    <div class="wrap">
        <h1>Stock Scanner Settings</h1>
        
        <div class="card">
            <h2>Backend Connection Status</h2>
            <?php
            $health = stock_scanner_check_backend_health();
            if ($health['status'] === 'healthy') {
                echo '<p style="color: green; font-size: 16px;"><strong>✓ Backend Connected</strong></p>';
                echo '<p>Your Django backend is responding correctly.</p>';
            } else {
                echo '<p style="color: red; font-size: 16px;"><strong>✗ Backend Disconnected</strong></p>';
                echo '<p>Error: ' . esc_html($health['message']) . '</p>';
                echo '<p><em>The theme will use fallback mock data until the backend is connected.</em></p>';
            }
            ?>
            
            <form method="post" style="margin-top: 20px;">
                <?php wp_nonce_field('test_connection', 'test_connection_nonce'); ?>
                <input type="hidden" name="test_connection" value="1">
                <?php submit_button('Test Connection', 'secondary', 'test_connection', false); ?>
            </form>
        </div>
        
        <form method="post" action="options.php">
            <?php
            settings_fields('stock_scanner_settings');
            do_settings_sections('stock-scanner-settings');
            submit_button();
            ?>
        </form>
        
        <div class="card">
            <h2>Backend Setup Instructions</h2>
            <p>To connect your WordPress theme to your Django backend:</p>
            <ol>
                <li><strong>Backend URL:</strong> Enter the full URL to your Django backend (e.g., <code>http://localhost:8000</code> or <code>https://your-backend.com</code>)</li>
                <li><strong>API Key:</strong> Enter your Django API authentication key (if required)</li>
                <li><strong>Timeout:</strong> Set the request timeout in seconds (default: 30)</li>
                <li>Click "Save Changes" and then "Test Connection" to verify the setup</li>
            </ol>
            
            <h3>Expected Django API Endpoints</h3>
            <p>Your Django backend should provide these endpoints:</p>
            <ul>
                <li><code>GET /api/health</code> - Health check endpoint</li>
                <li><code>GET /api/stocks/{symbol}</code> - Individual stock data</li>
                <li><code>GET /api/historical/{symbol}?range={range}</code> - Historical stock data</li>
                <li><code>GET /api/realtime/{symbol}</code> - Real-time stock data</li>
                <li><code>GET /api/market/overview</code> - Market overview data</li>
                <li><code>GET /api/watchlist/{user_id}</code> - User watchlist</li>
                <li><code>POST /api/watchlist/{user_id}</code> - Add to watchlist</li>
                <li><code>DELETE /api/watchlist/{user_id}/{symbol}</code> - Remove from watchlist</li>
                <li><code>GET /api/portfolio/{user_id}</code> - User portfolio</li>
                <li><code>GET /api/news?category={category}&limit={limit}</code> - Market news</li>
            </ul>
        </div>
    </div>
    <?php
}

/**
 * Settings section callback
 */
function stock_scanner_api_section_callback() {
    echo '<p>Configure your Django backend API connection settings below.</p>';
}

/**
 * Backend URL field callback
 */
function stock_scanner_backend_url_callback() {
    $options = get_option('stock_scanner_api_settings', array());
    $backend_url = $options['backend_url'] ?? 'http://localhost:8000';
    echo '<input type="url" name="stock_scanner_api_settings[backend_url]" value="' . esc_attr($backend_url) . '" class="regular-text" placeholder="http://localhost:8000" />';
    echo '<p class="description">Full URL to your Django backend (including protocol)</p>';
}

/**
 * API Key field callback
 */
function stock_scanner_api_key_callback() {
    $options = get_option('stock_scanner_api_settings', array());
    $api_key = $options['api_key'] ?? '';
    echo '<input type="password" name="stock_scanner_api_settings[api_key]" value="' . esc_attr($api_key) . '" class="regular-text" placeholder="Optional API key" />';
    echo '<p class="description">API key for backend authentication (if required)</p>';
}

/**
 * Timeout field callback
 */
function stock_scanner_timeout_callback() {
    $options = get_option('stock_scanner_api_settings', array());
    $timeout = $options['timeout'] ?? 30;
    echo '<input type="number" name="stock_scanner_api_settings[timeout]" value="' . esc_attr($timeout) . '" min="5" max="120" />';
    echo '<p class="description">Request timeout in seconds (5-120)</p>';
}

/**
 * Sanitize API settings
 */
function stock_scanner_sanitize_api_settings($input) {
    $sanitized = array();
    
    if (isset($input['backend_url'])) {
        $sanitized['backend_url'] = esc_url_raw($input['backend_url']);
    }
    
    if (isset($input['api_key'])) {
        $sanitized['api_key'] = sanitize_text_field($input['api_key']);
    }
    
    if (isset($input['timeout'])) {
        $timeout = intval($input['timeout']);
        $sanitized['timeout'] = max(5, min(120, $timeout)); // Clamp between 5-120 seconds
    }
    
    return $sanitized;
}

// =============================================================================
// DATA FORMATTING AND PROCESSING UTILITIES
// =============================================================================

/**
 * Format stock price for display
 */
function format_stock_price($price, $decimals = 2) {
    if (!is_numeric($price)) {
        return '--';
    }
    return '$' . number_format((float)$price, $decimals);
}

/**
 * Format percentage change with color coding
 */
function format_percentage_change($change, $decimals = 2, $include_color = false) {
    if (!is_numeric($change)) {
        return '--';
    }
    
    $formatted = number_format((float)$change, $decimals) . '%';
    $sign = $change >= 0 ? '+' : '';
    
    if ($include_color) {
        $color_class = $change >= 0 ? 'positive' : 'negative';
        return "<span class=\"change-{$color_class}\">{$sign}{$formatted}</span>";
    }
    
    return $sign . $formatted;
}

/**
 * Format volume numbers
 */
function format_volume($volume) {
    if (!is_numeric($volume)) {
        return '--';
    }
    
    $volume = (float)$volume;
    
    if ($volume >= 1000000000) {
        return number_format($volume / 1000000000, 1) . 'B';
    } elseif ($volume >= 1000000) {
        return number_format($volume / 1000000, 1) . 'M';
    } elseif ($volume >= 1000) {
        return number_format($volume / 1000, 1) . 'K';
    }
    
    return number_format($volume);
}

/**
 * Format market cap
 */
function format_market_cap($market_cap) {
    if (!is_numeric($market_cap)) {
        return '--';
    }
    
    $market_cap = (float)$market_cap;
    
    if ($market_cap >= 1000000000000) {
        return '$' . number_format($market_cap / 1000000000000, 2) . 'T';
    } elseif ($market_cap >= 1000000000) {
        return '$' . number_format($market_cap / 1000000000, 2) . 'B';
    } elseif ($market_cap >= 1000000) {
        return '$' . number_format($market_cap / 1000000, 2) . 'M';
    }
    
    return '$' . number_format($market_cap);
}

/**
 * Format currency amount
 */
function format_currency($amount, $decimals = 2) {
    if (!is_numeric($amount)) {
        return '--';
    }
    return '$' . number_format((float)$amount, $decimals);
}

/**
 * Format date for display
 */
function format_display_date($date, $format = 'M j, Y') {
    if (empty($date)) {
        return '--';
    }
    
    $timestamp = is_numeric($date) ? $date : strtotime($date);
    if (!$timestamp) {
        return '--';
    }
    
    return date($format, $timestamp);
}

/**
 * Format time for display
 */
function format_display_time($time, $format = 'g:i A') {
    if (empty($time)) {
        return '--';
    }
    
    $timestamp = is_numeric($time) ? $time : strtotime($time);
    if (!$timestamp) {
        return '--';
    }
    
    return date($format, $timestamp);
}

/**
 * Format stock data for table display
 */
function format_stock_for_table($stock_data) {
    if (!is_array($stock_data)) {
        return array();
    }
    
    return array(
        'symbol' => strtoupper($stock_data['symbol'] ?? ''),
        'name' => $stock_data['name'] ?? '--',
        'price' => format_stock_price($stock_data['price'] ?? 0),
        'change' => format_stock_price($stock_data['change'] ?? 0),
        'change_percent' => format_percentage_change($stock_data['change_percent'] ?? 0, 2, true),
        'volume' => format_volume($stock_data['volume'] ?? 0),
        'market_cap' => format_market_cap($stock_data['market_cap'] ?? 0),
        'pe_ratio' => is_numeric($stock_data['pe_ratio'] ?? null) ? number_format($stock_data['pe_ratio'], 2) : '--',
        'high_52w' => format_stock_price($stock_data['high_52w'] ?? 0),
        'low_52w' => format_stock_price($stock_data['low_52w'] ?? 0),
        'raw_price' => (float)($stock_data['price'] ?? 0),
        'raw_change' => (float)($stock_data['change'] ?? 0),
        'raw_change_percent' => (float)($stock_data['change_percent'] ?? 0),
        'raw_volume' => (int)($stock_data['volume'] ?? 0),
        'timestamp' => $stock_data['timestamp'] ?? time()
    );
}

/**
 * Format historical data for charts
 */
function format_historical_for_chart($historical_data) {
    if (!is_array($historical_data) || empty($historical_data['labels']) || empty($historical_data['prices'])) {
        return array(
            'labels' => array(),
            'prices' => array(),
            'volumes' => array(),
            'trend' => 0
        );
    }
    
    $formatted_labels = array();
    foreach ($historical_data['labels'] as $label) {
        $formatted_labels[] = format_display_date($label, 'M j');
    }
    
    return array(
        'labels' => $formatted_labels,
        'prices' => array_map('floatval', $historical_data['prices']),
        'volumes' => array_map('intval', $historical_data['volumes'] ?? array()),
        'trend' => (int)($historical_data['trend'] ?? 0),
        'symbol' => strtoupper($historical_data['symbol'] ?? ''),
        'range' => $historical_data['range'] ?? '1W'
    );
}

/**
 * Format portfolio data for display
 */
function format_portfolio_for_display($portfolio_data) {
    if (!is_array($portfolio_data)) {
        return array(
            'total_value' => '$0.00',
            'total_cost' => '$0.00',
            'total_gain_loss' => '$0.00',
            'total_gain_loss_percent' => '0.00%',
            'holdings' => array(),
            'raw_total_value' => 0,
            'raw_total_gain_loss' => 0
        );
    }
    
    $formatted_holdings = array();
    foreach ($portfolio_data['holdings'] ?? array() as $holding) {
        $formatted_holdings[] = array(
            'symbol' => strtoupper($holding['symbol'] ?? ''),
            'name' => $holding['name'] ?? '--',
            'shares' => number_format($holding['shares'] ?? 0),
            'avg_cost' => format_stock_price($holding['avg_cost'] ?? 0),
            'current_price' => format_stock_price($holding['current_price'] ?? 0),
            'market_value' => format_currency($holding['market_value'] ?? 0),
            'gain_loss' => format_currency($holding['gain_loss'] ?? 0),
            'gain_loss_percent' => format_percentage_change($holding['gain_loss_percent'] ?? 0, 2, true),
            'raw_shares' => (float)($holding['shares'] ?? 0),
            'raw_avg_cost' => (float)($holding['avg_cost'] ?? 0),
            'raw_current_price' => (float)($holding['current_price'] ?? 0),
            'raw_market_value' => (float)($holding['market_value'] ?? 0),
            'raw_gain_loss' => (float)($holding['gain_loss'] ?? 0),
            'raw_gain_loss_percent' => (float)($holding['gain_loss_percent'] ?? 0)
        );
    }
    
    return array(
        'total_value' => format_currency($portfolio_data['total_value'] ?? 0),
        'total_cost' => format_currency($portfolio_data['total_cost'] ?? 0),
        'total_gain_loss' => format_currency($portfolio_data['total_gain_loss'] ?? 0),
        'total_gain_loss_percent' => format_percentage_change($portfolio_data['total_gain_loss_percent'] ?? 0, 2, true),
        'holdings' => $formatted_holdings,
        'raw_total_value' => (float)($portfolio_data['total_value'] ?? 0),
        'raw_total_cost' => (float)($portfolio_data['total_cost'] ?? 0),
        'raw_total_gain_loss' => (float)($portfolio_data['total_gain_loss'] ?? 0),
        'raw_total_gain_loss_percent' => (float)($portfolio_data['total_gain_loss_percent'] ?? 0),
        'last_updated' => format_display_time($portfolio_data['last_updated'] ?? time())
    );
}

/**
 * Format market data for display
 */
function format_market_data_for_display($market_data) {
    if (!is_array($market_data)) {
        return array(
            'indices' => array(),
            'market_status' => 'closed',
            'last_updated' => '--',
            'advancing' => 0,
            'declining' => 0,
            'unchanged' => 0
        );
    }
    
    $formatted_indices = array();
    foreach ($market_data['indices'] ?? array() as $index) {
        $formatted_indices[] = array(
            'symbol' => strtoupper($index['symbol'] ?? ''),
            'name' => $index['name'] ?? '--',
            'price' => format_stock_price($index['price'] ?? 0),
            'change' => format_stock_price($index['change'] ?? 0),
            'change_percent' => format_percentage_change($index['change_percent'] ?? 0, 2, true),
            'raw_price' => (float)($index['price'] ?? 0),
            'raw_change' => (float)($index['change'] ?? 0),
            'raw_change_percent' => (float)($index['change_percent'] ?? 0)
        );
    }
    
    return array(
        'indices' => $formatted_indices,
        'market_status' => $market_data['market_status'] ?? 'closed',
        'last_updated' => format_display_time($market_data['last_updated'] ?? time()),
        'advancing' => number_format($market_data['advancing'] ?? 0),
        'declining' => number_format($market_data['declining'] ?? 0),
        'unchanged' => number_format($market_data['unchanged'] ?? 0),
        'raw_advancing' => (int)($market_data['advancing'] ?? 0),
        'raw_declining' => (int)($market_data['declining'] ?? 0),
        'raw_unchanged' => (int)($market_data['unchanged'] ?? 0)
    );
}

/**
 * Format news data for display
 */
function format_news_for_display($news_data) {
    if (!is_array($news_data) || empty($news_data['articles'])) {
        return array(
            'articles' => array(),
            'total' => 0,
            'category' => 'general'
        );
    }
    
    $formatted_articles = array();
    foreach ($news_data['articles'] as $article) {
        $formatted_articles[] = array(
            'title' => $article['title'] ?? 'No title',
            'summary' => $article['summary'] ?? 'No summary available',
            'source' => $article['source'] ?? 'Unknown',
            'published_at' => format_display_time($article['published_at'] ?? time(), 'M j, Y g:i A'),
            'url' => $article['url'] ?? '#',
            'category' => $article['category'] ?? 'general',
            'raw_published_at' => $article['published_at'] ?? time()
        );
    }
    
    return array(
        'articles' => $formatted_articles,
        'total' => count($formatted_articles),
        'category' => $news_data['category'] ?? 'general',
        'last_updated' => format_display_time($news_data['last_updated'] ?? time())
    );
}

/**
 * Format watchlist data for display
 */
function format_watchlist_for_display($watchlist_data) {
    if (!is_array($watchlist_data)) {
        return array();
    }
    
    $formatted_watchlist = array();
    foreach ($watchlist_data as $item) {
        if (is_string($item)) {
            // Simple symbol list
            $formatted_watchlist[] = array(
                'symbol' => strtoupper($item),
                'name' => '--',
                'price' => '--',
                'change' => '--',
                'change_percent' => '--',
                'volume' => '--'
            );
        } elseif (is_array($item)) {
            // Full stock data
            $formatted_watchlist[] = format_stock_for_table($item);
        }
    }
    
    return $formatted_watchlist;
}

/**
 * Sanitize and validate stock symbol
 */
function sanitize_stock_symbol($symbol) {
    if (!is_string($symbol)) {
        return '';
    }
    
    // Remove any non-alphanumeric characters and convert to uppercase
    $symbol = strtoupper(preg_replace('/[^A-Za-z0-9]/', '', $symbol));
    
    // Limit length to 10 characters (most stock symbols are 1-5 characters)
    return substr($symbol, 0, 10);
}

/**
 * Validate and sanitize time range parameter
 */
function sanitize_time_range($range) {
    $valid_ranges = array('1D', '1W', '1M', '3M', '1Y', '5Y');
    
    if (!in_array($range, $valid_ranges)) {
        return '1W'; // Default fallback
    }
    
    return $range;
}

/**
 * Get formatted data for AJAX endpoints
 */
function get_formatted_stock_data($symbol) {
    $symbol = sanitize_stock_symbol($symbol);
    if (empty($symbol)) {
        return new WP_Error('invalid_symbol', 'Invalid stock symbol provided');
    }
    
    $raw_data = get_stock_data($symbol);
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_stock_for_table($raw_data);
}

/**
 * Get formatted historical data for charts
 */
function get_formatted_historical_data($symbol, $range = '1W') {
    $symbol = sanitize_stock_symbol($symbol);
    $range = sanitize_time_range($range);
    
    if (empty($symbol)) {
        return new WP_Error('invalid_symbol', 'Invalid stock symbol provided');
    }
    
    $raw_data = make_backend_api_request("historical/{$symbol}", array('range' => $range));
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_historical_for_chart($raw_data);
}

/**
 * Get formatted portfolio data
 */
function get_formatted_portfolio_data($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return new WP_Error('no_user', 'User not authenticated');
    }
    
    $raw_data = make_backend_api_request("portfolio/{$user_id}");
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_portfolio_for_display($raw_data);
}

/**
 * Get formatted market data
 */
function get_formatted_market_data() {
    $raw_data = get_market_overview();
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_market_data_for_display($raw_data);
}

/**
 * Get formatted watchlist data
 */
function get_formatted_watchlist_data($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return new WP_Error('no_user', 'User not authenticated');
    }
    
    $raw_data = get_user_watchlist($user_id);
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_watchlist_for_display($raw_data);
}

/**
 * Get formatted news data
 */
function get_formatted_news_data($category = 'general', $limit = 20) {
    $raw_data = make_backend_api_request('news', array(
        'category' => $category,
        'limit' => $limit
    ));
    
    if (is_wp_error($raw_data)) {
        return $raw_data;
    }
    
    return format_news_for_display($raw_data);
}

// =============================================================================
// AJAX HANDLERS FOR FORMATTED DATA
// =============================================================================

/**
 * AJAX handler for formatted stock data
 */
function ajax_get_formatted_stock_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $symbol = sanitize_text_field($_POST['symbol'] ?? '');
    $formatted_data = get_formatted_stock_data($symbol);
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_stock_data', 'ajax_get_formatted_stock_data');
add_action('wp_ajax_nopriv_get_formatted_stock_data', 'ajax_get_formatted_stock_data');

/**
 * AJAX handler for formatted historical data
 */
function ajax_get_formatted_historical_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $symbol = sanitize_text_field($_POST['symbol'] ?? '');
    $range = sanitize_text_field($_POST['range'] ?? '1W');
    
    $formatted_data = get_formatted_historical_data($symbol, $range);
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_historical_data', 'ajax_get_formatted_historical_data');
add_action('wp_ajax_nopriv_get_formatted_historical_data', 'ajax_get_formatted_historical_data');

/**
 * AJAX handler for formatted portfolio data
 */
function ajax_get_formatted_portfolio_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $formatted_data = get_formatted_portfolio_data();
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_portfolio_data', 'ajax_get_formatted_portfolio_data');

/**
 * AJAX handler for formatted market data
 */
function ajax_get_formatted_market_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $formatted_data = get_formatted_market_data();
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_market_data', 'ajax_get_formatted_market_data');
add_action('wp_ajax_nopriv_get_formatted_market_data', 'ajax_get_formatted_market_data');

/**
 * AJAX handler for formatted watchlist data
 */
function ajax_get_formatted_watchlist_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $formatted_data = get_formatted_watchlist_data();
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_watchlist_data', 'ajax_get_formatted_watchlist_data');

/**
 * AJAX handler for formatted news data
 */
function ajax_get_formatted_news_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $category = sanitize_text_field($_POST['category'] ?? 'general');
    $limit = intval($_POST['limit'] ?? 20);
    
    $formatted_data = get_formatted_news_data($category, $limit);
    
    if (is_wp_error($formatted_data)) {
        wp_send_json_error($formatted_data->get_error_message());
    }
    
    wp_send_json_success($formatted_data);
}
add_action('wp_ajax_get_formatted_news_data', 'ajax_get_formatted_news_data');
add_action('wp_ajax_nopriv_get_formatted_news_data', 'ajax_get_formatted_news_data');

// =============================================================================
// THEME ACTIVATION: DELETE ALL PAGES AND CREATE FRESH ONES
// =============================================================================

/**
 * Theme activation hook - Delete all pages and create fresh ones
 */
function stock_scanner_zatra_activation() {
    // Delete ALL existing pages
    stock_scanner_delete_all_pages();
    
    // Create fresh pages for the theme
    stock_scanner_create_theme_pages();
    
    // Set homepage
    stock_scanner_set_homepage();
    
    // Create menus
    stock_scanner_create_menus();
    
    // Set default options
    stock_scanner_set_default_options();
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'stock_scanner_zatra_activation');

/**
 * Delete ALL existing pages
 */
function stock_scanner_delete_all_pages() {
    global $wpdb;
    
    // Get all page IDs
    $page_ids = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type = 'page'");
    
    // Force delete each page
    foreach ($page_ids as $page_id) {
        wp_delete_post($page_id, true); // true = force delete, bypass trash
    }
    
    // Clean up any remaining page meta
    $wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id NOT IN (SELECT ID FROM {$wpdb->posts})");
    
    // Clear any cached page data
    wp_cache_flush();
}

/**
 * Create all theme pages
 */
function stock_scanner_create_theme_pages() {
    $pages = array(
        // HOMEPAGE
        'home' => array(
            'title' => 'Home',
            'template' => 'home',
            'content' => 'Welcome to Stock Scanner Pro - Your comprehensive stock market analysis platform.',
            'menu_order' => 1
        ),
        
        // CORE TRADING TOOLS
        'dashboard' => array(
            'title' => 'Dashboard',
            'template' => 'dashboard',
            'content' => 'Your personal stock market dashboard with real-time data and analytics.',
            'menu_order' => 10
        ),
        'stock-lookup' => array(
            'title' => 'Stock Lookup',
            'template' => 'stock-lookup',
            'content' => 'Search and analyze individual stocks with real-time quotes and charts.',
            'menu_order' => 11
        ),
        'stock-news' => array(
            'title' => 'Stock News',
            'template' => 'stock-news',
            'content' => 'Latest market news and analysis from trusted financial sources.',
            'menu_order' => 12
        ),
        'stock-screener' => array(
            'title' => 'Stock Screener',
            'template' => 'stock-screener',
            'content' => 'Advanced stock screening tool with 50+ filtering criteria.',
            'menu_order' => 13
        ),
        'market-overview' => array(
            'title' => 'Market Overview',
            'template' => 'market-overview',
            'content' => 'Comprehensive market overview with indices, sectors, and analysis.',
            'menu_order' => 14
        ),
        'watchlist' => array(
            'title' => 'My Watchlist',
            'template' => 'watchlist',
            'content' => 'Manage your personal stock watchlists and track your favorite stocks.',
            'menu_order' => 15
        ),
        
        // PORTFOLIO & ACCOUNT
        'portfolio' => array(
            'title' => 'My Portfolio',
            'template' => 'portfolio',
            'content' => 'Track your investment portfolio with detailed analytics and performance metrics.',
            'menu_order' => 20
        ),
        'account' => array(
            'title' => 'My Account',
            'template' => 'account',
            'content' => 'Manage your account settings, subscription, and preferences.',
            'menu_order' => 21
        ),
        'billing-history' => array(
            'title' => 'Billing History',
            'template' => 'billing-history',
            'content' => 'View your payment history and manage billing information.',
            'menu_order' => 22
        ),
        'user-settings' => array(
            'title' => 'User Settings',
            'template' => 'user-settings',
            'content' => 'Customize your trading preferences and notification settings.',
            'menu_order' => 23
        ),
        
        // PREMIUM & PAYMENT
        'premium-plans' => array(
            'title' => 'Premium Plans',
            'template' => 'premium-plans',
            'content' => 'Choose the perfect plan for your trading needs with advanced features.',
            'menu_order' => 30
        ),
        'paypal-checkout' => array(
            'title' => 'PayPal Checkout',
            'template' => 'paypal-checkout',
            'content' => 'Complete your subscription payment securely through PayPal.',
            'menu_order' => 31
        ),
        'payment-success' => array(
            'title' => 'Payment Success',
            'template' => 'payment-success',
            'content' => 'Thank you for your payment! Your subscription has been activated.',
            'menu_order' => 32
        ),
        'payment-cancelled' => array(
            'title' => 'Payment Cancelled',
            'template' => 'payment-cancelled',
            'content' => 'Your payment was cancelled. You can try again or contact support.',
            'menu_order' => 33
        ),
        'compare-plans' => array(
            'title' => 'Compare Plans',
            'template' => 'compare-plans',
            'content' => 'Compare our subscription plans side-by-side to find the best fit.',
            'menu_order' => 34
        ),
        
        // PERSONALIZED FEATURES
        'personalized-news' => array(
            'title' => 'Personalized News',
            'template' => 'personalized-news',
            'content' => 'AI-curated news feed based on your interests and portfolio.',
            'menu_order' => 40
        ),
        
        // AUTHENTICATION
        'login' => array(
            'title' => 'Login',
            'template' => 'login',
            'content' => 'Sign in to your Stock Scanner Pro account.',
            'menu_order' => 50
        ),
        'signup' => array(
            'title' => 'Sign Up',
            'template' => 'signup',
            'content' => 'Create your Stock Scanner Pro account and start trading smarter.',
            'menu_order' => 51
        ),
        
        // HELP & SUPPORT
        'contact' => array(
            'title' => 'Contact Us',
            'template' => 'contact',
            'content' => 'Get in touch with our support team for assistance.',
            'menu_order' => 60
        ),
        'faq' => array(
            'title' => 'FAQ',
            'template' => 'faq',
            'content' => 'Frequently asked questions about Stock Scanner Pro.',
            'menu_order' => 61
        ),
        'help-center' => array(
            'title' => 'Help Center',
            'template' => 'help-center',
            'content' => 'Comprehensive help documentation and tutorials.',
            'menu_order' => 62
        ),
        'getting-started' => array(
            'title' => 'Getting Started',
            'template' => 'getting-started',
            'content' => 'New to Stock Scanner Pro? Start here for a quick overview.',
            'menu_order' => 63
        ),
        'how-it-works' => array(
            'title' => 'How It Works',
            'template' => 'how-it-works',
            'content' => 'Learn how Stock Scanner Pro helps you make better investment decisions.',
            'menu_order' => 64
        ),
        'glossary' => array(
            'title' => 'Glossary',
            'template' => 'glossary',
            'content' => 'Financial terms and definitions explained in simple language.',
            'menu_order' => 65
        ),
        'market-hours' => array(
            'title' => 'Market Hours',
            'template' => 'market-hours',
            'content' => 'Global market trading hours and holiday schedules.',
            'menu_order' => 66
        ),
        
        // LEGAL PAGES
        'privacy-policy' => array(
            'title' => 'Privacy Policy',
            'template' => 'privacy-policy',
            'content' => 'Our commitment to protecting your personal information.',
            'menu_order' => 70
        ),
        'terms-of-service' => array(
            'title' => 'Terms of Service',
            'template' => 'terms-of-service',
            'content' => 'Terms and conditions for using Stock Scanner Pro.',
            'menu_order' => 71
        ),
        'cookie-policy' => array(
            'title' => 'Cookie Policy',
            'template' => 'cookie-policy',
            'content' => 'Information about how we use cookies on our website.',
            'menu_order' => 72
        )
    );
    
    foreach ($pages as $slug => $page_data) {
        stock_scanner_create_page($slug, $page_data);
    }
}

/**
 * Create individual page
 */
function stock_scanner_create_page($slug, $page_data) {
    // Check if page already exists
    $existing_page = get_page_by_path($slug);
    if ($existing_page) {
        return $existing_page->ID;
    }
    
    $page_args = array(
        'post_title' => $page_data['title'],
        'post_content' => $page_data['content'],
        'post_status' => 'publish',
        'post_type' => 'page',
        'post_name' => $slug,
        'menu_order' => $page_data['menu_order'] ?? 0,
        'comment_status' => 'closed',
        'ping_status' => 'closed'
    );
    
    $page_id = wp_insert_post($page_args);
    
    if ($page_id && !is_wp_error($page_id)) {
        // Set page template if specified
        if (isset($page_data['template'])) {
            update_post_meta($page_id, '_wp_page_template', 'page-' . $page_data['template'] . '.php');
        }
        
        // Set additional meta data
        update_post_meta($page_id, '_stock_scanner_page', true);
        update_post_meta($page_id, '_stock_scanner_page_type', $page_data['template'] ?? 'default');
    }
    
    return $page_id;
}

/**
 * Set homepage
 */
function stock_scanner_set_homepage() {
    $home_page = get_page_by_path('home');
    if ($home_page) {
        update_option('show_on_front', 'page');
        update_option('page_on_front', $home_page->ID);
    }
}

/**
 * Create navigation menus
 */
function stock_scanner_create_menus() {
    // Create Primary Menu
    $primary_menu_id = wp_create_nav_menu('Primary Menu');
    if (!is_wp_error($primary_menu_id)) {
        // Add menu items
        $menu_items = array(
            'home' => 'Home',
            'dashboard' => 'Dashboard',
            'stock-lookup' => 'Stock Lookup',
            'stock-news' => 'Market News',
            'stock-screener' => 'Stock Screener',
            'market-overview' => 'Market Overview',
            'watchlist' => 'Watchlist',
            'portfolio' => 'Portfolio',
            'premium-plans' => 'Premium Plans'
        );
        
        $menu_order = 1;
        foreach ($menu_items as $slug => $title) {
            $page = get_page_by_path($slug);
            if ($page) {
                wp_update_nav_menu_item($primary_menu_id, 0, array(
                    'menu-item-title' => $title,
                    'menu-item-object' => 'page',
                    'menu-item-object-id' => $page->ID,
                    'menu-item-type' => 'post_type',
                    'menu-item-status' => 'publish',
                    'menu-item-position' => $menu_order++
                ));
            }
        }
        
        // Assign to primary location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['primary'] = $primary_menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
    
    // Create Footer Menu
    $footer_menu_id = wp_create_nav_menu('Footer Menu');
    if (!is_wp_error($footer_menu_id)) {
        $footer_items = array(
            'privacy-policy' => 'Privacy Policy',
            'terms-of-service' => 'Terms of Service',
            'cookie-policy' => 'Cookie Policy',
            'contact' => 'Contact Us',
            'help-center' => 'Help Center'
        );
        
        $menu_order = 1;
        foreach ($footer_items as $slug => $title) {
            $page = get_page_by_path($slug);
            if ($page) {
                wp_update_nav_menu_item($footer_menu_id, 0, array(
                    'menu-item-title' => $title,
                    'menu-item-object' => 'page',
                    'menu-item-object-id' => $page->ID,
                    'menu-item-type' => 'post_type',
                    'menu-item-status' => 'publish',
                    'menu-item-position' => $menu_order++
                ));
            }
        }
        
        // Assign to footer location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['footer'] = $footer_menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
}

/**
 * Set default theme options
 */
function stock_scanner_set_default_options() {
    // Theme customization defaults
    set_theme_mod('custom_logo', '');
    set_theme_mod('site_icon', '');
    
    // Stock Scanner specific options
    update_option('stock_scanner_theme_version', '1.0.0');
    update_option('stock_scanner_installation_date', current_time('mysql'));
    update_option('stock_scanner_pages_created', true);
    
    // Default API settings (can be configured later)
    $default_api_settings = array(
        'backend_url' => 'http://localhost:8000',
        'api_key' => '',
        'timeout' => 30,
        'cache_enabled' => true,
        'cache_duration' => 300 // 5 minutes
    );
    update_option('stock_scanner_api_settings', $default_api_settings);
    
    // Default user settings
    $default_user_settings = array(
        'default_watchlist_view' => 'list',
        'refresh_interval' => 30,
        'enable_notifications' => true,
        'enable_email_alerts' => true
    );
    update_option('stock_scanner_default_user_settings', $default_user_settings);
}

/**
 * Theme deactivation cleanup (optional)
 */
function stock_scanner_zatra_deactivation() {
    // Optional: Add cleanup code here if needed
    // For now, we'll leave pages intact when switching themes
    // flush_rewrite_rules();
}
add_action('switch_theme', 'stock_scanner_zatra_deactivation');

/**
 * Admin notice after theme activation
 */
function stock_scanner_zatra_activation_notice() {
    if (get_option('stock_scanner_pages_created')) {
        echo '<div class="notice notice-success is-dismissible">';
        echo '<p><strong>Stock Scanner Pro - Zatra Edition activated successfully!</strong></p>';
        echo '<p>All pages have been created and configured. Your site is ready to use.</p>';
        echo '<p><a href="' . admin_url('customize.php') . '" class="button button-primary">Customize Your Site</a> ';
        echo '<a href="' . home_url() . '" class="button">View Site</a></p>';
        echo '</div>';
        
        // Remove the notice after displaying it once
        delete_option('stock_scanner_pages_created');
    }
}
add_action('admin_notices', 'stock_scanner_zatra_activation_notice');

// =============================================================================
// ADDITIONAL HELPER FUNCTIONS
// =============================================================================

/**
 * Get theme pages for admin reference
 */
function stock_scanner_get_theme_pages() {
    $pages = get_posts(array(
        'post_type' => 'page',
        'meta_key' => '_stock_scanner_page',
        'meta_value' => true,
        'numberposts' => -1,
        'orderby' => 'menu_order',
        'order' => 'ASC'
    ));
    
    return $pages;
}

/**
 * Check if current page is a Stock Scanner page
 */
function is_stock_scanner_page() {
    if (!is_page()) {
        return false;
    }
    
    global $post;
    return get_post_meta($post->ID, '_stock_scanner_page', true);
}

/**
 * Get Stock Scanner page type
 */
function get_stock_scanner_page_type() {
    if (!is_stock_scanner_page()) {
        return false;
    }
    
    global $post;
    return get_post_meta($post->ID, '_stock_scanner_page_type', true);
}

// =============================================================================
// ENHANCED SEO FUNCTIONS
// =============================================================================

/**
 * Add custom SEO meta boxes to pages
 */
function zatra_add_seo_meta_boxes() {
    add_meta_box(
        'zatra_seo_meta',
        'SEO Settings',
        'zatra_seo_meta_callback',
        'page',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'zatra_add_seo_meta_boxes');

/**
 * SEO meta box callback
 */
function zatra_seo_meta_callback($post) {
    wp_nonce_field('zatra_seo_meta_nonce', 'zatra_seo_meta_nonce_field');
    
    $seo_description = get_post_meta($post->ID, '_seo_description', true);
    $seo_keywords = get_post_meta($post->ID, '_seo_keywords', true);
    $seo_title = get_post_meta($post->ID, '_seo_title', true);
    $noindex = get_post_meta($post->ID, '_seo_noindex', true);
    
    echo '<table class="form-table">';
    echo '<tr><th><label for="seo_title">SEO Title:</label></th>';
    echo '<td><input type="text" id="seo_title" name="seo_title" value="' . esc_attr($seo_title) . '" style="width:100%" /></td></tr>';
    echo '<tr><th><label for="seo_description">Meta Description:</label></th>';
    echo '<td><textarea id="seo_description" name="seo_description" rows="3" style="width:100%">' . esc_textarea($seo_description) . '</textarea></td></tr>';
    echo '<tr><th><label for="seo_keywords">Keywords:</label></th>';
    echo '<td><input type="text" id="seo_keywords" name="seo_keywords" value="' . esc_attr($seo_keywords) . '" style="width:100%" placeholder="Separate keywords with commas" /></td></tr>';
    echo '<tr><th><label for="seo_noindex">Search Engine Visibility:</label></th>';
    echo '<td><label><input type="checkbox" id="seo_noindex" name="seo_noindex" value="1" ' . checked($noindex, 1, false) . ' /> Discourage search engines from indexing this page</label></td></tr>';
    echo '</table>';
}

/**
 * Save SEO meta data
 */
function zatra_save_seo_meta($post_id) {
    if (!isset($_POST['zatra_seo_meta_nonce_field']) || !wp_verify_nonce($_POST['zatra_seo_meta_nonce_field'], 'zatra_seo_meta_nonce')) {
        return;
    }
    
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }
    
    if (!current_user_can('edit_post', $post_id)) {
        return;
    }
    
    if (isset($_POST['seo_title'])) {
        update_post_meta($post_id, '_seo_title', sanitize_text_field($_POST['seo_title']));
    }
    
    if (isset($_POST['seo_description'])) {
        update_post_meta($post_id, '_seo_description', sanitize_textarea_field($_POST['seo_description']));
    }
    
    if (isset($_POST['seo_keywords'])) {
        update_post_meta($post_id, '_seo_keywords', sanitize_text_field($_POST['seo_keywords']));
    }
    
    if (isset($_POST['seo_noindex'])) {
        update_post_meta($post_id, '_seo_noindex', 1);
    } else {
        delete_post_meta($post_id, '_seo_noindex');
    }
}
add_action('save_post', 'zatra_save_seo_meta');

/**
 * Custom document title for better SEO
 */
function zatra_custom_document_title($title) {
    global $post;
    
    if (is_singular() && isset($post)) {
        $custom_title = get_post_meta($post->ID, '_seo_title', true);
        if (!empty($custom_title)) {
            return $custom_title;
        }
    }
    
    return $title;
}
add_filter('pre_get_document_title', 'zatra_custom_document_title');

/**
 * Add robots meta tag based on settings
 */
function zatra_robots_meta() {
    global $post;
    
    if (is_singular() && isset($post)) {
        $noindex = get_post_meta($post->ID, '_seo_noindex', true);
        if ($noindex) {
            echo '<meta name="robots" content="noindex, nofollow">' . "\n";
            return;
        }
    }
    
    // Default robots tag is already handled in header.php
}
add_action('wp_head', 'zatra_robots_meta', 1);

/**
 * Generate breadcrumbs for better navigation and SEO
 */
function zatra_breadcrumbs() {
    $home_title = get_bloginfo('name');
    $delimiter = ' &raquo; ';
    $before = '<span class="current">';
    $after = '</span>';
    
    if (!is_home() && !is_front_page()) {
        echo '<div class="breadcrumbs" itemscope itemtype="https://schema.org/BreadcrumbList">';
        echo '<span itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
        echo '<a itemprop="item" href="' . esc_url(home_url()) . '"><span itemprop="name">' . $home_title . '</span></a>';
        echo '<meta itemprop="position" content="1" /></span>';
        
        if (is_page()) {
            $position = 2;
            global $post;
            if ($post->post_parent) {
                $parent_id = $post->post_parent;
                $breadcrumbs = array();
                while ($parent_id) {
                    $page = get_page($parent_id);
                    $breadcrumbs[] = '<span itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem"><a itemprop="item" href="' . get_permalink($page->ID) . '"><span itemprop="name">' . get_the_title($page->ID) . '</span></a><meta itemprop="position" content="' . $position . '" /></span>';
                    $parent_id = $page->post_parent;
                    $position++;
                }
                $breadcrumbs = array_reverse($breadcrumbs);
                foreach ($breadcrumbs as $breadcrumb) {
                    echo $delimiter . $breadcrumb;
                }
            }
            echo $delimiter . $before . get_the_title() . $after;
        }
        
        echo '</div>';
    }
}

/**
 * Add structured data for financial pages
 */
function zatra_add_financial_structured_data() {
    if (is_page_template('page-stock-screener.php') || is_page_template('page-market-overview.php')) {
        ?>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "FinancialService",
            "name": "<?php echo esc_js(get_bloginfo('name')); ?>",
            "description": "Professional stock market analysis and investment tools",
            "url": "<?php echo esc_url(home_url()); ?>",
            "serviceType": "Investment Analysis",
            "provider": {
                "@type": "Organization",
                "name": "<?php echo esc_js(get_bloginfo('name')); ?>"
            }
        }
        </script>
        <?php
    }
    
    if (is_page_template('page-premium-plans.php')) {
        ?>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Zatra Premium Subscription",
            "description": "Advanced stock market analysis tools and unlimited API access",
            "category": "Financial Software",
            "offers": {
                "@type": "Offer",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "<?php echo date('Y-12-31'); ?>"
            }
        }
        </script>
        <?php
    }
}
add_action('wp_head', 'zatra_add_financial_structured_data');

/**
 * Optimize images for SEO
 */
function zatra_add_image_alt_text($attr, $attachment, $size) {
    if (empty($attr['alt'])) {
        $alt_text = get_post_meta($attachment->ID, '_wp_attachment_image_alt', true);
        if (empty($alt_text)) {
            $alt_text = $attachment->post_title;
        }
        $attr['alt'] = $alt_text;
    }
    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'zatra_add_image_alt_text', 10, 3);

/**
 * Add rel="noopener" to external links for security and SEO
 */
function zatra_add_noopener_to_external_links($content) {
    $content = preg_replace_callback(
        '/<a([^>]*)href="(https?:\/\/(?!' . preg_quote(home_url(), '/') . ')[^"]*)"([^>]*)>/i',
        function($matches) {
            $attrs = $matches[1] . $matches[3];
            if (strpos($attrs, 'rel=') === false) {
                $attrs .= ' rel="noopener"';
            } else {
                $attrs = preg_replace('/rel="([^"]*)"/', 'rel="$1 noopener"', $attrs);
            }
            return '<a' . $matches[1] . 'href="' . $matches[2] . '"' . $matches[3] . $attrs . '>';
        },
        $content
    );
    return $content;
}
add_filter('the_content', 'zatra_add_noopener_to_external_links');

/**
 * Generate XML sitemap (basic implementation)
 */
function zatra_generate_sitemap() {
    if (isset($_GET['sitemap']) && $_GET['sitemap'] === 'xml') {
        header('Content-Type: application/xml; charset=utf-8');
        
        echo '<?xml version="1.0" encoding="UTF-8"?>';
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
        
        // Home page
        echo '<url>';
        echo '<loc>' . esc_url(home_url()) . '</loc>';
        echo '<lastmod>' . date('Y-m-d') . '</lastmod>';
        echo '<changefreq>daily</changefreq>';
        echo '<priority>1.0</priority>';
        echo '</url>';
        
        // Pages
        $pages = get_pages(array('post_status' => 'publish'));
        foreach ($pages as $page) {
            $noindex = get_post_meta($page->ID, '_seo_noindex', true);
            if (!$noindex) {
                echo '<url>';
                echo '<loc>' . esc_url(get_permalink($page->ID)) . '</loc>';
                echo '<lastmod>' . date('Y-m-d', strtotime($page->post_modified)) . '</lastmod>';
                echo '<changefreq>weekly</changefreq>';
                echo '<priority>0.8</priority>';
                echo '</url>';
            }
        }
        
        echo '</urlset>';
        exit;
    }
}
add_action('init', 'zatra_generate_sitemap');

/**
 * Add performance optimizations for SEO
 */
function zatra_performance_optimizations() {
    // Remove unnecessary WordPress features
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    
    // Remove emoji scripts for better performance
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('admin_print_styles', 'print_emoji_styles');
    
    // Remove WordPress version from RSS feeds
    add_filter('the_generator', '__return_empty_string');
}
add_action('init', 'zatra_performance_optimizations');

/**
 * Add schema markup for organization
 */
function zatra_organization_schema() {
    if (is_front_page()) {
        ?>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "<?php echo esc_js(get_bloginfo('name')); ?>",
            "description": "<?php echo esc_js(get_bloginfo('description')); ?>",
            "url": "<?php echo esc_url(home_url()); ?>",
            "logo": "<?php echo esc_url(get_template_directory_uri() . '/assets/images/logo.png'); ?>",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+1-555-0123",
                "contactType": "Customer Service"
            }
        }
        </script>
        <?php
    }
}
add_action('wp_head', 'zatra_organization_schema');

/**
 * Enhance page loading speed with resource optimization
 */
function zatra_optimize_resources() {
    // Defer non-critical JavaScript
    add_filter('script_loader_tag', function($tag, $handle) {
        if (in_array($handle, array('chart-js', 'stock-scanner-advanced-charts'))) {
            return str_replace(' src', ' defer src', $tag);
        }
        return $tag;
    }, 10, 2);
    
    // Add preload for critical resources
    add_action('wp_head', function() {
        echo '<link rel="preload" href="' . get_stylesheet_uri() . '" as="style">';
    }, 1);
}
add_action('init', 'zatra_optimize_resources');

/**
 * Add custom robots.txt content
 */
function zatra_custom_robots_txt($output, $public) {
    if ($public) {
        $robots_content = file_get_contents(get_template_directory() . '/robots.txt');
        if ($robots_content) {
            $robots_content = str_replace('{SITE_URL}', home_url(), $robots_content);
            return $robots_content;
        }
    }
    return $output;
}
add_filter('robots_txt', 'zatra_custom_robots_txt', 10, 2);

/**
 * Add breadcrumbs to page templates
 */
function zatra_add_breadcrumbs_to_pages() {
    if (is_page() && !is_front_page()) {
        add_action('wp_head', function() {
            echo '<script type="application/ld+json">';
            echo '{';
            echo '"@context": "https://schema.org",';
            echo '"@type": "BreadcrumbList",';
            echo '"itemListElement": [';
            echo '{';
            echo '"@type": "ListItem",';
            echo '"position": 1,';
            echo '"name": "' . esc_js(get_bloginfo('name')) . '",';
            echo '"item": "' . esc_url(home_url()) . '"';
            echo '}';
            if (is_page()) {
                echo ',{';
                echo '"@type": "ListItem",';
                echo '"position": 2,';
                echo '"name": "' . esc_js(get_the_title()) . '",';
                echo '"item": "' . esc_url(get_permalink()) . '"';
                echo '}';
            }
            echo ']';
            echo '}';
            echo '</script>';
        });
    }
}
add_action('wp', 'zatra_add_breadcrumbs_to_pages');

/**
 * Add financial sector specific meta tags
 */
function zatra_financial_meta_tags() {
    echo '<meta name="rating" content="general">';
    echo '<meta name="distribution" content="global">';
    echo '<meta name="revisit-after" content="1 days">';
    echo '<meta name="language" content="en">';
    echo '<meta name="classification" content="finance, business, investment, stock market">';
    echo '<meta name="subject" content="Stock Market Analysis and Investment Tools">';
    echo '<meta name="copyright" content="' . esc_attr(get_bloginfo('name')) . '">';
    
    // Financial specific meta tags
    if (is_page_template(array('page-market-overview.php', 'page-stock-screener.php', 'page-portfolio.php'))) {
        echo '<meta name="financial-service" content="investment-analysis">';
        echo '<meta name="market-data" content="real-time">';
        echo '<meta name="investment-disclaimer" content="true">';
    }
}
add_action('wp_head', 'zatra_financial_meta_tags', 15);

// Ensure critical pages use the correct templates even if they pre-exist
add_action('init', function() {
	$map = array(
		'compare-plans' => 'page-compare-plans.php',
		'paypal-checkout' => 'page-paypal-checkout.php',
		'payment-success' => 'page-payment-success.php',
		'payment-cancelled' => 'page-payment-cancelled.php'
	);
	foreach ($map as $slug => $template_file) {
		$page = get_page_by_path($slug);
		if ($page && get_post_meta($page->ID, '_wp_page_template', true) !== $template_file) {
			update_post_meta($page->ID, '_wp_page_template', $template_file);
		}
	}
});
