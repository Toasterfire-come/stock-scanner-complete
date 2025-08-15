<?php
/**
 * Template Name: Account
 * 
 * The template for displaying user account management
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="account-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-user-circle"></i>
                My Account
            </h1>
            <p class="page-subtitle">Manage your profile, subscription, and account preferences</p>
        </div>
    </div>

    <div class="account-content">
        <div class="container">
            <div class="account-layout">
                <!-- Account Sidebar -->
                <div class="account-sidebar">
                    <div class="user-info">
                        <div class="avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="user-details">
                            <div class="user-name"><?php echo esc_html(wp_get_current_user()->display_name); ?></div>
                            <div class="user-email"><?php echo esc_html(wp_get_current_user()->user_email); ?></div>
                            <div class="membership-badge">
                                <i class="fas fa-star"></i>
                                Pro Member
                            </div>
                        </div>
                    </div>

                    <nav class="account-nav">
                        <button class="nav-item active" data-section="profile">
                            <i class="fas fa-user"></i>
                            Profile
                        </button>
                        <button class="nav-item" data-section="subscription">
                            <i class="fas fa-credit-card"></i>
                            Subscription
                        </button>
                        <button class="nav-item" data-section="preferences">
                            <i class="fas fa-cog"></i>
                            Preferences
                        </button>
                        <button class="nav-item" data-section="security">
                            <i class="fas fa-shield-alt"></i>
                            Security
                        </button>
                        <button class="nav-item" data-section="notifications">
                            <i class="fas fa-bell"></i>
                            Notifications
                        </button>
                        <a href="/billing-history/" class="nav-item">
                            <i class="fas fa-receipt"></i>
                            Billing History
                        </a>
                    </nav>

                    <div class="account-actions">
                        <a href="<?php echo wp_logout_url(home_url()); ?>" class="btn btn-outline">
                            <i class="fas fa-sign-out-alt"></i>
                            Sign Out
                        </a>
                    </div>
                </div>

                <!-- Main Content -->
                <div class="account-main">
                    <!-- Profile Section -->
                    <div class="account-section active" id="profile">
                        <div class="section-header">
                            <h2>Profile Information</h2>
                            <p>Update your personal information and profile details</p>
                        </div>

                        <form class="profile-form" id="profileForm">
                            <?php wp_nonce_field('update_profile', 'profile_nonce'); ?>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="firstName">First Name</label>
                                    <input type="text" id="firstName" name="first_name" value="<?php echo esc_attr(get_user_meta(get_current_user_id(), 'first_name', true)); ?>" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label for="lastName">Last Name</label>
                                    <input type="text" id="lastName" name="last_name" value="<?php echo esc_attr(get_user_meta(get_current_user_id(), 'last_name', true)); ?>" class="form-input">
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="displayName">Display Name</label>
                                <input type="text" id="displayName" name="display_name" value="<?php echo esc_attr(wp_get_current_user()->display_name); ?>" class="form-input">
                            </div>

                            <div class="form-group">
                                <label for="email">Email Address</label>
                                <input type="email" id="email" name="email" value="<?php echo esc_attr(wp_get_current_user()->user_email); ?>" class="form-input">
                                <div class="field-note">Your email address is used for login and notifications</div>
                            </div>

                            <div class="form-group">
                                <label for="bio">Bio</label>
                                <textarea id="bio" name="bio" rows="4" class="form-textarea" placeholder="Tell us about yourself..."><?php echo esc_textarea(get_user_meta(get_current_user_id(), 'description', true)); ?></textarea>
                            </div>

                            <div class="form-group">
                                <label for="website">Website</label>
                                <input type="url" id="website" name="website" value="<?php echo esc_attr(get_user_meta(get_current_user_id(), 'user_url', true)); ?>" class="form-input" placeholder="https://...">
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i>
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- Subscription Section -->
                    <div class="account-section" id="subscription">
                        <div class="section-header">
                            <h2>Subscription Details</h2>
                            <p>Manage your subscription plan and billing information</p>
                        </div>

                        <div class="subscription-card">
                            <div class="plan-info">
                                <div class="plan-badge">
                                    <i class="fas fa-star"></i>
                                    Pro Plan
                                </div>
                                <div class="plan-details">
                                    <div class="plan-price">$29.99/month</div>
                                    <div class="plan-features">
                                        Real-time data, unlimited watchlists, premium alerts
                                    </div>
                                </div>
                            </div>
                            <div class="plan-actions">
                                <a href="/premium-plans/" class="btn btn-outline">Change Plan</a>
                                <button class="btn btn-danger" onclick="cancelSubscription()">Cancel</button>
                            </div>
                        </div>

                        <div class="subscription-details">
                            <div class="detail-row">
                                <span class="detail-label">Next Billing Date:</span>
                                <span class="detail-value">February 15, 2024</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Payment Method:</span>
                                <span class="detail-value">•••• •••• •••• 4321</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Status:</span>
                                <span class="detail-value status-active">Active</span>
                            </div>
                        </div>
                    </div>

                    <!-- Preferences Section -->
                    <div class="account-section" id="preferences">
                        <div class="section-header">
                            <h2>Trading Preferences</h2>
                            <p>Customize your trading experience and default settings</p>
                        </div>

                        <form class="preferences-form" id="preferencesForm">
                            <div class="form-group">
                                <label>Investment Experience</label>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="experience" value="beginner">
                                        <span class="radio-mark"></span>
                                        Beginner (< 1 year)
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="experience" value="intermediate" checked>
                                        <span class="radio-mark"></span>
                                        Intermediate (1-5 years)
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="experience" value="advanced">
                                        <span class="radio-mark"></span>
                                        Advanced (5+ years)
                                    </label>
                                </div>
                            </div>

                            <div class="form-group">
                                <label>Risk Tolerance</label>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="risk_tolerance" value="conservative">
                                        <span class="radio-mark"></span>
                                        Conservative
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="risk_tolerance" value="moderate" checked>
                                        <span class="radio-mark"></span>
                                        Moderate
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="risk_tolerance" value="aggressive">
                                        <span class="radio-mark"></span>
                                        Aggressive
                                    </label>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="defaultWatchlist">Default Watchlist View</label>
                                <select id="defaultWatchlist" name="default_watchlist" class="form-select">
                                    <option value="list">List View</option>
                                    <option value="grid">Grid View</option>
                                    <option value="chart">Chart View</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="refreshInterval">Data Refresh Interval</label>
                                <select id="refreshInterval" name="refresh_interval" class="form-select">
                                    <option value="1">1 second</option>
                                    <option value="5">5 seconds</option>
                                    <option value="30" selected>30 seconds</option>
                                    <option value="60">1 minute</option>
                                </select>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i>
                                    Save Preferences
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- Security Section -->
                    <div class="account-section" id="security">
                        <div class="section-header">
                            <h2>Security Settings</h2>
                            <p>Manage your password and security preferences</p>
                        </div>

                        <form class="security-form" id="securityForm">
                            <div class="form-group">
                                <label for="currentPassword">Current Password</label>
                                <input type="password" id="currentPassword" name="current_password" class="form-input">
                            </div>

                            <div class="form-group">
                                <label for="newPassword">New Password</label>
                                <input type="password" id="newPassword" name="new_password" class="form-input">
                                <div class="password-strength">
                                    <div class="strength-meter">
                                        <div class="strength-fill" id="strengthFill"></div>
                                    </div>
                                    <span class="strength-text" id="strengthText">Enter a password</span>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="confirmPassword">Confirm New Password</label>
                                <input type="password" id="confirmPassword" name="confirm_password" class="form-input">
                            </div>

                            <div class="security-options">
                                <h3>Security Options</h3>
                                <div class="checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="two_factor" checked>
                                        <span class="checkmark"></span>
                                        Enable Two-Factor Authentication
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="login_notifications" checked>
                                        <span class="checkmark"></span>
                                        Email notifications for new logins
                                    </label>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-shield-alt"></i>
                                    Update Security
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- Notifications Section -->
                    <div class="account-section" id="notifications">
                        <div class="section-header">
                            <h2>Notification Preferences</h2>
                            <p>Choose how and when you want to receive notifications</p>
                        </div>

                        <form class="notifications-form" id="notificationsForm">
                            <div class="notification-category">
                                <h3>Price Alerts</h3>
                                <div class="notification-options">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="price_alerts_email" checked>
                                        <span class="checkmark"></span>
                                        Email notifications
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="price_alerts_push" checked>
                                        <span class="checkmark"></span>
                                        Push notifications
                                    </label>
                                </div>
                            </div>

                            <div class="notification-category">
                                <h3>Market News</h3>
                                <div class="notification-options">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="news_email" checked>
                                        <span class="checkmark"></span>
                                        Daily market summary
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="breaking_news">
                                        <span class="checkmark"></span>
                                        Breaking news alerts
                                    </label>
                                </div>
                            </div>

                            <div class="notification-category">
                                <h3>Account Updates</h3>
                                <div class="notification-options">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="account_updates" checked>
                                        <span class="checkmark"></span>
                                        Account and billing updates
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="product_updates" checked>
                                        <span class="checkmark"></span>
                                        New features and product updates
                                    </label>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-bell"></i>
                                    Save Notifications
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.account-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 0 0;
}

.account-content {
    padding: 3rem 0;
}

.account-layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 3rem;
    align-items: start;
}

.account-sidebar {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: sticky;
    top: 2rem;
}

.user-info {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e1e5e9;
}

.avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: #3685fb;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1rem;
}

.user-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.user-email {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.membership-badge {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.account-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.nav-item {
    padding: 1rem;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.95rem;
    text-decoration: none;
    width: 100%;
    text-align: left;
}

.nav-item:hover,
.nav-item.active {
    background: #f0f9ff;
    color: #3685fb;
}

.nav-item i {
    width: 20px;
    text-align: center;
}

.account-actions {
    padding-top: 2rem;
    border-top: 1px solid #e1e5e9;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
}

.btn-outline {
    background: transparent;
    color: #666;
    border: 1px solid #e1e5e9;
    width: 100%;
    justify-content: center;
}

.btn-outline:hover {
    background: #f8f9fa;
    border-color: #3685fb;
    color: #3685fb;
}

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-danger {
    background: #ef4444;
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.account-main {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.account-section {
    display: none;
}

.account-section.active {
    display: block;
}

.section-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e1e5e9;
}

.section-header h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
}

.section-header p {
    color: #666;
    margin: 0;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
}

.form-input,
.form-select,
.form-textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
    box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.form-textarea {
    resize: vertical;
    min-height: 100px;
}

.field-note {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.5rem;
}

.radio-group,
.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.radio-label,
.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #666;
}

.radio-label input[type="radio"],
.checkbox-label input[type="checkbox"] {
    display: none;
}

.radio-mark,
.checkmark {
    width: 20px;
    height: 20px;
    border: 2px solid #e1e5e9;
    border-radius: 50%;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
}

.checkmark {
    border-radius: 4px;
}

.radio-label input[type="radio"]:checked + .radio-mark,
.checkbox-label input[type="checkbox"]:checked + .checkmark {
    background: #3685fb;
    border-color: #3685fb;
}

.radio-label input[type="radio"]:checked + .radio-mark::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    background: white;
    border-radius: 50%;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.form-actions {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e1e5e9;
}

.subscription-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.plan-badge {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.plan-price {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
}

.plan-features {
    color: #666;
    font-size: 0.9rem;
}

.plan-actions {
    display: flex;
    gap: 1rem;
}

.subscription-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
    border-bottom: none;
}

.detail-label {
    font-weight: 500;
    color: #666;
}

.detail-value {
    color: #1a1a1a;
    font-weight: 600;
}

.status-active {
    color: #10b981;
}

.password-strength {
    margin-top: 0.5rem;
}

.strength-meter {
    width: 100%;
    height: 4px;
    background: #e1e5e9;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.25rem;
}

.strength-fill {
    height: 100%;
    background: #ef4444;
    transition: all 0.3s;
    width: 0%;
}

.strength-text {
    font-size: 0.8rem;
    color: #666;
}

.security-options {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e1e5e9;
}

.security-options h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1rem 0;
}

.notification-category {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #f0f0f0;
}

.notification-category:last-child {
    border-bottom: none;
}

.notification-category h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1rem 0;
}

.notification-options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

@media (max-width: 1024px) {
    .account-layout {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .account-sidebar {
        position: static;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .subscription-card {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .plan-actions {
        justify-content: space-between;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeAccount();
});

function initializeAccount() {
    // Navigation
    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.dataset.section;
            switchSection(section);
        });
    });
    
    // Forms
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
    document.getElementById('preferencesForm').addEventListener('submit', handlePreferencesUpdate);
    document.getElementById('securityForm').addEventListener('submit', handleSecurityUpdate);
    document.getElementById('notificationsForm').addEventListener('submit', handleNotificationsUpdate);
    
    // Password strength
    document.getElementById('newPassword').addEventListener('input', updatePasswordStrength);
}

function switchSection(sectionId) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.account-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

function handleProfileUpdate(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Saved!';
        submitBtn.style.background = '#10b981';
        
        showNotification('Profile updated successfully!', 'success');
        
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.style.background = '#3685fb';
            submitBtn.disabled = false;
        }, 2000);
    }, 1500);
}

function handlePreferencesUpdate(e) {
    e.preventDefault();
    showNotification('Preferences saved successfully!', 'success');
}

function handleSecurityUpdate(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (!currentPassword) {
        showNotification('Please enter your current password', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showNotification('New passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 8) {
        showNotification('Password must be at least 8 characters long', 'error');
        return;
    }
    
    showNotification('Security settings updated successfully!', 'success');
    
    // Clear password fields
    document.getElementById('currentPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
}

function handleNotificationsUpdate(e) {
    e.preventDefault();
    showNotification('Notification preferences saved!', 'success');
}

function updatePasswordStrength() {
    const password = document.getElementById('newPassword').value;
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (!password) {
        strengthFill.style.width = '0%';
        strengthText.textContent = 'Enter a password';
        return;
    }
    
    let strength = 0;
    let feedback = [];
    
    // Length check
    if (password.length >= 8) strength += 25;
    else feedback.push('at least 8 characters');
    
    // Uppercase check
    if (/[A-Z]/.test(password)) strength += 25;
    else feedback.push('an uppercase letter');
    
    // Lowercase check
    if (/[a-z]/.test(password)) strength += 25;
    else feedback.push('a lowercase letter');
    
    // Number/special character check
    if (/[\d\W]/.test(password)) strength += 25;
    else feedback.push('a number or special character');
    
    // Update visual feedback
    strengthFill.style.width = strength + '%';
    
    if (strength <= 25) {
        strengthFill.style.background = '#ef4444';
        strengthText.textContent = 'Weak - Add ' + feedback.join(', ');
    } else if (strength <= 50) {
        strengthFill.style.background = '#f59e0b';
        strengthText.textContent = 'Fair - Add ' + feedback.join(', ');
    } else if (strength <= 75) {
        strengthFill.style.background = '#3b82f6';
        strengthText.textContent = 'Good';
    } else {
        strengthFill.style.background = '#10b981';
        strengthText.textContent = 'Strong';
    }
}

function cancelSubscription() {
    if (confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your current billing period.')) {
        showNotification('Subscription cancellation requested. You will receive a confirmation email shortly.', 'info');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3685fb',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
        zIndex: '1001',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        maxWidth: '400px'
    });
    
    const closeBtn = notification.querySelector('button');
    Object.assign(closeBtn.style, {
        background: 'none',
        border: 'none',
        color: 'white',
        fontSize: '1.25rem',
        cursor: 'pointer',
        padding: '0'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}
</script>

<?php get_footer(); ?>