<?php
/**
 * Template Name: Scanner
 * 
 * Real-time stock scanner with filters, results table, and chart panel
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Scanner filter categories
$filter_categories = array(
    'price' => array(
        'label' => __('Price', 'retail-trade-scanner'),
        'filters' => array(
            'price_min' => __('Minimum Price', 'retail-trade-scanner'),
            'price_max' => __('Maximum Price', 'retail-trade-scanner'),
            'price_change' => __('Price Change %', 'retail-trade-scanner')
        )
    ),
    'volume' => array(
        'label' => __('Volume', 'retail-trade-scanner'),
        'filters' => array(
            'volume_min' => __('Min Volume', 'retail-trade-scanner'),
            'avg_volume' => __('Avg Volume Ratio', 'retail-trade-scanner'),
            'volume_spike' => __('Volume Spike', 'retail-trade-scanner')
        )
    ),
    'technical' => array(
        'label' => __('Technical', 'retail-trade-scanner'),
        'filters' => array(
            'rsi' => __('RSI Range', 'retail-trade-scanner'),
            'macd' => __('MACD Signal', 'retail-trade-scanner'),
            'sma_cross' => __('SMA Crossover', 'retail-trade-scanner')
        )
    ),
    'fundamentals' => array(
        'label' => __('Fundamentals', 'retail-trade-scanner'),
        'filters' => array(
            'market_cap' => __('Market Cap', 'retail-trade-scanner'),
            'pe_ratio' => __('P/E Ratio', 'retail-trade-scanner'),
            'dividend_yield' => __('Dividend Yield', 'retail-trade-scanner')
        )
    )
);

// Sample scan results - in real implementation this would come from API
$scan_results = array(
    array(
        'symbol' => 'AAPL',
        'company' => 'Apple Inc.',
        'price' => '182.34',
        'change' => '+2.45%',
        'volume' => '52.3M',
        'market_cap' => '2.84T',
        'pe_ratio' => '28.5',
        'rsi' => '67.2',
        'type' => 'positive'
    ),
    array(
        'symbol' => 'TSLA',
        'company' => 'Tesla Inc.',
        'price' => '245.67',
        'change' => '-1.28%',
        'volume' => '28.9M',
        'market_cap' => '781.2B',
        'pe_ratio' => '45.3',
        'rsi' => '34.8',
        'type' => 'negative'
    ),
    array(
        'symbol' => 'NVDA',
        'company' => 'NVIDIA Corporation',
        'price' => '456.78',
        'change' => '+3.67%',
        'volume' => '35.7M',
        'market_cap' => '1.12T',
        'pe_ratio' => '52.1',
        'rsi' => '72.5',
        'type' => 'positive'
    )
);

$layout_args = array(
    'page_title' => __('Stock Scanner', 'retail-trade-scanner'),
    'page_description' => __('Real-time stock screening with advanced filters and technical indicators', 'retail-trade-scanner'),
    'page_class' => 'scanner-page',
    'header_actions' => array(
        array(
            'text' => __('Save Scan', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'save'
        ),
        array(
            'text' => __('Export Results', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'download'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="scanner-layout grid grid-cols-12 gap-lg">
    <!-- Filter Sidebar -->
    <div class="scanner-filters col-span-3">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Filters', 'retail-trade-scanner'); ?></h3>
                <div class="filter-actions">
                    <button class="btn btn-ghost btn-sm clear-filters">
                        <?php esc_html_e('Clear', 'retail-trade-scanner'); ?>
                    </button>
                    <button class="btn btn-primary btn-sm run-scan">
                        <?php echo rts_get_icon('search', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Scan', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>
            
            <div class="card-body">
                <form class="scanner-filter-form" id="scanner-filters">
                    <?php foreach ($filter_categories as $category_key => $category) : ?>
                        <div class="filter-group">
                            <h4 class="filter-group-title"><?php echo esc_html($category['label']); ?></h4>
                            
                            <?php foreach ($category['filters'] as $filter_key => $filter_label) : ?>
                                <div class="filter-field">
                                    <label class="form-label" for="<?php echo esc_attr($filter_key); ?>">
                                        <?php echo esc_html($filter_label); ?>
                                    </label>
                                    
                                    <?php if (strpos($filter_key, 'min') !== false || strpos($filter_key, 'max') !== false) : ?>
                                        <input type="number" 
                                               class="form-input" 
                                               id="<?php echo esc_attr($filter_key); ?>"
                                               name="<?php echo esc_attr($filter_key); ?>"
                                               placeholder="<?php echo esc_attr($filter_label); ?>">
                                    <?php elseif (strpos($filter_key, 'ratio') !== false || strpos($filter_key, 'yield') !== false) : ?>
                                        <div class="range-input">
                                            <input type="range" 
                                                   class="form-range" 
                                                   id="<?php echo esc_attr($filter_key); ?>"
                                                   name="<?php echo esc_attr($filter_key); ?>"
                                                   min="0" max="100" value="50">
                                            <span class="range-value">50</span>
                                        </div>
                                    <?php else : ?>
                                        <select class="form-select" id="<?php echo esc_attr($filter_key); ?>" name="<?php echo esc_attr($filter_key); ?>">
                                            <option value=""><?php esc_html_e('Any', 'retail-trade-scanner'); ?></option>
                                            <option value="bullish"><?php esc_html_e('Bullish', 'retail-trade-scanner'); ?></option>
                                            <option value="bearish"><?php esc_html_e('Bearish', 'retail-trade-scanner'); ?></option>
                                        </select>
                                    <?php endif; ?>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    <?php endforeach; ?>
                    
                    <!-- Preset Filters -->
                    <div class="filter-group">
                        <h4 class="filter-group-title"><?php esc_html_e('Quick Presets', 'retail-trade-scanner'); ?></h4>
                        <div class="filter-presets">
                            <button type="button" class="preset-btn" data-preset="momentum">
                                <?php esc_html_e('High Momentum', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="preset-btn" data-preset="value">
                                <?php esc_html_e('Value Stocks', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="preset-btn" data-preset="breakout">
                                <?php esc_html_e('Breakout Pattern', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="preset-btn" data-preset="dividend">
                                <?php esc_html_e('High Dividend', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Results Area -->
    <div class="scanner-results col-span-9">
        <!-- Results Header -->
        <div class="results-header flex items-center justify-between mb-lg">
            <div class="results-info">
                <h3><?php esc_html_e('Scan Results', 'retail-trade-scanner'); ?></h3>
                <p class="text-sm text-muted">
                    <span class="results-count">3</span> <?php esc_html_e('stocks found', 'retail-trade-scanner'); ?> • 
                    <?php esc_html_e('Last updated:', 'retail-trade-scanner'); ?> <span class="last-updated">2:45 PM</span>
                </p>
            </div>
            
            <div class="results-actions flex items-center gap-md">
                <button class="btn btn-ghost btn-sm auto-refresh-toggle">
                    <?php echo rts_get_icon('refresh', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Auto Refresh', 'retail-trade-scanner'); ?>
                </button>
                
                <div class="view-toggle">
                    <button class="view-btn active" data-view="table">
                        <?php echo rts_get_icon('table', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <button class="view-btn" data-view="grid">
                        <?php echo rts_get_icon('grid', ['width' => '16', 'height' => '16']); ?>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Results Table -->
        <div class="results-table-container card">
            <?php
            get_template_part('template-parts/components/table', null, array(
                'id' => 'scanner-results-table',
                'headers' => array(
                    'symbol' => __('Symbol', 'retail-trade-scanner'),
                    'price' => __('Price', 'retail-trade-scanner'),
                    'change' => __('Change', 'retail-trade-scanner'),
                    'volume' => __('Volume', 'retail-trade-scanner'),
                    'market_cap' => __('Market Cap', 'retail-trade-scanner'),
                    'pe_ratio' => __('P/E', 'retail-trade-scanner'),
                    'rsi' => __('RSI', 'retail-trade-scanner'),
                    'actions' => __('Actions', 'retail-trade-scanner')
                ),
                'data' => $scan_results,
                'sortable' => true,
                'selectable' => true,
                'pagination' => true
            ));
            ?>
        </div>
        
        <!-- Chart Panel -->
        <div class="chart-panel card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Chart Analysis', 'retail-trade-scanner'); ?></h3>
                <div class="chart-controls">
                    <select class="chart-symbol-select form-select">
                        <option value=""><?php esc_html_e('Select Symbol', 'retail-trade-scanner'); ?></option>
                        <?php foreach ($scan_results as $stock) : ?>
                            <option value="<?php echo esc_attr($stock['symbol']); ?>">
                                <?php echo esc_html($stock['symbol']); ?> - <?php echo esc_html($stock['company']); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    
                    <div class="timeframe-buttons">
                        <button class="timeframe-btn active" data-timeframe="1D">1D</button>
                        <button class="timeframe-btn" data-timeframe="1W">1W</button>
                        <button class="timeframe-btn" data-timeframe="1M">1M</button>
                        <button class="timeframe-btn" data-timeframe="3M">3M</button>
                    </div>
                </div>
            </div>
            
            <div class="card-body">
                <?php
                get_template_part('template-parts/components/chart-shell', null, array(
                    'title' => '',
                    'type' => 'candlestick',
                    'height' => '400px',
                    'loading' => false,
                    'show_controls' => true,
                    'variant' => 'trading'
                ));
                ?>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Scanner functionality
    const scannerForm = document.getElementById('scanner-filters');
    const runScanBtn = document.querySelector('.run-scan');
    const clearFiltersBtn = document.querySelector('.clear-filters');
    const autoRefreshToggle = document.querySelector('.auto-refresh-toggle');
    
    let autoRefreshInterval = null;
    
    // Run scan functionality
    if (runScanBtn) {
        runScanBtn.addEventListener('click', function() {
            runScan();
        });
    }
    
    // Clear filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            scannerForm.reset();
            updateResults();
        });
    }
    
    // Auto refresh toggle
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('click', function() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                this.classList.remove('active');
                RTS.showInfo('Auto-refresh disabled');
            } else {
                autoRefreshInterval = setInterval(runScan, 30000); // 30 seconds
                this.classList.add('active');
                RTS.showSuccess('Auto-refresh enabled (30s)');
            }
        });
    }
    
    // Preset filters
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const preset = this.dataset.preset;
            applyPreset(preset);
        });
    });
    
    // Range input updates
    document.querySelectorAll('.form-range').forEach(range => {
        range.addEventListener('input', function() {
            const valueSpan = this.parentElement.querySelector('.range-value');
            if (valueSpan) {
                valueSpan.textContent = this.value;
            }
        });
    });
    
    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            toggleResultsView(view);
        });
    });
    
    // Chart symbol selection
    const chartSymbolSelect = document.querySelector('.chart-symbol-select');
    if (chartSymbolSelect) {
        chartSymbolSelect.addEventListener('change', function() {
            const symbol = this.value;
            if (symbol) {
                loadChart(symbol);
            }
        });
    }
    
    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const timeframe = this.dataset.timeframe;
            const symbol = chartSymbolSelect ? chartSymbolSelect.value : null;
            if (symbol) {
                loadChart(symbol, timeframe);
            }
        });
    });
    
    function runScan() {
        runScanBtn.classList.add('loading');
        runScanBtn.disabled = true;
        
        // Get form data
        const formData = new FormData(scannerForm);
        const filters = Object.fromEntries(formData.entries());
        
        // Simulate API call
        setTimeout(() => {
            updateResults(filters);
            runScanBtn.classList.remove('loading');
            runScanBtn.disabled = false;
            
            // Update last updated time
            const lastUpdatedElement = document.querySelector('.last-updated');
            if (lastUpdatedElement) {
                lastUpdatedElement.textContent = new Date().toLocaleTimeString();
            }
            
            RTS.showSuccess('Scan completed successfully!');
        }, 2000);
    }
    
    function applyPreset(preset) {
        // Reset form first
        scannerForm.reset();
        
        // Apply preset values
        const presets = {
            momentum: {
                'price_change': '5',
                'volume_min': '1000000',
                'rsi': 'bullish'
            },
            value: {
                'pe_ratio': '15',
                'market_cap': '1000000000',
                'dividend_yield': '3'
            },
            breakout: {
                'price_change': '2',
                'volume_spike': 'bullish',
                'sma_cross': 'bullish'
            },
            dividend: {
                'dividend_yield': '4',
                'pe_ratio': '20'
            }
        };
        
        const presetData = presets[preset];
        if (presetData) {
            Object.entries(presetData).forEach(([key, value]) => {
                const input = scannerForm.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = value;
                    
                    // Update range display
                    if (input.type === 'range') {
                        const valueSpan = input.parentElement.querySelector('.range-value');
                        if (valueSpan) {
                            valueSpan.textContent = value;
                        }
                    }
                }
            });
            
            // Run scan with preset
            runScan();
        }
    }
    
    function updateResults(filters = {}) {
        // Update results count and table
        // In real implementation, this would make API call with filters
        console.log('Updating results with filters:', filters);
    }
    
    function toggleResultsView(view) {
        const tableContainer = document.querySelector('.results-table-container');
        if (view === 'grid') {
            tableContainer.classList.add('grid-view');
        } else {
            tableContainer.classList.remove('grid-view');
        }
    }
    
    function loadChart(symbol, timeframe = '1D') {
        console.log(`Loading chart for ${symbol} with timeframe ${timeframe}`);
        // In real implementation, this would load chart data
    }
});
</script>

<style>
/* Scanner-specific styles */
.scanner-layout {
    margin-bottom: var(--spacing-2xl);
}

