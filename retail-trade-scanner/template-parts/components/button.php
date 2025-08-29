<?php
/**
 * Button Component Template Part
 *
 * @package RetailTradeScanner
 */

// Default button attributes
$defaults = array(
    'text' => 'Button',
    'url' => '#',
    'variant' => 'primary', // primary, secondary, outline, ghost, gradient, magnetic, glass
    'size' => 'base', // xs, sm, base, lg, xl
    'icon' => '', // Icon ID from sprite
    'icon_position' => 'left', // left, right
    'type' => 'link', // link, button, submit
    'target' => '', // _blank, _self
    'disabled' => false,
    'loading' => false,
    'full_width' => false,
    'classes' => '',
    'attributes' => array(),
    'id' => '',
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Build CSS classes
$button_classes = array('btn');
$button_classes[] = 'btn-' . esc_attr($args['variant']);
$button_classes[] = 'btn-' . esc_attr($args['size']);

if ($args['full_width']) {
    $button_classes[] = 'btn-block';
}

if ($args['loading']) {
    $button_classes[] = 'loading';
}

if ($args['disabled']) {
    $button_classes[] = 'disabled';
}

if (!empty($args['classes'])) {
    $button_classes[] = $args['classes'];
}

// Build attributes
$attributes = array();
$attributes['class'] = implode(' ', $button_classes);

if (!empty($args['id'])) {
    $attributes['id'] = $args['id'];
}

if ($args['disabled']) {
    $attributes['disabled'] = 'disabled';
    $attributes['aria-disabled'] = 'true';
}

if ($args['loading']) {
    $attributes['aria-busy'] = 'true';
}

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}

// Render button content
$button_content = '';

// Add loading spinner if needed
if ($args['loading']) {
    $button_content .= '<span class="loading-spinner" aria-hidden="true"></span>';
}

// Add icon (left position)
if (!empty($args['icon']) && $args['icon_position'] === 'left') {
    $button_content .= rts_get_icon($args['icon'], array(
        'width' => $args['size'] === 'xs' ? '14' : ($args['size'] === 'sm' ? '16' : '20'),
        'height' => $args['size'] === 'xs' ? '14' : ($args['size'] === 'sm' ? '16' : '20'),
        'aria-hidden' => 'true'
    ));
}

// Add text content
$button_content .= '<span class="btn-text">' . esc_html($args['text']) . '</span>';

// Add icon (right position)
if (!empty($args['icon']) && $args['icon_position'] === 'right') {
    $button_content .= rts_get_icon($args['icon'], array(
        'width' => $args['size'] === 'xs' ? '14' : ($args['size'] === 'sm' ? '16' : '20'),
        'height' => $args['size'] === 'xs' ? '14' : ($args['size'] === 'sm' ? '16' : '20'),
        'aria-hidden' => 'true'
    ));
}

// Render button based on type
if ($args['type'] === 'link' && !empty($args['url'])) {
    $href_attrs = '';
    if (!empty($args['target'])) {
        $href_attrs .= ' target="' . esc_attr($args['target']) . '"';
        if ($args['target'] === '_blank') {
            $href_attrs .= ' rel="noopener noreferrer"';
        }
    }
    
    echo '<a href="' . esc_url($args['url']) . '"' . $href_attrs . $attr_string . '>' . $button_content . '</a>';
} else {
    $button_type = in_array($args['type'], array('button', 'submit', 'reset')) ? $args['type'] : 'button';
    echo '<button type="' . esc_attr($button_type) . '"' . $attr_string . '>' . $button_content . '</button>';
}

/*
Usage examples:

// Simple primary button
get_template_part('template-parts/components/button', null, array(
    'text' => 'Click Me',
    'url' => home_url('/action/')
));

// Secondary button with icon
get_template_part('template-parts/components/button', null, array(
    'text' => 'Search',
    'variant' => 'secondary',
    'icon' => 'search',
    'url' => home_url('/search/')
));

// Large magnetic button
get_template_part('template-parts/components/button', null, array(
    'text' => 'Get Started',
    'variant' => 'magnetic',
    'size' => 'lg',
    'icon' => 'arrow-right',
    'icon_position' => 'right'
));

// Form submit button
get_template_part('template-parts/components/button', null, array(
    'text' => 'Submit',
    'type' => 'submit',
    'variant' => 'primary',
    'loading' => false // Set to true to show loading state
));

// Disabled button
get_template_part('template-parts/components/button', null, array(
    'text' => 'Unavailable',
    'disabled' => true,
    'variant' => 'secondary'
));
*/