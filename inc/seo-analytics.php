<?php
/**
 * Production SEO & Analytics Features
 * Advanced SEO optimization and analytics integration
 */
if (!defined('ABSPATH')) { exit; }

/**
 * SEO & Analytics Class
 */
class RTS_SEO_Analytics {
    
    private $structured_data = array();
    
    public function __construct() {
        add_action('wp_head', array($this, 'add_meta_tags'), 1);
        add_action('wp_head', array($this, 'add_open_graph_tags'), 5);
        add_action('wp_head', array($this, 'add_twitter_cards'), 6);
        add_action('wp_head', array($this, 'add_structured_data'), 7);
        add_action('wp_head', array($this, 'add_canonical_url'), 8);
        add_action('wp_footer', array($this, 'add_analytics_code'), 5);
        
        // Sitemap generation
        add_action('init', array($this, 'init_sitemap'));
        add_action('wp_loaded', array($this, 'generate_sitemap'));
        
        // Schema markup
        add_action('wp_head', array($this, 'add_organization_schema'));
        add_filter('the_content', array($this, 'add_article_schema'));
        
        // SEO-friendly URLs
        add_filter('post_link', array($this, 'optimize_permalink_structure'), 10, 3);
        
        // Page speed insights
        add_action('wp_footer', array($this, 'add_performance_monitoring'));
    }
    
    /**
     * Add essential meta tags
     */
    public function add_meta_tags() {
        // Viewport meta tag
        echo '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' . "\n";
        
        // Theme color for browsers
        echo '<meta name="theme-color" content="#374a67">' . "\n";
        echo '<meta name="msapplication-TileColor" content="#374a67">' . "\n";
        
        // SEO meta tags
        $description = $this->get_meta_description();
        $keywords = $this->get_meta_keywords();
        
        if ($description) {
            echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
        }
        
        if ($keywords) {
            echo '<meta name="keywords" content="' . esc_attr($keywords) . '">' . "\n";
        }
        
        // Robots meta tag
        $robots = $this->get_robots_meta();
        if ($robots) {
            echo '<meta name="robots" content="' . esc_attr($robots) . '">' . "\n";
        }
        
        // Author meta tag
        if (is_single()) {
            $author = get_the_author();
            if ($author) {
                echo '<meta name="author" content="' . esc_attr($author) . '">' . "\n";
            }
        }
        
        // Language meta tag
        $language = get_locale();
        echo '<meta name="language" content="' . esc_attr($language) . '">' . "\n";
        
        // Generator meta tag (custom)
        echo '<meta name="generator" content="Retail Trade Scanner Theme v2.0.0">' . "\n";
    }
    
    /**
     * Get meta description
     */
    private function get_meta_description() {
        if (is_singular()) {
            $post = get_queried_object();
            if ($post->post_excerpt) {
                return wp_strip_all_tags($post->post_excerpt);
            } elseif ($post->post_content) {
                return wp_trim_words(wp_strip_all_tags($post->post_content), 30, '...');
            }
        } elseif (is_category() || is_tag() || is_tax()) {
            $term = get_queried_object();
            if ($term->description) {
                return wp_strip_all_tags($term->description);
            }
        } elseif (is_author()) {
            $author = get_queried_object();
            return sprintf(__('Posts by %s - Professional stock trading insights and market analysis.', 'retail-trade-scanner'), $author->display_name);
        } elseif (is_home() || is_front_page()) {
            return get_bloginfo('description') ?: __('Professional stock trading platform with advanced market analysis tools, real-time scanning, and portfolio management for retail investors.', 'retail-trade-scanner');
        }
        
        return get_bloginfo('description');
    }
    
