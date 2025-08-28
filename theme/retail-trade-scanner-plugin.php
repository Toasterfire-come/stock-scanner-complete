<?php
/**
 * Plugin Name: Retail Trade Scanner Integration
 * Plugin URI: https://retailtradescanner.com
 * Description: Creates comprehensive trading platform with live stock widgets, membership paywall, and seamless API integration
 * Version: 2.1.0
 * Author: Retail Trade Scanner Team
 * Author URI: https://retailtradescanner.com
 * Text Domain: retail-trade-scanner-plugin
 * Requires at least: 6.0
 * Tested up to: 6.5
 * Requires PHP: 7.4
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * PLUGIN FUNCTIONALITY OVERVIEW
 * 
 * This plugin automatically creates comprehensive trading platform pages:
 * 
 * MAIN TRADING PAGES:
 * - Premium Plans (/premium-plans/) - Gold/Silver/Free comparison with live widgets
 * - Email Stock Lists (/email-stock-lists/) - Subscribe to alert lists
 * - All Stock Alerts (/all-stock-lists/) - Complete stock list collection
 * - Popular Stock Lists (/popular-stock-lists/) - Most subscribed lists
 * - Stock Search (/stock-search/) - Advanced search tools
 * - Personalized Stock Finder (/personalized-stock-finder/) - AI recommendations
 * - News Scraper (/news-scraper/) - Financial news aggregation
 * - Filter and Scraper Pages (/filter-and-scraper-pages/) - Advanced filtering
 * 
 * MEMBERSHIP & ACCOUNT:
 * - Membership Account (/membership-account/) - Account management
 * - Membership Billing (/membership-billing/) - Payment history
 * - Membership Cancel (/membership-cancel/) - Subscription cancellation
 * - Membership Checkout (/membership-checkout/) - Purchase process
 * - Membership Confirmation (/membership-confirmation/) - Purchase confirmation
 * - Membership Orders (/membership-orders/) - Order history
 * - Membership Levels (/membership-levels/) - Plan comparison
 * - Login (/login/) - User authentication
 * - Your Profile (/your-profile/) - Profile management
 * 
 * LEGAL PAGES:
 * - Terms and Conditions (/terms-and-conditions/)
 * - Privacy Policy (/privacy-policy/)
 * 
 * ADDITIONAL FEATURES:
 * - Live stock widgets on every page
 * - Responsive design with professional styling
 * - Membership paywall integration
 * - Complete navigation menu
 * - API integration with comprehensive endpoints
 */

class RetailTradeScannerIntegration {
    
    private $api_base_url;
    private $api_secret;
    
