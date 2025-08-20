<?php
/**
 * Template Name: User Settings
 * 
 * User account settings, preferences, and subscription management
 *
 * @package StockScannerPro
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="user-settings-container">
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="container">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">Account Settings</h1>
                    <p class="text-gray-600 mt-2">Manage your account preferences and subscription</p>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="settings-layout">
            <!-- Settings Sidebar -->
            <aside class="settings-sidebar">
                <nav class="settings-nav" aria-label="Settings Navigation">
                    <ul class="settings-nav-list">
                        <li class="settings-nav-item">
                            <a href="#profile" class="settings-nav-link active" data-section="profile">
                                <i class="fas fa-user mr-3"></i>
                                Profile Information
                            </a>
                        </li>
                        <li class="settings-nav-item">
                            <a href="#preferences" class="settings-nav-link" data-section="preferences">
                                <i class="fas fa-cog mr-3"></i>
                                Preferences
                            </a>
                        </li>
                        <li class="settings-nav-item">
                            <a href="#notifications" class="settings-nav-link" data-section="notifications">
                                <i class="fas fa-bell mr-3"></i>
                                Notifications
                            </a>
                        </li>
                        <li class="settings-nav-item">
                            <a href="#subscription" class="settings-nav-link" data-section="subscription">
                                <i class="fas fa-credit-card mr-3"></i>
                                Subscription
                            </a>
                        </li>
                        <li class="settings-nav-item">
                            <a href="#security" class="settings-nav-link" data-section="security">
                                <i class="fas fa-shield-alt mr-3"></i>
                                Security
                            </a>
                        </li>
                        <li class="settings-nav-item">
                            <a href="#privacy" class="settings-nav-link" data-section="privacy">
                                <i class="fas fa-lock mr-3"></i>
                                Privacy
                            </a>
                        </li>
                    </ul>
                </nav>
            </aside>

            <!-- Settings Content -->
            <main class="settings-content">
                
                <!-- Profile Information Section -->
                <section id="profile-section" class="settings-section active">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Profile Information</h2>
                        <p class="settings-section-description">Update your personal information and avatar</p>
                    </div>

                    <div class="settings-card">
                        <form id="profile-form" class="settings-form">
                            <div class="profile-avatar-section mb-6">
                                <div class="avatar-upload-wrapper">
                                    <div class="current-avatar">
                                        <?php echo get_avatar(get_current_user_id(), 80, '', '', array('class' => 'avatar-image')); ?>
                                    </div>
                                    <div class="avatar-upload-controls">
                                        <button type="button" class="btn btn-outline-primary btn-sm" id="change-avatar-btn">
                                            <i class="fas fa-camera mr-2"></i>
                                            Change Avatar
                                        </button>
                                        <input type="file" id="avatar-upload" accept="image/*" style="display: none;">
                                    </div>
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label for="first-name" class="form-label">First Name</label>
                                    <input type="text" class="form-control" id="first-name" name="first_name" value="<?php echo esc_attr(get_user_meta(get_current_user_id(), 'first_name', true)); ?>">
                                </div>
                                <div class="form-group">
                                    <label for="last-name" class="form-label">Last Name</label>
                                    <input type="text" class="form-control" id="last-name" name="last_name" value="<?php echo esc_attr(get_user_meta(get_current_user_id(), 'last_name', true)); ?>">
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="display-name" class="form-label">Display Name</label>
                                <input type="text" class="form-control" id="display-name" name="display_name" value="<?php echo esc_attr(wp_get_current_user()->display_name); ?>">
                            </div>

                            <div class="form-group">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="user_email" value="<?php echo esc_attr(wp_get_current_user()->user_email); ?>">
                            </div>

                            <div class="form-group">
                                <label for="bio" class="form-label">Bio</label>
                                <textarea class="form-control" id="bio" name="description" rows="4" placeholder="Tell us about yourself"><?php echo esc_textarea(get_user_meta(get_current_user_id(), 'description', true)); ?></textarea>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Save Changes</button>
                                <button type="button" class="btn btn-outline-secondary" id="reset-profile-btn">Reset</button>
                            </div>
                        </form>
                    </div>
                </section>

                <!-- Preferences Section -->
                <section id="preferences-section" class="settings-section">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Preferences</h2>
                        <p class="settings-section-description">Customize your experience</p>
                    </div>

                    <div class="settings-card">
                        <form id="preferences-form" class="settings-form">
                            <div class="preference-group">
                                <h4 class="preference-group-title">Appearance</h4>
                                <div class="form-group">
                                    <label for="theme-preference" class="form-label">Theme</label>
                                    <select class="form-select" id="theme-preference" name="theme">
                                        <option value="auto">Auto (System)</option>
                                        <option value="light">Light</option>
                                        <option value="dark">Dark</option>
                                    </select>
                                </div>
                            </div>

                            <div class="preference-group">
                                <h4 class="preference-group-title">Dashboard</h4>
                                <div class="form-group">
                                    <label for="default-currency" class="form-label">Default Currency</label>
                                    <select class="form-select" id="default-currency" name="currency">
                                        <option value="USD">USD - US Dollar</option>
                                        <option value="EUR">EUR - Euro</option>
                                        <option value="GBP">GBP - British Pound</option>
                                        <option value="CAD">CAD - Canadian Dollar</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="refresh-interval" class="form-label">Data Refresh Interval</label>
                                    <select class="form-select" id="refresh-interval" name="refresh_interval">
                                        <option value="30">30 seconds</option>
                                        <option value="60">1 minute</option>
                                        <option value="120">2 minutes</option>
                                        <option value="300">5 minutes</option>
                                    </select>
                                </div>
                            </div>

                            <div class="preference-group">
                                <h4 class="preference-group-title">Trading</h4>
                                <div class="form-group">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="show-after-hours" name="show_after_hours">
                                        <label class="form-check-label" for="show-after-hours">
                                            Show after-hours trading data
                                        </label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="show-pre-market" name="show_pre_market">
                                        <label class="form-check-label" for="show-pre-market">
                                            Show pre-market trading data
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Save Preferences</button>
                            </div>
                        </form>
                    </div>
                </section>

                <!-- Notifications Section -->
                <section id="notifications-section" class="settings-section">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Notification Settings</h2>
                        <p class="settings-section-description">Choose how you want to be notified</p>
                    </div>

                    <div class="settings-card">
                        <form id="notifications-form" class="settings-form">
                            <div class="notification-group">
                                <h4 class="notification-group-title">Price Alerts</h4>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="email-price-alerts" name="email_price_alerts">
                                        <label class="form-check-label" for="email-price-alerts">
                                            Email notifications for price alerts
                                        </label>
                                    </div>
                                </div>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="browser-price-alerts" name="browser_price_alerts">
                                        <label class="form-check-label" for="browser-price-alerts">
                                            Browser notifications for price alerts
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="notification-group">
                                <h4 class="notification-group-title">Portfolio Updates</h4>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="daily-portfolio-email" name="daily_portfolio_email">
                                        <label class="form-check-label" for="daily-portfolio-email">
                                            Daily portfolio summary email
                                        </label>
                                    </div>
                                </div>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="weekly-portfolio-email" name="weekly_portfolio_email">
                                        <label class="form-check-label" for="weekly-portfolio-email">
                                            Weekly portfolio performance email
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="notification-group">
                                <h4 class="notification-group-title">News & Updates</h4>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="market-news-email" name="market_news_email">
                                        <label class="form-check-label" for="market-news-email">
                                            Market news and analysis
                                        </label>
                                    </div>
                                </div>
                                <div class="notification-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="product-updates-email" name="product_updates_email">
                                        <label class="form-check-label" for="product-updates-email">
                                            Product updates and new features
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Save Notification Settings</button>
                            </div>
                        </form>
                    </div>
                </section>

                <!-- Subscription Section -->
                <section id="subscription-section" class="settings-section">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Subscription & Billing</h2>
                        <p class="settings-section-description">Manage your subscription and billing information</p>
                    </div>

                    <div class="settings-card">
                        <div id="subscription-info">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </section>

                <!-- Security Section -->
                <section id="security-section" class="settings-section">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Security Settings</h2>
                        <p class="settings-section-description">Secure your account and data</p>
                    </div>

                    <div class="settings-card">
                        <form id="security-form" class="settings-form">
                            <div class="security-group">
                                <h4 class="security-group-title">Change Password</h4>
                                <div class="form-group">
                                    <label for="current-password" class="form-label">Current Password</label>
                                    <input type="password" class="form-control" id="current-password" name="current_password">
                                </div>
                                <div class="form-group">
                                    <label for="new-password" class="form-label">New Password</label>
                                    <input type="password" class="form-control" id="new-password" name="new_password">
                                </div>
                                <div class="form-group">
                                    <label for="confirm-password" class="form-label">Confirm New Password</label>
                                    <input type="password" class="form-control" id="confirm-password" name="confirm_password">
                                </div>
                            </div>

                            <div class="security-group">
                                <h4 class="security-group-title">Two-Factor Authentication</h4>
                                <div id="two-factor-status">
                                    <!-- Populated by JavaScript -->
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Update Security Settings</button>
                            </div>
                        </form>
                    </div>
                </section>

                <!-- Privacy Section -->
                <section id="privacy-section" class="settings-section">
                    <div class="settings-section-header">
                        <h2 class="settings-section-title">Privacy Settings</h2>
                        <p class="settings-section-description">Control your data and privacy preferences</p>
                    </div>

                    <div class="settings-card">
                        <form id="privacy-form" class="settings-form">
                            <div class="privacy-group">
                                <h4 class="privacy-group-title">Data Sharing</h4>
                                <div class="privacy-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="analytics-sharing" name="analytics_sharing">
                                        <label class="form-check-label" for="analytics-sharing">
                                            Share anonymized usage data to help improve our services
                                        </label>
                                    </div>
                                </div>
                                <div class="privacy-option">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="marketing-communications" name="marketing_communications">
                                        <label class="form-check-label" for="marketing-communications">
                                            Receive marketing communications from us
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="privacy-group">
                                <h4 class="privacy-group-title">Data Export & Deletion</h4>
                                <p class="privacy-description">You have the right to request a copy of your data or delete your account.</p>
                                <div class="privacy-actions">
                                    <button type="button" class="btn btn-outline-primary" id="export-data-btn">
                                        <i class="fas fa-download mr-2"></i>
                                        Export My Data
                                    </button>
                                    <button type="button" class="btn btn-outline-danger" id="delete-account-btn">
                                        <i class="fas fa-trash mr-2"></i>
                                        Delete Account
                                    </button>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">Save Privacy Settings</button>
                            </div>
                        </form>
                    </div>
                </section>

            </main>
        </div>
    </div>
</div>

<script>
// Initialize user settings when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerUserSettings !== 'undefined') {
        StockScannerUserSettings.init();
    }
});
</script>

<?php get_footer(); ?>