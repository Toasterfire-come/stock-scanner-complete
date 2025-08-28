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
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/stock-alerts/')); ?>" title="<?php esc_attr_e('Alerts','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('Alerts','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg></span>
          <span class="label"><?php esc_html_e('Alerts','retail-trade-scanner'); ?></span></a></li>
        <li><a class="icon-link" href="<?php echo esc_url(home_url('/membership-account/')); ?>" title="<?php esc_attr_e('My Account','retail-trade-scanner'); ?>" data-title="<?php esc_attr_e('My Account','retail-trade-scanner'); ?>">
          <span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span>
          <span class="label"><?php esc_html_e('My Account','retail-trade-scanner'); ?></span></a></li>
      </ul>
    </nav>
  <?php endif; ?>
</aside>