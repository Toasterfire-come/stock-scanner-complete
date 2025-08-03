<?php
/**
 * Stock Scanner Theme Functions
 * Integrates with Django API for stock data and news
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Enqueue scripts and styles
 */
function stock_scanner_enqueue_scripts() {
    // Enqueue jQuery (if not already loaded)
    wp_enqueue_script('jquery');
    
    // Enqueue custom JavaScript
    wp_enqueue_script(
        'stock-scanner-js',
        get_template_directory_uri() . '/js/stock-scanner.js',
        array('jquery'),
        '1.0.0',
        true
    );
    
    // Enqueue custom CSS
    wp_enqueue_style(
        'stock-scanner-css',
        get_template_directory_uri() . '/css/stock-scanner.css',
        array(),
        '1.0.0'
    );
    
    // Localize script with API URL
    wp_localize_script('stock-scanner-js', 'stockScannerAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'api_url' => 'http://127.0.0.1:8000/api', // Change to your Django server URL
        'nonce' => wp_create_nonce('stock_scanner_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');

/**
 * Add theme support
 */
function stock_scanner_theme_setup() {
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
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/**
 * Register widget areas
 */
function stock_scanner_widgets_init() {
    register_sidebar(array(
        'name'          => __('Stock Scanner Sidebar', 'stock-scanner'),
        'id'            => 'sidebar-1',
        'description'   => __('Add widgets here.', 'stock-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ));
}
add_action('widgets_init', 'stock_scanner_widgets_init');

/**
 * AJAX handler for stock data
 */
function stock_scanner_get_stocks() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $api_url = 'http://127.0.0.1:8000/api/wordpress/stocks/';
    $limit = isset($_POST['limit']) ? intval($_POST['limit']) : 10;
    $category = isset($_POST['category']) ? sanitize_text_field($_POST['category']) : '';
    
    $url = add_query_arg(array(
        'limit' => $limit,
        'category' => $category
    ), $api_url);
    
    $response = wp_remote_get($url);
    
    if (is_wp_error($response)) {
        wp_send_json_error('Failed to fetch stock data');
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    wp_send_json_success($data);
}
add_action('wp_ajax_get_stocks', 'stock_scanner_get_stocks');
add_action('wp_ajax_nopriv_get_stocks', 'stock_scanner_get_stocks');

/**
 * AJAX handler for news data
 */
function stock_scanner_get_news() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $api_url = 'http://127.0.0.1:8000/api/wordpress/news/';
    $limit = isset($_POST['limit']) ? intval($_POST['limit']) : 5;
    
    $url = add_query_arg(array(
        'limit' => $limit
    ), $api_url);
    
    $response = wp_remote_get($url);
    
    if (is_wp_error($response)) {
        wp_send_json_error('Failed to fetch news data');
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    wp_send_json_success($data);
}
add_action('wp_ajax_get_news', 'stock_scanner_get_news');
add_action('wp_ajax_nopriv_get_news', 'stock_scanner_get_news');

/**
 * Shortcode for stock ticker
 */
function stock_scanner_ticker_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => 10,
        'category' => '',
        'show_changes' => 'true'
    ), $atts);
    
    ob_start();
    ?>
    <div class="stock-ticker" 
         data-limit="<?php echo esc_attr($atts['limit']); ?>"
         data-category="<?php echo esc_attr($atts['category']); ?>"
         data-show-changes="<?php echo esc_attr($atts['show_changes']); ?>">
        <div class="ticker-loading">Loading stock data...</div>
        <div class="ticker-content" style="display: none;"></div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_ticker', 'stock_scanner_ticker_shortcode');

/**
 * Shortcode for news feed
 */
function stock_scanner_news_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => 5,
        'show_sentiment' => 'true'
    ), $atts);
    
    ob_start();
    ?>
    <div class="stock-news" 
         data-limit="<?php echo esc_attr($atts['limit']); ?>"
         data-show-sentiment="<?php echo esc_attr($atts['show_sentiment']); ?>">
        <div class="news-loading">Loading news...</div>
        <div class="news-content" style="display: none;"></div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_news', 'stock_scanner_news_shortcode');

/**
 * Add custom post types for stock data
 */
function stock_scanner_post_types() {
    // Stock Alert post type
    register_post_type('stock_alert', array(
        'labels' => array(
            'name' => 'Stock Alerts',
            'singular_name' => 'Stock Alert',
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'custom-fields'),
        'menu_icon' => 'dashicons-chart-line',
    ));
}
add_action('init', 'stock_scanner_post_types');

/**
 * Add custom meta boxes
 */
function stock_scanner_meta_boxes() {
    add_meta_box(
        'stock_data',
        'Stock Data',
        'stock_scanner_meta_box_callback',
        'stock_alert',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'stock_scanner_meta_boxes');

function stock_scanner_meta_box_callback($post) {
    wp_nonce_field('stock_scanner_meta_box', 'stock_scanner_meta_box_nonce');
    
    $ticker = get_post_meta($post->ID, '_stock_ticker', true);
    $price = get_post_meta($post->ID, '_stock_price', true);
    $change = get_post_meta($post->ID, '_stock_change', true);
    
    ?>
    <table class="form-table">
        <tr>
            <th><label for="stock_ticker">Ticker Symbol</label></th>
            <td><input type="text" id="stock_ticker" name="stock_ticker" value="<?php echo esc_attr($ticker); ?>" /></td>
        </tr>
        <tr>
            <th><label for="stock_price">Current Price</label></th>
            <td><input type="number" step="0.01" id="stock_price" name="stock_price" value="<?php echo esc_attr($price); ?>" /></td>
        </tr>
        <tr>
            <th><label for="stock_change">Price Change</label></th>
            <td><input type="number" step="0.01" id="stock_change" name="stock_change" value="<?php echo esc_attr($change); ?>" /></td>
        </tr>
    </table>
    <?php
}

/**
 * Save meta box data
 */
function stock_scanner_save_meta_box_data($post_id) {
    if (!isset($_POST['stock_scanner_meta_box_nonce'])) {
        return;
    }
    
    if (!wp_verify_nonce($_POST['stock_scanner_meta_box_nonce'], 'stock_scanner_meta_box')) {
        return;
    }
    
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }
    
    if (!current_user_can('edit_post', $post_id)) {
        return;
    }
    
    if (isset($_POST['stock_ticker'])) {
        update_post_meta($post_id, '_stock_ticker', sanitize_text_field($_POST['stock_ticker']));
    }
    
    if (isset($_POST['stock_price'])) {
        update_post_meta($post_id, '_stock_price', floatval($_POST['stock_price']));
    }
    
    if (isset($_POST['stock_change'])) {
        update_post_meta($post_id, '_stock_change', floatval($_POST['stock_change']));
    }
}
add_action('save_post', 'stock_scanner_save_meta_box_data');