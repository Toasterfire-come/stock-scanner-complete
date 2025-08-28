<?php
/** Minimal Header: Home at left, guest navigation with icons, and Sign in/Upgrade on right */
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

      <?php if (!is_user_logged_in()) : ?>
      <nav class="guest-nav" role="navigation" aria-label="<?php esc_attr_e('Guest Navigation','retail-trade-scanner'); ?>">
        <ul class="main-menu icon-menu">
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>" title="<?php esc_attr_e('Scanner','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Scanner','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Scanner','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/stock-search/')); ?>" title="<?php esc_attr_e('Search','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Search','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Search','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/popular-stock-lists/')); ?>" title="<?php esc_attr_e('Popular Lists','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Popular Lists','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19V6l12-2v13"/><path d="M9 10l12-2"/><path d="M3 7h3v13H3z"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Popular','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/email-stock-lists/')); ?>" title="<?php esc_attr_e('Email Lists','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Email Lists','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4z"/><path d="M22 6l-10 7L2 6"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Email Lists','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/news-scraper/')); ?>" title="<?php esc_attr_e('News Scraper','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('News Scraper','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h8M7 16h6"/></svg>
              </span>
              <span class="label"><?php esc_html_e('News','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/personalized-stock-finder/')); ?>" title="<?php esc_attr_e('Finder','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Finder','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3 7 7 1-5 5 2 7-7-4-7 4 2-7-5-5 7-1z"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Finder','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/filter-and-scraper-pages/')); ?>" title="<?php esc_attr_e('Filters','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Filters','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12 10 19 14 21 14 12 22 3"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Filters','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/membership-plans/')); ?>" title="<?php esc_attr_e('Plans','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Plans','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15 8.5 22 9.3 17 14 18.5 21 12 17.8 5.5 21 7 14 2 9.3 9 8.5 12 2"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Plans','retail-trade-scanner'); ?></span>
            </a>
          </li>
          <li class="menu-item">
            <a class="icon-link" href="<?php echo esc_url(home_url('/contact/')); ?>" title="<?php esc_attr_e('Contact','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Contact','retail-trade-scanner'); ?>">
              <span class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 6-9 12-9 12S3 16 3 10a9 9 0 1 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              </span>
              <span class="label"><?php esc_html_e('Contact','retail-trade-scanner'); ?></span>
            </a>
          </li>
        </ul>
      </nav>
      <?php endif; ?>

      <div class="user-menu">
        <span id="plan-badge" class="plan-badge" aria-live="polite"></span>
        <?php if (is_user_logged_in()) : ?>
          <span id="session-timer" class="session-timer" title="<?php echo esc_attr__('Time remaining before auto-logout', 'retail-trade-scanner'); ?>">--:--</span>
          <a id="session-policy-link" class="session-policy-link" href="#"><?php esc_html_e('Session policy', 'retail-trade-scanner'); ?></a>
          <a id="session-data-link" class="session-data-link" href="#"><?php esc_html_e('Session data', 'retail-trade-scanner'); ?></a>
          <a id="clear-session-data" class="clear-session-data" href="#"><?php esc_html_e('Clear data', 'retail-trade-scanner'); ?></a>
          <a id="refresh-plan" class="refresh-plan" href="#" aria-hidden="true"><?php esc_html_e('Refresh Plan', 'retail-trade-scanner'); ?></a>
        <?php endif; ?>
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