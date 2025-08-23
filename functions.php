<?php
/**
 * Stock Scanner Pro Theme Functions v3.0.0
 * COMPLETE JAVASCRIPT OVERHAUL - Enhanced Functions
 * 100% Vanilla JavaScript enforced across ALL PAGES
 * Advanced dependency chain and performance optimizations
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Theme constants
define('STOCK_SCANNER_VERSION', '3.0.0');
define('STOCK_SCANNER_THEME_DIR', get_template_directory());
define('STOCK_SCANNER_THEME_URI', get_template_directory_uri());

/**
 * Theme setup and support
 */
function stock_scanner_setup() {
    // Add theme support
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ));
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('responsive-embeds');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner'),
        'footer'  => __('Footer Menu', 'stock-scanner'),
    ));
    
    // Add custom image sizes
    add_image_size('stock-scanner-featured', 800, 450, true);
    add_image_size('stock-scanner-thumbnail', 300, 200, true);
}
add_action('after_setup_theme', 'stock_scanner_setup');

/**
 * ===== ENHANCED JAVASCRIPT LOADING v3.0.0 =====
 * ENFORCED ACROSS ALL PAGES with proper dependency chain
 */
function stock_scanner_enqueue_scripts() {
    // ===== REMOVE JQUERY COMPLETELY =====
    wp_deregister_script('jquery');
    wp_deregister_script('jquery-migrate');
    
    // ===== ENHANCED CSS LOADING =====
    // Main theme styles with higher version for cache busting
    wp_enqueue_style(
        'stock-scanner-style',
        get_stylesheet_uri(),
        array(),
        STOCK_SCANNER_VERSION . '-' . time(),
        'all'
    );
    
    // Enhanced premium styles - ENFORCED GLOBALLY
    wp_enqueue_style(
        'stock-scanner-enhanced-styles',
        STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css',
        array('stock-scanner-style'),
        STOCK_SCANNER_VERSION . '-enhanced',
        'all'
    );
    
    // ===== VANILLA JAVASCRIPT LOADING CHAIN =====
    // 1. Base enhanced theme functionality - LOADED ON ALL PAGES
    wp_enqueue_script(
        'stock-scanner-theme-enhanced',
        STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js',
        array(),
        STOCK_SCANNER_VERSION . '-enhanced',
        true
    );
    
    // 2. Advanced components - ENFORCED ON ALL PAGES
    wp_enqueue_script(
        'stock-scanner-advanced-components',
        STOCK_SCANNER_THEME_URI . '/assets/js/advanced-components.js',
        array('stock-scanner-theme-enhanced'),
        STOCK_SCANNER_VERSION . '-advanced',
        true
    );
    
    // 3. Performance optimized utilities - GLOBAL LOADING
    if (file_exists(STOCK_SCANNER_THEME_DIR . '/assets/js/performance-optimized-vanilla.js')) {
        wp_enqueue_script(
            'stock-scanner-performance',
            STOCK_SCANNER_THEME_URI . '/assets/js/performance-optimized-vanilla.js',
            array('stock-scanner-advanced-components'),
            STOCK_SCANNER_VERSION . '-performance',
            true
        );
    }
    
    // 4. Advanced UI components - PREMIUM FEATURES
    if (file_exists(STOCK_SCANNER_THEME_DIR . '/assets/js/advanced-ui-vanilla.js')) {
        wp_enqueue_script(
            'stock-scanner-advanced-ui',
            STOCK_SCANNER_THEME_URI . '/assets/js/advanced-ui-vanilla.js',
            array('stock-scanner-advanced-components'),
            STOCK_SCANNER_VERSION . '-ui',
            true
        );
    }
    
    // 5. Admin scripts (admin only)
    if (is_admin() && file_exists(STOCK_SCANNER_THEME_DIR . '/assets/js/admin-scripts.js')) {
        wp_enqueue_script(
            'stock-scanner-admin',
            STOCK_SCANNER_THEME_URI . '/assets/js/admin-scripts.js',
            array(),
            STOCK_SCANNER_VERSION . '-admin',
            true
        );
    }
    
    // ===== COMPREHENSIVE LOCALIZATION DATA =====
    $localize_data = array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'homeUrl' => home_url('/'),
        'themeUrl' => STOCK_SCANNER_THEME_URI,
        'version' => STOCK_SCANNER_VERSION,
        'isLoggedIn' => is_user_logged_in(),
        'currentUser' => is_user_logged_in() ? wp_get_current_user()->ID : 0,
        'restUrl' => rest_url('stock-scanner/v1/'),
        'restNonce' => wp_create_nonce('wp_rest'),
        
        // Enhanced theme settings
        'settings' => array(
            'enablePerformanceMonitoring' => get_option('stock_scanner_performance_monitoring', false),
            'enableAdvancedFeatures' => true,
            'cacheTimeout' => 300000, // 5 minutes
            'debounceDelay' => 300,
            'animationDuration' => 300,
            'notificationTimeout' => 5000,
        ),
        
        // API endpoints
        'endpoints' => array(
            'search' => rest_url('stock-scanner/v1/search'),
            'portfolio' => rest_url('stock-scanner/v1/portfolio'),
            'watchlist' => rest_url('stock-scanner/v1/watchlist'),
            'stocks' => rest_url('stock-scanner/v1/stocks'),
        ),
        
        // UI configuration
        'ui' => array(
            'pagination' => array(
                'defaultPageSize' => 10,
                'pageSizeOptions' => array(5, 10, 25, 50, 100),
                'maxVisiblePages' => 5,
            ),
            'table' => array(
                'sortable' => true,
                'filterable' => true,
                'exportable' => true,
            ),
            'search' => array(
                'minLength' => 2,
                'debounceDelay' => 300,
                'maxResults' => 10,
                'cacheResults' => true,
            ),
        ),
        
        // Translations
        'i18n' => array(
            'loading' => __('Loading...', 'stock-scanner'),
            'error' => __('An error occurred', 'stock-scanner'),
            'noResults' => __('No results found', 'stock-scanner'),
            'tryAgain' => __('Try again', 'stock-scanner'),
            'loadMore' => __('Load more', 'stock-scanner'),
            'exportCsv' => __('Export CSV', 'stock-scanner'),
            'exportJson' => __('Export JSON', 'stock-scanner'),
            'searchPlaceholder' => __('Search stocks, companies...', 'stock-scanner'),
            'confirmDelete' => __('Are you sure you want to delete this item?', 'stock-scanner'),
        )
    );
    
    // Localize script with comprehensive data
    wp_localize_script('stock-scanner-theme-enhanced', 'stockScannerData', $localize_data);
    
    // ===== PRELOAD CRITICAL RESOURCES =====
    add_action('wp_head', function() {
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js" as="script">';
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/assets/js/advanced-components.js" as="script">';
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css" as="style">';
    }, 1);
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');

