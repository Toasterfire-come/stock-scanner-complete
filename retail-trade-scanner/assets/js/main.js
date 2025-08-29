/**
 * Retail Trade Scanner Main JavaScript
 * 
 * @package RetailTradeScanner
 */

(function($) {
    'use strict';

    // Global app object
    window.RTS = window.RTS || {};

    /**
     * Initialize the application
     */
    RTS.init = function() {
        RTS.setupThemeToggle();
        RTS.setupMobileMenu();
        RTS.setupSearchModal();
        RTS.setupUserDropdown();
        RTS.setupNotifications();
        RTS.setupSidebar();
        RTS.setupScrollToTop();
        RTS.setupAnimations();
        RTS.setupToasts();
        RTS.setupForms();
        RTS.setupTables();
    };

    /**
     * Theme Toggle Functionality
     */
    RTS.setupThemeToggle = function() {
        const toggle = document.querySelector('.theme-toggle');
        const sunIcon = document.querySelector('.theme-toggle-sun');
        const moonIcon = document.querySelector('.theme-toggle-moon');
        
        if (!toggle) return;

        // Check for saved theme preference
        const currentTheme = localStorage.getItem('rts-theme') || 
                            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

        RTS.setTheme(currentTheme);

        toggle.addEventListener('click', function() {
            const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            RTS.setTheme(theme);
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addListener(function(e) {
            if (!localStorage.getItem('rts-theme')) {
                RTS.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    };

    /**
     * Set theme
     */
    RTS.setTheme = function(theme) {
        const sunIcon = document.querySelector('.theme-toggle-sun');
        const moonIcon = document.querySelector('.theme-toggle-moon');

        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('rts-theme', theme);

        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.classList.add('hidden');
                moonIcon.classList.remove('hidden');
            } else {
                sunIcon.classList.remove('hidden');
                moonIcon.classList.add('hidden');
            }
        }

        // Trigger custom event
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    };

    /**
     * Mobile Menu Functionality
     */
    RTS.setupMobileMenu = function() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const nav = document.querySelector('.main-navigation');
        
        if (!toggle || !nav) return;

        toggle.addEventListener('click', function() {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !expanded);
            nav.classList.toggle('mobile-active');
            toggle.querySelector('.hamburger').classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && nav.classList.contains('mobile-active')) {
                toggle.click();
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (nav.classList.contains('mobile-active') && 
                !nav.contains(e.target) && 
                !toggle.contains(e.target)) {
                toggle.click();
            }
        });
    };

    /**
     * Search Modal Functionality
     */
    RTS.setupSearchModal = function() {
        const searchToggle = document.querySelector('.search-toggle');
        const searchModal = document.querySelector('.search-modal');
        const searchClose = document.querySelector('.search-modal-close');
        const searchBackdrop = document.querySelector('.search-modal-backdrop');
        
        if (!searchToggle || !searchModal) return;

        function openSearch() {
            searchModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            const searchField = searchModal.querySelector('input[type="search"]');
            if (searchField) {
                setTimeout(() => searchField.focus(), 100);
            }
        }

        function closeSearch() {
            searchModal.classList.add('hidden');
            document.body.style.overflow = '';
        }

        searchToggle.addEventListener('click', openSearch);
        if (searchClose) searchClose.addEventListener('click', closeSearch);
        if (searchBackdrop) searchBackdrop.addEventListener('click', closeSearch);

        // Close on Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !searchModal.classList.contains('hidden')) {
                closeSearch();
            }
        });

        // Search functionality
        const searchField = searchModal ? searchModal.querySelector('input[type="search"]') : null;
        let searchTimeout;

        if (searchField) {
            searchField.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        RTS.performSearch(query);
                    }, 300);
                }
            });
        }
    };

    /**
     * Perform search with debouncing
     */
    RTS.performSearch = function(query) {
        // Implement search functionality
        console.log('Searching for:', query);
        
        // This would typically make an AJAX request to search endpoint
        if (typeof rtsAjax !== 'undefined') {
            $.ajax({
                url: rtsAjax.ajaxurl,
                type: 'POST',
                data: {
                    action: 'rts_search',
                    query: query,
                    nonce: rtsAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        RTS.displaySearchResults(response.data);
                    }
                }
            });
        }
    };

    /**
     * Display search results
     */
    RTS.displaySearchResults = function(results) {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;

        // Clear previous results
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = '<p class="no-results">No results found</p>';
            return;
        }

        // Display results
        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.className = 'search-result-item';
            resultElement.innerHTML = `
                <a href="${result.url}" class="search-result-link">
                    <h4>${result.title}</h4>
                    <p>${result.excerpt}</p>
                </a>
            `;
            resultsContainer.appendChild(resultElement);
        });
    };

    /**
     * User Dropdown Functionality
     */
    RTS.setupUserDropdown = function() {
        const toggle = document.querySelector('.user-menu-toggle');
        const dropdown = document.querySelector('.user-dropdown');
        
        if (!toggle || !dropdown) return;

        toggle.addEventListener('click', function() {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !expanded);
            dropdown.classList.toggle('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
                toggle.setAttribute('aria-expanded', 'false');
                dropdown.classList.add('hidden');
            }
        });
    };

    /**
     * Notifications Functionality
     */
    RTS.setupNotifications = function() {
        const toggle = document.querySelector('.notifications-toggle');
        
        if (!toggle) return;

        toggle.addEventListener('click', function() {
            // Implement notifications dropdown
            RTS.showToast('Notifications feature coming soon!', 'info');
        });
    };

    /**
     * Sidebar Functionality
     */
    RTS.setupSidebar = function() {
        const sidebar = document.querySelector('.sidebar');
        const collapseToggle = document.querySelector('.sidebar-collapse-toggle');
        
        if (!sidebar || !collapseToggle) return;

        // Load saved sidebar state
        const isCollapsed = localStorage.getItem('rts-sidebar-collapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
        }

        collapseToggle.addEventListener('click', function() {
            const collapsed = sidebar.classList.toggle('collapsed');
            localStorage.setItem('rts-sidebar-collapsed', collapsed);
            
            // Update aria-label
            const newLabel = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
            collapseToggle.setAttribute('aria-label', newLabel);
        });
    };

    /**
     * Scroll to Top Functionality
     */
    RTS.setupScrollToTop = function() {
        const backToTop = document.querySelector('.back-to-top');
        
        if (!backToTop) return;

        function toggleBackToTop() {
            if (window.scrollY > 300) {
                backToTop.classList.remove('hidden');
            } else {
                backToTop.classList.add('hidden');
            }
        }

        window.addEventListener('scroll', RTS.throttle(toggleBackToTop, 100));

        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    };

    /**
     * Animation Observer
     */
    RTS.setupAnimations = function() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('[class*="animate-"]').forEach(el => {
                observer.observe(el);
            });
        }
    };

    /**
     * Toast Notifications
     */
    RTS.setupToasts = function() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            const container = document.createElement('div');
            container.className = 'toast-container';
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-atomic', 'true');
            document.body.appendChild(container);
        }
    };

    /**
     * Show toast notification
     */
    RTS.showToast = function(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-scale-in`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" aria-label="Close notification">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        `;

        container.appendChild(toast);

        // Close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => RTS.hideToast(toast));

        // Auto-hide after duration
        setTimeout(() => RTS.hideToast(toast), duration);

        return toast;
    };

    /**
     * Hide toast notification
     */
    RTS.hideToast = function(toast) {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    };

    /**
     * Form Enhancements
     */
    RTS.setupForms = function() {
        // Floating label functionality
        document.querySelectorAll('.floating-label input, .floating-label textarea').forEach(input => {
            const label = input.nextElementSibling;
            if (!label) return;

            function updateLabel() {
                if (input.value || input === document.activeElement) {
                    label.classList.add('floating');
                } else {
                    label.classList.remove('floating');
                }
            }

            input.addEventListener('focus', updateLabel);
            input.addEventListener('blur', updateLabel);
            input.addEventListener('input', updateLabel);
            
            // Initial state
            updateLabel();
        });

        // Form validation
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!RTS.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    };

    /**
     * Form validation
     */
    RTS.validateForm = function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                RTS.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                RTS.hideFieldError(field);
            }
        });

        return isValid;
    };

    /**
     * Show field error
     */
    RTS.showFieldError = function(field, message) {
        const errorEl = field.parentNode.querySelector('.field-error') || 
                       document.createElement('div');
        
        errorEl.className = 'field-error text-danger text-sm';
        errorEl.textContent = message;
        
        if (!field.parentNode.querySelector('.field-error')) {
            field.parentNode.appendChild(errorEl);
        }
        
        field.classList.add('has-error');
    };

    /**
     * Hide field error
     */
    RTS.hideFieldError = function(field) {
        const errorEl = field.parentNode.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
        field.classList.remove('has-error');
    };

    /**
     * Table Enhancements
     */
    RTS.setupTables = function() {
        document.querySelectorAll('table.sortable').forEach(table => {
            RTS.makeSortable(table);
        });

        document.querySelectorAll('table.responsive').forEach(table => {
            RTS.makeResponsive(table);
        });
    };

    /**
     * Make table sortable
     */
    RTS.makeSortable = function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                const currentOrder = header.dataset.order || 'asc';
                const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                
                RTS.sortTable(table, column, newOrder);
                
                // Update header state
                headers.forEach(h => h.removeAttribute('data-order'));
                header.dataset.order = newOrder;
            });
        });
    };

    /**
     * Sort table
     */
    RTS.sortTable = function(table, column, order) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.querySelector(`[data-sort="${column}"]`)?.textContent || '';
            const bVal = b.querySelector(`[data-sort="${column}"]`)?.textContent || '';
            
            if (order === 'asc') {
                return aVal.localeCompare(bVal, undefined, { numeric: true });
            } else {
                return bVal.localeCompare(aVal, undefined, { numeric: true });
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    };

    /**
     * Utility Functions
     */
    
    RTS.throttle = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    RTS.debounce = function(func, wait, immediate) {
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
    };

    /**
     * Initialize when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', RTS.init);
    } else {
        RTS.init();
    }

})(jQuery);