<?php
/**
 * Watchlist Item Component
 * Reusable component for displaying individual watchlist entries
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Set default values
$item = $args['item'] ?? null;
$show_actions = $args['show_actions'] ?? true;
$layout = $args['layout'] ?? 'default'; // default, compact, detailed

if (!$item) {
    return;
}

// Calculate performance indicators
$performance = $item['current_price'] - $item['added_price'];
$performance_percent = $item['added_price'] > 0 ? ($performance / $item['added_price']) * 100 : 0;
$performance_class = $performance >= 0 ? 'positive' : 'negative';
$performance_icon = $performance >= 0 ? 'arrow-up' : 'arrow-down';

// Alert status indicators
$price_alert_class = '';
if ($item['target_price'] && $item['current_price'] >= $item['target_price']) {
    $price_alert_class = 'target-reached';
} elseif ($item['stop_loss'] && $item['current_price'] <= $item['stop_loss']) {
    $price_alert_class = 'stop-loss-triggered';
}

?>

<div class="watchlist-item layout-<?php echo esc_attr($layout); ?> <?php echo esc_attr($price_alert_class); ?>" 
     data-item-id="<?php echo esc_attr($item['id']); ?>"
     data-ticker="<?php echo esc_attr($item['ticker']); ?>"
     data-performance="<?php echo $performance >= 0 ? 'positive' : 'negative'; ?>">
     
    <!-- Stock Information -->
    <div class="stock-info">
        <div class="stock-symbol">
            <h6 class="ticker"><?php echo esc_html($item['ticker']); ?></h6>
            <?php if (!empty($item['stock_name']) && $layout !== 'compact'): ?>
                <p class="company-name"><?php echo esc_html($item['stock_name']); ?></p>
            <?php endif; ?>
        </div>
        
        <?php if ($layout === 'detailed' && !empty($item['notes'])): ?>
            <div class="item-notes">
                <small class="text-muted">
                    <i class="fas fa-sticky-note"></i>
                    <?php echo esc_html($item['notes']); ?>
                </small>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Price Information -->
    <div class="price-info">
        <div class="current-price">
            <span class="price-label">Current</span>
            <span class="price-value">$<?php echo number_format($item['current_price'], 2); ?></span>
        </div>
        
        <?php if ($layout !== 'compact'): ?>
            <div class="added-price">
                <span class="price-label">Added at</span>
                <span class="price-value">$<?php echo number_format($item['added_price'], 2); ?></span>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Performance -->
    <div class="performance-info">
        <div class="performance-change <?php echo $performance_class; ?>">
            <i class="fas fa-<?php echo $performance_icon; ?>"></i>
            <span class="change-amount">$<?php echo number_format(abs($performance), 2); ?></span>
            <span class="change-percent">(<?php echo number_format($performance_percent, 2); ?>%)</span>
        </div>
        
        <?php if ($layout === 'detailed'): ?>
            <div class="performance-since">
                <small class="text-muted">
                    Since <?php echo date('M j', strtotime($item['added_at'])); ?>
                </small>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Alerts & Targets -->
    <?php if ($layout !== 'compact' && ($item['target_price'] || $item['stop_loss'])): ?>
        <div class="alerts-info">
            <?php if ($item['target_price']): ?>
                <div class="target-price <?php echo $item['current_price'] >= $item['target_price'] ? 'reached' : ''; ?>">
                    <i class="fas fa-bullseye"></i>
                    <span class="alert-label">Target</span>
                    <span class="alert-value">$<?php echo number_format($item['target_price'], 2); ?></span>
                    <?php if ($item['current_price'] >= $item['target_price']): ?>
                        <i class="fas fa-check-circle text-success"></i>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($item['stop_loss']): ?>
                <div class="stop-loss <?php echo $item['current_price'] <= $item['stop_loss'] ? 'triggered' : ''; ?>">
                    <i class="fas fa-shield-alt"></i>
                    <span class="alert-label">Stop</span>
                    <span class="alert-value">$<?php echo number_format($item['stop_loss'], 2); ?></span>
                    <?php if ($item['current_price'] <= $item['stop_loss']): ?>
                        <i class="fas fa-exclamation-triangle text-warning"></i>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>
    
    <!-- Alert Indicators -->
    <div class="alert-indicators">
        <?php if ($item['price_alert_enabled']): ?>
            <span class="alert-badge price-alerts" title="Price alerts enabled">
                <i class="fas fa-bell"></i>
            </span>
        <?php endif; ?>
        
        <?php if ($item['news_alert_enabled']): ?>
            <span class="alert-badge news-alerts" title="News alerts enabled">
                <i class="fas fa-newspaper"></i>
            </span>
        <?php endif; ?>
        
        <?php if ($price_alert_class === 'target-reached'): ?>
            <span class="alert-badge target-reached" title="Target price reached">
                <i class="fas fa-flag"></i>
            </span>
        <?php elseif ($price_alert_class === 'stop-loss-triggered'): ?>
            <span class="alert-badge stop-triggered" title="Stop loss triggered">
                <i class="fas fa-exclamation"></i>
            </span>
        <?php endif; ?>
    </div>
    
    <!-- Actions -->
    <?php if ($show_actions): ?>
        <div class="item-actions">
            <div class="dropdown">
                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                        type="button" 
                        data-bs-toggle="dropdown" 
                        aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li>
                        <a class="dropdown-item" href="#" onclick="watchlistManager.editWatchlistItem(<?php echo $item['id']; ?>)">
                            <i class="fas fa-edit"></i> Edit Item
                        </a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="#" onclick="watchlistManager.updateTargetPrice(<?php echo $item['id']; ?>)">
                            <i class="fas fa-bullseye"></i> Set Target
                        </a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="#" onclick="watchlistManager.updateStopLoss(<?php echo $item['id']; ?>)">
                            <i class="fas fa-shield-alt"></i> Set Stop Loss
                        </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                        <a class="dropdown-item" href="#" onclick="watchlistManager.addToPortfolio('<?php echo $item['ticker']; ?>')">
                            <i class="fas fa-plus"></i> Add to Portfolio
                        </a>
                    </li>
                    <li>
                        <a class="dropdown-item" href="#" onclick="window.open('/stock-detail/<?php echo strtolower($item['ticker']); ?>/', '_blank')">
                            <i class="fas fa-external-link-alt"></i> View Details
                        </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                        <a class="dropdown-item text-danger" href="#" onclick="watchlistManager.removeFromWatchlist(<?php echo $item['id']; ?>)">
                            <i class="fas fa-trash"></i> Remove
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    <?php endif; ?>
</div>

<!-- Component Styles -->
<style>
.watchlist-item {
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-md, 0.375rem);
    padding: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-sm, 0.5rem);
    display: grid;
    grid-template-columns: 2fr 1.5fr 1.5fr 1fr auto auto;
    gap: var(--spacing-md, 1rem);
    align-items: center;
    transition: all var(--transition-fast, 0.15s ease-in-out);
    position: relative;
}

.watchlist-item:hover {
    background: var(--bg-secondary, #f8fafc);
    border-color: var(--primary-color, #2563eb);
    box-shadow: var(--shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
}

.watchlist-item[data-performance="positive"] {
    border-left: 3px solid var(--success-color, #059669);
}

.watchlist-item[data-performance="negative"] {
    border-left: 3px solid var(--danger-color, #dc2626);
}

.watchlist-item.target-reached {
    background: rgba(5, 150, 105, 0.05);
    border-color: var(--success-color, #059669);
}

.watchlist-item.stop-loss-triggered {
    background: rgba(220, 38, 38, 0.05);
    border-color: var(--danger-color, #dc2626);
}

/* Compact layout */
.watchlist-item.layout-compact {
    grid-template-columns: 1.5fr 1fr 1fr auto auto;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
}

