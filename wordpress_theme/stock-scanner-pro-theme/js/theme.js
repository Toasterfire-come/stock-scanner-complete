/**
 * Stock Scanner Theme JavaScript
 * Enhanced functionality for the theme
 */

jQuery(document).ready(function($) {
    
    /**
     * Smooth scrolling for anchor links
     */
    $('a[href*="#"]').on('click', function(e) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    /**
     * Mobile menu toggle
     */
    if (window.innerWidth <= 768) {
        const nav = $('.main-nav');
        const header = $('.site-header');
        
        // Add mobile menu button
        header.prepend('<button class="mobile-menu-toggle">☰</button>');
        
        $('.mobile-menu-toggle').on('click', function() {
            nav.toggleClass('mobile-active');
            $(this).text(nav.hasClass('mobile-active') ? '✕' : '☰');
        });
    }
    
    /**
     * Sticky header on scroll
     */
    let lastScrollTop = 0;
    $(window).scroll(function() {
        const scrollTop = $(this).scrollTop();
        const header = $('.site-header');
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            header.addClass('header-hidden');
        } else {
            // Scrolling up
            header.removeClass('header-hidden');
        }
        
        lastScrollTop = scrollTop;
    });
    
    /**
     * Animate elements on scroll
     */
    function animateOnScroll() {
        $('.stock-row, .pricing-plan, .watchlist-container').each(function() {
            const elementTop = $(this).offset().top;
            const elementBottom = elementTop + $(this).outerHeight();
            const viewportTop = $(window).scrollTop();
            const viewportBottom = viewportTop + $(window).height();
            
            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('animate-in');
            }
        });
    }
    
    // Run on scroll and initial load
    $(window).on('scroll', animateOnScroll);
    animateOnScroll();
    
    /**
     * Real-time clock for market hours
     */
    function updateMarketClock() {
        const now = new Date();
        const marketOpen = new Date();
        const marketClose = new Date();
        
        // Set market hours (9:30 AM - 4:00 PM ET)
        marketOpen.setHours(9, 30, 0);
        marketClose.setHours(16, 0, 0);
        
        const isMarketOpen = now >= marketOpen && now <= marketClose && now.getDay() >= 1 && now.getDay() <= 5;
        
        // Add market status to header
        if ($('.market-status').length === 0) {
            $('.user-menu').prepend(`
                <span class="market-status ${isMarketOpen ? 'open' : 'closed'}">
                    ${isMarketOpen ? '🟢 Market Open' : '🔴 Market Closed'}
                </span>
            `);
        }
    }
    
    updateMarketClock();
    setInterval(updateMarketClock, 60000); // Update every minute
    
    /**
     * Enhanced stock widget interactions
     */
    $(document).on('click', '.stock-scanner-widget', function() {
        $(this).addClass('widget-focused');
        setTimeout(() => {
            $(this).removeClass('widget-focused');
        }, 2000);
    });
    
    /**
     * Loading skeleton for slow-loading widgets
     */
    $('.stock-scanner-widget .loading').each(function() {
        if ($(this).is(':visible')) {
            $(this).addClass('loading-skeleton');
        }
    });
    
    /**
     * Auto-refresh stock data every 30 seconds
     */
    if (typeof stockScanner !== 'undefined') {
        setInterval(function() {
            if (document.visibilityState === 'visible') {
                stockScanner.refreshAllStocks();
            }
        }, 30000);
    }
    
    /**
     * Copy stock symbol to clipboard
     */
    $(document).on('click', '.stock-header h3', function() {
        const symbol = $(this).text().trim();
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(symbol).then(function() {
                // Show copied notification
                const notification = $('<div class="copy-notification">Copied ' + symbol + '!</div>');
                $('body').append(notification);
                
                setTimeout(() => {
                    notification.fadeOut(function() {
                        $(this).remove();
                    });
                }, 2000);
            });
        }
    });
    
    /**
     * Keyboard shortcuts
     */
    $(document).keydown(function(e) {
        // Ctrl/Cmd + R to refresh stock data
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 82 && typeof stockScanner !== 'undefined') {
            e.preventDefault();
            stockScanner.refreshAllStocks();
            
            // Show refresh notification
            const notification = $('<div class="refresh-notification">🔄 Refreshing stock data...</div>');
            $('body').append(notification);
            
            setTimeout(() => {
                notification.fadeOut(function() {
                    $(this).remove();
                });
            }, 2000);
        }
        
        // 'D' key to go to dashboard
        if (e.keyCode === 68 && !$(e.target).is('input, textarea')) {
            window.location.href = '/stock-dashboard/';
        }
        
        // 'W' key to go to watchlist
        if (e.keyCode === 87 && !$(e.target).is('input, textarea')) {
            window.location.href = '/stock-watchlist/';
        }
    });
    
    /**
     * Performance monitoring
     */
    function logPerformance() {
        if (performance.mark && performance.measure) {
            performance.mark('theme-js-loaded');
            
            // Log page load performance
            window.addEventListener('load', function() {
                performance.mark('page-loaded');
                performance.measure('page-load-time', 'navigationStart', 'page-loaded');
                
                const loadTime = performance.getEntriesByName('page-load-time')[0];
                if (loadTime && window.console) {
                    console.log(` Stock Scanner page loaded in ${Math.round(loadTime.duration)}ms`);
                }
            });
        }
    }
    
    logPerformance();
    
    /**
     * Error handling for stock widgets
     */
    $(document).on('error', '.stock-scanner-widget', function() {
        const widget = $(this);
        const errorMessage = $('<div class="widget-error">⚠️ Failed to load stock data. <button class="retry-btn">Retry</button></div>');
        
        widget.find('.loading').replaceWith(errorMessage);
        
        errorMessage.find('.retry-btn').on('click', function() {
            const symbol = widget.data('symbol');
            if (symbol && typeof stockScanner !== 'undefined') {
                stockScanner.refreshStock(symbol);
            }
        });
    });
    
});

