/**
 * Main Theme JavaScript
 * 
 * @package RetailTradeScanner
 */

(function() {
    'use strict';
    
    // Global RTS namespace
    window.RTS = {
        // Configuration
        config: {
            apiUrl: rtsAjax?.ajaxurl || '/wp-admin/admin-ajax.php',
            nonce: rtsAjax?.nonce || '',
            themeUrl: rtsAjax?.theme_url || '',
            debug: false
        },
        
        // Utility functions
        utils: {},
        
        // Component modules
        components: {},
        
        // Initialize theme
        init: function() {
            this.initComponents();
            this.initInteractivity();
            this.initAccessibility();
            this.initPerformanceOptimizations();
        },
        
        // Show success message
        showSuccess: function(message) {
            this.showToast(message, 'success');
        },
        
        // Show info message
        showInfo: function(message) {
            this.showToast(message, 'info');
        },
        
        // Show warning message
        showWarning: function(message) {
            this.showToast(message, 'warning');
        },
        
        // Show error message
        showError: function(message) {
            this.showToast(message, 'error');
        },
        
        // Show toast notification
        showToast: function(message, type = 'info') {
            const toast = this.createToast(message, type);
            const container = this.getToastContainer();
            container.appendChild(toast);
            
            // Animate in
            requestAnimationFrame(() => {
                toast.classList.add('toast-show');
            });
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                this.removeToast(toast);
            }, 5000);
        },
        
        createToast: function(message, type) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <div class="toast-content">
                    <div class="toast-icon">
                        ${this.getToastIcon(type)}
                    </div>
                    <div class="toast-message">${message}</div>
                    <button class="toast-close" aria-label="Close notification">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            `;
            
            // Add close functionality
            toast.querySelector('.toast-close').addEventListener('click', () => {
                this.removeToast(toast);
            });
            
            return toast;
        },
        
        getToastIcon: function(type) {
            const icons = {
                success: '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
                info: '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
                warning: '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>',
                error: '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>'
            };
            return icons[type] || icons.info;
        },
        
        getToastContainer: function() {
            let container = document.querySelector('.toast-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
            return container;
        },
        
        removeToast: function(toast) {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    };
    
    // Utility Functions
    RTS.utils = {
        // Debounce function
        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction() {
                const context = this;
                const args = arguments;
                const later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        },
        
        // Throttle function
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
            };
        },
        
        // Check if element is in viewport
        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        },
        
        // Smooth scroll to element
        scrollTo: function(element, offset = 0) {
            const targetPosition = element.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        },
        
        // Format currency
        formatCurrency: function(amount, currency = 'USD') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },
        
        // Format number with commas
        formatNumber: function(num) {
            return new Intl.NumberFormat().format(num);
        },
        
        // Parse percentage change
        parsePercentage: function(str) {
            const num = parseFloat(str.replace(/[^-0-9.]/g, ''));
            return isNaN(num) ? 0 : num;
        }
    };
    
    // Component Initialization
    RTS.initComponents = function() {
        // Sidebar functionality
        this.initSidebar();
        
        // Navigation enhancements
        this.initNavigation();
        
        // User interactions
        this.initUserInteractions();
        
        // Form enhancements
        this.initForms();
        
        // Back to top button
        this.initBackToTop();
        
        // Loading states
        this.initLoadingStates();
        
        // Animation on scroll
        this.initScrollAnimations();
        
        // Tooltips
        this.initTooltips();
    };
    
    // Sidebar functionality
    RTS.initSidebar = function() {
        const sidebarToggle = document.querySelector('.sidebar-collapse-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (!sidebarToggle || !sidebar) return;
        
        // Get saved state
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('sidebar-collapsed');
        }
        
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            const collapsed = sidebar.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', collapsed);
            
            // Update aria-expanded
            this.setAttribute('aria-expanded', !collapsed);
            
            // Update icon
            const icon = this.querySelector('svg');
            if (icon) {
                icon.style.transform = collapsed ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        });
        
        // Keyboard shortcut (Ctrl+B)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                sidebarToggle.click();
            }
        });
    };
    
    // Navigation enhancements
    RTS.initNavigation = function() {
        // User menu dropdown
        const userMenuToggle = document.querySelector('.user-menu-toggle');
        const userDropdown = document.querySelector('.user-dropdown');
        
        if (userMenuToggle && userDropdown) {
            userMenuToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                this.setAttribute('aria-expanded', !isExpanded);
                userDropdown.classList.toggle('hidden');
            });
            
            // Close on outside click
            document.addEventListener('click', function() {
                userMenuToggle.setAttribute('aria-expanded', 'false');
                userDropdown.classList.add('hidden');
            });
            
            // Keyboard navigation
            userDropdown.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    userMenuToggle.click();
                    userMenuToggle.focus();
                }
            });
        }
        
        // Notifications toggle
        const notificationsToggle = document.querySelector('.notifications-toggle');
        if (notificationsToggle) {
            notificationsToggle.addEventListener('click', function() {
                RTS.showInfo('Notifications panel would open here');
            });
        }
        
        // Active navigation highlighting
        this.highlightActiveNavigation();
    };
    
    RTS.highlightActiveNavigation = function() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .main-menu a');
        
        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath || (linkPath !== '/' && currentPath.includes(linkPath))) {
                link.classList.add('is-active');
                link.setAttribute('aria-current', 'page');
            }
        });
    };
    
    // User interactions
    RTS.initUserInteractions = function() {
        // Button loading states
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn');
            if (btn && btn.classList.contains('btn-loading-on-click')) {
                btn.classList.add('loading');
                btn.disabled = true;
                
                // Remove loading state after 2 seconds (adjust as needed)
                setTimeout(() => {
                    btn.classList.remove('loading');
                    btn.disabled = false;
                }, 2000);
            }
        });
        
        // Confirmation dialogs
        document.addEventListener('click', function(e) {
            const confirmBtn = e.target.closest('[data-confirm]');
            if (confirmBtn) {
                e.preventDefault();
                const message = confirmBtn.dataset.confirm;
                if (confirm(message)) {
                    // Proceed with action
                    if (confirmBtn.href) {
                        window.location.href = confirmBtn.href;
                    } else if (confirmBtn.type === 'submit') {
                        confirmBtn.closest('form').submit();
                    }
                }
            }
        });
    };
    
    // Form enhancements
    RTS.initForms = function() {
        // Floating labels
        const floatingInputs = document.querySelectorAll('.floating-label input, .floating-label textarea');
        floatingInputs.forEach(input => {
            // Check initial state
            if (input.value) {
                input.classList.add('has-value');
            }
            
            input.addEventListener('input', function() {
                if (this.value) {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
        });
        
        // Form validation feedback
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                }
            });
        });
        
        function validateForm(form) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }
            });
            
            return isValid;
        }
        
        function showFieldError(field, message) {
            clearFieldError(field);
            
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.textContent = message;
            
            field.parentNode.appendChild(errorElement);
            field.classList.add('field-invalid');
            field.setAttribute('aria-invalid', 'true');
        }
        
        function clearFieldError(field) {
            const existingError = field.parentNode.querySelector('.field-error');
            if (existingError) {
                existingError.remove();
            }
            field.classList.remove('field-invalid');
            field.removeAttribute('aria-invalid');
        }
    };
    
    // Back to top button
    RTS.initBackToTop = function() {
        const backToTopBtn = document.querySelector('.back-to-top');
        if (!backToTopBtn) return;
        
        const showBackToTop = this.utils.throttle(function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.remove('hidden');
            } else {
                backToTopBtn.classList.add('hidden');
            }
        }, 100);
        
        window.addEventListener('scroll', showBackToTop);
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    };
    
    // Loading states
    RTS.initLoadingStates = function() {
        // Show loading overlay
        this.showLoading = function(message = 'Loading...') {
            let overlay = document.querySelector('.loading-overlay');
            if (!overlay) return;
            
            const messageElement = overlay.querySelector('p');
            if (messageElement) {
                messageElement.textContent = message;
            }
            
            overlay.classList.remove('hidden');
            overlay.setAttribute('aria-hidden', 'false');
        };
        
        // Hide loading overlay
        this.hideLoading = function() {
            const overlay = document.querySelector('.loading-overlay');
            if (overlay) {
                overlay.classList.add('hidden');
                overlay.setAttribute('aria-hidden', 'true');
            }
        };
    };
    
    // Scroll animations
    RTS.initScrollAnimations = function() {
        const animatedElements = document.querySelectorAll('.animate-fade-up, .animate-slide-in, .animate-scale-in');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.animationDelay = '0s';
                        entry.target.style.animationPlayState = 'running';
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px'
            });
            
            animatedElements.forEach(el => {
                el.style.animationPlayState = 'paused';
                observer.observe(el);
            });
        }
    };
    
    // Tooltips
    RTS.initTooltips = function() {
        const tooltipElements = document.querySelectorAll('[title]');
        
        tooltipElements.forEach(element => {
            const title = element.getAttribute('title');
            if (!title) return;
            
            // Create tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = title;
            tooltip.setAttribute('role', 'tooltip');
            
            // Remove title to prevent default tooltip
            element.removeAttribute('title');
            element.setAttribute('data-tooltip', title);
            
            // Show on hover
            element.addEventListener('mouseenter', function() {
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
                
                tooltip.classList.add('tooltip-show');
            });
            
            // Hide on leave
            element.addEventListener('mouseleave', function() {
                tooltip.classList.remove('tooltip-show');
                setTimeout(() => {
                    if (tooltip.parentNode) {
                        tooltip.parentNode.removeChild(tooltip);
                    }
                }, 200);
            });
        });
    };
    
    // Interactivity enhancements
    RTS.initInteractivity = function() {
        // Magnetic buttons
        const magneticButtons = document.querySelectorAll('.btn-magnetic');
        magneticButtons.forEach(button => {
            button.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                this.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translate(0, 0)';
            });
        });
        
        // Ripple effect
        document.addEventListener('click', function(e) {
            const rippleElements = document.querySelectorAll('.btn-ripple, .card-ripple');
            const target = e.target.closest('.btn-ripple, .card-ripple');
            
            if (target) {
                const ripple = document.createElement('span');
                const rect = target.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.className = 'ripple-effect';
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                target.appendChild(ripple);
                
                setTimeout(() => {
                    if (ripple.parentNode) {
                        ripple.parentNode.removeChild(ripple);
                    }
                }, 600);
            }
        });
    };
    
    // Accessibility enhancements
    RTS.initAccessibility = function() {
        // Skip links
        const skipLinks = document.querySelectorAll('.skip-link');
        skipLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        });
        
        // Focus management for modals
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                const modal = document.querySelector('.modal:not(.hidden)');
                if (modal) {
                    trapFocus(modal, e);
                }
            }
        });
        
        function trapFocus(modal, e) {
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
        
        // Announce dynamic content changes
        this.announceToScreenReader = function(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        };
    };
    
    // Performance optimizations
    RTS.initPerformanceOptimizations = function() {
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const lazyImages = document.querySelectorAll('img[data-src]');
            
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        }
        
        // Preload critical resources on hover
        document.addEventListener('mouseover', this.utils.debounce(function(e) {
            const link = e.target.closest('a[href]');
            if (link && link.hostname === window.location.hostname) {
                const href = link.getAttribute('href');
                if (href && !document.querySelector(`link[rel="prefetch"][href="${href}"]`)) {
                    const prefetchLink = document.createElement('link');
                    prefetchLink.rel = 'prefetch';
                    prefetchLink.href = href;
                    document.head.appendChild(prefetchLink);
                }
            }
        }, 100));
    };
    
    // Additional Components
    RTS.components = {
        // Get icon helper for JavaScript
        getIcon: function(iconId, size = 24) {
            return `<svg width="${size}" height="${size}" class="icon"><use href="#${iconId}"></use></svg>`;
        },
        
        // Create notification
        createNotification: function(title, message, type = 'info', actions = []) {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <div class="notification-header">
                        <h4 class="notification-title">${title}</h4>
                        <button class="notification-close btn-icon btn-ghost" aria-label="Close">
                            ${this.getIcon('close', 16)}
                        </button>
                    </div>
                    <div class="notification-body">
                        <p class="notification-message">${message}</p>
                        ${actions.length > 0 ? `
                            <div class="notification-actions">
                                ${actions.map(action => `<button class="btn btn-sm ${action.class || 'btn-ghost'}" onclick="${action.onclick}">${action.text}</button>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            // Add close functionality
            notification.querySelector('.notification-close').addEventListener('click', () => {
                this.removeNotification(notification);
            });
            
            return notification;
        },
        
        // Remove notification
        removeNotification: function(notification) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        },
        
        // Create modal
        createModal: function(title, content, options = {}) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal glass-card" role="dialog" aria-modal="true" aria-labelledby="modal-title">
                    <div class="modal-header">
                        <h2 id="modal-title" class="modal-title">${title}</h2>
                        <button class="modal-close btn-icon btn-ghost" aria-label="Close modal">
                            ${this.getIcon('close', 20)}
                        </button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    ${options.actions ? `
                        <div class="modal-footer">
                            ${options.actions.map(action => `<button class="btn ${action.class || 'btn-secondary'}" onclick="${action.onclick}">${action.text}</button>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
            
            // Add close functionality
            modal.querySelector('.modal-close').addEventListener('click', () => {
                this.closeModal(modal);
            });
            
            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
            
            // Close on Escape
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    this.closeModal(modal);
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
            document.body.appendChild(modal);
            
            // Focus management
            requestAnimationFrame(() => {
                modal.querySelector('.modal-title').focus();
            });
            
            return modal;
        },
        
        // Close modal
        closeModal: function(modal) {
            modal.classList.add('modal-closing');
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        },
        
        // Create progress bar
        createProgressBar: function(progress = 0, options = {}) {
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = `
                <div class="progress-track">
                    <div class="progress-fill ${options.variant || ''}" style="width: ${progress}%"></div>
                </div>
                ${options.showLabel ? `<div class="progress-label">${progress}%</div>` : ''}
            `;
            
            // Update method
            progressBar.updateProgress = function(newProgress) {
                const fill = this.querySelector('.progress-fill');
                const label = this.querySelector('.progress-label');
                fill.style.width = `${newProgress}%`;
                if (label) {
                    label.textContent = `${newProgress}%`;
                }
            };
            
            return progressBar;
        }
    };
    
    // Enhanced search functionality
    RTS.initEnhancedSearch = function() {
        const searchInput = document.querySelector('.search-modal input[type="search"]');
        if (!searchInput) return;
        
        const searchResults = document.createElement('div');
        searchResults.className = 'search-results';
        searchInput.parentNode.appendChild(searchResults);
        
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query, searchResults);
            }, 300);
        });
        
        function performSearch(query, resultsContainer) {
            // Simulate search results
            const mockResults = [
                { type: 'stock', symbol: 'AAPL', name: 'Apple Inc.', price: '$175.43', change: '+1.23%' },
                { type: 'stock', symbol: 'TSLA', name: 'Tesla Inc.', price: '$234.56', change: '-2.45%' },
                { type: 'page', title: 'Portfolio Dashboard', url: '/portfolio/' },
                { type: 'page', title: 'Stock Scanner', url: '/scanner/' }
            ].filter(item => 
                item.symbol?.toLowerCase().includes(query.toLowerCase()) ||
                item.name?.toLowerCase().includes(query.toLowerCase()) ||
                item.title?.toLowerCase().includes(query.toLowerCase())
            );
            
            if (mockResults.length === 0) {
                resultsContainer.innerHTML = '<div class="search-no-results">No results found</div>';
                return;
            }
            
            resultsContainer.innerHTML = mockResults.map(result => {
                if (result.type === 'stock') {
                    return `
                        <div class="search-result-item search-stock">
                            <div class="stock-info">
                                <div class="stock-symbol">${result.symbol}</div>
                                <div class="stock-name">${result.name}</div>
                            </div>
                            <div class="stock-price">
                                <div class="price">${result.price}</div>
                                <div class="change ${result.change.startsWith('+') ? 'positive' : 'negative'}">${result.change}</div>
                            </div>
                        </div>
                    `;
                } else {
                    return `
                        <a href="${result.url}" class="search-result-item search-page">
                            <div class="page-icon">${RTS.components.getIcon('search', 16)}</div>
                            <div class="page-title">${result.title}</div>
                        </a>
                    `;
                }
            }).join('');
        }
    };
    
    // Real-time data simulation
    RTS.initRealtimeData = function() {
        if (!document.querySelector('.dashboard-page')) return;
        
        // Simulate real-time price updates
        setInterval(() => {
            updateRandomPrices();
        }, 5000);
        
        function updateRandomPrices() {
            const priceElements = document.querySelectorAll('.stock-price, .index-value');
            priceElements.forEach(element => {
                if (Math.random() > 0.7) { // 30% chance to update
                    const currentPrice = parseFloat(element.textContent.replace(/[^0-9.]/g, ''));
                    if (currentPrice) {
                        const change = (Math.random() - 0.5) * 10; // Random change
                        const newPrice = Math.max(0, currentPrice + change);
                        element.textContent = `$${newPrice.toFixed(2)}`;
                        
                        // Add flash effect
                        element.classList.add(change > 0 ? 'price-up' : 'price-down');
                        setTimeout(() => {
                            element.classList.remove('price-up', 'price-down');
                        }, 1000);
                    }
                }
            });
        }
    };
    
    // Keyboard shortcuts
    RTS.initKeyboardShortcuts = function() {
        document.addEventListener('keydown', function(e) {
            // Only process shortcuts when not in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            // Ctrl+K for search
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                const searchToggle = document.querySelector('.search-toggle');
                if (searchToggle) searchToggle.click();
            }
            
            // Ctrl+D for dashboard
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                window.location.href = '/dashboard/';
            }
            
            // Ctrl+S for scanner
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                window.location.href = '/scanner/';
            }
            
            // Esc to close modals/dropdowns
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal-overlay, .dropdown.active').forEach(el => {
                    el.classList.remove('active');
                    if (el.classList.contains('modal-overlay')) {
                        RTS.components.closeModal(el);
                    }
                });
            }
        });
    };
    
    // Update initialization
    const originalInit = RTS.init;
    RTS.init = function() {
        originalInit.call(this);
        this.initEnhancedSearch();
        this.initRealtimeData();
        this.initKeyboardShortcuts();
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            RTS.init();
        });
    } else {
        RTS.init();
    }
    
})();