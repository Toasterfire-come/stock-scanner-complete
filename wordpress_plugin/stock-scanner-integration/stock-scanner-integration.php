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
    
    // Create default pages
    create_stock_scanner_pages();
});

/**
 * Create default Stock Scanner pages
 */
function create_stock_scanner_pages() {
    $pages = array(
        'stock-dashboard' => array(
            'title' => 'Stock Dashboard',
            'content' => '
                <h2>📈 Real-Time Stock Dashboard</h2>
                <p>Monitor your favorite stocks with live data and charts.</p>
                
                <div class="stock-grid">
                    <div class="stock-row">
                        <h3>🏢 Technology Stocks</h3>
                        [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                        [stock_scanner symbol="GOOGL" show_chart="true" show_details="true"]
                        [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                        [stock_scanner symbol="TSLA" show_chart="true" show_details="true"]
                    </div>
                    
                    <div class="stock-row">
                        <h3>💰 Financial Stocks</h3>
                        [stock_scanner symbol="JPM" show_chart="true" show_details="true"]
                        [stock_scanner symbol="BAC" show_chart="true" show_details="true"]
                        [stock_scanner symbol="WFC" show_chart="true" show_details="true"]
                    </div>
                    
                    <div class="stock-row">
                        <h3>🛒 Consumer Stocks</h3>
                        [stock_scanner symbol="AMZN" show_chart="true" show_details="true"]
                        [stock_scanner symbol="WMT" show_chart="true" show_details="true"]
                        [stock_scanner symbol="HD" show_chart="true" show_details="true"]
                    </div>
                </div>
                
                <style>
                .stock-grid { max-width: 1200px; margin: 0 auto; }
                .stock-row { margin-bottom: 40px; }
                .stock-row h3 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                </style>
            ',
            'template' => 'page'
        ),
        'stock-watchlist' => array(
            'title' => 'My Stock Watchlist',
            'content' => '
                <h2>📋 Your Personal Stock Watchlist</h2>
                <p>Track your most important stocks in one place.</p>
                
                <div class="watchlist-container">
                    <h3>🎯 Top Picks</h3>
                    [stock_scanner symbol="AAPL" show_details="true"]
                    [stock_scanner symbol="NVDA" show_details="true"]
                    [stock_scanner symbol="AMD" show_details="true"]
                    
                    <h3>💎 Growth Stocks</h3>
                    [stock_scanner symbol="TSLA" show_details="true"]
                    [stock_scanner symbol="NFLX" show_details="true"]
                    [stock_scanner symbol="SHOP" show_details="true"]
                    
                    <h3>🏦 Dividend Stocks</h3>
                    [stock_scanner symbol="JNJ" show_details="true"]
                    [stock_scanner symbol="PG" show_details="true"]
                    [stock_scanner symbol="KO" show_details="true"]
                </div>
                
                <div class="upgrade-notice">
                    <h4>🚀 Want to track more stocks?</h4>
                    <p>Upgrade to Premium for 1,000 stocks per month or Professional for 10,000 stocks per month!</p>
                    <a href="/membership-account/membership-checkout/?level=2" class="button-premium">Upgrade to Premium</a>
                </div>
            ',
            'template' => 'page'
        ),
        'stock-market-news' => array(
            'title' => 'Stock Market News',
            'content' => '
                <h2>📰 Latest Stock Market News</h2>
                <p>Stay updated with the latest market movements and stock analysis.</p>
                
                <div class="news-stocks">
                    <h3>📈 Trending Stocks Today</h3>
                    [stock_scanner symbol="SPY" show_chart="true" show_details="true"]
                    [stock_scanner symbol="QQQ" show_chart="true" show_details="true"]
                    [stock_scanner symbol="DIA" show_chart="true" show_details="true"]
                </div>
                
                <div class="market-movers">
                    <h3>🚀 Market Movers</h3>
                    <p>Check out these stocks making headlines:</p>
                    [stock_scanner symbol="TSLA"]
                    [stock_scanner symbol="NVDA"]
                    [stock_scanner symbol="META"]
                    [stock_scanner symbol="GOOGL"]
                </div>
                
                <div class="market-analysis">
                    <h3>📊 Market Analysis</h3>
                    <p>Get insights into market trends with our real-time data.</p>
                    [stock_scanner symbol="VTI" show_chart="true"]
                    [stock_scanner symbol="VXUS" show_chart="true"]
                </div>
            ',
            'template' => 'page'
        ),
        'membership-plans' => array(
            'title' => 'Membership Plans',
            'content' => '
                <h2>🎯 Choose Your Stock Scanner Plan</h2>
                <p>Get the perfect plan for your stock tracking needs.</p>
                
                <div class="pricing-table">
                    <div class="pricing-plan free">
                        <h3>🆓 Free</h3>
                        <div class="price">$0<span>/month</span></div>
                        <ul>
                            <li>✅ 15 stocks per month</li>
                            <li>✅ Real-time data</li>
                            <li>✅ Basic charts</li>
                            <li>✅ Email alerts</li>
                        </ul>
                        <a href="/register/" class="button-free">Get Started</a>
                    </div>
                    
                    <div class="pricing-plan premium">
                        <h3>⭐ Premium</h3>
                        <div class="price">$9.99<span>/month</span></div>
                        <ul>
                            <li>✅ 1,000 stocks per month</li>
                            <li>✅ Advanced charts</li>
                            <li>✅ Historical data</li>
                            <li>✅ Priority support</li>
                            <li>✅ Custom watchlists</li>
                        </ul>
                        <a href="/membership-account/membership-checkout/?level=2" class="button-premium">Upgrade Now</a>
                    </div>
                    
                    <div class="pricing-plan professional">
                        <h3>💼 Professional</h3>
                        <div class="price">$29.99<span>/month</span></div>
                        <ul>
                            <li>✅ 10,000 stocks per month</li>
                            <li>✅ API access</li>
                            <li>✅ Custom indicators</li>
                            <li>✅ Portfolio tracking</li>
                            <li>✅ White-label options</li>
                        </ul>
                        <a href="/membership-account/membership-checkout/?level=3" class="button-professional">Go Pro</a>
                    </div>
                </div>
                
                <style>
                .pricing-table { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin: 30px 0; }
                .pricing-plan { border: 2px solid #e1e5e9; border-radius: 10px; padding: 30px; text-align: center; }
                .pricing-plan.premium { border-color: #f39c12; transform: scale(1.05); }
                .pricing-plan h3 { font-size: 1.8rem; margin-bottom: 15px; }
                .price { font-size: 2.5rem; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }
                .price span { font-size: 1rem; color: #7f8c8d; }
                .pricing-plan ul { list-style: none; padding: 0; margin: 20px 0; }
                .pricing-plan li { padding: 8px 0; }
                .button-free, .button-premium, .button-professional { 
                    display: inline-block; padding: 15px 30px; border-radius: 5px; 
                    text-decoration: none; font-weight: bold; margin-top: 20px; 
                }
                .button-free { background: #95a5a6; color: white; }
                .button-premium { background: #f39c12; color: white; }
                .button-professional { background: #9b59b6; color: white; }
                </style>
            ',
            'template' => 'page'
        ),
        'stock-alerts' => array(
            'title' => 'Stock Alerts',
            'content' => '
                <h2>🔔 Stock Price Alerts</h2>
                <p>Get notified when your stocks hit target prices.</p>
                
                <div class="alert-setup">
                    <h3>📧 Email Alert Examples</h3>
                    <p>Here are some stocks you might want to set alerts for:</p>
                    
                    [stock_scanner symbol="AAPL" show_details="true"]
                    <p><em>Set an alert when Apple reaches $200 or drops below $150</em></p>
                    
                    [stock_scanner symbol="TSLA" show_details="true"]
                    <p><em>Get notified when Tesla moves more than 5% in a day</em></p>
                    
                    [stock_scanner symbol="NVDA" show_details="true"]
                    <p><em>Alert me when NVIDIA hits a new all-time high</em></p>
                </div>
                
                <div class="alert-premium">
                    <h3>⚡ Premium Alert Features</h3>
                    <ul>
                        <li>📱 SMS alerts</li>
                        <li>📊 Technical indicator alerts</li>
                        <li>🎯 Multiple price targets</li>
                        <li>📈 Volume spike alerts</li>
                        <li>🔄 Recurring alerts</li>
                    </ul>
                    <a href="/membership-account/membership-checkout/?level=2" class="upgrade-button">Upgrade for Premium Alerts</a>
                </div>
            ',
            'template' => 'page'
        )
    );
    
    foreach ($pages as $slug => $page_data) {
        // Check if page already exists
        $existing_page = get_page_by_path($slug);
        if (!$existing_page) {
            $page_id = wp_insert_post(array(
                'post_title'   => $page_data['title'],
                'post_content' => $page_data['content'],
                'post_status'  => 'publish',
                'post_type'    => 'page',
                'post_name'    => $slug
            ));
            
            if ($page_id) {
                // Add to menu if it's the main dashboard
                if ($slug === 'stock-dashboard') {
                    update_option('stock_scanner_dashboard_page_id', $page_id);
                }
            }
        }
    }
    
    // Create a simple navigation menu
    $menu_name = 'Stock Scanner Menu';
    $menu_exists = wp_get_nav_menu_object($menu_name);
    
    if (!$menu_exists) {
        $menu_id = wp_create_nav_menu($menu_name);
        
        // Add menu items
        $menu_items = array(
            array('title' => 'Dashboard', 'url' => '/stock-dashboard/'),
            array('title' => 'Watchlist', 'url' => '/stock-watchlist/'),
            array('title' => 'Market News', 'url' => '/stock-market-news/'),
            array('title' => 'Alerts', 'url' => '/stock-alerts/'),
            array('title' => 'Pricing', 'url' => '/membership-plans/')
        );
        
        foreach ($menu_items as $item) {
            wp_update_nav_menu_item($menu_id, 0, array(
                'menu-item-title' => $item['title'],
                'menu-item-url' => home_url($item['url']),
                'menu-item-status' => 'publish'
            ));
        }
    }
}
?>