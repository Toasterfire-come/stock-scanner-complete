    </div><!-- #content -->

    <footer id="colophon" class="site-footer">
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-widgets">
                    <div class="footer-widget-area">
                        <div class="widget footer-about">
                            <h3 class="widget-title">📈 Stock Scanner</h3>
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
                        <h3>🚀 Ready to Start Analyzing Stocks?</h3>
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
                            <span class="badge-icon">⚡</span>
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

<style>
/* Professional Footer Styling with WordPress Admin Colors */
.site-footer {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: #ffffff;
    margin-top: 60px;
}

.footer-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.footer-content {
    padding: 60px 0 40px;
}

.footer-widgets {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 40px;
    margin-bottom: 50px;
}

.footer-widget-area .widget {
    background: rgba(255, 255, 255, 0.05);
    padding: 25px;
    border-radius: 8px;
    border-left: 4px solid var(--wp-admin-blue, #2271b1);
}

.widget-title {
    color: var(--wp-admin-blue, #2271b1);
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-about p {
    line-height: 1.6;
    color: #cccccc;
    margin-bottom: 20px;
}

.social-links {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.social-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: var(--wp-admin-blue, #2271b1);
    border-radius: 50%;
    text-decoration: none;
    transition: all 0.3s ease;
    font-size: 1.2rem;
}

.social-link:hover {
    background: #135e96;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(34, 113, 177, 0.3);
}

.footer-menu {
    list-style: none;
    margin: 0;
    padding: 0;
}

.footer-menu li {
    margin-bottom: 10px;
}

.footer-menu li a {
    color: #cccccc;
    text-decoration: none;
    transition: color 0.3s ease;
    display: flex;
    align-items: center;
    padding: 5px 0;
}

.footer-menu li a:hover {
    color: var(--wp-admin-blue, #2271b1);
    padding-left: 5px;
}

.contact-info {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #cccccc;
}

.contact-icon {
    font-size: 1.1rem;
    color: var(--wp-admin-blue, #2271b1);
}

.contact-item a {
    color: #cccccc;
    text-decoration: none;
    transition: color 0.3s ease;
}

.contact-item a:hover {
    color: var(--wp-admin-blue, #2271b1);
}

.features-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.features-list li {
    color: #cccccc;
    margin-bottom: 8px;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.features-list li:last-child {
    border-bottom: none;
}

/* Footer CTA Section */
.footer-pricing-cta {
    background: linear-gradient(135deg, var(--wp-admin-blue, #2271b1) 0%, #135e96 100%);
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}

.footer-pricing-cta::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
    opacity: 0.3;
}

.cta-content {
    position: relative;
    z-index: 1;
}

.cta-content h3 {
    font-size: 1.8rem;
    margin-bottom: 10px;
    color: white;
}

.cta-content p {
    font-size: 1.1rem;
    margin-bottom: 25px;
    color: rgba(255, 255, 255, 0.9);
}

.cta-buttons {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.btn-large {
    padding: 12px 30px;
    font-size: 1rem;
    font-weight: 600;
}

.btn-outline {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn-outline:hover {
    background: white;
    color: var(--wp-admin-blue, #2271b1);
}

/* Footer Bottom */
.footer-bottom {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 30px 0;
    background: rgba(0, 0, 0, 0.3);
}

.footer-bottom-content {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 30px;
    align-items: center;
}

.copyright p {
    margin: 0;
    color: #cccccc;
    font-size: 0.9rem;
    line-height: 1.4;
}

.disclaimer {
    font-size: 0.8rem !important;
    color: #999999 !important;
    font-style: italic;
}

.footer-badges {
    display: flex;
    gap: 20px;
    justify-content: center;
}

.security-badge {
    display: flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.1);
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    color: #cccccc;
}

.badge-icon {
    font-size: 0.9rem;
}

.footer-legal {
    display: flex;
    gap: 20px;
    justify-content: flex-end;
}

.footer-legal a {
    color: #cccccc;
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.3s ease;
}

.footer-legal a:hover {
    color: var(--wp-admin-blue, #2271b1);
}

/* Mobile Responsiveness */
@media (max-width: 1024px) {
    .footer-widgets {
        grid-template-columns: repeat(2, 1fr);
        gap: 30px;
    }
}

@media (max-width: 768px) {
    .footer-content {
        padding: 40px 0 30px;
    }
    
    .footer-widgets {
        grid-template-columns: 1fr;
        gap: 25px;
    }
    
    .footer-widget-area .widget {
        padding: 20px;
    }
    
    .footer-pricing-cta {
        padding: 30px 20px;
    }
    
    .cta-content h3 {
        font-size: 1.5rem;
    }
    
    .cta-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .btn-large {
        width: 100%;
        max-width: 280px;
    }
    
    .footer-bottom-content {
        grid-template-columns: 1fr;
        gap: 20px;
        text-align: center;
    }
    
    .footer-badges {
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .footer-legal {
        justify-content: center;
        flex-wrap: wrap;
    }
}

@media (max-width: 480px) {
    .footer-container {
        padding: 0 15px;
    }
    
    .footer-pricing-cta {
        padding: 25px 15px;
    }
    
    .cta-content h3 {
        font-size: 1.3rem;
    }
    
    .social-links {
        justify-content: center;
    }
    
    .footer-badges {
        gap: 10px;
    }
    
    .security-badge {
        padding: 6px 10px;
        font-size: 0.75rem;
    }
    
    .footer-legal {
        gap: 15px;
    }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .social-link,
    .footer-menu li a,
    .contact-item a,
    .footer-legal a {
        transition: none;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .site-footer {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }
    
    .footer-widget-area .widget {
        background: rgba(255, 255, 255, 0.03);
    }
}
</style>

<script>
// Footer interaction enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for footer links
    const footerLinks = document.querySelectorAll('.footer-menu a[href^="#"]');
    footerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to CTA buttons
    const ctaButtons = document.querySelectorAll('.cta-buttons .btn');
    ctaButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.opacity = '0.7';
            this.textContent = 'Loading...';
        });
    });
});
</script>

</body>
</html><?php

/**
 * Fallback menu for footer
 */
function stock_scanner_footer_fallback_menu() {
    echo '<ul class="footer-menu">';
    echo '<li><a href="' . home_url('/about/') . '">About</a></li>';
    echo '<li><a href="' . home_url('/contact/') . '">Contact</a></li>';
    echo '<li><a href="' . home_url('/privacy-policy/') . '">Privacy</a></li>';
    echo '<li><a href="' . home_url('/terms-of-service/') . '">Terms</a></li>';
    echo '<li><a href="' . home_url('/faq/') . '">FAQ</a></li>';
    echo '</ul>';
}

/**
 * Fallback menu for primary navigation
 */
function stock_scanner_fallback_menu() {
    echo '<ul class="primary-menu">';
    echo '<li><a href="' . home_url('/dashboard/') . '">Dashboard</a></li>';
    echo '<li><a href="' . home_url('/stock-scanner/') . '">Scanner</a></li>';
    
    // New feature menu items (only show if user is logged in)
    if (is_user_logged_in()) {
        echo '<li><a href="' . home_url('/portfolio/') . '"><span class="menu-icon">📊</span> My Portfolios</a></li>';
        echo '<li><a href="' . home_url('/watchlist/') . '"><span class="menu-icon">👁️</span> Watchlist</a></li>';
        echo '<li><a href="' . home_url('/personalized-news/') . '"><span class="menu-icon">📰</span> My News Feed</a></li>';
    }
    
    echo '<li><a href="' . home_url('/premium-plans/') . '">Plans</a></li>';
    echo '<li><a href="' . home_url('/contact/') . '">Contact</a></li>';
    echo '</ul>';
}
?>