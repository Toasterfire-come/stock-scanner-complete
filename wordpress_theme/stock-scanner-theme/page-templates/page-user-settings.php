<?php
/**
 * Template Name: User Settings Page
 * Complete user settings and preferences management
 */

// Security check
if (!defined('ABSPATH')) {
    exit;
}

// Redirect if user is not logged in
if (!is_user_logged_in()) {
    wp_redirect(home_url('/signup/?redirect_to=' . urlencode($_SERVER['REQUEST_URI'])));
    exit;
}

get_header();

$current_user = wp_get_current_user();
$membership_level = get_user_meta($current_user->ID, 'membership_level', true) ?: 'free';
?>

<div class="user-settings-container">
    <div class="settings-header">
        <h1>Account Settings</h1>
        <p class="settings-subtitle">Manage your profile, preferences, and account settings</p>
    </div>

    <div class="settings-content">
        <!-- Settings Navigation -->
        <div class="settings-nav">
            <nav class="settings-tabs">
                <a href="#profile" class="settings-tab active" data-tab="profile">
                    <span class="tab-icon">👤</span>
                    Profile
                </a>
                <a href="#portfolio-settings" class="settings-tab" data-tab="portfolio-settings">
                    <span class="tab-icon">📊</span>
                    Portfolio Settings
                </a>
                <a href="#news-preferences" class="settings-tab" data-tab="news-preferences">
                    <span class="tab-icon">📰</span>
                    News Preferences
                </a>
                <a href="#watchlist-settings" class="settings-tab" data-tab="watchlist-settings">
                    <span class="tab-icon">👁️</span>
                    Watchlist Settings
                </a>
                <a href="#notifications" class="settings-tab" data-tab="notifications">
                    <span class="tab-icon">🔔</span>
                    Notifications
                </a>
                <a href="#security" class="settings-tab" data-tab="security">
                    <span class="tab-icon">🔒</span>
                    Security
                </a>
                <a href="#data-export" class="settings-tab" data-tab="data-export">
                    <span class="tab-icon">📦</span>
                    Data Export
                </a>
                <a href="#membership" class="settings-tab" data-tab="membership">
                    <span class="tab-icon">⭐</span>
                    Membership
                </a>
            </nav>
        </div>

        <!-- Settings Content Panels -->
        <div class="settings-panels">
            <!-- Profile Settings -->
            <div class="settings-panel active" id="profile">
                <div class="panel-header">
                    <h2>Profile Information</h2>
                    <p>Update your personal information and display preferences</p>
                </div>

                <form class="settings-form" id="profile-form">
                    <div class="form-section">
                        <h3>Personal Information</h3>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="first-name">First Name</label>
                                <input type="text" id="first-name" name="first_name" 
                                       value="<?php echo esc_attr($current_user->first_name); ?>" class="form-control">
                            </div>
                            <div class="form-group">
                                <label for="last-name">Last Name</label>
                                <input type="text" id="last-name" name="last_name" 
                                       value="<?php echo esc_attr($current_user->last_name); ?>" class="form-control">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="display-name">Display Name</label>
                            <input type="text" id="display-name" name="display_name" 
                                   value="<?php echo esc_attr($current_user->display_name); ?>" class="form-control">
                        </div>

                        <div class="form-group">
                            <label for="email">Email Address</label>
                            <input type="email" id="email" name="user_email" 
                                   value="<?php echo esc_attr($current_user->user_email); ?>" class="form-control">
                        </div>

                        <div class="form-group">
                            <label for="bio">Bio</label>
                            <textarea id="bio" name="bio" rows="4" class="form-control" 
                                      placeholder="Tell us about your investment experience and interests..."><?php echo esc_textarea(get_user_meta($current_user->ID, 'bio', true)); ?></textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="investment-experience">Investment Experience</label>
                                <select id="investment-experience" name="investment_experience" class="form-control">
                                    <?php 
                                    $experience = get_user_meta($current_user->ID, 'investment_experience', true);
                                    $options = array(
                                        'beginner' => 'Beginner (Less than 1 year)',
                                        'intermediate' => 'Intermediate (1-5 years)',
                                        'advanced' => 'Advanced (5+ years)',
                                        'professional' => 'Professional Trader/Advisor'
                                    );
                                    ?>
                                    <option value="">Select your experience level</option>
                                    <?php foreach ($options as $value => $label): ?>
                                        <option value="<?php echo esc_attr($value); ?>" 
                                                <?php selected($experience, $value); ?>><?php echo esc_html($label); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="timezone">Timezone</label>
                                <select id="timezone" name="timezone" class="form-control">
                                    <?php 
                                    $user_timezone = get_user_meta($current_user->ID, 'timezone', true) ?: 'America/New_York';
                                    $timezones = array(
                                        'America/New_York' => 'Eastern Time (ET)',
                                        'America/Chicago' => 'Central Time (CT)',
                                        'America/Denver' => 'Mountain Time (MT)',
                                        'America/Los_Angeles' => 'Pacific Time (PT)',
                                        'Europe/London' => 'London (GMT)',
                                        'Europe/Paris' => 'Paris (CET)',
                                        'Asia/Tokyo' => 'Tokyo (JST)',
                                        'Asia/Shanghai' => 'Shanghai (CST)'
                                    );
                                    ?>
                                    <?php foreach ($timezones as $value => $label): ?>
                                        <option value="<?php echo esc_attr($value); ?>" 
                                                <?php selected($user_timezone, $value); ?>><?php echo esc_html($label); ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Display Preferences</h3>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="public_profile" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'public_profile', true), 1); ?>>
                                Make my profile public
                            </label>
                            <small class="form-text">Allow other users to view your profile and portfolio performance (if enabled)</small>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="show_portfolio_performance" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'show_portfolio_performance', true), 1); ?>>
                                Show portfolio performance publicly
                            </label>
                            <small class="form-text">Display your portfolio returns on your public profile</small>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Save Profile Changes</button>
                </form>
            </div>

            <!-- Portfolio Settings -->
            <div class="settings-panel" id="portfolio-settings">
                <div class="panel-header">
                    <h2>Portfolio Settings</h2>
                    <p>Configure your portfolio tracking preferences</p>
                </div>

                <form class="settings-form" id="portfolio-settings-form">
                    <div class="form-section">
                        <h3>Default Settings</h3>
                        
                        <div class="form-group">
                            <label for="default-portfolio-name">Default Portfolio Name Format</label>
                            <input type="text" id="default-portfolio-name" name="default_portfolio_name" 
                                   value="<?php echo esc_attr(get_user_meta($current_user->ID, 'default_portfolio_name', true) ?: 'Portfolio {date}'); ?>" 
                                   class="form-control">
                            <small class="form-text">Use {date} for current date, {user} for username</small>
                        </div>

                        <div class="form-group">
                            <label for="performance-calculation">Performance Calculation Frequency</label>
                            <select id="performance-calculation" name="performance_calculation_frequency" class="form-control">
                                <?php 
                                $freq = get_user_meta($current_user->ID, 'performance_calculation_frequency', true) ?: 'realtime';
                                ?>
                                <option value="realtime" <?php selected($freq, 'realtime'); ?>>Real-time</option>
                                <option value="hourly" <?php selected($freq, 'hourly'); ?>>Hourly</option>
                                <option value="daily" <?php selected($freq, 'daily'); ?>>Daily</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="default-currency">Default Currency</label>
                            <select id="default-currency" name="default_currency" class="form-control">
                                <?php 
                                $currency = get_user_meta($current_user->ID, 'default_currency', true) ?: 'USD';
                                $currencies = array('USD' => 'US Dollar ($)', 'EUR' => 'Euro (€)', 'GBP' => 'British Pound (£)', 'CAD' => 'Canadian Dollar (C$)');
                                ?>
                                <?php foreach ($currencies as $code => $name): ?>
                                    <option value="<?php echo esc_attr($code); ?>" 
                                            <?php selected($currency, $code); ?>><?php echo esc_html($name); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Import/Export Preferences</h3>
                        
                        <div class="form-group">
                            <label for="csv-format">Preferred CSV Format</label>
                            <select id="csv-format" name="csv_import_format" class="form-control">
                                <?php 
                                $format = get_user_meta($current_user->ID, 'csv_import_format', true) ?: 'standard';
                                ?>
                                <option value="standard" <?php selected($format, 'standard'); ?>>Standard Format</option>
                                <option value="broker_a" <?php selected($format, 'broker_a'); ?>>Broker Format A</option>
                                <option value="broker_b" <?php selected($format, 'broker_b'); ?>>Broker Format B</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="auto_sync_portfolios" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'auto_sync_portfolios', true), 1); ?>>
                                Auto-sync with external brokers (when available)
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Save Portfolio Settings</button>
                </form>
            </div>

            <!-- News Preferences -->
            <div class="settings-panel" id="news-preferences">
                <div class="panel-header">
                    <h2>News Preferences</h2>
                    <p>Customize your personalized news feed</p>
                </div>

                <form class="settings-form" id="news-preferences-form">
                    <div class="form-section">
                        <h3>News Delivery</h3>
                        
                        <div class="form-group">
                            <label for="news-frequency">News Update Frequency</label>
                            <select id="news-frequency" name="news_frequency" class="form-control">
                                <?php 
                                $news_freq = get_user_meta($current_user->ID, 'news_frequency', true) ?: 'hourly';
                                ?>
                                <option value="realtime" <?php selected($news_freq, 'realtime'); ?>>Real-time</option>
                                <option value="hourly" <?php selected($news_freq, 'hourly'); ?>>Hourly</option>
                                <option value="daily" <?php selected($news_freq, 'daily'); ?>>Daily Digest</option>
                                <option value="weekly" <?php selected($news_freq, 'weekly'); ?>>Weekly Summary</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="min-relevance">Minimum Relevance Score</label>
                            <input type="range" id="min-relevance" name="min_relevance_score" 
                                   min="0" max="100" value="<?php echo esc_attr(get_user_meta($current_user->ID, 'min_relevance_score', true) ?: '50'); ?>" 
                                   class="form-range">
                            <div class="range-labels">
                                <span>0% (All News)</span>
                                <span id="relevance-value">50%</span>
                                <span>100% (Highly Relevant)</span>
                            </div>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>News Categories</h3>
                        
                        <div class="checkbox-grid">
                            <?php 
                            $categories = array(
                                'earnings' => 'Earnings Reports',
                                'analyst_ratings' => 'Analyst Ratings',
                                'market_news' => 'Market News',
                                'economic_data' => 'Economic Data',
                                'mergers' => 'Mergers & Acquisitions',
                                'ipo' => 'IPOs',
                                'crypto' => 'Cryptocurrency',
                                'commodities' => 'Commodities'
                            );
                            $user_categories = get_user_meta($current_user->ID, 'preferred_news_categories', true) ?: array();
                            ?>
                            <?php foreach ($categories as $value => $label): ?>
                                <label class="checkbox-item">
                                    <input type="checkbox" name="preferred_news_categories[]" value="<?php echo esc_attr($value); ?>" 
                                           <?php checked(in_array($value, $user_categories)); ?>>
                                    <?php echo esc_html($label); ?>
                                </label>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Auto-sync Settings</h3>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="auto_sync_portfolio_news" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'auto_sync_portfolio_news', true), 1); ?>>
                                Automatically sync news interests with portfolio changes
                            </label>
                            <small class="form-text">When you add/remove stocks from portfolios, automatically update news preferences</small>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Save News Preferences</button>
                </form>
            </div>

            <!-- Watchlist Settings -->
            <div class="settings-panel" id="watchlist-settings">
                <div class="panel-header">
                    <h2>Watchlist Settings</h2>
                    <p>Configure your watchlist preferences and alerts</p>
                </div>

                <form class="settings-form" id="watchlist-settings-form">
                    <div class="form-section">
                        <h3>Default Settings</h3>
                        
                        <div class="form-group">
                            <label for="default-watchlist-name">Default Watchlist Name</label>
                            <input type="text" id="default-watchlist-name" name="default_watchlist_name" 
                                   value="<?php echo esc_attr(get_user_meta($current_user->ID, 'default_watchlist_name', true) ?: 'Watchlist {date}'); ?>" 
                                   class="form-control">
                        </div>

                        <div class="form-group">
                            <label for="export-format">Export Format Preference</label>
                            <select id="export-format" name="watchlist_export_format" class="form-control">
                                <?php 
                                $export_format = get_user_meta($current_user->ID, 'watchlist_export_format', true) ?: 'csv';
                                ?>
                                <option value="csv" <?php selected($export_format, 'csv'); ?>>CSV</option>
                                <option value="json" <?php selected($export_format, 'json'); ?>>JSON</option>
                                <option value="excel" <?php selected($export_format, 'excel'); ?>>Excel</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Price Alert Preferences</h3>
                        
                        <div class="form-group">
                            <label for="alert-frequency">Alert Check Frequency</label>
                            <select id="alert-frequency" name="price_alert_frequency" class="form-control">
                                <?php 
                                $alert_freq = get_user_meta($current_user->ID, 'price_alert_frequency', true) ?: '15min';
                                ?>
                                <option value="1min" <?php selected($alert_freq, '1min'); ?>>Every minute (Premium)</option>
                                <option value="5min" <?php selected($alert_freq, '5min'); ?>>Every 5 minutes</option>
                                <option value="15min" <?php selected($alert_freq, '15min'); ?>>Every 15 minutes</option>
                                <option value="1hour" <?php selected($alert_freq, '1hour'); ?>>Hourly</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="email_alerts" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'email_alerts', true), 1); ?>>
                                Send price alerts via email
                            </label>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="browser_notifications" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'browser_notifications', true), 1); ?>>
                                Show browser notifications for alerts
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Save Watchlist Settings</button>
                </form>
            </div>

            <!-- Notifications -->
            <div class="settings-panel" id="notifications">
                <div class="panel-header">
                    <h2>Notification Settings</h2>
                    <p>Control how and when you receive notifications</p>
                </div>

                <form class="settings-form" id="notification-form">
                    <div class="form-section">
                        <h3>Email Notifications</h3>
                        
                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>Price Alerts</strong>
                                <small>When stocks hit your target prices</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="email_price_alerts" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'email_price_alerts', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>Portfolio Updates</strong>
                                <small>Daily/weekly portfolio performance summaries</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="email_portfolio_updates" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'email_portfolio_updates', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>News Digest</strong>
                                <small>Personalized news summaries</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="email_news_digest" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'email_news_digest', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>Marketing Emails</strong>
                                <small>Product updates and educational content</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="email_marketing" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'email_marketing', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Push Notifications</h3>
                        
                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>Breaking News</strong>
                                <small>Important market news and alerts</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="push_breaking_news" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'push_breaking_news', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="notification-item">
                            <div class="notification-content">
                                <strong>Market Open/Close</strong>
                                <small>Notifications when markets open and close</small>
                            </div>
                            <label class="switch">
                                <input type="checkbox" name="push_market_hours" value="1" 
                                       <?php checked(get_user_meta($current_user->ID, 'push_market_hours', true), 1); ?>>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Save Notification Settings</button>
                </form>
            </div>

            <!-- Security -->
            <div class="settings-panel" id="security">
                <div class="panel-header">
                    <h2>Security Settings</h2>
                    <p>Manage your account security and privacy</p>
                </div>

                <div class="security-sections">
                    <div class="form-section">
                        <h3>Change Password</h3>
                        
                        <form class="settings-form" id="password-form">
                            <div class="form-group">
                                <label for="current-password">Current Password</label>
                                <input type="password" id="current-password" name="current_password" class="form-control" required>
                            </div>

                            <div class="form-group">
                                <label for="new-password">New Password</label>
                                <input type="password" id="new-password" name="new_password" class="form-control" required>
                                <div class="password-strength" id="password-strength-display"></div>
                            </div>

                            <div class="form-group">
                                <label for="confirm-password">Confirm New Password</label>
                                <input type="password" id="confirm-password" name="confirm_password" class="form-control" required>
                            </div>

                            <button type="submit" class="btn btn-primary">Update Password</button>
                        </form>
                    </div>

                    <div class="form-section">
                        <h3>Two-Factor Authentication</h3>
                        
                        <div class="security-feature">
                            <div class="feature-info">
                                <strong>Enable 2FA</strong>
                                <p>Add an extra layer of security to your account</p>
                            </div>
                            <button class="btn btn-outline" id="setup-2fa">Setup 2FA</button>
                        </div>
                    </div>

                    <div class="form-section">
                        <h3>Login Sessions</h3>
                        
                        <div class="session-list">
                            <div class="session-item">
                                <div class="session-info">
                                    <strong>Current Session</strong>
                                    <small>Chrome on Windows • Last active: Now</small>
                                </div>
                                <span class="session-status current">Current</span>
                            </div>
                        </div>
                        
                        <button class="btn btn-outline-danger" id="logout-all">Log Out All Other Sessions</button>
                    </div>
                </div>
            </div>

            <!-- Data Export -->
            <div class="settings-panel" id="data-export">
                <div class="panel-header">
                    <h2>Data Export</h2>
                    <p>Download your data for backup or transfer purposes</p>
                </div>

                <div class="export-sections">
                    <div class="export-option">
                        <div class="export-info">
                            <h3>🗂️ Complete Account Data</h3>
                            <p>Download all your account data including profile, portfolios, watchlists, and settings</p>
                            <small>Format: ZIP file containing JSON and CSV files</small>
                        </div>
                        <button class="btn btn-primary export-btn" data-type="complete">Download Complete Data</button>
                    </div>

                    <div class="export-option">
                        <div class="export-info">
                            <h3>📊 Portfolio Data</h3>
                            <p>Export all your portfolios, holdings, and transaction history</p>
                            <small>Format: CSV or JSON</small>
                        </div>
                        <div class="export-controls">
                            <select class="export-format" data-type="portfolios">
                                <option value="csv">CSV Format</option>
                                <option value="json">JSON Format</option>
                            </select>
                            <button class="btn btn-primary export-btn" data-type="portfolios">Download Portfolios</button>
                        </div>
                    </div>

                    <div class="export-option">
                        <div class="export-info">
                            <h3>👁️ Watchlist Data</h3>
                            <p>Export all your watchlists and alerts</p>
                            <small>Format: CSV or JSON</small>
                        </div>
                        <div class="export-controls">
                            <select class="export-format" data-type="watchlists">
                                <option value="csv">CSV Format</option>
                                <option value="json">JSON Format</option>
                            </select>
                            <button class="btn btn-primary export-btn" data-type="watchlists">Download Watchlists</button>
                        </div>
                    </div>

                    <div class="export-option">
                        <div class="export-info">
                            <h3>⚙️ Settings & Preferences</h3>
                            <p>Export your account settings and preferences</p>
                            <small>Format: JSON</small>
                        </div>
                        <button class="btn btn-primary export-btn" data-type="settings">Download Settings</button>
                    </div>
                </div>

                <div class="gdpr-notice">
                    <h4>📋 GDPR Data Request</h4>
                    <p>If you need a complete copy of all personal data we have about you (including data not accessible through this interface), you can request it using the button below. We'll email you a complete data archive within 30 days.</p>
                    <button class="btn btn-outline" id="gdpr-request">Request Complete GDPR Data Archive</button>
                </div>
            </div>

            <!-- Membership -->
            <div class="settings-panel" id="membership">
                <div class="panel-header">
                    <h2>Membership & Billing</h2>
                    <p>Manage your subscription and billing information</p>
                </div>

                <div class="membership-info">
                    <div class="current-plan">
                        <h3>Current Plan: <span class="plan-name <?php echo esc_attr($membership_level); ?>"><?php echo esc_html(ucfirst($membership_level)); ?></span></h3>
                        <?php if ($membership_level === 'free'): ?>
                            <p>Upgrade to unlock premium features and higher limits</p>
                        <?php else: ?>
                            <p>Thank you for being a premium member!</p>
                        <?php endif; ?>
                    </div>

                    <div class="plan-features">
                        <h4>Your Current Features:</h4>
                        <?php 
                        $limits = get_user_limits($current_user->ID);
                        ?>
                        <ul class="feature-list">
                            <li>📊 <?php echo $limits['portfolios'] == -1 ? 'Unlimited' : $limits['portfolios']; ?> Portfolios</li>
                            <li>👁️ <?php echo $limits['watchlists'] == -1 ? 'Unlimited' : $limits['watchlists']; ?> Watchlists</li>
                            <li>🔔 <?php echo $limits['api_calls'] == -1 ? 'Unlimited' : $limits['api_calls']; ?> API Calls/Month</li>
                            <li>📈 <?php echo $limits['holdings'] == -1 ? 'Unlimited' : $limits['holdings']; ?> Holdings per Portfolio</li>
                        </ul>
                    </div>

                    <?php if ($membership_level !== 'gold'): ?>
                        <div class="upgrade-section">
                            <h4>Upgrade Your Plan</h4>
                            <div class="upgrade-options">
                                <a href="/premium-plans/" class="btn btn-success">View Upgrade Options</a>
                                <a href="/premium-plans/?plan=gold" class="btn btn-outline">Go Gold - All Features</a>
                            </div>
                        </div>
                    <?php endif; ?>

                    <?php if ($membership_level !== 'free'): ?>
                        <div class="billing-section">
                            <h4>Billing Information</h4>
                            <p>Manage your payment method and billing details</p>
                            <button class="btn btn-outline" id="manage-billing">Manage Billing</button>
                            <button class="btn btn-outline-danger" id="cancel-subscription">Cancel Subscription</button>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* User Settings Page Styles */
