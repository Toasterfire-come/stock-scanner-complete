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

// Enqueue styles and integration script
add_action('wp_enqueue_scripts', function(){ $ver = wp_get_theme()->get('Version'); wp_enqueue_style('retail-trade-scanner-style', get_stylesheet_uri(), [], $ver); $api_url = get_option('stock_scanner_api_url', ''); $revenue_base = $api_url ? trailingslashit(str_replace('/api/', '/revenue/', $api_url)) : ''; $js_path = get_template_directory() . '/assets/js/theme-integration.js'; $js_url  = get_template_directory_uri() . '/assets/js/theme-integration.js'; if (file_exists($js_path)){ wp_enqueue_script('rts-theme-js', $js_url, [], $ver, true); wp_localize_script('rts-theme-js', 'rtsConfig', [ 'apiBase' => trailingslashit($api_url), 'revenueBase' => $revenue_base ]); } }, 20);

// Resource hints (preconnect/dns-prefetch) for API host
add_action('wp_head', function(){ $api_url = get_option('stock_scanner_api_url', ''); if (!$api_url) return; $p = wp_parse_url($api_url); if (!$p || empty($p['scheme']) || empty($p['host'])) return; $origin = esc_url($p['scheme'] . '://' . $p['host']); echo "\n<link rel=\"preconnect\" href=\"{$origin}\" crossorigin>"; echo "\n<link rel=\"dns-prefetch\" href=\"//{$p['host']}\">"; }, 3);

// JSON-LD Organization
add_action('wp_head', function(){ $org = [ '@context'=>'https://schema.org', '@type'=>'Organization', 'name'=>get_bloginfo('name'), 'url'=>home_url('/'), 'logo'=> (function_exists('has_custom_logo') && has_custom_logo()) ? wp_get_attachment_image_url(get_theme_mod('custom_logo'),'full') : '' ]; echo '<script type="application/ld+json">'.wp_json_encode($org).'</script>'; }, 6);

// Basic Open Graph / Twitter meta
add_action('wp_head', function(){ $title = wp_get_document_title(); $desc = get_bloginfo('description'); $url = esc_url(home_url(add_query_arg([],''))); $image = (is_singular() && has_post_thumbnail()) ? esc_url(get_the_post_thumbnail_url(null, 'large')) : ''; echo "\n<meta property=\"og:title\" content=\"".esc_attr($title)."\">\n<meta property=\"og:description\" content=\"".esc_attr($desc)."\">\n<meta property=\"og:url\" content=\"{$url}\">\n"; if ($image) echo "<meta property=\"og:image\" content=\"{$image}\">\n"; echo "<meta name=\"twitter:card\" content=\"summary_large_image\">\n<meta name=\"twitter:title\" content=\"".esc_attr($title)."\">\n<meta name=\"twitter:description\" content=\"".esc_attr($desc)."\">\n"; if ($image) echo "<meta name=\"twitter:image\" content=\"{$image}\">\n"; }, 5);

