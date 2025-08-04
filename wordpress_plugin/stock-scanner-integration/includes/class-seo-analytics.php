<?php
/**
 * SEO Analytics and Performance Tracking for Stock Scanner Professional
 * 
 * Tracks SEO metrics, page performance, and search rankings
 */

class StockScannerSEOAnalytics {
    
    private $table_name;
    
    public function __construct() {
        global $wpdb;
        $this->table_name = $wpdb->prefix . 'stock_scanner_seo_analytics';
        
        add_action('wp_head', [$this, 'add_tracking_scripts']);
        add_action('wp_footer', [$this, 'track_page_performance']);
        add_action('wp_ajax_stock_scanner_track_conversion', [$this, 'track_conversion']);
        add_action('wp_ajax_nopriv_stock_scanner_track_conversion', [$this, 'track_conversion']);
        
        // Create analytics table on activation
        register_activation_hook(STOCK_SCANNER_PRO_PLUGIN_FILE, [$this, 'create_analytics_table']);
    }
    
    /**
     * Create analytics table
     */
    public function create_analytics_table() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE {$this->table_name} (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            page_slug varchar(100) NOT NULL,
            page_url varchar(500) NOT NULL,
            user_agent text,
            referrer varchar(500),
            session_id varchar(100),
            time_on_page int(11) DEFAULT 0,
            scroll_depth int(3) DEFAULT 0,
            conversion_type varchar(50),
            conversion_value decimal(10,2) DEFAULT 0.00,
            utm_source varchar(100),
            utm_medium varchar(100),
            utm_campaign varchar(100),
            search_query varchar(500),
            device_type varchar(20),
            page_load_time decimal(5,3) DEFAULT 0.000,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY page_slug (page_slug),
            KEY session_id (session_id),
            KEY created_at (created_at)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
    
    /**
     * Add tracking scripts to head
     */
    public function add_tracking_scripts() {
        if (!$this->is_stock_scanner_page()) {
            return;
        }
        
        ?>
        <!-- Stock Scanner SEO Analytics -->
        <script>
        window.stockScannerAnalytics = {
            sessionId: '<?php echo $this->get_session_id(); ?>',
            pageSlug: '<?php echo $this->get_current_page_slug(); ?>',
            startTime: Date.now(),
            maxScroll: 0,
            ajaxUrl: '<?php echo admin_url('admin-ajax.php'); ?>',
            nonce: '<?php echo wp_create_nonce('stock_scanner_analytics'); ?>'
        };
        
        // Track scroll depth
        window.addEventListener('scroll', function() {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            window.stockScannerAnalytics.maxScroll = Math.max(window.stockScannerAnalytics.maxScroll, scrollPercent);
        });
        
        // Track page load time
        window.addEventListener('load', function() {
            window.stockScannerAnalytics.loadTime = (Date.now() - window.stockScannerAnalytics.startTime) / 1000;
        });
        
        // Track conversion events
        function trackConversion(type, value = 0) {
            fetch(window.stockScannerAnalytics.ajaxUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    action: 'stock_scanner_track_conversion',
                    nonce: window.stockScannerAnalytics.nonce,
                    conversion_type: type,
                    conversion_value: value,
                    session_id: window.stockScannerAnalytics.sessionId,
                    page_slug: window.stockScannerAnalytics.pageSlug
                })
            });
        }
        
        // Auto-track common conversions
        document.addEventListener('click', function(e) {
            if (e.target.matches('.plan-button, .cta-button')) {
                trackConversion('plan_click');
            }
            if (e.target.matches('a[href*="premium-plans"]')) {
                trackConversion('premium_interest');
            }
            if (e.target.matches('.stock-search-button')) {
                trackConversion('stock_search');
            }
        });
        </script>
        
        <!-- Google Analytics 4 Integration -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_MEASUREMENT_ID', {
            custom_map: {
                'custom_parameter_1': 'page_slug',
                'custom_parameter_2': 'user_type'
            }
        });
        
        // Enhanced ecommerce tracking for premium plans
        gtag('event', 'page_view', {
            page_slug: window.stockScannerAnalytics.pageSlug,
            user_type: '<?php echo is_user_logged_in() ? 'logged_in' : 'anonymous'; ?>'
        });
        </script>
        
        <!-- Core Web Vitals Tracking -->
        <script>
        function trackWebVitals() {
            if ('web-vital' in window) {
                // Track Largest Contentful Paint
                new PerformanceObserver((entryList) => {
                    for (const entry of entryList.getEntries()) {
                        if (entry.entryType === 'largest-contentful-paint') {
                            gtag('event', 'web_vitals', {
                                metric_name: 'LCP',
                                metric_value: Math.round(entry.startTime),
                                page_slug: window.stockScannerAnalytics.pageSlug
                            });
                        }
                    }
                }).observe({entryTypes: ['largest-contentful-paint']});
                
                // Track First Input Delay
                new PerformanceObserver((entryList) => {
                    for (const entry of entryList.getEntries()) {
                        gtag('event', 'web_vitals', {
                            metric_name: 'FID',
                            metric_value: Math.round(entry.processingStart - entry.startTime),
                            page_slug: window.stockScannerAnalytics.pageSlug
                        });
                    }
                }).observe({entryTypes: ['first-input']});
                
                // Track Cumulative Layout Shift
                let clsValue = 0;
                new PerformanceObserver((entryList) => {
                    for (const entry of entryList.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    }
                    gtag('event', 'web_vitals', {
                        metric_name: 'CLS',
                        metric_value: Math.round(clsValue * 1000),
                        page_slug: window.stockScannerAnalytics.pageSlug
                    });
                }).observe({entryTypes: ['layout-shift']});
            }
        }
        
        if (document.readyState === 'complete') {
            trackWebVitals();
        } else {
            window.addEventListener('load', trackWebVitals);
        }
        </script>
        <?php
    }
    
    /**
     * Track page performance in footer
     */
    public function track_page_performance() {
        if (!$this->is_stock_scanner_page()) {
            return;
        }
        
        ?>
        <script>
        // Send performance data when user leaves page
        window.addEventListener('beforeunload', function() {
            const timeOnPage = Math.round((Date.now() - window.stockScannerAnalytics.startTime) / 1000);
            const data = {
                action: 'stock_scanner_track_performance',
                nonce: window.stockScannerAnalytics.nonce,
                session_id: window.stockScannerAnalytics.sessionId,
                page_slug: window.stockScannerAnalytics.pageSlug,
                time_on_page: timeOnPage,
                scroll_depth: window.stockScannerAnalytics.maxScroll,
                page_load_time: window.stockScannerAnalytics.loadTime || 0
            };
            
            // Use sendBeacon for reliable data sending
            if (navigator.sendBeacon) {
                const formData = new FormData();
                Object.keys(data).forEach(key => formData.append(key, data[key]));
                navigator.sendBeacon(window.stockScannerAnalytics.ajaxUrl, formData);
            }
        });
        </script>
        <?php
    }
    
    /**
     * Handle conversion tracking AJAX
     */
    public function track_conversion() {
        check_ajax_referer('stock_scanner_analytics', 'nonce');
        
        global $wpdb;
        
        $data = [
            'session_id' => sanitize_text_field($_POST['session_id']),
            'page_slug' => sanitize_text_field($_POST['page_slug']),
            'page_url' => esc_url_raw($_SERVER['HTTP_REFERER'] ?? ''),
            'conversion_type' => sanitize_text_field($_POST['conversion_type']),
            'conversion_value' => floatval($_POST['conversion_value'] ?? 0),
            'user_agent' => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
            'referrer' => esc_url_raw($_SERVER['HTTP_REFERER'] ?? ''),
            'utm_source' => sanitize_text_field($_GET['utm_source'] ?? ''),
            'utm_medium' => sanitize_text_field($_GET['utm_medium'] ?? ''),
            'utm_campaign' => sanitize_text_field($_GET['utm_campaign'] ?? ''),
            'device_type' => $this->detect_device_type(),
            'time_on_page' => intval($_POST['time_on_page'] ?? 0),
            'scroll_depth' => intval($_POST['scroll_depth'] ?? 0),
            'page_load_time' => floatval($_POST['page_load_time'] ?? 0)
        ];
        
        $wpdb->insert($this->table_name, $data);
        
        wp_die();
    }
    
    /**
     * Get analytics dashboard data
     */
    public function get_analytics_data($date_range = '30 days') {
        global $wpdb;
        
        $date_condition = "created_at >= DATE_SUB(NOW(), INTERVAL {$date_range})";
        
        // Page performance metrics
        $page_performance = $wpdb->get_results("
            SELECT 
                page_slug,
                COUNT(*) as page_views,
                AVG(time_on_page) as avg_time_on_page,
                AVG(scroll_depth) as avg_scroll_depth,
                AVG(page_load_time) as avg_load_time,
                COUNT(DISTINCT session_id) as unique_visitors
            FROM {$this->table_name} 
            WHERE {$date_condition}
            GROUP BY page_slug
            ORDER BY page_views DESC
        ");
        
        // Conversion metrics
        $conversions = $wpdb->get_results("
            SELECT 
                conversion_type,
                COUNT(*) as conversion_count,
                SUM(conversion_value) as total_value
            FROM {$this->table_name} 
            WHERE {$date_condition} AND conversion_type IS NOT NULL
            GROUP BY conversion_type
            ORDER BY conversion_count DESC
        ");
        
        // Traffic sources
        $traffic_sources = $wpdb->get_results("
            SELECT 
                COALESCE(NULLIF(utm_source, ''), 'direct') as source,
                COUNT(*) as visits,
                COUNT(DISTINCT session_id) as unique_visitors
            FROM {$this->table_name} 
            WHERE {$date_condition}
            GROUP BY source
            ORDER BY visits DESC
        ");
        
        // Device breakdown
        $device_breakdown = $wpdb->get_results("
            SELECT 
                device_type,
                COUNT(*) as visits,
                AVG(time_on_page) as avg_time_on_page
            FROM {$this->table_name} 
            WHERE {$date_condition}
            GROUP BY device_type
            ORDER BY visits DESC
        ");
        
        return [
            'page_performance' => $page_performance,
            'conversions' => $conversions,
            'traffic_sources' => $traffic_sources,
            'device_breakdown' => $device_breakdown,
            'total_pageviews' => $wpdb->get_var("SELECT COUNT(*) FROM {$this->table_name} WHERE {$date_condition}"),
            'unique_visitors' => $wpdb->get_var("SELECT COUNT(DISTINCT session_id) FROM {$this->table_name} WHERE {$date_condition}")
        ];
    }
    
    /**
     * Generate SEO performance report
     */
    public function generate_seo_report() {
        $analytics = $this->get_analytics_data();
        
        $report = [
            'overview' => [
                'total_pageviews' => $analytics['total_pageviews'],
                'unique_visitors' => $analytics['unique_visitors'],
                'avg_pages_per_session' => round($analytics['total_pageviews'] / max($analytics['unique_visitors'], 1), 2)
            ],
            'top_pages' => array_slice($analytics['page_performance'], 0, 5),
            'conversion_rate' => $this->calculate_conversion_rate($analytics),
            'page_speed_score' => $this->calculate_page_speed_score($analytics),
            'mobile_friendliness' => $this->calculate_mobile_score($analytics),
            'seo_recommendations' => $this->generate_seo_recommendations($analytics)
        ];
        
        return $report;
    }
    
    /**
     * Calculate conversion rate
     */
    private function calculate_conversion_rate($analytics) {
        $total_conversions = array_sum(array_column($analytics['conversions'], 'conversion_count'));
        $conversion_rate = $analytics['unique_visitors'] > 0 ? 
            round(($total_conversions / $analytics['unique_visitors']) * 100, 2) : 0;
        
        return [
            'rate' => $conversion_rate,
            'total_conversions' => $total_conversions,
            'top_conversion' => $analytics['conversions'][0] ?? null
        ];
    }
    
    /**
     * Calculate page speed score
     */
    private function calculate_page_speed_score($analytics) {
        $avg_load_times = array_column($analytics['page_performance'], 'avg_load_time');
        $overall_avg = array_sum($avg_load_times) / max(count($avg_load_times), 1);
        
        // Score based on Google's recommendations
        if ($overall_avg <= 2.5) {
            $score = 'Good';
        } elseif ($overall_avg <= 4.0) {
            $score = 'Needs Improvement';
        } else {
            $score = 'Poor';
        }
        
        return [
            'score' => $score,
            'avg_load_time' => round($overall_avg, 3),
            'fastest_page' => $this->find_fastest_page($analytics['page_performance']),
            'slowest_page' => $this->find_slowest_page($analytics['page_performance'])
        ];
    }
    
    /**
     * Calculate mobile score
     */
    private function calculate_mobile_score($analytics) {
        $mobile_visits = 0;
        $total_visits = 0;
        
        foreach ($analytics['device_breakdown'] as $device) {
            $total_visits += $device->visits;
            if ($device->device_type === 'mobile') {
                $mobile_visits = $device->visits;
            }
        }
        
        $mobile_percentage = $total_visits > 0 ? round(($mobile_visits / $total_visits) * 100, 1) : 0;
        
        return [
            'mobile_percentage' => $mobile_percentage,
            'mobile_visits' => $mobile_visits,
            'total_visits' => $total_visits
        ];
    }
    
    /**
     * Generate SEO recommendations
     */
    private function generate_seo_recommendations($analytics) {
        $recommendations = [];
        
        // Page speed recommendations
        foreach ($analytics['page_performance'] as $page) {
            if ($page->avg_load_time > 4.0) {
                $recommendations[] = [
                    'type' => 'speed',
                    'priority' => 'high',
                    'message' => "Page '{$page->page_slug}' loads slowly ({$page->avg_load_time}s). Consider optimizing images and reducing script size."
                ];
            }
        }
        
        // Engagement recommendations
        foreach ($analytics['page_performance'] as $page) {
            if ($page->avg_time_on_page < 30) {
                $recommendations[] = [
                    'type' => 'engagement',
                    'priority' => 'medium',
                    'message' => "Low engagement on '{$page->page_slug}' ({$page->avg_time_on_page}s average). Consider improving content quality or page design."
                ];
            }
        }
        
        // Conversion recommendations
        $conversion_rate = $this->calculate_conversion_rate($analytics);
        if ($conversion_rate['rate'] < 2.0) {
            $recommendations[] = [
                'type' => 'conversion',
                'priority' => 'high',
                'message' => "Low conversion rate ({$conversion_rate['rate']}%). Consider A/B testing different call-to-action buttons or improving value propositions."
            ];
        }
        
        return $recommendations;
    }
    
    /**
     * Helper methods
     */
    private function is_stock_scanner_page() {
        global $post;
        if (!$post) return false;
        
        $stock_scanner_pages = ['dashboard', 'premium-plans', 'stock-scanner', 'watchlists', 'market-overview', 'analytics'];
        return in_array($post->post_name, $stock_scanner_pages);
    }
    
    private function get_session_id() {
        if (!session_id()) {
            session_start();
        }
        return session_id();
    }
    
    private function get_current_page_slug() {
        global $post;
        return $post ? $post->post_name : '';
    }
    
    private function detect_device_type() {
        $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        
        if (preg_match('/(tablet|ipad|playbook)|(android(?!.*(mobi|opera mini)))/i', $user_agent)) {
            return 'tablet';
        } elseif (preg_match('/(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|android|iemobile)/i', $user_agent)) {
            return 'mobile';
        } else {
            return 'desktop';
        }
    }
    
    private function find_fastest_page($pages) {
        $fastest = null;
        $min_time = PHP_FLOAT_MAX;
        
        foreach ($pages as $page) {
            if ($page->avg_load_time < $min_time) {
                $min_time = $page->avg_load_time;
                $fastest = $page;
            }
        }
        
        return $fastest;
    }
    
    private function find_slowest_page($pages) {
        $slowest = null;
        $max_time = 0;
        
        foreach ($pages as $page) {
            if ($page->avg_load_time > $max_time) {
                $max_time = $page->avg_load_time;
                $slowest = $page;
            }
        }
        
        return $slowest;
    }
}

// Initialize SEO analytics
new StockScannerSEOAnalytics();