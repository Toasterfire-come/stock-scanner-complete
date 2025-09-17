<?php
/**
 * Fallback menu function for primary navigation
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="nav-menu">';
    echo '<li><a href="' . esc_url(home_url('/')) . '">Home</a></li>';
    echo '<li><a href="' . esc_url(home_url('/dashboard/')) . '">Dashboard</a></li>';
    echo '<li><a href="' . esc_url(home_url('/portfolio/')) . '">Portfolio</a></li>';
    echo '<li><a href="' . esc_url(home_url('/watchlist/')) . '">Watchlist</a></li>';
    echo '<li><a href="' . esc_url(home_url('/premium-plans/')) . '">Premium</a></li>';
    echo '<li><a href="' . esc_url(home_url('/contact/')) . '">Contact</a></li>';
    echo '</ul>';
}

/**
 * Footer fallback menu
 */
function stock_scanner_footer_fallback_menu() {
    echo '<ul class="footer-menu">';
    echo '<li><a href="' . esc_url(home_url('/about/')) . '">About</a></li>';
    echo '<li><a href="' . esc_url(home_url('/contact/')) . '">Contact</a></li>';
    echo '<li><a href="' . esc_url(home_url('/privacy-policy/')) . '">Privacy</a></li>';
    echo '<li><a href="' . esc_url(home_url('/terms-of-service/')) . '">Terms</a></li>';
    echo '<li><a href="' . esc_url(home_url('/faq/')) . '">FAQ</a></li>';
    echo '</ul>';
}

/**
 * Stock Scanner Pro Theme - Production Ready Functions
 * 100% Vanilla JavaScript - No jQuery Dependencies
 * Version: 2.2.0 - Optimized
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme Setup
 */
function stock_scanner_setup() {
    // Add theme support for various features
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script'
    ));
    
    add_theme_support('post-thumbnails');
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('automatic-feed-links');
    add_theme_support('title-tag');
    add_theme_support('responsive-embeds');
    
    // Custom image sizes for stock scanner
    add_image_size('stock-thumbnail', 300, 200, true);
    add_image_size('portfolio-hero', 800, 400, true);
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => esc_html__('Primary Menu', 'stock-scanner'),
        'footer' => esc_html__('Footer Menu', 'stock-scanner'),
        'user-menu' => esc_html__('User Account Menu', 'stock-scanner')
    ));
}
add_action('after_setup_theme', 'stock_scanner_setup');

/**
 * Enqueue Scripts and Styles - 100% Vanilla JS
 */
function stock_scanner_scripts() {
    // Google Fonts - optimized loading
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap', array(), null);
    
    // Main theme stylesheet
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array('google-fonts'), '2.2.0');
    
    // Enhanced styles
    wp_enqueue_style('enhanced-styles', get_template_directory_uri() . '/assets/css/enhanced-styles.css', array('stock-scanner-style'), '2.2.0');
    
    // ONLY Vanilla JavaScript - NO jQuery
    wp_enqueue_script('stock-scanner-vanilla', get_template_directory_uri() . '/js/theme-optimized.js', array(), '2.2.0', true);
    
    // Performance optimized vanilla JS
    wp_enqueue_script('stock-scanner-performance', get_template_directory_uri() . '/assets/js/performance-optimized-vanilla.js', array(), '2.2.0', true);
    
    // Advanced UI vanilla JS
    wp_enqueue_script('stock-scanner-ui', get_template_directory_uri() . '/assets/js/advanced-ui-vanilla.js', array(), '2.2.0', true);
    
    // Localize script for AJAX and theme data
    wp_localize_script('stock-scanner-vanilla', 'stockScannerData', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'isLoggedIn' => is_user_logged_in(),
        'userId' => get_current_user_id(),
        'themeUrl' => get_template_directory_uri(),
        'apiBase' => home_url('/api/'),
        'strings' => array(
            'loading' => __('Loading...', 'stock-scanner'),
            'error' => __('An error occurred', 'stock-scanner'),
            'success' => __('Success!', 'stock-scanner'),
            'confirmDelete' => __('Are you sure you want to delete this?', 'stock-scanner')
        )
    ));
    
    // Comment reply script (WordPress core, vanilla JS)
    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Remove jQuery from frontend (force vanilla JS only)
 */
