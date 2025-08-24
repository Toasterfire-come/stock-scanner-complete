    </main><!-- #main -->

    <footer id="colophon" class="site-footer">
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-widgets">
                    <div class="footer-widget-area">
                        <div class="widget footer-about">
                            <h3 class="widget-title">Stock Scanner</h3>
                            <p>Professional stock analysis platform providing real-time market data, advanced screening tools, and portfolio tracking for investors and traders worldwide.</p>
                            <div class="social-links">
                                <?php
                                $social_sites = array(
                                    'twitter' => '🐦',
                                    'facebook' => '📘',
                                    'linkedin' => '💼',
                                    'youtube' => '📺',
                                    'instagram' => '📷'
                                );
                                
                                foreach ($social_sites as $site => $icon) {
                                    $url = get_theme_mod($site . '_url');
                                    if ($url) {
                                        echo '<a href="' . esc_url($url) . '" class="social-link" target="_blank" rel="noopener noreferrer" aria-label="' . ucfirst($site) . '">';
                                        echo '<span class="social-icon">' . $icon . '</span>';
                                        echo '</a>';
                                    }
                                }
                                ?>
                            </div>
                        </div>
                        <?php if (is_active_sidebar('footer-1')) dynamic_sidebar('footer-1'); ?>
                    </div>
                    
                    <div class="footer-widget-area">
                        <div class="widget footer-nav">
                            <h3 class="widget-title">Quick Links</h3>
                            <?php
                            wp_nav_menu(array(
                                'theme_location' => 'footer',
                                'menu_class'     => 'footer-menu',
                                'container'      => false,
                                'depth'          => 1,
                                'fallback_cb'    => 'stock_scanner_footer_fallback_menu',
                            ));
                            ?>
                        </div>
                        <?php if (is_active_sidebar('footer-2')) dynamic_sidebar('footer-2'); ?>
                    </div>
                    
                    <div class="footer-widget-area">
                        <div class="widget footer-contact">
                            <h3 class="widget-title">Contact Info</h3>
                            <div class="contact-info">
                                <div class="contact-item">
                                    <span class="contact-icon">📧</span>
                                    <a href="mailto:support@stockscanner.com">support@stockscanner.com</a>
                                </div>
                                <div class="contact-item">
                                    <span class="contact-icon">💬</span>
                                    <a href="/contact/">Get Support</a>
                                </div>
                                <div class="contact-item">
                                    <span class="contact-icon">📞</span>
                                    <span>24/7 Customer Support</span>
                                </div>
                            </div>
                        </div>
                        <?php if (is_active_sidebar('footer-3')) dynamic_sidebar('footer-3'); ?>
                    </div>
                    
                    <div class="footer-widget-area">
                        <div class="widget footer-features">
                            <h3 class="widget-title">Features</h3>
                            <ul class="features-list">
                                <li>✅ Real-time Stock Data</li>
                                <li>✅ Advanced Screening</li>
                                <li>✅ Portfolio Tracking</li>
                                <li>✅ Price Alerts</li>
                                <li>✅ Market Analysis</li>
                                <li>✅ Multiple Plan Options</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="footer-pricing-cta">
                    <div class="cta-content">
                        <h3>Ready to Start Analyzing Stocks?</h3>
                        <p>Join thousands of investors using our professional platform</p>
                        <div class="cta-buttons">
                            <?php if (!is_user_logged_in()): ?>
                                <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-large">Start Free Trial</a>
                                <a href="/premium-plans/" class="btn btn-outline btn-large">View Plans</a>
                            <?php else: ?>
                                <a href="/dashboard/" class="btn btn-primary btn-large">Go to Dashboard</a>
                                <?php if (function_exists('get_user_membership_level') && get_user_membership_level() === 'free'): ?>
                                    <a href="/premium-plans/" class="btn btn-outline btn-large">Upgrade Plan</a>
                                <?php endif; ?>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer-bottom">
                <div class="footer-bottom-content">
                    <div class="copyright">
                        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
                        <p class="disclaimer">Investment involves risk. Past performance does not guarantee future results.</p>
                    </div>
                    
                    <div class="footer-badges">
                        <div class="security-badge">
                            <span class="badge-icon">🔒</span>
                            <span class="badge-text">SSL Secured</span>
                        </div>
                        <div class="security-badge">
                            <span class="badge-icon">💳</span>
                            <span class="badge-text">PayPal Protected</span>
                        </div>
                        <div class="security-badge">
                            <span class="badge-icon"></span>
                            <span class="badge-text">99.9% Uptime</span>
                        </div>
                    </div>
                    
                    <div class="footer-legal">
                        <a href="/privacy-policy/">Privacy Policy</a>
                        <a href="/terms-of-service/">Terms of Service</a>
                        <a href="/contact/">Contact</a>
                    </div>
                </div>
            </div>
        </div>
    </footer>

</div><!-- #page -->

<?php wp_footer(); ?>
<script src="<?php echo get_template_directory_uri(); ?>/assets/js/visual-enhancements.js?v=<?php echo filemtime(get_template_directory() . '/assets/js/visual-enhancements.js'); ?>" defer></script>
</body>
</html>