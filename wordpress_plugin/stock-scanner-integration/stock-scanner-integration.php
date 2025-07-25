<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Plugin URI: https://retailtradescanner.com
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

// Include required files
require_once plugin_dir_path(__FILE__) . 'includes/usage-tracker.php';
require_once plugin_dir_path(__FILE__) . 'includes/api-interceptor.php';

class StockScannerIntegration {
    
    private $api_base_url;
    private $api_secret;
    private $usage_tracker;
    
    public function __construct() {
        $this->api_base_url = get_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        $this->api_secret = get_option('stock_scanner_api_secret', '');
        
        // Initialize usage tracker
        global $stock_scanner_usage_tracker;
        $this->usage_tracker = $stock_scanner_usage_tracker;
        
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('stock_scanner', array($this, 'stock_scanner_shortcode'));
        add_action('admin_menu', array($this, 'admin_menu'));
        add_action('wp_dashboard_setup', array($this, 'add_dashboard_widget'));
        
        // Professional page enhancement
        add_filter('the_content', array($this, 'enhance_page_content'));
        add_action('wp_head', array($this, 'add_professional_meta_tags'));
        
        // Usage tracking hooks
        add_action('wp_ajax_track_usage', array($this, 'track_user_usage'));
        add_action('wp_ajax_nopriv_track_usage', array($this, 'track_user_usage'));
        
        // Sales tax hooks
        add_filter('pmpro_tax', array($this, 'calculate_sales_tax'), 10, 3);
        add_action('pmpro_checkout_preheader', array($this, 'detect_user_location'));
        add_filter('pmpro_checkout_order', array($this, 'add_tax_to_order'), 10, 1);
        
        // Resource monitoring hooks
        add_action('wp_ajax_check_system_status', array($this, 'check_system_status'));
        add_action('wp_ajax_nopriv_check_system_status', array($this, 'check_system_status'));
    }
    
    public function init() {
        // Register AJAX actions
        add_action('wp_ajax_get_stock_data', array($this, 'ajax_get_stock_data'));
        add_action('wp_ajax_nopriv_get_stock_data', array($this, 'ajax_get_stock_data'));
        
        // Hook into PMP membership changes
        add_action('pmpro_after_change_membership_level', array($this, 'sync_membership_level'), 10, 2);
        
        // Create professional pages if they don't exist
        $this->create_professional_pages();
        
        // Register professional shortcodes
        $this->register_professional_shortcodes();
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('stock-scanner-js', plugin_dir_url(__FILE__) . 'assets/stock-scanner.js', array('jquery'), '2.0.0', true);
        wp_enqueue_style('stock-scanner-css', plugin_dir_url(__FILE__) . 'assets/stock-scanner.css', array(), '2.0.0');
        
        // Font Awesome for icons
        wp_enqueue_style('font-awesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css', array(), '6.0.0');
        
        // Professional styles for different membership levels
        $user_level = $this->get_user_membership_level();
        wp_enqueue_style('stock-scanner-level-' . $user_level, plugin_dir_url(__FILE__) . 'assets/level-' . $user_level . '.css', array('stock-scanner-css'), '2.0.0');
        
        // Localize script for AJAX with enhanced data
        wp_localize_script('stock-scanner-js', 'stock_scanner_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
            'user_level' => $user_level,
            'api_base' => $this->api_base_url,
            'features' => $this->get_available_features($user_level),
            'limits' => $this->get_user_limits($user_level),
            'system_status_url' => admin_url('admin-ajax.php?action=check_system_status'),
            'messages' => array(
                'upgrade_required' => 'This feature requires a higher membership level.',
                'limit_exceeded' => 'You have reached your daily limit.',
                'system_overload' => 'System is currently overloaded. Please try again later.',
                'loading' => 'Loading...',
                'error' => 'An error occurred. Please try again.',
                'retry' => 'Retry'
            )
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
    
    /**
     * Sales Tax Implementation
     */
    
    /**
     * Detect user location for tax calculation
     */
    public function detect_user_location() {
        if (!session_id()) {
            session_start();
        }
        
        // Try to get location from IP if not already detected
        if (!isset($_SESSION['user_state']) || !isset($_SESSION['user_country'])) {
            $location = $this->get_location_from_ip();
            $_SESSION['user_state'] = $location['state'];
            $_SESSION['user_country'] = $location['country'];
            $_SESSION['user_city'] = $location['city'];
        }
    }
    
    /**
     * Get location from IP address
     */
    private function get_location_from_ip() {
        $ip = $this->get_user_ip();
        
        // Use ipapi.co for free IP geolocation
        $response = wp_remote_get("http://ipapi.co/{$ip}/json/");
        
        if (!is_wp_error($response)) {
            $data = json_decode(wp_remote_retrieve_body($response), true);
            
            return array(
                'country' => isset($data['country_code']) ? $data['country_code'] : 'US',
                'state' => isset($data['region_code']) ? $data['region_code'] : '',
                'city' => isset($data['city']) ? $data['city'] : ''
            );
        }
        
        // Default to US if detection fails
        return array(
            'country' => 'US',
            'state' => '',
            'city' => ''
        );
    }
    
    /**
     * Get user's IP address
     */
    private function get_user_ip() {
        if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
            return $_SERVER['HTTP_CLIENT_IP'];
        } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            return $_SERVER['HTTP_X_FORWARDED_FOR'];
        } elseif (!empty($_SERVER['REMOTE_ADDR'])) {
            return $_SERVER['REMOTE_ADDR'];
        }
        return '127.0.0.1';
    }
    
