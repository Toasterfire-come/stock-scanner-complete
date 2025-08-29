<?php
/**
 * Badge Component Template Part
 *
 * @package RetailTradeScanner
 */

$args = wp_parse_args($args, array(
    'value' => '',
    'type' => 'neutral', // positive, negative, neutral, success, warning, danger, info
    'size' => 'base', // xs, sm, base, lg
    'variant' => 'default', // default, outline, solid
    'icon' => '',
    'custom_class' => ''
));

extract($args);

// Determine badge type based on value if not explicitly set
if ($type === 'neutral' && $value) {
    if (strpos($value, '+') === 0) {
        $type = 'positive';
    } elseif (strpos($value, '-') === 0) {
        $type = 'negative';
    }
}

$badge_classes = array('badge');
$badge_classes[] = 'badge-' . $type;
$badge_classes[] = 'badge-' . $size;
$badge_classes[] = 'badge-' . $variant;

if ($custom_class) {
    $badge_classes[] = $custom_class;
}

// Clean up value display
$display_value = $value;
$trend_icon = '';

if ($type === 'positive' && strpos($value, '+') === false && strpos($value, '%') !== false) {
    $display_value = '+' . $value;
}

// Add trend icons for certain types
if ($type === 'positive') {
    $trend_icon = 'trending-up';
} elseif ($type === 'negative') {
    $trend_icon = 'trending-down';
}
?>

<span class="<?php echo esc_attr(implode(' ', $badge_classes)); ?>" 
      <?php if ($type !== 'neutral') : ?>
      title="<?php echo esc_attr($display_value); ?>"
      <?php endif; ?>>
    
    <?php if ($icon || $trend_icon) : ?>
        <span class="badge-icon">
            <?php echo rts_get_icon($icon ?: $trend_icon, ['width' => '12', 'height' => '12']); ?>
        </span>
    <?php endif; ?>
    
    <span class="badge-text">
        <?php echo esc_html($display_value); ?>
    </span>
</span>

<style>
/* Badge Component Styles */
.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-weight: 600;
    border-radius: var(--radius-full);
    white-space: nowrap;
    transition: all var(--transition-fast) var(--easing-standard);
    line-height: 1;
}

/* Badge Types - Default Variant */
.badge.badge-positive {
    background: var(--success-light);
    color: var(--success);
}

.badge.badge-negative {
    background: var(--danger-light);
    color: var(--danger);
}

.badge.badge-neutral {
    background: var(--gray-100);
    color: var(--gray-600);
}

.badge.badge-success {
    background: var(--success-light);
    color: var(--success);
}

.badge.badge-warning {
    background: var(--warning-light);
    color: var(--warning);
}

.badge.badge-danger {
    background: var(--danger-light);
    color: var(--danger);
}

.badge.badge-info {
    background: var(--info-light);
    color: var(--info);
}

/* Badge Types - Outline Variant */
.badge.badge-outline.badge-positive {
    background: transparent;
    border: 1px solid var(--success);
    color: var(--success);
}

.badge.badge-outline.badge-negative {
    background: transparent;
    border: 1px solid var(--danger);
    color: var(--danger);
}

.badge.badge-outline.badge-neutral {
    background: transparent;
    border: 1px solid var(--gray-300);
    color: var(--gray-600);
}

.badge.badge-outline.badge-success {
    background: transparent;
    border: 1px solid var(--success);
    color: var(--success);
}

.badge.badge-outline.badge-warning {
    background: transparent;
    border: 1px solid var(--warning);
    color: var(--warning);
}

.badge.badge-outline.badge-danger {
    background: transparent;
    border: 1px solid var(--danger);
    color: var(--danger);
}

.badge.badge-outline.badge-info {
    background: transparent;
    border: 1px solid var(--info);
    color: var(--info);
}

/* Badge Types - Solid Variant */
.badge.badge-solid.badge-positive {
    background: var(--success);
    color: white;
}

.badge.badge-solid.badge-negative {
    background: var(--danger);
    color: white;
}

.badge.badge-solid.badge-neutral {
    background: var(--gray-600);
    color: white;
}

.badge.badge-solid.badge-success {
    background: var(--success);
    color: white;
}

.badge.badge-solid.badge-warning {
    background: var(--warning);
    color: white;
}

.badge.badge-solid.badge-danger {
    background: var(--danger);
    color: white;
}

.badge.badge-solid.badge-info {
    background: var(--info);
    color: white;
}

/* Badge Sizes */
.badge.badge-xs {
    padding: 2px var(--spacing-xs);
    font-size: 10px;
}

.badge.badge-sm {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--text-xs);
}

.badge.badge-base {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--text-sm);
}

.badge.badge-lg {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--text-base);
}

/* Badge Icon */
.badge-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

.badge.badge-xs .badge-icon svg {
    width: 10px;
    height: 10px;
}

.badge.badge-sm .badge-icon svg {
    width: 12px;
    height: 12px;
}

.badge.badge-base .badge-icon svg {
    width: 14px;
    height: 14px;
}

.badge.badge-lg .badge-icon svg {
    width: 16px;
    height: 16px;
}

/* Hover effects for interactive badges */
.badge:hover {
    transform: scale(1.05);
}

/* Dark Mode Adjustments */
[data-theme="dark"] .badge.badge-neutral {
    background: var(--gray-700);
    color: var(--gray-300);
}

[data-theme="dark"] .badge.badge-outline.badge-neutral {
    border-color: var(--gray-600);
    color: var(--gray-300);
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .badge {
        transition: none;
    }
    
    .badge:hover {
        transform: none;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .badge {
        border: 1px solid currentColor;
    }
    
    .badge.badge-solid {
        border: 2px solid white;
    }
}
</style>