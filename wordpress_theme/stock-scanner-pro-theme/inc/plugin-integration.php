<?php
/**
 * Plugin Integration Functions
 * Enhanced with customer notification system for security alerts
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Check if Stock Scanner plugin is active
 */
function is_stock_scanner_plugin_active() {
    return class_exists('Stock_Scanner_Integration');
}

/**
 * Get user membership level
 */
function get_user_membership_level($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return 'free';
    }
    
    $level = get_user_meta($user_id, 'membership_level', true);
    return $level ?: 'free';
}

/**
 * Get user API usage with enhanced security tracking
 */
function get_user_api_usage($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array('monthly_calls' => 0, 'daily_calls' => 0, 'hourly_calls' => 0, 'monthly_limit' => 15);
    }
    
    global $wpdb;
    $table = $wpdb->prefix . 'stock_scanner_usage';
    
    $current_month = date('Y-m');
    $current_date = date('Y-m-d');
    $current_hour = date('Y-m-d H:00:00');
    
    $monthly_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table WHERE user_id = %d AND DATE_FORMAT(created_at, '%%Y-%%m') = %s",
        $user_id, $current_month
    ));
    
    $daily_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table WHERE user_id = %d AND DATE(created_at) = %s",
        $user_id, $current_date
    ));
    
    $hourly_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table WHERE user_id = %d AND created_at >= %s",
        $user_id, $current_hour
    ));
    
    // Get suspicious activity count
    $suspicious_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table WHERE user_id = %d AND is_suspicious = 1 AND DATE_FORMAT(created_at, '%%Y-%%m') = %s",
        $user_id, $current_month
    ));
    
    $limits = get_membership_limits(get_user_membership_level($user_id));
    
    return array(
        'monthly_calls' => intval($monthly_calls),
        'daily_calls' => intval($daily_calls),
        'hourly_calls' => intval($hourly_calls),
        'suspicious_calls' => intval($suspicious_calls),
        'monthly_limit' => $limits['monthly'],
        'daily_limit' => $limits['daily'],
        'hourly_limit' => $limits['hourly']
    );
}

/**
 * Get membership limits with enhanced tracking
 */
function get_membership_limits($level = 'free') {
    $limits = array(
        'free' => array('monthly' => 15, 'daily' => 5, 'hourly' => 2),
        'bronze' => array('monthly' => 1500, 'daily' => 50, 'hourly' => 10),
        'silver' => array('monthly' => 5000, 'daily' => 200, 'hourly' => 25),
        'gold' => array('monthly' => -1, 'daily' => -1, 'hourly' => -1) // Unlimited
    );
    
    return $limits[$level] ?? $limits['free'];
}

/**
 * Check if user is banned or restricted
 */
function check_user_security_status($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array('status' => 'guest', 'message' => '');
    }
    
    global $wpdb;
    
    $subscription = $wpdb->get_row($wpdb->prepare(
        "SELECT is_banned, ban_reason, banned_at FROM {$wpdb->prefix}stock_scanner_subscriptions WHERE user_id = %d",
        $user_id
    ));
    
    if ($subscription && $subscription->is_banned) {
        return array(
            'status' => 'banned',
            'message' => $subscription->ban_reason,
            'banned_at' => $subscription->banned_at
        );
    }
    
    return array('status' => 'active', 'message' => '');
}

/**
 * Get user notifications
 */
function get_user_notifications($user_id = null, $unread_only = false) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array();
    }
    
    global $wpdb;
    
    $where_clause = "user_id = %d";
    $params = array($user_id);
    
    if ($unread_only) {
        $where_clause .= " AND is_read = 0";
    }
    
    $where_clause .= " AND (expires_at IS NULL OR expires_at > NOW())";
    
    $notifications = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM {$wpdb->prefix}stock_scanner_notifications 
         WHERE $where_clause 
         ORDER BY priority DESC, created_at DESC 
         LIMIT 10",
        ...$params
    ));
    
    return $notifications ?: array();
}

/**
 * Mark notification as read
 */
function mark_notification_read($notification_id, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    global $wpdb;
    
    return $wpdb->update(
        $wpdb->prefix . 'stock_scanner_notifications',
        array('is_read' => 1, 'read_at' => current_time('mysql')),
        array('id' => $notification_id, 'user_id' => $user_id)
    );
}

/**
 * Can user make API call (enhanced with security checks)
 */
function can_user_make_api_call($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    // Check if user is banned
    $security_status = check_user_security_status($user_id);
    if ($security_status['status'] === 'banned') {
        return false;
    }
    
    $usage = get_user_api_usage($user_id);
    $level = get_user_membership_level($user_id);
    $limits = get_membership_limits($level);
    
    if ($limits['monthly'] === -1) {
        return true; // Unlimited
    }
    
    return $usage['monthly_calls'] < $limits['monthly'] &&
           $usage['daily_calls'] < $limits['daily'] &&
           $usage['hourly_calls'] < $limits['hourly'];
}

/**
 * Enhanced dashboard shortcode with security notifications
 */
