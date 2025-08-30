<?php
/**
 * SEO Optimizations for Production
 * @package RetailTradeScanner
 */

if (!defined('ABSPATH')) { exit; }

/**
 * SEO optimization class
 */
class RTS_SEO {
    
    public function __construct() {
        add_action('wp_head', [$this, 'add_meta_tags'], 1);
        add_action('wp_head', [$this, 'add_schema_markup'], 5);
        add_action('wp_head', [$this, 'add_social_meta_tags'], 6);
        add_filter('document_title_parts', [$this, 'optimize_title']);
        add_filter('wp_title', [$this, 'optimize_wp_title'], 10, 2);
        add_action('wp_head', [$this, 'add_canonical_url']);
        add_action('wp_footer', [$this, 'add_analytics']);
        add_filter('the_content', [$this, 'optimize_content_seo']);
    }
    
    /**
     * Add essential meta tags
     */
    public function add_meta_tags() {
        // Viewport meta tag
        echo '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' . "\n";
        
        // Theme color for mobile browsers
        echo '<meta name="theme-color" content="#433e0e">' . "\n";
        echo '<meta name="msapplication-TileColor" content="#433e0e">' . "\n";
        
        // Description meta tag
        $description = $this->get_meta_description();
        if ($description) {
            echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
        }
        
        // Keywords meta tag (still used by some search engines)
        $keywords = $this->get_meta_keywords();
        if ($keywords) {
            echo '<meta name="keywords" content="' . esc_attr($keywords) . '">' . "\n";
        }
        
        // Author meta tag
        if (is_single()) {
            $author = get_the_author();
            echo '<meta name="author" content="' . esc_attr($author) . '">' . "\n";
        }
        
        // Robots meta tag
        $robots = $this->get_robots_meta();
        echo '<meta name="robots" content="' . esc_attr($robots) . '">' . "\n";
        
        // Canonical URL
        echo '<link rel="canonical" href="' . esc_url($this->get_canonical_url()) . '">' . "\n";
        
        // Hreflang for international SEO (if applicable)
        $this->add_hreflang_tags();
    }
    
    /**
     * Add Schema.org structured data
     */
    public function add_schema_markup() {
        $schema = [];
        
        if (is_single()) {
            $schema = $this->get_article_schema();
        } elseif (is_page()) {
            $schema = $this->get_webpage_schema();
        } elseif (is_home() || is_front_page()) {
            $schema = $this->get_website_schema();
        } elseif (is_archive()) {
            $schema = $this->get_collection_schema();
        }
        
        if (!empty($schema)) {
            echo '<script type="application/ld+json">' . "\n";
            echo wp_json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
            echo "\n" . '</script>' . "\n";
        }
    }
    
    /**
     * Add social media meta tags (Open Graph, Twitter Cards)
     */
    public function add_social_meta_tags() {
        // Open Graph meta tags
        echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr($this->get_og_title()) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($this->get_meta_description()) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url($this->get_canonical_url()) . '">' . "\n";
        echo '<meta property="og:type" content="' . esc_attr($this->get_og_type()) . '">' . "\n";
        echo '<meta property="og:locale" content="' . esc_attr(get_locale()) . '">' . "\n";
        
        // Open Graph image
        $og_image = $this->get_og_image();
        if ($og_image) {
            echo '<meta property="og:image" content="' . esc_url($og_image['url']) . '">' . "\n";
            echo '<meta property="og:image:width" content="' . esc_attr($og_image['width']) . '">' . "\n";
            echo '<meta property="og:image:height" content="' . esc_attr($og_image['height']) . '">' . "\n";
            echo '<meta property="og:image:alt" content="' . esc_attr($og_image['alt']) . '">' . "\n";
        }
        
        // Twitter Card meta tags
        echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
        echo '<meta name="twitter:title" content="' . esc_attr($this->get_og_title()) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr($this->get_meta_description()) . '">' . "\n";
        
        if ($og_image) {
            echo '<meta name="twitter:image" content="' . esc_url($og_image['url']) . '">' . "\n";
        }
        
        // Twitter site handle (if configured)
        $twitter_site = get_option('rts_twitter_handle');
        if ($twitter_site) {
            echo '<meta name="twitter:site" content="@' . esc_attr($twitter_site) . '">' . "\n";
        }
    }
    
    /**
     * Optimize page titles
     */
    public function optimize_title($title_parts) {
        $site_name = get_bloginfo('name');
        $tagline = get_bloginfo('description');
        
        if (is_front_page()) {
            $title_parts['title'] = $site_name;
            if ($tagline) {
                $title_parts['tagline'] = $tagline;
            }
        } elseif (is_single() || is_page()) {
            $title_parts['title'] = get_the_title();
        } elseif (is_category()) {
            $title_parts['title'] = single_cat_title('', false) . ' Archives';
        } elseif (is_tag()) {
            $title_parts['title'] = single_tag_title('', false) . ' Archives';
        } elseif (is_archive()) {
            $title_parts['title'] = get_the_archive_title();
        } elseif (is_search()) {
            $title_parts['title'] = 'Search Results for: ' . get_search_query();
        } elseif (is_404()) {
            $title_parts['title'] = 'Page Not Found';
        }
        
        return $title_parts;
    }
    
