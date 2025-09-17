/**
 * Stock Scanner Theme - Vanilla JavaScript
 * Production-ready theme functionality without jQuery dependencies
 */

(function() {
    'use strict';

    // Utility functions
    const Utils = {
        ready: function(callback) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', callback);
            } else {
                callback();
            }
        },

        select: function(selector, context = document) {
            return context.querySelector(selector);
        },

        selectAll: function(selector, context = document) {
            return context.querySelectorAll(selector);
        },

        addClass: function(element, className) {
            if (element) element.classList.add(className);
        },

        removeClass: function(element, className) {
            if (element) element.classList.remove(className);
        },

        toggleClass: function(element, className) {
            if (element) element.classList.toggle(className);
        },

        hasClass: function(element, className) {
            return element ? element.classList.contains(className) : false;
        },

        animate: function(element, properties, duration = 300, callback = null) {
            if (!element) return;
            
            const start = performance.now();
            const startStyles = {};
            
            // Get initial values
            Object.keys(properties).forEach(prop => {
                startStyles[prop] = parseFloat(getComputedStyle(element)[prop]) || 0;
            });

            function animateStep(timestamp) {
                const progress = Math.min((timestamp - start) / duration, 1);
                const easing = 1 - Math.pow(1 - progress, 3); // easeOutCubic

                Object.keys(properties).forEach(prop => {
                    const startValue = startStyles[prop];
                    const endValue = properties[prop];
                    const currentValue = startValue + (endValue - startValue) * easing;
                    element.style[prop] = currentValue + (prop === 'opacity' ? '' : 'px');
                });

                if (progress < 1) {
                    requestAnimationFrame(animateStep);
                } else if (callback) {
                    callback();
                }
            }

            requestAnimationFrame(animateStep);
        },

        fadeIn: function(element, duration = 300, callback = null) {
            if (!element) return;
            element.style.opacity = '0';
            element.style.display = 'block';
            this.animate(element, { opacity: 1 }, duration, callback);
        },

        fadeOut: function(element, duration = 300, callback = null) {
            if (!element) return;
            this.animate(element, { opacity: 0 }, duration, () => {
                element.style.display = 'none';
                if (callback) callback();
            });
        },

        slideUp: function(element, duration = 300, callback = null) {
            if (!element) return;
            const height = element.offsetHeight;
            element.style.overflow = 'hidden';
            this.animate(element, { height: 0 }, duration, () => {
                element.style.display = 'none';
                element.style.height = '';
                element.style.overflow = '';
                if (callback) callback();
            });
        },

        slideDown: function(element, duration = 300, callback = null) {
            if (!element) return;
            element.style.display = 'block';
            const height = element.scrollHeight;
            element.style.height = '0px';
            element.style.overflow = 'hidden';
            this.animate(element, { height: height }, duration, () => {
                element.style.height = '';
                element.style.overflow = '';
                if (callback) callback();
            });
        },

        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    timeout = null;
                    if (!immediate) func(...args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func(...args);
            };
        },

        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            }
        }
    };

    // Main Theme Class
    class StockScannerTheme {
        constructor() {
            this.lastScrollTop = 0;
            this.initializeComponents();
        }

        initializeComponents() {
            this.setupSmoothScrolling();
            this.setupMobileMenu();
            this.setupStickyHeader();
            this.setupScrollAnimations();
            this.setupMarketClock();
            this.setupStockWidgets();
            this.setupKeyboardShortcuts();
            this.setupNotifications();
            this.setupPerformanceMonitoring();
            this.setupLazyLoading();
            this.setupUserDropdown();
            this.setupThemeToggle();
        }

        setupSmoothScrolling() {
            const links = Utils.selectAll('a[href*="#"]');
            links.forEach(link => {
                link.addEventListener('click', (e) => {
                    const href = link.getAttribute('href');
                    if (href === '#') return;
                    
                    const targetId = href.split('#')[1];
                    if (!targetId) return;
                    
                    const target = Utils.select(`#${targetId}`);
                    if (target) {
                        e.preventDefault();
                        const headerOffset = 100;
                        const elementPosition = target.getBoundingClientRect().top;
                        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                        window.scrollTo({
                            top: offsetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
            });
        }

        setupMobileMenu() {
            const toggle = Utils.select('.menu-toggle, .mobile-menu-toggle');
            const nav = Utils.select('.main-navigation, .main-nav');
            const userToggle = Utils.select('.user-toggle');
            const userMenu = Utils.select('.user-menu');

            if (toggle && nav) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    Utils.toggleClass(nav, 'mobile-active');
                    Utils.toggleClass(toggle, 'active');
                    
                    const isExpanded = Utils.hasClass(nav, 'mobile-active');
                    toggle.setAttribute('aria-expanded', isExpanded);
                    
                    // Animate hamburger lines
                    const lines = Utils.selectAll('.hamburger span, .hamburger-line', toggle);
                    lines.forEach((line, index) => {
                        if (isExpanded) {
                            if (index === 0) line.style.transform = 'rotate(45deg) translate(5px, 5px)';
                            if (index === 1) line.style.opacity = '0';
                            if (index === 2) line.style.transform = 'rotate(-45deg) translate(7px, -6px)';
                        } else {
                            line.style.transform = '';
                            line.style.opacity = '';
                        }
                    });
                });

                // Close menu on outside click
                document.addEventListener('click', (e) => {
                    if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                        Utils.removeClass(nav, 'mobile-active');
                        Utils.removeClass(toggle, 'active');
                        toggle.setAttribute('aria-expanded', 'false');
                        
                        const lines = Utils.selectAll('.hamburger span, .hamburger-line', toggle);
                        lines.forEach(line => {
                            line.style.transform = '';
                            line.style.opacity = '';
                        });
                    }
                });

                // Close menu on link click
                nav.addEventListener('click', (e) => {
                    if (e.target.tagName === 'A') {
                        Utils.removeClass(nav, 'mobile-active');
                        Utils.removeClass(toggle, 'active');
                        toggle.setAttribute('aria-expanded', 'false');
                        
                        const lines = Utils.selectAll('.hamburger span, .hamburger-line', toggle);
                        lines.forEach(line => {
                            line.style.transform = '';
                            line.style.opacity = '';
                        });
                    }
                });
            }

            // User dropdown menu
            if (userToggle && userMenu) {
                userToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    Utils.toggleClass(userMenu, 'show');
                    const isExpanded = Utils.hasClass(userMenu, 'show');
                    userToggle.setAttribute('aria-expanded', isExpanded);
                });

                // Close dropdown on outside click
                document.addEventListener('click', (e) => {
                    if (!userToggle.contains(e.target) && !userMenu.contains(e.target)) {
                        Utils.removeClass(userMenu, 'show');
                        userToggle.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        }

        setupStickyHeader() {
            const header = Utils.select('.site-header');
            if (!header) return;

            const handleScroll = Utils.throttle(() => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > this.lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    Utils.addClass(header, 'header-hidden');
                } else {
                    // Scrolling up
                    Utils.removeClass(header, 'header-hidden');
                }
                
                if (scrollTop > 50) {
                    Utils.addClass(header, 'scrolled');
                } else {
                    Utils.removeClass(header, 'scrolled');
                }
                
                this.lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
            }, 10);

            window.addEventListener('scroll', handleScroll, { passive: true });
        }

        setupScrollAnimations() {
            const animatedElements = Utils.selectAll('.stock-row, .pricing-plan, .watchlist-container, .feature-card, .scroll-reveal');
            
            if (animatedElements.length === 0) return;

            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        Utils.addClass(entry.target, 'animate-in');
                        Utils.addClass(entry.target, 'revealed');
                    }
                });
            }, observerOptions);

            animatedElements.forEach(el => {
                observer.observe(el);
            });
        }

        setupMarketClock() {
            const updateMarketClock = () => {
                const now = new Date();
                const marketOpen = new Date();
                const marketClose = new Date();
                
                // Set market hours (9:30 AM - 4:00 PM ET)
                marketOpen.setHours(9, 30, 0);
                marketClose.setHours(16, 0, 0);
                
                const isMarketOpen = now >= marketOpen && now <= marketClose && 
                                   now.getDay() >= 1 && now.getDay() <= 5;
                
                // Update market status in header
                let statusElement = Utils.select('.market-status');
                const userMenu = Utils.select('.user-menu');
                
                if (!statusElement && userMenu) {
                    statusElement = document.createElement('span');
                    statusElement.className = 'market-status';
                    userMenu.insertBefore(statusElement, userMenu.firstChild);
                }
                
                if (statusElement) {
                    statusElement.className = `market-status ${isMarketOpen ? 'open' : 'closed'}`;
                    statusElement.innerHTML = isMarketOpen ? '🟢 Market Open' : '🔴 Market Closed';
                }
            };
            
            updateMarketClock();
            setInterval(updateMarketClock, 60000); // Update every minute
        }

        setupStockWidgets() {
            const widgets = Utils.selectAll('.stock-scanner-widget');
            
            widgets.forEach(widget => {
                widget.addEventListener('click', () => {
                    Utils.addClass(widget, 'widget-focused');
                    setTimeout(() => {
                        Utils.removeClass(widget, 'widget-focused');
                    }, 2000);
                });
            });

            // Copy stock symbol to clipboard
            const stockHeaders = Utils.selectAll('.stock-header h3');
            stockHeaders.forEach(header => {
                header.addEventListener('click', async () => {
                    const symbol = header.textContent.trim();
                    
                    try {
                        await navigator.clipboard.writeText(symbol);
                        this.showNotification(`Copied ${symbol}!`, 'success');
                    } catch (err) {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = symbol;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        this.showNotification(`Copied ${symbol}!`, 'success');
                    }
                });
            });

            // Auto-refresh stock data
            if (typeof stockScanner !== 'undefined') {
                setInterval(() => {
                    if (document.visibilityState === 'visible') {
                        stockScanner.refreshAllStocks();
                    }
                }, 30000);
            }
        }

        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + R to refresh stock data
                if ((e.ctrlKey || e.metaKey) && e.keyCode === 82 && typeof stockScanner !== 'undefined') {
                    e.preventDefault();
                    stockScanner.refreshAllStocks();
                    this.showNotification('🔄 Refreshing stock data...', 'info');
                }
                
                // 'D' key to go to dashboard
                if (e.keyCode === 68 && !this.isInputFocused(e.target)) {
                    window.location.href = '/dashboard/';
                }
                
                // 'W' key to go to watchlist
                if (e.keyCode === 87 && !this.isInputFocused(e.target)) {
                    window.location.href = '/watchlist/';
                }

                // Escape key to close modals and dropdowns
                if (e.keyCode === 27) {
                    const activeModal = Utils.select('.modal.show, .modal-enhanced.show');
                    if (activeModal) {
                        Utils.removeClass(activeModal, 'show');
                    }
                    
                    const activeDropdown = Utils.select('.user-menu.show');
                    if (activeDropdown) {
                        Utils.removeClass(activeDropdown, 'show');
                    }
                }
            });
        }

        setupNotifications() {
            // Create notification container if it doesn't exist
            if (!Utils.select('.notification-container')) {
                const container = document.createElement('div');
                container.className = 'notification-container';
                container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                `;
                document.body.appendChild(container);
            }
        }

        setupPerformanceMonitoring() {
            if (performance.mark && performance.measure) {
                performance.mark('theme-js-loaded');
                
                window.addEventListener('load', () => {
                    performance.mark('page-loaded');
                    
                    try {
                        performance.measure('page-load-time', 'navigationStart', 'page-loaded');
                        const loadTime = performance.getEntriesByName('page-load-time')[0];
                        
                        if (loadTime && window.console && window.location.hostname === 'localhost') {
                            console.log(`📊 Stock Scanner page loaded in ${Math.round(loadTime.duration)}ms`);
                        }
                    } catch (e) {
                        // Ignore errors in performance measurement
                    }
                });
            }
        }

        setupLazyLoading() {
            const lazyImages = Utils.selectAll('img[data-src]');
            
            if (lazyImages.length === 0) return;

            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        Utils.addClass(img, 'loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        }

        setupUserDropdown() {
            const userToggle = Utils.select('.user-toggle');
            const userMenu = Utils.select('.user-menu');

            if (userToggle && userMenu) {
                userToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    Utils.toggleClass(userMenu, 'show');
                });

                document.addEventListener('click', (e) => {
                    if (!userToggle.contains(e.target) && !userMenu.contains(e.target)) {
                        Utils.removeClass(userMenu, 'show');
                    }
                });
            }
        }

        setupThemeToggle() {
            window.toggleTheme = () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Update meta theme color
                const metaThemeColor = Utils.select('meta[name="theme-color"]');
                if (metaThemeColor) {
                    metaThemeColor.setAttribute('content', newTheme === 'dark' ? '#1a1a1a' : '#ffffff');
                }
            };

            // Load saved theme
            const savedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
            
            document.documentElement.setAttribute('data-theme', initialTheme);
        }

        // Utility methods
        showNotification(message, type = 'info', duration = 5000) {
            const container = Utils.select('.notification-container');
            if (!container) return;

            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            const icons = {
                success: '✓',
                error: '✗',
                warning: '⚠',
                info: 'ℹ'
            };

            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon">${icons[type] || icons.info}</span>
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
                </div>
            `;

            container.appendChild(notification);

            // Show with animation
            setTimeout(() => Utils.addClass(notification, 'show'), 100);

            // Auto remove
            if (duration > 0) {
                setTimeout(() => {
                    Utils.removeClass(notification, 'show');
                    setTimeout(() => notification.remove(), 500);
                }, duration);
            }
        }

        isInputFocused(element) {
            const inputTypes = ['INPUT', 'TEXTAREA', 'SELECT'];
            return inputTypes.includes(element.tagName) || element.isContentEditable;
        }

        // Error handling for widgets
        handleWidgetError(widget) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'widget-error';
            errorMessage.innerHTML = `
                ⚠️ Failed to load stock data. 
                <button class="retry-btn" onclick="location.reload()">Retry</button>
            `;
            
            const loading = Utils.select('.loading', widget);
            if (loading) {
                loading.replaceWith(errorMessage);
            } else {
                widget.appendChild(errorMessage);
            }
        }
    }

    // Initialize theme when DOM is ready
    Utils.ready(() => {
        window.stockScannerTheme = new StockScannerTheme();
        
        // Add global utilities
        window.StockScannerUtils = Utils;
        
        // Mark theme as loaded
        document.body.classList.add('theme-loaded');
    });

    // Add CSS for enhanced functionality
    const themeStyles = document.createElement('style');
    themeStyles.textContent = `
        /* Notification System */
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        }

        .notification {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 10px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 4px solid #3498db;
        }

        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }

        .notification.success {
            border-left-color: #27ae60;
        }

        .notification.error {
            border-left-color: #e74c3c;
        }

        .notification.warning {
            border-left-color: #f39c12;
        }

        .notification-content {
            display: flex;
            align-items: center;
            padding: 15px;
            gap: 10px;
        }

        .notification-icon {
            font-size: 18px;
            font-weight: bold;
        }

        .notification.success .notification-icon {
            color: #27ae60;
        }

        .notification.error .notification-icon {
            color: #e74c3c;
        }

        .notification.warning .notification-icon {
            color: #f39c12;
        }

        .notification.info .notification-icon {
            color: #3498db;
        }

        .notification-message {
            flex: 1;
            font-size: 14px;
            color: #2c3e50;
        }

        .notification-close {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #95a5a6;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .notification-close:hover {
            color: #7f8c8d;
        }

        /* Mobile Menu Enhancement */
        @media (max-width: 768px) {
            .main-navigation,
            .main-nav {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: rgba(74, 90, 58, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 0 0 12px 12px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            
            .main-navigation.mobile-active,
            .main-nav.mobile-active {
                display: block;
                animation: slideDown 0.3s ease;
            }
            
            .main-navigation ul,
            .main-nav ul {
                flex-direction: column;
                padding: 20px;
                gap: 10px;
            }

            .main-navigation li,
            .main-nav li {
                width: 100%;
            }

            .main-navigation a,
            .main-nav a {
                display: block;
                width: 100%;
                text-align: center;
                padding: 15px 20px;
                color: white;
                border-radius: 8px;
                transition: all 0.3s ease;
            }

            .main-navigation a:hover,
            .main-nav a:hover {
                background: rgba(255,255,255,0.1);
                transform: translateY(-2px);
            }
        }

        /* Header Animations */
        .site-header {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .site-header.header-hidden {
            transform: translateY(-100%);
        }

        .site-header.scrolled {
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }

        /* Market Status */
        .market-status {
            font-size: 0.9rem;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            margin-right: 15px;
            transition: all 0.3s ease;
        }

        .market-status.open {
            background: rgba(46, 204, 113, 0.1);
            color: #27ae60;
            border: 1px solid rgba(46, 204, 113, 0.3);
        }

        .market-status.closed {
            background: rgba(231, 76, 60, 0.1);
            color: #e74c3c;
            border: 1px solid rgba(231, 76, 60, 0.3);
        }

        /* Widget Animations */
        .stock-scanner-widget {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* User Dropdown */
        .user-menu {
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .user-menu.show {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        /* Widget Error Styles */
        .widget-error {
            text-align: center;
            padding: 20px;
            color: #e74c3c;
            background: #fdf2f2;
            border-radius: 8px;
            margin: 10px 0;
        }

        .retry-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
            transition: background 0.3s ease;
        }

        .retry-btn:hover {
            background: #c0392b;
        }

        /* Accessibility improvements */
        .stock-scanner-widget:focus-within {
            outline: 2px solid #3498db;
            outline-offset: 2px;
        }

        /* Lazy loaded images */
        img[data-src] {
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        img.loaded {
            opacity: 1;
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            .stock-scanner-widget,
            .pricing-plan,
            .site-header,
            .notification {
                transition: none;
                animation: none;
            }
        }

        /* Dark mode support */
        [data-theme="dark"] .notification {
            background: #2d3748;
            color: #e2e8f0;
        }

        [data-theme="dark"] .notification-message {
            color: #e2e8f0;
        }

        [data-theme="dark"] .widget-error {
            background: #2d1b1b;
            color: #feb2b2;
        }

        /* Theme loading state */
        body:not(.theme-loaded) .stock-scanner-widget,
        body:not(.theme-loaded) .feature-card {
            opacity: 0;
        }

        body.theme-loaded .stock-scanner-widget,
        body.theme-loaded .feature-card {
            opacity: 1;
            transition: opacity 0.3s ease;
        }
    `;

    document.head.appendChild(themeStyles);

})();