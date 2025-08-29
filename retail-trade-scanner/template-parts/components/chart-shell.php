<?php
/**
 * Chart Shell Component Template Part
 *
 * @package RetailTradeScanner
 */

$args = wp_parse_args($args, array(
    'title' => '',
    'type' => 'line', // line, bar, candlestick, pie, heatmap
    'height' => '300px',
    'loading' => false,
    'show_controls' => true,
    'variant' => 'default', // default, trading, performance, minimal
    'data_endpoint' => '',
    'custom_class' => ''
));

extract($args);

$chart_id = 'chart-' . uniqid();
$chart_classes = array('chart-shell', 'chart-' . $variant);

if ($custom_class) {
    $chart_classes[] = $custom_class;
}

// Chart configuration based on type
$chart_config = array(
    'line' => array(
        'icon' => 'trending-up',
        'description' => __('Line Chart', 'retail-trade-scanner')
    ),
    'bar' => array(
        'icon' => 'bar-chart',
        'description' => __('Bar Chart', 'retail-trade-scanner')
    ),
    'candlestick' => array(
        'icon' => 'activity',
        'description' => __('Candlestick Chart', 'retail-trade-scanner')
    ),
    'pie' => array(
        'icon' => 'pie-chart',
        'description' => __('Pie Chart', 'retail-trade-scanner')
    ),
    'heatmap' => array(
        'icon' => 'grid',
        'description' => __('Heatmap', 'retail-trade-scanner')
    )
);

$config = $chart_config[$type] ?? $chart_config['line'];
?>

