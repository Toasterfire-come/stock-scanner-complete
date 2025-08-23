<?php
/**
 * Stock Scanner Pro Theme Header Template v3.0.0
 * ULTRA-MODERN ENHANCED HEADER with Glassmorphism Effects
 * Premium design with advanced interactions and performance optimizations
 */
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="format-detection" content="telephone=no">
    <meta name="theme-color" content="#667eea">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    
    <!-- Enhanced Preconnect for Performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="//api.stockmarket.com">
    
    <!-- Progressive Enhancement -->
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    <link rel="dns-prefetch" href="//api.stockmarket.com">
    
    <!-- Prefetch Critical Resources -->
    <link rel="prefetch" href="<?php echo esc_url(get_template_directory_uri()); ?>/js/theme-enhanced.js">
    <link rel="prefetch" href="<?php echo esc_url(get_template_directory_uri()); ?>/assets/js/advanced-components.js">
    
    <?php wp_head(); ?>
    
    <!-- Enhanced Schema.org markup for SEO -->
    <?php
    $schema_data = array(
        '@context' => 'https://schema.org',
        '@type' => 'WebApplication',
        'name' => get_bloginfo('name', 'display'),
        'description' => get_bloginfo('description', 'display'),
        'url' => home_url('/'),
        'applicationCategory' => 'FinanceApplication',
        'operatingSystem' => 'Web Browser',
        'offers' => array(
            '@type' => 'Offer',
            'price' => '9',
            'priceCurrency' => 'USD',
            'priceValidUntil' => date('Y-12-31', strtotime('+1 year'))
        ),
        'aggregateRating' => array(
            '@type' => 'AggregateRating',
            'ratingValue' => '4.8',
            'reviewCount' => '2847'
        )
    );
    ?>
    <script type="application/ld+json"><?php echo wp_json_encode($schema_data); ?></script>
    
    <!-- Enhanced Critical CSS Inlining -->
    <style>
        /* Critical above-the-fold styles */
        .site-header { 
            position: sticky; 
            top: 0; 
            z-index: 1020; 
            backdrop-filter: blur(10px); 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        }
        .hero-section { 
            min-height: 60vh; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
        }
        .loading-skeleton { 
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); 
            background-size: 200% 100%; 
            animation: shimmer 1.5s infinite; 
        }
        @keyframes shimmer { 0% { background-position: -200px 0; } 100% { background-position: calc(200px + 100%) 0; } }
    </style>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Enhanced Skip to content link for accessibility -->
<a class="skip-link screen-reader-text" href="#main" tabindex="1"><?php _e('Skip to content', 'stock-scanner'); ?></a>

