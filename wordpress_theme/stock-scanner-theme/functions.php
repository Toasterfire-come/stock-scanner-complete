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
    wp_enqueue_style('stock-scanner-style', get_stylesheet_uri(), array(), '1.0.0');
    
    // Enqueue Chart.js for stock charts
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), '3.9.1', true);
    
    // Enqueue theme JavaScript
    wp_enqueue_script('stock-scanner-js', get_template_directory_uri() . '/js/theme.js', array('jquery'), '1.0.0', true);
    
    // Localize script for AJAX
    wp_localize_script('stock-scanner-js', 'stock_scanner_theme', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('stock_scanner_theme_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'stock_scanner_scripts');

/**
 * Fallback menu for when no menu is assigned
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . home_url('/stock-dashboard/') . '">Dashboard</a></li>';
    echo '<li><a href="' . home_url('/stock-watchlist/') . '">Watchlist</a></li>';
    echo '<li><a href="' . home_url('/stock-market-news/') . '">Market News</a></li>';
    echo '<li><a href="' . home_url('/stock-alerts/') . '">Alerts</a></li>';
    echo '<li><a href="' . home_url('/membership-plans/') . '">Pricing</a></li>';
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
            3 => 'membership-professional'
        );
        
        if (isset($level_classes[$level_id])) {
            $classes[] = $level_classes[$level_id];
        }
    }
    
    return $classes;
}
add_filter('body_class', 'stock_scanner_body_classes');

/**
 * Customize login page
 */
function stock_scanner_login_styles() {
    ?>
    <style type="text/css">
        .login h1 a {
            background-image: none;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 100%;
            height: 65px;
            font-size: 24px;
            font-weight: bold;
            line-height: 65px;
            text-decoration: none;
            text-indent: 0;
            overflow: hidden;
        }
        
        .login h1 a::before {
            content: "📈 Stock Scanner";
            display: block;
            color: #667eea;
        }
        
        .login form {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }
        
        .login form .input {
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .login form .input:focus {
            background: white;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }
        
        .login form .button-primary {
            background: #f39c12;
            border: none;
            border-radius: 5px;
            box-shadow: none;
            text-shadow: none;
            font-weight: 600;
        }
        
        .login form .button-primary:hover {
            background: #e67e22;
        }
    </style>
    <?php
}
add_action('login_enqueue_scripts', 'stock_scanner_login_styles');

/**
 * Change login logo URL
 */
function stock_scanner_login_logo_url() {
    return home_url();
}
add_filter('login_headerurl', 'stock_scanner_login_logo_url');

/**
 * Change login logo title
 */
function stock_scanner_login_logo_url_title() {
    return get_bloginfo('name') . ' - Stock Scanner';
}
add_filter('login_headertitle', 'stock_scanner_login_logo_url_title');

/**
 * Add custom dashboard widget for stock data
 */
function stock_scanner_dashboard_widget() {
    wp_add_dashboard_widget(
        'stock_scanner_widget',
        '📈 Stock Scanner Quick View',
        'stock_scanner_dashboard_widget_content'
    );
}
add_action('wp_dashboard_setup', 'stock_scanner_dashboard_widget');

/**
 * Dashboard widget content
 */
function stock_scanner_dashboard_widget_content() {
    ?>
    <div class="stock-scanner-dashboard-widget">
        <p><strong>Popular Stocks Today:</strong></p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 15px 0;">
            <?php echo do_shortcode('[stock_scanner symbol="AAPL"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="TSLA"]'); ?>
            <?php echo do_shortcode('[stock_scanner symbol="NVDA"]'); ?>
        </div>
        <p>
            <a href="<?php echo home_url('/stock-dashboard/'); ?>" class="button button-primary">
                View Full Dashboard
            </a>
        </p>
    </div>
    <style>
        .stock-scanner-dashboard-widget .stock-scanner-widget {
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }
    </style>
    <?php
}

/**
 * Add admin menu for Stock Scanner theme options
 */
function stock_scanner_admin_menu() {
    add_theme_page(
        'Stock Scanner Options',
        'Stock Scanner',
        'manage_options',
        'stock-scanner-options',
        'stock_scanner_options_page'
    );
}
add_action('admin_menu', 'stock_scanner_admin_menu');

/**
 * Theme options page
 */
function stock_scanner_options_page() {
    ?>
    <div class="wrap">
        <h1>📈 Stock Scanner Theme Options</h1>
        
        <div class="card">
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><a href="<?php echo admin_url('options-general.php?page=stock-scanner-settings'); ?>">Plugin Settings</a></li>
                <li><a href="<?php echo admin_url('edit.php?post_type=page'); ?>">Manage Pages</a></li>
                <li><a href="<?php echo admin_url('nav-menus.php'); ?>">Customize Menus</a></li>
                <li><a href="<?php echo admin_url('users.php?page=pmpro-memberslist'); ?>">Member List</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📊 Stock Scanner Pages</h2>
            <p>The following pages were automatically created when you activated the Stock Scanner plugin:</p>
            <ul>
                <li><strong>Stock Dashboard</strong> - <a href="<?php echo home_url('/stock-dashboard/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Stock Watchlist</strong> - <a href="<?php echo home_url('/stock-watchlist/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Market News</strong> - <a href="<?php echo home_url('/stock-market-news/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Stock Alerts</strong> - <a href="<?php echo home_url('/stock-alerts/'); ?>" target="_blank">View Page</a></li>
                <li><strong>Membership Plans</strong> - <a href="<?php echo home_url('/membership-plans/'); ?>" target="_blank">View Page</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🎨 Theme Features</h2>
            <ul>
                <li>✅ Responsive design for all devices</li>
                <li>✅ Dark mode support</li>
                <li>✅ Real-time stock widgets</li>
                <li>✅ Membership level badges</li>
                <li>✅ Custom login page styling</li>
                <li>✅ Dashboard stock widget</li>
                <li>✅ Professional pricing tables</li>
                <li>✅ Smooth animations and transitions</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🚀 Getting Started</h2>
            <ol>
                <li>Ensure the Stock Scanner plugin is activated and configured</li>
                <li>Set up Paid Membership Pro with your membership levels</li>
                <li>Configure your API settings in Settings → Stock Scanner</li>
                <li>Customize your navigation menu in Appearance → Menus</li>
                <li>Test the stock widgets on your pages</li>
            </ol>
        </div>
    </div>
    
    <style>
        .card {
            background: white;
            border: 1px solid #ccd0d4;
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 1px 1px rgba(0,0,0,0.04);
        }
        .card h2 {
            margin-top: 0;
            color: #23282d;
        }
        .card ul, .card ol {
            margin-left: 20px;
        }
        .card li {
            margin-bottom: 8px;
        }
    </style>
    <?php
}

/**
 * Remove admin bar for non-admins on frontend
 */
function stock_scanner_remove_admin_bar() {
    if (!current_user_can('administrator') && !is_admin()) {
        show_admin_bar(false);
    }
}
add_action('after_setup_theme', 'stock_scanner_remove_admin_bar');

/**
 * Add custom CSS for membership levels
 */
function stock_scanner_membership_styles() {
    ?>
    <style type="text/css">
        /* Premium member highlights */
        .membership-premium .stock-scanner-widget {
            border-left: 4px solid #f39c12;
        }
        
        /* Professional member highlights */
        .membership-professional .stock-scanner-widget {
            border-left: 4px solid #9b59b6;
            background: linear-gradient(135deg, #fff 0%, #f4f1f8 100%);
        }
        
        /* Hide upgrade notices for premium+ members */
        .membership-premium .upgrade-notice,
        .membership-professional .upgrade-notice {
            display: none;
        }
    </style>
    <?php
}
add_action('wp_head', 'stock_scanner_membership_styles');
?>