<?php
/**
 * Retail Trade Scanner Theme – Production Functions (Enhanced)
 * Version: 2.0.0 - Production Ready
 */
if (!defined('ABSPATH')) { exit; }

// Production-ready includes
require_once get_template_directory() . '/inc/security.php';
require_once get_template_directory() . '/inc/performance.php';
require_once get_template_directory() . '/inc/seo-analytics.php';
require_once get_template_directory() . '/inc/error-handling.php';
require_once get_template_directory() . '/inc/wordpress-standards.php';
require_once get_template_directory() . '/inc/browser-support.php';
require_once get_template_directory() . '/inc/monitoring.php';
require_once get_template_directory() . '/inc/plugin-integration.php';

// i18n
add_action('after_setup_theme', function(){ load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages'); });

// Theme setup
add_action('after_setup_theme', 'rts_theme_setup');
function rts_theme_setup() {
    // Add theme support for various features
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('title-tag');
    add_theme_support('customize-selective-refresh-widgets');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Navigation', 'retail-trade-scanner'),
        'footer' => __('Footer Navigation', 'retail-trade-scanner'),
        'social' => __('Social Media Menu', 'retail-trade-scanner'),
    ));
}

// Enqueue scripts and styles
add_action('wp_enqueue_scripts', 'rts_enqueue_assets');
function rts_enqueue_assets() {
    $theme_version = wp_get_theme()->get('Version');
    
    // Main stylesheet
    wp_enqueue_style('rts-style', get_stylesheet_uri(), array(), $theme_version);
    
    // Main JavaScript
    wp_enqueue_script('rts-theme-js', get_template_directory_uri() . '/assets/js/theme-integration.js', array('jquery'), $theme_version, true);
    wp_enqueue_script('rts-mobile-js', get_template_directory_uri() . '/assets/js/mobile-enhancements.js', array(), $theme_version, true);
    
    // Localize script
    wp_localize_script('rts-theme-js', 'rtsAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('rts_nonce'),
        'strings' => array(
            'loading' => __('Loading...', 'retail-trade-scanner'),
            'error' => __('An error occurred. Please try again.', 'retail-trade-scanner'),
            'success' => __('Success!', 'retail-trade-scanner'),
        ),
    ));
}

