    </main><!-- #primary -->

    <footer id="colophon" class="site-footer" role="contentinfo">
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-section footer-about">
                    <h3><?php bloginfo('name'); ?></h3>
                    <p><?php bloginfo('description'); ?></p>
                    <div class="footer-social">
                        <a href="#" aria-label="Twitter" rel="noopener"><i class="fab fa-twitter"></i></a>
                        <a href="#" aria-label="LinkedIn" rel="noopener"><i class="fab fa-linkedin"></i></a>
                        <a href="#" aria-label="Facebook" rel="noopener"><i class="fab fa-facebook"></i></a>
                    </div>
                </div>
                
                <div class="footer-section footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="<?php echo esc_url(home_url('/market-overview/')); ?>">Market Overview</a></li>
                        <li><a href="<?php echo esc_url(home_url('/stock-screener/')); ?>">Stock Screener</a></li>
                        <li><a href="<?php echo esc_url(home_url('/portfolio/')); ?>">Portfolio</a></li>
                        <li><a href="<?php echo esc_url(home_url('/watchlist/')); ?>">Watchlist</a></li>
                        <li><a href="<?php echo esc_url(home_url('/premium-plans/')); ?>">Premium Plans</a></li>
                    </ul>
                </div>
                
                <div class="footer-section footer-support">
                    <h4>Support</h4>
                    <ul>
                        <li><a href="<?php echo esc_url(home_url('/faq/')); ?>">FAQ</a></li>
                        <li><a href="<?php echo esc_url(home_url('/contact/')); ?>">Contact Us</a></li>
                        <li><a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>">Privacy Policy</a></li>
                        <li><a href="<?php echo esc_url(home_url('/terms-of-service/')); ?>">Terms of Service</a></li>
                    </ul>
                </div>
                
                <div class="footer-section footer-newsletter">
                    <h4>Stay Updated</h4>
                    <p>Get the latest market insights and platform updates.</p>
                    <form class="newsletter-form" action="#" method="post">
                        <input type="email" placeholder="Enter your email" required>
                        <button type="submit">Subscribe</button>
                    </form>
                </div>
            </div>
            
            <div class="footer-bottom">
                <div class="footer-copyright">
                    <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
                </div>
                <div class="footer-disclaimer">
                    <p><small>Investment involves risk. Past performance is not indicative of future results.</small></p>
                </div>
            </div>
        </div>
    </footer><!-- #colophon -->

</div><!-- #page -->

<!-- JSON-LD Structured Data for Footer Organization -->
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "<?php echo esc_js(get_bloginfo('name')); ?>",
    "url": "<?php echo esc_url(home_url()); ?>",
    "sameAs": [
        "https://twitter.com/zatrastocks",
        "https://linkedin.com/company/zatra",
        "https://facebook.com/zatrastocks"
    ],
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "Customer Service",
        "availableLanguage": "English"
    }
}
</script>

<?php wp_footer(); ?>

</body>
</html>