function stock_scanner_dashboard_shortcode($atts) {
    $atts = shortcode_atts(array(
        'show_notifications' => 'true',
        'show_security_status' => 'true'
    ), $atts);
    
    if (!is_user_logged_in()) {
        return '<div class="stock-scanner-login-prompt">
            <h3>📊 Access Your Dashboard</h3>
            <p>Please log in to access your Stock Scanner dashboard.</p>
            <a href="' . wp_login_url() . '" class="btn btn-primary">Login</a>
            <a href="' . wp_registration_url() . '" class="btn btn-outline">Sign Up Free</a>
        </div>';
    }
    
    $user_id = get_current_user_id();
    $user = wp_get_current_user();
    $usage = get_user_api_usage($user_id);
    $membership_level = get_user_membership_level($user_id);
    $security_status = check_user_security_status($user_id);
    $notifications = get_user_notifications($user_id, true);
    
    ob_start();
    ?>
    
    <div class="stock-scanner-dashboard">
        <?php if ($atts['show_notifications'] === 'true' && !empty($notifications)): ?>
        <!-- Security Notifications -->
        <div class="dashboard-notifications">
            <?php foreach ($notifications as $notification): ?>
            <div class="notification notification-<?php echo esc_attr($notification->type); ?> priority-<?php echo esc_attr($notification->priority); ?>">
                <div class="notification-header">
                    <span class="notification-icon">
                        <?php
                        switch ($notification->type) {
                            case 'account_banned': echo '🚫'; break;
                            case 'rate_limit': echo '⚠️'; break;
                            case 'security_alert': echo '🛡️'; break;
                            case 'account_unbanned': echo '✅'; break;
                            default: echo 'ℹ️';
                        }
                        ?>
                    </span>
                    <h4><?php echo esc_html($notification->title); ?></h4>
                    <button class="notification-close" data-notification-id="<?php echo esc_attr($notification->id); ?>">×</button>
                </div>
                <div class="notification-content">
                    <p><?php echo esc_html($notification->message); ?></p>
                    <small>
                        <?php echo wp_date('M j, Y H:i', strtotime($notification->created_at)); ?>
                    </small>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>
        
        <?php if ($security_status['status'] === 'banned'): ?>
        <!-- Account Banned Message -->
        <div class="security-alert banned-alert">
            <div class="alert-header">
                <span class="alert-icon">🚫</span>
                <h3>Account Suspended</h3>
            </div>
            <div class="alert-content">
                <p><strong>Your account has been suspended.</strong></p>
                <?php if ($security_status['message']): ?>
                <p>Reason: <?php echo esc_html($security_status['message']); ?></p>
                <?php endif; ?>
                <p>Please <a href="/contact/">contact support</a> if you believe this is an error.</p>
                <p><small>Suspended on: <?php echo wp_date('M j, Y H:i', strtotime($security_status['banned_at'])); ?></small></p>
            </div>
        </div>
        <?php return ob_get_clean(); endif; ?>
        
        <!-- Welcome Section -->
        <div class="dashboard-header">
            <h2>Welcome back, <?php echo esc_html($user->display_name); ?>! 📈</h2>
            <div class="membership-status">
                <span class="membership-badge membership-<?php echo esc_attr($membership_level); ?>">
                    <?php echo esc_html(ucfirst($membership_level)); ?> Plan
                </span>
                <?php if ($atts['show_security_status'] === 'true'): ?>
                <span class="security-status status-<?php echo esc_attr($security_status['status']); ?>">
                    <?php
                    switch ($security_status['status']) {
                        case 'active': echo '🔒 Secure'; break;
                        case 'banned': echo '🚫 Suspended'; break;
                        default: echo '👤 Guest';
                    }
                    ?>
                </span>
                <?php endif; ?>
            </div>
        </div>
        
        <!-- Usage Statistics with Security Indicators -->
        <div class="usage-stats">
            <h3>📊 Your Usage Statistics</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number"><?php echo number_format($usage['monthly_calls']); ?></div>
                    <div class="stat-label">API Calls This Month</div>
                    <div class="stat-limit">
                        Limit: <?php echo $usage['monthly_limit'] === -1 ? '∞' : number_format($usage['monthly_limit']); ?>
                    </div>
                    <div class="usage-bar">
                        <?php 
                        $percentage = $usage['monthly_limit'] > 0 ? ($usage['monthly_calls'] / $usage['monthly_limit']) * 100 : 0;
                        $bar_class = $percentage >= 90 ? 'critical' : ($percentage >= 75 ? 'warning' : 'normal');
                        ?>
                        <div class="usage-fill usage-<?php echo $bar_class; ?>" style="width: <?php echo min(100, $percentage); ?>%"></div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number"><?php echo number_format($usage['daily_calls']); ?></div>
                    <div class="stat-label">Calls Today</div>
                    <div class="stat-limit">
                        Limit: <?php echo $usage['daily_limit'] === -1 ? '∞' : number_format($usage['daily_limit']); ?>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number"><?php echo number_format($usage['hourly_calls']); ?></div>
                    <div class="stat-label">Calls This Hour</div>
                    <div class="stat-limit">
                        Limit: <?php echo $usage['hourly_limit'] === -1 ? '∞' : number_format($usage['hourly_limit']); ?>
                    </div>
                </div>
                
                <?php if ($usage['suspicious_calls'] > 0): ?>
                <div class="stat-card security-warning">
                    <div class="stat-number"><?php echo number_format($usage['suspicious_calls']); ?></div>
                    <div class="stat-label">⚠️ Flagged Requests</div>
                    <div class="stat-note">
                        Some requests were flagged as suspicious. 
                        <a href="/contact/">Contact support</a> if you think this is an error.
                    </div>
                </div>
                <?php endif; ?>
            </div>
        </div>
        
        <?php if ($membership_level === 'free'): ?>
        <!-- Upgrade Notice for Free Users -->
        <div class="upgrade-notice">
            <h3>🚀 Upgrade Your Plan</h3>
            <p>You're on the free plan with 15 API calls per month. Upgrade for more features!</p>
            <a href="/premium-plans/" class="btn btn-primary">View Premium Plans</a>
        </div>
        <?php endif; ?>
        
        <!-- Quick Stock Lookup (removed per UX update) -->
        <!-- Recent API Calls (removed per UX update) -->
    </div>
    
    <?php
    return ob_get_clean();
}
if (!shortcode_exists('stock_scanner_dashboard')) { add_shortcode('stock_scanner_dashboard', 'stock_scanner_dashboard_shortcode'); }

