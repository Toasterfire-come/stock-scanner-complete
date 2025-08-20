/**
 * Stock Scanner Pro - API Integration (Vanilla JS)
 */

class StockScannerAPI {
    constructor() {
        this.config = window.stockScannerConfig || {};
        this.baseUrl = this.config.apiUrl || '';
        this.nonce = this.config.nonce || '';
        this.ajaxUrl = this.config.ajaxUrl || '';
    }

    // Request wrapper with error handling
    async request(endpoint, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-WP-Nonce': this.nonce
            }
        };

        const config = { ...defaultOptions, ...options };
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // WordPress AJAX wrapper
    async ajaxRequest(action, data = {}) {
        const formData = new FormData();
        formData.append('action', action);
        formData.append('nonce', this.nonce);
        
        Object.keys(data).forEach(key => {
            formData.append(key, data[key]);
        });

        try {
            const response = await fetch(this.ajaxUrl, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                return result.data;
            } else {
                throw new Error(result.data || 'Unknown error');
            }
        } catch (error) {
            throw new Error(error.message || 'AJAX request failed');
        }
    }
}

// Stock Data API
class StockAPI extends StockScannerAPI {
    // Get stock data by ticker
    async getStock(ticker) {
        return await this.request(`stock/${ticker.toUpperCase()}/`);
    }

    // Search stocks
    async searchStocks(query, limit = 20) {
        return await this.request(`search/?q=${encodeURIComponent(query)}&limit=${limit}`);
    }

    // Get stock list with filters
    async getStocks(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return await this.request(`stocks/${params ? '?' + params : ''}`);
    }

    // Get trending stocks
    async getTrending(limit = 20) {
        return await this.request(`trending/?limit=${limit}`);
    }

    // Get market overview
    async getMarketOverview() {
        return await this.request('market-stats/');
    }

    // Get realtime data for multiple tickers
    async getRealTimeData(tickers) {
        const tickerList = Array.isArray(tickers) ? tickers.join(',') : tickers;
        return await this.ajaxRequest('stock_scanner_realtime_data', { tickers: tickerList });
    }
}

// Portfolio API
class PortfolioAPI extends StockScannerAPI {
    // Get user portfolio
    async getPortfolio() {
        return await this.ajaxRequest('stock_scanner_get_portfolio');
    }

    // Add stock to portfolio
    async addToPortfolio(ticker, shares, costBasis, purchaseDate = null) {
        return await this.ajaxRequest('stock_scanner_add_to_portfolio', {
            ticker: ticker.toUpperCase(),
            shares: parseFloat(shares),
            cost_basis: parseFloat(costBasis),
            purchase_date: purchaseDate
        });
    }

    // Remove from portfolio
    async removeFromPortfolio(holdingId) {
        return await this.ajaxRequest('stock_scanner_remove_from_portfolio', {
            holding_id: parseInt(holdingId)
        });
    }
    
