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
 * Compatibility: allow jQuery when required by active plugins (e.g., Stock Scanner Integration)
 */
function stock_scanner_plugin_uses_jquery() {
    // If the integration plugin is active (class exists) or any code opts in via filter, keep jQuery
    return class_exists('StockScannerIntegration') || apply_filters('stock_scanner_allow_jquery', false);
}

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
 * ===== ENHANCED JAVASCRIPT LOADING v3.0.0 - FIXED CSS LOADING =====
 */
function stock_scanner_enqueue_scripts() {
    // Remove jQuery unless a plugin requires it
    if (!stock_scanner_plugin_uses_jquery()) {
        wp_deregister_script('jquery');
        wp_deregister_script('jquery-migrate');
    }

    // Main stylesheet - KEEP THIS LOADED
    wp_enqueue_style(
        'stock-scanner-style',
        get_stylesheet_uri(),
        array(),
        STOCK_SCANNER_VERSION . '-' . time(),
        'all'
    );

    // Google Fonts
    wp_enqueue_style(
        'stock-scanner-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
        array(),
        STOCK_SCANNER_VERSION,
        'all'
    );

    // Enhanced premium styles - CREATE AND LOAD
    wp_enqueue_style(
        'stock-scanner-enhanced-styles',
        STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css',
        array('stock-scanner-style'),
        STOCK_SCANNER_VERSION . '-enhanced',
        'all'
    );

    // Vanilla JS modules (ensure jQuery conflict-free if present)
    wp_enqueue_script(
        'stock-scanner-theme-enhanced',
        STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js',
        stock_scanner_plugin_uses_jquery() ? array('jquery') : array(),
        STOCK_SCANNER_VERSION . '-enhanced',
        true
    );

    // Localize script for AJAX
    wp_localize_script('stock-scanner-theme-enhanced', 'stockScannerAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_nonce'),
        'homeUrl' => home_url('/'),
        'themeUrl' => STOCK_SCANNER_THEME_URI
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_enqueue_scripts');

/** Adjust jQuery handling on frontend for plugin compatibility */
function stock_scanner_adjust_jquery() {
    if (!is_admin() && !stock_scanner_plugin_uses_jquery()) {
        wp_deregister_script('jquery');
        wp_deregister_script('jquery-migrate');
        wp_deregister_script('jquery-core');
        wp_deregister_script('jquery-ui-core');
    } else {
        // Ensure jQuery is available if a plugin relies on it
        wp_enqueue_script('jquery');
    }
}
add_action('wp_enqueue_scripts', 'stock_scanner_adjust_jquery', 1);

// ... the remainder of functions.php stays unchanged (widgets, walkers, CPTs, etc.)