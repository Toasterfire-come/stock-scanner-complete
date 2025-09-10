/**
 * Performance-Optimized JavaScript for WordPress Stock Scanner Pro Theme
 * Includes lazy loading, debouncing, and WordPress-specific optimizations
 */

(function($) {
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
            
            if ('IntersectionObserver' in window) {
                return new IntersectionObserver(callback, {...defaultOptions, ...options});
            }
            return null;
        }
    };
    
    // WordPress Theme Mobile Menu Optimization
    const wpMobileMenu = {
        init() {
            const toggle = document.querySelector('.menu-toggle');
            const nav = document.querySelector('.main-navigation');
            
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
            
            // Handle escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && nav.classList.contains('active')) {
                    this.close(nav, toggle);
                }
            });
        },
        
        toggle(nav) {
            nav.classList.toggle('active');
            const isExpanded = nav.classList.contains('active');
            
            // Update ARIA for accessibility
            const toggle = document.querySelector('.menu-toggle');
            if (toggle) {
                toggle.setAttribute('aria-expanded', isExpanded);
            }
            
            // Animate hamburger lines
            const lines = toggle.querySelectorAll('.hamburger-line');
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
        },
        
        close(nav, toggle) {
            nav.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
            
            // Reset hamburger animation
            const lines = toggle.querySelectorAll('.hamburger-line');
            lines.forEach(line => {
                line.style.transform = '';
                line.style.opacity = '';
            });
        },
        
        handleOutsideClick(toggle, nav, e) {
            if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                this.close(nav, toggle);
            }
        },
        
        handleLinkClick(nav, e) {
            if (e.target.tagName === 'A') {
                const toggle = document.querySelector('.menu-toggle');
                this.close(nav, toggle);
            }
        }
    };
    
    // WordPress Lazy Loading for Images
    const wpLazyLoader = {
        init() {
            // Lazy load images with data-src
            const images = document.querySelectorAll('img[data-src]');
            if (images.length > 0) {
                const imageObserver = perfUtils.createObserver(this.loadImage.bind(this));
                if (imageObserver) {
                    images.forEach(img => imageObserver.observe(img));
                } else {
                    // Fallback for older browsers
                    this.loadAllImages(images);
                }
            }
            
            // Lazy load WordPress content sections
            const sections = document.querySelectorAll('[data-lazy-load]');
            if (sections.length > 0) {
                const sectionObserver = perfUtils.createObserver(this.loadSection.bind(this));
                if (sectionObserver) {
                    sections.forEach(section => sectionObserver.observe(section));
                }
            }
        },
        
        loadImage(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Create new image to test loading
                    const newImg = new Image();
                    newImg.onload = () => {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.add('loaded');
                        img.style.opacity = '1';
                    };
                    newImg.onerror = () => {
                        img.classList.add('error');
                    };
                    newImg.src = img.dataset.src;
                    
                    observer.unobserve(img);
                }
            });
        },
        
        loadSection(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const section = entry.target;
                    const loadFunction = section.dataset.lazyLoad;
                    
                    // Check if function exists globally
                    if (window[loadFunction] && typeof window[loadFunction] === 'function') {
                        window[loadFunction](section);
                    }
                    
                    observer.unobserve(section);
                }
            });
        },
        
        loadAllImages(images) {
            // Fallback for browsers without Intersection Observer
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
            });
        }
    };
    
    // WordPress Performance Monitoring
    const wpPerfMonitor = {
        init() {
            // Only monitor in development or when explicitly enabled
            if (window.location.hostname === 'localhost' || 
                window.stockScannerTheme?.enablePerformanceMonitoring) {
                this.measurePageLoad();
                this.monitorResources();
            }
        },
        
        measurePageLoad() {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        console.log('WordPress Theme Performance:', {
                            'DNS Lookup': (perfData.domainLookupEnd - perfData.domainLookupStart).toFixed(2) + 'ms',
                            'Connection': (perfData.connectEnd - perfData.connectStart).toFixed(2) + 'ms',
                            'Request': (perfData.responseStart - perfData.requestStart).toFixed(2) + 'ms',
                            'Response': (perfData.responseEnd - perfData.responseStart).toFixed(2) + 'ms',
                            'DOM Processing': (perfData.domComplete - perfData.domLoading).toFixed(2) + 'ms',
                            'Total Load Time': (perfData.loadEventEnd - perfData.navigationStart).toFixed(2) + 'ms'
                        });
                    }
                }, 100);
            });
        },
        
        monitorResources() {
            window.addEventListener('load', () => {
                const resources = performance.getEntriesByType('resource');
                const slowResources = resources.filter(resource => resource.duration > 1000);
                
                if (slowResources.length > 0) {
                    console.warn('Slow loading resources:', slowResources.map(r => ({
                        name: r.name,
                        duration: r.duration.toFixed(2) + 'ms',
                        size: r.transferSize ? (r.transferSize / 1024).toFixed(2) + 'KB' : 'Unknown'
                    })));
                }
            });
        }
    };
    
    // WordPress Optimized Scroll Handling
    const wpScrollHandler = {
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
            const header = document.querySelector('.site-header');
            
            if (header) {
                if (scrollY > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
            
            // Trigger custom WordPress event
            if (typeof $ !== 'undefined') {
                $(document).trigger('wpScrollUpdate', [scrollY]);
            }
        }
    };
    
    // WordPress Form Optimization
    const wpFormHandler = {
        init() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                this.optimizeForm(form);
            });
            
            // Handle WordPress comment forms specifically
            const commentForm = document.getElementById('commentform');
            if (commentForm) {
                this.optimizeCommentForm(commentForm);
            }
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
            
            // Optimize form submission
            form.addEventListener('submit', this.handleSubmit.bind(this, form));
        },
        
        optimizeCommentForm(form) {
            // Add loading state to comment form
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('input[type="submit"]');
                if (submitBtn) {
                    submitBtn.value = 'Submitting...';
                    submitBtn.disabled = true;
                }
            });
        },
        
        validateInput(input) {
            const isValid = input.checkValidity();
            input.classList.toggle('invalid', !isValid);
            input.classList.toggle('valid', isValid);
            
            // WordPress-specific validation feedback
            let feedback = input.parentNode.querySelector('.validation-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'validation-feedback';
                input.parentNode.appendChild(feedback);
            }
            
            if (!isValid && input.validationMessage) {
                feedback.textContent = input.validationMessage;
                feedback.style.color = '#dc3545';
            } else {
                feedback.textContent = '';
            }
        },
        
        handleSubmit(form, e) {
            // Add loading animation
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
            }
        }
    };
    
    // Initialize all WordPress theme optimizations
    const wpThemePerformance = {
        init() {
            // Critical path - load immediately
            wpMobileMenu.init();
            
            // Non-critical - defer to prevent blocking
            setTimeout(() => {
                wpLazyLoader.init();
                wpScrollHandler.init();
                wpFormHandler.init();
                wpPerfMonitor.init();
            }, 100);
            
            // WordPress-specific initializations
            this.initWordPressFeatures();
        },
        
        initWordPressFeatures() {
            // Handle WordPress admin bar
            const adminBar = document.getElementById('wpadminbar');
            if (adminBar) {
                document.body.style.paddingTop = adminBar.offsetHeight + 'px';
            }
            
            // Optimize WordPress widgets
            const widgets = document.querySelectorAll('.widget');
            widgets.forEach(widget => {
                widget.style.opacity = '0';
                widget.style.transform = 'translateY(20px)';
                widget.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    widget.style.opacity = '1';
                    widget.style.transform = 'translateY(0)';
                }, Math.random() * 200);
            });
        }
    };
    
    // Initialize when DOM is ready
    const init = () => {
        wpThemePerformance.init();
    };
    
    // Use multiple initialization methods for maximum compatibility
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // jQuery compatibility
    if (typeof $ !== 'undefined') {
        $(document).ready(init);
    }
    
    // Export for WordPress global use
    window.wpStockScannerPerf = {
        utils: perfUtils,
        mobileMenu: wpMobileMenu,
        lazyLoader: wpLazyLoader,
        scrollHandler: wpScrollHandler,
        formHandler: wpFormHandler
    };
    
})(typeof jQuery !== 'undefined' ? jQuery : null);