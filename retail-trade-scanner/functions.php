<?php
/**
 * Theme functions and definitions
 *
 * Production hardening + Compatibility with Stock Scanner Integration plugin (plugin-only branch)
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

// i18n
add_action('after_setup_theme', function(){
  load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages');
});

// Theme setup: supports and menus
add_action('after_setup_theme', function () {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('custom-logo', [
    'height'      => 48,
    'width'       => 48,
    'flex-height' => true,
    'flex-width'  => true,
  ]);
  add_theme_support('align-wide');
  add_theme_support('html5', ['search-form','gallery','caption','style','script','navigation-widgets']);
  add_theme_support('editor-styles');
  add_editor_style('editor-style.css');

  // Image sizes
  add_image_size('card-thumb', 800, 450, true);

  register_nav_menus([
    'primary' => __('Primary Navigation', 'retail-trade-scanner'),
    'footer'  => __('Footer Navigation', 'retail-trade-scanner'),
  ]);
}, 5);

// Assign plugin-created menu to theme locations if present and locations unassigned
add_action('after_setup_theme', function(){
  // Only run in non-CLI context
  if (defined('WP_CLI') && WP_CLI) { return; }

  $locations = get_nav_menu_locations();
  $need_primary = empty($locations['primary']);
  $need_footer  = empty($locations['footer']);
  if (!$need_primary && !$need_footer) { return; }

  $menu = wp_get_nav_menu_object('Stock Scanner Menu');
  if (!$menu) { return; }

  $menu_id = (int) $menu->term_id;
  if ($need_primary) { $locations['primary'] = $menu_id; }
  if ($need_footer)  { $locations['footer']  = $menu_id; }
  set_theme_mod('nav_menu_locations', $locations);
}, 50);

// Sidebars
add_action('widgets_init', function(){
  register_sidebar([
    'name'          => __('Primary Sidebar', 'retail-trade-scanner'),
    'id'            => 'sidebar-1',
    'description'   => __('Main sidebar area', 'retail-trade-scanner'),
    'before_widget' => '<section id="%1$s" class="widget %2$s">',
    'after_widget'  => '</section>',
    'before_title'  => '<h2 class="widget-title">',
    'after_title'   => '</h2>',
  ]);
  for ($i=1;$i<=3;$i++){
    register_sidebar([
      'name'          => sprintf(__('Footer %d', 'retail-trade-scanner'), $i),
      'id'            => 'footer-' . $i,
      'description'   => __('Footer widget area', 'retail-trade-scanner'),
      'before_widget' => '<section id="%1$s" class="widget %2$s">',
      'after_widget'  => '</section>',
      'before_title'  => '<h2 class="widget-title">',
      'after_title'   => '</h2>',
    ]);
  }
});

// Enqueue theme stylesheet
add_action('wp_enqueue_scripts', function(){
  wp_enqueue_style('retail-trade-scanner-style', get_stylesheet_uri(), [], wp_get_theme()->get('Version'));
});

// Basic Open Graph / Twitter meta
add_action('wp_head', function(){
  $title = wp_get_document_title();
  $desc  = get_bloginfo('description');
  $url   = esc_url(home_url(add_query_arg([],'')));
  $image = '';
  if (is_singular() && has_post_thumbnail()) {
    $image = esc_url( get_the_post_thumbnail_url(null, 'large') );
  }
  echo "\n<meta property=\"og:title\" content=\"" . esc_attr($title) . "\">\n";
  echo "<meta property=\"og:description\" content=\"" . esc_attr($desc) . "\">\n";
  echo "<meta property=\"og:url\" content=\"{$url}\">\n";
  if ($image) { echo "<meta property=\"og:image\" content=\"{$image}\">\n"; }
  echo "<meta name=\"twitter:card\" content=\"summary_large_image\">\n";
  echo "<meta name=\"twitter:title\" content=\"" . esc_attr($title) . "\">\n";
  echo "<meta name=\"twitter:description\" content=\"" . esc_attr($desc) . "\">\n";
  if ($image) { echo "<meta name=\"twitter:image\" content=\"{$image}\">\n"; }
}, 5);

// Theme activation hook – skip creating pages if plugin provides them
add_action('after_switch_theme', 'retail_trade_scanner_on_activate');
function retail_trade_scanner_on_activate() {
  // Prevent duplicate runs (e.g., multi-site switch)
  if (get_option('rts_activation_completed')) {
    return;
  }

  // If Stock Scanner plugin is active, rely on its page creation
  if (class_exists('StockScannerIntegration')) {
    update_option('rts_activation_completed', 1);
    // Try to bind plugin menu to theme locations if not set yet
    $locations = get_nav_menu_locations();
    $menu = wp_get_nav_menu_object('Stock Scanner Menu');
    if ($menu) {
      $menu_id = (int) $menu->term_id;
      if (empty($locations['primary'])) { $locations['primary'] = $menu_id; }
      if (empty($locations['footer']))  { $locations['footer']  = $menu_id; }
      set_theme_mod('nav_menu_locations', $locations);
    }
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

// Forms handlers (Subscribe & Contact) – keep theme forms working; can be replaced by plugin endpoints if needed
function rts_safe_redirect_back($param, $value){
  $url = wp_get_referer();
  if (!$url) { $url = home_url('/'); }
  $url = add_query_arg([$param => $value], $url);
  wp_safe_redirect($url);
  exit;
}

add_action('admin_post_nopriv_rts_subscribe', 'rts_handle_subscribe');
add_action('admin_post_rts_subscribe',        'rts_handle_subscribe');
function rts_handle_subscribe(){
  if (!isset($_POST['rts_subscribe_nonce']) || !wp_verify_nonce($_POST['rts_subscribe_nonce'], 'rts_subscribe')){
    rts_safe_redirect_back('subscribed', '0');
  }
  $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
  if (!is_email($email)) { rts_safe_redirect_back('subscribed', '0'); }
  $admin = get_option('admin_email');
  $msg = sprintf(__('New subscription: %s', 'retail-trade-scanner'), $email);
  @wp_mail($admin, __('New Subscription', 'retail-trade-scanner'), $msg);
  rts_safe_redirect_back('subscribed', '1');
}

add_action('admin_post_nopriv_rts_contact', 'rts_handle_contact');
add_action('admin_post_rts_contact',        'rts_handle_contact');
function rts_handle_contact(){
  if (!isset($_POST['rts_contact_nonce']) || !wp_verify_nonce($_POST['rts_contact_nonce'], 'rts_contact')){
    rts_safe_redirect_back('contact', 'error');
  }
  $name  = isset($_POST['name']) ? sanitize_text_field($_POST['name']) : '';
  $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
  $msg   = isset($_POST['message']) ? wp_kses_post($_POST['message']) : '';
  if (!$name || !is_email($email) || !$msg){ rts_safe_redirect_back('contact', 'invalid'); }
  $admin = get_option('admin_email');
  $subject = sprintf(__('Contact form from %s', 'retail-trade-scanner'), $name);
  $body = sprintf("Name: %s\nEmail: %s\n\n%s", $name, $email, wp_strip_all_tags($msg));
  @wp_mail($admin, $subject, $body);
  rts_safe_redirect_back('contact', 'sent');
}

// If plugin is active but API not configured, gently surface an admin notice in frontend for administrators
add_action('wp_footer', function(){
  if (!current_user_can('manage_options')) { return; }
  if (!class_exists('StockScannerIntegration')) { return; }
  $api_url = get_option('stock_scanner_api_url', '');
  $api_secret = get_option('stock_scanner_api_secret', '');
  if (empty($api_url) || empty($api_secret)) {
    echo '<div style="position:fixed;bottom:12px;right:12px;background:#111827;color:#fff;padding:10px 14px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.3);z-index:9999;opacity:.9">'
       . esc_html__('Stock Scanner plugin needs configuration: set API URL and Secret in Settings → Stock Scanner.', 'retail-trade-scanner')
       . '</div>';
  }
});