<?php
/**
 * Retail Trade Scan Net Theme Functions
 * 
 * Stock analysis and trading insights theme with seamless Django backend integration.
 * Features real-time stock data, SEO optimization, and mobile-first design.
 * 
 * @package RetailTradeScanNet
 * @version 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme Setup
 */
function retail_trade_scan_setup() {
    // Add default posts and comments RSS feed links to head
    add_theme_support('automatic-feed-links');
    
    // Let WordPress manage the document title
    add_theme_support('title-tag');
    
    // Enable support for Post Thumbnails on posts and pages
    add_theme_support('post-thumbnails');
    
    // Add support for responsive embedded content
    add_theme_support('responsive-embeds');
    
    // Add support for editor styles
    add_theme_support('editor-styles');
    
    // Add support for wide alignment
    add_theme_support('align-wide');
    
    // Register navigation menus
    register_nav_menus([
        'primary' => __('Primary Menu', 'retail-trade-scan'),
        'footer' => __('Footer Menu', 'retail-trade-scan'),
        'stock-menu' => __('Stock Menu', 'retail-trade-scan'),
    ]);
    
    // Add image sizes for stock-related content
    add_image_size('stock-thumbnail', 300, 200, true);
    add_image_size('stock-featured', 800, 400, true);
    add_image_size('stock-banner', 1200, 400, true);
}
add_action('after_setup_theme', 'retail_trade_scan_setup');

/**
 * Enqueue Scripts and Styles
 */
function retail_trade_scan_scripts() {
    // Theme stylesheet
    wp_enqueue_style(
        'retail-trade-scan-style',
        get_stylesheet_uri(),
        [],
        wp_get_theme()->get('Version')
    );
    
    // Stock integration JavaScript
    wp_enqueue_script(
        'retail-trade-scan-stock-js',
        get_template_directory_uri() . '/assets/js/stock-integration.js',
        ['jquery'],
        wp_get_theme()->get('Version'),
        true
    );
    
    // Mobile navigation JavaScript
    wp_enqueue_script(
        'retail-trade-scan-navigation',
        get_template_directory_uri() . '/assets/js/navigation.js',
        [],
        wp_get_theme()->get('Version'),
        true
    );
    
    // Localize script for AJAX calls
    wp_localize_script('retail-trade-scan-stock-js', 'stockAjax', [
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_nonce'),
        'django_api_url' => defined('DJANGO_API_URL') ? DJANGO_API_URL : '',
    ]);
    
    // Conditional loading for performance
    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'retail_trade_scan_scripts');

/**
 * Widget Areas
 */
