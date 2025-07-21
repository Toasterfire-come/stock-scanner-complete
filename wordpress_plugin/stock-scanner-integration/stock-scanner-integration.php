<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://github.com/Toasterfire-come/stock-scanner-complete
 * Description: Integrates WordPress with Django Stock Scanner API with paywall support
 * Version: 1.0.0
 * Author: Stock Scanner Team
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class StockScannerIntegration {
    
    private $api_base_url;
    private $api_secret;
    
    public function __construct() {
        $this->api_base_url = get_option('stock_scanner_api_url', 'https://api.yoursite.com/api/v1/');
        $this->api_secret = get_option('stock_scanner_api_secret', '');
        
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('stock_scanner', array($this, 'stock_scanner_shortcode'));
        add_action('admin_menu', array($this, 'admin_menu'));
    }
    
    public function init() {
        // Register AJAX actions
        add_action('wp_ajax_get_stock_data', array($this, 'ajax_get_stock_data'));
        add_action('wp_ajax_nopriv_get_stock_data', array($this, 'ajax_get_stock_data'));
        
        // Hook into PMP membership changes
        add_action('pmpro_after_change_membership_level', array($this, 'sync_membership_level'), 10, 2);
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('stock-scanner-js', plugin_dir_url(__FILE__) . 'assets/stock-scanner.js', array('jquery'), '1.0.0', true);
        wp_enqueue_style('stock-scanner-css', plugin_dir_url(__FILE__) . 'assets/stock-scanner.css', array(), '1.0.0');
        
        // Localize script for AJAX
        wp_localize_script('stock-scanner-js', 'stock_scanner_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ));
    }
    
    /**
     * Shortcode: [stock_scanner symbol="AAPL"]
     */
    public function stock_scanner_shortcode($atts) {
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
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $symbol = sanitize_text_field($_POST['symbol']);
        $user_id = get_current_user_id();
        
        // Check user permissions
        $user_level = $this->get_user_membership_level();
        $usage = $this->get_user_usage($user_id);
        
        if (!$this->can_user_access_stock($user_level, $usage)) {
            wp_send_json_error(array(
                'message' => 'Usage limit exceeded. Please upgrade your membership.',
                'usage' => $usage,
                'limit' => $this->get_usage_limit($user_level)
            ));
        }
        
        // Make API request
        $stock_data = $this->api_request('stocks/', array(
            'symbol' => $symbol,
            'user_id' => $user_id
        ));
        
        if ($stock_data) {
            wp_send_json_success($stock_data);
        } else {
            wp_send_json_error('Failed to fetch stock data');
        }
    }
    
    private function api_request($endpoint, $data = array()) {
        $url = $this->api_base_url . $endpoint;
        
        $args = array(
            'body' => json_encode($data),
            'headers' => array(
                'Content-Type' => 'application/json',
                'X-API-Secret' => $this->api_secret,
                'X-User-Level' => $this->get_user_membership_level(),
                'X-User-ID' => get_current_user_id()
            ),
            'timeout' => 30
        );
        
        $response = wp_remote_post($url, $args);
        
        if (is_wp_error($response)) {
            error_log('Stock Scanner API Error: ' . $response->get_error_message());
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        return json_decode($body, true);
    }
    
    private function get_user_membership_level() {
        if (!function_exists('pmpro_getMembershipLevelForUser')) {
            return 0; // Free level
        }
        
        $level = pmpro_getMembershipLevelForUser(get_current_user_id());
        return $level ? $level->id : 0;
    }
    
    private function get_user_usage($user_id) {
        $response = $this->api_request('user/usage/', array('user_id' => $user_id));
        return $response ? $response['usage'] : array('monthly' => 0, 'daily' => 0);
    }
    
    private function can_user_access_stock($user_level, $usage) {
        $limits = array(
            0 => 15,    // Free
            1 => 15,    // Free
            2 => 1000,  // Premium
            3 => 10000  // Professional
        );
        
        $limit = isset($limits[$user_level]) ? $limits[$user_level] : 15;
        return $usage['monthly'] < $limit;
    }
    
    private function get_usage_limit($user_level) {
        $limits = array(
            0 => 15,    // Free
            1 => 15,    // Free
            2 => 1000,  // Premium
            3 => 10000  // Professional
        );
        
        return isset($limits[$user_level]) ? $limits[$user_level] : 15;
    }
    
    private function render_paywall_message($user_level, $usage) {
        $limit = $this->get_usage_limit($user_level);
        
        ob_start();
        ?>
        <div class="stock-scanner-paywall">
            <div class="paywall-message">
                <h3>🚀 Upgrade to Get More Stock Data</h3>
                <p>You've used <strong><?php echo $usage['monthly']; ?></strong> out of <strong><?php echo $limit; ?></strong> stocks this month.</p>
                
                <div class="membership-options">
                    <div class="membership-tier">
                        <h4>Premium - $9.99/month</h4>
                        <p>1,000 stocks per month</p>
                        <a href="<?php echo pmpro_url('checkout', '?level=2'); ?>" class="btn btn-premium">Upgrade to Premium</a>
                    </div>
                    
                    <div class="membership-tier">
                        <h4>Professional - $29.99/month</h4>
                        <p>10,000 stocks per month</p>
                        <a href="<?php echo pmpro_url('checkout', '?level=3'); ?>" class="btn btn-professional">Upgrade to Professional</a>
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
        <div class="stock-scanner-widget" data-symbol="<?php echo esc_attr($atts['symbol']); ?>">
            <div class="stock-header">
                <h3><?php echo esc_html($atts['symbol']); ?></h3>
                <button class="refresh-btn" onclick="stockScanner.refreshStock('<?php echo esc_attr($atts['symbol']); ?>')">
                    Refresh
                </button>
            </div>
            
            <div class="stock-data">
                <div class="loading">Loading stock data...</div>
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
                    <label>Volume:</label>
                    <span class="volume"></span>
                </div>
                <div class="detail-item">
                    <label>Market Cap:</label>
                    <span class="market-cap"></span>
                </div>
            </div>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function sync_membership_level($level_id, $user_id) {
        // Sync membership level change with Django
        $this->api_request('user/membership/', array(
            'user_id' => $user_id,
            'level_id' => $level_id,
            'action' => 'level_change'
        ));
    }
    
    public function admin_menu() {
        add_options_page(
            'Stock Scanner Settings',
            'Stock Scanner',
            'manage_options',
            'stock-scanner-settings',
            array($this, 'admin_page')
        );
    }
    
    public function admin_page() {
        if (isset($_POST['submit'])) {
            update_option('stock_scanner_api_url', sanitize_url($_POST['api_url']));
            update_option('stock_scanner_api_secret', sanitize_text_field($_POST['api_secret']));
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        
        $api_url = get_option('stock_scanner_api_url', '');
        $api_secret = get_option('stock_scanner_api_secret', '');
        ?>
        <div class="wrap">
            <h1>Stock Scanner Settings</h1>
            <form method="post">
                <table class="form-table">
                    <tr>
                        <th scope="row">API URL</th>
                        <td>
                            <input type="url" name="api_url" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
                            <p class="description">Django API base URL (e.g., https://api.yoursite.com/api/v1/)</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">API Secret</th>
                        <td>
                            <input type="password" name="api_secret" value="<?php echo esc_attr($api_secret); ?>" class="regular-text" />
                            <p class="description">Shared secret key for API authentication</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
            
            <h2>Test API Connection</h2>
            <button type="button" onclick="testApiConnection()" class="button">Test Connection</button>
            <div id="test-result"></div>
            
            <script>
            function testApiConnection() {
                // Add API test functionality
                document.getElementById('test-result').innerHTML = '<p>Testing connection...</p>';
                
                jQuery.post(ajaxurl, {
                    action: 'test_stock_scanner_api',
                    nonce: '<?php echo wp_create_nonce('test_api'); ?>'
                }, function(response) {
                    if (response.success) {
                        document.getElementById('test-result').innerHTML = '<p style="color:green;">✅ API connection successful!</p>';
                    } else {
                        document.getElementById('test-result').innerHTML = '<p style="color:red;">❌ API connection failed: ' + response.data + '</p>';
                    }
                });
            }
            </script>
        </div>
        <?php
    }
}

// Initialize the plugin
new StockScannerIntegration();

// Activation hook
register_activation_hook(__FILE__, function() {
    // Set default options
    add_option('stock_scanner_api_url', 'https://api.yoursite.com/api/v1/');
    add_option('stock_scanner_api_secret', '');
});
?>