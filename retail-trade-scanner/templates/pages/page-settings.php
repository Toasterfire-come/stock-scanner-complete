<?php
/**
 * Template Name: Settings
 * 
 * User settings page with tabs for profile, notifications, API integrations, and security
 *
 * @package RetailTradeScanner
 */

// Redirect non-logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

$layout_args = array(
    'page_title' => __('Settings', 'retail-trade-scanner'),
    'page_description' => __('Manage your account preferences, notifications, and integrations', 'retail-trade-scanner'),
    'page_class' => 'settings-page',
    'header_actions' => array(
        array(
            'text' => __('Export Data', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'download'
        ),
        array(
            'text' => __('Save Changes', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'save',
            'id' => 'save-settings'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

// Get current user data
$current_user = wp_get_current_user();
?>

<div class="settings-layout">
    <!-- Settings Navigation -->
    <nav class="settings-nav card glass-card">
        <div class="nav-header">
            <div class="user-avatar">
                <?php echo get_avatar($current_user->ID, 48, '', '', array('class' => 'avatar-img')); ?>
                <div class="user-info">
                    <h3><?php echo esc_html($current_user->display_name); ?></h3>
                    <p><?php echo esc_html($current_user->user_email); ?></p>
                </div>
            </div>
        </div>
        
        <ul class="nav-tabs">
            <li class="nav-item">
                <button class="nav-link active" data-tab="profile">
                    <?php echo rts_get_icon('user', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Profile', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-tab="notifications">
                    <?php echo rts_get_icon('bell', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Notifications', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-tab="preferences">
                    <?php echo rts_get_icon('settings', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Preferences', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-tab="api">
                    <?php echo rts_get_icon('key', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('API Keys', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-tab="billing">
                    <?php echo rts_get_icon('credit-card', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Billing', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link" data-tab="security">
                    <?php echo rts_get_icon('shield', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Security', 'retail-trade-scanner'); ?></span>
                </button>
            </li>
        </ul>
    </nav>

    <!-- Settings Content -->
    <div class="settings-content">
        <!-- Profile Tab -->
        <div class="settings-panel active" id="profile-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('Profile Information', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Update your personal information and trading preferences', 'retail-trade-scanner'); ?></p>
            </div>
            
            <form class="settings-form" id="profile-form">
                <div class="form-section">
                    <h3><?php esc_html_e('Personal Information', 'retail-trade-scanner'); ?></h3>
                    <div class="form-grid">
                        <div class="form-field">
                            <label class="form-label" for="first-name">
                                <?php esc_html_e('First Name', 'retail-trade-scanner'); ?>
                            </label>
                            <input type="text" 
                                   id="first-name" 
                                   class="form-input" 
                                   value="<?php echo esc_attr($current_user->first_name); ?>"
                                   placeholder="<?php esc_attr_e('Enter your first name', 'retail-trade-scanner'); ?>">
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="last-name">
                                <?php esc_html_e('Last Name', 'retail-trade-scanner'); ?>
                            </label>
                            <input type="text" 
                                   id="last-name" 
                                   class="form-input" 
                                   value="<?php echo esc_attr($current_user->last_name); ?>"
                                   placeholder="<?php esc_attr_e('Enter your last name', 'retail-trade-scanner'); ?>">
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="email">
                                <?php esc_html_e('Email Address', 'retail-trade-scanner'); ?>
                            </label>
                            <input type="email" 
                                   id="email" 
                                   class="form-input" 
                                   value="<?php echo esc_attr($current_user->user_email); ?>"
                                   placeholder="<?php esc_attr_e('Enter your email', 'retail-trade-scanner'); ?>">
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="timezone">
                                <?php esc_html_e('Timezone', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="timezone" class="form-select">
                                <option value="UTC-8">(UTC-8) Pacific Time</option>
                                <option value="UTC-5" selected>(UTC-5) Eastern Time</option>
                                <option value="UTC-6">(UTC-6) Central Time</option>
                                <option value="UTC-7">(UTC-7) Mountain Time</option>
                                <option value="UTC+0">(UTC+0) Greenwich Time</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Trading Preferences', 'retail-trade-scanner'); ?></h3>
                    <div class="form-grid">
                        <div class="form-field">
                            <label class="form-label" for="default-exchange">
                                <?php esc_html_e('Default Exchange', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="default-exchange" class="form-select">
                                <option value="NASDAQ">NASDAQ</option>
                                <option value="NYSE">NYSE</option>
                                <option value="AMEX">AMEX</option>
                                <option value="OTC">OTC Markets</option>
                            </select>
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="default-currency">
                                <?php esc_html_e('Default Currency', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="default-currency" class="form-select">
                                <option value="USD">USD - US Dollar</option>
                                <option value="EUR">EUR - Euro</option>
                                <option value="GBP">GBP - British Pound</option>
                                <option value="CAD">CAD - Canadian Dollar</option>
                            </select>
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="risk-tolerance">
                                <?php esc_html_e('Risk Tolerance', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="risk-tolerance" class="form-select">
                                <option value="conservative">Conservative</option>
                                <option value="moderate">Moderate</option>
                                <option value="aggressive">Aggressive</option>
                            </select>
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="investment-style">
                                <?php esc_html_e('Investment Style', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="investment-style" class="form-select">
                                <option value="value">Value Investing</option>
                                <option value="growth">Growth Investing</option>
                                <option value="dividend">Dividend Investing</option>
                                <option value="momentum">Momentum Trading</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Avatar & Display', 'retail-trade-scanner'); ?></h3>
                    <div class="avatar-section">
                        <div class="current-avatar">
                            <?php echo get_avatar($current_user->ID, 80, '', '', array('class' => 'avatar-preview')); ?>
                        </div>
                        <div class="avatar-controls">
                            <button type="button" class="btn btn-outline upload-avatar">
                                <?php echo rts_get_icon('upload', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Upload New Avatar', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="btn btn-ghost remove-avatar">
                                <?php esc_html_e('Remove Avatar', 'retail-trade-scanner'); ?>
                            </button>
                            <p class="avatar-help">
                                <?php esc_html_e('Recommended: 200x200px, JPG or PNG, max 2MB', 'retail-trade-scanner'); ?>
                            </p>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <!-- Notifications Tab -->
        <div class="settings-panel" id="notifications-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('Notification Preferences', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Choose how and when you want to receive notifications', 'retail-trade-scanner'); ?></p>
            </div>
            
            <form class="settings-form" id="notifications-form">
                <div class="form-section">
                    <h3><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></h3>
                    <div class="notification-options">
                        <label class="notification-item">
                            <input type="checkbox" checked>
                            <div class="notification-info">
                                <h4><?php esc_html_e('Price Target Alerts', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Get notified when stocks reach your target prices', 'retail-trade-scanner'); ?></p>
                            </div>
                            <div class="notification-methods">
                                <label class="method-checkbox">
                                    <input type="checkbox" value="email" checked>
                                    <?php echo rts_get_icon('mail', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Email', 'retail-trade-scanner'); ?></span>
                                </label>
                                <label class="method-checkbox">
                                    <input type="checkbox" value="push">
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Push', 'retail-trade-scanner'); ?></span>
                                </label>
                                <label class="method-checkbox">
                                    <input type="checkbox" value="sms">
                                    <?php echo rts_get_icon('phone', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('SMS', 'retail-trade-scanner'); ?></span>
                                </label>
                            </div>
                        </label>
                        
                        <label class="notification-item">
                            <input type="checkbox" checked>
                            <div class="notification-info">
                                <h4><?php esc_html_e('Volume Spikes', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Alert when watchlist stocks have unusual volume', 'retail-trade-scanner'); ?></p>
                            </div>
                            <div class="notification-methods">
                                <label class="method-checkbox">
                                    <input type="checkbox" value="email" checked>
                                    <?php echo rts_get_icon('mail', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Email', 'retail-trade-scanner'); ?></span>
                                </label>
                                <label class="method-checkbox">
                                    <input type="checkbox" value="push" checked>
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Push', 'retail-trade-scanner'); ?></span>
                                </label>
                            </div>
                        </label>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Market Updates', 'retail-trade-scanner'); ?></h3>
                    <div class="notification-options">
                        <label class="notification-item">
                            <input type="checkbox" checked>
                            <div class="notification-info">
                                <h4><?php esc_html_e('Daily Market Summary', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Receive end-of-day market recap and your portfolio performance', 'retail-trade-scanner'); ?></p>
                            </div>
                            <div class="notification-timing">
                                <select class="form-select">
                                    <option value="4:30"><?php esc_html_e('4:30 PM EST', 'retail-trade-scanner'); ?></option>
                                    <option value="5:00"><?php esc_html_e('5:00 PM EST', 'retail-trade-scanner'); ?></option>
                                    <option value="6:00"><?php esc_html_e('6:00 PM EST', 'retail-trade-scanner'); ?></option>
                                </select>
                            </div>
                        </label>
                        
                        <label class="notification-item">
                            <input type="checkbox">
                            <div class="notification-info">
                                <h4><?php esc_html_e('Breaking News', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Important market-moving news and events', 'retail-trade-scanner'); ?></p>
                            </div>
                            <div class="notification-methods">
                                <label class="method-checkbox">
                                    <input type="checkbox" value="push">
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Push', 'retail-trade-scanner'); ?></span>
                                </label>
                            </div>
                        </label>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Account & System', 'retail-trade-scanner'); ?></h3>
                    <div class="notification-options">
                        <label class="notification-item">
                            <input type="checkbox" checked>
                            <div class="notification-info">
                                <h4><?php esc_html_e('Security Alerts', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Login attempts, password changes, and security updates', 'retail-trade-scanner'); ?></p>
                            </div>
                        </label>
                        
                        <label class="notification-item">
                            <input type="checkbox" checked>
                            <div class="notification-info">
                                <h4><?php esc_html_e('Product Updates', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('New features, improvements, and platform updates', 'retail-trade-scanner'); ?></p>
                            </div>
                        </label>
                    </div>
                </div>
            </form>
        </div>

        <!-- Preferences Tab -->
        <div class="settings-panel" id="preferences-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('Display Preferences', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Customize your trading interface and display options', 'retail-trade-scanner'); ?></p>
            </div>
            
            <form class="settings-form" id="preferences-form">
                <div class="form-section">
                    <h3><?php esc_html_e('Theme & Display', 'retail-trade-scanner'); ?></h3>
                    <div class="preference-grid">
                        <div class="preference-item">
                            <label class="preference-label">
                                <?php esc_html_e('Theme Mode', 'retail-trade-scanner'); ?>
                            </label>
                            <div class="theme-options">
                                <label class="theme-option">
                                    <input type="radio" name="theme" value="light" checked>
                                    <div class="theme-preview light">
                                        <div class="preview-header"></div>
                                        <div class="preview-content"></div>
                                    </div>
                                    <span><?php esc_html_e('Light', 'retail-trade-scanner'); ?></span>
                                </label>
                                <label class="theme-option">
                                    <input type="radio" name="theme" value="dark">
                                    <div class="theme-preview dark">
                                        <div class="preview-header"></div>
                                        <div class="preview-content"></div>
                                    </div>
                                    <span><?php esc_html_e('Dark', 'retail-trade-scanner'); ?></span>
                                </label>
                                <label class="theme-option">
                                    <input type="radio" name="theme" value="auto">
                                    <div class="theme-preview auto">
                                        <div class="preview-header"></div>
                                        <div class="preview-content"></div>
                                    </div>
                                    <span><?php esc_html_e('Auto', 'retail-trade-scanner'); ?></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="density">
                                <?php esc_html_e('Interface Density', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="density" class="form-select">
                                <option value="compact"><?php esc_html_e('Compact', 'retail-trade-scanner'); ?></option>
                                <option value="comfortable" selected><?php esc_html_e('Comfortable', 'retail-trade-scanner'); ?></option>
                                <option value="spacious"><?php esc_html_e('Spacious', 'retail-trade-scanner'); ?></option>
                            </select>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="animations">
                                <?php esc_html_e('Animations', 'retail-trade-scanner'); ?>
                            </label>
                            <div class="toggle-switch">
                                <input type="checkbox" id="animations" checked>
                                <label for="animations" class="toggle-label"></label>
                            </div>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="sounds">
                                <?php esc_html_e('Sound Effects', 'retail-trade-scanner'); ?>
                            </label>
                            <div class="toggle-switch">
                                <input type="checkbox" id="sounds">
                                <label for="sounds" class="toggle-label"></label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Data Display', 'retail-trade-scanner'); ?></h3>
                    <div class="preference-grid">
                        <div class="preference-item">
                            <label class="preference-label" for="number-format">
                                <?php esc_html_e('Number Format', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="number-format" class="form-select">
                                <option value="us">1,234.56 (US)</option>
                                <option value="eu">1.234,56 (EU)</option>
                                <option value="simplified">1.23K (Simplified)</option>
                            </select>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="date-format">
                                <?php esc_html_e('Date Format', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="date-format" class="form-select">
                                <option value="mm/dd/yyyy">MM/DD/YYYY</option>
                                <option value="dd/mm/yyyy">DD/MM/YYYY</option>
                                <option value="yyyy-mm-dd">YYYY-MM-DD</option>
                            </select>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="default-chart">
                                <?php esc_html_e('Default Chart Type', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="default-chart" class="form-select">
                                <option value="line"><?php esc_html_e('Line Chart', 'retail-trade-scanner'); ?></option>
                                <option value="candlestick"><?php esc_html_e('Candlestick', 'retail-trade-scanner'); ?></option>
                                <option value="bar"><?php esc_html_e('Bar Chart', 'retail-trade-scanner'); ?></option>
                            </select>
                        </div>
                        
                        <div class="preference-item">
                            <label class="preference-label" for="auto-refresh">
                                <?php esc_html_e('Auto Refresh Interval', 'retail-trade-scanner'); ?>
                            </label>
                            <select id="auto-refresh" class="form-select">
                                <option value="5">5 seconds</option>
                                <option value="15" selected>15 seconds</option>
                                <option value="30">30 seconds</option>
                                <option value="60">1 minute</option>
                                <option value="0">Disabled</option>
                            </select>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <!-- API Keys Tab -->
        <div class="settings-panel" id="api-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('API Integration', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Manage your API keys and third-party integrations', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="api-sections">
                <div class="api-section">
                    <h3><?php esc_html_e('Market Data Providers', 'retail-trade-scanner'); ?></h3>
                    <div class="api-providers">
                        <div class="api-provider">
                            <div class="provider-info">
                                <div class="provider-logo">
                                    <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iIzMzNzNkYyIvPjx0ZXh0IHg9IjIwIiB5PSIyNiIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSI+QVY8L3RleHQ+PC9zdmc+" alt="Alpha Vantage">
                                </div>
                                <div class="provider-details">
                                    <h4><?php esc_html_e('Alpha Vantage', 'retail-trade-scanner'); ?></h4>
                                    <p><?php esc_html_e('Real-time and historical stock data', 'retail-trade-scanner'); ?></p>
                                    <div class="provider-status connected">
                                        <?php echo rts_get_icon('check-circle', ['width' => '16', 'height' => '16']); ?>
                                        <span><?php esc_html_e('Connected', 'retail-trade-scanner'); ?></span>
                                    </div>
                                </div>
                            </div>
                            <div class="provider-actions">
                                <button class="btn btn-outline btn-sm manage-api">
                                    <?php esc_html_e('Manage', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                        </div>
                        
                        <div class="api-provider">
                            <div class="provider-info">
                                <div class="provider-logo">
                                    <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iIzAwN2NmZiIvPjx0ZXh0IHg9IjIwIiB5PSIyNiIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTIiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSI+SUVYPC90ZXh0Pjwvc3ZnPg==" alt="IEX Cloud">
                                </div>
                                <div class="provider-details">
                                    <h4><?php esc_html_e('IEX Cloud', 'retail-trade-scanner'); ?></h4>
                                    <p><?php esc_html_e('Market data and financial information', 'retail-trade-scanner'); ?></p>
                                    <div class="provider-status disconnected">
                                        <?php echo rts_get_icon('x-circle', ['width' => '16', 'height' => '16']); ?>
                                        <span><?php esc_html_e('Not Connected', 'retail-trade-scanner'); ?></span>
                                    </div>
                                </div>
                            </div>
                            <div class="provider-actions">
                                <button class="btn btn-primary btn-sm connect-api">
                                    <?php esc_html_e('Connect', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="api-section">
                    <h3><?php esc_html_e('Broker Integrations', 'retail-trade-scanner'); ?></h3>
                    <div class="integration-info">
                        <div class="info-card">
                            <?php echo rts_get_icon('info', ['width' => '24', 'height' => '24']); ?>
                            <div class="info-content">
                                <h4><?php esc_html_e('Coming Soon', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Direct broker integration for paper trading and order execution will be available in the next update.', 'retail-trade-scanner'); ?></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Billing Tab -->
        <div class="settings-panel" id="billing-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('Billing & Subscription', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Manage your subscription, payment methods, and billing history', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="billing-sections">
                <div class="billing-section">
                    <h3><?php esc_html_e('Current Plan', 'retail-trade-scanner'); ?></h3>
                    <div class="current-plan-card">
                        <div class="plan-info">
                            <h4><?php esc_html_e('Pro Plan', 'retail-trade-scanner'); ?></h4>
                            <p class="plan-price">$29.99<span>/month</span></p>
                            <div class="plan-features">
                                <div class="feature-item">
                                    <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Unlimited stock scans', 'retail-trade-scanner'); ?></span>
                                </div>
                                <div class="feature-item">
                                    <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Real-time market data', 'retail-trade-scanner'); ?></span>
                                </div>
                                <div class="feature-item">
                                    <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16']); ?>
                                    <span><?php esc_html_e('Advanced charting tools', 'retail-trade-scanner'); ?></span>
                                </div>
                            </div>
                        </div>
                        <div class="plan-actions">
                            <button class="btn btn-outline change-plan">
                                <?php esc_html_e('Change Plan', 'retail-trade-scanner'); ?>
                            </button>
                            <button class="btn btn-ghost cancel-subscription">
                                <?php esc_html_e('Cancel Subscription', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="billing-section">
                    <h3><?php esc_html_e('Payment Method', 'retail-trade-scanner'); ?></h3>
                    <div class="payment-methods">
                        <div class="payment-method active">
                            <div class="method-info">
                                <?php echo rts_get_icon('credit-card', ['width' => '24', 'height' => '24']); ?>
                                <div class="card-details">
                                    <span class="card-number">•••• •••• •••• 4242</span>
                                    <span class="card-expiry">Expires 12/25</span>
                                </div>
                            </div>
                            <div class="method-actions">
                                <button class="btn btn-ghost btn-sm">
                                    <?php esc_html_e('Edit', 'retail-trade-scanner'); ?>
                                </button>
                                <button class="btn btn-ghost btn-sm text-danger">
                                    <?php esc_html_e('Remove', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                        </div>
                        
                        <button class="btn btn-outline add-payment">
                            <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Add Payment Method', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </div>
                
                <div class="billing-section">
                    <h3><?php esc_html_e('Billing History', 'retail-trade-scanner'); ?></h3>
                    <div class="billing-history">
                        <div class="history-item">
                            <div class="invoice-info">
                                <span class="invoice-date">Jan 15, 2024</span>
                                <span class="invoice-amount">$29.99</span>
                                <span class="invoice-status paid">Paid</span>
                            </div>
                            <button class="btn btn-ghost btn-sm">
                                <?php echo rts_get_icon('download', ['width' => '14', 'height' => '14']); ?>
                                <?php esc_html_e('Download', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                        
                        <div class="history-item">
                            <div class="invoice-info">
                                <span class="invoice-date">Dec 15, 2023</span>
                                <span class="invoice-amount">$29.99</span>
                                <span class="invoice-status paid">Paid</span>
                            </div>
                            <button class="btn btn-ghost btn-sm">
                                <?php echo rts_get_icon('download', ['width' => '14', 'height' => '14']); ?>
                                <?php esc_html_e('Download', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Security Tab -->
        <div class="settings-panel" id="security-panel">
            <div class="panel-header">
                <h2><?php esc_html_e('Security Settings', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Manage your account security and access controls', 'retail-trade-scanner'); ?></p>
            </div>
            
            <form class="settings-form" id="security-form">
                <div class="form-section">
                    <h3><?php esc_html_e('Password & Authentication', 'retail-trade-scanner'); ?></h3>
                    <div class="security-items">
                        <div class="security-item">
                            <div class="security-info">
                                <h4><?php esc_html_e('Password', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Last changed 3 months ago', 'retail-trade-scanner'); ?></p>
                            </div>
                            <button class="btn btn-outline change-password">
                                <?php esc_html_e('Change Password', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                        
                        <div class="security-item">
                            <div class="security-info">
                                <h4><?php esc_html_e('Two-Factor Authentication', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Add an extra layer of security to your account', 'retail-trade-scanner'); ?></p>
                            </div>
                            <button class="btn btn-primary setup-2fa">
                                <?php esc_html_e('Setup 2FA', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Session Management', 'retail-trade-scanner'); ?></h3>
                    <div class="active-sessions">
                        <div class="session-item current">
                            <div class="session-info">
                                <div class="session-device">
                                    <?php echo rts_get_icon('monitor', ['width' => '20', 'height' => '20']); ?>
                                    <div class="device-details">
                                        <span class="device-name">Chrome on Windows</span>
                                        <span class="session-location">New York, NY</span>
                                    </div>
                                </div>
                                <div class="session-meta">
                                    <span class="session-status current">Current session</span>
                                    <span class="session-time">Active now</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="session-item">
                            <div class="session-info">
                                <div class="session-device">
                                    <?php echo rts_get_icon('smartphone', ['width' => '20', 'height' => '20']); ?>
                                    <div class="device-details">
                                        <span class="device-name">Mobile Safari</span>
                                        <span class="session-location">New York, NY</span>
                                    </div>
                                </div>
                                <div class="session-meta">
                                    <span class="session-time">2 hours ago</span>
                                </div>
                            </div>
                            <button class="btn btn-ghost btn-sm revoke-session">
                                <?php esc_html_e('Revoke', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3><?php esc_html_e('Account Actions', 'retail-trade-scanner'); ?></h3>
                    <div class="account-actions">
                        <div class="action-item">
                            <div class="action-info">
                                <h4><?php esc_html_e('Export Account Data', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Download a copy of your account data and activity', 'retail-trade-scanner'); ?></p>
                            </div>
                            <button class="btn btn-outline export-data">
                                <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Request Export', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                        
                        <div class="action-item danger">
                            <div class="action-info">
                                <h4><?php esc_html_e('Delete Account', 'retail-trade-scanner'); ?></h4>
                                <p><?php esc_html_e('Permanently delete your account and all associated data', 'retail-trade-scanner'); ?></p>
                            </div>
                            <button class="btn btn-danger delete-account">
                                <?php echo rts_get_icon('trash', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Delete Account', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Settings page functionality
    const navLinks = document.querySelectorAll('.nav-link');
    const settingsPanels = document.querySelectorAll('.settings-panel');
    const saveButton = document.getElementById('save-settings');
    
    // Tab navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show target panel
            settingsPanels.forEach(panel => {
                if (panel.id === targetTab + '-panel') {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });
        });
    });
    
    // Form handling
    const forms = document.querySelectorAll('.settings-form');
    forms.forEach(form => {
        form.addEventListener('change', function() {
            // Mark form as changed
            this.classList.add('changed');
            if (saveButton) {
                saveButton.classList.add('has-changes');
            }
        });
    });
    
    // Save settings
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            saveAllSettings();
        });
    }
    
    // Theme switching
    const themeOptions = document.querySelectorAll('input[name="theme"]');
    themeOptions.forEach(option => {
        option.addEventListener('change', function() {
            applyTheme(this.value);
        });
    });
    
    // Notification method toggles
    document.addEventListener('change', function(e) {
        if (e.target.closest('.notification-item input[type="checkbox"]')) {
            const mainCheckbox = e.target.closest('.notification-item').querySelector('input[type="checkbox"]');
            const methodCheckboxes = e.target.closest('.notification-item').querySelectorAll('.method-checkbox input');
            
            if (e.target === mainCheckbox) {
                // Main checkbox changed - toggle all methods
                methodCheckboxes.forEach(cb => {
                    cb.disabled = !mainCheckbox.checked;
                    if (!mainCheckbox.checked) {
                        cb.checked = false;
                    }
                });
            }
        }
    });
    
    // Avatar upload
    document.querySelector('.upload-avatar')?.addEventListener('click', function() {
        // Simulate file upload
        RTS.showInfo('Avatar upload functionality would be implemented here');
    });
    
    // API management
    document.addEventListener('click', function(e) {
        if (e.target.closest('.manage-api')) {
            manageAPIKey();
        }
        
        if (e.target.closest('.connect-api')) {
            connectAPI(e.target.closest('.api-provider'));
        }
        
        if (e.target.closest('.change-password')) {
            openPasswordChangeModal();
        }
        
        if (e.target.closest('.setup-2fa')) {
            setup2FA();
        }
        
        if (e.target.closest('.delete-account')) {
            confirmAccountDeletion();
        }
    });
    
    function saveAllSettings() {
        saveButton.classList.add('loading');
        
        // Collect all form data
        const formData = new FormData();
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    formData.append(input.name || input.id, input.checked);
                } else if (input.type === 'radio' && input.checked) {
                    formData.append(input.name, input.value);
                } else if (input.type !== 'radio') {
                    formData.append(input.name || input.id, input.value);
                }
            });
        });
        
        // Simulate API call
        setTimeout(() => {
            saveButton.classList.remove('loading', 'has-changes');
            forms.forEach(form => form.classList.remove('changed'));
            
            RTS.showSuccess('Settings saved successfully!');
        }, 2000);
    }
    
    function applyTheme(theme) {
        // Apply theme immediately for preview
        const body = document.body;
        body.classList.remove('theme-light', 'theme-dark', 'theme-auto');
        
        if (theme === 'auto') {
            // Use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
        } else {
            body.classList.add('theme-' + theme);
        }
    }
    
    function manageAPIKey() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Manage API Key</h3>
                    <button class="modal-close">${RTS.components.getIcon('x', 20)}</button>
                </div>
                <div class="modal-body">
                    <div class="form-field">
                        <label class="form-label">API Key</label>
                        <div class="key-input">
                            <input type="password" class="form-input" value="sk-xxxxxxxxxxxx" readonly>
                            <button class="btn btn-ghost btn-sm toggle-visibility">
                                ${RTS.components.getIcon('eye', 16)}
                            </button>
                        </div>
                    </div>
                    <div class="api-usage">
                        <h4>Usage This Month</h4>
                        <div class="usage-stats">
                            <div class="usage-item">
                                <span>Requests:</span>
                                <span>15,432 / 25,000</span>
                            </div>
                            <div class="usage-item">
                                <span>Last Request:</span>
                                <span>2 minutes ago</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-ghost">Cancel</button>
                    <button class="btn btn-danger">Revoke Key</button>
                    <button class="btn btn-primary">Regenerate</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal functionality
        modal.addEventListener('click', function(e) {
            if (e.target.closest('.modal-close') || e.target.classList.contains('modal-backdrop')) {
                document.body.removeChild(modal);
            }
        });
    }
    
    function connectAPI(providerElement) {
        const providerName = providerElement.querySelector('h4').textContent;
        
        RTS.showInfo(`Connecting to ${providerName}...`);
        
        // Simulate connection process
        setTimeout(() => {
            const statusElement = providerElement.querySelector('.provider-status');
            const actionButton = providerElement.querySelector('.connect-api');
            
            statusElement.className = 'provider-status connected';
            statusElement.innerHTML = `
                ${RTS.components.getIcon('check-circle', 16)}
                <span>Connected</span>
            `;
            
            actionButton.textContent = 'Manage';
            actionButton.className = 'btn btn-outline btn-sm manage-api';
            
            RTS.showSuccess(`Successfully connected to ${providerName}!`);
        }, 2000);
    }
    
    function openPasswordChangeModal() {
        RTS.showInfo('Password change modal would open here');
    }
    
    function setup2FA() {
        RTS.showInfo('2FA setup wizard would start here');
    }
    
    function confirmAccountDeletion() {
        if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            RTS.showError('Account deletion process would begin here');
        }
    }
});
</script>

<style>
/* Settings page specific styles */
.settings-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: var(--spacing-2xl);
    align-items: flex-start;
}

/* Settings Navigation */
.settings-nav {
    position: sticky;
    top: calc(var(--header-height, 72px) + var(--spacing-lg));
    padding: var(--spacing-xl);
}

.nav-header {
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.avatar-img {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-full);
}

.user-info h3 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
    font-size: var(--text-lg);
}

.user-info p {
    margin: 0;
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.nav-tabs {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.nav-item {
    margin: 0;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    width: 100%;
    background: transparent;
    border: none;
    border-radius: var(--radius-lg);
    color: var(--gray-600);
    font-size: var(--text-base);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    text-align: left;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--gray-800);
}

.nav-link.active {
    background: var(--primary-500);
    color: white;
}

/* Settings Content */
.settings-content {
    min-height: 600px;
}

.settings-panel {
    display: none;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--spacing-2xl);
}

.settings-panel.active {
    display: block;
}

.panel-header {
    margin-bottom: var(--spacing-2xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
}

.panel-header h2 {
    margin: 0 0 var(--spacing-sm);
    color: var(--gray-800);
}

.panel-header p {
    margin: 0;
    color: var(--gray-600);
    font-size: var(--text-lg);
}

.settings-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2xl);
}

.form-section {
    padding-bottom: var(--spacing-xl);
    border-bottom: 1px solid var(--gray-100);
}

.form-section:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.form-section h3 {
    margin: 0 0 var(--spacing-lg);
    color: var(--gray-800);
    font-size: var(--text-xl);
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.form-label {
    font-weight: 600;
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.form-input,
.form-select,
.form-textarea {
    padding: var(--spacing-md);
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: var(--text-base);
    transition: border-color var(--transition-fast);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

/* Avatar Section */
.avatar-section {
    display: flex;
    align-items: center;
    gap: var(--spacing-xl);
}

.current-avatar .avatar-preview {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-full);
    border: 4px solid var(--gray-200);
}

.avatar-controls {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.avatar-help {
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin: 0;
}

/* Notification Settings */
.notification-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.notification-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: background var(--transition-fast);
}

.notification-item:hover {
    background: var(--gray-50);
}

.notification-item > input[type="checkbox"] {
    margin-top: 4px;
}

.notification-info {
    flex: 1;
}

.notification-info h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
    font-size: var(--text-base);
}

.notification-info p {
    margin: 0;
    color: var(--gray-600);
    font-size: var(--text-sm);
    line-height: 1.4;
}

.notification-methods {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-sm);
}

.method-checkbox {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
    color: var(--gray-700);
    cursor: pointer;
}

.notification-timing {
    margin-top: var(--spacing-sm);
}

/* Preferences */
.preference-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-xl);
}

.preference-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.preference-label {
    font-weight: 600;
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.theme-options {
    display: flex;
    gap: var(--spacing-md);
}

.theme-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
}

.theme-preview {
    width: 60px;
    height: 40px;
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-md);
    position: relative;
    overflow: hidden;
    transition: border-color var(--transition-fast);
}

.theme-option input[type="radio"]:checked + .theme-preview {
    border-color: var(--primary-500);
}

.theme-preview.light {
    background: #ffffff;
}

.theme-preview.light .preview-header {
    height: 12px;
    background: #f3f4f6;
}

.theme-preview.light .preview-content {
    height: 28px;
    background: #ffffff;
}

.theme-preview.dark {
    background: #111827;
}

.theme-preview.dark .preview-header {
    height: 12px;
    background: #374151;
}

.theme-preview.dark .preview-content {
    height: 28px;
    background: #111827;
}

.theme-preview.auto {
    background: linear-gradient(45deg, #ffffff 50%, #111827 50%);
}

.theme-preview.auto .preview-header {
    height: 12px;
    background: linear-gradient(45deg, #f3f4f6 50%, #374151 50%);
}

.theme-preview.auto .preview-content {
    height: 28px;
    background: linear-gradient(45deg, #ffffff 50%, #111827 50%);
}

/* Toggle Switch */
.toggle-switch {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
}

.toggle-switch input[type="checkbox"] {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-label {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--gray-300);
    border-radius: 24px;
    transition: background var(--transition-fast);
}

.toggle-label::before {
    position: absolute;
    content: '';
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background: white;
    border-radius: 50%;
    transition: transform var(--transition-fast);
}

.toggle-switch input[type="checkbox"]:checked + .toggle-label {
    background: var(--primary-500);
}

.toggle-switch input[type="checkbox"]:checked + .toggle-label::before {
    transform: translateX(20px);
}

/* API Providers */
.api-providers {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.api-provider {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.provider-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.provider-logo img {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
}

.provider-details h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
}

.provider-details p {
    margin: 0 0 var(--spacing-sm);
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.provider-status {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
    font-weight: 500;
}

.provider-status.connected {
    color: var(--success);
}

.provider-status.disconnected {
    color: var(--gray-500);
}

/* Billing */
.current-plan-card {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: var(--spacing-xl);
    background: var(--primary-50);
    border: 1px solid var(--primary-200);
    border-radius: var(--radius-lg);
}

.plan-info h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--primary-800);
    font-size: var(--text-xl);
}

.plan-price {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--primary-600);
    margin-bottom: var(--spacing-md);
}

.plan-price span {
    font-size: var(--text-base);
    font-weight: 400;
    color: var(--gray-600);
}

.plan-features {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.feature-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.feature-item svg {
    color: var(--success);
}

.plan-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

/* Payment Methods */
.payment-methods {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.payment-method {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.payment-method.active {
    border-color: var(--primary-200);
    background: var(--primary-50);
}

.method-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.card-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.card-number {
    font-weight: 600;
    color: var(--gray-800);
}

.card-expiry {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.method-actions {
    display: flex;
    gap: var(--spacing-sm);
}

/* Billing History */
.billing-history {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.invoice-info {
    display: flex;
    gap: var(--spacing-lg);
    align-items: center;
}

.invoice-date {
    font-weight: 500;
    color: var(--gray-700);
}

.invoice-amount {
    font-weight: 600;
    color: var(--gray-800);
}

.invoice-status {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
}

.invoice-status.paid {
    background: var(--success-light);
    color: var(--success-dark);
}

/* Security */
.security-items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.security-info h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
}

.security-info p {
    margin: 0;
    color: var(--gray-600);
    font-size: var(--text-sm);
}

/* Active Sessions */
.active-sessions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.session-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.session-item.current {
    border-color: var(--success);
    background: var(--success-light);
}

.session-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    width: 100%;
}

.session-device {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.device-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.device-name {
    font-weight: 500;
    color: var(--gray-800);
}

.session-location {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.session-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: var(--spacing-xs);
    margin-left: auto;
    margin-right: var(--spacing-lg);
}

.session-status {
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
}

.session-status.current {
    color: var(--success);
}

.session-time {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

/* Account Actions */
.account-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.action-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
}

.action-item.danger {
    border-color: var(--danger-light);
    background: rgba(220, 38, 38, 0.02);
}

.action-info h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
}

.action-info p {
    margin: 0;
    color: var(--gray-600);
    font-size: var(--text-sm);
}

/* Loading states */
.settings-form.changed .form-field {
    position: relative;
}

.settings-form.changed .form-field::after {
    content: '';
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    background: var(--warning);
    border-radius: 50%;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .settings-layout {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }
    
    .settings-nav {
        position: static;
    }
    
    .nav-tabs {
        flex-direction: row;
        overflow-x: auto;
        gap: var(--spacing-sm);
    }
    
    .nav-link {
        white-space: nowrap;
        min-width: max-content;
    }
    
    .form-grid {
        grid-template-columns: 1fr;
    }
    
    .current-plan-card {
        flex-direction: column;
        align-items: stretch;
        gap: var(--spacing-lg);
    }
    
    .avatar-section {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media (max-width: 640px) {
    .notification-item {
        flex-direction: column;
        align-items: stretch;
        gap: var(--spacing-md);
    }
    
    .notification-methods {
        justify-content: flex-start;
    }
    
    .theme-options {
        justify-content: center;
    }
    
    .preference-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<?php get_footer(); ?>