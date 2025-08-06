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
        
        <!-- Quick Stock Lookup -->
        <div class="quick-lookup">
            <h3>🔍 Quick Stock Lookup</h3>
            <div class="lookup-form">
                <input type="text" id="stock-symbol" placeholder="Enter stock symbol (e.g., AAPL)" maxlength="10" />
                <button id="get-stock-quote" class="btn btn-primary">Get Quote</button>
            </div>
            <div id="stock-result" class="stock-result"></div>
        </div>
        
        <!-- Recent API Calls -->
        <div class="recent-calls">
            <h3>📈 Recent Activity</h3>
            <div id="recent-calls-list" class="calls-list">
                <div class="loading">Loading recent activity...</div>
            </div>
        </div>
    </div>
    
    <style>
    /* Enhanced dashboard styles with security indicators */
    .stock-scanner-dashboard {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Security Notifications */
    .dashboard-notifications {
        margin-bottom: 30px;
    }
    
    .notification {
        background: #fff;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .notification-rate_limit {
        border-left: 4px solid #dba617;
    }
    
    .notification-account_banned {
        border-left: 4px solid #d63638;
    }
    
    .notification-security_alert {
        border-left: 4px solid #2271b1;
    }
    
    .notification-account_unbanned {
        border-left: 4px solid #00a32a;
    }
    
    .priority-high {
        animation: pulse-notification 2s infinite;
    }
    
    @keyframes pulse-notification {
        0%, 100% { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        50% { box-shadow: 0 4px 12px rgba(214, 54, 56, 0.3); }
    }
    
    .notification-header {
        display: flex;
        align-items: center;
        padding: 15px 20px 10px;
        background: #f8f9fa;
    }
    
    .notification-icon {
        font-size: 1.5rem;
        margin-right: 10px;
    }
    
    .notification-header h4 {
        flex: 1;
        margin: 0;
        font-size: 1.1rem;
        color: #1d2327;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #646970;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-close:hover {
        color: #d63638;
    }
    
    .notification-content {
        padding: 10px 20px 15px;
    }
    
    .notification-content p {
        margin: 0 0 10px;
        line-height: 1.5;
    }
    
    .notification-content small {
        color: #646970;
        font-size: 0.9rem;
    }
    
    /* Security Alerts */
    .security-alert {
        background: linear-gradient(135deg, #d63638 0%, #b91c1c 100%);
        color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .alert-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    
    .alert-icon {
        font-size: 2rem;
        margin-right: 10px;
    }
    
    .alert-header h3 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    .alert-content p {
        margin: 10px 0;
        line-height: 1.6;
    }
    
    .alert-content a {
        color: white;
        text-decoration: underline;
    }
    
    /* Dashboard Header */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid #e1e1e1;
    }
    
    .dashboard-header h2 {
        margin: 0;
        color: #1d2327;
        font-size: 1.8rem;
    }
    
    .membership-status {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .security-status {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-active {
        background: #d1e7dd;
        color: #0f5132;
    }
    
    .status-banned {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e1e1e1;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .security-warning {
        border-color: #dba617;
        background: #fefce8;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2271b1;
        margin-bottom: 5px;
    }
    
    .security-warning .stat-number {
        color: #dba617;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #646970;
        margin-bottom: 10px;
    }
    
    .stat-limit {
        font-size: 0.8rem;
        color: #646970;
        margin-bottom: 10px;
    }
    
    .stat-note {
        font-size: 0.8rem;
        color: #92400e;
        line-height: 1.4;
        margin-top: 10px;
    }
    
    .stat-note a {
        color: #92400e;
        text-decoration: underline;
    }
    
    /* Usage Bar */
    .usage-bar {
        width: 100%;
        height: 6px;
        background: #e1e1e1;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .usage-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .usage-normal {
        background: #00a32a;
    }
    
    .usage-warning {
        background: #dba617;
    }
    
    .usage-critical {
        background: #d63638;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
        }
        
        .membership-status {
            flex-wrap: wrap;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .notification-header {
            padding: 12px 15px 8px;
        }
        
        .notification-content {
            padding: 8px 15px 12px;
        }
    }
    </style>
    
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_dashboard', 'stock_scanner_dashboard_shortcode');

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
        <div class="pricing-plan free-plan">
            <div class="plan-header">
                <h3>🆓 Free Plan</h3>
                <div class="price">$0<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>✅ 15 API calls per month</li>
                    <li>✅ Basic stock data</li>
                    <li>✅ Email support</li>
                    <li>✅ Community access</li>
                </ul>
            </div>
            <div class="plan-footer">
                <a href="<?php echo wp_registration_url(); ?>" class="btn btn-outline">Get Started</a>
            </div>
        </div>
        
        <div class="pricing-plan bronze-plan">
            <div class="plan-header">
                <h3>🥉 Bronze Plan</h3>
                <div class="price">$9.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>✅ 1,500 API calls per month</li>
                    <li>✅ Advanced stock data</li>
                    <li>✅ Priority support</li>
                    <li>✅ Historical data access</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="bronze" data-price="9.99">
                    Upgrade to Bronze
                </button>
            </div>
        </div>
        
        <div class="pricing-plan silver-plan <?php echo $atts['highlight'] === 'silver' ? 'highlighted' : ''; ?>">
            <?php if ($atts['highlight'] === 'silver'): ?>
            <div class="plan-badge">Most Popular</div>
            <?php endif; ?>
            <div class="plan-header">
                <h3>🥈 Silver Plan</h3>
                <div class="price">$19.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>✅ 5,000 API calls per month</li>
                    <li>✅ Real-time stock data</li>
                    <li>✅ Priority support</li>
                    <li>✅ Advanced analytics</li>
                    <li>✅ Custom alerts</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="silver" data-price="19.99">
                    Upgrade to Silver
                </button>
            </div>
        </div>
        
        <div class="pricing-plan gold-plan">
            <div class="plan-header">
                <h3>🥇 Gold Plan</h3>
                <div class="price">$49.99<span>/month</span></div>
            </div>
            <div class="plan-features">
                <ul>
                    <li>✅ Unlimited API calls</li>
                    <li>✅ Premium stock data</li>
                    <li>✅ Phone support</li>
                    <li>✅ Advanced analytics</li>
                    <li>✅ API access</li>
                    <li>✅ White-label options</li>
                </ul>
            </div>
            <div class="plan-footer">
                <button class="btn btn-primary upgrade-btn" data-plan="gold" data-price="49.99">
                    Upgrade to Gold
                </button>
            </div>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_pricing', 'stock_scanner_pricing_shortcode');

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
    
    // Mock stock data
    $data = array(
        'symbol' => strtoupper($symbol),
        'price' => number_format(rand(10, 500) + (rand(0, 99) / 100), 2),
        'change' => number_format((rand(-10, 10) + (rand(0, 99) / 100)), 2),
        'change_percent' => number_format((rand(-5, 5) + (rand(0, 99) / 100)), 2),
        'volume' => number_format(rand(100000, 10000000)),
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
    
    // Mock market data (replace with real API call)
    $market_data = array(
        'SPY' => array(
            'symbol' => 'SPY',
            'name' => 'S&P 500 ETF',
            'price' => number_format(rand(400, 500) + (rand(0, 99) / 100), 2),
            'change' => number_format((rand(-10, 10) + (rand(0, 99) / 100)), 2),
            'change_percent' => number_format((rand(-3, 3) + (rand(0, 99) / 100)), 2)
        ),
        'QQQ' => array(
            'symbol' => 'QQQ',
            'name' => 'NASDAQ-100 ETF',
            'price' => number_format(rand(300, 400) + (rand(0, 99) / 100), 2),
            'change' => number_format((rand(-8, 8) + (rand(0, 99) / 100)), 2),
            'change_percent' => number_format((rand(-2, 2) + (rand(0, 99) / 100)), 2)
        ),
        'DIA' => array(
            'symbol' => 'DIA',
            'name' => 'Dow Jones ETF',
            'price' => number_format(rand(350, 450) + (rand(0, 99) / 100), 2),
            'change' => number_format((rand(-6, 6) + (rand(0, 99) / 100)), 2),
            'change_percent' => number_format((rand(-2, 2) + (rand(0, 99) / 100)), 2)
        )
    );
    
    $html = '<div class="market-overview-grid">';
    foreach ($market_data as $data) {
        $changeClass = floatval($data['change']) >= 0 ? 'positive' : 'negative';
        $changeSymbol = floatval($data['change']) >= 0 ? '+' : '';
        
        $html .= '<div class="market-item">';
        $html .= '<h4>' . $data['symbol'] . '</h4>';
        $html .= '<p class="market-name">' . $data['name'] . '</p>';
        $html .= '<div class="market-price">$' . $data['price'] . '</div>';
        $html .= '<div class="market-change ' . $changeClass . '">';
        $html .= $changeSymbol . '$' . $data['change'] . ' (' . $changeSymbol . $data['change_percent'] . '%)';
        $html .= '</div>';
        $html .= '</div>';
    }
    $html .= '</div>';
    
    wp_send_json_success(array('html' => $html));
}
add_action('wp_ajax_get_market_overview', 'handle_market_overview_ajax');

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

// Add all other existing AJAX handlers here...
?>