    /**
     * Get meta keywords
     */
    private function get_meta_keywords() {
        $keywords = array();
        
        if (is_singular()) {
            $post_tags = get_the_tags();
            if ($post_tags) {
                foreach ($post_tags as $tag) {
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
        
        // Add default keywords
        $default_keywords = array(
            'stock trading',
            'market analysis',
            'portfolio management',
            'investment tools',
            'stock scanner',
            'trading platform',
            'financial technology'
        );
        
        $keywords = array_merge($keywords, $default_keywords);
        $keywords = array_unique($keywords);
        
        return implode(', ', array_slice($keywords, 0, 10));
    }
    
    /**
     * Get robots meta content
     */
    private function get_robots_meta() {
        if (is_admin() || is_preview() || is_search()) {
            return 'noindex, nofollow';
        }
        
        if (is_404()) {
            return 'noindex, nofollow';
        }
        
        if (is_attachment()) {
            return 'noindex, follow';
        }
        
        return 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1';
    }
    
    /**
     * Add Open Graph tags
     */
    public function add_open_graph_tags() {
        $og_title = $this->get_og_title();
        $og_description = $this->get_meta_description();
        $og_url = $this->get_canonical_url();
        $og_image = $this->get_og_image();
        $og_type = $this->get_og_type();
        
        echo '<meta property="og:title" content="' . esc_attr($og_title) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($og_description) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url($og_url) . '">' . "\n";
        echo '<meta property="og:type" content="' . esc_attr($og_type) . '">' . "\n";
        echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        echo '<meta property="og:locale" content="' . esc_attr(str_replace('-', '_', get_locale())) . '">' . "\n";
        
        if ($og_image) {
            echo '<meta property="og:image" content="' . esc_url($og_image['url']) . '">' . "\n";
            if (isset($og_image['width'])) {
                echo '<meta property="og:image:width" content="' . esc_attr($og_image['width']) . '">' . "\n";
            }
            if (isset($og_image['height'])) {
                echo '<meta property="og:image:height" content="' . esc_attr($og_image['height']) . '">' . "\n";
            }
            echo '<meta property="og:image:alt" content="' . esc_attr($og_title) . '">' . "\n";
        }
        
        // Article specific tags
        if (is_single() && $og_type === 'article') {
            $published_time = get_the_date('c');
            $modified_time = get_the_modified_date('c');
            $author = get_the_author();
            
            echo '<meta property="article:published_time" content="' . esc_attr($published_time) . '">' . "\n";
            echo '<meta property="article:modified_time" content="' . esc_attr($modified_time) . '">' . "\n";
            echo '<meta property="article:author" content="' . esc_attr($author) . '">' . "\n";
            
            $categories = get_the_category();
            if ($categories) {
                foreach ($categories as $category) {
                    echo '<meta property="article:section" content="' . esc_attr($category->name) . '">' . "\n";
                }
            }
            
            $tags = get_the_tags();
            if ($tags) {
                foreach ($tags as $tag) {
                    echo '<meta property="article:tag" content="' . esc_attr($tag->name) . '">' . "\n";
                }
            }
        }
    }
    
    /**
     * Add Twitter Cards
     */
    public function add_twitter_cards() {
        $twitter_card = 'summary_large_image';
        $twitter_title = $this->get_og_title();
        $twitter_description = $this->get_meta_description();
        $twitter_image = $this->get_og_image();
        
        echo '<meta name="twitter:card" content="' . esc_attr($twitter_card) . '">' . "\n";
        echo '<meta name="twitter:title" content="' . esc_attr($twitter_title) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr($twitter_description) . '">' . "\n";
        
        if ($twitter_image) {
            echo '<meta name="twitter:image" content="' . esc_url($twitter_image['url']) . '">' . "\n";
            echo '<meta name="twitter:image:alt" content="' . esc_attr($twitter_title) . '">' . "\n";
        }
        
        // Twitter site handle (can be configured)
        $twitter_site = get_theme_mod('rts_twitter_handle', '');
        if ($twitter_site) {
            echo '<meta name="twitter:site" content="@' . esc_attr(ltrim($twitter_site, '@')) . '">' . "\n";
        }
        
        if (is_single()) {
            $author_twitter = get_the_author_meta('twitter');
            if ($author_twitter) {
                echo '<meta name="twitter:creator" content="@' . esc_attr(ltrim($author_twitter, '@')) . '">' . "\n";
            }
        }
    }
    
    /**
     * Get Open Graph title
     */
    private function get_og_title() {
        if (is_singular()) {
            return get_the_title();
        } elseif (is_category() || is_tag() || is_tax()) {
            return single_term_title('', false);
        } elseif (is_author()) {
            return get_the_author();
        } elseif (is_home() || is_front_page()) {
            return get_bloginfo('name');
        }
        
        return wp_get_document_title();
    }
    
    /**
     * Get Open Graph type
     */
    private function get_og_type() {
        if (is_single()) {
            return 'article';
        } elseif (is_author()) {
            return 'profile';
        }
        
        return 'website';
    }
    
    /**
     * Get Open Graph image
     */
    private function get_og_image() {
        $image = null;
        
        if (is_singular() && has_post_thumbnail()) {
            $thumbnail_id = get_post_thumbnail_id();
            $image_data = wp_get_attachment_image_src($thumbnail_id, 'large');
            
            if ($image_data) {
                $image = array(
                    'url' => $image_data[0],
                    'width' => $image_data[1],
                    'height' => $image_data[2]
                );
            }
        }
        
        // Fallback to site logo or default image
        if (!$image) {
            $logo_id = get_theme_mod('custom_logo');
            if ($logo_id) {
                $logo_data = wp_get_attachment_image_src($logo_id, 'full');
                if ($logo_data) {
                    $image = array(
                        'url' => $logo_data[0],
                        'width' => $logo_data[1],
                        'height' => $logo_data[2]
                    );
                }
            }
        }
        
        // Default fallback image
        if (!$image) {
            $image = array(
                'url' => get_template_directory_uri() . '/assets/images/default-social.jpg',
                'width' => 1200,
                'height' => 630
            );
        }
        
        return $image;
    }
    
    /**
     * Add canonical URL
     */
    public function add_canonical_url() {
        $canonical_url = $this->get_canonical_url();
        echo '<link rel="canonical" href="' . esc_url($canonical_url) . '">' . "\n";
        
        // Add hreflang for multilingual sites
        $this->add_hreflang_tags();
    }
    
    /**
     * Get canonical URL
     */
    private function get_canonical_url() {
        if (is_singular()) {
            return get_permalink();
        } elseif (is_category() || is_tag() || is_tax()) {
            return get_term_link(get_queried_object());
        } elseif (is_author()) {
            return get_author_posts_url(get_queried_object_id());
        } elseif (is_home()) {
            return home_url('/');
        }
        
        return home_url(add_query_arg(array(), ''));
    }
    
    /**
     * Add hreflang tags
     */
    private function add_hreflang_tags() {
        // This would be expanded for multilingual sites
        $locale = get_locale();
        $lang = substr($locale, 0, 2);
        
        echo '<link rel="alternate" hreflang="' . esc_attr($lang) . '" href="' . esc_url($this->get_canonical_url()) . '">' . "\n";
        echo '<link rel="alternate" hreflang="x-default" href="' . esc_url($this->get_canonical_url()) . '">' . "\n";
    }
    
    /**
     * Add structured data
     */
    public function add_structured_data() {
        $structured_data = array();
        
        // Breadcrumb schema
        if (!is_front_page()) {
            $structured_data[] = $this->get_breadcrumb_schema();
        }
        
        // Page/Post specific schema
        if (is_singular()) {
            $structured_data[] = $this->get_article_schema();
        }
        
        // Output structured data
        if (!empty($structured_data)) {
            echo '<script type="application/ld+json">' . wp_json_encode($structured_data) . '</script>' . "\n";
        }
    }
    
    /**
     * Get breadcrumb schema
     */
    private function get_breadcrumb_schema() {
        $breadcrumbs = array(
            '@context' => 'https://schema.org',
            '@type' => 'BreadcrumbList',
            'itemListElement' => array()
        );
        
        // Home
        $breadcrumbs['itemListElement'][] = array(
            '@type' => 'ListItem',
            'position' => 1,
            'name' => get_bloginfo('name'),
            'item' => home_url('/')
        );
        
        $position = 2;
        
        if (is_category() || is_tag() || is_tax()) {
            $term = get_queried_object();
            $breadcrumbs['itemListElement'][] = array(
                '@type' => 'ListItem',
                'position' => $position,
                'name' => $term->name,
                'item' => get_term_link($term)
            );
        } elseif (is_singular()) {
            $post = get_queried_object();
            
            // Add categories for posts
            if (is_single()) {
                $categories = get_the_category($post->ID);
                if ($categories) {
                    $category = $categories[0];
                    $breadcrumbs['itemListElement'][] = array(
                        '@type' => 'ListItem',
                        'position' => $position++,
                        'name' => $category->name,
                        'item' => get_category_link($category->term_id)
                    );
                }
            }
            
            $breadcrumbs['itemListElement'][] = array(
                '@type' => 'ListItem',
                'position' => $position,
                'name' => get_the_title($post->ID),
                'item' => get_permalink($post->ID)
            );
        }
        
        return $breadcrumbs;
    }
    
    /**
     * Get article schema
     */
    private function get_article_schema() {
        if (!is_singular()) {
            return null;
        }
        
        $post = get_queried_object();
        $author = get_userdata($post->post_author);
        
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title($post->ID),
            'author' => array(
                '@type' => 'Person',
                'name' => $author->display_name,
                'url' => get_author_posts_url($author->ID)
            ),
            'publisher' => array(
                '@type' => 'Organization',
                'name' => get_bloginfo('name'),
                'url' => home_url('/'),
                'logo' => array(
                    '@type' => 'ImageObject',
                    'url' => $this->get_organization_logo()
                )
            ),
            'datePublished' => get_the_date('c', $post->ID),
            'dateModified' => get_the_modified_date('c', $post->ID),
            'description' => $this->get_meta_description(),
            'url' => get_permalink($post->ID)
        );
        
        // Add image if available
        if (has_post_thumbnail($post->ID)) {
            $image_data = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'large');
            if ($image_data) {
                $schema['image'] = array(
                    '@type' => 'ImageObject',
                    'url' => $image_data[0],
                    'width' => $image_data[1],
                    'height' => $image_data[2]
                );
            }
        }
        
        // Add article body
        $content = get_post_field('post_content', $post->ID);
        $schema['articleBody'] = wp_strip_all_tags($content);
        
        // Add categories as keywords
        $categories = get_the_category($post->ID);
        if ($categories) {
            $keywords = array();
            foreach ($categories as $category) {
                $keywords[] = $category->name;
            }
            $schema['keywords'] = implode(', ', $keywords);
        }
        
        return $schema;
    }
    
    /**
     * Add organization schema
     */
    public function add_organization_schema() {
        if (!is_front_page()) {
            return;
        }
        
        $organization = array(
            '@context' => 'https://schema.org',
            '@type' => 'Organization',
            'name' => get_bloginfo('name'),
            'description' => get_bloginfo('description'),
            'url' => home_url('/'),
            'logo' => $this->get_organization_logo(),
            'sameAs' => $this->get_social_media_urls(),
            'contactPoint' => array(
                '@type' => 'ContactPoint',
                'contactType' => 'customer service',
                'url' => home_url('/contact/')
            )
        );
        
        echo '<script type="application/ld+json">' . wp_json_encode($organization) . '</script>' . "\n";
    }
    
    /**
     * Get organization logo URL
     */
    private function get_organization_logo() {
        $logo_id = get_theme_mod('custom_logo');
        if ($logo_id) {
            $logo_data = wp_get_attachment_image_src($logo_id, 'full');
            if ($logo_data) {
                return $logo_data[0];
            }
        }
        
        return get_template_directory_uri() . '/assets/images/logo.png';
    }
    
    /**
     * Get social media URLs
     */
    private function get_social_media_urls() {
        $social_urls = array();
        
        $social_networks = array('facebook', 'twitter', 'linkedin', 'youtube', 'instagram');
        
        foreach ($social_networks as $network) {
            $url = get_theme_mod('rts_' . $network . '_url', '');
            if ($url) {
                $social_urls[] = esc_url($url);
            }
        }
        
        return $social_urls;
    }
    
    /**
     * Initialize sitemap
     */
    public function init_sitemap() {
        add_rewrite_rule('^sitemap\.xml$', 'index.php?rts_sitemap=1', 'top');
        add_rewrite_rule('^sitemap-([^/]+?)\.xml$', 'index.php?rts_sitemap=$matches[1]', 'top');
        
        add_filter('query_vars', function($vars) {
            $vars[] = 'rts_sitemap';
            return $vars;
        });
        
        add_action('template_redirect', array($this, 'serve_sitemap'));
    }
    
    /**
     * Serve sitemap
     */
    public function serve_sitemap() {
        $sitemap = get_query_var('rts_sitemap');
        
        if (!$sitemap) {
            return;
        }
        
        header('Content-Type: application/xml; charset=UTF-8');
        
        if ($sitemap === '1') {
            $this->output_sitemap_index();
        } else {
            $this->output_sitemap($sitemap);
        }
        
        exit;
    }
    
    /**
     * Output sitemap index
     */
    private function output_sitemap_index() {
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        
        $sitemaps = array('posts', 'pages', 'categories', 'tags');
        
        foreach ($sitemaps as $sitemap) {
            echo '<sitemap>' . "\n";
            echo '<loc>' . home_url("/sitemap-{$sitemap}.xml") . '</loc>' . "\n";
            echo '<lastmod>' . date('c') . '</lastmod>' . "\n";
            echo '</sitemap>' . "\n";
        }
        
        echo '</sitemapindex>' . "\n";
    }
    
    /**
     * Output specific sitemap
     */
    private function output_sitemap($type) {
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        
        switch ($type) {
            case 'posts':
                $this->output_posts_sitemap();
                break;
            case 'pages':
                $this->output_pages_sitemap();
                break;
            case 'categories':
                $this->output_categories_sitemap();
                break;
            case 'tags':
                $this->output_tags_sitemap();
                break;
        }
        
        echo '</urlset>' . "\n";
    }
    
    /**
     * Output posts sitemap
     */
    private function output_posts_sitemap() {
        $posts = get_posts(array(
            'numberposts' => -1,
            'post_status' => 'publish',
            'post_type' => 'post'
        ));
        
        foreach ($posts as $post) {
            echo '<url>' . "\n";
            echo '<loc>' . get_permalink($post->ID) . '</loc>' . "\n";
            echo '<lastmod>' . get_the_modified_date('c', $post->ID) . '</lastmod>' . "\n";
            echo '<changefreq>weekly</changefreq>' . "\n";
            echo '<priority>0.8</priority>' . "\n";
            echo '</url>' . "\n";
        }
    }
    
    /**
     * Output pages sitemap
     */
    private function output_pages_sitemap() {
        $pages = get_pages(array(
            'post_status' => 'publish'
        ));
        
        foreach ($pages as $page) {
            echo '<url>' . "\n";
            echo '<loc>' . get_permalink($page->ID) . '</loc>' . "\n";
            echo '<lastmod>' . get_the_modified_date('c', $page->ID) . '</lastmod>' . "\n";
            echo '<changefreq>monthly</changefreq>' . "\n";
            echo '<priority>0.6</priority>' . "\n";
            echo '</url>' . "\n";
        }
    }
    
    /**
     * Output categories sitemap
     */
    private function output_categories_sitemap() {
        $categories = get_categories(array(
            'hide_empty' => true
        ));
        
        foreach ($categories as $category) {
            echo '<url>' . "\n";
            echo '<loc>' . get_category_link($category->term_id) . '</loc>' . "\n";
            echo '<lastmod>' . date('c') . '</lastmod>' . "\n";
            echo '<changefreq>weekly</changefreq>' . "\n";
            echo '<priority>0.5</priority>' . "\n";
            echo '</url>' . "\n";
        }
    }
    
    /**
     * Output tags sitemap
     */
    private function output_tags_sitemap() {
        $tags = get_tags(array(
            'hide_empty' => true
        ));
        
        foreach ($tags as $tag) {
            echo '<url>' . "\n";
            echo '<loc>' . get_tag_link($tag->term_id) . '</loc>' . "\n";
            echo '<lastmod>' . date('c') . '</lastmod>' . "\n";
            echo '<changefreq>monthly</changefreq>' . "\n";
            echo '<priority>0.4</priority>' . "\n";
            echo '</url>' . "\n";
        }
    }
    
    /**
     * Generate sitemap files
     */
    public function generate_sitemap() {
        // Regenerate sitemap on post save
        add_action('save_post', function() {
            // Clear sitemap cache
            delete_transient('rts_sitemap_cache');
        });
    }
    
    /**
     * Add analytics code
     */
    public function add_analytics_code() {
        // Google Analytics 4
        $ga_id = get_theme_mod('rts_ga4_id', '');
        if ($ga_id && !is_admin() && !current_user_can('manage_options')) {
            ?>
            <!-- Google Analytics 4 -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=<?php echo esc_attr($ga_id); ?>"></script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '<?php echo esc_js($ga_id); ?>', {
                    anonymize_ip: true,
                    cookie_flags: 'secure;samesite=strict'
                });
                
                // Enhanced e-commerce tracking
                gtag('config', '<?php echo esc_js($ga_id); ?>', {
                    custom_map: {
                        'custom_parameter_1': 'trading_action',
                        'custom_parameter_2': 'portfolio_value'
                    }
                });
            </script>
            <?php
        }
        
