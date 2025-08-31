<?php if (!defined('ABSPATH')) { exit; } ?><!doctype html>
<html <?php language_attributes(); ?> data-theme="<?php echo esc_attr( get_user_setting('rts_theme','light') ); ?>">
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
      <button id="rts-theme-toggle" class="btn btn-outline" type="button">Toggle theme</button>
      <a class="btn btn-outline" href="<?php echo esc_url( wp_login_url() ); ?>">Sign in</a>
      <a class="btn btn-primary" href="<?php echo esc_url( site_url('/auth/sign-up') ); ?>">Get started</a>
    </div>
  </div>
</header>
<main class="site-main">
<script>
(function(){
  var btn = document.getElementById('rts-theme-toggle'); if(!btn) return;
  btn.addEventListener('click', function(){
    var html = document.documentElement; var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    try { window.localStorage.setItem('rts-theme', next); } catch(e){}
  });
  try { var saved = localStorage.getItem('rts-theme'); if(saved){ document.documentElement.setAttribute('data-theme', saved); } } catch(e){}
})();
</script>