    /**
     * Calculate sales tax based on location
     */
    public function calculate_sales_tax($tax, $values, $order) {
        if (!session_id()) {
            session_start();
        }
        
        $country = isset($_SESSION['user_country']) ? $_SESSION['user_country'] : 'US';
        $state = isset($_SESSION['user_state']) ? $_SESSION['user_state'] : '';
        
        // Only calculate tax for US customers
        if ($country !== 'US') {
            return 0;
        }
        
        $subtotal = floatval($order->subtotal);
        $tax_rate = $this->get_tax_rate_for_state($state);
        
        return $subtotal * ($tax_rate / 100);
    }
    
    /**
     * Get tax rate for US states (2024 rates)
     */
    private function get_tax_rate_for_state($state) {
        $tax_rates = array(
            'AL' => 4.00,  // Alabama
            'AK' => 0.00,  // Alaska
            'AZ' => 5.60,  // Arizona
            'AR' => 6.50,  // Arkansas
            'CA' => 7.25,  // California
            'CO' => 2.90,  // Colorado
            'CT' => 6.35,  // Connecticut
            'DE' => 0.00,  // Delaware
            'FL' => 6.00,  // Florida
            'GA' => 4.00,  // Georgia
            'HI' => 4.00,  // Hawaii
            'ID' => 6.00,  // Idaho
            'IL' => 6.25,  // Illinois
            'IN' => 7.00,  // Indiana
            'IA' => 6.00,  // Iowa
            'KS' => 6.50,  // Kansas
            'KY' => 6.00,  // Kentucky
            'LA' => 4.45,  // Louisiana
            'ME' => 5.50,  // Maine
            'MD' => 6.00,  // Maryland
            'MA' => 6.25,  // Massachusetts
            'MI' => 6.00,  // Michigan
            'MN' => 6.875, // Minnesota
            'MS' => 7.00,  // Mississippi
            'MO' => 4.225, // Missouri
            'MT' => 0.00,  // Montana
            'NE' => 5.50,  // Nebraska
            'NV' => 6.85,  // Nevada
            'NH' => 0.00,  // New Hampshire
            'NJ' => 6.625, // New Jersey
            'NM' => 5.125, // New Mexico
            'NY' => 8.00,  // New York
            'NC' => 4.75,  // North Carolina
            'ND' => 5.00,  // North Dakota
            'OH' => 5.75,  // Ohio
            'OK' => 4.50,  // Oklahoma
            'OR' => 0.00,  // Oregon
            'PA' => 6.00,  // Pennsylvania
            'RI' => 7.00,  // Rhode Island
            'SC' => 6.00,  // South Carolina
            'SD' => 4.50,  // South Dakota
            'TN' => 7.00,  // Tennessee
            'TX' => 6.25,  // Texas
            'UT' => 5.95,  // Utah
            'VT' => 6.00,  // Vermont
            'VA' => 5.30,  // Virginia
            'WA' => 6.50,  // Washington
            'WV' => 6.00,  // West Virginia
            'WI' => 5.00,  // Wisconsin
            'WY' => 4.00,  // Wyoming
            'DC' => 6.00   // District of Columbia
        );
        
        return isset($tax_rates[$state]) ? $tax_rates[$state] : 6.00; // Default 6% if state unknown
    }
    
