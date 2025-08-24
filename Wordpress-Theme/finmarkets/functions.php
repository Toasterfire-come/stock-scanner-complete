<?php
/**
 * FinMarkets Theme setup + External API integration (proxy via WP REST API)
 */
if (!defined('ABSPATH')) { exit; }

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

// ---------- Options (API Base + Key) ----------
const FINM_OPTION_KEY = 'finm_settings';
function finm_get_settings() {
  $defaults = [ 'api_base' => '', 'api_key' => '' ];
  $opt = get_option(FINM_OPTION_KEY, []);
  if (!is_array($opt)) $opt = [];
  return array_merge($defaults, $opt);
}
function finm_sanitize_url($url){
  $url = trim($url);
  if ($url === '') return '';
  // Ensure scheme
  if (!preg_match('#^https?://#i', $url)) { $url = 'https://' . $url; }
  // Remove trailing slashes
  return rtrim($url, "/ ");
}
add_action('admin_init', function(){
  register_setting('finm_group', FINM_OPTION_KEY, [
    'type' => 'array',
    'sanitize_callback' => function($value){
      return [
        'api_base' => finm_sanitize_url($value['api_base'] ?? ''),
        'api_key' => sanitize_text_field($value['api_key'] ?? ''),
      ];
    }
  ]);
  add_settings_section('finm_section', __('External API', 'finmarkets'), function(){
    echo '<p>Configure the base URL for your market data API. This theme will proxy requests through the WP REST API to avoid CORS and keep a strict CSP.</p>';
  }, 'finm_settings');
  add_settings_field('finm_api_base', __('API Base URL', 'finmarkets'), function(){
    $s = finm_get_settings();
    echo '<input type="url" class="regular-text" name="' . FINM_OPTION_KEY . '[api_base]" value="' . esc_attr($s['api_base']) . '" placeholder="https://api.example.com" />';
  }, 'finm_settings', 'finm_section');
  add_settings_field('finm_api_key', __('API Key (optional)', 'finmarkets'), function(){
    $s = finm_get_settings();
    echo '<input type="text" class="regular-text" name="' . FINM_OPTION_KEY . '[api_key]" value="' . esc_attr($s['api_key']) . '" placeholder="Bearer token or key" />';
  }, 'finm_settings', 'finm_section');
});
add_action('admin_menu', function(){
  add_theme_page(__('FinMarkets Settings','finmarkets'), __('FinMarkets Settings','finmarkets'), 'manage_options', 'finm-settings', function(){
    echo '<div class="wrap"><h1>FinMarkets Settings</h1><form method="post" action="options.php">';
    settings_fields('finm_group');
    do_settings_sections('finm_settings');
    submit_button();
    echo '</form><hr><h2>Connection Test</h2><p>Click to test your API /health endpoint via theme proxy.</p><p><button class="button button-primary" id="finmTest">Run health check</button></p><pre id="finmOut" style="max-height:260px; overflow:auto; background:#111; color:#0f0; padding:12px;">(results here)</pre></div>';
    echo '<script>document.getElementById("finmTest").addEventListener("click", async ()=>{ const out=document.getElementById("finmOut"); out.textContent="Testing..."; try{ const r=await fetch("' . esc_url_raw( rest_url('finm/v1/health') ) . '"); const j=await r.json(); out.textContent=JSON.stringify(j,null,2);}catch(e){ out.textContent=String(e);} });</script>';
  });
});