.scanner-filters {
    position: sticky;
    top: calc(var(--header-height, 72px) + var(--spacing-lg));
    align-self: flex-start;
    max-height: calc(100vh - var(--header-height, 72px) - var(--spacing-2xl));
    overflow-y: auto;
}

.filter-group {
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-group:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.filter-group-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
    margin: 0 0 var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.filter-field {
    margin-bottom: var(--spacing-md);
}

.filter-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.range-input {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.form-range {
    flex: 1;
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    outline: none;
    -webkit-appearance: none;
}

.form-range::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    background: var(--primary-500);
    border-radius: 50%;
    cursor: pointer;
}

.range-value {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--primary-600);
    min-width: 30px;
    text-align: center;
}

.filter-presets {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.preset-btn {
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    color: var(--gray-700);
    font-size: var(--text-sm);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.preset-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--primary-600);
}

.results-header {
    padding: var(--spacing-lg) 0;
}

.results-info h3 {
    margin: 0 0 var(--spacing-xs);
}

.results-actions {
    align-items: center;
}

.view-toggle {
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

.auto-refresh-toggle.active {
    background: var(--success);
    color: white;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .scanner-layout {
        grid-template-columns: 1fr;
    }
    
    .scanner-filters {
        position: static;
        max-height: none;
        margin-bottom: var(--spacing-lg);
    }
    
    .filter-presets {
        flex-direction: row;
        flex-wrap: wrap;
    }
    
    .results-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md);
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .filter-group-title {
    color: var(--gray-300);
}

[data-theme="dark"] .preset-btn {
    color: var(--gray-300);
}
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>