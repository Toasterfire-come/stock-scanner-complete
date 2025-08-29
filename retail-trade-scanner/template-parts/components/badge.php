<?php
/**
 * Badge Component Template Part
 *
 * @package RetailTradeScanner
 */

// Default badge attributes
$defaults = array(
    'text' => '',
    'value' => '', // For numeric values (price changes, percentages)
    'type' => 'neutral', // positive, negative, neutral, info, warning, danger, success
    'variant' => 'default', // default, pill, dot, outline
    'size' => 'base', // xs, sm, base, lg
    'icon' => '', // Icon ID from sprite
    'pulse' => false, // Add pulsing animation
    'classes' => '',
    'attributes' => array(),
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Build CSS classes
$badge_classes = array('badge');
$badge_classes[] = 'badge-' . esc_attr($args['type']);
$badge_classes[] = 'badge-' . esc_attr($args['variant']);
$badge_classes[] = 'badge-' . esc_attr($args['size']);

if ($args['pulse']) {
    $badge_classes[] = 'badge-pulse';
}

if (!empty($args['classes'])) {
    $badge_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'class' => implode(' ', $badge_classes)
);

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}

// Determine content
$display_text = !empty($args['text']) ? $args['text'] : $args['value'];

// Render badge content
$badge_content = '';

// Add dot for dot variant
if ($args['variant'] === 'dot') {
    $badge_content .= '<span class="badge-dot" aria-hidden="true"></span>';
}

// Add icon if specified
if (!empty($args['icon'])) {
    $icon_size = $args['size'] === 'xs' ? '12' : ($args['size'] === 'sm' ? '14' : '16');
    $badge_content .= rts_get_icon($args['icon'], array(
        'width' => $icon_size,
        'height' => $icon_size,
        'aria-hidden' => 'true'
    ));
}

// Add text content
if (!empty($display_text)) {
    $badge_content .= '<span class="badge-text">' . esc_html($display_text) . '</span>';
}

// Add percentage symbol for price changes
if (is_numeric($args['value']) && strpos($display_text, '%') === false) {
    // Check if it's likely a percentage value
    if (abs(floatval($args['value'])) < 100 && ($args['type'] === 'positive' || $args['type'] === 'negative')) {
        $formatted_value = number_format(floatval($args['value']), 2) . '%';
        $badge_content = '<span class="badge-text">' . esc_html($formatted_value) . '</span>';
    }
}

echo '<span' . $attr_string . '>' . $badge_content . '</span>';

/*
Usage examples:

// Positive price change
get_template_part('template-parts/components/badge', null, array(
    'value' => '+2.34',
    'type' => 'positive'
));

// Negative price change
get_template_part('template-parts/components/badge', null, array(
    'value' => '-1.28',
    'type' => 'negative'
));

// Status badge with icon
get_template_part('template-parts/components/badge', null, array(
    'text' => 'Active',
    'type' => 'success',
    'icon' => 'check-circle',
    'variant' => 'pill'
));

// Notification badge
get_template_part('template-parts/components/badge', null, array(
    'text' => '3',
    'type' => 'danger',
    'variant' => 'pill',
    'size' => 'sm'
));

// Dot indicator
get_template_part('template-parts/components/badge', null, array(
    'text' => 'Online',
    'type' => 'positive',
    'variant' => 'dot'
));

// Pulsing notification
get_template_part('template-parts/components/badge', null, array(
    'text' => 'New',
    'type' => 'info',
    'pulse' => true
));
*/
?>

<style>
/* Badge Component Styles - Add to main.css or component stylesheet */
.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--text-xs);
    font-weight: 600;
    line-height: 1;
    border-radius: var(--radius-sm);
    white-space: nowrap;
    transition: all var(--transition-fast) var(--easing-standard);
}

/* Badge Types */
.badge-positive {
    background: rgba(22, 163, 74, 0.1);
    color: var(--success);
    border: 1px solid rgba(22, 163, 74, 0.2);
}

.badge-negative {
    background: rgba(220, 38, 38, 0.1);
    color: var(--danger);
    border: 1px solid rgba(220, 38, 38, 0.2);
}

.badge-neutral {
    background: rgba(107, 114, 128, 0.1);
    color: var(--gray-600);
    border: 1px solid rgba(107, 114, 128, 0.2);
}

.badge-info {
    background: rgba(14, 165, 233, 0.1);
    color: var(--info);
    border: 1px solid rgba(14, 165, 233, 0.2);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning);
    border: 1px solid rgba(245, 158, 11, 0.2);
}

.badge-danger {
    background: rgba(220, 38, 38, 0.1);
    color: var(--danger);
    border: 1px solid rgba(220, 38, 38, 0.2);
}

.badge-success {
    background: rgba(22, 163, 74, 0.1);
    color: var(--success);
    border: 1px solid rgba(22, 163, 74, 0.2);
}

/* Badge Variants */
.badge-pill {
    border-radius: var(--radius-full);
    padding: var(--spacing-xs) var(--spacing-md);
}

.badge-dot {
    padding-left: var(--spacing-lg);
    position: relative;
}

.badge-dot .badge-dot {
    position: absolute;
    left: var(--spacing-sm);
    top: 50%;
    transform: translateY(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}

.badge-outline {
    background: transparent;
    border-width: 1px;
    border-style: solid;
}

/* Badge Sizes */
.badge-xs {
    font-size: 10px;
    padding: 2px var(--spacing-xs);
}

.badge-sm {
    font-size: 11px;
    padding: var(--spacing-xs) var(--spacing-sm);
}

.badge-lg {
    font-size: var(--text-sm);
    padding: var(--spacing-sm) var(--spacing-md);
}

/* Badge Animations */
.badge-pulse {
    animation: badge-pulse 2s infinite;
}

@keyframes badge-pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.05);
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .badge-neutral {
    background: rgba(156, 163, 175, 0.2);
    color: var(--gray-300);
}

[data-theme="dark"] .badge-positive {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
}

[data-theme="dark"] .badge-negative {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
}
</style>