.user-settings-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.settings-header {
    text-align: center;
    margin-bottom: 40px;
}

.settings-header h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin: 0 0 10px 0;
}

.settings-subtitle {
    color: #7f8c8d;
    font-size: 1.1rem;
    margin: 0;
}

.settings-content {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 30px;
}

/* Settings Navigation */
.settings-nav {
    position: sticky;
    top: 20px;
    height: fit-content;
}

.settings-tabs {
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.settings-tab {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    color: #7f8c8d;
    text-decoration: none;
    border-radius: 8px;
    transition: all 0.3s ease;
    margin-bottom: 2px;
}

.settings-tab:hover {
    background: #f8f9fa;
    color: #2c3e50;
}

.settings-tab.active {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.tab-icon {
    margin-right: 10px;
    font-size: 1.1rem;
}

/* Settings Panels */
.settings-panels {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.settings-panel {
    display: none;
}

.settings-panel.active {
    display: block;
    animation: fadeInSlide 0.4s ease-in-out;
}

@keyframes fadeInSlide {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.panel-header {
    margin-bottom: 30px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 15px;
}

.panel-header h2 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.8rem;
}

.panel-header p {
    margin: 0;
    color: #7f8c8d;
    font-size: 1.1rem;
}

/* Form Styles */
.settings-form {
    max-width: 800px;
}

.form-section {
    margin-bottom: 40px;
    padding: 25px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.form-section h3 {
    margin: 0 0 20px 0;
    color: #2c3e50;
    font-size: 1.3rem;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c3e50;
}

.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: white;
}

.form-control:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-text {
    display: block;
    margin-top: 5px;
    font-size: 0.9rem;
    color: #6c757d;
}

/* Range Slider */
.form-range {
    width: 100%;
    margin: 10px 0;
}

.range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #6c757d;
}

#relevance-value {
    font-weight: 600;
    color: #3498db;
}

/* Checkbox Grid */
.checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.checkbox-item {
    display: flex;
    align-items: center;
    padding: 10px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.checkbox-item:hover {
    background: #f1f3f4;
    border-color: #3498db;
}

.checkbox-item input[type="checkbox"] {
    margin-right: 10px;
    transform: scale(1.2);
}

/* Notification Items */
.notification-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-bottom: 10px;
}

.notification-content strong {
    display: block;
    color: #2c3e50;
    margin-bottom: 4px;
}

.notification-content small {
    color: #6c757d;
}

/* Toggle Switch */
.switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.4s;
    border-radius: 24px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: #3498db;
}

