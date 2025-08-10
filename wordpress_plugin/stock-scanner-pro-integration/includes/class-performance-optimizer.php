<?php
/**
 * Performance Optimizer Class for Stock Scanner Pro Plugin
 * Handles caching, database optimization, and compression
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Stock_Scanner_Performance_Optimizer {
    
    /**
     * Cache timeouts in seconds
     */
    const CACHE_TIMEOUTS = [
        'stock_data' => 60,        // 1 minute for real-time data
        'market_hours' => 3600,    // 1 hour for market hours
        'api_responses' => 300,    // 5 minutes for API responses
        'analytics' => 900,        // 15 minutes for analytics
        'trending' => 180,         // 3 minutes for trending data
    ];
    
    /**
     * Initialize performance optimizations
     */
    public function __construct() {
        add_action('init', [$this, 'init_performance_features']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_performance_scripts']);
        
        // WordPress-specific optimizations
        $this->init_wordpress_optimizations();
        
        // Cache management
        $this->init_cache_system();
        
        // Database optimizations
        $this->init_database_optimizations();
    }
    
    /**
     * Initialize performance features
     */
    public function init_performance_features() {
        // Enable object caching if available
        if (function_exists('wp_cache_set')) {
            add_filter('stock_scanner_cache_enabled', '__return_true');
        }
        
        // Add performance monitoring for admins
        if (current_user_can('administrator')) {
            add_action('wp_footer', [$this, 'add_performance_monitoring']);
        }
        
        // Optimize AJAX requests
        add_action('wp_ajax_stock_scanner_get_data', [$this, 'optimized_ajax_handler']);
        add_action('wp_ajax_nopriv_stock_scanner_get_data', [$this, 'optimized_ajax_handler']);
    }
    
    /**
     * Enqueue performance-optimized scripts
     */
    public function enqueue_performance_scripts() {
        // Plugin performance scripts
        wp_enqueue_script(
            'stock-scanner-plugin-performance',
            STOCK_SCANNER_PLUGIN_URL . 'assets/js/plugin-performance.js',
            ['jquery'],
            STOCK_SCANNER_PLUGIN_VERSION,
            true
        );
        
        // Localize script with performance settings
        wp_localize_script('stock-scanner-plugin-performance', 'stockScannerPerf', [
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_perf_nonce'),
            'cache_timeout' => self::CACHE_TIMEOUTS['api_responses'],
            'debug_mode' => defined('WP_DEBUG') && WP_DEBUG,
            'lazy_load_threshold' => 50, // pixels
        ]);
    }
    
    /**
     * Initialize WordPress-specific optimizations
     */
    private function init_wordpress_optimizations() {
        // Optimize WordPress queries
        add_action('pre_get_posts', [$this, 'optimize_queries']);
        
        // Add caching headers
        add_action('send_headers', [$this, 'add_cache_headers']);
        
        // Optimize admin performance
        if (is_admin()) {
            add_action('admin_init', [$this, 'optimize_admin_performance']);
        }
    }
    
    /**
     * Initialize cache system
     */
    private function init_cache_system() {
        // Set up transient-based caching for plugin data
        add_action('stock_scanner_clear_cache', [$this, 'clear_plugin_cache']);
        
        // Cache stock data with appropriate timeouts
        add_filter('stock_scanner_get_stock_data', [$this, 'cache_stock_data'], 10, 2);
    }
    
    /**
     * Initialize database optimizations
     */
    private function init_database_optimizations() {
        // Optimize database queries
        add_filter('stock_scanner_db_query', [$this, 'optimize_db_query'], 10, 2);
        
        // Add query monitoring
        if (defined('WP_DEBUG') && WP_DEBUG) {
            add_action('shutdown', [$this, 'monitor_db_queries']);
        }
    }
    
    /**
     * Generate cache key for stock data
     */
    public function generate_cache_key($prefix, $data = []) {
        $key_data = array_merge(['prefix' => $prefix], $data);
        $key_data['timestamp'] = floor(time() / 300); // 5-minute buckets
        
        return 'stock_scanner_' . md5(serialize($key_data));
    }
    
    /**
     * Cache stock data with appropriate timeout
     */
    public function cache_stock_data($data, $cache_key) {
        $timeout = self::CACHE_TIMEOUTS['stock_data'];
        
        // Use WordPress transients for caching
        set_transient($cache_key, $data, $timeout);
        
        return $data;
    }
    
    /**
     * Get cached stock data
     */
    public function get_cached_stock_data($cache_key) {
        return get_transient($cache_key);
    }
    
    /**
     * Optimized AJAX handler with caching
     */
    public function optimized_ajax_handler() {
        // Verify nonce
        if (!wp_verify_nonce($_POST['nonce'], 'stock_scanner_perf_nonce')) {
            wp_die('Security check failed');
        }
        
        $request_type = sanitize_text_field($_POST['type']);
        $cache_key = $this->generate_cache_key('ajax_' . $request_type, $_POST);
        
        // Try to get from cache first
        $cached_data = $this->get_cached_data($cache_key);
        if ($cached_data !== false) {
            wp_send_json_success($cached_data);
            return;
        }
        
        // Process request and cache result
        $data = $this->process_ajax_request($request_type, $_POST);
        $this->cache_data($cache_key, $data, self::CACHE_TIMEOUTS['api_responses']);
        
        wp_send_json_success($data);
    }
    
    /**
     * Process AJAX request based on type
     */
    private function process_ajax_request($type, $data) {
        switch ($type) {
            case 'trending_stocks':
                return $this->get_trending_stocks();
            case 'stock_details':
                return $this->get_stock_details($data['symbol']);
            case 'market_status':
                return $this->get_market_status();
            default:
                return ['error' => 'Unknown request type'];
        }
    }
    
    /**
     * Get trending stocks with caching
     */
    public function get_trending_stocks($limit = 10) {
        $cache_key = $this->generate_cache_key('trending_stocks', ['limit' => $limit]);
        $cached = $this->get_cached_data($cache_key);
        
        if ($cached !== false) {
            return $cached;
        }
        
        // Simulate trending stocks data (replace with actual API call)
        $trending = [
            ['symbol' => 'AAPL', 'change' => '+2.5%', 'price' => '$150.25'],
            ['symbol' => 'GOOGL', 'change' => '+1.8%', 'price' => '$2,750.00'],
            ['symbol' => 'MSFT', 'change' => '+3.2%', 'price' => '$305.50'],
            ['symbol' => 'AMZN', 'change' => '-0.5%', 'price' => '$3,200.75'],
            ['symbol' => 'TSLA', 'change' => '+5.7%', 'price' => '$850.00'],
        ];
        
        $result = array_slice($trending, 0, $limit);
        $this->cache_data($cache_key, $result, self::CACHE_TIMEOUTS['trending']);
        
        return $result;
    }
    
    /**
     * Get stock details with caching
     */
    public function get_stock_details($symbol) {
        $cache_key = $this->generate_cache_key('stock_details', ['symbol' => $symbol]);
        $cached = $this->get_cached_data($cache_key);
        
        if ($cached !== false) {
            return $cached;
        }
        
        // Simulate stock details (replace with actual API call)
        $details = [
            'symbol' => $symbol,
            'price' => '$' . number_format(rand(50, 500) + (rand(0, 99) / 100), 2),
            'change' => (rand(0, 1) ? '+' : '-') . number_format(rand(0, 10) + (rand(0, 99) / 100), 2) . '%',
            'volume' => number_format(rand(1000000, 50000000)),
            'market_cap' => '$' . number_format(rand(1, 100)) . 'B',
            'last_updated' => current_time('mysql')
        ];
        
        $this->cache_data($cache_key, $details, self::CACHE_TIMEOUTS['stock_data']);
        
        return $details;
    }
    
    /**
     * Get market status with caching
     */
    public function get_market_status() {
        $cache_key = $this->generate_cache_key('market_status');
        $cached = $this->get_cached_data($cache_key);
        
        if ($cached !== false) {
            return $cached;
        }
        
        // Simple market hours check (9:30 AM - 4:00 PM EST)
        $current_time = current_time('H:i');
        $is_open = ($current_time >= '09:30' && $current_time <= '16:00');
        
        $status = [
            'is_open' => $is_open,
            'status' => $is_open ? 'Open' : 'Closed',
            'next_open' => $is_open ? null : '9:30 AM EST',
            'timezone' => 'EST'
        ];
        
        $this->cache_data($cache_key, $status, self::CACHE_TIMEOUTS['market_hours']);
        
        return $status;
    }
    
    /**
     * Generic cache data method
     */
    public function cache_data($key, $data, $timeout) {
        return set_transient($key, $data, $timeout);
    }
    
    /**
     * Generic get cached data method
     */
    public function get_cached_data($key) {
        return get_transient($key);
    }
    
    /**
     * Clear plugin cache
     */
    public function clear_plugin_cache() {
        global $wpdb;
        
        // Delete all plugin-related transients
        $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s",
                '%transient_stock_scanner_%'
            )
        );
        
        // Also clear timeout transients
        $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s",
                '%transient_timeout_stock_scanner_%'
            )
        );
        
        do_action('stock_scanner_cache_cleared');
    }
    
    /**
     * Optimize WordPress queries
     */
    public function optimize_queries($query) {
        // Only affect main queries, not admin queries
        if (!is_admin() && $query->is_main_query()) {
            // Limit post meta queries
            $query->set('meta_query', []);
            
            // Optimize for mobile
            if (wp_is_mobile()) {
                $query->set('posts_per_page', 10);
            }
        }
    }
    
    /**
     * Add cache headers for better performance
     */
    public function add_cache_headers() {
        if (!is_admin() && !is_user_logged_in()) {
            $expires = 3600; // 1 hour
            header('Cache-Control: public, max-age=' . $expires);
            header('Expires: ' . gmdate('D, d M Y H:i:s', time() + $expires) . ' GMT');
        }
    }
    
    /**
     * Optimize admin performance
     */
    public function optimize_admin_performance() {
        // Remove unnecessary admin features for plugin pages
        if (isset($_GET['page']) && strpos($_GET['page'], 'stock-scanner') !== false) {
            // Disable some admin features that aren't needed
            remove_action('admin_print_styles', 'print_emoji_styles');
            remove_action('admin_print_scripts', 'print_emoji_detection_script');
        }
    }
    
    /**
     * Optimize database query
     */
    public function optimize_db_query($query, $params) {
        // Add basic query optimizations
        if (strpos($query, 'SELECT') === 0) {
            // Add LIMIT if not present for SELECT queries
            if (strpos($query, 'LIMIT') === false) {
                $query .= ' LIMIT 1000';
            }
        }
        
        return $query;
    }
    
    /**
     * Monitor database queries for performance
     */
    public function monitor_db_queries() {
        if (defined('SAVEQUERIES') && SAVEQUERIES) {
            global $wpdb;
            
            $total_time = 0;
            $slow_queries = 0;
            
            foreach ($wpdb->queries as $query) {
                $total_time += $query[1];
                if ($query[1] > 0.1) { // Queries taking more than 100ms
                    $slow_queries++;
                }
            }
            
            if ($slow_queries > 0) {
                error_log("Stock Scanner Plugin: {$slow_queries} slow queries detected. Total time: {$total_time}s");
            }
        }
    }
    
    /**
     * Add performance monitoring script to footer
     */
    public function add_performance_monitoring() {
        ?>
        <script>
        (function() {
            if (typeof window.performance !== 'undefined' && window.stockScannerPerf) {
                window.addEventListener('load', function() {
                    setTimeout(function() {
                        const perfData = performance.getEntriesByType('navigation')[0];
                        if (perfData && window.console) {
                            console.log('Stock Scanner Plugin Performance:', {
                                'Page Load': (perfData.loadEventEnd - perfData.navigationStart).toFixed(2) + 'ms',
                                'DOM Ready': (perfData.domContentLoadedEventEnd - perfData.navigationStart).toFixed(2) + 'ms',
                                'First Byte': (perfData.responseStart - perfData.navigationStart).toFixed(2) + 'ms'
                            });
                        }
                    }, 100);
                });
            }
        })();
        </script>
        <?php
    }
    
    /**
     * Get performance statistics
     */
    public function get_performance_stats() {
        $stats = [
            'cache_hits' => get_option('stock_scanner_cache_hits', 0),
            'cache_misses' => get_option('stock_scanner_cache_misses', 0),
            'total_queries' => 0,
            'slow_queries' => 0,
            'memory_usage' => memory_get_peak_usage(true),
            'last_updated' => current_time('mysql')
        ];
        
        // Calculate cache hit ratio
        $total_requests = $stats['cache_hits'] + $stats['cache_misses'];
        $stats['cache_hit_ratio'] = $total_requests > 0 ? 
            round(($stats['cache_hits'] / $total_requests) * 100, 2) : 0;
        
        return $stats;
    }
    
    /**
     * Update cache statistics
     */
    public function update_cache_stats($type) {
        $current = get_option('stock_scanner_cache_' . $type . 's', 0);
        update_option('stock_scanner_cache_' . $type . 's', $current + 1);
    }
}