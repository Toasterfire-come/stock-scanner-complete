/**
 * Stock Scanner Pro - Main JavaScript (Vanilla JS)
 */

// Main application object
class StockScannerApp {
    constructor() {
        this.init();
    }

    init() {
        this.initTheme();
        this.initNavigation();
        this.initSearch();
        this.initScrollEffects();
        this.initTooltips();
        this.initModals();
        this.bindGlobalEvents();
        this.checkConnectivity();
    }

    // Initialize theme functionality
    initTheme() {
        const savedTheme = localStorage.getItem('stock-scanner-theme') || 'light';
        this.setTheme(savedTheme);
        
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                this.setTheme(newTheme);
            });
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('stock-scanner-theme', theme);
        
        // Update theme toggle icon
        const darkIcon = document.querySelector('.dark-icon');
        const lightIcon = document.querySelector('.light-icon');
        
        if (darkIcon && lightIcon) {
            if (theme === 'dark') {
                darkIcon.classList.remove('hidden');
                lightIcon.classList.add('hidden');
            } else {
                darkIcon.classList.add('hidden');
                lightIcon.classList.remove('hidden');
            }
        }
    }

    // Initialize navigation
    initNavigation() {
        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuToggle && mobileMenu) {
            mobileMenuToggle.addEventListener('click', () => {
                const isExpanded = mobileMenuToggle.getAttribute('aria-expanded') === 'true';
                
                mobileMenuToggle.setAttribute('aria-expanded', !isExpanded);
                mobileMenu.classList.toggle('hidden');
                
                // Toggle icons
                const hamburgerIcon = mobileMenuToggle.querySelector('.hamburger-icon');
                const closeIcon = mobileMenuToggle.querySelector('.close-icon');
                if (hamburgerIcon && closeIcon) {
                    hamburgerIcon.classList.toggle('hidden');
                    closeIcon.classList.toggle('hidden');
                }
            });
        }

        // User menu dropdown
        const userMenuToggle = document.getElementById('user-menu-toggle');
        const userMenuDropdown = document.getElementById('user-menu-dropdown');
        
        if (userMenuToggle && userMenuDropdown) {
            userMenuToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isExpanded = userMenuToggle.getAttribute('aria-expanded') === 'true';
                
                userMenuToggle.setAttribute('aria-expanded', !isExpanded);
                userMenuDropdown.classList.toggle('hidden');
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (userMenuToggle && userMenuDropdown && 
                !userMenuToggle.contains(e.target) && 
                !userMenuDropdown.contains(e.target)) {
                userMenuDropdown.classList.add('hidden');
                userMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Smooth scrolling for anchor links
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                const targetId = e.target.getAttribute('href');
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    const headerHeight = 80;
                    const targetPosition = target.offsetTop - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    }

    // Initialize search functionality
    initSearch() {
        let searchTimeout;
        
        // Search overlay toggle
        const searchToggle = document.getElementById('search-toggle');
        const searchOverlay = document.getElementById('search-overlay');
        const searchClose = document.getElementById('search-close');
        const searchField = searchOverlay?.querySelector('.search-field');
        
        if (searchToggle && searchOverlay) {
            searchToggle.addEventListener('click', () => {
                searchOverlay.classList.remove('hidden');
                if (searchField) searchField.focus();
            });
        }

        if (searchClose && searchOverlay) {
            searchClose.addEventListener('click', () => {
                searchOverlay.classList.add('hidden');
            });
        }

        if (searchOverlay) {
            searchOverlay.addEventListener('click', (e) => {
                if (e.target === searchOverlay) {
                    searchOverlay.classList.add('hidden');
                }
            });
        }

        // Escape key closes search
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchOverlay) {
                searchOverlay.classList.add('hidden');
            }
        });

        // Live search
        if (searchField) {
            searchField.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                const suggestions = document.querySelector('.search-suggestions');
                
                clearTimeout(searchTimeout);
                
                if (query.length < 2) {
                    if (suggestions) suggestions.classList.add('hidden');
                    return;
                }
                
                searchTimeout = setTimeout(() => {
                    this.performSearch(query);
                }, 300);
            });
        }
    }

    // Perform search and show suggestions
    async performSearch(query) {
        const suggestions = document.querySelector('.search-suggestions');
        if (!suggestions) return;
        
        suggestions.innerHTML = '<div class="search-loading">Searching...</div>';
        suggestions.classList.remove('hidden');
        
        try {
            const data = await stockAPI.searchStocks(query, 5);
            
            if (data.success && data.results && data.results.length > 0) {
                let html = '<div class="search-results">';
                
                data.results.forEach(stock => {
                    html += `
                        <a href="/stock-lookup/?ticker=${stock.ticker}" class="search-result-item">
                            <div class="search-result-ticker">${stock.ticker}</div>
                            <div class="search-result-company">${stock.company_name}</div>
                            <div class="search-result-price">
                                ${Utils.formatCurrency(stock.current_price)}
                                <span class="${Utils.getPriceChangeClass(stock.change_percent)}">
                                    ${Utils.formatPercentage(stock.change_percent)}
                                </span>
                            </div>
                        </a>
                    `;
                });
                
                html += '</div>';
                suggestions.innerHTML = html;
            } else {
                suggestions.innerHTML = '<div class="search-no-results">No stocks found</div>';
            }
        } catch (error) {
            console.error('Search error:', error);
            suggestions.innerHTML = '<div class="search-error">Search failed. Please try again.</div>';
        }
    }

    // Initialize scroll effects
    initScrollEffects() {
        const backToTop = document.getElementById('back-to-top');
        
        window.addEventListener('scroll', () => {
            if (backToTop) {
                if (window.scrollY > 300) {
                    backToTop.classList.remove('opacity-0', 'pointer-events-none');
                } else {
                    backToTop.classList.add('opacity-0', 'pointer-events-none');
                }
            }
        });

        if (backToTop) {
            backToTop.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }

        // Market status bar scroll effect
        const marketStatusBar = document.getElementById('market-status-bar');
        if (marketStatusBar) {
            let lastScrollTop = 0;
            
            window.addEventListener('scroll', () => {
                const scrollTop = window.scrollY;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    marketStatusBar.classList.add('-translate-y-full');
                } else {
                    marketStatusBar.classList.remove('-translate-y-full');
                }
                
                lastScrollTop = scrollTop;
            });
        }
    }

    // Initialize tooltips
    initTooltips() {
        let currentTooltip = null;

        // Show tooltip on hover
        document.addEventListener('mouseenter', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                const tooltipText = e.target.getAttribute('data-tooltip');
                if (!tooltipText) return;
                
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip fixed z-50 bg-gray-800 text-white text-sm px-2 py-1 rounded shadow-lg pointer-events-none';
                tooltip.textContent = tooltipText;
                document.body.appendChild(tooltip);
                
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
                
                currentTooltip = tooltip;
            }
        }, true);

        // Hide tooltip
        document.addEventListener('mouseleave', (e) => {
            if (e.target.hasAttribute('data-tooltip') && currentTooltip) {
                currentTooltip.remove();
                currentTooltip = null;
            }
        }, true);
    }

    // Initialize modals
    initModals() {
        // Close modal when clicking backdrop
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.add('hidden');
            }
        });

        // Close modal with close button
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close')) {
                const modal = e.target.closest('.modal');
                if (modal) modal.classList.add('hidden');
            }
        });

        // Close modal with escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal:not(.hidden)');
                modals.forEach(modal => modal.classList.add('hidden'));
            }
        });
    }

    // Bind global events
    bindGlobalEvents() {
        // Newsletter signup
        document.addEventListener('submit', async (e) => {
            if (e.target.classList.contains('newsletter-form')) {
                e.preventDefault();
                
                const form = e.target;
                const emailInput = form.querySelector('input[name="email"]');
                const email = emailInput?.value.trim();
                
                if (!email || !this.isValidEmail(email)) {
                    Toast.show('Please enter a valid email address', 'error');
                    return;
                }
                
                const submitBtn = form.querySelector('.newsletter-submit');
                const originalText = submitBtn?.textContent;
                
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Subscribing...';
                }
                
                try {
                    const api = new StockScannerAPI();
                    await api.ajaxRequest('newsletter_signup', { email: email });
                    Toast.show('Successfully subscribed to newsletter!', 'success');
                    emailInput.value = '';
                } catch (error) {
                    console.error('Newsletter signup error:', error);
                    Toast.show('Failed to subscribe. Please try again.', 'error');
                } finally {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                    }
                }
            }
        });

        // Copy to clipboard functionality
        document.addEventListener('click', async (e) => {
            if (e.target.hasAttribute('data-copy')) {
                const text = e.target.getAttribute('data-copy') || e.target.textContent;
                
                try {
                    if (navigator.clipboard) {
                        await navigator.clipboard.writeText(text);
                    } else {
                        // Fallback for older browsers
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand('copy');
                        textarea.remove();
                    }
                    Toast.show('Copied to clipboard!', 'success');
                } catch (err) {
                    console.error('Failed to copy text: ', err);
                }
            }
        });

        // Print functionality
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-print')) {
                window.print();
            }
        });

        // External links
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && 
                e.target.href.startsWith('http') && 
                !e.target.href.includes(location.hostname)) {
                e.target.target = '_blank';
                e.target.rel = 'noopener noreferrer';
            }
        });
    }

    // Check API connectivity
    async checkConnectivity() {
        // Only check on dashboard and other data-heavy pages
        if (!document.body.classList.contains('page-template-page-dashboard')) return;
        
        try {
            await stockAPI.getMarketOverview();
            this.showConnectivityStatus('connected');
        } catch (error) {
            this.showConnectivityStatus('disconnected');
        }
    }

    // Show connectivity status
    showConnectivityStatus(status) {
        const message = status === 'connected' 
            ? 'Connected to market data' 
            : 'Unable to connect to market data';
        
        const type = status === 'connected' ? 'success' : 'warning';
        
        Toast.show(message, type, 2000);
    }

    // Email validation helper
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Show loading overlay
    showLoading(message = 'Loading...') {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
            const loadingText = loadingOverlay.querySelector('.loading-spinner span');
            if (loadingText) loadingText.textContent = message;
        }
    }

    // Hide loading overlay
    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
        }
    }

    // Format date helper
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // Format time helper
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize app when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.stockScannerApp = new StockScannerApp();
    
    // Update market time display every minute
    setInterval(function() {
        const marketTimeDisplay = document.getElementById('market-time-display');
        if (marketTimeDisplay) {
            const now = new Date();
            marketTimeDisplay.textContent = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short'
            });
        }
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

// Handle JavaScript errors gracefully
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', {
        message: event.message,
        source: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
    
    // Only show user-friendly message on critical errors
    if (event.message.includes('Cannot read property') || event.message.includes('is not defined')) {
        if (window.StockScannerAPI && window.StockScannerAPI.Toast) {
            window.StockScannerAPI.Toast.show('Something went wrong. Please refresh the page.', 'error');
        }
    }
});