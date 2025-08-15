<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="wp-nonce" content="<?php echo esc_attr( wp_create_nonce('wp_rest') ); ?>">
    
    <?php 
    // Enhanced SEO Meta Tags
    global $post;
    $site_name = get_bloginfo('name');
    $site_description = get_bloginfo('description');
    $site_url = home_url();
    
    // Get current page information
    $current_title = wp_get_document_title();
    $current_url = is_singular() ? get_permalink() : home_url(add_query_arg(array(),$wp->request));
    $current_description = $site_description;
    $current_keywords = 'stock scanner, market analysis, financial data, investment tools, portfolio management';
    
    // Page-specific SEO data
    if (is_singular() && isset($post)) {
        $excerpt = has_excerpt($post) ? get_the_excerpt($post) : wp_strip_all_tags(get_the_content(null, false, $post));
        if (!empty($excerpt)) { 
            $current_description = wp_trim_words($excerpt, 30); 
        }
        
        // Get custom meta if available
        $custom_description = get_post_meta($post->ID, '_seo_description', true);
        $custom_keywords = get_post_meta($post->ID, '_seo_keywords', true);
        
        if (!empty($custom_description)) {
            $current_description = $custom_description;
        }
        if (!empty($custom_keywords)) {
            $current_keywords = $custom_keywords;
        }
    }
    
    // Page template specific SEO
    if (is_page()) {
        $template = get_page_template_slug();
        switch ($template) {
            case 'page-dashboard.php':
                $current_description = 'Personal investment dashboard with real-time portfolio tracking, market data, and comprehensive financial analytics.';
                $current_keywords = 'investment dashboard, portfolio tracker, stock market dashboard, financial analytics';
                break;
            case 'page-market-overview.php':
                $current_description = 'Comprehensive market overview with real-time indices, sector performance, and market analysis tools.';
                $current_keywords = 'market overview, stock indices, market analysis, sector performance, financial markets';
                break;
            case 'page-stock-screener.php':
                $current_description = 'Advanced stock screener with customizable filters to find investment opportunities based on technical and fundamental analysis.';
                $current_keywords = 'stock screener, stock filter, investment screening, stock analysis tools';
                break;
            case 'page-portfolio.php':
                $current_description = 'Portfolio management tools for tracking investments, analyzing performance, and managing your financial assets.';
                $current_keywords = 'portfolio management, investment tracking, portfolio analysis, asset management';
                break;
            case 'page-watchlist.php':
                $current_description = 'Personal stock watchlist for monitoring favorite stocks with real-time quotes and price alerts.';
                $current_keywords = 'stock watchlist, stock monitoring, price alerts, investment tracking';
                break;
            case 'page-stock-news.php':
                $current_description = 'Latest financial news, market updates, and stock-specific news to stay informed about market trends.';
                $current_keywords = 'financial news, stock news, market updates, investment news';
                break;
            case 'page-premium-plans.php':
                $current_description = 'Upgrade to premium plans for advanced features, unlimited API calls, and professional investment tools.';
                $current_keywords = 'premium subscription, investment tools, professional features, trading platform';
                break;
        }
    }
    
    // Canonical URL
    $canonical_url = function_exists('wp_get_canonical_url') ? wp_get_canonical_url() : $current_url;
    
    // Image for social sharing
    $og_image = '';
    if (is_singular() && has_post_thumbnail($post)) {
        $img = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'full');
        if (!empty($img[0])) { 
            $og_image = $img[0]; 
        }
    }
    if (empty($og_image)) {
        $og_image = get_template_directory_uri() . '/assets/images/og-default.jpg';
    }
    ?>
    
    <!-- Basic Meta Tags -->
    <meta name="description" content="<?php echo esc_attr($current_description); ?>">
    <meta name="keywords" content="<?php echo esc_attr($current_keywords); ?>">
    <meta name="author" content="<?php echo esc_attr($site_name); ?>">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    
    <!-- Canonical URL -->
    <?php if ($canonical_url): ?>
        <link rel="canonical" href="<?php echo esc_url($canonical_url); ?>" />
    <?php endif; ?>
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:site_name" content="<?php echo esc_attr($site_name); ?>" />
    <meta property="og:title" content="<?php echo esc_attr($current_title); ?>" />
    <meta property="og:description" content="<?php echo esc_attr($current_description); ?>" />
    <meta property="og:url" content="<?php echo esc_url($current_url); ?>" />
    <meta property="og:type" content="<?php echo is_singular() ? 'article' : 'website'; ?>" />
    <meta property="og:image" content="<?php echo esc_url($og_image); ?>" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:locale" content="<?php echo get_locale(); ?>" />
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@zatrastocks" />
    <meta name="twitter:creator" content="@zatrastocks" />
    <meta name="twitter:title" content="<?php echo esc_attr($current_title); ?>" />
    <meta name="twitter:description" content="<?php echo esc_attr($current_description); ?>" />
    <meta name="twitter:image" content="<?php echo esc_url($og_image); ?>" />
    
    <!-- Additional SEO Meta Tags -->
    <meta name="theme-color" content="#1a73e8">
    <meta name="msapplication-TileColor" content="#1a73e8">
    <meta name="application-name" content="<?php echo esc_attr($site_name); ?>">
    
    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "<?php echo esc_js($site_name); ?>",
        "url": "<?php echo esc_url($site_url); ?>",
        "description": "<?php echo esc_js($site_description); ?>",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "<?php echo esc_url($site_url); ?>/?s={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }
    </script>
    
    <?php if (is_page()): ?>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "<?php echo esc_js($current_title); ?>",
        "description": "<?php echo esc_js($current_description); ?>",
        "url": "<?php echo esc_url($current_url); ?>",
        "isPartOf": {
            "@type": "WebSite",
            "name": "<?php echo esc_js($site_name); ?>",
            "url": "<?php echo esc_url($site_url); ?>"
        }
    }
    </script>
    <?php endif; ?>
    
    <?php if (is_page_template('page-dashboard.php') || is_page_template('page-portfolio.php')): ?>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Zatra Stock Scanner",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "description": "Professional stock market analysis and portfolio management platform",
        "url": "<?php echo esc_url($site_url); ?>",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }
    </script>
    <?php endif; ?>
    
    <!-- Favicon and App Icons -->
    <?php if (file_exists(get_template_directory() . '/assets/images/favicon.ico')): ?>
    <link rel="icon" type="image/x-icon" href="<?php echo get_template_directory_uri(); ?>/assets/images/favicon.ico">
    <?php endif; ?>
    <?php if (file_exists(get_template_directory() . '/assets/images/favicon-32x32.png')): ?>
    <link rel="icon" type="image/png" sizes="32x32" href="<?php echo get_template_directory_uri(); ?>/assets/images/favicon-32x32.png">
    <?php endif; ?>
    <?php if (file_exists(get_template_directory() . '/assets/images/favicon-16x16.png')): ?>
    <link rel="icon" type="image/png" sizes="16x16" href="<?php echo get_template_directory_uri(); ?>/assets/images/favicon-16x16.png">
    <?php endif; ?>
    <?php if (file_exists(get_template_directory() . '/assets/images/apple-touch-icon.png')): ?>
    <link rel="apple-touch-icon" sizes="180x180" href="<?php echo get_template_directory_uri(); ?>/assets/images/apple-touch-icon.png">
    <?php endif; ?>
    <?php if (file_exists(get_template_directory() . '/manifest.json') && file_exists(get_template_directory() . '/assets/images/icon-144x144.png')): ?>
    <link rel="manifest" href="<?php echo get_template_directory_uri(); ?>/manifest.json">
    <?php endif; ?>
    
    <!-- Preconnect to external domains for performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://cdn.jsdelivr.net">
    
    <!-- DNS Prefetch for external resources -->
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    <link rel="dns-prefetch" href="//cdn.jsdelivr.net">
    
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Skip to content', 'zatra'); ?></a>

    <header id="masthead" class="site-header" role="banner">
        <div class="header-container">
            <div class="site-branding">
                <a href="<?php echo esc_url(home_url('/')); ?>" class="site-logo" rel="home">
                    <span class="logo-text"><?php bloginfo('name'); ?></span>
                </a>
                <?php
                $description = get_bloginfo('description', 'display');
                if ($description || is_customize_preview()): ?>
                    <p class="site-description"><?php echo $description; ?></p>
                <?php endif; ?>
            </div>

            <nav id="site-navigation" class="main-navigation" role="navigation" aria-label="Primary Menu">
                <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="menu-text"><?php esc_html_e('Menu', 'zatra'); ?></span>
                </button>
                
                <div class="nav-menu-wrapper">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_id'        => 'primary-menu',
                        'menu_class'     => 'primary-menu',
                        'container'      => false,
                        'fallback_cb'    => false
                    ));
                    ?>
                </div>
            </nav>

            <div class="header-actions">
                <?php if (is_user_logged_in()): ?>
                    <?php
                    $user = wp_get_current_user();
                    $membership_level = function_exists('get_user_membership_level') ? get_user_membership_level() : 'free';
                    ?>
                    
                    <div class="user-info">
                        <div class="membership-badge membership-<?php echo esc_attr($membership_level); ?>">
                            <?php echo ucfirst($membership_level); ?>
                        </div>
                        
                        <div class="user-dropdown">
                            <button class="user-toggle" aria-expanded="false" aria-haspopup="true">
                                <span class="user-avatar">●</span>
                                <span class="user-name"><?php echo esc_html($user->display_name); ?></span>
                                <span class="dropdown-arrow">▼</span>
                            </button>
                            
                            <div class="user-menu" role="menu">
                                <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="user-menu-item" role="menuitem">
                                    Dashboard
                                </a>
                                <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="user-menu-item" role="menuitem">
                                    My Portfolio
                                </a>
                                <a href="<?php echo esc_url(home_url('/watchlist/')); ?>" class="user-menu-item" role="menuitem">
                                    Watchlist
                                </a>
                                <hr class="menu-divider">
                                <a href="<?php echo esc_url(home_url('/account/')); ?>" class="user-menu-item" role="menuitem">
                                    Account Settings
                                </a>
                                <?php if ($membership_level === 'free'): ?>
                                <a href="<?php echo esc_url(home_url('/premium-plans/')); ?>" class="user-menu-item upgrade-link" role="menuitem">
                                    Upgrade Plan
                                </a>
                                <?php endif; ?>
                                <hr class="menu-divider">
                                <a href="<?php echo wp_logout_url(home_url()); ?>" class="user-menu-item logout-link" role="menuitem">
                                    Logout
                                </a>
                            </div>
                        </div>
                    </div>
                <?php else: ?>
                    <div class="auth-links">
                        <a class="login-link" href="<?php echo esc_url(wp_login_url()); ?>"><?php esc_html_e('Log in', 'zatra'); ?></a>
                        <a class="signup-link" href="<?php echo esc_url(wp_registration_url()); ?>"><?php esc_html_e('Sign up', 'zatra'); ?></a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </header>

    <main id="primary" class="site-main" role="main">