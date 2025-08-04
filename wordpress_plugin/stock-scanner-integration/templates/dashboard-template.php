<?php
/**
 * Stock Scanner Professional - Dashboard Template
 * Version: 3.0.0
 * 
 * Professional dashboard template with WordPress admin styling
 * and seamless navigation between different sections
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Get current user data
$current_user = wp_get_current_user();
$membership_level = function_exists('pmpro_getMembershipLevelForUser') ? 
    pmpro_getMembershipLevelForUser($current_user->ID) : null;
$membership_name = $membership_level ? $membership_level->name : 'Free';

// Get user stats (mock data for demonstration)
$user_stats = [
    'api_calls_today' => 8,
    'api_limit' => 15,
    'watchlist_count' => 12,
    'alerts_active' => 5,
    'portfolio_value' => 125750.50,
    'portfolio_change' => 2.34
];

get_header(); ?>

<div class="stock-scanner-pro">
    <!-- Professional Navigation -->
    <nav class="stock-scanner-nav">
        <div class="stock-scanner-nav-container">
            <div class="nav-logo">
                <h2 style="margin: 0; color: var(--wp-primary);">
                    <span class="dashicons dashicons-chart-line" style="font-size: 24px; margin-right: 8px;"></span>
                    Stock Scanner Pro
                </h2>
            </div>
            
            <ul class="stock-scanner-nav-menu">
                <li class="stock-scanner-nav-item">
                    <a href="/stock-scanner-dashboard/" class="stock-scanner-nav-link active">
                        <span class="dashicons dashicons-dashboard"></span>
                        Dashboard
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/stock-scanner/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-search"></span>
                        Scanner
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/watchlists/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-visibility"></span>
                        Watchlists
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/stock-alerts/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-bell"></span>
                        Alerts
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/market-analysis/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-analytics"></span>
                        Analysis
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/news-feed/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-rss"></span>
                        News
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/premium-plans/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-star-filled"></span>
                        Premium
                    </a>
                </li>
            </ul>
            
            <button class="stock-scanner-nav-toggle">
                <span class="dashicons dashicons-menu"></span>
            </button>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="stock-scanner-page-content">
        <div class="stock-scanner-container">
            <!-- Dashboard Header -->
            <div class="dashboard-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--wp-spacing-xl);">
                <div>
                    <h1 style="margin: 0 0 var(--wp-spacing-sm) 0; color: var(--wp-text-primary); font-size: 28px; font-weight: 600;">
                        Welcome back, <?php echo esc_html($current_user->display_name); ?>!
                    </h1>
                    <p style="margin: 0; color: var(--wp-text-secondary); font-size: 16px;">
                        Here's your trading overview for today
                    </p>
                </div>
                
                <!-- Membership Status -->
                <div class="membership-status">
                    <div class="membership-status-header">
                        <span class="membership-status-badge <?php echo strtolower($membership_name); ?>">
                            <?php echo esc_html($membership_name); ?>
                        </span>
                        <?php if (is_user_logged_in()): ?>
                        <div style="margin-left: var(--wp-spacing-md); font-size: 13px; color: var(--wp-text-secondary);">
                            API Usage: <span class="api-usage-current"><?php echo $user_stats['api_calls_today']; ?></span>/<span class="api-usage-limit"><?php echo $user_stats['api_limit']; ?></span>
                            <div class="progress-bar" style="width: 100px; margin-top: 4px;">
                                <div class="progress-bar-fill" style="width: <?php echo ($user_stats['api_calls_today'] / $user_stats['api_limit']) * 100; ?>%;"></div>
                            </div>
                        </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
            
            <!-- Quick Stats Grid -->
            <div class="stock-scanner-grid four-columns mb-xl">
                <!-- Portfolio Value -->
                <div class="stock-scanner-widget">
                    <div class="stock-widget-header">
                        <h3 class="stock-widget-title">
                            <span class="dashicons dashicons-portfolio" style="color: var(--wp-primary);"></span>
                            Portfolio Value
                        </h3>
                    </div>
                    <div class="dashboard-widget-content">
                        <div class="stat-number">$<?php echo number_format($user_stats['portfolio_value'], 2); ?></div>
                        <div class="stat-change <?php echo $user_stats['portfolio_change'] >= 0 ? 'positive' : 'negative'; ?>">
                            <?php echo $user_stats['portfolio_change'] >= 0 ? '+' : ''; ?><?php echo $user_stats['portfolio_change']; ?>% Today
                        </div>
                    </div>
                </div>
                
                <!-- API Usage -->
                <div class="stock-scanner-widget">
                    <div class="stock-widget-header">
                        <h3 class="stock-widget-title">
                            <span class="dashicons dashicons-cloud" style="color: var(--wp-primary);"></span>
                            API Usage
                        </h3>
                    </div>
                    <div class="dashboard-widget-content">
                        <div class="stat-number"><?php echo $user_stats['api_calls_today']; ?></div>
                        <div class="stat-label">of <?php echo $user_stats['api_limit']; ?> calls today</div>
                        <div class="progress-bar">
                            <div class="progress-bar-fill <?php echo $user_stats['api_calls_today'] / $user_stats['api_limit'] > 0.8 ? 'warning' : ''; ?>" 
                                 style="width: <?php echo ($user_stats['api_calls_today'] / $user_stats['api_limit']) * 100; ?>%;"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Watchlists -->
                <div class="stock-scanner-widget">
                    <div class="stock-widget-header">
                        <h3 class="stock-widget-title">
                            <span class="dashicons dashicons-visibility" style="color: var(--wp-primary);"></span>
                            Watchlists
                        </h3>
                    </div>
                    <div class="dashboard-widget-content">
                        <div class="stat-number"><?php echo $user_stats['watchlist_count']; ?></div>
                        <div class="stat-label">Stocks tracked</div>
                        <a href="/watchlists/" class="btn btn-primary btn-small mt-md stock-scanner-nav-link">View All</a>
                    </div>
                </div>
                
                <!-- Active Alerts -->
                <div class="stock-scanner-widget">
                    <div class="stock-widget-header">
                        <h3 class="stock-widget-title">
                            <span class="dashicons dashicons-bell" style="color: var(--wp-primary);"></span>
                            Active Alerts
                        </h3>
                    </div>
                    <div class="dashboard-widget-content">
                        <div class="stat-number"><?php echo $user_stats['alerts_active']; ?></div>
                        <div class="stat-label">Price alerts set</div>
                        <a href="/stock-alerts/" class="btn btn-secondary btn-small mt-md stock-scanner-nav-link">Manage</a>
                    </div>
                </div>
            </div>
            
            <!-- Main Content Grid -->
            <div class="stock-scanner-grid two-columns">
                <!-- Live Stock Widgets -->
                <div>
                    <h2 style="color: var(--wp-text-primary); margin-bottom: var(--wp-spacing-lg);">Featured Stocks</h2>
                    
                    <!-- AAPL Widget -->
                    <div class="stock-scanner-widget" data-symbol="AAPL">
                        <div class="stock-widget-header">
                            <div>
                                <h3 class="stock-widget-title">Apple Inc.</h3>
                                <div class="stock-widget-symbol">AAPL</div>
                            </div>
                            <button class="stock-widget-refresh">
                                <span class="dashicons dashicons-update"></span>
                                Refresh
                            </button>
                        </div>
                        <div class="stock-widget-price">
                            <span class="stock-price-current">$175.43</span>
                            <span class="stock-price-change positive">+2.15 (+1.24%)</span>
                        </div>
                        <div class="stock-widget-details">
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">Volume:</span>
                                <span class="stock-detail-value">45.2M</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">Market Cap:</span>
                                <span class="stock-detail-value">$2.73T</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">P/E Ratio:</span>
                                <span class="stock-detail-value">28.95</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">52W High:</span>
                                <span class="stock-detail-value">$199.62</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- MSFT Widget -->
                    <div class="stock-scanner-widget" data-symbol="MSFT">
                        <div class="stock-widget-header">
                            <div>
                                <h3 class="stock-widget-title">Microsoft Corporation</h3>
                                <div class="stock-widget-symbol">MSFT</div>
                            </div>
                            <button class="stock-widget-refresh">
                                <span class="dashicons dashicons-update"></span>
                                Refresh
                            </button>
                        </div>
                        <div class="stock-widget-price">
                            <span class="stock-price-current">$378.92</span>
                            <span class="stock-price-change negative">-1.85 (-0.49%)</span>
                        </div>
                        <div class="stock-widget-details">
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">Volume:</span>
                                <span class="stock-detail-value">22.1M</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">Market Cap:</span>
                                <span class="stock-detail-value">$2.82T</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">P/E Ratio:</span>
                                <span class="stock-detail-value">32.47</span>
                            </div>
                            <div class="stock-detail-item">
                                <span class="stock-detail-label">52W High:</span>
                                <span class="stock-detail-value">$384.52</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Actions & Tools -->
                <div>
                    <h2 style="color: var(--wp-text-primary); margin-bottom: var(--wp-spacing-lg);">Quick Actions</h2>
                    
                    <!-- Stock Search -->
                    <div class="stock-scanner-widget">
                        <div class="stock-widget-header">
                            <h3 class="stock-widget-title">
                                <span class="dashicons dashicons-search"></span>
                                Stock Search
                            </h3>
                        </div>
                        <div class="dashboard-widget-content">
                            <form class="stock-search-form" data-ajax="true">
                                <div class="form-group">
                                    <input type="text" name="search" placeholder="Search stocks by symbol or name..." 
                                           class="form-input" style="margin-bottom: var(--wp-spacing-md);">
                                    <button type="submit" class="btn btn-primary">
                                        <span class="dashicons dashicons-search"></span>
                                        Search
                                    </button>
                                </div>
                                <div class="search-results"></div>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Market Overview -->
                    <div class="stock-scanner-widget">
                        <div class="stock-widget-header">
                            <h3 class="stock-widget-title">
                                <span class="dashicons dashicons-chart-area"></span>
                                Market Overview
                            </h3>
                        </div>
                        <div class="dashboard-widget-content">
                            <div class="market-indices">
                                <div class="market-index" style="display: flex; justify-content: space-between; padding: var(--wp-spacing-sm) 0; border-bottom: 1px solid var(--wp-border-light);">
                                    <span style="font-weight: 600;">S&P 500</span>
                                    <span style="color: var(--wp-success);">+0.85%</span>
                                </div>
                                <div class="market-index" style="display: flex; justify-content: space-between; padding: var(--wp-spacing-sm) 0; border-bottom: 1px solid var(--wp-border-light);">
                                    <span style="font-weight: 600;">NASDAQ</span>
                                    <span style="color: var(--wp-success);">+1.24%</span>
                                </div>
                                <div class="market-index" style="display: flex; justify-content: space-between; padding: var(--wp-spacing-sm) 0; border-bottom: 1px solid var(--wp-border-light);">
                                    <span style="font-weight: 600;">Dow Jones</span>
                                    <span style="color: var(--wp-error);">-0.32%</span>
                                </div>
                                <div class="market-index" style="display: flex; justify-content: space-between; padding: var(--wp-spacing-sm) 0;">
                                    <span style="font-weight: 600;">Russell 2000</span>
                                    <span style="color: var(--wp-success);">+0.67%</span>
                                </div>
                            </div>
                            <a href="/market-analysis/" class="btn btn-secondary mt-md stock-scanner-nav-link" style="width: 100%; justify-content: center;">
                                View Full Analysis
                            </a>
                        </div>
                    </div>
                    
                    <!-- Recent News -->
                    <div class="stock-scanner-widget">
                        <div class="stock-widget-header">
                            <h3 class="stock-widget-title">
                                <span class="dashicons dashicons-rss"></span>
                                Market News
                            </h3>
                        </div>
                        <div class="dashboard-widget-content">
                            <div class="news-items">
                                <div class="news-item" style="padding: var(--wp-spacing-sm) 0; border-bottom: 1px solid var(--wp-border-light);">
                                    <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">
                                        <a href="#" style="color: var(--wp-text-primary); text-decoration: none;">
                                            Tech stocks rally on strong earnings
                                        </a>
                                    </h4>
                                    <p style="margin: 0; font-size: 12px; color: var(--wp-text-secondary);">
                                        2 hours ago
                                    </p>
                                </div>
                                <div class="news-item" style="padding: var(--wp-spacing-sm) 0; border-bottom: 1px solid var(--wp-border-light);">
                                    <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">
                                        <a href="#" style="color: var(--wp-text-primary); text-decoration: none;">
                                            Fed signals potential rate cuts
                                        </a>
                                    </h4>
                                    <p style="margin: 0; font-size: 12px; color: var(--wp-text-secondary);">
                                        4 hours ago
                                    </p>
                                </div>
                                <div class="news-item" style="padding: var(--wp-spacing-sm) 0;">
                                    <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">
                                        <a href="#" style="color: var(--wp-text-primary); text-decoration: none;">
                                            Energy sector shows strength
                                        </a>
                                    </h4>
                                    <p style="margin: 0; font-size: 12px; color: var(--wp-text-secondary);">
                                        6 hours ago
                                    </p>
                                </div>
                            </div>
                            <a href="/news-feed/" class="btn btn-secondary mt-md stock-scanner-nav-link" style="width: 100%; justify-content: center;">
                                View All News
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Upgrade Prompt for Free Users -->
            <?php if (!$membership_level || $membership_level->id <= 1): ?>
            <div class="stock-scanner-widget" style="background: linear-gradient(135deg, var(--wp-primary), var(--wp-primary-hover)); color: white; border: none; margin-top: var(--wp-spacing-xl);">
                <div style="padding: var(--wp-spacing-xl); text-align: center;">
                    <h3 style="color: white; margin-bottom: var(--wp-spacing-md); font-size: 24px;">
                        <span class="dashicons dashicons-star-filled" style="font-size: 28px; margin-right: 8px;"></span>
                        Unlock Premium Features
                    </h3>
                    <p style="color: rgba(255,255,255,0.9); margin-bottom: var(--wp-spacing-lg); font-size: 16px;">
                        Get unlimited API calls, advanced analytics, real-time alerts, and more!
                    </p>
                    <a href="/premium-plans/" class="btn" style="background: white; color: var(--wp-primary); border-color: white; font-weight: 600; padding: var(--wp-spacing-md) var(--wp-spacing-xl);">
                        View Premium Plans
                    </a>
                </div>
            </div>
            <?php endif; ?>
        </div>
    </div>
    
    <!-- Footer -->
    <footer style="background: var(--wp-surface); border-top: 1px solid var(--wp-border); padding: var(--wp-spacing-xl) 0; margin-top: var(--wp-spacing-xxl); text-align: center; color: var(--wp-text-secondary);">
        <div class="stock-scanner-container">
            <p style="margin: 0;">
                &copy; <?php echo date('Y'); ?> Stock Scanner Professional. Built with 
                <span style="color: var(--wp-error);">♥</span> for traders.
            </p>
        </div>
    </footer>
</div>

<?php get_footer(); ?>