function retail_trade_scan_widgets_init() {
    // Main sidebar
    register_sidebar([
        'name'          => __('Main Sidebar', 'retail-trade-scan'),
        'id'            => 'sidebar-1',
        'description'   => __('Add widgets here.', 'retail-trade-scan'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ]);
    
    // Stock data sidebar
    register_sidebar([
        'name'          => __('Stock Data Sidebar', 'retail-trade-scan'),
        'id'            => 'stock-sidebar',
        'description'   => __('Stock-related widgets for financial content.', 'retail-trade-scan'),
        'before_widget' => '<section id="%1$s" class="widget stock-widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h4 class="widget-title">',
        'after_title'   => '</h4>',
    ]);
    
    // Footer widgets
    for ($i = 1; $i <= 3; $i++) {
        register_sidebar([
            'name'          => sprintf(__('Footer %d', 'retail-trade-scan'), $i),
            'id'            => "footer-{$i}",
            'description'   => sprintf(__('Footer widget area %d', 'retail-trade-scan'), $i),
            'before_widget' => '<section id="%1$s" class="widget %2$s">',
            'after_widget'  => '</section>',
            'before_title'  => '<h3 class="widget-title">',
            'after_title'   => '</h3>',
        ]);
    }
}
add_action('widgets_init', 'retail_trade_scan_widgets_init');

/**
 * SEO Enhancements
 */
function retail_trade_scan_seo_meta() {
    global $post;
    
    if (is_singular()) {
        // Meta description
        $meta_description = '';
        if (has_excerpt()) {
            $meta_description = get_the_excerpt();
        } elseif ($post) {
            $meta_description = wp_trim_words(strip_tags($post->post_content), 25);
        }
        
        if ($meta_description) {
            echo '<meta name="description" content="' . esc_attr($meta_description) . '">' . "\n";
        }
        
        // Meta keywords from categories and tags
        $keywords = [];
        $categories = get_the_category();
        foreach ($categories as $category) {
            $keywords[] = $category->name;
        }
        
        $tags = get_the_tags();
        if ($tags) {
            foreach ($tags as $tag) {
                $keywords[] = $tag->name;
            }
        }
        
        // Add stock-related keywords
        $stock_tickers = get_post_meta(get_the_ID(), 'stock_tickers', true);
        if ($stock_tickers) {
            $tickers = explode(',', $stock_tickers);
            foreach ($tickers as $ticker) {
                $keywords[] = trim($ticker);
                $keywords[] = trim($ticker) . ' stock';
            }
        }
        
        if (!empty($keywords)) {
            echo '<meta name="keywords" content="' . esc_attr(implode(', ', array_unique($keywords))) . '">' . "\n";
        }
        
        // Canonical URL
        echo '<link rel="canonical" href="' . esc_url(get_permalink()) . '">' . "\n";
        
        // Open Graph tags
        echo '<meta property="og:type" content="article">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_the_title()) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($meta_description) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url(get_permalink()) . '">' . "\n";
        echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        
        if (has_post_thumbnail()) {
            $thumbnail_url = get_the_post_thumbnail_url(get_the_ID(), 'large');
            echo '<meta property="og:image" content="' . esc_url($thumbnail_url) . '">' . "\n";
        }
        
        // Twitter Card tags
        echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
        echo '<meta name="twitter:title" content="' . esc_attr(get_the_title()) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr($meta_description) . '">' . "\n";
        
        if (has_post_thumbnail()) {
            $thumbnail_url = get_the_post_thumbnail_url(get_the_ID(), 'large');
            echo '<meta name="twitter:image" content="' . esc_url($thumbnail_url) . '">' . "\n";
        }
    }
}
add_action('wp_head', 'retail_trade_scan_seo_meta');

/**
 * Structured Data (JSON-LD)
 */
function retail_trade_scan_structured_data() {
    if (is_singular(['post', 'page'])) {
        global $post;
        
        $structured_data = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'description' => has_excerpt() ? get_the_excerpt() : wp_trim_words(strip_tags($post->post_content), 25),
            'url' => get_permalink(),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'author' => [
                '@type' => 'Person',
                'name' => get_the_author(),
            ],
            'publisher' => [
                '@type' => 'Organization',
                'name' => get_bloginfo('name'),
                'url' => home_url(),
            ],
        ];
        
        // Add stock-specific data
        $stock_tickers = get_post_meta(get_the_ID(), 'stock_tickers', true);
        if ($stock_tickers) {
            $tickers = array_map('trim', explode(',', $stock_tickers));
            $structured_data['about'] = [];
            
            foreach ($tickers as $ticker) {
                $structured_data['about'][] = [
                    '@type' => 'Corporation',
                    'name' => $ticker,
                    'tickerSymbol' => $ticker,
                ];
            }
        }
        
        echo '<script type="application/ld+json">' . json_encode($structured_data, JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
    }
}
add_action('wp_head', 'retail_trade_scan_structured_data');

/**
 * Custom Post Meta Boxes
 */
function retail_trade_scan_add_meta_boxes() {
    add_meta_box(
        'stock-data',
        __('Stock Data', 'retail-trade-scan'),
        'retail_trade_scan_stock_meta_box',
        'post',
        'normal',
        'high'
    );
    
    add_meta_box(
        'seo-data',
        __('SEO Settings', 'retail-trade-scan'),
        'retail_trade_scan_seo_meta_box',
        ['post', 'page'],
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'retail_trade_scan_add_meta_boxes');

/**
 * Stock Data Meta Box
 */
function retail_trade_scan_stock_meta_box($post) {
    wp_nonce_field('retail_trade_scan_meta_nonce', 'retail_trade_scan_meta_nonce');
    
    $stock_tickers = get_post_meta($post->ID, 'stock_tickers', true);
    $price_target = get_post_meta($post->ID, 'price_target', true);
    $risk_level = get_post_meta($post->ID, 'risk_level', true);
    $sector = get_post_meta($post->ID, 'sector', true);
    
    ?>
    <table class="form-table">
        <tr>
            <th><label for="stock_tickers"><?php _e('Stock Tickers', 'retail-trade-scan'); ?></label></th>
            <td>
                <input type="text" id="stock_tickers" name="stock_tickers" value="<?php echo esc_attr($stock_tickers); ?>" class="regular-text" />
                <p class="description"><?php _e('Comma-separated list of stock tickers (e.g., AAPL, MSFT, GOOGL)', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="price_target"><?php _e('Price Target', 'retail-trade-scan'); ?></label></th>
            <td>
                <input type="number" id="price_target" name="price_target" value="<?php echo esc_attr($price_target); ?>" step="0.01" />
                <p class="description"><?php _e('Analyst price target in USD', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="risk_level"><?php _e('Risk Level', 'retail-trade-scan'); ?></label></th>
            <td>
                <select id="risk_level" name="risk_level">
                    <option value=""><?php _e('Select Risk Level', 'retail-trade-scan'); ?></option>
                    <option value="low" <?php selected($risk_level, 'low'); ?>><?php _e('Low', 'retail-trade-scan'); ?></option>
                    <option value="medium" <?php selected($risk_level, 'medium'); ?>><?php _e('Medium', 'retail-trade-scan'); ?></option>
                    <option value="high" <?php selected($risk_level, 'high'); ?>><?php _e('High', 'retail-trade-scan'); ?></option>
                </select>
            </td>
        </tr>
        <tr>
            <th><label for="sector"><?php _e('Market Sector', 'retail-trade-scan'); ?></label></th>
            <td>
                <input type="text" id="sector" name="sector" value="<?php echo esc_attr($sector); ?>" class="regular-text" />
                <p class="description"><?php _e('Market sector (e.g., Technology, Healthcare, Finance)', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
    </table>
    <?php
}

/**
 * SEO Meta Box
 */
function retail_trade_scan_seo_meta_box($post) {
    $meta_description = get_post_meta($post->ID, 'meta_description', true);
    $meta_keywords = get_post_meta($post->ID, 'meta_keywords', true);
    $canonical_url = get_post_meta($post->ID, 'canonical_url', true);
    
    ?>
    <table class="form-table">
        <tr>
            <th><label for="meta_description"><?php _e('Meta Description', 'retail-trade-scan'); ?></label></th>
            <td>
                <textarea id="meta_description" name="meta_description" rows="3" class="large-text"><?php echo esc_textarea($meta_description); ?></textarea>
                <p class="description"><?php _e('SEO meta description (150-160 characters recommended)', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="meta_keywords"><?php _e('Meta Keywords', 'retail-trade-scan'); ?></label></th>
            <td>
                <input type="text" id="meta_keywords" name="meta_keywords" value="<?php echo esc_attr($meta_keywords); ?>" class="large-text" />
                <p class="description"><?php _e('Comma-separated keywords for SEO', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="canonical_url"><?php _e('Canonical URL', 'retail-trade-scan'); ?></label></th>
            <td>
                <input type="url" id="canonical_url" name="canonical_url" value="<?php echo esc_url($canonical_url); ?>" class="large-text" />
                <p class="description"><?php _e('Override default canonical URL if needed', 'retail-trade-scan'); ?></p>
            </td>
        </tr>
    </table>
    <?php
}

/**
 * Save Meta Box Data
 */
function retail_trade_scan_save_meta_boxes($post_id) {
    // Check nonce
    if (!isset($_POST['retail_trade_scan_meta_nonce']) || !wp_verify_nonce($_POST['retail_trade_scan_meta_nonce'], 'retail_trade_scan_meta_nonce')) {
        return;
    }
    
    // Check permissions
    if (!current_user_can('edit_post', $post_id)) {
        return;
    }
    
    // Save stock data
    $stock_fields = ['stock_tickers', 'price_target', 'risk_level', 'sector'];
    foreach ($stock_fields as $field) {
        if (isset($_POST[$field])) {
            update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
        }
    }
    
    // Save SEO data
    $seo_fields = ['meta_description', 'meta_keywords', 'canonical_url'];
    foreach ($seo_fields as $field) {
        if (isset($_POST[$field])) {
            if ($field === 'canonical_url') {
                update_post_meta($post_id, $field, esc_url_raw($_POST[$field]));
            } else {
                update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
            }
        }
    }
}
add_action('save_post', 'retail_trade_scan_save_meta_boxes');

/**
 * Stock Data Shortcodes
 */

// [stock_price ticker="AAPL"]
function retail_trade_scan_stock_price_shortcode($atts) {
    $atts = shortcode_atts([
        'ticker' => '',
        'format' => 'basic',
    ], $atts);
    
    if (empty($atts['ticker'])) {
        return '';
    }
    
    // Get stock data from Django API
    $stock_data = retail_trade_scan_get_stock_data($atts['ticker']);
    
    if (!$stock_data) {
        return '<span class="stock-ticker error">Error loading ' . esc_html($atts['ticker']) . '</span>';
    }
    
    $change_class = $stock_data['change'] >= 0 ? 'positive' : 'negative';
    
    return sprintf(
        '<span class="stock-ticker %s" data-ticker="%s">%s: $%s</span>',
        $change_class,
        esc_attr($atts['ticker']),
        esc_html($atts['ticker']),
        esc_html(number_format($stock_data['price'], 2))
    );
}
add_shortcode('stock_price', 'retail_trade_scan_stock_price_shortcode');

// [market_movers count="5"]
function retail_trade_scan_market_movers_shortcode($atts) {
    $atts = shortcode_atts([
        'count' => 5,
        'type' => 'gainers',
    ], $atts);
    
    // Get market movers from Django API
    $movers = retail_trade_scan_get_market_movers($atts['type'], $atts['count']);
    
    if (empty($movers)) {
        return '<p>Market data temporarily unavailable.</p>';
    }
    
    $output = '<div class="market-movers">';
    $output .= '<h4>' . esc_html(ucfirst($atts['type'])) . '</h4>';
    $output .= '<ul>';
    
    foreach ($movers as $stock) {
        $change_class = $stock['change'] >= 0 ? 'positive' : 'negative';
        $output .= sprintf(
            '<li><span class="stock-ticker %s">%s</span> $%s (%s%%)</li>',
            $change_class,
            esc_html($stock['ticker']),
            esc_html(number_format($stock['price'], 2)),
            esc_html(number_format($stock['change_percent'], 2))
        );
    }
    
    $output .= '</ul></div>';
    
    return $output;
}
add_shortcode('market_movers', 'retail_trade_scan_market_movers_shortcode');

/**
 * Helper Functions
 */

// Get stock data from Django API
function retail_trade_scan_get_stock_data($ticker) {
    if (!defined('DJANGO_API_URL')) {
        return false;
    }
    
    $cache_key = 'stock_data_' . $ticker;
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $api_url = DJANGO_API_URL . 'api/stocks/' . urlencode($ticker) . '/';
    $response = wp_remote_get($api_url, [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ],
    ]);
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (!$data || !$data['success'] || !isset($data['data'])) {
        return false;
    }
    
    $stock_info = $data['data'];
    $stock_data = [
        'ticker' => $stock_info['ticker'],
        'company_name' => $stock_info['company_name'],
        'price' => floatval($stock_info['current_price']),
        'change' => floatval($stock_info['price_change_today']),
        'change_percent' => floatval($stock_info['price_change_percent']),
        'volume' => intval($stock_info['volume_today']),
        'technical_rating' => $stock_info['technical_rating'],
        'last_update' => $stock_info['last_update'],
    ];
    
    // Cache for 2 minutes for real-time feel
    set_transient($cache_key, $stock_data, 2 * MINUTE_IN_SECONDS);
    
    return $stock_data;
}

// Get market movers
function retail_trade_scan_get_market_movers($type = 'gainers', $count = 5) {
    $cache_key = "market_movers_{$type}_{$count}";
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    if (!defined('DJANGO_API_URL')) {
        return [];
    }
    
    $api_url = DJANGO_API_URL . 'api/market-movers/?type=' . urlencode($type) . '&limit=' . intval($count);
    $response = wp_remote_get($api_url, [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ],
    ]);
    
    if (is_wp_error($response)) {
        return [];
    }
    
    $body = wp_remote_retrieve_body($response);
    $response_data = json_decode($body, true);
    
    if (!$response_data || !$response_data['success'] || !is_array($response_data['data'])) {
        return [];
    }
    
    // Cache for 1 minute
    set_transient($cache_key, $response_data['data'], MINUTE_IN_SECONDS);
    
    return $response_data['data'];
}

/**
 * Performance Optimizations
 */

// Optimize queries
function retail_trade_scan_optimize_queries() {
    // Remove query strings from static resources
    if (!is_admin()) {
        add_filter('script_loader_src', 'retail_trade_scan_remove_query_strings', 15, 1);
        add_filter('style_loader_src', 'retail_trade_scan_remove_query_strings', 15, 1);
    }
}
add_action('init', 'retail_trade_scan_optimize_queries');

function retail_trade_scan_remove_query_strings($src) {
    $output = preg_split("/(&ver|\?ver)/", $src);
    return $output[0];
}

// Preload critical resources
function retail_trade_scan_preload_resources() {
    echo '<link rel="preload" href="' . get_template_directory_uri() . '/assets/css/critical.css" as="style">' . "\n";
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">' . "\n";
    echo '<link rel="dns-prefetch" href="//cdnjs.cloudflare.com">' . "\n";
    
    if (defined('DJANGO_API_URL')) {
        $domain = parse_url(DJANGO_API_URL, PHP_URL_HOST);
        echo '<link rel="preconnect" href="https://' . esc_attr($domain) . '">' . "\n";
    }
}
add_action('wp_head', 'retail_trade_scan_preload_resources', 1);

/**
 * Security Enhancements
 */

// Remove WordPress version
remove_action('wp_head', 'wp_generator');

// Remove RSD link
remove_action('wp_head', 'rsd_link');

// Remove wlwmanifest.xml
remove_action('wp_head', 'wlwmanifest_link');

// Disable XML-RPC
add_filter('xmlrpc_enabled', '__return_false');

/**
 * Theme Customizer
 */
function retail_trade_scan_customize_register($wp_customize) {
    // Stock Settings Section
    $wp_customize->add_section('stock_settings', [
        'title' => __('Stock Settings', 'retail-trade-scan'),
        'priority' => 30,
    ]);
    
    // Django API URL
    $wp_customize->add_setting('django_api_url', [
        'default' => '',
        'sanitize_callback' => 'esc_url_raw',
    ]);
    
    $wp_customize->add_control('django_api_url', [
        'label' => __('Django API URL', 'retail-trade-scan'),
        'section' => 'stock_settings',
        'type' => 'url',
    ]);
    
    // Stock ticker display
    $wp_customize->add_setting('show_stock_tickers', [
        'default' => true,
        'sanitize_callback' => 'retail_trade_scan_sanitize_checkbox',
    ]);
    
    $wp_customize->add_control('show_stock_tickers', [
        'label' => __('Show Stock Tickers in Posts', 'retail-trade-scan'),
        'section' => 'stock_settings',
        'type' => 'checkbox',
    ]);
}
add_action('customize_register', 'retail_trade_scan_customize_register');

function retail_trade_scan_sanitize_checkbox($checked) {
    return ((isset($checked) && true == $checked) ? true : false);
}

/**
 * AJAX Handlers
 */

// Get stock data via AJAX
function retail_trade_scan_ajax_get_stock_data() {
    check_ajax_referer('stock_nonce', 'nonce');
    
    $ticker = sanitize_text_field($_POST['ticker'] ?? '');
    if (empty($ticker)) {
        wp_die('Invalid ticker');
    }
    
    $stock_data = retail_trade_scan_get_stock_data($ticker);
    
    if ($stock_data) {
        wp_send_json_success($stock_data);
    } else {
        wp_send_json_error('Stock data not available');
    }
}
add_action('wp_ajax_get_stock_data', 'retail_trade_scan_ajax_get_stock_data');
add_action('wp_ajax_nopriv_get_stock_data', 'retail_trade_scan_ajax_get_stock_data');

/**
 * Content Filters
 */

// Automatically add stock tickers to content
function retail_trade_scan_auto_add_stock_tickers($content) {
    if (!is_singular('post') || !in_the_loop() || !is_main_query()) {
        return $content;
    }
    
    $stock_tickers = get_post_meta(get_the_ID(), 'stock_tickers', true);
    if (empty($stock_tickers)) {
        return $content;
    }
    
    $tickers = array_map('trim', explode(',', $stock_tickers));
    $ticker_html = '<div class="post-stock-tickers" style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #2563eb;">';
    $ticker_html .= '<strong style="color: #1f2937;">' . __('📈 Related Stocks:', 'retail-trade-scan') . '</strong><br>';
    
    foreach ($tickers as $ticker) {
        $ticker_html .= do_shortcode('[stock_price ticker="' . esc_attr($ticker) . '"]') . ' ';
    }
    
    $ticker_html .= '</div>';
    
    return $content . $ticker_html;
}
add_filter('the_content', 'retail_trade_scan_auto_add_stock_tickers');

/**
 * Get market statistics from Django API
 */
function retail_trade_scan_get_market_stats() {
    if (!defined('DJANGO_API_URL')) {
        return false;
    }
    
    $cache_key = 'market_statistics';
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $api_url = DJANGO_API_URL . 'api/stats/';
    $response = wp_remote_get($api_url, [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ],
    ]);
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (!$data || !$data['success']) {
        return false;
    }
    
    // Cache for 3 minutes
    set_transient($cache_key, $data, 3 * MINUTE_IN_SECONDS);
    
    return $data;
}

/**
 * Subscribe email to Django backend
 */
function retail_trade_scan_subscribe_email($email, $category) {
    if (!defined('DJANGO_API_URL')) {
        return false;
    }
    
    $api_url = DJANGO_API_URL . 'api/wordpress/subscribe/';
    $post_data = json_encode([
        'email' => $email,
        'category' => $category
    ]);
    
    $response = wp_remote_post($api_url, [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ],
        'body' => $post_data,
    ]);
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    return $data && $data['success'];
}

/**
 * Search stocks from Django API
 */
function retail_trade_scan_search_stocks($query, $limit = 10) {
    if (!defined('DJANGO_API_URL') || empty($query)) {
        return [];
    }
    
    $cache_key = 'stock_search_' . md5($query . $limit);
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $api_url = DJANGO_API_URL . 'api/stocks/search/?q=' . urlencode($query) . '&limit=' . intval($limit);
    $response = wp_remote_get($api_url, [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ],
    ]);
    
    if (is_wp_error($response)) {
        return [];
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (!$data || !$data['success'] || !is_array($data['data'])) {
        return [];
    }
    
    // Cache for 30 seconds
    set_transient($cache_key, $data['data'], 30);
    
    return $data['data'];
}

/**
 * Handle subscription form submissions
 */
function retail_trade_scan_handle_subscription() {
    if (!isset($_POST['retail_trade_scan_subscribe_nonce']) || 
        !wp_verify_nonce($_POST['retail_trade_scan_subscribe_nonce'], 'retail_trade_scan_subscribe')) {
        return;
    }
    
    $email = sanitize_email($_POST['email'] ?? '');
    $category = sanitize_text_field($_POST['category'] ?? '');
    
    if (empty($email) || empty($category)) {
        wp_redirect(add_query_arg('subscription', 'error', wp_get_referer()));
        exit;
    }
    
    $success = retail_trade_scan_subscribe_email($email, $category);
    
    if ($success) {
        wp_redirect(add_query_arg('subscription', 'success', wp_get_referer()));
    } else {
        wp_redirect(add_query_arg('subscription', 'error', wp_get_referer()));
    }
    exit;
}
add_action('admin_post_retail_trade_scan_subscribe', 'retail_trade_scan_handle_subscription');
add_action('admin_post_nopriv_retail_trade_scan_subscribe', 'retail_trade_scan_handle_subscription');

/**
 * Display subscription messages
 */
function retail_trade_scan_subscription_messages() {
    if (isset($_GET['subscription'])) {
        if ($_GET['subscription'] === 'success') {
            echo '<div class="alert alert-success">✅ Successfully subscribed to stock alerts!</div>';
        } elseif ($_GET['subscription'] === 'error') {
            echo '<div class="alert alert-danger">❌ Subscription failed. Please try again.</div>';
        }
    }
}
add_action('wp_head', 'retail_trade_scan_subscription_messages');

/**
 * Enhanced stock price shortcode with Django integration
 */
function retail_trade_scan_enhanced_stock_price_shortcode($atts) {
    $atts = shortcode_atts([
        'ticker' => '',
        'format' => 'basic',
        'show_change' => 'true',
        'show_rating' => 'false',
    ], $atts);
    
    if (empty($atts['ticker'])) {
        return '';
    }
    
    // Get stock data from Django API
    $stock_data = retail_trade_scan_get_stock_data($atts['ticker']);
    
    if (!$stock_data) {
        return '<span class="stock-ticker error">❌ Error loading ' . esc_html($atts['ticker']) . '</span>';
    }
    
    $change_class = $stock_data['change'] >= 0 ? 'positive' : 'negative';
    $change_symbol = $stock_data['change'] >= 0 ? '▲' : '▼';
    
    $output = '<span class="stock-ticker ' . $change_class . '" data-ticker="' . esc_attr($atts['ticker']) . '">';
    $output .= '<strong>' . esc_html($atts['ticker']) . '</strong>: $' . number_format($stock_data['price'], 2);
    
    if ($atts['show_change'] === 'true' && isset($stock_data['change_percent'])) {
        $output .= ' <small>(' . $change_symbol . $stock_data['change_percent'] . '%)</small>';
    }
    
    if ($atts['show_rating'] === 'true' && isset($stock_data['technical_rating'])) {
        $rating_class = strtolower($stock_data['technical_rating']);
        $output .= ' <span class="rating-badge ' . $rating_class . '">' . $stock_data['technical_rating'] . '</span>';
    }
    
    $output .= '</span>';
    
    return $output;
}
// Override the original shortcode
remove_shortcode('stock_price');
add_shortcode('stock_price', 'retail_trade_scan_enhanced_stock_price_shortcode');

?>