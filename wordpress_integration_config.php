<?php
/**
 * WordPress Stock Scanner Integration Configuration
 * This file contains all the configuration and helper functions for integrating with Django API
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Django API Configuration
 */
class StockScannerAPI {
    
    private $api_url;
    private $api_key;
    private $timeout;
    
    public function __construct() {
        $this->api_url = defined('DJANGO_API_URL') ? DJANGO_API_URL : 'https://api.yourdomain.com';
        $this->api_key = defined('DJANGO_API_KEY') ? DJANGO_API_KEY : '';
        $this->timeout = 30;
    }
    
    /**
     * Make API request to Django backend
     */
    public function make_request($endpoint, $method = 'GET', $data = null) {
        $url = rtrim($this->api_url, '/') . '/api/' . ltrim($endpoint, '/');
        
        $args = array(
            'method' => $method,
            'timeout' => $this->timeout,
            'headers' => array(
                'Content-Type' => 'application/json',
                'User-Agent' => 'WordPress-StockScanner/1.0'
            )
        );
        
        // Add API key if available
        if (!empty($this->api_key)) {
            $args['headers']['Authorization'] = 'Bearer ' . $this->api_key;
        }
        
        // Add data for POST requests
        if ($method === 'POST' && !empty($data)) {
            $args['body'] = json_encode($data);
        }
        
        $response = wp_remote_request($url, $args);
        
        if (is_wp_error($response)) {
            error_log('StockScanner API Error: ' . $response->get_error_message());
            return false;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        
        if ($status_code !== 200) {
            error_log("StockScanner API Error: HTTP $status_code - $body");
            return false;
        }
        
        $decoded = json_decode($body, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log('StockScanner API Error: Invalid JSON response');
            return false;
        }
        
        return $decoded;
    }
    
    /**
     * Get stock data for WordPress display
     */
    public function get_stocks($limit = 50, $filters = array()) {
        $endpoint = 'wordpress/stocks/';
        if (!empty($filters)) {
            $endpoint .= '?' . http_build_query($filters);
        }
        
        return $this->make_request($endpoint);
    }
    
    /**
     * Get news data for WordPress display
     */
    public function get_news($limit = 20) {
        return $this->make_request("wordpress/news/?limit=$limit");
    }
    
    /**
     * Search stocks
     */
    public function search_stocks($query) {
        return $this->make_request("stocks/search/?q=" . urlencode($query));
    }
    
    /**
     * Get system status
     */
    public function get_system_status() {
        return $this->make_request('admin/status/');
    }
    
    /**
     * Get API providers status
     */
    public function get_api_status() {
        return $this->make_request('admin/api-providers/');
    }
}

/**
 * Global API instance
 */
function get_stock_scanner_api() {
    static $api = null;
    if ($api === null) {
        $api = new StockScannerAPI();
    }
    return $api;
}

/**
 * WordPress Shortcodes for Stock Scanner
 */

/**
 * Display stock data table
 * Usage: [stock_scanner_stocks limit="50" sort="volume"]
 */
function stock_scanner_stocks_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => 50,
        'sort' => 'volume',
        'template' => 'table'
    ), $atts);
    
    $api = get_stock_scanner_api();
    $stocks = $api->get_stocks($atts['limit'], array('sort' => $atts['sort']));
    
    if (!$stocks || empty($stocks['results'])) {
        return '<div class="stock-scanner-error">Unable to load stock data. Please try again later.</div>';
    }
    
    ob_start();
    
    if ($atts['template'] === 'cards') {
        include get_template_directory() . '/templates/stocks-cards.php';
    } else {
        include get_template_directory() . '/templates/stocks-table.php';
    }
    
    return ob_get_clean();
}
add_shortcode('stock_scanner_stocks', 'stock_scanner_stocks_shortcode');

/**
 * Display news articles
 * Usage: [stock_scanner_news limit="10"]
 */
