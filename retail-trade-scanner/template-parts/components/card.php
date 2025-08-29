<?php
/**
 * Card Component Template Part - KPI/Metric Cards
 *
 * @package RetailTradeScanner
 */

// Default card attributes
$defaults = array(
    'title' => '',
    'value' => '',
    'change' => '', // Change value (can be positive/negative)
    'change_type' => 'auto', // auto, positive, negative, neutral
    'subtitle' => '',
    'description' => '',
    'icon' => '',
    'chart_data' => array(), // Simple array for sparkline
    'variant' => 'default', // default, glass, elevated, outline
    'size' => 'base', // sm, base, lg
    'clickable' => false,
    'url' => '',
    'classes' => '',
    'attributes' => array(),
    'show_trend' => true,
    'loading' => false,
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Auto-detect change type
if ($args['change_type'] === 'auto' && !empty($args['change'])) {
    $change_value = floatval(str_replace(array('+', '%', '$', ','), '', $args['change']));
    if ($change_value > 0) {
        $args['change_type'] = 'positive';
    } elseif ($change_value < 0) {
        $args['change_type'] = 'negative';
    } else {
        $args['change_type'] = 'neutral';
    }
}

// Build CSS classes
$card_classes = array('card', 'metric-card');
$card_classes[] = 'card-' . esc_attr($args['variant']);
$card_classes[] = 'card-' . esc_attr($args['size']);

if ($args['clickable']) {
    $card_classes[] = 'card-clickable';
}

if ($args['loading']) {
    $card_classes[] = 'card-loading';
}

if (!empty($args['classes'])) {
    $card_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'class' => implode(' ', $card_classes)
);

// Add click functionality if needed
if ($args['clickable'] && !empty($args['url'])) {
    $attributes['data-url'] = esc_url($args['url']);
    $attributes['tabindex'] = '0';
    $attributes['role'] = 'button';
    $attributes['aria-label'] = sprintf(__('View details for %s', 'retail-trade-scanner'), $args['title']);
}

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}

// Generate unique ID for chart if needed
$chart_id = 'chart-' . wp_unique_id();
?>

<div<?php echo $attr_string; ?>>
    <?php if ($args['loading']) : ?>
        <div class="card-loading-overlay">
            <div class="loading-spinner" aria-label="<?php esc_attr_e('Loading...', 'retail-trade-scanner'); ?>"></div>
        </div>
    <?php endif; ?>

    <div class="card-header">
        <div class="card-header-content">
            <?php if (!empty($args['icon'])) : ?>
                <div class="card-icon">
                    <?php echo rts_get_icon($args['icon'], array(
                        'width' => $args['size'] === 'sm' ? '20' : '24',
                        'height' => $args['size'] === 'sm' ? '20' : '24',
                        'aria-hidden' => 'true'
                    )); ?>
                </div>
            <?php endif; ?>
            
            <div class="card-title-group">
                <?php if (!empty($args['title'])) : ?>
                    <h3 class="card-title"><?php echo esc_html($args['title']); ?></h3>
                <?php endif; ?>
                
                <?php if (!empty($args['subtitle'])) : ?>
                    <p class="card-subtitle"><?php echo esc_html($args['subtitle']); ?></p>
                <?php endif; ?>
            </div>
        </div>

        <?php if (!empty($args['change']) && $args['show_trend']) : ?>
            <div class="card-trend">
                <?php
                get_template_part('template-parts/components/badge', null, array(
                    'value' => $args['change'],
                    'type' => $args['change_type'],
                    'variant' => 'pill',
                    'size' => 'sm'
                ));
                ?>
            </div>
        <?php endif; ?>
    </div>

    <div class="card-body">
        <?php if (!empty($args['value'])) : ?>
            <div class="card-value">
                <span class="value-display"><?php echo esc_html($args['value']); ?></span>
            </div>
        <?php endif; ?>

        <?php if (!empty($args['description'])) : ?>
            <p class="card-description"><?php echo esc_html($args['description']); ?></p>
        <?php endif; ?>

        <?php if (!empty($args['chart_data']) && is_array($args['chart_data'])) : ?>
            <div class="card-chart">
                <canvas id="<?php echo esc_attr($chart_id); ?>" 
                        class="sparkline-chart" 
                        width="100" 
                        height="30"
                        aria-label="<?php esc_attr_e('Trend chart', 'retail-trade-scanner'); ?>"
                        role="img">
                    <?php
                    // Fallback text for accessibility
                    $trend = count($args['chart_data']) > 1 && 
                             end($args['chart_data']) > reset($args['chart_data']) ? 
                             __('Trending up', 'retail-trade-scanner') : 
                             __('Trending down', 'retail-trade-scanner');
                    echo esc_html($trend);
                    ?>
                </canvas>
                <script>
                // Simple sparkline chart rendering
                document.addEventListener('DOMContentLoaded', function() {
                    const canvas = document.getElementById('<?php echo esc_js($chart_id); ?>');
                    if (canvas && canvas.getContext) {
                        const ctx = canvas.getContext('2d');
                        const data = <?php echo wp_json_encode($args['chart_data']); ?>;
                        
                        if (data.length > 1) {
                            RTS.renderSparkline(ctx, data, {
                                width: canvas.width,
                                height: canvas.height,
                                color: '<?php echo $args['change_type'] === 'positive' ? '#16a34a' : ($args['change_type'] === 'negative' ? '#dc2626' : '#6b7280'); ?>'
                            });
                        }
                    }
                });
                </script>
            </div>
        <?php endif; ?>
    </div>

    <?php if ($args['clickable'] && !empty($args['url'])) : ?>
        <a href="<?php echo esc_url($args['url']); ?>" class="card-link-overlay" aria-hidden="true" tabindex="-1">
            <span class="sr-only"><?php echo sprintf(__('View details for %s', 'retail-trade-scanner'), $args['title']); ?></span>
        </a>
    <?php endif; ?>
