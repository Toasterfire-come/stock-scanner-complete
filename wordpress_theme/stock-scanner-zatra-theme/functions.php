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
