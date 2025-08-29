<?php
/**
 * Custom Walker for Navigation Menus
 *
 * @package RetailTradeScanner
 */

class Retail_Trade_Scanner_Walker_Nav_Menu extends Walker_Nav_Menu {
    
    /**
     * Starts the list before the elements are added.
     */
    public function start_lvl(&$output, $depth = 0, $args = null) {
        $indent = str_repeat("\t", $depth);
        $output .= "\n$indent<ul class=\"sub-menu glass-card\" role=\"menu\">\n";
    }

    /**
     * Ends the list after the elements are added.
     */
    public function end_lvl(&$output, $depth = 0, $args = null) {
        $indent = str_repeat("\t", $depth);
        $output .= "$indent</ul>\n";
    }

    /**
     * Starts the element output.
     */
    public function start_el(&$output, $item, $depth = 0, $args = null, $id = 0) {
        $indent = ($depth) ? str_repeat("\t", $depth) : '';

        $classes = empty($item->classes) ? array() : (array) $item->classes;
        $classes[] = 'menu-item-' . $item->ID;

        // Add active class for current item
        if (in_array('current-menu-item', $classes) || in_array('current-menu-ancestor', $classes)) {
            $classes[] = 'is-active';
        }

        // Add dropdown class if item has children
        if (in_array('menu-item-has-children', $classes)) {
            $classes[] = 'has-dropdown';
        }

        $class_names = join(' ', apply_filters('nav_menu_css_class', array_filter($classes), $item, $args));
        $class_names = $class_names ? ' class="' . esc_attr($class_names) . '"' : '';

        $id = apply_filters('nav_menu_item_id', 'menu-item-'. $item->ID, $item, $args);
        $id = $id ? ' id="' . esc_attr($id) . '"' : '';

        $output .= $indent . '<li' . $id . $class_names .'>';

        $attributes = ! empty($item->attr_title) ? ' title="'  . esc_attr($item->attr_title) .'"' : '';
        $attributes .= ! empty($item->target)     ? ' target="' . esc_attr($item->target     ) .'"' : '';
        $attributes .= ! empty($item->xfn)        ? ' rel="'    . esc_attr($item->xfn        ) .'"' : '';
        $attributes .= ! empty($item->url)        ? ' href="'   . esc_attr($item->url        ) .'"' : '';

        // Add nav-link class and icon
        $link_classes = 'nav-link flex items-center gap-sm';
        if (in_array('current-menu-item', $classes) || in_array('current-menu-ancestor', $classes)) {
            $link_classes .= ' is-active';
        }

        // Get icon from menu item description or title
        $icon = $this->get_menu_icon($item);

        $item_output = isset($args->before) ? $args->before : '';
        $item_output .= '<a class="' . $link_classes . '"' . $attributes . '>';
        $item_output .= $icon;
        $item_output .= '<span class="nav-label">';
        $item_output .= isset($args->link_before) ? $args->link_before : '';
        $item_output .= apply_filters('the_title', $item->title, $item->ID);
        $item_output .= isset($args->link_after) ? $args->link_after : '';
        $item_output .= '</span>';

        // Add dropdown arrow for parent items
        if (in_array('menu-item-has-children', $classes)) {
            $item_output .= rts_get_icon('chevron-down', ['width' => '16', 'height' => '16', 'class' => 'dropdown-icon']);
        }

        $item_output .= '</a>';
        $item_output .= isset($args->after) ? $args->after : '';

        $output .= apply_filters('walker_nav_menu_start_el', $item_output, $item, $depth, $args);
    }

    /**
     * Get icon for menu item
     */
    private function get_menu_icon($item) {
        // Check if item has an icon in description
        if (!empty($item->description)) {
            return rts_get_icon($item->description, ['width' => '20', 'height' => '20']);
        }

        // Default icons based on menu item title/URL
        $icon_map = [
            'dashboard' => 'dashboard',
            'scanner' => 'scanner',
            'search' => 'search',
            'popular' => 'popular',
            'email' => 'email',
            'news' => 'news',
            'finder' => 'finder',
            'filters' => 'filters',
            'plans' => 'plans',
            'contact' => 'contact',
            'portfolio' => 'portfolio',
            'alerts' => 'alerts',
            'watchlist' => 'watchlist',
        ];

        $title_lower = strtolower($item->title);
        foreach ($icon_map as $keyword => $icon) {
            if (strpos($title_lower, $keyword) !== false) {
                return rts_get_icon($icon, ['width' => '20', 'height' => '20']);
            }
        }

        return '';
    }

    /**
     * Ends the element output.
     */
    public function end_el(&$output, $item, $depth = 0, $args = null) {
        $output .= "</li>\n";
    }
}

/**
 * Fallback function for primary menu
 */
function retail_trade_scanner_fallback_menu() {
    $menu_items = [
        ['url' => home_url('/scanner/'), 'title' => 'Scanner', 'icon' => 'scanner'],
        ['url' => home_url('/search/'), 'title' => 'Search', 'icon' => 'search'],
        ['url' => home_url('/popular/'), 'title' => 'Popular', 'icon' => 'popular'],
        ['url' => home_url('/news/'), 'title' => 'News', 'icon' => 'news'],
        ['url' => home_url('/contact/'), 'title' => 'Contact', 'icon' => 'contact'],
    ];

    echo '<ul class="main-menu flex items-center gap-lg">';
    foreach ($menu_items as $item) {
        $is_active = (strpos($_SERVER['REQUEST_URI'], $item['url']) !== false) ? 'is-active' : '';
        echo '<li class="menu-item">';
        echo '<a href="' . esc_url($item['url']) . '" class="nav-link flex items-center gap-sm ' . $is_active . '">';
        echo rts_get_icon($item['icon'], ['width' => '20', 'height' => '20']);
        echo '<span class="nav-label">' . esc_html($item['title']) . '</span>';
        echo '</a>';
        echo '</li>';
    }
    echo '</ul>';
}