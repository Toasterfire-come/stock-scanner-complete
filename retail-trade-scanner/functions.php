<?php
/**
 * Retail Trade Scanner Theme Functions
 *
 * @package RetailTradeScanner
 * @version 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme Setup
 */
function retail_trade_scanner_setup() {
    // Make theme available for translation
    load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages');

    // Add default posts and comments RSS feed links to head
    add_theme_support('automatic-feed-links');

    // Let WordPress manage the document title
    add_theme_support('title-tag');

    // Enable support for Post Thumbnails on posts and pages
    add_theme_support('post-thumbnails');

    // Add theme support for selective refresh for widgets
    add_theme_support('customize-selective-refresh-widgets');

    // Add support for HTML5 markup
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ));

    // Add support for editor styles
    add_theme_support('editor-styles');

    // Enqueue editor styles
    add_editor_style('assets/css/editor-style.css');

    // Add support for responsive embeds
    add_theme_support('responsive-embeds');

    // Register navigation menus
    register_nav_menus(array(
        'primary' => esc_html__('Primary Navigation', 'retail-trade-scanner'),
        'footer' => esc_html__('Footer Navigation', 'retail-trade-scanner'),
    ));
}
add_action('after_setup_theme', 'retail_trade_scanner_setup');

/**
 * Enqueue Scripts and Styles
 */
function retail_trade_scanner_scripts() {
    // Theme styles
    wp_enqueue_style(
        'retail-trade-scanner-style',
        get_stylesheet_uri(),
        array(),
        filemtime(get_template_directory() . '/style.css')
    );

    // Main theme CSS
    wp_enqueue_style(
        'retail-trade-scanner-main',
        get_template_directory_uri() . '/assets/css/main.css',
        array(),
        filemtime(get_template_directory() . '/assets/css/main.css')
    );

    // Main theme JavaScript
    wp_enqueue_script(
        'retail-trade-scanner-main',
        get_template_directory_uri() . '/assets/js/main.js',
        array('jquery'),
        filemtime(get_template_directory() . '/assets/js/main.js'),
        true
    );

    // Localize script for AJAX
    wp_localize_script('retail-trade-scanner-main', 'rtsAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('rts_nonce'),
        'theme_url' => get_template_directory_uri(),
    ));

    // Comment reply script
    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'retail_trade_scanner_scripts');

/**
 * Enqueue Block Editor Assets
 */
function retail_trade_scanner_block_editor_assets() {
    wp_enqueue_style(
        'retail-trade-scanner-block-editor-style',
        get_template_directory_uri() . '/assets/css/block-editor-style.css',
        array(),
        filemtime(get_template_directory() . '/assets/css/block-editor-style.css')
    );
}
add_action('enqueue_block_editor_assets', 'retail_trade_scanner_block_editor_assets');

/**
 * Custom Icon Helper Function
 *
 * @param string $icon_id The icon ID from the sprite
 * @param array $attributes Additional SVG attributes
 * @return string SVG markup
 */
function rts_get_icon($icon_id, $attributes = array()) {
    $default_attributes = array(
        'width' => '24',
        'height' => '24',
        'class' => 'icon',
        'aria-hidden' => 'true',
    );

    $attributes = wp_parse_args($attributes, $default_attributes);
    
    $attr_string = '';
    foreach ($attributes as $attr => $value) {
        if ($value !== false) {
            $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
        }
    }

    return sprintf(
        '<svg%s><use href="#%s"></use></svg>',
        $attr_string,
        esc_attr($icon_id)
    );
}

/**
 * Add SVG Icon Sprite to Footer
 */
function retail_trade_scanner_add_svg_sprite() {
    $sprite_file = get_template_directory() . '/assets/icons/sprite.svg';
    
    if (file_exists($sprite_file)) {
        echo file_get_contents($sprite_file);
    }
}
add_action('wp_footer', 'retail_trade_scanner_add_svg_sprite', 1);

/**
 * Add Custom Body Classes
 */
function retail_trade_scanner_body_classes($classes) {
    // Add class for JavaScript detection
    $classes[] = 'no-js';

    // Add class for the active theme
    $classes[] = 'theme-retail-trade-scanner';

    // Add class for logged-in users
    if (is_user_logged_in()) {
        $classes[] = 'logged-in';
    }

    return $classes;
}
add_filter('body_class', 'retail_trade_scanner_body_classes');

/**
 * Inline Critical CSS
 */
function retail_trade_scanner_inline_critical_css() {
    $critical_css_file = get_template_directory() . '/assets/css/critical.css';
    
    if (file_exists($critical_css_file)) {
        echo '<style id="critical-css">';
        echo file_get_contents($critical_css_file);
        echo '</style>';
    }
}
add_action('wp_head', 'retail_trade_scanner_inline_critical_css', 1);

/**
 * Preload Critical Resources
 */
