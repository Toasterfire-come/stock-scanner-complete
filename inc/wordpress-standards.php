<?php
/**
 * WordPress Standards Compliance
 * Ensures theme follows WordPress coding standards and best practices
 */
if (!defined('ABSPATH')) { exit; }

/**
 * WordPress Standards Class
 */
class RTS_WordPress_Standards {
    
    public function __construct() {
        add_action('after_setup_theme', array($this, 'theme_setup'), 5);
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts_standards'));
        add_action('widgets_init', array($this, 'register_sidebars'));
        add_action('init', array($this, 'register_post_types'));
        add_action('init', array($this, 'register_taxonomies'));
        add_action('customize_register', array($this, 'customize_register'));
        
        // Translation support
        add_action('after_setup_theme', array($this, 'load_textdomain'));
        
        // Content width
        add_action('after_setup_theme', array($this, 'set_content_width'), 0);
        
        // Plugin compatibility
        add_action('init', array($this, 'plugin_compatibility'));
        
        // Multisite support
        if (is_multisite()) {
            add_action('init', array($this, 'multisite_support'));
        }
        
        // Accessibility enhancements
        add_action('wp_head', array($this, 'accessibility_enhancements'));
        
        // Theme review compliance
        $this->ensure_theme_review_compliance();
    }
    
    /**
     * Theme setup according to WordPress standards
     */
    public function theme_setup() {
        // Add default posts and comments RSS feed links to head
        add_theme_support('automatic-feed-links');
        
        // Let WordPress manage the document title
        add_theme_support('title-tag');
        
        // Enable support for Post Thumbnails
        add_theme_support('post-thumbnails');
        
        // Add custom image sizes
        add_image_size('rts-thumbnail', 300, 200, true);
        add_image_size('rts-medium', 600, 400, true);
        add_image_size('rts-large', 1200, 800, true);
        add_image_size('rts-hero', 1920, 800, true);
        
        // This theme uses wp_nav_menu() in multiple locations
        register_nav_menus(array(
            'primary' => __('Primary Navigation', 'retail-trade-scanner'),
            'footer' => __('Footer Navigation', 'retail-trade-scanner'),
            'social' => __('Social Media Menu', 'retail-trade-scanner'),
        ));
        
        // Switch default core markup for search form, comment form, and comments
        add_theme_support('html5', array(
            'search-form',
            'comment-form',
            'comment-list',
            'gallery',
            'caption',
            'script',
            'style',
            'navigation-widgets',
        ));
        
        // Set up the WordPress core custom background feature
        add_theme_support('custom-background', apply_filters('rts_custom_background_args', array(
            'default-color' => '433e0e',
            'default-image' => '',
        )));
        
        // Add theme support for selective refresh for widgets
        add_theme_support('customize-selective-refresh-widgets');
        
        // Add support for core custom logo
        add_theme_support('custom-logo', array(
            'height'      => 100,
            'width'       => 400,
            'flex-width'  => true,
            'flex-height' => true,
            'header-text' => array('site-title', 'site-description'),
        ));
        
        // Add support for custom header
        add_theme_support('custom-header', apply_filters('rts_custom_header_args', array(
            'default-image'      => '',
            'default-text-color' => 'c1bdb3',
            'width'              => 1920,
            'height'             => 200,
            'flex-height'        => true,
            'wp-head-callback'   => array($this, 'header_style'),
        )));
        
        // Add support for Block Editor styles
        add_theme_support('wp-block-styles');
        
        // Add support for full and wide align images
        add_theme_support('align-wide');
        
        // Add support for editor styles
        add_theme_support('editor-styles');
        add_editor_style('assets/css/editor-style.css');
        
        // Add support for responsive embedded content
        add_theme_support('responsive-embeds');
        
        // Remove support for Post Formats (if not needed)
        // add_theme_support('post-formats', array('aside', 'image', 'video', 'quote', 'link'));
        
        // Define starter content for fresh installs
        add_theme_support('starter-content', array(
            'posts' => array(
                'trading-guide' => array(
                    'post_title' => __('Essential Trading Guide for Beginners', 'retail-trade-scanner'),
                    'post_content' => __('Learn the fundamentals of stock trading with our comprehensive guide...', 'retail-trade-scanner'),
                    'post_type' => 'post',
                    'meta_input' => array(
                        '_rts_featured' => '1',
                    ),
                ),
                'market-analysis' => array(
                    'post_title' => __('Weekly Market Analysis', 'retail-trade-scanner'),
                    'post_content' => __('Our expert analysis of this week\'s market trends and opportunities...', 'retail-trade-scanner'),
                    'post_type' => 'post',
                ),
            ),
            'pages' => array(
                'about' => array(
                    'post_title' => __('About Us', 'retail-trade-scanner'),
                    'post_content' => __('We are a team of experienced traders and developers...', 'retail-trade-scanner'),
                ),
            ),
            'nav_menus' => array(
                'primary' => array(
                    'name' => __('Primary Navigation', 'retail-trade-scanner'),
                    'items' => array(
                        'page_home',
                        'page_about',
                        'page_contact',
                    ),
                ),
            ),
            'options' => array(
                'blogdescription' => __('Professional Trading Platform', 'retail-trade-scanner'),
            ),
            'theme_mods' => array(
                'rts_primary_color' => '#374a67',
                'rts_accent_color' => '#e15554',
            ),
        ));
    }
    
