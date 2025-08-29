<?php
/**
 * Chart Shell Component Template Part - Accessible Chart Container
 *
 * @package RetailTradeScanner
 */

// Default chart attributes
$defaults = array(
    'title' => '',
    'type' => 'line', // line, bar, pie, doughnut, area, candlestick, sparkline
    'height' => '400px',
    'width' => '100%',
    'data' => array(),
    'options' => array(),
    'responsive' => true,
    'show_legend' => true,
    'show_tooltip' => true,
    'show_controls' => true,
    'loading' => false,
    'error' => false,
    'error_message' => '',
    'empty_message' => '',
    'variant' => 'default', // default, minimal, glass
    'classes' => '',
    'attributes' => array(),
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Generate unique chart ID
$chart_id = 'chart-' . wp_unique_id();

// Build CSS classes
$chart_classes = array('chart-container');
$chart_classes[] = 'chart-' . esc_attr($args['type']);
$chart_classes[] = 'chart-' . esc_attr($args['variant']);

if ($args['responsive']) {
    $chart_classes[] = 'chart-responsive';
}

if ($args['loading']) {
    $chart_classes[] = 'chart-loading';
}

if ($args['error']) {
    $chart_classes[] = 'chart-error';
}

if (!empty($args['classes'])) {
    $chart_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'class' => implode(' ', $chart_classes),
    'data-chart-type' => $args['type'],
    'data-chart-id' => $chart_id,
);

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}

// Chart container style
$container_style = '';
if ($args['height']) {
    $container_style .= 'height: ' . esc_attr($args['height']) . ';';
}
if ($args['width']) {
    $container_style .= 'width: ' . esc_attr($args['width']) . ';';
}
?>

