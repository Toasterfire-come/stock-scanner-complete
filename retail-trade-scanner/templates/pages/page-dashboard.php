<?php
/**
 * Template Name: Dashboard
 * 
 * Dashboard page template with overview grid, KPIs, top movers, indices, market sentiment
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Sample data - in real implementation this would come from API/database
$portfolio_value = '$124,567.89';
$portfolio_change = '+5.23%';
$day_pl = '+$2,845.32';
$total_return = '+15.67%';

$top_movers = array(
    array('symbol' => 'AAPL', 'company' => 'Apple Inc.', 'price' => '$182.34', 'change' => '+2.45%', 'type' => 'positive'),
    array('symbol' => 'TSLA', 'company' => 'Tesla Inc.', 'price' => '$245.67', 'change' => '-1.28%', 'type' => 'negative'),
    array('symbol' => 'NVDA', 'company' => 'NVIDIA Corp.', 'price' => '$456.78', 'change' => '+3.67%', 'type' => 'positive'),
    array('symbol' => 'AMZN', 'company' => 'Amazon.com Inc.', 'price' => '$134.56', 'change' => '+0.89%', 'type' => 'positive'),
);

$market_indices = array(
    array('name' => 'S&P 500', 'value' => '4,567.23', 'change' => '+0.45%', 'type' => 'positive'),
    array('name' => 'NASDAQ', 'value' => '14,234.56', 'change' => '+0.78%', 'type' => 'positive'),
    array('name' => 'DOW JONES', 'value' => '34,567.89', 'change' => '-0.12%', 'type' => 'negative'),
);

$recent_alerts = array(
    array('message' => 'AAPL price target reached: $180.00', 'time' => '2 minutes ago', 'type' => 'success'),
    array('message' => 'High volume detected in TSLA', 'time' => '15 minutes ago', 'type' => 'info'),
    array('message' => 'Market volatility increasing', 'time' => '1 hour ago', 'type' => 'warning'),
);

// Layout configuration
$layout_args = array(
    'page_title' => __('Dashboard', 'retail-trade-scanner'),
    'page_description' => __('Overview of your portfolio performance and market activity', 'retail-trade-scanner'),
    'page_class' => 'dashboard-page',
    'header_actions' => array(
        array(
            'text' => __('Refresh Data', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'refresh',
            'classes' => 'refresh-data-btn'
        ),
        array(
            'text' => __('Export Report', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'download'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Dashboard Grid Layout -->
<div class="dashboard-grid bento-grid">
    <!-- Portfolio Overview Card -->
    <div class="dashboard-section bento-item-large">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Portfolio Overview', 'retail-trade-scanner'),
            'value' => $portfolio_value,
            'change' => $portfolio_change,
            'icon' => 'portfolio',
            'variant' => 'glass',
            'chart_data' => array(120000, 121000, 119000, 122000, 124567), // Sample chart data
            'clickable' => true,
            'url' => home_url('/portfolio/')
        ));
        ?>
    </div>

    <!-- Daily P/L Card -->
    <div class="dashboard-section bento-item-medium">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Today\'s P/L', 'retail-trade-scanner'),
            'value' => $day_pl,
            'change' => '+2.34%',
            'icon' => 'trending-up',
            'variant' => 'default',
            'size' => 'base'
        ));
        ?>
    </div>

    <!-- Total Return Card -->
    <div class="dashboard-section bento-item-small">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Total Return', 'retail-trade-scanner'),
            'value' => $total_return,
            'icon' => 'percent',
            'variant' => 'elevated',
            'size' => 'sm'
        ));
        ?>
    </div>

    <!-- Top Movers Section -->
    <div class="dashboard-section bento-item-medium">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Top Movers', 'retail-trade-scanner'); ?></h3>
                <a href="<?php echo esc_url(home_url('/popular/')); ?>" class="view-all-link">
                    <?php esc_html_e('View All', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', array('width' => '16', 'height' => '16')); ?>
                </a>
            </div>
            <div class="card-body">
                <div class="movers-list">
                    <?php foreach ($top_movers as $mover) : ?>
                        <div class="mover-item">
                            <div class="mover-info">
                                <span class="mover-symbol"><?php echo esc_html($mover['symbol']); ?></span>
                                <span class="mover-price"><?php echo esc_html($mover['price']); ?></span>
                            </div>
                            <div class="mover-change">
                                <?php
                                get_template_part('template-parts/components/badge', null, array(
                                    'value' => $mover['change'],
                                    'type' => $mover['type'],
                                    'size' => 'sm'
                                ));
                                ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </div>

    <!-- Market Indices -->
    <div class="dashboard-section bento-item-medium">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Market Indices', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <div class="indices-grid">
                    <?php foreach ($market_indices as $index) : ?>
                        <div class="index-item">
                            <h4 class="index-name"><?php echo esc_html($index['name']); ?></h4>
                            <div class="index-value"><?php echo esc_html($index['value']); ?></div>
                            <?php
                            get_template_part('template-parts/components/badge', null, array(
                                'value' => $index['change'],
                                'type' => $index['type'],
                                'size' => 'xs'
                            ));
                            ?>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </div>

    <!-- Recent Alerts -->
    <div class="dashboard-section bento-item-medium">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Recent Alerts', 'retail-trade-scanner'); ?></h3>
                <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="view-all-link">
                    <?php esc_html_e('Manage Alerts', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('settings', array('width' => '16', 'height' => '16')); ?>
                </a>
            </div>
            <div class="card-body">
                <div class="alerts-list">
                    <?php foreach ($recent_alerts as $alert) : ?>
                        <div class="alert-item">
                            <div class="alert-content">
                                <p class="alert-message"><?php echo esc_html($alert['message']); ?></p>
                                <span class="alert-time"><?php echo esc_html($alert['time']); ?></span>
                            </div>
                            <div class="alert-indicator">
                                <?php
                                $alert_icons = array(
                                    'success' => 'check-circle',
                                    'info' => 'info-circle',
                                    'warning' => 'alert-triangle'
                                );
                                echo rts_get_icon($alert_icons[$alert['type']] ?? 'info-circle', array(
                                    'width' => '16',
                                    'height' => '16',
                                    'class' => 'text-' . $alert['type']
                                ));
                                ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </div>

    <!-- Market Heatmap Section -->
    <div class="dashboard-section bento-item-large">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Market Heatmap', 'retail-trade-scanner'); ?></h3>
                <div class="heatmap-controls">
                    <button class="control-btn active" data-period="1d">1D</button>
                    <button class="control-btn" data-period="1w">1W</button>
                    <button class="control-btn" data-period="1m">1M</button>
                </div>
            </div>
            <div class="card-body">
                <div class="heatmap-container">
                    <div class="heatmap-placeholder">
                        <?php
                        get_template_part('template-parts/components/chart-shell', null, array(
                            'title' => '',
                            'type' => 'heatmap',
                            'height' => '300px',
                            'loading' => false,
                            'show_controls' => false,
                            'variant' => 'minimal'
                        ));
                        ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="dashboard-section bento-item-small">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Quick Actions', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <div class="quick-actions-grid">
                    <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="quick-action-item">
                        <?php echo rts_get_icon('scanner', array('width' => '24', 'height' => '24')); ?>
                        <span><?php esc_html_e('Scanner', 'retail-trade-scanner'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(home_url('/watchlists/')); ?>" class="quick-action-item">
                        <?php echo rts_get_icon('watchlist', array('width' => '24', 'height' => '24')); ?>
                        <span><?php esc_html_e('Watchlist', 'retail-trade-scanner'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(home_url('/news/')); ?>" class="quick-action-item">
                        <?php echo rts_get_icon('news', array('width' => '24', 'height' => '24')); ?>
                        <span><?php esc_html_e('News', 'retail-trade-scanner'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="quick-action-item">
                        <?php echo rts_get_icon('alerts', array('width' => '24', 'height' => '24')); ?>
                        <span><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Dashboard JavaScript -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Refresh data functionality
    const refreshBtn = document.querySelector('.refresh-data-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Show loading state
            this.classList.add('loading');
            this.disabled = true;
            
            // Simulate data refresh
            setTimeout(() => {
                this.classList.remove('loading');
                this.disabled = false;
                RTS.showSuccess('Dashboard data refreshed successfully!');
            }, 2000);
        });
    }
    
    // Heatmap controls
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update heatmap based on period
            const period = this.dataset.period;
            console.log('Updating heatmap for period:', period);
            // Implement heatmap update logic here
        });
    });
    
    // Auto-refresh dashboard data every 30 seconds
    setInterval(function() {
        // Implement background data refresh
        console.log('Auto-refreshing dashboard data...');
    }, 30000);
});
</script>

                </div> <!-- .page-content -->
            </div> <!-- .container -->
        </div> <!-- .page-content-section -->
    </main> <!-- .main-content-area -->
</div> <!-- .page-wrapper -->

<style>
/* Dashboard-specific styles */
.dashboard-grid {
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.dashboard-section {
    position: relative;
}

/* Top Movers Styles */
.movers-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.mover-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
}

