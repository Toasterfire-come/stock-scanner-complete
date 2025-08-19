<?php
/**
 * Page Manager for Stock Scanner Professional
 * 
 * Handles creation and management of WordPress pages for the plugin
 */

class StockScannerPageManager {
    
    private $pages;
    private $membership_manager;
    
    public function __construct() {
        $this->membership_manager = new StockScannerMembershipManager();
        $this->init_pages();
        $this->add_hooks();
    }
    
    /**
     * Initialize page configurations
     */
    private function init_pages() {
        $this->pages = [
            'stock-scanner-dashboard' => [
                'title' => 'Stock Scanner Dashboard',
                'content' => '[stock_scanner_dashboard]',
                'template' => 'dashboard-template.php',
                'requires_login' => false,
                'membership_required' => false
            ],
            'premium-plans' => [
                'title' => 'Premium Plans',
                'content' => '[stock_scanner_premium_plans]',
                'template' => 'premium-plans-template.php',
                'requires_login' => false,
                'membership_required' => false
            ],
            'stock-scanner' => [
                'title' => 'Stock Scanner',
                'content' => '[stock_scanner_tool]',
                'template' => 'stock-scanner-template.php',
                'requires_login' => false,
                'membership_required' => false
            ],
            'watchlists' => [
                'title' => 'Watchlists',
                'content' => '[stock_scanner_watchlists]',
                'template' => 'watchlists-template.php',
                'requires_login' => true,
                'membership_required' => false
            ],
            'market-overview' => [
                'title' => 'Market Overview',
                'content' => '[stock_scanner_market_overview]',
                'template' => 'market-overview-template.php',
                'requires_login' => false,
                'membership_required' => false
            ],
            'analytics' => [
                'title' => 'Analytics',
                'content' => '[stock_scanner_analytics]',
                'template' => 'analytics-template.php',
                'requires_login' => true,
                'membership_required' => 'silver'
            ],
            'payment-success' => [
                'title' => 'Payment Successful',
                'content' => '[stock_scanner_payment_success]',
                'template' => 'payment-success-template.php',
                'requires_login' => true,
                'membership_required' => false
            ],
            'payment-cancelled' => [
                'title' => 'Payment Cancelled',
                'content' => '[stock_scanner_payment_cancelled]',
                'template' => 'payment-cancelled-template.php',
                'requires_login' => false,
                'membership_required' => false
            ]
        ];
    }
    
