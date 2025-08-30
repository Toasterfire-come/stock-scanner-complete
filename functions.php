<?php
/**
 * Retail Trade Scanner Theme – Production Functions (Enhanced)
 */
if (!defined('ABSPATH')) { exit; }

// i18n
add_action('after_setup_theme', function(){ load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages'); });

// Include integration helpers
require_once get_template_directory() . '/inc/plugin-integration.php';

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
}, 20);

// Add critical CSS inline for above-the-fold content
add_action('wp_head', function() {
  if (!is_admin()) {
    echo '<style id="critical-css">
      :root{--background:#0f1115;--foreground:#e8eaed;--primary:#3b82f6;--border:#1f2937}
      body{background:var(--background);color:var(--foreground);margin:0;font-family:system-ui,-apple-system,sans-serif}
      .site-header{position:sticky;top:0;z-index:100;background:var(--background);border-bottom:1px solid var(--border)}
      .container{max-width:1200px;margin:0 auto;padding:0 1rem}
      .hidden{display:none!important}
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

// Enhanced activation with comprehensive page creation and template assignment
add_action('after_switch_theme', function(){
  if (get_option('rts_activation_completed')) return;
  
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
    [ 'slug'=>'dashboard', 'title'=>__('Dashboard','retail-trade-scanner'), 'template'=>'templates/pages/page-dashboard.php', 'content'=>__('Welcome to your trading dashboard. Monitor your portfolio, track market trends, and access key performance indicators.','retail-trade-scanner') ],
    [ 'slug'=>'scanner', 'title'=>__('Stock Scanner','retail-trade-scanner'), 'template'=>'templates/pages/page-scanner.php', 'content'=>__('Advanced stock screening tool to find trading opportunities based on your criteria.','retail-trade-scanner') ],
    [ 'slug'=>'watchlists', 'title'=>__('Watchlists','retail-trade-scanner'), 'template'=>'templates/pages/page-watchlists.php', 'content'=>__('Create and manage watchlists to track your favorite stocks and potential investments.','retail-trade-scanner') ],
    [ 'slug'=>'portfolio', 'title'=>__('Portfolio','retail-trade-scanner'), 'template'=>'templates/pages/page-portfolio.php', 'content'=>__('Track your investments, monitor performance, and analyze your portfolio allocation.','retail-trade-scanner') ],
    [ 'slug'=>'alerts', 'title'=>__('Price Alerts','retail-trade-scanner'), 'template'=>'templates/pages/page-alerts.php', 'content'=>__('Set up price alerts to stay informed about important market movements.','retail-trade-scanner') ],
    [ 'slug'=>'news', 'title'=>__('Market News','retail-trade-scanner'), 'template'=>'templates/pages/page-news.php', 'content'=>__('Stay updated with the latest market news and sentiment analysis.','retail-trade-scanner') ],
    [ 'slug'=>'api-docs', 'title'=>__('API Documentation','retail-trade-scanner'), 'template'=>'templates/pages/page-api-docs.php', 'content'=>__('Complete API documentation for developers and advanced users.','retail-trade-scanner') ],
    [ 'slug'=>'endpoint-status', 'title'=>__('System Status','retail-trade-scanner'), 'template'=>'templates/pages/page-endpoint-status.php', 'content'=>__('Real-time monitoring of our API endpoints and system health.','retail-trade-scanner') ],
    [ 'slug'=>'help', 'title'=>__('Help Center','retail-trade-scanner'), 'template'=>'templates/pages/page-help.php', 'content'=>__('Find answers to common questions and get the support you need.','retail-trade-scanner') ],
    [ 'slug'=>'tutorials', 'title'=>__('Tutorials','retail-trade-scanner'), 'template'=>'templates/pages/page-tutorials.php', 'content'=>__('Step-by-step guides to help you master the platform.','retail-trade-scanner') ],
    [ 'slug'=>'careers', 'title'=>__('Careers','retail-trade-scanner'), 'template'=>'templates/pages/page-careers.php', 'content'=>__('Join our team and help build the future of retail trading.','retail-trade-scanner') ],
    [ 'slug'=>'privacy-policy', 'title'=>__('Privacy Policy','retail-trade-scanner'), 'template'=>'templates/pages/page-privacy-policy.php', 'content'=>__('Our commitment to protecting your privacy and personal information.','retail-trade-scanner') ],
    [ 'slug'=>'terms-of-service', 'title'=>__('Terms of Service','retail-trade-scanner'), 'template'=>'templates/pages/page-terms-of-service.php', 'content'=>__('Terms and conditions for using our trading platform and services.','retail-trade-scanner') ],
    [ 'slug'=>'disclaimer', 'title'=>__('Legal Disclaimer','retail-trade-scanner'), 'template'=>'templates/pages/page-disclaimer.php', 'content'=>__('Important legal and investment disclaimers for platform users.','retail-trade-scanner') ],
    [ 'slug'=>'contact', 'title'=>__('Contact Us','retail-trade-scanner'), 'template'=>'templates/pages/page-contact.php', 'content'=>__('Get in touch with our team for support, feedback, or business inquiries.','retail-trade-scanner') ],
    [ 'slug'=>'paypal-checkout', 'title'=>__('Checkout','retail-trade-scanner'), 'template'=>'templates/pages/page-checkout-paypal.php', 'content'=>__('Secure payment processing for premium subscriptions.','retail-trade-scanner') ],
    [ 'slug'=>'payment-success', 'title'=>__('Payment Successful','retail-trade-scanner'), 'template'=>'', 'content'=>__('Thank you for your payment! Your subscription has been activated.','retail-trade-scanner') ],
    [ 'slug'=>'payment-cancelled', 'title'=>__('Payment Cancelled','retail-trade-scanner'), 'template'=>'', 'content'=>__('Your payment was cancelled. You can try again anytime.','retail-trade-scanner') ],
  ];
  
  // Create pages with better error handling
  $created_pages = [];
  $failed_pages = [];
  
  foreach ($pages as $p){
    $existing = get_page_by_path($p['slug']);
    
    if (!$existing){
      $page_data = [
        'post_title'   => $p['title'],
        'post_name'    => $p['slug'],
        'post_status'  => 'publish',
        'post_type'    => 'page',
        'post_content' => $p['content'],
        'post_excerpt' => substr($p['content'], 0, 155) . '...'
      ];
      
      $pid = wp_insert_post($page_data);
      
      if ($pid && !is_wp_error($pid)) {
        $created_pages[] = $p['title'];
        
        // Assign template if it exists
        if (!empty($p['template']) && file_exists(get_theme_file_path($p['template']))){
          update_post_meta($pid, '_wp_page_template', $p['template']);
        }
        
        // Set SEO-friendly meta
        update_post_meta($pid, '_yoast_wpseo_metadesc', $p['content']);
        
      } else {
        $failed_pages[] = $p['title'];
      }
    } else {
      // Update existing page template if needed
      if (!get_page_template_slug($existing->ID) && !empty($p['template']) && file_exists(get_theme_file_path($p['template']))){
        update_post_meta($existing->ID, '_wp_page_template', $p['template']);
      }
      
      // Update content if it's empty
      if (empty($existing->post_content) && !empty($p['content'])) {
        wp_update_post([
          'ID' => $existing->ID,
          'post_content' => $p['content']
        ]);
      }
    }
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
  
  // Log activation results for debugging
  if (!empty($created_pages)) {
    error_log('RTS Theme: Created pages: ' . implode(', ', $created_pages));
  }
  if (!empty($failed_pages)) {
    error_log('RTS Theme: Failed to create pages: ' . implode(', ', $failed_pages));
  }
  
  // Set theme activation as completed
  update_option('rts_activation_completed', 1);
  
  // Flush rewrite rules to ensure clean URLs
  flush_rewrite_rules();
});

// Forms – subscribe & contact (fallback if plugin not used)
function rts_safe_redirect_back($param, $value){ $url=wp_get_referer(); if(!$url) $url=home_url('/'); $url=add_query_arg([$param=>$value], $url); wp_safe_redirect($url); exit; }
add_action('admin_post_nopriv_rts_subscribe','rts_handle_subscribe'); add_action('admin_post_rts_subscribe','rts_handle_subscribe');
function rts_handle_subscribe(){ if(!isset($_POST['rts_subscribe_nonce'])||!wp_verify_nonce($_POST['rts_subscribe_nonce'],'rts_subscribe')) rts_safe_redirect_back('subscribed','0'); $email=isset($_POST['email'])?sanitize_email($_POST['email']):''; if(!is_email($email)) rts_safe_redirect_back('subscribed','0'); $admin=get_option('admin_email'); @wp_mail($admin, __('New Subscription','retail-trade-scanner'), sprintf(__('New subscription: %s','retail-trade-scanner'), $email)); rts_safe_redirect_back('subscribed','1'); }
add_action('admin_post_nopriv_rts_contact','rts_handle_contact'); add_action('admin_post_rts_contact','rts_handle_contact');
function rts_handle_contact(){ if(!isset($_POST['rts_contact_nonce'])||!wp_verify_nonce($_POST['rts_contact_nonce'],'rts_contact')) rts_safe_redirect_back('contact','error'); $name=sanitize_text_field($_POST['name']??''); $email=sanitize_email($_POST['email']??''); $msg=wp_kses_post($_POST['message']??''); if(!$name||!is_email($email)||!$msg) rts_safe_redirect_back('contact','invalid'); $admin=get_option('admin_email'); $subject=sprintf(__('Contact form from %s','retail-trade-scanner'), $name); $body=sprintf("Name: %s\nEmail: %s\n\n%s", $name, $email, wp_strip_all_tags($msg)); @wp_mail($admin, $subject, $body); rts_safe_redirect_back('contact','sent'); }

// Admin notice for plugin config (frontend visible to admins)
add_action('wp_footer', function(){ if(!current_user_can('manage_options')) return; if(!class_exists('StockScannerIntegration')) return; $api_url=get_option('stock_scanner_api_url',''); $api_secret=get_option('stock_scanner_api_secret',''); if(empty($api_url)||empty($api_secret)){ echo '<div style="position:fixed;bottom:12px;right:12px;background:#111827;color:#fff;padding:10px 14px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.3);z-index:9999;opacity:.9">'.esc_html__('Stock Scanner plugin needs configuration: set API URL and Secret in Settings → Stock Scanner.','retail-trade-scanner').'</div>'; } });