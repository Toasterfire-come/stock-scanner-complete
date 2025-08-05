<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
                            
                            <div class="user-menu">
                                <a href="/dashboard/" class="user-menu-item">
                                    <span class="item-icon">📊</span>
                                    Dashboard
                                </a>
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
                    <div class="auth-buttons">
                        <a href="<?php echo wp_login_url(); ?>" class="btn btn-outline">Login</a>
                        <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary">Sign Up Free</a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </header>

    <div id="content" class="site-content">

<style>
/* Professional Header Styling with WordPress Admin Colors */
.site-header {
    background: var(--wp-admin-background, #f0f0f1);
    border-bottom: 1px solid #c3c4c7;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 70px;
}

/* Site Branding */
.site-branding {
    flex-shrink: 0;
}

.site-logo {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: var(--wp-admin-blue, #2271b1);
    font-weight: 700;
    font-size: 1.4rem;
    transition: opacity 0.3s ease;
}

.site-logo:hover {
    opacity: 0.8;
}

.logo-icon {
    font-size: 1.8rem;
    margin-right: 8px;
}

.site-description {
    margin: 0;
    font-size: 0.85rem;
    color: var(--wp-admin-gray, #646970);
    max-width: 200px;
    line-height: 1.3;
}

/* Navigation */
.main-navigation {
    flex: 1;
    margin: 0 40px;
}

.menu-toggle {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    padding: 10px;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.hamburger-line {
    width: 25px;
    height: 3px;
    background: var(--wp-admin-blue, #2271b1);
    transition: all 0.3s ease;
}

.menu-text {
    font-size: 0.75rem;
    color: var(--wp-admin-gray, #646970);
    margin-top: 2px;
}

.primary-menu {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 30px;
    align-items: center;
}

.primary-menu li a {
    color: var(--wp-admin-gray, #646970);
    text-decoration: none;
    font-weight: 500;
    padding: 10px 0;
    position: relative;
    transition: color 0.3s ease;
}

.primary-menu li a:hover,
.primary-menu li.current-menu-item a {
    color: var(--wp-admin-blue, #2271b1);
}

.primary-menu li a::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--wp-admin-blue, #2271b1);
    transition: width 0.3s ease;
}

.primary-menu li a:hover::after,
.primary-menu li.current-menu-item a::after {
    width: 100%;
}

/* User Info Section */
.user-info {
    display: flex;
    align-items: center;
    gap: 15px;
}

.membership-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.membership-free {
    background: var(--wp-admin-gray, #646970);
    color: white;
}

.membership-bronze {
    background: #cd7f32;
    color: white;
}

.membership-silver {
    background: #c0c0c0;
    color: #333;
}

.membership-gold {
    background: #ffd700;
    color: #333;
}

/* Usage Indicator */
.usage-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.usage-text {
    font-size: 0.75rem;
    color: var(--wp-admin-gray, #646970);
    font-weight: 500;
}

.usage-bar {
    width: 40px;
    height: 4px;
    background: #e1e1e1;
    border-radius: 2px;
    overflow: hidden;
}

.usage-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.3s ease;
}

.usage-normal {
    background: var(--wp-admin-green, #00a32a);
}

.usage-warning {
    background: var(--wp-admin-yellow, #dba617);
}

.usage-critical {
    background: var(--wp-admin-red, #d63638);
}

/* User Dropdown */
.user-dropdown {
    position: relative;
}

.user-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 6px;
    transition: background 0.3s ease;
}

.user-toggle:hover {
    background: rgba(0,0,0,0.05);
}

.user-avatar {
    font-size: 1.2rem;
}

.user-name {
    font-weight: 500;
    color: var(--wp-admin-gray, #646970);
}

.dropdown-arrow {
    font-size: 0.7rem;
    color: var(--wp-admin-gray, #646970);
    transition: transform 0.3s ease;
}

.user-toggle[aria-expanded="true"] .dropdown-arrow {
    transform: rotate(180deg);
}

.user-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #c3c4c7;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    min-width: 200px;
    padding: 8px 0;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
    z-index: 1000;
}

.user-toggle[aria-expanded="true"] + .user-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.user-menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    color: var(--wp-admin-gray, #646970);
    text-decoration: none;
    transition: background 0.3s ease;
}

.user-menu-item:hover {
    background: #f6f7f7;
    color: var(--wp-admin-blue, #2271b1);
}

.upgrade-link {
    color: var(--wp-admin-blue, #2271b1) !important;
}

.logout-link {
    color: var(--wp-admin-red, #d63638) !important;
}

.menu-divider {
    margin: 8px 0;
    border: none;
    border-top: 1px solid #f0f0f1;
}

.item-icon {
    font-size: 0.9rem;
}

/* Auth Buttons */
.auth-buttons {
    display: flex;
    gap: 10px;
    align-items: center;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.btn-outline {
    color: var(--wp-admin-blue, #2271b1);
    border-color: var(--wp-admin-blue, #2271b1);
}

.btn-outline:hover {
    background: var(--wp-admin-blue, #2271b1);
    color: white;
}

.btn-primary {
    background: var(--wp-admin-blue, #2271b1);
    color: white;
}

.btn-primary:hover {
    background: #135e96;
}

/* Mobile Responsiveness */
@media (max-width: 1024px) {
    .header-container {
        padding: 0 15px;
    }
    
    .main-navigation {
        margin: 0 20px;
    }
    
    .primary-menu {
        gap: 20px;
    }
}

@media (max-width: 768px) {
    .header-container {
        flex-wrap: wrap;
        min-height: 60px;
    }
    
    .menu-toggle {
        display: flex;
        order: 3;
    }
    
    .main-navigation {
        order: 4;
        flex: 100%;
        margin: 0;
    }
    
    .nav-menu-wrapper {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    
    .menu-toggle[aria-expanded="true"] + .nav-menu-wrapper {
        max-height: 400px;
        padding: 20px 0;
    }
    
    .primary-menu {
        flex-direction: column;
        gap: 0;
        background: white;
        border: 1px solid #e1e1e1;
        border-radius: 6px;
        padding: 10px 0;
        margin-top: 10px;
    }
    
    .primary-menu li {
        width: 100%;
    }
    
    .primary-menu li a {
        display: block;
        padding: 12px 20px;
        border-bottom: 1px solid #f0f0f1;
    }
    
    .primary-menu li:last-child a {
        border-bottom: none;
    }
    
    .site-description {
        display: none;
    }
    
    .user-info {
        gap: 10px;
        order: 2;
    }
    
    .usage-indicator {
        display: none;
    }
    
    .user-name {
        display: none;
    }
}

@media (max-width: 480px) {
    .header-container {
        padding: 0 10px;
    }
    
    .logo-text {
        font-size: 1.1rem;
    }
    
    .auth-buttons {
        flex-direction: column;
        gap: 5px;
    }
    
    .btn {
        padding: 6px 12px;
        font-size: 0.8rem;
    }
}

/* Accessibility */
.skip-link {
    background: var(--wp-admin-blue, #2271b1);
    color: white;
    padding: 8px 16px;
    position: absolute;
    top: -40px;
    left: 6px;
    z-index: 100000;
    text-decoration: none;
    transition: top 0.3s ease;
}

.skip-link:focus {
    top: 7px;
}

.screen-reader-text {
    border: 0;
    clip: rect(1px, 1px, 1px, 1px);
    clip-path: inset(50%);
    height: 1px;
    margin: -1px;
    overflow: hidden;
    padding: 0;
    position: absolute !important;
    width: 1px;
    word-wrap: normal !important;
}

/* Animation for hamburger menu */
.menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(1) {
    transform: rotate(45deg) translate(6px, 6px);
}

.menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(2) {
    opacity: 0;
}

.menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(3) {
    transform: rotate(-45deg) translate(6px, -6px);
}
</style>

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
});
</script>