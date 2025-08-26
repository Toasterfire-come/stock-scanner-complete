<?php
/**
 * Enhanced Nav Walker: adds active classes and submenu toggles
 * Uses proper list semantics without unnecessary ARIA menu roles
 */
class StockScanner_Nav_Walker extends Walker_Nav_Menu {
    public function start_lvl( &$output, $depth = 0, $args = null ) {
        $indent = str_repeat("\t", $depth);
        $output .= "\n$indent<ul class=\"sub-menu\">\n";
    }

    public function end_lvl( &$output, $depth = 0, $args = null ) {
        $indent = str_repeat("\t", $depth);
        $output .= "$indent</ul>\n";
    }

    public function start_el( &$output, $item, $depth = 0, $args = null, $id = 0 ) {
        $classes = empty($item->classes) ? array() : (array) $item->classes;
        $has_children = in_array('menu-item-has-children', $classes, true);
        if (in_array('current-menu-item', $classes, true) || in_array('current_page_item', $classes, true)) {
            $classes[] = 'is-active';
        }
        $class_names = $classes ? ' class="menu-item ' . esc_attr(implode(' ', array_filter($classes))) . '"' : ' class="menu-item"';
        $output .= '<li' . $class_names . '>';

        $atts = '';
        $atts .= ! empty( $item->url ) ? ' href="' . esc_url( $item->url ) . '"' : '';
        $atts .= ' class="' . ( $depth === 0 ? 'top-link' : 'sub-link' ) . '"';
        if ($has_children) {
            $atts .= ' aria-haspopup="true" aria-expanded="false"';
        }

        $title = apply_filters('the_title', $item->title, $item->ID);
        $output .= '<a' . $atts . '>' . $title . '</a>';

        if ($has_children) {
            $toggle_id = 'submenu-toggle-' . $item->ID;
            $output .= '<button class="submenu-toggle" aria-controls="' . esc_attr($toggle_id) . '" aria-expanded="false" aria-label="Toggle submenu for ' . esc_attr($title) . '">'
                    . '<span class="submenu-caret">▾</span>'
                    . '</button>';
        }
    }

    public function end_el( &$output, $item, $depth = 0, $args = null ) {
        $output .= '</li>';
    }
}