function stock_scanner_news_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => 10,
        'template' => 'list'
    ), $atts);
    
    $api = get_stock_scanner_api();
    $news = $api->get_news($atts['limit']);
    
    if (!$news || empty($news['results'])) {
        return '<div class="stock-scanner-error">Unable to load news data. Please try again later.</div>';
    }
    
    ob_start();
    
    if ($atts['template'] === 'cards') {
        include get_template_directory() . '/templates/news-cards.php';
    } else {
        include get_template_directory() . '/templates/news-list.php';
    }
    
    return ob_get_clean();
}
add_shortcode('stock_scanner_news', 'stock_scanner_news_shortcode');

/**
 * Stock search widget
 * Usage: [stock_scanner_search]
 */
function stock_scanner_search_shortcode($atts) {
    ob_start();
    ?>
    <div class="stock-scanner-search">
        <form id="stock-search-form" method="get">
            <div class="search-input-group">
                <input type="text" 
                       id="stock-search-input" 
                       name="q" 
                       placeholder="Search stocks by ticker or company name..." 
                       required>
                <button type="submit" class="search-btn">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
        </form>
        <div id="stock-search-results"></div>
    </div>
    
    <script>
    jQuery(document).ready(function($) {
        $('#stock-search-form').on('submit', function(e) {
            e.preventDefault();
            
            const query = $('#stock-search-input').val();
            if (!query) return;
            
            $('#stock-search-results').html('<div class="loading">Searching...</div>');
            
            $.ajax({
                url: '<?php echo admin_url('admin-ajax.php'); ?>',
                type: 'POST',
                data: {
                    action: 'stock_scanner_search',
                    query: query,
                    nonce: '<?php echo wp_create_nonce('stock_scanner_search'); ?>'
                },
                success: function(response) {
                    if (response.success) {
                        $('#stock-search-results').html(response.data);
                    } else {
                        $('#stock-search-results').html('<div class="error">Search failed. Please try again.</div>');
                    }
                },
                error: function() {
                    $('#stock-search-results').html('<div class="error">Search failed. Please try again.</div>');
                }
            });
        });
    });
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_search', 'stock_scanner_search_shortcode');

/**
 * AJAX handler for stock search
 */
function handle_stock_scanner_search() {
    // Verify nonce
    if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_search')) {
        wp_die('Security check failed');
    }
    
    $query = sanitize_text_field($_POST['query']);
    if (empty($query)) {
        wp_send_json_error('Search query is required');
    }
    
    $api = get_stock_scanner_api();
    $results = $api->search_stocks($query);
    
    if (!$results) {
        wp_send_json_error('Search failed');
    }
    
    ob_start();
    if (!empty($results['results'])) {
        echo '<div class="search-results">';
        foreach ($results['results'] as $stock) {
            echo '<div class="search-result-item">';
            echo '<strong>' . esc_html($stock['ticker']) . '</strong> - ';
            echo esc_html($stock['company_name']);
            echo '<span class="price">$' . number_format($stock['current_price'], 2) . '</span>';
            echo '</div>';
        }
        echo '</div>';
    } else {
        echo '<div class="no-results">No stocks found matching your search.</div>';
    }
    $html = ob_get_clean();
    
    wp_send_json_success($html);
}
add_action('wp_ajax_stock_scanner_search', 'handle_stock_scanner_search');
add_action('wp_ajax_nopriv_stock_scanner_search', 'handle_stock_scanner_search');

/**
 * System status widget for admin
 * Usage: [stock_scanner_status] (admin only)
 */
