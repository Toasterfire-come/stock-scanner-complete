/**
 * Optimized JavaScript for Stock Scanner API
 * Performance-focused with lazy loading and efficient DOM manipulation
 */

(function() {
    'use strict';
    
    // Performance utilities
    const perfUtils = {
        // Debounce function for performance
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Throttle function for scroll events
        throttle: (func, limit) => {
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
        
        // Intersection Observer for lazy loading
        createObserver: (callback, options = {}) => {
            const defaultOptions = {
                root: null,
                rootMargin: '50px',
                threshold: 0.1
            };
            return new IntersectionObserver(callback, {...defaultOptions, ...options});
        }
    };
    
    // Mobile menu optimization
    const mobileMenu = {
        init() {
            const toggle = document.querySelector('.mobile-menu-toggle');
            const nav = document.querySelector('.nav, #nav-menu');
            
            if (!toggle || !nav) return;
            
            // Use event delegation for better performance
            toggle.addEventListener('click', this.toggle.bind(this, nav), { passive: true });
            
            // Close on outside click (debounced for performance)
            document.addEventListener('click', 
                perfUtils.debounce(this.handleOutsideClick.bind(this, toggle, nav), 100), 
                { passive: true }
            );
            
            // Close on link click
            nav.addEventListener('click', this.handleLinkClick.bind(this, nav), { passive: true });
        },
        
        toggle(nav) {
            nav.classList.toggle('active');
            const isExpanded = nav.classList.contains('active');
            
            // Update ARIA for accessibility
            const toggle = document.querySelector('.mobile-menu-toggle');
            if (toggle) {
                toggle.setAttribute('aria-expanded', isExpanded);
            }
        },
        
        handleOutsideClick(toggle, nav, e) {
            if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                nav.classList.remove('active');
                toggle.setAttribute('aria-expanded', 'false');
            }
        },
        
        handleLinkClick(nav, e) {
            if (e.target.tagName === 'A') {
                nav.classList.remove('active');
                const toggle = document.querySelector('.mobile-menu-toggle');
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            }
        }
    };
    
    // Lazy loading for images and content
    const lazyLoader = {
        init() {
            // Lazy load images
            const images = document.querySelectorAll('img[data-src]');
            if (images.length > 0) {
                const imageObserver = perfUtils.createObserver(this.loadImage.bind(this));
                images.forEach(img => imageObserver.observe(img));
            }
            
            // Lazy load heavy content sections
            const sections = document.querySelectorAll('[data-lazy-load]');
            if (sections.length > 0) {
                const sectionObserver = perfUtils.createObserver(this.loadSection.bind(this));
                sections.forEach(section => sectionObserver.observe(section));
            }
        },
        
        loadImage(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        },
        
        loadSection(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const section = entry.target;
                    const loadFunction = section.dataset.lazyLoad;
                    if (window[loadFunction] && typeof window[loadFunction] === 'function') {
                        window[loadFunction](section);
                    }
                    observer.unobserve(section);
                }
            });
        }
    };
    
    // Performance monitoring
    const perfMonitor = {
        init() {
            // Monitor Core Web Vitals
            if ('web-vital' in window) {
                this.measureCLS();
                this.measureFID();
                this.measureLCP();
            }
            
            // Monitor resource loading
            this.monitorResources();
        },
        
        measureCLS() {
            let clsValue = 0;
            let clsEntries = [];
            
            const observer = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        clsEntries.push(entry);
                    }
                }
            });
            
            observer.observe({entryTypes: ['layout-shift']});
        },
        
        measureFID() {
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    const FID = entry.processingStart - entry.startTime;
                    console.log('FID:', FID);
                }
            }).observe({entryTypes: ['first-input']});
        },
        
        measureLCP() {
            new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.startTime);
            }).observe({entryTypes: ['largest-contentful-paint']});
        },
        
        monitorResources() {
            // Monitor slow loading resources
            window.addEventListener('load', () => {
                const resources = performance.getEntriesByType('resource');
                resources.forEach(resource => {
                    if (resource.duration > 1000) { // Resources taking > 1s
                        console.warn('Slow resource:', resource.name, resource.duration + 'ms');
                    }
                });
            });
        }
    };
    
    // Optimized scroll handling
    const scrollHandler = {
        init() {
            let ticking = false;
            
            const handleScroll = () => {
                if (!ticking) {
                    requestAnimationFrame(() => {
                        this.updateScrollPosition();
                        ticking = false;
                    });
                    ticking = true;
                }
            };
            
            window.addEventListener('scroll', handleScroll, { passive: true });
        },
        
        updateScrollPosition() {
            const scrollY = window.pageYOffset;
            const header = document.querySelector('.header, .site-header');
            
            if (header) {
                if (scrollY > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
        }
    };
    
    // Form optimization
    const formHandler = {
        init() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                this.optimizeForm(form);
            });
        },
        
        optimizeForm(form) {
            // Debounce input validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('input', 
                    perfUtils.debounce(this.validateInput.bind(this, input), 300),
                    { passive: true }
                );
            });
        },
        
        validateInput(input) {
            // Simple validation logic
            const isValid = input.checkValidity();
            input.classList.toggle('invalid', !isValid);
            input.classList.toggle('valid', isValid);
        }
    };
    
    // Initialize everything when DOM is ready
    const init = () => {
        // Critical path - load immediately
        mobileMenu.init();
        
        // Non-critical - defer to prevent blocking
        setTimeout(() => {
            lazyLoader.init();
            scrollHandler.init();
            formHandler.init();
            
            // Only monitor performance in development/staging
            if (window.location.hostname === 'localhost' || window.location.hostname.includes('staging')) {
                perfMonitor.init();
            }
        }, 100);
    };
    
    // Use the most efficient DOM ready method
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export for potential external use
    window.stockScannerPerf = {
        utils: perfUtils,
        mobileMenu,
        lazyLoader
    };
    
})();