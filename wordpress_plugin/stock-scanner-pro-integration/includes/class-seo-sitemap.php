<?php
/**
 * SEO Sitemap Generator for Stock Scanner Professional
 * 
 * Generates XML sitemaps for better search engine indexing
 */

class StockScannerSitemap {
    
    public function __construct() {
        add_action('init', [$this, 'add_rewrite_rules']);
        add_action('template_redirect', [$this, 'handle_sitemap_request']);
        add_filter('robots_txt', [$this, 'add_sitemap_to_robots'], 10, 2);
        add_action('save_post', [$this, 'maybe_ping_on_save'], 10, 1);
    }
    
    /**
     * Add rewrite rules for sitemap URLs
     */
    public function add_rewrite_rules() {
        add_rewrite_rule(
            '^stock-scanner-sitemap\.xml$',
            'index.php?stock_scanner_sitemap=main',
            'top'
        );
        
        add_rewrite_rule(
            '^stock-scanner-sitemap-pages\.xml$',
            'index.php?stock_scanner_sitemap=pages',
            'top'
        );

        add_rewrite_rule(
            '^stock-scanner-sitemap-news\.xml$',
            'index.php?stock_scanner_sitemap=news',
            'top'
        );
        
        // Register query vars
        add_filter('query_vars', function($vars) {
            $vars[] = 'stock_scanner_sitemap';
            return $vars;
        });
    }
    
    /**
     * Handle sitemap requests
     */
    public function handle_sitemap_request() {
        $sitemap_type = get_query_var('stock_scanner_sitemap');
        
        if (!$sitemap_type) {
            return;
        }
        
        header('Content-Type: application/xml; charset=utf-8');
        header('X-Robots-Tag: noindex, follow');
        
        switch ($sitemap_type) {
            case 'main':
                $this->generate_main_sitemap();
                break;
            case 'pages':
                $this->generate_pages_sitemap();
                break;
            case 'news':
                $this->generate_news_sitemap();
                break;
            default:
                status_header(404);
                exit;
        }
        
        exit;
    }
    
    /**
     * Generate main sitemap index
     */
    private function generate_main_sitemap() {
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        
        // Pages sitemap
        echo "\t<sitemap>\n";
        echo "\t\t<loc>" . home_url('/stock-scanner-sitemap-pages.xml') . "</loc>\n";
        echo "\t\t<lastmod>" . date('c') . "</lastmod>\n";
        echo "\t</sitemap>\n";

        // News sitemap
        echo "\t<sitemap>\n";
        echo "\t\t<loc>" . home_url('/stock-scanner-sitemap-news.xml') . "</loc>\n";
        echo "\t\t<lastmod>" . date('c') . "</lastmod>\n";
        echo "\t</sitemap>\n";
        
        echo '</sitemapindex>';
    }
    
    /**
     * Generate pages sitemap
     */
    private function generate_pages_sitemap() {
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' . "\n";
        
        $pages = $this->get_stock_scanner_pages();
        
        foreach ($pages as $page) {
            echo "\t<url>\n";
            echo "\t\t<loc>" . esc_url($page['url']) . "</loc>\n";
            echo "\t\t<lastmod>" . $page['lastmod'] . "</lastmod>\n";
            echo "\t\t<changefreq>" . $page['changefreq'] . "</changefreq>\n";
            echo "\t\t<priority>" . $page['priority'] . "</priority>\n";
            
            // Add images if available
            if (!empty($page['images'])) {
                foreach ($page['images'] as $image) {
                    echo "\t\t<image:image>\n";
                    echo "\t\t\t<image:loc>" . esc_url($image['url']) . "</image:loc>\n";
                    echo "\t\t\t<image:caption>" . esc_html($image['caption']) . "</image:caption>\n";
                    echo "\t\t</image:image>\n";
                }
            }
            
            echo "\t</url>\n";
        }
        
        echo '</urlset>';
    }
    
    /**
     * Get all stock scanner pages for sitemap
     */
    private function get_stock_scanner_pages() {
        $pages = [];
        
        // Main pages
        $main_pages = [
            'dashboard' => [
                'url' => home_url('/stock-scanner-dashboard/'),
                'priority' => '1.0',
                'changefreq' => 'daily'
            ],
            'premium-plans' => [
                'url' => home_url('/premium-plans/'),
                'priority' => '0.9',
                'changefreq' => 'weekly'
            ],
            'stock-scanner' => [
                'url' => home_url('/stock-scanner/'),
                'priority' => '0.9',
                'changefreq' => 'daily'
            ],
            'watchlists' => [
                'url' => home_url('/watchlists/'),
                'priority' => '0.8',
                'changefreq' => 'daily'
            ],
            'market-overview' => [
                'url' => home_url('/market-overview/'),
                'priority' => '0.8',
                'changefreq' => 'hourly'
            ],
            'analytics' => [
                'url' => home_url('/analytics/'),
                'priority' => '0.8',
                'changefreq' => 'daily'
            ]
        ];
        
        foreach ($main_pages as $slug => $page_info) {
            // Check if page exists
            $page = get_page_by_path($slug);
            if ($page) {
                $pages[] = [
                    'url' => $page_info['url'],
                    'lastmod' => date('c', strtotime($page->post_modified)),
                    'changefreq' => $page_info['changefreq'],
                    'priority' => $page_info['priority'],
                    'images' => $this->get_page_images($slug)
                ];
            } else {
                // Page doesn't exist, use default lastmod
                $pages[] = [
                    'url' => $page_info['url'],
                    'lastmod' => date('c'),
                    'changefreq' => $page_info['changefreq'],
                    'priority' => $page_info['priority'],
                    'images' => $this->get_page_images($slug)
                ];
            }
        }
        
        return $pages;
    }
    
