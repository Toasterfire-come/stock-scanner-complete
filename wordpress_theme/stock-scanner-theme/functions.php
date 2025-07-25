<?php
/**
 * Stock Scanner Theme Functions
 * Sets up theme features and navigation with SEO & AI optimizations
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
        'breadcrumb' => __('Breadcrumb Menu', 'stock-scanner'),
    ));
    
    // Add support for featured images
    add_theme_support('post-thumbnails');
    set_post_thumbnail_size(1200, 630, true); // For social media sharing
    
    // Add RSS feed links to head for better SEO
    add_theme_support('automatic-feed-links');
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/**
 * SEO & Performance Optimizations
 */

/**
 * Add comprehensive meta tags for SEO and AI ranking
 */
function stock_scanner_seo_meta_tags() {
    global $post;
    
    // Get current page info
    $page_title = '';
    $page_description = '';
    $page_keywords = '';
    $canonical_url = '';
    $og_image = '';
    
    if (is_front_page()) {
        $page_title = get_bloginfo('name') . ' - Advanced Stock Market Scanner & Analysis Platform';
        $page_description = 'Professional stock market scanning, real-time NASDAQ data, news analysis, and portfolio tracking. Advanced AI-powered stock analysis tools for investors and traders.';
        $page_keywords = 'stock scanner, NASDAQ stocks, stock market analysis, real-time stock data, portfolio tracking, stock alerts, market news, investment tools, trading platform';
        $canonical_url = home_url('/');
    } elseif (is_page()) {
        $page_title = get_the_title() . ' - ' . get_bloginfo('name');
        $page_description = get_post_meta($post->ID, '_yoast_wpseo_metadesc', true) ?: wp_trim_words(get_the_content(), 25);
        $page_keywords = get_post_meta($post->ID, 'seo_keywords', true) ?: 'stock market, financial analysis, investment tools';
        $canonical_url = get_permalink();
        
        // Page-specific optimizations
        if (strpos(get_the_title(), 'Stock') !== false || strpos(get_the_title(), 'Market') !== false) {
            $page_keywords .= ', stock screening, market data, financial metrics';
        }
    } elseif (is_single()) {
        $page_title = get_the_title() . ' - ' . get_bloginfo('name');
        $page_description = wp_trim_words(get_the_content(), 25);
        $page_keywords = 'stock market news, financial analysis, market updates, investment insights';
        $canonical_url = get_permalink();
    }
    
    // Get featured image for Open Graph
    if (has_post_thumbnail()) {
        $og_image = get_the_post_thumbnail_url(null, 'large');
    } else {
        $og_image = get_template_directory_uri() . '/images/stock-scanner-og-default.jpg';
    }
    
    // Output meta tags
    echo '<meta name="description" content="' . esc_attr($page_description) . '">' . "\n";
    echo '<meta name="keywords" content="' . esc_attr($page_keywords) . '">' . "\n";
    echo '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">' . "\n";
    echo '<link rel="canonical" href="' . esc_url($canonical_url) . '">' . "\n";
    
    // Open Graph tags for social media
    echo '<meta property="og:locale" content="en_US">' . "\n";
    echo '<meta property="og:type" content="website">' . "\n";
    echo '<meta property="og:title" content="' . esc_attr($page_title) . '">' . "\n";
    echo '<meta property="og:description" content="' . esc_attr($page_description) . '">' . "\n";
    echo '<meta property="og:url" content="' . esc_url($canonical_url) . '">' . "\n";
    echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
    echo '<meta property="og:image" content="' . esc_url($og_image) . '">' . "\n";
    echo '<meta property="og:image:width" content="1200">' . "\n";
    echo '<meta property="og:image:height" content="630">' . "\n";
    
    // Twitter Card tags
    echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
    echo '<meta name="twitter:title" content="' . esc_attr($page_title) . '">' . "\n";
    echo '<meta name="twitter:description" content="' . esc_attr($page_description) . '">' . "\n";
    echo '<meta name="twitter:image" content="' . esc_url($og_image) . '">' . "\n";
    
    // Additional SEO meta tags
    echo '<meta name="author" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
    echo '<meta name="generator" content="Stock Scanner Pro Theme">' . "\n";
    echo '<meta name="theme-color" content="#667eea">' . "\n";
    
    // Structured data for better AI understanding
    stock_scanner_structured_data();
}
add_action('wp_head', 'stock_scanner_seo_meta_tags', 1);

/**
 * Add structured data (JSON-LD) for AI and search engines
 */
