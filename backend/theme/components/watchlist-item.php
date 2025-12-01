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