    /**
     * Get images for a specific page
     */
    private function get_page_images($page_slug) {
        $images = [];
        $plugin_url = plugin_dir_url(dirname(__FILE__));
        
        // Common images for all pages
        $common_images = [
            [
                'url' => $plugin_url . 'assets/images/stock-scanner-dashboard.jpg',
                'caption' => 'Stock Scanner Professional Dashboard'
            ],
            [
                'url' => $plugin_url . 'assets/images/stock-scanner-logo.png',
                'caption' => 'Stock Scanner Professional Logo'
            ]
        ];
        
        // Page-specific images
        $page_images = [
            'dashboard' => [
                [
                    'url' => $plugin_url . 'assets/images/dashboard-overview.jpg',
                    'caption' => 'Professional Trading Dashboard Overview'
                ],
                [
                    'url' => $plugin_url . 'assets/images/market-status.jpg',
                    'caption' => 'Real-time Market Status Display'
                ]
            ],
            'premium-plans' => [
                [
                    'url' => $plugin_url . 'assets/images/pricing-plans.jpg',
                    'caption' => 'Stock Scanner Premium Plans Comparison'
                ],
                [
                    'url' => $plugin_url . 'assets/images/features-comparison.jpg',
                    'caption' => 'Premium Features Comparison Table'
                ]
            ],
            'stock-scanner' => [
                [
                    'url' => $plugin_url . 'assets/images/stock-scanner-interface.jpg',
                    'caption' => 'Advanced Stock Scanner Interface'
                ],
                [
                    'url' => $plugin_url . 'assets/images/technical-indicators.jpg',
                    'caption' => 'Technical Indicators and Analysis Tools'
                ]
            ],
            'watchlists' => [
                [
                    'url' => $plugin_url . 'assets/images/watchlist-management.jpg',
                    'caption' => 'Custom Watchlist Management Interface'
                ]
            ],
            'market-overview' => [
                [
                    'url' => $plugin_url . 'assets/images/market-overview.jpg',
                    'caption' => 'Live Market Overview Dashboard'
                ]
            ],
            'analytics' => [
                [
                    'url' => $plugin_url . 'assets/images/ai-analytics.jpg',
                    'caption' => 'AI-Powered Stock Analytics and Insights'
                ]
            ]
        ];
        
        // Combine common and page-specific images
        $images = array_merge($common_images, $page_images[$page_slug] ?? []);
        
        return $images;
    }
    
    /**
     * Add sitemap reference to robots.txt
     */
    public function add_sitemap_to_robots($output, $public) {
        if ($public) {
            $output .= "\n# Stock Scanner Professional Sitemaps\n";
            $output .= "Sitemap: " . home_url('/stock-scanner-sitemap.xml') . "\n";
        }
        
        return $output;
    }
    
    /**
     * Ping search engines about sitemap updates
     */
    public function ping_search_engines() {
        $sitemap_url = urlencode(home_url('/stock-scanner-sitemap.xml'));
        
        $ping_urls = [
            'google' => "https://www.google.com/ping?sitemap={$sitemap_url}",
            'bing' => "https://www.bing.com/ping?sitemap={$sitemap_url}",
        ];
        
        foreach ($ping_urls as $engine => $url) {
            wp_remote_get($url, [
                'timeout' => 5,
                'blocking' => false
            ]);
        }
    }

    // Ping engines when plugin pages update
    public function maybe_ping_on_save($post_id) {
        if (get_post_type($post_id) !== 'page') { return; }
        if (get_post_meta($post_id, 'stock_scanner_page', true)) {
            $this->ping_search_engines();
        }
    }
    
    /**
     * Generate News Sitemap for time-sensitive content
     */
    public function generate_news_sitemap() {
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">' . "\n";
        
        // Add market overview as news content (updates frequently)
        echo "\t<url>\n";
        echo "\t\t<loc>" . home_url('/market-overview/') . "</loc>\n";
        echo "\t\t<news:news>\n";
        echo "\t\t\t<news:publication>\n";
        echo "\t\t\t\t<news:name>Stock Scanner Professional</news:name>\n";
        echo "\t\t\t\t<news:language>en</news:language>\n";
        echo "\t\t\t</news:publication>\n";
        echo "\t\t\t<news:publication_date>" . date('c') . "</news:publication_date>\n";
        echo "\t\t\t<news:title>Live Stock Market Overview and Analysis</news:title>\n";
        echo "\t\t\t<news:keywords>stock market, market analysis, real-time data, trading</news:keywords>\n";
        echo "\t\t</news:news>\n";
        echo "\t</url>\n";
        
        echo '</urlset>';
    }
}
 
// Initialize sitemap generator
new StockScannerSitemap();