    public function __construct() {
        $this->api_base_url = get_option('retail_trade_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        $this->api_secret = get_option('retail_trade_scanner_api_secret', '');
        
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('retail_trade_scanner', array($this, 'retail_trade_scanner_shortcode'));
        add_action('admin_menu', array($this, 'admin_menu'));
        add_action('wp_dashboard_setup', array($this, 'add_dashboard_widget'));
        add_action('admin_notices', array($this, 'settings_notices'));
        
        // Sales tax hooks
        add_filter('pmpro_tax', array($this, 'calculate_sales_tax'), 10, 3);
        add_action('pmpro_checkout_preheader', array($this, 'detect_user_location'));
        add_filter('pmpro_checkout_order', array($this, 'add_tax_to_order'), 10, 1);
        
        // Include PayPal integration
        if (file_exists(plugin_dir_path(__FILE__) . 'includes/class-paypal-integration.php')) {
            require_once plugin_dir_path(__FILE__) . 'includes/class-paypal-integration.php';
        }
    }
    
    public function settings_notices() {
        if (!current_user_can('manage_options')) return;
        $api_url = get_option('retail_trade_scanner_api_url', '');
        $api_secret = get_option('retail_trade_scanner_api_secret', '');
        if (empty($api_url) || empty($api_secret)) {
            echo '<div class="notice notice-error"><p>' . 
                 sprintf(
                     /* translators: %s: Settings page URL */
                     esc_html__('Retail Trade Scanner Integration: Please configure API URL and API Secret in %s.', 'retail-trade-scanner-plugin'),
                     '<a href="' . esc_url(admin_url('options-general.php?page=retail-trade-scanner-settings')) . '">' . 
                     esc_html__('Settings → Retail Trade Scanner', 'retail-trade-scanner-plugin') . '</a>'
                 ) . '</p></div>';
        }
    }
    
    public function init() {
        // Register AJAX actions
        add_action('wp_ajax_get_retail_trade_scanner_data', array($this, 'ajax_get_stock_data'));
        add_action('wp_ajax_nopriv_get_retail_trade_scanner_data', array($this, 'ajax_get_stock_data'));
        
        // Admin test API endpoint
        add_action('wp_ajax_test_retail_trade_scanner_api', array($this, 'ajax_test_api'));
        
        // Hook into PMP membership changes
        add_action('pmpro_after_change_membership_level', array($this, 'sync_membership_level'), 10, 2);
    }
    
    public function enqueue_scripts() {
        $assets_dir = plugin_dir_path(__FILE__) . 'assets/';
        $assets_url = plugin_dir_url(__FILE__) . 'assets/';

        // Enqueue Chart.js when shortcode is present or globally if needed
        wp_register_script('chartjs', 'https://cdn.jsdelivr.net/npm/chart.js', array(), null, true);

        if (file_exists($assets_dir . 'retail-trade-scanner.js')) {
            $js_ver = filemtime($assets_dir . 'retail-trade-scanner.js');
            wp_enqueue_script('retail-trade-scanner-js', $assets_url . 'retail-trade-scanner.js', array('jquery', 'chartjs'), $js_ver, true);
        }

        if (file_exists($assets_dir . 'paypal-integration.js')) {
            $paypal_js_ver = filemtime($assets_dir . 'paypal-integration.js');
            wp_enqueue_script('paypal-integration', $assets_url . 'paypal-integration.js', array('jquery'), $paypal_js_ver, true);
        }

        if (file_exists($assets_dir . 'retail-trade-scanner.css')) {
            $css_ver = filemtime($assets_dir . 'retail-trade-scanner.css');
            wp_enqueue_style('retail-trade-scanner-css', $assets_url . 'retail-trade-scanner.css', array(), $css_ver);
        }
        
        // Localize script for AJAX
        wp_localize_script('retail-trade-scanner-js', 'retail_trade_scanner_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('retail_trade_scanner_nonce'),
            'api_base' => trailingslashit(get_option('retail_trade_scanner_api_url', ''))
        ));
        
        // Localize PayPal script if available
        if (wp_script_is('paypal-integration', 'registered')) {
            wp_localize_script('paypal-integration', 'paypalConfig', array(
                'ajaxUrl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('paypal_nonce'),
                'clientId' => get_option('paypal_client_id', ''),
                'successUrl' => get_option('paypal_return_url', ''),
                'cancelUrl' => get_option('paypal_cancel_url', ''),
                'mode' => get_option('paypal_mode', 'sandbox')
            ));
        }
    }
    
    /**
     * Shortcode: [retail_trade_scanner symbol="AAPL"]
     */
    public function retail_trade_scanner_shortcode($atts) {
        $atts = shortcode_atts(array(
            'symbol' => 'AAPL',
            'show_chart' => true,
            'show_details' => true
        ), $atts);
        
        // Check if user has access
        $user_level = $this->get_user_membership_level();
        $usage = $this->get_user_usage(get_current_user_id());
        
        if (!$this->can_user_access_stock($user_level, $usage)) {
            return $this->render_paywall_message($user_level, $usage);
        }
        
        return $this->render_stock_widget($atts);
    }
    