// ---------- Enqueue styles and scripts ----------
add_action('wp_enqueue_scripts', function () {
  // Inter
  wp_enqueue_style('finmarkets-inter', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap', [], null);
  // Main stylesheet
  wp_enqueue_style('finmarkets-style', get_stylesheet_uri(), ['finmarkets-inter'], wp_get_theme()->get('Version'));
  // Mock + API + App
  wp_enqueue_script('finmarkets-mock', get_template_directory_uri() . '/assets/js/mock.js', [], wp_get_theme()->get('Version'), true);
  wp_enqueue_script('finmarkets-api', get_template_directory_uri() . '/assets/js/api.js', [], wp_get_theme()->get('Version'), true);
  wp_enqueue_script('finmarkets-app', get_template_directory_uri() . '/assets/js/app.js', ['finmarkets-mock','finmarkets-api'], wp_get_theme()->get('Version'), true);

  // Pass REST base
  wp_localize_script('finmarkets-api', 'finmConfig', [
    'restBase' => esc_url_raw( rest_url('finm/v1') ),
    'hasApiBase' => (bool) finm_get_settings()['api_base'],
  ]);
});

// Defer our scripts
add_filter('script_loader_tag', function ($tag, $handle, $src) {
  $defer = ['finmarkets-mock', 'finmarkets-api', 'finmarkets-app'];
  if (in_array($handle, $defer, true)) { return '<script src="' . esc_url($src) . '" defer></script>'; }
  return $tag;
}, 10, 3);

// Security headers (theme-level)
add_action('send_headers', function () {
  header('X-Frame-Options: SAMEORIGIN');
  header('X-XSS-Protection: 1; mode=block');
  header('X-Content-Type-Options: nosniff');
});

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
});

function finm_api_base(){
  $b = finm_get_settings()['api_base'];
  return $b ? rtrim($b, '/') : '';
}
function finm_build_url($path){
  $base = finm_api_base();
  if (!$base) return '';
  // ensure single slash
  return $base . (str_starts_with($path, '/') ? $path : '/' . $path);
}
function finm_req_headers($needs_key=false){
  $h = [ 'Accept' => 'application/json' ];
  $key = finm_get_settings()['api_key'];
  if ($needs_key && $key) { $h['Authorization'] = 'Bearer ' . $key; }
  return $h;
}
function finm_proxy_get($path, $args=[], $needs_key=false){
  $url = finm_build_url($path);
  if (!$url) return new WP_REST_Response(['success'=>false,'message'=>'API base not configured'], 400);
  $q = ['timeout' => 10, 'headers' => finm_req_headers($needs_key)];
  if (!empty($args)) { $url = add_query_arg(array_map('rawurlencode', $args), $url); }
  $r = wp_remote_get($url, $q);
  if (is_wp_error($r)) return new WP_REST_Response(['success'=>false,'message'=>$r->get_error_message()], 502);
  $code = wp_remote_retrieve_response_code($r);
  $body = wp_remote_retrieve_body($r);
  $json = json_decode($body, true);
  if (json_last_error() === JSON_ERROR_NONE) return new WP_REST_Response($json, $code);
  return new WP_REST_Response(['html' => $body, 'status_code' => $code], $code);
}

// Route handlers
function finm_route_health(WP_REST_Request $req){
  // Try /health then /api/health
  $r = finm_proxy_get('/health/');
  if ($r->get_status() >= 400) { $r = finm_proxy_get('/api/health/'); }
  return $r;
}
function finm_route_stocks(WP_REST_Request $req){
  $args = $req->get_params();
  return finm_proxy_get('/api/stocks/', $args);
}
function finm_route_stock(WP_REST_Request $req){
  $ticker = strtoupper(sanitize_text_field($req['ticker']));
  $r = finm_proxy_get('/api/stock/' . rawurlencode($ticker) . '/');
  if ($r->get_status() >= 400) { $r = finm_proxy_get('/api/stocks/' . rawurlencode($ticker) . '/'); }
  return $r;
}
function finm_route_search(WP_REST_Request $req){
  $q = [ 'q' => $req->get_param('q') ];
  return finm_proxy_get('/api/search/', $q);
}
function finm_route_trending(WP_REST_Request $req){
  return finm_proxy_get('/api/trending/');
}
function finm_route_market_stats(WP_REST_Request $req){
  return finm_proxy_get('/api/market-stats/');
}
function finm_route_endpoint_status(WP_REST_Request $req){
  return finm_proxy_get('/endpoint-status/');
}
function finm_route_revenue_analytics(WP_REST_Request $req){
  return finm_proxy_get('/revenue/revenue-analytics/');
}
function finm_route_revenue_analytics_month(WP_REST_Request $req){
  $m = sanitize_text_field($req['month']);
  return finm_proxy_get('/revenue/revenue-analytics/' . rawurlencode($m) . '/');
}