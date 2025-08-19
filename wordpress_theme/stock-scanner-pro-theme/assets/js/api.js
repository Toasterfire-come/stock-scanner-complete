/**
 * Stock Scanner Pro - API Integration
 */

(function($) {
    'use strict';

    // API Configuration
    const API = {
        baseUrl: stockScannerConfig.apiUrl,
        nonce: stockScannerConfig.nonce,
        ajaxUrl: stockScannerConfig.ajaxUrl,
        
        // Request wrapper with error handling
        request: function(endpoint, options = {}) {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': this.nonce
                }
            };

            const config = { ...defaultOptions, ...options };
            const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;

            return fetch(url, config)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP Error: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API Request Error:', error);
                    throw error;
                });
        },

        // WordPress AJAX wrapper
        ajaxRequest: function(action, data = {}) {
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: this.ajaxUrl,
                    type: 'POST',
                    data: {
                        action: action,
                        nonce: this.nonce,
                        ...data
                    },
                    success: function(response) {
                        if (response.success) {
                            resolve(response.data);
                        } else {
                            reject(new Error(response.data || 'Unknown error'));
                        }
                    },
                    error: function(xhr, status, error) {
                        reject(new Error(error || 'AJAX request failed'));
                    }
                });
            });
        }
    };

    // Stock Data API
    const StockAPI = {
        // Get stock data by ticker
        getStock: function(ticker) {
            return API.request(`stock/${ticker.toUpperCase()}/`);
        },

        // Search stocks
        searchStocks: function(query, limit = 20) {
            return API.request(`search/?q=${encodeURIComponent(query)}&limit=${limit}`);
        },

        // Get stock list with filters
        getStocks: function(filters = {}) {
            const params = new URLSearchParams(filters).toString();
            return API.request(`stocks/${params ? '?' + params : ''}`);
        },

        // Get trending stocks
        getTrending: function(limit = 20) {
            return API.request(`trending/?limit=${limit}`);
        },

        // Get market overview
        getMarketOverview: function() {
            return API.request('market-stats/');
        },

        // Get realtime data for multiple tickers
        getRealTimeData: function(tickers) {
            const tickerList = Array.isArray(tickers) ? tickers.join(',') : tickers;
            return API.ajaxRequest('stock_scanner_realtime_data', { tickers: tickerList });
        }
    };

    // Portfolio API
    const PortfolioAPI = {
        // Get user portfolio
        getPortfolio: function() {
            return API.request('portfolio/');
        },

        // Add stock to portfolio
        addToPortfolio: function(ticker, shares, price) {
            return API.request('portfolio/', {
                method: 'POST',
                body: JSON.stringify({
                    ticker: ticker.toUpperCase(),
                    shares: parseFloat(shares),
                    price: parseFloat(price)
                })
            });
        },

        // Update portfolio holding
        updateHolding: function(holdingId, data) {
            return API.request(`portfolio/holdings/${holdingId}/`, {
                method: 'PATCH',
                body: JSON.stringify(data)
            });
        },

        // Remove from portfolio
        removeFromPortfolio: function(holdingId) {
            return API.request(`portfolio/holdings/${holdingId}/`, {
                method: 'DELETE'
            });
        }
    };

    // Watchlist API
    const WatchlistAPI = {
        // Get user watchlist
        getWatchlist: function() {
            return API.request('watchlist/');
        },

        // Add to watchlist
        addToWatchlist: function(ticker, notes = '') {
            return API.request('watchlist/', {
                method: 'POST',
                body: JSON.stringify({
                    ticker: ticker.toUpperCase(),
                    notes: notes
                })
            });
        },

        // Update watchlist item
        updateWatchlistItem: function(itemId, data) {
            return API.request(`watchlist/${itemId}/`, {
                method: 'PATCH',
                body: JSON.stringify(data)
            });
        },

        // Remove from watchlist
        removeFromWatchlist: function(itemId) {
            return API.request(`watchlist/${itemId}/`, {
                method: 'DELETE'
            });
        }
    };

    // News API
    const NewsAPI = {
        // Get general news
        getNews: function(limit = 20) {
            return API.request(`news/?limit=${limit}`);
        },

        // Get news for specific ticker
        getStockNews: function(ticker, limit = 10) {
            return API.request(`news/?ticker=${ticker.toUpperCase()}&limit=${limit}`);
        },

        // Get personalized news
        getPersonalizedNews: function(limit = 20) {
            return API.request(`news/personalized/?limit=${limit}`);
        }
    };

    // Alerts API
    const AlertsAPI = {
        // Create price alert
        createAlert: function(ticker, targetPrice, condition, email) {
            return API.request('alerts/create/', {
                method: 'POST',
                body: JSON.stringify({
                    ticker: ticker.toUpperCase(),
                    target_price: parseFloat(targetPrice),
                    condition: condition,
                    email: email
                })
            });
        },

        // Get user alerts
        getAlerts: function() {
            return API.request('alerts/');
        },

        // Update alert
        updateAlert: function(alertId, data) {
            return API.request(`alerts/${alertId}/`, {
                method: 'PATCH',
                body: JSON.stringify(data)
            });
        },

        // Delete alert
        deleteAlert: function(alertId) {
            return API.request(`alerts/${alertId}/`, {
                method: 'DELETE'
            });
        }
    };

    // Utility functions
    const Utils = {
        // Format currency
        formatCurrency: function(value, decimals = 2) {
            if (value === null || value === undefined || isNaN(value)) {
                return '$0.00';
            }
            return `$${parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        },

        // Format percentage
        formatPercentage: function(value, decimals = 2, showSign = true) {
            if (value === null || value === undefined || isNaN(value)) {
                return '0.00%';
            }
            const formatted = parseFloat(value).toFixed(decimals) + '%';
            return showSign && value > 0 ? '+' + formatted : formatted;
        },

        // Format large numbers
        formatNumber: function(value) {
            if (value === null || value === undefined || isNaN(value)) {
                return '0';
            }
            
            const num = parseInt(value);
            if (num >= 1000000000) {
                return (num / 1000000000).toFixed(1) + 'B';
            } else if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toLocaleString();
        },

        // Get price change class
        getPriceChangeClass: function(change) {
            if (change > 0) return 'price-positive text-success';
            if (change < 0) return 'price-negative text-danger';
            return 'price-neutral text-muted';
        },

        // Validate ticker symbol
        validateTicker: function(ticker) {
            if (!ticker) return false;
            const cleaned = ticker.trim().toUpperCase();
            return /^[A-Z]{1,5}$/.test(cleaned) ? cleaned : false;
        },

        // Show loading state
        showLoading: function(element, message = 'Loading...') {
            const $element = $(element);
            $element.addClass('loading');
            
            if (!$element.find('.loading-overlay').length) {
                $element.append(`
                    <div class="loading-overlay">
                        <div class="loading-spinner">
                            <div class="spinner"></div>
                            <span>${message}</span>
                        </div>
                    </div>
                `);
            }
        },

        // Hide loading state
        hideLoading: function(element) {
            const $element = $(element);
            $element.removeClass('loading');
            $element.find('.loading-overlay').remove();
        },

        // Show error message
        showError: function(element, message) {
            const $element = $(element);
            $element.html(`
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">${message}</div>
                    <button class="error-retry btn btn-sm btn-primary">Try Again</button>
                </div>
            `);
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // Real-time data manager
    const RealTimeManager = {
        intervals: new Map(),
        
        // Start real-time updates for tickers
        startUpdates: function(tickers, callback, interval = 30000) {
            const key = Array.isArray(tickers) ? tickers.join(',') : tickers;
            
            // Clear existing interval if any
            this.stopUpdates(key);
            
            // Initial fetch
            this.fetchData(tickers, callback);
            
            // Set up interval
            const intervalId = setInterval(() => {
                this.fetchData(tickers, callback);
            }, interval);
            
            this.intervals.set(key, intervalId);
        },
        
        // Stop real-time updates
        stopUpdates: function(tickers) {
            const key = Array.isArray(tickers) ? tickers.join(',') : tickers;
            
            if (this.intervals.has(key)) {
                clearInterval(this.intervals.get(key));
                this.intervals.delete(key);
            }
        },
        
        // Fetch data for tickers
        fetchData: function(tickers, callback) {
            StockAPI.getRealTimeData(tickers)
                .then(data => {
                    if (callback && typeof callback === 'function') {
                        callback(data);
                    }
                })
                .catch(error => {
                    console.error('Real-time data fetch error:', error);
                });
        },
        
        // Stop all updates
        stopAll: function() {
            this.intervals.forEach((intervalId) => {
                clearInterval(intervalId);
            });
            this.intervals.clear();
        }
    };

    // Toast notification system
    const Toast = {
        show: function(message, type = 'info', duration = 5000) {
            const toastId = 'toast-' + Date.now();
            const toastHtml = `
                <div id="${toastId}" class="toast toast-${type} opacity-0 transform translate-x-full">
                    <div class="toast-content">
                        <span class="toast-message">${message}</span>
                        <button class="toast-close" onclick="Toast.hide('${toastId}')">&times;</button>
                    </div>
                </div>
            `;
            
            $('#toast-container').append(toastHtml);
            
            // Animate in
            setTimeout(() => {
                $(`#${toastId}`).removeClass('opacity-0 translate-x-full');
            }, 100);
            
            // Auto hide
            setTimeout(() => {
                this.hide(toastId);
            }, duration);
        },
        
        hide: function(toastId) {
            const $toast = $(`#${toastId}`);
            $toast.addClass('opacity-0 translate-x-full');
            
            setTimeout(() => {
                $toast.remove();
            }, 300);
        }
    };

    // Export APIs to global scope
    window.StockScannerAPI = {
        Stock: StockAPI,
        Portfolio: PortfolioAPI,
        Watchlist: WatchlistAPI,
        News: NewsAPI,
        Alerts: AlertsAPI,
        Utils: Utils,
        RealTime: RealTimeManager,
        Toast: Toast
    };

    // Initialize on document ready
    $(document).ready(function() {
        // Auto-start real-time updates if tickers are found on page
        const $stockElements = $('[data-ticker]');
        if ($stockElements.length > 0) {
            const tickers = [];
            $stockElements.each(function() {
                const ticker = $(this).data('ticker');
                if (ticker && tickers.indexOf(ticker) === -1) {
                    tickers.push(ticker);
                }
            });
            
            if (tickers.length > 0) {
                RealTimeManager.startUpdates(tickers, function(data) {
                    // Update elements with real-time data
                    $stockElements.each(function() {
                        const $element = $(this);
                        const ticker = $element.data('ticker');
                        
                        if (data[ticker]) {
                            const stockData = data[ticker];
                            
                            // Update price
                            $element.find('.stock-price').text(Utils.formatCurrency(stockData.current_price));
                            
                            // Update change
                            const change = stockData.price_change_today || 0;
                            const changePercent = stockData.change_percent || 0;
                            const $changeElement = $element.find('.stock-change');
                            
                            $changeElement
                                .text(`${Utils.formatCurrency(change)} (${Utils.formatPercentage(changePercent)})`)
                                .removeClass('price-positive price-negative price-neutral')
                                .addClass(Utils.getPriceChangeClass(change));
                        }
                    });
                });
            }
        }
    });

    // Clean up on page unload
    $(window).on('beforeunload', function() {
        RealTimeManager.stopAll();
    });

})(jQuery);