/**
 * Enhanced pricing shortcode (keep existing)
 */
function stock_scanner_pricing_shortcode($atts) {
    // Keep existing pricing shortcode implementation
    $atts = shortcode_atts(array(
        'highlight' => 'silver'
    ), $atts);
    
    ob_start();
    ?>
    <div class="pricing-table">        
        <div class="pricing-plan bronze-plan">
            <div class="plan-header">
                <h3>Bronze Plan</h3>
                <div class="price">$24.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>1,500 API calls per month</li>
                    <li>Advanced stock data</li>
                    <li>Email support</li>
                    <li>Historical data access</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="bronze" data-price="24.99" onclick="redirectToPayPal('bronze', '24.99')">
                    Upgrade to Bronze
                </button>
            </div>
        </div>
        
        <div class="pricing-plan silver-plan <?php echo $atts['highlight'] === 'silver' ? 'highlighted' : ''; ?>">
            <?php if ($atts['highlight'] === 'silver'): ?>
            <div class="plan-badge">Most Popular</div>
            <?php endif; ?>
            <div class="plan-header">
                <h3>Silver Plan</h3>
                <div class="price">$39.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>5,000 API calls per month</li>
                    <li>Real-time stock data</li>
                    <li>Email support</li>
                    <li>Advanced analytics</li>
                    <li>Custom alerts</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="silver" data-price="39.99" onclick="redirectToPayPal('silver', '39.99')">
                    Upgrade to Silver
                </button>
            </div>
        </div>
        
        <div class="pricing-plan gold-plan">
            <div class="plan-header">
                <h3>Gold Plan</h3>
                <div class="price">$89.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>Unlimited API calls</li>
                    <li>Premium stock data</li>
                    <li>Phone support</li>
                    <li>Advanced analytics</li>
                    <li>API access</li>
                    <li>White-label options</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="gold" data-price="89.99" onclick="redirectToPayPal('gold', '89.99')">
                    Upgrade to Gold
                </button>
            </div>
        </div>
    </div>
    
    <!-- Free Plan - Centered Below -->
    <div class="free-plan-section">
        <div class="pricing-plan free-plan-centered">
            <div class="plan-header">
                <h3>Free Plan</h3>
                <div class="price">$0<span>/month</span></div>
            </div>
            <div class="plan-features">
                <div class="limits-grid">
                    <div class="limit-item">
                        <span class="limit-number">15</span>
                        <span class="limit-label">Monthly Calls</span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-number">5</span>
                        <span class="limit-label">Daily Calls</span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-number">2</span>
                        <span class="limit-label">Hourly Calls</span>
                    </div>
                </div>
            </div>
            <div class="plan-footer">
                <a href="<?php echo wp_registration_url(); ?>" class="btn btn-outline">Get Started Free</a>
            </div>
        </div>
    </div>
    
    <script>
    function redirectToPayPal(plan, price) {
        if (confirm(`Upgrade to ${plan.charAt(0).toUpperCase() + plan.slice(1)} plan for $${price}/month?`)) {
            window.location.href = '/payment-success/?plan=' + plan + '&price=' + price;
        }
    }
    </script>
    
    <?php
    return ob_get_clean();
}
if (!shortcode_exists('stock_scanner_pricing')) { add_shortcode('stock_scanner_pricing', 'stock_scanner_pricing_shortcode'); }

/**
 * AJAX: Dismiss notification
 */
function handle_dismiss_notification_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $notification_id = intval($_POST['notification_id'] ?? 0);
    $user_id = get_current_user_id();
    
    if (!$user_id || !$notification_id) {
        wp_send_json_error('Invalid request');
    }
    
    $result = mark_notification_read($notification_id, $user_id);
    
    if ($result) {
        wp_send_json_success('Notification dismissed');
    } else {
        wp_send_json_error('Failed to dismiss notification');
    }
}
add_action('wp_ajax_dismiss_notification', 'handle_dismiss_notification_ajax');

