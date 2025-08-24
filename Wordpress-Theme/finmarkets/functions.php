<?php
/**
 * FinMarkets Theme setup
 */
if (!defined('ABSPATH')) { exit; }

add_action('after_setup_theme', function () {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('html5', ['search-form', 'gallery', 'caption', 'script', 'style']);
  register_nav_menus([
    'primary' => __('Primary Menu', 'finmarkets'),
    'footer' => __('Footer Menu', 'finmarkets')
  ]);
});

/**
 * Enqueue styles and scripts (vanilla, deferred)
 */
add_action('wp_enqueue_scripts', function () {
  // Inter from Google Fonts
  wp_enqueue_style('finmarkets-inter', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap', [], null);
  // Main theme stylesheet
  wp_enqueue_style('finmarkets-style', get_stylesheet_uri(), ['finmarkets-inter'], wp_get_theme()->get('Version'));

  // Mock data for frontend-only experience (no external APIs yet)
  wp_enqueue_script('finmarkets-mock', get_template_directory_uri() . '/assets/js/mock.js', [], wp_get_theme()->get('Version'), true);
});

/**
 * Add 'defer' to our scripts for better performance
 */
add_filter('script_loader_tag', function ($tag, $handle, $src) {
  $defer_handles = ['finmarkets-mock'];
  if (in_array($handle, $defer_handles, true)) {
    return '<script src="' . esc_url($src) . '" defer></script>';
  }
  return $tag;
}, 10, 3);

/**
 * Basic security hardening via headers (theme-level, limited). Recommend server-level CSP and HSTS.
 */
add_action('send_headers', function () {
  // Frameguard
  header('X-Frame-Options: SAMEORIGIN');
  // XSS Protection (legacy)
  header('X-XSS-Protection: 1; mode=block');
  // Content Type sniffing
  header('X-Content-Type-Options: nosniff');
});