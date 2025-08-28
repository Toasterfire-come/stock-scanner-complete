<?php
/** Sidebar: visible only to signed-in users; provides icon navigation */
if (!is_user_logged_in()) { return; }
?>
<aside class="site-sidebar" role="complementary" aria-label="<?php esc_attr_e('Sidebar Navigation', 'retail-trade-scanner'); ?>">
  <?php if (is_active_sidebar('primary-sidebar')): ?>
    <?php dynamic_sidebar('primary-sidebar'); ?>
  <?php else: ?>
    <nav class="sidebar-nav" aria-label="<?php esc_attr_e('Member navigation', 'retail-trade-scanner'); ?>">
      <ul class="sidebar-menu">
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>" title="<?php esc_attr_e('Dashboard','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Dashboard','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h7v7H3zM14 3h7v4h-7zM14 12h7v9h-7zM3 14h7v7H3z"/></svg></span>
          <span class="label"><?php esc_html_e('Dashboard','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/stock-watchlist/')); ?>" title="<?php esc_attr_e('Watchlist','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Watchlist','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></span>
          <span class="label"><?php esc_html_e('Watchlist','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/stock-search/')); ?>" title="<?php esc_attr_e('Search','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Search','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></span>
          <span class="label"><?php esc_html_e('Search','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/popular-stock-lists/')); ?>" title="<?php esc_attr_e('Popular Lists','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Popular Lists','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19V6l12-2v13"/><path d="M9 10l12-2"/><path d="M3 7h3v13H3z"/></svg></span>
          <span class="label"><?php esc_html_e('Popular','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/email-stock-lists/')); ?>" title="<?php esc_attr_e('Email Lists','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Email Lists','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4z"/><path d="M22 6l-10 7L2 6"/></svg></span>
          <span class="label"><?php esc_html_e('Email Lists','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/news-scraper/')); ?>" title="<?php esc_attr_e('News Scraper','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('News Scraper','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h8M7 16h6"/></svg></span>
          <span class="label"><?php esc_html_e('News','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/personalized-stock-finder/')); ?>" title="<?php esc_attr_e('Finder','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Finder','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3 7 7 1-5 5 2 7-7-4-7 4 2-7-5-5 7-1z"/></svg></span>
          <span class="label"><?php esc_html_e('Finder','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/filter-and-scraper-pages/')); ?>" title="<?php esc_attr_e('Filters','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Filters','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12 10 19 14 21 14 12 22 3"/></svg></span>
          <span class="label"><?php esc_html_e('Filters','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/membership-account/')); ?>" title="<?php esc_attr_e('My Account','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('My Account','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span>
          <span class="label"><?php esc_html_e('My Account','retail-trade-scanner'); ?></span></a></li>
      </ul>
    </nav>
  <?php endif; ?>
</aside>