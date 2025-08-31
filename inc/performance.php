<?php
/**
 * Performance Optimizations for Production
 * @package RetailTradeScanner
 */

if (!defined('ABSPATH')) { exit; }

/**
 * Production performance optimizations
 */
class RTS_Performance {
    
    public function __construct() {
        add_action('init', [$this, 'init_performance']);
        add_action('wp_enqueue_scripts', [$this, 'optimize_assets']);
        add_action('wp_head', [$this, 'add_preload_hints'], 1);
        add_filter('script_loader_tag', [$this, 'add_async_defer'], 10, 3);
        add_filter('style_loader_tag', [$this, 'add_preload_stylesheets'], 10, 4);
        add_action('wp_footer', [$this, 'add_performance_monitoring']);
    }
    
    /**
     * Initialize performance optimizations
     */
    public function init_performance() {
        // Enable gzip compression
        if (!ob_get_level() && !ini_get('zlib.output_compression')) {
            add_action('init', 'ob_start');
        }
        
        // Remove unnecessary WordPress features
        remove_action('wp_head', 'print_emoji_detection_script', 7);
        remove_action('wp_print_styles', 'print_emoji_styles');
        remove_action('admin_print_scripts', 'print_emoji_detection_script');
        remove_action('admin_print_styles', 'print_emoji_styles');
        
        // Disable embeds if not needed
        add_action('wp_footer', [$this, 'deregister_embed_script']);
        remove_action('wp_head', 'wp_oembed_add_discovery_links');
        
        // Optimize database queries
        add_action('pre_get_posts', [$this, 'optimize_queries']);
        
        // Enable browser caching
        add_action('send_headers', [$this, 'add_cache_headers']);
        
        // Optimize images
        add_filter('wp_get_attachment_image_attributes', [$this, 'add_image_attributes'], 10, 3);
        
        // Clean up wp_head
        remove_action('wp_head', 'adjacent_posts_rel_link_wp_head');
        remove_action('wp_head', 'wp_resource_hints', 2);
    }
    
    /**
     * Optimize asset loading
     */
    public function optimize_assets() {
        if (!is_admin()) {
            // Remove unnecessary scripts
            wp_deregister_script('wp-embed');
            
            // Combine and minify CSS/JS (in production environment)
            if (defined('WP_ENV') && WP_ENV === 'production') {
                $this->minify_assets();
            }
            
            // Add resource hints
            wp_enqueue_script('rts-preload', '', [], '', false);
            wp_add_inline_script('rts-preload', $this->get_preload_script(), 'before');
        }
    }
    
    /**
     * Add preload hints for critical resources
     */
    public function add_preload_hints() {
        // Preload critical fonts
        echo '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . "\n";
        echo '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"></noscript>' . "\n";
        
        // Preload critical CSS
        $critical_css = get_template_directory_uri() . '/assets/css/critical.css';
        if (file_exists(get_template_directory() . '/assets/css/critical.css')) {
            echo '<link rel="preload" href="' . esc_url($critical_css) . '" as="style">' . "\n";
        }
        
        // DNS prefetch for external resources
        echo '<link rel="dns-prefetch" href="//fonts.googleapis.com">' . "\n";
        echo '<link rel="dns-prefetch" href="//fonts.gstatic.com">' . "\n";
        echo '<link rel="dns-prefetch" href="//www.google-analytics.com">' . "\n";
        
        // Preconnect to critical origins
        echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
    }
    
    /**
     * Add async/defer to scripts
     */
    public function add_async_defer($tag, $handle, $src) {
        // Scripts that should be async
        $async_scripts = ['google-analytics', 'gtag', 'rts-analytics'];
        
        // Scripts that should be defer
        $defer_scripts = ['rts-theme-js', 'rts-mobile-js'];
        
        if (in_array($handle, $async_scripts)) {
            return str_replace('<script ', '<script async ', $tag);
        }
        
        if (in_array($handle, $defer_scripts)) {
            return str_replace('<script ', '<script defer ', $tag);
        }
        
        return $tag;
    }
    
    /**
     * Add preload for stylesheets
     */
    public function add_preload_stylesheets($html, $handle, $href, $media) {
        // Critical stylesheets to preload
        $preload_styles = ['rts-style'];
        
        if (in_array($handle, $preload_styles)) {
            $html = '<link rel="preload" href="' . $href . '" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' . 
                    '<noscript>' . $html . '</noscript>';
        }
        
        return $html;
    }
    
    /**
     * Deregister embed script
     */
    public function deregister_embed_script() {
        wp_deregister_script('wp-embed');
    }
    
    /**
     * Optimize database queries
     */
    public function optimize_queries($query) {
        if (!is_admin() && $query->is_main_query()) {
            // Limit posts per page for better performance
            if (is_home()) {
                $query->set('posts_per_page', 12);
            }
            
            // Only load necessary fields
            if (is_archive() || is_home()) {
                $query->set('no_found_rows', true);
                $query->set('update_post_meta_cache', false);
                $query->set('update_post_term_cache', false);
            }
        }
    }
    
