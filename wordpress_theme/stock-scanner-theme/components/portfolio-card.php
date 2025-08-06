<?php
/**
 * Portfolio Card Component
 * Reusable component for displaying portfolio information
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Set default values
$portfolio = $args['portfolio'] ?? null;
$show_actions = $args['show_actions'] ?? true;
$card_size = $args['size'] ?? 'default'; // default, compact, detailed
$layout = $args['layout'] ?? 'vertical'; // vertical, horizontal

if (!$portfolio) {
    return;
}

// Calculate performance indicators
$return_class = $portfolio['total_return'] >= 0 ? 'positive' : 'negative';
$return_icon = $portfolio['total_return'] >= 0 ? 'arrow-up' : 'arrow-down';

// Format values
$total_value = number_format($portfolio['total_value'], 2);
$total_return = number_format($portfolio['total_return'], 2);
$return_percent = number_format($portfolio['total_return_percent'], 2);

?>

<div class="portfolio-card size-<?php echo esc_attr($card_size); ?> layout-<?php echo esc_attr($layout); ?>" 
     data-portfolio-id="<?php echo esc_attr($portfolio['id']); ?>"
     data-return="<?php echo $portfolio['total_return'] >= 0 ? 'positive' : 'negative'; ?>">
     
    <!-- Portfolio Header -->
    <div class="portfolio-header">
        <div class="portfolio-title-section">
            <h5 class="portfolio-name">
                <?php echo esc_html($portfolio['name']); ?>
            </h5>
            
            <?php if (!empty($portfolio['description']) && $card_size !== 'compact'): ?>
                <p class="portfolio-description">
                    <?php echo esc_html($portfolio['description']); ?>
                </p>
            <?php endif; ?>
            
            <div class="portfolio-meta">
                <?php if ($portfolio['is_public']): ?>
                    <span class="badge bg-success">
                        <i class="fas fa-globe"></i> Public
                    </span>
                <?php else: ?>
                    <span class="badge bg-secondary">
                        <i class="fas fa-lock"></i> Private
                    </span>
                <?php endif; ?>
                
                <?php if (!empty($portfolio['holdings_count'])): ?>
                    <span class="holdings-count">
                        <i class="fas fa-layer-group"></i> 
                        <?php echo esc_html($portfolio['holdings_count']); ?> holdings
                    </span>
                <?php endif; ?>
                
                <span class="created-date">
                    <i class="fas fa-calendar"></i>
                    <?php echo esc_html(date('M j, Y', strtotime($portfolio['created_at']))); ?>
                </span>
            </div>
        </div>
        
        <?php if ($show_actions): ?>
            <div class="portfolio-actions">
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            type="button" 
                            data-bs-toggle="dropdown" 
                            aria-expanded="false">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li>
                            <a class="dropdown-item" href="#" onclick="portfolioManager.viewPortfolio(<?php echo $portfolio['id']; ?>)">
                                <i class="fas fa-eye"></i> View Details
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="#" onclick="portfolioManager.editPortfolio(<?php echo $portfolio['id']; ?>)">
                                <i class="fas fa-edit"></i> Edit Portfolio
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="#" onclick="portfolioManager.addHoldingModal(<?php echo $portfolio['id']; ?>)">
                                <i class="fas fa-plus"></i> Add Holding
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item" href="#" onclick="portfolioManager.exportPortfolio(<?php echo $portfolio['id']; ?>, 'csv')">
                                <i class="fas fa-download"></i> Export CSV
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="#" onclick="portfolioManager.sharePortfolio(<?php echo $portfolio['id']; ?>)">
                                <i class="fas fa-share"></i> Share Portfolio
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item text-danger" href="#" onclick="portfolioManager.deletePortfolio(<?php echo $portfolio['id']; ?>)">
                                <i class="fas fa-trash"></i> Delete Portfolio
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Portfolio Stats -->
    <div class="portfolio-stats">
        <div class="row">
            <div class="col-md-4">
                <div class="stat-item">
                    <label>Total Value</label>
                    <div class="stat-value total-value">
                        $<?php echo $total_value; ?>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="stat-item">
                    <label>Total Return</label>
                    <div class="stat-value return-value <?php echo $return_class; ?>">
                        <i class="fas fa-<?php echo $return_icon; ?>"></i>
                        $<?php echo $total_return; ?>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="stat-item">
                    <label>Return %</label>
                    <div class="stat-value return-percent <?php echo $return_class; ?>">
                        <i class="fas fa-<?php echo $return_icon; ?>"></i>
                        <?php echo $return_percent; ?>%
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Portfolio Performance Chart (for detailed view) -->
    <?php if ($card_size === 'detailed' && !empty($portfolio['performance_data'])): ?>
        <div class="portfolio-chart">
            <canvas id="portfolio-chart-<?php echo $portfolio['id']; ?>" 
                    data-portfolio-id="<?php echo $portfolio['id']; ?>"
                    height="200"></canvas>
        </div>
    <?php endif; ?>
    
    <!-- Recent Holdings (for detailed view) -->
    <?php if ($card_size === 'detailed' && !empty($portfolio['recent_holdings'])): ?>
        <div class="recent-holdings">
            <h6>Recent Holdings</h6>
            <div class="holdings-list">
                <?php foreach ($portfolio['recent_holdings'] as $holding): ?>
                    <div class="holding-item">
                        <div class="holding-info">
                            <strong class="ticker"><?php echo esc_html($holding['ticker']); ?></strong>
                            <span class="shares"><?php echo esc_html($holding['shares']); ?> shares</span>
                        </div>
                        <div class="holding-value <?php echo $holding['gain_loss'] >= 0 ? 'positive' : 'negative'; ?>">
                            $<?php echo number_format($holding['current_value'], 2); ?>
                            <small>(<?php echo number_format($holding['gain_loss_percent'], 2); ?>%)</small>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    <?php endif; ?>
    
    <!-- Social Stats (for public portfolios) -->
    <?php if ($portfolio['is_public'] && ($portfolio['followers_count'] > 0 || $portfolio['likes_count'] > 0)): ?>
        <div class="social-stats">
            <?php if ($portfolio['followers_count'] > 0): ?>
                <span class="followers">
                    <i class="fas fa-users"></i>
                    <?php echo number_format($portfolio['followers_count']); ?> followers
                </span>
            <?php endif; ?>
            
            <?php if ($portfolio['likes_count'] > 0): ?>
                <span class="likes">
                    <i class="fas fa-heart"></i>
                    <?php echo number_format($portfolio['likes_count']); ?> likes
                </span>
            <?php endif; ?>
        </div>
    <?php endif; ?>
    
    <!-- Action Footer (for compact view) -->
    <?php if ($card_size === 'compact' && $show_actions): ?>
        <div class="portfolio-footer">
            <div class="quick-actions">
                <button class="btn btn-sm btn-outline-primary" 
                        onclick="portfolioManager.viewPortfolio(<?php echo $portfolio['id']; ?>)">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-sm btn-outline-success" 
                        onclick="portfolioManager.addHoldingModal(<?php echo $portfolio['id']; ?>)">
                    <i class="fas fa-plus"></i> Add
                </button>
            </div>
        </div>
    <?php endif; ?>
</div>

<!-- Component Styles -->
<style>
.portfolio-card {
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
    transition: all var(--transition-normal, 0.3s ease-in-out);
    box-shadow: var(--shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
    height: 100%;
    display: flex;
    flex-direction: column;
}

.portfolio-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));
    border-color: var(--primary-color, #2563eb);
}

.portfolio-card[data-return="positive"] {
    border-left: 4px solid var(--success-color, #059669);
}

.portfolio-card[data-return="negative"] {
    border-left: 4px solid var(--danger-color, #dc2626);
}

/* Layout variations */
.portfolio-card.layout-horizontal {
    flex-direction: row;
    align-items: center;
}

