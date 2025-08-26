<?php
/**
 * Optional Simple Nav Walker for adding active classes
 */
class StockScanner_Nav_Walker extends Walker_Nav_Menu {
    function start_el( &$output, $item, $depth = 0, $args = null, $id = 0 ) {
        $classes = empty($item->classes) ? array() : (array) $item->classes;
        if (in_array('current-menu-item', $classes) || in_array('current_page_item', $classes)) {
            $classes[] = 'is-active';
        }
        $class_names = join( ' ', array_map('esc_attr', array_filter($classes)) );
        $output .= '<li class="menu-item ' . $class_names . '">';
        $atts = !empty($item->url) ? ' href="' . esc_url($item->url) . '"' : '';
        $output .= '<a' . $atts . '>' . apply_filters('the_title', $item->title, $item->ID) . '</a>';
    }
    function end_el( &$output, $item, $depth = 0, $args = null ) {
        $output .= '</li>';
    }
}