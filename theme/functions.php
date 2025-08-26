<?php
/**
 * Stock Scanner Theme Functions (with admin-configurable idle policy + session policy notes)
 */
if (!defined('ABSPATH')) { exit; }

/* ---------------- Include template parts ---------------- */
require_once get_template_directory() . '/template-parts/nav-walker.php';

/* ---------------- Theme setup ---------------- */
function stock_scanner_theme_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', [ 'height' => 80, 'width'  => 240, 'flex-height' => true, 'flex-width' => true ]);
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('customize-selective-refresh-widgets');
    register_nav_menus(array('primary' => __('Primary Menu', 'finmarkets')));
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
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '2.0.1');
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '2.0.1', true);
    if (function_exists('wp_script_add_data')) { wp_script_add_data('stock-scanner-js', 'defer', true); wp_script_add_data('chart-js', 'defer', true); }

    // Idle settings
    $idle_enabled = (int)get_option('ssc_idle_enabled', 1);
    $idle_hours   = (int)get_option('ssc_idle_hours', 12);
    $idle_hours   = max(1, $idle_hours);

    // Backend test mode (no backend) if plugin URL missing
    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    $no_backend = empty($api_base);

    wp_localize_script('stock_scanner-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce'),
        'logged_in' => is_user_logged_in(),
        'logout_url' => wp_logout_url(home_url('/')),
        'user_id' => is_user_logged_in() ? get_current_user_id() : 0,
        'idle_enabled' => (bool)$idle_enabled,
        'idle_limit_ms' => $idle_hours * 60 * 60 * 1000,
        'warn_threshold_ms' => 2 * 60 * 1000,
        'no_backend' => $no_backend,
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

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

/* ---------------- Login page styles are now in style.css ---------------- */
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

/* ---------------- Admin menu quick links + save options ---------------- */
function stock_scanner_admin_menu() { add_theme_page('Stock Scanner Options','Stock Scanner','manage_options','stock-scanner-options','stock_scanner_options_page'); }
add_action('admin_menu', 'stock_scanner_admin_menu');

function stock_scanner_save_theme_options() {
    if (!current_user_can('manage_options')) wp_die('Forbidden');
    check_admin_referer('stock_scanner_save_theme');
    $enabled = isset($_POST['ssc_idle_enabled']) ? 1 : 0;
    $hours   = isset($_POST['ssc_idle_hours']) ? (int)$_POST['ssc_idle_hours'] : 12;
    $hours   = max(1, $hours);
    update_option('ssc_idle_enabled', $enabled);
    update_option('ssc_idle_hours', $hours);
    $redirect = add_query_arg('updated', '1', wp_get_referer() ?: admin_url('themes.php?page=stock-scanner-options'));
    wp_safe_redirect($redirect); exit;
}
add_action('admin_post_stock_scanner_save_theme', 'stock_scanner_save_theme_options');

