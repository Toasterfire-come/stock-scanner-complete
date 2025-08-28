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
<a class="skip-link" href="#main-content"><?php esc_html_e('Skip to content', 'retail-trade-scanner'); ?></a>
<header class="site-header" role="banner">
    <div class="container">
        <div class="header-content">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="site-title">
                <?php if (function_exists('the_custom_logo') && has_custom_logo()) { 
                    the_custom_logo(); 
                } else { 
                    echo '📈 ' . esc_html(get_bloginfo('name')); 
                } ?>
            </a>
            <nav class="main-nav" role="navigation" aria-label="<?php esc_attr_e('Primary Navigation', 'retail-trade-scanner'); ?>">
                <?php
                $walker = class_exists('RetailTradeScanner_Nav_Walker') ? new RetailTradeScanner_Nav_Walker() : null;
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_class' => 'main-menu',
                    'fallback_cb' => 'retail_trade_scanner_fallback_menu',
                    'walker' => $walker
                ));
                ?>
            </nav>
            <div class="user-menu">
                <?php if (is_user_logged_in()): ?>
                    <?php
                    $user_level = 0;
                    if (function_exists('pmpro_getMembershipLevelForUser')) { 
                        $level = pmpro_getMembershipLevelForUser(get_current_user_id()); 
                        $user_level = $level ? intval($level->id) : 0; 
                    }
                    $level_names = array(
                        0 => __('Free', 'retail-trade-scanner'), 
                        1 => __('Free', 'retail-trade-scanner'), 
                        2 => __('Premium', 'retail-trade-scanner'), 
                        3 => __('Professional', 'retail-trade-scanner'), 
                        4 => __('Gold', 'retail-trade-scanner')
                    );
                    $level_classes = array(
                        0 => '', 
                        1 => '', 
                        2 => 'premium', 
                        3 => 'professional', 
                        4 => 'gold'
                    );
                    ?>
                    <span class="membership-badge <?php echo esc_attr(isset($level_classes[$user_level]) ? $level_classes[$user_level] : ''); ?>">
                        <?php echo esc_html(isset($level_names[$user_level]) ? $level_names[$user_level] : __('Member', 'retail-trade-scanner')); ?>
                    </span>
                    <span id="plan-badge" class="plan-badge" title="<?php esc_attr_e('Billing plan', 'retail-trade-scanner'); ?>">...</span>
                    <a id="refresh-plan" class="refresh-plan" href="#" title="<?php esc_attr_e('Refresh plan (hold Alt to reveal)', 'retail-trade-scanner'); ?>"><?php esc_html_e('Refresh Plan', 'retail-trade-scanner'); ?></a>
                    <a id="session-policy-link" class="session-policy-link" href="#" title="<?php esc_attr_e('View session policy', 'retail-trade-scanner'); ?>"><?php esc_html_e('Session policy', 'retail-trade-scanner'); ?></a>
                    <a id="session-data-link" class="session-data-link" href="#" title="<?php esc_attr_e('View session cookies & cache', 'retail-trade-scanner'); ?>"><?php esc_html_e('Session data', 'retail-trade-scanner'); ?></a>
                    <a id="clear-session-data" class="clear-session-data" href="#" title="<?php esc_attr_e('Clear cached session data', 'retail-trade-scanner'); ?>"><?php esc_html_e('Clear', 'retail-trade-scanner'); ?></a>
                    <span id="session-timer" class="session-timer" aria-live="polite" title="<?php esc_attr_e('Time remaining in session', 'retail-trade-scanner'); ?>"></span>
                    <a href="<?php echo esc_url(wp_logout_url(home_url())); ?>"><?php esc_html_e('Logout', 'retail-trade-scanner'); ?></a>
                <?php else: ?>
                    <a href="<?php echo esc_url(wp_login_url()); ?>"><?php esc_html_e('Login', 'retail-trade-scanner'); ?></a>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>"><?php esc_html_e('Sign Up', 'retail-trade-scanner'); ?></a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</header>