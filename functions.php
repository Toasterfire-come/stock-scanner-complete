<?php
/**
 * Stock Scanner Pro Theme Functions v3.0.0
 * COMPLETE JAVASCRIPT OVERHAUL - Enhanced Functions
 * 100% Vanilla JavaScript enforced across ALL PAGES
 * Advanced dependency chain and performance optimizations
 */

// Prevent direct access
if (!defined('ABSPATH')) { exit; }

// Theme constants
define('STOCK_SCANNER_VERSION', '3.0.0');
define('STOCK_SCANNER_THEME_DIR', get_template_directory());
define('STOCK_SCANNER_THEME_URI', get_template_directory_uri());

/**
 * Theme setup and support
 */
function stock_scanner_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form','comment-form','comment-list','gallery','caption','style','script'));
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('responsive-embeds');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
    register_nav_menus(array('primary' => __('Primary Menu', 'stock-scanner'), 'footer'  => __('Footer Menu', 'stock-scanner')));
    add_image_size('stock-scanner-featured', 800, 450, true);
    add_image_size('stock-scanner-thumbnail', 300, 200, true);
}
add_action('after_setup_theme', 'stock_scanner_setup');

/**
 * ===== ENHANCED JAVASCRIPT LOADING v3.0.0 =====
 */
function stock_scanner_enqueue_scripts() {
    // Remove jQuery
    wp_deregister_script('jquery');
    wp_deregister_script('jquery-migrate');

    // Base stylesheet (kept for theme header recognition, will be dequeued below)
    wp_enqueue_style(
        'stock-scanner-style',
        get_stylesheet_uri(),
        array(),
        STOCK_SCANNER_VERSION . '-' . time(),
        'all'
    );

    // Enhanced premium styles (will be dequeued below)
    wp_enqueue_style(
        'stock-scanner-enhanced-styles',
        STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css',
        array('stock-scanner-style'),
        STOCK_SCANNER_VERSION . '-enhanced',
        'all'
    );

    // Compatibility layer (will be dequeued below)
    if (file_exists(STOCK_SCANNER_THEME_DIR . '/assets/css/compat.css')) {
        wp_enqueue_style(
            'stock-scanner-compat',
            STOCK_SCANNER_THEME_URI . '/assets/css/compat.css',
            array('stock-scanner-enhanced-styles'),
            STOCK_SCANNER_VERSION . '-compat',
            'all'
        );
    }

    // Vanilla JS modules
    wp_enqueue_script(
        'stock-scanner-theme-enhanced',
        STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js',
        array(),
        STOCK_SCANNER_VERSION . '-enhanced',
        true
    );

    // NEW: inject all CSS via JS
    wp_enqueue_script(
        'stock-scanner-styles-injector',
        STOCK_SCANNER_THEME_URI . '/js/styles-injector.js',
        array('stock-scanner-theme-enhanced'),
        STOCK_SCANNER_VERSION . '-styles-inject',
        true
    );

    // Ensure styles are not double-applied: move CSS to JS by dequeuing CSS styles
    wp_dequeue_style('stock-scanner-compat');
    wp_dequeue_style('stock-scanner-enhanced-styles');
    wp_dequeue_style('stock-scanner-style');

    // Preload signals (kept)
    add_action('wp_head', function() {
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js" as="script">';
        echo '<link rel="preload" href="' . STOCK_SCANNER_THEME_URI . '/js/styles-injector.js" as="script">';
    }, 1);
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');

/** Force remove jQuery on frontend */
function stock_scanner_remove_jquery() {
    if (!is_admin()) {
        wp_deregister_script('jquery');
        wp_deregister_script('jquery-migrate');
        wp_deregister_script('jquery-core');
        wp_deregister_script('jquery-ui-core');
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_remove_jquery', 1);

// ... the remainder of functions.php stays unchanged (widgets, walkers, CPTs, etc.)