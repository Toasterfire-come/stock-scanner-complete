<?php
/**
 * FinMarkets Theme setup + External API integration (proxy via WP REST API) + PayPal config
 */
if (!defined('ABSPATH')) { exit; }

// Polyfill for PHP &lt; 8 for better compatibility
yif (!function_exists('str_starts_with')) {
  function str_starts_with($haystack, $needle) {
    return $needle === '' || strncmp($haystack, $needle, strlen($needle)) === 0;
  }
}

// ---------- Theme supports ----------
add_action('after_setup_theme', function () {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('html5', ['search-form', 'gallery', 'caption', 'script', 'style']);
  register_nav_menus([
    'primary' => __('Primary Menu', 'finmarkets'),
    'footer' => __('Footer Menu', 'finmarkets')
  ]);
});

// Auto-create key pages on theme activation
add_action('after_switch_theme', function(){
  $pages = [
    // title => [slug, template]
    'Home' => ['home', ''],
    'Stock Screener' => ['screener', 'template-screener.php'],
    'Market Overview' => ['market-overview', 'template-market-overview.php'],
    'Portfolio Management' => ['portfolio', 'template-portfolio.php'],
    'Stock Lookup' => ['stock-lookup', 'template-lookup.php'],
    'News' => ['news', 'template-news.php'],
    'Watchlist' => ['watchlist', 'template-watchlist.php'],
    'User Settings' => ['user-settings', 'template-user-settings.php'],
    'Checkout' => ['checkout', 'template-payments-checkout.php'],
    'Payment Success' => ['payment-success', 'template-payments-success.php'],
    'Payment Canceled' => ['payment-cancel', 'template-payments-cancel.php'],
    'About' => ['about', 'template-about.php'],
    'Help Center' => ['help-center', 'template-help.php'],
    'FAQ' => ['faq', 'template-faq.php'],
    'Contact' => ['contact', 'template-contact.php'],
    'Glossary' => ['glossary', 'template-glossary.php'],
    'How It Works' => ['how-it-works', 'template-how-it-works.php'],
    'Getting Started' => ['getting-started', 'template-getting-started.php'],
    'Roadmap' => ['roadmap', 'template-roadmap.php'],
    'Login' => ['login', 'template-login.php'],
    'Signup' => ['signup', 'template-signup.php'],
    'Dashboard' => ['dashboard', 'template-dashboard.php'],
    'Account' => ['account', 'template-account.php'],
    'Billing History' => ['billing-history', 'template-billing-history.php'],
    'Premium Plans' => ['premium-plans', 'template-premium-plans.php'],
    'Compare Plans' => ['compare-plans', 'template-compare-plans.php'],
    'Privacy Policy' => ['privacy', 'template-privacy.php'],
    'Terms of Service' => ['terms', 'template-terms.php'],
    'Security' => ['security', 'template-security.php'],
    'Accessibility' => ['accessibility', 'template-accessibility.php'],
    'Status' => ['status', 'template-status.php'],
    'Sitemap' => ['sitemap', 'template-sitemap.php'],
    'Market Hours' => ['market-hours', 'template-market-hours.php'],
    'Endpoint Status' => ['endpoint-status', 'template-endpoint-status.php'],
    'Revenue Analytics' => ['revenue-analytics', 'template-revenue-analytics.php'],
    'Components' => ['components', 'template-components.php'],
    'Keyboard Shortcuts' => ['keyboard-shortcuts', 'template-keyboard-shortcuts.php'],
    'Notifications' => ['notifications', 'template-notifications.php'],
    'Subscriptions' => ['subscriptions', 'template-subscriptions.php'],
    'Newsletter' => ['newsletter', 'template-newsletter.php'],
    'Data Request' => ['data-request', 'template-data-request.php'],
    'Cookie Policy' => ['cookie-policy', 'template-cookies.php'],
  ];

  foreach($pages as $title => $info){
    list($slug, $tpl) = $info;
    $existing = get_page_by_path($slug);
    if(!$existing){
      $pid = wp_insert_post([
        'post_title' => $title,
        'post_name' => $slug,
        'post_status' => 'publish',
        'post_type' => 'page'
      ]);
      if($pid && $tpl){ update_post_meta($pid, '_wp_page_template', $tpl); }
      if($title === 'Home'){
        update_option('page_on_front', $pid);
        update_option('show_on_front', 'page');
      }
    } else {
      if($tpl){ update_post_meta($existing->ID, '_wp_page_template', $tpl); }
      if($title === 'Home'){
        update_option('page_on_front', $existing->ID);
        update_option('show_on_front', 'page');
      }
    }
  }
});