function stock_scanner_structured_data() {
    global $post;
    
    $structured_data = array();
    
    // Website schema
    $structured_data['website'] = array(
        '@context' => 'https://schema.org',
        '@type' => 'WebSite',
        'name' => get_bloginfo('name'),
        'description' => get_bloginfo('description'),
        'url' => home_url('/'),
        'potentialAction' => array(
            '@type' => 'SearchAction',
            'target' => array(
                '@type' => 'EntryPoint',
                'urlTemplate' => home_url('/?s={search_term_string}')
            ),
            'query-input' => 'required name=search_term_string'
        )
    );
    
    // Organization schema
    $structured_data['organization'] = array(
        '@context' => 'https://schema.org',
        '@type' => 'FinancialService',
        'name' => get_bloginfo('name'),
        'description' => 'Professional stock market analysis and trading tools platform',
        'url' => home_url('/'),
        'logo' => array(
            '@type' => 'ImageObject',
            'url' => get_template_directory_uri() . '/images/logo.png'
        ),
        'serviceType' => 'Financial Analysis Software',
        'areaServed' => 'Global',
        'hasOfferCatalog' => array(
            '@type' => 'OfferCatalog',
            'name' => 'Stock Analysis Services',
            'itemListElement' => array(
                array(
                    '@type' => 'Offer',
                    'itemOffered' => array(
                        '@type' => 'Service',
                        'name' => 'Real-time Stock Data',
                        'description' => 'Live NASDAQ stock prices and market data'
                    )
                ),
                array(
                    '@type' => 'Offer',
                    'itemOffered' => array(
                        '@type' => 'Service',
                        'name' => 'Stock Analysis Tools',
                        'description' => 'Advanced technical and fundamental analysis'
                    )
                ),
                array(
                    '@type' => 'Offer',
                    'itemOffered' => array(
                        '@type' => 'Service',
                        'name' => 'Market News Analysis',
                        'description' => 'AI-powered sentiment analysis of financial news'
                    )
                )
            )
        )
    );
    
    // Page-specific schema
    if (is_front_page()) {
        $structured_data['webpage'] = array(
            '@context' => 'https://schema.org',
            '@type' => 'WebPage',
            'name' => 'Stock Market Scanner - Real-time Analysis Platform',
            'description' => 'Advanced stock market scanning platform with real-time NASDAQ data, AI-powered analysis, and professional trading tools.',
            'url' => home_url('/'),
            'mainEntity' => array(
                '@type' => 'SoftwareApplication',
                'name' => get_bloginfo('name'),
                'applicationCategory' => 'FinanceApplication',
                'operatingSystem' => 'Web Browser',
                'offers' => array(
                    '@type' => 'Offer',
                    'price' => '0',
                    'priceCurrency' => 'USD'
                ),
                'featureList' => array(
                    'Real-time NASDAQ stock data',
                    'Advanced stock screening',
                    'Portfolio tracking',
                    'Market news analysis',
                    'Stock alerts and notifications',
                    'Technical analysis tools'
                )
            )
        );
    } elseif (is_page() && $post) {
        $structured_data['webpage'] = array(
            '@context' => 'https://schema.org',
            '@type' => 'WebPage',
            'name' => get_the_title(),
            'description' => wp_trim_words(get_the_content(), 25),
            'url' => get_permalink(),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'author' => array(
                '@type' => 'Organization',
                'name' => get_bloginfo('name')
            )
        );
    }
    
    // Output structured data
    foreach ($structured_data as $key => $data) {
        echo '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
    }
}

/**
 * Add breadcrumbs for better navigation and SEO
 */
function stock_scanner_breadcrumbs() {
    if (is_front_page()) return;
    
    echo '<nav class="breadcrumbs" aria-label="Breadcrumb navigation">';
    echo '<ol class="breadcrumb-list" itemscope itemtype="https://schema.org/BreadcrumbList">';
    
    // Home link
    echo '<li class="breadcrumb-item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
    echo '<a href="' . home_url('/') . '" itemprop="item"><span itemprop="name">Home</span></a>';
    echo '<meta itemprop="position" content="1" />';
    echo '</li>';
    
    $position = 2;
    
    if (is_page()) {
        global $post;
        if ($post->post_parent) {
            $parent_id = $post->post_parent;
            $breadcrumbs = array();
            
            while ($parent_id) {
                $page = get_page($parent_id);
                $breadcrumbs[] = array(
                    'title' => get_the_title($page->ID),
                    'url' => get_permalink($page->ID)
                );
                $parent_id = $page->post_parent;
            }
            
            $breadcrumbs = array_reverse($breadcrumbs);
            
            foreach ($breadcrumbs as $crumb) {
                echo '<li class="breadcrumb-item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
                echo '<a href="' . $crumb['url'] . '" itemprop="item"><span itemprop="name">' . $crumb['title'] . '</span></a>';
                echo '<meta itemprop="position" content="' . $position . '" />';
                echo '</li>';
                $position++;
            }
        }
        
        echo '<li class="breadcrumb-item active" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';
        echo '<span itemprop="name">' . get_the_title() . '</span>';
        echo '<meta itemprop="position" content="' . $position . '" />';
        echo '</li>';
    }
    
    echo '</ol>';
    echo '</nav>';
}

