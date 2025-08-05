<?php
/**
 * Stock Scanner Theme Functions
 * Sets up theme features and navigation
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme setup
 */
function stock_scanner_theme_setup() {
    // Add theme support for various features
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('customize-selective-refresh-widgets');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner'),
        'footer' => __('Footer Menu', 'stock-scanner'),
    ));
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/**
 * Enqueue scripts and styles
 */
function stock_scanner_scripts() {
    // Enqueue theme stylesheet
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '1.0.0');
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Enqueue theme JavaScript
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '1.0.0', true);
    
    // Enqueue plugin integration JavaScript
    wp_enqueue_script('stock-scanner-plugin-js', get_template_directory_uri() . '/assets/js/plugin-integration.js', array('jquery', 'stock-scanner-js'), '1.0.0', true);
    
    // Localize script for AJAX
    wp_localize_script('stock-scanner-plugin-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Include plugin integration
 */
require_once get_template_directory() . '/inc/plugin-integration.php';

/**
 * Theme activation - Clear existing pages and create new ones
 */
function stock_scanner_theme_activation() {
    // Clear existing Stock Scanner pages
    stock_scanner_clear_existing_pages();
    
    // Create new pages
    stock_scanner_create_pages();
    
    // Create menus
    stock_scanner_create_menus();
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'stock_scanner_theme_activation');

/**
 * Clear existing Stock Scanner pages
 */
function stock_scanner_clear_existing_pages() {
    $page_slugs = array(
        'dashboard', 'stock-scanner', 'watchlist', 'market-overview', 'account', 
        'premium-plans', 'payment-success', 'payment-cancelled', 'contact', 
        'about', 'privacy-policy', 'terms-of-service', 'faq'
    );
    
    foreach ($page_slugs as $slug) {
        $page = get_page_by_path($slug);
        if ($page) {
            wp_delete_post($page->ID, true);
        }
    }
    
    // Also clear any pages with Stock Scanner in the title
    $existing_pages = get_posts(array(
        'post_type' => 'page',
        'post_status' => 'any',
        's' => 'Stock Scanner',
        'posts_per_page' => -1
    ));
    
    foreach ($existing_pages as $page) {
        wp_delete_post($page->ID, true);
    }
}

/**
 * Create Stock Scanner pages
 */
function stock_scanner_create_pages() {
    $pages = array(
        array(
            'title' => 'Dashboard',
            'slug' => 'dashboard',
            'content' => '[stock_scanner_dashboard]',
            'template' => 'page-dashboard.php'
        ),
        array(
            'title' => 'Stock Scanner',
            'slug' => 'stock-scanner',
            'content' => '<h2>Stock Scanner</h2><p>Scan and analyze stocks with our powerful tools.</p>[stock_scanner_dashboard]',
            'template' => 'page-scanner.php'
        ),
        array(
            'title' => 'My Watchlist',
            'slug' => 'watchlist',
            'content' => '<h2>My Watchlist</h2><p>Track your favorite stocks and monitor their performance.</p>',
            'template' => 'page-watchlist.php'
        ),
        array(
            'title' => 'Market Overview',
            'slug' => 'market-overview',
            'content' => '<h2>Market Overview</h2><p>Stay updated with the latest market trends and data.</p>',
            'template' => 'page-market-overview.php'
        ),
        array(
            'title' => 'My Account',
            'slug' => 'account',
            'content' => '<h2>Account Management</h2><p>Manage your subscription and account settings.</p>[stock_scanner_dashboard]',
            'template' => 'page-account.php'
        ),
        array(
            'title' => 'Premium Plans',
            'slug' => 'premium-plans',
            'content' => '[stock_scanner_pricing]',
            'template' => 'page-premium-plans.php'
        ),
        array(
            'title' => 'Payment Success',
            'slug' => 'payment-success',
            'content' => '<h2>Payment Successful!</h2><p>Thank you for your purchase. Your account has been upgraded.</p><p><a href="/dashboard/">Go to Dashboard</a></p>',
            'template' => 'page-payment-success.php'
        ),
        array(
            'title' => 'Payment Cancelled',
            'slug' => 'payment-cancelled',
            'content' => '<h2>Payment Cancelled</h2><p>Your payment was cancelled. You can try again anytime.</p><p><a href="/premium-plans/">View Plans</a></p>',
            'template' => 'page-payment-cancelled.php'
        ),
        array(
            'title' => 'Contact Us',
            'slug' => 'contact',
            'content' => '<h2>Contact Us</h2><p>Get in touch with our support team.</p>',
            'template' => 'page-contact.php'
        ),
        array(
            'title' => 'About Us',
            'slug' => 'about',
            'content' => '<h2>About Stock Scanner</h2><p>Professional stock analysis tools for informed investment decisions.</p>',
            'template' => 'page-about.php'
        ),
        array(
            'title' => 'Privacy Policy',
            'slug' => 'privacy-policy',
            'content' => '<h2>Privacy Policy</h2><p>We respect your privacy and protect your personal information.</p>',
            'template' => 'page-privacy.php'
        ),
        array(
            'title' => 'Terms of Service',
            'slug' => 'terms-of-service',
            'content' => '<h2>Terms of Service</h2><p>Terms and conditions for using our service.</p>',
            'template' => 'page-terms.php'
        ),
        array(
            'title' => 'FAQ',
            'slug' => 'faq',
            'content' => '<h2>Frequently Asked Questions</h2><p>Find answers to common questions about our service.</p>',
            'template' => 'page-faq.php'
        )
    );
    
    foreach ($pages as $page_data) {
        $page = array(
            'post_title' => $page_data['title'],
            'post_name' => $page_data['slug'],
            'post_content' => $page_data['content'],
            'post_status' => 'publish',
            'post_type' => 'page',
            'post_author' => 1,
            'menu_order' => 0
        );
        
        $page_id = wp_insert_post($page);
        
        if ($page_id && !is_wp_error($page_id)) {
            // Set page template if specified
            if (isset($page_data['template'])) {
                update_post_meta($page_id, '_wp_page_template', $page_data['template']);
            }
        }
    }
    
    // Set homepage to use front-page.php if it exists, otherwise use index.php
    $homepage = get_page_by_path('dashboard');
    if ($homepage) {
        update_option('page_on_front', $homepage->ID);
        update_option('show_on_front', 'page');
    }
}

/**
 * Create navigation menus
 */
function stock_scanner_create_menus() {
    // Delete existing menus
    $existing_menus = wp_get_nav_menus();
    foreach ($existing_menus as $menu) {
        if (strpos($menu->name, 'Stock Scanner') !== false || 
            in_array($menu->name, array('Primary Menu', 'Footer Menu'))) {
            wp_delete_nav_menu($menu->term_id);
        }
    }
    
    // Create Primary Menu
    $primary_menu_id = wp_create_nav_menu('Stock Scanner Primary');
    if (!is_wp_error($primary_menu_id)) {
        $menu_items = array(
            array('title' => 'Dashboard', 'url' => '/dashboard/'),
            array('title' => 'Stock Scanner', 'url' => '/stock-scanner/'),
            array('title' => 'Watchlist', 'url' => '/watchlist/'),
            array('title' => 'Market Overview', 'url' => '/market-overview/'),
            array('title' => 'Premium Plans', 'url' => '/premium-plans/'),
            array('title' => 'Contact', 'url' => '/contact/')
        );
        
        foreach ($menu_items as $item) {
            wp_update_nav_menu_item($primary_menu_id, 0, array(
                'menu-item-title' => $item['title'],
                'menu-item-url' => home_url($item['url']),
                'menu-item-status' => 'publish',
                'menu-item-type' => 'custom'
            ));
        }
        
        // Assign to primary location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['primary'] = $primary_menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
    
    // Create Footer Menu
    $footer_menu_id = wp_create_nav_menu('Stock Scanner Footer');
    if (!is_wp_error($footer_menu_id)) {
        $footer_items = array(
            array('title' => 'About', 'url' => '/about/'),
            array('title' => 'Privacy Policy', 'url' => '/privacy-policy/'),
            array('title' => 'Terms of Service', 'url' => '/terms-of-service/'),
            array('title' => 'FAQ', 'url' => '/faq/')
        );
        
        foreach ($footer_items as $item) {
            wp_update_nav_menu_item($footer_menu_id, 0, array(
                'menu-item-title' => $item['title'],
                'menu-item-url' => home_url($item['url']),
                'menu-item-status' => 'publish',
                'menu-item-type' => 'custom'
            ));
        }
        
        // Assign to footer location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['footer'] = $footer_menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
}

/**
 * Fallback menu for when no menu is assigned
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . home_url('/premium-plans/') . '">Premium Plans</a></li>';
    echo '<li><a href="' . home_url('/email-stock-lists/') . '">Email Lists</a></li>';
    echo '<li><a href="' . home_url('/stock-search/') . '">Stock Search</a></li>';
    echo '<li><a href="' . home_url('/popular-stock-lists/') . '">Popular Lists</a></li>';
    echo '<li><a href="' . home_url('/news-scrapper/') . '">News Scraper</a></li>';
    echo '<li><a href="' . home_url('/membership-account/') . '">My Account</a></li>';
    echo '</ul>';
}

/**
 * Add body classes for different membership levels
 */
function stock_scanner_body_classes($classes) {
    if (is_user_logged_in() && function_exists('pmpro_getMembershipLevelForUser')) {
        $level = pmpro_getMembershipLevelForUser(get_current_user_id());
        $level_id = $level ? $level->id : 0;
        
        $level_classes = array(
            0 => 'membership-free',
            1 => 'membership-free', 
            2 => 'membership-premium',
            3 => 'membership-professional'
        );
        
        if (isset($level_classes[$level_id])) {
            $classes[] = $level_classes[$level_id];
        }
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Customize login page
 */
function stock_scanner_login_styles() {
    ?>
    <style type="text/css">
        .login h1 a {
            background-image: none;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 100%;
            height: 65px;
            font-size: 24px;
            font-weight: bold;
            line-height: 65px;
            text-decoration: none;
            text-indent: 0;
            overflow: hidden;
        }
        
        .login h1 a::before {
            content: "📈 Stock Scanner";
            display: block;
            color: #667eea;
        }
        
        .login form {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }
        
        .login form .input {
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .login form .input:focus {
            background: white;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }
        
        .login form .button-primary {
            background: #f39c12;
            border: none;
            border-radius: 5px;
            box-shadow: none;
            text-shadow: none;
            font-weight: 600;
        }
        
        .login form .button-primary:hover {
            background: #e67e22;
        }
    </style>
    <?php
}
add_action('login_enqueue_scripts', 'stock_scanner_login_styles');

/**
 * Change login logo URL
 */
function stock_scanner_login_logo_url() {
    return home_url();
}
add_filter('login_headerurl', 'stock_scanner_login_logo_url');

/**
 * Change login logo title
 */
function stock_scanner_login_logo_url_title() {
    return get_bloginfo('name') . ' - Stock Scanner';
}
add_filter('login_headertitle', 'stock_scanner_login_logo_url_title');

/**
 * Add custom dashboard widget for stock data
 */
function stock_scanner_dashboard_widget() {
    wp_add_dashboard_widget(
        'stock_scanner_widget',
        '📈 Stock Scanner Quick View',
        'stock_scanner_dashboard_widget_content'
    );
}
add_action('wp_dashboard_setup', 'stock_scanner_dashboard_widget');

/**
 * Dashboard widget content
 */
function stock_scanner_dashboard_widget_content() {
    ?>
    <div class="stock-scanner-dashboard-widget">
        <p><strong>Popular Stocks Today:</strong></p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 15px 0;">
            <?php echo do_shortcode('[stock_scanner symbol="AAPL"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="TSLA"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="NVDA"]'); ?>
        </div>
        <p>
            <a href="<?php echo home_url('/stock-dashboard/'); ?>" class="button button-primary">
                View Full Dashboard
            </a>
        </p>
    </div>
    <style>
        .stock-scanner-dashboard-widget .stock-scanner-widget {
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }
    </style>
    <?php
}

/**
 * Add admin menu for Stock Scanner theme options
 */
function stock_scanner_admin_menu() {
    add_theme_page(
        'Stock Scanner Options',
        'Stock Scanner',
        'manage_options',
        'stock-scanner-options',
        'stock_scanner_options_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_menu');

/**
 * Theme options page
 */
function stock_scanner_options_page() {
    ?>
    <div class="wrap">
        <h1>📈 Stock Scanner Theme Options</h1>
        
        <div class="card">
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><a href="<?php echo admin_url('options-general.php?page=stock-scanner-settings'); ?>">Plugin Settings</a></li>
                <li><a href="<?php echo admin_url('edit.php?post_type=page'); ?>">Manage Pages</a></li>
                <li><a href="<?php echo admin_url('nav-menus.php'); ?>">Customize Menus</a></li>
                <li><a href="<?php echo admin_url('users.php?page=pmpro-memberslist'); ?>">Member List</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📊 Stock Scanner Pages</h2>
            <p>The following pages were automatically created when you activated the Stock Scanner plugin:</p>
            <ul>
                <li><strong>About Retail Trade Scan Net</strong> - <a href="<?php echo home_url('/about/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Contact Us</strong> - <a href="<?php echo home_url('/contact/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Stock Dashboard</strong> - <a href="<?php echo home_url('/stock-dashboard/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Stock Watchlist</strong> - <a href="<?php echo home_url('/stock-watchlist/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Market News</strong> - <a href="<?php echo home_url('/stock-market-news/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Stock Alerts</strong> - <a href="<?php echo home_url('/stock-alerts/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Membership Plans</strong> - <a href="<?php echo home_url('/membership-plans/'); ?>" target="_blank">View Page</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🎨 Theme Features</h2>
            <ul>
                <li>✅ Responsive design for all devices</li>
                <li>✅ Dark mode support</li>
                <li>✅ Real-time stock widgets</li>
                <li>✅ Membership level badges</li>
                <li>✅ Custom login page styling</li>
                <li>✅ Dashboard stock widget</li>
                <li>✅ Professional pricing tables</li>
                <li>✅ Smooth animations and transitions</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🚀 Getting Started</h2>
            <ol>
                <li>Ensure the Stock Scanner plugin is activated and configured</li>
                <li>Set up Paid Membership Pro with your membership levels</li>
                <li>Configure your API settings in Settings → Stock Scanner</li>
                <li>Customize your navigation menu in Appearance → Menus</li>
                <li>Test the stock widgets on your pages</li>
            </ol>
        </div>
    </div>
    
    <style>
        .card {
            background: white;
            border: 1px solid #ccd0d4;
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 1px 1px rgba(0,0,0,0.04);
        }
        .card h2 {
            margin-top: 0;
            color: #23282d;
        }
        .card ul, .card ol {
            margin-left: 20px;
        }
        .card li {
            margin-bottom: 8px;
        }
    </style>
    <?php
}

/**
 * Widget areas
 */
function stock_scanner_widgets_init() {
    register_sidebar(array(
        'name' => __('Footer Widget Area 1', 'stock-scanner'),
        'id' => 'footer-1',
        'description' => __('Widgets in this area will be shown in the first footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
    
    register_sidebar(array(
        'name' => __('Footer Widget Area 2', 'stock-scanner'),
        'id' => 'footer-2',
        'description' => __('Widgets in this area will be shown in the second footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
    
    register_sidebar(array(
        'name' => __('Footer Widget Area 3', 'stock-scanner'),
        'id' => 'footer-3',
        'description' => __('Widgets in this area will be shown in the third footer column.', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * Customizer additions
 */
function stock_scanner_customize_register($wp_customize) {
    // Theme Colors Section
    $wp_customize->add_section('stock_scanner_colors', array(
        'title' => __('Stock Scanner Colors', 'stock-scanner'),
        'priority' => 30,
    ));
    
    // Primary Color
    $wp_customize->add_setting('primary_color', array(
        'default' => '#2271b1',
        'sanitize_callback' => 'sanitize_hex_color',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'primary_color', array(
        'label' => __('Primary Color', 'stock-scanner'),
        'section' => 'stock_scanner_colors',
        'settings' => 'primary_color',
    )));
    
    // Social Links Section
    $wp_customize->add_section('stock_scanner_social', array(
        'title' => __('Social Links', 'stock-scanner'),
        'priority' => 35,
    ));
    
    // Social Media Links
    $social_sites = array('twitter', 'facebook', 'linkedin', 'youtube');
    foreach ($social_sites as $site) {
        $wp_customize->add_setting($site . '_url', array(
            'default' => '',
            'sanitize_callback' => 'esc_url_raw',
        ));
        
        $wp_customize->add_control($site . '_url', array(
            'label' => sprintf(__('%s URL', 'stock-scanner'), ucfirst($site)),
            'section' => 'stock_scanner_social',
            'type' => 'url',
        ));
    }
}
add_action('customize_register', 'stock_scanner_customize_register');

/**
 * Add custom body classes
 */
function stock_scanner_body_classes($classes) {
    if (is_user_logged_in() && function_exists('get_user_membership_level')) {
        $user_id = get_current_user_id();
        $membership_level = get_user_membership_level($user_id);
        $classes[] = 'membership-' . $membership_level;
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Remove admin bar for non-admins on frontend
 */
function stock_scanner_remove_admin_bar() {
    if (!current_user_can('administrator') && !is_admin()) {
        show_admin_bar(false);
    }
}
add_action('after_setup_theme', 'stock_scanner_remove_admin_bar');

/**
 * Add custom CSS for membership levels
 */
function stock_scanner_membership_styles() {
    ?>
    <style type="text/css">
        /* Premium member highlights */
        .membership-premium .stock-scanner-widget {
            border-left: 4px solid #f39c12;
        }
        
        /* Professional member highlights */
        .membership-professional .stock-scanner-widget {
            border-left: 4px solid #9b59b6;
            background: linear-gradient(135deg, #fff 0%, #f4f1f8 100%);
        }
        
        /* Hide upgrade notices for premium+ members */
        .membership-premium .upgrade-notice,
        .membership-professional .upgrade-notice {
            display: none;
        }
    </style>
    <?php
}
add_action('wp_head', 'stock_scanner_membership_styles');

/**
 * Add structured data for SEO
 */
function stock_scanner_structured_data() {
    if (is_front_page() || is_home()) {
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Organization',
            'name' => get_bloginfo('name'),
            'url' => home_url(),
            'description' => get_bloginfo('description'),
            'sameAs' => array()
        );
        
        // Add social media links
        $social_sites = array('twitter', 'facebook', 'linkedin', 'youtube');
        foreach ($social_sites as $site) {
            $url = get_theme_mod($site . '_url');
            if ($url) {
                $schema['sameAs'][] = $url;
            }
        }
        
        echo '<script type="application/ld+json">' . json_encode($schema) . '</script>';
    }
}
add_action('wp_head', 'stock_scanner_structured_data');

/**
 * Add meta tags for SEO and social sharing
 */
function stock_scanner_meta_tags() {
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<meta name="theme-color" content="' . get_theme_mod('primary_color', '#2271b1') . '">';
    
    // Open Graph tags
    echo '<meta property="og:site_name" content="' . get_bloginfo('name') . '">';
    echo '<meta property="og:type" content="website">';
    echo '<meta property="og:url" content="' . get_permalink() . '">';
    echo '<meta property="og:title" content="' . get_the_title() . '">';
    echo '<meta property="og:description" content="' . get_bloginfo('description') . '">';
    
    // Twitter Card tags
    echo '<meta name="twitter:card" content="summary_large_image">';
    echo '<meta name="twitter:title" content="' . get_the_title() . '">';
    echo '<meta name="twitter:description" content="' . get_bloginfo('description') . '">';
}
add_action('wp_head', 'stock_scanner_meta_tags');
?>