/**
 * Performance-Optimized Vanilla JavaScript for WordPress Stock Scanner Pro Theme
 * Pure vanilla JS implementation without jQuery dependencies
 */

(function() {
    'use strict';
    
    // Performance utilities
    const PerfUtils = {
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
        },

        // DOM ready helper
        ready: (callback) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', callback);
            } else {
                callback();
            }
        },

        // Selector helpers
        select: (selector, context = document) => context.querySelector(selector),
        selectAll: (selector, context = document) => context.querySelectorAll(selector)
    };
    
    // WordPress Theme Mobile Menu Optimization
    const WPMobileMenu = {
        init() {
            const toggle = PerfUtils.select('.menu-toggle');
            const nav = PerfUtils.select('.main-navigation');
            
            if (!toggle || !nav) return;
            
            // Use event delegation for better performance
            toggle.addEventListener('click', this.toggle.bind(this, nav), { passive: true });
            
            // Close on outside click (debounced for performance)
            document.addEventListener('click', 
                PerfUtils.debounce(this.handleOutsideClick.bind(this, toggle, nav), 100), 
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
            const toggle = PerfUtils.select('.menu-toggle');
            if (toggle) {
                toggle.setAttribute('aria-expanded', isExpanded);
            }
            
            // Animate hamburger lines with vanilla JS
            const lines = PerfUtils.selectAll('.hamburger-line', toggle);
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
            const lines = PerfUtils.selectAll('.hamburger-line', toggle);
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
                const toggle = PerfUtils.select('.menu-toggle');
                this.close(nav, toggle);
            }
        }
    };
    
    // WordPress Lazy Loading for Images
    const WPLazyLoader = {
        init() {
            // Lazy load images with data-src
            const images = PerfUtils.selectAll('img[data-src]');
            if (images.length > 0) {
                const imageObserver = PerfUtils.createObserver(this.loadImage.bind(this));
                if (imageObserver) {
                    images.forEach(img => imageObserver.observe(img));
                } else {
                    // Fallback for older browsers
                    this.loadAllImages(images);
                }
            }
            
            // Lazy load WordPress content sections
            const sections = PerfUtils.selectAll('[data-lazy-load]');
            if (sections.length > 0) {
                const sectionObserver = PerfUtils.createObserver(this.loadSection.bind(this));
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
                        img.alt = 'Failed to load image';
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
    const WPPerfMonitor = {
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
                    if (!performance.getEntriesByType) return;
                    
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData && console.log) {
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
                if (!performance.getEntriesByType) return;
                
                const resources = performance.getEntriesByType('resource');
                const slowResources = resources.filter(resource => resource.duration > 1000);
                
                if (slowResources.length > 0 && console.warn) {
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
    const WPScrollHandler = {
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
            const header = PerfUtils.select('.site-header');
            
            if (header) {
                if (scrollY > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
            
            // Trigger custom event for other components
            const scrollEvent = new CustomEvent('wpScrollUpdate', { 
                detail: { scrollY: scrollY }
            });
            document.dispatchEvent(scrollEvent);
        }
    };
    
    // WordPress Form Optimization
    const WPFormHandler = {
        init() {
            const forms = PerfUtils.selectAll('form');
            forms.forEach(form => {
                this.optimizeForm(form);
            });
            
            // Handle WordPress comment forms specifically
            const commentForm = PerfUtils.select('#commentform');
            if (commentForm) {
                this.optimizeCommentForm(commentForm);
            }
        },
        
        optimizeForm(form) {
            // Debounce input validation
            const inputs = PerfUtils.selectAll('input, textarea, select', form);
            inputs.forEach(input => {
                input.addEventListener('input', 
                    PerfUtils.debounce(this.validateInput.bind(this, input), 300),
                    { passive: true }
                );
            });
            
            // Optimize form submission
            form.addEventListener('submit', this.handleSubmit.bind(this, form));
        },
        
        optimizeCommentForm(form) {
            // Add loading state to comment form
            form.addEventListener('submit', (e) => {
                const submitBtn = PerfUtils.select('input[type="submit"]', form);
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
            const submitBtn = PerfUtils.select('input[type="submit"], button[type="submit"]', form);
            if (submitBtn) {
                submitBtn.classList.add('loading');
                
                // Add spinner
                const spinner = document.createElement('span');
                spinner.className = 'spinner';
                spinner.innerHTML = '⟳';
                spinner.style.cssText = 'animation: spin 1s linear infinite; margin-left: 5px;';
                submitBtn.appendChild(spinner);
            }
        }
    };

    // Enhanced Features
    const WPEnhancedFeatures = {
        init() {
            this.setupThemeToggle();
            this.setupProgressBars();
            this.setupTooltips();
            this.setupModals();
        },

        setupThemeToggle() {
            // Load saved theme or system preference
            const savedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
            
            document.documentElement.setAttribute('data-theme', initialTheme);

            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
                }
            });

            // Global theme toggle function
            window.toggleTheme = () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Update meta theme color
                const metaThemeColor = PerfUtils.select('meta[name="theme-color"]');
                if (metaThemeColor) {
                    metaThemeColor.setAttribute('content', newTheme === 'dark' ? '#1a1a1a' : '#ffffff');
                }
            };
        },

        setupProgressBars() {
            const progressBars = PerfUtils.selectAll('.progress-bar[data-progress]');
            
            const progressObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const bar = entry.target;
                        const progress = bar.dataset.progress;
                        const fill = PerfUtils.select('.progress-fill', bar);
                        
                        if (fill) {
                            fill.style.width = '0%';
                            setTimeout(() => {
                                fill.style.transition = 'width 1s ease-out';
                                fill.style.width = progress + '%';
                            }, 100);
                        }
                        
                        progressObserver.unobserve(bar);
                    }
                });
            });

            progressBars.forEach(bar => progressObserver.observe(bar));
        },

        setupTooltips() {
            document.addEventListener('mouseenter', (e) => {
                const target = e.target.closest('[data-tooltip]');
                if (target) {
                    this.showTooltip(target, target.dataset.tooltip);
                }
            }, true);

            document.addEventListener('mouseleave', (e) => {
                const target = e.target.closest('[data-tooltip]');
                if (target) {
                    this.hideTooltip(target);
                }
            }, true);
        },

        showTooltip(element, text) {
            if (element._tooltip) return;

            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = text;
            tooltip.style.cssText = `
                position: absolute;
                background: #2c3e50;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 0.85rem;
                z-index: 10000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                white-space: nowrap;
            `;

            document.body.appendChild(tooltip);

            const rect = element.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();
            
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltipRect.width / 2}px`;
            tooltip.style.top = `${rect.top - tooltipRect.height - 5}px`;

            setTimeout(() => tooltip.style.opacity = '1', 10);
            element._tooltip = tooltip;
        },

        hideTooltip(element) {
            if (element._tooltip) {
                element._tooltip.remove();
                delete element._tooltip;
            }
        },

        setupModals() {
            // Modal trigger handling
            document.addEventListener('click', (e) => {
                const trigger = e.target.closest('[data-modal]');
                if (trigger) {
                    e.preventDefault();
                    const modalId = trigger.dataset.modal;
                    const modal = PerfUtils.select(`#${modalId}`);
                    if (modal) {
                        this.showModal(modal);
                    }
                }

                // Modal close handling
                const closeBtn = e.target.closest('.modal-close, [data-modal-close]');
                if (closeBtn) {
                    e.preventDefault();
                    const modal = closeBtn.closest('.modal');
                    if (modal) {
                        this.hideModal(modal);
                    }
                }
            });

            // Close modal on backdrop click
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal')) {
                    this.hideModal(e.target);
                }
            });

            // Close modal on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    const activeModal = PerfUtils.select('.modal.show');
                    if (activeModal) {
                        this.hideModal(activeModal);
                    }
                }
            });
        },

        showModal(modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Focus first focusable element
            const focusable = PerfUtils.select('input, button, select, textarea, [tabindex]:not([tabindex="-1"])', modal);
            if (focusable) {
                setTimeout(() => focusable.focus(), 100);
            }
        },

        hideModal(modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    };
    
    // Initialize all WordPress theme optimizations
    const WPThemePerformance = {
        init() {
            // Critical path - load immediately
            WPMobileMenu.init();
            
            // Non-critical - defer to prevent blocking
            setTimeout(() => {
                WPLazyLoader.init();
                WPScrollHandler.init();
                WPFormHandler.init();
                WPPerfMonitor.init();
                WPEnhancedFeatures.init();
            }, 100);
            
            // WordPress-specific initializations
            this.initWordPressFeatures();
        },
        
        initWordPressFeatures() {
            // Handle WordPress admin bar
            const adminBar = PerfUtils.select('#wpadminbar');
            if (adminBar) {
                document.body.style.paddingTop = adminBar.offsetHeight + 'px';
            }
            
            // Optimize WordPress widgets with staggered animation
            const widgets = PerfUtils.selectAll('.widget');
            widgets.forEach((widget, index) => {
                widget.style.opacity = '0';
                widget.style.transform = 'translateY(20px)';
                widget.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    widget.style.opacity = '1';
                    widget.style.transform = 'translateY(0)';
                }, 100 + (index * 50));
            });

            // Add loading completed class
            setTimeout(() => {
                document.body.classList.add('wp-theme-loaded');
            }, 500);
        }
    };
    
    // Initialize when DOM is ready
    const init = () => {
        WPThemePerformance.init();
    };
    
    // Use multiple initialization methods for maximum compatibility
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export for WordPress global use
    window.wpStockScannerPerf = {
        utils: PerfUtils,
        mobileMenu: WPMobileMenu,
        lazyLoader: WPLazyLoader,
        scrollHandler: WPScrollHandler,
        formHandler: WPFormHandler,
        enhancedFeatures: WPEnhancedFeatures
    };

    // Add performance CSS
    const perfStyles = document.createElement('style');
    perfStyles.textContent = `
        /* Performance optimizations */
        .wp-theme-loaded .widget {
            will-change: auto;
        }

        .loading {
            position: relative;
        }

        .loading::after {
            content: '';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: translateY(-50%) rotate(0deg); }
            100% { transform: translateY(-50%) rotate(360deg); }
        }

        .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
        }

        /* Modal styles */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }

        .modal.show {
            opacity: 1;
            visibility: visible;
        }

        .modal-content {
            background: white;
            border-radius: 8px;
            max-width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }

        .modal.show .modal-content {
            transform: scale(1);
        }

        /* Progress bars */
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
        }

        /* Validation styles */
        .validation-feedback {
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        input.invalid,
        textarea.invalid,
        select.invalid {
            border-color: #dc3545;
        }

        input.valid,
        textarea.valid,
        select.valid {
            border-color: #28a745;
        }

        /* Image loading states */
        img[data-src] {
            background: #f8f9fa;
            min-height: 100px;
        }

        img.loaded {
            animation: fadeIn 0.3s ease;
        }

        img.error {
            background: #f8d7da;
            color: #721c24;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        img.error::before {
            content: '⚠ Failed to load';
            font-size: 0.875rem;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Dark theme optimizations */
        [data-theme="dark"] .modal-content {
            background: #2d3748;
            color: #e2e8f0;
        }

        [data-theme="dark"] .progress-bar {
            background: #4a5568;
        }

        [data-theme="dark"] .tooltip {
            background: #1a202c !important;
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            .widget,
            .modal,
            .progress-fill {
                transition: none;
                animation: none;
            }
        }
    `;

    document.head.appendChild(perfStyles);
    
})();