function stock_scanner_status_shortcode($atts) {
    if (!current_user_can('manage_options')) {
        return '<div class="stock-scanner-error">Access denied.</div>';
    }
    
    $api = get_stock_scanner_api();
    $status = $api->get_system_status();
    
    if (!$status) {
        return '<div class="stock-scanner-error">Unable to fetch system status.</div>';
    }
    
    ob_start();
    ?>
    <div class="stock-scanner-status">
        <h3>Stock Scanner System Status</h3>
        <div class="status-grid">
            <div class="status-item">
                <label>Total Stocks:</label>
                <span><?php echo number_format($status['total_stocks'] ?? 0); ?></span>
            </div>
            <div class="status-item">
                <label>Last Update:</label>
                <span><?php echo esc_html($status['last_update'] ?? 'Never'); ?></span>
            </div>
            <div class="status-item">
                <label>Success Rate:</label>
                <span><?php echo esc_html($status['success_rate'] ?? 0); ?>%</span>
            </div>
            <div class="status-item">
                <label>News Articles:</label>
                <span><?php echo number_format($status['total_news'] ?? 0); ?></span>
            </div>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_status', 'stock_scanner_status_shortcode');

/**
 * Enqueue frontend scripts and styles
 */
function stock_scanner_enqueue_scripts() {
    wp_enqueue_style('stock-scanner-frontend', get_template_directory_uri() . '/css/stock-scanner.css', array(), '1.0.0');
    wp_enqueue_script('stock-scanner-frontend', get_template_directory_uri() . '/js/stock-scanner.js', array('jquery'), '1.0.0', true);
    
    // Localize script for AJAX
    wp_localize_script('stock-scanner-frontend', 'stockScannerAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');

/**
 * Add admin menu for Stock Scanner settings
 */
function stock_scanner_admin_menu() {
    add_options_page(
        'Stock Scanner Settings',
        'Stock Scanner',
        'manage_options',
        'stock-scanner-settings',
        'stock_scanner_settings_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_menu');

/**
 * Settings page content
 */
function stock_scanner_settings_page() {
    if (isset($_POST['submit'])) {
        update_option('stock_scanner_api_url', sanitize_text_field($_POST['api_url']));
        update_option('stock_scanner_api_key', sanitize_text_field($_POST['api_key']));
        echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
    }
    
    $api_url = get_option('stock_scanner_api_url', 'https://api.yourdomain.com');
    $api_key = get_option('stock_scanner_api_key', '');
    ?>
    <div class="wrap">
        <h1>Stock Scanner Settings</h1>
        <form method="post" action="">
            <table class="form-table">
                <tr>
                    <th scope="row">Django API URL</th>
                    <td>
                        <input type="url" name="api_url" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
                        <p class="description">The URL of your Django API (e.g., https://api.yourdomain.com)</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">API Key</th>
                    <td>
                        <input type="text" name="api_key" value="<?php echo esc_attr($api_key); ?>" class="regular-text" />
                        <p class="description">Optional API key for authentication</p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
        
        <h2>System Status</h2>
        <?php echo do_shortcode('[stock_scanner_status]'); ?>
    </div>
    <?php
}

/**
 * Register settings
 */
function stock_scanner_register_settings() {
    register_setting('stock_scanner_settings', 'stock_scanner_api_url');
    register_setting('stock_scanner_settings', 'stock_scanner_api_key');
}
add_action('admin_init', 'stock_scanner_register_settings');

/**
 * Health check cron job
 */
function stock_scanner_health_check() {
    $api = get_stock_scanner_api();
    $status = $api->get_system_status();
    
    if (!$status) {
        // Log error or send notification
        error_log('Stock Scanner API health check failed');
        
        // Optionally send email to admin
        $admin_email = get_option('admin_email');
        if ($admin_email) {
            wp_mail(
                $admin_email,
                'Stock Scanner API Health Check Failed',
                'The Stock Scanner API is not responding. Please check the Django backend.'
            );
        }
    }
}

// Schedule health check (runs every 15 minutes)
if (!wp_next_scheduled('stock_scanner_health_check')) {
    wp_schedule_event(time(), 'fifteen_minutes', 'stock_scanner_health_check');
}
add_action('stock_scanner_health_check', 'stock_scanner_health_check');

// Add custom cron interval
function stock_scanner_cron_intervals($schedules) {
    $schedules['fifteen_minutes'] = array(
        'interval' => 900,
        'display' => __('Every 15 Minutes')
    );
    return $schedules;
}
add_filter('cron_schedules', 'stock_scanner_cron_intervals');
?>