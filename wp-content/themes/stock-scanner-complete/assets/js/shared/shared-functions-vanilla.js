/**
 * Stock Scanner Theme - Shared Functions - Pure Vanilla JavaScript
 * Advanced functionality for Portfolio, Watchlist, and News features without jQuery
 */

// Global configuration
const StockScannerVanilla = {
    apiUrl: (typeof stockScannerData !== 'undefined' && stockScannerData.apiBase) ? stockScannerData.apiBase : '/api/',
    nonce: document.querySelector('meta[name="wp-nonce"]')?.content || '',
    currentUser: null,
    cache: new Map(),
    
    // API helper
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-WP-Nonce': this.nonce
            }
        };
        
        try {
            const response = await fetch(this.apiUrl + endpoint, { ...defaultOptions, ...options });
            const contentType = response.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');
            const payload = isJson ? await response.json() : await response.text();
            
            if (!response.ok) {
                const message = isJson && payload && payload.message ? payload.message : ('HTTP ' + response.status);
                throw new Error(message);
            }
            
            if (!isJson) {
                return payload;
            }
            
            return this.normalizeResponse(endpoint, payload);
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    },

    normalizeResponse(endpoint, json) {
        try {
            const path = (endpoint || '').toLowerCase();
            if (json && typeof json === 'object') {
                if (Object.prototype.hasOwnProperty.call(json, 'success')) {
                    if (Object.prototype.hasOwnProperty.call(json, 'data')) {
                        if (path.includes('watchlist/list')) {
                            return (json.data && json.data.watchlists) ? json.data.watchlists : (json.data || []);
                        }
                        if (path.includes('portfolio/list')) {
                            return (json.data && json.data.portfolios) ? json.data.portfolios : (json.data || []);
                        }
                        if (path.includes('news/feed')) {
                            if (json.data && Array.isArray(json.data.news_items)) {
                                return json.data.news_items;
                            }
                        }
                        return json.data;
                    }
                }
                if (Object.prototype.hasOwnProperty.call(json, 'results')) {
                    return json.results;
                }
                if (Object.prototype.hasOwnProperty.call(json, 'news_items')) {
                    return json.news_items;
                }
            }
            return json;
        } catch (e) {
            return json;
        }
    },
    
    // Utility functions
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    formatPercentage(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2
        }).format(value / 100);
    },
    
    showNotification(message, type = 'info') {
        if (window.showNotification) {
            window.showNotification(message, type);
            return;
        }

        // Fallback notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-left: 4px solid ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 400px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 18px; cursor: pointer; color: #95a5a6;">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show animation
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    },

    // DOM utility functions
    select: (selector, context = document) => context.querySelector(selector),
    selectAll: (selector, context = document) => context.querySelectorAll(selector),
    addClass: (element, className) => element?.classList.add(className),
    removeClass: (element, className) => element?.classList.remove(className),
    toggleClass: (element, className) => element?.classList.toggle(className)
};

/**
 * Portfolio Manager Class - Vanilla JS
 */
class PortfolioManagerVanilla {
    constructor() {
        this.portfolios = [];
        this.currentPortfolio = null;
        this.priceUpdateInterval = null;
    }
    
    async init() {
        try {
            await this.loadPortfolios();
            this.setupEventListeners();
            this.startPriceUpdates();
        } catch (error) {
            console.error('Portfolio Manager initialization failed:', error);
            StockScannerVanilla.showNotification('Failed to initialize portfolio manager', 'error');
        }
    }
    
    async loadPortfolios() {
        try {
            this.portfolios = await StockScannerVanilla.apiCall('portfolio/list/');
            this.renderPortfolios();
        } catch (error) {
            console.error('Failed to load portfolios:', error);
            StockScannerVanilla.showNotification('Failed to load portfolios', 'error');
        }
    }
    