/**
 * AJAX: Get user notifications
 */
function handle_get_notifications_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Not logged in');
    }
    
    $notifications = get_user_notifications($user_id, true);
    
    wp_send_json_success(array(
        'notifications' => $notifications,
        'count' => count($notifications)
    ));
}
add_action('wp_ajax_get_notifications', 'handle_get_notifications_ajax');

/**
 * AJAX handler for stock quotes
 */
function handle_stock_quote_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $symbol = sanitize_text_field($_POST['symbol'] ?? '');
    if (empty($symbol)) {
        wp_send_json_error('Stock symbol is required');
    }
    
    $user_id = get_current_user_id();
    if (!can_user_make_api_call($user_id)) {
        wp_send_json_error(array(
            'message' => 'API limit reached. Please upgrade your plan for more calls.',
            'upgrade_url' => '/premium-plans/'
        ));
    }
    
    // Check security status
    $security_status = check_user_security_status($user_id);
    if ($security_status['status'] === 'banned') {
        wp_send_json_error(array(
            'message' => 'Account suspended: ' . $security_status['message'],
            'contact_url' => '/contact/'
        ));
    }
    
    // Get real stock data from Django backend
    $response = make_backend_api_request("stock/{$symbol}/");
    
    if (is_wp_error($response) || empty($response)) {
        error_log("Stock API fallback for symbol: {$symbol}. Error: " . (is_wp_error($response) ? $response->get_error_message() : 'Empty response'));
        
        // Generate sample data for popular stocks as fallback
        $sample_stocks = array(
            'AAPL' => array('name' => 'Apple Inc.', 'current_price' => 175.43, 'price_change_today' => 2.15, 'change_percent' => 1.24, 'volume' => 52300000, 'market_cap' => 2800000000000, 'pe_ratio' => 28.5),
            'GOOGL' => array('name' => 'Alphabet Inc.', 'current_price' => 138.21, 'price_change_today' => -1.45, 'change_percent' => -1.04, 'volume' => 25700000, 'market_cap' => 1700000000000, 'pe_ratio' => 25.2),
            'TSLA' => array('name' => 'Tesla Inc.', 'current_price' => 248.50, 'price_change_today' => 8.32, 'change_percent' => 3.46, 'volume' => 95200000, 'market_cap' => 789000000000, 'pe_ratio' => 65.4),
            'MSFT' => array('name' => 'Microsoft Corp.', 'current_price' => 378.85, 'price_change_today' => 4.67, 'change_percent' => 1.25, 'volume' => 28400000, 'market_cap' => 2800000000000, 'pe_ratio' => 31.8),
            'NVDA' => array('name' => 'NVIDIA Corp.', 'current_price' => 875.28, 'price_change_today' => 15.42, 'change_percent' => 1.79, 'volume' => 38900000, 'market_cap' => 2200000000000, 'pe_ratio' => 72.1),
            'AMZN' => array('name' => 'Amazon.com Inc.', 'current_price' => 145.86, 'price_change_today' => 3.21, 'change_percent' => 2.25, 'volume' => 35800000, 'market_cap' => 1520000000000, 'pe_ratio' => 43.2),
            'META' => array('name' => 'Meta Platforms Inc.', 'current_price' => 298.47, 'price_change_today' => -2.15, 'change_percent' => -0.71, 'volume' => 18900000, 'market_cap' => 758000000000, 'pe_ratio' => 23.1),
            'IWM' => array('name' => 'iShares Russell 2000 ETF', 'current_price' => 208.45, 'price_change_today' => 1.75, 'change_percent' => 0.85, 'volume' => 42100000, 'market_cap' => 32000000000, 'pe_ratio' => null)
        );
        
        if (isset($sample_stocks[strtoupper($symbol)])) {
            $response = $sample_stocks[strtoupper($symbol)];
            $response['ticker'] = strtoupper($symbol);
            $response['exchange'] = 'NASDAQ';
            $response['is_fallback'] = true;
        } else {
            // Return error for unknown symbols when backend is unavailable
            wp_send_json_error(array(
                'message' => "Stock symbol '{$symbol}' not found. Real-time data service is temporarily unavailable.",
                'suggestion' => 'Please try one of these popular symbols: AAPL, GOOGL, TSLA, MSFT, NVDA, AMZN, META, IWM'
            ));
            return;
        }
    }
    
    // Format response data
    $data = array(
        'symbol' => strtoupper($symbol),
        'name' => $response['name'] ?? $response['company_name'] ?? $symbol,
        'price' => number_format(floatval($response['current_price'] ?? 0), 2),
        'change' => number_format(floatval($response['price_change_today'] ?? 0), 2),
        'change_percent' => number_format(floatval($response['change_percent'] ?? 0), 2),
        'volume' => number_format(intval($response['volume'] ?? 0)),
        'market_cap' => isset($response['market_cap']) ? number_format(floatval($response['market_cap'])) : null,
        'pe_ratio' => $response['pe_ratio'] ?? null,
        'high_52_week' => $response['high_52_week'] ?? null,
        'low_52_week' => $response['low_52_week'] ?? null,
        'exchange' => $response['exchange'] ?? null,
        'timestamp' => current_time('mysql'),
        'usage_remaining' => get_user_api_usage($user_id)
    );
    
    wp_send_json_success($data);
}
add_action('wp_ajax_stock_scanner_get_quote', 'handle_stock_quote_ajax');
add_action('wp_ajax_nopriv_stock_scanner_get_quote', 'handle_stock_quote_ajax');

