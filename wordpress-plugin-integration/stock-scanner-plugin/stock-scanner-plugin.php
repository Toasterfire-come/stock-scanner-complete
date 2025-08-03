<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://your-domain.com
 * Description: Integrates with Django Stock Scanner API for real-time stock data and news
 * Version: 1.0.0
 * Author: Stock Scanner Team
 * License: GPL v2 or later
 * Text Domain: stock-scanner-plugin
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Stock Scanner Plugin Class
 */
class StockScannerPlugin {
    
    private $api_url;
    private $api_timeout;
    private $cache_duration;
    
    public function __construct() {
        $this->api_url = get_option('stock_scanner_api_url', 'http://127.0.0.1:8000/api');
        $this->api_timeout = 30;
        $this->cache_duration = 300; // 5 minutes
        
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_ajax_get_stocks', array($this, 'ajax_get_stocks'));
        add_action('wp_ajax_nopriv_get_stocks', array($this, 'ajax_get_stocks'));
        add_action('wp_ajax_get_news', array($this, 'ajax_get_news'));
        add_action('wp_ajax_nopriv_get_news', array($this, 'ajax_get_news'));
        add_action('wp_ajax_get_market_summary', array($this, 'ajax_get_market_summary'));
        add_action('wp_ajax_nopriv_get_market_summary', array($this, 'ajax_get_market_summary'));
        
        // Add shortcodes
        add_shortcode('stock_ticker', array($this, 'stock_ticker_shortcode'));
        add_shortcode('stock_news', array($this, 'stock_news_shortcode'));
        add_shortcode('market_summary', array($this, 'market_summary_shortcode'));
        
        // Add admin menu
        add_action('admin_menu', array($this, 'admin_menu'));
        
        // Add widget
        add_action('widgets_init', array($this, 'register_widgets'));
        
        // Add settings
        add_action('admin_init', array($this, 'admin_init'));
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        // Load text domain for translations
        load_plugin_textdomain('stock-scanner-plugin', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    /**
     * Enqueue scripts and styles
     */
    public function enqueue_scripts() {
        wp_enqueue_script('jquery');
        
        wp_enqueue_script(
            'stock-scanner-plugin-js',
            plugin_dir_url(__FILE__) . 'js/stock-scanner-plugin.js',
            array('jquery'),
            '1.0.0',
            true
        );
        
        wp_enqueue_style(
            'stock-scanner-plugin-css',
            plugin_dir_url(__FILE__) . 'css/stock-scanner-plugin.css',
            array(),
            '1.0.0'
        );
        
        // Localize script
        wp_localize_script('stock-scanner-plugin-js', 'stockScannerAjax', array(
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
            'api_url' => $this->api_url,
            'cache_duration' => $this->cache_duration
        ));
    }
    
    /**
     * AJAX handler for stock data
     */
    public function ajax_get_stocks() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $limit = isset($_POST['limit']) ? intval($_POST['limit']) : 10;
        $category = isset($_POST['category']) ? sanitize_text_field($_POST['category']) : '';
        $search = isset($_POST['search']) ? sanitize_text_field($_POST['search']) : '';
        
        // Check cache first
        $cache_key = 'stock_scanner_stocks_' . md5($limit . $category . $search);
        $cached_data = get_transient($cache_key);
        
        if ($cached_data !== false) {
            wp_send_json_success($cached_data);
            return;
        }
        
        // Build API URL
        $api_url = trailingslashit($this->api_url) . 'wordpress/stocks/';
        $api_url = add_query_arg(array(
            'limit' => $limit,
            'category' => $category,
            'search' => $search
        ), $api_url);
        
        // Make API request
        $response = $this->make_api_request($api_url);
        
        if (is_wp_error($response)) {
            wp_send_json_error('Failed to fetch stock data: ' . $response->get_error_message());
            return;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            wp_send_json_error('Invalid JSON response from API');
            return;
        }
        
        // Cache the response
        set_transient($cache_key, $data, $this->cache_duration);
        
        wp_send_json_success($data);
    }
    
    /**
     * AJAX handler for news data
     */
    public function ajax_get_news() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $limit = isset($_POST['limit']) ? intval($_POST['limit']) : 5;
        $show_sentiment = isset($_POST['show_sentiment']) ? (bool)$_POST['show_sentiment'] : true;
        
        // Check cache first
        $cache_key = 'stock_scanner_news_' . md5($limit . $show_sentiment);
        $cached_data = get_transient($cache_key);
        
        if ($cached_data !== false) {
            wp_send_json_success($cached_data);
            return;
        }
        
        // Build API URL
        $api_url = trailingslashit($this->api_url) . 'wordpress/news/';
        $api_url = add_query_arg(array(
            'limit' => $limit
        ), $api_url);
        
        // Make API request
        $response = $this->make_api_request($api_url);
        
        if (is_wp_error($response)) {
            wp_send_json_error('Failed to fetch news data: ' . $response->get_error_message());
            return;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            wp_send_json_error('Invalid JSON response from API');
            return;
        }
        
        // Cache the response
        set_transient($cache_key, $data, $this->cache_duration);
        
        wp_send_json_success($data);
    }
    
