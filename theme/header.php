<?php
/** Minimal Header: Home at left, Sign in (guests) or Upgrade (members) at right */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#main-content"><?php esc_html_e('Skip to content','retail-trade-scanner'); ?></a>
<header class="site-header" role="banner">
  <div class="container">
    <div class="header-content">
      <a href="<?php echo esc_url(home_url('/')); ?>" class="site-title"><?php if(function_exists('the_custom_logo') && has_custom_logo()){ the_custom_logo(); } else { echo '📈 ' . esc_html(get_bloginfo('name')); } ?></a>
      <div class="user-menu">
        <?php if (is_user_logged_in()) : ?>
          <?php if (get_theme_mod('rts_show_upgrade', true)) : ?>
            <a class="btn btn-gold" href="<?php echo esc_url(home_url('/membership-account/membership-checkout/')); ?>"><?php esc_html_e('Upgrade','retail-trade-scanner'); ?></a>
          <?php endif; ?>
          <a class="btn btn-secondary" href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>"><?php esc_html_e('Logout','retail-trade-scanner'); ?></a>
        <?php else: ?>
          <a class="btn btn-primary" href="<?php echo esc_url(wp_login_url()); ?>"><?php esc_html_e('Sign in','retail-trade-scanner'); ?></a>
        <?php endif; ?>
      </div>
    </div>
  </div>
</header>