<!-- Enhanced Header with Glassmorphism -->
<header class="site-header glass-nav" role="banner" itemscope itemtype="https://schema.org/WPHeader">
    <div class="header-container">
        
        <!-- Premium Logo and Brand Section -->
        <div class="site-branding" itemscope itemtype="https://schema.org/Organization">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="logo-link" rel="home" 
               aria-label="<?php echo esc_attr( get_bloginfo('name', 'display') ); ?> - Home"
               itemprop="url">
                <div class="logo-container glass-card">
                    <img src="<?php echo esc_url(get_template_directory_uri()); ?>/assets/images/logo.png" 
                         alt="<?php echo esc_attr( get_bloginfo('name', 'display') ); ?> Logo" 
                         class="logo-image"
                         width="120" 
                         height="45"
                         loading="eager"
                         decoding="async"
                         itemprop="logo">
                    <div class="brand-text">
                        <span class="logo-text text-gradient" itemprop="name">
                            <?php echo esc_html( get_bloginfo('name', 'display') ); ?>
                        </span>
                        <?php 
                        $description = get_bloginfo('description', 'display');
                        if ($description || is_customize_preview()) : ?>
                            <span class="site-description" itemprop="description">
                                <?php echo esc_html( $description ); ?>
                            </span>
                        <?php endif; ?>
                    </div>
                </div>
            </a>
        </div>

        <!-- Enhanced Mobile Menu Toggle -->
        <button class="menu-toggle btn-icon glass" 
                aria-controls="primary-menu" 
                aria-expanded="false" 
                aria-label="<?php _e('Toggle navigation menu', 'stock-scanner'); ?>"
                data-mobile-menu-toggle>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="screen-reader-text"><?php _e('Menu', 'stock-scanner'); ?></span>
        </button>

        <!-- Enhanced Primary Navigation -->
        <nav class="main-navigation glass-nav" role="navigation" 
             aria-label="<?php _e('Primary Menu', 'stock-scanner'); ?>"
             itemscope itemtype="https://schema.org/SiteNavigationElement">
            <?php
            wp_nav_menu(array(
                'theme_location' => 'primary',
                'menu_id'        => 'primary-menu',
                'menu_class'     => 'nav-menu enhanced-nav',
                'container'      => false,
                'fallback_cb'    => 'stock_scanner_fallback_menu',
                'walker'         => new Stock_Scanner_Nav_Walker(),
                'depth'          => 2,
            ));
            ?>
        </nav>

        <!-- Premium Header Actions -->
        <div class="header-actions">
            
            <!-- Enhanced Theme Toggle with Animation -->
            <button class="theme-toggle btn-icon glass" 
                    aria-label="<?php _e('Toggle dark mode', 'stock-scanner'); ?>" 
                    title="<?php _e('Toggle Theme', 'stock-scanner'); ?>"
                    data-theme-toggle>
                <span class="theme-icon light-icon">🌙</span>
                <span class="theme-icon dark-icon">☀️</span>
            </button>

            <!-- Enhanced Search Toggle -->
            <button class="search-toggle btn-icon glass" 
                    aria-label="<?php _e('Toggle search', 'stock-scanner'); ?>" 
                    title="<?php _e('Search', 'stock-scanner'); ?>"
                    data-search-toggle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="M21 21l-4.35-4.35"></path>
                </svg>
            </button>

            <?php if (is_user_logged_in()) : ?>
                <!-- Enhanced User Info & Menu -->
                <div class="user-info animate-fade-in">
                    <?php
                    $current_user = wp_get_current_user();
                    $user_meta = get_user_meta($current_user->ID);
                    $membership_level = get_user_meta($current_user->ID, 'membership_level', true) ?: 'free';
                    ?>
                    
                    <!-- Premium Membership Badge -->
                    <span class="membership-badge <?php echo esc_attr($membership_level); ?> glass">
                        <?php echo esc_html(ucfirst($membership_level)); ?>
                    </span>

                    <!-- Enhanced User Dropdown -->
                    <div class="user-dropdown">
                        <button class="user-toggle glass" 
                                aria-expanded="false" 
                                aria-haspopup="true"
                                data-user-menu-toggle>
                            <div class="user-avatar">
                                <?php echo get_avatar($current_user->ID, 36, '', '', array('class' => 'avatar-img')); ?>
                            </div>
                            <span class="user-name"><?php echo esc_html($current_user->display_name); ?></span>
                            <svg class="dropdown-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                <polyline points="6,9 12,15 18,9"></polyline>
                            </svg>
                        </button>

                        <div class="user-menu glass-modal animate-scale-in" role="menu" data-user-menu>
                            <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <rect x="3" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="14" width="7" height="7"></rect>
                                    <rect x="3" y="14" width="7" height="7"></rect>
                                </svg>
                                <?php _e('Dashboard', 'stock-scanner'); ?>
                            </a>
                            <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <line x1="12" y1="1" x2="12" y2="23"></line>
                                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                                </svg>
                                <?php _e('Portfolio', 'stock-scanner'); ?>
                            </a>
                            <a href="<?php echo esc_url(home_url('/watchlist/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                    <circle cx="12" cy="12" r="3"></circle>
                                </svg>
                                <?php _e('Watchlist', 'stock-scanner'); ?>
                            </a>
                            <hr class="menu-divider">
                            <a href="<?php echo esc_url(home_url('/account-settings/')); ?>" class="user-menu-item" role="menuitem">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <circle cx="12" cy="12" r="3"></circle>
                                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                </svg>
                                <?php _e('Settings', 'stock-scanner'); ?>
                            </a>
                            <?php if ($membership_level === 'free') : ?>
                                <a href="<?php echo esc_url(home_url('/premium-plans/')); ?>" class="user-menu-item premium-upgrade" role="menuitem">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                        <polygon points="12,2 15.09,8.26 22,9 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9 8.91,8.26"></polygon>
                                    </svg>
                                    <?php _e('Upgrade to Premium', 'stock-scanner'); ?>
                                </a>
                            <?php endif; ?>
                            <hr class="menu-divider">
                            <a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>" class="user-menu-item logout" role="menuitem">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16,17 21,12 16,7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                                <?php _e('Logout', 'stock-scanner'); ?>
                            </a>
                        </div>
                    </div>
                </div>
            <?php else : ?>
                <!-- Enhanced Login/Register Actions -->
                <div class="auth-actions animate-fade-in">
                    <a href="<?php echo esc_url(wp_login_url()); ?>" class="btn btn-outline btn-sm glass">
                        <?php _e('Login', 'stock-scanner'); ?>
                    </a>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-sm gradient-primary">
                        <?php _e('Get Started', 'stock-scanner'); ?>
                    </a>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <!-- Enhanced Search Overlay with Advanced Features -->
    <div class="search-overlay glass-modal" aria-hidden="true" data-search-overlay>
        <div class="search-container glass-card animate-scale-in">
            <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
                <div class="search-input-group">
                    <label for="search-field" class="screen-reader-text"><?php _e('Search for:', 'stock-scanner'); ?></label>
                    <input type="search" 
                           id="search-field" 
                           class="search-field" 
                           placeholder="<?php _e('Search stocks, companies, or articles...', 'stock-scanner'); ?>" 
                           value="<?php echo get_search_query(); ?>" 
                           name="s" 
                           autocomplete="off"
                           autocorrect="off"
                           autocapitalize="off"
                           spellcheck="false"
                           data-advanced-search>
                    <button type="submit" class="search-submit gradient-primary" aria-label="<?php _e('Search', 'stock-scanner'); ?>">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="M21 21l-4.35-4.35"></path>
                        </svg>
                    </button>
                </div>
                
                <!-- Enhanced Search Suggestions -->
                <div class="search-suggestions">
                    <div class="popular-searches">
                        <h4><?php _e('Popular Searches', 'stock-scanner'); ?></h4>
                        <div class="search-tags">
                            <a href="?s=AAPL" class="search-tag glass">AAPL</a>
                            <a href="?s=TSLA" class="search-tag glass">TSLA</a>
                            <a href="?s=GOOGL" class="search-tag glass">GOOGL</a>
                            <a href="?s=MSFT" class="search-tag glass">MSFT</a>
                            <a href="?s=AMZN" class="search-tag glass">AMZN</a>
                            <a href="?s=META" class="search-tag glass">META</a>
                        </div>
                    </div>
                    
                    <!-- Live Search Results Container -->
                    <div class="live-search-results" data-search-results style="display: none;">
                        <h4><?php _e('Search Results', 'stock-scanner'); ?></h4>
                        <div class="results-container"></div>
                    </div>
                </div>
            </form>
            
            <button class="search-close btn-icon glass" aria-label="<?php _e('Close search', 'stock-scanner'); ?>" data-search-close>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    </div>
</header>

<!-- Enhanced Progress Bar for Page Loading -->
<div class="page-loading-bar gradient-primary" aria-hidden="true" data-loading-bar></div>

<!-- Main Content Area -->
<main id="main" class="site-main" role="main" itemscope itemtype="https://schema.org/WebPageElement">