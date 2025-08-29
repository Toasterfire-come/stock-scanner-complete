<?php
/**
 * The header for our theme
 *
 * @package RetailTradeScanner
 */

?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="skip-link sr-only" href="#main"><?php esc_html_e('Skip to main content', 'retail-trade-scanner'); ?></a>

<div class="site-container">
    <header class="site-header glass-card" role="banner">
        <div class="container">
            <div class="header-content flex items-center justify-between">
                <!-- Logo -->
                <div class="site-branding">
                    <?php if (has_custom_logo()) : ?>
                        <div class="site-logo">
                            <?php the_custom_logo(); ?>
                        </div>
                    <?php else : ?>
                        <h1 class="site-title">
                            <a href="<?php echo esc_url(home_url('/')); ?>" rel="home" class="site-title-link">
                                <?php echo rts_get_icon('scanner', ['class' => 'site-logo-icon', 'width' => '32', 'height' => '32']); ?>
                                <?php bloginfo('name'); ?>
                            </a>
                        </h1>
                    <?php endif; ?>
                </div>

                <!-- Main Navigation -->
                <nav class="main-navigation" role="navigation" aria-label="<?php esc_attr_e('Main Navigation', 'retail-trade-scanner'); ?>">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_class' => 'main-menu flex items-center gap-lg',
                        'container' => false,
                        'fallback_cb' => 'retail_trade_scanner_fallback_menu',
                        'depth' => 2,
                        'walker' => new Retail_Trade_Scanner_Walker_Nav_Menu(),
                    ));
                    ?>
                    
                    <!-- Mobile Menu Toggle -->
                    <button class="mobile-menu-toggle btn-icon btn-ghost" aria-expanded="false" aria-controls="main-menu" aria-label="<?php esc_attr_e('Toggle mobile menu', 'retail-trade-scanner'); ?>">
                        <span class="hamburger">
                            <span></span>
                            <span></span>
                            <span></span>
                        </span>
                    </button>
                </nav>

                <!-- User Actions -->
                <div class="header-actions flex items-center gap-md">
                    <!-- Search -->
                    <div class="header-search">
                        <button class="search-toggle btn-icon btn-ghost" aria-label="<?php esc_attr_e('Open search', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
                        </button>
                    </div>

                    <?php if (is_user_logged_in()) : ?>
                        <!-- Notifications -->
                        <div class="notifications">
                            <button class="notifications-toggle btn-icon btn-ghost" aria-label="<?php esc_attr_e('Notifications', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('alerts', ['width' => '20', 'height' => '20']); ?>
                                <span class="notification-badge">3</span>
                            </button>
                        </div>

                        <!-- User Menu -->
                        <div class="user-menu">
                            <button class="user-menu-toggle btn-ghost flex items-center gap-sm" aria-expanded="false" aria-haspopup="true">
                                <img class="user-avatar" src="<?php echo esc_url(get_avatar_url(get_current_user_id(), ['size' => 32])); ?>" alt="<?php esc_attr_e('User Avatar', 'retail-trade-scanner'); ?>" width="32" height="32">
                                <span class="user-name"><?php echo esc_html(wp_get_current_user()->display_name); ?></span>
                                <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            
                            <div class="user-dropdown glass-card hidden" role="menu">
                                <a href="<?php echo esc_url(admin_url('profile.php')); ?>" class="dropdown-item" role="menuitem">
                                    <?php echo rts_get_icon('settings', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Profile', 'retail-trade-scanner'); ?>
                                </a>
                                <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="dropdown-item" role="menuitem">
                                    <?php echo rts_get_icon('portfolio', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?>
                                </a>
                                <a href="<?php echo esc_url(wp_logout_url(home_url())); ?>" class="dropdown-item" role="menuitem">
                                    <?php echo rts_get_icon('logout', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Sign Out', 'retail-trade-scanner'); ?>
                                </a>
                            </div>
                        </div>
                    <?php else : ?>
                        <!-- Sign In Button -->
                        <a href="<?php echo esc_url(wp_login_url()); ?>" class="btn btn-primary btn-magnetic">
                            <?php esc_html_e('Sign In', 'retail-trade-scanner'); ?>
                        </a>
                    <?php endif; ?>

                    <!-- Theme Toggle -->
                    <button class="theme-toggle btn-icon btn-ghost" aria-label="<?php esc_attr_e('Toggle dark mode', 'retail-trade-scanner'); ?>">
                        <span class="theme-toggle-sun"><?php echo rts_get_icon('sun', ['width' => '20', 'height' => '20']); ?></span>
                        <span class="theme-toggle-moon hidden"><?php echo rts_get_icon('moon', ['width' => '20', 'height' => '20']); ?></span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Search Modal -->
        <div class="search-modal hidden" role="dialog" aria-modal="true" aria-labelledby="search-title">
            <div class="search-modal-backdrop"></div>
            <div class="search-modal-content glass-card">
                <div class="search-modal-header">
                    <h2 id="search-title" class="sr-only"><?php esc_html_e('Search', 'retail-trade-scanner'); ?></h2>
                    <button class="search-modal-close btn-icon btn-ghost" aria-label="<?php esc_attr_e('Close search', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('close', ['width' => '24', 'height' => '24']); ?>
                    </button>
                </div>
                <div class="search-modal-body">
                    <?php get_search_form(); ?>
                    <div class="search-suggestions">
                        <div class="search-category">
                            <h3><?php esc_html_e('Popular Searches', 'retail-trade-scanner'); ?></h3>
                            <div class="search-tags">
                                <button class="search-tag">AAPL</button>
                                <button class="search-tag">TSLA</button>
                                <button class="search-tag">NVDA</button>
                                <button class="search-tag">S&P 500</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Sidebar for authenticated users -->
    <?php if (is_user_logged_in()) : ?>
        <aside class="sidebar glass-card" role="complementary" aria-label="<?php esc_attr_e('Main Navigation', 'retail-trade-scanner'); ?>">
            <div class="sidebar-content">
                <nav class="sidebar-nav" role="navigation">
                    <div class="nav-section">
                        <h3 class="nav-section-title"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></h3>
                        <ul class="nav-menu">
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="nav-link <?php echo (is_page('dashboard')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('dashboard', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('Overview', 'retail-trade-scanner'); ?></span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="nav-link <?php echo (is_page('scanner')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('Scanner', 'retail-trade-scanner'); ?></span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/watchlists/')); ?>" class="nav-link <?php echo (is_page('watchlists')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('watchlist', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('Watchlists', 'retail-trade-scanner'); ?></span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="nav-link <?php echo (is_page('portfolio')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('portfolio', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></span>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <div class="nav-section">
                        <h3 class="nav-section-title"><?php esc_html_e('Tools', 'retail-trade-scanner'); ?></h3>
                        <ul class="nav-menu">
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="nav-link <?php echo (is_page('alerts')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('alerts', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></span>
                                    <span class="nav-badge">2</span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="<?php echo esc_url(home_url('/news/')); ?>" class="nav-link <?php echo (is_page('news')) ? 'is-active' : ''; ?>">
                                    <?php echo rts_get_icon('news', ['width' => '20', 'height' => '20']); ?>
                                    <span class="nav-label"><?php esc_html_e('News', 'retail-trade-scanner'); ?></span>
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>

                <!-- Sidebar Footer -->
                <div class="sidebar-footer">
                    <button class="sidebar-collapse-toggle btn-ghost" aria-label="<?php esc_attr_e('Collapse sidebar', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('chevron-left', ['width' => '20', 'height' => '20']); ?>
                    </button>
                </div>
            </div>
        </aside>
    <?php endif; ?>

    <!-- Main Content Container -->
    <main id="main" class="main-content" role="main">