/**
 * Add CSS for enhanced functionality
 */
const themeStyles = `
<style>
/* Mobile menu styles */
@media (max-width: 768px) {
    .mobile-menu-toggle {
        display: block;
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
    }
    
    .main-nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(102, 126, 234, 0.95);
        backdrop-filter: blur(10px);
    }
    
    .main-nav.mobile-active {
        display: block;
    }
    
    .main-nav ul {
        flex-direction: column;
        padding: 1rem;
    }
}

/* Header animations */
.site-header {
    transition: transform 0.3s ease;
}

.site-header.header-hidden {
    transform: translateY(-100%);
}

/* Market status */
.market-status {
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.2);
}

.market-status.open {
    background: rgba(46, 204, 113, 0.2);
    color: #2ecc71;
}

.market-status.closed {
    background: rgba(231, 76, 60, 0.2);
    color: #e74c3c;
}

/* Widget animations */
.stock-scanner-widget {
    transition: all 0.3s ease;
}

.stock-scanner-widget.widget-focused {
    transform: scale(1.02);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Notifications */
.copy-notification, .refresh-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #2ecc71;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 5px;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
}

.refresh-notification {
    background: #3498db;
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Widget error styles */
.widget-error {
    text-align: center;
    padding: 2rem;
    color: #e74c3c;
    background: #fdf2f2;
    border-radius: 5px;
    margin: 1rem 0;
}

.retry-btn {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 3px;
    cursor: pointer;
    margin-left: 0.5rem;
}

.retry-btn:hover {
    background: #c0392b;
}

/* Accessibility improvements */
.stock-scanner-widget:focus-within {
    outline: 2px solid #3498db;
    outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .stock-scanner-widget,
    .pricing-plan,
    .site-header {
        transition: none;
        animation: none;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', themeStyles);