<div<?php echo $attr_string; ?><?php echo $container_style ? ' style="' . $container_style . '"' : ''; ?>>
    <?php if (!empty($args['title'])) : ?>
        <div class="chart-header">
            <h3 class="chart-title"><?php echo esc_html($args['title']); ?></h3>
            
            <?php if ($args['show_controls']) : ?>
                <div class="chart-controls">
                    <div class="chart-timeframe">
                        <button class="timeframe-btn active" data-timeframe="1D">1D</button>
                        <button class="timeframe-btn" data-timeframe="1W">1W</button>
                        <button class="timeframe-btn" data-timeframe="1M">1M</button>
                        <button class="timeframe-btn" data-timeframe="3M">3M</button>
                        <button class="timeframe-btn" data-timeframe="1Y">1Y</button>
                        <button class="timeframe-btn" data-timeframe="MAX">MAX</button>
                    </div>
                    
                    <div class="chart-actions">
                        <button class="chart-action-btn btn-icon btn-ghost" 
                                title="<?php esc_attr_e('Fullscreen', 'retail-trade-scanner'); ?>"
                                data-action="fullscreen">
                            <?php echo rts_get_icon('maximize', array('width' => '16', 'height' => '16')); ?>
                        </button>
                        
                        <button class="chart-action-btn btn-icon btn-ghost" 
                                title="<?php esc_attr_e('Download', 'retail-trade-scanner'); ?>"
                                data-action="download">
                            <?php echo rts_get_icon('download', array('width' => '16', 'height' => '16')); ?>
                        </button>
                        
                        <button class="chart-action-btn btn-icon btn-ghost" 
                                title="<?php esc_attr_e('Refresh', 'retail-trade-scanner'); ?>"
                                data-action="refresh">
                            <?php echo rts_get_icon('refresh', array('width' => '16', 'height' => '16')); ?>
                        </button>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>

    <div class="chart-content">
        <?php if ($args['loading']) : ?>
            <div class="chart-loading-state">
                <div class="loading-spinner"></div>
                <p><?php esc_html_e('Loading chart data...', 'retail-trade-scanner'); ?></p>
            </div>
        
        <?php elseif ($args['error']) : ?>
            <div class="chart-error-state">
                <?php echo rts_get_icon('alert-circle', array('width' => '48', 'height' => '48', 'class' => 'error-icon')); ?>
                <h4><?php esc_html_e('Chart Error', 'retail-trade-scanner'); ?></h4>
                <p><?php echo esc_html($args['error_message'] ?: __('Unable to load chart data. Please try again.', 'retail-trade-scanner')); ?></p>
                <button class="btn btn-outline btn-sm" onclick="location.reload()">
                    <?php echo rts_get_icon('refresh', array('width' => '16', 'height' => '16')); ?>
                    <?php esc_html_e('Retry', 'retail-trade-scanner'); ?>
                </button>
            </div>
        
        <?php elseif (empty($args['data'])) : ?>
            <div class="chart-empty-state">
                <?php echo rts_get_icon('bar-chart', array('width' => '48', 'height' => '48', 'class' => 'empty-icon')); ?>
                <h4><?php esc_html_e('No Data Available', 'retail-trade-scanner'); ?></h4>
                <p><?php echo esc_html($args['empty_message'] ?: __('Chart data is not available at this time.', 'retail-trade-scanner')); ?></p>
            </div>
        
        <?php else : ?>
            <div class="chart-canvas-wrapper">
                <canvas id="<?php echo esc_attr($chart_id); ?>" 
                        class="chart-canvas"
                        role="img"
                        aria-label="<?php echo esc_attr($args['title'] ?: __('Chart visualization', 'retail-trade-scanner')); ?>">
                    <?php
                    // Fallback content for accessibility
                    if (!empty($args['data']) && is_array($args['data'])) {
                        echo esc_html(__('Chart showing data visualization. Enable JavaScript for full functionality.', 'retail-trade-scanner'));
                    }
                    ?>
                </canvas>
            </div>

            <?php if ($args['show_legend'] && !empty($args['data']['datasets'])) : ?>
                <div class="chart-legend" role="list" aria-label="<?php esc_attr_e('Chart legend', 'retail-trade-scanner'); ?>">
                    <?php foreach ($args['data']['datasets'] as $index => $dataset) : ?>
                        <div class="legend-item" role="listitem">
                            <span class="legend-color" 
                                  style="background-color: <?php echo esc_attr($dataset['backgroundColor'] ?? $dataset['borderColor'] ?? '#6B7280'); ?>"
                                  aria-hidden="true"></span>
                            <span class="legend-label"><?php echo esc_html($dataset['label'] ?? 'Dataset ' . ($index + 1)); ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        <?php endif; ?>
    </div>

    <?php if ($args['show_tooltip']) : ?>
        <div class="chart-tooltip" role="tooltip" aria-hidden="true">
            <div class="tooltip-content"></div>
        </div>
    <?php endif; ?>

    <!-- Chart Initialization Script -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const chartContainer = document.querySelector('[data-chart-id="<?php echo esc_js($chart_id); ?>"]');
        const canvas = document.getElementById('<?php echo esc_js($chart_id); ?>');
        
        if (canvas && canvas.getContext && window.Chart) {
            const chartData = <?php echo wp_json_encode($args['data']); ?>;
            const chartOptions = <?php echo wp_json_encode($args['options']); ?>;
            
            // Initialize chart
            const chart = new Chart(canvas, {
                type: '<?php echo esc_js($args['type']); ?>',
                data: chartData,
                options: {
                    responsive: <?php echo $args['responsive'] ? 'true' : 'false'; ?>,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: <?php echo $args['show_legend'] ? 'true' : 'false'; ?>,
                            position: 'bottom'
                        },
                        tooltip: {
                            enabled: <?php echo $args['show_tooltip'] ? 'true' : 'false'; ?>,
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#FFFFFF',
                            bodyColor: '#FFFFFF',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            cornerRadius: 8,
                            displayColors: true,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.y !== null) {
                                        label += new Intl.NumberFormat('en-US', {
                                            style: 'currency',
                                            currency: 'USD'
                                        }).format(context.parsed.y);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        }
                    },
                    ...chartOptions
                }
            });

            // Store chart instance for external access
            chartContainer.chartInstance = chart;

            // Handle timeframe controls
            chartContainer.querySelectorAll('.timeframe-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    // Remove active class from all buttons
                    chartContainer.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
                    // Add active class to clicked button
                    this.classList.add('active');
                    
                    // Trigger custom event for chart update
                    const event = new CustomEvent('chartTimeframeChange', {
                        detail: {
                            chartId: '<?php echo esc_js($chart_id); ?>',
                            timeframe: this.dataset.timeframe,
                            chart: chart
                        }
                    });
                    document.dispatchEvent(event);
                });
            });

            // Handle chart actions
            chartContainer.querySelectorAll('.chart-action-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const action = this.dataset.action;
                    
                    switch (action) {
                        case 'fullscreen':
                            chartContainer.classList.toggle('chart-fullscreen');
                            chart.resize();
                            break;
                        case 'download':
                            const link = document.createElement('a');
                            link.download = 'chart-<?php echo esc_js($chart_id); ?>.png';
                            link.href = canvas.toDataURL();
                            link.click();
                            break;
                        case 'refresh':
                            // Trigger custom event for chart refresh
                            const refreshEvent = new CustomEvent('chartRefresh', {
                                detail: {
                                    chartId: '<?php echo esc_js($chart_id); ?>',
                                    chart: chart
                                }
                            });
                            document.dispatchEvent(refreshEvent);
                            break;
                    }
                });
            });
        } else {
            console.warn('Chart.js library not loaded or canvas not supported');
        }
    });
    </script>
</div>

<?php
/*
Usage examples:

// Basic line chart
$chart_data = array(
    'labels' => array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'),
    'datasets' => array(
        array(
            'label' => 'Stock Price',
            'data' => array(100, 105, 103, 108, 110, 115),
            'borderColor' => '#3B82F6',
            'backgroundColor' => 'rgba(59, 130, 246, 0.1)',
            'fill' => true
        )
    )
);

get_template_part('template-parts/components/chart-shell', null, array(
    'title' => 'AAPL Stock Performance',
    'type' => 'line',
    'data' => $chart_data,
    'height' => '400px'
));

// Candlestick chart for trading
get_template_part('template-parts/components/chart-shell', null, array(
    'title' => 'AAPL Candlestick Chart',
    'type' => 'candlestick',
    'data' => $ohlc_data,
    'show_controls' => true,
    'variant' => 'glass'
));

// Loading state
get_template_part('template-parts/components/chart-shell', null, array(
    'title' => 'Loading Chart',
    'loading' => true,
    'height' => '300px'
));

// Error state
get_template_part('template-parts/components/chart-shell', null, array(
    'title' => 'Chart Error',
    'error' => true,
    'error_message' => 'Failed to fetch market data'
));
*/