/**
 * AJAX handler for recent API calls
 */
function handle_recent_calls_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to view recent calls.');
        return;
    }
    
    if (!is_stock_scanner_plugin_active()) {
        wp_send_json_success(array('calls' => array()));
        return;
    }
    
    global $wpdb;
    $table_name = $wpdb->prefix . 'stock_scanner_usage';
    
    $recent_calls = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM $table_name WHERE user_id = %d ORDER BY created_at DESC LIMIT 10",
        $user_id
    ));
    
    wp_send_json_success(array('calls' => $recent_calls));
}
add_action('wp_ajax_get_recent_calls', 'handle_recent_calls_ajax');

/**
 * AJAX handler for membership upgrades
 */
function handle_membership_upgrade_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to upgrade your membership.');
        return;
    }
    
    $plan = sanitize_text_field($_POST['plan']);
    $price = floatval($_POST['price']);
    
    if (!in_array($plan, array('bronze', 'silver', 'gold'))) {
        wp_send_json_error('Invalid plan selected.');
        return;
    }
    
    // Here you would integrate with PayPal or your payment processor
    // For now, we'll return success with payment URL
    
    $payment_data = array(
        'plan' => $plan,
        'price' => $price,
        'user_id' => $user_id,
        'return_url' => home_url('/payment-success/'),
        'cancel_url' => home_url('/premium-plans/'),
        'payment_url' => 'https://www.paypal.com/cgi-bin/webscr' // Replace with actual PayPal URL
    );
    
    wp_send_json_success($payment_data);
}
add_action('wp_ajax_upgrade_membership', 'handle_membership_upgrade_ajax');

/**
 * AJAX handler for adding to watchlist
 */
function handle_add_to_watchlist_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to add stocks to your watchlist.');
        return;
    }
    
    $symbol = sanitize_text_field($_POST['symbol']);
    if (empty($symbol)) {
        wp_send_json_error('Please provide a valid stock symbol.');
        return;
    }
    
    // Get current watchlist
    $watchlist = get_user_meta($user_id, 'stock_watchlist', true) ?: array();
    
    // Add symbol if not already in watchlist
    if (!in_array($symbol, $watchlist)) {
        $watchlist[] = $symbol;
        update_user_meta($user_id, 'stock_watchlist', $watchlist);
        wp_send_json_success(array('message' => 'Added ' . $symbol . ' to watchlist'));
    } else {
        wp_send_json_error('Stock is already in your watchlist.');
    }
}
add_action('wp_ajax_add_to_watchlist', 'handle_add_to_watchlist_ajax');

/**
 * AJAX handler for removing from watchlist
 */
function handle_remove_from_watchlist_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to manage your watchlist.');
        return;
    }
    
    $symbol = sanitize_text_field($_POST['symbol']);
    if (empty($symbol)) {
        wp_send_json_error('Please provide a valid stock symbol.');
        return;
    }
    
    // Get current watchlist
    $watchlist = get_user_meta($user_id, 'stock_watchlist', true) ?: array();
    
    // Remove symbol from watchlist
    $watchlist = array_diff($watchlist, array($symbol));
    update_user_meta($user_id, 'stock_watchlist', $watchlist);
    
    wp_send_json_success(array('message' => 'Removed ' . $symbol . ' from watchlist'));
}
add_action('wp_ajax_remove_from_watchlist', 'handle_remove_from_watchlist_ajax');

/**
 * AJAX handler for market overview
 */
function handle_market_overview_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to view market overview.');
        return;
    }
    
    if (!can_user_make_api_call($user_id)) {
        wp_send_json_error('API limit reached. Please upgrade your plan.');
        return;
    }
    
    // Log API usage
    if (is_stock_scanner_plugin_active()) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'stock_scanner_usage';
        $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'endpoint' => 'market_overview',
                'symbol' => 'MARKET_DATA',
                'created_at' => current_time('mysql')
            )
        );
    }
    
    // Get real market data from Django backend
    $response = make_backend_api_request('market-stats/');
    
    if (is_wp_error($response) || empty($response)) {
        // Fallback to sample data if backend is not available
        $market_data = array(
            'market_overview' => array(
                'total_stocks' => 3500,
                'gainers' => 1250,
                'losers' => 980,
                'unchanged' => 1270,
                'gainer_percentage' => 35.7
            ),
            'message' => 'Using sample data - Backend unavailable'
        );
    } else {
        $market_data = $response;
    }
    
    $html = '<div class="market-overview-grid">';
    
    // Check if we have market overview data
    if (isset($market_data['market_overview'])) {
        $overview = $market_data['market_overview'];
        $html .= '<div class="market-summary">';
        $html .= '<div class="market-item">';
        $html .= '<h4>Market Summary</h4>';
        $html .= '<p class="market-name">Total Stocks: ' . $overview['total_stocks'] . '</p>';
        $html .= '<div class="market-stats">';
        $html .= '<span class="stat positive">Gainers: ' . $overview['gainers'] . '</span>';
        $html .= '<span class="stat negative">Losers: ' . $overview['losers'] . '</span>';
        $html .= '<span class="stat neutral">Unchanged: ' . $overview['unchanged'] . '</span>';
        $html .= '</div>';
        $html .= '</div>';
        $html .= '</div>';
    }
    
    $html .= '</div>';
    
    wp_send_json_success(array('data' => $market_data, 'html' => $html));
}
add_action('wp_ajax_get_market_overview', 'handle_market_overview_ajax');

