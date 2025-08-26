<?php
/**
 * Stock Scanner Theme Functions
 * Sets up theme features and navigation
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Theme setup
 */
function stock_scanner_theme_setup() {
    // Add theme support for various features
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', [
        'height' => 80,
        'width'  => 240,
        'flex-height' => true,
        'flex-width' => true,
    ]);
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    add_theme_support('customize-selective-refresh-widgets');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'stock-scanner'),
    ));
}
add_action('after_setup_theme', 'stock_scanner_theme_setup');

/**
 * Enqueue scripts and styles
 */
function stock_scanner_scripts() {
    // Enqueue theme stylesheet
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '1.0.1');
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Enqueue theme JavaScript
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '1.0.1', true);
    
    // Localize script for AJAX
    wp_localize_script('stock-scanner-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce'),
        'logged_in' => is_user_logged_in(),
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Fallback menu for when no menu is assigned
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . home_url('/premium-plans/') . '">Premium Plans</a></li>';
    echo '<li><a href="' . home_url('/email-stock-lists/') . '">Email Lists</a></li>';
    echo '<li><a href="' . home_url('/stock-search/') . '">Stock Search</a></li>';
    echo '<li><a href="' . home_url('/popular-stock-lists/') . '">Popular Lists</a></li>';
    echo '<li><a href="' . home_url('/news-scrapper/') . '">News Scraper</a></li>';
    echo '<li><a href="' . home_url('/membership-account/') . '">My Account</a></li>';
    echo '</ul>';
}

/**
 * Add body classes for different membership levels
 */
function stock_scanner_body_classes($classes) {
    if (is_user_logged_in() && function_exists('pmpro_getMembershipLevelForUser')) {
        $level = pmpro_getMembershipLevelForUser(get_current_user_id());
        $level_id = $level ? $level->id : 0;
        
        $level_classes = array(
            0 => 'membership-free',
            1 => 'membership-free', 
            2 => 'membership-premium',
            3 => 'membership-professional',
            4 => 'membership-gold'
        );
        
        if (isset($level_classes[$level_id])) {
            $classes[] = $level_classes[$level_id];
        }
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/** Login page styles */
function stock_scanner_login_styles() {
    ?>
    <style type="text/css">
        .login h1 a { background-image: none; width: 100%; height: 65px; font-size: 24px; font-weight: bold; line-height: 65px; text-indent: 0; }
        .login h1 a::before { content: "📈 Stock Scanner"; color: #667eea; }
        .login form { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
        .login form .input { background: rgba(255,255,255,0.9); border: none; border-radius: 5px; margin-bottom: 10px; }
        .login form .button-primary { background: #f39c12; border: none; border-radius: 5px; }
    </style>
    <?php
}
add_action('login_enqueue_scripts', 'stock_scanner_login_styles');
function stock_scanner_login_logo_url() { return home_url(); }
add_filter('login_headerurl', 'stock_scanner_login_logo_url');
function stock_scanner_login_logo_url_title() { return get_bloginfo('name') . ' - Stock Scanner'; }
add_filter('login_headertitle', 'stock_scanner_login_logo_url_title');

/** Dashboard widget */
function stock_scanner_dashboard_widget() {
    wp_add_dashboard_widget('stock_scanner_widget','📈 Stock Scanner Quick View','stock_scanner_dashboard_widget_content');
}
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

/** Admin menu (theme options quick links) */
function stock_scanner_admin_menu() {
    add_theme_page('Stock Scanner Options','Stock Scanner','manage_options','stock-scanner-options','stock_scanner_options_page');
}
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

/** Remove admin bar for non-admins */
function stock_scanner_remove_admin_bar() {
    if (!current_user_can('administrator') && !is_admin()) { show_admin_bar(false); }
}
add_action('after_setup_theme', 'stock_scanner_remove_admin_bar');

/** Membership styles + plan badge */
function stock_scanner_membership_styles() {
    ?>
    <style type="text/css">
        .membership-premium .stock-scanner-widget { border-left: 4px solid #f39c12; }
        .membership-professional .stock-scanner-widget { border-left: 4px solid #9b59b6; background: linear-gradient(135deg,#fff 0%,#f4f1f8 100%);} 
        .membership-premium .upgrade-notice, .membership-professional .upgrade-notice { display:none; }
        .plan-badge { background:#eef0f2;border:2px solid #cfd6dd;padding:6px 12px;border-radius:999px;font-size:.85rem;font-weight:600;color:#334155; }
        .plan-badge.premium{border-color:#f39c12;color:#f39c12}.plan-badge.professional{border-color:#9b59b6;color:#9b59b6}.plan-badge.gold{border-color:#c9a961;color:#c9a961}.plan-badge.silver{border-color:#95a5a6;color:#95a5a6}
    </style>
    <?php
}
add_action('wp_head', 'stock_scanner_membership_styles');

/** AJAX: plan badge via backend */
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
    $code = wp_remote_retrieve_response_code($response);
    $body = wp_remote_retrieve_body($response);
    if ($code>=200 && $code<300) { $data = json_decode($body, true); if (!$data) { wp_send_json_success(array('source'=>'backend','raw'=>$body)); } wp_send_json_success(array('source'=>'backend','data'=>$data)); }
    $plan = stock_scanner_plan_from_pmpro($user_id); wp_send_json_success(array('source'=>'fallback','plan'=>$plan,'status'=>$code));
}
add_action('wp_ajax_stock_scanner_get_current_plan', 'stock_scanner_get_current_plan_ajax');

/** Map PMPro -> plan object */
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

/** AJAX: Admin-only health */
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

/** Admin notice if plugin API config missing */
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

/** Ensure screenshot.png exists (attempt GD; fallback to tiny PNG) */
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
    // 1x1 transparent png fallback
    $b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottQAAAABJRU5ErkJggg==';
    file_put_contents($path, base64_decode($b64));
}
add_action('admin_init', 'stock_scanner_ensure_screenshot');

?>