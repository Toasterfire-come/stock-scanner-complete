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
	// Add default posts and comments RSS feed links to head.
	add_theme_support( 'automatic-feed-links' );

	// Let WordPress manage the document title.
	add_theme_support( 'title-tag' );

	// Enable support for Post Thumbnails.
	add_theme_support( 'post-thumbnails' );
    
    // Make theme available for translation.
	load_theme_textdomain( 'stock-scanner-zatra' );

	// Admin editor styles.
	add_theme_support( 'editor-styles' );

	// Switch default core markup for different forms to output valid HTML5.
	add_theme_support( 'html5', array( 'comment-form', 'comment-list', 'search-form', 'gallery', 'caption' ) );

	// Add support for responsive embeds.
	add_theme_support( 'responsive-embeds' );

	// Add theme support for selective refresh for widgets.
	add_theme_support( 'customize-selective-refresh-widgets' );

	// Enable block styles.
	add_theme_support( 'wp-block-styles' );
	
	// Enable wide alignment
	add_theme_support( 'align-wide' );

	// Enqueue editor styles.
	add_editor_style();
	
	// Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner-zatra'),
        'footer' => __('Footer Menu', 'stock-scanner-zatra'),
        'mobile' => __('Mobile Menu', 'stock-scanner-zatra'),
    ));
    
    // Set content width for responsive images
    $GLOBALS['content_width'] = 1200;
}
add_action( 'after_setup_theme', 'stock_scanner_zatra_setup' );

/**
 * Enqueue scripts and styles.
 */
function stock_scanner_zatra_scripts() {
	// Font Awesome
	wp_enqueue_style('font-awesome', get_template_directory_uri() . '/assets/framework/font-awesome-6/css/all.css', array());
	wp_enqueue_style('font-awesome-min', get_template_directory_uri() . '/assets/framework/font-awesome-6/css/all.min.css', array());
	
	// Theme stylesheet
	$style_file = get_stylesheet_directory() . '/style.css';
    $style_ver = file_exists($style_file) ? filemtime($style_file) : '1.0.0';
	wp_enqueue_style( 'stock-scanner-zatra-style', get_stylesheet_uri(), array(), $style_ver);
	
	// Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Theme JavaScript
    wp_enqueue_script(
        'stock-scanner-zatra-js',
        get_template_directory_uri() . '/assets/js/theme.js',
        array('jquery', 'chart-js'),
        $style_ver,
        true
    );
    
    // Localize script with theme settings
    wp_localize_script('stock-scanner-zatra-js', 'stockScannerTheme', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'theme_url' => get_template_directory_uri(),
    ));
}
add_action( 'wp_enqueue_scripts', 'stock_scanner_zatra_scripts' );

/**
 * Register block patterns category.
 */
function stock_scanner_zatra_register_block_patterns_category() {
	register_block_pattern_category(
		'stock-scanner-zatra',
		array(
			'label' => esc_html__( 'Stock Scanner Pro', 'stock-scanner-zatra' ),
		)
	);
}
add_action( 'init', 'stock_scanner_zatra_register_block_patterns_category', 9 );

/**
 * Backend API Integration Functions
 */

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
    $api_url = get_backend_api_url($endpoint);
    $api_key = $api_settings['api_key'] ?? '';
    $timeout = $api_settings['timeout'] ?? 30;
    
    if (!$api_url) {
        return new WP_Error('no_backend_url', 'Backend URL not configured');
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
    
    $response = wp_remote_request($api_url, $args);
    
    if (is_wp_error($response)) {
        return $response;
    }
    
    $status_code = wp_remote_retrieve_response_code($response);
    $body = wp_remote_retrieve_body($response);
    
    if ($status_code >= 400) {
        return new WP_Error('api_error', "API request failed with status $status_code: $body");
    }
    
    return json_decode($body, true);
}

/**
 * Check if user is authenticated
 */
function is_user_authenticated() {
    return is_user_logged_in();
}

/**
 * Get user subscription status
 */
function get_user_subscription_status() {
    if (!is_user_logged_in()) {
        return 'guest';
    }
    
    $user_meta = get_user_meta(get_current_user_id(), 'subscription_status', true);
    return $user_meta ?: 'free';
}

/**
 * Check if user has premium access
 */
function user_has_premium_access() {
    $status = get_user_subscription_status();
    return in_array($status, ['premium', 'pro', 'enterprise']);
}

/**
 * Redirect to login if not authenticated
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
    return make_backend_api_request('stocks/' . $symbol);
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
    
    return make_backend_api_request('watchlist', array('user_id' => $user_id));
}

/**
 * Add custom body classes
 */
function stock_scanner_zatra_body_classes($classes) {
    $classes[] = 'stock-scanner-theme';
    
    if (user_has_premium_access()) {
        $classes[] = 'premium-user';
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_zatra_body_classes');

/**
 * Custom page templates redirect handling
 */
function stock_scanner_zatra_template_redirect() {
    // Handle authentication requirements for protected pages
    $protected_pages = array('dashboard', 'portfolio', 'account', 'billing-history', 'user-settings', 'watchlist');
    
    foreach ($protected_pages as $page) {
        if (is_page($page)) {
            require_authentication();
            break;
        }
    }
}
add_action('template_redirect', 'stock_scanner_zatra_template_redirect');
