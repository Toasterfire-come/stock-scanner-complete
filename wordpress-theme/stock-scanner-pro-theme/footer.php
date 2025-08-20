<?php
/**
 * Footer template
 *
 * @package StockScannerPro
 */
?>

    </div><!-- #content -->

    <!-- Footer -->
    <footer id="colophon" class="site-footer bg-gray-900 text-white">
        
        <!-- Main Footer Content -->
        <div class="footer-main py-12">
            <div class="container mx-auto px-4">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    
                    <!-- Company Info -->
                    <div class="footer-section">
                        <div class="footer-logo mb-4">
                            <?php if (has_custom_logo()) : ?>
                                <?php the_custom_logo(); ?>
                            <?php else : ?>
                                <h3 class="text-xl font-bold text-white">
                                    <?php bloginfo('name'); ?>
                                </h3>
                            <?php endif; ?>
                        </div>
                        
                        <p class="text-gray-300 text-sm mb-4">
                            <?php 
                            $description = get_bloginfo('description', 'display');
                            if ($description) {
                                echo esc_html($description);
                            } else {
                                _e('Professional stock market analysis and portfolio management platform.', 'stock-scanner-pro');
                            }
                            ?>
                        </p>

                        <!-- Social Links -->
                        <div class="social-links flex items-center space-x-4">
                            <a href="#" class="text-gray-400 hover:text-white transition-colors" aria-label="Twitter">
                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"/>
                                </svg>
                            </a>
                            <a href="#" class="text-gray-400 hover:text-white transition-colors" aria-label="LinkedIn">
                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                                </svg>
                            </a>
                            <a href="#" class="text-gray-400 hover:text-white transition-colors" aria-label="GitHub">
                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                </svg>
                            </a>
                        </div>
                    </div>

                    <!-- Products -->
                    <div class="footer-section">
                        <h4 class="text-lg font-semibold text-white mb-4">
                            <?php _e('Products', 'stock-scanner-pro'); ?>
                        </h4>
                        <ul class="footer-links space-y-2">
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('market-overview'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Market Overview', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('stock-lookup'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Stock Lookup', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('portfolio'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Portfolio Tracker', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('watchlist'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Watchlist', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('stock-news'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Market News', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <!-- Support -->
                    <div class="footer-section">
                        <h4 class="text-lg font-semibold text-white mb-4">
                            <?php _e('Support', 'stock-scanner-pro'); ?>
                        </h4>
                        <ul class="footer-links space-y-2">
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('help-center'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Help Center', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('getting-started'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Getting Started', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('faq'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('FAQ', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('contact'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Contact Us', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('status'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('System Status', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <!-- Account -->
                    <div class="footer-section">
                        <h4 class="text-lg font-semibold text-white mb-4">
                            <?php _e('Account', 'stock-scanner-pro'); ?>
                        </h4>
                        <ul class="footer-links space-y-2">
                            <?php if (is_user_logged_in()) : ?>
                                <li>
                                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('dashboard'))); ?>" 
                                       class="text-gray-300 hover:text-white text-sm transition-colors">
                                        <?php _e('Dashboard', 'stock-scanner-pro'); ?>
                                    </a>
                                </li>
                                <li>
                                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('account'))); ?>" 
                                       class="text-gray-300 hover:text-white text-sm transition-colors">
                                        <?php _e('My Account', 'stock-scanner-pro'); ?>
                                    </a>
                                </li>
                                <li>
                                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('billing-history'))); ?>" 
                                       class="text-gray-300 hover:text-white text-sm transition-colors">
                                        <?php _e('Billing', 'stock-scanner-pro'); ?>
                                    </a>
                                </li>
                            <?php else : ?>
                                <li>
                                    <a href="<?php echo wp_login_url(); ?>" 
                                       class="text-gray-300 hover:text-white text-sm transition-colors">
                                        <?php _e('Sign In', 'stock-scanner-pro'); ?>
                                    </a>
                                </li>
                                <li>
                                    <a href="<?php echo wp_registration_url(); ?>" 
                                       class="text-gray-300 hover:text-white text-sm transition-colors">
                                        <?php _e('Create Account', 'stock-scanner-pro'); ?>
                                    </a>
                                </li>
                            <?php endif; ?>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('premium-plans'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Pricing', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('compare-plans'))); ?>" 
                                   class="text-gray-300 hover:text-white text-sm transition-colors">
                                    <?php _e('Compare Plans', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Newsletter Signup -->
        <div class="footer-newsletter bg-gray-800 py-8 border-t border-gray-700">
            <div class="container mx-auto px-4">
                <div class="max-w-2xl mx-auto text-center">
                    <h4 class="text-lg font-semibold text-white mb-2">
                        <?php _e('Stay Updated', 'stock-scanner-pro'); ?>
                    </h4>
                    <p class="text-gray-300 text-sm mb-4">
                        <?php _e('Get the latest market insights and product updates delivered to your inbox.', 'stock-scanner-pro'); ?>
                    </p>
                    
                    <form class="newsletter-form flex flex-col sm:flex-row gap-3 max-w-md mx-auto" 
                          action="<?php echo admin_url('admin-ajax.php'); ?>" 
                          method="post">
                        <input type="hidden" name="action" value="newsletter_signup">
                        <?php wp_nonce_field('newsletter_signup', 'newsletter_nonce'); ?>
                        
                        <input type="email" 
                               name="email" 
                               class="newsletter-email flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               placeholder="<?php _e('Enter your email', 'stock-scanner-pro'); ?>" 
                               required>
                        
                        <button type="submit" 
                                class="newsletter-submit bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium transition-colors">
                            <?php _e('Subscribe', 'stock-scanner-pro'); ?>
                        </button>
                    </form>
                    
                    <p class="text-xs text-gray-400 mt-3">
                        <?php _e('We respect your privacy. Unsubscribe at any time.', 'stock-scanner-pro'); ?>
                    </p>
                </div>
            </div>
        </div>

        <!-- Footer Bottom -->
        <div class="footer-bottom bg-gray-800 py-6 border-t border-gray-700">
            <div class="container mx-auto px-4">
                <div class="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
                    
                    <!-- Copyright -->
                    <div class="copyright text-sm text-gray-400">
                        <?php
                        printf(
                            __('© %s %s. All rights reserved.', 'stock-scanner-pro'),
                            date('Y'),
                            get_bloginfo('name')
                        );
                        ?>
                    </div>

                    <!-- Footer Menu -->
                    <nav class="footer-nav" aria-label="<?php _e('Footer Navigation', 'stock-scanner-pro'); ?>">
                        <?php
                        wp_nav_menu(array(
                            'theme_location' => 'footer',
                            'menu_class' => 'footer-menu flex items-center space-x-6 text-sm',
                            'container' => false,
                            'fallback_cb' => '__return_false',
                            'depth' => 1,
                        ));
                        
                        // Default footer links if no menu is set
                        if (!has_nav_menu('footer')) :
                        ?>
                        <ul class="footer-menu flex items-center space-x-6 text-sm">
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('privacy-policy'))); ?>" 
                                   class="text-gray-400 hover:text-white transition-colors">
                                    <?php _e('Privacy', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('terms'))); ?>" 
                                   class="text-gray-400 hover:text-white transition-colors">
                                    <?php _e('Terms', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('cookie-policy'))); ?>" 
                                   class="text-gray-400 hover:text-white transition-colors">
                                    <?php _e('Cookies', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                            <li>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('accessibility'))); ?>" 
                                   class="text-gray-400 hover:text-white transition-colors">
                                    <?php _e('Accessibility', 'stock-scanner-pro'); ?>
                                </a>
                            </li>
                        </ul>
                        <?php endif; ?>
                    </nav>
                </div>
            </div>
        </div>
    </footer>

