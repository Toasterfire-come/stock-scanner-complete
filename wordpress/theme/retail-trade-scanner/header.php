<?php if (!defined('ABSPATH')) { exit; } ?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<header class="site-header">
  <div class="container" style="display:flex;align-items:center;justify-content:space-between;height:64px;">
    <a href="<?php echo esc_url(home_url('/')); ?>" class="logo" style="display:flex;gap:10px;align-items:center;text-decoration:none;color:inherit;">
      <span style="width:32px;height:32px;border-radius:10px;background:var(--accent);display:inline-block;"></span>
      <strong>Retail Trade Scanner</strong>
    </a>
    <nav class="nav" aria-label="Primary">
      <?php wp_nav_menu([ 'theme_location' => 'primary', 'container' => false, 'fallback_cb' => 'rts_menu_fallback', 'items_wrap' => '%3$s' ]); ?>
    </nav>
    <div style="display:flex;gap:10px;align-items:center;">
      <a class="btn btn-outline" href="<?php echo esc_url( wp_login_url() ); ?>">Sign in</a>
      <a class="btn btn-primary" href="<?php echo esc_url( site_url('/auth/sign-up') ); ?>">Get started</a>
    </div>
  </div>
</header>
<main class="site-main">