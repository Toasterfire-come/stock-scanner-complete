<?php
/**
 * Stock Scanner Pro Theme Header Template
 * Version: 2.2.0 - Production Ready with Professional Logo
 */
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="format-detection" content="telephone=no">
    <meta name="theme-color" content="#667eea">
    
    <!-- Preconnect to external resources -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- DNS prefetch for performance -->
    <link rel="dns-prefetch" href="//api.stockmarket.com">
    
    <?php wp_head(); ?>
    
    <!-- Schema.org markup for SEO -->
    <?php
    $schema_data = array(
        '@context' => 'https://schema.org',
        '@type' => 'WebSite',
        'name' => get_bloginfo('name', 'display'),
        'description' => get_bloginfo('description', 'display'),
        'url' => home_url('/')
    );
    ?>
    <script type="application/ld+json"><?php echo wp_json_encode($schema_data); ?></script>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Skip to content link for accessibility -->
<a class="skip-link screen-reader-text" href="#main"><?php _e('Skip to content', 'stock-scanner'); ?></a>

<header class="site-header" role="banner">
    <div class="header-container">
        
        <!-- Logo and Brand Section -->
        <div class="site-branding">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="logo-link" rel="home" aria-label="<?php echo esc_attr( get_bloginfo('name', 'display') ); ?> - Home">
                <div class="logo-container">
                    <img src="<?php echo esc_url(get_template_directory_uri()); ?>/assets/images/logo.png" 
                         alt="<?php echo esc_attr( get_bloginfo('name', 'display') ); ?> Logo" 
                         class="logo-image"
                         width="120" 
                         height="60"
                         loading="eager"
                         decoding="async">
                    <div class="brand-text">
                        <span class="logo-text"><?php echo esc_html( get_bloginfo('name', 'display') ); ?></span>
                        <?php 
                        $description = get_bloginfo('description', 'display');
                        if ($description || is_customize_preview()) : ?>
                            <span class="site-description"><?php echo esc_html( $description ); ?></span>
                        <?php endif; ?>
                    </div>
                </div>
            </a>
        </div>

        <!-- Mobile Menu Toggle -->
        <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false" aria-label="Toggle navigation menu">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="screen-reader-text">Menu</span>
        </button>

        <!-- Primary Navigation -->
        <nav class="main-navigation" role="navigation" aria-label="Primary Menu">
            <?php
            wp_nav_menu(array(
                'theme_location' => 'primary',
                'menu_id'        => 'primary-menu',
                'menu_class'     => 'nav-menu',
                'container'      => false,
                'fallback_cb'    => 'stock_scanner_fallback_menu',
                'walker'         => new Stock_Scanner_Nav_Walker(),
                'depth'          => 2,
            ));
            ?>
        </nav>

        <!-- Header Actions -->
        <div class="header-actions">
            
            <!-- Theme Toggle -->
            <button class="theme-toggle btn-icon" aria-label="Toggle dark mode" title="Toggle Theme">
                <span class="theme-icon light-icon">🌙</span>
                <span class="theme-icon dark-icon">☀️</span>
            </button>

            <!-- Search Toggle -->
            <button class="search-toggle btn-icon" aria-label="Toggle search" title="Search">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="M21 21l-4.35-4.35"></path>
                </svg>
            </button>

            <?php if (is_user_logged_in()) : ?>
                <!-- User Info & Menu -->
                <div class="user-info">
                    <?php
                    $current_user = wp_get_current_user();
                    $user_meta = get_user_meta($current_user->ID);
                    $membership_level = get_user_meta($current_user->ID, 'membership_level', true) ?: 'free';
                    ?>
                    
                    <!-- Membership Badge -->
                    <span class="membership-badge <?php echo esc_attr($membership_level); ?>">
                        <?php echo esc_html(ucfirst($membership_level)); ?>
                    </span>

                    <!-- User Dropdown -->
                    <div class="user-dropdown">
                        <button class="user-toggle" aria-expanded="false" aria-haspopup="true">
                            <div class="user-avatar">
                                <?php echo get_avatar($current_user->ID, 32, '', '', array('class' => 'avatar-img')); ?>
                            </div>
                            <span class="user-name"><?php echo esc_html($current_user->display_name); ?></span>
                            <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6,9 12,15 18,9"></polyline>
                            </svg>
                        </button>

                        <div class="user-menu" role="menu">
                            <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="3" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="14" width="7" height="7"></rect>
                                    <rect x="3" y="14" width="7" height="7"></rect>
                                </svg>
                                Dashboard
                            </a>
                            <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="12" y1="1" x2="12" y2="23"></line>
                                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                                </svg>
                                Portfolio
                            </a>
                            <a href="<?php echo esc_url(home_url('/watchlist/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                    <circle cx="12" cy="12" r="3"></circle>
                                </svg>
                                Watchlist
                            </a>
                            <hr class="menu-divider">
                            <a href="<?php echo esc_url(home_url('/account-settings/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="3"></circle>
                                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                </svg>
                                Settings
                            </a>
                            <?php if ($membership_level === 'free') : ?>
                                <a href="<?php echo esc_url(home_url('/premium-plans/')); ?>" class="user-menu-item premium-upgrade" role="menuitem">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polygon points="12,2 15.09,8.26 22,9 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9 8.91,8.26"></polygon>
                                    </svg>
                                    Upgrade to Premium
                                </a>
                            <?php endif; ?>
                            <hr class="menu-divider">
                            <a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>" class="user-menu-item logout" role="menuitem">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16,17 21,12 16,7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                                Logout
                            </a>
                        </div>
                    </div>
                </div>
            <?php else : ?>
                <!-- Login/Register Actions -->
                <div class="auth-actions">
                    <a href="<?php echo esc_url(wp_login_url()); ?>" class="btn btn-outline btn-sm">
                        Login
                    </a>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-sm">
                        Get Started
                    </a>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <!-- Search Overlay -->
    <div class="search-overlay" aria-hidden="true">
        <div class="search-container">
            <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
                <div class="search-input-group">
                    <label for="search-field" class="screen-reader-text">Search for:</label>
                    <input type="search" 
                           id="search-field" 
                           class="search-field" 
                           placeholder="Search stocks, companies, or articles..." 
                           value="<?php echo get_search_query(); ?>" 
                           name="s" 
                           autocomplete="off"
                           autocorrect="off"
                           autocapitalize="off"
                           spellcheck="false">
                    <button type="submit" class="search-submit" aria-label="Search">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="M21 21l-4.35-4.35"></path>
                        </svg>
                    </button>
                </div>
                <div class="search-suggestions">
                    <div class="popular-searches">
                        <h4>Popular Searches</h4>
                        <div class="search-tags">
                            <a href="?s=AAPL" class="search-tag">AAPL</a>
                            <a href="?s=TSLA" class="search-tag">TSLA</a>
                            <a href="?s=GOOGL" class="search-tag">GOOGL</a>
                            <a href="?s=MSFT" class="search-tag">MSFT</a>
                            <a href="?s=AMZN" class="search-tag">AMZN</a>
                        </div>
                    </div>
                </div>
            </form>
            <button class="search-close" aria-label="Close search">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    </div>
</header>

<!-- Progress Bar for Page Loading -->
<div class="page-loading-bar" aria-hidden="true"></div>

<main id="main" class="site-main" role="main">