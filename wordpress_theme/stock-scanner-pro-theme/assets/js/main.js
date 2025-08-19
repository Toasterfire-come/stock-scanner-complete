/**
 * Stock Scanner Pro - Main JavaScript
 */

(function($) {
    'use strict';

    // Main application object
    const StockScannerApp = {
        init: function() {
            this.initTheme();
            this.initNavigation();
            this.initSearch();
            this.initScrollEffects();
            this.initTooltips();
            this.initModals();
            this.bindGlobalEvents();
            this.checkConnectivity();
        },

        // Initialize theme functionality
        initTheme: function() {
            const savedTheme = localStorage.getItem('stock-scanner-theme') || 'light';
            this.setTheme(savedTheme);
            
            $(document).on('click', '#theme-toggle', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                this.setTheme(newTheme);
            });
        },

        setTheme: function(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('stock-scanner-theme', theme);
            
            // Update theme toggle icon
            const $darkIcon = $('.dark-icon');
            const $lightIcon = $('.light-icon');
            
            if (theme === 'dark') {
                $darkIcon.removeClass('hidden');
                $lightIcon.addClass('hidden');
            } else {
                $darkIcon.addClass('hidden');
                $lightIcon.removeClass('hidden');
            }
        },

        // Initialize navigation
        initNavigation: function() {
            // Mobile menu toggle
            $(document).on('click', '#mobile-menu-toggle', function() {
                const $button = $(this);
                const $menu = $('#mobile-menu');
                const isExpanded = $button.attr('aria-expanded') === 'true';
                
                $button.attr('aria-expanded', !isExpanded);
                $menu.toggleClass('hidden');
                
                // Toggle icons
                $button.find('.hamburger-icon').toggleClass('hidden');
                $button.find('.close-icon').toggleClass('hidden');
            });

            // User menu dropdown
            $(document).on('click', '#user-menu-toggle', function(e) {
                e.stopPropagation();
                const $dropdown = $('#user-menu-dropdown');
                const isExpanded = $(this).attr('aria-expanded') === 'true';
                
                $(this).attr('aria-expanded', !isExpanded);
                $dropdown.toggleClass('hidden');
            });

            // Close dropdowns when clicking outside
            $(document).on('click', function(e) {
                if (!$(e.target).closest('#user-menu-toggle, #user-menu-dropdown').length) {
                    $('#user-menu-dropdown').addClass('hidden');
                    $('#user-menu-toggle').attr('aria-expanded', 'false');
                }
            });

            // Smooth scrolling for anchor links
            $(document).on('click', 'a[href^="#"]', function(e) {
                const target = $(this.hash);
                if (target.length) {
                    e.preventDefault();
                    $('html, body').animate({
                        scrollTop: target.offset().top - 80
                    }, 500);
                }
            });
        },

        // Initialize search functionality
        initSearch: function() {
            let searchTimeout;
            
            // Search overlay toggle
            $(document).on('click', '#search-toggle', () => {
                $('#search-overlay').removeClass('hidden');
                $('#search-overlay .search-field').focus();
            });

            $(document).on('click', '#search-close, #search-overlay', function(e) {
                if (e.target === this) {
                    $('#search-overlay').addClass('hidden');
                }
            });

            // Escape key closes search
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape') {
                    $('#search-overlay').addClass('hidden');
                }
            });

            // Live search
            $(document).on('input', '.search-field', function() {
                const query = $(this).val().trim();
                const $suggestions = $('.search-suggestions');
                
                clearTimeout(searchTimeout);
                
                if (query.length < 2) {
                    $suggestions.addClass('hidden');
                    return;
                }
                
                searchTimeout = setTimeout(() => {
                    this.performSearch(query);
                }, 300);
            }.bind(this));
        },

        // Perform search and show suggestions
        performSearch: function(query) {
            const $suggestions = $('.search-suggestions');
            
            $suggestions.html('<div class="search-loading">Searching...</div>').removeClass('hidden');
            
            StockScannerAPI.Stock.searchStocks(query, 5)
                .then(data => {
                    if (data.success && data.results && data.results.length > 0) {
                        let html = '<div class="search-results">';
                        
                        data.results.forEach(stock => {
                            html += `
                                <a href="/stock-lookup/?ticker=${stock.ticker}" class="search-result-item">
                                    <div class="search-result-ticker">${stock.ticker}</div>
                                    <div class="search-result-company">${stock.company_name}</div>
                                    <div class="search-result-price">
                                        ${StockScannerAPI.Utils.formatCurrency(stock.current_price)}
                                        <span class="${StockScannerAPI.Utils.getPriceChangeClass(stock.change_percent)}">
                                            ${StockScannerAPI.Utils.formatPercentage(stock.change_percent)}
                                        </span>
                                    </div>
                                </a>
                            `;
                        });
                        
                        html += '</div>';
                        $suggestions.html(html);
                    } else {
                        $suggestions.html('<div class="search-no-results">No stocks found</div>');
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    $suggestions.html('<div class="search-error">Search failed. Please try again.</div>');
                });
        },

        // Initialize scroll effects
        initScrollEffects: function() {
            const $backToTop = $('#back-to-top');
            
            $(window).on('scroll', function() {
                if ($(window).scrollTop() > 300) {
                    $backToTop.removeClass('opacity-0 pointer-events-none');
                } else {
                    $backToTop.addClass('opacity-0 pointer-events-none');
                }
            });

            $(document).on('click', '#back-to-top', function() {
                $('html, body').animate({ scrollTop: 0 }, 500);
            });

            // Market status bar scroll effect
            const $marketStatusBar = $('#market-status-bar');
            if ($marketStatusBar.length) {
                let lastScrollTop = 0;
                
                $(window).on('scroll', function() {
                    const scrollTop = $(this).scrollTop();
                    
                    if (scrollTop > lastScrollTop && scrollTop > 100) {
                        $marketStatusBar.addClass('-translate-y-full');
                    } else {
                        $marketStatusBar.removeClass('-translate-y-full');
                    }
                    
                    lastScrollTop = scrollTop;
                });
            }
        },

        // Initialize tooltips
        initTooltips: function() {
            // Simple tooltip implementation
            $(document).on('mouseenter', '[data-tooltip]', function() {
                const $element = $(this);
                const tooltipText = $element.data('tooltip');
                
                if (!tooltipText) return;
                
                const tooltip = $(`<div class="tooltip">${tooltipText}</div>`);
                $('body').append(tooltip);
                
                const elementOffset = $element.offset();
                const elementHeight = $element.outerHeight();
                const elementWidth = $element.outerWidth();
                const tooltipWidth = tooltip.outerWidth();
                
                tooltip.css({
                    position: 'absolute',
                    top: elementOffset.top - tooltip.outerHeight() - 5,
                    left: elementOffset.left + (elementWidth / 2) - (tooltipWidth / 2),
                    zIndex: 9999
                });
                
                $element.data('tooltip-element', tooltip);
            });

            $(document).on('mouseleave', '[data-tooltip]', function() {
                const tooltip = $(this).data('tooltip-element');
                if (tooltip) {
                    tooltip.remove();
                    $(this).removeData('tooltip-element');
                }
            });
        },

        // Initialize modals
        initModals: function() {
            // Close modal when clicking backdrop
            $(document).on('click', '.modal', function(e) {
                if (e.target === this) {
                    $(this).addClass('hidden');
                }
            });

            // Close modal with close button
            $(document).on('click', '.modal-close', function() {
                $(this).closest('.modal').addClass('hidden');
            });

            // Close modal with escape key
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape') {
                    $('.modal').addClass('hidden');
                }
            });
        },

        // Bind global events
        bindGlobalEvents: function() {
            // Newsletter signup
            $(document).on('submit', '.newsletter-form', function(e) {
                e.preventDefault();
                
                const $form = $(this);
                const email = $form.find('input[name="email"]').val().trim();
                
                if (!email || !this.isValidEmail(email)) {
                    StockScannerAPI.Toast.show('Please enter a valid email address', 'error');
                    return;
                }
                
                const $submitBtn = $form.find('.newsletter-submit');
                const originalText = $submitBtn.text();
                
                $submitBtn.prop('disabled', true).text('Subscribing...');
                
                StockScannerAPI.ajaxRequest('newsletter_signup', { email: email })
                    .then(response => {
                        StockScannerAPI.Toast.show('Successfully subscribed to newsletter!', 'success');
                        $form.find('input[name="email"]').val('');
                    })
                    .catch(error => {
                        console.error('Newsletter signup error:', error);
                        StockScannerAPI.Toast.show('Failed to subscribe. Please try again.', 'error');
                    })
                    .finally(() => {
                        $submitBtn.prop('disabled', false).text(originalText);
                    });
            }.bind(this));

            // Copy to clipboard functionality
            $(document).on('click', '[data-copy]', function() {
                const text = $(this).data('copy') || $(this).text();
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        StockScannerAPI.Toast.show('Copied to clipboard!', 'success');
                    });
                } else {
                    // Fallback for older browsers
                    const textarea = $('<textarea>').val(text).appendTo('body').select();
                    document.execCommand('copy');
                    textarea.remove();
                    StockScannerAPI.Toast.show('Copied to clipboard!', 'success');
                }
            });

            // Print functionality
            $(document).on('click', '[data-print]', function() {
                window.print();
            });

            // External links
            $(document).on('click', 'a[href^="http"]:not([href*="' + location.hostname + '"])', function() {
                $(this).attr('target', '_blank').attr('rel', 'noopener noreferrer');
            });
        },

        // Check API connectivity
        checkConnectivity: function() {
            // Only check on dashboard and other data-heavy pages
            if (!$('body').hasClass('page-template-page-dashboard')) return;
            
            StockScannerAPI.Stock.getMarketOverview()
                .then(() => {
                    this.showConnectivityStatus('connected');
                })
                .catch(() => {
                    this.showConnectivityStatus('disconnected');
                });
        },

        // Show connectivity status
        showConnectivityStatus: function(status) {
            const message = status === 'connected' 
                ? 'Connected to market data' 
                : 'Unable to connect to market data';
            
            const type = status === 'connected' ? 'success' : 'warning';
            
            StockScannerAPI.Toast.show(message, type, 2000);
        },

        // Email validation helper
        isValidEmail: function(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        // Show loading overlay
        showLoading: function(message = 'Loading...') {
            $('#loading-overlay').removeClass('hidden');
            $('#loading-overlay .loading-spinner span').text(message);
        },

        // Hide loading overlay
        hideLoading: function() {
            $('#loading-overlay').addClass('hidden');
        },

        // Format date helper
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        // Format time helper
        formatTime: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    };

    // Initialize app when document is ready
    $(document).ready(function() {
        StockScannerApp.init();
        
        // Update market time display every minute
        setInterval(function() {
            const now = new Date();
            $('#market-time-display').text(now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short'
            }));
        }, 60000);
    });

    // Export to global scope
    window.StockScannerApp = StockScannerApp;

    // Service Worker registration (if available)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('SW registered: ', registration);
                })
                .catch(function(registrationError) {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }

})(jQuery);

// Handle JavaScript errors gracefully
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('JavaScript Error:', { msg, url, lineNo, columnNo, error });
    
    // Only show user-friendly message on critical errors
    if (msg.includes('Cannot read property') || msg.includes('is not defined')) {
        if (window.StockScannerAPI && window.StockScannerAPI.Toast) {
            window.StockScannerAPI.Toast.show('Something went wrong. Please refresh the page.', 'error');
        }
    }
    
    return false;
};