// Activation – skip creating pages if plugin provides them
add_action('after_switch_theme', function(){ if (get_option('rts_activation_completed')) return; if (class_exists('StockScannerIntegration')){ $locations = get_nav_menu_locations(); $menu = wp_get_nav_menu_object('Stock Scanner Menu'); if ($menu){ $id=(int)$menu->term_id; if (empty($locations['primary'])) $locations['primary']=$id; if (empty($locations['footer'])) $locations['footer']=$id; set_theme_mod('nav_menu_locations', $locations); } update_option('rts_activation_completed', 1); return; } $pages = [ [ 'slug'=>'dashboard', 'title'=>__('Dashboard','retail-trade-scanner'), 'template'=>'templates/pages/page-dashboard.php' ], [ 'slug'=>'scanner', 'title'=>__('Scanner','retail-trade-scanner'), 'template'=>'templates/pages/page-scanner.php' ], [ 'slug'=>'watchlists', 'title'=>__('Watchlists','retail-trade-scanner'), 'template'=>'templates/pages/page-watchlists.php' ], [ 'slug'=>'portfolio', 'title'=>__('Portfolio','retail-trade-scanner'), 'template'=>'templates/pages/page-portfolio.php' ], [ 'slug'=>'alerts', 'title'=>__('Alerts','retail-trade-scanner'), 'template'=>'templates/pages/page-alerts.php' ], [ 'slug'=>'news', 'title'=>__('News','retail-trade-scanner'), 'template'=>'templates/pages/page-news.php' ], [ 'slug'=>'api-docs', 'title'=>__('API Docs','retail-trade-scanner'), 'template'=>'templates/pages/page-api-docs.php' ], [ 'slug'=>'endpoint-status', 'title'=>__('Endpoint Status','retail-trade-scanner'), 'template'=>'templates/pages/page-endpoint-status.php' ], [ 'slug'=>'help', 'title'=>__('Help','retail-trade-scanner'), 'template'=>'templates/pages/page-help.php' ], [ 'slug'=>'tutorials', 'title'=>__('Tutorials','retail-trade-scanner'), 'template'=>'templates/pages/page-tutorials.php' ], [ 'slug'=>'careers', 'title'=>__('Careers','retail-trade-scanner'), 'template'=>'templates/pages/page-careers.php' ], [ 'slug'=>'privacy-policy', 'title'=>__('Privacy Policy','retail-trade-scanner'), 'template'=>'templates/pages/page-privacy-policy.php' ], [ 'slug'=>'terms-of-service', 'title'=>__('Terms of Service','retail-trade-scanner'), 'template'=>'templates/pages/page-terms-of-service.php' ], [ 'slug'=>'disclaimer', 'title'=>__('Disclaimer','retail-trade-scanner'), 'template'=>'templates/pages/page-disclaimer.php' ], [ 'slug'=>'contact', 'title'=>__('Contact','retail-trade-scanner'), 'template'=>'templates/pages/page-contact.php' ], [ 'slug'=>'paypal-checkout', 'title'=>__('PayPal Checkout','retail-trade-scanner'), 'template'=>'templates/pages/page-checkout-paypal.php' ], [ 'slug'=>'payment-success', 'title'=>__('Payment Success','retail-trade-scanner'), 'template'=>'' ], [ 'slug'=>'payment-cancelled', 'title'=>__('Payment Cancelled','retail-trade-scanner'), 'template'=>'' ], ]; foreach ($pages as $p){ $existing = get_page_by_path($p['slug']); if (!$existing){ $pid = wp_insert_post([ 'post_title'=>$p['title'], 'post_name'=>$p['slug'], 'post_status'=>'publish', 'post_type'=>'page', 'post_content'=>'' ]); if ($pid && !is_wp_error($pid) && !empty($p['template']) && file_exists(get_theme_file_path($p['template']))){ update_post_meta($pid, '_wp_page_template', $p['template']); } } else if (!get_page_template_slug($existing->ID) && !empty($p['template']) && file_exists(get_theme_file_path($p['template']))){ update_post_meta($existing->ID, '_wp_page_template', $p['template']); } } update_option('rts_activation_completed', 1); });

// Forms – subscribe & contact (fallback if plugin not used)
function rts_safe_redirect_back($param, $value){ $url=wp_get_referer(); if(!$url) $url=home_url('/'); $url=add_query_arg([$param=>$value], $url); wp_safe_redirect($url); exit; }
add_action('admin_post_nopriv_rts_subscribe','rts_handle_subscribe'); add_action('admin_post_rts_subscribe','rts_handle_subscribe');
function rts_handle_subscribe(){ if(!isset($_POST['rts_subscribe_nonce'])||!wp_verify_nonce($_POST['rts_subscribe_nonce'],'rts_subscribe')) rts_safe_redirect_back('subscribed','0'); $email=isset($_POST['email'])?sanitize_email($_POST['email']):''; if(!is_email($email)) rts_safe_redirect_back('subscribed','0'); $admin=get_option('admin_email'); @wp_mail($admin, __('New Subscription','retail-trade-scanner'), sprintf(__('New subscription: %s','retail-trade-scanner'), $email)); rts_safe_redirect_back('subscribed','1'); }
add_action('admin_post_nopriv_rts_contact','rts_handle_contact'); add_action('admin_post_rts_contact','rts_handle_contact');
function rts_handle_contact(){ if(!isset($_POST['rts_contact_nonce'])||!wp_verify_nonce($_POST['rts_contact_nonce'],'rts_contact')) rts_safe_redirect_back('contact','error'); $name=sanitize_text_field($_POST['name']??''); $email=sanitize_email($_POST['email']??''); $msg=wp_kses_post($_POST['message']??''); if(!$name||!is_email($email)||!$msg) rts_safe_redirect_back('contact','invalid'); $admin=get_option('admin_email'); $subject=sprintf(__('Contact form from %s','retail-trade-scanner'), $name); $body=sprintf("Name: %s\nEmail: %s\n\n%s", $name, $email, wp_strip_all_tags($msg)); @wp_mail($admin, $subject, $body); rts_safe_redirect_back('contact','sent'); }

// Admin notice for plugin config (frontend visible to admins)
add_action('wp_footer', function(){ if(!current_user_can('manage_options')) return; if(!class_exists('StockScannerIntegration')) return; $api_url=get_option('stock_scanner_api_url',''); $api_secret=get_option('stock_scanner_api_secret',''); if(empty($api_url)||empty($api_secret)){ echo '<div style="position:fixed;bottom:12px;right:12px;background:#111827;color:#fff;padding:10px 14px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.3);z-index:9999;opacity:.9">'.esc_html__('Stock Scanner plugin needs configuration: set API URL and Secret in Settings → Stock Scanner.','retail-trade-scanner').'</div>'; } });