function retail_trade_scanner_preload_resources() {
    // Preload primary font
    echo '<link rel="preload" href="' . get_template_directory_uri() . '/assets/fonts/inter-display-var.woff2" as="font" type="font/woff2" crossorigin>';
    echo '<link rel="preload" href="' . get_template_directory_uri() . '/assets/fonts/inter-text-var.woff2" as="font" type="font/woff2" crossorigin>';
}
add_action('wp_head', 'retail_trade_scanner_preload_resources', 2);

/**
 * Add Theme Customizer Options
 */
function retail_trade_scanner_customize_register($wp_customize) {
    // Theme Options Section
    $wp_customize->add_section('retail_trade_scanner_options', array(
        'title' => __('Theme Options', 'retail-trade-scanner'),
        'priority' => 30,
    ));

    // Dark Mode Toggle
    $wp_customize->add_setting('rts_dark_mode', array(
        'default' => false,
        'sanitize_callback' => 'retail_trade_scanner_sanitize_checkbox',
    ));

    $wp_customize->add_control('rts_dark_mode', array(
        'label' => __('Enable Dark Mode', 'retail-trade-scanner'),
        'section' => 'retail_trade_scanner_options',
        'type' => 'checkbox',
    ));

    // Animation Settings
    $wp_customize->add_setting('rts_enable_animations', array(
        'default' => true,
        'sanitize_callback' => 'retail_trade_scanner_sanitize_checkbox',
    ));

    $wp_customize->add_control('rts_enable_animations', array(
        'label' => __('Enable Animations', 'retail-trade-scanner'),
        'section' => 'retail_trade_scanner_options',
        'type' => 'checkbox',
    ));
}
add_action('customize_register', 'retail_trade_scanner_customize_register');

/**
 * Sanitize Checkbox
 */
function retail_trade_scanner_sanitize_checkbox($checked) {
    return ((isset($checked) && true == $checked) ? true : false);
}

/**
 * Add Customizer CSS to Head
 */
function retail_trade_scanner_customizer_css() {
    $dark_mode = get_theme_mod('rts_dark_mode', false);
    $enable_animations = get_theme_mod('rts_enable_animations', true);

    $css = '<style type="text/css" id="customizer-css">';

    if ($dark_mode) {
        $css .= '
        :root {
            --surface-raised: var(--gray-900);
            --surface-overlay: rgba(17, 24, 39, 0.95);
            --text-primary: var(--gray-100);
        }
        body {
            background: var(--gray-900);
            color: var(--gray-100);
        }';
    }

    if (!$enable_animations) {
        $css .= '
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }';
    }

    $css .= '</style>';
    
    echo $css;
}
add_action('wp_head', 'retail_trade_scanner_customizer_css');

/**
 * Register Widget Areas
 */
function retail_trade_scanner_widgets_init() {
    register_sidebar(array(
        'name' => esc_html__('Sidebar', 'retail-trade-scanner'),
        'id' => 'sidebar-1',
        'description' => esc_html__('Add widgets here.', 'retail-trade-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));

    register_sidebar(array(
        'name' => esc_html__('Footer 1', 'retail-trade-scanner'),
        'id' => 'footer-1',
        'description' => esc_html__('Add widgets here.', 'retail-trade-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));

    register_sidebar(array(
        'name' => esc_html__('Footer 2', 'retail-trade-scanner'),
        'id' => 'footer-2',
        'description' => esc_html__('Add widgets here.', 'retail-trade-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));

    register_sidebar(array(
        'name' => esc_html__('Footer 3', 'retail-trade-scanner'),
        'id' => 'footer-3',
        'description' => esc_html__('Add widgets here.', 'retail-trade-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
}
add_action('widgets_init', 'retail_trade_scanner_widgets_init');

/**
 * Improve Theme Performance
 */

// Remove unnecessary WordPress features
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'feed_links', 2);
remove_action('wp_head', 'feed_links_extra', 3);
remove_action('wp_head', 'index_rel_link');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'start_post_rel_link', 10, 0);
remove_action('wp_head', 'parent_post_rel_link', 10, 0);
remove_action('wp_head', 'adjacent_posts_rel_link', 10, 0);
remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10, 0);
remove_action('wp_head', 'wp_shortlink_wp_head', 10, 0);

// Disable emoji scripts
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('admin_print_scripts', 'print_emoji_detection_script');
remove_action('wp_print_styles', 'print_emoji_styles');
remove_action('admin_print_styles', 'print_emoji_styles');

/**
 * Add JavaScript to replace 'no-js' class
 */
function retail_trade_scanner_js_detection() {
    echo "<script>document.documentElement.className = document.documentElement.className.replace('no-js', 'js');</script>\n";
}
add_action('wp_head', 'retail_trade_scanner_js_detection', 0);

/**
 * Security Headers
 */
function retail_trade_scanner_security_headers() {
    if (!is_admin()) {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}
add_action('send_headers', 'retail_trade_scanner_security_headers');