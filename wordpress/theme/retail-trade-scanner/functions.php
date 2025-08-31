<?php
/**
 * Retail Trade Scanner Theme functions
 */

if (!defined('ABSPATH')) { exit; }

function rts_setup() {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('automatic-feed-links');
  register_nav_menus([
    'primary' => __('Primary Menu', 'rts'),
    'footer'  => __('Footer Menu', 'rts'),
  ]);
}
add_action('after_setup_theme', 'rts_setup');

function rts_enqueue_assets() {
  // Google fonts
  wp_enqueue_style('rts-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap', [], null);
  // Theme CSS
  wp_enqueue_style('rts-style', get_stylesheet_uri(), [], wp_get_theme()->get('Version'));
  $theme_css = get_template_directory_uri() . '/assets/css/theme.css';
  if (file_exists(get_template_directory() . '/assets/css/theme.css')) {
    wp_enqueue_style('rts-theme', $theme_css, ['rts-style'], wp_get_theme()->get('Version'));
  }

  // Theme JS
  wp_enqueue_script('rts-theme', get_template_directory_uri() . '/assets/js/theme.js', ['jquery'], wp_get_theme()->get('Version'), true);

  // REST endpoints (assume plugin registers routes under stock-scanner/v1)
  $endpoints = apply_filters('rts_endpoints', [
    'alerts_create' => rest_url('stock-scanner/v1/alerts/create'),
    'alerts_list' => rest_url('stock-scanner/v1/alerts'),
    'trending' => rest_url('stock-scanner/v1/trending'),
    'market_stats' => rest_url('stock-scanner/v1/market-stats'),
    'stocks' => rest_url('stock-scanner/v1/stocks'),
    'search' => rest_url('stock-scanner/v1/search'),
    'notifications_history' => rest_url('stock-scanner/v1/notifications/history'),
    'notifications_mark_read' => rest_url('stock-scanner/v1/notifications/mark-read'),
    'portfolio' => rest_url('stock-scanner/v1/portfolio'),
    'portfolio_add' => rest_url('stock-scanner/v1/portfolio/add'),
    'watchlist' => rest_url('stock-scanner/v1/watchlist'),
    'watchlist_add' => rest_url('stock-scanner/v1/watchlist/add'),
  ]);

  wp_localize_script('rts-theme', 'RTS', [
    'rest' => [
      'root' => esc_url_raw(rest_url()),
      'nonce' => wp_create_nonce('wp_rest'),
      'endpoints' => $endpoints,
    ],
    'theme' => [
      'palette' => [
        'background' => '#f7fff7', 'foreground' => '#32373b', 'accent' => '#ef8354', 'secondary' => '#6ca6c1', 'muted' => '#e8efe9', 'border' => '#d6dde1'
      ]
    ]
  ]);
}
add_action('wp_enqueue_scripts', 'rts_enqueue_assets');

// Utility: set a primary menu fallback
function rts_menu_fallback() {
  echo '<ul class="menu"><li><a href="' . esc_url(home_url('/')) . '">Home</a></li></ul>';
}