// ---------- Options (API + PayPal) ----------
const FINM_OPTION_KEY = 'finm_settings';
function finm_get_settings() {
  $defaults = [
    'api_base' => '',
    'api_key' => '',
    'paypal_client_id' => '',
    'paypal_currency' => 'USD',
    'paypal_env' => 'sandbox',
    'paypal_amount_pro' => '19.00',
    'paypal_brand_name' => 'FinMarkets Pro'
  ];
  $opt = get_option(FINM_OPTION_KEY, []);
  if (!is_array($opt)) $opt = [];
  return array_merge($defaults, $opt);
}
function finm_sanitize_url($url){ $url = trim($url); if ($url === '') return ''; if (!preg_match('#^https?://#i', $url)) { $url = 'https://' . $url; } return rtrim($url, "/ "); }

// Settings sections and fields (API + PayPal)
add_action('admin_init', function(){
  register_setting('finm_group', FINM_OPTION_KEY, [
    'type' => 'array',
    'sanitize_callback' => function($value){
      return [
        'api_base' => finm_sanitize_url($value['api_base'] ?? ''),
        'api_key' => sanitize_text_field($value['api_key'] ?? ''),
        'paypal_client_id' => sanitize_text_field($value['paypal_client_id'] ?? ''),
        'paypal_currency' => sanitize_text_field($value['paypal_currency'] ?? 'USD'),
        'paypal_env' => in_array($value['paypal_env'] ?? 'sandbox', ['sandbox','live'], true) ? ($value['paypal_env'] ?? 'sandbox') : 'sandbox',
        'paypal_amount_pro' => preg_replace('#[^0-9\.]#','', $value['paypal_amount_pro'] ?? '19.00'),
        'paypal_brand_name' => sanitize_text_field($value['paypal_brand_name'] ?? 'FinMarkets Pro'),
      ];
    }
  ]);
  add_settings_section('finm_section', __('External API', 'finmarkets'), function(){ echo '<p>Configure base URL for your market data API. Requests are proxied via WP REST to avoid CORS.</p>'; }, 'finm_settings');
  add_settings_field('finm_api_base', __('API Base URL', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="url" class="regular-text" name="' . FINM_OPTION_KEY . '[api_base]" value="' . esc_attr($s['api_base']) . '" placeholder="https://api.example.com" />'; }, 'finm_settings', 'finm_section');
  add_settings_field('finm_api_key', __('API Key (optional)', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="text" class="regular-text" name="' . FINM_OPTION_KEY . '[api_key]" value="' . esc_attr($s['api_key']) . '" placeholder="Bearer token or key" />'; }, 'finm_settings', 'finm_section');
  add_settings_section('finm_pp', __('PayPal', 'finmarkets'), function(){ echo '<p>Enter your PayPal Client ID and defaults. Buttons are rendered on the Checkout template.</p>'; }, 'finm_settings');
  add_settings_field('finm_pp_id', __('Client ID', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="text" class="regular-text" name="' . FINM_OPTION_KEY . '[paypal_client_id]" value="' . esc_attr($s['paypal_client_id']) . '" placeholder="Abc123..." />'; }, 'finm_settings', 'finm_pp');
  add_settings_field('finm_pp_env', __('Environment', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<select name="' . FINM_OPTION_KEY . '[paypal_env]'><option value="sandbox"' . selected($s['paypal_env'],'sandbox',false) . '>Sandbox</option><option value="live"' . selected($s['paypal_env'],'live',false) . '>Live</option></select>'; }, 'finm_settings', 'finm_pp');
  add_settings_field('finm_pp_currency', __('Currency', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="text" name="' . FINM_OPTION_KEY . '[paypal_currency]" value="' . esc_attr($s['paypal_currency']) . '" size="6" />'; }, 'finm_settings', 'finm_pp');
  add_settings_field('finm_pp_amount', __('Pro Plan Price', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="text" name="' . FINM_OPTION_KEY . '[paypal_amount_pro]" value="' . esc_attr($s['paypal_amount_pro']) . '" size="8" />'; }, 'finm_settings', 'finm_pp');
  add_settings_field('finm_pp_brand', __('Brand Name', 'finmarkets'), function(){ $s = finm_get_settings(); echo '<input type="text" class="regular-text" name="' . FINM_OPTION_KEY . '[paypal_brand_name]" value="' . esc_attr($s['paypal_brand_name']) . '" />'; }, 'finm_settings', 'finm_pp');
});

add_action('admin_menu', function(){
  add_theme_page(__('FinMarkets Settings','finmarkets'), __('FinMarkets Settings','finmarkets'), 'manage_options', 'finm-settings', function(){
    $s = finm_get_settings();
    echo '<div class="wrap"><h1>FinMarkets Settings</h1><form method="post" action="options.php">';
    settings_fields('finm_group');
    do_settings_sections('finm_settings');
    submit_button();
    echo '</form><hr><h2>Connection Test</h2><p>Test /health via theme proxy.</p><p><button class="button button-primary" id="finmTest">Run health check</button></p><pre id="finmOut" style="max-height:260px; overflow:auto; background:#111; color:#0f0; padding:12px;">(results here)</pre>';
    echo '<p class="description">REST base: ' . esc_html( rest_url('finm/v1') ) . ' • API base: ' . esc_html($s['api_base'] ?: '(not set)') . ' • PayPal: ' . esc_html(($s['paypal_client_id']?'configured':'not set')) . '</p>';
    echo '</div>';
    echo '<script>document.getElementById("finmTest").addEventListener("click", async ()=>{ const out=document.getElementById("finmOut"); out.textContent="Testing..."; try{ const r=await fetch("' . esc_url_raw( rest_url('finm/v1/health') ) . '"); const j=await r.json(); out.textContent=JSON.stringify(j,null,2);}catch(e){ out.textContent=String(e);} });</script>';
  });
});

// ---------- Enqueue styles and scripts ----------
add_action('wp_enqueue_scripts', function () {
  wp_enqueue_style('finmarkets-inter', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap', [], null);
  wp_enqueue_style('finmarkets-style', get_stylesheet_uri(), ['finmarkets-inter'], wp_get_theme()->get('Version'));
  wp_enqueue_script('finmarkets-mock', get_template_directory_uri() . '/assets/js/mock.js', [], wp_get_theme()->get('Version'), true);
  wp_enqueue_script('finmarkets-api', get_template_directory_uri() . '/assets/js/api.js', [], wp_get_theme()->get('Version'), true);
  wp_enqueue_script('finmarkets-app', get_template_directory_uri() . '/assets/js/app.js', ['finmarkets-mock','finmarkets-api'], wp_get_theme()->get('Version'), true);
  wp_enqueue_script('finmarkets-ui', get_template_directory_uri() . '/assets/js/ui.js', [], wp_get_theme()->get('Version'), true);
  wp_localize_script('finmarkets-api', 'finmConfig', [
    'restBase' => esc_url_raw( rest_url('finm/v1') ),
    'hasApiBase' => (bool) finm_get_settings()['api_base'],
  ]);
});
add_filter('script_loader_tag', function ($tag, $handle, $src) {
  $defer = ['finmarkets-mock', 'finmarkets-api', 'finmarkets-app', 'finmarkets-ui'];
  if (in_array($handle, $defer, true)) { return '<script src="' . esc_url($src) . '" defer></script>'; }
  return $tag;
}, 10, 3);
add_action('send_headers', function () { header('X-Frame-Options: SAMEORIGIN'); header('X-XSS-Protection: 1; mode=block'); header('X-Content-Type-Options: nosniff'); });

// ---------- REST proxy routes ----------
add_action('rest_api_init', function(){
  register_rest_route('finm/v1', '/health', ['methods' => 'GET', 'callback' => 'finm_route_health']);
  register_rest_route('finm/v1', '/stocks', ['methods' => 'GET', 'callback' => 'finm_route_stocks']);
  register_rest_route('finm/v1', '/stock/(?P<ticker>[A-Za-z0-9\.-]+)', ['methods' => 'GET', 'callback' => 'finm_route_stock']);
  register_rest_route('finm/v1', '/search', ['methods' => 'GET', 'callback' => 'finm_route_search']);
  register_rest_route('finm/v1', '/trending', ['methods' => 'GET', 'callback' => 'finm_route_trending']);
  register_rest_route('finm/v1', '/market-stats', ['methods' => 'GET', 'callback' => 'finm_route_market_stats']);
  register_rest_route('finm/v1', '/endpoint-status', ['methods' => 'GET', 'callback' => 'finm_route_endpoint_status']);
  register_rest_route('finm/v1', '/revenue/analytics', ['methods' => 'GET', 'callback' => 'finm_route_revenue_analytics']);
  register_rest_route('finm/v1', '/revenue/analytics/(?P<month>[^/]+)', ['methods' => 'GET', 'callback' => 'finm_route_revenue_analytics_month']);
  register_rest_route('finm/v1', '/paypal-config', ['methods'=>'GET','callback'=>function(){ $s=finm_get_settings(); return [ 'client_id'=>$s['paypal_client_id'], 'currency'=>$s['paypal_currency'], 'env'=>$s['paypal_env'], 'amount_pro'=>$s['paypal_amount_pro'], 'brand'=>$s['paypal_brand_name'] ]; }]);
  register_rest_route('finm/v1', '/api/(?P<path>.+)', ['methods' => ['GET','POST','DELETE'], 'callback' => function(WP_REST_Request $req){ return finm_route_generic($req, 'api'); }, 'args' => ['path' => ['sanitize_callback' => 'sanitize_text_field']]]);
  register_rest_route('finm/v1', '/revenue/(?P<path>.+)', ['methods' => ['GET','POST','DELETE'], 'callback' => function(WP_REST_Request $req){ return finm_route_generic($req, 'revenue'); }, 'args' => ['path' => ['sanitize_callback' => 'sanitize_text_field']]]);
});

function finm_api_base(){ $b = finm_get_settings()['api_base']; return $b ? rtrim($b, '/') : ''; }
function finm_build_url($path){ $base = finm_api_base(); if (!$base) return ''; return $base . (str_starts_with($path, '/') ? $path : '/' . $path); }
function finm_req_headers($needs_key=false){ $h = [ 'Accept' => 'application/json' ]; $key = finm_get_settings()['api_key']; if ($needs_key && $key) { $h['Authorization'] = 'Bearer ' . $key; } return $h; }
function finm_format_response($r){ if (is_wp_error($r)) return new WP_REST_Response(['success'=>false,'message'=>$r->get_error_message()], 502); $code = wp_remote_retrieve_response_code($r); $body = wp_remote_retrieve_body($r); $json = json_decode($body, true); if (json_last_error() === JSON_ERROR_NONE) return new WP_REST_Response($json, $code); return new WP_REST_Response(['html' => $body, 'status_code' => $code], $code); }
function finm_proxy_get($path, $args=[], $needs_key=false){ $url = finm_build_url($path); if (!$url) return new WP_REST_Response(['success'=>false,'message'=>'API base not configured'], 400); if (!empty($args)) { $url = add_query_arg($args, $url); } $r = wp_remote_get($url, ['timeout'=>12,'headers'=>finm_req_headers($needs_key)]); return finm_format_response($r); }
function finm_proxy_send($method, $path, $payload=null, $needs_key=true){ $url = finm_build_url($path); if (!$url) return new WP_REST_Response(['success'=>false,'message'=>'API base not configured'], 400); $args=['timeout'=>15,'method'=>$method,'headers'=>array_merge(finm_req_headers($needs_key), ['Content-Type'=>'application/json'])]; if ($payload !== null) { $args['body']=wp_json_encode($payload); } $r=wp_remote_request($url,$args); return finm_format_response($r); }

function finm_route_health(WP_REST_Request $req){ $r = finm_proxy_get('/health/'); if ($r->get_status() >= 400) { $r = finm_proxy_get('/api/health/'); } return $r; }
function finm_route_stocks(WP_REST_Request $req){ return finm_proxy_get('/api/stocks/', $req->get_params()); }
function finm_route_stock(WP_REST_Request $req){ $t = strtoupper(sanitize_text_field($req['ticker'])); $r = finm_proxy_get('/api/stock/' . rawurlencode($t) . '/'); if ($r->get_status() >= 400) { $r = finm_proxy_get('/api/stocks/' . rawurlencode($t) . '/'); } return $r; }
function finm_route_search(WP_REST_Request $req){ return finm_proxy_get('/api/search/', ['q'=>$req->get_param('q')]); }
function finm_route_trending(WP_REST_Request $req){ return finm_proxy_get('/api/trending/'); }
function finm_route_market_stats(WP_REST_Request $req){ return finm_proxy_get('/api/market-stats/'); }
function finm_route_endpoint_status(WP_REST_Request $req){ return finm_proxy_get('/endpoint-status/'); }
function finm_route_revenue_analytics(WP_REST_Request $req){ return finm_proxy_get('/revenue/revenue-analytics/'); }
function finm_route_revenue_analytics_month(WP_REST_Request $req){ return finm_proxy_get('/revenue/revenue-analytics/' . rawurlencode($req['month']) . '/'); }
function finm_route_generic(WP_REST_Request $req, $prefix){ $path = sanitize_text_field($req['path']); $method = strtoupper($req->get_method()); if (!preg_match('#^[A-Za-z0-9_\-/\.,]+$#', $path)) { return new WP_REST_Response(['success'=>false,'message'=>'Invalid path'], 400); } $full = '/' . trim($prefix, '/') . '/' . ltrim($path, '/'); if ($method === 'GET') { return finm_proxy_get($full, $req->get_params(), false); } elseif ($method === 'POST') { $payload = $req->get_json_params(); return finm_proxy_send('POST', $full, $payload, true); } elseif ($method === 'DELETE') { return finm_proxy_send('DELETE', $full, null, true); } return new WP_REST_Response(['success'=>false,'message'=>'Method not allowed'], 405); }

// ---------- Shortcodes ----------
add_shortcode('finm_health', function(){ $rest = esc_url( rest_url('finm/v1/health') ); ob_start(); ?>
  <span class="badge" id="finmHealthBadge">Checking…</span>
  <script defer>(function(){document.addEventListener('DOMContentLoaded', async function(){ const el=document.getElementById('finmHealthBadge'); try{ const r=await fetch('<?php echo $rest; ?>'); const j=await r.json(); const st=(j.status||'').toLowerCase(); if(st==='healthy'){ el.textContent='API: Healthy'; el.classList.add('badge-green'); } else { el.textContent='API: Degraded'; el.classList.add('badge-red'); } }catch(e){ el.textContent='API: Offline'; el.classList.add('badge-red'); } });})();</script>
<?php return ob_get_clean(); });