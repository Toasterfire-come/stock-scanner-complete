<?php
/**
 * Production Performance Optimizations
 * Advanced caching, minification, and performance enhancements
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Performance Class - Handles all performance optimizations
 */
class RTS_Performance {
    
    private $cache_version;
    private $is_mobile;
    
    public function __construct() {
        $this->cache_version = get_theme_mod('rts_cache_version', '1.0.0');
        $this->is_mobile = wp_is_mobile();
        
        add_action('init', array($this, 'init_performance_features'));
        add_action('wp_enqueue_scripts', array($this, 'optimize_assets'), 5);
        add_action('wp_head', array($this, 'add_performance_headers'), 1);
        add_action('wp_footer', array($this, 'add_performance_footer'), 999);
        
        // Browser caching
        add_action('send_headers', array($this, 'set_cache_headers'));
        
        // Database optimization
        add_action('wp_loaded', array($this, 'optimize_database_queries'));
        
        // Image optimization
        add_filter('wp_get_attachment_image_src', array($this, 'optimize_image_src'), 10, 4);
        add_filter('the_content', array($this, 'lazy_load_images'), 20);
        
        // Clean up WordPress head
        add_action('init', array($this, 'cleanup_wordpress_head'));
    }
    
    /**
     * Initialize performance features
     */
    public function init_performance_features() {
        // Enable output buffering for compression
        if (!ob_get_level() && !ini_get('zlib.output_compression')) {
            ob_start('ob_gzhandler');
        }
        
        // Optimize WordPress queries
        $this->optimize_wp_queries();
        
        // Initialize caching
        $this->init_caching();
        
        // Preload critical resources
        add_action('wp_head', array($this, 'preload_critical_resources'), 1);
        
        // Critical CSS optimization
        add_action('wp_head', array($this, 'inline_critical_css'), 2);
        
        // JavaScript optimization
        add_filter('script_loader_tag', array($this, 'defer_non_critical_js'), 10, 2);
    }
    
    /**
     * Optimize WordPress queries
     */
    private function optimize_wp_queries() {
        // Disable unnecessary queries
        remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10);
        remove_action('wp_head', 'wp_shortlink_wp_head', 10);
        
        // Optimize main query
        add_action('pre_get_posts', array($this, 'optimize_main_query'));
        