.portfolio-card.layout-horizontal .portfolio-header {
    flex: 1;
    margin-bottom: 0;
    margin-right: var(--spacing-lg, 1.5rem);
}

.portfolio-card.layout-horizontal .portfolio-stats {
    flex: 2;
}

/* Size variations */
.portfolio-card.size-compact {
    padding: var(--spacing-md, 1rem);
}

.portfolio-card.size-compact .portfolio-name {
    font-size: 1rem;
}

.portfolio-card.size-detailed {
    padding: var(--spacing-xl, 2rem);
}

/* Header styling */
.portfolio-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.portfolio-title-section {
    flex: 1;
}

.portfolio-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
    margin: 0 0 var(--spacing-sm, 0.5rem) 0;
}

.portfolio-description {
    color: var(--text-secondary, #64748b);
    font-size: 0.875rem;
    margin: 0 0 var(--spacing-md, 1rem) 0;
    line-height: 1.5;
}

.portfolio-meta {
    display: flex;
    gap: var(--spacing-sm, 0.5rem);
    align-items: center;
    flex-wrap: wrap;
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
}

.portfolio-meta .badge {
    font-size: 0.65rem;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}

.portfolio-meta span {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
}

/* Stats styling */
.portfolio-stats {
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.stat-item {
    text-align: center;
    padding: var(--spacing-sm, 0.5rem);
}

.stat-item label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
    font-weight: 500;
    margin-bottom: var(--spacing-xs, 0.25rem);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-value {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs, 0.25rem);
}

.stat-value.positive {
    color: var(--success-color, #059669);
}

.stat-value.negative {
    color: var(--danger-color, #dc2626);
}

/* Holdings list */
.recent-holdings {
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.recent-holdings h6 {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: var(--spacing-md, 1rem);
    color: var(--text-primary, #1e293b);
}

.holding-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm, 0.5rem) 0;
    border-bottom: 1px solid var(--border-muted, #f1f5f9);
}

.holding-item:last-child {
    border-bottom: none;
}

.holding-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
}

.holding-info .ticker {
    font-weight: 600;
    color: var(--primary-color, #2563eb);
}

.holding-info .shares {
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
}

.holding-value {
    text-align: right;
    font-weight: 600;
}

.holding-value small {
    display: block;
    font-size: 0.75rem;
    font-weight: 500;
}

/* Social stats */
.social-stats {
    display: flex;
    gap: var(--spacing-md, 1rem);
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
    padding-top: var(--spacing-md, 1rem);
    border-top: 1px solid var(--border-muted, #f1f5f9);
}

.social-stats span {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
}

/* Footer actions */
.portfolio-footer {
    margin-top: auto;
    padding-top: var(--spacing-md, 1rem);
    border-top: 1px solid var(--border-muted, #f1f5f9);
}

.quick-actions {
    display: flex;
    gap: var(--spacing-sm, 0.5rem);
    justify-content: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .portfolio-card.layout-horizontal {
        flex-direction: column;
    }
    
    .portfolio-card.layout-horizontal .portfolio-header {
        margin-right: 0;
        margin-bottom: var(--spacing-lg, 1.5rem);
    }
    
    .portfolio-meta {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-xs, 0.25rem);
    }
    
    .stat-item {
        padding: var(--spacing-xs, 0.25rem);
    }
    
    .stat-value {
        font-size: 1rem;
    }
}
</style>

<?php
// Initialize chart if detailed view and performance data exists
if ($card_size === 'detailed' && !empty($portfolio['performance_data'])): ?>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('portfolio-chart-<?php echo $portfolio['id']; ?>');
    if (chartCanvas && window.Chart) {
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: <?php echo json_encode($portfolio['performance_data']['labels']); ?>,
                datasets: [{
                    label: 'Portfolio Value',
                    data: <?php echo json_encode($portfolio['performance_data']['values']); ?>,
                    borderColor: '<?php echo $return_class === "positive" ? "#059669" : "#dc2626"; ?>',
                    backgroundColor: '<?php echo $return_class === "positive" ? "#05966920" : "#dc262620"; ?>',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Value: $' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
});
</script>
<?php endif; ?>