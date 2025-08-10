<?php
/**
 * Stock Scanner Theme Functions
 * Professional WordPress theme with SEO optimization and AI ranking features
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
    add_theme_support('automatic-feed-links');
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');
    add_theme_support('wp-block-styles');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner'),
        'footer' => __('Footer Menu', 'stock-scanner'),
        'mobile' => __('Mobile Menu', 'stock-scanner'),
    ));
    
    // Set content width for responsive images
    $GLOBALS['content_width'] = 1200;
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/**
 * Enqueue scripts and styles with performance optimizations
 */
function stock_scanner_scripts() {
    // Performance: Inline critical CSS for fastest first paint
    add_action('wp_head', 'stock_scanner_inline_critical_css', 1);
    
    // Enqueue theme stylesheet with WordPress admin colors (non-blocking)
    $style_file = get_stylesheet_directory() . '/style.css';
    $style_ver = file_exists($style_file) ? filemtime($style_file) : '2.1.0';
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), $style_ver);
    
    // Performance: Load CSS non-blocking
    add_filter('style_loader_tag', 'stock_scanner_async_css', 10, 2);
    
    // Add shared styles for unified color scheme across pages
    if (file_exists(get_template_directory() . '/assets/css/shared-styles.css')) {
        wp_enqueue_style('stock-scanner-shared', get_template_directory_uri() . '/assets/css/shared-styles.css', array(), $style_ver);
    }
    
    // Performance: Enqueue optimized JavaScript
    wp_enqueue_script(
        'stock-scanner-performance',
        get_template_directory_uri() . '/assets/js/performance-optimized.js',
        array('jquery'),
        $style_ver,
        true // Load in footer
    );
    
    // Performance: Add preload hints for critical resources
    add_action('wp_head', 'stock_scanner_resource_hints', 2);
    
    // Performance: Localize script with theme settings
    wp_localize_script('stock-scanner-performance', 'stockScannerTheme', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'enablePerformanceMonitoring' => defined('WP_DEBUG') && WP_DEBUG,
        'lazyLoadOffset' => '50px',
        'debounceDelay' => 300
    ));
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Enqueue theme JavaScript (check if file exists)
    if (file_exists(get_template_directory() . '/assets/js/theme.js')) {
        wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/assets/js/theme.js', array('jquery'), '2.0.0', true);
    }
    // Chart.js theme defaults
    if (file_exists(get_template_directory() . '/assets/js/chart-theme.js')) {
        wp_enqueue_script('stock-scanner-chart-theme', get_template_directory_uri() . '/assets/js/chart-theme.js', array('chart-js'), '1.0.0', true);
    }
    
    // Enqueue plugin integration JavaScript
    if (file_exists(get_template_directory() . '/assets/js/plugin-integration.js')) {
        wp_enqueue_script('stock-scanner-plugin-js', get_template_directory_uri() . '/assets/js/plugin-integration.js', array('jquery'), '2.0.0', true);
    }
    
    // Localize script for AJAX with WordPress admin colors
    // Localize both plugin integration and enhanced UI consumers
    wp_localize_script('stock-scanner-plugin-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce'),
        'colors' => array(
            'primary' => get_theme_mod('primary_color', '#2271b1'),
            'secondary' => '#646970',
            'success' => '#00a32a',
            'error' => '#d63638',
            'warning' => '#dba617',
            'background' => '#f0f0f1'
        ),
        'api_limits' => array(
            'free' => 15,
            'bronze' => 1500,
            'silver' => 5000,
            'gold' => -1
        ),
        'settings' => (class_exists('StockScannerThemeSettings') ? StockScannerThemeSettings::get_settings() : array()),
        'rest_nonce' => wp_create_nonce('wp_rest')
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

// Ensure Bootstrap and shared scripts required by News/Watchlist are present
add_action('wp_enqueue_scripts', function() {
    // Determine current context
    $is_home = is_front_page() || is_home();
    $is_screener = is_page('stock-screener');
    $is_watchlist = is_page('watchlist');
    $is_news = is_page('stock-news') || is_page('news-feed');
    $is_portfolio = is_page('portfolio');

    // Bootstrap CSS/JS for theme UI components used by templates (load on needed pages only)
    if ($is_home || $is_screener || $is_watchlist || $is_news || $is_portfolio) {
        // Bootstrap CSS removed to keep a single site-wide stylesheet
        // wp_enqueue_style('bootstrap-5', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css', [], '5.3.2');
        wp_enqueue_script('bootstrap-5', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js', [], '5.3.2', true);
    }

    // Shared functions (managers for News/Watchlist/Portfolio)
    if (($is_watchlist || $is_news || $is_portfolio) && file_exists(get_template_directory() . '/assets/js/shared/shared-functions.js')) {
        wp_enqueue_script('stock-scanner-shared', get_template_directory_uri() . '/assets/js/shared/shared-functions.js', ['jquery'], '2.0.0', true);
    }
    // Enhanced UI helpers (skeletons, offline, cmd palette)
    if (($is_home || $is_screener || $is_watchlist || $is_news || $is_portfolio) && file_exists(get_template_directory() . '/assets/js/enhanced/enhanced-ui.js')) {
        wp_enqueue_script('stock-scanner-enhanced-ui', get_template_directory_uri() . '/assets/js/enhanced/enhanced-ui.js', ['jquery'], '2.0.0', true);
    }
    // Screener advanced features (URL sync, saved screens)
    if ($is_screener && file_exists(get_template_directory() . '/assets/js/advanced-screener.js')) {
        wp_enqueue_script('stock-scanner-advanced-screener', get_template_directory_uri() . '/assets/js/advanced-screener.js', ['jquery','stock-scanner-plugin-js'], '2.0.1', true);
    }
}, 11);

/**
 * Include plugin integration
 */
require_once get_template_directory() . '/inc/plugin-integration.php';
require_once get_template_directory() . '/inc/admin-settings.php';

// Admin settings is already included above - this duplicate removed to fix include conflicts

// Create screener saved screens table on theme activation if it doesn't exist
function stock_scanner_create_tables(){
    global $wpdb; $charset = $wpdb->get_charset_collate();
    $table = $wpdb->prefix . 'stock_scanner_screens';
    $sql = "CREATE TABLE IF NOT EXISTS $table (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        name VARCHAR(190) NOT NULL,
        payload TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        PRIMARY KEY (id),
        KEY user_id (user_id)
    ) $charset;";
    require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    dbDelta($sql);
}
add_action('after_switch_theme', 'stock_scanner_create_tables');

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
    
    // Setup SEO defaults
    stock_scanner_setup_seo_defaults();
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'stock_scanner_theme_activation');

