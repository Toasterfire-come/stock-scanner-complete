<?php if (!defined('ABSPATH')) { exit; } ?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https://*.paypal.com https://*.paypalobjects.com; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com 'self' data:; script-src 'self' 'unsafe-inline' https://www.paypal.com; connect-src 'self' https://*.paypal.com https://*.paypalobjects.com;" />
  <?php wp_head(); ?>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
</head>
<?php
  // Determine if this page should require auth (set by templates via global)
  global $finm_requires_auth;
  $requires_auth = isset($finm_requires_auth) ? (bool)$finm_requires_auth : false;
?>
<body <?php body_class(); ?> data-requires-auth="<?php echo $requires_auth ? 'true' : 'false'; ?>">
  <a class="screen-reader-text" href="#main">Skip to content</a>

  <header class="header" role="banner">
    <div class="container header-inner">
      <a class="brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="FinMarkets Home">
        <span class="brand-badge" aria-hidden="true"></span>
        <span>FinMarkets</span>
      </a>

      <!-- Expanding Search -->
      <form class="search" role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
        <button class="search-btn" aria-label="Search">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/></svg>
        </button>
        <input class="search-input" id="s" name="s" type="search" placeholder="Search…" autocomplete="off" />
      </form>

      <nav class="nav" aria-label="Main menu">
        <?php if (has_nav_menu('primary')) { wp_nav_menu(['theme_location'=>'primary','container'=>false,'items_wrap'=>'<ul>%3$s</ul>']); } else { ?>
          <a href="<?php echo esc_url(home_url('/#screener')); ?>">Screener</a>
          <a href="<?php echo esc_url(home_url('/#watchlist')); ?>">Watchlist</a>
          <a href="<?php echo esc_url(home_url('/#news')); ?>">News</a>
          <a href="<?php echo esc_url(home_url('/#pricing')); ?>">Pricing</a>
        <?php } ?>
      </nav>

      <div class="header-cta">
        <!-- Home icon (always visible) -->
        <a class="btn btn-ghost home-icon" href="<?php echo esc_url(home_url('/')); ?>" title="Home" aria-label="Home">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 10.5l9-7 9 7V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
        </a>
        <a id="signupLink" class="btn" href="<?php echo esc_url(home_url('/signup')); ?>">Sign up</a>
        <button id="themeToggle" class="btn" aria-pressed="false" title="Toggle theme">Dark Theme</button>
      </div>
    </div>

    <!-- Minimal header notice for guests on protected pages -->
    <div class="guest-banner" role="note" aria-live="polite">
      <span class="muted">You are not signed in.</span>
      <a class="btn btn-primary" href="<?php echo esc_url(home_url('/signup')); ?>">Create account</a>
      <a class="btn" href="<?php echo esc_url(home_url('/login')); ?>">Sign in</a>
    </div>
  </header>

  <main id="main">
</body>
</html>