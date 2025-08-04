<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="<?php bloginfo('description'); ?>">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <link rel="pingback" href="<?php bloginfo('pingback_url'); ?>">
    
    <!-- Preload critical fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="<?php echo get_template_directory_uri(); ?>/assets/favicon.ico">
    
    <?php wp_head(); ?>
    
    <!-- Custom meta tags for stock scanner -->
    <meta name="theme-color" content="#2563eb">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="<?php bloginfo('name'); ?>">
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Skip to content', 'stock-scanner'); ?></a>

    <!-- Header -->
    <header id="masthead" class="site-header">
        <div class="container">
            <div class="header-content">
                <!-- Site Branding -->
                <div class="site-branding">
                    <div class="brand-content">
                        <h1 class="site-title">
                            <a href="<?php echo esc_url(home_url('/')); ?>" rel="home">
                                <?php bloginfo('name'); ?>
                            </a>
                        </h1>
                        <p class="site-description"><?php bloginfo('description'); ?></p>
                    </div>
                </div>

                <!-- Main Navigation -->
                <nav id="site-navigation" class="main-navigation">
                    <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                        <span class="menu-toggle-icon"></span>
                        <span class="screen-reader-text"><?php esc_html_e('Menu', 'stock-scanner'); ?></span>
                    </button>
                    
                    <div class="nav-menu-wrapper">
                        <?php
                        wp_nav_menu(array(
                            'theme_location' => 'primary',
                            'menu_id'        => 'primary-menu',
                            'menu_class'     => 'nav-menu',
                            'container'      => false,
                            'fallback_cb'    => 'stock_scanner_fallback_menu',
                        ));
                        ?>
                    </div>
                </nav>

                <!-- Header Actions -->
                <div class="header-actions">
                    <button class="btn btn-primary btn-sm" id="refresh-data">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
                        </svg>
                        Refresh
                    </button>
                    
                    <div class="market-status">
                        <span class="status-indicator" id="market-status-indicator"></span>
                        <span class="status-text" id="market-status-text">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Live Ticker Bar -->
    <div class="live-ticker-bar">
        <div class="container-fluid">
            <div class="ticker-container" id="live-ticker">
                <!-- Ticker items will be populated by JavaScript -->
                <div class="ticker-item">
                    <span class="ticker-symbol">AAPL</span>
                    <span class="ticker-price">$150.25</span>
                    <span class="ticker-change positive">+2.5%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">MSFT</span>
                    <span class="ticker-price">$320.10</span>
                    <span class="ticker-change positive">+1.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">GOOGL</span>
                    <span class="ticker-price">$2,850.75</span>
                    <span class="ticker-change negative">-0.5%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">TSLA</span>
                    <span class="ticker-price">$750.30</span>
                    <span class="ticker-change positive">+3.2%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">AMZN</span>
                    <span class="ticker-price">$3,200.45</span>
                    <span class="ticker-change positive">+1.1%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">NVDA</span>
                    <span class="ticker-price">$450.80</span>
                    <span class="ticker-change positive">+4.2%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">META</span>
                    <span class="ticker-price">$280.15</span>
                    <span class="ticker-change negative">-0.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">NFLX</span>
                    <span class="ticker-price">$580.90</span>
                    <span class="ticker-change positive">+2.1%</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Page Header -->
    <?php if (!is_front_page()): ?>
    <div class="page-header">
        <div class="container">
            <div class="page-header-content">
                <h1 class="page-title">
                    <?php
                    if (is_home() && !is_front_page()) {
                        single_post_title();
                    } elseif (is_archive()) {
                        the_archive_title();
                    } elseif (is_search()) {
                        printf(esc_html__('Search Results for: %s', 'stock-scanner'), '<span>' . get_search_query() . '</span>');
                    } elseif (is_404()) {
                        esc_html_e('Page Not Found', 'stock-scanner');
                    } else {
                        the_title();
                    }
                    ?>
                </h1>
                
                <?php if (is_archive() || is_search()): ?>
                <div class="page-description">
                    <?php
                    if (is_archive()) {
                        the_archive_description();
                    } elseif (is_search()) {
                        printf(esc_html__('Found %d results', 'stock-scanner'), $wp_query->found_posts);
                    }
                    ?>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <!-- Main Content -->
    <div id="content" class="site-content">
        <div class="container">
            <div class="content-area">
                <main id="primary" class="site-main content-main">
                    <div class="content-wrapper">