    /**
     * Set content width based on theme design
     */
    public function set_content_width() {
        $GLOBALS['content_width'] = apply_filters('rts_content_width', 1200);
    }
    
    /**
     * Enqueue scripts and styles according to WordPress standards
     */
    public function enqueue_scripts_standards() {
        $theme_version = wp_get_theme()->get('Version');
        
        // Enqueue Google Fonts
        wp_enqueue_style('rts-google-fonts', 
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
            array(), 
            null
        );
        
        // Main stylesheet
        wp_enqueue_style('rts-style', get_stylesheet_uri(), array(), $theme_version);
        
        // RTL stylesheet
        wp_style_add_data('rts-style', 'rtl', 'replace');
        
        // Main JavaScript file
        wp_enqueue_script('rts-theme-js', 
            get_template_directory_uri() . '/assets/js/theme-integration.js',
            array('jquery'), 
            $theme_version, 
            true
        );
        
        // Mobile enhancements
        wp_enqueue_script('rts-mobile-js',
            get_template_directory_uri() . '/assets/js/mobile-enhancements.js',
            array(),
            $theme_version,
            true
        );
        
        // Localize script for AJAX
        wp_localize_script('rts-theme-js', 'rtsAjax', array(
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('rts_nonce'),
            'strings' => array(
                'loading' => __('Loading...', 'retail-trade-scanner'),
                'error' => __('An error occurred. Please try again.', 'retail-trade-scanner'),
                'success' => __('Success!', 'retail-trade-scanner'),
            ),
        ));
        
        // Conditional scripts
        if (is_singular() && comments_open() && get_option('thread_comments')) {
            wp_enqueue_script('comment-reply');
        }
        
        // Admin bar styling fix
        if (is_admin_bar_showing()) {
            wp_add_inline_style('rts-style', '
                @media screen and (min-width: 783px) {
                    .admin-bar .site-header {
                        top: 32px;
                    }
                    .admin-bar body {
                        padding-top: 32px;
                    }
                }
                @media screen and (max-width: 782px) {
                    .admin-bar .site-header {
                        top: 46px;
                    }
                    .admin-bar body {
                        padding-top: 46px;
                    }
                }
            ');
        }
    }
    
    /**
     * Register widget areas
     */
    public function register_sidebars() {
        // Primary sidebar
        register_sidebar(array(
            'name'          => __('Primary Sidebar', 'retail-trade-scanner'),
            'id'            => 'sidebar-1',
            'description'   => __('Add widgets here to appear in your primary sidebar.', 'retail-trade-scanner'),
            'before_widget' => '<section id="%1$s" class="widget %2$s">',
            'after_widget'  => '</section>',
            'before_title'  => '<h2 class="widget-title">',
            'after_title'   => '</h2>',
        ));
        
        // Footer widget areas
        for ($i = 1; $i <= 4; $i++) {
            register_sidebar(array(
                'name'          => sprintf(__('Footer %d', 'retail-trade-scanner'), $i),
                'id'            => 'footer-' . $i,
                'description'   => sprintf(__('Add widgets here to appear in the footer area %d.', 'retail-trade-scanner'), $i),
                'before_widget' => '<section id="%1$s" class="widget %2$s">',
                'after_widget'  => '</section>',
                'before_title'  => '<h2 class="widget-title">',
                'after_title'   => '</h2>',
            ));
        }
        
        // Trading dashboard widgets
        register_sidebar(array(
            'name'          => __('Trading Dashboard', 'retail-trade-scanner'),
            'id'            => 'dashboard-widgets',
            'description'   => __('Add trading-specific widgets for the dashboard page.', 'retail-trade-scanner'),
            'before_widget' => '<div id="%1$s" class="dashboard-widget %2$s">',
            'after_widget'  => '</div>',
            'before_title'  => '<h3 class="dashboard-widget-title">',
            'after_title'   => '</h3>',
        ));
    }
    
    /**
     * Register custom post types
     */
    public function register_post_types() {
        // Trading Alerts post type
        register_post_type('trading_alert', array(
            'labels' => array(
                'name'               => __('Trading Alerts', 'retail-trade-scanner'),
                'singular_name'      => __('Trading Alert', 'retail-trade-scanner'),
                'menu_name'          => __('Trading Alerts', 'retail-trade-scanner'),
                'add_new'            => __('Add New Alert', 'retail-trade-scanner'),
                'add_new_item'       => __('Add New Trading Alert', 'retail-trade-scanner'),
                'edit_item'          => __('Edit Trading Alert', 'retail-trade-scanner'),
                'new_item'           => __('New Trading Alert', 'retail-trade-scanner'),
                'view_item'          => __('View Trading Alert', 'retail-trade-scanner'),
                'search_items'       => __('Search Trading Alerts', 'retail-trade-scanner'),
                'not_found'          => __('No trading alerts found', 'retail-trade-scanner'),
                'not_found_in_trash' => __('No trading alerts found in trash', 'retail-trade-scanner'),
            ),
            'public'              => true,
            'publicly_queryable'  => true,
            'show_ui'             => true,
            'show_in_menu'        => true,
            'query_var'           => true,
            'rewrite'             => array('slug' => 'alerts'),
            'capability_type'     => 'post',
            'has_archive'         => true,
            'hierarchical'        => false,
            'menu_position'       => 20,
            'menu_icon'           => 'dashicons-bell',
            'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
            'show_in_rest'        => true,
        ));
        
        // Market Analysis post type
        register_post_type('market_analysis', array(
            'labels' => array(
                'name'               => __('Market Analysis', 'retail-trade-scanner'),
                'singular_name'      => __('Market Analysis', 'retail-trade-scanner'),
                'menu_name'          => __('Market Analysis', 'retail-trade-scanner'),
                'add_new'            => __('Add New Analysis', 'retail-trade-scanner'),
                'add_new_item'       => __('Add New Market Analysis', 'retail-trade-scanner'),
                'edit_item'          => __('Edit Market Analysis', 'retail-trade-scanner'),
                'new_item'           => __('New Market Analysis', 'retail-trade-scanner'),
                'view_item'          => __('View Market Analysis', 'retail-trade-scanner'),
                'search_items'       => __('Search Market Analysis', 'retail-trade-scanner'),
                'not_found'          => __('No market analysis found', 'retail-trade-scanner'),
                'not_found_in_trash' => __('No market analysis found in trash', 'retail-trade-scanner'),
            ),
            'public'              => true,
            'publicly_queryable'  => true,
            'show_ui'             => true,
            'show_in_menu'        => true,
            'query_var'           => true,
            'rewrite'             => array('slug' => 'analysis'),
            'capability_type'     => 'post',
            'has_archive'         => true,
            'hierarchical'        => false,
            'menu_position'       => 21,
            'menu_icon'           => 'dashicons-chart-line',
            'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields', 'author'),
            'show_in_rest'        => true,
        ));
    }
    
