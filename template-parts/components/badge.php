<?php
/**
 * Badge Component
 * Args: text, class
 */
if (!defined('ABSPATH')) { exit; }
$defaults = [ 'text' => '', 'class' => '' ];
$args = wp_parse_args( $args ?? [], $defaults );
?>
<span class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs <?php echo esc_attr($args['class']); ?>"><?php echo esc_html( $args['text'] ); ?></span>