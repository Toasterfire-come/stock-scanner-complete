/**
 * Stock Scanner Theme - Optimized Vanilla JavaScript
 * Production-ready, 100% vanilla JS implementation (NO jQuery)
 * Version: 2.2.0 - Fully Optimized
 */

(function() {
    'use strict';

    // Core utility functions
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
            if (element && className) element.classList.add(className);
        },

        removeClass: function(element, className) {
            if (element && className) element.classList.remove(className);
        },

        toggleClass: function(element, className) {
            if (element && className) element.classList.toggle(className);
        },

        hasClass: function(element, className) {
            return element ? element.classList.contains(className) : false;
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
        },

        animate: function(element, properties, duration = 300, callback = null) {
            if (!element) return;
            
            const start = performance.now();
            const startStyles = {};
            
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
        }
    };

    // Complete API client
    const API_BASE = '/api/';
    const Api = {
        base: API_BASE,
        // Root and system
        root: () => Api.get('/'),
        health: () => Api.get('/health/'),
        docs: () => Api.get('/docs/'),
        endpointStatus: () => Api.get('/endpoint-status/'),
        // Stocks (core)
        index: () => Api.get('/'),
        stocks: {
            list: () => Api.get('/stocks/'),
            detail: (ticker) => Api.get(`/stocks/${encodeURIComponent(ticker)}/`),
            detailAlias: (ticker) => Api.get(`/stock/${encodeURIComponent(ticker)}/`),
            search: (q) => Api.get(`/stocks/search/?q=${encodeURIComponent(q)}`),
            realtime: (ticker) => Api.get(`/realtime/${encodeURIComponent(ticker)}/`),
            trending: () => Api.get('/trending/'),
            marketStats: () => Api.get('/market-stats/'),
            filter: (params) => Api.get(`/filter/?${new URLSearchParams(params)}`),
            statistics: () => Api.get('/statistics/'),
        },
        // WordPress-friendly
        wordpress: {
            stocks: () => Api.get('/wordpress/stocks/'),
            news: () => Api.get('/wordpress/news/'),
            alerts: () => Api.get('/wordpress/alerts/'),
        },
        // Content update triggers (secured)
        content: {
            updateStocks: (body) => Api.post('/stocks/update/', body),
            updateNews: (body) => Api.post('/news/update/', body),
        },
        // Alerts
        alerts: {
            create: (body) => Api.post('/alerts/create/', body),
        },
        // Subscriptions
        subscription: (body) => Api.post('/subscription/', body),
        wordpressSubscribe: (body) => Api.post('/wordpress/subscribe/', body),
        // Auth, user, billing, notifications
        auth: {
            login: (body) => Api.post('/auth/login/', body),
            logout: (body) => Api.post('/auth/logout/', body),
        },
        user: {
            profile: (body, method = 'GET') => Api.request('/user/profile/', { method, body }),
            changePassword: (body) => Api.post('/user/change-password/', body),
            marketData: () => Api.get('/market-data/'),
            updatePayment: (body) => Api.post('/user/update-payment/', body),
            billingHistory: () => Api.get('/user/billing-history/'),
            billingHistoryAlt: () => Api.get('/billing/history/'),
            billingDownload: (invoiceId) => Api.get(`/billing/download/${encodeURIComponent(invoiceId)}/`),
            currentPlan: () => Api.get('/billing/current-plan/'),
            changePlan: (body) => Api.post('/billing/change-plan/', body),
            billingStats: () => Api.get('/billing/stats/'),
            updatePaymentMethod: (body) => Api.post('/billing/update-payment-method/', body),
            notificationSettings: (body, method='GET') => Api.request('/user/notification-settings/', { method, body }),
            notificationSettingsAlt: (body, method='GET') => Api.request('/notifications/settings/', { method, body }),
            notificationsHistory: () => Api.get('/notifications/history/'),
            notificationsMarkRead: (body) => Api.post('/notifications/mark-read/', body),
            usageStats: () => Api.get('/usage-stats/'),
        },
        // Portfolio (updated REST + legacy extras)
        portfolio: {
            get: () => Api.get('/portfolio/'),
            add: (body) => Api.post('/portfolio/add/', body),
            deleteHolding: (holdingId) => Api.delete(`/portfolio/${encodeURIComponent(holdingId)}/`),
            // legacy extras
            create: (body) => Api.post('/portfolio/create/', body),
            list: () => Api.get('/portfolio/list/'),
            deletePortfolio: (portfolioId) => Api.delete(`/portfolio/${encodeURIComponent(portfolioId)}/delete/`),
            updatePortfolio: (portfolioId, body) => Api.put(`/portfolio/${encodeURIComponent(portfolioId)}/update/`, body),
            performance: (portfolioId) => Api.get(`/portfolio/${encodeURIComponent(portfolioId)}/performance/`),
            addHolding: (body) => Api.post('/portfolio/add-holding/', body),
            sellHolding: (body) => Api.post('/portfolio/sell-holding/', body),
            importCsv: (body) => Api.post('/portfolio/import-csv/', body),
            alertRoi: () => Api.get('/portfolio/alert-roi/'),
        },
        // Watchlist (updated REST + legacy extras)
        watchlist: {
            get: () => Api.get('/watchlist/'),
            add: (body) => Api.post('/watchlist/add/', body),
            delete: (itemId) => Api.delete(`/watchlist/${encodeURIComponent(itemId)}/`),
            create: (body) => Api.post('/watchlist/create/', body),
            list: () => Api.get('/watchlist/list/'),
            update: (watchlistId, body) => Api.put(`/watchlist/${encodeURIComponent(watchlistId)}/update/`, body),
            deleteLegacy: (watchlistId) => Api.delete(`/watchlist/${encodeURIComponent(watchlistId)}/delete/`),
            performance: (watchlistId) => Api.get(`/watchlist/${encodeURIComponent(watchlistId)}/performance/`),
            addStock: (body) => Api.post('/watchlist/add-stock/', body),
            removeStock: (body) => Api.post('/watchlist/remove-stock/', body),
            updateItem: (itemId, body) => Api.put(`/watchlist/item/${encodeURIComponent(itemId)}/`, body),
            exportCsv: (watchlistId) => Api.get(`/watchlist/${encodeURIComponent(watchlistId)}/export/csv/`),
            exportJson: (watchlistId) => Api.get(`/watchlist/${encodeURIComponent(watchlistId)}/export/json/`),
            importCsv: (body) => Api.post('/watchlist/import/csv/', body),
            importJson: (body) => Api.post('/watchlist/import/json/', body),
        },
        // News personalization
        news: {
            feed: () => Api.get('/news/feed/'),
            markRead: (body) => Api.post('/news/mark-read/', body),
            markClicked: (body) => Api.post('/news/mark-clicked/', body),
            preferences: (body) => Api.post('/news/preferences/', body),
            syncPortfolio: (body) => Api.post('/news/sync-portfolio/', body),
            analytics: () => Api.get('/news/analytics/'),
        },
        // Revenue and discounts
        revenue: {
            validateDiscount: (body) => Api.post('/revenue/validate-discount/', body),
            applyDiscount: (body) => Api.post('/revenue/apply-discount/', body),
            recordPayment: (body) => Api.post('/revenue/record-payment/', body),
            revenueAnalytics: (monthYear) => monthYear ? Api.get(`/revenue/revenue-analytics/${encodeURIComponent(monthYear)}/`) : Api.get('/revenue/revenue-analytics/'),
            initializeCodes: (body) => Api.post('/revenue/initialize-codes/', body),
            monthlySummary: (monthYear) => Api.get(`/revenue/monthly-summary/${encodeURIComponent(monthYear)}/`),
        },
        // Core request helpers
        async request(endpoint, options={}) {
            const url = endpoint.startsWith('http') ? endpoint : `${Api.base.replace(/\/$/, '')}${endpoint}`;
            const headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
            const body = options.body && headers['Content-Type'] === 'application/json'
                ? JSON.stringify(options.body)
                : options.body || undefined;
            const resp = await fetch(url, Object.assign({}, options, { headers, body }));
            const contentType = resp.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');
            if (!resp.ok) {
                const errData = isJson ? await resp.json().catch(() => ({})) : await resp.text().catch(() => '');
                const error = new Error(`HTTP ${resp.status}`);
                error.data = errData;
                throw error;
            }
            return isJson ? resp.json() : resp.text();
        },
        get(endpoint, options={}) { return Api.request(endpoint, Object.assign({ method: 'GET' }, options)); },
        post(endpoint, body, options={}) { return Api.request(endpoint, Object.assign({ method: 'POST', body }, options)); },
        put(endpoint, body, options={}) { return Api.request(endpoint, Object.assign({ method: 'PUT', body }, options)); },
        delete(endpoint, options={}) { return Api.request(endpoint, Object.assign({ method: 'DELETE' }, options)); },
    };

    window.StockScannerAPI = Api;

    // Main Theme Controller
    class StockScannerTheme {
        constructor() {
            this.lastScrollTop = 0;
            this.isScrolling = false;
            this.init();
        }

        init() {
            this.setupMobileMenu();
            this.setupStickyHeader();
            this.setupSmoothScrolling();
            this.setupScrollAnimations();
            this.setupNotificationSystem();
            this.setupStockWidgets();
            this.setupKeyboardShortcuts();
            this.setupThemeToggle();
            this.setupUserDropdown();
            this.setupFormHandling();
            this.enhanceFooterInteractions();
        }

        setupMobileMenu() {
            const toggle = Utils.select('.menu-toggle');
            const nav = Utils.select('.main-navigation');
            
            if (!toggle || !nav) return;

            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileMenu(nav, toggle);
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                    this.closeMobileMenu(nav, toggle);
                }
            });

            // Close on link click
            nav.addEventListener('click', (e) => {
                if (e.target.tagName === 'A') {
                    this.closeMobileMenu(nav, toggle);
                }
            });

            // Close on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && Utils.hasClass(nav, 'mobile-active')) {
                    this.closeMobileMenu(nav, toggle);
                }
            });
        }

        toggleMobileMenu(nav, toggle) {
            Utils.toggleClass(nav, 'mobile-active');
            Utils.toggleClass(toggle, 'active');
            
            const isExpanded = Utils.hasClass(nav, 'mobile-active');
            toggle.setAttribute('aria-expanded', isExpanded);
            
            // Animate hamburger
            this.animateHamburger(toggle, isExpanded);
        }

        closeMobileMenu(nav, toggle) {
            Utils.removeClass(nav, 'mobile-active');
            Utils.removeClass(toggle, 'active');
            toggle.setAttribute('aria-expanded', 'false');
            this.animateHamburger(toggle, false);
        }

        animateHamburger(toggle, isActive) {
            const lines = Utils.selectAll('.hamburger-line', toggle);
            lines.forEach((line, index) => {
                if (isActive) {
                    if (index === 0) line.style.transform = 'rotate(45deg) translate(5px, 5px)';
                    if (index === 1) line.style.opacity = '0';
                    if (index === 2) line.style.transform = 'rotate(-45deg) translate(7px, -6px)';
                } else {
                    line.style.transform = '';
                    line.style.opacity = '';
                }
            });
        }

        setupStickyHeader() {
            const header = Utils.select('.site-header');
            if (!header) return;

            const handleScroll = Utils.throttle(() => {
                if (this.isScrolling) return;
                this.isScrolling = true;

                requestAnimationFrame(() => {
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    
                    if (scrollTop > this.lastScrollTop && scrollTop > 100) {
                        Utils.addClass(header, 'header-hidden');
                    } else {
                        Utils.removeClass(header, 'header-hidden');
                    }
                    
                    if (scrollTop > 50) {
                        Utils.addClass(header, 'scrolled');
                    } else {
                        Utils.removeClass(header, 'scrolled');
                    }
                    
                    this.lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
                    this.isScrolling = false;
                });
            }, 10);

            window.addEventListener('scroll', handleScroll, { passive: true });
        }

        setupSmoothScrolling() {
            const links = Utils.selectAll('a[href*="#"]');
            links.forEach(link => {
                link.addEventListener('click', (e) => {
                    const href = link.getAttribute('href');
                    if (href === '#' || href.indexOf('#') === -1) return;
                    
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

        setupScrollAnimations() {
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

            const animatedElements = Utils.selectAll('.scroll-reveal, .stock-scanner-widget, .card, .pricing-plan');
            animatedElements.forEach(el => {
                observer.observe(el);
            });
        }

        setupNotificationSystem() {
            if (!Utils.select('.notification-container')) {
                const container = document.createElement('div');
                container.className = 'notification-container';
                document.body.appendChild(container);
            }

            window.showNotification = (message, type = 'info', duration = 5000) => {
                this.createNotification(message, type, duration);
            };
        }

        createNotification(message, type, duration) {
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
                    <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
                </div>
            `;

            container.appendChild(notification);
            setTimeout(() => Utils.addClass(notification, 'show'), 100);

            if (duration > 0) {
                setTimeout(() => {
                    Utils.removeClass(notification, 'show');
                    setTimeout(() => notification.remove(), 500);
                }, duration);
            }
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

            // Copy stock symbol functionality
            const stockHeaders = Utils.selectAll('.stock-header h3');
            stockHeaders.forEach(header => {
                header.addEventListener('click', async () => {
                    const symbol = header.textContent.trim();
                    
                    try {
                        await navigator.clipboard.writeText(symbol);
                        this.createNotification(`Copied ${symbol}!`, 'success');
                    } catch (err) {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = symbol;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        this.createNotification(`Copied ${symbol}!`, 'success');
                    }
                });
            });

            // Auto-refresh functionality
            if (typeof stockScannerData !== 'undefined') {
                setInterval(() => {
                    if (document.visibilityState === 'visible') {
                        this.refreshStockData();
                    }
                }, 30000);
            }
        }

        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                if (this.isInputFocused(e.target)) return;

                // Ctrl/Cmd + R to refresh stock data
                if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                    e.preventDefault();
                    this.refreshStockData();
                    this.createNotification('🔄 Refreshing stock data...', 'info');
                }
                
                // 'D' key to go to dashboard
                if (e.key === 'd' || e.key === 'D') {
                    window.location.href = '/dashboard/';
                }
                
                // 'W' key to go to watchlist
                if (e.key === 'w' || e.key === 'W') {
                    window.location.href = '/watchlist/';
                }

                // Escape key to close modals and dropdowns
                if (e.key === 'Escape') {
                    this.closeAllModals();
                    this.closeAllDropdowns();
                }
            });
        }

        setupThemeToggle() {
            // Load saved theme or system preference
            const savedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
            
            document.documentElement.setAttribute('data-theme', initialTheme);

            // Global theme toggle function
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

            // Attach click handler to header theme toggle button
            Utils.ready(() => {
                const themeToggleBtn = Utils.select('.theme-toggle');
                if (themeToggleBtn) {
                    themeToggleBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        window.toggleTheme();
                    });
                }
            });

            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
                }
            });
        }

        setupUserDropdown() {
            const userToggle = Utils.select('.user-toggle');
            const userMenu = Utils.select('.user-menu');

            if (userToggle && userMenu) {
                userToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    Utils.toggleClass(userMenu, 'show');
                    const isExpanded = Utils.hasClass(userMenu, 'show');
                    userToggle.setAttribute('aria-expanded', isExpanded);
                });

                document.addEventListener('click', (e) => {
                    if (!userToggle.contains(e.target) && !userMenu.contains(e.target)) {
                        Utils.removeClass(userMenu, 'show');
                        userToggle.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        }

        setupFormHandling() {
            const forms = Utils.selectAll('form');
            forms.forEach(form => {
                this.enhanceForm(form);
            });
        }

        enhanceForm(form) {
            // Add loading states
            form.addEventListener('submit', (e) => {
                const submitBtn = Utils.select('input[type="submit"], button[type="submit"]', form);
                if (submitBtn) {
                    Utils.addClass(submitBtn, 'loading');
                    submitBtn.disabled = true;
                    
                    const originalText = submitBtn.textContent || submitBtn.value;
                    if (submitBtn.tagName === 'INPUT') {
                        submitBtn.value = 'Submitting...';
                    } else {
                        submitBtn.textContent = 'Submitting...';
                    }
                    
                    // Restore state after 5 seconds (fallback)
                    setTimeout(() => {
                        Utils.removeClass(submitBtn, 'loading');
                        submitBtn.disabled = false;
                        if (submitBtn.tagName === 'INPUT') {
                            submitBtn.value = originalText;
                        } else {
                            submitBtn.textContent = originalText;
                        }
                    }, 5000);
                }
            });

            // Input validation
            const inputs = Utils.selectAll('input, textarea, select', form);
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateInput(input);
                });
            });
        }

        validateInput(input) {
            const isValid = input.checkValidity();
            Utils.toggleClass(input, 'invalid', !isValid);
            Utils.toggleClass(input, 'valid', isValid);
        }

        setupModalSystem() {
            document.addEventListener('click', (e) => {
                // Modal triggers
                const trigger = e.target.closest('[data-modal]');
                if (trigger) {
                    e.preventDefault();
                    const modalId = trigger.dataset.modal;
                    const modal = Utils.select(`#${modalId}`);
                    if (modal) {
                        this.showModal(modal);
                    }
                }

                // Modal close buttons
                const closeBtn = e.target.closest('.modal-close, [data-modal-close]');
                if (closeBtn) {
                    e.preventDefault();
                    const modal = closeBtn.closest('.modal');
                    if (modal) {
                        this.hideModal(modal);
                    }
                }

                // Backdrop click
                if (e.target.classList.contains('modal')) {
                    this.hideModal(e.target);
                }
            });
        }

        showModal(modal) {
            Utils.addClass(modal, 'show');
            document.body.style.overflow = 'hidden';
            
            // Focus management
            const focusable = Utils.select('input, button, select, textarea, [tabindex]:not([tabindex="-1"])', modal);
            if (focusable) {
                setTimeout(() => focusable.focus(), 100);
            }
        }

        hideModal(modal) {
            Utils.removeClass(modal, 'show');
            document.body.style.overflow = '';
        }

        setupPerformanceMonitoring() {
            if (performance.mark && performance.measure && 
                (window.location.hostname === 'localhost' || 
                 (typeof stockScannerData !== 'undefined' && stockScannerData.enablePerformanceMonitoring))) {
                
                performance.mark('theme-js-loaded');
                
                window.addEventListener('load', () => {
                    performance.mark('page-loaded');
                    
                    try {
                        performance.measure('page-load-time', 'navigationStart', 'page-loaded');
                        const loadTime = performance.getEntriesByName('page-load-time')[0];
                        
                        if (loadTime && console.log) {
                            console.log(`📊 Stock Scanner (Vanilla JS) loaded in ${Math.round(loadTime.duration)}ms`);
                        }
                    } catch (e) {
                        // Ignore performance measurement errors
                    }
                });
            }
        }

        setupSearchFunctionality() {
            const searchToggle = Utils.select('.search-toggle');
            const searchOverlay = Utils.select('.search-overlay');
            const searchClose = Utils.select('.search-close');
            const searchField = Utils.select('.search-field');
            
            // Toggle search overlay
            if (searchToggle && searchOverlay) {
                searchToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showSearchOverlay();
                });
            }
            
            // Close search overlay
            if (searchClose) {
                searchClose.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.hideSearchOverlay();
                });
            }
            
            // Close on overlay click
            if (searchOverlay) {
                searchOverlay.addEventListener('click', (e) => {
                    if (e.target === searchOverlay) {
                        this.hideSearchOverlay();
                    }
                });
            }
            
            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && searchOverlay && Utils.hasClass(searchOverlay, 'show')) {
                    this.hideSearchOverlay();
                }
            });
            
            // Search functionality
            const searchInputs = Utils.selectAll('.search-input, input[type="search"]');
            searchInputs.forEach(input => {
                input.addEventListener('input', Utils.debounce((e) => {
                    const query = e.target.value.trim();
                    if (query.length >= 2) {
                        this.performSearch(query, input);
                    }
                }, 300));
            });
        }
        
        showSearchOverlay() {
            const searchOverlay = Utils.select('.search-overlay');
            const searchField = Utils.select('.search-field');
            
            if (searchOverlay) {
                Utils.addClass(searchOverlay, 'show');
                searchOverlay.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden';
                
                // Focus search field
                if (searchField) {
                    setTimeout(() => searchField.focus(), 100);
                }
            }
        }
        
        hideSearchOverlay() {
            const searchOverlay = Utils.select('.search-overlay');
            
            if (searchOverlay) {
                Utils.removeClass(searchOverlay, 'show');
                searchOverlay.setAttribute('aria-hidden', 'true');
                document.body.style.overflow = '';
            }
        }

        performSearch(query, input) {
            // Add search functionality here
            console.log('Searching for:', query);
        }

        initializeComponents() {
            // Initialize dashboard components
            if (Utils.select('.stock-scanner-dashboard')) {
                this.initDashboard();
            }

            // Initialize pricing components
            if (Utils.select('.pricing-table')) {
                this.initPricingTable();
            }

            // Mark theme as loaded
            setTimeout(() => {
                Utils.addClass(document.body, 'theme-loaded');
            }, 100);
        }

        initDashboard() {
            const dashboard = Utils.select('.stock-scanner-dashboard');
            if (!dashboard) return;

            // Refresh button functionality
            const refreshBtn = Utils.select('[data-action="refresh"]', dashboard);
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.refreshDashboardData();
                });
            }

            // Export button functionality
            const exportBtn = Utils.select('[data-action="export"]', dashboard);
            if (exportBtn) {
                exportBtn.addEventListener('click', () => {
                    this.exportDashboardData();
                });
            }

            // Load initial data
            this.loadDashboardData();
        }

        initPricingTable() {
            const pricingPlans = Utils.selectAll('.pricing-plan');
            pricingPlans.forEach(plan => {
                plan.addEventListener('mouseenter', () => {
                    Utils.addClass(plan, 'highlighted');
                });
                
                plan.addEventListener('mouseleave', () => {
                    Utils.removeClass(plan, 'highlighted');
                });
            });
        }

        // API and data methods
        async loadDashboardData() {
            if (typeof window.StockScannerAPI === 'undefined') return;

            try {
                const data = await StockScannerAPI.portfolio.get();
                // Normalize shape if backend returns {success,data}
                const payload = data && data.data ? data.data : data;
                this.updateDashboardData(payload);
            } catch (error) {
                console.error('Failed to load dashboard data', error);
            }
        }

        updateDashboardData(data) {
            const totalValueEl = Utils.select('[data-portfolio="total-value"]');
            const dailyChangeEl = Utils.select('[data-portfolio="daily-change"]');
            const totalReturnEl = Utils.select('[data-portfolio="total-return"]');

            if (totalValueEl) totalValueEl.textContent = `$${data.total_value.toLocaleString()}`;
            if (dailyChangeEl) dailyChangeEl.textContent = `+$${data.daily_change.toLocaleString()}`;
            if (totalReturnEl) totalReturnEl.textContent = '+5.25%';
        }

        refreshDashboardData() {
            this.createNotification('Refreshing dashboard...', 'info', 2000);
            this.loadDashboardData();
        }

        refreshStockData() {
            const widgets = Utils.selectAll('.stock-scanner-widget');
            widgets.forEach(widget => {
                Utils.addClass(widget, 'refreshing');
                setTimeout(() => {
                    Utils.removeClass(widget, 'refreshing');
                }, 1000);
            });
        }

        exportDashboardData() {
            this.createNotification('Exporting data...', 'info', 2000);
            // Export functionality here
        }

        // Utility methods
        isInputFocused(element) {
            const inputTypes = ['INPUT', 'TEXTAREA', 'SELECT'];
            return inputTypes.includes(element.tagName) || element.isContentEditable;
        }

        closeAllModals() {
            const activeModals = Utils.selectAll('.modal.show');
            activeModals.forEach(modal => this.hideModal(modal));
        }

        closeAllDropdowns() {
            const activeDropdowns = Utils.selectAll('.user-menu.show, .dropdown.show');
            activeDropdowns.forEach(dropdown => {
                Utils.removeClass(dropdown, 'show');
            });
        }

        enhanceFooterInteractions() {
            // Smooth scroll for footer in-page links
            const footerLinks = Utils.selectAll('.footer-menu a[href^="#"]');
            footerLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            });

            // Add loading states to CTA buttons
            const ctaButtons = Utils.selectAll('.cta-buttons .btn');
            ctaButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.style.opacity = '0.7';
                    this.textContent = 'Loading...';
                });
            });
        }
    }

    // Initialize theme when DOM is ready
    Utils.ready(() => {
        window.stockScannerTheme = new StockScannerTheme();
        
        // Export utilities for global use
        window.StockScannerUtils = Utils;
        
        // Mark as initialized
        Utils.addClass(document.body, 'vanilla-js-initialized');
        document.body.classList.add('theme-fully-loaded');
        
        console.log('🚀 Stock Scanner Theme loaded (100% Vanilla JS)');
    });

})();