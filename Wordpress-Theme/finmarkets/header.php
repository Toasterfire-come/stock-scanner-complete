<?php if (!defined('ABSPATH')) { exit; } ?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com 'self' data:; script-src 'self'; connect-src 'self';" />
  <?php wp_head(); ?>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
</head>
<body <?php body_class(); ?>>
  <a class="screen-reader-text" href="#main">Skip to content</a>
  <header class="header" role="banner">
    <div class="container header-inner" role="navigation" aria-label="Primary">
      <a class="brand" href="<?php echo esc_url(home_url('/')); ?>">
        <span class="brand-badge" aria-hidden="true"></span>
        <span>FinMarkets</span>
      </a>
      <nav class="nav" aria-label="Main menu">
        <?php wp_nav_menu([
          'theme_location' => 'primary',
          'container' => false,
          'items_wrap' => '%3$s',
          'link_before' => '',
          'link_after' => '',
          'fallback_cb' => false
        ]); ?>
        <a href="#screener">Screener</a>
        <a href="#watchlist">Watchlist</a>
        <a href="#news">News</a>
        <a href="#pricing">Pricing</a>
      </nav>
      <div>
        <button class="btn" id="loginBtn" aria-haspopup="dialog">Sign in</button>
        <a class="btn btn-primary" href="#pricing">Get Pro</a>
      </div>
    </div>
  </header>
  <main id="main">