    renderPortfolios() {
        const container = StockScannerVanilla.select('#portfolios-grid');
        if (!container) return;
        
        if (this.portfolios.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="empty-state">
                        <div class="empty-icon">📊</div>
                        <h3>No Portfolios Yet</h3>
                        <p>Create your first portfolio to start tracking your investments</p>
                        <button class="btn btn-primary" id="create-first-portfolio">Create Portfolio</button>
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.portfolios.map(portfolio => `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="portfolio-card" data-portfolio-id="${portfolio.id}">
                    <div class="portfolio-header">
                        <h5 class="portfolio-name">${portfolio.name}</h5>
                        <div class="portfolio-actions">
                            <button class="btn btn-sm btn-outline-primary" onclick="portfolioManagerVanilla.viewPortfolio(${portfolio.id})">
                                👁️
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="portfolioManagerVanilla.editPortfolio(${portfolio.id})">
                                ✏️
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="portfolioManagerVanilla.deletePortfolio(${portfolio.id})">
                                🗑️
                            </button>
                        </div>
                    </div>
                    <div class="portfolio-stats">
                        <div class="stat">
                            <label>Total Value</label>
                            <span class="value">${StockScannerVanilla.formatCurrency(portfolio.total_value)}</span>
                        </div>
                        <div class="stat">
                            <label>Total Return</label>
                            <span class="value ${portfolio.total_return >= 0 ? 'positive' : 'negative'}">
                                ${StockScannerVanilla.formatCurrency(portfolio.total_return)}
                                (${StockScannerVanilla.formatPercentage(portfolio.total_return_percent)})
                            </span>
                        </div>
                        <div class="stat">
                            <label>Holdings</label>
                            <span class="value">${portfolio.holdings_count || 0}</span>
                        </div>
                    </div>
                    ${portfolio.description ? `<p class="portfolio-description">${portfolio.description}</p>` : ''}
                    <div class="portfolio-badges">
                        ${portfolio.is_public ? '<span class="badge bg-success">Public</span>' : '<span class="badge bg-secondary">Private</span>'}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async createPortfolio() {
        const nameInput = StockScannerVanilla.select('#portfolio-name');
        const descriptionInput = StockScannerVanilla.select('#portfolio-description');
        const publicInput = StockScannerVanilla.select('#portfolio-public');
        
        if (!nameInput || !nameInput.value.trim()) {
            StockScannerVanilla.showNotification('Portfolio name is required', 'error');
            return;
        }
        
        try {
            await StockScannerVanilla.apiCall('portfolio/create/', {
                method: 'POST',
                body: JSON.stringify({
                    name: nameInput.value.trim(),
                    description: descriptionInput?.value.trim() || '',
                    is_public: publicInput?.checked || false
                })
            });
            
            StockScannerVanilla.showNotification('Portfolio created successfully', 'success');
            this.loadPortfolios();
            
            // Close modal and reset form
            this.hideModal('#createPortfolioModal');
            this.resetForm('#create-portfolio-form');
            
        } catch (error) {
            console.error('Failed to create portfolio:', error);
            StockScannerVanilla.showNotification('Failed to create portfolio: ' + error.message, 'error');
        }
    }
    
    async addHolding() {
        const portfolioIdInput = StockScannerVanilla.select('#holding-portfolio-id');
        const tickerInput = StockScannerVanilla.select('#stock-ticker');
        const sharesInput = StockScannerVanilla.select('#shares-amount');
        const costInput = StockScannerVanilla.select('#average-cost');
        const priceInput = StockScannerVanilla.select('#current-price');
        const sourceInput = StockScannerVanilla.select('#alert-source');
        
        if (!tickerInput?.value || !sharesInput?.value || !costInput?.value) {
            StockScannerVanilla.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            await StockScannerVanilla.apiCall('portfolio/add-holding/', {
                method: 'POST',
                body: JSON.stringify({
                    portfolio_id: parseInt(portfolioIdInput.value),
                    stock_ticker: tickerInput.value.toUpperCase(),
                    shares: parseFloat(sharesInput.value),
                    average_cost: parseFloat(costInput.value),
                    current_price: priceInput?.value ? parseFloat(priceInput.value) : null,
                    from_alert: sourceInput?.value || null
                })
            });
            
            StockScannerVanilla.showNotification('Holding added successfully', 'success');
            this.loadPortfolios();
            
            // Close modal and reset form
            this.hideModal('#addHoldingModal');
            this.resetForm('#add-holding-form');
            
        } catch (error) {
            console.error('Failed to add holding:', error);
            StockScannerVanilla.showNotification('Failed to add holding: ' + error.message, 'error');
        }
    }
    
    async searchStocks(query) {
        if (query.length < 2) return;
        
        try {
            const results = await StockScannerVanilla.apiCall(`stocks/search/?q=${encodeURIComponent(query)}`);
            this.displayStockSearchResults(results);
        } catch (error) {
            console.error('Stock search failed:', error);
        }
    }
    
    displayStockSearchResults(results) {
        const container = StockScannerVanilla.select('#stock-search-results');
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = '<div class="search-result">No stocks found</div>';
            return;
        }
        
        container.innerHTML = results.slice(0, 5).map(stock => `
            <div class="search-result" onclick="portfolioManagerVanilla.selectStock('${stock.ticker}', '${stock.name}')">
                <strong>${stock.ticker}</strong> - ${stock.name}
                ${stock.current_price ? `<span class="price">${StockScannerVanilla.formatCurrency(stock.current_price)}</span>` : ''}
            </div>
        `).join('');
    }
    
    selectStock(ticker, name) {
        const tickerInput = StockScannerVanilla.select('#stock-ticker');
        const resultsContainer = StockScannerVanilla.select('#stock-search-results');
        
        if (tickerInput) {
            tickerInput.value = ticker;
        }
        
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
        
        // Auto-fill current price if available
        this.fetchCurrentPrice(ticker);
    }
    
    async fetchCurrentPrice(ticker) {
        try {
            const data = await StockScannerVanilla.apiCall(`stocks/${ticker}/`);
            const priceInput = StockScannerVanilla.select('#current-price');
            if (data.current_price && priceInput) {
                priceInput.value = data.current_price;
            }
        } catch (error) {
            console.error('Failed to fetch current price:', error);
        }
    }
    
    startPriceUpdates() {
        // Update prices every 30 seconds
        this.priceUpdateInterval = setInterval(() => {
            this.updatePrices();
        }, 30000);
    }
    
    async updatePrices() {
        try {
            // Only update if portfolios are visible
            if (!StockScannerVanilla.select('#portfolios-grid')) return;
            
            await this.loadPortfolios();
        } catch (error) {
            console.error('Price update failed:', error);
        }
    }
    
    setupEventListeners() {
        // Create first portfolio button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'create-first-portfolio') {
                this.showModal('#createPortfolioModal');
            }
        });

        // Form submissions
        const createForm = StockScannerVanilla.select('#create-portfolio-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createPortfolio();
            });
        }

        const holdingForm = StockScannerVanilla.select('#add-holding-form');
        if (holdingForm) {
            holdingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addHolding();
            });
        }

        // Stock search
        const searchInput = StockScannerVanilla.select('#stock-search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchStocks(e.target.value);
                }, 300);
            });
        }
    }

    // Modal management
    showModal(selector) {
        const modal = StockScannerVanilla.select(selector);
        if (modal) {
            StockScannerVanilla.addClass(modal, 'show');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal(selector) {
        const modal = StockScannerVanilla.select(selector);
        if (modal) {
            StockScannerVanilla.removeClass(modal, 'show');
            document.body.style.overflow = '';
        }
    }

    resetForm(selector) {
        const form = StockScannerVanilla.select(selector);
        if (form) {
            form.reset();
        }
    }

    // Portfolio actions
    viewPortfolio(id) {
        window.location.href = `/portfolio/${id}/`;
    }

    editPortfolio(id) {
        // Implementation for edit functionality
        console.log('Edit portfolio:', id);
    }

    async deletePortfolio(id) {
        if (!confirm('Are you sure you want to delete this portfolio?')) {
            return;
        }

        try {
            await StockScannerVanilla.apiCall(`portfolio/${id}/delete/`, {
                method: 'DELETE'
            });
            
            StockScannerVanilla.showNotification('Portfolio deleted successfully', 'success');
            this.loadPortfolios();
        } catch (error) {
            console.error('Failed to delete portfolio:', error);
            StockScannerVanilla.showNotification('Failed to delete portfolio: ' + error.message, 'error');
        }
    }
}

/**
 * Watchlist Manager Class - Vanilla JS
 */
class WatchlistManagerVanilla {
    constructor() {
        this.watchlists = [];
        this.currentWatchlist = null;
        this.priceUpdateInterval = null;
    }
    
    async init() {
        try {
            await this.loadWatchlists();
            this.setupEventListeners();
            this.startPriceUpdates();
        } catch (error) {
            console.error('Watchlist Manager initialization failed:', error);
            StockScannerVanilla.showNotification('Failed to initialize watchlist manager', 'error');
        }
    }
    
    async loadWatchlists() {
        try {
            this.watchlists = await StockScannerVanilla.apiCall('watchlist/list/');
            this.renderWatchlists();
        } catch (error) {
            console.error('Failed to load watchlists:', error);
            StockScannerVanilla.showNotification('Failed to load watchlists', 'error');
        }
    }
    
    renderWatchlists() {
        const container = StockScannerVanilla.select('#watchlists-container');
        if (!container) return;
        
        if (this.watchlists.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="empty-state">
                        <div class="empty-icon">👁️</div>
                        <h3>No Watchlists Yet</h3>
                        <p>Create your first watchlist or add from suggested stocks:</p>
                        <div class="suggested-stocks" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 20px 0;">
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('AAPL')">AAPL</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('MSFT')">MSFT</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('NVDA')">NVDA</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('AMZN')">AMZN</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('TSLA')">TSLA</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.quickAddSuggested('GOOGL')">GOOGL</button>
                        </div>
                        <button class="btn btn-primary" id="create-first-watchlist">Create Watchlist</button>
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.watchlists.map(watchlist => `
            <div class="col-lg-6 col-md-12 mb-4">
                <div class="watchlist-card" data-watchlist-id="${watchlist.id}">
                    <div class="watchlist-header">
                        <h5 class="watchlist-name">${watchlist.name}</h5>
                        <div class="watchlist-actions">
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManagerVanilla.viewWatchlist(${watchlist.id})">
                                👁️
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="watchlistManagerVanilla.exportWatchlist(${watchlist.id}, 'csv')">
                                📊 CSV
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="watchlistManagerVanilla.exportWatchlist(${watchlist.id}, 'json')">
                                📄 JSON
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="watchlistManagerVanilla.deleteWatchlist(${watchlist.id})">
                                🗑️
                            </button>
                        </div>
                    </div>
                    <div class="watchlist-stats">
                        <div class="stat">
                            <label>Total Stocks</label>
                            <span class="value">${watchlist.items_count || 0}</span>
                        </div>
                        <div class="stat">
                            <label>Avg Performance</label>
                            <span class="value ${(watchlist.average_performance || 0) >= 0 ? 'positive' : 'negative'}">
                                ${StockScannerVanilla.formatPercentage(watchlist.average_performance || 0)}
                            </span>
                        </div>
                        <div class="stat">
                            <label>Best Performer</label>
                            <span class="value positive">${watchlist.best_performer || 'N/A'}</span>
                        </div>
                    </div>
                    ${watchlist.description ? `<p class="watchlist-description">${watchlist.description}</p>` : ''}
                    <div class="watchlist-items-preview">
                        ${watchlist.recent_items ? watchlist.recent_items.slice(0, 3).map(item => `
                            <span class="stock-ticker">${item.ticker}</span>
                        `).join('') : ''}
                        ${(watchlist.items_count || 0) > 3 ? `<span class="more-count">+${(watchlist.items_count || 0) - 3} more</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async quickAddSuggested(ticker) {
        try {
            // Create a default watchlist if none exists
            if (!this.watchlists || this.watchlists.length === 0) {
                await this.createDefaultWatchlist();
            }
            
            const firstWatchlist = this.watchlists[0];
            if (firstWatchlist) {
                await this.addStockToWatchlist(firstWatchlist.id, ticker);
            }
        } catch (error) {
            console.error('Failed to add suggested stock:', error);
            StockScannerVanilla.showNotification('Failed to add suggested stock', 'error');
        }
    }

    async createDefaultWatchlist() {
        try {
            await StockScannerVanilla.apiCall('watchlist/create/', {
                method: 'POST',
                body: JSON.stringify({
                    name: 'My Watchlist',
                    description: 'Auto-created watchlist'
                })
            });
            await this.loadWatchlists();
        } catch (error) {
            console.error('Failed to create default watchlist:', error);
            throw error;
        }
    }

    async addStockToWatchlist(watchlistId, ticker) {
        try {
            await StockScannerVanilla.apiCall('watchlist/add-stock/', {
                method: 'POST',
                body: JSON.stringify({
                    watchlist_id: parseInt(watchlistId),
                    stock_ticker: ticker,
                    price_alert_enabled: false,
                    news_alert_enabled: true
                })
            });
            
            StockScannerVanilla.showNotification(`${ticker} added to watchlist`, 'success');
            await this.loadWatchlists();
        } catch (error) {
            console.error('Failed to add stock to watchlist:', error);
            throw error;
        }
    }
    
    setupEventListeners() {
        // Create first watchlist button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'create-first-watchlist') {
                this.showModal('#createWatchlistModal');
            }
        });

        // Form submissions
        const createForm = StockScannerVanilla.select('#create-watchlist-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createWatchlist();
            });
        }
    }

    async createWatchlist() {
        const nameInput = StockScannerVanilla.select('#watchlist-name');
        const descriptionInput = StockScannerVanilla.select('#watchlist-description');
        
        if (!nameInput || !nameInput.value.trim()) {
            StockScannerVanilla.showNotification('Watchlist name is required', 'error');
            return;
        }
        
        try {
            await StockScannerVanilla.apiCall('watchlist/create/', {
                method: 'POST',
                body: JSON.stringify({
                    name: nameInput.value.trim(),
                    description: descriptionInput?.value.trim() || ''
                })
            });
            
            StockScannerVanilla.showNotification('Watchlist created successfully', 'success');
            this.loadWatchlists();
            
            // Close modal and reset form
            this.hideModal('#createWatchlistModal');
            this.resetForm('#create-watchlist-form');
            
        } catch (error) {
            console.error('Failed to create watchlist:', error);
            StockScannerVanilla.showNotification('Failed to create watchlist: ' + error.message, 'error');
        }
    }

    startPriceUpdates() {
        // Update prices every 30 seconds
        this.priceUpdateInterval = setInterval(() => {
            this.updatePrices();
        }, 30000);
    }
    
    async updatePrices() {
        try {
            // Only update if watchlists are visible
            if (!StockScannerVanilla.select('#watchlists-container')) return;
            
            await this.loadWatchlists();
        } catch (error) {
            console.error('Price update failed:', error);
        }
    }

    // Modal and form management
    showModal(selector) {
        const modal = StockScannerVanilla.select(selector);
        if (modal) {
            StockScannerVanilla.addClass(modal, 'show');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal(selector) {
        const modal = StockScannerVanilla.select(selector);
        if (modal) {
            StockScannerVanilla.removeClass(modal, 'show');
            document.body.style.overflow = '';
        }
    }

    resetForm(selector) {
        const form = StockScannerVanilla.select(selector);
        if (form) {
            form.reset();
        }
    }

    // Watchlist actions
    viewWatchlist(id) {
        window.location.href = `/watchlist/${id}/`;
    }

    async exportWatchlist(id, format) {
        try {
            const response = await fetch(`${StockScannerVanilla.apiUrl}watchlist/${id}/export/${format}/`, {
                method: 'GET',
                headers: {
                    'X-WP-Nonce': StockScannerVanilla.nonce
                }
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `watchlist_${id}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            StockScannerVanilla.showNotification(`Watchlist exported as ${format.toUpperCase()}`, 'success');
            
        } catch (error) {
            console.error('Failed to export watchlist:', error);
            StockScannerVanilla.showNotification('Failed to export watchlist', 'error');
        }
    }

    async deleteWatchlist(id) {
        if (!confirm('Are you sure you want to delete this watchlist?')) {
            return;
        }

        try {
            await StockScannerVanilla.apiCall(`watchlist/${id}/delete/`, {
                method: 'DELETE'
            });
            
            StockScannerVanilla.showNotification('Watchlist deleted successfully', 'success');
            this.loadWatchlists();
        } catch (error) {
            console.error('Failed to delete watchlist:', error);
            StockScannerVanilla.showNotification('Failed to delete watchlist: ' + error.message, 'error');
        }
    }
}

// Initialize managers when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize portfolio manager if on portfolio page
    if (StockScannerVanilla.select('#portfolios-grid')) {
        window.portfolioManagerVanilla = new PortfolioManagerVanilla();
        window.portfolioManagerVanilla.init();
    }
    
    // Initialize watchlist manager if on watchlist page
    if (StockScannerVanilla.select('#watchlists-container')) {
        window.watchlistManagerVanilla = new WatchlistManagerVanilla();
        window.watchlistManagerVanilla.init();
    }
});

// Export for global use
window.StockScannerVanilla = StockScannerVanilla;
window.PortfolioManagerVanilla = PortfolioManagerVanilla;
window.WatchlistManagerVanilla = WatchlistManagerVanilla;