/**
 * Clear existing Stock Scanner pages
 */
function stock_scanner_clear_existing_pages() {
    $page_slugs = array(
        'dashboard', 'stock-scanner', 'stock-screener', 'stock-news', 'watchlist', 'market-overview', 'account', 
        'premium-plans', 'payment-success', 'payment-cancelled', 'contact', 
        'about', 'privacy-policy', 'terms-of-service', 'faq', 'stock-search',
        'news-feed', 'personalized-news', 'portfolio', 'alerts', 'help', 'api-docs',
        // Also remove plugin-created slugs to avoid duplicates
        'stock-scanner-dashboard', 'watchlists', 'analytics'
    );
    
    foreach ($page_slugs as $slug) {
        // Redirect deprecated enhanced-watchlist to watchlist
        if ($slug === 'enhanced-watchlist') {
            $deprecated = get_page_by_path('enhanced-watchlist');
            if ($deprecated) {
                // Update slug to redirect content
                wp_update_post(array('ID' => $deprecated->ID, 'post_name' => 'watchlist')); // ensure URL matches
            }
        }
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
        'meta_query' => array(
            'relation' => 'OR',
            array(
                'key' => 'stock_scanner_page',
                'compare' => 'EXISTS',
            ),
            array(
                'key' => '_stock_scanner_page',
                'compare' => 'EXISTS',
            ),
        ),
        'posts_per_page' => -1
    ));
    
    foreach ($existing_pages as $page) {
        wp_delete_post($page->ID, true);
    }
}

/**
 * Create Stock Scanner pages with SEO optimization
 */
