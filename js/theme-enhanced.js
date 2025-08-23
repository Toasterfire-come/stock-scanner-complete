/**
 * Stock Scanner Pro Theme - Enhanced JavaScript v3.0.0
 * COMPLETE JAVASCRIPT OVERHAUL with Premium Interactions
 * 100% Vanilla JavaScript with advanced browser APIs and modern patterns
 * 
 * Features:
 * - Premium theme system with smooth transitions
 * - Advanced search with debouncing and caching
 * - Glassmorphism navigation effects
 * - Professional notification system
 * - Modern modal management
 * - Enhanced scroll animations
 * - Progressive loading states
 * - Performance optimizations
 */

(function() {
    'use strict';

    // ===== CORE THEME CLASS WITH ENHANCED FEATURES =====
    class StockScannerThemeEnhanced {
        constructor() {
            this.theme = this.getStoredTheme() || this.getSystemTheme();
            this.searchCache = new Map();
            this.observers = new Map();
            this.debounceTimers = new Map();
            this.loadingStates = new Set();
            this.notifications = [];
            this.modals = new Map();
            
            this.init();
        }

        // ===== INITIALIZATION =====
        init() {
            this.setTheme(this.theme);
            this.initializeComponents();
            this.setupEventListeners();
            this.initializeAnimations();
            this.initializePerformanceMonitoring();
            
            // Mark theme as loaded
            document.documentElement.classList.add('theme-loaded');
            console.log('✅ Stock Scanner Enhanced v3.0.0 - Theme loaded successfully');
        }

        // ===== ENHANCED THEME SYSTEM =====
        initializeComponents() {
            // Header enhancements
            this.initializeHeader();
            
            // Search system
            this.initializeSearch();
            
            // Navigation enhancements
            this.initializeNavigation();
            
            // Card animations
            this.initializeCards();
            
            // Form enhancements
            this.initializeForms();
            
            // Loading states
            this.initializeLoadingStates();
            
            console.log('✅ Stock Scanner Enhanced v3.0.0 - All components initialized');
        }

        // ===== PREMIUM HEADER WITH GLASSMORPHISM =====
        initializeHeader() {
            const header = document.querySelector('.site-header');
            if (!header) return;

            let lastScrollY = window.scrollY;
            let ticking = false;

            const updateHeader = () => {
                const scrollY = window.scrollY;
                const scrollDirection = scrollY > lastScrollY ? 'down' : 'up';
                
                // Add scrolled class for glassmorphism effect
                if (scrollY > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
                
                // Hide header on scroll down (optional)
                if (scrollY > 200 && scrollDirection === 'down') {
                    header.classList.add('header-hidden');
                } else {
                    header.classList.remove('header-hidden');
                }
                
                lastScrollY = scrollY;
                ticking = false;
            };

            const onScroll = () => {
                if (!ticking) {
                    requestAnimationFrame(updateHeader);
                    ticking = true;
                }
            };

            window.addEventListener('scroll', onScroll, { passive: true });

            // Logo hover effects
            const logoContainer = document.querySelector('.logo-container');
            if (logoContainer) {
                logoContainer.addEventListener('mouseenter', () => {
                    logoContainer.style.transform = 'translateY(-2px) scale(1.02)';
                });
                
                logoContainer.addEventListener('mouseleave', () => {
                    logoContainer.style.transform = '';
                });
            }
        }

        // ===== ADVANCED THEME TOGGLE =====
        toggleTheme() {
            const newTheme = this.theme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
            this.showNotification(`Switched to ${newTheme} mode`, 'info', 2000);
        }

        setTheme(theme) {
            this.theme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('stock-scanner-theme', theme);
            
            // Animate theme transition
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        }

        getStoredTheme() {
            return localStorage.getItem('stock-scanner-theme');
        }

        getSystemTheme() {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        // ===== PREMIUM SEARCH SYSTEM =====
        initializeSearch() {
            const searchToggle = document.querySelector('.search-toggle');
            const searchOverlay = document.querySelector('.search-overlay');
            const searchField = document.querySelector('.search-field');
            const searchClose = document.querySelector('.search-close');
            const searchForm = document.querySelector('.search-form');

            if (!searchToggle || !searchOverlay) return;

            // Show search overlay
            searchToggle.addEventListener('click', () => {
                this.showSearchOverlay();
            });

            // Hide search overlay
            searchClose?.addEventListener('click', () => {
                this.hideSearchOverlay();
            });

            // Close on overlay click
            searchOverlay.addEventListener('click', (e) => {
                if (e.target === searchOverlay) {
                    this.hideSearchOverlay();
                }
            });

            // Close on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && searchOverlay.classList.contains('show')) {
                    this.hideSearchOverlay();
                }
            });

            // Enhanced search functionality
            if (searchField) {
                this.initializeAdvancedSearch(searchField);
            }
        }

        showSearchOverlay() {
            const overlay = document.querySelector('.search-overlay');
            const field = document.querySelector('.search-field');
            
            if (overlay) {
                overlay.classList.add('show');
                overlay.setAttribute('aria-hidden', 'false');
                
                // Focus the search field after animation
                setTimeout(() => {
                    if (field) {
                        field.focus();
                    }
                }, 150);
            }
        }

        hideSearchOverlay() {
            const overlay = document.querySelector('.search-overlay');
            
            if (overlay) {
                overlay.classList.remove('show');
                overlay.setAttribute('aria-hidden', 'true');
            }
        }

        initializeAdvancedSearch(searchField) {
            let debounceTimer;
            
            searchField.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });

            // Search suggestions
            const searchTags = document.querySelectorAll('.search-tag');
            searchTags.forEach(tag => {
                tag.addEventListener('click', (e) => {
                    e.preventDefault();
                    const query = tag.textContent;
                    searchField.value = query;
                    this.performSearch(query);
                });
            });
        }

        performSearch(query) {
            if (!query.trim()) return;

            // Check cache first
            if (this.searchCache.has(query)) {
                const cachedResults = this.searchCache.get(query);
                this.displaySearchResults(cachedResults);
                return;
            }

            // Show loading state
            this.showSearchLoading();

            // Simulate API call (replace with actual API)
            setTimeout(() => {
                const results = this.mockSearchResults(query);
                this.searchCache.set(query, results);
                this.displaySearchResults(results);
                this.hideSearchLoading();
            }, 500);
        }

        mockSearchResults(query) {
            // Return empty results - implement real search functionality
            return [];
        }

        showSearchLoading() {
            // Implementation for search loading state
            console.log('Search loading...');
        }

        hideSearchLoading() {
            // Implementation for hiding search loading state
            console.log('Search complete');
        }

        displaySearchResults(results) {
            // Implementation for displaying search results
            console.log('Search results:', results);
        }

        // ===== PREMIUM NOTIFICATION SYSTEM =====
        showNotification(message, type = 'info', duration = 5000) {
            const notification = this.createNotification(message, type, duration);
            this.addNotificationToDOM(notification);
            
            // Auto-remove after duration
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, duration);
        }

        createNotification(message, type, duration) {
            const id = 'notification-' + Date.now() + Math.random().toString(36).substr(2, 9);
            const icons = {
                success: '✅',
                error: '❌',
                warning: '⚠️',
                info: 'ℹ️'
            };

            return {
                id,
                message,
                type,
                duration,
                icon: icons[type] || icons.info,
                timestamp: Date.now()
            };
        }

        addNotificationToDOM(notification) {
            // Create container if it doesn't exist
            let container = document.querySelector('.notification-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'notification-container';
                document.body.appendChild(container);
            }

            // Create notification element
            const element = document.createElement('div');
            element.className = `notification ${notification.type}`;
            element.id = notification.id;
            element.innerHTML = `
                <div class="notification-content">
                    <div class="notification-icon">${notification.icon}</div>
                    <div class="notification-text">
                        <div class="notification-message">${notification.message}</div>
                    </div>
                    <button class="notification-close" aria-label="Close notification">×</button>
                </div>
            `;

            // Add event listener for close button
            const closeBtn = element.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                this.removeNotification(notification.id);
            });

            // Add to container and show
            container.appendChild(element);
            
            // Trigger animation
            requestAnimationFrame(() => {
                element.classList.add('show');
            });

            this.notifications.push(notification);
        }

        removeNotification(id) {
            const element = document.getElementById(id);
            if (element) {
                element.classList.remove('show');
                setTimeout(() => {
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                }, 300);
            }

            // Remove from notifications array
            this.notifications = this.notifications.filter(n => n.id !== id);
        }

        // ===== ENHANCED NAVIGATION =====
        initializeNavigation() {
            const menuToggle = document.querySelector('.menu-toggle');
            const navigation = document.querySelector('.main-navigation');
            const userToggle = document.querySelector('.user-toggle');
            const userMenu = document.querySelector('.user-menu');

            // Mobile menu toggle
            if (menuToggle && navigation) {
                menuToggle.addEventListener('click', () => {
                    const isActive = navigation.classList.contains('mobile-active');
                    
                    if (isActive) {
                        navigation.classList.remove('mobile-active');
                        menuToggle.setAttribute('aria-expanded', 'false');
                    } else {
                        navigation.classList.add('mobile-active');
                        menuToggle.setAttribute('aria-expanded', 'true');
                    }
                });
            }

            // User dropdown menu
            if (userToggle && userMenu) {
                userToggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const isOpen = userMenu.classList.contains('show');
                    
                    if (isOpen) {
                        this.closeUserMenu();
                    } else {
                        this.openUserMenu();
                    }
                });

                // Close menu when clicking outside
                document.addEventListener('click', () => {
                    this.closeUserMenu();
                });

                userMenu.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
            }

            // Enhanced nav link hover effects
            const navLinks = document.querySelectorAll('.main-navigation a');
            navLinks.forEach(link => {
                link.addEventListener('mouseenter', () => {
                    link.style.transform = 'translateY(-2px) scale(1.05)';
                });
                
                link.addEventListener('mouseleave', () => {
                    link.style.transform = '';
                });
            });
        }

        openUserMenu() {
            const userToggle = document.querySelector('.user-toggle');
            const userMenu = document.querySelector('.user-menu');
            
            if (userToggle && userMenu) {
                userMenu.classList.add('show');
                userToggle.setAttribute('aria-expanded', 'true');
            }
        }

        closeUserMenu() {
            const userToggle = document.querySelector('.user-toggle');
            const userMenu = document.querySelector('.user-menu');
            
            if (userToggle && userMenu) {
                userMenu.classList.remove('show');
                userToggle.setAttribute('aria-expanded', 'false');
            }
        }

        // ===== ENHANCED CARD ANIMATIONS =====
        initializeCards() {
            const cards = document.querySelectorAll('.card, .feature-card, .pricing-plan, .stock-scanner-widget');
            
            cards.forEach(card => {
                // Enhanced hover effects
                card.addEventListener('mouseenter', () => {
                    card.style.transform = 'translateY(-8px) scale(1.02)';
                    card.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.2)';
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.transform = '';
                    card.style.boxShadow = '';
                });

                // Click animation
                card.addEventListener('mousedown', () => {
                    card.style.transform = 'translateY(-6px) scale(1.01)';
                });
                
                card.addEventListener('mouseup', () => {
                    card.style.transform = 'translateY(-8px) scale(1.02)';
                });
            });
        }

        // ===== SCROLL ANIMATIONS =====
        initializeAnimations() {
            // Intersection Observer for scroll animations
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            // Observe scroll reveal elements
            const revealElements = document.querySelectorAll('.scroll-reveal, .feature-card, .pricing-plan');
            revealElements.forEach(el => {
                observer.observe(el);
            });

            this.observers.set('scroll-reveal', observer);
        }

        // ===== FORM ENHANCEMENTS =====
        initializeForms() {
            const formControls = document.querySelectorAll('.form-control');
            
            formControls.forEach(control => {
                // Enhanced focus effects
                control.addEventListener('focus', () => {
                    control.parentElement?.classList.add('focused');
                    control.style.transform = 'translateY(-1px)';
                });
                
                control.addEventListener('blur', () => {
                    control.parentElement?.classList.remove('focused');
                    control.style.transform = '';
                });

                // Real-time validation feedback
                control.addEventListener('input', () => {
                    this.validateField(control);
                });
            });
        }

        validateField(field) {
            // Basic validation logic
            const isValid = field.checkValidity();
            
            if (isValid) {
                field.classList.remove('invalid');
                field.classList.add('valid');
            } else {
                field.classList.remove('valid');
                field.classList.add('invalid');
            }
        }

        // ===== LOADING STATES =====
        initializeLoadingStates() {
            const buttons = document.querySelectorAll('.btn');
            
            buttons.forEach(button => {
                button.addEventListener('click', (e) => {
                    // Skip if it's a link
                    if (button.tagName === 'A' && button.href) return;
                    
                    this.setButtonLoading(button, true);
                    
                    // Simulate async operation
                    setTimeout(() => {
                        this.setButtonLoading(button, false);
                    }, 2000);
                });
            });
        }

        setButtonLoading(button, isLoading) {
            if (isLoading) {
                button.classList.add('loading');
                button.disabled = true;
                button.setAttribute('aria-busy', 'true');
            } else {
                button.classList.remove('loading');
                button.disabled = false;
                button.removeAttribute('aria-busy');
            }
        }

        // ===== PERFORMANCE MONITORING =====
        initializePerformanceMonitoring() {
            if (typeof performance === 'undefined') return;

            // Page load performance
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    console.log('📊 Performance Metrics:', {
                        pageLoadTime: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                        domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                        firstPaint: this.getFirstPaint(),
                        memoryUsage: this.getMemoryUsage()
                    });
                }, 0);
            });
        }

        getFirstPaint() {
            const paintEntries = performance.getEntriesByType('paint');
            const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
            return firstPaint ? Math.round(firstPaint.startTime) : null;
        }

        getMemoryUsage() {
            if ('memory' in performance) {
                return {
                    used: Math.round(performance.memory.usedJSHeapSize / 1048576),
                    total: Math.round(performance.memory.totalJSHeapSize / 1048576),
                    limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
                };
            }
            return null;
        }

        // ===== EVENT LISTENERS SETUP =====
        setupEventListeners() {
            // Theme toggle
            const themeToggle = document.querySelector('.theme-toggle');
            if (themeToggle) {
                themeToggle.addEventListener('click', () => this.toggleTheme());
            }

            // System theme change detection
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!this.getStoredTheme()) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });

            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    switch (e.key) {
                        case 'k':
                            e.preventDefault();
                            this.showSearchOverlay();
                            break;
                        case 'd':
                            e.preventDefault();
                            window.location.href = '/dashboard/';
                            break;
                    }
                }
            });

            // Window events
            window.addEventListener('beforeunload', () => {
                this.cleanup();
            });
        }

        // ===== UTILITY METHODS =====
        debounce(func, wait, immediate) {
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
        }

        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }

        // ===== CLEANUP =====
        cleanup() {
            // Clean up observers
            this.observers.forEach(observer => observer.disconnect());
            this.observers.clear();
            
            // Clear timers
            this.debounceTimers.forEach(timer => clearTimeout(timer));
            this.debounceTimers.clear();
            
            // Clear cache
            this.searchCache.clear();
        }
    }

    // ===== INITIALIZATION =====
    let themeInstance;

    function initializeTheme() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                themeInstance = new StockScannerThemeEnhanced();
            });
        } else {
            themeInstance = new StockScannerThemeEnhanced();
        }
    }

    // ===== GLOBAL API =====
    window.stockScannerTheme = {
        toggleTheme: () => themeInstance?.toggleTheme(),
        showNotification: (message, type, duration) => themeInstance?.showNotification(message, type, duration),
        showSearchOverlay: () => themeInstance?.showSearchOverlay(),
        hideSearchOverlay: () => themeInstance?.hideSearchOverlay()
    };

    // Auto-initialize
    initializeTheme();

})();