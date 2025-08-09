<?php
/**
 * Performance Chart Component
 * Reusable component for displaying performance visualizations
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Set default values
$chart_data = $args['data'] ?? null;
$chart_type = $args['type'] ?? 'line'; // line, bar, pie, doughnut
$chart_id = $args['id'] ?? 'chart-' . uniqid();
$title = $args['title'] ?? '';
$height = $args['height'] ?? 300;
$show_legend = $args['show_legend'] ?? true;
$color_scheme = $args['color_scheme'] ?? 'default'; // default, positive, negative, mixed

if (!$chart_data) {
    return;
}

// Color schemes
$colors = [
    'default' => ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
    'positive' => ['#059669', '#10b981', '#34d399', '#6ee7b7'],
    'negative' => ['#dc2626', '#ef4444', '#f87171', '#fca5a5'],
    'mixed' => ['#059669', '#dc2626', '#f59e0b', '#2563eb']
];

$chart_colors = $colors[$color_scheme] ?? $colors['default'];

?>

<div class="performance-chart-container" data-chart-id="<?php echo esc_attr($chart_id); ?>">
    <?php if ($title): ?>
        <div class="chart-header">
            <h6 class="chart-title"><?php echo esc_html($title); ?></h6>
        </div>
    <?php endif; ?>
    
    <div class="chart-wrapper">
        <canvas id="<?php echo esc_attr($chart_id); ?>" 
                width="100%" 
                height="<?php echo esc_attr($height); ?>"
                data-chart-type="<?php echo esc_attr($chart_type); ?>"
                data-chart-data="<?php echo esc_attr(json_encode($chart_data)); ?>"
                data-color-scheme="<?php echo esc_attr($color_scheme); ?>">
        </canvas>
    </div>
    
    <?php if (!empty($chart_data['summary'])): ?>
        <div class="chart-summary">
            <?php foreach ($chart_data['summary'] as $key => $value): ?>
                <div class="summary-item">
                    <span class="summary-label"><?php echo esc_html(ucfirst(str_replace('_', ' ', $key))); ?></span>
                    <span class="summary-value"><?php echo esc_html($value); ?></span>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>

<!-- Component Styles -->
<style>
.performance-chart-container {
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.chart-header {
    margin-bottom: var(--spacing-md, 1rem);
    padding-bottom: var(--spacing-sm, 0.5rem);
    border-bottom: 1px solid var(--border-muted, #f1f5f9);
}

.chart-title {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
}

.chart-wrapper {
    position: relative;
    margin-bottom: var(--spacing-md, 1rem);
}

.chart-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--spacing-md, 1rem);
    padding-top: var(--spacing-md, 1rem);
    border-top: 1px solid var(--border-muted, #f1f5f9);
}

.summary-item {
    text-align: center;
    padding: var(--spacing-sm, 0.5rem);
}

.summary-label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-secondary, #64748b);
    font-weight: 500;
    margin-bottom: var(--spacing-xs, 0.25rem);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.summary-value {
    display: block;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .performance-chart-container {
        padding: var(--spacing-md, 1rem);
    }
    
    .chart-summary {
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: var(--spacing-sm, 0.5rem);
    }
    
    .summary-value {
        font-size: 1rem;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('<?php echo $chart_id; ?>');
    if (!canvas || !window.Chart) {
        console.warn('Chart.js library not loaded or canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const chartType = canvas.dataset.chartType;
    const chartData = JSON.parse(canvas.dataset.chartData);
    const colorScheme = canvas.dataset.colorScheme;
    
    // Color configuration
    const colors = {
        'default': ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
        'positive': ['#059669', '#10b981', '#34d399', '#6ee7b7'],
        'negative': ['#dc2626', '#ef4444', '#f87171', '#fca5a5'],
        'mixed': ['#059669', '#dc2626', '#f59e0b', '#2563eb']
    };
    
    const chartColors = colors[colorScheme] || colors['default'];
    
    // Prepare datasets with colors
    const datasets = chartData.datasets.map((dataset, index) => {
        const color = chartColors[index % chartColors.length];
        return {
            ...dataset,
            borderColor: color,
            backgroundColor: chartType === 'line' ? color + '20' : color,
            borderWidth: 2,
            fill: chartType === 'line' ? true : false,
            tension: chartType === 'line' ? 0.4 : 0
        };
    });
    
    // Chart configuration
    const config = {
        type: chartType,
        data: {
            labels: chartData.labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: <?php echo $show_legend ? 'true' : 'false'; ?>,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            
                            // Format value based on data type
                            const value = context.parsed.y || context.parsed;
                            if (typeof value === 'number') {
                                if (chartData.format === 'currency') {
                                    label += '$' + value.toLocaleString();
                                } else if (chartData.format === 'percentage') {
                                    label += value.toFixed(2) + '%';
                                } else {
                                    label += value.toLocaleString();
                                }
                            } else {
                                label += value;
                            }
                            
                            return label;
                        }
                    }
                }
            },
            scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
                x: {
                    display: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    beginAtZero: chartData.beginAtZero !== false,
                    grid: {
                        color: '#f1f5f9'
                    },
                    ticks: {
                        callback: function(value) {
                            if (chartData.format === 'currency') {
                                return '$' + value.toLocaleString();
                            } else if (chartData.format === 'percentage') {
                                return value.toFixed(1) + '%';
                            }
                            return value.toLocaleString();
                        }
                    }
                }
            } : {},
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    };
    
    // Create chart
    const chart = new Chart(ctx, config);
    
    // Store chart instance for potential updates
    canvas.chartInstance = chart;
    
    // Add resize observer for responsive behavior
    if (window.ResizeObserver) {
        const resizeObserver = new ResizeObserver(() => {
            chart.resize();
        });
        resizeObserver.observe(canvas.parentElement);
    }
});

// Global function to update chart data
window.updateChart = function(chartId, newData) {
    const canvas = document.getElementById(chartId);
    if (canvas && canvas.chartInstance) {
        const chart = canvas.chartInstance;
        chart.data = newData;
        chart.update('animate');
    }
};
</script>