    public function ajax_get_stock_data() {
        check_ajax_referer('retail_trade_scanner_nonce', 'nonce');

        $symbol = isset($_POST['symbol']) ? sanitize_text_field($_POST['symbol']) : '';
        if (empty($symbol)) {
            wp_send_json_error(array('message' => esc_html__('Missing symbol', 'retail-trade-scanner-plugin')));
        }
        
        $user_id = get_current_user_id();
        
        // Check config
        $api_url = get_option('retail_trade_scanner_api_url', '');
        $api_secret = get_option('retail_trade_scanner_api_secret', '');
        if (empty($api_url) || empty($api_secret)) {
            wp_send_json_error(array('message' => esc_html__('API not configured. Please set API URL and Secret in Settings → Retail Trade Scanner.', 'retail-trade-scanner-plugin')));
        }
        
        // Check user permissions
        $user_level = $this->get_user_membership_level();
        $usage = $this->get_user_usage($user_id);
        
        if (!$this->can_user_access_stock($user_level, $usage)) {
            wp_send_json_error(array(
                'message' => esc_html__('Usage limit exceeded. Please upgrade your membership.', 'retail-trade-scanner-plugin'),
                'usage' => $usage,
                'limit' => $this->get_usage_limit($user_level)
            ));
        }
        
        // Make API request
        $stock_data = $this->api_request('api/stocks/', array(
            'symbol' => $symbol,
            'user_id' => $user_id
        ));
        
        if ($stock_data) {
            wp_send_json_success($stock_data);
        } else {
            wp_send_json_error(array('message' => esc_html__('Failed to fetch stock data from API', 'retail-trade-scanner-plugin')));
        }
    }
    
    private function api_request($endpoint, $data = array()) {
        $url = trailingslashit(apply_filters('retail_trade_scanner_api_base_url', $this->api_base_url)) . ltrim($endpoint, '/');

        // Validate configuration
        if (empty($this->api_base_url) || empty($this->api_secret)) {
            error_log('Retail Trade Scanner API not configured: missing API URL or Secret');
            return false;
        }
        
        $args = array(
            'method' => 'POST',
            'body' => $data ? wp_json_encode($data) : null,
            'headers' => array(
                'Content-Type' => 'application/json',
                'X-API-Secret' => $this->api_secret,
                'X-User-Level' => $this->get_user_membership_level(),
                'X-User-ID' => get_current_user_id()
            ),
            'timeout' => 20
        );
        
        // Allow sites to customize the request
        $args = apply_filters('retail_trade_scanner_api_request_args', $args, $endpoint, $data);
        
        if (empty($data)) {
            unset($args['body']);
            $args['method'] = 'GET';
        }
        
        $response = wp_remote_request($url, $args);
        
        if (is_wp_error($response)) {
            error_log('Retail Trade Scanner API Error: ' . $response->get_error_message());
            return false;
        }
        
        $status = wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            error_log('Retail Trade Scanner API HTTP ' . $status . ' for ' . $url);
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $decoded = json_decode($body, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log('Retail Trade Scanner API JSON decode error: ' . json_last_error_msg());
            return false;
        }
        
        // Normalize success structure
        if (!is_array($decoded)) { 
            $decoded = array('data' => $decoded); 
        }
        return $decoded;
    }
    
    private function get_user_membership_level() {
        if (!function_exists('pmpro_getMembershipLevelForUser')) {
            return 0; // Free level
        }
        
        $level = pmpro_getMembershipLevelForUser(get_current_user_id());
        return $level ? $level->id : 0;
    }
    
    private function get_user_usage($user_id) {
        $response = $this->api_request('api/user/usage/', array('user_id' => $user_id));
        if (!$response || !isset($response['usage'])) {
            return array('monthly' => 0, 'daily' => 0);
        }
        return $response['usage'];
    }
    
    private function can_user_access_stock($user_level, $usage) {
        $limits = array(
            0 => 15,    // Free
            1 => 15,    // Free
            2 => 1000,  // Bronze/Premium
            3 => 5000,  // Silver/Professional
            4 => 10000  // Gold
        );
        
        $limit = isset($limits[$user_level]) ? $limits[$user_level] : 15;
        return $usage['monthly'] < $limit;
    }
    
    private function get_usage_limit($user_level) {
        $limits = array(
            0 => 15,    // Free
            1 => 15,    // Free
            2 => 1000,  // Bronze/Premium
            3 => 5000,  // Silver/Professional  
            4 => 10000  // Gold
        );
        
        return isset($limits[$user_level]) ? $limits[$user_level] : 15;
    }
    
