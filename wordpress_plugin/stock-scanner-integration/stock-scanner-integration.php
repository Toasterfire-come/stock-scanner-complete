<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://github.com/Toasterfire-come/stock-scanner-complete
 * Description: Creates 19 pages from XML export with live stock widgets, membership paywall, and seamless Django API integration
 * Version: 2.0.0
 * Author: Stock Scanner Team
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * PLUGIN FUNCTIONALITY OVERVIEW
 * 
 * This plugin automatically creates 19 pages based on the WordPress XML export:
 * 
 * MAIN TRADING PAGES:
 * - Premium Plans (/premium-plans/) - Gold/Silver/Free comparison with live widgets
 * - Email Stock Lists (/email-stock-lists/) - Subscribe to alert lists
 * - All Stock Alerts (/all-stock-lists/) - Complete stock list collection
 * - Popular Stock Lists (/popular-stock-lists/) - Most subscribed lists
 * - Stock Search (/stock-search/) - Advanced search tools
 * - Personalized Stock Finder (/personalized-stock-finder/) - AI recommendations
 * - News Scrapper (/news-scrapper/) - Financial news aggregation
 * - Filter and Scrapper Pages (/filter-and-scrapper-pages/) - Advanced filtering
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
 * - Responsive design matching XML formatting
 * - Membership paywall integration
 * - Complete navigation menu
 * - Django API integration
 */

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
        'premium-plans' => array(
            'title' => 'Premium Plans',
            'content' => '
                <h3>Gold Plan</h3>
                <p>Our gold scanner plan will perfectly highlight your trading style and bring you to success. With unlimited access to our over 40 email lists, in-depth stock look up, and personalized stock search, you will stay informed and in the action. If you are interested in elevating your positions, check out if our gold plan is right for you.</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/membership-account/membership-checkout/?level=3" class="wp-block-button__link wp-element-button" style="background: #f39c12; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;">Buy Gold Plan</a>
                </div>
                
                <h4>Silver Plan</h4>
                <p>Upon purchase of the silver scanner plan, you will receive access to unlimited access of our most popular email lists, stock lookup, and limited access to personalized stock search. With access to our tools you will receive an edge on the market at a practical price. If you are excited to further improve your trading, check out the silver plan.</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/membership-account/membership-checkout/?level=2" class="wp-block-button__link wp-element-button" style="background: #95a5a6; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;">Buy Silver Plan</a>
                </div>
                
                <h3>📊 Live Stock Analysis</h3>
                [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                
                <table class="comparison-table" style="width: 100%; border-collapse: collapse; margin: 40px 0;">
                    <tr><th></th><th>Gold Plan</th><th>Silver Plan</th><th>Free Plan</th></tr>
                    <tr><td>All Email Lists</td><td style="text-align: center;">✔</td><td style="text-align: center;"></td><td style="text-align: center;"></td></tr>
                    <tr><td>Popular Email Lists</td><td style="text-align: center;">✔</td><td style="text-align: center;">✔</td><td style="text-align: center;"></td></tr>
                    <tr><td>Detailed Stock Lookup</td><td style="text-align: center;">✔</td><td style="text-align: center;"></td><td style="text-align: center;"></td></tr>
                    <tr><td>Stock Lookup</td><td style="text-align: center;">✔</td><td style="text-align: center;">✔</td><td style="text-align: center;"></td></tr>
                    <tr><td>Personalized Stock Search</td><td style="text-align: center;">✔</td><td style="text-align: center;">✔</td><td style="text-align: center;">✔</td></tr>
                    <tr><td>Discounted Prepaid Package</td><td style="text-align: center;">30% Discount</td><td style="text-align: center;">10% Discount</td><td style="text-align: center;"></td></tr>
                </table>
            ',
            'template' => 'page'
        ),
        'email-stock-lists' => array(
            'title' => 'Email Stock Lists',
            'content' => '
                <p>Our email stock lists will keep you informed and up to date on the changing market. Look below for all of our stock lists, chose your favorites and subscribe.</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/popular-stock-lists/" style="margin: 10px; padding: 12px 24px; border: 2px solid #007cba; color: #007cba; text-decoration: none; border-radius: 5px;">Popular Stock Lists</a>
                    <a href="/all-stock-lists/" style="margin: 10px; padding: 12px 24px; border: 2px solid #007cba; color: #007cba; text-decoration: none; border-radius: 5px;">All Stock Lists</a>
                </div>
                
                <h3>📈 Featured Stocks</h3>
                [stock_scanner symbol="TSLA" show_details="true"]
                [stock_scanner symbol="NVDA" show_details="true"]
                
                <h5><strong>Frequently asked questions</strong></h5>
                
                <details>
                    <summary>Why am I not able to access all of the stock lists?</summary>
                    <p>If you are subscribed to the silver plan, then you will be unable to access the complete stock list until you upgrade your plan.</p>
                </details>
                
                <details>
                    <summary>Will subscribing to a list spam my email?</summary>
                    <p>Our lists will only send you a email when a new stock passes, so depending on the list the volume of stocks that pass each thresh hold might be different, if quantity of emails is your concern then be careful when subscribing to a list.</p>
                </details>
                
                <details>
                    <summary>How quickly will I be informed by this list?</summary>
                    <p>Our services scan every three minutes to keep subscribers informed.</p>
                </details>
            ',
            'template' => 'page'
        ),
        'all-stock-lists' => array(
            'title' => 'All Stock Alerts',
            'content' => '
                <h2>Complete Stock Alert Lists</h2>
                <p>Access our comprehensive collection of stock alert lists. Monitor market movements with precision and never miss a trading opportunity.</p>
                
                <h3>🔥 Top Performers</h3>
                [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                [stock_scanner symbol="GOOGL" show_chart="true" show_details="true"]
                [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                
                <h3>📊 Market Movers</h3>
                [stock_scanner symbol="TSLA" show_details="true"]
                [stock_scanner symbol="NVDA" show_details="true"]
                [stock_scanner symbol="AMD" show_details="true"]
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 30px 0;">
                    <h4>🚀 Upgrade for Full Access</h4>
                    <p>Get unlimited access to all stock lists with our premium plans!</p>
                    <a href="/premium-plans/" style="background: rgba(255,255,255,0.2); color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold;">View Premium Plans</a>
                </div>
            ',
            'template' => 'page'
        ),
        'popular-stock-lists' => array(
            'title' => 'Popular Stock Lists',
            'content' => '
                <h2>Most Popular Stock Lists</h2>
                <p>These are our most subscribed and highest performing stock alert lists. Perfect for traders who want the best market insights.</p>
                
                <h3>🎯 Technology Leaders</h3>
                [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                [stock_scanner symbol="GOOGL" show_chart="true" show_details="true"]
                
                <h3>⚡ High Growth Stocks</h3>
                [stock_scanner symbol="TSLA" show_details="true"]
                [stock_scanner symbol="NVDA" show_details="true"]
                [stock_scanner symbol="META" show_details="true"]
                
                <h3>💎 Market Favorites</h3>
                [stock_scanner symbol="AMZN" show_details="true"]
                [stock_scanner symbol="NFLX" show_details="true"]
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="/email-stock-lists/" style="background: #007cba; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;">Browse All Lists</a>
                </p>
            ',
            'template' => 'page'
        ),
        'stock-search' => array(
            'title' => 'Stock Search',
            'content' => '
                <h2>Advanced Stock Search</h2>
                <p>Use our powerful search tools to find the perfect stocks for your portfolio. Filter by sector, performance, market cap, and more.</p>
                
                <h3>🔍 Quick Search Examples</h3>
                [stock_scanner symbol="SPY" show_chart="true" show_details="true"]
                [stock_scanner symbol="QQQ" show_chart="true" show_details="true"]
                
                <h3>📈 Trending Searches</h3>
                [stock_scanner symbol="AAPL" show_details="true"]
                [stock_scanner symbol="TSLA" show_details="true"]
                [stock_scanner symbol="NVDA" show_details="true"]
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>🎯 Pro Search Features</h4>
                    <ul>
                        <li>Advanced filtering options</li>
                        <li>Technical indicator screening</li>
                        <li>Custom alerts setup</li>
                        <li>Portfolio integration</li>
                    </ul>
                    <p><a href="/premium-plans/">Upgrade to unlock advanced search features</a></p>
                </div>
            ',
            'template' => 'page'
        ),
        'personalized-stock-finder' => array(
            'title' => 'Personalized Stock Finder',
            'content' => '
                <h2>Your Personalized Stock Finder</h2>
                <p>Get customized stock recommendations based on your trading style, risk tolerance, and investment goals.</p>
                
                <h3>🎯 Recommended for You</h3>
                [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                
                <h3>💡 Smart Suggestions</h3>
                [stock_scanner symbol="GOOGL" show_details="true"]
                [stock_scanner symbol="AMZN" show_details="true"]
                
                <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white; padding: 25px; border-radius: 10px; margin: 30px 0;">
                    <h4>🚀 Get Personalized Recommendations</h4>
                    <p>Our AI analyzes your preferences and market conditions to suggest the best stocks for your portfolio.</p>
                    <a href="/premium-plans/" style="background: rgba(255,255,255,0.2); color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold;">Start Your Analysis</a>
                </div>
            ',
            'template' => 'page'
        ),
        'terms-and-conditions' => array(
            'title' => 'Terms and Conditions',
            'content' => '
                <h2>Terms and Conditions</h2>
                <p><strong>Last updated:</strong> January 21, 2025</p>
                
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
                [stock_scanner symbol="SPY" show_details="true"]
                
                <h3>6. Contact</h3>
                <p>For questions about these terms, contact us at: legal@retailtradescanner.com</p>
            ',
            'template' => 'page'
        ),
        'privacy-policy' => array(
            'title' => 'Privacy Policy',
            'content' => '
                <h2>Privacy Policy</h2>
                <p><strong>Last updated:</strong> January 21, 2025</p>
                
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
                [stock_scanner symbol="AAPL" show_details="true"]
                
                <h3>6. Contact Us</h3>
                <p>If you have questions about this Privacy Policy, contact us at: privacy@retailtradescanner.com</p>
            ',
            'template' => 'page'
        ),
        'news-scrapper' => array(
            'title' => 'News Scrapper',
            'content' => '
                <h2>Financial News Scraper</h2>
                <p>Stay updated with the latest financial news and market analysis from multiple sources, all in one place.</p>
                
                <h3>📰 Latest Market News</h3>
                [stock_scanner symbol="SPY" show_chart="true" show_details="true"]
                [stock_scanner symbol="QQQ" show_chart="true" show_details="true"]
                
                <h3>🔥 Trending Stories</h3>
                [stock_scanner symbol="AAPL" show_details="true"]
                [stock_scanner symbol="TSLA" show_details="true"]
                [stock_scanner symbol="NVDA" show_details="true"]
                
                <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60;">
                    <h4>📊 Real-Time Updates</h4>
                    <p>Our news scraper monitors hundreds of financial news sources to bring you the most relevant and timely information.</p>
                </div>
                
                <h3>💡 News Categories</h3>
                <ul>
                    <li>📈 Market Analysis</li>
                    <li>💼 Company Earnings</li>
                    <li>🏦 Economic Indicators</li>
                    <li>🌍 Global Markets</li>
                    <li>⚡ Breaking News</li>
                </ul>
            ',
            'template' => 'page'
        ),
        'filter-and-scrapper-pages' => array(
            'title' => 'Filter and Scrapper Pages',
            'content' => '
                <h2>Advanced Filtering & Data Scraping</h2>
                <p>Use our powerful filtering tools and data scrapers to find exactly what you\'re looking for in the markets.</p>
                
                <h3>🔍 Smart Filters</h3>
                [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                
                <h3>📊 Data Scraping Tools</h3>
                [stock_scanner symbol="GOOGL" show_details="true"]
                [stock_scanner symbol="AMZN" show_details="true"]
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h4>📈 Technical Filters</h4>
                        <ul>
                            <li>Price movements</li>
                            <li>Volume analysis</li>
                            <li>RSI indicators</li>
                            <li>Moving averages</li>
                        </ul>
                    </div>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h4>💰 Fundamental Filters</h4>
                        <ul>
                            <li>P/E ratios</li>
                            <li>Market cap</li>
                            <li>Dividend yield</li>
                            <li>Revenue growth</li>
                        </ul>
                    </div>
                </div>
                
                <p style="text-align: center;">
                    <a href="/premium-plans/" style="background: #007cba; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;">Access Advanced Tools</a>
                </p>
            ',
            'template' => 'page'
        ),
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
        ),
        'membership-account' => array(
            'title' => 'Membership Account',
            'content' => '
                <h2>Your Membership Account</h2>
                <p>Manage your subscription, view usage statistics, and update your account settings.</p>
                
                <h3>📊 Account Overview</h3>
                [stock_scanner symbol="AAPL" show_details="true"]
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>Current Plan</h4>
                    <p>Your current membership level and benefits will be displayed here.</p>
                </div>
            ',
            'template' => 'page'
        ),
        'membership-billing' => array(
            'title' => 'Membership Billing',
            'content' => '
                <h2>Billing Information</h2>
                <p>View your billing history and manage payment methods.</p>
                
                <h3>💳 Payment Methods</h3>
                [stock_scanner symbol="MSFT" show_details="true"]
            ',
            'template' => 'page'
        ),
        'membership-cancel' => array(
            'title' => 'Membership Cancel',
            'content' => '
                <h2>Cancel Membership</h2>
                <p>We\'re sorry to see you go. Cancel your membership here.</p>
                
                <h3>📉 Before You Go</h3>
                [stock_scanner symbol="TSLA" show_details="true"]
            ',
            'template' => 'page'
        ),
        'membership-checkout' => array(
            'title' => 'Membership Checkout',
            'content' => '
                <h2>Membership Checkout</h2>
                <p>Complete your subscription purchase.</p>
                
                <h3>🛒 Checkout Process</h3>
                [stock_scanner symbol="GOOGL" show_details="true"]
            ',
            'template' => 'page'
        ),
        'membership-confirmation' => array(
            'title' => 'Membership Confirmation',
            'content' => '
                <h2>Membership Confirmation</h2>
                <p>Thank you for your purchase! Your membership is now active.</p>
                
                <h3>🎉 Welcome</h3>
                [stock_scanner symbol="NVDA" show_details="true"]
            ',
            'template' => 'page'
        ),
        'membership-orders' => array(
            'title' => 'Membership Orders',
            'content' => '
                <h2>Your Orders</h2>
                <p>View your order history and transaction details.</p>
                
                <h3>📦 Order History</h3>
                [stock_scanner symbol="AMZN" show_details="true"]
            ',
            'template' => 'page'
        ),
        'membership-levels' => array(
            'title' => 'Membership Levels',
            'content' => '
                <h2>Membership Levels</h2>
                <p>Compare our membership tiers and find the perfect plan for you.</p>
                
                <h3>🏆 Available Plans</h3>
                [stock_scanner symbol="SPY" show_details="true"]
                
                <p><a href="/premium-plans/">View detailed pricing</a></p>
            ',
            'template' => 'page'
        ),
        'login' => array(
            'title' => 'Log In',
            'content' => '
                <h2>Member Login</h2>
                <p>Sign in to access your account and premium features.</p>
                
                <h3>🔐 Secure Access</h3>
                [stock_scanner symbol="AAPL" show_details="true"]
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><a href="/wp-login.php">WordPress Login</a></p>
                </div>
            ',
            'template' => 'page'
        ),
        'your-profile' => array(
            'title' => 'Your Profile',
            'content' => '
                <h2>User Profile</h2>
                <p>Manage your personal information and preferences.</p>
                
                <h3>👤 Profile Settings</h3>
                [stock_scanner symbol="MSFT" show_details="true"]
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
            array('title' => 'Premium Plans', 'url' => '/premium-plans/'),
            array('title' => 'Email Lists', 'url' => '/email-stock-lists/'),
            array('title' => 'Stock Search', 'url' => '/stock-search/'),
            array('title' => 'Popular Lists', 'url' => '/popular-stock-lists/'),
            array('title' => 'All Lists', 'url' => '/all-stock-lists/'),
            array('title' => 'News Scraper', 'url' => '/news-scrapper/'),
            array('title' => 'My Account', 'url' => '/membership-account/'),
            array('title' => 'Login', 'url' => '/login/')
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