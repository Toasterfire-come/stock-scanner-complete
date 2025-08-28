<?php
/** Sidebar: visible only to signed-in users; provides navigation */
if (!is_user_logged_in()) { return; }
?>
<aside class="site-sidebar" role="complementary" aria-label="<?php esc_attr_e('Sidebar Navigation', 'retail-trade-scanner'); ?>">
  <?php if (is_active_sidebar('primary-sidebar')): ?>
    <?php dynamic_sidebar('primary-sidebar'); ?>
  <?php else: ?>
    <nav class="sidebar-nav" aria-label="<?php esc_attr_e('Member navigation', 'retail-trade-scanner'); ?>">
      <ul class="sidebar-menu">
        <li><a class="top-link" href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/stock-watchlist/')); ?>"><?php esc_html_e('Watchlist', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/stock-search/')); ?>"><?php esc_html_e('Stock Search', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/membership-account/')); ?>"><?php esc_html_e('My Account', 'retail-trade-scanner'); ?></a></li>
      </ul>
    </nav>
  <?php endif; ?>
</aside>