    /**
     * Add tax to checkout order
     */
    public function add_tax_to_order($order) {
        if (!session_id()) {
            session_start();
        }
        
        $country = isset($_SESSION['user_country']) ? $_SESSION['user_country'] : 'US';
        $state = isset($_SESSION['user_state']) ? $_SESSION['user_state'] : '';
        
        if ($country === 'US') {
            $tax_rate = $this->get_tax_rate_for_state($state);
            $tax_amount = $order->subtotal * ($tax_rate / 100);
            
            $order->tax = $tax_amount;
            $order->total = $order->subtotal + $tax_amount;
            
            // Add tax line item for display
            if ($tax_amount > 0) {
                $state_name = $this->get_state_name($state);
                $order->tax_rate = $tax_rate;
                $order->tax_description = "Sales Tax ({$state_name} {$tax_rate}%)";
            }
        }
        
        return $order;
    }
    
    /**
     * Get full state name from code
     */
    private function get_state_name($state_code) {
        $states = array(
            'AL' => 'Alabama', 'AK' => 'Alaska', 'AZ' => 'Arizona', 'AR' => 'Arkansas',
            'CA' => 'California', 'CO' => 'Colorado', 'CT' => 'Connecticut', 'DE' => 'Delaware',
            'FL' => 'Florida', 'GA' => 'Georgia', 'HI' => 'Hawaii', 'ID' => 'Idaho',
            'IL' => 'Illinois', 'IN' => 'Indiana', 'IA' => 'Iowa', 'KS' => 'Kansas',
            'KY' => 'Kentucky', 'LA' => 'Louisiana', 'ME' => 'Maine', 'MD' => 'Maryland',
            'MA' => 'Massachusetts', 'MI' => 'Michigan', 'MN' => 'Minnesota', 'MS' => 'Mississippi',
            'MO' => 'Missouri', 'MT' => 'Montana', 'NE' => 'Nebraska', 'NV' => 'Nevada',
            'NH' => 'New Hampshire', 'NJ' => 'New Jersey', 'NM' => 'New Mexico', 'NY' => 'New York',
            'NC' => 'North Carolina', 'ND' => 'North Dakota', 'OH' => 'Ohio', 'OK' => 'Oklahoma',
            'OR' => 'Oregon', 'PA' => 'Pennsylvania', 'RI' => 'Rhode Island', 'SC' => 'South Carolina',
            'SD' => 'South Dakota', 'TN' => 'Tennessee', 'TX' => 'Texas', 'UT' => 'Utah',
            'VT' => 'Vermont', 'VA' => 'Virginia', 'WA' => 'Washington', 'WV' => 'West Virginia',
            'WI' => 'Wisconsin', 'WY' => 'Wyoming', 'DC' => 'District of Columbia'
        );
        
        return isset($states[$state_code]) ? $states[$state_code] : $state_code;
    }
    
    /**
     * Add dashboard widget to WordPress admin
     */
    public function add_dashboard_widget() {
        wp_add_dashboard_widget(
            'stock_scanner_analytics',
            '📊 Stock Scanner Analytics',
            array($this, 'dashboard_widget_content')
        );
    }
    
