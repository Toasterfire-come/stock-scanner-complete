<?php
/**
 * Stock Scanner Theme Functions
 */
if (!defined('ABSPATH')) { exit; }

/* ---------------- Theme setup ---------------- */
function stock_scanner_theme_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', [ 'height' => 80, 'width'  => 240, 'flex-height' => true, 'flex-width' => true ]);
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('customize-selective-refresh-widgets');
    register_nav_menus(array('primary' => __('Primary Menu', 'stock-scanner')));
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/* ---------------- Sidebar (widgets) ---------------- */
function stock_scanner_register_sidebars() {
    register_sidebar(array(
        'name'          => __('Primary Sidebar', 'stock-scanner'),
        'id'            => 'primary-sidebar',
        'description'   => __('Add widgets here to appear in your sidebar.', 'stock-scanner'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
}
add_action('widgets_init', 'stock_scanner_register_sidebars');

/* ---------------- Enqueue styles/scripts ---------------- */
function stock_scanner_scripts() {
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '1.1.0');
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '1.1.0', true);
    // Defer non-critical scripts for perf
    if (function_exists('wp_script_add_data')) {
        wp_script_add_data('stock-scanner-js', 'defer', true);
        wp_script_add_data('chart-js', 'defer', true);
    }
    wp_localize_script('stock-scanner-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce'),
        'logged_in' => is_user_logged_in(),
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/* Preconnect to Google Fonts for perf */
function stock_scanner_resource_hints($hints, $relation_type) {
    if ('preconnect' === $relation_type) {
        $hints[] = 'https://fonts.googleapis.com';
        $hints[] = array('href' => 'https://fonts.gstatic.com', 'crossorigin');
    }
    return $hints;
}
add_filter('wp_resource_hints', 'stock_scanner_resource_hints', 10, 2);

/* ---------------- Fallback menu ---------------- */
function stock_scanner_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . esc_url(home_url('/premium-plans/')) . '">Premium Plans</a></li>';
    echo '<li><a href="' . esc_url(home_url('/email-stock-lists/')) . '">Email Lists</a></li>';
    echo '<li><a href="' . esc_url(home_url('/stock-search/')) . '">Stock Search</a></li>';
    echo '<li><a href="' . esc_url(home_url('/popular-stock-lists/')) . '">Popular Lists</a></li>';
    echo '<li><a href="' . esc_url(home_url('/news-scrapper/')) . '">News Scraper</a></li>';
    echo '<li><a href="' . esc_url(home_url('/membership-account/')) . '">My Account</a></li>';
    echo '</ul>';
}

/* ---------------- Body classes for membership ---------------- */
function stock_scanner_body_classes($classes) {
    if (is_user_logged_in() && function_exists('pmpro_getMembershipLevelForUser')) {
        $level = pmpro_getMembershipLevelForUser(get_current_user_id());
        $level_id = $level ? $level->id : 0;
        $level_classes = array(0 => 'membership-free', 1 => 'membership-free', 2 => 'membership-premium', 3 => 'membership-professional', 4 => 'membership-gold');
        if (isset($level_classes[$level_id])) $classes[] = $level_classes[$level_id];
    }
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/* ---------------- Login page styles ---------------- */
function stock_scanner_login_styles() {
    ?>
    <style>.login h1 a{background-image:none;width:100%;height:65px;font-size:24px;font-weight:bold;line-height:65px;text-indent:0}.login h1 a::before{content:"📈 Stock Scanner";color:#667eea}.login form{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border:none;box-shadow:0 8px 30px rgba(0,0,0,.12)}.login form .input{background:rgba(255,255,255,.9);border:none;border-radius:5px;margin-bottom:10px}.login form .button-primary{background:#f39c12;border:none;border-radius:5px}</style>
    <?php
}
add_action('login_enqueue_scripts', 'stock_scanner_login_styles');
function stock_scanner_login_logo_url() { return home_url(); }
add_filter('login_headerurl', 'stock_scanner_login_logo_url');
function stock_scanner_login_logo_url_title() { return get_bloginfo('name') . ' - Stock Scanner'; }
add_filter('login_headertitle', 'stock_scanner_login_logo_url_title');

/* ---------------- Dashboard widget ---------------- */
function stock_scanner_dashboard_widget() { wp_add_dashboard_widget('stock_scanner_widget','📈 Stock Scanner Quick View','stock_scanner_dashboard_widget_content'); }
add_action('wp_dashboard_setup', 'stock_scanner_dashboard_widget');
function stock_scanner_dashboard_widget_content() {
    ?>
    <div class="stock-scanner-dashboard-widget">
        <p><strong>Popular Stocks Today:</strong></p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:15px 0;">
            <?php echo do_shortcode('[stock_scanner symbol="AAPL"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="TSLA"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="NVDA"]'); ?>
        </div>
        <p><a href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>" class="button button-primary">View Full Dashboard</a></p>
    </div>
    <?php
}

/* ---------------- Admin menu quick links ---------------- */
function stock_scanner_admin_menu() { add_theme_page('Stock Scanner Options','Stock Scanner','manage_options','stock-scanner-options','stock_scanner_options_page'); }
add_action('admin_menu', 'stock_scanner_admin_menu');
function stock_scanner_options_page() {
    ?>
    <div class="wrap">
        <h1>📈 Stock Scanner Theme Options</h1>
        <div class="card"><h2>🔗 Quick Links</h2><ul>
            <li><a href="<?php echo esc_url(admin_url('options-general.php?page=stock-scanner-settings')); ?>">Plugin Settings</a></li>
            <li><a href="<?php echo esc_url(admin_url('edit.php?post_type=page')); ?>">Manage Pages</a></li>
            <li><a href="<?php echo esc_url(admin_url('nav-menus.php')); ?>">Customize Menus</a></li>
            <li><a href="<?php echo esc_url(admin_url('users.php?page=pmpro-memberslist')); ?>">Member List</a></li>
        </ul></div>
        <div class="card"><h2>🚀 Getting Started</h2>
            <ol>
                <li>Activate the Stock Scanner plugin and configure API settings</li>
                <li>Set up Paid Memberships Pro levels</li>
                <li>Create a page using template "Backend Offline" for diagnostics</li>
            </ol>
        </div>
    </div>
    <?php
}

/* ---------------- Remove admin bar for non-admins ---------------- */
function stock_scanner_remove_admin_bar() { if (!current_user_can('administrator') && !is_admin()) { show_admin_bar(false); } }
add_action('after_setup_theme', 'stock_scanner_remove_admin_bar');

/* ---------------- Membership & plan badge styles ---------------- */
function stock_scanner_membership_styles() {
    ?>
    <style>
        .membership-premium .stock-scanner-widget{border-left:4px solid #f39c12}
        .membership-professional .stock-scanner-widget{border-left:4px solid #9b59b6;background:linear-gradient(135deg,#fff 0%,#f4f1f8 100%)}
        .membership-premium .upgrade-notice,.membership-professional .upgrade-notice{display:none}
        .plan-badge{background:#eef0f2;border:2px solid #cfd6dd;padding:6px 12px;border-radius:999px;font-size:.85rem;font-weight:600;color:#334155}
        .plan-badge.premium{border-color:#f39c12;color:#f39c12}.plan-badge.professional{border-color:#9b59b6;color:#9b59b6}.plan-badge.gold{border-color:#c9a961;color:#c9a961}.plan-badge.silver{border-color:#95a5a6;color:#95a5a6}
        /* Widgets */
        .widget{background:var(--white);border:1px solid var(--medium-gray);border-radius:12px;padding:18px;box-shadow:var(--shadow-sm)}
        .widget-title{margin:0 0 12px;background:var(--primary-gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
        /* Skip link */
        .skip-link{position:absolute;left:-999px;top:auto;width:1px;height:1px;overflow:hidden}
        .skip-link:focus{position:absolute;left:12px;top:12px;width:auto;height:auto;padding:8px 12px;background:#111827;color:#fff;border-radius:8px;z-index:9999}
        /* Focus visible */
        a:focus-visible, button:focus-visible, input:focus-visible{outline:3px solid #667eea;outline-offset:2px;border-radius:6px}
    </style>
    <?php
}
add_action('wp_head', 'stock_scanner_membership_styles');

/* ---------------- AJAX: plan badge via backend ---------------- */
function stock_scanner_get_current_plan_ajax() {
    if (!is_user_logged_in()) { wp_send_json_error(array('message' => 'Unauthenticated'), 401); }
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    $secret = get_option('stock_scanner_api_secret', '');
    if (empty($api_base) || empty($secret)) {
        $user_id = get_current_user_id();
        $plan = stock_scanner_plan_from_pmpro($user_id);
        wp_send_json_success(array('source'=>'pmpro','plan'=>$plan));
    }
    $url = $api_base . '/billing/current-plan';
    $user_id = get_current_user_id();
    $level_id = 0;
    if (function_exists('pmpro_getMembershipLevelForUser')) { $level = pmpro_getMembershipLevelForUser($user_id); $level_id = $level ? intval($level->id) : 0; }
    $response = wp_remote_get($url, array('headers'=>array('Content-Type'=>'application/json','X-API-Secret'=>$secret,'X-User-Level'=>$level_id,'X-User-ID'=>$user_id), 'timeout'=>20));
    if (is_wp_error($response)) { $plan = stock_scanner_plan_from_pmpro($user_id); wp_send_json_success(array('source'=>'fallback','plan'=>$plan,'error'=>$response->get_error_message())); }
    $code = wp_remote_retrieve_response_code($response); $body = wp_remote_retrieve_body($response);
    if ($code>=200 && $code<300) { $data = json_decode($body, true); if (!$data) { wp_send_json_success(array('source'=>'backend','raw'=>$body)); } wp_send_json_success(array('source'=>'backend','data'=>$data)); }
    $plan = stock_scanner_plan_from_pmpro($user_id); wp_send_json_success(array('source'=>'fallback','plan'=>$plan,'status'=>$code));
}
add_action('wp_ajax_stock_scanner_get_current_plan', 'stock_scanner_get_current_plan_ajax');

/* Map PMPro -> simple plan object */
function stock_scanner_plan_from_pmpro($user_id) {
    $plan = array('name'=>'Free','slug'=>'free','premium'=>false,'level_id'=>0);
    if (function_exists('pmpro_getMembershipLevelForUser')) {
        $level = pmpro_getMembershipLevelForUser($user_id);
        if ($level) {
            $plan['level_id'] = intval($level->id);
            switch (intval($level->id)) {
                case 2: $plan['name']='Premium'; $plan['slug']='premium'; $plan['premium']=true; break;
                case 3: $plan['name']='Professional'; $plan['slug']='professional'; $plan['premium']=true; break;
                case 4: $plan['name']='Gold'; $plan['slug']='gold'; $plan['premium']=true; break;
                default: $plan['name']='Free'; $plan['slug']='free'; $plan['premium']=false; break;
            }
        }
    }
    return $plan;
}

/* ---------------- AJAX: Admin-only health ---------------- */
function stock_scanner_get_health_ajax() {
    if (!current_user_can('manage_options')) { wp_send_json_error(array('message'=>'Forbidden'), 403); }
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    $secret = get_option('stock_scanner_api_secret', '');
    if (empty($api_base)) { wp_send_json_error(array('message'=>'API base not configured')); }
    $headers = array('Content-Type'=>'application/json'); if (!empty($secret)) { $headers['X-API-Secret'] = $secret; }
    $response = wp_remote_get($api_base . '/health', array('headers'=>$headers,'timeout'=>15));
    if (is_wp_error($response)) { wp_send_json_error(array('message'=>$response->get_error_message())); }
    $code = wp_remote_retrieve_response_code($response); $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true); if ($data === null) { wp_send_json_success(array('status'=>$code,'raw'=>$body)); }
    wp_send_json_success(array('status'=>$code,'data'=>$data));
}
add_action('wp_ajax_stock_scanner_get_health', 'stock_scanner_get_health_ajax');

/* ---------------- Admin notice if API config missing ---------------- */
function stock_scanner_admin_notices() {
    if (!current_user_can('manage_options')) return;
    $api_url = get_option('stock_scanner_api_url', '');
    $api_secret = get_option('stock_scanner_api_secret', '');
    if (empty($api_url) || empty($api_secret)) {
        $settings_link = esc_url(admin_url('options-general.php?page=stock-scanner-settings'));
        echo '<div class="notice notice-warning is-dismissible"><p>Stock Scanner: Please configure the API URL and Secret in <a href="' . $settings_link . '">Settings → Stock Scanner</a> to enable plan badges and health checks.</p></div>';
    }
}
add_action('admin_notices', 'stock_scanner_admin_notices');

/* ---------------- Ensure screenshot.png exists ---------------- */
function stock_scanner_ensure_screenshot() {
    $path = get_stylesheet_directory() . '/screenshot.png';
    if (file_exists($path)) return;
    if (function_exists('imagecreatetruecolor')) {
        $w=1200;$h=900; $im=imagecreatetruecolor($w,$h);
        $bg=imagecolorallocate($im, 240, 242, 245); imagefilledrectangle($im,0,0,$w,$h,$bg);
        $bar=imagecolorallocate($im, 102,126,234); imagefilledrectangle($im,0,0,$w,12,$bar);
        $txt=imagecolorallocate($im, 51,65,85); imagestring($im, 5, 40, 40, 'Stock Scanner Theme', $txt);
        imagestring($im, 3, 40, 70, 'Professional WordPress theme for stock analysis', $txt);
        imagepng($im, $path); imagedestroy($im);
        return;
    }
    $b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottQAAAABJRU5ErkJggg==';
    file_put_contents($path, base64_decode($b64));
}
add_action('admin_init', 'stock_scanner_ensure_screenshot');

/* ---------------- Featured posts shortcode ---------------- */
function stock_scanner_featured_posts_shortcode($atts) {
    $atts = shortcode_atts(array('count'=>3,'category'=>'','sticky'=>'auto'), $atts, 'featured_posts');
    $count = max(1, intval($atts['count']));
    $query_args = array('posts_per_page'=>$count, 'ignore_sticky_posts'=>false);
    if ($atts['sticky']==='only') { $sticky = get_option('sticky_posts'); $query_args['post__in'] = $sticky; $query_args['orderby']='date'; }
    if (!empty($atts['category'])) { $query_args['category_name'] = sanitize_text_field($atts['category']); }
    $q = new WP_Query($query_args);
    ob_start();
    if ($q->have_posts()): ?>
      <div class="pricing-table" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
        <?php while($q->have_posts()): $q->the_post(); ?>
          <article <?php post_class('card'); ?> >
            <div class="card-header">
              <h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
              <div class="card-subtitle"><?php echo esc_html(get_the_date()); ?></div>
            </div>
            <div class="card-body">
              <?php if (has_post_thumbnail()) {
                echo get_the_post_thumbnail(get_the_ID(), 'medium_large', array('style'=>'border-radius:12px;width:100%;height:auto;margin-bottom:10px;','loading'=>'lazy','decoding'=>'async'));
              } ?>
              <?php the_excerpt(); ?>
            </div>
            <div class="card-footer"><a class="btn btn-primary" href="<?php the_permalink(); ?>"><span>Read More</span></a></div>
          </article>
        <?php endwhile; wp_reset_postdata(); ?>
      </div>
    <?php else: ?>
      <div class="card"><div class="card-body">No featured posts yet.</div></div>
    <?php endif; return ob_get_clean();
}
add_shortcode('featured_posts', 'stock_scanner_featured_posts_shortcode');

/* ---------------- Customizer: brand colors & typography ---------------- */
function stock_scanner_customize_register($wp_customize){
    $wp_customize->add_section('ssc_branding', array('title'=>__('Branding','stock-scanner'),'priority'=>30));
    $wp_customize->add_setting('ssc_primary_start', array('default'=>'#667eea','sanitize_callback'=>'sanitize_hex_color'));
    $wp_customize->add_setting('ssc_primary_end', array('default'=>'#764ba2','sanitize_callback'=>'sanitize_hex_color'));
    $wp_customize->add_setting('ssc_accent', array('default'=>'#f39c12','sanitize_callback'=>'sanitize_hex_color'));
    $wp_customize->add_setting('ssc_radius', array('default'=>12,'sanitize_callback'=>'absint'));
    $wp_customize->add_setting('ssc_body_font', array('default'=>'system','sanitize_callback'=>'sanitize_text_field'));
    $wp_customize->add_setting('ssc_heading_font', array('default'=>'playfair','sanitize_callback'=>'sanitize_text_field'));
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize,'ssc_primary_start',array('label'=>__('Primary Gradient Start','stock-scanner'),'section'=>'ssc_branding')));
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize,'ssc_primary_end',array('label'=>__('Primary Gradient End','stock-scanner'),'section'=>'ssc_branding')));
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize,'ssc_accent',array('label'=>__('Accent Color','stock-scanner'),'section'=>'ssc_branding')));
    $wp_customize->add_control('ssc_radius', array('type'=>'range','label'=>__('Corner Radius (px)','stock-scanner'),'section'=>'ssc_branding','input_attrs'=>array('min'=>0,'max'=>24,'step'=>1)));
    $wp_customize->add_control('ssc_body_font', array('type'=>'select','label'=>__('Body Font','stock-scanner'),'section'=>'ssc_branding','choices'=>array('system'=>'System UI','inter'=>'Inter','poppins'=>'Poppins','georgia'=>'Georgia')));
    $wp_customize->add_control('ssc_heading_font', array('type'=>'select','label'=>__('Heading Font','stock-scanner'),'section'=>'ssc_branding','choices'=>array('playfair'=>'Playfair Display','poppins'=>'Poppins','georgia'=>'Georgia','system'=>'System UI')));
}
add_action('customize_register', 'stock_scanner_customize_register');

function stock_scanner_customizer_css() {
    $start = get_theme_mod('ssc_primary_start', '#667eea');
    $end = get_theme_mod('ssc_primary_end', '#764ba2');
    $accent = get_theme_mod('ssc_accent', '#f39c12');
    $radius = intval(get_theme_mod('ssc_radius', 12));
    $body_font = get_theme_mod('ssc_body_font', 'system');
    $heading_font = get_theme_mod('ssc_heading_font', 'playfair');
    $fonts = array(
        'system' => "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        'inter' => "'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        'poppins' => "'Poppins', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        'georgia' => "'Georgia', 'Times New Roman', serif",
        'playfair' => "'Playfair Display', 'Georgia', serif",
    );
    $body_stack = isset($fonts[$body_font]) ? $fonts[$body_font] : $fonts['system'];
    $heading_stack = isset($fonts[$heading_font]) ? $fonts[$heading_font] : $fonts['playfair'];
    ?>
    <style id="stock-scanner-customizer-vars">
      :root{
        --primary-gradient: linear-gradient(135deg, <?php echo esc_html($start); ?> 0%, <?php echo esc_html($end); ?> 100%);
        --accent-gold: <?php echo esc_html($accent); ?>;
        --radius-xl: <?php echo $radius; ?>px;
        --font-primary: <?php echo esc_html($body_stack); ?>;
        --font-heading: <?php echo esc_html($heading_stack); ?>;
      }
      .btn-gold{ background: linear-gradient(135deg, var(--accent-gold) 0%, #e67e22 100%); }
    </style>
    <?php
}
add_action('wp_head','stock_scanner_customizer_css', 20);

/* ---------------- Accessibility: Skiplink target helper ---------------- */
function stock_scanner_main_id_filter($content){ return $content; }
// No filter needed, templates include id="main-content".

/* ---------------- Keep existing Backend Offline template (backend-offline.php) ---------------- */
// File exists separately.

?>