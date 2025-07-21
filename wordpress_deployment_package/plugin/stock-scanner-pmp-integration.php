<?php
/**
 * Plugin Name: Stock Scanner PMP Integration
 * Plugin URI: https://retailtradescan.net
 * Description: Integrates Stock Scanner with Paid Membership Pro for member-only stock data access
 * Version: 1.0.0
 * Author: Retail Trade Scan Net
 * License: GPL v2 or later
 * 
 * Requires: Paid Membership Pro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Plugin constants
define('STOCK_SCANNER_PMP_VERSION', '1.0.0');
define('STOCK_SCANNER_PMP_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('STOCK_SCANNER_PMP_PLUGIN_URL', plugin_dir_url(__FILE__));

/**
 * Main plugin class
 */
class StockScannerPMPIntegration {
    
    public function __init() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('rest_api_init', array($this, 'register_api_endpoints'));
        
        // PMP integration hooks
        add_action('pmpro_after_checkout', array($this, 'sync_membership_to_django'));
        add_action('pmpro_after_change_membership_level', array($this, 'sync_membership_change'));
        
        // Shortcodes
        add_shortcode('stock_price_protected', array($this, 'protected_stock_price_shortcode'));
        add_shortcode('member_stock_dashboard', array($this, 'member_dashboard_shortcode'));
        add_shortcode('stock_upgrade_notice', array($this, 'upgrade_notice_shortcode'));
    }
    
    public function init() {
        // Check if PMP is active
        if (!function_exists('pmpro_getLevel')) {
            add_action('admin_notices', array($this, 'pmp_required_notice'));
            return;
        }
        
        // Initialize plugin features
        $this->setup_membership_levels();
    }
    
    public function pmp_required_notice() {
        echo '<div class="notice notice-error"><p>';
        echo '<strong>Stock Scanner PMP Integration:</strong> Paid Membership Pro is required for this plugin to work.';
        echo '</p></div>';
    }
    
    /**
     * Setup membership level mappings
     */
    public function setup_membership_levels() {
        // Define stock access levels for each PMP level
        $this->membership_levels = array(
            0 => array( // Free
                'name' => 'Free',
                'stocks_per_month' => 15,         // 15 stock views per month
                'stocks_per_day' => 5,            // 5 stock views per day (to spread out usage)
                'api_calls_per_hour' => 20,       // 20 API calls per hour
                'features' => array('basic_prices', 'limited_data')
            ),
            1 => array( // Basic
                'name' => 'Basic',
                'stocks_per_month' => 1500,       // 1,500 stock views per month
                'stocks_per_day' => 50,           // 50 stock views per day
                'api_calls_per_hour' => 100,      // 100 API calls per hour
                'features' => array('real_time_prices', 'volume_data', 'basic_charts')
            ),
            2 => array( // Premium
                'name' => 'Premium',
                'stocks_per_month' => 6000,       // 6,000 stock views per month
                'stocks_per_day' => 200,          // 200 stock views per day
                'api_calls_per_hour' => 500,      // 500 API calls per hour
                'features' => array('technical_indicators', 'alerts', 'advanced_charts', 'portfolio_tracking')
            ),
            3 => array( // Pro
                'name' => 'Pro',
                'stocks_per_month' => -1,         // Unlimited stock views
                'stocks_per_day' => -1,           // Unlimited daily views
                'api_calls_per_hour' => -1,       // Unlimited API calls
                'features' => array('ai_analysis', 'predictions', 'insider_data', 'api_access', 'white_label')
            )
        );
    }
    
    /**
     * Enqueue scripts and styles
     */
    public function enqueue_scripts() {
        wp_enqueue_script(
            'stock-scanner-pmp',
            STOCK_SCANNER_PMP_PLUGIN_URL . 'assets/stock-scanner-pmp.js',
            array('jquery'),
            STOCK_SCANNER_PMP_VERSION,
            true
        );
        
        // Pass data to JavaScript
        wp_localize_script('stock-scanner-pmp', 'stockScannerPMP', array(
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_pmp'),
            'django_api_url' => defined('DJANGO_API_URL') ? DJANGO_API_URL : '',
            'user_level' => $this->get_user_membership_level(),
            'features' => $this->get_user_features()
        ));
        
        wp_enqueue_style(
            'stock-scanner-pmp',
            STOCK_SCANNER_PMP_PLUGIN_URL . 'assets/stock-scanner-pmp.css',
            array(),
            STOCK_SCANNER_PMP_VERSION
        );
    }
    
    /**
     * Register REST API endpoints
     */
    public function register_api_endpoints() {
        // Endpoint for Django to verify user membership
        register_rest_route('pmp/v1', '/member/verify', array(
            'methods' => 'GET',
            'callback' => array($this, 'verify_member_api'),
            'permission_callback' => array($this, 'verify_member_permission')
        ));
        
        // Endpoint to get user's stock access limits
        register_rest_route('stock-scanner/v1', '/user/limits', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_user_limits_api'),
            'permission_callback' => '__return_true'
        ));
    }
    
    /**
     * API endpoint to verify member for Django
     */
    public function verify_member_api($request) {
        $user_id = get_current_user_id();
        
        if (!$user_id) {
            return new WP_Error('not_logged_in', 'User not logged in', array('status' => 401));
        }
        
        $membership_level = pmpro_getMembershipLevelForUser($user_id);
        $level_id = $membership_level ? $membership_level->id : 0;
        
        // Get level configuration
        $level_config = isset($this->membership_levels[$level_id]) 
            ? $this->membership_levels[$level_id] 
            : $this->membership_levels[0];
        
        // Check if membership is active
        $is_active = !empty($membership_level) && pmpro_hasMembershipLevel($level_id, $user_id);
        
        return array(
            'success' => true,
            'user_id' => $user_id,
            'membership_level' => array(
                'id' => $level_id,
                'name' => $level_config['name'],
                'enddate' => $membership_level ? $membership_level->enddate : null
            ),
            'is_active' => $is_active,
            'features' => $level_config['features'],
            'limits' => array(
                'stock_limit' => $level_config['stock_limit'],
                'api_calls_per_hour' => $level_config['api_calls_per_hour']
            ),
            'expires_at' => $membership_level && $membership_level->enddate 
                ? date('c', strtotime($membership_level->enddate))
                : null
        );
    }
    
    public function verify_member_permission($request) {
        return current_user_can('read');
    }
    
    /**
     * Get user limits API
     */
    public function get_user_limits_api($request) {
        $user_id = get_current_user_id();
        $level_id = $this->get_user_membership_level();
        
        $level_config = isset($this->membership_levels[$level_id]) 
            ? $this->membership_levels[$level_id] 
            : $this->membership_levels[0];
        
        // Get current usage
        $monthly_usage = $this->get_monthly_stock_usage($user_id);
        $daily_usage = $this->get_daily_stock_usage($user_id);
        
        return array(
            'level_id' => $level_id,
            'level_name' => $level_config['name'],
            'limits' => array(
                'stocks_per_month' => $level_config['stocks_per_month'],
                'stocks_per_day' => $level_config['stocks_per_day'],
                'api_calls_per_hour' => $level_config['api_calls_per_hour']
            ),
            'usage' => array(
                'stocks_this_month' => $monthly_usage,
                'stocks_today' => $daily_usage,
                'remaining_monthly' => $level_config['stocks_per_month'] == -1 ? -1 : max(0, $level_config['stocks_per_month'] - $monthly_usage),
                'remaining_daily' => $level_config['stocks_per_day'] == -1 ? -1 : max(0, $level_config['stocks_per_day'] - $daily_usage)
            ),
            'features' => $level_config['features']
        );
    }
    
    /**
     * Get monthly stock usage for user
     */
    public function get_monthly_stock_usage($user_id) {
        $current_month = date('Y-m');
        $usage_key = "stock_usage_monthly_{$user_id}_{$current_month}";
        
        return get_user_meta($user_id, $usage_key, true) ?: 0;
    }
    
    /**
     * Get daily stock usage for user
     */
    public function get_daily_stock_usage($user_id) {
        $current_date = date('Y-m-d');
        $usage_key = "stock_usage_daily_{$user_id}_{$current_date}";
        
        return get_user_meta($user_id, $usage_key, true) ?: 0;
    }
    
    /**
     * Track stock view for user
     */
    public function track_stock_view($user_id, $ticker = '') {
        if (!$user_id) return false;
        
        $current_month = date('Y-m');
        $current_date = date('Y-m-d');
        
        // Update monthly usage
        $monthly_key = "stock_usage_monthly_{$user_id}_{$current_month}";
        $monthly_usage = get_user_meta($user_id, $monthly_key, true) ?: 0;
        update_user_meta($user_id, $monthly_key, $monthly_usage + 1);
        
        // Update daily usage
        $daily_key = "stock_usage_daily_{$user_id}_{$current_date}";
        $daily_usage = get_user_meta($user_id, $daily_key, true) ?: 0;
        update_user_meta($user_id, $daily_key, $daily_usage + 1);
        
        // Log the view
        $log_key = "stock_view_log_{$user_id}";
        $log = get_user_meta($user_id, $log_key, true) ?: array();
        $log[] = array(
            'ticker' => $ticker,
            'timestamp' => current_time('mysql'),
            'date' => $current_date
        );
        
        // Keep only last 100 entries
        if (count($log) > 100) {
            $log = array_slice($log, -100);
        }
        
        update_user_meta($user_id, $log_key, $log);
        
        return true;
    }
    
    /**
     * Check if user has reached their limits
     */
    public function check_user_limits($user_id) {
        $level_id = $this->get_user_membership_level();
        $level_config = isset($this->membership_levels[$level_id]) 
            ? $this->membership_levels[$level_id] 
            : $this->membership_levels[0];
        
        // Check monthly limit
        if ($level_config['stocks_per_month'] != -1) {
            $monthly_usage = $this->get_monthly_stock_usage($user_id);
            if ($monthly_usage >= $level_config['stocks_per_month']) {
                return array(
                    'allowed' => false,
                    'reason' => 'monthly_limit_exceeded',
                    'limit_type' => 'monthly',
                    'limit' => $level_config['stocks_per_month'],
                    'usage' => $monthly_usage
                );
            }
        }
        
        // Check daily limit
        if ($level_config['stocks_per_day'] != -1) {
            $daily_usage = $this->get_daily_stock_usage($user_id);
            if ($daily_usage >= $level_config['stocks_per_day']) {
                return array(
                    'allowed' => false,
                    'reason' => 'daily_limit_exceeded',
                    'limit_type' => 'daily',
                    'limit' => $level_config['stocks_per_day'],
                    'usage' => $daily_usage
                );
            }
        }
        
        return array('allowed' => true);
    }
    
    /**
     * Get user's membership level
     */
    public function get_user_membership_level() {
        if (!function_exists('pmpro_getMembershipLevelForUser')) {
            return 0;
        }
        
        $user_id = get_current_user_id();
        if (!$user_id) {
            return 0;
        }
        
        $membership_level = pmpro_getMembershipLevelForUser($user_id);
        return $membership_level ? $membership_level->id : 0;
    }
    
    /**
     * Get user's available features
     */
    public function get_user_features() {
        $level_id = $this->get_user_membership_level();
        $level_config = isset($this->membership_levels[$level_id]) 
            ? $this->membership_levels[$level_id] 
            : $this->membership_levels[0];
        
        return $level_config['features'];
    }
    
    /**
     * Sync membership to Django when user signs up
     */
    public function sync_membership_to_django($user_id) {
        if (!defined('DJANGO_API_URL')) {
            return;
        }
        
        $user = get_user_by('id', $user_id);
        if (!$user) {
            return;
        }
        
        $membership_level = pmpro_getMembershipLevelForUser($user_id);
        $level_id = $membership_level ? $membership_level->id : 0;
        
        // Send to Django
        $this->send_membership_sync($user->user_email, $level_id);
    }
    
    /**
     * Sync membership changes to Django
     */
    public function sync_membership_change($level_id, $user_id) {
        if (!defined('DJANGO_API_URL')) {
            return;
        }
        
        $user = get_user_by('id', $user_id);
        if (!$user) {
            return;
        }
        
        $this->send_membership_sync($user->user_email, $level_id);
    }
    
    /**
     * Send membership sync to Django
     */
    private function send_membership_sync($email, $level_id) {
        $api_url = rtrim(DJANGO_API_URL, '/') . '/api/wordpress/membership-sync/';
        
        $data = array(
            'email' => $email,
            'membership_level' => $level_id,
            'timestamp' => current_time('c')
        );
        
        wp_remote_post($api_url, array(
            'body' => json_encode($data),
            'headers' => array(
                'Content-Type' => 'application/json'
            ),
            'timeout' => 15
        ));
    }
    
    /**
     * Protected stock price shortcode
     */
    public function protected_stock_price_shortcode($atts) {
        $atts = shortcode_atts(array(
            'ticker' => '',
            'format' => 'basic',
            'required_level' => 'basic'
        ), $atts);
        
        if (empty($atts['ticker'])) {
            return '<span class="error">Ticker required</span>';
        }
        
        $user_level = $this->get_user_membership_level();
        $required_level_id = array_search($atts['required_level'], array_column($this->membership_levels, 'name'));
        
        if ($user_level < $required_level_id) {
            return $this->render_upgrade_notice($atts['required_level']);
        }
        
        // User has access - show stock data
        return $this->render_stock_data($atts['ticker'], $atts['format']);
    }
    
    /**
     * Member dashboard shortcode
     */
    public function member_dashboard_shortcode($atts) {
        $user_id = get_current_user_id();
        
        if (!$user_id) {
            return '<p>Please <a href="' . wp_login_url() . '">login</a> to view your dashboard.</p>';
        }
        
        $level_id = $this->get_user_membership_level();
        $level_config = $this->membership_levels[$level_id];
        
        // Get usage stats
        $monthly_usage = $this->get_monthly_stock_usage($user_id);
        $daily_usage = $this->get_daily_stock_usage($user_id);
        
        ob_start();
        ?>
        <div class="stock-scanner-member-dashboard">
            <h3>Your Stock Scanner Membership</h3>
            
            <div class="membership-info">
                <div class="level-badge level-<?php echo $level_id; ?>">
                    <?php echo esc_html($level_config['name']); ?> Member
                </div>
                
                <div class="usage-stats">
                    <h4>Monthly Usage</h4>
                    <div class="usage-bar">
                        <?php 
                        $monthly_limit = $level_config['stocks_per_month'];
                        $monthly_percent = $monthly_limit == -1 ? 0 : min(100, ($monthly_usage / $monthly_limit) * 100);
                        ?>
                        <div class="usage-progress">
                            <div class="usage-fill" style="width: <?php echo $monthly_percent; ?>%"></div>
                        </div>
                        <div class="usage-text">
                            <?php echo $monthly_usage; ?> / <?php echo $monthly_limit == -1 ? '∞' : $monthly_limit; ?> stocks this month
                        </div>
                    </div>
                    
                    <h4>Daily Usage</h4>
                    <div class="usage-bar">
                        <?php 
                        $daily_limit = $level_config['stocks_per_day'];
                        $daily_percent = $daily_limit == -1 ? 0 : min(100, ($daily_usage / $daily_limit) * 100);
                        ?>
                        <div class="usage-progress">
                            <div class="usage-fill" style="width: <?php echo $daily_percent; ?>%"></div>
                        </div>
                        <div class="usage-text">
                            <?php echo $daily_usage; ?> / <?php echo $daily_limit == -1 ? '∞' : $daily_limit; ?> stocks today
                        </div>
                    </div>
                </div>
                
                <div class="limits">
                    <div class="limit-item">
                        <span class="label">Monthly Allowance:</span>
                        <span class="value">
                            <?php echo $level_config['stocks_per_month'] == -1 ? 'Unlimited' : number_format($level_config['stocks_per_month']); ?>
                        </span>
                    </div>
                    
                    <div class="limit-item">
                        <span class="label">Daily Allowance:</span>
                        <span class="value">
                            <?php echo $level_config['stocks_per_day'] == -1 ? 'Unlimited' : $level_config['stocks_per_day']; ?>
                        </span>
                    </div>
                    
                    <div class="limit-item">
                        <span class="label">API Calls/Hour:</span>
                        <span class="value">
                            <?php echo $level_config['api_calls_per_hour'] == -1 ? 'Unlimited' : $level_config['api_calls_per_hour']; ?>
                        </span>
                    </div>
                </div>
                
                <div class="features">
                    <h4>Your Features:</h4>
                    <ul>
                        <?php foreach ($level_config['features'] as $feature): ?>
                            <li><?php echo esc_html(str_replace('_', ' ', ucfirst($feature))); ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
                
                <?php if ($level_id < 3): ?>
                    <div class="upgrade-section">
                        <h4>Upgrade for More Features:</h4>
                        <a href="<?php echo pmpro_url('levels'); ?>" class="upgrade-button">
                            View Membership Levels
                        </a>
                    </div>
                <?php endif; ?>
            </div>
            
            <div class="stock-scanner-tools">
                <h4>Quick Tools:</h4>
                <div class="tool-buttons">
                    <a href="#" class="tool-button" data-tool="search">Stock Search</a>
                    <a href="#" class="tool-button" data-tool="watchlist">My Watchlist</a>
                    <?php if (in_array('alerts', $level_config['features'])): ?>
                        <a href="#" class="tool-button" data-tool="alerts">Price Alerts</a>
                    <?php endif; ?>
                    <?php if (in_array('portfolio_tracking', $level_config['features'])): ?>
                        <a href="#" class="tool-button" data-tool="portfolio">Portfolio</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Upgrade notice shortcode
     */
    public function upgrade_notice_shortcode($atts) {
        $atts = shortcode_atts(array(
            'required_level' => 'basic',
            'feature' => 'this feature'
        ), $atts);
        
        return $this->render_upgrade_notice($atts['required_level'], $atts['feature']);
    }
    
    /**
     * Render upgrade notice
     */
    private function render_upgrade_notice($required_level, $feature = 'this content') {
        $levels_url = function_exists('pmpro_url') ? pmpro_url('levels') : '/membership-levels/';
        
        ob_start();
        ?>
        <div class="stock-scanner-upgrade-notice">
            <div class="upgrade-icon">🔒</div>
            <div class="upgrade-content">
                <h4>Upgrade Required</h4>
                <p><?php echo ucfirst($required_level); ?> membership required to access <?php echo esc_html($feature); ?>.</p>
                <a href="<?php echo esc_url($levels_url); ?>" class="upgrade-button">
                    Upgrade Now
                </a>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Render stock data
     */
    private function render_stock_data($ticker, $format) {
        if (!defined('DJANGO_API_URL')) {
            return '<span class="error">API not configured</span>';
        }
        
        // Get user token for API call
        $user_token = $this->get_user_api_token();
        
        // This would make an AJAX call to your Django API
        return '<div class="stock-data" data-ticker="' . esc_attr($ticker) . '" data-format="' . esc_attr($format) . '" data-token="' . esc_attr($user_token) . '">Loading ' . esc_html($ticker) . '...</div>';
    }
    
    /**
     * Get user API token for Django
     */
    private function get_user_api_token() {
        $user_id = get_current_user_id();
        if (!$user_id) {
            return '';
        }
        
        // Generate a simple token based on user ID and membership level
        $level_id = $this->get_user_membership_level();
        return base64_encode($user_id . ':' . $level_id . ':' . wp_create_nonce('stock_api_' . $user_id));
    }
}

// Initialize the plugin
$stock_scanner_pmp = new StockScannerPMPIntegration();
$stock_scanner_pmp->init();

/**
 * Helper functions for themes
 */

/**
 * Check if user has access to specific stock feature
 */
function stock_scanner_user_can_access($feature) {
    global $stock_scanner_pmp;
    
    if (!$stock_scanner_pmp) {
        return false;
    }
    
    $user_features = $stock_scanner_pmp->get_user_features();
    return in_array($feature, $user_features);
}

/**
 * Get user's stock access limit
 */
function stock_scanner_get_user_limit() {
    global $stock_scanner_pmp;
    
    if (!$stock_scanner_pmp) {
        return 10; // Default free limit
    }
    
    $level_id = $stock_scanner_pmp->get_user_membership_level();
    $levels = $stock_scanner_pmp->membership_levels;
    
    return isset($levels[$level_id]) ? $levels[$level_id]['stock_limit'] : 10;
}

/**
 * Display stock data with membership protection
 */
function stock_scanner_display_protected_data($ticker, $required_level = 'basic') {
    echo do_shortcode('[stock_price_protected ticker="' . esc_attr($ticker) . '" required_level="' . esc_attr($required_level) . '"]');
}
?>