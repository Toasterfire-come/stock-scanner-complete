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
                        <li><a href="<?php echo esc_url(home_url('/')); ?>">Home</a></li>
                        <li><a href="<?php echo esc_url(home_url('/docs/')); ?>">API Documentation</a></li>
                        <li><a href="<?php echo esc_url(home_url('/status/')); ?>">System Status</a></li>
                        <li><a href="<?php echo esc_url(home_url('/market-overview/')); ?>">Market Overview</a></li>
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

<style>
.app-menu { margin-left: 1rem; position: relative; }
.app-menu-toggle { display:inline-flex; align-items:center; justify-content:center; width:40px; height:40px; border-radius:10px; border:1px solid var(--border-secondary, #334155); background: var(--bg-dark, #0b1220); cursor:pointer; }
.waffle { display:grid; grid-template-columns: repeat(3, 6px); grid-auto-rows:6px; gap:4px; }
.waffle span { display:block; width:6px; height:6px; border-radius:50%; background: var(--text-secondary, #cbd5e1); }
.dropdown-menu { position:absolute; top: calc(100% + 8px); right:0; background: var(--bg-white, #1e293b); border:1px solid var(--border-light, #334155); border-radius:12px; box-shadow: 0 12px 32px rgba(0,0,0,0.5); min-width:220px; opacity:0; visibility:hidden; transform: translateY(-10px); transition: all .2s ease; z-index:1001; }
.dropdown-menu.active { opacity:1; visibility:visible; transform: translateY(0); }
.dropdown-item { display:flex; align-items:center; padding: 0.6rem 0.9rem; color: var(--text-secondary, #cbd5e1); text-decoration:none; font-weight:700; }
.dropdown-item:hover { background: var(--bg-dark, #0b1220); color: var(--text-primary, #f8fafc); }
</style>