function stock_scanner_create_pages() {
    $pages = array(
        array(
            'title' => 'Home',
            'slug' => 'home',
            'content' => '',
            'meta_description' => 'Professional stock scanner platform with real-time data, powerful screening, and personalized insights.',
            'template' => 'page-templates/page-home.php'
        ),
        array(
            'title' => 'Dashboard',
            'slug' => 'dashboard',
            'content' => '[stock_scanner_dashboard]',
            'meta_description' => 'Your personalized Stock Scanner dashboard with market overview, usage stats, and quick actions.',
            'template' => 'page-dashboard.php'
        ),
        array(
            'title' => 'Stock Lookup',
            'slug' => 'stock-lookup',
            'content' => '<div class="page-content-wrapper">[stock_lookup_tool]</div>',
            'meta_description' => 'Real-time stock quote lookup with current prices, volume, and basic stock information.',
            'template' => 'page-templates/page-stock-lookup.php'
        ),
        array(
            'title' => 'Stock News',
            'slug' => 'stock-news',
            'content' => '<div class="page-content-wrapper">[stock_news_feed]</div>',
            'meta_description' => 'Latest stock market news, financial analysis, and market updates for informed trading decisions.',
            'template' => 'page-templates/page-stock-news.php'
        ),
        array(
            'title' => 'Stock Screener',
            'slug' => 'stock-screener',
            'content' => '<div class="page-content-wrapper">[stock_scanner_tool]</div>',
            'meta_description' => 'Professional stock screener with advanced filtering options to find stocks matching your investment criteria.',
            'template' => 'page-templates/page-stock-screener.php'
        ),
        
        array(
            'title' => 'My Watchlist',
            'slug' => 'watchlist',
            'content' => '<div class="page-content-wrapper">[stock_watchlist_manager]</div>',
            'meta_description' => 'Manage your stock watchlist with real-time price tracking, alerts, and portfolio monitoring tools.',
            'template' => 'page-watchlist.php'
        ),
        // Enhanced Watchlist deprecated in favor of unified Watchlist page
        // array(
        //     'title' => 'Enhanced Watchlist',
        //     'slug' => 'enhanced-watchlist',
        //     'content' => '',
        //     'meta_description' => 'Advanced watchlist management with import/export, performance tracking, and alerts.',
        //     'template' => 'page-templates/page-enhanced-watchlist.php'
        // ),
        array(
            'title' => 'My Portfolio',
            'slug' => 'portfolio',
            'content' => '',
            'meta_description' => 'Create and manage your investment portfolios with real-time performance analytics and ROI tracking.',
            'template' => 'page-templates/page-portfolio.php'
        ),
        array(
            'title' => 'Market Overview',
            'slug' => 'market-overview',
            'content' => '<div class="page-content-wrapper">[market_overview_dashboard]</div>',
            'meta_description' => 'Comprehensive market overview with real-time data on major indices, market trends, and stock performance.',
            'template' => 'page-templates/page-market-overview.php'
        ),
        array(
            'title' => 'My Account',
            'slug' => 'account',
            'content' => '<div class="page-content-wrapper">[user_account_manager]</div>',
            'meta_description' => 'Manage your Stock Scanner account, subscription plans, and view detailed usage statistics.',
            'template' => 'page-account.php'
        ),
        array(
            'title' => 'Premium Plans',
            'slug' => 'premium-plans',
            'content' => '[stock_scanner_pricing]',
            'meta_description' => 'Choose from our flexible premium plans with advanced stock analysis tools, unlimited API calls, and priority support.',
            'template' => 'page-premium-plans.php'
        ),
        array(
            'title' => 'Payment Success',
            'slug' => 'payment-success',
            'content' => '<h2>Payment Successful!</h2><p>Thank you for upgrading! Your premium features are now active.</p><p><a href="/dashboard/">Go to Dashboard</a></p>',
            'meta_description' => 'Payment confirmation page for Stock Scanner premium subscription upgrade.',
            'template' => 'page-payment-success.php'
        ),
        array(
            'title' => 'Payment Cancelled',
            'slug' => 'payment-cancelled',
            'content' => '<h2>Payment Cancelled</h2><p>Your payment was cancelled. You can try again anytime.</p><p><a href="/premium-plans/">View Plans</a></p>',
            'meta_description' => 'Payment cancellation page for Stock Scanner subscription.',
            'template' => 'page-payment-cancelled.php'
        ),
        array(
            'title' => 'Contact Us',
            'slug' => 'contact',
            'content' => '<h2>Contact Stock Scanner Support</h2><p>Get help with your account or technical questions from our expert support team.</p>',
            'meta_description' => 'Contact Stock Scanner support team for account help, technical assistance, and customer service.',
            'template' => 'page-contact.php'
        ),
        array(
            'title' => 'About Stock Scanner',
            'slug' => 'about',
            'content' => '<h2>About Stock Scanner</h2><p>Professional stock analysis platform providing real-time market data and advanced trading tools for investors.</p>',
            'meta_description' => 'Learn about Stock Scanner - the professional platform for stock analysis, market data, and investment research tools.',
            'template' => 'page-about.php'
        ),
        array(
            'title' => 'Privacy Policy',
            'slug' => 'privacy-policy',
            'content' => '<h2>Privacy Policy</h2><p>We protect your personal information and respect your privacy rights in accordance with data protection laws.</p>',
            'meta_description' => 'Stock Scanner privacy policy - how we collect, use, and protect your personal and financial information.',
            'template' => 'page-privacy.php'
        ),
        array(
            'title' => 'Terms of Service',
            'slug' => 'terms-of-service',
            'content' => '<h2>Terms of Service</h2><p>Terms and conditions for using Stock Scanner platform and services.</p>',
            'meta_description' => 'Stock Scanner terms of service and user agreement for platform usage and subscription services.',
            'template' => 'page-terms.php'
        ),
        array(
            'title' => 'Frequently Asked Questions',
            'slug' => 'faq',
            'content' => '<h2>FAQ</h2><p>Common questions about Stock Scanner features, pricing, and account management.</p>',
            'meta_description' => 'Frequently asked questions about Stock Scanner platform, features, pricing plans, and account management.',
            'template' => 'page-faq.php'
        ),
        array(
            'title' => 'Login',
            'slug' => 'login',
            'content' => '',
            'meta_description' => 'Login to access your Stock Scanner dashboard and tools.',
            'template' => 'page-login.php'
        ),
        array(
            'title' => 'Getting Started',
            'slug' => 'getting-started',
            'content' => '',
            'meta_description' => 'Step-by-step guide to get started with Stock Scanner.',
            'template' => 'page-getting-started.php'
        ),
        array(
            'title' => 'How It Works',
            'slug' => 'how-it-works',
            'content' => '',
            'meta_description' => 'Overview of how Stock Scanner works and key features.',
            'template' => 'page-how-it-works.php'
        ),
        array(
            'title' => 'Help Center',
            'slug' => 'help-center',
            'content' => '',
            'meta_description' => 'Help Center with guides, FAQs, and tips.',
            'template' => 'page-help-center.php'
        ),
        array(
            'title' => 'Glossary',
            'slug' => 'glossary',
            'content' => '',
            'meta_description' => 'Glossary of common stock market terms and definitions.',
            'template' => 'page-glossary.php'
        ),
        array(
            'title' => 'Market Hours & Holidays',
            'slug' => 'market-hours',
            'content' => '',
            'meta_description' => 'Market hours and holiday schedule for major exchanges.',
            'template' => 'page-market-hours.php'
        ),
        array(
            'title' => 'Keyboard Shortcuts',
            'slug' => 'shortcuts',
            'content' => '',
            'meta_description' => 'Keyboard shortcuts to navigate the app faster.',
            'template' => 'page-keyboard-shortcuts.php'
        ),
        array(
            'title' => 'Accessibility',
            'slug' => 'accessibility',
            'content' => '',
            'meta_description' => 'Our commitment to accessibility and inclusive design.',
            'template' => 'page-accessibility.php'
        ),
        array(
            'title' => 'Security',
            'slug' => 'security',
            'content' => '',
            'meta_description' => 'Security practices and how we protect your data.',
            'template' => 'page-security.php'
        ),
        array(
            'title' => 'Cookie Policy',
            'slug' => 'cookie-policy',
            'content' => '',
            'meta_description' => 'Information about cookies used by the site.',
            'template' => 'page-cookie-policy.php'
        ),
        array(
            'title' => 'System Status',
            'slug' => 'status',
            'content' => '',
            'meta_description' => 'Current system status and recent incidents.',
            'template' => 'page-status.php'
        ),
        array(
            'title' => 'Compare Plans',
            'slug' => 'compare-plans',
            'content' => '',
            'meta_description' => 'Compare all plans and features side-by-side.',
            'template' => 'page-compare-plans.php'
        ),
        array(
            'title' => 'Release Notes',
            'slug' => 'release-notes',
            'content' => '',
            'meta_description' => 'Latest improvements and changes to Stock Scanner.',
            'template' => 'page-release-notes.php'
        ),
        array(
            'title' => 'Roadmap',
            'slug' => 'roadmap',
            'content' => '',
            'meta_description' => 'Upcoming features and priorities.',
            'template' => 'page-roadmap.php'
        ),
        array(
            'title' => 'Sitemap',
            'slug' => 'sitemap',
            'content' => '',
            'meta_description' => 'Explore all major pages at a glance.',
            'template' => 'page-sitemap.php'
        ),
        array(
            'title' => 'Personalized News',
            'slug' => 'personalized-news',
            'content' => '',
            'meta_description' => 'Tailored stock market news feed based on your holdings, watchlists, and interests.',
            'template' => 'page-templates/page-personalized-news.php'
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
            
            // Add SEO meta description
            if (isset($page_data['meta_description'])) {
                update_post_meta($page_id, '_stock_scanner_meta_description', $page_data['meta_description']);
            }
            
            // Add structured data
            update_post_meta($page_id, '_stock_scanner_page', 'yes');
        }
    }
    
    // Set homepage to dashboard for logged-in users
            $homepage = get_page_by_path('dashboard');
        // Also set a static posts page if none set to avoid redirect loops
        if (!get_option('page_for_posts')) {
            $posts_page = get_page_by_path('news-feed');
            if ($posts_page) {
                update_option('page_for_posts', $posts_page->ID);
            }
        }
    if ($homepage) {
        update_option('page_on_front', $homepage->ID);
        update_option('show_on_front', 'page');
    }
}

/**
 * Create navigation menus with professional structure
 */