<div class="<?php echo esc_attr(implode(' ', $chart_classes)); ?>" id="<?php echo esc_attr($chart_id); ?>">
    
    <?php if ($title || $show_controls) : ?>
        <div class="chart-header">
            <?php if ($title) : ?>
                <div class="chart-title-section">
                    <h4 class="chart-title"><?php echo esc_html($title); ?></h4>
                    <span class="chart-type" title="<?php echo esc_attr($config['description']); ?>">
                        <?php echo rts_get_icon($config['icon'], ['width' => '16', 'height' => '16']); ?>
                    </span>
                </div>
            <?php endif; ?>
            
            <?php if ($show_controls) : ?>
                <div class="chart-controls">
                    <?php if ($variant === 'trading') : ?>
                        <!-- Trading-specific controls -->
                        <div class="chart-indicators">
                            <button class="indicator-btn" data-indicator="sma" title="<?php esc_attr_e('Simple Moving Average', 'retail-trade-scanner'); ?>">
                                SMA
                            </button>
                            <button class="indicator-btn" data-indicator="rsi" title="<?php esc_attr_e('Relative Strength Index', 'retail-trade-scanner'); ?>">
                                RSI
                            </button>
                            <button class="indicator-btn" data-indicator="macd" title="<?php esc_attr_e('MACD', 'retail-trade-scanner'); ?>">
                                MACD
                            </button>
                            <button class="indicator-btn" data-indicator="bollinger" title="<?php esc_attr_e('Bollinger Bands', 'retail-trade-scanner'); ?>">
                                BB
                            </button>
                        </div>
                    <?php endif; ?>
                    
                    <div class="chart-actions">
                        <button class="chart-action-btn" data-action="fullscreen" title="<?php esc_attr_e('Fullscreen', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('maximize', ['width' => '16', 'height' => '16']); ?>
                        </button>
                        
                        <button class="chart-action-btn" data-action="download" title="<?php esc_attr_e('Download Chart', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                        </button>
                        
                        <div class="chart-settings-dropdown">
                            <button class="chart-action-btn dropdown-toggle" data-action="settings" title="<?php esc_attr_e('Chart Settings', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('settings', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            
                            <div class="dropdown-menu hidden">
                                <div class="dropdown-item">
                                    <label class="dropdown-label">
                                        <input type="checkbox" class="chart-setting" data-setting="grid" checked>
                                        <?php esc_html_e('Show Grid', 'retail-trade-scanner'); ?>
                                    </label>
                                </div>
                                <div class="dropdown-item">
                                    <label class="dropdown-label">
                                        <input type="checkbox" class="chart-setting" data-setting="crosshair" checked>
                                        <?php esc_html_e('Crosshair', 'retail-trade-scanner'); ?>
                                    </label>
                                </div>
                                <div class="dropdown-item">
                                    <label class="dropdown-label">
                                        <input type="checkbox" class="chart-setting" data-setting="volume">
                                        <?php esc_html_e('Volume', 'retail-trade-scanner'); ?>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>
    
    <div class="chart-container" style="height: <?php echo esc_attr($height); ?>;">
        
        <?php if ($loading) : ?>
            <div class="chart-loading">
                <div class="chart-loading-content">
                    <div class="loading-spinner"></div>
                    <p><?php esc_html_e('Loading chart data...', 'retail-trade-scanner'); ?></p>
                </div>
            </div>
            
        <?php else : ?>
            <!-- Chart placeholder/canvas -->
            <div class="chart-canvas" 
                 data-chart-type="<?php echo esc_attr($type); ?>"
                 data-chart-variant="<?php echo esc_attr($variant); ?>"
                 data-endpoint="<?php echo esc_attr($data_endpoint); ?>">
                
                <?php if ($type === 'heatmap') : ?>
                    <!-- Heatmap placeholder -->
                    <div class="heatmap-grid">
                        <?php for ($i = 0; $i < 50; $i++) : ?>
                            <div class="heatmap-cell" data-value="<?php echo rand(-5, 5); ?>"></div>
                        <?php endfor; ?>
                    </div>
                    
                <?php else : ?>
                    <!-- Generic chart placeholder -->
                    <div class="chart-placeholder">
                        <div class="chart-placeholder-content">
                            <?php echo rts_get_icon($config['icon'], ['width' => '64', 'height' => '64', 'class' => 'chart-placeholder-icon']); ?>
                            <p><?php echo esc_html($config['description']); ?></p>
                            <small><?php esc_html_e('Chart will render here', 'retail-trade-scanner'); ?></small>
                        </div>
                    </div>
                <?php endif; ?>
            </div>
        <?php endif; ?>
        
        <!-- Chart tooltip (hidden by default) -->
        <div class="chart-tooltip hidden" id="<?php echo esc_attr($chart_id . '-tooltip'); ?>">
            <div class="tooltip-content"></div>
        </div>
    </div>
    
    <?php if ($variant === 'trading' && $show_controls) : ?>
        <!-- Trading chart legend -->
        <div class="chart-legend">
            <div class="legend-items">
                <div class="legend-item">
                    <span class="legend-color" style="background: var(--success);"></span>
                    <span class="legend-label"><?php esc_html_e('Price', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="legend-item hidden" data-indicator="volume">
                    <span class="legend-color" style="background: var(--info);"></span>
                    <span class="legend-label"><?php esc_html_e('Volume', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="legend-item hidden" data-indicator="sma">
                    <span class="legend-color" style="background: var(--warning);"></span>
                    <span class="legend-label"><?php esc_html_e('SMA(20)', 'retail-trade-scanner'); ?></span>
                </div>
            </div>
        </div>
    <?php endif; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeChart('<?php echo $chart_id; ?>');
});

function initializeChart(chartId) {
    const chartShell = document.getElementById(chartId);
    if (!chartShell) return;
    
    const chartCanvas = chartShell.querySelector('.chart-canvas');
    const chartType = chartCanvas.dataset.chartType;
    const chartVariant = chartCanvas.dataset.chartVariant;
    
    // Initialize chart controls
    initChartControls(chartShell);
    
    // Load chart based on type
    switch (chartType) {
        case 'line':
            initLineChart(chartCanvas);
            break;
        case 'candlestick':
            initCandlestickChart(chartCanvas);
            break;
        case 'pie':
            initPieChart(chartCanvas);
            break;
        case 'heatmap':
            initHeatmap(chartCanvas);
            break;
        default:
            console.log('Chart type not implemented:', chartType);
    }
}

