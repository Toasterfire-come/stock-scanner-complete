<?php
/**
 * Stock Scanner Pro - Zatra Edition Functions
 * 
 * Complete theme setup with backend integration, page management, and premium features
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme Setup
 */
function stock_scanner_pro_setup() {
    // Add theme support
    add_theme_support('automatic-feed-links');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('responsive-embeds');
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
    add_theme_support('editor-styles');
    
    // Make theme available for translation
    load_theme_textdomain('stock-scanner-pro', get_template_directory() . '/languages');
    
    // Add editor styles
    add_editor_style();
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner-pro'),
        'footer' => __('Footer Menu', 'stock-scanner-pro'),
        'user-account' => __('User Account Menu', 'stock-scanner-pro'),
    ));
}
add_action('after_setup_theme', 'stock_scanner_pro_setup');

/**
 * Enqueue Scripts and Styles
 */
function stock_scanner_pro_scripts() {
    // Theme styles (maintain original Zatra styling)
    wp_enqueue_style('zatra-style', get_stylesheet_uri(), array(), wp_get_theme()->get('Version'));
    
    // Font Awesome
    wp_enqueue_style('font-awesome', get_template_directory_uri() . '/assets/framework/font-awesome-6/css/all.css', array(), '6.0.0');
    
    // Stock Scanner Pro enhanced styles
    wp_enqueue_style('stock-scanner-pro-css', get_template_directory_uri() . '/assets/css/stock-scanner-pro.css', array('zatra-style'), wp_get_theme()->get('Version'));
    
    // Chart.js for advanced charts
    wp_enqueue_script('chartjs', 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js', array(), '3.9.1', true);
    
    // Theme JavaScript
    wp_enqueue_script('stock-scanner-pro-main', get_template_directory_uri() . '/assets/js/main.js', array('jquery', 'chartjs'), wp_get_theme()->get('Version'), true);
    
    // Localize script for AJAX
    wp_localize_script('stock-scanner-pro-main', 'stockScannerAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'backend_url' => get_backend_api_url(),
        'user_tier' => get_user_tier(),
        'rate_limits' => get_user_rate_limits()
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_pro_scripts');

/**
 * Backend API Integration Functions
 */
function get_backend_api_url($endpoint = '') {
    $api_settings = get_option('stock_scanner_api_settings', array());
    $backend_url = $api_settings['backend_url'] ?? 'http://localhost:8000';
    if (empty($backend_url)) {
        $backend_url = 'http://localhost:8000';
    }
    return rtrim($backend_url, '/') . '/api/' . ltrim($endpoint, '/');
}

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
 * User Tier Management
 */
function get_user_tier($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return 'free';
    }
    
    return get_user_meta($user_id, 'subscription_tier', true) ?: 'free';
}

function get_user_rate_limits($user_id = null) {
    $tier = get_user_tier($user_id);
    
    $limits = array(
        'free' => array(
            'api_calls_per_month' => 15,
            'max_watchlist_items' => 3,
            'real_time_data' => false,
            'advanced_charts' => false,
            'data_export' => false
        ),
        'basic' => array(
            'api_calls_per_month' => 1500,
            'max_watchlist_items' => 25,
            'real_time_data' => true,
            'advanced_charts' => true,
            'data_export' => true
        ),
        'pro' => array(
            'api_calls_per_month' => 5000,
            'max_watchlist_items' => 100,
            'real_time_data' => true,
            'advanced_charts' => true,
            'data_export' => true
        ),
        'enterprise' => array(
            'api_calls_per_month' => 999999,
            'max_watchlist_items' => 9999,
            'real_time_data' => true,
            'advanced_charts' => true,
            'data_export' => true
        )
    );
    
    return $limits[$tier] ?? $limits['free'];
}

/**
 * Create All Required Pages on Theme Activation
 */
function create_stock_scanner_pages() {
    $pages = array(
        // Core Pages
        'home' => array(
            'title' => 'Stock Scanner Pro - Home',
            'content' => '[stock_scanner_homepage]',
            'template' => 'page-home.php'
        ),
        'dashboard' => array(
            'title' => 'Dashboard',
            'content' => '[stock_scanner_dashboard]',
            'template' => 'page-dashboard.php'
        ),
        'stock-lookup' => array(
            'title' => 'Stock Lookup',
            'content' => '[stock_lookup_tool]',
            'template' => 'page-stock-lookup.php'
        ),
        'stock-news' => array(
            'title' => 'Stock News',
            'content' => '[stock_news_feed]',
            'template' => 'page-stock-news.php'
        ),
        'stock-screener' => array(
            'title' => 'Stock Screener',
            'content' => '[stock_screener_tool]',
            'template' => 'page-stock-screener.php'
        ),
        'market-overview' => array(
            'title' => 'Market Overview',
            'content' => '[market_overview_dashboard]',
            'template' => 'page-market-overview.php'
        ),
        'watchlist' => array(
            'title' => 'My Watchlist',
            'content' => '[user_watchlist]',
            'template' => 'page-watchlist.php'
        ),
        
        // Portfolio & Account
        'portfolio' => array(
            'title' => 'My Portfolio',
            'content' => '[user_portfolio]',
            'template' => 'page-portfolio.php'
        ),
        'account' => array(
            'title' => 'My Account',
            'content' => '[user_account_dashboard]',
            'template' => 'page-account.php'
        ),
        'billing-history' => array(
            'title' => 'Billing History',
            'content' => '[billing_history]',
            'template' => 'page-billing-history.php'
        ),
        'user-settings' => array(
            'title' => 'User Settings',
            'content' => '[user_settings_panel]',
            'template' => 'page-user-settings.php'
        ),
        
        // Premium & Payment
        'premium-plans' => array(
            'title' => 'Premium Plans',
            'content' => '[premium_plans_comparison]',
            'template' => 'page-premium-plans.php'
        ),
        'paypal-checkout' => array(
            'title' => 'PayPal Checkout',
            'content' => '[paypal_checkout_form]',
            'template' => 'page-paypal-checkout.php'
        ),
        'payment-success' => array(
            'title' => 'Payment Success',
            'content' => '[payment_success_message]',
            'template' => 'page-payment-success.php'
        ),
        'payment-cancelled' => array(
            'title' => 'Payment Cancelled',
            'content' => '[payment_cancelled_message]',
            'template' => 'page-payment-cancelled.php'
        ),
        'compare-plans' => array(
            'title' => 'Compare Plans',
            'content' => '[plans_comparison_table]',
            'template' => 'page-compare-plans.php'
        ),
        
        // User Access
        'login' => array(
            'title' => 'Login',
            'content' => '[custom_login_form]',
            'template' => 'page-login.php'
        ),
        'signup' => array(
            'title' => 'Sign Up',
            'content' => '[custom_signup_form]',
            'template' => 'page-signup.php'
        ),
        
        // Help & Support
        'contact' => array(
            'title' => 'Contact Us',
            'content' => '[contact_form]',
            'template' => 'page-contact.php'
        ),
        'faq' => array(
            'title' => 'FAQ',
            'content' => '[faq_accordion]',
            'template' => 'page-faq.php'
        ),
        'help-center' => array(
            'title' => 'Help Center',
            'content' => '[help_center_hub]',
            'template' => 'page-help-center.php'
        ),
        'getting-started' => array(
            'title' => 'Getting Started',
            'content' => '[getting_started_guide]',
            'template' => 'page-getting-started.php'
        ),
        'how-it-works' => array(
            'title' => 'How It Works',
            'content' => '[how_it_works_explanation]',
            'template' => 'page-how-it-works.php'
        ),
        'glossary' => array(
            'title' => 'Glossary',
            'content' => '[financial_glossary]',
            'template' => 'page-glossary.php'
        ),
        'market-hours' => array(
            'title' => 'Market Hours',
            'content' => '[market_hours_display]',
            'template' => 'page-market-hours.php'
        ),
        
        // Legal Pages
        'privacy-policy' => array(
            'title' => 'Privacy Policy',
            'content' => '[privacy_policy_content]',
            'template' => 'page-privacy-policy.php'
        ),
        'terms-of-service' => array(
            'title' => 'Terms of Service',
            'content' => '[terms_of_service_content]',
            'template' => 'page-terms-of-service.php'
        ),
        'cookie-policy' => array(
            'title' => 'Cookie Policy',
            'content' => '[cookie_policy_content]',
            'template' => 'page-cookie-policy.php'
        ),
        
        // Personalized Features
        'personalized-news' => array(
            'title' => 'Personalized News',
            'content' => '[personalized_news_feed]',
            'template' => 'page-personalized-news.php'
        )
    );
    
    foreach ($pages as $slug => $page_data) {
        // Check if page already exists
        $existing_page = get_page_by_path($slug);
        
        if (!$existing_page) {
            $page_id = wp_insert_post(array(
                'post_title' => $page_data['title'],
                'post_content' => $page_data['content'],
                'post_status' => 'publish',
                'post_type' => 'page',
                'post_name' => $slug,
                'post_author' => 1
            ));
            
            if ($page_id && !is_wp_error($page_id)) {
                // Set custom template
                update_post_meta($page_id, '_wp_page_template', $page_data['template']);
                
                // Set as homepage if it's the home page
                if ($slug === 'home') {
                    update_option('show_on_front', 'page');
                    update_option('page_on_front', $page_id);
                }
            }
        }
    }
    
    // Create navigation menu
    create_stock_scanner_menu();
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

/**
 * Create Navigation Menu
 */
function create_stock_scanner_menu() {
    $menu_name = 'Stock Scanner Pro Menu';
    $menu_exists = wp_get_nav_menu_object($menu_name);
    
    if (!$menu_exists) {
        $menu_id = wp_create_nav_menu($menu_name);
        
        $menu_items = array(
            array('title' => 'Home', 'url' => home_url('/home/')),
            array('title' => 'Dashboard', 'url' => home_url('/dashboard/')),
            array('title' => 'Stock Lookup', 'url' => home_url('/stock-lookup/')),
            array('title' => 'Screener', 'url' => home_url('/stock-screener/')),
            array('title' => 'Market Overview', 'url' => home_url('/market-overview/')),
            array('title' => 'Watchlist', 'url' => home_url('/watchlist/')),
            array('title' => 'Portfolio', 'url' => home_url('/portfolio/')),
            array('title' => 'Premium', 'url' => home_url('/premium-plans/')),
            array('title' => 'Help', 'url' => home_url('/help-center/'))
        );
        
        foreach ($menu_items as $item) {
            wp_update_nav_menu_item($menu_id, 0, array(
                'menu-item-title' => $item['title'],
                'menu-item-url' => $item['url'],
                'menu-item-status' => 'publish'
            ));
        }
        
        // Assign menu to location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['primary'] = $menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
}

/**
 * Delete All Pages on Theme Deactivation
 */
function delete_stock_scanner_pages() {
    $page_slugs = array(
        'home', 'dashboard', 'stock-lookup', 'stock-news', 'stock-screener', 
        'market-overview', 'watchlist', 'portfolio', 'account', 'billing-history',
        'user-settings', 'premium-plans', 'paypal-checkout', 'payment-success',
        'payment-cancelled', 'compare-plans', 'login', 'signup', 'contact',
        'faq', 'help-center', 'getting-started', 'how-it-works', 'glossary',
        'market-hours', 'privacy-policy', 'terms-of-service', 'cookie-policy',
        'personalized-news'
    );
    
    foreach ($page_slugs as $slug) {
        $page = get_page_by_path($slug);
        if ($page) {
            wp_delete_post($page->ID, true);
        }
    }
}

/**
 * Theme Activation Hook
 */
function stock_scanner_pro_activation() {
    // Delete existing pages first
    delete_stock_scanner_pages();
    
    // Create new pages
    create_stock_scanner_pages();
    
    // Set default options
    update_option('stock_scanner_theme_activated', true);
    update_option('stock_scanner_api_settings', array(
        'backend_url' => 'http://localhost:8000',
        'api_key' => '',
        'timeout' => 30
    ));
}
add_action('after_switch_theme', 'stock_scanner_pro_activation');

/**
 * Theme Deactivation Hook
 */
function stock_scanner_pro_deactivation() {
    delete_stock_scanner_pages();
    delete_option('stock_scanner_theme_activated');
}
add_action('switch_theme', 'stock_scanner_pro_deactivation');

/**
 * Admin Settings Page
 */
function stock_scanner_admin_menu() {
    add_options_page(
        'Stock Scanner Pro Settings',
        'Stock Scanner Pro',
        'manage_options',
        'stock-scanner-pro',
        'stock_scanner_admin_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_menu');

function stock_scanner_admin_page() {
    if (isset($_POST['submit'])) {
        $settings = array(
            'backend_url' => sanitize_url($_POST['backend_url']),
            'api_key' => sanitize_text_field($_POST['api_key']),
            'timeout' => intval($_POST['timeout'])
        );
        update_option('stock_scanner_api_settings', $settings);
        echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
    }
    
    $settings = get_option('stock_scanner_api_settings', array());
    ?>
    <div class="wrap">
        <h1>Stock Scanner Pro Settings</h1>
        <form method="post" action="">
            <table class="form-table">
                <tr>
                    <th scope="row">Backend URL</th>
                    <td><input type="url" name="backend_url" value="<?php echo esc_attr($settings['backend_url'] ?? 'http://localhost:8000'); ?>" class="regular-text" /></td>
                </tr>
                <tr>
                    <th scope="row">API Key</th>
                    <td><input type="text" name="api_key" value="<?php echo esc_attr($settings['api_key'] ?? ''); ?>" class="regular-text" /></td>
                </tr>
                <tr>
                    <th scope="row">Timeout (seconds)</th>
                    <td><input type="number" name="timeout" value="<?php echo esc_attr($settings['timeout'] ?? 30); ?>" min="5" max="120" /></td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
        
        <h2>System Status</h2>
        <p><strong>Theme Version:</strong> <?php echo wp_get_theme()->get('Version'); ?></p>
        <p><strong>Pages Created:</strong> <?php echo get_option('stock_scanner_theme_activated') ? 'Yes' : 'No'; ?></p>
        <p><strong>Backend Connection:</strong> 
            <?php 
            $test = make_backend_api_request('health/');
            echo is_wp_error($test) ? '<span style="color: red;">Failed</span>' : '<span style="color: green;">Connected</span>';
            ?>
        </p>
    </div>
    <?php
}

/**
 * Register Block Patterns Category
 */
function stock_scanner_register_block_patterns_category() {
    register_block_pattern_category(
        'stock-scanner-pro',
        array(
            'label' => esc_html__('Stock Scanner Pro', 'stock-scanner-pro'),
        )
    );
}
add_action('init', 'stock_scanner_register_block_patterns_category', 9);

/**
 * Custom Body Classes
 */
function stock_scanner_body_classes($classes) {
    $user_tier = get_user_tier();
    $classes[] = 'user-tier-' . $user_tier;
    
    if (is_user_logged_in()) {
        $classes[] = 'user-logged-in';
    } else {
        $classes[] = 'user-logged-out';
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Shortcode Registration (will be implemented in separate files)
 */
function register_stock_scanner_shortcodes() {
    // Core functionality shortcodes
    add_shortcode('stock_scanner_homepage', 'render_homepage_shortcode');
    add_shortcode('stock_scanner_dashboard', 'render_dashboard_shortcode');
    add_shortcode('stock_lookup_tool', 'render_stock_lookup_shortcode');
    add_shortcode('stock_news_feed', 'render_stock_news_shortcode');
    add_shortcode('stock_screener_tool', 'render_stock_screener_shortcode');
    add_shortcode('market_overview_dashboard', 'render_market_overview_shortcode');
    add_shortcode('user_watchlist', 'render_watchlist_shortcode');
    add_shortcode('user_portfolio', 'render_portfolio_shortcode');
    add_shortcode('premium_plans_comparison', 'render_premium_plans_shortcode');
    add_shortcode('paypal_checkout_form', 'render_paypal_checkout_shortcode');
    
    // User management shortcodes
    add_shortcode('user_account_dashboard', 'render_account_dashboard_shortcode');
    add_shortcode('billing_history', 'render_billing_history_shortcode');
    add_shortcode('user_settings_panel', 'render_user_settings_shortcode');
    add_shortcode('custom_login_form', 'render_login_form_shortcode');
    add_shortcode('custom_signup_form', 'render_signup_form_shortcode');
    
    // Content shortcodes
    add_shortcode('contact_form', 'render_contact_form_shortcode');
    add_shortcode('faq_accordion', 'render_faq_shortcode');
    add_shortcode('help_center_hub', 'render_help_center_shortcode');
    add_shortcode('getting_started_guide', 'render_getting_started_shortcode');
    add_shortcode('how_it_works_explanation', 'render_how_it_works_shortcode');
    add_shortcode('financial_glossary', 'render_glossary_shortcode');
    add_shortcode('market_hours_display', 'render_market_hours_shortcode');
    
    // Legal shortcodes
    add_shortcode('privacy_policy_content', 'render_privacy_policy_shortcode');
    add_shortcode('terms_of_service_content', 'render_terms_shortcode');
    add_shortcode('cookie_policy_content', 'render_cookie_policy_shortcode');
    
    // Payment shortcodes
    add_shortcode('payment_success_message', 'render_payment_success_shortcode');
    add_shortcode('payment_cancelled_message', 'render_payment_cancelled_shortcode');
    add_shortcode('plans_comparison_table', 'render_plans_comparison_shortcode');
    
    // Personalized features
    add_shortcode('personalized_news_feed', 'render_personalized_news_shortcode');
}
add_action('init', 'register_stock_scanner_shortcodes');

// Include shortcode implementations
require_once get_template_directory() . '/inc/shortcodes.php';
