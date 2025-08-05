<?php
/**
 * Stock Scanner Admin Interface
 * Comprehensive admin pages for security analytics, rate limiting, and user management
 */

if (!defined('ABSPATH')) {
    exit;
}

class Stock_Scanner_Admin_Interface {
    
    private $plugin_instance;
    
    public function __construct($plugin_instance) {
        $this->plugin_instance = $plugin_instance;
        add_action('wp_ajax_stock_scanner_ban_user', array($this, 'ajax_ban_user'));
        add_action('wp_ajax_stock_scanner_unban_user', array($this, 'ajax_unban_user'));
        add_action('wp_ajax_stock_scanner_update_rate_limits', array($this, 'ajax_update_rate_limits'));
        add_action('wp_ajax_stock_scanner_get_security_data', array($this, 'ajax_get_security_data'));
        add_action('wp_ajax_stock_scanner_block_ip', array($this, 'ajax_block_ip'));
    }
    
    /**
     * Security Analytics Page
     */
    public function security_analytics_page() {
        global $wpdb;
        
        // Get recent security events
        $security_events = $wpdb->get_results(
            "SELECT * FROM {$wpdb->prefix}stock_scanner_security 
             ORDER BY created_at DESC LIMIT 50"
        );
        
        // Get bot detection stats
        $bot_stats = $wpdb->get_results(
            "SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_requests,
                SUM(CASE WHEN bot_score > 50 THEN 1 ELSE 0 END) as suspicious_requests,
                AVG(bot_score) as avg_bot_score
             FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
             GROUP BY DATE(created_at) 
             ORDER BY date DESC"
        );
        
        // Get top suspicious IPs
        $suspicious_ips = $wpdb->get_results(
            "SELECT 
                ip_address,
                COUNT(*) as request_count,
                AVG(bot_score) as avg_bot_score,
                MAX(created_at) as last_seen
             FROM {$wpdb->prefix}stock_scanner_usage 
             WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR) AND bot_score > 30
             GROUP BY ip_address 
             ORDER BY avg_bot_score DESC, request_count DESC 
             LIMIT 20"
        );
        
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>🛡️ Security Analytics Dashboard</h1>
            
            <div class="security-dashboard-grid">
                <!-- Summary Cards -->
                <div class="dashboard-cards">
                    <div class="security-card">
                        <div class="card-icon">🚨</div>
                        <div class="card-content">
                            <h3>Security Events (24h)</h3>
                            <span class="card-number"><?php echo count($security_events); ?></span>
                        </div>
                    </div>
                    
                    <div class="security-card">
                        <div class="card-icon">🤖</div>
                        <div class="card-content">
                            <h3>Bot Detection Rate</h3>
                            <span class="card-number">
                                <?php 
                                $total_today = $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage WHERE DATE(created_at) = CURDATE()");
                                $bots_today = $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_usage WHERE DATE(created_at) = CURDATE() AND bot_score > 50");
                                echo $total_today > 0 ? round(($bots_today / $total_today) * 100, 1) : 0;
                                ?>%
                            </span>
                        </div>
                    </div>
                    
                    <div class="security-card">
                        <div class="card-icon">⛔</div>
                        <div class="card-content">
                            <h3>Banned Users</h3>
                            <span class="card-number">
                                <?php echo $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_subscriptions WHERE is_banned = 1"); ?>
                            </span>
                        </div>
                    </div>
                    