input:checked + .slider:before {
    transform: translateX(26px);
}

/* Security Features */
.security-sections .form-section {
    background: white;
    border: 1px solid #e9ecef;
}

.security-feature {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

.feature-info strong {
    display: block;
    color: #2c3e50;
    margin-bottom: 5px;
}

.feature-info p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
}

.session-list {
    margin: 20px 0;
}

.session-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-bottom: 10px;
}

.session-info strong {
    display: block;
    color: #2c3e50;
}

.session-info small {
    color: #6c757d;
}

.session-status {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.session-status.current {
    background: #d1ecf1;
    color: #0c5460;
}

/* Export Options */
.export-sections {
    margin-bottom: 30px;
}

.export-option {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 25px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-bottom: 15px;
}

.export-info h3 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.2rem;
}

.export-info p {
    margin: 0 0 5px 0;
    color: #495057;
}

.export-info small {
    color: #6c757d;
}

.export-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.export-format {
    padding: 8px 12px;
    border: 1px solid #ced4da;
    border-radius: 6px;
    background: white;
}

.gdpr-notice {
    background: #e7f3ff;
    border: 1px solid #b8daff;
    border-radius: 8px;
    padding: 20px;
    margin-top: 30px;
}

.gdpr-notice h4 {
    margin: 0 0 10px 0;
    color: #004085;
}

