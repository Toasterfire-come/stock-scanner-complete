<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="wp-nonce" content="<?php echo esc_attr( wp_create_nonce('wp_rest') ); ?>">
    <?php 
    // SEO: Canonical URL
    if (function_exists('wp_get_canonical_url')) {
        $canonical = wp_get_canonical_url();
    } else {
        $canonical = is_singular() ? get_permalink() : home_url(add_query_arg(array(),$wp->request));
    }
    if ($canonical): ?>
        <link rel="canonical" href="<?php echo esc_url($canonical); ?>" />
    <?php endif; ?>
    <?php 
        // SEO: Open Graph and Twitter
        global $post;
        $site_name = get_bloginfo('name');
        $title = wp_get_document_title();
        $description = get_bloginfo('description');
        if (is_singular() && isset($post)) {
            $excerpt = has_excerpt($post) ? get_the_excerpt($post) : wp_strip_all_tags(get_the_content(null, false, $post));
            if (!empty($excerpt)) { $description = wp_trim_words($excerpt, 30); }
        }
        $url = $canonical ? $canonical : home_url();
        $image = '';
        if (is_singular() && has_post_thumbnail($post)) {
            $img = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'full');
            if (!empty($img[0])) { $image = $img[0]; }
        }
        if (empty($image)) {
            // Fallback theme image if exists
            $fallback = get_template_directory_uri() . '/assets/images/og-default.jpg';
            $image = $fallback;
        }
    ?>
    <meta property="og:site_name" content="<?php echo esc_attr($site_name); ?>" />
    <meta property="og:title" content="<?php echo esc_attr($title); ?>" />
    <meta property="og:description" content="<?php echo esc_attr($description); ?>" />
    <meta property="og:url" content="<?php echo esc_url($url); ?>" />
    <meta property="og:type" content="<?php echo is_singular() ? 'article' : 'website'; ?>" />
    <meta property="og:image" content="<?php echo esc_url($image); ?>" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="<?php echo esc_attr($title); ?>" />
    <meta name="twitter:description" content="<?php echo esc_attr($description); ?>" />
    <meta name="twitter:image" content="<?php echo esc_url($image); ?>" />
        <link rel="manifest" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/manifest.webmanifest' ); ?>">
    <?php wp_head(); ?>
  </head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Skip to content', 'stock-scanner'); ?></a>

    <header id="masthead" class="site-header">
        <div class="header-container">
            <div class="site-branding">
                <a href="<?php echo esc_url(home_url('/')); ?>" class="site-logo">
                    <span class="logo-icon">📈</span>
                    <span class="logo-text"><?php bloginfo('name'); ?></span>
                </a>
                <?php
                $description = get_bloginfo('description', 'display');
                if ($description || is_customize_preview()): ?>
                    <p class="site-description"><?php echo $description; ?></p>
                <?php endif; ?>
            </div>

            <nav id="site-navigation" class="main-navigation">
                <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="menu-text"><?php esc_html_e('Menu', 'stock-scanner'); ?></span>
                </button>
                
                <div class="nav-menu-wrapper">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_id'        => 'primary-menu',
                        'menu_class'     => 'primary-menu',
                        'container'      => false,
                        'fallback_cb'    => 'stock_scanner_fallback_menu',
                        'walker'         => new Stock_Scanner_Nav_Walker()
                    ));
                    ?>
                </div>
            </nav>

            <div class="header-actions">
                <?php if (is_user_logged_in()): ?>
                    <?php
                    $user = wp_get_current_user();
                    $membership_level = function_exists('get_user_membership_level') ? get_user_membership_level() : 'free';
                    $usage = function_exists('get_user_api_usage') ? get_user_api_usage() : array('monthly_calls' => 0, 'monthly_limit' => 15);
                    ?>
                    
                    <div class="user-info">
                        <div class="membership-badge membership-<?php echo esc_attr($membership_level); ?>">
                            <?php echo ucfirst($membership_level); ?>
                        </div>
                        
                        <div class="usage-indicator">
                            <span class="usage-text">
                                <?php echo esc_html($usage['monthly_calls']); ?>/<?php echo $usage['monthly_limit'] === -1 ? '∞' : esc_html($usage['monthly_limit']); ?>
                            </span>
                            <div class="usage-bar">
                                <?php 
                                $percentage = $usage['monthly_limit'] > 0 ? ($usage['monthly_calls'] / $usage['monthly_limit']) * 100 : 0;
                                $bar_class = $percentage >= 90 ? 'usage-critical' : ($percentage >= 75 ? 'usage-warning' : 'usage-normal');
                                ?>
                                <div class="usage-fill <?php echo $bar_class; ?>" style="width: <?php echo min(100, $percentage); ?>%"></div>
                            </div>
                        </div>
                        
                        <div class="user-dropdown">
                            <button class="user-toggle" aria-expanded="false">
                                <span class="user-avatar">👤</span>
                                <span class="user-name"><?php echo esc_html($user->display_name); ?></span>
                                <span class="dropdown-arrow">▼</span>
                            </button>
                            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme" aria-label="Toggle theme">🌓</button>
                            
                            <div class="user-menu">
                                <a href="/dashboard/" class="user-menu-item">
                                    <span class="item-icon">📊</span>
                                    Dashboard
                                </a>
                                <hr class="menu-divider">
                                <a href="/portfolio/" class="user-menu-item">
                                    <span class="item-icon">📈</span>
                                    My Portfolios
                                </a>
                                <a href="/watchlist/" class="user-menu-item">
                                    <span class="item-icon">👁️</span>
                                    Watchlist
                                </a>
                                <a href="/personalized-news/" class="user-menu-item">
                                    <span class="item-icon">📰</span>
                                    My News Feed
                                </a>
                                <hr class="menu-divider">
                                <a href="/account/" class="user-menu-item">
                                    <span class="item-icon">⚙️</span>
                                    Account Settings
                                </a>
                                <?php if ($membership_level === 'free'): ?>
                                <a href="/premium-plans/" class="user-menu-item upgrade-link">
                                    <span class="item-icon">⭐</span>
                                    Upgrade Plan
                                </a>
                                <?php endif; ?>
                                <hr class="menu-divider">
                                <a href="<?php echo wp_logout_url(home_url()); ?>" class="user-menu-item logout-link">
                                    <span class="item-icon">🚪</span>
                                    Logout
                                </a>
                            </div>
                        </div>
                    </div>
                <?php else: ?>
                    <div class="auth-links">
                        <a class="login-link" href="<?php echo esc_url(wp_login_url()); ?>"><?php esc_html_e('Log in', 'stock-scanner'); ?></a>
                        <a class="signup-link" href="<?php echo esc_url(wp_registration_url()); ?>"><?php esc_html_e('Sign up', 'stock-scanner'); ?></a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </header>

    <div id="content" class="site-content">


<script>
// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const userToggle = document.querySelector('.user-toggle');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const expanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !expanded);
        });
    }
    
    if (userToggle) {
        userToggle.addEventListener('click', function() {
            const expanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !expanded);
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userToggle.contains(e.target)) {
                userToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // Mobile menu toggle functionality (unified design)
    const mobileMenuToggle = document.querySelector('.menu-toggle');
    const mainNavigation = document.querySelector('.main-navigation');
    
    if (mobileMenuToggle && mainNavigation) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNavigation.classList.toggle('active');
            const expanded = mainNavigation.classList.contains('active');
            this.setAttribute('aria-expanded', expanded);
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenuToggle.contains(e.target) && !mainNavigation.contains(e.target)) {
                mainNavigation.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Close mobile menu when clicking on a link
        const menuLinks = mainNavigation.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mainNavigation.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }
});
</script>