/**
 * AJAX handler for market movers (gainers, losers, most active)
 */
function handle_market_movers_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to view market data.');
        return;
    }
    
    if (!can_user_make_api_call($user_id)) {
        wp_send_json_error('API limit reached. Please upgrade your plan.');
        return;
    }
    
    // Log API usage
    if (is_stock_scanner_plugin_active()) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'stock_scanner_usage';
        $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'endpoint' => 'market_movers',
                'symbol' => 'MARKET_MOVERS',
                'created_at' => current_time('mysql')
            )
        );
    }
    
    // Get real trending data from Django backend
    $response = make_backend_api_request('trending/');
    
    if (is_wp_error($response) || empty($response)) {
        // Fallback to sample data if backend is not available
        $fallback_data = array(
            'top_gainers' => array(
                array('ticker' => 'NVDA', 'name' => 'NVIDIA Corp', 'current_price' => 875.28, 'price_change_today' => 45.32, 'change_percent' => 5.46, 'volume' => 38900000),
                array('ticker' => 'TSLA', 'name' => 'Tesla Inc', 'current_price' => 248.50, 'price_change_today' => 18.75, 'change_percent' => 8.16, 'volume' => 95200000),
                array('ticker' => 'AMD', 'name' => 'Advanced Micro Devices', 'current_price' => 154.20, 'price_change_today' => 12.80, 'change_percent' => 9.05, 'volume' => 42100000)
            ),
            'most_active' => array(
                array('ticker' => 'AAPL', 'name' => 'Apple Inc', 'current_price' => 175.43, 'price_change_today' => 2.15, 'change_percent' => 1.24, 'volume' => 152300000),
                array('ticker' => 'TSLA', 'name' => 'Tesla Inc', 'current_price' => 248.50, 'price_change_today' => 18.75, 'change_percent' => 8.16, 'volume' => 95200000),
                array('ticker' => 'SQQQ', 'name' => 'ProShares UltraPro Short QQQ', 'current_price' => 8.45, 'price_change_today' => -0.25, 'change_percent' => -2.87, 'volume' => 89400000)
            ),
            'message' => 'Using sample data - Backend unavailable'
        );
        wp_send_json_success($fallback_data);
        return;
    }
    
    wp_send_json_success($response);
}
add_action('wp_ajax_get_market_movers', 'handle_market_movers_ajax');

/**
 * AJAX handler for major indices data
 */
function handle_major_indices_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to view market data.');
        return;
    }
    
    if (!can_user_make_api_call($user_id)) {
        wp_send_json_error('API limit reached. Please upgrade your plan.');
        return;
    }
    
    // Log API usage
    if (is_stock_scanner_plugin_active()) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'stock_scanner_usage';
        $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'endpoint' => 'major_indices',
                'symbol' => 'INDICES',
                'created_at' => current_time('mysql')
            )
        );
    }
    
    // Get major indices symbols
    $indices = ['SPY', 'QQQ', 'DIA', 'IWM', 'VIX', 'DXY'];
    $indices_data = array();
    
    foreach ($indices as $symbol) {
        $response = make_backend_api_request("stock/{$symbol}/");
        if (!is_wp_error($response) && !empty($response)) {
            $indices_data[] = $response;
        }
    }
    
    // If no data from backend, provide fallback sample data
    if (empty($indices_data)) {
        $indices_data = array(
            array('ticker' => 'SPY', 'name' => 'S&P 500 ETF', 'current_price' => 475.50, 'price_change_today' => 2.85, 'change_percent' => 0.60),
            array('ticker' => 'QQQ', 'name' => 'NASDAQ-100 ETF', 'current_price' => 378.45, 'price_change_today' => 6.30, 'change_percent' => 1.69),
            array('ticker' => 'DIA', 'name' => 'Dow Jones ETF', 'current_price' => 385.80, 'price_change_today' => -1.20, 'change_percent' => -0.31),
            array('ticker' => 'IWM', 'name' => 'Russell 2000 ETF', 'current_price' => 208.45, 'price_change_today' => 1.75, 'change_percent' => 0.85),
            array('ticker' => 'VIX', 'name' => 'Volatility Index', 'current_price' => 14.23, 'price_change_today' => -0.85, 'change_percent' => -5.64),
            array('ticker' => 'DXY', 'name' => 'US Dollar Index', 'current_price' => 103.45, 'price_change_today' => 0.12, 'change_percent' => 0.12)
        );
    }
    
    wp_send_json_success($indices_data);
}
add_action('wp_ajax_get_major_indices', 'handle_major_indices_ajax');

