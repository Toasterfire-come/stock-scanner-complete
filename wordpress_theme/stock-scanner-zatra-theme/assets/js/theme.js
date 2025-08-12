/**
 * Stock Scanner Pro - Zatra Edition
 * Main Theme JavaScript
 */

(function($) {
    'use strict';

    // Theme object
    const StockScannerTheme = {
        
        // Initialize theme
        init: function() {
            this.setupEventListeners();
            this.initializeComponents();
            this.setupAjax();
        },

        // Setup event listeners
        setupEventListeners: function() {
            // Mobile menu toggle
            $(document).on('click', '.mobile-menu-toggle', this.toggleMobileMenu);
            
            // Search functionality
            $(document).on('submit', '.stock-search-form', this.handleStockSearch);
            
            // Watchlist actions
            $(document).on('click', '.add-to-watchlist', this.addToWatchlist);
            $(document).on('click', '.remove-from-watchlist', this.removeFromWatchlist);
            
            // Real-time updates
            if (typeof stockScannerTheme !== 'undefined') {
                this.startRealTimeUpdates();
            }
        },

        // Initialize components
        initializeComponents: function() {
            // Initialize charts if Chart.js is available
            if (typeof Chart !== 'undefined') {
                this.initializeCharts();
            }
            
            // Initialize tooltips
            this.initializeTooltips();
            
            // Initialize lazy loading
            this.initializeLazyLoading();
        },

        // Setup AJAX with nonce
        setupAjax: function() {
            if (typeof stockScannerTheme !== 'undefined') {
                $.ajaxSetup({
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader('X-WP-Nonce', stockScannerTheme.nonce);
                    }
                });
            }
        },

        // Toggle mobile menu
        toggleMobileMenu: function(e) {
            e.preventDefault();
            $('.mobile-menu').toggleClass('active');
            $('body').toggleClass('mobile-menu-open');
        },

        // Handle stock search
        handleStockSearch: function(e) {
            e.preventDefault();
            const form = $(this);
            const symbol = form.find('input[name="symbol"]').val();
            
            if (!symbol) return;
            
            StockScannerTheme.searchStock(symbol);
        },

        // Search for stock data
        searchStock: function(symbol) {
            const loadingIndicator = $('.search-loading');
            const resultsContainer = $('.search-results');
            
            loadingIndicator.show();
            resultsContainer.empty();
            
            $.ajax({
                url: stockScannerTheme.ajaxurl,
                type: 'POST',
                data: {
                    action: 'search_stock',
                    symbol: symbol,
                    nonce: stockScannerTheme.nonce
                },
                success: function(response) {
                    loadingIndicator.hide();
                    if (response.success) {
                        StockScannerTheme.displayStockData(response.data);
                    } else {
                        resultsContainer.html('<p class="error">Stock not found or API error.</p>');
                    }
                },
                error: function() {
                    loadingIndicator.hide();
                    resultsContainer.html('<p class="error">Connection error. Please try again.</p>');
                }
            });
        },

        // Display stock data
        displayStockData: function(data) {
            const resultsContainer = $('.search-results');
            const template = `
                <div class="stock-result">
                    <h3>${data.symbol} - ${data.name}</h3>
                    <div class="stock-price">
                        <span class="current-price">$${data.price}</span>
                        <span class="change ${data.change >= 0 ? 'positive' : 'negative'}">
                            ${data.change >= 0 ? '+' : ''}${data.change} (${data.changePercent}%)
                        </span>
                    </div>
                    <div class="stock-actions">
                        <button class="btn btn-primary add-to-watchlist" data-symbol="${data.symbol}">
                            Add to Watchlist
                        </button>
                    </div>
                </div>
            `;
            resultsContainer.html(template);
        },

        // Add to watchlist
        addToWatchlist: function(e) {
            e.preventDefault();
            const button = $(this);
            const symbol = button.data('symbol');
            
            button.prop('disabled', true).text('Adding...');
            
            $.ajax({
                url: stockScannerTheme.ajaxurl,
                type: 'POST',
                data: {
                    action: 'add_to_watchlist',
                    symbol: symbol,
                    nonce: stockScannerTheme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        button.removeClass('add-to-watchlist')
                              .addClass('remove-from-watchlist')
                              .text('Remove from Watchlist');
                        StockScannerTheme.showNotification('Added to watchlist!', 'success');
                    } else {
                        StockScannerTheme.showNotification('Failed to add to watchlist.', 'error');
                    }
                },
                complete: function() {
                    button.prop('disabled', false);
                }
            });
        },

        // Remove from watchlist
        removeFromWatchlist: function(e) {
            e.preventDefault();
            const button = $(this);
            const symbol = button.data('symbol');
            
            button.prop('disabled', true).text('Removing...');
            
            $.ajax({
                url: stockScannerTheme.ajaxurl,
                type: 'POST',
                data: {
                    action: 'remove_from_watchlist',
                    symbol: symbol,
                    nonce: stockScannerTheme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        button.removeClass('remove-from-watchlist')
                              .addClass('add-to-watchlist')
                              .text('Add to Watchlist');
                        StockScannerTheme.showNotification('Removed from watchlist!', 'success');
                    } else {
                        StockScannerTheme.showNotification('Failed to remove from watchlist.', 'error');
                    }
                },
                complete: function() {
                    button.prop('disabled', false);
                }
            });
        },

        // Initialize charts
        initializeCharts: function() {
            $('.stock-chart').each(function() {
                const canvas = this;
                const symbol = $(canvas).data('symbol');
                
                if (symbol) {
                    StockScannerTheme.createStockChart(canvas, symbol);
                }
            });
        },

        // Create stock chart
        createStockChart: function(canvas, symbol) {
            const ctx = canvas.getContext('2d');
            
            // Default chart configuration
            const config = {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: symbol,
                        data: [],
                        borderColor: '#3685fb',
                        backgroundColor: 'rgba(54, 133, 251, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            };
            
            new Chart(ctx, config);
        },

        // Initialize tooltips
        initializeTooltips: function() {
            $('[data-tooltip]').each(function() {
                const element = $(this);
                const tooltip = element.data('tooltip');
                
                element.attr('title', tooltip);
            });
        },

        // Initialize lazy loading
        initializeLazyLoading: function() {
            if ('IntersectionObserver' in window) {
                const imageObserver = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }
                    });
                });

                document.querySelectorAll('img[data-src]').forEach(img => {
                    imageObserver.observe(img);
                });
            }
        },

        // Start real-time updates
        startRealTimeUpdates: function() {
            // Update stock prices every 30 seconds
            setInterval(() => {
                this.updateStockPrices();
            }, 30000);
        },

        // Update stock prices
        updateStockPrices: function() {
            const stockElements = $('.stock-price[data-symbol]');
            
            if (stockElements.length === 0) return;
            
            const symbols = [];
            stockElements.each(function() {
                symbols.push($(this).data('symbol'));
            });
            
            $.ajax({
                url: stockScannerTheme.ajaxurl,
                type: 'POST',
                data: {
                    action: 'get_stock_prices',
                    symbols: symbols.join(','),
                    nonce: stockScannerTheme.nonce
                },
                success: function(response) {
                    if (response.success && response.data) {
                        Object.keys(response.data).forEach(symbol => {
                            const data = response.data[symbol];
                            const element = $(`.stock-price[data-symbol="${symbol}"]`);
                            
                            element.find('.current-price').text(`$${data.price}`);
                            element.find('.change')
                                   .removeClass('positive negative')
                                   .addClass(data.change >= 0 ? 'positive' : 'negative')
                                   .text(`${data.change >= 0 ? '+' : ''}${data.change} (${data.changePercent}%)`);
                        });
                    }
                }
            });
        },

        // Show notification
        showNotification: function(message, type = 'info') {
            const notification = $(`
                <div class="notification notification-${type}">
                    <span>${message}</span>
                    <button class="notification-close">&times;</button>
                </div>
            `);
            
            $('body').append(notification);
            
            setTimeout(() => {
                notification.addClass('show');
            }, 100);
            
            setTimeout(() => {
                notification.removeClass('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
            
            notification.find('.notification-close').on('click', function() {
                notification.removeClass('show');
                setTimeout(() => notification.remove(), 300);
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        StockScannerTheme.init();
    });

    // Expose to global scope
    window.StockScannerTheme = StockScannerTheme;

})(jQuery);