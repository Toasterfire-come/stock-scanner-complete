<?php
/**
 * SEO Optimizer for Stock Scanner Professional
 *
 * Outputs canonical tags, meta descriptions, OpenGraph/Twitter tags,
 * and JSON-LD structured data optimized for AI ranking on plugin pages.
 */

if (!defined('ABSPATH')) {
    exit;
}

if (!class_exists('StockScannerSEOOptimizer')) {
    class StockScannerSEOOptimizer {
        private $enabled;

        public function __construct() {
            // Allow disabling via option
            $this->enabled = apply_filters('stock_scanner_seo_enabled', get_option('stock_scanner_seo_enabled', 'yes') === 'yes');

            if (!$this->enabled) {
                return;
            }

            // If a major SEO plugin is active, do not duplicate
            if ($this->is_seo_plugin_active()) {
                return;
            }

            add_action('wp_head', [$this, 'render_meta_tags'], 1);
            add_filter('pre_get_document_title', [$this, 'filter_document_title'], 10);
        }

        private function is_seo_plugin_active() {
            // Yoast or Rank Math present
            return defined('WPSEO_VERSION') || defined('RANK_MATH_VERSION');
        }

        private function is_plugin_page(): bool {
            global $post;
            return $post && (bool) get_post_meta($post->ID, 'stock_scanner_page', true);
        }

        public function filter_document_title($title) {
            if (!$this->is_plugin_page()) {
                return $title;
            }

            $parts = $this->get_page_meta();
            if (!empty($parts['title'])) {
                return $parts['title'];
            }
            return $title;
        }

        public function render_meta_tags() {
            if (!is_singular() && !is_front_page() && !is_home() && !$this->is_plugin_page()) {
                return;
            }

            $meta = $this->get_page_meta();

            // Canonical
            $canonical = function_exists('wp_get_canonical_url') ? wp_get_canonical_url() : '';
            if (!$canonical) {
                $canonical = is_singular() ? get_permalink() : home_url(add_query_arg([], $GLOBALS['wp']->request ?? ''));
            }
            echo '<link rel="canonical" href="' . esc_url($canonical) . '" />' . "\n";

            // Meta description
            if (!empty($meta['description'])) {
                echo '<meta name="description" content="' . esc_attr($meta['description']) . '" />' . "\n";
            }

            // OpenGraph
            echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '" />' . "\n";
            echo '<meta property="og:locale" content="' . esc_attr(get_locale()) . '" />' . "\n";
            echo '<meta property="og:type" content="' . ($this->is_plugin_page() ? 'article' : 'website') . '" />' . "\n";
            echo '<meta property="og:url" content="' . esc_url($canonical) . '" />' . "\n";
            if (!empty($meta['title'])) {
                echo '<meta property="og:title" content="' . esc_attr($meta['title']) . '" />' . "\n";
            }
            if (!empty($meta['description'])) {
                echo '<meta property="og:description" content="' . esc_attr($meta['description']) . '" />' . "\n";
            }
            if (!empty($meta['image'])) {
                echo '<meta property="og:image" content="' . esc_url($meta['image']) . '" />' . "\n";
            }

            // Twitter
            echo '<meta name="twitter:card" content="summary_large_image" />' . "\n";
            if (!empty($meta['title'])) {
                echo '<meta name="twitter:title" content="' . esc_attr($meta['title']) . '" />' . "\n";
            }
            if (!empty($meta['description'])) {
                echo '<meta name="twitter:description" content="' . esc_attr($meta['description']) . '" />' . "\n";
            }
            if (!empty($meta['image'])) {
                echo '<meta name="twitter:image" content="' . esc_url($meta['image']) . '" />' . "\n";
            }

            // JSON-LD
            $schemas = $this->build_json_ld($meta, $canonical);
            foreach ($schemas as $schema) {
                echo '<script type="application/ld+json">' . wp_json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
            }
        }

        private function get_page_meta(): array {
            global $post;
            $site_name = get_bloginfo('name');
            $default_desc = get_bloginfo('description');
            $title = $site_name;
            $description = $default_desc ?: 'Professional stock scanner with real-time market data and advanced analysis tools';

            // Prefer post-specific
            if ($post) {
                $custom_title = get_post_meta($post->ID, 'stock_scanner_meta_title', true);
                $custom_desc = get_post_meta($post->ID, 'stock_scanner_meta_description', true);
                if ($custom_title) { $title = $custom_title; }
                if ($custom_desc) { $description = $custom_desc; }

                // Sensible defaults by slug
                $slug = $post->post_name;
                switch ($slug) {
                    case 'stock-scanner-dashboard':
                        $title = $custom_title ?: ($site_name . ' Dashboard');
                        $description = $custom_desc ?: 'Your personalized stock scanner dashboard with live market insights.';
                        break;
                    case 'premium-plans':
                        $title = $custom_title ?: ($site_name . ' Premium Plans');
                        $description = $custom_desc ?: 'Compare Stock Scanner Professional pricing and features. Upgrade to unlock AI analytics and real-time scanning.';
                        break;
                    case 'stock-scanner':
                        $title = $custom_title ?: 'Stock Scanner – Real-time Screener and Analysis';
                        $description = $custom_desc ?: 'Scan and analyze stocks with advanced filters, indicators, and AI insights.';
                        break;
                    case 'watchlists':
                        $title = $custom_title ?: 'Watchlists – Track Stocks and Alerts';
                        $description = $custom_desc ?: 'Create and manage custom stock watchlists with alerts and performance tracking.';
                        break;
                    case 'market-overview':
                        $title = $custom_title ?: 'Market Overview – Live Indices, Sectors, News';
                        $description = $custom_desc ?: 'Live market overview with indices, sector performance, and trending tickers.';
                        break;
                    case 'analytics':
                        $title = $custom_title ?: 'AI-Powered Analytics';
                        $description = $custom_desc ?: 'Deeper insights powered by AI for portfolios, watchlists, and market trends.';
                        break;
                }
            }

            // Image: prefer site icon
            $image = get_site_icon_url(512);
            if (!$image) {
                // Fallback: theme screenshot or homepage
                $image = get_theme_file_uri('screenshot.png');
                if (!$image) {
                    $image = home_url('/');
                }
            }

            return [
                'title' => $title,
                'description' => $description,
                'image' => $image,
            ];
        }

        private function build_json_ld(array $meta, string $canonical): array {
            $schemas = [];

            // Organization
            $schemas[] = [
                '@context' => 'https://schema.org',
                '@type' => 'Organization',
                'name' => get_bloginfo('name'),
                'url' => home_url('/'),
                'logo' => get_site_icon_url(512) ?: '',
                'sameAs' => array_values(array_filter([
                    get_theme_mod('twitter_url'),
                    get_theme_mod('facebook_url'),
                    get_theme_mod('linkedin_url'),
                ]))
            ];

            // WebSite + SearchAction
            $schemas[] = [
                '@context' => 'https://schema.org',
                '@type' => 'WebSite',
                'url' => home_url('/'),
                'name' => get_bloginfo('name'),
                'potentialAction' => [
                    '@type' => 'SearchAction',
                    'target' => home_url('/?s={search_term_string}'),
                    'query-input' => 'required name=search_term_string'
                ]
            ];

            // Breadcrumbs for plugin pages
            if ($this->is_plugin_page()) {
                global $post;
                $schemas[] = [
                    '@context' => 'https://schema.org',
                    '@type' => 'BreadcrumbList',
                    'itemListElement' => [
                        [
                            '@type' => 'ListItem',
                            'position' => 1,
                            'name' => 'Home',
                            'item' => home_url('/')
                        ],
                        [
                            '@type' => 'ListItem',
                            'position' => 2,
                            'name' => wp_strip_all_tags(get_the_title($post)),
                            'item' => $canonical
                        ]
                    ]
                ];

                // WebPage
                $schemas[] = [
                    '@context' => 'https://schema.org',
                    '@type' => 'WebPage',
                    'name' => $meta['title'],
                    'url' => $canonical,
                    'inLanguage' => get_locale(),
                    'description' => $meta['description'],
                    'datePublished' => get_the_date('c', $post),
                    'dateModified' => get_the_modified_date('c', $post)
                ];

                // SoftwareApplication signaling SaaS
                $schemas[] = [
                    '@context' => 'https://schema.org',
                    '@type' => 'SoftwareApplication',
                    'name' => 'Stock Scanner Professional',
                    'applicationCategory' => 'BusinessApplication',
                    'operatingSystem' => 'Web',
                    'offers' => [
                        '@type' => 'Offer',
                        'url' => home_url('/premium-plans/'),
                        'priceCurrency' => get_woocommerce_currency() ?: 'USD',
                        'availability' => 'https://schema.org/InStock'
                    ]
                ];
            }

            return $schemas;
        }
    }
}

// Initialize
new StockScannerSEOOptimizer();