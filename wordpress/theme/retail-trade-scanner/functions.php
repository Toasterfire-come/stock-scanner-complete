<?php
/**
 * Retail Trade Scanner Theme functions
 */

if (!defined('ABSPATH')) { exit; }

require_once get_template_directory() . '/inc/auto-pages.php';
require_once get_template_directory() . '/inc/seo-schema.php';
require_once get_template_directory() . '/inc/meta-tags.php';

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

function rts_asset_ver($path) {
  $file = get_template_directory() . $path;
  return file_exists($file) ? filemtime($file) : wp_get_theme()->get('Version');
}

function rts_enqueue_assets() {
  // Google fonts
  wp_enqueue_style('rts-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap', [], null);
  // Theme CSS (base)
  wp_enqueue_style('rts-style', get_stylesheet_uri(), [], rts_asset_ver('/style.css'));
  // Optional built CSS bundle
  if (file_exists(get_template_directory() . '/assets/css/theme.css')) {
    wp_enqueue_style('rts-theme', get_template_directory_uri() . '/assets/css/theme.css', ['rts-style'], rts_asset_ver('/assets/css/theme.css'));
  }

  // Theme JS
  wp_enqueue_script('rts-theme', get_template_directory_uri() . '/assets/js/theme.js', ['jquery'], rts_asset_ver('/assets/js/theme.js'), true);

  // REST endpoints (assume plugin registers routes under stock-scanner/v1)
  $endpoints = apply_filters('rts_endpoints', [
    'health' => rest_url('stock-scanner/v1/health'),
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
    'portfolio_delete' => rest_url('stock-scanner/v1/portfolio/delete'),
    'watchlist' => rest_url('stock-scanner/v1/watchlist'),
    'watchlist_add' => rest_url('stock-scanner/v1/watchlist/add'),
    'watchlist_delete' => rest_url('stock-scanner/v1/watchlist/delete'),
    'subscription' => rest_url('stock-scanner/v1/subscription'),
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