    /**
     * Optimize wp_title for older themes
     */
    public function optimize_wp_title($title, $sep) {
        if (is_feed()) {
            return $title;
        }
        
        global $page, $paged;
        
        $title .= get_bloginfo('name', 'display');
        
        $site_description = get_bloginfo('description', 'display');
        if ($site_description && (is_home() || is_front_page())) {
            $title .= " $sep $site_description";
        }
        
        if (($paged >= 2 || $page >= 2) && !is_404()) {
            $title .= " $sep " . sprintf(__('Page %s', 'retail-trade-scanner'), max($paged, $page));
        }
        
        return $title;
    }
    
    /**
     * Add canonical URL
     */
    public function add_canonical_url() {
        // WordPress handles this automatically, but we can customize it
        $canonical = $this->get_canonical_url();
        remove_action('wp_head', 'rel_canonical');
        echo '<link rel="canonical" href="' . esc_url($canonical) . '">' . "\n";
    }
    
    /**
     * Add Google Analytics and other tracking
     */
    public function add_analytics() {
        $ga_id = get_option('rts_google_analytics_id');
        
        if ($ga_id && !is_admin() && !current_user_can('administrator')) {
            ?>
            <!-- Global site tag (gtag.js) - Google Analytics -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=<?php echo esc_attr($ga_id); ?>"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '<?php echo esc_attr($ga_id); ?>', {
                anonymize_ip: true,
                allow_google_signals: false,
                allow_ad_personalization_signals: false
              });
            </script>
            <?php
        }
    }
    
    /**
     * Optimize content for SEO
     */
    public function optimize_content_seo($content) {
        if (is_singular()) {
            // Add reading time schema
            $reading_time = $this->calculate_reading_time($content);
            $content = '<div itemscope itemtype="http://schema.org/Article">' . 
                      '<meta itemprop="timeRequired" content="PT' . $reading_time . 'M">' . 
                      $content . '</div>';
        }
        
        return $content;
    }
    
    /**
     * Get meta description
     */
    private function get_meta_description() {
        $description = '';
        
        if (is_single() || is_page()) {
            $excerpt = get_the_excerpt();
            $description = $excerpt ? wp_trim_words($excerpt, 25) : '';
        } elseif (is_category()) {
            $description = category_description();
        } elseif (is_tag()) {
            $description = tag_description();
        } elseif (is_archive()) {
            $description = get_the_archive_description();
        } elseif (is_home() || is_front_page()) {
            $description = get_bloginfo('description');
        }
        
        return wp_strip_all_tags($description);
    }
    
    /**
     * Get meta keywords
     */
    private function get_meta_keywords() {
        $keywords = [];
        
        if (is_single()) {
            $tags = get_the_tags();
            if ($tags) {
                foreach ($tags as $tag) {
                    $keywords[] = $tag->name;
                }
            }
            
            $categories = get_the_category();
            if ($categories) {
                foreach ($categories as $category) {
                    $keywords[] = $category->name;
                }
            }
        }
        
        // Add site-wide keywords
        $site_keywords = get_option('rts_site_keywords', 'stock trading, market analysis, portfolio tracking');
        if ($site_keywords) {
            $keywords = array_merge($keywords, explode(',', $site_keywords));
        }
        
        return implode(', ', array_unique($keywords));
    }
    
    /**
     * Get robots meta tag content
     */
    private function get_robots_meta() {
        if (is_search() || is_404()) {
            return 'noindex, nofollow';
        }
        
        if (is_archive() && !is_category() && !is_tag()) {
            return 'noindex, follow';
        }
        
        return 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1';
    }
    
    /**
     * Get canonical URL
     */
    private function get_canonical_url() {
        global $wp;
        
        if (is_front_page()) {
            return home_url('/');
        }
        
        return home_url(add_query_arg([], $wp->request));
    }
    
    /**
     * Get Open Graph title
     */
    private function get_og_title() {
        if (is_single() || is_page()) {
            return get_the_title();
        } elseif (is_front_page()) {
            return get_bloginfo('name') . ' - ' . get_bloginfo('description');
        } else {
            return wp_get_document_title();
        }
    }
    
    /**
     * Get Open Graph type
     */
    private function get_og_type() {
        if (is_single()) {
            return 'article';
        } elseif (is_front_page()) {
            return 'website';
        } else {
            return 'webpage';
        }
    }
    
    /**
     * Get Open Graph image
     */
    private function get_og_image() {
        $image = null;
        
        if (is_single() && has_post_thumbnail()) {
            $image_id = get_post_thumbnail_id();
            $image_data = wp_get_attachment_image_src($image_id, 'large');
            
            if ($image_data) {
                $image = [
                    'url' => $image_data[0],
                    'width' => $image_data[1],
                    'height' => $image_data[2],
                    'alt' => get_post_meta($image_id, '_wp_attachment_image_alt', true)
                ];
            }
        }
        
        // Fallback to site logo or default image
        if (!$image) {
            $default_image = get_option('rts_default_og_image');
            if ($default_image) {
                $image = [
                    'url' => $default_image,
                    'width' => 1200,
                    'height' => 630,
                    'alt' => get_bloginfo('name') . ' Logo'
                ];
            }
        }
        
        return $image;
    }
    
    /**
     * Get article schema
     */
    private function get_article_schema() {
        if (!is_single()) return [];
        
        global $post;
        
        return [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'description' => get_the_excerpt(),
            'author' => [
                '@type' => 'Person',
                'name' => get_the_author(),
                'url' => get_author_posts_url(get_the_author_meta('ID'))
            ],
            'publisher' => [
                '@type' => 'Organization',
                'name' => get_bloginfo('name'),
                'logo' => [
                    '@type' => 'ImageObject',
                    'url' => get_site_icon_url()
                ]
            ],
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'mainEntityOfPage' => [
                '@type' => 'WebPage',
                '@id' => get_permalink()
            ],
            'image' => $this->get_og_image()['url'] ?? get_site_icon_url(),
            'wordCount' => str_word_count(strip_tags(get_the_content())),
            'timeRequired' => 'PT' . $this->calculate_reading_time(get_the_content()) . 'M'
        ];
    }
    
    /**
     * Get website schema
     */
    private function get_website_schema() {
        return [
            '@context' => 'https://schema.org',
            '@type' => 'WebSite',
            'name' => get_bloginfo('name'),
            'description' => get_bloginfo('description'),
            'url' => home_url(),
            'potentialAction' => [
                '@type' => 'SearchAction',
                'target' => home_url('/?s={search_term_string}'),
                'query-input' => 'required name=search_term_string'
            ]
        ];
    }
    
    /**
     * Get webpage schema
     */
    private function get_webpage_schema() {
        return [
            '@context' => 'https://schema.org',
            '@type' => 'WebPage',
            'name' => get_the_title(),
            'description' => get_the_excerpt(),
            'url' => get_permalink(),
            'isPartOf' => [
                '@type' => 'WebSite',
                'name' => get_bloginfo('name'),
                'url' => home_url()
            ]
        ];
    }
    
    /**
     * Get collection schema for archives
     */
    private function get_collection_schema() {
        return [
            '@context' => 'https://schema.org',
            '@type' => 'CollectionPage',
            'name' => get_the_archive_title(),
            'description' => get_the_archive_description(),
            'url' => home_url(add_query_arg([], $_SERVER['REQUEST_URI']))
        ];
    }
    
    /**
     * Add hreflang tags for international SEO
     */
    private function add_hreflang_tags() {
        // This would be implemented if you have multiple language versions
        $languages = get_option('rts_hreflang_languages', []);
        
        foreach ($languages as $lang => $url) {
            echo '<link rel="alternate" hreflang="' . esc_attr($lang) . '" href="' . esc_url($url) . '">' . "\n";
        }
    }
    
    /**
     * Calculate reading time
     */
    private function calculate_reading_time($content) {
        $word_count = str_word_count(strip_tags($content));
        return ceil($word_count / 200); // 200 words per minute average
    }
}

// Initialize SEO
new RTS_SEO();

/**
 * XML Sitemap generation helper
 */
function rts_generate_sitemap() {
    if (!current_user_can('administrator')) {
        return;
    }
    
    $sitemap = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
    $sitemap .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
    
    // Homepage
    $sitemap .= '<url><loc>' . home_url() . '</loc><changefreq>daily</changefreq><priority>1.0</priority></url>' . "\n";
    
    // Pages
    $pages = get_pages();
    foreach ($pages as $page) {
        $sitemap .= '<url><loc>' . get_permalink($page->ID) . '</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>' . "\n";
    }
    
    // Posts
    $posts = get_posts(['numberposts' => -1]);
    foreach ($posts as $post) {
        $sitemap .= '<url><loc>' . get_permalink($post->ID) . '</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>' . "\n";
    }
    
    $sitemap .= '</urlset>';
    
    file_put_contents(ABSPATH . 'sitemap.xml', $sitemap);
}

// Generate sitemap on content update
add_action('save_post', 'rts_generate_sitemap');
add_action('after_switch_theme', 'rts_generate_sitemap');