function stock_scanner_options_page() {
    $enabled = (int)get_option('ssc_idle_enabled', 1);
    $hours   = (int)get_option('ssc_idle_hours', 12);
    ?>
    <div class="wrap">
        <h1>📈 Stock Scanner Theme Options</h1>
        <?php if (!empty($_GET['updated'])): ?><div class="notice notice-success is-dismissible"><p>Settings saved.</p></div><?php endif; ?>
        <div class="card"><h2>🔗 Quick Links</h2><ul>
            <li><a href="<?php echo esc_url(admin_url('options-general.php?page=stock-scanner-settings')); ?>">Plugin Settings</a></li>
            <li><a href="<?php echo esc_url(admin_url('edit.php?post_type=page')); ?>">Manage Pages</a></li>
            <li><a href="<?php echo esc_url(admin_url('nav-menus.php')); ?>">Customize Menus</a></li>
            <li><a href="<?php echo esc_url(admin_url('users.php?page=pmpro-memberslist')); ?>">Member List</a></li>
        </ul></div>

        <div class="card">
            <h2>🔒 Session Policy</h2>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('stock_scanner_save_theme'); ?>
                <input type="hidden" name="action" value="stock_scanner_save_theme" />
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row"><label for="ssc_idle_enabled">Enable idle auto-logout</label></th>
                        <td>
                            <label><input type="checkbox" id="ssc_idle_enabled" name="ssc_idle_enabled" value="1" <?php checked($enabled, 1); ?> /> After inactivity, sign out users automatically</label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="ssc_idle_hours">Idle timeout (hours)</label></th>
                        <td>
                            <input type="number" id="ssc_idle_hours" name="ssc_idle_hours" min="1" max="72" step="1" value="<?php echo esc_attr($hours); ?>" />
                            <p class="description">Default: 12 hours. The browser-side timer logs the user out after this idle period.</p>
                        </td>
                    </tr>
                </table>
                <p><button type="submit" class="button button-primary">Save Changes</button></p>
            </form>
        </div>

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

/* ---------------- Membership & plan badge styles are now in style.css ---------------- */
// Styles moved to main stylesheet for better performance and maintainability

/* ---------------- Keep posts out: redirect/404 post views ---------------- */
function stock_scanner_block_posts_templates() {
    if (is_admin()) return;
    if (is_home() && !is_front_page()) { wp_redirect(home_url('/'), 301); exit; }
    if (is_single() && get_post_type() === 'post') { global $wp_query; $wp_query->set_404(); status_header(404); include(get_query_template('404')); exit; }
    if (is_category() || is_tag() || is_date() || (function_exists('is_post_type_archive') && is_post_type_archive('post'))) { global $wp_query; $wp_query->set_404(); status_header(404); include(get_query_template('404')); exit; }
}
add_action('template_redirect', 'stock_scanner_block_posts_templates');

/* Force search to pages only */
function stock_scanner_filter_queries($q){ if (is_admin() || !$q->is_main_query()) return; if ($q->is_search()) { $q->set('post_type', array('page')); } }
add_action('pre_get_posts','stock_scanner_filter_queries');

/* ---------------- AJAX: plan badge via backend ---------------- */
function stock_scanner_get_current_plan_ajax() {
    if (!is_user_logged_in()) { wp_send_json_error(array('message' => 'Unauthenticated'), 401); }
    check_ajax_referer('stock_scanner_theme_nonce', 'nonce');
    $api_base = rtrim(get_option('stock_scanner_api_url', ''), '/');
    $secret = get_option('stock_scanner_api_secret', '');
    if (empty($api_base) || empty($secret)) { $user_id = get_current_user_id(); $plan = stock_scanner_plan_from_pmpro($user_id); wp_send_json_success(array('source'=>'pmpro','plan'=>$plan)); }
    $url = $api_base . '/billing/current-plan';
    $user_id = get_current_user_id();
    $level_id = 0; if (function_exists('pmpro_getMembershipLevelForUser')) { $level = pmpro_getMembershipLevelForUser($user_id); $level_id = $level ? intval($level->id) : 0; }
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
            switch (intval($level->id)) { case 2: $plan['name']='Premium'; $plan['slug']='premium'; $plan['premium']=true; break; case 3: $plan['name']='Professional'; $plan['slug']='professional'; $plan['premium']=true; break; case 4: $plan['name']='Gold'; $plan['slug']='gold'; $plan['premium']=true; break; default: $plan['name']='Free'; $plan['slug']='free'; $plan['premium']=false; break; }
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
function stock_scanner_admin_notices() { if (!current_user_can('manage_options')) return; $api_url = get_option('stock_scanner_api_url', ''); $api_secret = get_option('stock_scanner_api_secret', ''); if (empty($api_url) || empty($api_secret)) { $settings_link = esc_url(admin_url('options-general.php?page=stock-scanner-settings')); echo '<div class="notice notice-warning is-dismissible"><p>Stock Scanner: Please configure the API URL and Secret in <a href="' . $settings_link . '">Settings → Stock Scanner</a> to enable plan badges and health checks.</p></div>'; } }
add_action('admin_notices', 'stock_scanner_admin_notices');

/* ---------------- Ensure screenshot.png exists ---------------- */
function stock_scanner_ensure_screenshot() { $path = get_stylesheet_directory() . '/screenshot.png'; if (file_exists($path)) return; if (function_exists('imagecreatetruecolor')) { $w=1200;$h=900; $im=imagecreatetruecolor($w,$h); $bg=imagecolorallocate($im, 240, 242, 245); imagefilledrectangle($im,0,0,$w,$h,$bg); $bar=imagecolorallocate($im, 102,126,234); imagefilledrectangle($im,0,0,$w,12,$bar); $txt=imagecolorallocate($im, 51,65,85); imagestring($im, 5, 40, 40, 'Stock Scanner Theme', $txt); imagestring($im, 3, 40, 70, 'Professional WordPress theme for stock analysis', $txt); imagepng($im, $path); imagedestroy($im); return; } $b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottQAAAABJRU5ErkJggg=='; file_put_contents($path, base64_decode($b64)); }
add_action('admin_init', 'stock_scanner_ensure_screenshot');

/* ---------------- Featured pages shortcode (no posts) ---------------- */
function stock_scanner_featured_pages_shortcode($atts) { $atts = shortcode_atts(array('ids'=>'','count'=>3,'parent'=>0), $atts, 'featured_pages'); $args = array('post_type'=>'page','posts_per_page'=>max(1,intval($atts['count'])),'orderby'=>'menu_order title','order'=>'ASC'); if (!empty($atts['ids'])) { $ids = array_map('intval', explode(',', $atts['ids'])); $args['post__in'] = $ids; $args['orderby']='post__in'; } if (!empty($atts['parent'])) { $args['post_parent'] = intval($atts['parent']); } $q = new WP_Query($args); ob_start(); if ($q->have_posts()): ?>
  <div class="pricing-table" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
    <?php while($q->have_posts()): $q->the_post(); ?>
      <article <?php post_class('card'); ?> >
        <div class="card-header">
          <h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
        </div>
        <div class="card-body">
          <?php if (has_post_thumbnail()) { echo get_the_post_thumbnail(get_the_ID(),'medium_large',array('style'=>'border-radius:12px;width:100%;height:auto;margin-bottom:10px;','loading'=>'lazy','decoding'=>'async')); } ?>
          <?php the_excerpt(); ?>
        </div>
        <div class="card-footer"><a class="btn btn-primary" href="<?php the_permalink(); ?>"><span>Learn More</span></a></div>
      </article>
    <?php endwhile; wp_reset_postdata(); ?>
  </div>
<?php else: ?>
  <div class="card"><div class="card-body">No pages selected.</div></div>
<?php endif; return ob_get_clean(); }
add_shortcode('featured_pages','stock_scanner_featured_pages_shortcode');

/* ---------------- Session Policy helpers (user/profile + shortcode) ---------------- */
function stock_scanner_get_idle_settings() { $enabled = (int)get_option('ssc_idle_enabled', 1); $hours = (int)get_option('ssc_idle_hours', 12); if ($hours < 1) $hours = 12; return array($enabled, $hours); }
function stock_scanner_session_policy_text() { list($enabled, $hours) = stock_scanner_get_idle_settings(); if ($enabled) { return sprintf('For your security, you will be signed out automatically after %d hour%s of inactivity. You will receive a 2-minute warning to stay signed in.', $hours, $hours === 1 ? '' : 's'); } else { return 'Auto-logout after inactivity is currently disabled on this site.'; } }
function stock_scanner_session_policy_shortcode() { return '<p class="description">' . esc_html(stock_scanner_session_policy_text()) . '</p>'; }
add_shortcode('session_policy_note', 'stock_scanner_session_policy_shortcode');
function stock_scanner_session_policy_profile_note($user) { if (!current_user_can('read', $user->ID)) return; echo '<h2>Session Policy</h2><p>' . esc_html(stock_scanner_session_policy_text()) . '</p>'; }
add_action('show_user_profile', 'stock_scanner_session_policy_profile_note');
add_action('edit_user_profile', 'stock_scanner_session_policy_profile_note');

?>