    /**
     * Add cache headers
     */
    public function add_cache_headers() {
        if (!is_admin() && !is_user_logged_in()) {
            $expires = gmdate('D, d M Y H:i:s', time() + MONTH_IN_SECONDS) . ' GMT';
            
            header('Expires: ' . $expires);
            header('Cache-Control: public, max-age=' . MONTH_IN_SECONDS);
            header('Pragma: cache');
            
            // ETags for better caching
            $etag = md5(get_template_directory() . filemtime(get_template_directory() . '/style.css'));
            header('ETag: "' . $etag . '"');
            
            if (isset($_SERVER['HTTP_IF_NONE_MATCH']) && $_SERVER['HTTP_IF_NONE_MATCH'] === '"' . $etag . '"') {
                header('HTTP/1.1 304 Not Modified');
                exit;
            }
        }
    }
    
    /**
     * Add image optimization attributes
     */
    public function add_image_attributes($attr, $attachment, $size) {
        // Add loading="lazy" for better performance
        if (!isset($attr['loading'])) {
            $attr['loading'] = 'lazy';
        }
        
        // Add decoding="async" for non-critical images
        if (!isset($attr['decoding'])) {
            $attr['decoding'] = 'async';
        }
        
        return $attr;
    }
    
    /**
     * Minify assets (simple implementation)
     */
    private function minify_assets() {
        // This is a basic implementation
        // In production, use a proper build tool like Webpack or Gulp
        
        $css_files = [
            get_template_directory() . '/style.css',
            get_template_directory() . '/assets/css/additional.css'
        ];
        
        $minified_css = '';
        foreach ($css_files as $file) {
            if (file_exists($file)) {
                $css = file_get_contents($file);
                // Basic minification
                $css = preg_replace('/\s+/', ' ', $css);
                $css = str_replace(['; ', ' {', '{ ', ' }', '} ', ': '], [';', '{', '{', '}', '}', ':'], $css);
                $minified_css .= $css;
            }
        }
        
        // Save minified CSS
        $minified_path = get_template_directory() . '/assets/css/minified.css';
        if (!file_exists($minified_path) || filemtime(get_template_directory() . '/style.css') > filemtime($minified_path)) {
            file_put_contents($minified_path, $minified_css);
        }
    }
    
    /**
     * Get preload script for critical resources
     */
    private function get_preload_script() {
        return "
        (function() {
            // Preload critical pages
            var criticalPages = ['/dashboard/', '/scanner/', '/portfolio/'];
            var preloadedPages = [];
            
            function preloadPage(url) {
                if (preloadedPages.indexOf(url) === -1) {
                    var link = document.createElement('link');
                    link.rel = 'prefetch';
                    link.href = url;
                    document.head.appendChild(link);
                    preloadedPages.push(url);
                }
            }
            
            // Preload on hover
            document.addEventListener('mouseover', function(e) {
                var link = e.target.closest('a');
                if (link && link.href) {
                    var path = new URL(link.href).pathname;
                    if (criticalPages.indexOf(path) !== -1) {
                        preloadPage(link.href);
                    }
                }
            });
            
            // Preload critical pages after load
            setTimeout(function() {
                criticalPages.forEach(function(page) {
                    preloadPage(window.location.origin + page);
                });
            }, 2000);
        })();
        ";
    }
    
    /**
     * Add performance monitoring
     */
    public function add_performance_monitoring() {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            echo '<script>
                if ("performance" in window) {
                    window.addEventListener("load", function() {
                        setTimeout(function() {
                            var perfData = performance.timing;
                            var loadTime = perfData.loadEventEnd - perfData.navigationStart;
                            var domReady = perfData.domContentLoadedEventEnd - perfData.navigationStart;
                            
                            console.log("Page Load Time: " + loadTime + "ms");
                            console.log("DOM Ready: " + domReady + "ms");
                            
                            // Send to analytics if available
                            if (typeof gtag !== "undefined") {
                                gtag("event", "timing_complete", {
                                    name: "load",
                                    value: loadTime
                                });
                            }
                        }, 0);
                    });
                }
            </script>';
        }
    }
}

// Initialize performance optimizations
new RTS_Performance();

/**
 * Object cache helpers
 */
function rts_get_cached($key, $callback, $expiration = 3600) {
    $cached = wp_cache_get($key, 'rts');
    
    if ($cached === false) {
        $cached = call_user_func($callback);
        wp_cache_set($key, $cached, 'rts', $expiration);
    }
    
    return $cached;
}

/**
 * Database query optimization
 */
function rts_optimize_query($query) {
    global $wpdb;
    
    // Add query cache
    $cache_key = 'rts_query_' . md5($query);
    $result = wp_cache_get($cache_key, 'rts');
    
    if ($result === false) {
        $result = $wpdb->get_results($query);
        wp_cache_set($cache_key, $result, 'rts', 300); // 5 minutes
    }
    
    return $result;
}

/**
 * Critical CSS inline for above-the-fold content
 */
function rts_inline_critical_css() {
    $critical_css = get_template_directory() . '/assets/css/critical.css';
    
    if (file_exists($critical_css)) {
        echo '<style id="critical-css">';
        echo file_get_contents($critical_css);
        echo '</style>';
    }
}
add_action('wp_head', 'rts_inline_critical_css', 1);