    /**
     * Add WordPress hooks
     */
    private function add_hooks() {
        // Avoid creating duplicate pages if the Stock Scanner Pro Theme is active
        if (!wp_get_theme() || stripos(wp_get_theme()->get('Name'), 'Stock Scanner Pro Theme') === false) {
            add_action('init', [$this, 'create_pages']);
        }
        add_action('template_redirect', [$this, 'handle_page_access']);
        add_filter('the_content', [$this, 'filter_page_content']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_page_assets']);
        
        // Shortcode handlers
        add_shortcode('stock_scanner_dashboard', [$this, 'dashboard_shortcode']);
        add_shortcode('stock_scanner_premium_plans', [$this, 'premium_plans_shortcode']);
        add_shortcode('stock_scanner_tool', [$this, 'stock_scanner_shortcode']);
        add_shortcode('stock_screener_tool', [$this, 'stock_scanner_shortcode']);
        add_shortcode('stock_scanner_watchlists', [$this, 'watchlists_shortcode']);
        add_shortcode('stock_scanner_market_overview', [$this, 'market_overview_shortcode']);
        add_shortcode('stock_scanner_analytics', [$this, 'analytics_shortcode']);
        add_shortcode('stock_scanner_payment_success', [$this, 'payment_success_shortcode']);
        add_shortcode('stock_scanner_payment_cancelled', [$this, 'payment_cancelled_shortcode']);
    }
    
    /**
     * Create WordPress pages for the plugin
     */
    public function create_pages() {
        foreach ($this->pages as $slug => $page_config) {
            $existing_page = get_page_by_path($slug);
            
            if (!$existing_page) {
                $page_data = [
                    'post_title' => $page_config['title'],
                    'post_content' => $page_config['content'],
                    'post_name' => $slug,
                    'post_status' => 'publish',
                    'post_type' => 'page',
                    'comment_status' => 'closed',
                    'ping_status' => 'closed'
                ];
                
                $page_id = wp_insert_post($page_data);
                
                if ($page_id && !is_wp_error($page_id)) {
                    // Set page template
                    update_post_meta($page_id, '_wp_page_template', 'stock-scanner-' . $page_config['template']);
                    
                    // Mark as plugin page
                    update_post_meta($page_id, 'stock_scanner_page', true);
                    
                    // Store page configuration
                    update_post_meta($page_id, 'stock_scanner_config', $page_config);
                }
            }
        }
    }
    
    /**
     * Handle page access control
     */
    public function handle_page_access() {
        global $post;
        
        if (!$post || !get_post_meta($post->ID, 'stock_scanner_page', true)) {
            return;
        }
        
        $config = get_post_meta($post->ID, 'stock_scanner_config', true);
        
        if (!$config) {
            return;
        }
        
        // Check login requirement
        if ($config['requires_login'] && !is_user_logged_in()) {
            wp_redirect(wp_login_url(get_permalink()));
            exit;
        }
        
        // Check membership requirement
        if ($config['membership_required'] && is_user_logged_in()) {
            $user_level = $this->membership_manager->get_user_membership_level();
            
            if ($config['membership_required'] !== true && $user_level !== $config['membership_required']) {
                // Check if user has at least the required level
                $level_hierarchy = ['free', 'bronze', 'silver', 'gold'];
                $user_level_index = array_search($user_level, $level_hierarchy);
                $required_level_index = array_search($config['membership_required'], $level_hierarchy);
                
                if ($user_level_index === false || $required_level_index === false || $user_level_index < $required_level_index) {
                    wp_redirect(home_url('/premium-plans/?upgrade_required=' . $config['membership_required']));
                    exit;
                }
            }
        }
    }
    
    /**
     * Filter page content to use custom templates
     */
    public function filter_page_content($content) {
        global $post;
        
        if (!$post || !get_post_meta($post->ID, 'stock_scanner_page', true)) {
            return $content;
        }
        
        $config = get_post_meta($post->ID, 'stock_scanner_config', true);
        
        if ($config && isset($config['template'])) {
            $template_path = STOCK_SCANNER_PLUGIN_DIR . 'templates/' . $config['template'];
            
            if (file_exists($template_path)) {
                ob_start();
                include $template_path;
                return ob_get_clean();
            }
        }
        
        return $content;
    }
    
    /**
     * Enqueue page-specific assets
     */
    public function enqueue_page_assets() {
        global $post;
        
        if (!$post || !get_post_meta($post->ID, 'stock_scanner_page', true)) {
            return;
        }
        
        // Main plugin assets
        wp_enqueue_style(
            'stock-scanner-professional',
            STOCK_SCANNER_PLUGIN_URL . 'assets/css/stock-scanner-professional.css',
            [],
            STOCK_SCANNER_VERSION
        );
        
        wp_enqueue_script(
            'stock-scanner-professional',
            STOCK_SCANNER_PLUGIN_URL . 'assets/js/stock-scanner-professional.js',
            ['jquery'],
            STOCK_SCANNER_VERSION,
            true
        );
        
        wp_enqueue_script(
            'seamless-navigation',
            STOCK_SCANNER_PLUGIN_URL . 'assets/js/seamless-navigation.js',
            ['jquery'],
            STOCK_SCANNER_VERSION,
            true
        );
        
        // Chart.js for analytics and data visualization
        wp_enqueue_script(
            'chart-js',
            'https://cdn.jsdelivr.net/npm/chart.js',
            [],
            '3.9.1',
            true
        );
        
        // Localize script with necessary data
        wp_localize_script('stock-scanner-professional', 'stockScannerData', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
            'userId' => get_current_user_id(),
            'userLevel' => $this->membership_manager->get_user_membership_level(),
            'isLoggedIn' => is_user_logged_in(),
            'homeUrl' => home_url(),
            'pluginUrl' => STOCK_SCANNER_PLUGIN_URL,
            'strings' => [
                'loading' => 'Loading...',
                'error' => 'An error occurred. Please try again.',
                'success' => 'Operation completed successfully.',
                'confirm' => 'Are you sure?',
                'login_required' => 'Please log in to access this feature.',
                'upgrade_required' => 'This feature requires a premium subscription.',
                'rate_limit' => 'Rate limit exceeded. Please upgrade your plan.'
            ]
        ]);
    }
    
    /**
     * Dashboard shortcode handler
     */
    public function dashboard_shortcode($atts) {
        $atts = shortcode_atts([
            'user_id' => get_current_user_id()
        ], $atts);
        
        ob_start();
        
        // Check if user is logged in
        if (!is_user_logged_in()) {
            echo '<div class="stock-scanner-login-prompt">';
            echo '<h3>Welcome to Stock Scanner Professional</h3>';
            echo '<p>Please <a href="' . wp_login_url(get_permalink()) . '">log in</a> or <a href="' . wp_registration_url() . '">register</a> to access your dashboard.</p>';
            echo '</div>';
            return ob_get_clean();
        }
        
        $user_data = [
            'id' => $atts['user_id'],
            'display_name' => get_userdata($atts['user_id'])->display_name,
            'membership_level' => $this->membership_manager->get_user_membership_level($atts['user_id']),
            'usage_stats' => $this->membership_manager->get_user_usage_stats($atts['user_id'])
        ];
        
        // Include dashboard template with user data
        include STOCK_SCANNER_PLUGIN_DIR . 'templates/dashboard-template.php';
        
        return ob_get_clean();
    }
    