function stock_scanner_remove_jquery() {
    if (!is_admin()) {
        // Only deregister if no plugin explicitly enqueued jQuery already
        if (!wp_script_is('jquery', 'enqueued') && !wp_script_is('jquery', 'to_print')) {
            wp_deregister_script('jquery');
            wp_deregister_script('jquery-migrate');
        }
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_remove_jquery', 1);

/**
 * Optimize WordPress for performance
 */
function stock_scanner_optimize_wp() {
    // Remove unnecessary WordPress features
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    remove_action('wp_head', 'adjacent_posts_rel_link_wp_head');
    
    // Disable emojis (performance optimization)
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('admin_print_styles', 'print_emoji_styles');
    
    // Remove WordPress version from scripts and styles
    add_filter('script_loader_src', 'stock_scanner_remove_version', 15, 1);
    add_filter('style_loader_src', 'stock_scanner_remove_version', 15, 1);
}
add_action('init', 'stock_scanner_optimize_wp');

function stock_scanner_remove_version($src) {
    if (strpos($src, 'ver=') && !is_admin()) {
        $src = remove_query_arg('ver', $src);
    }
    return $src;
}

/**
 * Widget Areas
 */
function stock_scanner_widgets_init() {
    // Sidebar
    register_sidebar(array(
        'name'          => esc_html__('Sidebar', 'stock-scanner'),
        'id'            => 'sidebar-1',
        'description'   => esc_html__('Add widgets here.', 'stock-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    
    // Footer widgets
    for ($i = 1; $i <= 4; $i++) {
        register_sidebar(array(
            'name'          => sprintf(esc_html__('Footer %d', 'stock-scanner'), $i),
            'id'            => 'footer-' . $i,
            'description'   => sprintf(esc_html__('Footer widget area %d', 'stock-scanner'), $i),
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget'  => '</div>',
            'before_title'  => '<h4 class="widget-title">',
            'after_title'   => '</h4>',
        ));
    }
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * Custom Walker for Navigation Menu
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
        
        $id = apply_filters('nav_menu_item_id', 'menu-item-'. $item->ID, $item, $args);
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
 * Stock Scanner Shortcodes
 */
function stock_scanner_dashboard_shortcode($atts) {
    $atts = shortcode_atts(array(
        'user_id' => get_current_user_id(),
        'view' => 'full'
    ), $atts);
    
    if (!is_user_logged_in()) {
        return '<div class="alert alert-warning">Please log in to view your dashboard.</div>';
    }
    
    ob_start();
    ?>
    <div class="stock-scanner-dashboard" data-user-id="<?php echo esc_attr($atts['user_id']); ?>">
        <div class="dashboard-header">
            <h2>Your Stock Dashboard</h2>
            <div class="dashboard-actions">
                <button class="btn btn-primary" data-action="refresh">Refresh Data</button>
                <button class="btn btn-secondary" data-action="export">Export</button>
            </div>
        </div>
        
        <div class="dashboard-widgets">
            <div class="row">
                <div class="col-md-8">
                    <div class="widget-portfolio">
                        <h3>Portfolio Overview</h3>
                        <div class="portfolio-stats">
                            <div class="stat">
                                <label>Total Value</label>
                                <div class="value" data-portfolio="total-value">$0.00</div>
                            </div>
                            <div class="stat">
                                <label>Today's Change</label>
                                <div class="value" data-portfolio="daily-change">+$0.00</div>
                            </div>
                            <div class="stat">
                                <label>Total Return</label>
                                <div class="value" data-portfolio="total-return">+0.00%</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="widget-watchlist">
                        <h3>Watchlist</h3>
                        <div class="watchlist-items" data-watchlist="recent">
                            <div class="loading">Loading watchlist...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_dashboard', 'stock_scanner_dashboard_shortcode');

function stock_scanner_pricing_shortcode($atts) {
    $atts = shortcode_atts(array(
        'style' => 'cards'
    ), $atts);
    
    ob_start();
    ?>
    <div class="pricing-table">
        <div class="row">
            <div class="col-lg-4">
                <div class="pricing-plan">
                    <h3>Free</h3>
                    <div class="price">$0<span>/month</span></div>
                    <ul>
                        <li>15 API calls per month</li>
                        <li>Basic stock data</li>
                        <li>Email support</li>
                        <li>Community access</li>
                    </ul>
                    <a href="<?php echo wp_registration_url(); ?>" class="btn btn-secondary">Get Started</a>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="pricing-plan premium">
                    <h3>Premium</h3>
                    <div class="price">$29<span>/month</span></div>
                    <ul>
                        <li>Unlimited API calls</li>
                        <li>Real-time data</li>
                        <li>Advanced charts</li>
                        <li>Priority support</li>
                        <li>Portfolio tracking</li>
                    </ul>
                    <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="pricing-plan">
                    <h3>Professional</h3>
                    <div class="price">$99<span>/month</span></div>
                    <ul>
                        <li>Everything in Premium</li>
                        <li>API access</li>
                        <li>Custom indicators</li>
                        <li>White-label options</li>
                        <li>Dedicated support</li>
                    </ul>
                    <a href="/premium-plans/" class="btn btn-outline-primary">Contact Sales</a>
                </div>
            </div>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_pricing', 'stock_scanner_pricing_shortcode');

/**
 * REST API Endpoints for Stock Scanner
 */
function stock_scanner_register_api_routes() {
    register_rest_route('stock-scanner/v1', '/portfolio/(?P<id>\d+)', array(
        'methods' => 'GET',
        'callback' => 'stock_scanner_get_portfolio',
        'permission_callback' => 'stock_scanner_check_permissions'
    ));
    
    register_rest_route('stock-scanner/v1', '/watchlist', array(
        'methods' => array('GET', 'POST'),
        'callback' => 'stock_scanner_handle_watchlist',
        'permission_callback' => 'stock_scanner_check_permissions'
    ));
}
add_action('rest_api_init', 'stock_scanner_register_api_routes');

function stock_scanner_check_permissions() {
    return is_user_logged_in();
}

function stock_scanner_get_portfolio($request) {
    $portfolio_id = $request['id'];
    $user_id = get_current_user_id();
    
    // Mock data - replace with actual database queries
    return new WP_REST_Response(array(
        'success' => true,
        'data' => array(
            'id' => $portfolio_id,
            'name' => 'My Portfolio',
            'total_value' => 50000.00,
            'daily_change' => 1250.50,
            'holdings' => array(
                array('symbol' => 'AAPL', 'shares' => 100, 'value' => 15000),
                array('symbol' => 'GOOGL', 'shares' => 50, 'value' => 35000)
            )
        )
    ), 200);
}

function stock_scanner_handle_watchlist($request) {
    $method = $request->get_method();
    $user_id = get_current_user_id();
    
    if ($method === 'GET') {
        // Return user's watchlist
        return new WP_REST_Response(array(
            'success' => true,
            'data' => array(
                'watchlist' => array(
                    array('symbol' => 'AAPL', 'price' => 150.25, 'change' => '+2.50'),
                    array('symbol' => 'TSLA', 'price' => 800.15, 'change' => '-5.25'),
                    array('symbol' => 'MSFT', 'price' => 310.75, 'change' => '+1.15')
                )
            )
        ), 200);
    } else {
        // Add to watchlist
        $symbol = sanitize_text_field($request->get_param('symbol'));
        
        return new WP_REST_Response(array(
            'success' => true,
            'message' => "Added {$symbol} to watchlist"
        ), 201);
    }
}

/**
 * Admin Enhancements
 */
function stock_scanner_admin_init() {
    // Add custom theme options page
    add_theme_page(
        'Stock Scanner Options',
        'Theme Options',
        'manage_options',
        'stock-scanner-options',
        'stock_scanner_options_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_init');

function stock_scanner_options_page() {
    ?>
    <div class="wrap">
        <h1>Stock Scanner Theme Options</h1>
        <form method="post" action="options.php">
            <?php
            settings_fields('stock_scanner_options');
            do_settings_sections('stock_scanner_options');
            ?>
            <table class="form-table">
                <tr>
                    <th scope="row">API Key</th>
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
        // Consider adding a Content-Security-Policy header via server config or plugin
    }
}
add_action('send_headers', 'stock_scanner_security_headers');

/**
 * Performance optimizations
 */
function stock_scanner_performance_optimizations() {
    // Preload key resources
    add_action('wp_head', function() {
        echo '<link rel="preload" href="' . get_template_directory_uri() . '/assets/css/enhanced-styles.css" as="style">';
        echo '<link rel="preload" href="' . get_template_directory_uri() . '/js/theme-optimized.js" as="script">';

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
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

// Clean up WordPress head
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'rsd_link');

// Theme loaded - mark as ready
add_action('wp_footer', function() {
    // Moved to theme JS to avoid inline script for CSP
});

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