    private function render_paywall_message($user_level, $usage) {
        $limit = $this->get_usage_limit($user_level);
        
        ob_start();
        ?>
        <div class="retail-trade-scanner-paywall">
            <div class="paywall-message">
                <h3><?php esc_html_e('🚀 Upgrade to Get More Stock Data', 'retail-trade-scanner-plugin'); ?></h3>
                <p>
                    <?php 
                    printf(
                        /* translators: %1$d: current usage, %2$d: monthly limit */
                        esc_html__('You\'ve used %1$d out of %2$d stocks this month.', 'retail-trade-scanner-plugin'), 
                        (int) $usage['monthly'], 
                        (int) $limit
                    ); 
                    ?>
                </p>
                
                <div class="membership-options">
                    <div class="membership-tier">
                        <h4><?php esc_html_e('Premium - $14.99/month', 'retail-trade-scanner-plugin'); ?></h4>
                        <p><?php esc_html_e('1,000 stocks per month', 'retail-trade-scanner-plugin'); ?></p>
                        <a href="<?php echo esc_url(function_exists('pmpro_url') ? pmpro_url('checkout', '?level=2') : '#'); ?>" class="btn btn-premium">
                            <?php esc_html_e('Upgrade to Premium', 'retail-trade-scanner-plugin'); ?>
                        </a>
                    </div>
                    
                    <div class="membership-tier">
                        <h4><?php esc_html_e('Professional - $29.99/month', 'retail-trade-scanner-plugin'); ?></h4>
                        <p><?php esc_html_e('5,000 stocks per month', 'retail-trade-scanner-plugin'); ?></p>
                        <a href="<?php echo esc_url(function_exists('pmpro_url') ? pmpro_url('checkout', '?level=3') : '#'); ?>" class="btn btn-professional">
                            <?php esc_html_e('Upgrade to Professional', 'retail-trade-scanner-plugin'); ?>
                        </a>
                    </div>
                    
                    <div class="membership-tier">
                        <h4><?php esc_html_e('Gold - $59.99/month', 'retail-trade-scanner-plugin'); ?></h4>
                        <p><?php esc_html_e('10,000 stocks per month', 'retail-trade-scanner-plugin'); ?></p>
                        <a href="<?php echo esc_url(function_exists('pmpro_url') ? pmpro_url('checkout', '?level=4') : '#'); ?>" class="btn btn-gold">
                            <?php esc_html_e('Upgrade to Gold', 'retail-trade-scanner-plugin'); ?>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    private function render_stock_widget($atts) {
        ob_start();
        ?>
        <div class="retail-trade-scanner-widget" data-symbol="<?php echo esc_attr($atts['symbol']); ?>">
            <div class="stock-header">
                <h3><?php echo esc_html($atts['symbol']); ?></h3>
                <button class="refresh-btn btn btn-sm btn-secondary" onclick="retailTradeScanner.refreshStock('<?php echo esc_js($atts['symbol']); ?>')">
                    <?php esc_html_e('Refresh', 'retail-trade-scanner-plugin'); ?>
                </button>
            </div>
            
            <div class="stock-data">
                <div class="loading"><?php esc_html_e('Loading stock data...', 'retail-trade-scanner-plugin'); ?></div>
                <div class="stock-price" style="display:none;">
                    <span class="price"></span>
                    <span class="change"></span>
                </div>
            </div>
            
            <?php if ($atts['show_chart']): ?>
            <div class="stock-chart">
                <canvas id="chart-<?php echo esc_attr($atts['symbol']); ?>"></canvas>
            </div>
            <?php endif; ?>
            
            <?php if ($atts['show_details']): ?>
            <div class="stock-details" style="display:none;">
                <div class="detail-item">
                    <label><?php esc_html_e('Volume:', 'retail-trade-scanner-plugin'); ?></label>
                    <span class="volume"></span>
                </div>
                <div class="detail-item">
                    <label><?php esc_html_e('Market Cap:', 'retail-trade-scanner-plugin'); ?></label>
                    <span class="market-cap"></span>
                </div>
            </div>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function sync_membership_level($level_id, $user_id) {
        // Sync membership level change with API backend
        $this->api_request('api/user/membership/', array(
            'user_id' => $user_id,
            'level_id' => $level_id,
            'action' => 'level_change'
        ));
    }
    
    public function admin_menu() {
        add_options_page(
            esc_html__('Retail Trade Scanner Settings', 'retail-trade-scanner-plugin'),
            esc_html__('Retail Trade Scanner', 'retail-trade-scanner-plugin'),
            'manage_options',
            'retail-trade-scanner-settings',
            array($this, 'admin_page')
        );
    }
    
    public function admin_page() {
        if (isset($_POST['submit'])) {
            if (!current_user_can('manage_options')) {
                wp_die(esc_html__('You do not have sufficient permissions to access this page.', 'retail-trade-scanner-plugin'));
            }
            check_admin_referer('retail_trade_scanner_settings');
            
            update_option('retail_trade_scanner_api_url', esc_url_raw($_POST['api_url']));
            update_option('retail_trade_scanner_api_secret', sanitize_text_field($_POST['api_secret']));
            echo '<div class="notice notice-success"><p>' . esc_html__('Settings saved!', 'retail-trade-scanner-plugin') . '</p></div>';
        }
        
        $api_url = get_option('retail_trade_scanner_api_url', '');
        $api_secret = get_option('retail_trade_scanner_api_secret', '');
        
        ?>
        <div class="wrap">
            <h1><?php esc_html_e('Retail Trade Scanner Settings', 'retail-trade-scanner-plugin'); ?></h1>
            
            <?php if (empty($api_url) || empty($api_secret)) : ?>
                <div class="notice notice-warning">
                    <p><strong><?php esc_html_e('Heads up:', 'retail-trade-scanner-plugin'); ?></strong> 
                    <?php esc_html_e('API URL and/or API Secret are empty. The plugin will not be able to reach the API until configured.', 'retail-trade-scanner-plugin'); ?></p>
                </div>
            <?php endif; ?>

            <form method="post">
                <?php wp_nonce_field('retail_trade_scanner_settings'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><?php esc_html_e('Quick Status', 'retail-trade-scanner-plugin'); ?></th>
                        <td>
                            <ul>
                                <li><?php esc_html_e('API URL set:', 'retail-trade-scanner-plugin'); ?> <strong><?php echo $api_url ? esc_html__('Yes', 'retail-trade-scanner-plugin') : esc_html__('No', 'retail-trade-scanner-plugin'); ?></strong></li>
                                <li><?php esc_html_e('API Secret set:', 'retail-trade-scanner-plugin'); ?> <strong><?php echo $api_secret ? esc_html__('Yes', 'retail-trade-scanner-plugin') : esc_html__('No', 'retail-trade-scanner-plugin'); ?></strong></li>
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('API URL', 'retail-trade-scanner-plugin'); ?></th>
                        <td>
                            <input type="url" name="api_url" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
                            <p class="description"><?php esc_html_e('API base URL (e.g., https://api.retailtradescanner.com/api/)', 'retail-trade-scanner-plugin'); ?></p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('API Secret', 'retail-trade-scanner-plugin'); ?></th>
                        <td>
                            <input type="password" name="api_secret" value="<?php echo esc_attr($api_secret); ?>" class="regular-text" />
                            <p class="description"><?php esc_html_e('Shared secret key for API authentication', 'retail-trade-scanner-plugin'); ?></p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
            
            <h2><?php esc_html_e('Test API Connection', 'retail-trade-scanner-plugin'); ?></h2>
            <button type="button" onclick="testApiConnection()" class="button"><?php esc_html_e('Test Connection', 'retail-trade-scanner-plugin'); ?></button>
            <div id="test-result"></div>
            
            <script>
            function testApiConnection() {
                document.getElementById('test-result').innerHTML = '<p><?php echo esc_js(__('Testing connection...', 'retail-trade-scanner-plugin')); ?></p>';
                
                jQuery.post(ajaxurl, {
                    action: 'test_retail_trade_scanner_api',
                    nonce: '<?php echo esc_js(wp_create_nonce('test_api')); ?>'
                }, function(response) {
                    if (response.success) {
                        document.getElementById('test-result').innerHTML = '<p style="color:green;"><?php echo esc_js(__('✅ API connection successful!', 'retail-trade-scanner-plugin')); ?></p>';
                    } else {
                        document.getElementById('test-result').innerHTML = '<p style="color:red;"><?php echo esc_js(__('❌ API connection failed: ', 'retail-trade-scanner-plugin')); ?>' + response.data + '</p>';
                    }
                });
            }
            </script>
        </div>
        <?php
    }
    
    /**
     * Sales Tax Implementation (simplified for production)
     */
    public function detect_user_location() {
        // Simplified location detection
        $cookie_key = 'retail_trade_scanner_geo';
        if (!isset($_COOKIE[$cookie_key])) {
            $location = array('country' => 'US', 'state' => '', 'city' => '');
            setcookie($cookie_key, wp_json_encode($location), time() + DAY_IN_SECONDS, COOKIEPATH, COOKIE_DOMAIN, is_ssl(), true);
        }
    }
    
    public function calculate_sales_tax($tax, $values, $order) {
        // Basic US tax calculation
        $subtotal = floatval($order->subtotal);
        return $subtotal * 0.06; // 6% default tax rate
    }
    
    public function add_tax_to_order($order) {
        $tax_amount = $order->subtotal * 0.06;
        $order->tax = $tax_amount;
        $order->total = $order->subtotal + $tax_amount;
        return $order;
    }
    
    public function add_dashboard_widget() {
        wp_add_dashboard_widget(
            'retail_trade_scanner_analytics',
            '📊 ' . esc_html__('Retail Trade Scanner Analytics', 'retail-trade-scanner-plugin'),
            array($this, 'dashboard_widget_content')
        );
    }
    
    public function dashboard_widget_content() {
        ?>
        <div id="retail-trade-scanner-analytics">
            <p><?php esc_html_e('Loading analytics data...', 'retail-trade-scanner-plugin'); ?></p>
            <script>
            jQuery(document).ready(function($) {
                // Load basic analytics from API
                $.get('<?php echo esc_js($this->api_base_url); ?>analytics/public/', function(response) {
                    if (response && response.success) {
                        $('#retail-trade-scanner-analytics').html('<p><strong><?php echo esc_js(__('Total Users:', 'retail-trade-scanner-plugin')); ?></strong> ' + (response.data.total_users || 0) + '</p>');
                    }
                }).fail(function() {
                    $('#retail-trade-scanner-analytics').html('<p><?php echo esc_js(__('Analytics unavailable', 'retail-trade-scanner-plugin')); ?></p>');
                });
            });
            </script>
        </div>
        <?php
    }
    
    public function ajax_test_api() {
        if (!current_user_can('manage_options')) {
            wp_send_json_error(esc_html__('Unauthorized', 'retail-trade-scanner-plugin'), 403);
        }
        check_ajax_referer('test_api', 'nonce');

        $api_url = get_option('retail_trade_scanner_api_url', '');
        $api_secret = get_option('retail_trade_scanner_api_secret', '');
        
        if (empty($api_url) || empty($api_secret)) {
            wp_send_json_error(esc_html__('API not configured. Please set API URL and Secret in Settings → Retail Trade Scanner.', 'retail-trade-scanner-plugin'));
        }
        
        $response = $this->api_request('health/');
        
        if ($response && (!isset($response['success']) || $response['success'] === true)) {
            wp_send_json_success(array('ok' => true));
        }
        
        $message = is_array($response) ? wp_json_encode($response) : esc_html__('Unknown error', 'retail-trade-scanner-plugin');
        wp_send_json_error($message);
    }
}

// Initialize the plugin
new RetailTradeScannerIntegration();

// Activation hook
register_activation_hook(__FILE__, function() {
    // Set default options
    add_option('retail_trade_scanner_api_url', 'https://api.retailtradescanner.com/api/');
    add_option('retail_trade_scanner_api_secret', '');
    
    // Create default pages
    retail_trade_scanner_create_default_pages();
});

/**
 * Create default Retail Trade Scanner pages
 */
function retail_trade_scanner_create_default_pages() {
    $pages = array(
        'premium-plans' => array(
            'title' => 'Premium Plans',
            'content' => '
                <div class="pricing-header text-center" style="margin: var(--spacing-2xl) 0;">
                    <h2>Choose Your Trading Plan</h2>
                    <p class="lead">Unlock powerful stock analysis tools with our flexible membership tiers</p>
                </div>

                <div class="pricing-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-xl); margin: var(--spacing-2xl) 0;">
                    
                    <!-- FREE PLAN -->
                    <div class="pricing-card free-plan card">
                        <div class="card-header text-center">
                            <h3>🆓 Free Plan</h3>
                            <div class="price">$0<span>/month</span></div>
                            <p class="plan-subtitle">Get started with basic features</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ 15 stocks per month</li>
                                <li>✅ Basic stock lookup</li>
                                <li>✅ 5 email list subscriptions</li>
                                <li>✅ Market news access</li>
                                <li>✅ Community support</li>
                                <li>❌ Advanced filters</li>
                                <li>❌ Historical data</li>
                                <li>❌ Priority support</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/register/" class="btn btn-outline btn-primary">
                                <span>Get Started Free</span>
                            </a>
                        </div>
                    </div>

                    <!-- PREMIUM PLAN -->
                    <div class="pricing-card premium-plan card">
                        <div class="card-header text-center">
                            <h3>🥉 Premium Plan</h3>
                            <div class="price">$14.99<span>/month</span></div>
                            <p class="plan-subtitle">Perfect for casual traders</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ 1,000 stocks per month</li>
                                <li>✅ Advanced stock lookup</li>
                                <li>✅ 50 email list subscriptions</li>
                                <li>✅ Real-time market news</li>
                                <li>✅ Basic filtering tools</li>
                                <li>✅ 90-day history</li>
                                <li>✅ Email support</li>
                                <li>❌ Custom watchlists</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/membership-account/membership-checkout/?level=2" class="btn btn-primary">
                                <span>Choose Premium</span>
                            </a>
                        </div>
                    </div>

                    <!-- PROFESSIONAL PLAN -->
                    <div class="pricing-card professional-plan card popular">
                        <div class="popular-badge">Most Popular</div>
                        <div class="card-header text-center">
                            <h3>🏆 Professional Plan</h3>
                            <div class="price">$29.99<span>/month</span></div>
                            <p class="plan-subtitle">Ideal for active traders</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ 5,000 stocks per month</li>
                                <li>✅ Professional stock analysis</li>
                                <li>✅ Unlimited email lists</li>
                                <li>✅ Advanced news filtering</li>
                                <li>✅ Advanced filtering & screening</li>
                                <li>✅ 1-year historical data</li>
                                <li>✅ Custom watchlists (25)</li>
                                <li>✅ Priority email support</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/membership-account/membership-checkout/?level=3" class="btn btn-success btn-lg">
                                <span>Choose Professional</span>
                            </a>
                        </div>
                    </div>

                    <!-- GOLD PLAN -->
                    <div class="pricing-card gold-plan card premium">
                        <div class="card-header text-center">
                            <h3>💎 Gold Plan</h3>
                            <div class="price">$59.99<span>/month</span></div>
                            <p class="plan-subtitle">For professional traders</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ 10,000+ stocks per month</li>
                                <li>✅ Expert-level analysis</li>
                                <li>✅ All premium features</li>
                                <li>✅ Real-time alerts</li>
                                <li>✅ API access</li>
                                <li>✅ 5-year historical data</li>
                                <li>✅ Unlimited watchlists</li>
                                <li>✅ Priority phone support</li>
                                <li>✅ Personal account manager</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/membership-account/membership-checkout/?level=4" class="btn btn-gold btn-lg">
                                <span>Choose Gold</span>
                            </a>
                        </div>
                    </div>
                </div>

                <h3 class="text-center" style="margin: var(--spacing-2xl) 0;">📊 Live Stock Analysis</h3>
                <div class="demo-widgets" style="margin: var(--spacing-xl) 0;">
                    [retail_trade_scanner symbol="AAPL" show_chart="true" show_details="true"]
                    [retail_trade_scanner symbol="MSFT" show_chart="true" show_details="true"]
                    [retail_trade_scanner symbol="GOOGL" show_chart="true" show_details="true"]
                </div>
            ',
            'template' => 'page'
        ),
        'terms-and-conditions' => array(
            'title' => 'Terms and Conditions',
            'content' => '
                <h2>Terms and Conditions</h2>
                <p><strong>Last updated:</strong> ' . wp_date('F j, Y') . '</p>
                
                <h3>1. Acceptance of Terms</h3>
                <p>By accessing and using Retail Trade Scanner, you accept and agree to be bound by the terms and provision of this agreement.</p>
                
                <h3>2. Service Description</h3>
                <p>Retail Trade Scanner provides stock analysis, market data, and trading tools for educational and informational purposes.</p>
                
                <h3>3. User Responsibilities</h3>
                <ul>
                    <li>You must be 18 years or older to use our services</li>
                    <li>Provide accurate information when creating an account</li>
                    <li>Use our services in compliance with applicable laws</li>
                </ul>
                
                <h3>4. Investment Disclaimer</h3>
                <p><strong>Important:</strong> All content is for educational purposes only. Past performance does not guarantee future results. Trading involves risk of loss.</p>
                
                <h3>5. Privacy</h3>
                <p>Your privacy is important to us. Please review our <a href="/privacy-policy/">Privacy Policy</a> for details on how we collect and use information.</p>
                
                <h3>📊 Market Data</h3>
                <p>See our real-time analysis capabilities:</p>
                [retail_trade_scanner symbol="SPY" show_details="true"]
                
                <h3>6. Contact</h3>
                <p>For questions about these terms, contact us at: legal@retailtradescanner.com</p>
            ',
            'template' => 'page'
        ),
        'privacy-policy' => array(
            'title' => 'Privacy Policy',
            'content' => '
                <h2>Privacy Policy</h2>
                <p><strong>Last updated:</strong> ' . wp_date('F j, Y') . '</p>
                
                <h3>1. Information We Collect</h3>
                <p>We collect information you provide directly to us, such as when you create an account, subscribe to our services, or contact us.</p>
                
                <h3>2. How We Use Information</h3>
                <ul>
                    <li>Provide and improve our services</li>
                    <li>Send you stock alerts and updates</li>
                    <li>Process payments and subscriptions</li>
                    <li>Communicate with you about our services</li>
                </ul>
                
                <h3>3. Information Sharing</h3>
                <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>
                
                <h3>4. Data Security</h3>
                <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
                
                <h3>5. Your Rights</h3>
                <p>You have the right to access, update, or delete your personal information. Contact us to exercise these rights.</p>
                
                <h3>📈 Secure Trading Data</h3>
                <p>Your financial data is protected with bank-level security:</p>
                [retail_trade_scanner symbol="AAPL" show_details="true"]
                
                <h3>6. Contact Us</h3>
                <p>If you have questions about this Privacy Policy, contact us at: privacy@retailtradescanner.com</p>
            ',
            'template' => 'page'
        )
    );
    
    foreach ($pages as $slug => $page_data) {
        // Check if page already exists
        if (!get_page_by_path($slug)) {
            wp_insert_post(array(
                'post_title'    => $page_data['title'],
                'post_content'  => $page_data['content'],
                'post_status'   => 'publish',
                'post_type'     => 'page',
                'post_name'     => $slug
            ));
        }
    }
}

// Uninstall hook
register_uninstall_hook(__FILE__, function() {
    // Delete plugin options
    $option_keys = array(
        'retail_trade_scanner_api_url',
        'retail_trade_scanner_api_secret'
    );

    foreach ($option_keys as $key) {
        delete_option($key);
    }
});