/**
 * Force remove jQuery from frontend - ESSENTIAL FOR VANILLA JS
 */
function stock_scanner_remove_jquery() {
    if (!is_admin()) {
        wp_deregister_script('jquery');
        wp_deregister_script('jquery-migrate');
        wp_deregister_script('jquery-core');
        wp_deregister_script('jquery-ui-core');
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_remove_jquery', 1);

/**
 * Enhanced widget areas
 */
function stock_scanner_widgets_init() {
    register_sidebar(array(
        'name'          => __('Footer Widget Area 1', 'stock-scanner'),
        'id'            => 'footer-1',
        'description'   => __('Add widgets here to appear in the first footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    
    register_sidebar(array(
        'name'          => __('Footer Widget Area 2', 'stock-scanner'),
        'id'            => 'footer-2',
        'description'   => __('Add widgets here to appear in the second footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    
    register_sidebar(array(
        'name'          => __('Footer Widget Area 3', 'stock-scanner'),
        'id'            => 'footer-3',
        'description'   => __('Add widgets here to appear in the third footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * Enhanced Navigation Walker
 */
class Stock_Scanner_Nav_Walker extends Walker_Nav_Menu {
    function start_lvl(&$output, $depth = 0, $args = null) {
        $indent = str_repeat("\t", $depth);
        $output .= "\n$indent<ul class=\"sub-menu\">\n";
    }

    function end_lvl(&$output, $depth = 0, $args = null) {
        $indent = str_repeat("\t", $depth);
        $output .= "$indent</ul>\n";
    }

    function start_el(&$output, $item, $depth = 0, $args = null, $id = 0) {
        $indent = ($depth) ? str_repeat("\t", $depth) : '';

        $classes = empty($item->classes) ? array() : (array) $item->classes;
        $classes[] = 'menu-item-' . $item->ID;

        $class_names = join(' ', apply_filters('nav_menu_css_class', array_filter($classes), $item, $args));
        $class_names = $class_names ? ' class="' . esc_attr($class_names) . '"' : '';

        $id = apply_filters('nav_menu_item_id', 'menu-item-' . $item->ID, $item, $args);
        $id = $id ? ' id="' . esc_attr($id) . '"' : '';

        $output .= $indent . '<li' . $id . $class_names .'>';

        $attributes = ! empty($item->attr_title) ? ' title="'  . esc_attr($item->attr_title) .'"' : '';
        $attributes .= ! empty($item->target)     ? ' target="' . esc_attr($item->target     ) .'"' : '';
        $attributes .= ! empty($item->xfn)        ? ' rel="'    . esc_attr($item->xfn        ) .'"' : '';
        $attributes .= ! empty($item->url)        ? ' href="'   . esc_attr($item->url        ) .'"' : '';

        $item_output = isset($args->before) ? $args->before : '';
        $item_output .= '<a' . $attributes . '>';
        $item_output .= (isset($args->link_before) ? $args->link_before : '') . apply_filters('the_title', $item->title, $item->ID) . (isset($args->link_after) ? $args->link_after : '');
        $item_output .= '</a>';
        $item_output .= isset($args->after) ? $args->after : '';

        $output .= apply_filters('walker_nav_menu_start_el', $item_output, $item, $depth, $args);
    }

    function end_el(&$output, $item, $depth = 0, $args = null) {
        $output .= "</li>\n";
    }
}

/**
 * Fallback menu functions
 */
function stock_scanner_fallback_menu() {
    $menu_items = array(
        array('title' => 'Home', 'url' => home_url('/')),
        array('title' => 'Dashboard', 'url' => home_url('/dashboard/')),
        array('title' => 'Stock Screener', 'url' => home_url('/stock-screener/')),
        array('title' => 'Portfolio', 'url' => home_url('/portfolio/')),
        array('title' => 'Watchlist', 'url' => home_url('/watchlist/')),
        array('title' => 'Pricing', 'url' => home_url('/premium-plans/')),
    );
    
    echo '<ul class="nav-menu fallback-menu">';
    foreach ($menu_items as $item) {
        $current = (home_url(add_query_arg(array(), $_SERVER['REQUEST_URI'])) === $item['url']) ? ' class="current-menu-item"' : '';
        echo '<li' . $current . '><a href="' . esc_url($item['url']) . '">' . esc_html($item['title']) . '</a></li>';
    }
    echo '</ul>';
}

function stock_scanner_footer_fallback_menu() {
    $menu_items = array(
        array('title' => 'About', 'url' => home_url('/about/')),
        array('title' => 'Contact', 'url' => home_url('/contact/')),
        array('title' => 'Privacy Policy', 'url' => home_url('/privacy-policy/')),
        array('title' => 'Terms of Service', 'url' => home_url('/terms-of-service/')),
    );
    
    echo '<ul class="footer-menu fallback-menu">';
    foreach ($menu_items as $item) {
        echo '<li><a href="' . esc_url($item['url']) . '">' . esc_html($item['title']) . '</a></li>';
    }
    echo '</ul>';
}

/**
 * ===== ENHANCED SHORTCODES =====
 */

/**
 * Stock Scanner Dashboard Shortcode
 */
function stock_scanner_dashboard_shortcode($atts) {
    $atts = shortcode_atts(array(
        'user_id' => get_current_user_id(),
        'show_portfolio' => 'true',
        'show_watchlist' => 'true',
        'show_news' => 'true',
    ), $atts);

    if (!is_user_logged_in()) {
        return '<div class="dashboard-login-required">
            <h3>Login Required</h3>
            <p>Please log in to access your dashboard.</p>
            <a href="' . wp_login_url() . '" class="btn btn-primary">Login</a>
        </div>';
    }

    ob_start();
    ?>
    <div class="stock-scanner-dashboard">
        <div class="dashboard-header">
            <h2>Welcome back, <?php echo esc_html(wp_get_current_user()->display_name); ?>!</h2>
            <p>Here's your portfolio overview and latest market updates.</p>
        </div>
        
        <div class="dashboard-grid">
            <?php if ($atts['show_portfolio'] === 'true'): ?>
            <div class="dashboard-section portfolio-section">
                <div class="section-header">
                    <h3>Portfolio Performance</h3>
                    <a href="/portfolio/" class="btn btn-outline btn-sm">View All</a>
                </div>
                <div class="portfolio-widgets">
                    <!-- Portfolio data will be loaded dynamically via API -->
                    <div class="loading-skeleton portfolio-widget">
                        <div class="widget-title">Loading...</div>
                    </div>
                </div>
            </div>
            <?php endif; ?>
            
            <?php if ($atts['show_watchlist'] === 'true'): ?>
            <div class="dashboard-section watchlist-section">
                <div class="section-header">
                    <h3>Watchlist</h3>
                    <a href="/watchlist/" class="btn btn-outline btn-sm">Manage</a>
                </div>
                <div class="watchlist-items">
                    <!-- Watchlist data will be loaded dynamically via API -->
                    <div class="loading-skeleton">Loading watchlist...</div>
                </div>
            </div>
            <?php endif; ?>
            
            <?php if ($atts['show_news'] === 'true'): ?>
            <div class="dashboard-section news-section">
                <div class="section-header">
                    <h3>Market News</h3>
                    <a href="/stock-news/" class="btn btn-outline btn-sm">All News</a>
                </div>
                <div class="news-items">
                    <!-- News data will be loaded dynamically via API -->
                    <div class="loading-skeleton">Loading market news...</div>
                </div>
            </div>
            <?php endif; ?>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_dashboard', 'stock_scanner_dashboard_shortcode');

/**
 * Enhanced Pricing Table Shortcode
 */
function stock_scanner_pricing_shortcode($atts) {
    $atts = shortcode_atts(array(
        'show_trial' => 'true',
        'highlight_plan' => 'premium',
    ), $atts);

    ob_start();
    ?>
    <div class="pricing-table">
        <div class="pricing-plan basic">
            <h3>Basic</h3>
            <div class="price">$9<span>/month</span></div>
            <ul>
                <li>✅ Real-time quotes for 100 stocks</li>
                <li>✅ Basic stock screening</li>
                <li>✅ Portfolio tracking</li>
                <li>✅ Email alerts</li>
                <li>✅ Mobile app access</li>
                <li>❌ Advanced technical analysis</li>
                <li>❌ Custom screening criteria</li>
                <li>❌ Premium research reports</li>
            </ul>
            <a href="<?php echo is_user_logged_in() ? '/premium-plans/' : wp_registration_url(); ?>" class="btn btn-outline">
                <?php echo $atts['show_trial'] === 'true' ? '7-Day Trial for $1' : 'Choose Basic'; ?>
            </a>
        </div>
        
        <div class="pricing-plan premium <?php echo $atts['highlight_plan'] === 'premium' ? 'highlighted' : ''; ?>">
            <h3>Premium</h3>
            <div class="price">$29<span>/month</span></div>
            <ul>
                <li>✅ Real-time quotes for unlimited stocks</li>
                <li>✅ Advanced stock screening</li>
                <li>✅ Unlimited portfolio tracking</li>
                <li>✅ Real-time alerts (SMS + Email)</li>
                <li>✅ Mobile + Desktop apps</li>
                <li>✅ Advanced technical analysis</li>
                <li>✅ Custom screening criteria</li>
                <li>✅ Premium research reports</li>
            </ul>
            <a href="<?php echo is_user_logged_in() ? '/premium-plans/' : wp_registration_url(); ?>" class="btn btn-primary">
                <?php echo $atts['show_trial'] === 'true' ? '7-Day Trial for $1' : 'Choose Premium'; ?>
            </a>
        </div>
        
        <div class="pricing-plan professional">
            <h3>Professional</h3>
            <div class="price">$79<span>/month</span></div>
            <ul>
                <li>✅ Everything in Premium</li>
                <li>✅ API access for trading platforms</li>
                <li>✅ Advanced backtesting tools</li>
                <li>✅ Priority customer support</li>
                <li>✅ Custom indicators</li>
                <li>✅ Institutional-grade data</li>
                <li>✅ White-label solutions</li>
                <li>✅ Dedicated account manager</li>
            </ul>
            <a href="<?php echo is_user_logged_in() ? '/premium-plans/' : wp_registration_url(); ?>" class="btn btn-outline">
                <?php echo $atts['show_trial'] === 'true' ? '7-Day Trial for $1' : 'Choose Professional'; ?>
            </a>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_pricing', 'stock_scanner_pricing_shortcode');

/**
 * Enhanced REST API endpoints
 */
function stock_scanner_register_api_routes() {
    register_rest_route('stock-scanner/v1', '/search', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_api_search',
        'permission_callback' => '__return_true',
        'args' => array(
            'q' => array(
                'required' => true,
                'sanitize_callback' => 'sanitize_text_field',
            ),
            'limit' => array(
                'default' => 10,
                'sanitize_callback' => 'absint',
            ),
        ),
    ));
    
    register_rest_route('stock-scanner/v1', '/portfolio/(?P<id>\d+)', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_api_get_portfolio',
        'permission_callback' => 'is_user_logged_in',
    ));
    
    register_rest_route('stock-scanner/v1', '/watchlist', array(
        'methods' => array('GET', 'POST'),
        'callback' => 'stock_scanner_api_watchlist',
        'permission_callback' => 'is_user_logged_in',
    ));
}
add_action('rest_api_init', 'stock_scanner_register_api_routes');

function stock_scanner_api_search($request) {
    $query = $request['q'];
    $limit = $request['limit'];
    
    // TODO: Implement actual API search functionality
    // This should connect to your stock market data provider
    
    return array(
        'success' => false,
        'message' => 'Search functionality requires stock market API integration',
        'results' => array()
    );
}

function stock_scanner_api_get_portfolio($request) {
    $user_id = $request['id'];
    
    // TODO: Implement actual portfolio data retrieval
    // This should fetch real user portfolio data from database
    
    return array(
        'success' => false,
        'message' => 'Portfolio API requires database integration and user data',
        'user_id' => $user_id,
        'data' => array()
    );
}

function stock_scanner_api_watchlist($request) {
    if ($request->get_method() === 'GET') {
        // TODO: Implement actual watchlist retrieval
        return array(
            'success' => false,
            'message' => 'Watchlist API requires database integration',
            'data' => array()
        );
    } else {
        // TODO: Implement actual watchlist add functionality
        return array(
            'success' => false,
            'message' => 'Watchlist add functionality requires database integration'
        );
    }
}

/**
 * Theme options page
 */
function stock_scanner_add_admin_menu() {
    add_theme_page(
        'Stock Scanner Options',
        'Stock Scanner',
        'manage_options',
        'stock-scanner-options',
        'stock_scanner_options_page'
    );
}
add_action('admin_menu', 'stock_scanner_add_admin_menu');

function stock_scanner_options_page() {
    if (isset($_POST['submit'])) {
        update_option('stock_scanner_api_key', sanitize_text_field($_POST['stock_scanner_api_key']));
        update_option('stock_scanner_performance_monitoring', isset($_POST['stock_scanner_performance_monitoring']));
        echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
    }
    ?>
    <div class="wrap">
        <h1>Stock Scanner Pro Options</h1>
        <form method="post" action="">
            <table class="form-table">
                <tr>
                    <th scope="row">Stock Market API Key</th>
                    <td>
                        <input type="text" name="stock_scanner_api_key" value="<?php echo esc_attr(get_option('stock_scanner_api_key')); ?>" class="regular-text" />
                        <p class="description">Enter your stock market API key</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">Enable Performance Monitoring</th>
                    <td>
                        <input type="checkbox" name="stock_scanner_performance_monitoring" value="1" <?php checked(1, get_option('stock_scanner_performance_monitoring'), true); ?> />
                        <p class="description">Enable performance monitoring in development</p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

/**
 * Security enhancements
 */
function stock_scanner_security_headers() {
    if (!is_admin()) {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}
add_action('send_headers', 'stock_scanner_security_headers');

/**
 * Performance optimizations
 */
function stock_scanner_performance_optimizations() {
    // Preload key resources
    add_action('wp_head', function() {
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css" as="style">';
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js" as="script">';
        echo '<link rel="dns-prefetch" href="//api.stockmarket.com">';
    });
    
    // Optimize database queries
    add_action('pre_get_posts', function($query) {
        if (!is_admin() && $query->is_main_query()) {
            if (is_home()) {
                $query->set('posts_per_page', 10);
            }
        }
    });
}
add_action('init', 'stock_scanner_performance_optimizations');

/**
 * Theme customizer
 */
function stock_scanner_customize_register($wp_customize) {
    // Colors section
    $wp_customize->add_section('stock_scanner_colors', array(
        'title' => __('Stock Scanner Colors', 'stock-scanner'),
        'priority' => 30,
    ));
    
    $wp_customize->add_setting('primary_color', array(
        'default' => '#667eea',
        'sanitize_callback' => 'sanitize_hex_color',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'primary_color', array(
        'label' => __('Primary Color', 'stock-scanner'),
        'section' => 'stock_scanner_colors',
        'settings' => 'primary_color',
    )));
}
add_action('customize_register', 'stock_scanner_customize_register');

/**
 * Custom body classes
 */
function stock_scanner_body_classes($classes) {
    if (is_user_logged_in()) {
        $classes[] = 'user-logged-in';
    }
    
    if (wp_is_mobile()) {
        $classes[] = 'mobile-device';
    }
    
    $classes[] = 'vanilla-js-theme';
    $classes[] = 'production-ready';
    $classes[] = 'enhanced-v3';
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

// Clean up WordPress head
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'rsd_link');

// Use WordPress resource hints API for preconnect/dns-prefetch
function stock_scanner_resource_hints($urls, $relation_type) {
    if ('preconnect' === $relation_type) {
        $urls[] = array('href' => 'https://fonts.googleapis.com', 'crossorigin');
        $urls[] = array('href' => 'https://fonts.gstatic.com', 'crossorigin');
    }
    if ('dns-prefetch' === $relation_type) {
        $urls[] = '//api.stockmarket.com';
    }
    return $urls;
}
add_filter('wp_resource_hints', 'stock_scanner_resource_hints', 10, 2);

/**
 * Enable theme updates and activation
 */
add_action('after_switch_theme', function() {
    // Clear any cached CSS/JS
    if (function_exists('wp_cache_flush')) {
        wp_cache_flush();
    }
    
    // Flush rewrite rules
    flush_rewrite_rules();
    
    // Create default pages if they don't exist
    $pages = array(
        'dashboard' => 'Dashboard',
        'portfolio' => 'Portfolio',
        'watchlist' => 'Watchlist',
        'stock-screener' => 'Stock Screener',
        'premium-plans' => 'Premium Plans',
    );
    
    foreach ($pages as $slug => $title) {
        if (!get_page_by_path($slug)) {
            wp_insert_post(array(
                'post_title' => $title,
                'post_name' => $slug,
                'post_status' => 'publish',
                'post_type' => 'page',
                'post_content' => '[stock_scanner_dashboard]'
            ));
        }
    }
});

// Mark theme as fully loaded and enhanced
add_action('wp_footer', function() {
    echo '<script>document.documentElement.classList.add("theme-enhanced-loaded");</script>';
}, 999);