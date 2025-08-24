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
        STOCK_SCANNER_VERSION,
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
    $enhanced_css_path = STOCK_SCANNER_THEME_DIR . '/assets/css/enhanced-styles.css';
    if (file_exists($enhanced_css_path)) {
        wp_enqueue_style(
            'stock-scanner-enhanced-styles',
            STOCK_SCANNER_THEME_URI . '/assets/css/enhanced-styles.css',
            array('stock-scanner-style'),
            STOCK_SCANNER_VERSION,
            'all'
        );
    }

    // Vanilla JS modules (ensure jQuery conflict-free if present)
    $enhanced_js_path = STOCK_SCANNER_THEME_DIR . '/js/theme-enhanced.js';
    if (file_exists($enhanced_js_path)) {
        wp_enqueue_script(
            'stock-scanner-theme-enhanced',
            STOCK_SCANNER_THEME_URI . '/js/theme-enhanced.js',
            stock_scanner_plugin_uses_jquery() ? array('jquery') : array(),
            STOCK_SCANNER_VERSION,
            true
        );
        
        // Add async/defer for performance
        add_filter('script_loader_tag', function($tag, $handle) {
            if ($handle === 'stock-scanner-theme-enhanced') {
                return str_replace(' src', ' defer src', $tag);
            }
            return $tag;
        }, 10, 2);
        
        // Localize script for AJAX
        wp_localize_script('stock-scanner-theme-enhanced', 'stockScannerAjax', array(
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
            'homeUrl' => home_url('/'),
            'themeUrl' => STOCK_SCANNER_THEME_URI
        ));
    }
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

/**
 * Production Performance Optimizations
 */
function stock_scanner_performance_optimizations() {
    // Remove WordPress emoji scripts and styles
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_styles', 'print_emoji_styles');
    remove_filter('the_content_feed', 'wp_staticize_emoji');
    remove_filter('comment_text_rss', 'wp_staticize_emoji');
    remove_filter('wp_mail', 'wp_staticize_emoji_for_email');
    
    // Remove WordPress block editor styles on front end if not needed
    if (!is_admin()) {
        wp_dequeue_style('wp-block-library');
        wp_dequeue_style('wp-block-library-theme');
        wp_dequeue_style('wc-block-style');
    }
    
    // Optimize Google Fonts loading
    add_filter('style_loader_tag', function($html, $handle) {
        if ($handle === 'stock-scanner-fonts') {
            return str_replace("rel='stylesheet'", "rel='preload' as='style' onload=\"this.onload=null;this.rel='stylesheet'\"", $html) . 
                   '<noscript>' . $html . '</noscript>';
        }
        return $html;
    }, 10, 2);
}
add_action('init', 'stock_scanner_performance_optimizations');

/**
 * Security Headers for Production
 */
function stock_scanner_security_headers() {
    if (!is_admin()) {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}
add_action('send_headers', 'stock_scanner_security_headers');

/**
 * Clean up WordPress head for production
 */
function stock_scanner_clean_head() {
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'start_post_rel_link');
    remove_action('wp_head', 'index_rel_link');
    remove_action('wp_head', 'adjacent_posts_rel_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    remove_action('wp_head', 'rest_output_link_wp_head');
    remove_action('wp_head', 'wp_oembed_add_discovery_links');
}
add_action('after_setup_theme', 'stock_scanner_clean_head');

/**
 * Optimize images for production
 */
function stock_scanner_optimize_images() {
    // Enable WebP support if available
    add_filter('wp_image_editors', function($editors) {
        return array('WP_Image_Editor_Imagick', 'WP_Image_Editor_GD');
    });
    
    // Add loading="lazy" to images
    add_filter('wp_get_attachment_image_attributes', function($attr) {
        if (!isset($attr['loading'])) {
            $attr['loading'] = 'lazy';
        }
        if (!isset($attr['decoding'])) {
            $attr['decoding'] = 'async';
        }
        return $attr;
    });
}
add_action('init', 'stock_scanner_optimize_images');

// ... the remainder of functions.php stays unchanged (widgets, walkers, CPTs, etc.)