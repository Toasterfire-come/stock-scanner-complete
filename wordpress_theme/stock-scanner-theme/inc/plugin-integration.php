<?php
/**
 * Stock Scanner Plugin Integration
 * Handles all communication between theme and plugin
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
    
    if (!is_stock_scanner_plugin_active() || !$user_id) {
        return 'free';
    }
    
    return get_user_meta($user_id, 'membership_level', true) ?: 'free';
}

/**
 * Get user API usage
 */
function get_user_api_usage($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!is_stock_scanner_plugin_active() || !$user_id) {
        return array(
            'monthly_calls' => 0,
            'daily_calls' => 0,
            'hourly_calls' => 0,
            'monthly_limit' => 15
        );
    }
    
    global $wpdb;
    $table_name = $wpdb->prefix . 'stock_scanner_usage';
    
    $current_month = date('Y-m');
    $current_date = date('Y-m-d');
    $current_hour = date('Y-m-d H:00:00');
    
    $monthly_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table_name WHERE user_id = %d AND DATE_FORMAT(created_at, '%%Y-%%m') = %s",
        $user_id, $current_month
    ));
    
    $daily_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table_name WHERE user_id = %d AND DATE(created_at) = %s",
        $user_id, $current_date
    ));
    
    $hourly_calls = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM $table_name WHERE user_id = %d AND created_at >= %s",
        $user_id, $current_hour
    ));
    
    $membership_level = get_user_membership_level($user_id);
    $limits = get_membership_limits($membership_level);
    
    return array(
        'monthly_calls' => intval($monthly_calls),
        'daily_calls' => intval($daily_calls),
        'hourly_calls' => intval($hourly_calls),
        'monthly_limit' => $limits['monthly'],
        'daily_limit' => $limits['daily'],
        'hourly_limit' => $limits['hourly']
    );
}

/**
 * Get membership limits
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
 * Check if user can make API call
 */
function can_user_make_api_call($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $usage = get_user_api_usage($user_id);
    $membership_level = get_user_membership_level($user_id);
    $limits = get_membership_limits($membership_level);
    
    // Check if unlimited (gold)
    if ($limits['monthly'] === -1) {
        return true;
    }
    
    // Check monthly limit
    if ($usage['monthly_calls'] >= $limits['monthly']) {
        return false;
    }
    
    // Check daily limit
    if ($usage['daily_calls'] >= $limits['daily']) {
        return false;
    }
    
    // Check hourly limit
    if ($usage['hourly_calls'] >= $limits['hourly']) {
        return false;
    }
    
    return true;
}

/**
 * Dashboard shortcode
 */