/* Detailed layout */
.watchlist-item.layout-detailed {
    grid-template-columns: 2.5fr 1.5fr 1.5fr 2fr auto auto;
    padding: var(--spacing-lg, 1.5rem);
}

/* Stock Info */
.stock-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
}

.ticker {
    font-size: 1rem;
    font-weight: 700;
    color: var(--primary-color, #2563eb);
    margin: 0;
    letter-spacing: 0.5px;
}

.company-name {
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
    margin: 0;
    line-height: 1.3;
}

.item-notes {
    margin-top: var(--spacing-xs, 0.25rem);
}

.item-notes small {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
}

/* Price Info */
.price-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
}

.price-label {
    font-size: 0.65rem;
    color: var(--text-secondary, #64748b);
    text-transform: uppercase;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.price-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
}

/* Performance Info */
.performance-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
    align-items: flex-end;
}

.performance-change {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
    font-weight: 600;
}

.performance-change.positive {
    color: var(--success-color, #059669);
}

.performance-change.negative {
    color: var(--danger-color, #dc2626);
}

.change-amount {
    font-size: 0.875rem;
}

.change-percent {
    font-size: 0.75rem;
    opacity: 0.9;
}

.performance-since {
    text-align: right;
}

/* Alerts Info */
.alerts-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
    font-size: 0.75rem;
}

.target-price,
.stop-loss {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    background: var(--bg-muted, #f1f5f9);
}

.target-price.reached {
    background: rgba(5, 150, 105, 0.1);
    color: var(--success-color, #059669);
}

.stop-loss.triggered {
    background: rgba(220, 38, 38, 0.1);
    color: var(--danger-color, #dc2626);
}

.alert-label {
    font-weight: 500;
    min-width: 30px;
}

.alert-value {
    font-weight: 600;
}

/* Alert Indicators */
.alert-indicators {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs, 0.25rem);
    align-items: center;
}

.alert-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 0.65rem;
    color: white;
}

.alert-badge.price-alerts {
    background: var(--info-color, #0284c7);
}

.alert-badge.news-alerts {
    background: var(--warning-color, #d97706);
}

.alert-badge.target-reached {
    background: var(--success-color, #059669);
    animation: pulse 2s infinite;
}

.alert-badge.stop-triggered {
    background: var(--danger-color, #dc2626);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* Item Actions */
.item-actions {
    justify-self: end;
}

/* Responsive Design */
@media (max-width: 992px) {
    .watchlist-item {
        grid-template-columns: 1fr;
        gap: var(--spacing-sm, 0.5rem);
    }
    
    .watchlist-item.layout-compact,
    .watchlist-item.layout-detailed {
        grid-template-columns: 1fr;
    }
    
    .performance-info {
        align-items: flex-start;
    }
    
    .alerts-info {
        flex-direction: row;
        flex-wrap: wrap;
    }
    
    .alert-indicators {
        flex-direction: row;
        align-items: flex-start;
    }
}

@media (max-width: 768px) {
    .watchlist-item {
        padding: var(--spacing-sm, 0.5rem);
    }
    
    .ticker {
        font-size: 0.875rem;
    }
    
    .price-value {
        font-size: 0.75rem;
    }
    
    .change-amount {
        font-size: 0.75rem;
    }
}
</style>