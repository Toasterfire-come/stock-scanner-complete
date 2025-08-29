<?php
/**
 * Template Name: Portfolio
 * 
 * Portfolio tracking with positions, performance charts, allocation analysis
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Sample portfolio data - in real implementation this would come from API/database
$portfolio_summary = array(
    'total_value' => '$124,567.89',
    'day_change' => '+$2,845.32',
    'day_change_percent' => '+2.34%',
    'total_return' => '+$18,567.89',
    'total_return_percent' => '+17.54%',
    'buying_power' => '$8,432.11'
);

$positions = array(
    array(
        'symbol' => 'AAPL',
        'company' => 'Apple Inc.',
        'shares' => '150',
        'avg_cost' => '$165.40',
        'current_price' => '$182.34',
        'market_value' => '$27,351.00',
        'unrealized_pl' => '+$2,541.00',
        'unrealized_pl_percent' => '+10.24%',
        'weight' => '21.95%',
        'type' => 'positive'
    ),
    array(
        'symbol' => 'TSLA',
        'company' => 'Tesla Inc.',
        'shares' => '50',
        'avg_cost' => '$255.80',
        'current_price' => '$245.67',
        'market_value' => '$12,283.50',
        'unrealized_pl' => '-$506.50',
        'unrealized_pl_percent' => '-3.96%',
        'weight' => '9.86%',
        'type' => 'negative'
    ),
    array(
        'symbol' => 'NVDA',
        'company' => 'NVIDIA Corporation',
        'shares' => '75',
        'avg_cost' => '$420.15',
        'current_price' => '$456.78',
        'market_value' => '$34,258.50',
        'unrealized_pl' => '+$2,747.25',
        'unrealized_pl_percent' => '+8.72%',
        'weight' => '27.51%',
        'type' => 'positive'
    )
);

$recent_transactions = array(
    array(
        'type' => 'BUY',
        'symbol' => 'AAPL',
        'shares' => '25',
        'price' => '$178.45',
        'total' => '$4,461.25',
        'date' => '2024-01-15',
        'time' => '10:30 AM'
    ),
    array(
        'type' => 'SELL',
        'symbol' => 'MSFT',
        'shares' => '40',
        'price' => '$412.67',
        'total' => '$16,506.80',
        'date' => '2024-01-14',
        'time' => '2:15 PM'
    ),
    array(
        'type' => 'BUY',
        'symbol' => 'NVDA',
        'shares' => '10',
        'price' => '$445.30',
        'total' => '$4,453.00',
        'date' => '2024-01-12',
        'time' => '11:45 AM'
    )
);

$layout_args = array(
    'page_title' => __('Portfolio', 'retail-trade-scanner'),
    'page_description' => __('Track your investment performance and manage your positions', 'retail-trade-scanner'),
    'page_class' => 'portfolio-page',
    'header_actions' => array(
        array(
            'text' => __('Add Position', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'plus'
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

<!-- Portfolio Overview Cards -->
<div class="portfolio-overview grid grid-4 gap-lg mb-2xl">
    <div class="overview-card">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Total Value', 'retail-trade-scanner'),
            'value' => $portfolio_summary['total_value'],
            'change' => $portfolio_summary['day_change'],
            'change_percent' => $portfolio_summary['day_change_percent'],
            'icon' => 'portfolio',
            'variant' => 'glass'
        ));
        ?>
    </div>
    
    <div class="overview-card">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Total Return', 'retail-trade-scanner'),
            'value' => $portfolio_summary['total_return'],
            'change_percent' => $portfolio_summary['total_return_percent'],
            'icon' => 'trending-up',
            'variant' => 'elevated'
        ));
        ?>
    </div>
    
    <div class="overview-card">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Day Change', 'retail-trade-scanner'),
            'value' => $portfolio_summary['day_change'],
            'change_percent' => $portfolio_summary['day_change_percent'],
            'icon' => 'activity',
            'variant' => 'default'
        ));
        ?>
    </div>
    
    <div class="overview-card">
        <?php
        get_template_part('template-parts/components/card', null, array(
            'title' => __('Buying Power', 'retail-trade-scanner'),
            'value' => $portfolio_summary['buying_power'],
            'icon' => 'dollar-sign',
            'variant' => 'glass'
        ));
        ?>
    </div>
</div>

<!-- Main Portfolio Content -->
<div class="portfolio-content grid grid-cols-12 gap-lg">
    
    <!-- Performance Chart -->
    <div class="portfolio-chart col-span-8">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Performance Chart', 'retail-trade-scanner'); ?></h3>
                <div class="chart-controls">
                    <div class="timeframe-buttons">
                        <button class="timeframe-btn active" data-period="1D">1D</button>
                        <button class="timeframe-btn" data-period="1W">1W</button>
                        <button class="timeframe-btn" data-period="1M">1M</button>
                        <button class="timeframe-btn" data-period="3M">3M</button>
                        <button class="timeframe-btn" data-period="1Y">1Y</button>
                        <button class="timeframe-btn" data-period="ALL">ALL</button>
                    </div>
                </div>
            </div>
            
            <div class="card-body">
                <?php
                get_template_part('template-parts/components/chart-shell', null, array(
                    'title' => '',
                    'type' => 'line',
                    'height' => '350px',
                    'loading' => false,
                    'show_controls' => false,
                    'variant' => 'performance'
                ));
                ?>
            </div>
        </div>
    </div>
    
    <!-- Allocation Breakdown -->
    <div class="portfolio-allocation col-span-4">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Allocation', 'retail-trade-scanner'); ?></h3>
                <div class="allocation-toggle">
                    <button class="toggle-btn active" data-view="sector">Sector</button>
                    <button class="toggle-btn" data-view="position">Position</button>
                </div>
            </div>
            
            <div class="card-body">
                <!-- Pie Chart Placeholder -->
                <div class="allocation-chart">
                    <?php
                    get_template_part('template-parts/components/chart-shell', null, array(
                        'title' => '',
                        'type' => 'pie',
                        'height' => '200px',
                        'loading' => false,
                        'show_controls' => false,
                        'variant' => 'minimal'
                    ));
                    ?>
                </div>
                
                <!-- Allocation Legend -->
                <div class="allocation-legend">
                    <div class="legend-item">
                        <span class="legend-color" style="background: #3b82f6;"></span>
                        <span class="legend-label">Technology</span>
                        <span class="legend-value">58.46%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #10b981;"></span>
                        <span class="legend-label">Consumer</span>
                        <span class="legend-value">21.95%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #f59e0b;"></span>
                        <span class="legend-label">Auto</span>
                        <span class="legend-value">9.86%</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ef4444;"></span>
                        <span class="legend-label">Cash</span>
                        <span class="legend-value">9.73%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Positions Table -->
    <div class="portfolio-positions col-span-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Positions', 'retail-trade-scanner'); ?></h3>
                <div class="positions-actions">
                    <button class="btn btn-ghost btn-sm">
                        <?php echo rts_get_icon('filter', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Filter', 'retail-trade-scanner'); ?>
                    </button>
                    <button class="btn btn-outline btn-sm">
                        <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>
            
            <div class="card-body">
                <?php
                get_template_part('template-parts/components/table', null, array(
                    'id' => 'positions-table',
                    'headers' => array(
                        'symbol' => __('Symbol', 'retail-trade-scanner'),
                        'shares' => __('Shares', 'retail-trade-scanner'),
                        'avg_cost' => __('Avg Cost', 'retail-trade-scanner'),
                        'current_price' => __('Current', 'retail-trade-scanner'),
                        'market_value' => __('Market Value', 'retail-trade-scanner'),
                        'unrealized_pl' => __('Unrealized P/L', 'retail-trade-scanner'),
                        'weight' => __('Weight', 'retail-trade-scanner'),
                        'actions' => __('Actions', 'retail-trade-scanner')
                    ),
                    'data' => $positions,
                    'sortable' => true,
                    'variant' => 'positions'
                ));
                ?>
            </div>
        </div>
    </div>
    
    <!-- Recent Transactions -->
    <div class="portfolio-transactions col-span-6">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Recent Transactions', 'retail-trade-scanner'); ?></h3>
                <a href="<?php echo esc_url(home_url('/transactions/')); ?>" class="view-all-link">
                    <?php esc_html_e('View All', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>
            
            <div class="card-body">
                <div class="transactions-list">
                    <?php foreach ($recent_transactions as $transaction) : ?>
                        <div class="transaction-item">
                            <div class="transaction-type">
                                <span class="type-badge <?php echo strtolower($transaction['type']); ?>">
                                    <?php echo esc_html($transaction['type']); ?>
                                </span>
                            </div>
                            
                            <div class="transaction-details">
                                <div class="transaction-header">
                                    <span class="symbol"><?php echo esc_html($transaction['symbol']); ?></span>
                                    <span class="shares"><?php echo esc_html($transaction['shares']); ?> shares</span>
                                </div>
                                <div class="transaction-meta">
                                    <span class="price">@<?php echo esc_html($transaction['price']); ?></span>
                                    <span class="date"><?php echo esc_html($transaction['date']); ?></span>
                                </div>
                            </div>
                            
                            <div class="transaction-amount">
                                <?php echo esc_html($transaction['total']); ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Performance Metrics -->
    <div class="portfolio-metrics col-span-6">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Performance Metrics', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Beta', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value">1.15</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Alpha', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value positive">+2.34%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Sharpe Ratio', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value">1.67</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Max Drawdown', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value negative">-8.45%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Win Rate', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value">67.5%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label"><?php esc_html_e('Avg Hold Time', 'retail-trade-scanner'); ?></span>
                        <span class="metric-value">45 days</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const period = this.dataset.period;
            updatePerformanceChart(period);
        });
    });
    
    // Allocation toggle
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            updateAllocationView(view);
        });
    });
    
    function updatePerformanceChart(period) {
        console.log('Updating performance chart for period:', period);
        // In real implementation, this would update the chart with new data
    }
    
    function updateAllocationView(view) {
        console.log('Updating allocation view:', view);
        // In real implementation, this would switch between sector and position allocation
    }
    
    // Auto-refresh portfolio data every minute
    setInterval(function() {
        console.log('Auto-refreshing portfolio data...');
        // In real implementation, this would update prices and P/L
    }, 60000);
});
</script>

<style>
/* Portfolio-specific styles */
.portfolio-overview {
    margin-bottom: var(--spacing-2xl);
}

