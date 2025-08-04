<?php
/**
 * Admin Dashboard for Stock Scanner Professional
 * 
 * Handles WordPress admin interface, settings, user management, and analytics
 */

class StockScannerAdminDashboard {
    
    private $membership_manager;
    private $seo_analytics;
    
    public function __construct() {
        $this->membership_manager = new StockScannerMembershipManager();
        add_action('admin_menu', [$this, 'add_admin_menu']);
        add_action('admin_init', [$this, 'admin_init']);
        add_action('admin_enqueue_scripts', [$this, 'admin_enqueue_scripts']);
        add_action('wp_ajax_update_user_membership', [$this, 'update_user_membership_ajax']);
        add_action('wp_ajax_get_analytics_data', [$this, 'get_analytics_data_ajax']);
    }
    
    /**
     * Add admin menu pages
     */
    public function add_admin_menu() {
        // Main menu page
        add_menu_page(
            'Stock Scanner Pro',
            'Stock Scanner Pro',
            'manage_options',
            'stock-scanner-pro',
            [$this, 'admin_page_dashboard'],
            'dashicons-chart-line',
            30
        );
        
        // Submenu pages
        add_submenu_page(
            'stock-scanner-pro',
            'Dashboard',
            'Dashboard',
            'manage_options',
            'stock-scanner-pro',
            [$this, 'admin_page_dashboard']
        );
        
        add_submenu_page(
            'stock-scanner-pro',
            'User Management',
            'Users',
            'manage_options',
            'stock-scanner-users',
            [$this, 'admin_page_users']
        );
        
        add_submenu_page(
            'stock-scanner-pro',
            'Settings',
            'Settings',
            'manage_options',
            'stock-scanner-settings',
            [$this, 'admin_page_settings']
        );
        
        add_submenu_page(
            'stock-scanner-pro',
            'Analytics',
            'Analytics',
            'manage_options',
            'stock-scanner-analytics',
            [$this, 'admin_page_analytics']
        );
        
        add_submenu_page(
            'stock-scanner-pro',
            'Payment Logs',
            'Payments',
            'manage_options',
            'stock-scanner-payments',
            [$this, 'admin_page_payments']
        );
    }
    
    /**
     * Initialize admin settings
     */
    public function admin_init() {
        // Register settings
        register_setting('stock_scanner_settings', 'stock_api_quote_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_search_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_market_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_technical_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_news_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_options_endpoint');
        register_setting('stock_scanner_settings', 'stock_api_level2_endpoint');
        
        // PayPal settings
        register_setting('stock_scanner_settings', 'paypal_mode');
        register_setting('stock_scanner_settings', 'paypal_client_id');
        register_setting('stock_scanner_settings', 'paypal_client_secret');
        register_setting('stock_scanner_settings', 'paypal_webhook_url');
        register_setting('stock_scanner_settings', 'paypal_return_url');
        register_setting('stock_scanner_settings', 'paypal_cancel_url');
        
        // Plugin settings
        register_setting('stock_scanner_settings', 'stock_scanner_enable_logging');
        register_setting('stock_scanner_settings', 'stock_scanner_log_level');
        register_setting('stock_scanner_settings', 'stock_scanner_cache_duration');
    }
    