    /**
     * AJAX handler for market summary
     */
    public function ajax_get_market_summary() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        // Check cache first
        $cache_key = 'stock_scanner_market_summary';
        $cached_data = get_transient($cache_key);
        
        if ($cached_data !== false) {
            wp_send_json_success($cached_data);
            return;
        }
        
        // Build API URL
        $api_url = trailingslashit($this->api_url) . 'market/stats/';
        
        // Make API request
        $response = $this->make_api_request($api_url);
        
        if (is_wp_error($response)) {
            // Return sample data if API fails
            $sample_data = array(
                'S&P 500' => array('value' => '4,567.89', 'change' => '+1.23%'),
                'NASDAQ' => array('value' => '14,234.56', 'change' => '+0.87%'),
                'DOW' => array('value' => '34,567.12', 'change' => '+0.45%')
            );
            wp_send_json_success($sample_data);
            return;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            wp_send_json_error('Invalid JSON response from API');
            return;
        }
        
        // Cache the response
        set_transient($cache_key, $data, $this->cache_duration);
        
        wp_send_json_success($data);
    }
    
    /**
     * Make API request with error handling
     */
    private function make_api_request($url) {
        $args = array(
            'timeout' => $this->api_timeout,
            'headers' => array(
                'User-Agent' => 'WordPress Stock Scanner Plugin/1.0.0',
                'Accept' => 'application/json'
            )
        );
        
        $response = wp_remote_get($url, $args);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        $response_code = wp_remote_retrieve_response_code($response);
        
        if ($response_code !== 200) {
            return new WP_Error('api_error', 'API returned status code: ' . $response_code);
        }
        
        return $response;
    }
    
    /**
     * Stock ticker shortcode
     */
    public function stock_ticker_shortcode($atts) {
        $atts = shortcode_atts(array(
            'limit' => 10,
            'category' => '',
            'show_changes' => 'true',
            'auto_refresh' => 'true',
            'refresh_interval' => 30
        ), $atts);
        
        $unique_id = 'stock-ticker-' . uniqid();
        
        ob_start();
        ?>
        <div class="stock-ticker-widget" 
             id="<?php echo esc_attr($unique_id); ?>"
             data-limit="<?php echo esc_attr($atts['limit']); ?>"
             data-category="<?php echo esc_attr($atts['category']); ?>"
             data-show-changes="<?php echo esc_attr($atts['show_changes']); ?>"
             data-auto-refresh="<?php echo esc_attr($atts['auto_refresh']); ?>"
             data-refresh-interval="<?php echo esc_attr($atts['refresh_interval']); ?>">
            
            <div class="ticker-loading">
                <div class="loading-spinner"></div>
                <p>Loading stock data...</p>
            </div>
            
            <div class="ticker-content" style="display: none;">
                <div class="ticker-header">
                    <h3>Live Stock Ticker</h3>
                    <span class="last-updated"></span>
                </div>
                <div class="ticker-items"></div>
            </div>
            
            <div class="ticker-error" style="display: none;">
                <p>Unable to load stock data. Please try again later.</p>
                <button class="retry-btn">Retry</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Stock news shortcode
     */
    public function stock_news_shortcode($atts) {
        $atts = shortcode_atts(array(
            'limit' => 5,
            'show_sentiment' => 'true',
            'auto_refresh' => 'true',
            'refresh_interval' => 60
        ), $atts);
        
        $unique_id = 'stock-news-' . uniqid();
        
        ob_start();
        ?>
        <div class="stock-news-widget" 
             id="<?php echo esc_attr($unique_id); ?>"
             data-limit="<?php echo esc_attr($atts['limit']); ?>"
             data-show-sentiment="<?php echo esc_attr($atts['show_sentiment']); ?>"
             data-auto-refresh="<?php echo esc_attr($atts['auto_refresh']); ?>"
             data-refresh-interval="<?php echo esc_attr($atts['refresh_interval']); ?>">
            
            <div class="news-loading">
                <div class="loading-spinner"></div>
                <p>Loading news...</p>
            </div>
            
            <div class="news-content" style="display: none;">
                <div class="news-header">
                    <h3>Latest Market News</h3>
                    <span class="last-updated"></span>
                </div>
                <div class="news-items"></div>
            </div>
            
            <div class="news-error" style="display: none;">
                <p>Unable to load news. Please try again later.</p>
                <button class="retry-btn">Retry</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Market summary shortcode
     */
    public function market_summary_shortcode($atts) {
        $atts = shortcode_atts(array(
            'show_changes' => 'true',
            'auto_refresh' => 'true',
            'refresh_interval' => 60
        ), $atts);
        
        $unique_id = 'market-summary-' . uniqid();
        
        ob_start();
        ?>
        <div class="market-summary-widget" 
             id="<?php echo esc_attr($unique_id); ?>"
             data-show-changes="<?php echo esc_attr($atts['show_changes']); ?>"
             data-auto-refresh="<?php echo esc_attr($atts['auto_refresh']); ?>"
             data-refresh-interval="<?php echo esc_attr($atts['refresh_interval']); ?>">
            
            <div class="summary-loading">
                <div class="loading-spinner"></div>
                <p>Loading market data...</p>
            </div>
            
            <div class="summary-content" style="display: none;">
                <div class="summary-header">
                    <h3>Market Summary</h3>
                    <span class="last-updated"></span>
                </div>
                <div class="summary-items"></div>
            </div>
            
            <div class="summary-error" style="display: none;">
                <p>Unable to load market data. Please try again later.</p>
                <button class="retry-btn">Retry</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Add admin menu
     */
    public function admin_menu() {
        add_options_page(
            'Stock Scanner Settings',
            'Stock Scanner',
            'manage_options',
            'stock-scanner-settings',
            array($this, 'admin_page')
        );
    }
    
    /**
     * Admin page
     */
    public function admin_page() {
        if (isset($_POST['submit'])) {
            // Save API settings
            update_option('stock_scanner_api_url', sanitize_url($_POST['api_url']));
            $this->api_url = get_option('stock_scanner_api_url');
            
            // Save PayPal settings
            update_option('paypal_mode', sanitize_text_field($_POST['paypal_mode']));
            update_option('paypal_client_id', sanitize_text_field($_POST['paypal_client_id']));
            update_option('paypal_client_secret', sanitize_text_field($_POST['paypal_client_secret']));
            update_option('paypal_webhook_url', sanitize_url($_POST['paypal_webhook_url']));
            update_option('paypal_return_url', sanitize_url($_POST['paypal_return_url']));
            update_option('paypal_cancel_url', sanitize_url($_POST['paypal_cancel_url']));
            
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        
        // Debug: Check if PayPal settings exist
        $paypal_mode = get_option('paypal_mode', 'sandbox');
        $paypal_client_id = get_option('paypal_client_id', '');
        $paypal_client_secret = get_option('paypal_client_secret', '');
        $paypal_webhook_url = get_option('paypal_webhook_url', '');
        $paypal_return_url = get_option('paypal_return_url', '');
        $paypal_cancel_url = get_option('paypal_cancel_url', '');
        
        ?>
        <div class="wrap">
            <h1>Stock Scanner Settings</h1>
            
            <!-- Debug Info (remove in production) -->
            <div class="notice notice-info">
                <p><strong>Debug Info:</strong> PayPal settings are loaded and ready to display.</p>
            </div>
            
            <form method="post">
                <h2>API Configuration</h2>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="api_url">Django API URL</label>
                        </th>
                        <td>
                            <input type="url" id="api_url" name="api_url" 
                                   value="<?php echo esc_attr($this->api_url); ?>" 
                                   class="regular-text" />
                            <p class="description">
                                Enter the URL of your Django API server (e.g., http://your-domain.com/api)
                            </p>
                        </td>
                    </tr>
                </table>
                
                <h2>PayPal Configuration</h2>
                <table class="form-table">
                    <tr>
                        <th scope="row">PayPal Mode</th>
                        <td>
                            <select name="paypal_mode">
                                <option value="sandbox" <?php selected($paypal_mode, 'sandbox'); ?>>Sandbox (Testing)</option>
                                <option value="live" <?php selected($paypal_mode, 'live'); ?>>Live (Production)</option>
                            </select>
                            <p class="description">Use Sandbox for testing, Live for production</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Client ID</th>
                        <td>
                            <input type="text" name="paypal_client_id" 
                                   value="<?php echo esc_attr($paypal_client_id); ?>" 
                                   class="regular-text" />
                            <p class="description">Your PayPal App Client ID from the Developer Dashboard</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Client Secret</th>
                        <td>
                            <input type="password" name="paypal_client_secret" 
                                   value="<?php echo esc_attr($paypal_client_secret); ?>" 
                                   class="regular-text" />
                            <p class="description">Your PayPal App Client Secret from the Developer Dashboard</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Webhook URL</th>
                        <td>
                            <input type="url" name="paypal_webhook_url" 
                                   value="<?php echo esc_attr($paypal_webhook_url); ?>" 
                                   class="regular-text" />
                            <p class="description">Set this URL in your PayPal Developer Dashboard: <?php echo home_url('/wp-json/stock-scanner/v1/paypal-webhook'); ?></p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Return URL</th>
                        <td>
                            <input type="url" name="paypal_return_url" 
                                   value="<?php echo esc_attr($paypal_return_url); ?>" 
                                   class="regular-text" />
                            <p class="description">URL where users return after successful payment</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Cancel URL</th>
                        <td>
                            <input type="url" name="paypal_cancel_url" 
                                   value="<?php echo esc_attr($paypal_cancel_url); ?>" 
                                   class="regular-text" />
                            <p class="description">URL where users return after cancelled payment</p>
                        </td>
                    </tr>
                </table>
                
                <?php submit_button(); ?>
            </form>
            
            <h2>Test API Connection</h2>
            <button type="button" id="test-api-btn" class="button">Test Connection</button>
            <div id="test-result"></div>
            
            <h2>Shortcode Examples</h2>
            <div class="shortcode-examples">
                <h3>Stock Ticker</h3>
                <code>[stock_ticker limit="10" category="gainers"]</code>
                
                <h3>News Feed</h3>
                <code>[stock_news limit="5" show_sentiment="true"]</code>
                
                <h3>Market Summary</h3>
                <code>[market_summary show_changes="true"]</code>
            </div>
        </div>
        <?php
    }
    
    /**
     * Admin init
     */
    public function admin_init() {
        // Register API settings
        register_setting('stock_scanner_settings', 'stock_scanner_api_url');
        
        // Register PayPal settings
        register_setting('stock_scanner_settings', 'paypal_mode');
        register_setting('stock_scanner_settings', 'paypal_client_id');
        register_setting('stock_scanner_settings', 'paypal_client_secret');
        register_setting('stock_scanner_settings', 'paypal_webhook_url');
        register_setting('stock_scanner_settings', 'paypal_return_url');
        register_setting('stock_scanner_settings', 'paypal_cancel_url');
    }
    
    /**
     * Register widgets
     */
    public function register_widgets() {
        register_widget('StockScannerWidget');
    }
}

/**
 * Stock Scanner Widget
 */
class StockScannerWidget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'stock_scanner_widget',
            'Stock Scanner Widget',
            array('description' => 'Display stock data and news')
        );
    }
    
    public function widget($args, $instance) {
        echo $args['before_widget'];
        
        if (!empty($instance['title'])) {
            echo $args['before_title'] . apply_filters('widget_title', $instance['title']) . $args['after_title'];
        }
        
        $type = isset($instance['type']) ? $instance['type'] : 'ticker';
        $limit = isset($instance['limit']) ? intval($instance['limit']) : 5;
        
        switch ($type) {
            case 'ticker':
                echo do_shortcode("[stock_ticker limit=\"{$limit}\"]");
                break;
            case 'news':
                echo do_shortcode("[stock_news limit=\"{$limit}\"]");
                break;
            case 'summary':
                echo do_shortcode("[market_summary]");
                break;
        }
        
        echo $args['after_widget'];
    }
    
    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : '';
        $type = !empty($instance['type']) ? $instance['type'] : 'ticker';
        $limit = !empty($instance['limit']) ? intval($instance['limit']) : 5;
        ?>
        <p>
            <label for="<?php echo $this->get_field_id('title'); ?>">Title:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('title'); ?>" 
                   name="<?php echo $this->get_field_name('title'); ?>" type="text" 
                   value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('type'); ?>">Widget Type:</label>
            <select class="widefat" id="<?php echo $this->get_field_id('type'); ?>" 
                    name="<?php echo $this->get_field_name('type'); ?>">
                <option value="ticker" <?php selected($type, 'ticker'); ?>>Stock Ticker</option>
                <option value="news" <?php selected($type, 'news'); ?>>News Feed</option>
                <option value="summary" <?php selected($type, 'summary'); ?>>Market Summary</option>
            </select>
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('limit'); ?>">Limit:</label>
            <input class="tiny-text" id="<?php echo $this->get_field_id('limit'); ?>" 
                   name="<?php echo $this->get_field_name('limit'); ?>" type="number" 
                   value="<?php echo esc_attr($limit); ?>" min="1" max="20">
        </p>
        <?php
    }
    
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? strip_tags($new_instance['title']) : '';
        $instance['type'] = (!empty($new_instance['type'])) ? strip_tags($new_instance['type']) : 'ticker';
        $instance['limit'] = (!empty($new_instance['limit'])) ? intval($new_instance['limit']) : 5;
        return $instance;
    }
}

// Initialize the plugin
new StockScannerPlugin();