    // Update portfolio holding (placeholder for future implementation)
    async updateHolding(holdingId, data) {
        return await this.request(`portfolio/holdings/${holdingId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
}

// Watchlist API
class WatchlistAPI extends StockScannerAPI {
    // Get user watchlist
    async getWatchlist() {
        return await this.request('watchlist/');
    }

    // Add to watchlist
    async addToWatchlist(ticker, notes = '') {
        return await this.request('watchlist/', {
            method: 'POST',
            body: JSON.stringify({
                ticker: ticker.toUpperCase(),
                notes: notes
            })
        });
    }

    // Update watchlist item
    async updateWatchlistItem(itemId, data) {
        return await this.request(`watchlist/${itemId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    // Remove from watchlist
    async removeFromWatchlist(itemId) {
        return await this.request(`watchlist/${itemId}/`, {
            method: 'DELETE'
        });
    }
}

// News API
class NewsAPI extends StockScannerAPI {
    // Get general news
    async getNews(limit = 20) {
        return await this.request(`news/?limit=${limit}`);
    }

    // Get news for specific ticker
    async getStockNews(ticker, limit = 10) {
        return await this.request(`news/?ticker=${ticker.toUpperCase()}&limit=${limit}`);
    }

    // Get personalized news
    async getPersonalizedNews(limit = 20) {
        return await this.request(`news/personalized/?limit=${limit}`);
    }
}

// Alerts API
class AlertsAPI extends StockScannerAPI {
    // Create price alert
    async createAlert(ticker, targetPrice, condition, email) {
        return await this.request('alerts/create/', {
            method: 'POST',
            body: JSON.stringify({
                ticker: ticker.toUpperCase(),
                target_price: parseFloat(targetPrice),
                condition: condition,
                email: email
            })
        });
    }

    // Get user alerts
    async getAlerts() {
        return await this.request('alerts/');
    }

    // Update alert
    async updateAlert(alertId, data) {
        return await this.request(`alerts/${alertId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    // Delete alert
    async deleteAlert(alertId) {
        return await this.request(`alerts/${alertId}/`, {
            method: 'DELETE'
        });
    }
}

// Payment API
class PaymentAPI extends StockScannerAPI {
    // Create payment intent
    async createPaymentIntent(amount, currency = 'USD') {
        return await this.request('payments/create-intent/', {
            method: 'POST',
            body: JSON.stringify({
                amount: amount,
                currency: currency
            })
        });
    }

    // Process subscription
    async createSubscription(planId, paymentMethodId) {
        return await this.request('payments/subscription/', {
            method: 'POST',
            body: JSON.stringify({
                plan_id: planId,
                payment_method_id: paymentMethodId
            })
        });
    }

    // Cancel subscription
    async cancelSubscription(subscriptionId) {
        return await this.request(`payments/subscription/${subscriptionId}/cancel/`, {
            method: 'POST'
        });
    }

    // Get billing history
    async getBillingHistory() {
        return await this.request('billing/history/');
    }

    // Download invoice
    async downloadInvoice(invoiceId) {
        return await this.request(`billing/invoice/${invoiceId}/download/`);
    }
}

// User Management API
class UserAPI extends StockScannerAPI {
    // Get user profile
    async getProfile() {
        return await this.request('user/profile/');
    }

    // Update user profile
    async updateProfile(profileData) {
        return await this.request('user/profile/', {
            method: 'PATCH',
            body: JSON.stringify(profileData)
        });
    }

    // Change password
    async changePassword(currentPassword, newPassword) {
        return await this.request('user/change-password/', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
    }

    // Get subscription details
    async getSubscription() {
        return await this.request('user/subscription/');
    }

    // Update notification preferences
    async updateNotificationPreferences(preferences) {
        return await this.request('user/notifications/', {
            method: 'PATCH',
            body: JSON.stringify(preferences)
        });
    }
}

// Utility functions
class Utils {
    // Format currency
    static formatCurrency(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '$0.00';
        }
        return `$${parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
    }

    // Format percentage
    static formatPercentage(value, decimals = 2, showSign = true) {
        if (value === null || value === undefined || isNaN(value)) {
            return '0.00%';
        }
        const formatted = parseFloat(value).toFixed(decimals) + '%';
        return showSign && value > 0 ? '+' + formatted : formatted;
    }

    // Format large numbers
    static formatNumber(value) {
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
    }

    // Get price change class
    static getPriceChangeClass(change) {
        if (change > 0) return 'price-positive text-success';
        if (change < 0) return 'price-negative text-danger';
        return 'price-neutral text-muted';
    }

    // Validate ticker symbol
    static validateTicker(ticker) {
        if (!ticker) return false;
        const cleaned = ticker.trim().toUpperCase();
        return /^[A-Z]{1,5}$/.test(cleaned) ? cleaned : false;
    }

    // Show loading state
    static showLoading(element, message = 'Loading...') {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;
        
        el.classList.add('loading');
        
        if (!el.querySelector('.loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <span>${message}</span>
                </div>
            `;
            el.appendChild(overlay);
        }
    }

    // Hide loading state
    static hideLoading(element) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;
        
        el.classList.remove('loading');
        const overlay = el.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Show error message
    static showError(element, message) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;
        
        el.innerHTML = `
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <div class="error-message">${message}</div>
                <button class="error-retry btn btn-sm btn-primary">Try Again</button>
            </div>
        `;
    }

    // Debounce function
    static debounce(func, wait) {
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
}

// Real-time data manager
class RealTimeManager {
    constructor() {
        this.intervals = new Map();
        this.stockAPI = new StockAPI();
    }
    
    // Start real-time updates for tickers
    startUpdates(tickers, callback, interval = 30000) {
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
    }
    
    // Stop real-time updates
    stopUpdates(tickers) {
        const key = Array.isArray(tickers) ? tickers.join(',') : tickers;
        
        if (this.intervals.has(key)) {
            clearInterval(this.intervals.get(key));
            this.intervals.delete(key);
        }
    }
    
    // Fetch data for tickers
    async fetchData(tickers, callback) {
        try {
            const data = await this.stockAPI.getRealTimeData(tickers);
            if (callback && typeof callback === 'function') {
                callback(data);
            }
        } catch (error) {
            console.error('Real-time data fetch error:', error);
        }
    }
    
    // Stop all updates
    stopAll() {
        this.intervals.forEach((intervalId) => {
            clearInterval(intervalId);
        });
        this.intervals.clear();
    }
}

// Toast notification system
class Toast {
    static show(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const toastContainer = document.getElementById('toast-container');
        
        if (!toastContainer) {
            console.warn('Toast container not found');
            return;
        }

        const toastElement = document.createElement('div');
        toastElement.id = toastId;
        toastElement.className = `toast toast-${type} opacity-0 transform translate-x-full transition-all duration-300`;
        toastElement.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="Toast.hide('${toastId}')">&times;</button>
            </div>
        `;
        
        toastContainer.appendChild(toastElement);
        
        // Animate in
        setTimeout(() => {
            toastElement.classList.remove('opacity-0', 'translate-x-full');
        }, 100);
        
        // Auto hide
        setTimeout(() => {
            Toast.hide(toastId);
        }, duration);
    }
    
    static hide(toastId) {
        const toast = document.getElementById(toastId);
        if (!toast) return;
        
        toast.classList.add('opacity-0', 'translate-x-full');
        
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

// Initialize APIs
const stockAPI = new StockAPI();
const portfolioAPI = new PortfolioAPI();
const watchlistAPI = new WatchlistAPI();
const newsAPI = new NewsAPI();
const alertsAPI = new AlertsAPI();
const paymentAPI = new PaymentAPI();
const userAPI = new UserAPI();
const realTimeManager = new RealTimeManager();

// Export APIs to global scope
window.StockScannerAPI = {
    Stock: stockAPI,
    Portfolio: portfolioAPI,
    Watchlist: watchlistAPI,
    News: newsAPI,
    Alerts: alertsAPI,
    Payment: paymentAPI,
    User: userAPI,
    Utils: Utils,
    RealTime: realTimeManager,
    Toast: Toast
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-start real-time updates if tickers are found on page
    const stockElements = document.querySelectorAll('[data-ticker]');
    if (stockElements.length > 0) {
        const tickers = [];
        stockElements.forEach(element => {
            const ticker = element.dataset.ticker;
            if (ticker && tickers.indexOf(ticker) === -1) {
                tickers.push(ticker);
            }
        });
        
        if (tickers.length > 0) {
            realTimeManager.startUpdates(tickers, function(data) {
                // Update elements with real-time data
                stockElements.forEach(element => {
                    const ticker = element.dataset.ticker;
                    
                    if (data[ticker]) {
                        const stockData = data[ticker];
                        
                        // Update price
                        const priceElement = element.querySelector('.stock-price');
                        if (priceElement) {
                            priceElement.textContent = Utils.formatCurrency(stockData.current_price);
                        }
                        
                        // Update change
                        const change = stockData.price_change_today || 0;
                        const changePercent = stockData.change_percent || 0;
                        const changeElement = element.querySelector('.stock-change');
                        
                        if (changeElement) {
                            changeElement.textContent = `${Utils.formatCurrency(change)} (${Utils.formatPercentage(changePercent)})`;
                            changeElement.className = 'stock-change ' + Utils.getPriceChangeClass(change);
                        }
                    }
                });
            });
        }
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    realTimeManager.stopAll();
});