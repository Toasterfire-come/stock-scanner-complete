<?php
/**
 * Theme Footer
 */
?>
<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h4><?php echo esc_html(get_bloginfo('name')); ?></h4>
                <ul>
                    <li><a href="<?php echo esc_url(home_url('/about/')); ?>"><?php esc_html_e('About', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/stock-watchlist/')); ?>"><?php esc_html_e('Watchlist', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/stock-market-news/')); ?>"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/stock-alerts/')); ?>"><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4><?php esc_html_e('Membership', 'retail-trade-scanner'); ?></h4>
                <ul>
                    <li><a href="<?php echo esc_url(home_url('/membership-plans/')); ?>"><?php esc_html_e('Pricing Plans', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/membership-account/')); ?>"><?php esc_html_e('My Account', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/membership-account/membership-checkout/')); ?>"><?php esc_html_e('Upgrade', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/membership-account/membership-cancel/')); ?>"><?php esc_html_e('Cancel', 'retail-trade-scanner'); ?></a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4><?php esc_html_e('Support', 'retail-trade-scanner'); ?></h4>
                <ul>
                    <li><a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact Us', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/help/')); ?>"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/api-docs/')); ?>"><?php esc_html_e('API Documentation', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/privacy/')); ?>"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4><?php esc_html_e('Connect', 'retail-trade-scanner'); ?></h4>
                <ul>
                    <li><a href="#" rel="noopener"><?php esc_html_e('Twitter', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#" rel="noopener"><?php esc_html_e('LinkedIn', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#" rel="noopener"><?php esc_html_e('GitHub', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#" rel="noopener"><?php esc_html_e('Discord', 'retail-trade-scanner'); ?></a></li>
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