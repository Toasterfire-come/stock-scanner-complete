<?php /** Footer with conditional links for guests/members */ ?>
<footer class="site-footer">
  <div class="container">
    <div class="footer-content">
      <div class="footer-section">
        <h4><?php echo esc_html(get_bloginfo('name')); ?></h4>
        <ul>
          <li><a href="<?php echo esc_url(home_url('/about/')); ?>"><?php esc_html_e('About', 'retail-trade-scanner'); ?></a></li>
          <li><a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact', 'retail-trade-scanner'); ?></a></li>
          <li><a href="<?php echo esc_url(home_url('/stock-market-news/')); ?>"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></a></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4><?php esc_html_e('Membership', 'retail-trade-scanner'); ?></h4>
        <ul>
          <?php if (!is_user_logged_in()) : ?>
            <li><a href="<?php echo esc_url(home_url('/membership-plans/')); ?>"><?php esc_html_e('Pricing Plans', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(wp_login_url()); ?>"><?php esc_html_e('Login', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(wp_registration_url()); ?>"><?php esc_html_e('Sign Up', 'retail-trade-scanner'); ?></a></li>
          <?php else: ?>
            <li><a href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(home_url('/membership-account/')); ?>"><?php esc_html_e('My Account', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(home_url('/membership-account/membership-checkout/')); ?>"><?php esc_html_e('Upgrade', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(home_url('/membership-orders/')); ?>"><?php esc_html_e('Billing History', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(home_url('/membership-billing/')); ?>"><?php esc_html_e('Invoices', 'retail-trade-scanner'); ?></a></li>
            <li><a href="<?php echo esc_url(home_url('/membership-account/membership-cancel/')); ?>"><?php esc_html_e('Cancel', 'retail-trade-scanner'); ?></a></li>
          <?php endif; ?>
        </ul>
      </div>
      <div class="footer-section">
        <h4><?php esc_html_e('Support', 'retail-trade-scanner'); ?></h4>
        <ul>
          <li><a href="<?php echo esc_url(home_url('/help/')); ?>"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></a></li>
          <li><a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></a></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4><?php esc_html_e('Connect', 'retail-trade-scanner'); ?></h4>
        <ul>
          <li><a href="#" rel="noopener">Twitter/X</a></li>
          <li><a href="#" rel="noopener">LinkedIn</a></li>
          <li><a href="#" rel="noopener">GitHub</a></li>
          <li><a href="#" rel="noopener">Discord</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <?php echo esc_html(wp_date('Y')); ?> <?php echo esc_html(get_bloginfo('name')); ?>. <?php esc_html_e('All rights reserved.', 'retail-trade-scanner'); ?></p>
    </div>
  </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>