<?php
/**
 * Template Name: Dashboard
 * 
 * User dashboard with portfolio summary, watchlist, and market overview
 *
 * @package StockScannerPro
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="dashboard-container">
    
    <!-- Dashboard Sidebar -->
    <aside class="dashboard-sidebar">
        <div class="dashboard-user-info mb-6">
            <div class="user-avatar mb-3">
                <?php echo get_avatar(get_current_user_id(), 64, '', '', array('class' => 'w-16 h-16 rounded-full')); ?>
            </div>
            <h3 class="user-name text-lg font-semibold text-gray-900">
                <?php echo wp_get_current_user()->display_name; ?>
            </h3>
            <p class="user-plan text-sm text-gray-600">
                <?php
                $subscription = stock_scanner_get_user_subscription();
                echo esc_html(ucfirst($subscription['plan'])) . ' Plan';
                ?>
            </p>
        </div>

        <nav class="dashboard-nav" aria-label="Dashboard Navigation">
            <?php
            wp_nav_menu(array(
                'theme_location' => 'dashboard',
                'menu_class' => 'dashboard-menu space-y-2',
                'container' => false,
                'fallback_cb' => 'stock_scanner_default_dashboard_menu',
            ));
            ?>
        </nav>
    </aside>

    <!-- Dashboard Main Content -->
    <main class="dashboard-main">
        
        <!-- Dashboard Header -->
        <div class="dashboard-header mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p class="text-gray-600 mt-1">Welcome back! Here's your market overview.</p>
                </div>
                <div class="dashboard-actions">
                    <button class="btn btn-outline-primary btn-sm" data-action="refresh-dashboard">
                        <i class="fas fa-sync-alt mr-2"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div id="quick-actions" class="mb-8">
            <!-- Populated by JavaScript -->
        </div>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid dashboard-grid-2 mb-8">
            
            <!-- Portfolio Summary -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h2 class="dashboard-card-title">Portfolio Summary</h2>
                    <div class="dashboard-card-subtitle">Your investment overview</div>
                </div>
                <div id="portfolio-summary">
                    <!-- Populated by JavaScript -->
                </div>
                <div class="mt-4">
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('portfolio'))); ?>" 
                       class="btn btn-primary btn-sm">
                        View Full Portfolio
                    </a>
                </div>
            </div>

            <!-- Market Overview -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h2 class="dashboard-card-title">Market Overview</h2>
                    <div class="dashboard-card-subtitle">Today's market summary</div>
                </div>
                <div id="market-overview">
                    <!-- Populated by JavaScript -->
                </div>
                <div class="mt-4">
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('market-overview'))); ?>" 
                       class="btn btn-primary btn-sm">
                        View Market Details
                    </a>
                </div>
            </div>
        </div>

        <!-- Watchlist and News -->
        <div class="dashboard-grid dashboard-grid-2">
            
            <!-- Watchlist Preview -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h2 class="dashboard-card-title">Watchlist</h2>
                    <div class="dashboard-card-subtitle">Your tracked stocks</div>
                </div>
                <div id="watchlist-preview">
                    <!-- Populated by JavaScript -->
                </div>
                <div class="mt-4">
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('watchlist'))); ?>" 
                       class="btn btn-primary btn-sm">
                        Manage Watchlist
                    </a>
                </div>
            </div>

            <!-- News Feed -->
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h2 class="dashboard-card-title">Market News</h2>
                    <div class="dashboard-card-subtitle">Latest updates</div>
                </div>
                <div id="news-feed">
                    <!-- Populated by JavaScript -->
                </div>
                <div class="mt-4">
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('stock-news'))); ?>" 
                       class="btn btn-primary btn-sm">
                        View All News
                    </a>
                </div>
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="dashboard-card mt-8">
            <div class="dashboard-card-header">
                <h2 class="dashboard-card-title">Recent Activity</h2>
                <div class="dashboard-card-subtitle">Your latest actions</div>
            </div>
            
            <?php
            $user_id = get_current_user_id();
            $activity_log = get_user_meta($user_id, 'stock_scanner_activity_log', true);
            
            if (!empty($activity_log) && is_array($activity_log)) :
                $recent_activity = array_slice($activity_log, 0, 10);
            ?>
                <div class="activity-feed">
                    <?php foreach ($recent_activity as $activity) : ?>
                        <div class="activity-item flex items-start gap-3 py-3 border-b border-gray-100">
                            <div class="activity-icon mt-1">
                                <?php
                                $icon = 'fas fa-circle';
                                switch ($activity['activity']) {
                                    case 'login':
                                        $icon = 'fas fa-sign-in-alt text-green-500';
                                        break;
                                    case 'portfolio_update':
                                        $icon = 'fas fa-chart-line text-blue-500';
                                        break;
                                    case 'watchlist_update':
                                        $icon = 'fas fa-eye text-purple-500';
                                        break;
                                    case 'alert_created':
                                        $icon = 'fas fa-bell text-orange-500';
                                        break;
                                }
                                ?>
                                <i class="<?php echo esc_attr($icon); ?>"></i>
                            </div>
                            <div class="activity-content flex-1">
                                <div class="activity-description text-sm text-gray-900">
                                    <?php
                                    switch ($activity['activity']) {
                                        case 'login':
                                            echo 'Logged into account';
                                            break;
                                        case 'portfolio_update':
                                            echo 'Updated portfolio';
                                            break;
                                        case 'watchlist_update':
                                            echo 'Modified watchlist';
                                            break;
                                        case 'alert_created':
                                            echo 'Created price alert';
                                            break;
                                        default:
                                            echo esc_html(ucfirst(str_replace('_', ' ', $activity['activity'])));
                                    }
                                    ?>
                                </div>
                                <div class="activity-time text-xs text-gray-500">
                                    <?php echo human_time_diff(strtotime($activity['timestamp']), current_time('timestamp')) . ' ago'; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php else : ?>
                <p class="text-gray-600">No recent activity found.</p>
            <?php endif; ?>
        </div>
    </main>
</div>

<script>
// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerDashboard !== 'undefined') {
        StockScannerDashboard.init();
    }
});
</script>

<?php get_footer(); ?>