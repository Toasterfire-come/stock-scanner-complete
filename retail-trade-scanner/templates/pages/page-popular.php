<?php
/**
 * Template Name: Popular
 * 
 * Popular stocks lists - trending, most active, gainers, and losers
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Popular Stocks', 'retail-trade-scanner'),
    'page_description' => __('Explore trending stocks, top gainers, losers, and most active securities', 'retail-trade-scanner'),
    'page_class' => 'popular-page',
    'header_actions' => array(
        array(
            'text' => __('Export List', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'download'
        ),
        array(
            'text' => __('Create Watchlist', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'watchlist'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

// Sample data for different categories
$stock_lists = array(
    'trending' => array(
        array('symbol' => 'NVDA', 'name' => 'NVIDIA Corp', 'price' => '456.78', 'change' => '+3.67%', 'volume' => '35.7M', 'type' => 'positive'),
        array('symbol' => 'TSLA', 'name' => 'Tesla Inc', 'price' => '245.67', 'change' => '+2.45%', 'volume' => '28.9M', 'type' => 'positive'),
        array('symbol' => 'AAPL', 'name' => 'Apple Inc', 'price' => '182.34', 'change' => '+1.23%', 'volume' => '52.3M', 'type' => 'positive'),
        array('symbol' => 'AMZN', 'name' => 'Amazon.com', 'price' => '134.89', 'change' => '+0.89%', 'volume' => '41.2M', 'type' => 'positive'),
        array('symbol' => 'GOOGL', 'name' => 'Alphabet Inc', 'price' => '128.76', 'change' => '+0.56%', 'volume' => '25.8M', 'type' => 'positive')
    ),
    'gainers' => array(
        array('symbol' => 'AMD', 'name' => 'Advanced Micro Devices', 'price' => '112.45', 'change' => '+8.92%', 'volume' => '89.3M', 'type' => 'positive'),
        array('symbol' => 'NVDA', 'name' => 'NVIDIA Corp', 'price' => '456.78', 'change' => '+7.23%', 'volume' => '65.7M', 'type' => 'positive'),
        array('symbol' => 'PLTR', 'name' => 'Palantir Technologies', 'price' => '18.67', 'change' => '+6.45%', 'volume' => '73.2M', 'type' => 'positive'),
        array('symbol' => 'RBLX', 'name' => 'Roblox Corporation', 'price' => '39.84', 'change' => '+5.78%', 'volume' => '45.6M', 'type' => 'positive'),
        array('symbol' => 'ZM', 'name' => 'Zoom Video Communications', 'price' => '67.23', 'change' => '+5.12%', 'volume' => '32.1M', 'type' => 'positive')
    ),
    'losers' => array(
        array('symbol' => 'NFLX', 'name' => 'Netflix Inc', 'price' => '423.56', 'change' => '-4.23%', 'volume' => '18.9M', 'type' => 'negative'),
        array('symbol' => 'PYPL', 'name' => 'PayPal Holdings', 'price' => '58.92', 'change' => '-3.78%', 'volume' => '24.5M', 'type' => 'negative'),
        array('symbol' => 'SPOT', 'name' => 'Spotify Technology', 'price' => '156.78', 'change' => '-3.45%', 'volume' => '12.3M', 'type' => 'negative'),
        array('symbol' => 'SHOP', 'name' => 'Shopify Inc', 'price' => '67.89', 'change' => '-2.98%', 'volume' => '15.7M', 'type' => 'negative'),
        array('symbol' => 'UBER', 'name' => 'Uber Technologies', 'price' => '42.56', 'change' => '-2.67%', 'volume' => '28.4M', 'type' => 'negative')
    ),
    'active' => array(
        array('symbol' => 'SPY', 'name' => 'SPDR S&P 500 ETF Trust', 'price' => '423.78', 'change' => '+0.12%', 'volume' => '156.2M', 'type' => 'positive'),
        array('symbol' => 'QQQ', 'name' => 'Invesco QQQ Trust', 'price' => '367.89', 'change' => '+0.34%', 'volume' => '98.7M', 'type' => 'positive'),
        array('symbol' => 'TSLA', 'name' => 'Tesla Inc', 'price' => '245.67', 'change' => '-1.23%', 'volume' => '87.3M', 'type' => 'negative'),
        array('symbol' => 'AAPL', 'name' => 'Apple Inc', 'price' => '182.34', 'change' => '+0.89%', 'volume' => '76.5M', 'type' => 'positive'),
        array('symbol' => 'AMD', 'name' => 'Advanced Micro Devices', 'price' => '112.45', 'change' => '+2.45%', 'volume' => '65.8M', 'type' => 'positive')
    )
);
?>

<div class="popular-layout">
    <!-- Market Summary Cards -->
    <section class="market-summary">
        <div class="summary-grid grid grid-4">
            <div class="summary-card glass-card animate-scale-in">
                <div class="summary-header">
                    <?php echo rts_get_icon('trending-up', ['width' => '24', 'height' => '24', 'class' => 'summary-icon text-success']); ?>
                    <h3><?php esc_html_e('Market Trend', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="summary-content">
                    <div class="summary-value text-success">Bullish</div>
                    <div class="summary-meta"><?php esc_html_e('67% of stocks up today', 'retail-trade-scanner'); ?></div>
                </div>
            </div>

            <div class="summary-card glass-card animate-scale-in">
                <div class="summary-header">
                    <?php echo rts_get_icon('activity', ['width' => '24', 'height' => '24', 'class' => 'summary-icon text-primary']); ?>
                    <h3><?php esc_html_e('Volume', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="summary-content">
                    <div class="summary-value">2.8B</div>
                    <div class="summary-meta"><?php esc_html_e('Total shares traded', 'retail-trade-scanner'); ?></div>
                </div>
            </div>

            <div class="summary-card glass-card animate-scale-in">
                <div class="summary-header">
                    <?php echo rts_get_icon('trending-up', ['width' => '24', 'height' => '24', 'class' => 'summary-icon text-success']); ?>
                    <h3><?php esc_html_e('Top Gainer', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="summary-content">
                    <div class="summary-value">AMD</div>
                    <div class="summary-meta text-success">+8.92%</div>
                </div>
            </div>

            <div class="summary-card glass-card animate-scale-in">
                <div class="summary-header">
                    <?php echo rts_get_icon('trending-down', ['width' => '24', 'height' => '24', 'class' => 'summary-icon text-danger']); ?>
                    <h3><?php esc_html_e('Top Loser', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="summary-content">
                    <div class="summary-value">NFLX</div>
                    <div class="summary-meta text-danger">-4.23%</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Popular Lists Navigation -->
    <section class="popular-navigation">
        <div class="nav-container card glass-card">
            <nav class="popular-tabs">
                <button class="popular-tab active" data-category="trending">
                    <?php echo rts_get_icon('trending-up', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Trending', 'retail-trade-scanner'); ?></span>
                    <span class="tab-badge">5</span>
                </button>
                <button class="popular-tab" data-category="gainers">
                    <?php echo rts_get_icon('arrow-up', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Top Gainers', 'retail-trade-scanner'); ?></span>
                    <span class="tab-badge">5</span>
                </button>
                <button class="popular-tab" data-category="losers">
                    <?php echo rts_get_icon('arrow-down', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Top Losers', 'retail-trade-scanner'); ?></span>
                    <span class="tab-badge">5</span>
                </button>
                <button class="popular-tab" data-category="active">
                    <?php echo rts_get_icon('activity', ['width' => '20', 'height' => '20']); ?>
                    <span><?php esc_html_e('Most Active', 'retail-trade-scanner'); ?></span>
                    <span class="tab-badge">5</span>
                </button>
            </nav>
            
            <div class="list-controls">
                <div class="view-options">
                    <button class="view-btn active" data-view="list">
                        <?php echo rts_get_icon('list', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <button class="view-btn" data-view="grid">
                        <?php echo rts_get_icon('grid', ['width' => '16', 'height' => '16']); ?>
                    </button>
                </div>
                
                <div class="refresh-control">
                    <button class="btn btn-ghost btn-sm auto-refresh-btn">
                        <?php echo rts_get_icon('refresh', ['width' => '16', 'height' => '16']); ?>
                        <span><?php esc_html_e('Auto Refresh', 'retail-trade-scanner'); ?></span>
                    </button>
                    <span class="last-updated"><?php esc_html_e('Updated 2 min ago', 'retail-trade-scanner'); ?></span>
                </div>
            </div>
        </div>
    </section>

    <!-- Stock Lists -->
    <section class="stock-lists">
        <?php foreach ($stock_lists as $category => $stocks) : ?>
            <div class="stock-list-container <?php echo $category === 'trending' ? 'active' : 'hidden'; ?>" data-category="<?php echo esc_attr($category); ?>">
                <div class="stock-list-header">
                    <h3 class="list-title">
                        <?php
                        $titles = array(
                            'trending' => __('Trending Stocks', 'retail-trade-scanner'),
                            'gainers' => __('Top Gainers', 'retail-trade-scanner'),
                            'losers' => __('Top Losers', 'retail-trade-scanner'),
                            'active' => __('Most Active', 'retail-trade-scanner')
                        );
                        echo esc_html($titles[$category]);
                        ?>
                    </h3>
                    <div class="list-actions">
                        <select class="form-select time-filter">
                            <option value="1d"><?php esc_html_e('Today', 'retail-trade-scanner'); ?></option>
                            <option value="1w"><?php esc_html_e('This Week', 'retail-trade-scanner'); ?></option>
                            <option value="1m"><?php esc_html_e('This Month', 'retail-trade-scanner'); ?></option>
                        </select>
                        <button class="btn btn-outline btn-sm export-list">
                            <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                            <span><?php esc_html_e('Export', 'retail-trade-scanner'); ?></span>
                        </button>
                    </div>
                </div>

                <!-- List View -->
                <div class="stock-list list-view">
                    <?php foreach ($stocks as $index => $stock) : ?>
                        <div class="stock-item card animate-fade-up" style="animation-delay: <?php echo $index * 0.1; ?>s;">
                            <div class="stock-rank">
                                <span class="rank-number"><?php echo $index + 1; ?></span>
                            </div>
                            
                            <div class="stock-identity">
                                <div class="stock-symbol">
                                    <a href="<?php echo esc_url(home_url("/search/?symbol={$stock['symbol']}")); ?>" class="symbol-link">
                                        <?php echo esc_html($stock['symbol']); ?>
                                    </a>
                                </div>
                                <div class="stock-name"><?php echo esc_html($stock['name']); ?></div>
                            </div>
                            
                            <div class="stock-price">
                                <span class="price-value">$<?php echo esc_html($stock['price']); ?></span>
                            </div>
                            
                            <div class="stock-change">
                                <span class="change-value <?php echo $stock['type'] === 'positive' ? 'text-success' : 'text-danger'; ?>">
                                    <?php echo esc_html($stock['change']); ?>
                                </span>
                            </div>
                            
                            <div class="stock-volume">
                                <span class="volume-value"><?php echo esc_html($stock['volume']); ?></span>
                                <span class="volume-label"><?php esc_html_e('Vol', 'retail-trade-scanner'); ?></span>
                            </div>
                            
                            <div class="stock-chart">
                                <div class="mini-sparkline" data-symbol="<?php echo esc_attr($stock['symbol']); ?>">
                                    <!-- Mini chart placeholder -->
                                    <svg width="80" height="30" class="sparkline-svg">
                                        <path class="sparkline-path <?php echo $stock['type'] === 'positive' ? 'positive' : 'negative'; ?>" 
                                              d="M 0 15 Q 20 <?php echo $stock['type'] === 'positive' ? '5' : '25'; ?> 40 10 T 80 <?php echo $stock['type'] === 'positive' ? '8' : '22'; ?>" 
                                              fill="none" 
                                              stroke-width="2"/>
                                    </svg>
                                </div>
                            </div>
                            
                            <div class="stock-actions">
                                <button class="btn btn-ghost btn-icon add-to-watchlist" 
                                        data-symbol="<?php echo esc_attr($stock['symbol']); ?>"
                                        title="<?php esc_attr_e('Add to Watchlist', 'retail-trade-scanner'); ?>">
                                    <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                                </button>
                                <button class="btn btn-ghost btn-icon set-alert" 
                                        data-symbol="<?php echo esc_attr($stock['symbol']); ?>"
                                        title="<?php esc_attr_e('Set Alert', 'retail-trade-scanner'); ?>">
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                </button>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>

                <!-- Grid View -->
                <div class="stock-grid grid-view hidden">
                    <?php foreach ($stocks as $stock) : ?>
                        <div class="stock-card glass-card">
                            <div class="stock-card-header">
                                <div class="stock-symbol">
                                    <a href="<?php echo esc_url(home_url("/search/?symbol={$stock['symbol']}")); ?>" class="symbol-link">
                                        <?php echo esc_html($stock['symbol']); ?>
                                    </a>
                                </div>
                                <div class="card-actions">
                                    <button class="btn btn-ghost btn-icon add-to-watchlist" data-symbol="<?php echo esc_attr($stock['symbol']); ?>">
                                        <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                                    </button>
                                </div>
                            </div>
                            
                            <div class="stock-card-content">
                                <div class="stock-name"><?php echo esc_html($stock['name']); ?></div>
                                <div class="stock-price">
                                    <span class="price-value">$<?php echo esc_html($stock['price']); ?></span>
                                    <span class="change-value <?php echo $stock['type'] === 'positive' ? 'text-success' : 'text-danger'; ?>">
                                        <?php echo esc_html($stock['change']); ?>
                                    </span>
                                </div>
                                <div class="stock-volume">
                                    <span><?php esc_html_e('Volume:', 'retail-trade-scanner'); ?> <?php echo esc_html($stock['volume']); ?></span>
                                </div>
                            </div>
                            
                            <div class="stock-card-chart">
                                <div class="mini-sparkline" data-symbol="<?php echo esc_attr($stock['symbol']); ?>">
                                    <svg width="100%" height="40" class="sparkline-svg">
                                        <path class="sparkline-path <?php echo $stock['type'] === 'positive' ? 'positive' : 'negative'; ?>" 
                                              d="M 0 20 Q 25 <?php echo $stock['type'] === 'positive' ? '8' : '32'; ?> 50 15 T 100 <?php echo $stock['type'] === 'positive' ? '10' : '30'; ?>" 
                                              fill="none" 
                                              stroke-width="2"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endforeach; ?>
    </section>

    <!-- Market Heatmap -->
    <section class="market-heatmap">
        <div class="heatmap-container card glass-card">
            <div class="heatmap-header">
                <h3><?php esc_html_e('Market Heatmap', 'retail-trade-scanner'); ?></h3>
                <div class="heatmap-controls">
                    <select class="form-select heatmap-metric">
                        <option value="change"><?php esc_html_e('Price Change %', 'retail-trade-scanner'); ?></option>
                        <option value="volume"><?php esc_html_e('Volume', 'retail-trade-scanner'); ?></option>
                        <option value="market_cap"><?php esc_html_e('Market Cap', 'retail-trade-scanner'); ?></option>
                    </select>
                </div>
            </div>
            
            <div class="heatmap-grid">
                <?php
                $heatmap_stocks = array_slice($stock_lists['trending'], 0, 15);
                foreach ($heatmap_stocks as $stock) :
                    $intensity = abs(floatval(str_replace(['%', '+'], '', $stock['change'])));
                    $opacity = min(0.8, $intensity / 10);
                ?>
                    <div class="heatmap-cell <?php echo $stock['type']; ?>" 
                         style="opacity: <?php echo $opacity; ?>"
                         data-symbol="<?php echo esc_attr($stock['symbol']); ?>"
                         title="<?php echo esc_attr("{$stock['symbol']}: {$stock['change']}"); ?>">
                        <div class="cell-symbol"><?php echo esc_html($stock['symbol']); ?></div>
                        <div class="cell-change"><?php echo esc_html($stock['change']); ?></div>
                    </div>
                <?php endforeach; ?>
            </div>
            
            <div class="heatmap-legend">
                <div class="legend-item">
                    <div class="legend-color negative"></div>
                    <span><?php esc_html_e('Negative', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="legend-scale">
                    <span><?php esc_html_e('0%', 'retail-trade-scanner'); ?></span>
                    <div class="scale-gradient"></div>
                    <span><?php esc_html_e('10%+', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="legend-item">
                    <div class="legend-color positive"></div>
                    <span><?php esc_html_e('Positive', 'retail-trade-scanner'); ?></span>
                </div>
            </div>
        </div>
    </section>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Popular page functionality
    const popularTabs = document.querySelectorAll('.popular-tab');
    const stockListContainers = document.querySelectorAll('.stock-list-container');
    const viewBtns = document.querySelectorAll('.view-btn');
    const autoRefreshBtn = document.querySelector('.auto-refresh-btn');
    
    let autoRefreshInterval = null;
    
    // Tab switching
    popularTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // Update active tab
            popularTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding list
            stockListContainers.forEach(container => {
                if (container.dataset.category === category) {
                    container.classList.remove('hidden');
                    container.classList.add('active');
                } else {
                    container.classList.add('hidden');
                    container.classList.remove('active');
                }
            });
        });
    });
    
    // View toggle
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            toggleView(view);
        });
    });
    
    // Auto refresh toggle
    if (autoRefreshBtn) {
        autoRefreshBtn.addEventListener('click', function() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                this.classList.remove('active');
                RTS.showInfo('Auto-refresh disabled');
            } else {
                autoRefreshInterval = setInterval(refreshData, 30000);
                this.classList.add('active');
                RTS.showSuccess('Auto-refresh enabled (30s)');
            }
        });
    }
    
    // Add to watchlist functionality
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-watchlist')) {
            const btn = e.target.closest('.add-to-watchlist');
            const symbol = btn.dataset.symbol;
            addToWatchlist(symbol, btn);
        }
    });
    
    // Set alert functionality
    document.addEventListener('click', function(e) {
        if (e.target.closest('.set-alert')) {
            const btn = e.target.closest('.set-alert');
            const symbol = btn.dataset.symbol;
            setAlert(symbol);
        }
    });
    
    // Heatmap interactions
    document.querySelectorAll('.heatmap-cell').forEach(cell => {
        cell.addEventListener('click', function() {
            const symbol = this.dataset.symbol;
            window.location.href = `/search/?symbol=${symbol}`;
        });
    });
    
    function toggleView(view) {
        const activeContainer = document.querySelector('.stock-list-container.active');
        if (!activeContainer) return;
        
        const listView = activeContainer.querySelector('.list-view');
        const gridView = activeContainer.querySelector('.grid-view');
        
        if (view === 'grid') {
            listView.classList.add('hidden');
            gridView.classList.remove('hidden');
        } else {
            gridView.classList.add('hidden');
            listView.classList.remove('hidden');
        }
    }
    
    function addToWatchlist(symbol, btn) {
        // Add loading state
        btn.classList.add('loading');
        
        // Simulate API call
        setTimeout(() => {
            btn.classList.remove('loading');
            btn.classList.add('added');
            btn.innerHTML = RTS.components.getIcon('check', 16);
            btn.title = 'Added to watchlist';
            
            RTS.showSuccess(`${symbol} added to watchlist`);
            
            // Reset after 2 seconds
            setTimeout(() => {
                btn.classList.remove('added');
                btn.innerHTML = RTS.components.getIcon('plus', 16);
                btn.title = 'Add to watchlist';
            }, 2000);
        }, 1000);
    }
    
    function setAlert(symbol) {
        // Open alert modal or redirect to alerts page
        RTS.showInfo(`Setting alert for ${symbol}`);
        // In real implementation, this would open a modal or redirect
    }
    
    function refreshData() {
        // Simulate data refresh
        const lastUpdated = document.querySelector('.last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = 'Updated just now';
        }
        
        // Update stock prices with small random changes
        document.querySelectorAll('.price-value').forEach(priceEl => {
            const currentPrice = parseFloat(priceEl.textContent.replace('$', ''));
            const change = (Math.random() - 0.5) * 2; // Random change between -1 and +1
            const newPrice = (currentPrice + change).toFixed(2);
            priceEl.textContent = `$${newPrice}`;
        });
        
        console.log('Data refreshed');
    }
    
    // Initialize sparklines
    initSparklines();
    
    function initSparklines() {
        document.querySelectorAll('.mini-sparkline').forEach(sparkline => {
            const svg = sparkline.querySelector('svg');
            if (svg) {
                // Add hover effects or animations here
                svg.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.1)';
                });
                
                svg.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                });
            }
        });
    }
});
</script>

<style>
/* Popular page specific styles */
.popular-layout {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

/* Market Summary */
.summary-grid {
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.summary-card {
    padding: var(--spacing-xl);
    text-align: center;
    transition: all var(--transition-normal) var(--easing-standard);
}

.summary-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.summary-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.summary-icon {
    width: 32px;
    height: 32px;
}

.summary-header h3 {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.summary-value {
    font-size: var(--text-2xl);
    font-weight: 700;
    margin-bottom: var(--spacing-xs);
}

.summary-meta {
    font-size: var(--text-sm);
    color: var(--gray-500);
}

/* Popular Navigation */
.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg) var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
}

.popular-tabs {
    display: flex;
    gap: var(--spacing-md);
}

.popular-tab {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-lg);
    background: transparent;
    border: 2px solid transparent;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    font-weight: 500;
    color: var(--gray-600);
}

