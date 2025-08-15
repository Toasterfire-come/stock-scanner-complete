<?php
/**
 * Template Name: User Settings
 * 
 * The template for displaying user preferences and configuration settings
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="user-settings-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-cog"></i>
                User Settings
            </h1>
            <p class="page-subtitle">Customize your trading experience and platform preferences</p>
        </div>
    </div>

    <div class="settings-content">
        <div class="container">
            <div class="settings-layout">
                <!-- Settings Navigation -->
                <div class="settings-sidebar">
                    <nav class="settings-nav">
                        <button class="nav-item active" data-section="trading">
                            <i class="fas fa-chart-line"></i>
                            Trading Preferences
                        </button>
                        <button class="nav-item" data-section="display">
                            <i class="fas fa-desktop"></i>
                            Display & Layout
                        </button>
                        <button class="nav-item" data-section="notifications">
                            <i class="fas fa-bell"></i>
                            Notifications
                        </button>
                        <button class="nav-item" data-section="data">
                            <i class="fas fa-database"></i>
                            Data & API
                        </button>
                        <button class="nav-item" data-section="privacy">
                            <i class="fas fa-shield-alt"></i>
                            Privacy & Security
                        </button>
                        <button class="nav-item" data-section="advanced">
                            <i class="fas fa-tools"></i>
                            Advanced Settings
                        </button>
                    </nav>

                    <div class="settings-actions">
                        <button class="btn btn-primary" id="saveAllSettings">
                            <i class="fas fa-save"></i>
                            Save All Changes
                        </button>
                        <button class="btn btn-outline" id="resetToDefaults">
                            <i class="fas fa-undo"></i>
                            Reset to Defaults
                        </button>
                    </div>
                </div>

                <!-- Settings Content -->
                <div class="settings-main">
                    <!-- Trading Preferences -->
                    <div class="settings-section active" id="trading">
                        <div class="section-header">
                            <h2>Trading Preferences</h2>
                            <p>Configure your default trading and analysis settings</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Investment Profile</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="investmentExperience">Investment Experience</label>
                                        <select id="investmentExperience" class="form-select">
                                            <option value="beginner">Beginner (< 1 year)</option>
                                            <option value="intermediate" selected>Intermediate (1-5 years)</option>
                                            <option value="advanced">Advanced (5+ years)</option>
                                            <option value="professional">Professional Trader</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="riskTolerance">Risk Tolerance</label>
                                        <select id="riskTolerance" class="form-select">
                                            <option value="conservative">Conservative</option>
                                            <option value="moderate" selected>Moderate</option>
                                            <option value="aggressive">Aggressive</option>
                                            <option value="very-aggressive">Very Aggressive</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="investmentGoal">Primary Investment Goal</label>
                                        <select id="investmentGoal" class="form-select">
                                            <option value="growth">Long-term Growth</option>
                                            <option value="income">Income Generation</option>
                                            <option value="preservation">Capital Preservation</option>
                                            <option value="speculation">Speculation/Trading</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="timeHorizon">Investment Time Horizon</label>
                                        <select id="timeHorizon" class="form-select">
                                            <option value="short">Short-term (< 1 year)</option>
                                            <option value="medium">Medium-term (1-5 years)</option>
                                            <option value="long" selected>Long-term (5+ years)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Default Chart Settings</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="defaultChartType">Default Chart Type</label>
                                        <select id="defaultChartType" class="form-select">
                                            <option value="line" selected>Line Chart</option>
                                            <option value="candlestick">Candlestick</option>
                                            <option value="area">Area Chart</option>
                                            <option value="volume">Volume Chart</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="defaultTimeframe">Default Timeframe</label>
                                        <select id="defaultTimeframe" class="form-select">
                                            <option value="1D">1 Day</option>
                                            <option value="1W" selected>1 Week</option>
                                            <option value="1M">1 Month</option>
                                            <option value="3M">3 Months</option>
                                            <option value="1Y">1 Year</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="technicalIndicators">Default Technical Indicators</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="indicators" value="sma" checked>
                                                <span class="checkmark"></span>
                                                Simple Moving Average (SMA)
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="indicators" value="ema">
                                                <span class="checkmark"></span>
                                                Exponential Moving Average (EMA)
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="indicators" value="bollinger">
                                                <span class="checkmark"></span>
                                                Bollinger Bands
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="indicators" value="rsi">
                                                <span class="checkmark"></span>
                                                RSI
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Watchlist Preferences</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="defaultWatchlistView">Default View</label>
                                        <select id="defaultWatchlistView" class="form-select">
                                            <option value="list" selected>List View</option>
                                            <option value="grid">Grid View</option>
                                            <option value="chart">Chart View</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="watchlistColumns">Visible Columns</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="columns" value="price" checked>
                                                <span class="checkmark"></span>
                                                Current Price
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="columns" value="change" checked>
                                                <span class="checkmark"></span>
                                                Price Change
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="columns" value="volume" checked>
                                                <span class="checkmark"></span>
                                                Volume
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="columns" value="market_cap">
                                                <span class="checkmark"></span>
                                                Market Cap
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Display & Layout -->
                    <div class="settings-section" id="display">
                        <div class="section-header">
                            <h2>Display & Layout</h2>
                            <p>Customize the appearance and layout of your dashboard</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Theme & Appearance</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="colorTheme">Color Theme</label>
                                        <div class="theme-selector">
                                            <label class="theme-option">
                                                <input type="radio" name="theme" value="light" checked>
                                                <div class="theme-preview light">
                                                    <div class="theme-colors">
                                                        <span class="color-bg"></span>
                                                        <span class="color-primary"></span>
                                                        <span class="color-text"></span>
                                                    </div>
                                                    <span class="theme-name">Light</span>
                                                </div>
                                            </label>
                                            <label class="theme-option">
                                                <input type="radio" name="theme" value="dark">
                                                <div class="theme-preview dark">
                                                    <div class="theme-colors">
                                                        <span class="color-bg"></span>
                                                        <span class="color-primary"></span>
                                                        <span class="color-text"></span>
                                                    </div>
                                                    <span class="theme-name">Dark</span>
                                                </div>
                                            </label>
                                            <label class="theme-option">
                                                <input type="radio" name="theme" value="auto">
                                                <div class="theme-preview auto">
                                                    <div class="theme-colors">
                                                        <span class="color-bg"></span>
                                                        <span class="color-primary"></span>
                                                        <span class="color-text"></span>
                                                    </div>
                                                    <span class="theme-name">Auto</span>
                                                </div>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="fontSize">Font Size</label>
                                        <select id="fontSize" class="form-select">
                                            <option value="small">Small</option>
                                            <option value="medium" selected>Medium</option>
                                            <option value="large">Large</option>
                                            <option value="extra-large">Extra Large</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="density">Interface Density</label>
                                        <select id="density" class="form-select">
                                            <option value="compact">Compact</option>
                                            <option value="comfortable" selected>Comfortable</option>
                                            <option value="spacious">Spacious</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Dashboard Layout</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Dashboard Widgets</label>
                                        <div class="widget-manager">
                                            <div class="widget-list">
                                                <div class="widget-item" draggable="true">
                                                    <div class="widget-info">
                                                        <i class="fas fa-chart-line"></i>
                                                        <span>Market Overview</span>
                                                    </div>
                                                    <div class="widget-controls">
                                                        <input type="checkbox" checked>
                                                        <i class="fas fa-grip-vertical"></i>
                                                    </div>
                                                </div>
                                                <div class="widget-item" draggable="true">
                                                    <div class="widget-info">
                                                        <i class="fas fa-star"></i>
                                                        <span>Watchlist</span>
                                                    </div>
                                                    <div class="widget-controls">
                                                        <input type="checkbox" checked>
                                                        <i class="fas fa-grip-vertical"></i>
                                                    </div>
                                                </div>
                                                <div class="widget-item" draggable="true">
                                                    <div class="widget-info">
                                                        <i class="fas fa-newspaper"></i>
                                                        <span>Recent News</span>
                                                    </div>
                                                    <div class="widget-controls">
                                                        <input type="checkbox" checked>
                                                        <i class="fas fa-grip-vertical"></i>
                                                    </div>
                                                </div>
                                                <div class="widget-item" draggable="true">
                                                    <div class="widget-info">
                                                        <i class="fas fa-briefcase"></i>
                                                        <span>Portfolio Summary</span>
                                                    </div>
                                                    <div class="widget-controls">
                                                        <input type="checkbox">
                                                        <i class="fas fa-grip-vertical"></i>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Data Display</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="numberFormat">Number Format</label>
                                        <select id="numberFormat" class="form-select">
                                            <option value="us" selected>US Format (1,234.56)</option>
                                            <option value="eu">European Format (1.234,56)</option>
                                            <option value="in">Indian Format (1,23,456.78)</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="currencyDisplay">Currency Display</label>
                                        <select id="currencyDisplay" class="form-select">
                                            <option value="symbol" selected>Symbol ($123.45)</option>
                                            <option value="code">Code (USD 123.45)</option>
                                            <option value="name">Name (123.45 US Dollars)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="percentageDecimals">Percentage Decimals</label>
                                        <select id="percentageDecimals" class="form-select">
                                            <option value="0">0 decimals (12%)</option>
                                            <option value="1">1 decimal (12.3%)</option>
                                            <option value="2" selected>2 decimals (12.34%)</option>
                                            <option value="3">3 decimals (12.345%)</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Color Coding</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="colorCoding" value="gains" checked>
                                                <span class="checkmark"></span>
                                                Color code gains/losses
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="colorCoding" value="volume" checked>
                                                <span class="checkmark"></span>
                                                Color code volume changes
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Notifications -->
                    <div class="settings-section" id="notifications">
                        <div class="section-header">
                            <h2>Notification Settings</h2>
                            <p>Configure how and when you receive alerts and notifications</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Price Alerts</h3>
                                <div class="notification-options">
                                    <div class="notification-type">
                                        <div class="notification-header">
                                            <h4>Price Movement Alerts</h4>
                                            <label class="toggle-switch">
                                                <input type="checkbox" checked>
                                                <span class="toggle-slider"></span>
                                            </label>
                                        </div>
                                        <div class="notification-channels">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="priceAlerts" value="email" checked>
                                                <span class="checkmark"></span>
                                                Email notifications
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="priceAlerts" value="push" checked>
                                                <span class="checkmark"></span>
                                                Push notifications
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="priceAlerts" value="sms">
                                                <span class="checkmark"></span>
                                                SMS notifications (Premium)
                                            </label>
                                        </div>
                                    </div>

                                    <div class="notification-type">
                                        <div class="notification-header">
                                            <h4>Volume Alerts</h4>
                                            <label class="toggle-switch">
                                                <input type="checkbox">
                                                <span class="toggle-slider"></span>
                                            </label>
                                        </div>
                                        <div class="notification-channels">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="volumeAlerts" value="email">
                                                <span class="checkmark"></span>
                                                Email notifications
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="volumeAlerts" value="push">
                                                <span class="checkmark"></span>
                                                Push notifications
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Market News</h3>
                                <div class="notification-options">
                                    <div class="notification-type">
                                        <div class="notification-header">
                                            <h4>Breaking News</h4>
                                            <label class="toggle-switch">
                                                <input type="checkbox" checked>
                                                <span class="toggle-slider"></span>
                                            </label>
                                        </div>
                                        <div class="notification-settings">
                                            <div class="form-group">
                                                <label for="newsFrequency">Frequency</label>
                                                <select id="newsFrequency" class="form-select">
                                                    <option value="immediate" selected>Immediate</option>
                                                    <option value="hourly">Hourly digest</option>
                                                    <option value="daily">Daily digest</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>System Notifications</h3>
                                <div class="notification-options">
                                    <div class="notification-type">
                                        <div class="notification-header">
                                            <h4>Account Updates</h4>
                                            <label class="toggle-switch">
                                                <input type="checkbox" checked>
                                                <span class="toggle-slider"></span>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="notification-type">
                                        <div class="notification-header">
                                            <h4>Product Updates</h4>
                                            <label class="toggle-switch">
                                                <input type="checkbox" checked>
                                                <span class="toggle-slider"></span>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Data & API -->
                    <div class="settings-section" id="data">
                        <div class="section-header">
                            <h2>Data & API Settings</h2>
                            <p>Configure data refresh rates and API preferences</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Data Refresh</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="refreshInterval">Auto-refresh Interval</label>
                                        <select id="refreshInterval" class="form-select">
                                            <option value="5">5 seconds</option>
                                            <option value="15">15 seconds</option>
                                            <option value="30" selected>30 seconds</option>
                                            <option value="60">1 minute</option>
                                            <option value="300">5 minutes</option>
                                            <option value="0">Manual only</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="dataQuality">Data Quality</label>
                                        <select id="dataQuality" class="form-select">
                                            <option value="realtime">Real-time (Premium)</option>
                                            <option value="delayed" selected>15-minute delayed</option>
                                            <option value="eod">End of day</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Auto-refresh Options</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="autoRefresh" value="charts" checked>
                                                <span class="checkmark"></span>
                                                Auto-refresh charts
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="autoRefresh" value="watchlist" checked>
                                                <span class="checkmark"></span>
                                                Auto-refresh watchlists
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="autoRefresh" value="news">
                                                <span class="checkmark"></span>
                                                Auto-refresh news
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>API Configuration</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="apiTimeout">Request Timeout</label>
                                        <select id="apiTimeout" class="form-select">
                                            <option value="10">10 seconds</option>
                                            <option value="30" selected>30 seconds</option>
                                            <option value="60">60 seconds</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="maxRetries">Max Retries</label>
                                        <select id="maxRetries" class="form-select">
                                            <option value="0">No retries</option>
                                            <option value="1">1 retry</option>
                                            <option value="3" selected>3 retries</option>
                                            <option value="5">5 retries</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Data Usage</h3>
                                <div class="usage-stats">
                                    <div class="usage-item">
                                        <div class="usage-info">
                                            <span class="usage-label">API Calls Today</span>
                                            <span class="usage-value">1,247 / 10,000</span>
                                        </div>
                                        <div class="usage-bar">
                                            <div class="usage-fill" style="width: 12.47%"></div>
                                        </div>
                                    </div>
                                    <div class="usage-item">
                                        <div class="usage-info">
                                            <span class="usage-label">Data Downloaded</span>
                                            <span class="usage-value">45.2 MB / 1 GB</span>
                                        </div>
                                        <div class="usage-bar">
                                            <div class="usage-fill" style="width: 4.52%"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Privacy & Security -->
                    <div class="settings-section" id="privacy">
                        <div class="section-header">
                            <h2>Privacy & Security</h2>
                            <p>Manage your privacy settings and security preferences</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Data Privacy</h3>
                                <div class="privacy-options">
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="privacy" value="analytics" checked>
                                        <span class="checkmark"></span>
                                        Allow usage analytics to improve the platform
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="privacy" value="personalization" checked>
                                        <span class="checkmark"></span>
                                        Enable personalized recommendations
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="privacy" value="marketing">
                                        <span class="checkmark"></span>
                                        Receive marketing communications
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" name="privacy" value="thirdparty">
                                        <span class="checkmark"></span>
                                        Share data with trusted partners
                                    </label>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Session Security</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="sessionTimeout">Auto-logout After</label>
                                        <select id="sessionTimeout" class="form-select">
                                            <option value="30">30 minutes</option>
                                            <option value="60" selected>1 hour</option>
                                            <option value="240">4 hours</option>
                                            <option value="480">8 hours</option>
                                            <option value="0">Never</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Security Options</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="security" value="2fa" checked>
                                                <span class="checkmark"></span>
                                                Two-factor authentication
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="security" value="loginAlerts" checked>
                                                <span class="checkmark"></span>
                                                Login alerts
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Advanced Settings -->
                    <div class="settings-section" id="advanced">
                        <div class="section-header">
                            <h2>Advanced Settings</h2>
                            <p>Advanced configuration options for power users</p>
                        </div>

                        <div class="settings-groups">
                            <div class="settings-group">
                                <h3>Performance</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="cacheSize">Cache Size</label>
                                        <select id="cacheSize" class="form-select">
                                            <option value="50">50 MB</option>
                                            <option value="100" selected>100 MB</option>
                                            <option value="250">250 MB</option>
                                            <option value="500">500 MB</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Performance Options</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="performance" value="preload" checked>
                                                <span class="checkmark"></span>
                                                Preload data
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="performance" value="compression" checked>
                                                <span class="checkmark"></span>
                                                Enable compression
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Developer Options</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Debug Settings</label>
                                        <div class="checkbox-group">
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="debug" value="console">
                                                <span class="checkmark"></span>
                                                Enable console logging
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="debug" value="performance">
                                                <span class="checkmark"></span>
                                                Show performance metrics
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="settings-group">
                                <h3>Data Management</h3>
                                <div class="data-actions">
                                    <button class="btn btn-outline" id="clearCache">
                                        <i class="fas fa-trash"></i>
                                        Clear Cache
                                    </button>
                                    <button class="btn btn-outline" id="exportSettings">
                                        <i class="fas fa-download"></i>
                                        Export Settings
                                    </button>
                                    <button class="btn btn-outline" id="importSettings">
                                        <i class="fas fa-upload"></i>
                                        Import Settings
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.user-settings-container {
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

.settings-content {
    padding: 3rem 0;
}

.settings-layout {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 3rem;
    align-items: start;
}

.settings-sidebar {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: sticky;
    top: 2rem;
}

.settings-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border: none;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.95rem;
    font-weight: 500;
    color: #666;
    text-align: left;
    width: 100%;
}

.nav-item:hover {
    background: #f8f9fa;
    color: #3685fb;
}

.nav-item.active {
    background: #f0f9ff;
    color: #3685fb;
    border-left: 3px solid #3685fb;
}

.nav-item i {
    width: 20px;
    text-align: center;
}

.settings-actions {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.settings-main {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}

.settings-section {
    display: none;
    padding: 2rem;
}

.settings-section.active {
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
    font-size: 1rem;
}

.settings-groups {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.settings-group {
    padding: 1.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    background: #fafbfc;
}

.settings-group h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 1.5rem 0;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.form-row:last-child {
    margin-bottom: 0;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-size: 0.95rem;
    font-weight: 500;
    color: #333;
}

.form-select,
.form-input {
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
    background: white;
}

.form-select:focus,
.form-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #333;
}

.checkbox-label input[type="checkbox"] {
    display: none;
}

.checkmark {
    width: 20px;
    height: 20px;
    border: 2px solid #e1e5e9;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
    background: #3685fb;
    border-color: #3685fb;
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

.theme-selector {
    display: flex;
    gap: 1rem;
}

.theme-option {
    cursor: pointer;
}

.theme-option input[type="radio"] {
    display: none;
}

.theme-preview {
    padding: 1rem;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    text-align: center;
    transition: all 0.2s;
    min-width: 100px;
}

.theme-option input[type="radio"]:checked + .theme-preview {
    border-color: #3685fb;
    background: #f0f9ff;
}

.theme-colors {
    display: flex;
    justify-content: center;
    gap: 4px;
    margin-bottom: 0.5rem;
}

.color-bg,
.color-primary,
.color-text {
    width: 16px;
    height: 16px;
    border-radius: 50%;
}

.light .color-bg { background: #ffffff; border: 1px solid #ddd; }
.light .color-primary { background: #3685fb; }
.light .color-text { background: #333333; }

.dark .color-bg { background: #1a1a1a; }
.dark .color-primary { background: #60a5fa; }
.dark .color-text { background: #ffffff; }

.auto .color-bg { background: linear-gradient(45deg, #ffffff 50%, #1a1a1a 50%); }
.auto .color-primary { background: #3685fb; }
.auto .color-text { background: linear-gradient(45deg, #333333 50%, #ffffff 50%); }

.theme-name {
    font-size: 0.85rem;
    font-weight: 500;
    color: #666;
}

.widget-manager {
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: white;
}

.widget-list {
    display: flex;
    flex-direction: column;
}

.widget-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    cursor: move;
    transition: background 0.2s;
}

.widget-item:last-child {
    border-bottom: none;
}

.widget-item:hover {
    background: #f8f9fa;
}

.widget-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.widget-info i {
    color: #666;
    width: 20px;
    text-align: center;
}

.widget-controls {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.widget-controls i {
    color: #999;
    cursor: grab;
}

.notification-options {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.notification-type {
    padding: 1rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: white;
}

.notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.notification-header h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0;
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.3s;
    border-radius: 24px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: #3685fb;
}

input:checked + .toggle-slider:before {
    transform: translateX(26px);
}

.notification-channels {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-left: 1rem;
}

.notification-settings {
    margin-top: 1rem;
}

.usage-stats {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.usage-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.usage-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.usage-label {
    font-size: 0.9rem;
    color: #666;
}

.usage-value {
    font-size: 0.9rem;
    font-weight: 600;
    color: #333;
}

.usage-bar {
    height: 6px;
    background: #e1e5e9;
    border-radius: 3px;
    overflow: hidden;
}

.usage-fill {
    height: 100%;
    background: #3685fb;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.privacy-options {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.data-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
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

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-outline {
    background: transparent;
    color: #666;
    border: 1px solid #e1e5e9;
}

.btn-outline:hover {
    background: #f8f9fa;
    border-color: #3685fb;
    color: #3685fb;
}

@media (max-width: 1024px) {
    .settings-layout {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .settings-sidebar {
        position: static;
    }
    
    .settings-nav {
        flex-direction: row;
        overflow-x: auto;
        gap: 0.25rem;
    }
    
    .nav-item {
        flex-shrink: 0;
        min-width: 150px;
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
        gap: 1rem;
    }
    
    .theme-selector {
        flex-direction: column;
    }
    
    .data-actions {
        flex-direction: column;
    }
    
    .settings-actions {
        flex-direction: row;
        gap: 0.5rem;
    }
    
    .settings-actions .btn {
        flex: 1;
        justify-content: center;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeUserSettings();
});

function initializeUserSettings() {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.settings-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetSection = item.dataset.section;
            
            // Update navigation
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update sections
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetSection).classList.add('active');
        });
    });
    
    // Save settings
    document.getElementById('saveAllSettings').addEventListener('click', saveAllSettings);
    
    // Reset to defaults
    document.getElementById('resetToDefaults').addEventListener('click', resetToDefaults);
    
    // Data management actions
    document.getElementById('clearCache').addEventListener('click', clearCache);
    document.getElementById('exportSettings').addEventListener('click', exportSettings);
    document.getElementById('importSettings').addEventListener('click', importSettings);
    
    // Theme selector
    const themeInputs = document.querySelectorAll('input[name="theme"]');
    themeInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            if (e.target.checked) {
                applyTheme(e.target.value);
            }
        });
    });
    
    // Widget drag and drop
    initializeWidgetDragDrop();
    
    // Load saved settings
    loadUserSettings();
}

function saveAllSettings() {
    showNotification('Saving settings...', 'info');
    
    // Collect all form data
    const settings = {
        trading: collectTradingSettings(),
        display: collectDisplaySettings(),
        notifications: collectNotificationSettings(),
        data: collectDataSettings(),
        privacy: collectPrivacySettings(),
        advanced: collectAdvancedSettings()
    };
    
    // Simulate API call to save settings
    setTimeout(() => {
        // Save to localStorage for demo
        localStorage.setItem('userSettings', JSON.stringify(settings));
        showNotification('Settings saved successfully!', 'success');
    }, 1500);
}

function collectTradingSettings() {
    return {
        investmentExperience: document.getElementById('investmentExperience').value,
        riskTolerance: document.getElementById('riskTolerance').value,
        investmentGoal: document.getElementById('investmentGoal').value,
        timeHorizon: document.getElementById('timeHorizon').value,
        defaultChartType: document.getElementById('defaultChartType').value,
        defaultTimeframe: document.getElementById('defaultTimeframe').value,
        technicalIndicators: Array.from(document.querySelectorAll('input[name="indicators"]:checked')).map(cb => cb.value),
        defaultWatchlistView: document.getElementById('defaultWatchlistView').value,
        watchlistColumns: Array.from(document.querySelectorAll('input[name="columns"]:checked')).map(cb => cb.value)
    };
}

function collectDisplaySettings() {
    return {
        theme: document.querySelector('input[name="theme"]:checked').value,
        fontSize: document.getElementById('fontSize').value,
        density: document.getElementById('density').value,
        numberFormat: document.getElementById('numberFormat').value,
        currencyDisplay: document.getElementById('currencyDisplay').value,
        percentageDecimals: document.getElementById('percentageDecimals').value,
        colorCoding: Array.from(document.querySelectorAll('input[name="colorCoding"]:checked')).map(cb => cb.value),
        widgets: collectWidgetSettings()
    };
}

function collectNotificationSettings() {
    return {
        priceAlerts: {
            enabled: document.querySelector('.notification-type:nth-child(1) input[type="checkbox"]').checked,
            channels: Array.from(document.querySelectorAll('input[name="priceAlerts"]:checked')).map(cb => cb.value)
        },
        volumeAlerts: {
            enabled: document.querySelector('.notification-type:nth-child(2) input[type="checkbox"]').checked,
            channels: Array.from(document.querySelectorAll('input[name="volumeAlerts"]:checked')).map(cb => cb.value)
        },
        breakingNews: {
            enabled: document.querySelector('#notifications .notification-type:nth-child(1) input[type="checkbox"]').checked,
            frequency: document.getElementById('newsFrequency').value
        }
    };
}

function collectDataSettings() {
    return {
        refreshInterval: document.getElementById('refreshInterval').value,
        dataQuality: document.getElementById('dataQuality').value,
        autoRefresh: Array.from(document.querySelectorAll('input[name="autoRefresh"]:checked')).map(cb => cb.value),
        apiTimeout: document.getElementById('apiTimeout').value,
        maxRetries: document.getElementById('maxRetries').value
    };
}

function collectPrivacySettings() {
    return {
        privacy: Array.from(document.querySelectorAll('input[name="privacy"]:checked')).map(cb => cb.value),
        sessionTimeout: document.getElementById('sessionTimeout').value,
        security: Array.from(document.querySelectorAll('input[name="security"]:checked')).map(cb => cb.value)
    };
}

function collectAdvancedSettings() {
    return {
        cacheSize: document.getElementById('cacheSize').value,
        performance: Array.from(document.querySelectorAll('input[name="performance"]:checked')).map(cb => cb.value),
        debug: Array.from(document.querySelectorAll('input[name="debug"]:checked')).map(cb => cb.value)
    };
}

function collectWidgetSettings() {
    const widgets = [];
    document.querySelectorAll('.widget-item').forEach((widget, index) => {
        const checkbox = widget.querySelector('input[type="checkbox"]');
        const name = widget.querySelector('.widget-info span').textContent;
        widgets.push({
            name: name,
            enabled: checkbox.checked,
            order: index
        });
    });
    return widgets;
}

function loadUserSettings() {
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        applySettings(settings);
    }
}

function applySettings(settings) {
    // Apply trading settings
    if (settings.trading) {
        document.getElementById('investmentExperience').value = settings.trading.investmentExperience || 'intermediate';
        document.getElementById('riskTolerance').value = settings.trading.riskTolerance || 'moderate';
        // ... apply other settings
    }
    
    // Apply display settings
    if (settings.display) {
        if (settings.display.theme) {
            document.querySelector(`input[name="theme"][value="${settings.display.theme}"]`).checked = true;
            applyTheme(settings.display.theme);
        }
        // ... apply other display settings
    }
    
    // Apply other settings...
}

function resetToDefaults() {
    if (confirm('Are you sure you want to reset all settings to their default values? This action cannot be undone.')) {
        showNotification('Resetting to default settings...', 'info');
        
        setTimeout(() => {
            // Clear saved settings
            localStorage.removeItem('userSettings');
            
            // Reset form values to defaults
            resetFormDefaults();
            
            showNotification('Settings reset to defaults successfully!', 'success');
        }, 1500);
    }
}

function resetFormDefaults() {
    // Reset all form elements to their default values
    document.getElementById('investmentExperience').value = 'intermediate';
    document.getElementById('riskTolerance').value = 'moderate';
    document.querySelector('input[name="theme"][value="light"]').checked = true;
    applyTheme('light');
    
    // Reset checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.checked = cb.hasAttribute('checked');
    });
    
    // Reset other form elements...
}

function applyTheme(theme) {
    const body = document.body;
    body.classList.remove('light-theme', 'dark-theme', 'auto-theme');
    
    if (theme === 'dark') {
        body.classList.add('dark-theme');
    } else if (theme === 'auto') {
        // Detect system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        body.classList.add(prefersDark ? 'dark-theme' : 'light-theme');
    } else {
        body.classList.add('light-theme');
    }
    
    // Update chart theme if AdvancedCharts is available
    if (window.AdvancedCharts) {
        window.AdvancedCharts.currentTheme = theme === 'dark' ? 'dark' : 'light';
        localStorage.setItem('chart-theme', window.AdvancedCharts.currentTheme);
    }
}

function initializeWidgetDragDrop() {
    const widgetList = document.querySelector('.widget-list');
    let draggedElement = null;
    
    document.querySelectorAll('.widget-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggedElement = item;
            item.style.opacity = '0.5';
        });
        
        item.addEventListener('dragend', (e) => {
            item.style.opacity = '1';
            draggedElement = null;
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            if (draggedElement && draggedElement !== item) {
                const rect = item.getBoundingClientRect();
                const midpoint = rect.top + rect.height / 2;
                
                if (e.clientY < midpoint) {
                    widgetList.insertBefore(draggedElement, item);
                } else {
                    widgetList.insertBefore(draggedElement, item.nextSibling);
                }
            }
        });
    });
}

function clearCache() {
    showNotification('Clearing cache...', 'info');
    
    setTimeout(() => {
        // Clear various caches
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => caches.delete(name));
            });
        }
        
        // Clear localStorage cache items
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('cache_') || key.startsWith('data_')) {
                localStorage.removeItem(key);
            }
        });
        
        showNotification('Cache cleared successfully!', 'success');
    }, 1000);
}

function exportSettings() {
    showNotification('Exporting settings...', 'info');
    
    const settings = {
        trading: collectTradingSettings(),
        display: collectDisplaySettings(),
        notifications: collectNotificationSettings(),
        data: collectDataSettings(),
        privacy: collectPrivacySettings(),
        advanced: collectAdvancedSettings(),
        exportDate: new Date().toISOString(),
        version: '1.0'
    };
    
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `stock-scanner-settings-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showNotification('Settings exported successfully!', 'success');
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const settings = JSON.parse(e.target.result);
                    applySettings(settings);
                    showNotification('Settings imported successfully!', 'success');
                } catch (error) {
                    showNotification('Error importing settings. Please check the file format.', 'error');
                }
            };
            reader.readAsText(file);
        }
    });
    
    input.click();
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
        zIndex: '1003',
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