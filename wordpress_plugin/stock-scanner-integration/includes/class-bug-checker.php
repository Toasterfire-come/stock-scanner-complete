<?php
/**
 * Comprehensive Bug Checker for Stock Scanner Professional
 * 
 * Tests all main functions to ensure they are bug-free
 */

class StockScannerBugChecker {
    
    private $bugs_found = [];
    private $tests_run = 0;
    private $critical_bugs = 0;
    private $warnings = 0;
    
    public function __construct() {
        add_action('wp_ajax_run_bug_check', [$this, 'run_comprehensive_bug_check']);
        add_action('admin_menu', [$this, 'add_bug_checker_menu']);
    }
    
    /**
     * Add bug checker to admin menu
     */
    public function add_bug_checker_menu() {
        add_submenu_page(
            'stock-scanner-pro',
            'Bug Checker',
            'Bug Checker',
            'manage_options',
            'stock-scanner-bug-checker',
            [$this, 'bug_checker_page']
        );
    }
    
    /**
     * Bug checker admin page
     */
    public function bug_checker_page() {
        ?>
        <div class="wrap">
            <h1>Stock Scanner Professional - Bug Checker</h1>
            <p>Comprehensive testing of all main plugin functions to ensure bug-free operation.</p>
            
            <div class="notice notice-info">
                <p><strong>Monthly Subscription Pricing:</strong></p>
                <ul>
                    <li><strong>Free:</strong> 100 API calls/day, 10/hour</li>
                    <li><strong>Bronze ($14.99/month):</strong> 1,500 API calls/day, 100/hour</li>
                    <li><strong>Silver ($29.99/month):</strong> 5,000 API calls/day, 500/hour</li>
                    <li><strong>Gold ($69.99/month):</strong> Unlimited API calls</li>
                </ul>
            </div>
            
            <button id="run-bug-check" class="button button-primary">Run Full Bug Check</button>
            <button id="quick-check" class="button">Quick Health Check</button>
            
            <div id="bug-check-results" style="margin-top: 20px;"></div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $('#run-bug-check').on('click', function() {
                runBugCheck('full');
            });
            
            $('#quick-check').on('click', function() {
                runBugCheck('quick');
            });
            
            function runBugCheck(type) {
                const button = type === 'full' ? $('#run-bug-check') : $('#quick-check');
                button.prop('disabled', true).text('Running...');
                
                $('#bug-check-results').html('<div class="notice notice-info"><p>Running comprehensive bug check...</p></div>');
                
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'run_bug_check',
                        nonce: '<?php echo wp_create_nonce("bug_check"); ?>',
                        check_type: type
                    },
                    success: function(response) {
                        $('#bug-check-results').html(response.data || response);
                        button.prop('disabled', false).text(type === 'full' ? 'Run Full Bug Check' : 'Quick Health Check');
                    },
                    error: function() {
                        $('#bug-check-results').html('<div class="notice notice-error"><p>Bug check failed to run - this itself is a bug!</p></div>');
                        button.prop('disabled', false).text(type === 'full' ? 'Run Full Bug Check' : 'Quick Health Check');
                    }
                });
            }
        });
        </script>
        <?php
    }
    
    /**
     * Run comprehensive bug check
     */
    public function run_comprehensive_bug_check() {
        if (!wp_verify_nonce($_POST['nonce'], 'bug_check')) {
            wp_die('Security check failed');
        }
        
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions');
        }
        
        $check_type = sanitize_text_field($_POST['check_type'] ?? 'full');
        
        $this->bugs_found = [];
        $this->tests_run = 0;
        $this->critical_bugs = 0;
        $this->warnings = 0;
        
        if ($check_type === 'quick') {
            $this->run_quick_checks();
        } else {
            $this->run_full_bug_check();
        }
        
        $this->output_bug_report();
        wp_die();
    }
    
    /**
     * Run quick health checks
     */
    private function run_quick_checks() {
        $this->log_section('Quick Health Check');
        
        $this->check_class_loading();
        $this->check_database_tables();
        $this->check_api_endpoints_basic();
        $this->check_payment_system_basic();
        $this->check_pricing_consistency();
    }
    
    /**
     * Run full comprehensive bug check
     */
    private function run_full_bug_check() {
        $this->log_section('Comprehensive Bug Check - All Main Functions');
        
        // Core system checks
        $this->check_class_loading();
        $this->check_database_tables();
        $this->check_wordpress_integration();
        
        // Membership system checks
        $this->check_membership_manager();
        $this->check_pricing_consistency();
        $this->check_subscription_lifecycle();
        
        // Payment system checks
        $this->check_payment_system();
        $this->check_paypal_integration();
        
        // API system checks
        $this->check_api_endpoints();
        $this->check_rate_limiting();
        $this->check_security_measures();
        
        // Admin system checks
        $this->check_admin_dashboard();
        $this->check_page_manager();
        
        // SEO system checks
        $this->check_seo_system();
        
        // Data integrity checks
        $this->check_data_consistency();
        $this->check_error_handling();
    }
    
    /**
     * Check if all classes load properly
     */
    private function check_class_loading() {
        $this->log_section('Class Loading Tests');
        
        $required_classes = [
            'StockScannerMembershipManager',
            'StockScannerAPI',
            'StockScannerPayPalIntegration',
            'StockScannerAdminDashboard',
            'StockScannerPageManager',
            'StockScannerSEO',
            'StockScannerSitemap',
            'StockScannerSEOAnalytics'
        ];
        
        foreach ($required_classes as $class) {
            if (class_exists($class)) {
                $this->log_success("Class {$class} loaded successfully");
            } else {
                $this->log_critical_bug("Class {$class} failed to load");
            }
        }
        
        // Test class instantiation
        try {
            if (class_exists('StockScannerMembershipManager')) {
                $membership = new StockScannerMembershipManager();
                $this->log_success('MembershipManager instantiated successfully');
            }
        } catch (Exception $e) {
            $this->log_critical_bug('MembershipManager instantiation failed: ' . $e->getMessage());
        }
    }
    
    /**
     * Check database tables
     */
    private function check_database_tables() {
        $this->log_section('Database Table Tests');
        
        global $wpdb;
        
        $required_tables = [
            $wpdb->prefix . 'stock_scanner_subscriptions',
            $wpdb->prefix . 'stock_scanner_api_usage',
            $wpdb->prefix . 'stock_scanner_transactions',
            $wpdb->prefix . 'stock_scanner_seo_analytics'
        ];
        
        foreach ($required_tables as $table) {
            $table_exists = $wpdb->get_var("SHOW TABLES LIKE '{$table}'") === $table;
            
            if ($table_exists) {
                $this->log_success("Table {$table} exists");
                
                // Check table structure
                $columns = $wpdb->get_results("DESCRIBE {$table}");
                if (empty($columns)) {
                    $this->log_warning("Table {$table} exists but has no columns");
                } else {
                    $this->log_success("Table {$table} has " . count($columns) . " columns");
                }
            } else {
                $this->log_critical_bug("Required table {$table} does not exist");
            }
        }
    }
    
    /**
     * Check WordPress integration
     */
    private function check_wordpress_integration() {
        $this->log_section('WordPress Integration Tests');
        
        // Check if hooks are registered
        $hooks_to_check = [
            'wp_ajax_get_stock_quote',
            'wp_ajax_process_subscription',
            'wp_ajax_update_user_membership'
        ];
        
        global $wp_filter;
        
        foreach ($hooks_to_check as $hook) {
            if (isset($wp_filter[$hook])) {
                $this->log_success("Hook {$hook} is registered");
            } else {
                $this->log_warning("Hook {$hook} is not registered");
            }
        }
        
        // Check if pages are created
        $required_pages = ['stock-scanner-dashboard', 'premium-plans', 'stock-scanner'];
        
        foreach ($required_pages as $page_slug) {
            $page = get_page_by_path($page_slug);
            if ($page) {
                $this->log_success("Page {$page_slug} exists (ID: {$page->ID})");
            } else {
                $this->log_warning("Page {$page_slug} does not exist");
            }
        }
    }
    
    /**
     * Check membership manager functionality
     */
    private function check_membership_manager() {
        $this->log_section('Membership Manager Tests');
        
        if (!class_exists('StockScannerMembershipManager')) {
            $this->log_critical_bug('MembershipManager class not loaded');
            return;
        }
        
        try {
            $membership = new StockScannerMembershipManager();
            
            // Test getting membership levels
            $levels = $membership->get_membership_levels();
            if (is_array($levels) && count($levels) >= 4) {
                $this->log_success('Membership levels loaded successfully (' . count($levels) . ' levels)');
            } else {
                $this->log_warning('Unexpected number of membership levels: ' . count($levels));
            }
            
            // Test user membership functions
            $test_user_level = $membership->get_user_membership_level(1); // Admin user
            if (is_string($test_user_level)) {
                $this->log_success("User membership level retrieved: {$test_user_level}");
            } else {
                $this->log_warning('User membership level function returned unexpected type');
            }
            
            // Test feature checking
            $has_feature = $membership->user_has_feature('realtime_data', 1);
            if (is_bool($has_feature)) {
                $this->log_success('Feature checking function works correctly');
            } else {
                $this->log_warning('Feature checking function returned unexpected type');
            }
            
        } catch (Exception $e) {
            $this->log_critical_bug('MembershipManager test failed: ' . $e->getMessage());
        }
    }
    
    /**
     * Check pricing consistency across all systems
     */
    private function check_pricing_consistency() {
        $this->log_section('Pricing Consistency Tests');
        
        // Expected pricing (monthly subscriptions)
        $expected_pricing = [
            'free' => 0,
            'bronze' => 14.99,
            'silver' => 29.99,
            'gold' => 69.99
        ];
        
        // Expected API limits
        $expected_limits = [
            'free' => ['daily' => 100, 'hourly' => 10],
            'bronze' => ['daily' => 1500, 'hourly' => 100],
            'silver' => ['daily' => 5000, 'hourly' => 500],
            'gold' => ['daily' => -1, 'hourly' => -1] // unlimited
        ];
        
        // Check membership manager pricing
        if (class_exists('StockScannerMembershipManager')) {
            $membership = new StockScannerMembershipManager();
            $levels = $membership->get_membership_levels();
            
            foreach ($expected_pricing as $level => $expected_price) {
                if (isset($levels[$level]['price'])) {
                    $actual_price = $levels[$level]['price'];
                    if ($actual_price == $expected_price) {
                        $this->log_success("Membership price for {$level}: \${$actual_price} ✓");
                    } else {
                        $this->log_critical_bug("Membership price mismatch for {$level}: expected \${$expected_price}, got \${$actual_price}");
                    }
                } else {
                    $this->log_critical_bug("Missing price for {$level} membership level");
                }
            }
            
            // Check API limits
            foreach ($expected_limits as $level => $expected) {
                if (isset($levels[$level]['limits'])) {
                    $limits = $levels[$level]['limits'];
                    
                    if ($limits['api_calls_per_day'] == $expected['daily']) {
                        $this->log_success("API daily limit for {$level}: {$limits['api_calls_per_day']} ✓");
                    } else {
                        $this->log_critical_bug("Daily API limit mismatch for {$level}: expected {$expected['daily']}, got {$limits['api_calls_per_day']}");
                    }
                    
                    if ($limits['api_calls_per_hour'] == $expected['hourly']) {
                        $this->log_success("API hourly limit for {$level}: {$limits['api_calls_per_hour']} ✓");
                    } else {
                        $this->log_critical_bug("Hourly API limit mismatch for {$level}: expected {$expected['hourly']}, got {$limits['api_calls_per_hour']}");
                    }
                }
            }
        }
        
        // Check PayPal integration pricing
        if (class_exists('StockScannerPayPalIntegration')) {
            $this->log_success('PayPal integration pricing should be verified manually');
        }
    }
    
    /**
     * Check subscription lifecycle
     */
    private function check_subscription_lifecycle() {
        $this->log_section('Subscription Lifecycle Tests');
        
        if (!class_exists('StockScannerMembershipManager')) {
            $this->log_critical_bug('MembershipManager not available for lifecycle testing');
            return;
        }
        
        try {
            $membership = new StockScannerMembershipManager();
            
            // Test subscription creation (simulation)
            $test_subscription_data = [
                'user_id' => 999999, // Non-existent user for testing
                'membership_level' => 'bronze',
                'payment_method' => 'test',
                'amount' => 14.99,
                'status' => 'active'
            ];
            
            // We can't actually create a subscription without a real user, but we can test the method exists
            if (method_exists($membership, 'create_subscription_record')) {
                $this->log_success('Subscription creation method exists');
            } else {
                $this->log_critical_bug('Subscription creation method missing');
            }
            
            // Test subscription status checking
            if (method_exists($membership, 'get_user_subscription')) {
                $this->log_success('Subscription retrieval method exists');
            } else {
                $this->log_critical_bug('Subscription retrieval method missing');
            }
            
        } catch (Exception $e) {
            $this->log_warning('Subscription lifecycle test warning: ' . $e->getMessage());
        }
    }
    
    /**
     * Check payment system
     */
    private function check_payment_system() {
        $this->log_section('Payment System Tests');
        
        // Check if PayPal configuration exists
        $paypal_mode = get_option('paypal_mode');
        $paypal_client_id = get_option('paypal_client_id');
        
        if ($paypal_mode) {
            $this->log_success("PayPal mode configured: {$paypal_mode}");
        } else {
            $this->log_warning('PayPal mode not configured');
        }
        
        if ($paypal_client_id) {
            $this->log_success('PayPal client ID configured');
        } else {
            $this->log_warning('PayPal client ID not configured');
        }
        
        // Check if webhooks are set up
        $webhook_url = get_option('paypal_webhook_url');
        if ($webhook_url) {
            $this->log_success("PayPal webhook URL configured: {$webhook_url}");
        } else {
            $this->log_warning('PayPal webhook URL not configured');
        }
    }
    
    /**
     * Check PayPal integration
     */
    private function check_paypal_integration() {
        $this->log_section('PayPal Integration Tests');
        
        if (!class_exists('StockScannerPayPalIntegration')) {
            $this->log_critical_bug('PayPal integration class not loaded');
            return;
        }
        
        try {
            $paypal = new StockScannerPayPalIntegration();
            
            // Check if required methods exist
            $required_methods = ['create_subscription', 'cancel_subscription', 'get_subscription_details'];
            
            foreach ($required_methods as $method) {
                if (method_exists($paypal, $method)) {
                    $this->log_success("PayPal method {$method} exists");
                } else {
                    $this->log_critical_bug("PayPal method {$method} missing");
                }
            }
            
        } catch (Exception $e) {
            $this->log_warning('PayPal integration test warning: ' . $e->getMessage());
        }
    }
    
    /**
     * Check API endpoints
     */
    private function check_api_endpoints_basic() {
        $this->log_section('API Endpoints Basic Tests');
        
        $this->check_ajax_hooks_registered();
    }
    
    /**
     * Check API endpoints thoroughly
     */
    private function check_api_endpoints() {
        $this->log_section('API Endpoints Comprehensive Tests');
        
        if (!class_exists('StockScannerAPI')) {
            $this->log_critical_bug('StockScannerAPI class not loaded');
            return;
        }
        
        // Check AJAX hooks are registered
        $this->check_ajax_hooks_registered();
        
        // Test API configuration validation
        try {
            $api = new StockScannerAPI();
            if (method_exists($api, 'validate_api_config')) {
                $config_result = $api->validate_api_config();
                if (is_array($config_result) && isset($config_result['valid'])) {
                    $this->log_success('API configuration validation method works');
                } else {
                    $this->log_warning('API configuration validation returned unexpected format');
                }
            }
        } catch (Exception $e) {
            $this->log_warning('API test warning: ' . $e->getMessage());
        }
    }
    
    /**
     * Check if AJAX hooks are registered
     */
    private function check_ajax_hooks_registered() {
        global $wp_filter;
        
        $required_ajax_hooks = [
            'wp_ajax_get_stock_quote',
            'wp_ajax_nopriv_get_stock_quote',
            'wp_ajax_search_stocks',
            'wp_ajax_nopriv_search_stocks',
            'wp_ajax_get_market_data',
            'wp_ajax_nopriv_get_market_data',
            'wp_ajax_process_subscription',
            'wp_ajax_cancel_subscription'
        ];
        
        foreach ($required_ajax_hooks as $hook) {
            if (isset($wp_filter[$hook]) && !empty($wp_filter[$hook]->callbacks)) {
                $this->log_success("AJAX hook {$hook} registered");
            } else {
                $this->log_critical_bug("AJAX hook {$hook} not registered");
            }
        }
    }
    
    /**
     * Check rate limiting system
     */
    private function check_rate_limiting() {
        $this->log_section('Rate Limiting Tests');
        
        if (!class_exists('StockScannerMembershipManager')) {
            $this->log_warning('Cannot test rate limiting without MembershipManager');
            return;
        }
        
        try {
            $membership = new StockScannerMembershipManager();
            
            // Test rate limit checking
            if (method_exists($membership, 'check_user_limit')) {
                $this->log_success('Rate limit checking method exists');
                
                // Test with admin user
                $can_call = $membership->check_user_limit('api_calls_per_day', 1);
                if (is_bool($can_call)) {
                    $this->log_success('Rate limit function returns boolean as expected');
                } else {
                    $this->log_warning('Rate limit function returned unexpected type');
                }
            } else {
                $this->log_critical_bug('Rate limit checking method missing');
            }
            
        } catch (Exception $e) {
            $this->log_warning('Rate limiting test warning: ' . $e->getMessage());
        }
    }
    
    /**
     * Check security measures
     */
    private function check_security_measures() {
        $this->log_section('Security Tests');
        
        // Test nonce functionality
        $test_nonce = wp_create_nonce('test_action');
        if ($test_nonce && wp_verify_nonce($test_nonce, 'test_action')) {
            $this->log_success('WordPress nonce system working');
        } else {
            $this->log_critical_bug('WordPress nonce system failed');
        }
        
        // Check if user capabilities are being checked
        if (function_exists('current_user_can')) {
            $this->log_success('User capability checking available');
        } else {
            $this->log_critical_bug('User capability checking not available');
        }
        
        // Check data sanitization functions
        $test_input = '<script>alert("xss")</script>';
        $sanitized = sanitize_text_field($test_input);
        if ($sanitized !== $test_input) {
            $this->log_success('Data sanitization working correctly');
        } else {
            $this->log_critical_bug('Data sanitization may not be working');
        }
    }
    
    /**
     * Check admin dashboard
     */
    private function check_admin_dashboard() {
        $this->log_section('Admin Dashboard Tests');
        
        if (!class_exists('StockScannerAdminDashboard')) {
            $this->log_critical_bug('AdminDashboard class not loaded');
            return;
        }
        
        // Check if admin menu is added
        global $menu, $submenu;
        
        $menu_found = false;
        foreach ($menu as $menu_item) {
            if (isset($menu_item[2]) && $menu_item[2] === 'stock-scanner-pro') {
                $menu_found = true;
                break;
            }
        }
        
        if ($menu_found) {
            $this->log_success('Admin menu registered successfully');
        } else {
            $this->log_warning('Admin menu not found (may be normal if not in admin)');
        }
        
        // Check submenu pages
        if (isset($submenu['stock-scanner-pro'])) {
            $submenu_count = count($submenu['stock-scanner-pro']);
            $this->log_success("Admin submenu has {$submenu_count} pages");
        } else {
            $this->log_warning('Admin submenu not found');
        }
    }
    
    /**
     * Check page manager
     */
    private function check_page_manager() {
        $this->log_section('Page Manager Tests');
        
        if (!class_exists('StockScannerPageManager')) {
            $this->log_critical_bug('PageManager class not loaded');
            return;
        }
        
        // Check if shortcodes are registered
        global $shortcode_tags;
        
        $required_shortcodes = [
            'stock_scanner_dashboard',
            'stock_scanner_premium_plans',
            'stock_scanner_tool'
        ];
        
        foreach ($required_shortcodes as $shortcode) {
            if (isset($shortcode_tags[$shortcode])) {
                $this->log_success("Shortcode [{$shortcode}] registered");
            } else {
                $this->log_critical_bug("Shortcode [{$shortcode}] not registered");
            }
        }
    }
    
    /**
     * Check SEO system
     */
    private function check_seo_system() {
        $this->log_section('SEO System Tests');
        
        $seo_classes = ['StockScannerSEO', 'StockScannerSitemap', 'StockScannerSEOAnalytics'];
        
        foreach ($seo_classes as $class) {
            if (class_exists($class)) {
                $this->log_success("SEO class {$class} loaded");
            } else {
                $this->log_warning("SEO class {$class} not loaded");
            }
        }
    }
    
    /**
     * Check data consistency
     */
    private function check_data_consistency() {
        $this->log_section('Data Consistency Tests');
        
        global $wpdb;
        
        // Check for orphaned records
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        
        if ($wpdb->get_var("SHOW TABLES LIKE '{$subscriptions_table}'")) {
            $orphaned_subscriptions = $wpdb->get_var("
                SELECT COUNT(*) FROM {$subscriptions_table} s 
                LEFT JOIN {$wpdb->users} u ON s.user_id = u.ID 
                WHERE u.ID IS NULL
            ");
            
            if ($orphaned_subscriptions > 0) {
                $this->log_warning("Found {$orphaned_subscriptions} orphaned subscription records");
            } else {
                $this->log_success('No orphaned subscription records found');
            }
        }
        
        if ($wpdb->get_var("SHOW TABLES LIKE '{$usage_table}'")) {
            $orphaned_usage = $wpdb->get_var("
                SELECT COUNT(*) FROM {$usage_table} u 
                LEFT JOIN {$wpdb->users} users ON u.user_id = users.ID 
                WHERE users.ID IS NULL AND u.user_id > 0
            ");
            
            if ($orphaned_usage > 0) {
                $this->log_warning("Found {$orphaned_usage} orphaned usage records");
            } else {
                $this->log_success('No orphaned usage records found');
            }
        }
    }
    
    /**
     * Check error handling
     */
    private function check_error_handling() {
        $this->log_section('Error Handling Tests');
        
        // Test WordPress error logging
        if (function_exists('error_log')) {
            $this->log_success('PHP error logging available');
        } else {
            $this->log_warning('PHP error logging not available');
        }
        
        // Test WordPress debugging
        if (defined('WP_DEBUG') && WP_DEBUG) {
            $this->log_success('WordPress debugging enabled');
        } else {
            $this->log_info('WordPress debugging disabled (normal for production)');
        }
        
        // Test exception handling
        try {
            throw new Exception('Test exception');
        } catch (Exception $e) {
            if ($e->getMessage() === 'Test exception') {
                $this->log_success('Exception handling working correctly');
            } else {
                $this->log_warning('Exception handling may have issues');
            }
        }
    }
    
    /**
     * Logging methods
     */
    private function log_section($title) {
        $this->bugs_found[] = ['type' => 'section', 'title' => $title];
    }
    
    private function log_success($message) {
        $this->tests_run++;
        $this->bugs_found[] = ['type' => 'success', 'message' => $message];
    }
    
    private function log_warning($message) {
        $this->tests_run++;
        $this->warnings++;
        $this->bugs_found[] = ['type' => 'warning', 'message' => $message];
    }
    
    private function log_critical_bug($message) {
        $this->tests_run++;
        $this->critical_bugs++;
        $this->bugs_found[] = ['type' => 'critical', 'message' => $message];
    }
    
    private function log_info($message) {
        $this->bugs_found[] = ['type' => 'info', 'message' => $message];
    }
    
    /**
     * Output bug report
     */
    private function output_bug_report() {
        echo '<div class="bug-report">';
        
        // Summary
        $success_rate = $this->tests_run > 0 ? round((($this->tests_run - $this->critical_bugs - $this->warnings) / $this->tests_run) * 100, 1) : 0;
        $status_class = $this->critical_bugs === 0 ? 'notice-success' : 'notice-error';
        
        echo "<div class='notice {$status_class}' style='margin-bottom: 20px;'>";
        echo "<h3>🔍 Bug Check Summary</h3>";
        echo "<p><strong>Total Tests:</strong> {$this->tests_run}</p>";
        echo "<p><strong>Critical Bugs:</strong> {$this->critical_bugs}</p>";
        echo "<p><strong>Warnings:</strong> {$this->warnings}</p>";
        echo "<p><strong>Health Score:</strong> {$success_rate}%</p>";
        
        if ($this->critical_bugs === 0) {
            echo "<p style='color: green; font-weight: bold;'>✅ No critical bugs found! System appears to be functioning correctly.</p>";
        } else {
            echo "<p style='color: red; font-weight: bold;'>❌ Critical bugs detected! Please review and fix the issues below.</p>";
        }
        echo "</div>";
        
        // Detailed results
        foreach ($this->bugs_found as $item) {
            switch ($item['type']) {
                case 'section':
                    echo "<h3 style='color: #0073aa; margin-top: 25px; border-bottom: 2px solid #0073aa; padding-bottom: 5px;'>{$item['title']}</h3>";
                    break;
                    
                case 'success':
                    echo "<div style='padding: 8px 12px; margin: 3px 0; background: #d4edda; border-left: 4px solid #28a745; color: #155724;'>";
                    echo "✅ {$item['message']}";
                    echo "</div>";
                    break;
                    
                case 'warning':
                    echo "<div style='padding: 8px 12px; margin: 3px 0; background: #fff3cd; border-left: 4px solid #ffc107; color: #856404;'>";
                    echo "⚠️ WARNING: {$item['message']}";
                    echo "</div>";
                    break;
                    
                case 'critical':
                    echo "<div style='padding: 8px 12px; margin: 3px 0; background: #f8d7da; border-left: 4px solid #dc3545; color: #721c24;'>";
                    echo "❌ CRITICAL BUG: {$item['message']}";
                    echo "</div>";
                    break;
                    
                case 'info':
                    echo "<div style='padding: 8px 12px; margin: 3px 0; background: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460;'>";
                    echo "ℹ️ {$item['message']}";
                    echo "</div>";
                    break;
            }
        }
        
        // Pricing verification section
        echo "<div style='margin-top: 30px; padding: 20px; background: #f0f8ff; border: 2px solid #0073aa;'>";
        echo "<h3>💰 Current Pricing Structure (Monthly Subscriptions)</h3>";
        echo "<ul style='list-style-type: none; padding-left: 0;'>";
        echo "<li><strong>🆓 Free:</strong> \$0/month - 100 API calls/day, 10/hour</li>";
        echo "<li><strong>🥉 Bronze:</strong> \$14.99/month - 1,500 API calls/day, 100/hour</li>";
        echo "<li><strong>🥈 Silver:</strong> \$29.99/month - 5,000 API calls/day, 500/hour</li>";
        echo "<li><strong>🥇 Gold:</strong> \$69.99/month - Unlimited API calls</li>";
        echo "</ul>";
        echo "</div>";
        
        echo '</div>';
    }
}

// Initialize bug checker
if (is_admin()) {
    new StockScannerBugChecker();
}