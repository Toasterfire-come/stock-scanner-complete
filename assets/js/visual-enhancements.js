/**
 * Visual Enhancements JavaScript - Stock Scanner Pro Theme
 * Modern interactions, animations, and visual consistency
 */

(function() {
    'use strict';
    
    // Utility functions
    const utils = {
        select: (selector) => document.querySelector(selector),
        selectAll: (selector) => document.querySelectorAll(selector),
        
        ready: (callback) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', callback);
            } else {
                callback();
            }
        },

        throttle: (func, delay) => {
            let timeoutId;
            let lastExecTime = 0;
            return function (...args) {
                const currentTime = Date.now();
                
                if (currentTime - lastExecTime > delay) {
                    func.apply(this, args);
                    lastExecTime = currentTime;
                } else {
                    clearTimeout(timeoutId);
                    timeoutId = setTimeout(() => {
                        func.apply(this, args);
                        lastExecTime = Date.now();
                    }, delay - (currentTime - lastExecTime));
                }
            };
        },

        debounce: (func, delay) => {
            let timeoutId;
            return function (...args) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(this, args), delay);
            };
        }
    };

    // Animation Observer for scroll-triggered animations
    const AnimationObserver = {
        init() {
            if (!('IntersectionObserver' in window)) return;
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px'
            });

            // Observe all fade-up elements
            utils.selectAll('.fade-up, .fade-in, .scale-in, .slide-left').forEach(el => {
                observer.observe(el);
            });
        }
    };

    // Enhanced Button Interactions
    const ButtonEnhancements = {
        init() {
            // Add ripple effect to buttons
            utils.selectAll('.btn-system, .btn-primary-system, .btn-secondary-system, .btn-glass-system').forEach(button => {
                button.addEventListener('click', this.createRipple.bind(this));
            });

            // Enhanced hover effects
            utils.selectAll('.card-interactive').forEach(card => {
                this.enhanceCardHover(card);
            });
        },

        createRipple(e) {
            const button = e.currentTarget;
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                left: ${x}px;
                top: ${y}px;
                width: ${size}px;
                height: ${size}px;
                pointer-events: none;
            `;

            // Add ripple animation CSS if not exists
            if (!document.querySelector('#ripple-styles')) {
                const style = document.createElement('style');
                style.id = 'ripple-styles';
                style.textContent = `
                    @keyframes ripple {
                        to { transform: scale(4); opacity: 0; }
                    }
                `;
                document.head.appendChild(style);
            }

            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        },

        enhanceCardHover(card) {
            let tiltTimeout;

            card.addEventListener('mousemove', (e) => {
                clearTimeout(tiltTimeout);
                
                const rect = card.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const deltaX = (e.clientX - centerX) / rect.width;
                const deltaY = (e.clientY - centerY) / rect.height;

                const tiltX = deltaY * 5; // Max 5 degrees
                const tiltY = deltaX * -5;

                card.style.transform = `
                    perspective(1000px) 
                    rotateX(${tiltX}deg) 
                    rotateY(${tiltY}deg) 
                    translateY(-8px) 
                    scale(1.02)
                `;
            });

            card.addEventListener('mouseleave', () => {
                tiltTimeout = setTimeout(() => {
                    card.style.transform = '';
                }, 100);
            });
        }
    };

    // Enhanced Mobile Menu
    const MobileMenu = {
        init() {
            const toggleBtn = utils.select('.mobile-menu-toggle');
            const mobileNav = utils.select('.mobile-navigation');
            
            if (!toggleBtn || !mobileNav) return;

            toggleBtn.addEventListener('click', () => {
                this.toggle(toggleBtn, mobileNav);
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!toggleBtn.contains(e.target) && !mobileNav.contains(e.target)) {
                    this.close(toggleBtn, mobileNav);
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && mobileNav.style.display !== 'none') {
                    this.close(toggleBtn, mobileNav);
                }
            });
        },

        toggle(toggleBtn, mobileNav) {
            const isOpen = mobileNav.style.display !== 'none';
            
            if (isOpen) {
                this.close(toggleBtn, mobileNav);
            } else {
                this.open(toggleBtn, mobileNav);
            }
        },

        open(toggleBtn, mobileNav) {
            mobileNav.style.display = 'block';
            toggleBtn.setAttribute('aria-expanded', 'true');
            
            // Animate hamburger to X
            const lines = toggleBtn.querySelectorAll('.hamburger-line');
            if (lines.length >= 3) {
                lines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                lines[1].style.opacity = '0';
                lines[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
            }
        },

        close(toggleBtn, mobileNav) {
            mobileNav.style.display = 'none';
            toggleBtn.setAttribute('aria-expanded', 'false');
            
            // Reset hamburger
            const lines = toggleBtn.querySelectorAll('.hamburger-line');
            lines.forEach(line => {
                line.style.transform = '';
                line.style.opacity = '';
            });
        }
    };

    // Enhanced Theme Toggle
    const ThemeToggle = {
        init() {
            const toggleBtn = utils.select('#theme-toggle');
            if (!toggleBtn) return;

            // Load saved theme
            const savedTheme = localStorage.getItem('stock-scanner-theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
            
            this.setTheme(initialTheme);

            toggleBtn.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
                localStorage.setItem('stock-scanner-theme', newTheme);
            });
        },

        setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            
            const lightIcon = utils.select('.theme-icon-light');
            const darkIcon = utils.select('.theme-icon-dark');
            
            if (lightIcon && darkIcon) {
                if (theme === 'dark') {
                    lightIcon.style.display = 'none';
                    darkIcon.style.display = 'block';
                } else {
                    lightIcon.style.display = 'block';
                    darkIcon.style.display = 'none';
                }
            }

            // Update meta theme color
            const metaTheme = utils.select('meta[name="theme-color"]');
            if (metaTheme) {
                metaTheme.setAttribute('content', theme === 'dark' ? '#111827' : '#667eea');
            }
        }
    };

    // Enhanced User Menu
    const UserMenu = {
        init() {
            const userButton = utils.select('.user-avatar');
            const userDropdown = utils.select('.user-dropdown');
            
            if (!userButton || !userDropdown) return;

            userButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggle(userDropdown);
            });

            // Close on outside click
            document.addEventListener('click', () => {
                this.close(userDropdown);
            });

            // Prevent dropdown from closing when clicking inside
            userDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        },

        toggle(dropdown) {
            const isVisible = dropdown.style.display !== 'none';
            
            if (isVisible) {
                this.close(dropdown);
            } else {
                this.open(dropdown);
            }
        },

        open(dropdown) {
            dropdown.style.display = 'block';
            dropdown.style.opacity = '0';
            dropdown.style.transform = 'translateY(-10px)';
            
            // Animate in
            requestAnimationFrame(() => {
                dropdown.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                dropdown.style.opacity = '1';
                dropdown.style.transform = 'translateY(0)';
            });
        },

        close(dropdown) {
            dropdown.style.opacity = '0';
            dropdown.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                dropdown.style.display = 'none';
            }, 300);
        }
    };

    // Smooth Scrolling for Anchor Links
    const SmoothScroll = {
        init() {
            utils.selectAll('a[href^="#"]').forEach(link => {
                link.addEventListener('click', (e) => {
                    const targetId = link.getAttribute('href');
                    if (targetId === '#') return;
                    
                    const target = utils.select(targetId);
                    if (!target) return;
                    
                    e.preventDefault();
                    
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                });
            });
        }
    };

    // Performance Monitoring (Development Only)
    const PerformanceMonitor = {
        init() {
            if (window.location.hostname !== 'localhost' && !window.StockScannerDebug) return;
            
            // Monitor long tasks
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver((list) => {
                    list.getEntries().forEach((entry) => {
                        if (entry.duration > 50) {
                            console.warn('Long task detected:', entry);
                        }
                    });
                });
                
                observer.observe({ entryTypes: ['longtask'] });
            }
        }
    };

    // Form Enhancements
    const FormEnhancements = {
        init() {
            // Enhance all form inputs
            utils.selectAll('.form-input-system').forEach(input => {
                this.enhanceInput(input);
            });
        },

        enhanceInput(input) {
            const container = input.parentNode;
            
            // Add focus effect
            input.addEventListener('focus', () => {
                container.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                container.classList.remove('focused');
                if (!input.value.trim()) {
                    container.classList.remove('has-content');
                } else {
                    container.classList.add('has-content');
                }
            });
            
            // Check initial content
            if (input.value.trim()) {
                container.classList.add('has-content');
            }
        }
    };

    // Initialize all enhancements
    utils.ready(() => {
        AnimationObserver.init();
        ButtonEnhancements.init();
        MobileMenu.init();
        ThemeToggle.init();
        UserMenu.init();
        SmoothScroll.init();
        PerformanceMonitor.init();
        FormEnhancements.init();
        
        // Mark as loaded
        document.body.classList.add('visual-enhancements-loaded');
        
        console.log('✅ Stock Scanner Visual Enhancements Loaded');
    });

    // Export for global access
    window.StockScannerVisuals = {
        utils,
        AnimationObserver,
        ButtonEnhancements,
        ThemeToggle
    };

})();