.gdpr-notice p {
    margin: 0 0 15px 0;
    color: #004085;
}

/* Membership Section */
.membership-info {
    max-width: 600px;
}

.current-plan {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.current-plan h3 {
    margin: 0 0 10px 0;
    color: #2c3e50;
}

.plan-name {
    text-transform: capitalize;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.9rem;
}

.plan-name.free {
    background: #6c757d;
    color: white;
}

.plan-name.bronze {
    background: #cd7f32;
    color: white;
}

.plan-name.silver {
    background: #c0c0c0;
    color: #000;
}

.plan-name.gold {
    background: #ffd700;
    color: #000;
}

.plan-features {
    margin-bottom: 25px;
}

.feature-list {
    list-style: none;
    padding: 0;
    margin: 10px 0;
}

.feature-list li {
    padding: 8px 0;
    border-bottom: 1px solid #e9ecef;
    font-size: 1rem;
}

.upgrade-section,
.billing-section {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.upgrade-options {
    display: flex;
    gap: 15px;
    margin-top: 15px;
}

/* Buttons */
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #2980b9, #21618c);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.btn-success {
    background: linear-gradient(135deg, #27ae60, #229954);
    color: white;
}

.btn-success:hover {
    background: linear-gradient(135deg, #229954, #1e8449);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
}

.btn-outline {
    background: transparent;
    border: 2px solid #3498db;
    color: #3498db;
}

.btn-outline:hover {
    background: #3498db;
    color: white;
}

.btn-outline-danger {
    background: transparent;
    border: 2px solid #e74c3c;
    color: #e74c3c;
}

.btn-outline-danger:hover {
    background: #e74c3c;
    color: white;
}

/* Password Strength */
.password-strength {
    margin-top: 8px;
    font-size: 0.9rem;
    font-weight: 600;
}

.password-strength.weak { color: #e74c3c; }
.password-strength.medium { color: #f39c12; }
.password-strength.strong { color: #27ae60; }

/* Responsive Design */
@media (max-width: 768px) {
    .settings-content {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .settings-nav {
        position: static;
    }
    
    .settings-tabs {
        flex-direction: row;
        overflow-x: auto;
        padding: 10px;
    }
    
    .settings-tab {
        white-space: nowrap;
        min-width: fit-content;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .export-option {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
    
    .export-controls {
        width: 100%;
        justify-content: flex-end;
    }
    
    .upgrade-options {
        flex-direction: column;
    }
    
    .checkbox-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .user-settings-container {
        padding: 10px;
    }
    
    .settings-panels {
        padding: 20px;
    }
    
    .form-section {
        padding: 15px;
    }
}
</style>

<script>
// Settings page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Tab navigation
    const tabs = document.querySelectorAll('.settings-tab');
    const panels = document.querySelectorAll('.settings-panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetPanel = this.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show target panel
            panels.forEach(p => p.classList.remove('active'));
            document.getElementById(targetPanel).classList.add('active');
            
            // Update URL hash
            window.location.hash = targetPanel;
            
            // Scroll to top of content
            document.querySelector('.settings-panels').scrollTop = 0;
        });
    });
    
    // Check URL hash on load
    if (window.location.hash) {
        const targetTab = window.location.hash.substring(1);
        const targetTabElement = document.querySelector(`[data-tab="${targetTab}"]`);
        if (targetTabElement) {
            targetTabElement.click();
        }
    }
    
    // Range slider for relevance score
    const relevanceSlider = document.getElementById('min-relevance');
    const relevanceValue = document.getElementById('relevance-value');
    
    if (relevanceSlider && relevanceValue) {
        relevanceSlider.addEventListener('input', function() {
            relevanceValue.textContent = this.value + '%';
        });
    }
    
    // Password strength checker
    const newPasswordField = document.getElementById('new-password');
    const strengthDisplay = document.getElementById('password-strength-display');
    
    if (newPasswordField && strengthDisplay) {
        newPasswordField.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            
            if (password.length >= 8) strength++;
            if (/[a-z]/.test(password)) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;
            
            strengthDisplay.className = 'password-strength';
            
            if (strength < 3) {
                strengthDisplay.textContent = 'Weak password';
                strengthDisplay.classList.add('weak');
            } else if (strength < 4) {
                strengthDisplay.textContent = 'Medium strength';
                strengthDisplay.classList.add('medium');
            } else {
                strengthDisplay.textContent = 'Strong password';
                strengthDisplay.classList.add('strong');
            }
        });
    }
    
    // Form submissions
    const forms = document.querySelectorAll('.settings-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';
            
            // Simulate form submission
            setTimeout(function() {
                alert('Settings saved successfully!');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 1000);
        });
    });
    
    // Export functionality
    const exportBtns = document.querySelectorAll('.export-btn');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const exportType = this.getAttribute('data-type');
            const formatSelect = document.querySelector(`.export-format[data-type="${exportType}"]`);
            const format = formatSelect ? formatSelect.value : 'json';
            
            this.disabled = true;
            this.textContent = 'Preparing Export...';
            
            // Simulate export preparation
            setTimeout(() => {
                alert(`${exportType} data export ready for download (${format} format)`);
                this.disabled = false;
                this.textContent = this.textContent.replace('Preparing Export...', 'Download');
            }, 2000);
        });
    });
    
    // GDPR request
    const gdprBtn = document.getElementById('gdpr-request');
    if (gdprBtn) {
        gdprBtn.addEventListener('click', function() {
            if (confirm('Request complete GDPR data archive? We will email you the archive within 30 days.')) {
                this.disabled = true;
                this.textContent = 'Request Submitted';
                alert('GDPR data request submitted. You will receive an email confirmation shortly.');
            }
        });
    }
    
    // 2FA setup
    const setup2faBtn = document.getElementById('setup-2fa');
    if (setup2faBtn) {
        setup2faBtn.addEventListener('click', function() {
            alert('2FA setup would redirect to authentication setup page');
        });
    }
    
    // Logout all sessions
    const logoutAllBtn = document.getElementById('logout-all');
    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', function() {
            if (confirm('Log out all other sessions? You will remain logged in on this device.')) {
                alert('All other sessions have been logged out.');
            }
        });
    }
    
    // Billing management
    const manageBillingBtn = document.getElementById('manage-billing');
    if (manageBillingBtn) {
        manageBillingBtn.addEventListener('click', function() {
            alert('Would redirect to billing management portal');
        });
    }
    
    // Cancel subscription
    const cancelSubBtn = document.getElementById('cancel-subscription');
    if (cancelSubBtn) {
        cancelSubBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to cancel your subscription? This action cannot be undone.')) {
                alert('Subscription cancellation would be processed');
            }
        });
    }
});
</script>

<?php get_footer(); ?>