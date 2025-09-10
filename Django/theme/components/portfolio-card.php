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