<?php
/**
 * Sidebar template - visible only to signed-in users
 * If no widgets are configured, show a smart fallback navigation.
 */
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
        <li><a class="top-link" href="<?php echo esc_url(home_url('/stock-alerts/')); ?>"><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/stock-market-news/')); ?>"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/membership-account/')); ?>"><?php esc_html_e('My Account', 'retail-trade-scanner'); ?></a></li>
        <li><a class="top-link" href="<?php echo esc_url(home_url('/membership-account/membership-checkout/')); ?>"><?php esc_html_e('Upgrade', 'retail-trade-scanner'); ?></a></li>
      </ul>
    </nav>
  <?php endif; ?>
</aside>