// Create essential pages on theme activation
add_action('after_switch_theme', 'rts_create_essential_pages');
function rts_create_essential_pages() {
    $pages = array(
        'dashboard' => array(
            'title' => __('Dashboard', 'retail-trade-scanner'),
            'template' => 'page-dashboard'
        ),
        'scanner' => array(
            'title' => __('Stock Scanner', 'retail-trade-scanner'),
            'template' => 'page-scanner'
        ),
        'portfolio' => array(
            'title' => __('Portfolio', 'retail-trade-scanner'),
            'template' => 'page-portfolio'
        ),
        'watchlists' => array(
            'title' => __('Watchlists', 'retail-trade-scanner'),
            'template' => 'page-watchlists'
        ),
        'alerts' => array(
            'title' => __('Price Alerts', 'retail-trade-scanner'),
            'template' => 'page-alerts'
        ),
        'news' => array(
            'title' => __('Market News', 'retail-trade-scanner'),
            'template' => 'page-news'
        ),
        'tutorials' => array(
            'title' => __('Tutorials', 'retail-trade-scanner'),
            'template' => 'page-tutorials'
        ),
        'help' => array(
            'title' => __('Help Center', 'retail-trade-scanner'),
            'template' => 'page-help'
        )
    );
    
    foreach ($pages as $slug => $page_data) {
        if (!get_page_by_path($slug)) {
            wp_insert_post(array(
                'post_title' => $page_data['title'],
                'post_name' => $slug,
                'post_content' => '',
                'post_status' => 'publish',
                'post_type' => 'page',
                'meta_input' => array(
                    '_wp_page_template' => 'templates/pages/' . $page_data['template'] . '.php'
                )
            ));
        }
    }
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

// AJAX handlers for theme functionality
add_action('wp_ajax_rts_subscribe', 'rts_handle_subscription');
add_action('wp_ajax_nopriv_rts_subscribe', 'rts_handle_subscription');
function rts_handle_subscription() {
    // Security check
    if (!wp_verify_nonce($_POST['rts_subscribe_nonce'] ?? '', 'rts_subscribe')) {
        wp_die(__('Security check failed.', 'retail-trade-scanner'));
    }
    
    $email = sanitize_email($_POST['email'] ?? '');
    
    if (!is_email($email)) {
        wp_send_json_error(__('Please enter a valid email address.', 'retail-trade-scanner'));
    }
    
    // Store subscription (this would typically integrate with an email service)
    $subscriptions = get_option('rts_subscriptions', array());
    
    if (!in_array($email, $subscriptions)) {
        $subscriptions[] = $email;
        update_option('rts_subscriptions', $subscriptions);
        
        // Send notification email to admin
        $admin_email = get_option('admin_email');
        $subject = sprintf(__('[%s] New Newsletter Subscription', 'retail-trade-scanner'), get_bloginfo('name'));
        $message = sprintf(__('New subscription: %s', 'retail-trade-scanner'), $email);
        wp_mail($admin_email, $subject, $message);
        
        wp_send_json_success(__('Thank you for subscribing!', 'retail-trade-scanner'));
    } else {
        wp_send_json_error(__('You are already subscribed.', 'retail-trade-scanner'));
    }
}

// Health status endpoint for monitoring
add_action('wp_ajax_rts_health_status', 'rts_health_status_endpoint');
add_action('wp_ajax_nopriv_rts_health_status', 'rts_health_status_endpoint');
function rts_health_status_endpoint() {
    // Simple health check
    $health = array(
        'status' => 'healthy',
        'timestamp' => current_time('c'),
        'version' => wp_get_theme()->get('Version'),
        'php_version' => PHP_VERSION,
        'wp_version' => get_bloginfo('version'),
        'memory_usage' => memory_get_peak_usage(true),
        'memory_limit' => wp_convert_hr_to_bytes(ini_get('memory_limit')),
    );
    
    // Check database connection
    global $wpdb;
    $db_check = $wpdb->get_var('SELECT 1');
    if ($db_check !== '1') {
        $health['status'] = 'unhealthy';
        $health['issues'][] = 'Database connection failed';
    }
    
    wp_send_json($health);
}

// Custom body classes
add_filter('body_class', 'rts_body_classes');
function rts_body_classes($classes) {
    // Add sidebar state class
    if (is_page(array('dashboard', 'scanner', 'portfolio', 'watchlists', 'alerts', 'news'))) {
        $classes[] = 'has-sidebar';
    }
    
    // Add page-specific classes
    if (is_front_page()) {
        $classes[] = 'home-page';
    }
    
    return $classes;
}

// Theme activation hook
add_action('after_switch_theme', 'rts_theme_activation');
function rts_theme_activation() {
    // Set default customizer values
    set_theme_mod('rts_primary_color', '#374a67');
    set_theme_mod('rts_accent_color', '#e15554');
    set_theme_mod('rts_font_size', 16);
    set_theme_mod('rts_container_width', 1200);
    set_theme_mod('rts_sidebar_position', 'right');
    
    // Log theme activation
    if (function_exists('rts_log_system_event')) {
        rts_log_system_event('theme_activated', array(
            'theme' => 'Retail Trade Scanner',
            'version' => wp_get_theme()->get('Version')
        ));
    }
}

// Theme deactivation cleanup
add_action('switch_theme', 'rts_theme_deactivation');
function rts_theme_deactivation() {
    // Clear scheduled events
    wp_clear_scheduled_hook('rts_daily_health_check');
    wp_clear_scheduled_hook('rts_weekly_maintenance');
    
    // Log theme deactivation
    if (function_exists('rts_log_system_event')) {
        rts_log_system_event('theme_deactivated', array(
            'theme' => 'Retail Trade Scanner',
            'version' => wp_get_theme()->get('Version')
        ));
    }
}

// Add theme version to admin footer
add_filter('admin_footer_text', 'rts_admin_footer_text');
function rts_admin_footer_text($text) {
    $theme = wp_get_theme();
    return $text . ' | ' . $theme->get('Name') . ' v' . $theme->get('Version');
}

// Production-ready error handling
if (!WP_DEBUG) {
    // Hide errors from visitors in production
    ini_set('display_errors', 0);
    error_reporting(0);
    
    // Custom error page for fatal errors
    register_shutdown_function('rts_fatal_error_handler');
    function rts_fatal_error_handler() {
        $error = error_get_last();
        if ($error && in_array($error['type'], array(E_ERROR, E_CORE_ERROR, E_COMPILE_ERROR, E_PARSE))) {
            if (!headers_sent()) {
                header('HTTP/1.1 500 Internal Server Error');
                header('Content-Type: text/html; charset=utf-8');
            }
            
            include get_template_directory() . '/templates/error-500.php';
            exit;
        }
    }
}

// Performance optimization hooks
add_action('wp_head', 'rts_performance_hints', 1);
function rts_performance_hints() {
    // DNS prefetch for external resources
    echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">' . "\n";
    echo '<link rel="dns-prefetch" href="//fonts.gstatic.com">' . "\n";
    
    // Preload critical resources
    echo '<link rel="preload" href="' . get_stylesheet_uri() . '" as="style">' . "\n";
    echo '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" as="style">' . "\n";
}

// Security headers
add_action('send_headers', 'rts_security_headers');
function rts_security_headers() {
    if (!is_admin()) {
        header('X-Frame-Options: SAMEORIGIN');
        header('X-Content-Type-Options: nosniff');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');
    }
}

// Log theme load time for monitoring
if (WP_DEBUG) {
    add_action('wp_footer', 'rts_log_load_time');
    function rts_log_load_time() {
        $load_time = timer_stop(0, 3);
        if ($load_time > 2.0) {
            error_log("RTS Theme: Slow load time detected - {$load_time}s on " . $_SERVER['REQUEST_URI']);
        }
    }
}

// Theme setup: supports, editor, menus
add_action('after_setup_theme', function () {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('custom-logo', [ 'height'=>48, 'width'=>48, 'flex-height'=>true, 'flex-width'=>true ]);
  add_theme_support('align-wide');
  add_theme_support('html5', ['search-form','gallery','caption','style','script','navigation-widgets']);
  add_theme_support('editor-styles');
  add_editor_style('editor-style.css');
  add_image_size('card-thumb', 800, 450, true);
  register_nav_menus([ 'primary' => __('Primary Navigation', 'retail-trade-scanner'), 'footer' => __('Footer Navigation', 'retail-trade-scanner') ]);
}, 5);

// Add aria-current to current menu links
add_filter('nav_menu_link_attributes', function($atts, $item){ if (!empty($item->current)) { $atts['aria-current'] = 'page'; } return $atts; }, 10, 2);

// Bind plugin-created menu to theme locations if available
add_action('after_setup_theme', function(){ if (defined('WP_CLI') && WP_CLI) { return; } $locations = get_nav_menu_locations(); $need_primary = empty($locations['primary']); $need_footer  = empty($locations['footer']); if (!$need_primary && !$need_footer) return; $menu = wp_get_nav_menu_object('Stock Scanner Menu'); if (!$menu) return; $menu_id = (int) $menu->term_id; if ($need_primary) $locations['primary'] = $menu_id; if ($need_footer)  $locations['footer']  = $menu_id; set_theme_mod('nav_menu_locations', $locations); }, 50);

// Sidebars
add_action('widgets_init', function(){ register_sidebar([ 'name' => __('Primary Sidebar', 'retail-trade-scanner'), 'id'=>'sidebar-1', 'description'=>__('Main sidebar area','retail-trade-scanner'), 'before_widget'=>'<section id="%1$s" class="widget %2$s">', 'after_widget'=>'</section>', 'before_title'=>'<h2 class="widget-title">', 'after_title'=>'</h2>' ]); for ($i=1;$i<=3;$i++){ register_sidebar([ 'name'=>sprintf(__('Footer %d', 'retail-trade-scanner'), $i), 'id'=>'footer-'.$i, 'description'=>__('Footer widget area','retail-trade-scanner'), 'before_widget'=>'<section id="%1$s" class="widget %2$s">', 'after_widget'=>'</section>', 'before_title'=>'<h2 class="widget-title">', 'after_title'=>'</h2>' ]); } });

// Performance optimization: CSS/JS minification and optimization
add_action('wp_enqueue_scripts', function(){
  $ver = wp_get_theme()->get('Version');
  $is_debug = defined('WP_DEBUG') && WP_DEBUG;
  
  // Enqueue main stylesheet with optimization
  wp_enqueue_style('retail-trade-scanner-style', get_stylesheet_uri(), [], $ver);
  
  // Add performance optimizations for production
  if (!$is_debug) {
    // Add resource hints for better performance
    add_action('wp_head', function() {
      echo '<link rel="preload" href="' . get_stylesheet_uri() . '" as="style">';
      echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">';
    }, 1);
  }
  
  // API configuration
  $api_url = get_option('stock_scanner_api_url', '');
  $revenue_base = $api_url ? trailingslashit(str_replace('/api/', '/revenue/', $api_url)) : '';
  
  // Enqueue JavaScript with optimization
  $js_path = get_template_directory() . '/assets/js/theme-integration.js';
  $js_url  = get_template_directory_uri() . '/assets/js/theme-integration.js';
  
  if (file_exists($js_path)){
    // Load JS in footer for better performance
    wp_enqueue_script('rts-theme-js', $js_url, [], $ver, true);
    
    // Localize script with configuration
    wp_localize_script('rts-theme-js', 'rtsConfig', [
      'apiBase' => trailingslashit($api_url),
      'revenueBase' => $revenue_base,
      'isDebug' => $is_debug,
      'ajaxUrl' => admin_url('admin-ajax.php'),
      'nonce' => wp_create_nonce('rts_nonce')
    ]);
  }
  
  // Enqueue mobile enhancements
  $mobile_js_path = get_template_directory() . '/assets/js/mobile-enhancements.js';
  $mobile_js_url  = get_template_directory_uri() . '/assets/js/mobile-enhancements.js';
  
  if (file_exists($mobile_js_path)){
    wp_enqueue_script('rts-mobile-js', $mobile_js_url, [], $ver, true);
  }
}, 20);

// Add critical CSS inline for above-the-fold content with new color scheme
add_action('wp_head', function() {
  if (!is_admin()) {
    echo '<style id="critical-css">
      :root{
        --drab-dark-brown:#433e0e;
        --yinmn-blue:#374a67;
        --indian-red:#e15554;
        --silver:#c1bdb3;
        --davys-gray:#5f5b6b;
        --background:var(--drab-dark-brown);
        --foreground:var(--silver);
        --primary:var(--yinmn-blue);
        --accent:var(--indian-red);
        --border:rgba(193,189,179,0.2);
        --sidebar-width:280px;
        --sidebar-collapsed:64px;
        --header-height:64px;
      }
      *{box-sizing:border-box}
      body{
        background:var(--background);
        color:var(--foreground);
        margin:0;
        font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
        padding-left:var(--sidebar-collapsed);
        transition:padding-left 0.3s cubic-bezier(0.4,0,0.2,1);
      }
      body.sidebar-expanded{padding-left:var(--sidebar-width)}
      @media(max-width:768px){body,body.sidebar-expanded{padding-left:0}}
      .site-header{
        position:fixed;
        top:0;
        left:var(--sidebar-collapsed);
        right:0;
        height:var(--header-height);
        background:rgba(67,62,14,0.95);
        backdrop-filter:blur(12px);
        border-bottom:1px solid var(--border);
        z-index:90;
        transition:left 0.3s cubic-bezier(0.4,0,0.2,1);
      }
      .container{max-width:1200px;margin:0 auto;padding:0 2rem}
      .hidden{display:none!important}
      .sidebar{
        position:fixed;
        top:0;
        left:0;
        width:var(--sidebar-collapsed);
        height:100vh;
        background:linear-gradient(180deg,var(--drab-dark-brown) 0%,#3a3308 100%);
        border-right:1px solid var(--border);
        z-index:100;
        transition:width 0.3s cubic-bezier(0.4,0,0.2,1);
        overflow:hidden;
      }
    </style>';
  }
}, 1);

// Optimize WordPress head cleanup
add_action('init', function() {
  // Remove unnecessary WordPress head elements
  remove_action('wp_head', 'wp_generator');
  remove_action('wp_head', 'wlwmanifest_link');
  remove_action('wp_head', 'rsd_link');
  remove_action('wp_head', 'wp_shortlink_wp_head');
  
  // Remove emoji scripts for better performance
  remove_action('wp_head', 'print_emoji_detection_script', 7);
  remove_action('wp_print_styles', 'print_emoji_styles');
});

// Resource hints (preconnect/dns-prefetch) for API host
add_action('wp_head', function(){ $api_url = get_option('stock_scanner_api_url', ''); if (!$api_url) return; $p = wp_parse_url($api_url); if (!$p || empty($p['scheme']) || empty($p['host'])) return; $origin = esc_url($p['scheme'] . '://' . $p['host']); echo "\n<link rel=\"preconnect\" href=\"{$origin}\" crossorigin>"; echo "\n<link rel=\"dns-prefetch\" href=\"//{$p['host']}\">"; }, 3);

// JSON-LD Organization
add_action('wp_head', function(){ $org = [ '@context'=>'https://schema.org', '@type'=>'Organization', 'name'=>get_bloginfo('name'), 'url'=>home_url('/'), 'logo'=> (function_exists('has_custom_logo') && has_custom_logo()) ? wp_get_attachment_image_url(get_theme_mod('custom_logo'),'full') : '' ]; echo '<script type="application/ld+json">'.wp_json_encode($org).'</script>'; }, 6);

// Basic Open Graph / Twitter meta
add_action('wp_head', function(){ $title = wp_get_document_title(); $desc = get_bloginfo('description'); $url = esc_url(home_url(add_query_arg([],''))); $image = (is_singular() && has_post_thumbnail()) ? esc_url(get_the_post_thumbnail_url(null, 'large')) : ''; echo "\n<meta property=\"og:title\" content=\"".esc_attr($title)."\">\n<meta property=\"og:description\" content=\"".esc_attr($desc)."\">\n<meta property=\"og:url\" content=\"{$url}\">\n"; if ($image) echo "<meta property=\"og:image\" content=\"{$image}\">\n"; echo "<meta name=\"twitter:card\" content=\"summary_large_image\">\n<meta name=\"twitter:title\" content=\"".esc_attr($title)."\">\n<meta name=\"twitter:description\" content=\"".esc_attr($desc)."\">\n"; if ($image) echo "<meta name=\"twitter:image\" content=\"{$image}\">\n"; }, 5);

// Force page creation - can be called multiple times safely
function rts_create_essential_pages() {
  // Always try to create pages, even if activation was marked complete
  $force_create = true;
  
  // Bind plugin-created menu to theme locations if available
  if (class_exists('StockScannerIntegration')){
    $locations = get_nav_menu_locations();
    $menu = wp_get_nav_menu_object('Stock Scanner Menu');
    if ($menu){
      $id=(int)$menu->term_id;
      if (empty($locations['primary'])) $locations['primary']=$id;
      if (empty($locations['footer'])) $locations['footer']=$id;
      set_theme_mod('nav_menu_locations', $locations);
    }
  }
  
  
  // Comprehensive page creation with proper templates
  $pages = [
    [ 'slug'=>'dashboard', 'title'=>'Dashboard', 'template'=>'templates/pages/page-dashboard.php', 'content'=>'Welcome to your trading dashboard. Monitor your portfolio, track market trends, and access key performance indicators.' ],
    [ 'slug'=>'scanner', 'title'=>'Stock Scanner', 'template'=>'templates/pages/page-scanner.php', 'content'=>'Advanced stock screening tool to find trading opportunities based on your criteria.' ],
    [ 'slug'=>'watchlists', 'title'=>'Watchlists', 'template'=>'templates/pages/page-watchlists.php', 'content'=>'Create and manage watchlists to track your favorite stocks and potential investments.' ],
    [ 'slug'=>'portfolio', 'title'=>'Portfolio', 'template'=>'templates/pages/page-portfolio.php', 'content'=>'Track your investments, monitor performance, and analyze your portfolio allocation.' ],
    [ 'slug'=>'alerts', 'title'=>'Price Alerts', 'template'=>'templates/pages/page-alerts.php', 'content'=>'Set up price alerts to stay informed about important market movements.' ],
    [ 'slug'=>'news', 'title'=>'Market News', 'template'=>'templates/pages/page-news.php', 'content'=>'Stay updated with the latest market news and sentiment analysis.' ],
    [ 'slug'=>'help', 'title'=>'Help Center', 'template'=>'templates/pages/page-help.php', 'content'=>'Find answers to common questions and get the support you need.' ],
    [ 'slug'=>'tutorials', 'title'=>'Tutorials', 'template'=>'templates/pages/page-tutorials.php', 'content'=>'Step-by-step guides to help you master the platform.' ],
    [ 'slug'=>'contact', 'title'=>'Contact Us', 'template'=>'templates/pages/page-contact.php', 'content'=>'Get in touch with our team for support, feedback, or business inquiries.' ],
    [ 'slug'=>'privacy-policy', 'title'=>'Privacy Policy', 'template'=>'templates/pages/page-privacy-policy.php', 'content'=>'Our commitment to protecting your privacy and personal information.' ],
    [ 'slug'=>'terms-of-service', 'title'=>'Terms of Service', 'template'=>'templates/pages/page-terms-of-service.php', 'content'=>'Terms and conditions for using our trading platform and services.' ],
    [ 'slug'=>'disclaimer', 'title'=>'Legal Disclaimer', 'template'=>'templates/pages/page-disclaimer.php', 'content'=>'Important legal and investment disclaimers for platform users.' ],
  ];
  
  // Create pages with better error handling
  $created_count = 0;
  $updated_count = 0;
  
  foreach ($pages as $p){
    $existing = get_page_by_path($p['slug']);
    
    if (!$existing || $force_create){
      if ($existing) {
        // Update existing page
        $page_data = [
          'ID' => $existing->ID,
          'post_title'   => $p['title'],
          'post_content' => $p['content'],
          'post_status'  => 'publish'
        ];
        wp_update_post($page_data);
        $updated_count++;
        $page_id = $existing->ID;
      } else {
        // Create new page
        $page_data = [
          'post_title'   => $p['title'],
          'post_name'    => $p['slug'],
          'post_status'  => 'publish',
          'post_type'    => 'page',
          'post_content' => $p['content'],
          'post_excerpt' => substr($p['content'], 0, 155) . '...'
        ];
        
        $page_id = wp_insert_post($page_data);
        if ($page_id && !is_wp_error($page_id)) {
          $created_count++;
        }
      }
      
      // Assign template if it exists and we have a valid page ID
      if (isset($page_id) && $page_id && !is_wp_error($page_id)) {
        if (!empty($p['template']) && file_exists(get_theme_file_path($p['template']))){
          update_post_meta($page_id, '_wp_page_template', $p['template']);
        }
        
        // Set SEO-friendly meta
        update_post_meta($page_id, '_yoast_wpseo_metadesc', $p['content']);
      }
    }
  }
  
  // Log results
  error_log("RTS Theme: Created {$created_count} pages, updated {$updated_count} pages");
  
  return ['created' => $created_count, 'updated' => $updated_count];
}
// Add multiple activation hooks and manual trigger
add_action('after_switch_theme', 'rts_create_essential_pages');
add_action('init', function() {
  // Also try on init if pages don't exist
  $pages_exist = get_page_by_path('dashboard') && get_page_by_path('scanner');
  if (!$pages_exist) {
    rts_create_essential_pages();
  }
});

// Manual trigger function for testing/debugging
function rts_force_create_pages() {
  $results = rts_create_essential_pages();
  
  // Create basic menu structure
  $menu_obj = wp_get_nav_menu_object('Main Menu');
  if (!$menu_obj) {
    $menu_id = wp_create_nav_menu('Main Menu');
    
    // Add core pages to menu
    $core_pages = ['dashboard', 'scanner', 'portfolio', 'watchlists', 'alerts', 'help', 'contact'];
    foreach ($core_pages as $slug) {
      $page = get_page_by_path($slug);
      if ($page) {
        wp_update_nav_menu_item($menu_id, 0, [
          'menu-item-title'     => get_the_title($page->ID),
          'menu-item-object'    => 'page',
          'menu-item-object-id' => (int)$page->ID,
          'menu-item-type'      => 'post_type',
          'menu-item-status'    => 'publish'
        ]);
      }
    }
    
    // Assign to primary location
    $locations = get_nav_menu_locations();
    $locations['primary'] = (int)$menu_id;
    set_theme_mod('nav_menu_locations', $locations);
  }
  
  // Set dashboard as front page
  $dashboard_page = get_page_by_path('dashboard');
  if ($dashboard_page) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', intval($dashboard_page->ID));
  }
  
  // Flush rewrite rules
  flush_rewrite_rules();
  
  return $results;
}

// Set static front page to Dashboard and create/set Blog as posts page
  $dashboard_page = get_page_by_path('dashboard');
  if ($dashboard_page){
    update_option('show_on_front', 'page');
    update_option('page_on_front', intval($dashboard_page->ID));
  }
  
  $blog_page = get_page_by_path('blog');
  if (!$blog_page){
    $blog_id = wp_insert_post([
      'post_title'  => __('Blog','retail-trade-scanner'),
      'post_name'   => 'blog',
      'post_status' => 'publish',
      'post_type'   => 'page',
      'post_content'=> __('Stay updated with the latest market insights, trading tips, and platform updates.','retail-trade-scanner')
    ]);
    if ($blog_id && !is_wp_error($blog_id)){
      $blog_page = get_post($blog_id);
    }
  }
  if ($blog_page){
    update_option('page_for_posts', intval($blog_page->ID));
  }

  // Enhanced menu creation with better organization
  $locations = get_nav_menu_locations();
  $existing_primary = !empty($locations['primary']) ? (int)$locations['primary'] : 0;
  $existing_footer  = !empty($locations['footer'])  ? (int)$locations['footer']  : 0;

  // Create comprehensive "Stock Scanner Menu"
  $menu_obj = wp_get_nav_menu_object('Stock Scanner Menu');
  if (!$menu_obj){
    $menu_id = wp_create_nav_menu('Stock Scanner Menu');
  } else {
    $menu_id = (int)$menu_obj->term_id;
  }

  // Helper: add menu item with better organization
  $ensure_menu_item = function($menu_id, $page_slug, $parent_id = 0){
    $page = get_page_by_path($page_slug);
    if (!$page) return 0;
    
    $items = wp_get_nav_menu_items($menu_id);
    $already = false;
    if (is_array($items)){
      foreach ($items as $it){ 
        if ((int)$it->object_id === (int)$page->ID){ 
          $already = true; 
          break; 
        } 
      }
    }
    
    if (!$already){
      return wp_update_nav_menu_item($menu_id, 0, [
        'menu-item-title'     => get_the_title($page->ID),
        'menu-item-object'    => 'page',
        'menu-item-object-id' => (int)$page->ID,
        'menu-item-type'      => 'post_type',
        'menu-item-status'    => 'publish',
        'menu-item-parent-id' => $parent_id
      ]);
    }
    return 0;
  };

  // Populate main menu with organized structure
  if ($menu_id){
    // Core trading features
    foreach (['dashboard','scanner','watchlists','portfolio','alerts'] as $slug){
      $ensure_menu_item($menu_id, $slug);
    }
    
    // Information & support
    foreach (['news','help','tutorials'] as $slug){
      $ensure_menu_item($menu_id, $slug);
    }
    
    // API & developer tools
    foreach (['api-docs','endpoint-status'] as $slug){
      $ensure_menu_item($menu_id, $slug);
    }
  }

  // Assign menu to primary location if empty
  if (!$existing_primary && $menu_id){ 
    $locations['primary'] = (int)$menu_id; 
  }

  // Create organized Footer menu
  $footer_menu = wp_get_nav_menu_object('Footer Menu');
  if (!$footer_menu){
    $footer_menu_id = wp_create_nav_menu('Footer Menu');
  } else {
    $footer_menu_id = (int)$footer_menu->term_id;
  }
  
  if ($footer_menu_id){
    // Legal pages
    foreach (['privacy-policy','terms-of-service','disclaimer'] as $slug){
      $ensure_menu_item($footer_menu_id, $slug);
    }
    // Support
    foreach (['contact','help','careers'] as $slug){
      $ensure_menu_item($footer_menu_id, $slug);
    }
  }
  
  if (!$existing_footer && !empty($footer_menu_id)){ 
    $locations['footer'] = (int)$footer_menu_id; 
  }
  
  if (!empty($locations)){ 
    set_theme_mod('nav_menu_locations', $locations); 
  }
  
// Add admin menu for manual page creation
add_action('admin_menu', function() {
  add_theme_page(
    'Create Pages',
    'Create Pages', 
    'manage_options',
    'rts-create-pages',
    'rts_admin_create_pages'
  );
});

function rts_admin_create_pages() {
  if (isset($_POST['create_pages'])) {
    $results = rts_force_create_pages();
    echo '<div class="notice notice-success"><p>Pages created successfully! Created: ' . $results['created'] . ', Updated: ' . $results['updated'] . '</p></div>';
  }
  
  ?>
  <div class="wrap">
    <h1>Create Theme Pages</h1>
    <p>This will create all required pages for the Retail Trade Scanner theme.</p>
    
    <form method="post">
      <table class="form-table">
        <tr>
          <th scope="row">Pages to Create</th>
          <td>
            <ul>
              <li>Dashboard (Front Page)</li>
              <li>Stock Scanner</li>
              <li>Watchlists</li>
              <li>Portfolio</li>
              <li>Price Alerts</li>
              <li>Market News</li>
              <li>Help Center</li>
              <li>Tutorials</li>
              <li>Contact Us</li>
              <li>Privacy Policy</li>
              <li>Terms of Service</li>
              <li>Legal Disclaimer</li>
            </ul>
          </td>
        </tr>
      </table>
      
      <?php submit_button('Create All Pages', 'primary', 'create_pages'); ?>
    </form>
  </div>
  <?php
}

// Also try to create pages on admin_init if they don't exist
add_action('admin_init', function() {
  if (is_admin() && current_user_can('manage_options')) {
    $dashboard_exists = get_page_by_path('dashboard');
    if (!$dashboard_exists) {
      // Show admin notice
      add_action('admin_notices', function() {
        echo '<div class="notice notice-warning is-dismissible">';
        echo '<p><strong>Retail Trade Scanner:</strong> Theme pages need to be created. ';
        echo '<a href="' . admin_url('themes.php?page=rts-create-pages') . '">Create Pages Now</a>';
        echo '</p></div>';
      });
    }
  }
});

// Forms – subscribe & contact (fallback if plugin not used)
function rts_safe_redirect_back($param, $value){ $url=wp_get_referer(); if(!$url) $url=home_url('/'); $url=add_query_arg([$param=>$value], $url); wp_safe_redirect($url); exit; }
add_action('admin_post_nopriv_rts_subscribe','rts_handle_subscribe'); add_action('admin_post_rts_subscribe','rts_handle_subscribe');
function rts_handle_subscribe(){ if(!isset($_POST['rts_subscribe_nonce'])||!wp_verify_nonce($_POST['rts_subscribe_nonce'],'rts_subscribe')) rts_safe_redirect_back('subscribed','0'); $email=isset($_POST['email'])?sanitize_email($_POST['email']):''; if(!is_email($email)) rts_safe_redirect_back('subscribed','0'); $admin=get_option('admin_email'); @wp_mail($admin, __('New Subscription','retail-trade-scanner'), sprintf(__('New subscription: %s','retail-trade-scanner'), $email)); rts_safe_redirect_back('subscribed','1'); }
add_action('admin_post_nopriv_rts_contact','rts_handle_contact'); add_action('admin_post_rts_contact','rts_handle_contact');
function rts_handle_contact(){ if(!isset($_POST['rts_contact_nonce'])||!wp_verify_nonce($_POST['rts_contact_nonce'],'rts_contact')) rts_safe_redirect_back('contact','error'); $name=sanitize_text_field($_POST['name']??''); $email=sanitize_email($_POST['email']??''); $msg=wp_kses_post($_POST['message']??''); if(!$name||!is_email($email)||!$msg) rts_safe_redirect_back('contact','invalid'); $admin=get_option('admin_email'); $subject=sprintf(__('Contact form from %s','retail-trade-scanner'), $name); $body=sprintf("Name: %s\nEmail: %s\n\n%s", $name, $email, wp_strip_all_tags($msg)); @wp_mail($admin, $subject, $body); rts_safe_redirect_back('contact','sent'); }

// Admin notice for plugin config (frontend visible to admins)
add_action('wp_footer', function(){ if(!current_user_can('manage_options')) return; if(!class_exists('StockScannerIntegration')) return; $api_url=get_option('stock_scanner_api_url',''); $api_secret=get_option('stock_scanner_api_secret',''); if(empty($api_url)||empty($api_secret)){ echo '<div style="position:fixed;bottom:12px;right:12px;background:#111827;color:#fff;padding:10px 14px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.3);z-index:9999;opacity:.9">'.esc_html__('Stock Scanner plugin needs configuration: set API URL and Secret in Settings → Stock Scanner.','retail-trade-scanner').'</div>'; } });

// Helper function for estimated reading time
function estimated_reading_time($post_id = null) {
    if (!$post_id) {
        $post_id = get_the_ID();
    }
    
    $content = get_post_field('post_content', $post_id);
    if (!$content) {
        return '1 ' . __('min read', 'retail-trade-scanner');
    }
    
    // Strip shortcodes and HTML tags
    $content = strip_shortcodes($content);
    $content = wp_strip_all_tags($content);
    
    // Count words
    $word_count = str_word_count($content);
    
    // Calculate reading time (average 200 words per minute)
    $reading_time = ceil($word_count / 200);
    
    // Handle singular/plural
    if ($reading_time <= 1) {
        return '1 ' . __('min read', 'retail-trade-scanner');
    } else {
        return $reading_time . ' ' . __('min read', 'retail-trade-scanner');
    }
}

// Add excerpt length filter
add_filter('excerpt_length', function($length) {
    return 25;
});

// Custom excerpt more text
add_filter('excerpt_more', function($more) {
    return '...';
});

// Safe file include function
function rts_safe_include_template($template_path, $variables = array()) {
    if (!file_exists($template_path)) {
        rts_log_error("Template file not found: {$template_path}");
        return false;
    }
    
    // Extract variables for template
    if (!empty($variables)) {
        extract($variables, EXTR_SKIP);
    }
    
    ob_start();
    include $template_path;
    return ob_get_clean();
}