                    <div class="security-card">
                        <div class="card-icon">⚠️</div>
                        <div class="card-content">
                            <h3>Admin Alerts</h3>
                            <span class="card-number">
                                <?php echo $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}stock_scanner_security WHERE event_type = 'suspicious_user_alert' AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)"); ?>
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Bot Detection Chart -->
                <div class="chart-container">
                    <h3>📊 Bot Detection Trends (7 Days)</h3>
                    <canvas id="botDetectionChart" width="400" height="200"></canvas>
                </div>
                
                <!-- Suspicious IPs Table -->
                <div class="suspicious-ips">
                    <h3>🎯 Most Suspicious IPs (24h)</h3>
                    <div class="table-container">
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th>IP Address</th>
                                    <th>Requests</th>
                                    <th>Bot Score</th>
                                    <th>Last Seen</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($suspicious_ips as $ip): ?>
                                <tr class="<?php echo $ip->avg_bot_score > 70 ? 'high-risk' : ($ip->avg_bot_score > 50 ? 'medium-risk' : 'low-risk'); ?>">
                                    <td>
                                        <strong><?php echo esc_html($ip->ip_address); ?></strong>
                                        <div class="row-actions">
                                            <a href="https://whatismyipaddress.com/ip/<?php echo esc_attr($ip->ip_address); ?>" target="_blank">Lookup</a>
                                        </div>
                                    </td>
                                    <td><?php echo number_format($ip->request_count); ?></td>
                                    <td>
                                        <span class="bot-score-badge score-<?php echo $ip->avg_bot_score > 70 ? 'high' : ($ip->avg_bot_score > 50 ? 'medium' : 'low'); ?>">
                                            <?php echo round($ip->avg_bot_score); ?>%
                                        </span>
                                    </td>
                                    <td><?php echo wp_date('M j, H:i', strtotime($ip->last_seen)); ?></td>
                                    <td>
                                        <button class="button button-small block-ip-btn" data-ip="<?php echo esc_attr($ip->ip_address); ?>">
                                            Block IP
                                        </button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Recent Security Events -->
                <div class="security-events">
                    <h3>🔍 Recent Security Events</h3>
                    <div class="table-container">
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Event Type</th>
                                    <th>Severity</th>
                                    <th>IP Address</th>
                                    <th>Description</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($security_events as $event): ?>
                                <tr class="severity-<?php echo esc_attr($event->severity); ?>">
                                    <td><?php echo wp_date('M j, H:i', strtotime($event->created_at)); ?></td>
                                    <td>
                                        <span class="event-type-badge"><?php echo esc_html($event->event_type); ?></span>
                                    </td>
                                    <td>
                                        <span class="severity-badge severity-<?php echo esc_attr($event->severity); ?>">
                                            <?php echo esc_html(ucfirst($event->severity)); ?>
                                        </span>
                                    </td>
                                    <td><?php echo esc_html($event->ip_address); ?></td>
                                    <td><?php echo esc_html($event->description); ?></td>
                                    <td>
                                        <?php if ($event->data): ?>
                                        <button class="button button-small view-details-btn" data-details="<?php echo esc_attr($event->data); ?>">
                                            View Details
                                        </button>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        // Chart.js implementation for bot detection trends
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('botDetectionChart').getContext('2d');
            const chartData = <?php echo json_encode(array_reverse($bot_stats)); ?>;
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map(d => d.date),
                    datasets: [{
                        label: 'Total Requests',
                        data: chartData.map(d => d.total_requests),
                        borderColor: '#2271b1',
                        backgroundColor: 'rgba(34, 113, 177, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Suspicious Requests',
                        data: chartData.map(d => d.suspicious_requests),
                        borderColor: '#d63638',
                        backgroundColor: 'rgba(214, 54, 56, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
        </script>
        <?php
    }
    
    /**
     * Rate Limiting Management Page
     */
    public function rate_limits_page() {
        global $wpdb;
        
        // Handle form submission
        if (isset($_POST['update_rate_limits']) && wp_verify_nonce($_POST['_wpnonce'], 'update_rate_limits')) {
            $this->update_rate_limit_settings();
        }
        
        $current_settings = json_decode(get_option('stock_scanner_rate_limits'), true);
        
        // Get current rate limit violations
        $violations = $wpdb->get_results(
            "SELECT ip_address, COUNT(*) as violation_count, MAX(created_at) as last_violation
             FROM {$wpdb->prefix}stock_scanner_security 
             WHERE event_type = 'rate_limit_exceeded' AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
             GROUP BY ip_address 
             ORDER BY violation_count DESC 
             LIMIT 20"
        );
        
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>⚡ Rate Limiting & Anti-Bot Settings</h1>
            
            <div class="rate-limits-container">
                <!-- Settings Form -->
                <div class="settings-panel">
                    <h2>🔧 Rate Limiting Configuration</h2>
                    <form method="post" action="">
                        <?php wp_nonce_field('update_rate_limits'); ?>
                        
                        <table class="form-table">
                            <tr>
                                <th scope="row">Requests per Minute</th>
                                <td>
                                    <input type="number" name="requests_per_minute" value="<?php echo esc_attr($current_settings['requests_per_minute']); ?>" min="1" max="1000" />
                                    <p class="description">Maximum requests allowed per minute from a single IP</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Requests per Hour</th>
                                <td>
                                    <input type="number" name="requests_per_hour" value="<?php echo esc_attr($current_settings['requests_per_hour']); ?>" min="1" max="10000" />
                                    <p class="description">Maximum requests allowed per hour from a single IP</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Requests per Day</th>
                                <td>
                                    <input type="number" name="requests_per_day" value="<?php echo esc_attr($current_settings['requests_per_day']); ?>" min="1" max="100000" />
                                    <p class="description">Maximum requests allowed per day from a single IP</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Bot Detection</th>
                                <td>
                                    <label>
                                        <input type="checkbox" name="bot_detection_enabled" value="1" <?php checked($current_settings['bot_detection_enabled']); ?> />
                                        Enable automatic bot detection
                                    </label>
                                    <p class="description">Automatically analyze requests for bot patterns</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Auto-Ban</th>
                                <td>
                                    <label>
                                        <input type="checkbox" name="auto_ban_enabled" value="1" <?php checked($current_settings['auto_ban_enabled']); ?> disabled />
                                        Enable automatic banning for high bot scores <strong>(DISABLED - Admin Discretion Only)</strong>
                                    </label>
                                    <p class="description">Automatic banning is disabled. Users are flagged for admin review instead.</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Auto Rate Limiting</th>
                                <td>
                                    <label>
                                        <input type="checkbox" name="auto_rate_limit_enabled" value="1" <?php checked($current_settings['auto_rate_limit_enabled'] ?? false); ?> />
                                        Enable automatic rate limiting enforcement
                                    </label>
                                    <p class="description">When disabled, rate limits are advisory only and logged for admin review</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Alert Threshold</th>
                                <td>
                                    <input type="number" name="alert_threshold" value="<?php echo esc_attr($current_settings['alert_threshold'] ?? 60); ?>" min="1" max="100" />
                                    <p class="description">Bot score threshold for alerting admins about suspicious users (1-100)</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Bot Score Threshold</th>
                                <td>
                                    <input type="number" name="bot_score_threshold" value="<?php echo esc_attr($current_settings['bot_score_threshold']); ?>" min="1" max="100" />
                                    <p class="description">Bot score threshold for automatic banning (1-100)</p>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">Suspicious Threshold</th>
                                <td>
                                    <input type="number" name="suspicious_threshold" value="<?php echo esc_attr($current_settings['suspicious_threshold']); ?>" min="1" max="100" />
                                    <p class="description">Bot score threshold for flagging as suspicious (1-100)</p>
                                </td>
                            </tr>
                        </table>
                        
                        <?php submit_button('Update Rate Limits', 'primary', 'update_rate_limits'); ?>
                    </form>
                </div>
                
                <!-- Rate Limit Violations -->
                <div class="violations-panel">
                    <h2>🚨 Recent Rate Limit Violations (24h)</h2>
                    <div class="table-container">
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th>IP Address</th>
                                    <th>Violations</th>
                                    <th>Last Violation</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($violations as $violation): ?>
                                <tr>
                                    <td><strong><?php echo esc_html($violation->ip_address); ?></strong></td>
                                    <td>
                                        <span class="violation-count"><?php echo number_format($violation->violation_count); ?></span>
                                    </td>
                                    <td><?php echo wp_date('M j, H:i', strtotime($violation->last_violation)); ?></td>
                                    <td>
                                        <button class="button button-small block-ip-btn" data-ip="<?php echo esc_attr($violation->ip_address); ?>">
                                            Block IP
                                        </button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }
    
    /**
     * User Management Page
     */
    public function user_management_page() {
        global $wpdb;
        
        // Get users with suspicious activity
        $suspicious_users = $wpdb->get_results(
            "SELECT u.ID, u.user_login, u.user_email, u.user_registered,
                    s.plan, s.status, s.is_banned, s.ban_reason, s.banned_at,
                    AVG(usage.bot_score) as avg_bot_score,
                    COUNT(usage.id) as total_requests,
                    SUM(CASE WHEN usage.is_suspicious = 1 THEN 1 ELSE 0 END) as suspicious_requests
             FROM {$wpdb->users} u
             LEFT JOIN {$wpdb->prefix}stock_scanner_subscriptions s ON u.ID = s.user_id
             LEFT JOIN {$wpdb->prefix}stock_scanner_usage usage ON u.ID = usage.user_id
             WHERE usage.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
             GROUP BY u.ID
             HAVING avg_bot_score > 30 OR suspicious_requests > 5
             ORDER BY avg_bot_score DESC, suspicious_requests DESC
             LIMIT 50"
        );
        
        // Get banned users
        $banned_users = $wpdb->get_results(
            "SELECT u.ID, u.user_login, u.user_email, 
                    s.ban_reason, s.banned_at, s.banned_by
             FROM {$wpdb->users} u
             JOIN {$wpdb->prefix}stock_scanner_subscriptions s ON u.ID = s.user_id
             WHERE s.is_banned = 1
             ORDER BY s.banned_at DESC"
        );
        
        ?>
        <div class="wrap stock-scanner-admin">
            <h1>👥 User Management & Account Control</h1>
            
            <div class="user-management-tabs">
                <nav class="nav-tab-wrapper">
                    <a href="#suspicious-users" class="nav-tab nav-tab-active">Suspicious Users</a>
                    <a href="#banned-users" class="nav-tab">Banned Users</a>
                    <a href="#bulk-actions" class="nav-tab">Bulk Actions</a>
                </nav>
                
                <!-- Suspicious Users Tab -->
                <div id="suspicious-users" class="tab-content">
                    <h2>🚨 Users with Suspicious Activity</h2>
                    <div class="table-container">
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Email</th>
                                    <th>Plan</th>
                                    <th>Avg Bot Score</th>
                                    <th>Total Requests</th>
                                    <th>Suspicious</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($suspicious_users as $user): ?>
                                <tr class="<?php echo $user->is_banned ? 'banned-user' : ''; ?>">
                                    <td>
                                        <strong><?php echo esc_html($user->user_login); ?></strong>
                                        <div class="row-actions">
                                            <a href="<?php echo admin_url('user-edit.php?user_id=' . $user->ID); ?>">Edit</a>
                                        </div>
                                    </td>
                                    <td><?php echo esc_html($user->user_email); ?></td>
                                    <td>
                                        <span class="plan-badge plan-<?php echo esc_attr($user->plan); ?>">
                                            <?php echo esc_html(ucfirst($user->plan)); ?>
                                        </span>
                                    </td>
                                    <td>
                                        <span class="bot-score-badge score-<?php echo $user->avg_bot_score > 70 ? 'high' : ($user->avg_bot_score > 50 ? 'medium' : 'low'); ?>">
                                            <?php echo round($user->avg_bot_score); ?>%
                                        </span>
                                    </td>
                                    <td><?php echo number_format($user->total_requests); ?></td>
                                    <td>
                                        <span class="suspicious-count"><?php echo number_format($user->suspicious_requests); ?></span>
                                    </td>
                                    <td>
                                        <?php if ($user->is_banned): ?>
                                            <span class="status-banned">BANNED</span>
                                        <?php else: ?>
                                            <span class="status-active">Active</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($user->is_banned): ?>
                                            <button class="button button-small unban-user-btn" data-user-id="<?php echo esc_attr($user->ID); ?>">
                                                Unban
                                            </button>
                                        <?php else: ?>
                                            <button class="button button-small ban-user-btn" data-user-id="<?php echo esc_attr($user->ID); ?>">
                                                Ban User
                                            </button>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Banned Users Tab -->
                <div id="banned-users" class="tab-content" style="display: none;">
                    <h2>⛔ Currently Banned Users</h2>
                    <div class="table-container">
                        <table class="wp-list-table widefat fixed striped">
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Email</th>
                                    <th>Ban Reason</th>
                                    <th>Banned Date</th>
                                    <th>Banned By</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($banned_users as $user): ?>
                                <tr>
                                    <td>
                                        <strong><?php echo esc_html($user->user_login); ?></strong>
                                    </td>
                                    <td><?php echo esc_html($user->user_email); ?></td>
                                    <td><?php echo esc_html($user->ban_reason); ?></td>
                                    <td><?php echo wp_date('M j, Y H:i', strtotime($user->banned_at)); ?></td>
                                    <td>
                                        <?php 
                                        if ($user->banned_by == 0) {
                                            echo 'System';
                                        } else {
                                            $admin = get_user_by('ID', $user->banned_by);
                                            echo $admin ? esc_html($admin->user_login) : 'Unknown';
                                        }
                                        ?>
                                    </td>
                                    <td>
                                        <button class="button button-small unban-user-btn" data-user-id="<?php echo esc_attr($user->ID); ?>">
                                            Unban User
                                        </button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Bulk Actions Tab -->
                <div id="bulk-actions" class="tab-content" style="display: none;">
                    <h2>⚡ Bulk User Actions</h2>
                    
                    <div class="bulk-actions-panel">
                        <div class="action-section">
                            <h3>🚨 Admin Actions</h3>
                            <button class="button button-large button-primary" id="bulk-ban-high-bot-score">
                                Review & Ban High Risk Users (Score > 80%)
                            </button>
                            <button class="button button-large" id="bulk-reset-limits">
                                Clear Rate Limit Logs
                            </button>
                            <button class="button button-large button-secondary" id="bulk-unban-all">
                                Unban All Banned Users
                            </button>
                            <button class="button button-large" id="bulk-alert-review">
                                Review All Suspicious Alerts
                            </button>
                        </div>
                        
                        <div class="action-section">
                            <h3>📊 Analysis Actions</h3>
                            <button class="button button-large" id="analyze-patterns">
                                Run Pattern Analysis
                            </button>
                            <button class="button button-large" id="export-security-log">
                                Export Security Log
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Ban User Modal -->
        <div id="ban-user-modal" class="stock-scanner-modal" style="display: none;">
            <div class="modal-content">
                <h3>Ban User Account</h3>
                <form id="ban-user-form">
                    <input type="hidden" id="ban-user-id" name="user_id" />
                    <p>
                        <label for="ban-reason">Reason for ban:</label>
                        <textarea id="ban-reason" name="ban_reason" rows="3" style="width: 100%;" placeholder="Enter reason for banning this user..."></textarea>
                    </p>
                    <p>
                        <label>
                            <input type="checkbox" name="notify_user" value="1" checked />
                            Send notification to user
                        </label>
                    </p>
                    <div class="modal-actions">
                        <button type="submit" class="button button-primary">Ban User</button>
                        <button type="button" class="button cancel-modal">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            // Tab switching
            $('.nav-tab').click(function(e) {
                e.preventDefault();
                $('.nav-tab').removeClass('nav-tab-active');
                $(this).addClass('nav-tab-active');
                $('.tab-content').hide();
                $($(this).attr('href')).show();
            });
            
            // Ban user functionality
            $('.ban-user-btn').click(function() {
                const userId = $(this).data('user-id');
                $('#ban-user-id').val(userId);
                $('#ban-user-modal').show();
            });
            
            $('.cancel-modal').click(function() {
                $('.stock-scanner-modal').hide();
            });
            
            $('#ban-user-form').submit(function(e) {
                e.preventDefault();
                // AJAX ban user implementation
                const formData = $(this).serialize();
                $.post(ajaxurl, {
                    action: 'stock_scanner_ban_user',
                    nonce: stockScannerAdmin.nonce,
                    ...Object.fromEntries(new URLSearchParams(formData))
                }, function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + response.data);
                    }
                });
            });
            
            // Unban user
            $('.unban-user-btn').click(function() {
                if (confirm(stockScannerAdmin.strings.confirm_unban)) {
                    const userId = $(this).data('user-id');
                    $.post(ajaxurl, {
                        action: 'stock_scanner_unban_user',
                        nonce: stockScannerAdmin.nonce,
                        user_id: userId
                    }, function(response) {
                        if (response.success) {
                            location.reload();
                        } else {
                            alert('Error: ' + response.data);
                        }
                    });
                }
            });
            
            // Block IP
            $('.block-ip-btn').click(function() {
                const ip = $(this).data('ip');
                if (confirm('Are you sure you want to block IP: ' + ip + '?')) {
                    $.post(ajaxurl, {
                        action: 'stock_scanner_block_ip',
                        nonce: stockScannerAdmin.nonce,
                        ip_address: ip
                    }, function(response) {
                        if (response.success) {
                            alert('IP blocked successfully');
                            location.reload();
                        } else {
                            alert('Error: ' + response.data);
                        }
                    });
                }
            });
        });
        </script>
        <?php
    }
    
    /**
     * Settings Page
     */
    public function settings_page() {
        // Settings implementation
        ?>
        <div class="wrap">
            <h1>⚙️ Stock Scanner Security Settings</h1>
            
            <form method="post" action="options.php">
                <?php 
                settings_fields('stock_scanner_settings');
                do_settings_sections('stock_scanner_settings');
                ?>
                
                <table class="form-table">
                    <tr>
                        <th scope="row">Security Mode</th>
                        <td>
                            <select name="stock_scanner_security_mode">
                                <option value="normal">Normal</option>
                                <option value="strict">Strict</option>
                                <option value="paranoid">Paranoid</option>
                            </select>
                            <p class="description">Choose security level for bot detection</p>
                        </td>
                    </tr>
                </table>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Update rate limit settings
     */
    private function update_rate_limit_settings() {
        $settings = array(
            'requests_per_minute' => intval($_POST['requests_per_minute']),
            'requests_per_hour' => intval($_POST['requests_per_hour']),
            'requests_per_day' => intval($_POST['requests_per_day']),
            'bot_detection_enabled' => isset($_POST['bot_detection_enabled']),
            'auto_ban_enabled' => false, // Always disabled - admin discretion only
            'auto_rate_limit_enabled' => isset($_POST['auto_rate_limit_enabled']),
            'bot_score_threshold' => intval($_POST['bot_score_threshold']),
            'suspicious_threshold' => intval($_POST['suspicious_threshold']),
            'alert_threshold' => intval($_POST['alert_threshold'])
        );
        
        update_option('stock_scanner_rate_limits', json_encode($settings));
        
        $message = 'Rate limiting settings updated successfully!';
        if (!$settings['auto_rate_limit_enabled']) {
            $message .= ' Rate limits are now advisory only and will not automatically block users.';
        }
        
        echo '<div class="notice notice-success"><p>' . $message . '</p></div>';
    }
    
    /**
     * AJAX: Ban User
     */
    public function ajax_ban_user() {
        check_ajax_referer('stock_scanner_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error('Insufficient permissions');
        }
        
        $user_id = intval($_POST['user_id']);
        $ban_reason = sanitize_text_field($_POST['ban_reason']);
        $notify_user = isset($_POST['notify_user']);
        
        global $wpdb;
        
        $result = $wpdb->update(
            $wpdb->prefix . 'stock_scanner_subscriptions',
            array(
                'is_banned' => 1,
                'ban_reason' => $ban_reason,
                'banned_at' => current_time('mysql'),
                'banned_by' => get_current_user_id()
            ),
            array('user_id' => $user_id)
        );
        
        if ($result !== false) {
            if ($notify_user) {
                $this->send_ban_notification($user_id, $ban_reason);
            }
            
            wp_send_json_success('User banned successfully');
        } else {
            wp_send_json_error('Failed to ban user');
        }
    }
    
    /**
     * AJAX: Unban User
     */
    public function ajax_unban_user() {
        check_ajax_referer('stock_scanner_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error('Insufficient permissions');
        }
        
        $user_id = intval($_POST['user_id']);
        
        global $wpdb;
        
        $result = $wpdb->update(
            $wpdb->prefix . 'stock_scanner_subscriptions',
            array(
                'is_banned' => 0,
                'ban_reason' => null,
                'banned_at' => null,
                'banned_by' => null
            ),
            array('user_id' => $user_id)
        );
        
        if ($result !== false) {
            $this->send_unban_notification($user_id);
            wp_send_json_success('User unbanned successfully');
        } else {
            wp_send_json_error('Failed to unban user');
        }
    }
    
    /**
     * AJAX: Block IP
     */
    public function ajax_block_ip() {
        check_ajax_referer('stock_scanner_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error('Insufficient permissions');
        }
        
        $ip_address = sanitize_text_field($_POST['ip_address']);
        
        global $wpdb;
        
        $result = $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_rate_limits',
            array(
                'ip_address' => $ip_address,
                'endpoint' => '*',
                'requests_count' => 9999,
                'window_start' => current_time('mysql'),
                'window_end' => date('Y-m-d H:i:s', strtotime('+1 year')),
                'is_blocked' => 1,
                'block_reason' => 'Admin blocked IP'
            )
        );
        
        if ($result) {
            wp_send_json_success('IP blocked successfully');
        } else {
            wp_send_json_error('Failed to block IP');
        }
    }
    
    /**
     * Send ban notification to user
     */
    private function send_ban_notification($user_id, $reason) {
        global $wpdb;
        
        $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_notifications',
            array(
                'user_id' => $user_id,
                'type' => 'account_banned',
                'title' => 'Account Suspended',
                'message' => "Your account has been suspended by an administrator. Reason: $reason. Please contact support if you believe this is an error.",
                'priority' => 'high'
            )
        );
    }
    
    /**
     * Send unban notification to user
     */
    private function send_unban_notification($user_id) {
        global $wpdb;
        
        $wpdb->insert(
            $wpdb->prefix . 'stock_scanner_notifications',
            array(
                'user_id' => $user_id,
                'type' => 'account_unbanned',
                'title' => 'Account Restored',
                'message' => 'Your account has been restored by an administrator. You can now use our services normally.',
                'priority' => 'normal'
            )
        );
    }
}
?>