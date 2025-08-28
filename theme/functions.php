<?php
/**
 * Retail Trade Scanner Theme Functions (production-ready)
 */
if (!defined('ABSPATH')) { exit; }

require_once get_template_directory() . '/template-parts/nav-walker.php';

/* ---------------- Theme setup ---------------- */
function rts_theme_setup() {
    load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages');
    add_theme_support('automatic-feed-links');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', [ 'height' => 80, 'width' => 240, 'flex-height' => true, 'flex-width' => true ]);
    add_theme_support('html5', ['search-form','comment-form','comment-list','gallery','caption']);
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('responsive-embeds');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
    add_theme_support('editor-styles');
    add_editor_style();

    register_nav_menus(['primary' => esc_html__('Primary Menu', 'retail-trade-scanner')]);

    global $content_width; if (!isset($content_width)) { $content_width = 1200; }
}
add_action('after_setup_theme', 'rts_theme_setup');

/* ---------------- Sidebar (widgets) ---------------- */
function rts_register_sidebars() {
    register_sidebar([
        'name'          => esc_html__('Primary Sidebar', 'retail-trade-scanner'),
        'id'            => 'primary-sidebar',
        'description'   => esc_html__('Add widgets here to appear in your sidebar.', 'retail-trade-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ]);
}
add_action('widgets_init', 'rts_register_sidebars');

/* ---------------- Helper: detect if current view needs Chart.js ---------------- */
function rts_needs_chart() {
    // Front/home templates include stock widgets
    if (is_front_page() || is_home()) return true;

    // Scan posts in main query for [stock_scanner] shortcode
    global $wp_query;
    if (!empty($wp_query) && is_a($wp_query, 'WP_Query') && !empty($wp_query->posts)) {
        foreach ($wp_query->posts as $p) {
            if (!empty($p->post_content) && has_shortcode($p->post_content, 'stock_scanner')) {
                return true;
            }
        }
    }

    // Common tool pages that typically render charts
    if (is_page(array('stock-dashboard','stock-search','personalized-stock-finder'))) return true;

    return false;
}

/* ---------------- Enqueue styles/scripts (with Chart.js lazy-loading) ---------------- */
function rts_scripts() {
    wp_enqueue_style('rts-style', get_stylesheet_uri(), [], '2.2.0');

    // Chart.js: prefer existing 'chartjs' handle (from plugins), else load local copy when needed
    if (wp_script_is('chartjs', 'registered') || wp_script_is('chartjs', 'enqueued')) {
        if (rts_needs_chart()) {
            wp_enqueue_script('chartjs');
        }
    } else {
        if (!wp_script_is('chart-js', 'registered') && !wp_script_is('chart-js', 'enqueued')) {
            wp_register_script('chart-js', get_template_directory_uri() . '/js/vendor/chart.umd.min.js', [], '4.4.3', true);
            if (function_exists('wp_script_add_data')) { wp_script_add_data('chart-js', 'defer', true); }
        }
        if (rts_needs_chart()) {
            wp_enqueue_script('chart-js');
        }
    }

    // Theme script (no dependency on Chart.js)
    wp_enqueue_script('rts-js', get_template_directory_uri() . '/js/theme.js', ['jquery'], '2.2.0', true);
    if (function_exists('wp_script_add_data')) { wp_script_add_data('rts-js', 'defer', true); }

    // Localized data
    $idle_enabled = (int) get_option('rts_idle_enabled', 1);
    $idle_hours   = max(1, (int) get_option('rts_idle_hours', 12));

    // Prefer stock_scanner_api_url, fallback to retail_trade_scanner_api_url
    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    if (empty($api_base)) { $api_base = rtrim(get_option('retail_trade_scanner_api_url', ''), '/'); }

    wp_localize_script('rts-js', 'retail_trade_scanner_theme', [
        'ajax_url'          => admin_url('admin-ajax.php'),
        'nonce'             => wp_create_nonce('retail_trade_scanner_theme_nonce'),
        'logged_in'         => is_user_logged_in(),
        'logout_url'        => wp_logout_url(home_url('/')),
        'user_id'           => is_user_logged_in() ? get_current_user_id() : 0,
        'idle_enabled'      => (bool) $idle_enabled,
        'idle_limit_ms'     => $idle_hours * 60 * 60 * 1000,
        'warn_threshold_ms' => 2 * 60 * 1000,
        'no_backend'        => empty($api_base),
    ]);
}
add_action('wp_enqueue_scripts', 'rts_scripts');

/* Resource hints */
add_filter('wp_resource_hints', function($hints, $rel){ if ($rel==='preconnect'){ $hints[]='https://fonts.googleapis.com'; $hints[]=['href'=>'https://fonts.gstatic.com','crossorigin']; } return $hints; }, 10, 2);

/* Fallback menu for nav walker */
function rts_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . esc_url(home_url('/membership-plans/')) . '">' . esc_html__('Plans', 'retail-trade-scanner') . '</a></li>';
    echo '<li><a href="' . esc_url(home_url('/stock-search/')) . '">' . esc_html__('Stock Search', 'retail-trade-scanner') . '</a></li>';
    echo '<li><a href="' . esc_url(home_url('/popular-stock-lists/')) . '">' . esc_html__('Popular Lists', 'retail-trade-scanner') . '</a></li>';
    echo '<li><a href="' . esc_url(home_url('/membership-account/')) . '">' . esc_html__('My Account', 'retail-trade-scanner') . '</a></li>';
    echo '</ul>';
}

/* Body classes by membership */
add_filter('body_class', function($classes){ if (is_user_logged_in() && function_exists('pmpro_getMembershipLevelForUser')) { $l=pmpro_getMembershipLevelForUser(get_current_user_id()); $id=$l? (int)$l->id:0; $map=[0=>'membership-free',1=>'membership-free',2=>'membership-premium',3=>'membership-professional',4=>'membership-gold']; if(isset($map[$id])) $classes[]=$map[$id]; } return $classes;});

/* Login page tweaks */
add_filter('login_headerurl', function(){ return home_url(); });
add_filter('login_headertext', function(){ return get_bloginfo('name') . ' - ' . esc_html__('Retail Trade Scanner', 'retail-trade-scanner'); });

/* Dashboard widget */
add_action('wp_dashboard_setup', function(){ wp_add_dashboard_widget('rts_widget', esc_html__('📈 Retail Trade Scanner Quick View','retail-trade-scanner'), function(){ ?>
<div class="retail-trade-scanner-dashboard-widget">
  <p><strong><?php esc_html_e('Popular Stocks Today:', 'retail-trade-scanner'); ?></strong></p>
  <div class="dashboard-widget-grid">
    <?php echo do_shortcode('[stock_scanner symbol="AAPL"]'); ?>
    <?php echo do_shortcode('[stock_scanner symbol="TSLA"]'); ?>
    <?php echo do_shortcode('[stock_scanner symbol="NVDA"]'); ?>
  </div>
  <p><a href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>" class="button button-primary"><?php esc_html_e('View Full Dashboard','retail-trade-scanner'); ?></a></p>
</div>
<?php }); });

/* Admin menu + options page with Health test button */
add_action('admin_menu', function(){ add_theme_page(esc_html__('Retail Trade Scanner Options','retail-trade-scanner'), esc_html__('Trade Scanner','retail-trade-scanner'), 'manage_options', 'retail-trade-scanner-options', 'rts_options_page'); });
function rts_save_theme_options(){ if(!current_user_can('manage_options')){ wp_die(esc_html__('Insufficient permissions.','retail-trade-scanner')); } check_admin_referer('rts_save_theme'); $enabled = isset($_POST['rts_idle_enabled'])?1:0; $hours=max(1,(int)($_POST['rts_idle_hours']??12)); update_option('rts_idle_enabled',$enabled); update_option('rts_idle_hours',$hours); wp_safe_redirect(add_query_arg('updated','1', wp_get_referer()?: admin_url('themes.php?page=retail-trade-scanner-options'))); exit; }
add_action('admin_post_rts_save_theme','rts_save_theme_options');
function rts_options_page(){ $enabled=(int)get_option('rts_idle_enabled',1); $hours=(int)get_option('rts_idle_hours',12); ?>
<div class="wrap">
  <h1><?php esc_html_e('📈 Retail Trade Scanner Theme Options','retail-trade-scanner'); ?></h1>
  <?php if(!empty($_GET['updated'])): ?><div class="notice notice-success is-dismissible"><p><?php esc_html_e('Settings saved.','retail-trade-scanner'); ?></p></div><?php endif; ?>

  <div class="card">
    <h2><?php esc_html_e('🔒 Session Policy','retail-trade-scanner'); ?></h2>
    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
      <?php wp_nonce_field('rts_save_theme'); ?><input type="hidden" name="action" value="rts_save_theme" />
      <table class="form-table" role="presentation">
        <tr><th><label for="rts_idle_enabled"><?php esc_html_e('Enable idle auto-logout','retail-trade-scanner'); ?></label></th><td><label><input type="checkbox" id="rts_idle_enabled" name="rts_idle_enabled" value="1" <?php checked($enabled,1); ?> /> <?php esc_html_e('After inactivity, sign out users automatically','retail-trade-scanner'); ?></label></td></tr>
        <tr><th><label for="rts_idle_hours"><?php esc_html_e('Idle timeout (hours)','retail-trade-scanner'); ?></label></th><td><input type="number" id="rts_idle_hours" name="rts_idle_hours" min="1" max="72" step="1" value="<?php echo esc_attr($hours); ?>" /><p class="description"><?php esc_html_e('Default: 12 hours.','retail-trade-scanner'); ?></p></td></tr>
      </table>
      <?php submit_button(); ?>
    </form>
  </div>

  <div class="card">
    <h2><?php esc_html_e('🩺 Backend Health','retail-trade-scanner'); ?></h2>
    <p><?php esc_html_e('Test the configured API health endpoint and view the response.','retail-trade-scanner'); ?></p>
    <p><button id="rts-test-health" class="button button-secondary"><?php esc_html_e('Test Backend Health','retail-trade-scanner'); ?></button></p>
    <pre id="rts-health-output" style="max-height:280px;overflow:auto;background:#111;color:#ddd;padding:12px;border-radius:8px;"></pre>
    <script>
      jQuery(function($){
        $('#rts-test-health').on('click', function(){
          var $out = $('#rts-health-output');
          $out.text('<?php echo esc_js(__('Testing…', 'retail-trade-scanner')); ?>');
          $.post(ajaxurl, { action: 'retail_trade_scanner_get_health', nonce: '<?php echo esc_js(wp_create_nonce('retail_trade_scanner_theme_nonce')); ?>' }, function(res){
            try { $out.text(JSON.stringify(res, null, 2)); } catch(e){ $out.text(res ? String(res) : ''); }
          }).fail(function(xhr){ $out.text('Error: ' + (xhr.responseText || xhr.status)); });
        });
      });
    </script>
  </div>
</div>
<?php }

/* ---------- Excerpt and Read More ---------- */
add_filter('excerpt_length', function(){ return 26; });
add_filter('excerpt_more', function(){ return ' …'; });

/* ---------------- AJAX: plan badge via backend ---------------- */
function rts_ajax_current_plan(){ if(!is_user_logged_in()){ wp_send_json_error(['message'=>'Unauthenticated'],401);} check_ajax_referer('retail_trade_scanner_theme_nonce','nonce'); $api_base=rtrim(get_option('stock_scanner_api_url',''),'/'); if (empty($api_base)) { $api_base=rtrim(get_option('retail_trade_scanner_api_url',''),'/'); } $secret=get_option('stock_scanner_api_secret',''); if (empty($secret)) { $secret = get_option('retail_trade_scanner_api_secret',''); } if(empty($api_base)||empty($secret)){ $plan=rts_plan_from_pmpro(get_current_user_id()); wp_send_json_success(['source'=>'pmpro','plan'=>$plan]); }
    $url=$api_base.'/billing/current-plan/'; $user_id=get_current_user_id(); $level_id=0; if(function_exists('pmpro_getMembershipLevelForUser')){ $l=pmpro_getMembershipLevelForUser($user_id); $level_id=$l? (int)$l->id:0; }
    $res=wp_remote_get($url,['headers'=>['Content-Type'=>'application/json','X-API-Secret'=>$secret,'X-User-Level'=>$level_id,'X-User-ID'=>$user_id],'timeout'=>20]);
    if(is_wp_error($res)){ $plan=rts_plan_from_pmpro($user_id); wp_send_json_success(['source'=>'fallback','plan'=>$plan,'error'=>$res->get_error_message()]); }
    $code=wp_remote_retrieve_response_code($res); $body=wp_remote_retrieve_body($res); if($code>=200 && $code<300){ $data=json_decode($body,true); if(!$data){ wp_send_json_success(['source'=>'backend','raw'=>$body]); } wp_send_json_success(['source'=>'backend','data'=>$data]); }
    $plan=rts_plan_from_pmpro($user_id); wp_send_json_success(['source'=>'fallback','plan'=>$plan,'status'=>$code]); }
add_action('wp_ajax_retail_trade_scanner_get_current_plan','rts_ajax_current_plan');
function rts_plan_from_pmpro($user_id){ $plan=['name'=>'Free','slug'=>'free','premium'=>false,'level_id'=>0]; if(function_exists('pmpro_getMembershipLevelForUser')){ $l=pmpro_getMembershipLevelForUser($user_id); if($l){ $id=(int)$l->id; $plan['level_id']=$id; if ($id===2) { $plan=['name'=>'Premium','slug'=>'premium','premium'=>true,'level_id'=>2]; } elseif ($id===3) { $plan=['name'=>'Professional','slug'=>'professional','premium'=>true,'level_id'=>3]; } elseif ($id===4) { $plan=['name'=>'Gold','slug'=>'gold','premium'=>true,'level_id'=>4]; } } } return $plan; }

/* ---------------- Admin notices if API config missing ---------------- */
add_action('admin_notices', function(){ if(!current_user_can('manage_options')) return; $api_url=get_option('stock_scanner_api_url',''); if (empty($api_url)) { $api_url=get_option('retail_trade_scanner_api_url',''); } $api_secret=get_option('stock_scanner_api_secret',''); if (empty($api_secret)) { $api_secret=get_option('retail_trade_scanner_api_secret',''); } if(empty($api_url)||empty($api_secret)){ $link=esc_url(admin_url('options-general.php?page=stock-scanner-settings')); echo '<div class="notice notice-warning is-dismissible"><p>'. sprintf(esc_html__('Retail Trade Scanner: Please configure the API URL and Secret in %s.','retail-trade-scanner'), '<a href="'.$link.'">'.esc_html__('Settings → Stock Scanner','retail-trade-scanner').'</a>').'</p></div>'; }});

/* ---------------- Ensure screenshot.png exists ---------------- */
add_action('admin_init', function(){ $path=get_stylesheet_directory().'/screenshot.png'; if(file_exists($path)) return; if(function_exists('imagecreatetruecolor')){ $w=1200;$h=900;$im=imagecreatetruecolor($w,$h); $bg=imagecolorallocate($im,240,242,245); imagefilledrectangle($im,0,0,$w,$h,$bg); $bar=imagecolorallocate($im,102,126,234); imagefilledrectangle($im,0,0,$w,12,$bar); $txt=imagecolorallocate($im,51,65,85); imagestring($im,5,40,40,'Retail Trade Scanner Theme',$txt); imagestring($im,3,40,70,'Professional WordPress theme for retail trade analysis',$txt); imagepng($im,$path); imagedestroy($im); } else { $b64='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottQAAAABJRU5ErkJggg=='; file_put_contents($path, base64_decode($b64)); } });

/* ---------------- Featured pages shortcode ---------------- */
function rts_featured_pages_shortcode($atts){ $atts=shortcode_atts(['ids'=>'','count'=>3,'parent'=>0],$atts,'featured_pages'); $args=['post_type'=>'page','posts_per_page'=>max(1,(int)$atts['count']),'orderby'=>'menu_order title','order'=>'ASC']; if(!empty($atts['ids'])){ $ids=array_map('intval', explode(',', $atts['ids'])); $args['post__in']=$ids; $args['orderby']='post__in'; } if(!empty($atts['parent'])){ $args['post_parent']=(int)$atts['parent']; } $q=new WP_Query($args); ob_start(); if($q->have_posts()): ?>
<div class="pricing-table">
  <?php while($q->have_posts()): $q->the_post(); ?>
  <article <?php post_class('card'); ?> >
    <div class="card-header"><h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3></div>
    <div class="card-body">
      <?php if(has_post_thumbnail()){ echo get_the_post_thumbnail(get_the_ID(), 'medium_large', ['class'=>'card-thumbnail','loading'=>'lazy','decoding'=>'async']); } ?>
      <?php the_excerpt(); ?>
    </div>
    <div class="card-footer"><a class="btn btn-primary" href="<?php the_permalink(); ?>"><span><?php esc_html_e('Learn More','retail-trade-scanner'); ?></span></a></div>
  </article>
  <?php endwhile; wp_reset_postdata(); ?>
</div>
<?php else: ?>
<div class="card"><div class="card-body"><?php esc_html_e('No pages selected.','retail-trade-scanner'); ?></div></div>
<?php endif; return ob_get_clean(); }
add_shortcode('featured_pages','rts_featured_pages_shortcode');

/* ---------------- Theme Customizer ---------------- */
function rts_customize_register($wp_customize){
    $wp_customize->add_section('rts_header', ['title'=>__('Header','retail-trade-scanner'),'priority'=>30]);
    $wp_customize->add_setting('rts_show_upgrade', ['default'=>true,'sanitize_callback'=>'rest_sanitize_boolean']);
    $wp_customize->add_control('rts_show_upgrade', ['type'=>'checkbox','section'=>'rts_header','label'=>__('Show Upgrade button for members','retail-trade-scanner')]);

    $wp_customize->add_section('rts_footer', ['title'=>__('Footer','retail-trade-scanner'),'priority'=>31]);
    $wp_customize->add_setting('rts_footer_show_user_links', ['default'=>true,'sanitize_callback'=>'rest_sanitize_boolean']);
    $wp_customize->add_control('rts_footer_show_user_links', ['type'=>'checkbox','section'=>'rts_footer','label'=>__('Show user links in footer when signed in','retail-trade-scanner')]);
}
add_action('customize_register','rts_customize_register');

/* ---------------- Basic Schema Markup ---------------- */
add_action('wp_head', function(){ $schema=['@context'=>'https://schema.org','@type'=> is_front_page()? 'WebSite':'WebPage','name'=> get_bloginfo('name'),'url'=> home_url('/')]; if(is_singular()){ $schema['@type']='Article'; $schema['headline']=get_the_title(); $schema['datePublished']=get_post_time('c',true); $schema['dateModified']=get_post_modified_time('c',true);} echo '<script type="application/ld+json">'. wp_json_encode($schema) .'</script>'; }, 99);

/* ---------------- Reusable Upgrade CTA ---------------- */
function rts_upgrade_cta($atts = []) {
    $defaults = ['style' => 'banner'];
    $atts = shortcode_atts($defaults, $atts, 'upgrade_cta');

    $is_logged = is_user_logged_in();
    $plan = $is_logged ? rts_plan_from_pmpro(get_current_user_id()) : ['slug' => 'guest', 'name' => 'Guest', 'premium' => false];

    // Hide CTA for high-tier users
    if (!empty($plan['premium'])) return '';

    ob_start(); ?>
    <section class="card upgrade-cta">
      <div class="card-header">
        <h2 class="card-title"><?php echo $is_logged ? esc_html__('Unlock more with Premium', 'retail-trade-scanner') : esc_html__('Start free, upgrade anytime', 'retail-trade-scanner'); ?></h2>
        <div class="card-subtitle"><?php echo $is_logged ? esc_html__('Higher limits, more tools, priority access.', 'retail-trade-scanner') : esc_html__('Create an account to access more tools and insights.', 'retail-trade-scanner'); ?></div>
      </div>
      <div class="card-body">
        <ul class="feature-list">
          <li><?php esc_html_e('Advanced screening & filters', 'retail-trade-scanner'); ?></li>
          <li><?php esc_html_e('Real-time widgets & longer history', 'retail-trade-scanner'); ?></li>
          <li><?php esc_html_e('Higher monthly usage limits', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>
      <div class="card-footer">
        <?php if ($is_logged) : ?>
          <a class="btn btn-gold" href="<?php echo esc_url(home_url('/membership-account/membership-checkout/')); ?>"><?php esc_html_e('Upgrade now', 'retail-trade-scanner'); ?></a>
        <?php else: ?>
          <a class="btn btn-primary" href="<?php echo esc_url(wp_registration_url()); ?>"><?php esc_html_e('Create account', 'retail-trade-scanner'); ?></a>
          <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/membership-plans/')); ?>"><?php esc_html_e('See plans', 'retail-trade-scanner'); ?></a>
        <?php endif; ?>
      </div>
    </section>
    <?php return ob_get_clean();
}
add_shortcode('upgrade_cta', 'rts_upgrade_cta');

/* ---------------- AJAX: Backend health check for admin tools ---------------- */
add_action('wp_ajax_retail_trade_scanner_get_health', function(){
    if (!current_user_can('manage_options')) {
        wp_send_json_error(['message' => esc_html__('Unauthorized', 'retail-trade-scanner')], 403);
    }
    check_ajax_referer('retail_trade_scanner_theme_nonce', 'nonce');

    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    if (empty($api_base)) { $api_base = rtrim(get_option('retail_trade_scanner_api_url', ''), '/'); }
    $secret   = get_option('stock_scanner_api_secret', '');
    if (empty($secret)) { $secret = get_option('retail_trade_scanner_api_secret', ''); }

    if (empty($api_base)) {
        wp_send_json_error(['message' => esc_html__('API base URL is not configured.', 'retail-trade-scanner')]);
    }

    $url  = trailingslashit($api_base) . 'health/';
    $args = [
        'timeout' => 20,
        'headers' => array_filter([
            'Content-Type' => 'application/json',
            'X-API-Secret' => $secret,
        ]),
    ];

    $res = wp_remote_get($url, $args);
    if (is_wp_error($res)) {
        wp_send_json_error(['message' => $res->get_error_message()]);
    }
    $code = (int) wp_remote_retrieve_response_code($res);
    $body = wp_remote_retrieve_body($res);
    $data = json_decode($body, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($data)) {
        wp_send_json_success(['status' => $code, 'data' => $data]);
    }
    wp_send_json_success(['status' => $code, 'raw' => $body]);
});

/* ---------------- Shortcode alias: [stock_scanner] -> [retail_trade_scanner] ---------------- */
if (!shortcode_exists('stock_scanner')) {
    add_shortcode('stock_scanner', function($atts = []){
        $atts = is_array($atts) ? $atts : [];
        // If the primary shortcode exists, delegate to it
        if (shortcode_exists('retail_trade_scanner')) {
            // Build attribute string safely
            $parts = [];
            foreach ($atts as $k => $v) {
                $parts[] = sanitize_key($k) . '="' . esc_attr($v) . '"';
            }
            $attr_str = $parts ? (' ' . implode(' ', $parts)) : '';
            return do_shortcode('[retail_trade_scanner' . $attr_str . ']');
        }
        // Graceful fallback UI
        ob_start(); ?>
        <div class="card">
            <div class="card-body">
                <?php esc_html_e('Stock widget is unavailable. Please configure the Retail Trade Scanner plugin/API.', 'retail-trade-scanner'); ?>
            </div>
        </div>
        <?php return ob_get_clean();
    });
}