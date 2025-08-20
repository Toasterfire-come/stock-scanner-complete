<?php
/**
 * Stock Scanner Pro Theme Functions
 *
 * @package StockScannerPro
 * @version 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Theme version for cache busting
define('STOCK_SCANNER_VERSION', '1.0.0');

// Theme directory paths
define('STOCK_SCANNER_THEME_DIR', get_template_directory());
define('STOCK_SCANNER_THEME_URL', get_template_directory_uri());

/**
 * Theme Setup
 */
function stock_scanner_setup() {
    // Add theme support
    add_theme_support('post-thumbnails');
    add_theme_support('title-tag');
    add_theme_support('custom-logo');
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ));

    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Navigation', 'stock-scanner-pro'),
        'dashboard' => __('Dashboard Navigation', 'stock-scanner-pro'),
        'footer' => __('Footer Navigation', 'stock-scanner-pro'),
    ));

    // Add support for responsive embeds
    add_theme_support('responsive-embeds');

    // Set content width
    if (!isset($content_width)) {
        $content_width = 1200;
    }
}
add_action('after_setup_theme', 'stock_scanner_setup');

/**
 * Enqueue Scripts and Styles
 */
function stock_scanner_scripts() {
    // Main stylesheet
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), STOCK_SCANNER_VERSION);
    
    // Dashboard styles
    wp_enqueue_style('stock-scanner-dashboard', 
        STOCK_SCANNER_THEME_URL . '/assets/css/dashboard.css', 
        array('stock-scanner-style'), 
        STOCK_SCANNER_VERSION
    );

    // Charts CSS
    wp_enqueue_style('stock-scanner-charts', 
        STOCK_SCANNER_THEME_URL . '/assets/css/charts.css', 
        array(), 
        STOCK_SCANNER_VERSION
    );

    // Font Awesome
    wp_enqueue_style('font-awesome', 
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css', 
        array(), 
        '6.4.0'
    );

    // Chart.js
    wp_enqueue_script('chart-js', 
        'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js', 
        array(), 
        '4.4.0', 
        true
    );

    // API integration
    wp_enqueue_script('stock-scanner-api', 
        STOCK_SCANNER_THEME_URL . '/assets/js/api.js', 
        array('jquery'), 
        STOCK_SCANNER_VERSION, 
        true
    );

    // Dashboard functionality
    wp_enqueue_script('stock-scanner-dashboard', 
        STOCK_SCANNER_THEME_URL . '/assets/js/dashboard.js', 
        array('jquery', 'stock-scanner-api'), 
        STOCK_SCANNER_VERSION, 
        true
    );

    // Chart functionality
    wp_enqueue_script('stock-scanner-charts', 
        STOCK_SCANNER_THEME_URL . '/assets/js/charts.js', 
        array('chart-js'), 
        STOCK_SCANNER_VERSION, 
        true
    );

    // Main theme JavaScript
    wp_enqueue_script('stock-scanner-main', 
        STOCK_SCANNER_THEME_URL . '/assets/js/main.js', 
        array('jquery'), 
        STOCK_SCANNER_VERSION, 
        true
    );

    // Localize scripts with API configuration
    wp_localize_script('stock-scanner-api', 'stockScannerConfig', array(
        'apiUrl' => get_option('stock_scanner_api_url', 'http://localhost:8000/api'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'userLoggedIn' => is_user_logged_in(),
        'userId' => get_current_user_id(),
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Admin Scripts and Styles
 */
function stock_scanner_admin_scripts($hook) {
    wp_enqueue_style('stock-scanner-admin', 
        STOCK_SCANNER_THEME_URL . '/assets/css/admin.css', 
        array(), 
        STOCK_SCANNER_VERSION
    );
}
add_action('admin_enqueue_scripts', 'stock_scanner_admin_scripts');

/**
 * Include Required Files
 */
require_once STOCK_SCANNER_THEME_DIR . '/includes/api-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/user-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/stock-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/chart-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/security-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/portfolio-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/watchlist-functions.php';
require_once STOCK_SCANNER_THEME_DIR . '/includes/realtime-functions.php';

/**
 * Widget Areas
 */
function stock_scanner_widgets_init() {
    register_sidebar(array(
        'name' => __('Sidebar', 'stock-scanner-pro'),
        'id' => 'sidebar-1',
        'description' => __('Add widgets here to appear in your sidebar.', 'stock-scanner-pro'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));

    register_sidebar(array(
        'name' => __('Dashboard Sidebar', 'stock-scanner-pro'),
        'id' => 'dashboard-sidebar',
        'description' => __('Widgets for dashboard pages.', 'stock-scanner-pro'),
        'before_widget' => '<div id="%1$s" class="dashboard-widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h4 class="dashboard-widget-title">',
        'after_title' => '</h4>',
    ));
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * Custom Post Types
 */
function stock_scanner_register_post_types() {
    // Stock Alerts Post Type
    register_post_type('stock_alert', array(
        'labels' => array(
            'name' => __('Stock Alerts', 'stock-scanner-pro'),
            'singular_name' => __('Stock Alert', 'stock-scanner-pro'),
        ),
        'public' => false,
        'show_ui' => true,
        'show_in_menu' => true,
        'capability_type' => 'post',
        'supports' => array('title', 'editor', 'custom-fields'),
    ));

    // Market News Post Type
    register_post_type('market_news', array(
        'labels' => array(
            'name' => __('Market News', 'stock-scanner-pro'),
            'singular_name' => __('Market News', 'stock-scanner-pro'),
        ),
        'public' => true,
        'show_in_rest' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'has_archive' => true,
        'rewrite' => array('slug' => 'market-news'),
    ));
}
add_action('init', 'stock_scanner_register_post_types');

/**
 * Theme Options Page
 */
function stock_scanner_add_theme_options() {
    add_theme_page(
        __('Stock Scanner Options', 'stock-scanner-pro'),
        __('Theme Options', 'stock-scanner-pro'),
        'manage_options',
        'stock-scanner-options',
        'stock_scanner_options_page'
    );
}
add_action('admin_menu', 'stock_scanner_add_theme_options');

function stock_scanner_options_page() {
    if (isset($_POST['submit'])) {
        update_option('stock_scanner_api_url', sanitize_url($_POST['api_url']));
        update_option('stock_scanner_api_key', sanitize_text_field($_POST['api_key']));
        update_option('stock_scanner_cache_timeout', intval($_POST['cache_timeout']));
        echo '<div class="notice notice-success"><p>' . __('Settings saved!', 'stock-scanner-pro') . '</p></div>';
    }

    $api_url = get_option('stock_scanner_api_url', 'http://localhost:8000/api');
    $api_key = get_option('stock_scanner_api_key', '');
    $cache_timeout = get_option('stock_scanner_cache_timeout', 300);
    ?>
    <div class="wrap">
        <h1><?php _e('Stock Scanner Theme Options', 'stock-scanner-pro'); ?></h1>
        <form method="post" action="">
            <table class="form-table">
                <tr>
                    <th scope="row"><?php _e('API URL', 'stock-scanner-pro'); ?></th>
                    <td>
                        <input type="url" name="api_url" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
                        <p class="description"><?php _e('Django backend API base URL', 'stock-scanner-pro'); ?></p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><?php _e('API Key', 'stock-scanner-pro'); ?></th>
                    <td>
                        <input type="password" name="api_key" value="<?php echo esc_attr($api_key); ?>" class="regular-text" />
                        <p class="description"><?php _e('API authentication key', 'stock-scanner-pro'); ?></p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><?php _e('Cache Timeout (seconds)', 'stock-scanner-pro'); ?></th>
                    <td>
                        <input type="number" name="cache_timeout" value="<?php echo esc_attr($cache_timeout); ?>" min="60" max="3600" />
                        <p class="description"><?php _e('How long to cache API responses', 'stock-scanner-pro'); ?></p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

/**
 * AJAX Handlers
 */
function stock_scanner_ajax_get_stock_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $ticker = sanitize_text_field($_POST['ticker']);
    $stock_data = stock_scanner_get_stock_data($ticker);
    
    wp_send_json_success($stock_data);
}
add_action('wp_ajax_get_stock_data', 'stock_scanner_ajax_get_stock_data');
add_action('wp_ajax_nopriv_get_stock_data', 'stock_scanner_ajax_get_stock_data');

function stock_scanner_ajax_get_market_overview() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $market_data = stock_scanner_get_market_overview();
    
    wp_send_json_success($market_data);
}
add_action('wp_ajax_get_market_overview', 'stock_scanner_ajax_get_market_overview');
add_action('wp_ajax_nopriv_get_market_overview', 'stock_scanner_ajax_get_market_overview');

/**
 * Body Classes
 */
function stock_scanner_body_classes($classes) {
    // Add page template class
    if (is_page_template()) {
        $template = get_page_template_slug();
        $template_class = 'page-template-' . str_replace(array('.php', '/', '_'), array('', '-', '-'), $template);
        $classes[] = $template_class;
    }

    // Add user authentication class
    if (is_user_logged_in()) {
        $classes[] = 'user-logged-in';
    } else {
        $classes[] = 'user-logged-out';
    }

    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Custom Login Styling
 */
function stock_scanner_login_styles() {
    wp_enqueue_style('stock-scanner-login', 
        STOCK_SCANNER_THEME_URL . '/assets/css/login.css', 
        array(), 
        STOCK_SCANNER_VERSION
    );
}
add_action('login_enqueue_scripts', 'stock_scanner_login_styles');

/**
 * Security Headers
 */
function stock_scanner_security_headers() {
    if (!is_admin()) {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}
add_action('send_headers', 'stock_scanner_security_headers');

/**
 * Remove unnecessary WordPress features for security
 */
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'rsd_link');

/**
 * Disable file editing in admin
 */
if (!defined('DISALLOW_FILE_EDIT')) {
    define('DISALLOW_FILE_EDIT', true);
}

/**
 * Additional AJAX Handlers for Portfolio and Watchlist
 */

// Portfolio AJAX handlers
function stock_scanner_ajax_add_to_portfolio() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $ticker = sanitize_text_field($_POST['ticker'] ?? '');
    $shares = floatval($_POST['shares'] ?? 0);
    $cost_basis = floatval($_POST['cost_basis'] ?? 0);
    $purchase_date = sanitize_text_field($_POST['purchase_date'] ?? '');
    
    $result = stock_scanner_add_to_portfolio($user_id, $ticker, $shares, $cost_basis, $purchase_date);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_add_to_portfolio', 'stock_scanner_ajax_add_to_portfolio');

function stock_scanner_ajax_remove_from_portfolio() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $holding_id = intval($_POST['holding_id'] ?? 0);
    
    $result = stock_scanner_remove_from_portfolio($user_id, $holding_id);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_remove_from_portfolio', 'stock_scanner_ajax_remove_from_portfolio');

function stock_scanner_ajax_get_portfolio() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $result = stock_scanner_get_user_portfolio_complete($user_id);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_get_portfolio', 'stock_scanner_ajax_get_portfolio');

// Watchlist AJAX handlers
function stock_scanner_ajax_add_to_watchlist() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $ticker = sanitize_text_field($_POST['ticker'] ?? '');
    $notes = sanitize_textarea_field($_POST['notes'] ?? '');
    $category = sanitize_text_field($_POST['category'] ?? 'default');
    
    $result = stock_scanner_add_to_watchlist($user_id, $ticker, $notes, $category);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_add_to_watchlist', 'stock_scanner_ajax_add_to_watchlist');

function stock_scanner_ajax_remove_from_watchlist() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $item_id = intval($_POST['item_id'] ?? 0);
    
    $result = stock_scanner_remove_from_watchlist($user_id, $item_id);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_remove_from_watchlist', 'stock_scanner_ajax_remove_from_watchlist');

function stock_scanner_ajax_get_watchlist() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $result = stock_scanner_get_user_watchlist_complete($user_id);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_get_watchlist', 'stock_scanner_ajax_get_watchlist');

// Price Alert AJAX handlers
function stock_scanner_ajax_create_price_alert() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    if (!is_user_logged_in()) {
        wp_send_json_error('User not authenticated');
        return;
    }
    
    $user_id = get_current_user_id();
    $ticker = sanitize_text_field($_POST['ticker'] ?? '');
    $target_price = floatval($_POST['target_price'] ?? 0);
    $condition = sanitize_text_field($_POST['condition'] ?? '');
    $email = sanitize_email($_POST['email'] ?? '');
    
    $result = stock_scanner_create_price_alert($user_id, $ticker, $target_price, $condition, $email);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_stock_scanner_create_price_alert', 'stock_scanner_ajax_create_price_alert');

/**
 * Theme activation hook
 */
function stock_scanner_theme_activation() {
    // Create necessary pages
    $pages = array(
        'Dashboard' => 'page-templates/page-dashboard.php',
        'Market Overview' => 'page-templates/page-market-overview.php',
        'Portfolio' => 'page-templates/page-portfolio.php',
        'Watchlist' => 'page-templates/page-watchlist.php',
        'Stock Lookup' => 'page-templates/page-stock-lookup.php',
        'Account Settings' => 'page-templates/page-user-settings.php',
    );

    foreach ($pages as $title => $template) {
        $page_check = get_page_by_title($title);
        if (!isset($page_check->ID)) {
            $page_data = array(
                'post_type' => 'page',
                'post_title' => $title,
                'post_content' => '',
                'post_status' => 'publish',
                'post_author' => 1,
                'post_slug' => sanitize_title($title),
                'page_template' => $template
            );
            $page_id = wp_insert_post($page_data);
            
            if (!is_wp_error($page_id)) {
                update_post_meta($page_id, '_wp_page_template', $template);
            }
        }
    }

    // Set default options
    if (!get_option('stock_scanner_api_url')) {
        update_option('stock_scanner_api_url', 'http://localhost:8000/api');
    }
    if (!get_option('stock_scanner_cache_timeout')) {
        update_option('stock_scanner_cache_timeout', 300);
    }
    
    // Create database tables
    stock_scanner_create_portfolio_table();
    stock_scanner_create_watchlist_table();
    stock_scanner_create_alerts_table();
}
add_action('after_switch_theme', 'stock_scanner_theme_activation');