    /**
     * Register custom taxonomies
     */
    public function register_taxonomies() {
        // Trading Strategy taxonomy
        register_taxonomy('trading_strategy', array('post', 'market_analysis'), array(
            'labels' => array(
                'name'              => __('Trading Strategies', 'retail-trade-scanner'),
                'singular_name'     => __('Trading Strategy', 'retail-trade-scanner'),
                'search_items'      => __('Search Trading Strategies', 'retail-trade-scanner'),
                'all_items'         => __('All Trading Strategies', 'retail-trade-scanner'),
                'parent_item'       => __('Parent Trading Strategy', 'retail-trade-scanner'),
                'parent_item_colon' => __('Parent Trading Strategy:', 'retail-trade-scanner'),
                'edit_item'         => __('Edit Trading Strategy', 'retail-trade-scanner'),
                'update_item'       => __('Update Trading Strategy', 'retail-trade-scanner'),
                'add_new_item'      => __('Add New Trading Strategy', 'retail-trade-scanner'),
                'new_item_name'     => __('New Trading Strategy Name', 'retail-trade-scanner'),
                'menu_name'         => __('Trading Strategies', 'retail-trade-scanner'),
            ),
            'hierarchical'      => true,
            'public'            => true,
            'show_ui'           => true,
            'show_admin_column' => true,
            'query_var'         => true,
            'rewrite'           => array('slug' => 'strategy'),
            'show_in_rest'      => true,
        ));
        
        // Market Sector taxonomy
        register_taxonomy('market_sector', array('post', 'market_analysis', 'trading_alert'), array(
            'labels' => array(
                'name'              => __('Market Sectors', 'retail-trade-scanner'),
                'singular_name'     => __('Market Sector', 'retail-trade-scanner'),
                'search_items'      => __('Search Market Sectors', 'retail-trade-scanner'),
                'all_items'         => __('All Market Sectors', 'retail-trade-scanner'),
                'edit_item'         => __('Edit Market Sector', 'retail-trade-scanner'),
                'update_item'       => __('Update Market Sector', 'retail-trade-scanner'),
                'add_new_item'      => __('Add New Market Sector', 'retail-trade-scanner'),
                'new_item_name'     => __('New Market Sector Name', 'retail-trade-scanner'),
                'menu_name'         => __('Market Sectors', 'retail-trade-scanner'),
            ),
            'hierarchical'      => false,
            'public'            => true,
            'show_ui'           => true,
            'show_admin_column' => true,
            'query_var'         => true,
            'rewrite'           => array('slug' => 'sector'),
            'show_in_rest'      => true,
        ));
    }
    