    /**
     * Premium plans shortcode handler
     */
    public function premium_plans_shortcode($atts) {
        $atts = shortcode_atts([
            'highlight' => 'bronze'
        ], $atts);
        
        ob_start();
        
        $membership_levels = $this->membership_manager->get_membership_levels();
        $current_user_level = $this->membership_manager->get_user_membership_level();
        
        // Include premium plans template
        include STOCK_SCANNER_PLUGIN_DIR . 'templates/premium-plans-template.php';
        
        return ob_get_clean();
    }
    
    /**
     * Stock scanner tool shortcode handler
     */
    public function stock_scanner_shortcode($atts) {
        $atts = shortcode_atts([
            'default_view' => 'screener'
        ], $atts);
        
        ob_start();
        
        echo '<div id="stock-scanner-app" class="stock-scanner-professional">';
        echo '<div class="scanner-interface">';
        echo '<h2>Professional Stock Scanner</h2>';
        echo '<div id="scanner-controls"></div>';
        echo '<div id="scanner-results"></div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Watchlists shortcode handler
     */
    public function watchlists_shortcode($atts) {
        if (!is_user_logged_in()) {
            return '<div class="login-required">Please log in to manage your watchlists.</div>';
        }
        
        ob_start();
        
        echo '<div id="watchlists-app" class="stock-scanner-professional">';
        echo '<div class="watchlists-interface">';
        echo '<h2>My Watchlists</h2>';
        echo '<div id="watchlist-tabs"></div>';
        echo '<div id="watchlist-content"></div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Market overview shortcode handler
     */
    public function market_overview_shortcode($atts) {
        ob_start();
        
        echo '<div id="market-overview-app" class="stock-scanner-professional">';
        echo '<div class="market-overview-interface">';
        echo '<h2>Live Market Overview</h2>';
        echo '<div id="market-indices"></div>';
        echo '<div id="sector-performance"></div>';
        echo '<div id="market-news"></div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Analytics shortcode handler
     */
    public function analytics_shortcode($atts) {
        if (!is_user_logged_in()) {
            return '<div class="login-required">Please log in to access analytics.</div>';
        }
        
        $user_level = $this->membership_manager->get_user_membership_level();
        if (!$this->membership_manager->user_has_feature('ai_insights')) {
            return '<div class="upgrade-required">AI Analytics requires a Silver or Gold subscription. <a href="' . home_url('/premium-plans/') . '">Upgrade now</a></div>';
        }
        
        ob_start();
        
        echo '<div id="analytics-app" class="stock-scanner-professional">';
        echo '<div class="analytics-interface">';
        echo '<h2>AI-Powered Analytics</h2>';
        echo '<div id="analytics-dashboard"></div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Payment success shortcode handler
     */
    public function payment_success_shortcode($atts) {
        ob_start();
        
        echo '<div class="payment-success stock-scanner-professional">';
        echo '<div class="success-message">';
        echo '<h2>Payment Successful!</h2>';
        echo '<p>Thank you for upgrading to Stock Scanner Professional. Your new features are now active.</p>';
        echo '<div class="success-actions">';
        echo '<a href="' . home_url('/stock-scanner-dashboard/') . '" class="button button-primary">Go to Dashboard</a>';
        echo '<a href="' . home_url('/stock-scanner/') . '" class="button">Start Scanning</a>';
        echo '</div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Payment cancelled shortcode handler
     */
    public function payment_cancelled_shortcode($atts) {
        ob_start();
        
        echo '<div class="payment-cancelled stock-scanner-professional">';
        echo '<div class="cancelled-message">';
        echo '<h2>Payment Cancelled</h2>';
        echo '<p>Your payment was cancelled. You can try again anytime or continue with the free plan.</p>';
        echo '<div class="cancelled-actions">';
        echo '<a href="' . home_url('/premium-plans/') . '" class="button button-primary">Try Again</a>';
        echo '<a href="' . home_url('/stock-scanner-dashboard/') . '" class="button">Free Dashboard</a>';
        echo '</div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
    
    /**
     * Get page configuration
     */
    public function get_page_config($slug) {
        return isset($this->pages[$slug]) ? $this->pages[$slug] : null;
    }
    
    /**
     * Check if current page is a plugin page
     */
    public function is_plugin_page() {
        global $post;
        return $post && get_post_meta($post->ID, 'stock_scanner_page', true);
    }
    
    /**
     * Delete plugin pages (cleanup on deactivation)
     */
    public function delete_pages() {
        foreach (array_keys($this->pages) as $slug) {
            $page = get_page_by_path($slug);
            if ($page && get_post_meta($page->ID, 'stock_scanner_page', true)) {
                wp_delete_post($page->ID, true);
            }
        }
    }
}

// Initialize page manager
new StockScannerPageManager();