</div>

<?php
/*
Usage examples:

// Basic KPI card
get_template_part('template-parts/components/card', null, array(
    'title' => 'Portfolio Value',
    'value' => '$124,567.89',
    'change' => '+5.23%',
    'icon' => 'portfolio'
));

// Stock price card
get_template_part('template-parts/components/card', null, array(
    'title' => 'AAPL',
    'subtitle' => 'Apple Inc.',
    'value' => '$182.34',
    'change' => '+2.45%',
    'description' => 'Technology stock showing strong performance',
    'chart_data' => array(175, 178, 180, 182, 185, 182),
    'clickable' => true,
    'url' => home_url('/stock/aapl/')
));

// Market index card
get_template_part('template-parts/components/card', null, array(
    'title' => 'S&P 500',
    'value' => '4,567.23',
    'change' => '-0.12%',
    'variant' => 'glass',
    'icon' => 'trending-up'
));

// Loading state card
get_template_part('template-parts/components/card', null, array(
    'title' => 'Loading Data',
    'loading' => true,
    'variant' => 'outline'
));
*/
?>

<style>
/* Metric Card Component Styles */
.metric-card {
    position: relative;
    transition: all var(--transition-normal) var(--easing-standard);
}

.metric-card.card-clickable {
    cursor: pointer;
}

.metric-card.card-clickable:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.card-header-content {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    flex: 1;
    min-width: 0;
}

.card-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    color: white;
    border-radius: var(--radius-lg);
}

.card-sm .card-icon {
    width: 40px;
    height: 40px;
}

.card-lg .card-icon {
    width: 56px;
    height: 56px;
}

.card-title-group {
    min-width: 0;
    flex: 1;
}

.card-title {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0;
    line-height: 1.2;
}

.card-sm .card-title {
    font-size: var(--text-base);
}

.card-lg .card-title {
    font-size: var(--text-xl);
}

.card-subtitle {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: var(--spacing-xs) 0 0;
    line-height: 1.3;
}

.card-trend {
    flex-shrink: 0;
}

.card-body {
    padding: 0;
}

.card-value {
    margin-bottom: var(--spacing-md);
}

.value-display {
    font-size: var(--text-3xl);
    font-weight: 900;
    color: var(--gray-900);
    line-height: 1;
}

.card-sm .value-display {
    font-size: var(--text-2xl);
}

.card-lg .value-display {
    font-size: var(--text-4xl);
}

.card-description {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: 0 0 var(--spacing-lg);
    line-height: 1.4;
}

.card-chart {
    margin-top: var(--spacing-lg);
}

.sparkline-chart {
    width: 100%;
    height: 30px;
    display: block;
}

.card-link-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    text-decoration: none;
    z-index: 1;
}

.card-loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(2px);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: inherit;
    z-index: 2;
}

/* Card Variants */
.card-glass {
    background: var(--surface-glass);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-elevated {
    box-shadow: var(--shadow-xl);
}

.card-outline {
    background: transparent;
    border: 2px solid var(--gray-200);
}

/* Card Sizes */
.card-sm {
    padding: var(--spacing-md);
}

.card-lg {
    padding: var(--spacing-2xl);
}

/* Dark mode adjustments */
[data-theme="dark"] .card-title {
    color: var(--gray-100);
}

[data-theme="dark"] .value-display {
    color: var(--gray-100);
}

[data-theme="dark"] .card-outline {
    border-color: var(--gray-700);
}

/* Focus styles for accessibility */
.card-clickable:focus-visible {
    outline: 3px solid var(--primary-500);
    outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .card-header {
        flex-direction: column;
        align-items: stretch;
    }
    
    .card-header-content {
        align-items: center;
    }
    
    .value-display {
        font-size: var(--text-2xl);
    }
}
</style>