.popular-tab:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--gray-800);
}

.popular-tab.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

.tab-badge {
    background: rgba(255, 255, 255, 0.2);
    color: inherit;
    padding: 2px 8px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 600;
}

.popular-tab.active .tab-badge {
    background: rgba(255, 255, 255, 0.3);
}

.list-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.view-options {
    display: flex;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.view-btn {
    padding: var(--spacing-sm);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.view-btn.active {
    background: var(--primary-500);
    color: white;
}

.refresh-control {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.auto-refresh-btn.active {
    background: var(--success);
    color: white;
}

.last-updated {
    font-size: var(--text-sm);
    color: var(--gray-500);
}

/* Stock Lists */
.stock-list-container {
    margin-bottom: var(--spacing-xl);
}

.stock-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.list-title {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-800);
    margin: 0;
}

.list-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

/* List View */
.stock-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.stock-item {
    display: grid;
    grid-template-columns: 40px 1fr auto auto auto 100px auto;
    align-items: center;
    gap: var(--spacing-lg);
    padding: var(--spacing-lg);
    transition: all var(--transition-fast) var(--easing-standard);
    border-radius: var(--radius-lg);
}

.stock-item:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateX(4px);
}

.stock-rank {
    display: flex;
    align-items: center;
    justify-content: center;
}

.rank-number {
    font-weight: 700;
    color: var(--gray-500);
    font-size: var(--text-lg);
}

.stock-identity {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.stock-symbol .symbol-link {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--primary-600);
    text-decoration: none;
    transition: color var(--transition-fast);
}

.stock-symbol .symbol-link:hover {
    color: var(--primary-700);
}

.stock-name {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.stock-price .price-value {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-900);
}

.stock-change .change-value {
    font-weight: 600;
    font-size: var(--text-base);
}

.stock-volume {
    text-align: right;
}

.volume-value {
    font-weight: 600;
    color: var(--gray-700);
}

.volume-label {
    font-size: var(--text-xs);
    color: var(--gray-500);
    display: block;
}

.stock-chart {
    display: flex;
    justify-content: center;
}

.mini-sparkline svg {
    transition: transform var(--transition-fast);
}

.sparkline-path {
    stroke-width: 2;
    fill: none;
}

.sparkline-path.positive {
    stroke: var(--success);
}

.sparkline-path.negative {
    stroke: var(--danger);
}

.stock-actions {
    display: flex;
    gap: var(--spacing-xs);
}

/* Grid View */
.stock-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-lg);
}

