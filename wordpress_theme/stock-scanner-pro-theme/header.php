<?php
/**
 * Header template
 *
 * @package StockScannerPro
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="theme-color" content="#0ea5e9">
    
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    
    <!-- Skip Link -->
    <a class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-md z-50" 
       href="#main">
        <?php _e('Skip to main content', 'stock-scanner-pro'); ?>
    </a>

    <!-- Header -->
    <header id="masthead" class="site-header bg-white border-b border-gray-200 sticky top-0 z-40 backdrop-blur-sm bg-white/95">
        <div class="container mx-auto">
            <div class="flex items-center justify-between h-16 px-4">
                
                <!-- Logo & Site Title -->
                <div class="site-branding flex items-center">
                    <?php if (has_custom_logo()) : ?>
                        <div class="custom-logo-link">
                            <?php the_custom_logo(); ?>
                        </div>
                    <?php else : ?>
                        <div class="site-title-group">
                            <h1 class="site-title text-xl font-bold text-gray-900">
                                <a href="<?php echo esc_url(home_url('/')); ?>" class="hover:text-blue-600 transition-colors">
                                    <?php bloginfo('name'); ?>
                                </a>
                            </h1>
                            <?php 
                            $description = get_bloginfo('description', 'display');
                            if ($description || is_customize_preview()) : ?>
                                <p class="site-description text-sm text-gray-600 mt-1">
                                    <?php echo $description; ?>
                                </p>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </div>

                <!-- Primary Navigation -->
                <nav id="site-navigation" class="main-navigation hidden lg:block" aria-label="<?php _e('Primary Navigation', 'stock-scanner-pro'); ?>">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_class' => 'primary-menu flex items-center space-x-8',
                        'container' => false,
                        'fallback_cb' => 'stock_scanner_default_menu',
                        'walker' => new Stock_Scanner_Nav_Walker(),
                    ));
                    ?>
                </nav>

                <!-- User Actions & Mobile Menu -->
                <div class="header-actions flex items-center space-x-4">
                    
                    <!-- Search Toggle -->
                    <button id="search-toggle" 
                            class="search-toggle p-2 text-gray-600 hover:text-gray-900 transition-colors"
                            aria-label="<?php _e('Toggle search', 'stock-scanner-pro'); ?>">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                        </svg>
                    </button>

                    <!-- Theme Toggle -->
                    <button id="theme-toggle" 
                            class="theme-toggle p-2 text-gray-600 hover:text-gray-900 transition-colors"
                            aria-label="<?php _e('Toggle dark mode', 'stock-scanner-pro'); ?>">
                        <svg class="w-5 h-5 dark-icon hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
                        </svg>
                        <svg class="w-5 h-5 light-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                        </svg>
                    </button>

                    <!-- User Menu -->
                    <?php if (is_user_logged_in()) : ?>
                        <div class="user-menu relative">
                            <button id="user-menu-toggle" 
                                    class="user-menu-toggle flex items-center space-x-2 p-2 rounded-md hover:bg-gray-100 transition-colors"
                                    aria-haspopup="true" 
                                    aria-expanded="false">
                                <?php echo get_avatar(get_current_user_id(), 32, '', '', array('class' => 'w-8 h-8 rounded-full')); ?>
                                <span class="hidden sm:block text-sm font-medium text-gray-700">
                                    <?php echo wp_get_current_user()->display_name; ?>
                                </span>
                                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                </svg>
                            </button>

                            <div id="user-menu-dropdown" 
                                 class="user-menu-dropdown absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 hidden"
                                 role="menu">
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('dashboard'))); ?>" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                                    <i class="fas fa-tachometer-alt w-4 mr-3 text-gray-400"></i>
                                    <?php _e('Dashboard', 'stock-scanner-pro'); ?>
                                </a>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('portfolio'))); ?>" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                                    <i class="fas fa-chart-line w-4 mr-3 text-gray-400"></i>
                                    <?php _e('Portfolio', 'stock-scanner-pro'); ?>
                                </a>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('watchlist'))); ?>" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                                    <i class="fas fa-eye w-4 mr-3 text-gray-400"></i>
                                    <?php _e('Watchlist', 'stock-scanner-pro'); ?>
                                </a>
                                <div class="border-t border-gray-100 my-1"></div>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('account-settings'))); ?>" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                                    <i class="fas fa-cog w-4 mr-3 text-gray-400"></i>
                                    <?php _e('Settings', 'stock-scanner-pro'); ?>
                                </a>
                                <a href="<?php echo wp_logout_url(home_url()); ?>" 
                                   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
                                    <i class="fas fa-sign-out-alt w-4 mr-3 text-gray-400"></i>
                                    <?php _e('Sign Out', 'stock-scanner-pro'); ?>
                                </a>
                            </div>
                        </div>
                    <?php else : ?>
                        <div class="auth-buttons flex items-center space-x-3">
                            <a href="<?php echo wp_login_url(get_permalink()); ?>" 
                               class="login-button text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
                                <?php _e('Sign In', 'stock-scanner-pro'); ?>
                            </a>
                            <a href="<?php echo wp_registration_url(); ?>" 
                               class="register-button bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-md transition-colors">
                                <?php _e('Get Started', 'stock-scanner-pro'); ?>
                            </a>
                        </div>
                    <?php endif; ?>

                    <!-- Mobile Menu Toggle -->
                    <button id="mobile-menu-toggle" 
                            class="mobile-menu-toggle lg:hidden p-2 text-gray-600 hover:text-gray-900"
                            aria-label="<?php _e('Toggle mobile menu', 'stock-scanner-pro'); ?>"
                            aria-controls="mobile-menu"
                            aria-expanded="false">
                        <svg class="w-6 h-6 hamburger-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                        </svg>
                        <svg class="w-6 h-6 close-icon hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Mobile Menu -->
            <div id="mobile-menu" class="mobile-menu lg:hidden hidden border-t border-gray-200">
                <nav class="mobile-navigation py-4" aria-label="<?php _e('Mobile Navigation', 'stock-scanner-pro'); ?>">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_class' => 'mobile-menu-list space-y-2',
                        'container' => false,
                        'fallback_cb' => 'stock_scanner_default_mobile_menu',
                        'walker' => new Stock_Scanner_Mobile_Nav_Walker(),
                    ));
                    ?>
                </nav>
            </div>

            <!-- Search Overlay -->
            <div id="search-overlay" class="search-overlay fixed inset-0 bg-black bg-opacity-50 z-50 hidden">
                <div class="search-container flex items-center justify-center min-h-screen p-4">
                    <div class="search-box bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">
                                <?php _e('Search Stocks', 'stock-scanner-pro'); ?>
                            </h3>
                            <button id="search-close" class="search-close text-gray-400 hover:text-gray-600">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                </svg>
                            </button>
                        </div>
                        
                        <form class="search-form" role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
                            <div class="relative">
                                <input type="search" 
                                       name="s" 
                                       class="search-field w-full px-4 py-3 pl-12 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                       placeholder="<?php _e('Search for stocks, news, or pages...', 'stock-scanner-pro'); ?>"
                                       value="<?php echo get_search_query(); ?>"
                                       autocomplete="off">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                                    </svg>
                                </div>
                            </div>
                            
                            <div class="search-suggestions mt-4 hidden">
                                <!-- Dynamic search suggestions will be loaded here -->
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Market Status Bar (for financial pages) -->
    <?php if (is_page_template('page-templates/page-dashboard.php') || 
              is_page_template('page-templates/page-market-overview.php') ||
              is_page_template('page-templates/page-portfolio.php')) : ?>
    
    <div id="market-status-bar" class="market-status-bar bg-gray-900 text-white py-2 text-sm">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
                    <div class="market-status flex items-center space-x-2">
                        <div class="status-indicator w-2 h-2 rounded-full bg-green-400"></div>
                        <span class="status-text"><?php _e('Markets Open', 'stock-scanner-pro'); ?></span>
                    </div>
                    
                    <div class="market-indices flex items-center space-x-4 text-xs">
                        <div class="index-item">
                            <span class="index-name font-medium">S&P 500:</span>
                            <span class="index-value font-mono">4,185.47</span>
                            <span class="index-change text-green-400">+0.85%</span>
                        </div>
                        <div class="index-item">
                            <span class="index-name font-medium">NASDAQ:</span>
                            <span class="index-value font-mono">12,972.05</span>
                            <span class="index-change text-red-400">-0.23%</span>
                        </div>
                    </div>
                </div>
                
                <div class="market-time text-xs">
                    <span id="market-time-display">
                        <?php echo current_time('g:i A T'); ?>
                    </span>
                </div>
            </div>
        </div>
    </div>
    
    <?php endif; ?>

    <!-- Main Content Area -->
    <div id="content" class="site-content">