    /**
     * Dashboard widget content
     */
    public function dashboard_widget_content() {
        ?>
        <div id="stock-scanner-analytics">
            <div class="analytics-loading">
                <p>⏳ Loading analytics data...</p>
            </div>
            
            <div class="analytics-content" style="display: none;">
                <div class="analytics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0;">
                    
                    <div class="stat-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4 style="margin: 0; color: #007cba;">👥 Total Members</h4>
                        <p class="total-members" style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #333;">-</p>
                    </div>
                    
                    <div class="stat-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4 style="margin: 0; color: #28a745;">💰 Monthly Revenue</h4>
                        <p class="monthly-revenue" style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #333;">-</p>
                    </div>
                    
                    <div class="stat-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4 style="margin: 0; color: #ffc107;">📈 Avg Per Person</h4>
                        <p class="avg-spending" style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #333;">-</p>
                    </div>
                    
                    <div class="stat-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4 style="margin: 0; color: #17a2b8;">📅 Annual Projected</h4>
                        <p class="annual-projected" style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #333;">-</p>
                    </div>
                    
                </div>
                
                <div class="membership-breakdown" style="margin: 20px 0;">
                    <h4>📊 Membership Distribution</h4>
                    <div class="membership-bars">
                        <div class="tier-bar" style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>🆓 Free</span>
                                <span class="free-count">-</span>
                            </div>
                            <div style="background: #e9ecef; height: 20px; border-radius: 10px;">
                                <div class="free-bar" style="background: #6c757d; height: 100%; border-radius: 10px; width: 0%;"></div>
                            </div>
                        </div>
                        
                        <div class="tier-bar" style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>🥉 Basic ($9.99)</span>
                                <span class="basic-count">-</span>
                            </div>
                            <div style="background: #e9ecef; height: 20px; border-radius: 10px;">
                                <div class="basic-bar" style="background: #007cba; height: 100%; border-radius: 10px; width: 0%;"></div>
                            </div>
                        </div>
                        
                        <div class="tier-bar" style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>🏆 Professional ($29.99)</span>
                                <span class="professional-count">-</span>
                            </div>
                            <div style="background: #e9ecef; height: 20px; border-radius: 10px;">
                                <div class="professional-bar" style="background: #28a745; height: 100%; border-radius: 10px; width: 0%;"></div>
                            </div>
                        </div>
                        
                        <div class="tier-bar" style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>💎 Expert ($49.99)</span>
                                <span class="expert-count">-</span>
                            </div>
                            <div style="background: #e9ecef; height: 20px; border-radius: 10px;">
                                <div class="expert-bar" style="background: #ffc107; height: 100%; border-radius: 10px; width: 0%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="analytics-footer" style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e9ecef; text-align: center;">
                    <p style="margin: 0; color: #6c757d; font-size: 12px;">
                        Last updated: <span class="last-updated">-</span>
                    </p>
                    <button type="button" id="refresh-analytics" class="button button-small" style="margin-top: 10px;">
                        🔄 Refresh Data
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            function loadAnalytics() {
                $.ajax({
                    url: '<?php echo esc_url($this->api_base_url); ?>analytics/public/',
                    method: 'GET',
                    success: function(response) {
                        if (response.success) {
                            const data = response.data;
                            
                            // Update main stats
                            $('.total-members').text(data.total_members.toLocaleString());
                            $('.monthly-revenue').text('$' + data.monthly_revenue.toLocaleString());
                            $('.avg-spending').text('$' + data.avg_spending_per_person.toFixed(2));
                            $('.annual-projected').text('$' + (data.monthly_revenue * 12).toLocaleString());
                            
                                                         // Update membership breakdown from real API data
                             const totalMembers = data.total_members;
                             
                             // If we have no members yet, show all as free
                             const membershipData = {
                                 free: totalMembers,
                                 basic: 0,
                                 professional: 0,
                                 expert: 0
                             };
                            
                            $('.free-count').text(membershipData.free);
                            $('.basic-count').text(membershipData.basic);
                            $('.professional-count').text(membershipData.professional);
                            $('.expert-count').text(membershipData.expert);
                            
                            // Update progress bars
                            $('.free-bar').css('width', (membershipData.free / totalMembers * 100) + '%');
                            $('.basic-bar').css('width', (membershipData.basic / totalMembers * 100) + '%');
                            $('.professional-bar').css('width', (membershipData.professional / totalMembers * 100) + '%');
                            $('.expert-bar').css('width', (membershipData.expert / totalMembers * 100) + '%');
                            
                            $('.last-updated').text(data.last_updated);
                            
                            $('.analytics-loading').hide();
                            $('.analytics-content').show();
                        }
                    },
                    error: function() {
                        $('.analytics-loading').html('<p style="color: red;">❌ Failed to load analytics data</p>');
                    }
                });
            }
            
            // Load analytics on page load
            loadAnalytics();
            
            // Refresh button
            $('#refresh-analytics').click(function() {
                $('.analytics-content').hide();
                $('.analytics-loading').show().html('<p>⏳ Refreshing analytics data...</p>');
                loadAnalytics();
            });
        });
        </script>
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

                    <!-- BASIC PLAN -->
                    <div class="pricing-card basic-plan card">
                        <div class="card-header text-center">
                            <h3>🥉 Basic Plan</h3>
                            <div class="price">$9.99<span>/month</span></div>
                            <p class="plan-subtitle">Perfect for casual traders</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ 100 stocks per month</li>
                                <li>✅ Advanced stock lookup</li>
                                <li>✅ 15 email list subscriptions</li>
                                <li>✅ Real-time market news</li>
                                <li>✅ Basic filtering tools</li>
                                <li>✅ 30-day history</li>
                                <li>✅ Email support</li>
                                <li>❌ Custom watchlists</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/membership-account/membership-checkout/?level=1" class="btn btn-primary">
                                <span>Choose Basic</span>
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
                                <li>✅ 1,000 stocks per month</li>
                                <li>✅ Professional stock analysis</li>
                                <li>✅ Unlimited email lists</li>
                                <li>✅ Advanced news filtering</li>
                                <li>✅ Advanced filtering & screening</li>
                                <li>✅ 1-year historical data</li>
                                <li>✅ Custom watchlists (10)</li>
                                <li>✅ Priority email support</li>
                            </ul>
                        </div>
                        <div class="card-footer text-center">
                            <a href="/membership-account/membership-checkout/?level=2" class="btn btn-success btn-lg">
                                <span>Choose Professional</span>
                            </a>
                        </div>
                    </div>

                    <!-- EXPERT PLAN -->
                    <div class="pricing-card expert-plan card premium">
                        <div class="card-header text-center">
                            <h3>💎 Expert Plan</h3>
                            <div class="price">$49.99<span>/month</span></div>
                            <p class="plan-subtitle">For professional traders</p>
                        </div>
                        <div class="card-body">
                            <ul class="feature-list">
                                <li>✅ Unlimited stocks</li>
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
                            <a href="/membership-account/membership-checkout/?level=3" class="btn btn-gold btn-lg animate-pulse">
                                <span>Choose Expert</span>
                            </a>
                        </div>
                    </div>
                </div>

                <h3 class="text-center" style="margin: var(--spacing-2xl) 0;">📊 Live Stock Analysis</h3>
                <div class="demo-widgets" style="margin: var(--spacing-xl) 0;">
                    [stock_scanner symbol="AAPL" show_chart="true" show_details="true"]
                    [stock_scanner symbol="MSFT" show_chart="true" show_details="true"]
                    [stock_scanner symbol="GOOGL" show_chart="true" show_details="true"]
                </div>
                
                <div class="comparison-section" style="margin: var(--spacing-3xl) 0;">
                    <h3 class="text-center">📋 Feature Comparison</h3>
                    <table class="comparison-table" style="width: 100%; border-collapse: collapse; margin: 40px 0;">
                        <thead>
                            <tr>
                                <th style="text-align: left;">Features</th>
                                <th style="text-align: center;">Free</th>
                                <th style="text-align: center;">Basic</th>
                                <th style="text-align: center;">Professional</th>
                                <th style="text-align: center;">Expert</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Monthly Stock Lookups</td><td style="text-align: center;">15</td><td style="text-align: center;">100</td><td style="text-align: center;">1,000</td><td style="text-align: center;">Unlimited</td></tr>
                            <tr><td>Email List Subscriptions</td><td style="text-align: center;">5</td><td style="text-align: center;">15</td><td style="text-align: center;">Unlimited</td><td style="text-align: center;">Unlimited</td></tr>
                            <tr><td>Advanced Filtering</td><td style="text-align: center;">❌</td><td style="text-align: center;">Basic</td><td style="text-align: center;">✅</td><td style="text-align: center;">✅</td></tr>
                            <tr><td>Historical Data</td><td style="text-align: center;">❌</td><td style="text-align: center;">30 days</td><td style="text-align: center;">1 year</td><td style="text-align: center;">5 years</td></tr>
                            <tr><td>Custom Watchlists</td><td style="text-align: center;">❌</td><td style="text-align: center;">❌</td><td style="text-align: center;">10</td><td style="text-align: center;">Unlimited</td></tr>
                            <tr><td>API Access</td><td style="text-align: center;">❌</td><td style="text-align: center;">❌</td><td style="text-align: center;">❌</td><td style="text-align: center;">✅</td></tr>
                            <tr><td>Support Level</td><td style="text-align: center;">Community</td><td style="text-align: center;">Email</td><td style="text-align: center;">Priority</td><td style="text-align: center;">Phone + Manager</td></tr>
                            <tr><td>Real-time Alerts</td><td style="text-align: center;">❌</td><td style="text-align: center;">❌</td><td style="text-align: center;">Email</td><td style="text-align: center;">SMS + Email</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="faq-section" style="margin: var(--spacing-3xl) 0;">
                    <h3 class="text-center">❓ Frequently Asked Questions</h3>
                    <details>
                        <summary>Can I upgrade or downgrade my plan anytime?</summary>
                        <p>Yes! You can change your plan at any time. Upgrades take effect immediately, and downgrades take effect at your next billing cycle.</p>
                    </details>
                    <details>
                        <summary>What happens if I exceed my monthly stock lookup limit?</summary>
                        <p>We will notify you when you reach 80% of your limit. If you exceed it, you can either upgrade your plan or wait until next month for your limit to reset.</p>
                    </details>
                    <details>
                        <summary>Do you offer annual discounts?</summary>
                        <p>Yes! Annual plans save you 20% compared to monthly billing. Contact our sales team for enterprise pricing.</p>
                    </details>
                    <details>
                        <summary>What payment methods do you accept?</summary>
                        <p>We accept all major credit cards, PayPal, and bank transfers for annual plans.</p>
                    </details>
                </div>
            ',
            'template' => 'page'
        ),
        'email-stock-lists' => array(
            'title' => 'Email Stock Lists',
            'content' => '
                <p>Our email stock lists will keep you informed and up to date on the changing market. Look below for all of our stock lists, chose your favorites and subscribe.</p>
                
                <div class="text-center d-flex justify-content-center gap-md flex-wrap" style="margin: var(--spacing-xl) 0;">
                    <a href="/popular-stock-lists/" class="btn btn-outline btn-primary">
                        <span>🌟 Popular Stock Lists</span>
                    </a>
                    <a href="/all-stock-lists/" class="btn btn-outline btn-primary">
                        <span>📋 All Stock Lists</span>
                    </a>
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
                
                <div class="card bg-primary text-center animate-fade-in" style="margin: var(--spacing-2xl) 0;">
                    <div class="card-body">
                        <h4 class="text-white">🚀 Upgrade for Full Access</h4>
                        <p class="text-white" style="opacity: 0.9;">Get unlimited access to all stock lists with our premium plans!</p>
                        <a href="/premium-plans/" class="btn btn-secondary">
                            <span>View Premium Plans</span>
                        </a>
                    </div>
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
    
    /**
     * Get user membership level
     */
    private function get_user_membership_level() {
        $user_id = get_current_user_id();
        
        if (function_exists('pmpro_getMembershipLevelForUser')) {
            $level = pmpro_getMembershipLevelForUser($user_id);
            if ($level && $level->id) {
                switch ($level->id) {
                    case 1: return 'free';
                    case 2: return 'premium';
                    case 3: return 'professional';
                    default: return 'free';
                }
            }
        }
        
        return $user_id > 0 ? 'free' : 'free';
    }
    
    /**
     * Get available features for user level
     */
    private function get_available_features($user_level) {
        $features = array(
            'free' => array('basic_search', 'limited_data', 'basic_charts'),
            'premium' => array('advanced_search', 'real_time_data', 'premium_charts', 'email_alerts', 'portfolio_tracking'),
            'professional' => array('all_features', 'professional_indicators', 'advanced_analytics', 'api_access', 'priority_support', 'custom_alerts', 'backtesting')
        );
        
        return $features[$user_level] ?? $features['free'];
    }
    
    /**
     * Get user limits for membership level
     */
    private function get_user_limits($user_level) {
        $limits = array(
            'free' => array(
                'api_calls_daily' => 100,
                'searches_daily' => 20,
                'news_articles_daily' => 50,
                'concurrent_requests' => 2,
                'data_retention_days' => 7
            ),
            'premium' => array(
                'api_calls_daily' => 2500,
                'searches_daily' => 500,
                'news_articles_daily' => 1000,
                'concurrent_requests' => 5,
                'data_retention_days' => 30
            ),
            'professional' => array(
                'api_calls_daily' => 10000,
                'searches_daily' => 2000,
                'news_articles_daily' => 5000,
                'concurrent_requests' => 10,
                'data_retention_days' => 365
            )
        );
        
        return $limits[$user_level] ?? $limits['free'];
    }
    
    /**
     * Create professional pages
     */
    private function create_professional_pages() {
        $professional_pages = array(
            'professional-dashboard' => array(
                'title' => 'Professional Dashboard',
                'content' => '[stock_scanner_widget symbol="SPY" style="professional" show_indicators="true"]
                             [stock_scanner_search style="professional" show_filters="true"]
                             [stock_scanner_news template="professional" limit="10"]',
                'template' => 'page-professional.php'
            ),
            'advanced-analytics' => array(
                'title' => 'Advanced Analytics',
                'content' => '[stock_scanner_portfolio style="professional"]
                             [stock_scanner_alerts style="professional"]',
                'template' => 'page-analytics.php'
            ),
            'market-insights' => array(
                'title' => 'Market Insights',
                'content' => '[stock_scanner_news template="insights" limit="20"]
                             [stock_scanner_sentiment_analysis]',
                'template' => 'page-insights.php'
            )
        );
        
        foreach ($professional_pages as $slug => $page_data) {
            $existing_page = get_page_by_path($slug);
            
            if (!$existing_page) {
                $page_id = wp_insert_post(array(
                    'post_title' => $page_data['title'],
                    'post_content' => $page_data['content'],
                    'post_status' => 'publish',
                    'post_type' => 'page',
                    'post_name' => $slug
                ));
                
                if ($page_id && isset($page_data['template'])) {
                    update_post_meta($page_id, '_wp_page_template', $page_data['template']);
                }
            }
        }
    }
    
    /**
     * Register professional shortcodes
     */
    private function register_professional_shortcodes() {
        add_shortcode('stock_scanner_portfolio', array($this, 'render_portfolio_shortcode'));
        add_shortcode('stock_scanner_alerts', array($this, 'render_alerts_shortcode'));
        add_shortcode('stock_scanner_sentiment_analysis', array($this, 'render_sentiment_shortcode'));
        add_shortcode('stock_scanner_system_status', array($this, 'render_system_status_shortcode'));
    }
    
    /**
     * Enhance page content with professional features
     */
    public function enhance_page_content($content) {
        if (is_page()) {
            $user_level = $this->get_user_membership_level();
            
            // Add usage tracking to all API calls
            $content = $this->add_usage_tracking_to_content($content);
            
            // Add professional styling wrapper
            if ($user_level === 'professional') {
                $content = '<div class="professional-content-wrapper">' . $content . '</div>';
            } elseif ($user_level === 'premium') {
                $content = '<div class="premium-content-wrapper">' . $content . '</div>';
            } else {
                $content = '<div class="free-content-wrapper">' . $content . '</div>';
            }
            
            // Add system status indicator for professional users
            if ($user_level === 'professional') {
                $content .= $this->render_system_status_indicator();
            }
        }
        
        return $content;
    }
    
    /**
     * Add professional meta tags
     */
    public function add_professional_meta_tags() {
        if (is_page()) {
            $user_level = $this->get_user_membership_level();
            
            echo '<meta name="stock-scanner-user-level" content="' . esc_attr($user_level) . '">' . "\n";
            echo '<meta name="stock-scanner-features" content="' . esc_attr(implode(',', $this->get_available_features($user_level))) . '">' . "\n";
            
            // Add professional page specific meta tags
            global $post;
            if ($post && strpos($post->post_name, 'professional') !== false) {
                echo '<meta name="stock-scanner-page-type" content="professional">' . "\n";
                echo '<meta name="stock-scanner-requires-auth" content="true">' . "\n";
            }
        }
    }
    
    /**
     * Track user usage via AJAX
     */
    public function track_user_usage() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        $action_type = sanitize_text_field($_POST['action_type'] ?? 'page_view');
        $endpoint = sanitize_text_field($_POST['endpoint'] ?? '');
        $response_time = floatval($_POST['response_time'] ?? 0);
        
        if ($this->usage_tracker) {
            $tracking_id = $this->usage_tracker->track_usage(
                $user_id,
                $action_type,
                $endpoint,
                $response_time
            );
            
            wp_send_json_success(array(
                'tracking_id' => $tracking_id,
                'user_level' => $this->get_user_membership_level(),
                'remaining_calls' => $this->get_remaining_calls($user_id)
            ));
        } else {
            wp_send_json_error('Usage tracker not available');
        }
    }
    
    /**
     * Check system status via AJAX
     */
    public function check_system_status() {
        if ($this->usage_tracker) {
            $status = $this->usage_tracker->get_current_system_status();
            
            wp_send_json_success(array(
                'status' => $status,
                'timestamp' => current_time('mysql'),
                'user_level' => $this->get_user_membership_level()
            ));
        } else {
            wp_send_json_error('System status not available');
        }
    }
    
    /**
     * Get remaining API calls for user
     */
    private function get_remaining_calls($user_id) {
        if (!$this->usage_tracker) return 0;
        
        $user_level = $this->get_user_membership_level();
        $limits = $this->get_user_limits($user_level);
        
        // This would need to be implemented in the usage tracker
        // For now, return a placeholder
        return $limits['api_calls_daily'] ?? 100;
    }
    
    /**
     * Add usage tracking to content
     */
    private function add_usage_tracking_to_content($content) {
        // Add data attributes to track interactions
        $content = str_replace(
            array('[stock_scanner_widget', '[stock_scanner_search', '[stock_scanner_news'),
            array('[stock_scanner_widget data-track="true"', '[stock_scanner_search data-track="true"', '[stock_scanner_news data-track="true"'),
            $content
        );
        
        return $content;
    }
    
    /**
     * Render system status indicator
     */
    private function render_system_status_indicator() {
        ob_start();
        ?>
        <div id="system-status-indicator" class="professional-system-status">
            <div class="status-icon">
                <i class="fas fa-circle" id="status-light"></i>
            </div>
            <div class="status-text">
                <span id="status-message">Checking system status...</span>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            function updateSystemStatus() {
                $.ajax({
                    url: stock_scanner_ajax.system_status_url,
                    type: 'POST',
                    data: {
                        action: 'check_system_status',
                        nonce: stock_scanner_ajax.nonce
                    },
                    success: function(response) {
                        if (response.success) {
                            const status = response.data.status;
                            const statusLight = $('#status-light');
                            const statusMessage = $('#status-message');
                            
                            statusLight.removeClass('text-success text-warning text-danger');
                            
                            switch(status.alert_level) {
                                case 'none':
                                    statusLight.addClass('text-success');
                                    statusMessage.text('System operating normally');
                                    break;
                                case 'warning':
                                    statusLight.addClass('text-warning');
                                    statusMessage.text('System under moderate load');
                                    break;
                                case 'critical':
                                    statusLight.addClass('text-danger');
                                    statusMessage.text('System under heavy load');
                                    break;
                            }
                        }
                    }
                });
            }
            
            // Update status immediately and then every 30 seconds
            updateSystemStatus();
            setInterval(updateSystemStatus, 30000);
        });
        </script>
        
        <style>
        .professional-system-status {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 12px;
            backdrop-filter: blur(10px);
        }
        
        .status-icon {
            font-size: 8px;
        }
        
        .text-success { color: #48bb78; }
        .text-warning { color: #ed8936; }
        .text-danger { color: #f56565; }
        </style>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Render portfolio shortcode
     */
    public function render_portfolio_shortcode($atts) {
        $user_level = $this->get_user_membership_level();
        
        if ($user_level === 'free') {
            return '<div class="upgrade-notice">Portfolio tracking requires a Premium subscription. <a href="/premium-plans/">Upgrade now</a></div>';
        }
        
        return '[stock_scanner_widget symbol="PORTFOLIO" style="professional" show_chart="true"]';
    }
    
    /**
     * Render alerts shortcode
     */
    public function render_alerts_shortcode($atts) {
        $user_level = $this->get_user_membership_level();
        
        if ($user_level === 'free') {
            return '<div class="upgrade-notice">Advanced alerts require a Premium subscription. <a href="/premium-plans/">Upgrade now</a></div>';
        }
        
        return '<div class="stock-scanner-alerts professional-alerts">Alert system coming soon...</div>';
    }
    
    /**
     * Render sentiment analysis shortcode
     */
    public function render_sentiment_shortcode($atts) {
        $user_level = $this->get_user_membership_level();
        
        if ($user_level !== 'professional') {
            return '<div class="upgrade-notice">Sentiment analysis requires a Professional subscription. <a href="/premium-plans/">Upgrade now</a></div>';
        }
        
        return '<div class="stock-scanner-sentiment professional-sentiment">Sentiment analysis coming soon...</div>';
    }
    
    /**
     * Render system status shortcode
     */
    public function render_system_status_shortcode($atts) {
        $user_level = $this->get_user_membership_level();
        
        if ($user_level !== 'professional') {
            return '<div class="upgrade-notice">System status monitoring requires a Professional subscription. <a href="/premium-plans/">Upgrade now</a></div>';
        }
        
        return $this->render_system_status_indicator();
    }
}
?>