.stock-card {
    padding: var(--spacing-lg);
    transition: all var(--transition-normal) var(--easing-standard);
}

.stock-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.stock-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.stock-card .stock-symbol .symbol-link {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--primary-600);
    text-decoration: none;
}

.stock-card-content {
    margin-bottom: var(--spacing-md);
}

.stock-card .stock-name {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin-bottom: var(--spacing-sm);
}

.stock-card .stock-price {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
}

.stock-card .price-value {
    font-size: var(--text-lg);
    font-weight: 600;
}

.stock-card .stock-volume {
    font-size: var(--text-sm);
    color: var(--gray-500);
}

.stock-card-chart {
    height: 40px;
}

/* Market Heatmap */
.heatmap-container {
    padding: var(--spacing-xl);
}

.heatmap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.heatmap-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.heatmap-cell {
    aspect-ratio: 1;
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    min-height: 80px;
}

.heatmap-cell:hover {
    transform: scale(1.05);
    z-index: 1;
}

.heatmap-cell.positive {
    background: var(--success);
    color: white;
}

.heatmap-cell.negative {
    background: var(--danger);
    color: white;
}

.cell-symbol {
    font-weight: 700;
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-xs);
}

.cell-change {
    font-size: var(--text-xs);
    font-weight: 600;
}

.heatmap-legend {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-lg);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
}

.legend-color {
    width: 16px;
    height: 16px;
    border-radius: var(--radius-sm);
}

.legend-color.positive {
    background: var(--success);
}

.legend-color.negative {
    background: var(--danger);
}

.legend-scale {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.scale-gradient {
    width: 100px;
    height: 8px;
    background: linear-gradient(to right, var(--danger), var(--gray-300), var(--success));
    border-radius: var(--radius-full);
}

/* Loading states */
.add-to-watchlist.loading {
    animation: pulse 1s infinite;
}

.add-to-watchlist.added {
    background: var(--success);
    color: white;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .nav-container {
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .popular-tabs {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .stock-item {
        grid-template-columns: 30px 1fr auto;
        gap: var(--spacing-md);
    }
    
    .stock-chart,
    .stock-volume {
        display: none;
    }
    
    .summary-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .summary-grid {
        grid-template-columns: 1fr;
    }
    
    .popular-tabs {
        flex-direction: column;
        width: 100%;
    }
    
    .popular-tab {
        justify-content: center;
    }
    
    .heatmap-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
</style>

<?php get_footer(); ?>