/**
 * AJAX handler for contact form
 */
function handle_contact_form_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $name = sanitize_text_field($_POST['name']);
    $email = sanitize_email($_POST['email']);
    $subject = sanitize_text_field($_POST['subject']);
    $message = sanitize_textarea_field($_POST['message']);
    
    if (empty($name) || empty($email) || empty($subject) || empty($message)) {
        wp_send_json_error('Please fill in all required fields.');
        return;
    }
    
    if (!is_email($email)) {
        wp_send_json_error('Please provide a valid email address.');
        return;
    }
    
    // Send email
    $to = get_option('admin_email');
    $email_subject = 'Contact Form: ' . $subject;
    $email_message = "Name: {$name}\n";
    $email_message .= "Email: {$email}\n";
    $email_message .= "Subject: {$subject}\n\n";
    $email_message .= "Message:\n{$message}";
    
    $headers = array('Content-Type: text/plain; charset=UTF-8');
    
    $sent = wp_mail($to, $email_subject, $email_message, $headers);
    
    if ($sent) {
        wp_send_json_success(array('message' => 'Thank you for your message. We will get back to you soon!'));
    } else {
        wp_send_json_error('Failed to send message. Please try again later.');
    }
}
add_action('wp_ajax_submit_contact_form', 'handle_contact_form_ajax');
add_action('wp_ajax_nopriv_submit_contact_form', 'handle_contact_form_ajax');

/**
 * AJAX handler for usage stats
 */
function handle_usage_stats_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to view usage stats.');
        return;
    }
    
    $usage = get_user_api_usage($user_id);
    wp_send_json_success($usage);
}
add_action('wp_ajax_get_usage_stats', 'handle_usage_stats_ajax');

/**
 * Stock Lookup Tool Shortcode
 */
function stock_lookup_tool_shortcode($atts) {
    if (!is_stock_scanner_plugin_active()) {
        return '<div class="plugin-notice">Stock Scanner plugin is not active.</div>';
    }
    
    // Render the dashboard shortcode rather than outputting the literal tag
    return do_shortcode('[stock_scanner_dashboard]');
}
if (!shortcode_exists('stock_lookup_tool')) { add_shortcode('stock_lookup_tool', 'stock_lookup_tool_shortcode'); }

/**
 * Stock News Feed Shortcode
 */
function stock_news_feed_shortcode($atts) {
    return '<div id="stock-news-feed" class="stock-news-container">
        <div class="news-loading">Loading latest stock news...</div>
    </div>';
}
if (!shortcode_exists('stock_news_feed')) { add_shortcode('stock_news_feed', 'stock_news_feed_shortcode'); }

/**
 * Stock Screener Tool Shortcode
 */
function stock_screener_tool_shortcode($atts) {
    return '<div id="stock-screener-tool" class="screener-container">
        <div class="screener-loading">Loading stock screening tools...</div>
    </div>';
}
if (!shortcode_exists('stock_screener_tool')) { add_shortcode('stock_screener_tool', 'stock_screener_tool_shortcode'); }

/**
 * Market Overview Dashboard Shortcode
 */
function market_overview_dashboard_shortcode($atts) {
    return '<div id="market-overview-dashboard" class="market-dashboard">
        <div class="market-loading">Loading market overview...</div>
    </div>';
}
if (!shortcode_exists('market_overview_dashboard')) { add_shortcode('market_overview_dashboard', 'market_overview_dashboard_shortcode'); }

/**
 * Technical Analysis Tools Shortcode
 */
function technical_analysis_tools_shortcode($atts) {
    return '<div id="technical-analysis-tools" class="technical-tools">
        <div class="technical-loading">Loading technical analysis tools...</div>
    </div>';
}
if (!shortcode_exists('technical_analysis_tools')) { add_shortcode('technical_analysis_tools', 'technical_analysis_tools_shortcode'); }

/**
 * Options Data Viewer Shortcode
 */
function options_data_viewer_shortcode($atts) {
    return '<div id="options-data-viewer" class="options-container">
        <div class="options-loading">Loading options data viewer...</div>
    </div>';
}
if (!shortcode_exists('options_data_viewer')) { add_shortcode('options_data_viewer', 'options_data_viewer_shortcode'); }

/**
 * Level 2 Data Viewer Shortcode
 */
function level2_data_viewer_shortcode($atts) {
    return '<div id="level2-data-viewer" class="level2-container">
        <div class="level2-loading">Loading Level 2 data viewer...</div>
    </div>';
}
if (!shortcode_exists('level2_data_viewer')) { add_shortcode('level2_data_viewer', 'level2_data_viewer_shortcode'); }

/**
 * Stock Watchlist Manager Shortcode
 */
