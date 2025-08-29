<?php
/**
 * Theme functions and definitions (extended)
 */
if (!defined('ABSPATH')) { exit; }

require_once get_template_directory() . '/functions.php';

// Enqueue integration JS and pass API base from plugin settings if present
add_action('wp_enqueue_scripts', function(){
  $api_url = get_option('stock_scanner_api_url', '');
  $revenue_base = $api_url ? trailingslashit(str_replace('/api/', '/revenue/', $api_url)) : '';
  wp_enqueue_script('rts-theme-js', get_template_directory_uri() . '/assets/js/theme-integration.js', [], wp_get_theme()->get('Version'), true);
  wp_localize_script('rts-theme-js', 'rtsConfig', [
    'apiBase' => trailingslashit($api_url),
    'revenueBase' => $revenue_base,
  ]);
}, 20);