        // Cache expensive queries
        add_filter('posts_request', array($this, 'cache_database_queries'), 10, 2);
    }
    
    /**
     * Optimize main query
     */
    public function optimize_main_query($query) {
        if (!is_admin() && $query->is_main_query()) {
            if (is_home() || is_front_page()) {
                $query->set('posts_per_page', 6);
                $query->set('meta_query', array(
                    array(
                        'key' => '_rts_featured',
                        'value' => '1',
                        'compare' => '!='
                    )
                ));
            }
        }
    }
    
    /**
     * Cache database queries
     */
    public function cache_database_queries($request, $query) {
        if (!is_admin() && $query->is_main_query()) {
            $cache_key = 'rts_query_' . md5($request);
            $cached_result = wp_cache_get($cache_key, 'rts_queries');
            
            if ($cached_result !== false) {
                return $cached_result;
            }
            
            // Cache for 1 hour
            wp_cache_set($cache_key, $request, 'rts_queries', 3600);
        }
        
        return $request;
    }
    
    /**
     * Initialize caching system
     */
    private function init_caching() {
        // Object caching for expensive operations
        add_action('wp_ajax_rts_clear_cache', array($this, 'clear_theme_cache'));
        add_action('wp_ajax_nopriv_rts_clear_cache', array($this, 'clear_theme_cache'));
        
        // Menu caching
        add_filter('pre_wp_nav_menu', array($this, 'cache_navigation_menu'), 10, 2);
        
        // Widget caching
        add_filter('widget_display_callback', array($this, 'cache_widget_output'), 10, 3);
    }
    
    /**
     * Cache navigation menu
     */
    public function cache_navigation_menu($nav_menu, $args) {
        if (!isset($args->theme_location)) {
            return $nav_menu;
        }
        
        $cache_key = 'rts_nav_' . $args->theme_location . '_' . $this->cache_version;
        $cached_menu = wp_cache_get($cache_key, 'rts_navigation');
        
        if ($cached_menu !== false) {
            return $cached_menu;
        }
        
        // Let WordPress generate the menu normally, then cache it
        return $nav_menu;
    }
    
    /**
     * Cache widget output
     */
    public function cache_widget_output($instance, $widget, $args) {
        $cache_key = 'rts_widget_' . $widget->id . '_' . $this->cache_version;
        $cached_widget = wp_cache_get($cache_key, 'rts_widgets');
        
        if ($cached_widget !== false) {
            echo $cached_widget;
            return false; // Skip normal widget output
        }
        
        // Start output buffering
        ob_start();
        
        // Return instance to continue normal processing
        return $instance;
    }
    
    /**
     * Optimize assets loading
     */
    public function optimize_assets() {
        // Remove unnecessary default styles
        wp_dequeue_style('wp-block-library');
        wp_dequeue_style('wp-block-library-theme');
        wp_dequeue_style('classic-theme-styles');
        
        // Combine and minify CSS
        $this->combine_css_files();
        
        // Optimize JavaScript loading
        $this->optimize_javascript();
        
        // Conditional loading for mobile
        if ($this->is_mobile) {
            $this->load_mobile_optimized_assets();
        }
    }
    
    /**
     * Combine CSS files
     */
    private function combine_css_files() {
        $css_files = array(
            get_stylesheet_uri(),
            get_template_directory_uri() . '/assets/css/additional.css'
        );
        
        $combined_css = $this->get_combined_css($css_files);
        
        if ($combined_css) {
            wp_enqueue_style('rts-combined', $combined_css, array(), $this->cache_version);
        }
    }
    
    /**
     * Get combined CSS file path
     */
    private function get_combined_css($css_files) {
        $cache_key = 'rts_combined_css_' . md5(implode('|', $css_files));
        $combined_file = wp_cache_get($cache_key, 'rts_assets');
        
        if ($combined_file !== false && file_exists($combined_file)) {
            return str_replace(ABSPATH, home_url('/'), $combined_file);
        }
        
        // Generate combined CSS file
        $combined_content = '';
        foreach ($css_files as $css_file) {
            if (file_exists($css_file) || filter_var($css_file, FILTER_VALIDATE_URL)) {
                $content = file_get_contents($css_file);
                if ($content) {
                    $combined_content .= $this->minify_css($content) . "\n";
                }
            }
        }
        
        if ($combined_content) {
            $upload_dir = wp_upload_dir();
            $combined_file = $upload_dir['basedir'] . '/rts-cache/combined-' . md5($combined_content) . '.css';
            
            // Create directory if it doesn't exist
            wp_mkdir_p(dirname($combined_file));
            
            // Write combined file
            file_put_contents($combined_file, $combined_content);
            
            // Cache the file path
            wp_cache_set($cache_key, $combined_file, 'rts_assets', 86400);
            
            return str_replace(ABSPATH, home_url('/'), $combined_file);
        }
        
        return false;
    }
    
    /**
     * Minify CSS
     */
    private function minify_css($css) {
        // Remove comments
        $css = preg_replace('!/\*[^*]*\*+([^/][^*]*\*+)*/!', '', $css);
        
        // Remove whitespace
        $css = str_replace(array("\r\n", "\r", "\n", "\t", '  ', '    ', '    '), '', $css);
        
        // Remove unnecessary spaces
        $css = preg_replace('/\s*([:;{}])\s*/', '$1', $css);
        
        return trim($css);
    }
    
    /**
     * Optimize JavaScript loading
     */
    private function optimize_javascript() {
        // Defer non-critical JavaScript
        add_filter('script_loader_tag', array($this, 'defer_non_critical_js'), 10, 2);
        
        // Preload critical JavaScript
        $critical_js = array(
            'rts-theme-js',
            'rts-mobile-js'
        );
        
        foreach ($critical_js as $handle) {
            if (wp_script_is($handle, 'enqueued')) {
                $src = wp_scripts()->registered[$handle]->src;
                echo '<link rel="preload" href="' . esc_url($src) . '" as="script">';
            }
        }
    }
    
    /**
     * Defer non-critical JavaScript
     */
    public function defer_non_critical_js($tag, $handle) {
        $critical_scripts = array('jquery', 'rts-theme-js');
        
        if (!in_array($handle, $critical_scripts)) {
            return str_replace(' src', ' defer src', $tag);
        }
        
        return $tag;
    }
    
    /**
     * Load mobile-optimized assets
     */
    private function load_mobile_optimized_assets() {
        // Load smaller images for mobile
        add_filter('wp_get_attachment_image_src', array($this, 'mobile_image_optimization'), 10, 4);
        
        // Reduce JavaScript payload for mobile
        wp_dequeue_script('comment-reply');
        
        // Load critical mobile CSS inline
        $mobile_css = $this->get_critical_mobile_css();
        if ($mobile_css) {
            echo '<style id="mobile-critical-css">' . $mobile_css . '</style>';
        }
    }
    
    /**
     * Get critical mobile CSS
     */
    private function get_critical_mobile_css() {
        $cache_key = 'rts_mobile_critical_css_' . $this->cache_version;
        $cached_css = wp_cache_get($cache_key, 'rts_critical_css');
        
        if ($cached_css !== false) {
            return $cached_css;
        }
        
        $critical_css = '
            @media (max-width: 768px) {
                .sidebar { transform: translateX(-100%); }
                .site-main { padding-left: 16px; padding-right: 16px; }
                .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
                .btn { padding: 14px 20px; font-size: 16px; }
                input, textarea, select { font-size: 16px; }
            }
        ';
        
        $minified_css = $this->minify_css($critical_css);
        wp_cache_set($cache_key, $minified_css, 'rts_critical_css', 86400);
        
        return $minified_css;
    }
    
    /**
     * Add performance headers
     */
    public function add_performance_headers() {
        // DNS prefetch for external resources
        echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">' . "\n";
        echo '<link rel="dns-prefetch" href="//fonts.gstatic.com">' . "\n";
        echo '<link rel="dns-prefetch" href="//www.google-analytics.com">' . "\n";
        
        // Preconnect to critical external resources
        echo '<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>' . "\n";
        echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
        
        // Resource hints for internal resources
        echo '<link rel="prefetch" href="' . esc_url(home_url('/dashboard/')) . '">' . "\n";
        echo '<link rel="prefetch" href="' . esc_url(home_url('/scanner/')) . '">' . "\n";
    }
    
    /**
     * Preload critical resources
     */
    public function preload_critical_resources() {
        // Preload critical CSS
        $stylesheet_uri = get_stylesheet_uri();
        echo '<link rel="preload" href="' . esc_url($stylesheet_uri) . '" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . "\n";
        echo '<noscript><link rel="stylesheet" href="' . esc_url($stylesheet_uri) . '"></noscript>' . "\n";
        
        // Preload critical fonts
        echo '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . "\n";
    }
    
    /**
     * Inline critical CSS
     */
    public function inline_critical_css() {
        $cache_key = 'rts_critical_css_' . $this->cache_version;
        $critical_css = wp_cache_get($cache_key, 'rts_critical_css');
        
        if ($critical_css === false) {
            $critical_css = $this->generate_critical_css();
            wp_cache_set($cache_key, $critical_css, 'rts_critical_css', 86400);
        }
        
        if ($critical_css) {
            echo '<style id="critical-css-inline">' . $critical_css . '</style>' . "\n";
        }
    }
    
    /**
     * Generate critical CSS
     */
    private function generate_critical_css() {
        // Critical CSS for above-the-fold content
        $critical_css = '
            :root{--drab-dark-brown:#433e0e;--yinmn-blue:#374a67;--indian-red:#e15554;--silver:#c1bdb3;--davys-gray:#5f5b6b;--background:var(--drab-dark-brown);--foreground:var(--silver);--primary:var(--yinmn-blue);--accent:var(--indian-red);--border:rgba(193,189,179,0.2);--sidebar-width:280px;--sidebar-collapsed:64px;--header-height:64px}
            *{box-sizing:border-box}
            body{background:var(--background);color:var(--foreground);margin:0;font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;padding-left:var(--sidebar-collapsed);transition:padding-left 0.3s cubic-bezier(0.4,0,0.2,1)}
            .site-header{position:fixed;top:0;left:var(--sidebar-collapsed);right:0;height:var(--header-height);background:rgba(67,62,14,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:90}
            .sidebar{position:fixed;top:0;left:0;width:var(--sidebar-collapsed);height:100vh;background:linear-gradient(180deg,var(--drab-dark-brown) 0%,#3a3308 100%);border-right:1px solid var(--border);z-index:100;transition:width 0.3s cubic-bezier(0.4,0,0.2,1);overflow:hidden}
            .site-main{padding-top:calc(var(--header-height) + 32px);min-height:calc(100vh - var(--header-height));max-width:1200px;margin:0 auto;padding-left:32px;padding-right:32px}
            .card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;box-shadow:0 1px 2px rgba(0,0,0,0.15);transition:all 0.2s ease}
            .hidden{display:none!important}
            @media(max-width:768px){body,body.sidebar-expanded{padding-left:0}.site-header{left:0}.site-main{padding-left:16px;padding-right:16px}}
        ';
        
        return $this->minify_css($critical_css);
    }
    
    /**
     * Set cache headers
     */
    public function set_cache_headers() {
        if (!is_admin()) {
            $expires = 3600; // 1 hour for dynamic content
            
            if (is_singular() || is_page()) {
                $expires = 86400; // 24 hours for pages
            }
            
            header('Cache-Control: public, max-age=' . $expires);
            header('Expires: ' . gmdate('D, d M Y H:i:s', time() + $expires) . ' GMT');
            
            // ETag for better caching
            $etag = md5($_SERVER['REQUEST_URI'] . $this->cache_version);
            header('ETag: "' . $etag . '"');
            
            if (isset($_SERVER['HTTP_IF_NONE_MATCH']) && $_SERVER['HTTP_IF_NONE_MATCH'] === '"' . $etag . '"') {
                header('HTTP/1.1 304 Not Modified');
                exit;
            }
        }
    }
    
    /**
     * Optimize image sources
     */
    public function optimize_image_src($image, $attachment_id, $size, $icon) {
        if ($this->is_mobile && is_array($image)) {
            // Use smaller images for mobile
            $mobile_sizes = array(
                'large' => 'medium',
                'medium_large' => 'medium',
                'medium' => 'thumbnail'
            );
            
            if (isset($mobile_sizes[$size])) {
                return wp_get_attachment_image_src($attachment_id, $mobile_sizes[$size], $icon);
            }
        }
        
        return $image;
    }
    
    /**
     * Mobile image optimization
     */
    public function mobile_image_optimization($image, $attachment_id, $size, $icon) {
        if ($this->is_mobile && is_array($image)) {
            // Reduce image quality for mobile
            add_filter('jpeg_quality', function() { return 75; });
            add_filter('wp_editor_set_quality', function() { return 75; });
        }
        
        return $image;
    }
    
    /**
     * Lazy load images
     */
    public function lazy_load_images($content) {
        // Add loading="lazy" to images
        $content = preg_replace('/<img((?:[^>](?!loading=))*+)>/i', '<img$1 loading="lazy">', $content);
        
        return $content;
    }
    
    /**
     * Clean up WordPress head
     */
    public function cleanup_wordpress_head() {
        // Remove unnecessary head elements
        remove_action('wp_head', 'wp_generator');
        remove_action('wp_head', 'wlwmanifest_link');
        remove_action('wp_head', 'rsd_link');
        remove_action('wp_head', 'wp_shortlink_wp_head');
        remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10);
        
        // Remove emoji scripts
        remove_action('wp_head', 'print_emoji_detection_script', 7);
        remove_action('wp_print_styles', 'print_emoji_styles');
        remove_action('admin_print_scripts', 'print_emoji_detection_script');
        remove_action('admin_print_styles', 'print_emoji_styles');
        
        // Remove REST API links
        remove_action('wp_head', 'rest_output_link_wp_head');
        remove_action('wp_head', 'wp_oembed_add_discovery_links');
        
        // Disable embeds
        remove_action('wp_head', 'wp_oembed_add_discovery_links');
        remove_action('wp_head', 'wp_oembed_add_host_js');
    }
    
    /**
     * Add performance footer
     */
    public function add_performance_footer() {
        // Add service worker registration
        if (!is_admin()) {
            echo '<script>
                if ("serviceWorker" in navigator) {
                    window.addEventListener("load", function() {
                        // Future: Service worker implementation
                    });
                }
            </script>';
        }
        
        // Performance monitoring
        if (WP_DEBUG) {
            $this->output_performance_metrics();
        }
    }
    
    /**
     * Output performance metrics for debugging
     */
    private function output_performance_metrics() {
        global $wpdb;
        
        $queries = get_num_queries();
        $memory = size_format(memory_get_peak_usage(true));
        $load_time = timer_stop(0, 3);
        
        echo '<!-- Performance Metrics: Queries: ' . $queries . ', Memory: ' . $memory . ', Load Time: ' . $load_time . 's -->';
    }
    
    /**
     * Clear theme cache
     */
    public function clear_theme_cache() {
        wp_cache_flush();
        
        // Clear file-based cache
        $upload_dir = wp_upload_dir();
        $cache_dir = $upload_dir['basedir'] . '/rts-cache/';
        
        if (is_dir($cache_dir)) {
            $files = glob($cache_dir . '*');
            foreach ($files as $file) {
                if (is_file($file)) {
                    unlink($file);
                }
            }
        }
        
        wp_send_json_success(array('message' => 'Cache cleared successfully'));
    }
    
    /**
     * Optimize database queries
     */
    public function optimize_database_queries() {
        // Index optimization
        global $wpdb;
        
        // Add indexes for better performance
        $indexes = array(
            'rts_subscriptions' => array(
                'email' => 'email',
                'status' => 'status',
                'subscription_date' => 'subscription_date'
            ),
            'rts_login_attempts' => array(
                'ip_time' => 'ip_address, attempt_time'
            )
        );
        
        foreach ($indexes as $table => $table_indexes) {
            $full_table_name = $wpdb->prefix . $table;
            
            if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($full_table_name)))) {
                foreach ($table_indexes as $index_name => $columns) {
                    $index_exists = $wpdb->get_var($wpdb->prepare(
                        "SHOW INDEX FROM {$full_table_name} WHERE Key_name = %s",
                        $index_name
                    ));
                    
                    if (!$index_exists) {
                        $wpdb->query("ALTER TABLE {$full_table_name} ADD INDEX {$index_name} ({$columns})");
                    }
                }
            }
        }
    }
}