        // Facebook Pixel
        $fb_pixel_id = get_theme_mod('rts_fb_pixel_id', '');
        if ($fb_pixel_id && !is_admin() && !current_user_can('manage_options')) {
            ?>
            <!-- Facebook Pixel -->
            <script>
                !function(f,b,e,v,n,t,s)
                {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
                n.callMethod.apply(n,arguments):n.queue.push(arguments)};
                if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
                n.queue=[];t=b.createElement(e);t.async=!0;
                t.src=v;s=b.getElementsByTagName(e)[0];
                s.parentNode.insertBefore(t,s)}(window, document,'script',
                'https://connect.facebook.net/en_US/fbevents.js');
                fbq('init', '<?php echo esc_js($fb_pixel_id); ?>');
                fbq('track', 'PageView');
            </script>
            <noscript>
                <img height="1" width="1" style="display:none" 
                     src="https://www.facebook.com/tr?id=<?php echo esc_attr($fb_pixel_id); ?>&ev=PageView&noscript=1"/>
            </noscript>
            <?php
        }
    }
    
    /**
     * Add performance monitoring
     */
    public function add_performance_monitoring() {
        if (WP_DEBUG || current_user_can('manage_options')) {
            ?>
            <script>
                // Core Web Vitals monitoring
                function sendToAnalytics(metric) {
                    if (typeof gtag !== 'undefined') {
                        gtag('event', metric.name, {
                            event_category: 'Web Vitals',
                            event_label: metric.id,
                            value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
                            non_interaction: true,
                        });
                    }
                    
                    console.log('Web Vital:', metric);
                }
                
                // Load web-vitals library
                if ('requestIdleCallback' in window) {
                    requestIdleCallback(() => {
                        import('https://unpkg.com/web-vitals@3/dist/web-vitals.js').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
                            getCLS(sendToAnalytics);
                            getFID(sendToAnalytics);
                            getFCP(sendToAnalytics);
                            getLCP(sendToAnalytics);
                            getTTFB(sendToAnalytics);
                        });
                    });
                }
            </script>
            <?php
        }
    }
    
    /**
     * Optimize permalink structure
     */
    public function optimize_permalink_structure($permalink, $post, $leavename) {
        // Add trailing slash for consistency
        if (!$leavename && !is_admin()) {
            $permalink = trailingslashit($permalink);
        }
        
        return $permalink;
    }
    
    /**
     * Add article schema to content
     */
    public function add_article_schema($content) {
        if (is_single() && in_the_loop() && is_main_query()) {
            $schema_data = $this->get_article_schema();
            if ($schema_data) {
                $schema_json = '<script type="application/ld+json">' . wp_json_encode($schema_data) . '</script>';
                $content = $schema_json . $content;
            }
        }
        
        return $content;
    }
}