</div><!-- #page -->

<!-- Back to Top Button -->
<button id="back-to-top" 
        class="back-to-top fixed bottom-8 right-8 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all duration-300 opacity-0 pointer-events-none"
        aria-label="<?php _e('Back to top', 'stock-scanner-pro'); ?>">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
    </svg>
</button>

<!-- Toast Notifications Container -->
<div id="toast-container" class="toast-container fixed top-4 right-4 z-50 space-y-2"></div>

<!-- Loading Overlay -->
<div id="loading-overlay" class="loading-overlay fixed inset-0 bg-black bg-opacity-50 z-50 hidden">
    <div class="flex items-center justify-center min-h-screen">
        <div class="loading-spinner bg-white rounded-lg p-8 shadow-xl">
            <div class="flex items-center space-x-3">
                <div class="spinner"></div>
                <span class="text-gray-900 font-medium">
                    <?php _e('Loading...', 'stock-scanner-pro'); ?>
                </span>
            </div>
        </div>
    </div>
</div>

<?php wp_footer(); ?>

<!-- Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "<?php bloginfo('name'); ?>",
  "url": "<?php echo home_url(); ?>",
  "logo": "<?php echo wp_get_attachment_image_url(get_theme_mod('custom_logo'), 'full'); ?>",
  "description": "<?php bloginfo('description'); ?>",
  "sameAs": [
    "https://twitter.com/stockscanner",
    "https://linkedin.com/company/stockscanner"
  ]
}
</script>

</body>
</html>