<?php
/**
 * Theme functions and definitions
 *
 * Adds an activation routine that creates required pages if they do not exist
 * and assigns appropriate page templates when available. It will not overwrite
 * existing content.
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

// Theme activation hook
add_action('after_switch_theme', 'retail_trade_scanner_on_activate');

/**
 * Run on theme activation.
 * - Creates required pages if they don't exist
 * - Assigns page templates when corresponding template files are present
 * - Does not overwrite existing page content
 */
function retail_trade_scanner_on_activate() {
  // Prevent duplicate runs (e.g., multi-site switch)
  if (get_option('rts_activation_completed')) {
    return;
  }

  $pages = [
    [ 'slug' => 'dashboard',        'title' => __('Dashboard', 'retail-trade-scanner'),      'template' => 'templates/pages/page-dashboard.php' ],
    [ 'slug' => 'scanner',          'title' => __('Scanner', 'retail-trade-scanner'),        'template' => 'templates/pages/page-scanner.php' ],
    [ 'slug' => 'watchlists',       'title' => __('Watchlists', 'retail-trade-scanner'),     'template' => 'templates/pages/page-watchlists.php' ],
    [ 'slug' => 'portfolio',        'title' => __('Portfolio', 'retail-trade-scanner'),      'template' => 'templates/pages/page-portfolio.php' ],
    [ 'slug' => 'alerts',           'title' => __('Alerts', 'retail-trade-scanner'),         'template' => 'templates/pages/page-alerts.php' ],
    [ 'slug' => 'news',             'title' => __('News', 'retail-trade-scanner'),           'template' => 'templates/pages/page-news.php' ],
    [ 'slug' => 'api-docs',         'title' => __('API Docs', 'retail-trade-scanner'),       'template' => 'templates/pages/page-api-docs.php' ],
    [ 'slug' => 'help',             'title' => __('Help', 'retail-trade-scanner'),           'template' => 'templates/pages/page-help.php' ],
    [ 'slug' => 'tutorials',        'title' => __('Tutorials', 'retail-trade-scanner'),      'template' => 'templates/pages/page-tutorials.php' ],
    [ 'slug' => 'careers',          'title' => __('Careers', 'retail-trade-scanner'),        'template' => 'templates/pages/page-careers.php' ],
    [ 'slug' => 'privacy-policy',   'title' => __('Privacy Policy', 'retail-trade-scanner'), 'template' => 'templates/pages/page-privacy-policy.php' ],
    [ 'slug' => 'terms-of-service', 'title' => __('Terms of Service', 'retail-trade-scanner'),'template' => 'templates/pages/page-terms-of-service.php' ],
    [ 'slug' => 'disclaimer',       'title' => __('Disclaimer', 'retail-trade-scanner'),     'template' => 'templates/pages/page-disclaimer.php' ],
    [ 'slug' => 'contact',          'title' => __('Contact', 'retail-trade-scanner'),        'template' => 'templates/pages/page-contact.php' ],
  ];

  foreach ( $pages as $page ) {
    $slug     = sanitize_title( $page['slug'] );
    $title    = sanitize_text_field( $page['title'] );
    $template = isset($page['template']) ? $page['template'] : '';

    $existing = get_page_by_path( $slug );

    if ( ! $existing ) {
      // Create page if it doesn't exist
      $postarr = [
        'post_title'   => $title,
        'post_name'    => $slug,
        'post_status'  => 'publish',
        'post_type'    => 'page',
        'post_content' => '', // no content; won't overwrite anything existing
      ];
      $page_id = wp_insert_post( $postarr );

      if ( $page_id && ! is_wp_error( $page_id ) && $template ) {
        // Assign template only if the template file exists in the theme
        if ( file_exists( get_theme_file_path( $template ) ) ) {
          update_post_meta( $page_id, '_wp_page_template', $template );
        }
      }
    } else {
      // Page exists – optional: set template if not already set and file exists
      if ( $template && file_exists( get_theme_file_path( $template ) ) ) {
        $current_tpl = get_page_template_slug( $existing->ID );
        if ( empty( $current_tpl ) || $current_tpl === 'default' ) {
          update_post_meta( $existing->ID, '_wp_page_template', $template );
        }
      }
    }
  }

  update_option('rts_activation_completed', 1);
}