// Initialize SEO & Analytics
new RTS_SEO_Analytics();

/**
 * SEO Utility Functions
 */

/**
 * Get optimized title for SEO
 */
function rts_get_seo_title($post_id = null) {
    if (!$post_id) {
        $post_id = get_the_ID();
    }
    
    $title = get_the_title($post_id);
    $site_name = get_bloginfo('name');
    
    if (is_front_page()) {
        return $site_name . ' - ' . get_bloginfo('description');
    }
    
    return $title . ' - ' . $site_name;
}

/**
 * Generate meta description for SEO
 */
function rts_generate_meta_description($content, $length = 160) {
    $description = wp_strip_all_tags($content);
    $description = preg_replace('/\s+/', ' ', $description);
    $description = trim($description);
    
    if (strlen($description) > $length) {
        $description = substr($description, 0, $length);
        $description = substr($description, 0, strrpos($description, ' ')) . '...';
    }
    
    return $description;
}

/**
 * Add schema markup to specific content types
 */
function rts_add_faq_schema($faqs) {
    $schema = array(
        '@context' => 'https://schema.org',
        '@type' => 'FAQPage',
        'mainEntity' => array()
    );
    
    foreach ($faqs as $faq) {
        $schema['mainEntity'][] = array(
            '@type' => 'Question',
            'name' => $faq['question'],
            'acceptedAnswer' => array(
                '@type' => 'Answer',
                'text' => $faq['answer']
            )
        );
    }
    
    return '<script type="application/ld+json">' . wp_json_encode($schema) . '</script>';
}