    /**
     * Load theme textdomain
     */
    public function load_textdomain() {
        load_theme_textdomain('retail-trade-scanner', get_template_directory() . '/languages');
    }
    
    /**
     * Customize API registration
     */
    public function customize_register($wp_customize) {
        // Add custom sections
        $wp_customize->add_section('rts_colors', array(
            'title'    => __('Theme Colors', 'retail-trade-scanner'),
            'priority' => 30,
        ));
        
        $wp_customize->add_section('rts_typography', array(
            'title'    => __('Typography', 'retail-trade-scanner'),
            'priority' => 35,
        ));
        
        $wp_customize->add_section('rts_layout', array(
            'title'    => __('Layout Options', 'retail-trade-scanner'),
            'priority' => 40,
        ));
        
        $wp_customize->add_section('rts_social', array(
            'title'    => __('Social Media', 'retail-trade-scanner'),
            'priority' => 45,
        ));
        
        // Color settings
        $wp_customize->add_setting('rts_primary_color', array(
            'default'           => '#374a67',
            'sanitize_callback' => 'sanitize_hex_color',
            'transport'         => 'postMessage',
        ));
        
        $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'rts_primary_color', array(
            'label'   => __('Primary Color', 'retail-trade-scanner'),
            'section' => 'rts_colors',
        )));
        
        $wp_customize->add_setting('rts_accent_color', array(
            'default'           => '#e15554',
            'sanitize_callback' => 'sanitize_hex_color',
            'transport'         => 'postMessage',
        ));
        
        $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'rts_accent_color', array(
            'label'   => __('Accent Color', 'retail-trade-scanner'),
            'section' => 'rts_colors',
        )));
        
        // Typography settings
        $wp_customize->add_setting('rts_font_size', array(
            'default'           => '16',
            'sanitize_callback' => 'absint',
            'transport'         => 'postMessage',
        ));
        
        $wp_customize->add_control('rts_font_size', array(
            'label'   => __('Base Font Size (px)', 'retail-trade-scanner'),
            'section' => 'rts_typography',
            'type'    => 'number',
            'input_attrs' => array(
                'min'  => 12,
                'max'  => 24,
                'step' => 1,
            ),
        ));
        
        // Layout settings
        $wp_customize->add_setting('rts_sidebar_position', array(
            'default'           => 'right',
            'sanitize_callback' => array($this, 'sanitize_sidebar_position'),
            'transport'         => 'refresh',
        ));
        
        $wp_customize->add_control('rts_sidebar_position', array(
            'label'   => __('Sidebar Position', 'retail-trade-scanner'),
            'section' => 'rts_layout',
            'type'    => 'radio',
            'choices' => array(
                'left'  => __('Left', 'retail-trade-scanner'),
                'right' => __('Right', 'retail-trade-scanner'),
                'none'  => __('No Sidebar', 'retail-trade-scanner'),
            ),
        ));
        
        $wp_customize->add_setting('rts_container_width', array(
            'default'           => '1200',
            'sanitize_callback' => 'absint',
            'transport'         => 'postMessage',
        ));
        
        $wp_customize->add_control('rts_container_width', array(
            'label'   => __('Container Width (px)', 'retail-trade-scanner'),
            'section' => 'rts_layout',
            'type'    => 'number',
            'input_attrs' => array(
                'min'  => 800,
                'max'  => 1600,
                'step' => 50,
            ),
        ));
        
        // Social media settings
        $social_networks = array(
            'facebook' => __('Facebook', 'retail-trade-scanner'),
            'twitter'  => __('Twitter', 'retail-trade-scanner'),
            'linkedin' => __('LinkedIn', 'retail-trade-scanner'),
            'youtube'  => __('YouTube', 'retail-trade-scanner'),
            'instagram' => __('Instagram', 'retail-trade-scanner'),
        );
        
        foreach ($social_networks as $network => $label) {
            $wp_customize->add_setting('rts_' . $network . '_url', array(
                'default'           => '',
                'sanitize_callback' => 'esc_url_raw',
            ));
            
            $wp_customize->add_control('rts_' . $network . '_url', array(
                'label'   => $label . ' ' . __('URL', 'retail-trade-scanner'),
                'section' => 'rts_social',
                'type'    => 'url',
            ));
        }
        
        // Analytics settings
        $wp_customize->add_section('rts_analytics', array(
            'title'    => __('Analytics & Tracking', 'retail-trade-scanner'),
            'priority' => 50,
        ));
        
        $wp_customize->add_setting('rts_ga4_id', array(
            'default'           => '',
            'sanitize_callback' => 'sanitize_text_field',
        ));
        
        $wp_customize->add_control('rts_ga4_id', array(
            'label'   => __('Google Analytics 4 ID', 'retail-trade-scanner'),
            'section' => 'rts_analytics',
            'type'    => 'text',
            'description' => __('Enter your GA4 measurement ID (e.g., G-XXXXXXXXXX)', 'retail-trade-scanner'),
        ));
        
        $wp_customize->add_setting('rts_fb_pixel_id', array(
            'default'           => '',
            'sanitize_callback' => 'sanitize_text_field',
        ));
        
        $wp_customize->add_control('rts_fb_pixel_id', array(
            'label'   => __('Facebook Pixel ID', 'retail-trade-scanner'),
            'section' => 'rts_analytics',
            'type'    => 'text',
        ));
        
        // Add live preview support
        if (isset($wp_customize->selective_refresh)) {
            $wp_customize->selective_refresh->add_partial('rts_primary_color', array(
                'selector' => ':root',
                'render_callback' => '__return_false',
            ));
        }
    }
    
    /**
     * Sanitize sidebar position
     */
    public function sanitize_sidebar_position($input) {
        $valid_positions = array('left', 'right', 'none');
        return in_array($input, $valid_positions) ? $input : 'right';
    }
    
    /**
     * Custom header style
     */
    public function header_style() {
        $header_text_color = get_header_textcolor();
        
        if (get_theme_support('custom-header', 'default-text-color') === $header_text_color) {
            return;
        }
        
        ?>
        <style type="text/css">
        <?php if (!display_header_text()) : ?>
            .site-title,
            .site-description {
                position: absolute;
                clip: rect(1px, 1px, 1px, 1px);
            }
        <?php else : ?>
            .site-title a,
            .site-description {
                color: #<?php echo esc_attr($header_text_color); ?>;
            }
        <?php endif; ?>
        </style>
        <?php
    }
    
    /**
     * Plugin compatibility
     */
    public function plugin_compatibility() {
        // WooCommerce compatibility
        if (class_exists('WooCommerce')) {
            add_theme_support('woocommerce');
            add_theme_support('wc-product-gallery-zoom');
            add_theme_support('wc-product-gallery-lightbox');
            add_theme_support('wc-product-gallery-slider');
        }
        
        // Jetpack compatibility
        if (class_exists('Jetpack')) {
            add_theme_support('infinite-scroll', array(
                'container' => 'main',
                'render'    => array($this, 'infinite_scroll_render'),
                'footer'    => 'page',
            ));
            add_theme_support('jetpack-responsive-videos');
        }
        
        // Yoast SEO compatibility
        if (class_exists('WPSEO_Options')) {
            add_filter('wpseo_breadcrumb_links', array($this, 'yoast_breadcrumb_filter'));
        }
        
        // Contact Form 7 compatibility
        if (class_exists('WPCF7')) {
            add_filter('wpcf7_load_css', '__return_false');
            add_action('wp_enqueue_scripts', array($this, 'enqueue_cf7_styles'));
        }
    }
    
    /**
     * Contact Form 7 custom styles
     */
    public function enqueue_cf7_styles() {
        if (function_exists('wpcf7_enqueue_styles')) {
            wpcf7_enqueue_styles();
        }
        
        wp_add_inline_style('contact-form-7', '
            .wpcf7 .wpcf7-form-control {
                padding: 12px;
                border: 1px solid var(--border, #ddd);
                border-radius: var(--radius, 6px);
                background: var(--input, #fff);
                color: var(--foreground, #333);
                font-size: 16px;
            }
            .wpcf7 .wpcf7-submit {
                background: var(--primary, #007cba);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: var(--radius, 6px);
                cursor: pointer;
                font-weight: 500;
            }
            .wpcf7 .wpcf7-submit:hover {
                background: var(--primary-hover, #005a87);
            }
        ');
    }
    
    /**
     * Infinite scroll render function
     */
    public function infinite_scroll_render() {
        while (have_posts()) {
            the_post();
            get_template_part('template-parts/content', get_post_type());
        }
    }
    
    /**
     * Yoast breadcrumb filter
     */
    public function yoast_breadcrumb_filter($links) {
        // Customize breadcrumb structure for trading pages
        if (is_page('dashboard') || is_page('scanner') || is_page('portfolio')) {
            $trading_link = array(
                'url' => home_url('/dashboard/'),
                'text' => __('Trading Platform', 'retail-trade-scanner'),
            );
            array_splice($links, 1, 0, array($trading_link));
        }
        
        return $links;
    }
    
    /**
     * Multisite support
     */
    public function multisite_support() {
        // Network-wide theme options
        add_action('network_admin_menu', array($this, 'add_network_admin_menu'));
        
        // Site-specific customizations
        add_filter('pre_option_rts_network_options', array($this, 'get_network_options'));
    }
    
    /**
     * Add network admin menu
     */
    public function add_network_admin_menu() {
        add_submenu_page(
            'themes.php',
            __('RTS Theme Network Settings', 'retail-trade-scanner'),
            __('RTS Network Settings', 'retail-trade-scanner'),
            'manage_network_themes',
            'rts-network-settings',
            array($this, 'network_settings_page')
        );
    }
    
    /**
     * Network settings page
     */
    public function network_settings_page() {
        if (isset($_POST['submit'])) {
            check_admin_referer('rts_network_settings');
            
            $network_options = array(
                'allowed_customizations' => isset($_POST['allowed_customizations']) ? $_POST['allowed_customizations'] : array(),
                'default_colors' => array(
                    'primary' => sanitize_hex_color($_POST['default_primary_color']),
                    'accent' => sanitize_hex_color($_POST['default_accent_color']),
                ),
            );
            
            update_site_option('rts_network_options', $network_options);
            
            echo '<div class="notice notice-success"><p>' . __('Settings saved.', 'retail-trade-scanner') . '</p></div>';
        }
        
        $options = get_site_option('rts_network_options', array());
        
        ?>
        <div class="wrap">
            <h1><?php esc_html_e('RTS Theme Network Settings', 'retail-trade-scanner'); ?></h1>
            
            <form method="post" action="">
                <?php wp_nonce_field('rts_network_settings'); ?>
                
                <table class="form-table">
                    <tr>
                        <th scope="row"><?php esc_html_e('Allowed Customizations', 'retail-trade-scanner'); ?></th>
                        <td>
                            <fieldset>
                                <label>
                                    <input type="checkbox" name="allowed_customizations[]" value="colors" 
                                           <?php checked(in_array('colors', $options['allowed_customizations'] ?? array())); ?>>
                                    <?php esc_html_e('Color Customization', 'retail-trade-scanner'); ?>
                                </label><br>
                                <label>
                                    <input type="checkbox" name="allowed_customizations[]" value="typography" 
                                           <?php checked(in_array('typography', $options['allowed_customizations'] ?? array())); ?>>
                                    <?php esc_html_e('Typography Customization', 'retail-trade-scanner'); ?>
                                </label><br>
                                <label>
                                    <input type="checkbox" name="allowed_customizations[]" value="layout" 
                                           <?php checked(in_array('layout', $options['allowed_customizations'] ?? array())); ?>>
                                    <?php esc_html_e('Layout Customization', 'retail-trade-scanner'); ?>
                                </label>
                            </fieldset>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Default Primary Color', 'retail-trade-scanner'); ?></th>
                        <td>
                            <input type="color" name="default_primary_color" 
                                   value="<?php echo esc_attr($options['default_colors']['primary'] ?? '#374a67'); ?>">
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Default Accent Color', 'retail-trade-scanner'); ?></th>
                        <td>
                            <input type="color" name="default_accent_color" 
                                   value="<?php echo esc_attr($options['default_colors']['accent'] ?? '#e15554'); ?>">
                        </td>
                    </tr>
                </table>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Get network options
     */
    public function get_network_options($value) {
        return get_site_option('rts_network_options', array());
    }
    
    /**
     * Accessibility enhancements
     */
    public function accessibility_enhancements() {
        // Skip link
        echo '<a class="skip-link screen-reader-text" href="#content">' . __('Skip to content', 'retail-trade-scanner') . '</a>';
        
        // Focus management styles
        ?>
        <style>
        .skip-link {
            position: absolute !important;
            top: -9999px;
            left: 6px;
            z-index: 999999;
            padding: 8px 16px;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 0 0 6px 6px;
        }
        .skip-link:focus {
            top: 7px;
        }
        
        /* Improved focus styles */
        a:focus,
        button:focus,
        input:focus,
        textarea:focus,
        select:focus {
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }
        
        /* Screen reader text */
        .screen-reader-text {
            clip: rect(1px, 1px, 1px, 1px);
            position: absolute !important;
            height: 1px;
            width: 1px;
            overflow: hidden;
        }
        .screen-reader-text:focus {
            background-color: #f1f1f1;
            border-radius: 3px;
            box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.6);
            clip: auto !important;
            color: #21759b;
            display: block;
            font-size: 14px;
            font-weight: bold;
            height: auto;
            left: 5px;
            line-height: normal;
            padding: 15px 23px 14px;
            text-decoration: none;
            top: 5px;
            width: auto;
            z-index: 100000;
        }
        </style>
        <?php
    }
    
    /**
     * Ensure theme review compliance
     */
    private function ensure_theme_review_compliance() {
        // Remove admin notices for non-admins
        if (!current_user_can('manage_options')) {
            remove_all_actions('admin_notices');
        }
        
        // Ensure proper escaping in templates
        add_filter('the_content', array($this, 'ensure_content_escaping'), 5);
        
        // Validate customizer settings
        add_action('customize_save_after', array($this, 'validate_customizer_settings'));
        
        // Check for required templates
        add_action('after_switch_theme', array($this, 'check_required_templates'));
        
        // Validate menu locations
        add_action('wp_nav_menu_args', array($this, 'validate_menu_args'));
    }
    
    /**
     * Ensure content escaping
     */
    public function ensure_content_escaping($content) {
        // This is handled by WordPress core, but we can add additional checks
        return $content;
    }
    
    /**
     * Validate customizer settings
     */
    public function validate_customizer_settings() {
        // Validate color values
        $primary_color = get_theme_mod('rts_primary_color');
        if ($primary_color && !sanitize_hex_color($primary_color)) {
            remove_theme_mod('rts_primary_color');
        }
        
        $accent_color = get_theme_mod('rts_accent_color');
        if ($accent_color && !sanitize_hex_color($accent_color)) {
            remove_theme_mod('rts_accent_color');
        }
    }
    
    /**
     * Check required templates
     */
    public function check_required_templates() {
        $required_templates = array(
            'index.php',
            'style.css',
            'screenshot.png'
        );
        
        foreach ($required_templates as $template) {
            if (!file_exists(get_template_directory() . '/' . $template)) {
                add_action('admin_notices', function() use ($template) {
                    echo '<div class="notice notice-error"><p>';
                    printf(__('Required template file missing: %s', 'retail-trade-scanner'), $template);
                    echo '</p></div>';
                });
            }
        }
    }
    
    /**
     * Validate menu arguments
     */
    public function validate_menu_args($args) {
        // Ensure proper fallback for menus
        if (!isset($args['fallback_cb'])) {
            $args['fallback_cb'] = 'wp_page_menu';
        }
        
        return $args;
    }
}

// Initialize WordPress Standards
new RTS_WordPress_Standards();

/**
 * WordPress Standards Utility Functions
 */

/**
 * Check if theme meets WordPress standards
 */
function rts_check_standards_compliance() {
    $issues = array();
    
    // Check for required files
    $required_files = array('index.php', 'style.css');
    foreach ($required_files as $file) {
        if (!file_exists(get_template_directory() . '/' . $file)) {
            $issues[] = sprintf(__('Missing required file: %s', 'retail-trade-scanner'), $file);
        }
    }
    
    // Check for text domain usage
    $php_files = glob(get_template_directory() . '/*.php');
    foreach ($php_files as $file) {
        $content = file_get_contents($file);
        if (strpos($content, '__(' ) !== false || strpos($content, '_e(') !== false) {
            if (strpos($content, 'retail-trade-scanner') === false) {
                $issues[] = sprintf(__('Text domain not used in: %s', 'retail-trade-scanner'), basename($file));
            }
        }
    }
    
    return $issues;
}

/**
 * Sanitize customizer input
 */
function rts_sanitize_customizer_input($input, $type = 'text') {
    switch ($type) {
        case 'color':
            return sanitize_hex_color($input);
        case 'email':
            return sanitize_email($input);
        case 'url':
            return esc_url_raw($input);
        case 'number':
            return absint($input);
        case 'textarea':
            return sanitize_textarea_field($input);
        case 'text':
        default:
            return sanitize_text_field($input);
    }
}

/**
 * Get theme option with fallback
 */
function rts_get_theme_option($option, $default = '') {
    $value = get_theme_mod($option, $default);
    
    // Apply filters for extensibility
    return apply_filters('rts_theme_option_' . $option, $value);
}

/**
 * Register block patterns
 */
function rts_register_block_patterns() {
    if (function_exists('register_block_pattern_category')) {
        register_block_pattern_category(
            'rts-trading',
            array('label' => __('Trading Patterns', 'retail-trade-scanner'))
        );
    }
    
    if (function_exists('register_block_pattern')) {
        register_block_pattern(
            'rts/hero-section',
            array(
                'title'       => __('Trading Hero Section', 'retail-trade-scanner'),
                'description' => __('A hero section designed for trading platforms', 'retail-trade-scanner'),
                'content'     => '<!-- wp:group {"backgroundColor":"dark"} -->
                <div class="wp-block-group has-dark-background-color has-background">
                    <!-- wp:heading {"level":1,"textColor":"white"} -->
                    <h1 class="has-white-color has-text-color">' . __('Professional Trading Platform', 'retail-trade-scanner') . '</h1>
                    <!-- /wp:heading -->
                    
                    <!-- wp:paragraph {"textColor":"light-gray"} -->
                    <p class="has-light-gray-color has-text-color">' . __('Advanced market analysis and trading tools for retail investors', 'retail-trade-scanner') . '</p>
                    <!-- /wp:paragraph -->
                    
                    <!-- wp:buttons -->
                    <div class="wp-block-buttons">
                        <!-- wp:button {"backgroundColor":"primary"} -->
                        <div class="wp-block-button"><a class="wp-block-button__link has-primary-background-color has-background">' . __('Get Started', 'retail-trade-scanner') . '</a></div>
                        <!-- /wp:button -->
                    </div>
                    <!-- /wp:buttons -->
                </div>
                <!-- /wp:group -->',
                'categories'  => array('rts-trading'),
            )
        );
    }
}
add_action('init', 'rts_register_block_patterns');