function stock_watchlist_manager_shortcode($atts) {
    return '<div id="watchlist-manager" class="watchlist-container">
        <div class="watchlist-loading">Loading watchlist manager...</div>
    </div>';
}
if (!shortcode_exists('stock_watchlist_manager')) { add_shortcode('stock_watchlist_manager', 'stock_watchlist_manager_shortcode'); }

/**
 * User Account Manager Shortcode
 */
function user_account_manager_shortcode($atts) {
    return '[stock_scanner_dashboard]'; // Reuse existing dashboard functionality
}
if (!shortcode_exists('user_account_manager')) { add_shortcode('user_account_manager', 'user_account_manager_shortcode'); }

/**
 * Advanced Contact Form Shortcode
 */
function contact_form_advanced_shortcode($atts) {
    return '<div id="advanced-contact-form" class="contact-form-container">
        <form id="stock-scanner-contact-form" class="contact-form">
            <div class="form-group">
                <label for="contact-name">Name *</label>
                <input type="text" id="contact-name" name="name" required>
            </div>
            <div class="form-group">
                <label for="contact-email">Email *</label>
                <input type="email" id="contact-email" name="email" required>
            </div>
            <div class="form-group">
                <label for="contact-subject">Subject *</label>
                <select id="contact-subject" name="subject" required>
                    <option value="">Select a topic</option>
                    <option value="general">General Inquiry</option>
                    <option value="technical">Technical Support</option>
                    <option value="billing">Billing Question</option>
                    <option value="feature">Feature Request</option>
                    <option value="bug">Bug Report</option>
                </select>
            </div>
            <div class="form-group">
                <label for="contact-message">Message *</label>
                <textarea id="contact-message" name="message" rows="6" required></textarea>
            </div>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Send Message</button>
            </div>
        </form>
    </div>';
}
add_shortcode('contact_form_advanced', 'contact_form_advanced_shortcode');

/**
 * Screener Saved Screens (membership-gated)
 */
function stock_scanner_require_membership_level($min_level = 'silver') {
    if (!is_user_logged_in()) {
        wp_send_json_error('Login required');
    }
    if (!function_exists('get_user_membership_level')) {
        wp_send_json_error('Membership unavailable');
    }
    $level = get_user_membership_level(get_current_user_id());
    $order = ['free'=>0,'bronze'=>1,'silver'=>2,'gold'=>3];
    if (($order[$level] ?? -1) < ($order[$min_level] ?? 99)) {
        wp_send_json_error('Upgrade required');
    }
}

function screener_sanitize_name($name){
    $name = sanitize_text_field($name);
    return wp_trim_words($name, 8, '');
}

function ajax_screener_list_screens(){
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    stock_scanner_require_membership_level('silver');
    global $wpdb; $uid = get_current_user_id();
    $table = $wpdb->prefix . 'stock_scanner_screens';
    $rows = $wpdb->get_results($wpdb->prepare("SELECT id,name,created_at,updated_at FROM $table WHERE user_id=%d ORDER BY updated_at DESC LIMIT 50", $uid), ARRAY_A);
    wp_send_json_success($rows ?: []);
}
add_action('wp_ajax_screener_list_screens', 'ajax_screener_list_screens');

function ajax_screener_save_screen(){
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    stock_scanner_require_membership_level('silver');
    global $wpdb; $uid = get_current_user_id();
    $name = screener_sanitize_name($_POST['name'] ?? '');
    $payload = sanitize_text_field($_POST['payload'] ?? '');
    if (!$name || !$payload) wp_send_json_error('Invalid');
    $table = $wpdb->prefix . 'stock_scanner_screens';
    $wpdb->insert($table, [
        'user_id'=>$uid,
        'name'=>$name,
        'payload'=>$payload,
        'created_at'=>current_time('mysql'),
        'updated_at'=>current_time('mysql')
    ], ['%d','%s','%s','%s','%s']);
    wp_send_json_success(['id'=>$wpdb->insert_id]);
}
add_action('wp_ajax_screener_save_screen', 'ajax_screener_save_screen');

function ajax_screener_get_screen(){
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    stock_scanner_require_membership_level('silver');
    global $wpdb; $uid = get_current_user_id();
    $id = absint($_POST['id'] ?? 0);
    if (!$id) wp_send_json_error('Invalid');
    $table = $wpdb->prefix . 'stock_scanner_screens';
    $row = $wpdb->get_row($wpdb->prepare("SELECT id,name,payload FROM $table WHERE id=%d AND user_id=%d", $id, $uid), ARRAY_A);
    if (!$row) wp_send_json_error('Not found');
    wp_send_json_success($row);
}
add_action('wp_ajax_screener_get_screen', 'ajax_screener_get_screen');

function ajax_screener_delete_screen(){
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    stock_scanner_require_membership_level('silver');
    global $wpdb; $uid = get_current_user_id();
    $id = absint($_POST['id'] ?? 0);
    if (!$id) wp_send_json_error('Invalid');
    $table = $wpdb->prefix . 'stock_scanner_screens';
    $wpdb->delete($table, ['id'=>$id,'user_id'=>$uid], ['%d','%d']);
    wp_send_json_success(true);
}
add_action('wp_ajax_screener_delete_screen', 'ajax_screener_delete_screen');

?>