// Initialize performance optimizations
new RTS_Performance();

/**
 * Additional performance utilities
 */

/**
 * Get optimized image URL with WebP support
 */
function rts_get_optimized_image($attachment_id, $size = 'medium') {
    $image_url = wp_get_attachment_image_url($attachment_id, $size);
    
    // Check if WebP is supported
    if (function_exists('imagewebp') && isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'image/webp') !== false) {
        $webp_url = preg_replace('/\.(jpg|jpeg|png)$/i', '.webp', $image_url);
        
        // Check if WebP version exists
        $webp_path = str_replace(home_url(), ABSPATH, $webp_url);
        if (file_exists($webp_path)) {
            return $webp_url;
        }
    }
    
    return $image_url;
}

/**
 * Preload critical resources
 */
function rts_preload_resource($url, $type = 'script', $crossorigin = false) {
    $crossorigin_attr = $crossorigin ? ' crossorigin' : '';
    echo '<link rel="preload" href="' . esc_url($url) . '" as="' . esc_attr($type) . '"' . $crossorigin_attr . '>' . "\n";
}

/**
 * Generate critical CSS for specific page
 */
function rts_generate_page_critical_css($page_template = '') {
    $cache_key = 'rts_critical_css_' . md5($page_template . get_queried_object_id());
    $critical_css = wp_cache_get($cache_key, 'rts_critical_css');
    
    if ($critical_css === false) {
        // Generate page-specific critical CSS
        $critical_css = rts_extract_critical_css($page_template);
        wp_cache_set($cache_key, $critical_css, 'rts_critical_css', 86400);
    }
    
    return $critical_css;
}

/**
 * Extract critical CSS (placeholder for advanced implementation)
 */
function rts_extract_critical_css($template = '') {
    // This would integrate with tools like Critical CSS generators
    // For now, return basic critical CSS
    return '
        :root { --primary: #374a67; --background: #433e0e; }
        body { font-family: Inter, sans-serif; margin: 0; }
        .site-header { height: 64px; position: fixed; top: 0; width: 100%; }
        .site-main { padding-top: 96px; }
    ';
}