function initChartControls(chartShell) {
    // Indicator buttons
    chartShell.querySelectorAll('.indicator-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('active');
            const indicator = this.dataset.indicator;
            toggleIndicator(indicator, this.classList.contains('active'));
        });
    });
    
    // Chart action buttons
    chartShell.querySelectorAll('.chart-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            handleChartAction(action, chartShell);
        });
    });
    
    // Settings dropdown
    const dropdownToggle = chartShell.querySelector('.dropdown-toggle');
    const dropdownMenu = chartShell.querySelector('.dropdown-menu');
    
    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('hidden');
        });
        
        document.addEventListener('click', function() {
            dropdownMenu.classList.add('hidden');
        });
        
        // Chart settings
        chartShell.querySelectorAll('.chart-setting').forEach(setting => {
            setting.addEventListener('change', function() {
                const settingName = this.dataset.setting;
                const isEnabled = this.checked;
                applyChartSetting(settingName, isEnabled, chartShell);
            });
        });
    }
}

function initLineChart(canvas) {
    // Replace placeholder with actual chart
    // In a real implementation, this would use a charting library like Chart.js, D3, or TradingView
    console.log('Initializing line chart');
}

function initCandlestickChart(canvas) {
    console.log('Initializing candlestick chart');
}

function initPieChart(canvas) {
    console.log('Initializing pie chart');
}

function initHeatmap(canvas) {
    const cells = canvas.querySelectorAll('.heatmap-cell');
    
    cells.forEach(cell => {
        const value = parseFloat(cell.dataset.value);
        const intensity = Math.abs(value) / 5; // Normalize to 0-1
        
        if (value > 0) {
            cell.style.backgroundColor = `rgba(34, 197, 94, ${intensity})`;
        } else if (value < 0) {
            cell.style.backgroundColor = `rgba(239, 68, 68, ${intensity})`;
        } else {
            cell.style.backgroundColor = 'var(--gray-100)';
        }
        
        cell.textContent = value > 0 ? `+${value.toFixed(1)}%` : `${value.toFixed(1)}%`;
        
        // Add hover tooltip
        cell.addEventListener('mouseenter', function(e) {
            showTooltip(e, `Value: ${value.toFixed(2)}%`);
        });
        
        cell.addEventListener('mouseleave', hideTooltip);
    });
}

function toggleIndicator(indicator, isActive) {
    console.log(`Toggling ${indicator} indicator:`, isActive);
    
    // Show/hide legend item
    const legendItem = document.querySelector(`[data-indicator="${indicator}"]`);
    if (legendItem) {
        legendItem.classList.toggle('hidden', !isActive);
    }
}

function handleChartAction(action, chartShell) {
    switch (action) {
        case 'fullscreen':
            toggleFullscreen(chartShell);
            break;
        case 'download':
            downloadChart(chartShell);
            break;
        case 'settings':
            // Handled by dropdown toggle
            break;
    }
}

function applyChartSetting(setting, isEnabled, chartShell) {
    console.log(`Applying chart setting ${setting}:`, isEnabled);
    
    // Apply setting to chart
    const chartCanvas = chartShell.querySelector('.chart-canvas');
    chartCanvas.classList.toggle(`setting-${setting}`, isEnabled);
}

function toggleFullscreen(chartShell) {
    if (chartShell.classList.contains('fullscreen')) {
        chartShell.classList.remove('fullscreen');
        document.body.style.overflow = '';
    } else {
        chartShell.classList.add('fullscreen');
        document.body.style.overflow = 'hidden';
    }
}

function downloadChart(chartShell) {
    console.log('Downloading chart...');
    // In real implementation, this would export the chart as PNG/SVG
    RTS.showSuccess('Chart download started');
}

