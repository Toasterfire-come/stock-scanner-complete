    <footer id="colophon" class="site-footer">
        <div class="container">
            <div class="footer-content">
                <!-- Company Info -->
                <div class="footer-section">
                    <h3><?php bloginfo('name'); ?></h3>
                    <p><?php bloginfo('description'); ?></p>
                    <p>Professional stock market analysis and real-time data for informed trading decisions.</p>
                </div>

                <!-- Quick Links -->
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="<?php echo esc_url(home_url('/')); ?>">Home</a></li>
                        <li><a href="<?php echo esc_url(home_url('/stocks/')); ?>">Stocks</a></li>
                        <li><a href="<?php echo esc_url(home_url('/news/')); ?>">News</a></li>
                        <li><a href="<?php echo esc_url(home_url('/market-summary/')); ?>">Market Summary</a></li>
                    </ul>
                </div>

                <!-- Market Data -->
                <div class="footer-section">
                    <h3>Market Data</h3>
                    <ul class="footer-links">
                        <li><a href="<?php echo esc_url(home_url('/stocks/gainers/')); ?>">Top Gainers</a></li>
                        <li><a href="<?php echo esc_url(home_url('/stocks/losers/')); ?>">Top Losers</a></li>
                        <li><a href="<?php echo esc_url(home_url('/stocks/volume/')); ?>">High Volume</a></li>
                        <li><a href="<?php echo esc_url(home_url('/stocks/movers/')); ?>">Biggest Movers</a></li>
                    </ul>
                </div>

                <!-- Support -->
                <div class="footer-section">
                    <h3>Support</h3>
                    <ul class="footer-links">
                        <li><a href="<?php echo esc_url(home_url('/contact/')); ?>">Contact Us</a></li>
                        <li><a href="<?php echo esc_url(home_url('/help/')); ?>">Help Center</a></li>
                        <li><a href="<?php echo esc_url(home_url('/privacy/')); ?>">Privacy Policy</a></li>
                        <li><a href="<?php echo esc_url(home_url('/terms/')); ?>">Terms of Service</a></li>
                    </ul>
                </div>
            </div>

            <!-- Footer Bottom -->
            <div class="footer-bottom">
                <div class="footer-bottom-content">
                    <div class="copyright">
                        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
                    </div>
                    
                    <div class="footer-actions">
                        <div class="social-links">
                            <a href="#" class="social-link" aria-label="Twitter">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/>
                                </svg>
                            </a>
                            <a href="#" class="social-link" aria-label="LinkedIn">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                                    <rect x="2" y="9" width="4" height="12"/>
                                    <circle cx="4" cy="4" r="2"/>
                                </svg>
                            </a>
                            <a href="#" class="social-link" aria-label="GitHub">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                                </svg>
                            </a>
                        </div>
                        
                        <div class="market-status-footer">
                            <span class="status-indicator" id="footer-market-status"></span>
                            <span class="status-text" id="footer-status-text">Market Closed</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </footer><!-- #colophon -->
</div><!-- #page -->

<!-- Back to Top Button -->
<button id="back-to-top" class="back-to-top" aria-label="Back to top">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="18,15 12,9 6,15"/>
    </svg>
</button>

<!-- Loading Overlay -->
<div id="loading-overlay" class="loading-overlay">
    <div class="loading-content">
        <div class="spinner"></div>
        <p>Loading data...</p>
    </div>
</div>

<!-- Notification Toast -->
<div id="notification-toast" class="notification-toast">
    <div class="toast-content">
        <span class="toast-message" id="toast-message"></span>
        <button class="toast-close" id="toast-close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    </div>
</div>

<?php wp_footer(); ?>

<script>
// Initialize theme functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    // Initialize back to top button
    initBackToTop();
    
    // Initialize loading overlay
    initLoadingOverlay();
    
    // Initialize notifications
    initNotifications();
    
    // Initialize market status
    initMarketStatus();
    
    // Initialize refresh functionality
    initRefreshData();
});

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
}

// Back to top button
function initBackToTop() {
    const backToTop = document.getElementById('back-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Loading overlay
function initLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    
    window.showLoading = function() {
        overlay.classList.add('visible');
    };
    
    window.hideLoading = function() {
        overlay.classList.remove('visible');
    };
}

// Notifications
function initNotifications() {
    const toast = document.getElementById('notification-toast');
    const message = document.getElementById('toast-message');
    const closeBtn = document.getElementById('toast-close');
    
    window.showNotification = function(text, type = 'info') {
        message.textContent = text;
        toast.className = `notification-toast ${type}`;
        toast.classList.add('visible');
        
        setTimeout(() => {
            toast.classList.remove('visible');
        }, 5000);
    };
    
    closeBtn.addEventListener('click', function() {
        toast.classList.remove('visible');
    });
}

// Market status
function initMarketStatus() {
    const statusIndicator = document.getElementById('market-status-indicator');
    const statusText = document.getElementById('market-status-text');
    const footerStatus = document.getElementById('footer-market-status');
    const footerText = document.getElementById('footer-status-text');
    
    // Check if market is open (simplified logic)
    const now = new Date();
    const day = now.getDay();
    const hour = now.getHours();
    
    const isMarketOpen = day >= 1 && day <= 5 && hour >= 9 && hour < 16;
    
    if (isMarketOpen) {
        statusIndicator.classList.add('open');
        statusText.textContent = 'Market Open';
        footerStatus.classList.add('open');
        footerText.textContent = 'Market Open';
    } else {
        statusIndicator.classList.add('closed');
        statusText.textContent = 'Market Closed';
        footerStatus.classList.add('closed');
        footerText.textContent = 'Market Closed';
    }
}

// Refresh data functionality
function initRefreshData() {
    const refreshBtn = document.getElementById('refresh-data');
    const refreshStocksBtn = document.getElementById('refresh-stocks');
    
    function refreshData() {
        showLoading();
        
        // Trigger data refresh
        if (typeof window.refreshStockData === 'function') {
            window.refreshStockData();
        }
        
        // Show notification
        setTimeout(() => {
            hideLoading();
            showNotification('Data refreshed successfully!', 'success');
        }, 2000);
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    if (refreshStocksBtn) {
        refreshStocksBtn.addEventListener('click', refreshData);
    }
}
</script>

</body>
</html>