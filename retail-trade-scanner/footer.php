</main><!-- #main -->

    <footer class="site-footer glass-card" role="contentinfo">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4 class="footer-title"><?php bloginfo('name'); ?></h4>
                    <p class="footer-description">
                        <?php esc_html_e('Advanced stock scanning and trading analytics platform for modern investors.', 'retail-trade-scanner'); ?>
                    </p>
                    <div class="social-links">
                        <a href="#" class="social-link" aria-label="<?php esc_attr_e('Follow us on Twitter', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('twitter', ['width' => '20', 'height' => '20']); ?>
                        </a>
                        <a href="#" class="social-link" aria-label="<?php esc_attr_e('Follow us on LinkedIn', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('linkedin', ['width' => '20', 'height' => '20']); ?>
                        </a>
                        <a href="#" class="social-link" aria-label="<?php esc_attr_e('View our GitHub', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('github', ['width' => '20', 'height' => '20']); ?>
                        </a>
                    </div>
                </div>

                <div class="footer-section">
                    <h4 class="footer-title"><?php esc_html_e('Platform', 'retail-trade-scanner'); ?></h4>
                    <ul class="footer-menu">
                        <li><a href="<?php echo esc_url(home_url('/scanner/')); ?>"><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/portfolio/')); ?>"><?php esc_html_e('Portfolio Tracker', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/alerts/')); ?>"><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/news/')); ?>"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></a></li>
                    </ul>
                </div>

                <div class="footer-section">
                    <h4 class="footer-title"><?php esc_html_e('Resources', 'retail-trade-scanner'); ?></h4>
                    <ul class="footer-menu">
                        <li><a href="<?php echo esc_url(home_url('/api-docs/')); ?>"><?php esc_html_e('API Documentation', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/help/')); ?>"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/tutorials/')); ?>"><?php esc_html_e('Tutorials', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/blog/')); ?>"><?php esc_html_e('Blog', 'retail-trade-scanner'); ?></a></li>
                    </ul>
                </div>

                <div class="footer-section">
                    <h4 class="footer-title"><?php esc_html_e('Legal', 'retail-trade-scanner'); ?></h4>
                    <ul class="footer-menu">
                        <li><a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/terms-of-service/')); ?>"><?php esc_html_e('Terms of Service', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/disclaimer/')); ?>"><?php esc_html_e('Disclaimer', 'retail-trade-scanner'); ?></a></li>
                        <li><a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact Us', 'retail-trade-scanner'); ?></a></li>
                    </ul>
                </div>
            </div>

            <div class="footer-bottom">
                <div class="footer-bottom-content flex items-center justify-between">
                    <div class="footer-copyright">
                        <p>&copy; <?php echo esc_html(date('Y')); ?> <?php bloginfo('name'); ?>. <?php esc_html_e('All rights reserved.', 'retail-trade-scanner'); ?></p>
                    </div>
                    
                    <div class="footer-disclaimer">
                        <p class="text-sm text-muted">
                            <?php esc_html_e('Not financial advice. Trading involves risk of loss.', 'retail-trade-scanner'); ?>
                        </p>
                    </div>

                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'footer',
                        'menu_class' => 'footer-nav flex gap-lg',
                        'container' => false,
                        'depth' => 1,
                        'fallback_cb' => false,
                    ));
                    ?>
                </div>
            </div>
        </div>

        <!-- Back to Top Button -->
        <button class="back-to-top btn-icon btn-primary btn-magnetic hidden" aria-label="<?php esc_attr_e('Back to top', 'retail-trade-scanner'); ?>">
            <?php echo rts_get_icon('chevron-up', ['width' => '20', 'height' => '20']); ?>
        </button>
    </footer>
</div><!-- .site-container -->

<!-- Toast Container -->
<div class="toast-container" aria-live="polite" aria-atomic="true"></div>

<!-- Loading Overlay -->
<div class="loading-overlay hidden" aria-hidden="true">
    <div class="loading-spinner-large">
        <div class="spinner"></div>
        <p><?php esc_html_e('Loading...', 'retail-trade-scanner'); ?></p>
    </div>
</div>

<?php wp_footer(); ?>

<!-- Critical JavaScript for immediate functionality -->
<script>
// Replace no-js class
document.documentElement.classList.replace('no-js', 'js');

// Theme toggle functionality
function initThemeToggle() {
    const toggle = document.querySelector('.theme-toggle');
    const sunIcon = document.querySelector('.theme-toggle-sun');
    const moonIcon = document.querySelector('.theme-toggle-moon');
    
    if (!toggle) return;
    
    // Check for saved theme preference or default to 'light' mode
    const currentTheme = localStorage.getItem('theme') || 
                        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }
    
    toggle.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (theme === 'dark') {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    });
}

// Initialize on DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
} else {
    initThemeToggle();
}

// Mobile menu toggle
function initMobileMenu() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.main-navigation');
    
    if (!toggle || !nav) return;
    
    toggle.addEventListener('click', function() {
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !expanded);
        nav.classList.toggle('mobile-active');
        
        // Update hamburger animation
        toggle.querySelector('.hamburger').classList.toggle('active');
    });
}

// Search modal functionality
function initSearchModal() {
    const searchToggle = document.querySelector('.search-toggle');
    const searchModal = document.querySelector('.search-modal');
    const searchClose = document.querySelector('.search-modal-close');
    const searchBackdrop = document.querySelector('.search-modal-backdrop');
    
    if (!searchToggle || !searchModal) return;
    
    function openSearch() {
        searchModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        searchModal.querySelector('input[type="search"]')?.focus();
    }
    
    function closeSearch() {
        searchModal.classList.add('hidden');
        document.body.style.overflow = '';
    }
    
    searchToggle.addEventListener('click', openSearch);
    searchClose?.addEventListener('click', closeSearch);
    searchBackdrop?.addEventListener('click', closeSearch);
    
    // Close on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !searchModal.classList.contains('hidden')) {
            closeSearch();
        }
    });
}

// Initialize all functionality
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initSearchModal();
});
</script>

</body>
</html>