    /**
     * Enqueue admin scripts and styles
     */
    public function admin_enqueue_scripts($hook) {
        if (strpos($hook, 'stock-scanner') === false) {
            return;
        }
        
        wp_enqueue_script(
            'stock-scanner-admin',
            STOCK_SCANNER_PRO_PLUGIN_URL . 'assets/js/admin.js',
            ['jquery', 'wp-util'],
            STOCK_SCANNER_PRO_VERSION,
            true
        );
        
        wp_enqueue_style(
            'stock-scanner-admin',
            STOCK_SCANNER_PRO_PLUGIN_URL . 'assets/css/admin-dashboard.css',
            [],
            STOCK_SCANNER_PRO_VERSION
        );
        
        // Chart.js for analytics
        wp_enqueue_script(
            'chart-js',
            'https://cdn.jsdelivr.net/npm/chart.js',
            [],
            '3.9.1',
            true
        );
        
        wp_localize_script('stock-scanner-admin', 'stockScannerAdmin', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_admin'),
            'strings' => [
                'confirm_delete' => 'Are you sure you want to delete this?',
                'confirm_reset' => 'Are you sure you want to reset all data?',
                'success' => 'Operation completed successfully',
                'error' => 'An error occurred. Please try again.'
            ]
        ]);
    }
    
    /**
     * Dashboard admin page
     */
    public function admin_page_dashboard() {
        $stats = $this->get_dashboard_stats();
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>Stock Scanner Professional - Dashboard</h1>
            
            <div class="dashboard-widgets-wrap">
                <div class="metabox-holder">
                    <div class="postbox-container" style="width: 75%;">
                        <div class="postbox">
                            <h2 class="hndle">Overview</h2>
                            <div class="inside">
                                <div class="main-stats">
                                    <div class="stat-box">
                                        <h3><?php echo number_format($stats['total_users']); ?></h3>
                                        <p>Total Users</p>
                                    </div>
                                    <div class="stat-box">
                                        <h3><?php echo number_format($stats['premium_users']); ?></h3>
                                        <p>Premium Users</p>
                                    </div>
                                    <div class="stat-box">
                                        <h3>$<?php echo number_format($stats['monthly_revenue'], 2); ?></h3>
                                        <p>Monthly Revenue</p>
                                    </div>
                                    <div class="stat-box">
                                        <h3><?php echo number_format($stats['api_calls_today']); ?></h3>
                                        <p>API Calls Today</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="postbox">
                            <h2 class="hndle">Recent Activity</h2>
                            <div class="inside">
                                <table class="wp-list-table widefat fixed striped">
                                    <thead>
                                        <tr>
                                            <th>User</th>
                                            <th>Action</th>
                                            <th>Date</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($stats['recent_activity'] as $activity): ?>
                                        <tr>
                                            <td><?php echo esc_html($activity['user']); ?></td>
                                            <td><?php echo esc_html($activity['action']); ?></td>
                                            <td><?php echo esc_html($activity['date']); ?></td>
                                            <td>
                                                <span class="status-<?php echo esc_attr($activity['status']); ?>">
                                                    <?php echo esc_html(ucfirst($activity['status'])); ?>
                                                </span>
                                            </td>
                                        </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="postbox-container" style="width: 25%;">
                        <div class="postbox">
                            <h2 class="hndle">Quick Actions</h2>
                            <div class="inside">
                                <p><a href="<?php echo admin_url('admin.php?page=stock-scanner-settings'); ?>" class="button button-primary">Settings</a></p>
                                <p><a href="<?php echo admin_url('admin.php?page=stock-scanner-users'); ?>" class="button">Manage Users</a></p>
                                <p><a href="<?php echo admin_url('admin.php?page=stock-scanner-analytics'); ?>" class="button">View Analytics</a></p>
                                <p><button class="button" onclick="checkSystemHealth()">System Health Check</button></p>
                            </div>
                        </div>
                        
                        <div class="postbox">
                            <h2 class="hndle">Membership Distribution</h2>
                            <div class="inside">
                                <canvas id="membershipChart" width="200" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        // Membership distribution chart
        const ctx = document.getElementById('membershipChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Free', 'Bronze', 'Silver', 'Gold'],
                datasets: [{
                    data: [<?php echo implode(',', $stats['membership_distribution']); ?>],
                    backgroundColor: ['#e0e0e0', '#cd7f32', '#c0c0c0', '#ffd700']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        
        function checkSystemHealth() {
            // Implement system health check
            alert('System health check would run here');
        }
        </script>
        <?php
    }
    
    /**
     * Users admin page
     */
    public function admin_page_users() {
        $users = $this->get_users_with_membership();
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>User Management</h1>
            
            <div class="tablenav top">
                <div class="alignleft actions">
                    <select id="bulk-action-selector-top" name="action">
                        <option value="-1">Bulk Actions</option>
                        <option value="upgrade">Upgrade to Bronze</option>
                        <option value="downgrade">Downgrade to Free</option>
                        <option value="cancel">Cancel Subscription</option>
                    </select>
                    <input type="submit" class="button action" value="Apply">
                </div>
                <div class="alignright actions">
                    <input type="search" placeholder="Search users..." class="search-input">
                    <input type="submit" class="button" value="Search">
                </div>
            </div>
            
            <table class="wp-list-table widefat fixed striped users">
                <thead>
                    <tr>
                        <td class="manage-column column-cb check-column">
                            <input type="checkbox" id="cb-select-all-1">
                        </td>
                        <th>User</th>
                        <th>Email</th>
                        <th>Membership</th>
                        <th>Status</th>
                        <th>Revenue</th>
                        <th>API Usage</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                    <tr>
                        <th class="check-column">
                            <input type="checkbox" name="users[]" value="<?php echo $user['id']; ?>">
                        </th>
                        <td>
                            <strong><?php echo esc_html($user['display_name']); ?></strong><br>
                            <small>ID: <?php echo $user['id']; ?></small>
                        </td>
                        <td><?php echo esc_html($user['email']); ?></td>
                        <td>
                            <select class="membership-select" data-user-id="<?php echo $user['id']; ?>">
                                <option value="free" <?php selected($user['membership'], 'free'); ?>>Free</option>
                                <option value="bronze" <?php selected($user['membership'], 'bronze'); ?>>Bronze</option>
                                <option value="silver" <?php selected($user['membership'], 'silver'); ?>>Silver</option>
                                <option value="gold" <?php selected($user['membership'], 'gold'); ?>>Gold</option>
                            </select>
                        </td>
                        <td>
                            <span class="status-<?php echo esc_attr($user['status']); ?>">
                                <?php echo esc_html(ucfirst($user['status'])); ?>
                            </span>
                        </td>
                        <td>$<?php echo number_format($user['revenue'], 2); ?></td>
                        <td>
                            <?php echo $user['api_usage']['daily']; ?>/<?php echo $user['api_usage']['limit']; ?>
                            <div class="usage-bar">
                                <div class="usage-fill" style="width: <?php echo min(100, ($user['api_usage']['daily'] / max($user['api_usage']['limit'], 1)) * 100); ?>%"></div>
                            </div>
                        </td>
                        <td>
                            <button class="button button-small" onclick="viewUser(<?php echo $user['id']; ?>)">View</button>
                            <button class="button button-small" onclick="editUser(<?php echo $user['id']; ?>)">Edit</button>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <script>
        // Handle membership changes
        jQuery('.membership-select').on('change', function() {
            const userId = jQuery(this).data('user-id');
            const newMembership = jQuery(this).val();
            
            if (confirm('Are you sure you want to change this user\'s membership?')) {
                updateUserMembership(userId, newMembership);
            }
        });
        
        function updateUserMembership(userId, membership) {
            jQuery.ajax({
                url: stockScannerAdmin.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'update_user_membership',
                    nonce: stockScannerAdmin.nonce,
                    user_id: userId,
                    membership: membership
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + response.data);
                    }
                }
            });
        }
        
        function viewUser(userId) {
            // Implement user detail view
            window.location.href = 'user-edit.php?user_id=' + userId;
        }
        
        function editUser(userId) {
            // Implement user editing
            window.location.href = 'user-edit.php?user_id=' + userId;
        }
        </script>
        <?php
    }
    
    /**
     * Settings admin page
     */
    public function admin_page_settings() {
        if (isset($_POST['submit'])) {
            // Save settings
            foreach ($_POST as $key => $value) {
                if (strpos($key, 'stock_') === 0 || strpos($key, 'paypal_') === 0) {
                    update_option($key, sanitize_text_field($value));
                }
            }
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>Stock Scanner Settings</h1>
            
            <form method="post" action="">
                <?php wp_nonce_field('stock_scanner_settings'); ?>
                
                <h2 class="nav-tab-wrapper">
                    <a href="#api-settings" class="nav-tab nav-tab-active">API Settings</a>
                    <a href="#paypal-settings" class="nav-tab">PayPal Settings</a>
                    <a href="#general-settings" class="nav-tab">General Settings</a>
                </h2>
                
                <div id="api-settings" class="tab-content">
                    <h3>Stock Data API Configuration</h3>
                    <table class="form-table">
                        <tr>
                            <th>Quote Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_quote_endpoint" value="<?php echo esc_attr(get_option('stock_api_quote_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for real-time stock quotes</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Search Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_search_endpoint" value="<?php echo esc_attr(get_option('stock_api_search_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for stock symbol search</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Market Data Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_market_endpoint" value="<?php echo esc_attr(get_option('stock_api_market_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for market overview data</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Technical Indicators Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_technical_endpoint" value="<?php echo esc_attr(get_option('stock_api_technical_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for technical analysis data</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Options Data Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_options_endpoint" value="<?php echo esc_attr(get_option('stock_api_options_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for options chain data (Premium)</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Level 2 Data Endpoint</th>
                            <td>
                                <input type="url" name="stock_api_level2_endpoint" value="<?php echo esc_attr(get_option('stock_api_level2_endpoint')); ?>" class="regular-text">
                                <p class="description">API endpoint for Level 2 market data (Premium)</p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div id="paypal-settings" class="tab-content" style="display: none;">
                    <h3>PayPal Payment Configuration</h3>
                    <table class="form-table">
                        <tr>
                            <th>PayPal Mode</th>
                            <td>
                                <select name="paypal_mode">
                                    <option value="sandbox" <?php selected(get_option('paypal_mode'), 'sandbox'); ?>>Sandbox (Testing)</option>
                                    <option value="live" <?php selected(get_option('paypal_mode'), 'live'); ?>>Live (Production)</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <th>Client ID</th>
                            <td>
                                <input type="text" name="paypal_client_id" value="<?php echo esc_attr(get_option('paypal_client_id')); ?>" class="regular-text">
                                <p class="description">PayPal application Client ID</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Client Secret</th>
                            <td>
                                <input type="password" name="paypal_client_secret" value="<?php echo esc_attr(get_option('paypal_client_secret')); ?>" class="regular-text">
                                <p class="description">PayPal application Client Secret</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Webhook URL</th>
                            <td>
                                <input type="url" name="paypal_webhook_url" value="<?php echo esc_attr(get_option('paypal_webhook_url', home_url('/wp-json/stock-scanner/v1/paypal-webhook'))); ?>" class="regular-text">
                                <p class="description">URL for PayPal webhook notifications</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Return URL</th>
                            <td>
                                <input type="url" name="paypal_return_url" value="<?php echo esc_attr(get_option('paypal_return_url', home_url('/payment-success/'))); ?>" class="regular-text">
                                <p class="description">URL to redirect after successful payment</p>
                            </td>
                        </tr>
                        <tr>
                            <th>Cancel URL</th>
                            <td>
                                <input type="url" name="paypal_cancel_url" value="<?php echo esc_attr(get_option('paypal_cancel_url', home_url('/payment-cancelled/'))); ?>" class="regular-text">
                                <p class="description">URL to redirect after cancelled payment</p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div id="general-settings" class="tab-content" style="display: none;">
                    <h3>General Plugin Settings</h3>
                    <table class="form-table">
                        <tr>
                            <th>Enable Logging</th>
                            <td>
                                <input type="checkbox" name="stock_scanner_enable_logging" value="1" <?php checked(get_option('stock_scanner_enable_logging')); ?>>
                                <label>Enable detailed logging for debugging</label>
                            </td>
                        </tr>
                        <tr>
                            <th>Log Level</th>
                            <td>
                                <select name="stock_scanner_log_level">
                                    <option value="error" <?php selected(get_option('stock_scanner_log_level'), 'error'); ?>>Error</option>
                                    <option value="warning" <?php selected(get_option('stock_scanner_log_level'), 'warning'); ?>>Warning</option>
                                    <option value="info" <?php selected(get_option('stock_scanner_log_level'), 'info'); ?>>Info</option>
                                    <option value="debug" <?php selected(get_option('stock_scanner_log_level'), 'debug'); ?>>Debug</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <th>Cache Duration</th>
                            <td>
                                <input type="number" name="stock_scanner_cache_duration" value="<?php echo esc_attr(get_option('stock_scanner_cache_duration', 300)); ?>" min="60" max="3600">
                                <label>seconds (60-3600)</label>
                                <p class="description">How long to cache API responses</p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        
        <script>
        // Tab switching
        jQuery('.nav-tab').on('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            jQuery('.nav-tab').removeClass('nav-tab-active');
            jQuery('.tab-content').hide();
            
            // Add active class to clicked tab
            jQuery(this).addClass('nav-tab-active');
            
            // Show corresponding content
            const target = jQuery(this).attr('href');
            jQuery(target).show();
        });
        </script>
        <?php
    }
    
    /**
     * Analytics admin page
     */
    public function admin_page_analytics() {
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>Analytics Dashboard</h1>
            
            <div class="analytics-filters">
                <select id="date-range">
                    <option value="7">Last 7 days</option>
                    <option value="30" selected>Last 30 days</option>
                    <option value="90">Last 90 days</option>
                    <option value="365">Last year</option>
                </select>
                <button class="button" onclick="loadAnalytics()">Refresh</button>
            </div>
            
            <div class="analytics-grid">
                <div class="analytics-widget">
                    <h3>Revenue Trends</h3>
                    <canvas id="revenueChart"></canvas>
                </div>
                
                <div class="analytics-widget">
                    <h3>User Growth</h3>
                    <canvas id="userGrowthChart"></canvas>
                </div>
                
                <div class="analytics-widget">
                    <h3>API Usage</h3>
                    <canvas id="apiUsageChart"></canvas>
                </div>
                
                <div class="analytics-widget">
                    <h3>Conversion Funnel</h3>
                    <div id="conversionFunnel"></div>
                </div>
            </div>
        </div>
        
        <script>
        function loadAnalytics() {
            const dateRange = jQuery('#date-range').val();
            
            jQuery.ajax({
                url: stockScannerAdmin.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'get_analytics_data',
                    nonce: stockScannerAdmin.nonce,
                    date_range: dateRange
                },
                success: function(response) {
                    if (response.success) {
                        renderCharts(response.data);
                    }
                }
            });
        }
        
        function renderCharts(data) {
            // Implement chart rendering
            console.log('Analytics data:', data);
        }
        
        // Load analytics on page load
        jQuery(document).ready(function() {
            loadAnalytics();
        });
        </script>
        <?php
    }
    
    /**
     * Payments admin page
     */
    public function admin_page_payments() {
        $transactions = $this->get_payment_transactions();
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>Payment Transactions</h1>
            
            <div class="tablenav top">
                <div class="alignleft actions">
                    <select name="status-filter">
                        <option value="">All Statuses</option>
                        <option value="completed">Completed</option>
                        <option value="pending">Pending</option>
                        <option value="failed">Failed</option>
                        <option value="refunded">Refunded</option>
                    </select>
                    <select name="method-filter">
                        <option value="">All Methods</option>
                        <option value="paypal">PayPal</option>
                        <option value="stripe">Stripe</option>
                    </select>
                    <input type="submit" class="button" value="Filter">
                </div>
            </div>
            
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th>Transaction ID</th>
                        <th>User</th>
                        <th>Amount</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($transactions as $transaction): ?>
                    <tr>
                        <td><code><?php echo esc_html($transaction['transaction_id']); ?></code></td>
                        <td><?php echo esc_html($transaction['user_name']); ?></td>
                        <td>$<?php echo number_format($transaction['amount'], 2); ?></td>
                        <td><?php echo esc_html(ucfirst($transaction['payment_method'])); ?></td>
                        <td>
                            <span class="status-<?php echo esc_attr($transaction['status']); ?>">
                                <?php echo esc_html(ucfirst($transaction['status'])); ?>
                            </span>
                        </td>
                        <td><?php echo esc_html($transaction['created_at']); ?></td>
                        <td>
                            <button class="button button-small" onclick="viewTransaction('<?php echo esc_js($transaction['transaction_id']); ?>')">View</button>
                            <?php if ($transaction['status'] === 'completed'): ?>
                            <button class="button button-small" onclick="refundTransaction('<?php echo esc_js($transaction['transaction_id']); ?>')">Refund</button>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <script>
        function viewTransaction(transactionId) {
            // Implement transaction details view
            alert('View transaction: ' + transactionId);
        }
        
        function refundTransaction(transactionId) {
            if (confirm('Are you sure you want to refund this transaction?')) {
                // Implement refund functionality
                alert('Refund transaction: ' + transactionId);
            }
        }
        </script>
        <?php
    }
    
    /**
     * Get dashboard statistics
     */
    private function get_dashboard_stats() {
        global $wpdb;
        
        $subscriptions_table = $wpdb->prefix . 'stock_scanner_subscriptions';
        $usage_table = $wpdb->prefix . 'stock_scanner_api_usage';
        
        // Total users
        $total_users = $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users}");
        
        // Premium users
        $premium_users = $wpdb->get_var("
            SELECT COUNT(DISTINCT user_id) 
            FROM {$subscriptions_table} 
            WHERE status = 'active' AND membership_level != 'free'
        ");
        
        // Monthly revenue
        $monthly_revenue = $wpdb->get_var("
            SELECT SUM(amount) 
            FROM {$subscriptions_table} 
            WHERE status = 'active' 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        ") ?: 0;
        
        // API calls today
        $api_calls_today = $wpdb->get_var("
            SELECT SUM(calls_count) 
            FROM {$usage_table} 
            WHERE usage_date = CURDATE()
        ") ?: 0;
        
        // Membership distribution
        $membership_counts = $wpdb->get_results("
            SELECT membership_level, COUNT(*) as count 
            FROM {$subscriptions_table} 
            WHERE status = 'active' 
            GROUP BY membership_level
        ");
        
        $distribution = [0, 0, 0, 0]; // free, bronze, silver, gold
        foreach ($membership_counts as $count) {
            switch ($count->membership_level) {
                case 'free': $distribution[0] = $count->count; break;
                case 'bronze': $distribution[1] = $count->count; break;
                case 'silver': $distribution[2] = $count->count; break;
                case 'gold': $distribution[3] = $count->count; break;
            }
        }
        
        // Recent activity (mock data for now)
        $recent_activity = [
            ['user' => 'John Doe', 'action' => 'Upgraded to Silver', 'date' => '2024-01-15 10:30', 'status' => 'success'],
            ['user' => 'Jane Smith', 'action' => 'API Limit Reached', 'date' => '2024-01-15 09:15', 'status' => 'warning'],
            ['user' => 'Bob Johnson', 'action' => 'New Registration', 'date' => '2024-01-15 08:45', 'status' => 'info'],
            ['user' => 'Alice Brown', 'action' => 'Payment Failed', 'date' => '2024-01-14 16:20', 'status' => 'error'],
        ];
        
        return [
            'total_users' => $total_users,
            'premium_users' => $premium_users,
            'monthly_revenue' => $monthly_revenue,
            'api_calls_today' => $api_calls_today,
            'membership_distribution' => $distribution,
            'recent_activity' => $recent_activity
        ];
    }
    
    /**
     * Get users with membership information
     */
    private function get_users_with_membership() {
        global $wpdb;
        
        $users = $wpdb->get_results("
            SELECT u.ID, u.display_name, u.user_email, 
                   COALESCE(s.membership_level, 'free') as membership_level,
                   COALESCE(s.status, 'active') as status,
                   COALESCE(s.amount, 0) as amount
            FROM {$wpdb->users} u
            LEFT JOIN {$wpdb->prefix}stock_scanner_subscriptions s ON u.ID = s.user_id AND s.status = 'active'
            ORDER BY u.ID DESC
            LIMIT 50
        ");
        
        $result = [];
        foreach ($users as $user) {
            $usage_stats = $this->membership_manager->get_user_usage_stats($user->ID);
            
            $result[] = [
                'id' => $user->ID,
                'display_name' => $user->display_name,
                'email' => $user->user_email,
                'membership' => $user->membership_level,
                'status' => $user->status,
                'revenue' => $user->amount,
                'api_usage' => [
                    'daily' => $usage_stats['daily_api_calls']['used'],
                    'limit' => $usage_stats['daily_api_calls']['limit']
                ]
            ];
        }
        
        return $result;
    }
    
    /**
     * Get payment transactions
     */
    private function get_payment_transactions() {
        global $wpdb;
        
        $transactions = $wpdb->get_results("
            SELECT t.*, u.display_name as user_name
            FROM {$wpdb->prefix}stock_scanner_transactions t
            LEFT JOIN {$wpdb->users} u ON t.user_id = u.ID
            ORDER BY t.created_at DESC
            LIMIT 100
        ");
        
        return $transactions ?: [];
    }
    
    /**
     * Update user membership AJAX handler
     */
    public function update_user_membership_ajax() {
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_admin')) {
            wp_die(json_encode(['success' => false, 'data' => 'Security check failed']));
        }
        
        if (!current_user_can('manage_options')) {
            wp_die(json_encode(['success' => false, 'data' => 'Insufficient permissions']));
        }
        
        $user_id = intval($_POST['user_id']);
        $membership = sanitize_text_field($_POST['membership']);
        
        try {
            // Update user's membership
            $this->membership_manager->create_subscription_record([
                'user_id' => $user_id,
                'membership_level' => $membership,
                'payment_method' => 'admin',
                'amount' => 0,
                'status' => 'active'
            ]);
            
            wp_die(json_encode(['success' => true, 'data' => 'Membership updated successfully']));
            
        } catch (Exception $e) {
            wp_die(json_encode(['success' => false, 'data' => $e->getMessage()]));
        }
    }
    
    /**
     * Get analytics data AJAX handler
     */
    public function get_analytics_data_ajax() {
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_admin')) {
            wp_die(json_encode(['success' => false, 'data' => 'Security check failed']));
        }
        
        if (!current_user_can('manage_options')) {
            wp_die(json_encode(['success' => false, 'data' => 'Insufficient permissions']));
        }
        
        $date_range = sanitize_text_field($_POST['date_range'] ?? '30');
        
        // Get analytics data
        if (class_exists('StockScannerSEOAnalytics')) {
            $analytics = new StockScannerSEOAnalytics();
            $data = $analytics->get_analytics_data($date_range . ' days');
            
            wp_die(json_encode(['success' => true, 'data' => $data]));
        } else {
            wp_die(json_encode(['success' => false, 'data' => 'Analytics not available']));
        }
    }
}

// Initialize admin dashboard
if (is_admin()) {
    new StockScannerAdminDashboard();
}