.portfolio-content {
    margin-bottom: var(--spacing-2xl);
}

.chart-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.timeframe-buttons {
    display: flex;
    gap: var(--spacing-xs);
}

.timeframe-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.timeframe-btn:hover,
.timeframe-btn.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

.allocation-toggle {
    display: flex;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.toggle-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: transparent;
    border: none;
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.toggle-btn.active {
    background: var(--primary-500);
    color: white;
}

.allocation-legend {
    margin-top: var(--spacing-lg);
}

.legend-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.legend-item:last-child {
    border-bottom: none;
}

.legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: var(--spacing-sm);
}

.legend-label {
    flex: 1;
    font-size: var(--text-sm);
}

.legend-value {
    font-size: var(--text-sm);
    font-weight: 600;
}

.transactions-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.transaction-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
}

.transaction-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.type-badge {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
}

.type-badge.buy {
    background: var(--success-light);
    color: var(--success);
}

.type-badge.sell {
    background: var(--danger-light);
    color: var(--danger);
}

.transaction-details {
    flex: 1;
    min-width: 0;
}

.transaction-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xs);
}

.transaction-header .symbol {
    font-weight: 700;
    font-size: var(--text-sm);
}

.transaction-header .shares {
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.transaction-meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.transaction-amount {
    font-weight: 600;
    font-size: var(--text-sm);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
}

.metric-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-lg);
}

.metric-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.metric-value {
    font-weight: 600;
    font-size: var(--text-sm);
}

.metric-value.positive {
    color: var(--success);
}

.metric-value.negative {
    color: var(--danger);
}

.positions-actions {
    display: flex;
    gap: var(--spacing-sm);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
    .portfolio-content {
        grid-template-columns: 1fr;
    }
    
    .portfolio-chart,
    .portfolio-allocation {
        grid-column: span 1;
    }
    
    .portfolio-transactions,
    .portfolio-metrics {
        grid-column: span 1;
    }
}

@media (max-width: 640px) {
    .portfolio-overview {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .timeframe-buttons {
        flex-wrap: wrap;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .transaction-item {
        flex-direction: column;
        align-items: flex-start;
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .legend-item {
    border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .metric-label,
[data-theme="dark"] .transaction-meta {
    color: var(--gray-400);
<?php get_template_part('template-parts/layout/main-shell-end'); ?>

}
</style>

<?php get_footer(); ?>