function showTooltip(event, content) {
    const tooltip = event.target.closest('.chart-shell').querySelector('.chart-tooltip');
    if (tooltip) {
        tooltip.querySelector('.tooltip-content').textContent = content;
        tooltip.classList.remove('hidden');
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
    }
}

function hideTooltip(event) {
    const tooltip = event.target.closest('.chart-shell').querySelector('.chart-tooltip');
    if (tooltip) {
        tooltip.classList.add('hidden');
    }
}
</script>

<style>
/* Chart Shell Component Styles */
.chart-shell {
    position: relative;
    background: var(--surface-raised);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.chart-shell.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: var(--z-modal);
    border-radius: 0;
}

.chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.chart-title-section {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.chart-title {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0;
}

.chart-type {
    color: var(--gray-500);
}

.chart-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.chart-indicators {
    display: flex;
    gap: var(--spacing-xs);
}

.indicator-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: transparent;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.indicator-btn:hover,
.indicator-btn.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

.chart-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.chart-action-btn {
    padding: var(--spacing-sm);
    background: transparent;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.chart-action-btn:hover {
    background: var(--gray-100);
}

.chart-settings-dropdown {
    position: relative;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    z-index: var(--z-dropdown);
    min-width: 180px;
    margin-top: var(--spacing-xs);
}

.dropdown-item {
    padding: var(--spacing-sm) var(--spacing-md);
    border-bottom: 1px solid var(--gray-100);
}

.dropdown-item:last-child {
    border-bottom: none;
}

.dropdown-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
    cursor: pointer;
}

.chart-container {
    position: relative;
    overflow: hidden;
}

.chart-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: var(--gray-50);
}

.chart-loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    color: var(--gray-500);
}

.chart-canvas {
    width: 100%;
    height: 100%;
    position: relative;
}

.chart-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: var(--gray-50);
}

.chart-placeholder-content {
    text-align: center;
    color: var(--gray-400);
}

.chart-placeholder-icon {
    margin-bottom: var(--spacing-md);
    opacity: 0.5;
}

.chart-placeholder p {
    font-size: var(--text-lg);
    font-weight: 600;
    margin: 0 0 var(--spacing-xs);
}

.chart-placeholder small {
    font-size: var(--text-sm);
}

/* Heatmap specific styles */
.heatmap-grid {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 2px;
    padding: var(--spacing-md);
    height: 100%;
}

.heatmap-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--text-xs);
    font-weight: 600;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.heatmap-cell:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-md);
    z-index: 1;
}

/* Chart tooltip */
.chart-tooltip {
    position: absolute;
    background: var(--gray-900);
    color: white;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-lg);
    font-size: var(--text-sm);
    pointer-events: none;
    z-index: var(--z-tooltip);
}

.chart-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: var(--gray-900);
}

/* Chart legend */
.chart-legend {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.legend-items {
    display: flex;
    gap: var(--spacing-lg);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
}

.legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

/* Chart variants */
.chart-shell.chart-minimal .chart-header {
    display: none;
}

.chart-shell.chart-minimal .chart-legend {
    display: none;
}

.chart-shell.chart-trading .chart-indicators {
    display: flex;
}

.chart-shell.chart-performance .chart-controls {
    justify-content: flex-end;
}

/* Responsive design */
@media (max-width: 768px) {
    .chart-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md);
    }
    
    .chart-controls {
        width: 100%;
        justify-content: space-between;
    }
    
    .heatmap-grid {
        grid-template-columns: repeat(5, 1fr);
    }
    
    .legend-items {
        flex-wrap: wrap;
        justify-content: center;
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .chart-header,
[data-theme="dark"] .chart-legend {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .chart-title {
    color: var(--gray-100);
}

[data-theme="dark"] .chart-placeholder {
    background: var(--gray-800);
}

[data-theme="dark"] .chart-placeholder-content {
    color: var(--gray-500);
}

[data-theme="dark"] .chart-loading {
    background: var(--gray-800);
}

[data-theme="dark"] .dropdown-menu {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .dropdown-item {
    border-color: var(--gray-700);
}
</style>