function stock_scanner_create_menus() {
    // Delete existing menus
    $existing_menus = wp_get_nav_menus();
    foreach ($existing_menus as $menu) {
        if (strpos($menu->name, 'Stock Scanner') !== false || 
            in_array($menu->name, array('Primary Menu', 'Footer Menu', 'Mobile Menu'))) {
            wp_delete_nav_menu($menu->term_id);
        }
    }
    
    // Create Primary Menu
    $primary_menu_id = wp_create_nav_menu('Stock Scanner Primary');
    if (!is_wp_error($primary_menu_id)) {
        $menu_items = array(
            array('title' => 'Dashboard', 'url' => '/dashboard/', 'icon' => '📊'),
            array('title' => 'Stock Lookup', 'url' => '/stock-lookup/', 'icon' => '🔍'),
            array('title' => 'Stock News', 'url' => '/stock-news/', 'icon' => '📰'),
            array('title' => 'Stock Screener', 'url' => '/stock-screener/', 'icon' => '🔎'),
            array('title' => 'Market Overview', 'url' => '/market-overview/', 'icon' => '📈'),
            array('title' => 'Watchlist', 'url' => '/watchlist/', 'icon' => '📋'),
            array('title' => 'Premium Plans', 'url' => '/premium-plans/', 'icon' => '⭐'),
            array('title' => 'Contact', 'url' => '/contact/', 'icon' => '📞')
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
            array('title' => 'FAQ', 'url' => '/faq/'),
            array('title' => 'Contact', 'url' => '/contact/')
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
 * Setup SEO defaults for AI ranking optimization
 */
function stock_scanner_setup_seo_defaults() {
    // Set default SEO options
    add_option('stock_scanner_seo_title_format', '%%title%% | %%sitename%% - Professional Stock Analysis');
    add_option('stock_scanner_seo_description_format', '%%description%% Professional stock scanner with real-time market data and advanced analysis tools.');
    add_option('stock_scanner_og_image', get_template_directory_uri() . '/assets/images/og-image.jpg');
    add_option('stock_scanner_schema_organization', json_encode(array(
        '@context' => 'https://schema.org',
        '@type' => 'FinancialService',
        'name' => get_bloginfo('name'),
        'url' => home_url(),
        'description' => 'Professional stock scanner and market analysis platform',
        'serviceType' => 'Financial Data Analysis',
        'areaServed' => 'Global',
        'hasOfferCatalog' => array(
            '@type' => 'OfferCatalog',
            'name' => 'Stock Analysis Plans',
            'itemListElement' => array(
                array('@type' => 'Offer', 'name' => 'Free Plan', 'price' => '0'),
                array('@type' => 'Offer', 'name' => 'Bronze Plan', 'price' => '9.99'),
                array('@type' => 'Offer', 'name' => 'Silver Plan', 'price' => '19.99'),
                array('@type' => 'Offer', 'name' => 'Gold Plan', 'price' => '49.99')
            )
        )
    )));
}

/**
 * Widget areas with enhanced functionality
 */
function stock_scanner_widgets_init() {
    register_sidebar(array(
        'name' => __('Footer Widget Area 1', 'stock-scanner'),
        'id' => 'footer-1',
        'description' => __('Company information and links', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
    
    register_sidebar(array(
        'name' => __('Footer Widget Area 2', 'stock-scanner'),
        'id' => 'footer-2',
        'description' => __('Quick links and navigation', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
    
    register_sidebar(array(
        'name' => __('Footer Widget Area 3', 'stock-scanner'),
        'id' => 'footer-3',
        'description' => __('Contact information and social links', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
    
    register_sidebar(array(
        'name' => __('Dashboard Sidebar', 'stock-scanner'),
        'id' => 'dashboard-sidebar',
        'description' => __('Widgets for the dashboard page', 'stock-scanner'),
        'before_widget' => '<div id="%1$s" class="dashboard-widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h4 class="dashboard-widget-title">',
        'after_title' => '</h4>',
    ));
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * Enhanced customizer with WordPress admin colors
 */
function stock_scanner_customize_register($wp_customize) {
    // WordPress Admin Color Palette Section
    $wp_customize->add_section('stock_scanner_colors', array(
        'title' => __('WordPress Admin Colors', 'stock-scanner'),
        'description' => __('Customize colors using WordPress admin palette', 'stock-scanner'),
        'priority' => 30,
    ));
    
    // Primary Color (WordPress Blue)
    $wp_customize->add_setting('primary_color', array(
        'default' => '#2271b1',
        'sanitize_callback' => 'sanitize_hex_color',
        'transport' => 'refresh',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'primary_color', array(
        'label' => __('Primary Color (WordPress Blue)', 'stock-scanner'),
        'section' => 'stock_scanner_colors',
        'settings' => 'primary_color',
        'description' => __('Default: #2271b1', 'stock-scanner'),
    )));
    
    // Secondary Color (WordPress Gray)
    $wp_customize->add_setting('secondary_color', array(
        'default' => '#646970',
        'sanitize_callback' => 'sanitize_hex_color',
        'transport' => 'refresh',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'secondary_color', array(
        'label' => __('Secondary Color (WordPress Gray)', 'stock-scanner'),
        'section' => 'stock_scanner_colors',
        'settings' => 'secondary_color',
        'description' => __('Default: #646970', 'stock-scanner'),
    )));
    
    // SEO Settings Section
    $wp_customize->add_section('stock_scanner_seo', array(
        'title' => __('SEO & AI Optimization', 'stock-scanner'),
        'description' => __('Configure SEO settings for better search engine ranking', 'stock-scanner'),
        'priority' => 35,
    ));
    
    // Site Description for SEO
    $wp_customize->add_setting('seo_description', array(
        'default' => 'Professional stock scanner with real-time market data, advanced analysis tools, and portfolio tracking for investors and traders.',
        'sanitize_callback' => 'sanitize_textarea_field',
    ));
    
    $wp_customize->add_control('seo_description', array(
        'label' => __('SEO Description', 'stock-scanner'),
        'section' => 'stock_scanner_seo',
        'type' => 'textarea',
        'description' => __('Main description for search engines and AI platforms', 'stock-scanner'),
    ));
    
    // Keywords for AI ranking
    $wp_customize->add_setting('seo_keywords', array(
        'default' => 'stock scanner, market analysis, real-time stock data, portfolio tracking, investment tools, financial analysis',
        'sanitize_callback' => 'sanitize_text_field',
    ));
    
    $wp_customize->add_control('seo_keywords', array(
        'label' => __('SEO Keywords', 'stock-scanner'),
        'section' => 'stock_scanner_seo',
        'type' => 'text',
        'description' => __('Keywords for AI platforms and search engines', 'stock-scanner'),
    ));
    
    // Social Links Section
    $wp_customize->add_section('stock_scanner_social', array(
        'title' => __('Social Links', 'stock-scanner'),
        'description' => __('Add social media links for better SEO', 'stock-scanner'),
        'priority' => 40,
    ));
    
    // Social Media Links for SEO
    $social_sites = array('twitter', 'facebook', 'linkedin', 'youtube', 'instagram');
    foreach ($social_sites as $site) {
        $wp_customize->add_setting($site . '_url', array(
            'default' => '',
            'sanitize_callback' => 'esc_url_raw',
        ));
        
        $wp_customize->add_control($site . '_url', array(
            'label' => sprintf(__('%s URL', 'stock-scanner'), ucfirst($site)),
            'section' => 'stock_scanner_social',
            'type' => 'url',
            'description' => __('Improves SEO and social signals', 'stock-scanner'),
        ));
    }
}
add_action('customize_register', 'stock_scanner_customize_register');

/**
 * Add custom body classes for styling and AI identification
 */
function stock_scanner_body_classes($classes) {
    // Add membership level class
    if (is_user_logged_in() && function_exists('get_user_membership_level')) {
        $user_id = get_current_user_id();
        $membership_level = get_user_membership_level($user_id);
        $classes[] = 'membership-' . $membership_level;
    }
    
    // Add page-specific classes for AI understanding
    if (is_page()) {
        global $post;
        $classes[] = 'stock-scanner-page';
        $classes[] = 'page-' . $post->post_name;
        
        // Add financial services class for AI recognition
        $classes[] = 'financial-services';
        $classes[] = 'stock-analysis-platform';
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Enhanced SEO and structured data for AI ranking
 */
function stock_scanner_head_seo() {
    // Basic SEO meta tags
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<meta name="theme-color" content="' . get_theme_mod('primary_color', '#2271b1') . '">';
    echo '<meta name="robots" content="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large">';
    
    // Keywords for AI platforms
    $keywords = get_theme_mod('seo_keywords', 'stock scanner, market analysis, real-time stock data, portfolio tracking, investment tools');
    echo '<meta name="keywords" content="' . esc_attr($keywords) . '">';
    
    // Author and publisher info
    echo '<meta name="author" content="' . get_bloginfo('name') . '">';
    echo '<link rel="publisher" href="' . home_url() . '">';
    
    // Canonical URL
    if (is_singular()) {
        echo '<link rel="canonical" href="' . get_permalink() . '">';
    } else {
        echo '<link rel="canonical" href="' . home_url() . '">';
    }
    
    // Open Graph tags for social sharing and AI
    $og_description = get_theme_mod('seo_description', 'Professional stock scanner with real-time market data and advanced analysis tools');
    echo '<meta property="og:site_name" content="' . get_bloginfo('name') . '">';
    echo '<meta property="og:type" content="website">';
    echo '<meta property="og:locale" content="en_US">';
    
    if (is_singular()) {
        echo '<meta property="og:url" content="' . get_permalink() . '">';
        echo '<meta property="og:title" content="' . get_the_title() . ' | ' . get_bloginfo('name') . '">';
        
        $meta_desc = get_post_meta(get_the_ID(), '_stock_scanner_meta_description', true);
        if ($meta_desc) {
            echo '<meta property="og:description" content="' . esc_attr($meta_desc) . '">';
            echo '<meta name="description" content="' . esc_attr($meta_desc) . '">';
        } else {
            echo '<meta property="og:description" content="' . esc_attr($og_description) . '">';
            echo '<meta name="description" content="' . esc_attr($og_description) . '">';
        }
    } else {
        echo '<meta property="og:url" content="' . home_url() . '">';
        echo '<meta property="og:title" content="' . get_bloginfo('name') . ' - Professional Stock Analysis Platform">';
        echo '<meta property="og:description" content="' . esc_attr($og_description) . '">';
        echo '<meta name="description" content="' . esc_attr($og_description) . '">';
    }
    
    // Twitter Card tags
    echo '<meta name="twitter:card" content="summary_large_image">';
    echo '<meta name="twitter:site" content="@stockscanner">';
    
    if (is_singular()) {
        echo '<meta name="twitter:title" content="' . get_the_title() . '">';
    } else {
        echo '<meta name="twitter:title" content="' . get_bloginfo('name') . '">';
    }
    
    // Financial service specific meta tags for AI
    echo '<meta name="category" content="Financial Services">';
    echo '<meta name="coverage" content="Worldwide">';
    echo '<meta name="distribution" content="Global">';
    echo '<meta name="rating" content="General">';
    
    // Preconnect to external domains for performance
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    echo '<link rel="preconnect" href="https://cdn.jsdelivr.net">';
    echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">';
    echo '<link rel="dns-prefetch" href="//fonts.gstatic.com">';
    echo '<link rel="dns-prefetch" href="//cdn.jsdelivr.net">';
}
add_action('wp_head', 'stock_scanner_head_seo', 1);

/**
 * Custom navigation walker to hide current page link
 */
class Stock_Scanner_Nav_Walker extends Walker_Nav_Menu {
    function start_el(&$output, $item, $depth = 0, $args = null, $id = 0) {
        global $wp_query;
        
        $current_page = get_queried_object();
        $current_slug = '';
        if ($current_page && isset($current_page->post_name)) {
            $current_slug = $current_page->post_name;
        }
        
        // Skip rendering if this is the current page
        $item_url = $item->url;
        if (strpos($item_url, '/' . $current_slug . '/') !== false) {
            return;
        }
        
        $indent = ($depth) ? str_repeat("\t", $depth) : '';
        
        $classes = empty($item->classes) ? array() : (array) $item->classes;
        $classes[] = 'menu-item-' . $item->ID;
        
        $class_names = join(' ', apply_filters('nav_menu_css_class', array_filter($classes), $item, $args));
        $class_names = $class_names ? ' class="' . esc_attr($class_names) . '"' : '';
        
        $id = apply_filters('nav_menu_item_id', 'menu-item-' . $item->ID, $item, $args);
        $id = $id ? ' id="' . esc_attr($id) . '"' : '';
        
        $output .= $indent . '<li' . $id . $class_names .'>';
        
        $attributes = ! empty($item->attr_title) ? ' title="' . esc_attr($item->attr_title) .'"' : '';
        $attributes .= ! empty($item->target) ? ' target="' . esc_attr($item->target ) .'"' : '';
        $attributes .= ! empty($item->xfn) ? ' rel="' . esc_attr($item->xfn ) .'"' : '';
        $attributes .= ! empty($item->url) ? ' href="' . esc_attr($item->url ) .'"' : '';
        
        $item_output = $args->before ?? '';
        $item_output .= '<a' . $attributes .'>';
        $item_output .= ($args->link_before ?? '') . apply_filters('the_title', $item->title, $item->ID) . ($args->link_after ?? '');
        $item_output .= '</a>';
        $item_output .= $args->after ?? '';
        
        $output .= apply_filters('walker_nav_menu_start_el', $item_output, $item, $depth, $args);
    }
}

/**
 * Comprehensive structured data for AI ranking
 */
function stock_scanner_structured_data() {
    $schema_data = array();
    
    // Organization schema
    $schema_data[] = array(
        '@context' => 'https://schema.org',
        '@type' => 'FinancialService',
        'name' => get_bloginfo('name'),
        'alternateName' => 'Stock Scanner',
        'url' => home_url(),
        'description' => get_theme_mod('seo_description', 'Professional stock scanner with real-time market data and advanced analysis tools'),
        'foundingDate' => '2024',
        'serviceType' => 'Financial Data Analysis',
        'areaServed' => 'Worldwide',
        'hasOfferCatalog' => array(
            '@type' => 'OfferCatalog',
            'name' => 'Stock Analysis Plans',
            'itemListElement' => array(
                array(
                    '@type' => 'Offer',
                    'name' => 'Free Plan',
                    'description' => '15 API calls per month',
                    'price' => '0',
                    'priceCurrency' => 'USD'
                ),
                array(
                    '@type' => 'Offer',
                    'name' => 'Bronze Plan',
                    'description' => '1,500 API calls per month',
                    'price' => '9.99',
                    'priceCurrency' => 'USD'
                ),
                array(
                    '@type' => 'Offer',
                    'name' => 'Silver Plan',
                    'description' => '5,000 API calls per month',
                    'price' => '19.99',
                    'priceCurrency' => 'USD'
                ),
                array(
                    '@type' => 'Offer',
                    'name' => 'Gold Plan',
                    'description' => 'Unlimited API calls',
                    'price' => '49.99',
                    'priceCurrency' => 'USD'
                )
            )
        ),
        'contactPoint' => array(
            '@type' => 'ContactPoint',
            'contactType' => 'Customer Service',
            'url' => home_url('/contact/'),
            'availableLanguage' => 'English'
        )
    );
    
    // Add social media links
    $social_links = array();
    $social_sites = array('twitter', 'facebook', 'linkedin', 'youtube', 'instagram');
    foreach ($social_sites as $site) {
        $url = get_theme_mod($site . '_url');
        if ($url) {
            $social_links[] = $url;
        }
    }
    
    if (!empty($social_links)) {
        $schema_data[0]['sameAs'] = $social_links;
    }
    
    // Website schema
    $schema_data[] = array(
        '@context' => 'https://schema.org',
        '@type' => 'WebSite',
        'name' => get_bloginfo('name'),
        'url' => home_url(),
        'description' => get_theme_mod('seo_description'),
        'inLanguage' => 'en-US',
        'potentialAction' => array(
            '@type' => 'SearchAction',
            'target' => home_url('/stock-scanner/?search={search_term_string}'),
            'query-input' => 'required name=search_term_string'
        )
    );
    
    // Breadcrumb schema for navigation
    if (is_page() && !is_front_page()) {
        $schema_data[] = array(
            '@context' => 'https://schema.org',
            '@type' => 'BreadcrumbList',
            'itemListElement' => array(
                array(
                    '@type' => 'ListItem',
                    'position' => 1,
                    'name' => 'Home',
                    'item' => home_url()
                ),
                array(
                    '@type' => 'ListItem',
                    'position' => 2,
                    'name' => get_the_title(),
                    'item' => get_permalink()
                )
            )
        );
    }
    
    // FAQ schema for FAQ page
    if (is_page('faq')) {
        $schema_data[] = array(
            '@context' => 'https://schema.org',
            '@type' => 'FAQPage',
            'mainEntity' => array(
                array(
                    '@type' => 'Question',
                    'name' => 'How many stocks can I scan with the free plan?',
                    'acceptedAnswer' => array(
                        '@type' => 'Answer',
                        'text' => 'The free plan includes 15 API calls per month, allowing you to analyze 15 different stocks.'
                    )
                ),
                array(
                    '@type' => 'Question',
                    'name' => 'What payment methods do you accept?',
                    'acceptedAnswer' => array(
                        '@type' => 'Answer',
                        'text' => 'We accept all major credit cards and PayPal for secure payment processing.'
                    )
                ),
                array(
                    '@type' => 'Question',
                    'name' => 'Can I cancel my subscription anytime?',
                    'acceptedAnswer' => array(
                        '@type' => 'Answer',
                        'text' => 'Yes, you can cancel your subscription at any time with no cancellation fees.'
                    )
                )
            )
        );
    }
    
    // Output all schema data
    foreach ($schema_data as $schema) {
        echo '<script type="application/ld+json">' . wp_json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}
add_action('wp_head', 'stock_scanner_structured_data', 2);

/**
 * Custom CSS for WordPress admin color palette
 */
function stock_scanner_custom_css() {
    $primary_color = get_theme_mod('primary_color', '#2271b1');
    $secondary_color = get_theme_mod('secondary_color', '#646970');
    
    ?>
    <style type="text/css">
        :root {
            --wp-admin-blue: <?php echo $primary_color; ?>;
            --wp-admin-blue-hover: #135e96;
            --wp-admin-gray: <?php echo $secondary_color; ?>;
            --wp-admin-gray-hover: #50575e;
            --wp-admin-green: #00a32a;
            --wp-admin-red: #d63638;
            --wp-admin-yellow: #dba617;
            --wp-admin-background: #f0f0f1;
        }
        
        /* Apply WordPress colors throughout the site */
        .btn-primary, .button-primary {
            background-color: var(--wp-admin-blue) !important;
            border-color: var(--wp-admin-blue) !important;
        }
        
        .btn-primary:hover, .button-primary:hover {
            background-color: var(--wp-admin-blue-hover) !important;
            border-color: var(--wp-admin-blue-hover) !important;
        }
        
        .btn-secondary, .button-secondary {
            background-color: var(--wp-admin-gray) !important;
            border-color: var(--wp-admin-gray) !important;
        }
        
        .btn-secondary:hover, .button-secondary:hover {
            background-color: var(--wp-admin-gray-hover) !important;
            border-color: var(--wp-admin-gray-hover) !important;
        }
        
        .text-success, .success { color: var(--wp-admin-green) !important; }
        .text-error, .error { color: var(--wp-admin-red) !important; }
        .text-warning, .warning { color: var(--wp-admin-yellow) !important; }
        
        /* Navigation styling with WordPress colors */
        .main-nav a:hover {
            color: var(--wp-admin-blue) !important;
        }
        
        /* Membership badges with WordPress colors */
        .membership-free { 
            background: var(--wp-admin-gray); 
            color: white; 
        }
        .membership-bronze { 
            background: #cd7f32; 
            color: white; 
        }
        .membership-silver { 
            background: #c0c0c0; 
            color: #333; 
        }
        .membership-gold { 
            background: #ffd700; 
            color: #333; 
        }
        
        /* Form elements with WordPress styling */
        input[type="text"], input[type="email"], input[type="password"], 
        textarea, select {
            border: 1px solid #8c8f94;
            border-radius: 4px;
            padding: 8px 12px;
        }
        
        input[type="text"]:focus, input[type="email"]:focus, 
        input[type="password"]:focus, textarea:focus, select:focus {
            border-color: var(--wp-admin-blue);
            box-shadow: 0 0 0 1px var(--wp-admin-blue);
            outline: none;
        }
        
        /* Professional styling for all elements */
        .site-header {
            background: var(--wp-admin-background);
            border-bottom: 1px solid #c3c4c7;
        }
        
        .hero-section {
            background: linear-gradient(135deg, var(--wp-admin-blue) 0%, var(--wp-admin-blue-hover) 100%);
        }
    </style>
    <?php
}
// add_action('wp_head', 'stock_scanner_custom_css', 20);

/**
 * Remove admin bar for non-admins on frontend
 */
function stock_scanner_remove_admin_bar() {
    if (!current_user_can('administrator') && !is_admin()) {
        show_admin_bar(false);
    }
}
add_action('after_setup_theme', 'stock_scanner_remove_admin_bar');

// Performance optimizations moved to line 1577 to avoid duplication

/**
 * Custom post types for enhanced SEO
 */
function stock_scanner_custom_post_types() {
    // Stock Analysis post type
    register_post_type('stock_analysis', array(
        'labels' => array(
            'name' => 'Stock Analysis',
            'singular_name' => 'Analysis',
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'analysis'),
        'show_in_rest' => true,
    ));
    
    // Market News post type
    register_post_type('market_news', array(
        'labels' => array(
            'name' => 'Market News',
            'singular_name' => 'News',
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'news'),
        'show_in_rest' => true,
    ));
}
add_action('init', 'stock_scanner_custom_post_types');

/**
 * Custom taxonomies for better organization
 */
function stock_scanner_custom_taxonomies() {
    // Stock sectors taxonomy
    register_taxonomy('stock_sector', array('stock_analysis'), array(
        'labels' => array(
            'name' => 'Stock Sectors',
            'singular_name' => 'Sector',
        ),
        'public' => true,
        'hierarchical' => true,
        'rewrite' => array('slug' => 'sector'),
        'show_in_rest' => true,
    ));
    
    // Market categories taxonomy
    register_taxonomy('market_category', array('market_news'), array(
        'labels' => array(
            'name' => 'Market Categories',
            'singular_name' => 'Category',
        ),
        'public' => true,
        'hierarchical' => true,
        'rewrite' => array('slug' => 'category'),
        'show_in_rest' => true,
    ));
}
add_action('init', 'stock_scanner_custom_taxonomies');

/**
 * Include admin settings (already included at top of file to avoid duplication)
 */
// Admin settings included at line 155 - duplicate removed

/**
 * Helper function to get stock scanner settings
 */
function get_stock_scanner_setting($setting_group, $key, $default = null) {
    $settings = get_option($setting_group, array());
    return isset($settings[$key]) ? $settings[$key] : $default;
}

/**
 * Check if a feature is enabled
 */
function is_stock_scanner_feature_enabled($feature) {
    $feature_settings = get_option('stock_scanner_feature_settings', array());
    return isset($feature_settings[$feature]) && $feature_settings[$feature];
}

/**
 * Get user limits based on membership level
 */
function get_user_limits($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    // Get user membership level (this would be determined by your membership system)
    $membership_level = get_user_meta($user_id, 'membership_level', true) ?: 'free';
    
    $limit_settings = get_option('stock_scanner_limit_settings', array());
    
    return array(
        'api_calls' => $limit_settings[$membership_level . '_api_calls'] ?? 15,
        'portfolios' => $limit_settings[$membership_level . '_portfolios'] ?? 1,
        'watchlists' => $limit_settings[$membership_level . '_watchlists'] ?? 2,
        'holdings' => $limit_settings[$membership_level . '_holdings'] ?? 10
    );
}

/**
 * Get backend API URL
 */
function get_backend_api_url($endpoint = '') {
    $api_settings = get_option('stock_scanner_api_settings', array());
    $backend_url = $api_settings['backend_url'] ?? '';
    
    if (empty($backend_url)) {
        return false;
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
 * Check if maintenance mode is enabled
 */
function is_maintenance_mode_enabled() {
    $advanced_settings = get_option('stock_scanner_advanced_settings', array());
    return isset($advanced_settings['maintenance_mode']) && $advanced_settings['maintenance_mode'];
}

/**
 * Redirect to maintenance page if maintenance mode is enabled
 */
function check_maintenance_mode() {
    if (is_maintenance_mode_enabled() && !current_user_can('administrator') && !is_admin()) {
        $advanced_settings = get_option('stock_scanner_advanced_settings', array());
        $message = $advanced_settings['maintenance_message'] ?? 'We are currently performing scheduled maintenance. Please check back soon.';
        
        wp_die($message, 'Maintenance Mode', array('response' => 503));
    }
}
add_action('wp', 'check_maintenance_mode');

/**
 * AJAX: Register user from signup page
 */
function stock_scanner_register_user() {
    if (!isset($_POST['signup_nonce']) || !wp_verify_nonce($_POST['signup_nonce'], 'user_signup_nonce')) {
        wp_send_json_error('Invalid request.');
    }

    $email = sanitize_email($_POST['user_email'] ?? '');
    $username = sanitize_user($_POST['user_login'] ?? '');
    $password = $_POST['user_pass'] ?? '';
    $password_confirm = $_POST['user_pass_confirm'] ?? '';
    $first_name = sanitize_text_field($_POST['first_name'] ?? '');
    $last_name = sanitize_text_field($_POST['last_name'] ?? '');

    if (empty($email) || empty($username) || empty($password) || empty($password_confirm)) {
        wp_send_json_error('Please complete all required fields.');
    }
    if (!is_email($email)) {
        wp_send_json_error('Please enter a valid email.');
    }
    if (username_exists($username) || email_exists($email)) {
        wp_send_json_error('Username or email already exists.');
    }
    if ($password !== $password_confirm) {
        wp_send_json_error('Passwords do not match.');
    }

    $user_id = wp_create_user($username, $password, $email);
    if (is_wp_error($user_id)) {
        wp_send_json_error('Failed to create account: ' . $user_id->get_error_message());
    }

    // Set profile fields
    wp_update_user(array(
        'ID' => $user_id,
        'first_name' => $first_name,
        'last_name' => $last_name,
        'display_name' => trim($first_name . ' ' . $last_name) ?: $username,
    ));

    // Log in the user
    $creds = array(
        'user_login' => $username,
        'user_password' => $password,
        'remember' => true,
    );
    $user = wp_signon($creds, false);
    if (is_wp_error($user)) {
        wp_send_json_error('Account created, but login failed: ' . $user->get_error_message());
    }

    wp_send_json_success(array('redirect' => home_url('/dashboard/')));
}
add_action('wp_ajax_nopriv_stock_scanner_register_user', 'stock_scanner_register_user');

add_action('init', function(){
    $ensure = function($title, $slug, $template, $content = ''){
        if (!get_page_by_path($slug)) {
            $page_id = wp_insert_post(array(
                'post_title' => $title,
                'post_name' => $slug,
                'post_status' => 'publish',
                'post_type' => 'page',
                'post_author' => 1,
                'post_content' => $content,
            ));
            if ($page_id && !is_wp_error($page_id)) {
                update_post_meta($page_id, '_wp_page_template', $template);
                update_post_meta($page_id, '_stock_scanner_page', 'yes');
            }
        }
    };

    $ensure_template = function($slug, $template){
        $page = get_page_by_path($slug);
        if ($page && !is_wp_error($page)) {
            $current = get_page_template_slug($page->ID);
            if ($current !== $template) {
                update_post_meta($page->ID, '_wp_page_template', $template);
            }
        }
    };

    // Ensure critical feature pages exist without requiring theme re-activation
    $ensure('My Watchlist', 'watchlist', 'page-watchlist.php', '<div class="page-content-wrapper">[stock_watchlist_manager]</div>');
    // Enhanced Watchlist deprecated; use unified Watchlist page
    // $ensure('Enhanced Watchlist', 'enhanced-watchlist', 'page-templates/page-enhanced-watchlist.php');
    $ensure('My Portfolio', 'portfolio', 'page-templates/page-portfolio.php');
    $ensure('Personalized News', 'personalized-news', 'page-templates/page-personalized-news.php');

    // Enforce correct templates for existing pages that users report redirecting to dashboard
    $ensure_template('stock-news', 'page-templates/page-stock-news.php');
    $ensure_template('stock-screener', 'page-templates/page-stock-screener.php');
});

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
    // If the Dashboard is set as the static front page or we're already on it, do not redirect
    if (is_page($dashboard->ID) || ((int) get_option('page_on_front') === (int) $dashboard->ID)) {
        return;
    }
    wp_safe_redirect($dashboard_url, 302);
    exit;
});

/**
 * =======================================================================
 * PERFORMANCE OPTIMIZATION FUNCTIONS
 * =======================================================================
 */

/**
 * Inline critical CSS for fastest first paint
 */
function stock_scanner_inline_critical_css() {
    $critical_css_file = get_template_directory() . '/assets/css/critical.css';
    
    if (file_exists($critical_css_file)) {
        $critical_css = file_get_contents($critical_css_file);
        if ($critical_css) {
            echo '<style id="critical-css">' . $critical_css . '</style>';
        }
    }
}

/**
 * Make CSS non-blocking for better performance
 */
function stock_scanner_async_css($tag, $handle) {
    // Skip critical CSS and admin styles
    if (strpos($handle, 'critical') !== false || is_admin()) {
        return $tag;
    }
    
    // Make CSS non-blocking
    $tag = str_replace("rel='stylesheet'", "rel='preload' as='style' onload=\"this.onload=null;this.rel='stylesheet'\"", $tag);
    $tag .= '<noscript>' . str_replace("rel='preload' as='style' onload=\"this.onload=null;this.rel='stylesheet'\"", "rel='stylesheet'", $tag) . '</noscript>';
    
    return $tag;
}

/**
 * Add resource hints for better performance
 */
function stock_scanner_resource_hints() {
    // DNS prefetch for external resources
    echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">';
    echo '<link rel="dns-prefetch" href="//fonts.gstatic.com">';
    echo '<link rel="dns-prefetch" href="//cdn.jsdelivr.net">';
    
    // Preconnect to critical external domains
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    
    // Preload critical theme assets
    $theme_dir = get_template_directory_uri();
    echo '<link rel="preload" href="' . $theme_dir . '/assets/js/performance-optimized.js" as="script">';
    echo '<link rel="preload" href="' . $theme_dir . '/assets/css/shared-styles.css" as="style">';
}

/**
 * Optimize WordPress for performance
 */
function stock_scanner_performance_optimizations() {
    // Remove unnecessary WordPress features that slow down the site
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    remove_action('wp_head', 'adjacent_posts_rel_link_wp_head');
    
    // Remove emoji scripts (performance drain)
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('admin_print_styles', 'print_emoji_styles');
    
    // Disable embeds for better performance
    remove_action('wp_head', 'wp_oembed_add_discovery_links');
    remove_action('wp_head', 'wp_oembed_add_host_js');
    
    // Remove query strings from static resources for better caching
    add_filter('script_loader_src', 'stock_scanner_remove_query_strings', 15);
    add_filter('style_loader_src', 'stock_scanner_remove_query_strings', 15);
}
add_action('init', 'stock_scanner_performance_optimizations');

/**
 * Remove query strings from static resources
 */
function stock_scanner_remove_query_strings($src) {
    if (strpos($src, '?ver=')) {
        $src = remove_query_arg('ver', $src);
    }
    return $src;
}

/**
 * Add performance-focused image optimization
 */
function stock_scanner_optimize_images($attr, $attachment) {
    // Add lazy loading to images
    if (!is_admin() && !empty($attr['src'])) {
        $attr['loading'] = 'lazy';
        $attr['decoding'] = 'async';
        
        // Add responsive image classes
        $attr['class'] = (isset($attr['class']) ? $attr['class'] . ' ' : '') . 'optimized-image';
    }
    
    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'stock_scanner_optimize_images', 10, 2);

/**
 * Enable WordPress caching headers
 */
function stock_scanner_add_cache_headers() {
    if (!is_admin() && !is_user_logged_in()) {
        // Set cache headers for static content
        $expires = 604800; // 1 week
        header('Cache-Control: public, max-age=' . $expires);
        header('Expires: ' . gmdate('D, d M Y H:i:s', time() + $expires) . ' GMT');
    }
}
add_action('send_headers', 'stock_scanner_add_cache_headers');

/**
 * Add performance monitoring for logged-in admins
 */
function stock_scanner_performance_monitor() {
    if (current_user_can('administrator') && defined('WP_DEBUG') && WP_DEBUG) {
        add_action('wp_footer', function() {
            echo '<script>
                if (window.wpStockScannerPerf) {
                    console.log("WordPress Theme Performance Monitoring Enabled");
                }
            </script>';
        });
    }
}
add_action('wp_loaded', 'stock_scanner_performance_monitor');

?>