.mover-item:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(4px);
}

.mover-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.mover-symbol {
    font-weight: 700;
    font-size: var(--text-sm);
    color: var(--gray-900);
}

.mover-price {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

/* Market Indices Styles */
.indices-grid {
    display: grid;
    gap: var(--spacing-md);
}

.index-item {
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
}

.index-item:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.index-name {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--gray-600);
    margin: 0 0 var(--spacing-xs);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.index-value {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--spacing-sm);
}

/* Alerts Styles */
.alerts-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.alert-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-sm);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
}

.alert-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.alert-content {
    flex: 1;
    min-width: 0;
}

.alert-message {
    font-size: var(--text-sm);
    color: var(--gray-800);
    margin: 0 0 var(--spacing-xs);
    line-height: 1.4;
}

.alert-time {
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.alert-indicator {
    flex-shrink: 0;
    margin-top: 2px;
}

/* Heatmap Styles */
.heatmap-controls {
    display: flex;
    gap: var(--spacing-xs);
}

.control-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--gray-600);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.control-btn:hover,
.control-btn.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

/* Quick Actions Styles */
.quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
}

.quick-action-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-lg) var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    color: var(--gray-700);
    text-decoration: none;
    transition: all var(--transition-normal) var(--easing-standard);
    font-size: var(--text-sm);
    font-weight: 600;
}

.quick-action-item:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--primary-600);
    transform: translateY(-2px);
    text-decoration: none;
    box-shadow: var(--shadow-md);
}

/* View All Links */
.view-all-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--primary-600);
    text-decoration: none;
    transition: all var(--transition-fast) var(--easing-standard);
}

.view-all-link:hover {
    color: var(--primary-700);
    text-decoration: none;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
    .dashboard-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .bento-item-large,
    .bento-item-medium,
    .bento-item-small {
        grid-column: span 1;
        grid-row: auto;
    }
}

@media (max-width: 640px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .indices-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .quick-actions-grid {
        grid-template-columns: repeat(4, 1fr);
    }
    
    .quick-action-item {
        padding: var(--spacing-md) var(--spacing-xs);
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .mover-symbol,
[data-theme="dark"] .index-value,
[data-theme="dark"] .alert-message {
    color: var(--gray-100);
}

[data-theme="dark"] .mover-price,
[data-theme="dark"] .alert-time {
    color: var(--gray-400);
}
</style>

<?php get_footer(); ?>