/**
 * Optimize images for performance and SEO
 */
function stock_scanner_optimize_images($attr, $attachment, $size) {
    $attr['loading'] = 'lazy';
    $attr['decoding'] = 'async';
    
    // Add structured data to images
    if (!empty($attachment->post_excerpt)) {
        $attr['alt'] = $attachment->post_excerpt;
    } elseif (!empty($attachment->post_title)) {
        $attr['alt'] = $attachment->post_title;
    }
    
    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'stock_scanner_optimize_images', 10, 3);

/**
 * Add preload hints for critical resources
 */
function stock_scanner_preload_resources() {
    // Preload critical CSS
    echo '<link rel="preload" href="' . get_stylesheet_uri() . '" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . "\n";
    
    // Preload critical fonts
    echo '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . "\n";
    
    // DNS prefetch for external resources
    echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">' . "\n";
    echo '<link rel="dns-prefetch" href="//cdnjs.cloudflare.com">' . "\n";
    
    // Preconnect to critical third-party origins
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
}
add_action('wp_head', 'stock_scanner_preload_resources', 1);

/**
 * Enqueue scripts and styles with optimization
 */
function stock_scanner_scripts() {
    // Enqueue theme stylesheet with version for cache busting
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '2.0.0');
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js', array(), '3.9.1', true);
    
    // Enqueue theme JavaScript with optimization
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '2.0.0', true);
    
    // Localize script for AJAX with additional data for AI optimization
    wp_localize_script('stock-scanner-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce'),
        'site_url' => home_url('/'),
        'theme_url' => get_template_directory_uri(),
        'is_user_logged_in' => is_user_logged_in(),
        'current_page' => get_queried_object_id(),
        'search_placeholder' => __('Search stocks, companies, or tickers...', 'stock-scanner')
    ));
    
    // Add critical CSS inline for above-the-fold content
    $critical_css = '
        .site-header{background:var(--white);backdrop-filter:blur(20px);border-bottom:1px solid var(--medium-gray);padding:var(--spacing-lg) 0;position:sticky;top:0;z-index:1000;box-shadow:var(--shadow-sm)}
        .container{max-width:1400px;margin:0 auto;padding:0 var(--spacing-xl)}
        .loading{display:inline-block;width:20px;height:20px;border:3px solid #f3f3f3;border-top:3px solid #3498db;border-radius:50%;animation:spin 2s linear infinite}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
    ';
    wp_add_inline_style('stock-scanner-style', $critical_css);
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Add schema markup to navigation menus
 */
function stock_scanner_nav_menu_args($args) {
    if ($args['theme_location'] === 'primary') {
        $args['container_class'] = 'main-navigation';
        $args['menu_class'] = 'main-menu';
        $args['fallback_cb'] = 'stock_scanner_fallback_menu';
        
        // Add schema markup
        $args['items_wrap'] = '<ul id="%1$s" class="%2$s" itemscope itemtype="https://schema.org/SiteNavigationElement">%3$s</ul>';
    }
    return $args;
}
add_filter('wp_nav_menu_args', 'stock_scanner_nav_menu_args');

/**
 * Add schema markup to menu items
 */
function stock_scanner_nav_menu_link_attributes($atts, $item, $args) {
    if ($args->theme_location === 'primary') {
        $atts['itemprop'] = 'url';
    }
    return $atts;
}
add_filter('nav_menu_link_attributes', 'stock_scanner_nav_menu_link_attributes', 10, 3);

/**
 * Fallback menu for when no menu is assigned
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="main-menu" itemscope itemtype="https://schema.org/SiteNavigationElement">';
    echo '<li><a href="' . home_url('/premium-plans/') . '" itemprop="url"><span itemprop="name">Premium Plans</span></a></li>';
    echo '<li><a href="' . home_url('/email-stock-lists/') . '" itemprop="url"><span itemprop="name">Email Lists</span></a></li>';
    echo '<li><a href="' . home_url('/stock-search/') . '" itemprop="url"><span itemprop="name">Stock Search</span></a></li>';
    echo '<li><a href="' . home_url('/popular-stock-lists/') . '" itemprop="url"><span itemprop="name">Popular Lists</span></a></li>';
    echo '<li><a href="' . home_url('/news-scrapper/') . '" itemprop="url"><span itemprop="name">News Scraper</span></a></li>';
    echo '<li><a href="' . home_url('/membership-account/') . '" itemprop="url"><span itemprop="name">My Account</span></a></li>';
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
    
    // Add page-specific classes for better targeting
    if (is_page()) {
        $classes[] = 'page-' . sanitize_html_class(get_post_field('post_name'));
    }
    
    // Add device-specific classes
    if (wp_is_mobile()) {
        $classes[] = 'mobile-device';
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Optimize page titles for SEO
 */
function stock_scanner_document_title_parts($title) {
    if (is_front_page()) {
        $title['title'] = 'Stock Market Scanner & Analysis Platform';
        $title['tagline'] = 'Real-time NASDAQ Data & AI-Powered Insights';
    } elseif (is_page()) {
        $title['site'] = get_bloginfo('name');
        
        // Add context for stock-related pages
        if (strpos(get_the_title(), 'Stock') !== false) {
            $title['tagline'] = 'Professional Stock Analysis Tools';
        } elseif (strpos(get_the_title(), 'Market') !== false) {
            $title['tagline'] = 'Real-time Market Data & News';
        }
    }
    
    return $title;
}
add_filter('document_title_parts', 'stock_scanner_document_title_parts');

/**
 * Add hreflang tags for international SEO (if applicable)
 */
function stock_scanner_hreflang_tags() {
    if (is_front_page()) {
        echo '<link rel="alternate" hreflang="en" href="' . home_url('/') . '">' . "\n";
        echo '<link rel="alternate" hreflang="x-default" href="' . home_url('/') . '">' . "\n";
    }
}
add_action('wp_head', 'stock_scanner_hreflang_tags');

/**
 * Add content security policy for better security and performance
 */
function stock_scanner_security_headers() {
    if (!is_admin()) {
        header("X-Content-Type-Options: nosniff");
        header("X-Frame-Options: SAMEORIGIN");
        header("X-XSS-Protection: 1; mode=block");
        header("Referrer-Policy: strict-origin-when-cross-origin");
    }
}
add_action('send_headers', 'stock_scanner_security_headers');

/**
 * Optimize database queries for better performance
 */
function stock_scanner_optimize_queries() {
    // Remove unnecessary queries
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    
    // Remove emoji scripts for better performance
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
}
add_action('init', 'stock_scanner_optimize_queries');

/**
 * Add sitemap generation for better SEO
 */
function stock_scanner_add_sitemap() {
    add_rewrite_rule('^sitemap\.xml$', 'index.php?stock_scanner_sitemap=1', 'top');
}
add_action('init', 'stock_scanner_add_sitemap');

function stock_scanner_sitemap_template() {
    if (get_query_var('stock_scanner_sitemap')) {
        header('Content-Type: application/xml; charset=utf-8');
        
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        
        // Homepage
        echo '<url>' . "\n";
        echo '<loc>' . home_url('/') . '</loc>' . "\n";
        echo '<lastmod>' . date('Y-m-d\TH:i:s+00:00') . '</lastmod>' . "\n";
        echo '<changefreq>daily</changefreq>' . "\n";
        echo '<priority>1.0</priority>' . "\n";
        echo '</url>' . "\n";
        
        // Pages
        $pages = get_pages();
        foreach ($pages as $page) {
            echo '<url>' . "\n";
            echo '<loc>' . get_permalink($page->ID) . '</loc>' . "\n";
            echo '<lastmod>' . date('Y-m-d\TH:i:s+00:00', strtotime($page->post_modified)) . '</lastmod>' . "\n";
            echo '<changefreq>weekly</changefreq>' . "\n";
            echo '<priority>0.8</priority>' . "\n";
            echo '</url>' . "\n";
        }
        
        echo '</urlset>';
        exit;
    }
}
add_action('template_redirect', 'stock_scanner_sitemap_template');

function stock_scanner_sitemap_query_vars($vars) {
    $vars[] = 'stock_scanner_sitemap';
    return $vars;
}
add_filter('query_vars', 'stock_scanner_sitemap_query_vars');

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
?>