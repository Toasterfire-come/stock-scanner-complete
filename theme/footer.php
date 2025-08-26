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
                    <li><a href="/about/">About</a></li>
                    <li><a href="/contact/">Contact</a></li>
                    <li><a href="/stock-dashboard/">Dashboard</a></li>
                    <li><a href="/stock-watchlist/">Watchlist</a></li>
                    <li><a href="/stock-market-news/">Market News</a></li>
                    <li><a href="/stock-alerts/">Alerts</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Membership</h4>
                <ul>
                    <li><a href="/membership-plans/">Pricing Plans</a></li>
                    <li><a href="/membership-account/">My Account</a></li>
                    <li><a href="/membership-account/membership-checkout/">Upgrade</a></li>
                    <li><a href="/membership-account/membership-cancel/">Cancel</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Support</h4>
                <ul>
                    <li><a href="/contact/">Contact Us</a></li>
                    <li><a href="/help/">Help Center</a></li>
                    <li><a href="/api-docs/">API Documentation</a></li>
                    <li><a href="/privacy/">Privacy Policy</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Connect</h4>
                <ul>
                    <li><a href="#">Twitter</a></li>
                    <li><a href="#">LinkedIn</a></li>
                    <li><a href="#">GitHub</a></li>
                    <li><a href="#">Discord</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; <?php echo esc_html(wp_date('Y')); ?> <?php echo esc_html(get_bloginfo('name')); ?>. <?php _e('All rights reserved.', 'finmarkets'); ?></p>
        </div>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>