function stock_scanner_dashboard_shortcode($atts) {
    if (!is_user_logged_in()) {
        return '<p>Please <a href="' . wp_login_url(get_permalink()) . '">login</a> to view your dashboard.</p>';
    }
    
    $user_id = get_current_user_id();
    $usage = get_user_api_usage($user_id);
    $membership_level = get_user_membership_level($user_id);
    $limits = get_membership_limits($membership_level);
    
    $monthly_percentage = $limits['monthly'] > 0 ? ($usage['monthly_calls'] / $limits['monthly']) * 100 : 0;
    $daily_percentage = $limits['daily'] > 0 ? ($usage['daily_calls'] / $limits['daily']) * 100 : 0;
    
    ob_start();
    ?>
    <div class="stock-scanner-dashboard">
        <div class="dashboard-header">
            <h2>Your Stock Scanner Dashboard</h2>
            <div class="membership-badge membership-<?php echo esc_attr($membership_level); ?>">
                <?php echo ucfirst($membership_level); ?> Member
            </div>
        </div>
        
        <div class="usage-stats">
            <div class="usage-card">
                <h3>Monthly Usage</h3>
                <div class="usage-bar">
                    <div class="usage-fill" style="width: <?php echo min(100, $monthly_percentage); ?>%"></div>
                </div>
                <p>
                    <?php echo esc_html($usage['monthly_calls']); ?> / 
                    <?php echo $limits['monthly'] === -1 ? 'Unlimited' : esc_html($limits['monthly']); ?> calls
                </p>
                <?php if ($monthly_percentage >= 75 && $limits['monthly'] > 0): ?>
                    <div class="usage-warning">
                        <?php if ($monthly_percentage >= 90): ?>
                            <span class="warning-high">⚠️ Running low on calls!</span>
                        <?php else: ?>
                            <span class="warning-medium">⚡ Consider upgrading soon</span>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
            </div>
            
            <div class="usage-card">
                <h3>Daily Usage</h3>
                <div class="usage-bar">
                    <div class="usage-fill" style="width: <?php echo min(100, $daily_percentage); ?>%"></div>
                </div>
                <p>
                    <?php echo esc_html($usage['daily_calls']); ?> / 
                    <?php echo $limits['daily'] === -1 ? 'Unlimited' : esc_html($limits['daily']); ?> calls today
                </p>
            </div>
        </div>
        
        <?php if ($membership_level === 'free'): ?>
        <div class="upgrade-notice">
            <h3>🚀 Upgrade for More Features</h3>
            <p>Get more API calls and premium features with our paid plans!</p>
            <a href="/premium-plans/" class="btn btn-primary">View Plans</a>
        </div>
        <?php endif; ?>
        
        <div class="quick-actions">
            <h3>Quick Stock Lookup</h3>
            <div class="stock-lookup">
                <input type="text" id="stock-symbol" placeholder="Enter stock symbol (e.g., AAPL)" maxlength="10">
                <button id="get-stock-quote" class="btn btn-secondary">Get Quote</button>
            </div>
            <div id="stock-result"></div>
        </div>
        
        <div class="recent-activity">
            <h3>Recent API Usage</h3>
            <div id="recent-calls">
                <p>Loading recent activity...</p>
            </div>
        </div>
    </div>
    
    <style>
    .stock-scanner-dashboard {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 2px solid #e1e1e1;
    }
    
    .membership-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.9em;
    }
    
    .membership-free { background: #e1e1e1; color: #666; }
    .membership-bronze { background: #cd7f32; color: white; }
    .membership-silver { background: #c0c0c0; color: #333; }
    .membership-gold { background: #ffd700; color: #333; }
    
    .usage-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .usage-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e1e1e1;
    }
    
    .usage-bar {
        width: 100%;
        height: 20px;
        background: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .usage-fill {
        height: 100%;
        background: linear-gradient(90deg, #2271b1 0%, #135e96 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .usage-warning {
        margin-top: 10px;
        padding: 8px 12px;
        border-radius: 4px;
    }
    
    .warning-medium {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .warning-high {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .upgrade-notice {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .quick-actions, .recent-activity {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e1e1e1;
        margin-bottom: 20px;
    }
    
    .stock-lookup {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    #stock-symbol {
        flex: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 16px;
    }
    
    .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .btn-primary {
        background: #2271b1;
        color: white;
    }
    
    .btn-primary:hover {
        background: #135e96;
    }
    
    .btn-secondary {
        background: #646970;
        color: white;
    }
    
    .btn-secondary:hover {
        background: #50575e;
    }
    
    #stock-result {
        margin-top: 15px;
        padding: 15px;
        background: #f9f9f9;
        border-radius: 4px;
        border-left: 4px solid #2271b1;
    }
    
    @media (max-width: 768px) {
        .usage-stats {
            grid-template-columns: 1fr;
        }
        
        .dashboard-header {
            flex-direction: column;
            gap: 15px;
            text-align: center;
        }
        
        .stock-lookup {
            flex-direction: column;
        }
    }
    </style>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_dashboard', 'stock_scanner_dashboard_shortcode');

/**
 * Pricing table shortcode
 */
function stock_scanner_pricing_shortcode($atts) {
    $user_id = get_current_user_id();
    $current_level = $user_id ? get_user_membership_level($user_id) : 'free';
    
    ob_start();
    ?>
    <div class="pricing-table">
        <div class="pricing-header">
            <h2>Choose Your Plan</h2>
            <p>Select the perfect plan for your stock analysis needs</p>
        </div>
        
        <div class="pricing-grid">
            <div class="pricing-card <?php echo $current_level === 'free' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Free</h3>
                    <div class="price">$0<span>/month</span></div>
                </div>
                <ul class="features">
                    <li>✓ 15 API calls/month</li>
                    <li>✓ Basic stock quotes</li>
                    <li>✓ Simple charts</li>
                    <li>✓ Email support</li>
                </ul>
                <?php if ($current_level === 'free'): ?>
                    <button class="btn btn-current" disabled>Current Plan</button>
                <?php else: ?>
                    <button class="btn btn-downgrade" data-plan="free">Downgrade</button>
                <?php endif; ?>
            </div>
            
            <div class="pricing-card featured <?php echo $current_level === 'bronze' ? 'current-plan' : ''; ?>">
                <div class="plan-badge">Most Popular</div>
                <div class="plan-header">
                    <h3>Bronze</h3>
                    <div class="price">$9.99<span>/month</span></div>
                </div>
                <ul class="features">
                    <li>✓ 1,500 API calls/month</li>
                    <li>✓ Real-time quotes</li>
                    <li>✓ Advanced charts</li>
                    <li>✓ Technical indicators</li>
                    <li>✓ Priority support</li>
                </ul>
                <?php if ($current_level === 'bronze'): ?>
                    <button class="btn btn-current" disabled>Current Plan</button>
                <?php elseif ($user_id): ?>
                    <button class="btn btn-primary upgrade-btn" data-plan="bronze" data-price="9.99">
                        <?php echo in_array($current_level, ['silver', 'gold']) ? 'Downgrade' : 'Upgrade'; ?>
                    </button>
                <?php else: ?>
                    <button class="btn btn-primary" onclick="window.location.href='<?php echo wp_login_url(); ?>'">Login to Subscribe</button>
                <?php endif; ?>
            </div>
            
            <div class="pricing-card <?php echo $current_level === 'silver' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Silver</h3>
                    <div class="price">$19.99<span>/month</span></div>
                </div>
                <ul class="features">
                    <li>✓ 5,000 API calls/month</li>
                    <li>✓ Everything in Bronze</li>
                    <li>✓ Portfolio tracking</li>
                    <li>✓ Alerts & notifications</li>
                    <li>✓ API access</li>
                </ul>
                <?php if ($current_level === 'silver'): ?>
                    <button class="btn btn-current" disabled>Current Plan</button>
                <?php elseif ($user_id): ?>
                    <button class="btn btn-primary upgrade-btn" data-plan="silver" data-price="19.99">
                        <?php echo $current_level === 'gold' ? 'Downgrade' : 'Upgrade'; ?>
                    </button>
                <?php else: ?>
                    <button class="btn btn-primary" onclick="window.location.href='<?php echo wp_login_url(); ?>'">Login to Subscribe</button>
                <?php endif; ?>
            </div>
            
            <div class="pricing-card premium <?php echo $current_level === 'gold' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Gold</h3>
                    <div class="price">$49.99<span>/month</span></div>
                </div>
                <ul class="features">
                    <li>✓ Unlimited API calls</li>
                    <li>✓ Everything in Silver</li>
                    <li>✓ Custom indicators</li>
                    <li>✓ White-label access</li>
                    <li>✓ 24/7 phone support</li>
                </ul>
                <?php if ($current_level === 'gold'): ?>
                    <button class="btn btn-current" disabled>Current Plan</button>
                <?php elseif ($user_id): ?>
                    <button class="btn btn-premium upgrade-btn" data-plan="gold" data-price="49.99">Upgrade</button>
                <?php else: ?>
                    <button class="btn btn-premium" onclick="window.location.href='<?php echo wp_login_url(); ?>'">Login to Subscribe</button>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="pricing-footer">
            <p>All plans include SSL security, uptime guarantee, and can be cancelled anytime.</p>
            <div class="security-badges">
                <span class="badge">🔒 SSL Secured</span>
                <span class="badge">💳 PayPal Protected</span>
                <span class="badge">⚡ 99.9% Uptime</span>
            </div>
        </div>
    </div>
    
    <style>
    .pricing-table {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .pricing-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .pricing-header h2 {
        font-size: 2.5em;
        color: #2271b1;
        margin-bottom: 10px;
    }
    
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 30px;
        margin-bottom: 40px;
    }
    
    .pricing-card {
        background: white;
        border-radius: 12px;
        padding: 30px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px solid #e1e1e1;
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .pricing-card.featured {
        border-color: #2271b1;
        transform: scale(1.05);
    }
    
    .pricing-card.current-plan {
        border-color: #00a32a;
        background: linear-gradient(135deg, #f8fff8 0%, #e6f7e6 100%);
    }
    
    .plan-badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: #2271b1;
        color: white;
        padding: 6px 20px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
    }
    
    .plan-header {
        text-align: center;
        margin-bottom: 25px;
    }
    
    .plan-header h3 {
        font-size: 1.8em;
        color: #333;
        margin-bottom: 10px;
    }
    
    .price {
        font-size: 2.5em;
        font-weight: bold;
        color: #2271b1;
    }
    
    .price span {
        font-size: 0.6em;
        color: #666;
    }
    
    .features {
        list-style: none;
        padding: 0;
        margin: 0 0 25px 0;
    }
    
    .features li {
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
        color: #555;
    }
    
    .btn {
        width: 100%;
        padding: 12px 20px;
        border: none;
        border-radius: 6px;
        font-size: 1.1em;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    .btn-primary {
        background: #2271b1;
        color: white;
    }
    
    .btn-primary:hover {
        background: #135e96;
    }
    
    .btn-premium {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #333;
    }
    
    .btn-premium:hover {
        background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%);
    }
    
    .btn-current {
        background: #00a32a;
        color: white;
        cursor: not-allowed;
    }
    
    .btn-downgrade {
        background: #646970;
        color: white;
    }
    
    .pricing-footer {
        text-align: center;
        color: #666;
    }
    
    .security-badges {
        margin-top: 20px;
    }
    
    .badge {
        display: inline-block;
        background: #f0f0f0;
        padding: 8px 15px;
        margin: 0 5px;
        border-radius: 20px;
        font-size: 0.9em;
    }
    
    @media (max-width: 768px) {
        .pricing-grid {
            grid-template-columns: 1fr;
        }
        
        .pricing-card.featured {
            transform: none;
        }
        
        .pricing-header h2 {
            font-size: 2em;
        }
    }
    </style>
    <?php
    return ob_get_clean();
}
add_shortcode('stock_scanner_pricing', 'stock_scanner_pricing_shortcode');

/**
 * AJAX handler for stock quotes
 */
function handle_stock_quote_ajax() {
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    
    $user_id = get_current_user_id();
    if (!$user_id) {
        wp_send_json_error('Please login to get stock quotes.');
        return;
    }
    
    if (!can_user_make_api_call($user_id)) {
        wp_send_json_error('API limit reached. Please upgrade your plan.');
        return;
    }
    
    $symbol = sanitize_text_field($_POST['symbol']);
    if (empty($symbol)) {
        wp_send_json_error('Please provide a stock symbol.');
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
                'endpoint' => 'stock_quote',
                'symbol' => $symbol,
                'created_at' => current_time('mysql')
            )
        );
    }
    
    // Mock stock data (replace with real API call)
    $stock_data = array(
        'symbol' => strtoupper($symbol),
        'price' => number_format(rand(10, 500) + (rand(0, 99) / 100), 2),
        'change' => number_format((rand(-10, 10) + (rand(0, 99) / 100)), 2),
        'change_percent' => number_format((rand(-5, 5) + (rand(0, 99) / 100)), 2),
        'volume' => number_format(rand(100000, 10000000)),
        'timestamp' => current_time('mysql')
    );
    
    wp_send_json_success($stock_data);
}
add_action('wp_ajax_get_stock_quote', 'handle_stock_quote_ajax');
add_action('wp_ajax_nopriv_get_stock_quote', 'handle_stock_quote_ajax');

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