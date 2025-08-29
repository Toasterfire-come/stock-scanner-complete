<?php
/**
 * Template for Dashboard Page
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="dashboard-page">
    <!-- Breadcrumbs -->
    <nav class="breadcrumbs" aria-label="Breadcrumb">
        <div class="container">
            <ol class="breadcrumb-list">
                <li class="breadcrumb-item">
                    <a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
                </li>
                <li class="breadcrumb-separator"><?php echo rts_get_icon('chevron-right', ['width' => '16', 'height' => '16']); ?></li>
                <li class="breadcrumb-item active"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></li>
            </ol>
        </div>
    </nav>

    <!-- Page Header -->
    <div class="page-header">
        <div class="container">
            <div class="page-header-content">
                <div class="page-header-text">
                    <h1 class="page-title">
                        <?php echo rts_get_icon('dashboard', ['width' => '32', 'height' => '32', 'class' => 'page-title-icon']); ?>
                        <?php esc_html_e('Trading Dashboard', 'retail-trade-scanner'); ?>
                    </h1>
                    <p class="page-description">
                        <?php esc_html_e('Monitor your portfolio, track market trends, and manage your investments all in one place.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
                <div class="page-header-actions">
                    <button class="btn btn-secondary" id="refresh-dashboard">
                        <?php echo rts_get_icon('activity', ['width' => '20', 'height' => '20']); ?>
                        <?php esc_html_e('Refresh Data', 'retail-trade-scanner'); ?>
                    </button>
                    <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn btn-primary">
                        <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                        <?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?>
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Dashboard Content -->
    <div class="container">
        <!-- KPI Cards -->
        <section class="kpi-section">
            <div class="grid grid-4 gap-xl">
                <div class="kpi-card glass-card animate-scale-in">
                    <div class="kpi-header">
                        <h3 class="kpi-title"><?php esc_html_e('Portfolio Value', 'retail-trade-scanner'); ?></h3>
                        <?php echo rts_get_icon('portfolio', ['width' => '24', 'height' => '24', 'class' => 'kpi-icon']); ?>
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-value loading-value" data-endpoint="portfolio-value">$--</div>
                        <div class="kpi-change">
                            <span class="change-value loading-value" data-endpoint="portfolio-change">--</span>
                            <span class="change-period"><?php esc_html_e('Today', 'retail-trade-scanner'); ?></span>
                        </div>
                    </div>
                </div>

                <div class="kpi-card glass-card animate-scale-in">
                    <div class="kpi-header">
                        <h3 class="kpi-title"><?php esc_html_e('Total P&L', 'retail-trade-scanner'); ?></h3>
                        <?php echo rts_get_icon('trending-up', ['width' => '24', 'height' => '24', 'class' => 'kpi-icon']); ?>
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-value loading-value" data-endpoint="total-pl">$--</div>
                        <div class="kpi-change">
                            <span class="change-value loading-value" data-endpoint="pl-change">--</span>
                            <span class="change-period"><?php esc_html_e('All Time', 'retail-trade-scanner'); ?></span>
                        </div>
                    </div>
                </div>

                <div class="kpi-card glass-card animate-scale-in">
                    <div class="kpi-header">
                        <h3 class="kpi-title"><?php esc_html_e('Active Positions', 'retail-trade-scanner'); ?></h3>
                        <?php echo rts_get_icon('activity', ['width' => '24', 'height' => '24', 'class' => 'kpi-icon']); ?>
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-value loading-value" data-endpoint="active-positions">--</div>
                        <div class="kpi-meta">
                            <span class="loading-value" data-endpoint="winning-positions">--</span> <?php esc_html_e('winning', 'retail-trade-scanner'); ?>
                        </div>
                    </div>
                </div>

                <div class="kpi-card glass-card animate-scale-in">
                    <div class="kpi-header">
                        <h3 class="kpi-title"><?php esc_html_e('Watchlist Alerts', 'retail-trade-scanner'); ?></h3>
                        <?php echo rts_get_icon('alerts', ['width' => '24', 'height' => '24', 'class' => 'kpi-icon']); ?>
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-value loading-value" data-endpoint="active-alerts">--</div>
                        <div class="kpi-meta">
                            <span class="loading-value" data-endpoint="triggered-alerts">--</span> <?php esc_html_e('triggered', 'retail-trade-scanner'); ?>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Main Dashboard Grid -->
        <section class="dashboard-grid bento-grid">
            <!-- Market Overview -->
            <div class="dashboard-widget bento-item-large glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Market Overview', 'retail-trade-scanner'); ?></h3>
                    <div class="widget-actions">
                        <button class="btn-icon btn-ghost" title="<?php esc_attr_e('Settings', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('settings', ['width' => '16', 'height' => '16']); ?>
                        </button>
                    </div>
                </div>
                <div class="widget-content">
                    <div class="market-indices">
                        <div class="index-item">
                            <span class="index-name">S&P 500</span>
                            <span class="index-value loading-value" data-endpoint="sp500">--</span>
                            <span class="index-change loading-value" data-endpoint="sp500-change">--</span>
                        </div>
                        <div class="index-item">
                            <span class="index-name">NASDAQ</span>
                            <span class="index-value loading-value" data-endpoint="nasdaq">--</span>
                            <span class="index-change loading-value" data-endpoint="nasdaq-change">--</span>
                        </div>
                        <div class="index-item">
                            <span class="index-name">DOW</span>
                            <span class="index-value loading-value" data-endpoint="dow">--</span>
                            <span class="index-change loading-value" data-endpoint="dow-change">--</span>
                        </div>
                    </div>
                    <div class="market-chart">
                        <canvas id="market-chart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>

            <!-- Top Movers -->
            <div class="dashboard-widget bento-item-medium glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Top Movers', 'retail-trade-scanner'); ?></h3>
                    <div class="widget-tabs">
                        <button class="tab-btn active" data-tab="gainers"><?php esc_html_e('Gainers', 'retail-trade-scanner'); ?></button>
                        <button class="tab-btn" data-tab="losers"><?php esc_html_e('Losers', 'retail-trade-scanner'); ?></button>
                    </div>
                </div>
                <div class="widget-content">
                    <div class="movers-list" id="gainers-list">
                        <!-- Dynamic content loaded via JavaScript -->
                        <div class="mover-skeleton">
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                            <div class="skeleton" style="width: 80px; height: 20px;"></div>
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                        </div>
                        <div class="mover-skeleton">
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                            <div class="skeleton" style="width: 80px; height: 20px;"></div>
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                        </div>
                        <div class="mover-skeleton">
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                            <div class="skeleton" style="width: 80px; height: 20px;"></div>
                            <div class="skeleton" style="width: 60px; height: 20px;"></div>
                        </div>
                    </div>
                    <div class="movers-list hidden" id="losers-list">
                        <!-- Dynamic content loaded via JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Portfolio Allocation -->
            <div class="dashboard-widget bento-item-medium glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Portfolio Allocation', 'retail-trade-scanner'); ?></h3>
                    <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="btn btn-sm btn-outline">
                        <?php esc_html_e('View Details', 'retail-trade-scanner'); ?>
                    </a>
                </div>
                <div class="widget-content">
                    <div class="allocation-chart">
                        <canvas id="allocation-chart" width="300" height="300"></canvas>
                    </div>
                    <div class="allocation-legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: #3b82f6;"></div>
                            <span class="legend-label"><?php esc_html_e('Stocks', 'retail-trade-scanner'); ?></span>
                            <span class="legend-value loading-value" data-endpoint="stocks-allocation">--</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #d946ef;"></div>
                            <span class="legend-label"><?php esc_html_e('Crypto', 'retail-trade-scanner'); ?></span>
                            <span class="legend-value loading-value" data-endpoint="crypto-allocation">--</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #16a34a;"></div>
                            <span class="legend-label"><?php esc_html_e('Cash', 'retail-trade-scanner'); ?></span>
                            <span class="legend-value loading-value" data-endpoint="cash-allocation">--</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="dashboard-widget bento-item-medium glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Recent Activity', 'retail-trade-scanner'); ?></h3>
                    <div class="widget-actions">
                        <button class="btn btn-sm btn-ghost"><?php esc_html_e('View All', 'retail-trade-scanner'); ?></button>
                    </div>
                </div>
                <div class="widget-content">
                    <div class="activity-list">
                        <!-- Dynamic content loaded via JavaScript -->
                        <div class="activity-skeleton">
                            <div class="skeleton-circle" style="width: 32px; height: 32px;"></div>
                            <div class="skeleton-content">
                                <div class="skeleton" style="width: 120px; height: 16px;"></div>
                                <div class="skeleton" style="width: 80px; height: 14px; margin-top: 4px;"></div>
                            </div>
                        </div>
                        <div class="activity-skeleton">
                            <div class="skeleton-circle" style="width: 32px; height: 32px;"></div>
                            <div class="skeleton-content">
                                <div class="skeleton" style="width: 120px; height: 16px;"></div>
                                <div class="skeleton" style="width: 80px; height: 14px; margin-top: 4px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="dashboard-widget bento-item-small glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Quick Actions', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="widget-content">
                    <div class="quick-actions">
                        <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="action-btn">
                            <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Scan Stocks', 'retail-trade-scanner'); ?></span>
                        </a>
                        <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="action-btn">
                            <?php echo rts_get_icon('alerts', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Set Alert', 'retail-trade-scanner'); ?></span>
                        </a>
                        <a href="<?php echo esc_url(home_url('/watchlists/')); ?>" class="action-btn">
                            <?php echo rts_get_icon('watchlist', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Watchlist', 'retail-trade-scanner'); ?></span>
                        </a>
                        <a href="<?php echo esc_url(home_url('/news/')); ?>" class="action-btn">
                            <?php echo rts_get_icon('news', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('News', 'retail-trade-scanner'); ?></span>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Market News -->
            <div class="dashboard-widget bento-item-medium glass-card">
                <div class="widget-header">
                    <h3 class="widget-title"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></h3>
                    <a href="<?php echo esc_url(home_url('/news/')); ?>" class="btn btn-sm btn-outline">
                        <?php esc_html_e('View All', 'retail-trade-scanner'); ?>
                    </a>
                </div>
                <div class="widget-content">
                    <div class="news-list">
                        <!-- Dynamic content loaded via JavaScript -->
                        <div class="news-skeleton">
                            <div class="skeleton" style="width: 100%; height: 16px;"></div>
                            <div class="skeleton" style="width: 80%; height: 14px; margin-top: 4px;"></div>
                            <div class="skeleton" style="width: 60px; height: 12px; margin-top: 8px;"></div>
                        </div>
                        <div class="news-skeleton">
                            <div class="skeleton" style="width: 100%; height: 16px;"></div>
                            <div class="skeleton" style="width: 80%; height: 14px; margin-top: 4px;"></div>
                            <div class="skeleton" style="width: 60px; height: 12px; margin-top: 8px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</div>

<!-- Dashboard JavaScript -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initDashboard();
    
    // Tab switching
    initTabSwitching();
    
    // Refresh functionality
    initRefreshButton();
    
    // Load dashboard data
    loadDashboardData();
    
    // Set up auto-refresh
    setInterval(loadDashboardData, 60000); // Refresh every minute
});

function initDashboard() {
    console.log('Dashboard initialized');
    RTS.showInfo('Dashboard loaded successfully');
}

function initTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tab = this.dataset.tab;
            
            // Update active tab
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide content
            document.querySelectorAll('.movers-list').forEach(list => list.classList.add('hidden'));
            const targetList = document.getElementById(tab + '-list');
            if (targetList) {
                targetList.classList.remove('hidden');
            }
        });
    });
}

function initRefreshButton() {
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.classList.add('loading');
            loadDashboardData();
            
            setTimeout(() => {
                this.classList.remove('loading');
                RTS.showSuccess('Dashboard refreshed');
            }, 2000);
        });
    }
}

function loadDashboardData() {
    // Simulate loading real data
    setTimeout(() => {
        updateKPIs();
        updateMarketData();
        updatePortfolioData();
        updateActivity();
        updateNews();
        hideSkeletons();
    }, 1500);
}

function updateKPIs() {
    // Update portfolio value
    updateValue('[data-endpoint="portfolio-value"]', '$124,567.89');
    updateValue('[data-endpoint="portfolio-change"]', '+$2,341.56 (+1.92%)', 'positive');
    
    // Update P&L
    updateValue('[data-endpoint="total-pl"]', '+$12,456.78');
    updateValue('[data-endpoint="pl-change"]', '+15.67%', 'positive');
    
    // Update positions
    updateValue('[data-endpoint="active-positions"]', '23');
    updateValue('[data-endpoint="winning-positions"]', '18');
    
    // Update alerts
    updateValue('[data-endpoint="active-alerts"]', '12');
    updateValue('[data-endpoint="triggered-alerts"]', '3');
}

function updateMarketData() {
    // Update market indices
    updateValue('[data-endpoint="sp500"]', '4,234.56');
    updateValue('[data-endpoint="sp500-change"]', '+0.45%', 'positive');
    
    updateValue('[data-endpoint="nasdaq"]', '12,987.34');
    updateValue('[data-endpoint="nasdaq-change"]', '-0.23%', 'negative');
    
    updateValue('[data-endpoint="dow"]', '34,567.89');
    updateValue('[data-endpoint="dow-change"]', '+0.12%', 'positive');
}

function updatePortfolioData() {
    // Update allocation
    updateValue('[data-endpoint="stocks-allocation"]', '65%');
    updateValue('[data-endpoint="crypto-allocation"]', '25%');
    updateValue('[data-endpoint="cash-allocation"]', '10%');
}

function updateActivity() {
    const activityList = document.querySelector('.activity-list');
    if (activityList) {
        activityList.innerHTML = `
            <div class="activity-item">
                <div class="activity-icon bg-success">
                    ${RTS.components.getIcon('trending-up', 16)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">Bought 50 shares of AAPL</div>
                    <div class="activity-time">2 hours ago</div>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-icon bg-danger">
                    ${RTS.components.getIcon('trending-down', 16)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">Sold 100 shares of TSLA</div>
                    <div class="activity-time">4 hours ago</div>
                </div>
            </div>
        `;
    }
}

function updateNews() {
    const newsList = document.querySelector('.news-list');
    if (newsList) {
        newsList.innerHTML = `
            <div class="news-item">
                <div class="news-title">Fed Considers Rate Cut Amid Economic Concerns</div>
                <div class="news-excerpt">Federal Reserve officials signal potential monetary policy shift...</div>
                <div class="news-time">1 hour ago</div>
            </div>
            <div class="news-item">
                <div class="news-title">Tech Stocks Rally on AI Breakthrough</div>
                <div class="news-excerpt">Major technology companies see gains following artificial intelligence...</div>
                <div class="news-time">3 hours ago</div>
            </div>
        `;
    }
}

function updateValue(selector, value, changeType = null) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = value;
        element.classList.remove('loading-value');
        
        if (changeType) {
            element.classList.add(changeType === 'positive' ? 'text-success' : 'text-danger');
        }
    }
}

function hideSkeletons() {
    document.querySelectorAll('.skeleton, .mover-skeleton, .activity-skeleton, .news-skeleton').forEach(skeleton => {
        skeleton.style.display = 'none';
    });
}
</script>

<?php
get_footer();
?>