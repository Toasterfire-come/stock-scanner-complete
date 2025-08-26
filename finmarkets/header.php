<?php
/** Theme Header with Skip Link and ARIA nav */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header" role="banner">
    <div class="container">
        <div class="header-content">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="site-title">
                <?php if (function_exists('the_custom_logo') && has_custom_logo()) { the_custom_logo(); } else { echo '📈 ' . esc_html(get_bloginfo('name')); } ?>
            </a>
            <nav class="main-nav" role="navigation" aria-label="Primary Navigation">
                <?php
                $walker = class_exists('StockScanner_Nav_Walker') ? new StockScanner_Nav_Walker() : null;
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_class' => 'main-menu',
                    'fallback_cb' => 'stock_scanner_fallback_menu',
                    'walker' => $walker
                ));
                ?>
            </nav>
            <div class="user-menu">
                <?php if (is_user_logged_in()): ?>
                    <?php
                    $user_level = 0;
                    if (function_exists('pmpro_getMembershipLevelForUser')) { $level = pmpro_getMembershipLevelForUser(get_current_user_id()); $user_level = $level ? intval($level->id) : 0; }
                    $level_names = array(0 => 'Free', 1 => 'Free', 2 => 'Premium', 3 => 'Professional', 4 => 'Gold');
                    $level_classes = array(0 => '', 1 => '', 2 => 'premium', 3 => 'professional', 4 => 'gold');
                    ?>
                    <span class="membership-badge <?php echo esc_attr(isset($level_classes[$user_level]) ? $level_classes[$user_level] : ''); ?>"><?php echo esc_html(isset($level_names[$user_level]) ? $level_names[$user_level] : 'Member'); ?></span>
                    <span id="plan-badge" class="plan-badge" title="Billing plan">...</span>
                    <a id="refresh-plan" class="refresh-plan" href="#" title="Refresh plan (hold Alt to reveal)">Refresh Plan</a>
                    <a id="session-policy-link" class="session-policy-link" href="#" title="View session policy">Session policy</a>
                    <span id="session-timer" class="session-timer" aria-live="polite" title="Time remaining in session"></span>
                    <a href="<?php echo esc_url(wp_logout_url(home_url())); ?>">Logout</a>
                <?php else: ?>
                    <a href="<?php echo esc_url(wp_login_url()); ?>">Login</a>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>">Sign Up</a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</header>