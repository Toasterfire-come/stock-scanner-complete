/**
 * Stock Scanner Theme - Shared Functions
 * Advanced JavaScript functionality for Portfolio, Watchlist, and News features
 */

// Global configuration
const StockScanner = {
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
    },

    // Normalizes various REST shapes to what the UI expects
    normalizeResponse(endpoint, json) {
        try {
            const path = (endpoint || '').toLowerCase();
            if (json && typeof json === 'object') {
                if (Object.prototype.hasOwnProperty.call(json, 'success')) {
                    // Common wrapper { success, data }
                    if (Object.prototype.hasOwnProperty.call(json, 'data')) {
                        // Special-case list endpoints used by UI
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
                // Search endpoints often return { results }
                if (Object.prototype.hasOwnProperty.call(json, 'results')) {
                    return json.results;
                }
                // Some feeds return { news_items }
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
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        // Remove on click
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
};

/**
 * Portfolio Manager Class
 */
class PortfolioManager {
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
            StockScanner.showNotification('Failed to initialize portfolio manager', 'error');
        }
    }
    
    async loadPortfolios() {
        try {
            this.portfolios = await StockScanner.apiCall('portfolio/list/');
            this.renderPortfolios();
        } catch (error) {
            console.error('Failed to load portfolios:', error);
            StockScanner.showNotification('Failed to load portfolios', 'error');
        }
    }
    
    renderPortfolios() {
        const container = document.getElementById('portfolios-grid');
        if (!container) return;
        
        if (this.portfolios.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="empty-state">
                        <i class="fas fa-chart-pie fa-3x mb-3"></i>
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
                            <button class="btn btn-sm btn-outline-primary" onclick="portfolioManager.viewPortfolio(${portfolio.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="portfolioManager.editPortfolio(${portfolio.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="portfolioManager.deletePortfolio(${portfolio.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="portfolio-stats">
                        <div class="stat">
                            <label>Total Value</label>
                            <span class="value">${StockScanner.formatCurrency(portfolio.total_value)}</span>
                        </div>
                        <div class="stat">
                            <label>Total Return</label>
                            <span class="value ${portfolio.total_return >= 0 ? 'positive' : 'negative'}">
                                ${StockScanner.formatCurrency(portfolio.total_return)}
                                (${StockScanner.formatPercentage(portfolio.total_return_percent)})
                            </span>
                        </div>
                        <div class="stat">
                            <label>Holdings</label>
                            <span class="value">${portfolio.holdings_count || 0}</span>
                        </div>
                    </div>
                    ${portfolio.description ? `<p class="portfolio-description">${portfolio.description}</p>` : ''}
                    ${portfolio.is_public ? '<span class="badge bg-success">Public</span>' : '<span class="badge bg-secondary">Private</span>'}
                </div>
            </div>
        `).join('');
    }
    
    async createPortfolio() {
        const name = document.getElementById('portfolio-name').value;
        const description = document.getElementById('portfolio-description').value;
        const isPublic = document.getElementById('portfolio-public').checked;
        
        if (!name.trim()) {
            StockScanner.showNotification('Portfolio name is required', 'error');
            return;
        }
        
        try {
            await StockScanner.apiCall('portfolio/create/', {
                method: 'POST',
                body: JSON.stringify({
                    name: name.trim(),
                    description: description.trim(),
                    is_public: isPublic
                })
            });
            
            StockScanner.showNotification('Portfolio created successfully', 'success');
            this.loadPortfolios();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createPortfolioModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('create-portfolio-form').reset();
            
        } catch (error) {
            console.error('Failed to create portfolio:', error);
            StockScanner.showNotification('Failed to create portfolio: ' + error.message, 'error');
        }
    }
    
    async addHolding() {
        const portfolioId = document.getElementById('holding-portfolio-id').value;
        const ticker = document.getElementById('stock-ticker').value.toUpperCase();
        const shares = parseFloat(document.getElementById('shares-amount').value);
        const averageCost = parseFloat(document.getElementById('average-cost').value);
        const currentPrice = parseFloat(document.getElementById('current-price').value) || null;
        const alertSource = document.getElementById('alert-source').value || null;
        
        if (!ticker || !shares || !averageCost) {
            StockScanner.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            await StockScanner.apiCall('portfolio/add-holding/', {
                method: 'POST',
                body: JSON.stringify({
                    portfolio_id: parseInt(portfolioId),
                    stock_ticker: ticker,
                    shares: shares,
                    average_cost: averageCost,
                    current_price: currentPrice,
                    from_alert: alertSource
                })
            });
            
            StockScanner.showNotification('Holding added successfully', 'success');
            this.loadPortfolios();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addHoldingModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('add-holding-form').reset();
            
        } catch (error) {
            console.error('Failed to add holding:', error);
            StockScanner.showNotification('Failed to add holding: ' + error.message, 'error');
        }
    }
    
    async importFromCSV() {
        const portfolioName = document.getElementById('import-portfolio-name').value;
        const fileInput = document.getElementById('csv-file');
        const file = fileInput.files[0];
        
        if (!portfolioName.trim() || !file) {
            StockScanner.showNotification('Please provide a portfolio name and select a CSV file', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('portfolio_name', portfolioName.trim());
        formData.append('csv_file', file);
        
        try {
            const response = await fetch(StockScanner.apiUrl + 'portfolio/import-csv/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-WP-Nonce': StockScanner.nonce,
                    'Accept': 'application/json'
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Import failed');
            }
            
            StockScanner.showNotification('Portfolio imported successfully', 'success');
            this.loadPortfolios();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('importCsvModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('import-csv-form').reset();
            
        } catch (error) {
            console.error('Failed to import portfolio:', error);
            StockScanner.showNotification('Failed to import portfolio: ' + error.message, 'error');
        }
    }
    
    async loadROIAnalytics() {
        try {
            const analytics = await StockScanner.apiCall('portfolio/alert-roi/');
            this.renderROIAnalytics(analytics);
        } catch (error) {
            console.error('Failed to load ROI analytics:', error);
            StockScanner.showNotification('Failed to load ROI analytics', 'error');
        }
    }
    
    renderROIAnalytics(analytics) {
        const container = document.getElementById('roi-analytics-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="roi-summary">
                <h6>Alert-Based Trading Performance</h6>
                <div class="row">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Success Rate</label>
                            <span class="value">${StockScanner.formatPercentage(analytics.success_rate)}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Total Trades</label>
                            <span class="value">${analytics.total_trades}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Avg ROI</label>
                            <span class="value">${StockScanner.formatPercentage(analytics.average_roi)}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Best Trade</label>
                            <span class="value">${StockScanner.formatPercentage(analytics.best_trade)}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="roi-details">
                <h6>Performance by Category</h6>
                ${analytics.by_category ? Object.entries(analytics.by_category).map(([category, stats]) => `
                    <div class="category-performance">
                        <h6>${category}</h6>
                        <div class="stats">
                            <span>Success Rate: ${StockScanner.formatPercentage(stats.success_rate)}</span>
                            <span>Avg ROI: ${StockScanner.formatPercentage(stats.average_roi)}</span>
                            <span>Trades: ${stats.total_trades}</span>
                        </div>
                    </div>
                `).join('') : '<p>No category data available</p>'}
            </div>
        `;
    }
    
    sortPortfolios(sortBy) {
        const sortedPortfolios = [...this.portfolios].sort((a, b) => {
            switch (sortBy) {
                case 'performance':
                    return b.total_return_percent - a.total_return_percent;
                case 'value':
                    return b.total_value - a.total_value;
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'created':
                default:
                    return new Date(b.created_at) - new Date(a.created_at);
            }
        });
        
        this.portfolios = sortedPortfolios;
        this.renderPortfolios();
    }
    
    async searchStocks(query) {
        if (query.length < 2) return;
        
        try {
            const results = await StockScanner.apiCall(`stocks/search/?q=${encodeURIComponent(query)}`);
            this.displayStockSearchResults(results);
        } catch (error) {
            console.error('Stock search failed:', error);
        }
    }
    
    displayStockSearchResults(results) {
        const container = document.getElementById('stock-search-results');
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = '<div class="search-result">No stocks found</div>';
            return;
        }
        
        container.innerHTML = results.slice(0, 5).map(stock => `
            <div class="search-result" onclick="portfolioManager.selectStock('${stock.ticker}', '${stock.name}')">
                <strong>${stock.ticker}</strong> - ${stock.name}
                ${stock.current_price ? `<span class="price">${StockScanner.formatCurrency(stock.current_price)}</span>` : ''}
            </div>
        `).join('');
    }
    
    selectStock(ticker, name) {
        document.getElementById('stock-ticker').value = ticker;
        document.getElementById('stock-search-results').innerHTML = '';
        
        // Auto-fill current price if available
        this.fetchCurrentPrice(ticker);
    }
    
    async fetchCurrentPrice(ticker) {
        try {
            const data = await StockScanner.apiCall(`stocks/${ticker}/`);
            if (data.current_price) {
                document.getElementById('current-price').value = data.current_price;
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
            if (!document.getElementById('portfolios-grid')) return;
            
            await this.loadPortfolios();
        } catch (error) {
            console.error('Price update failed:', error);
        }
    }
    
    setupEventListeners() {
        // Set up event listeners for forms and buttons
        const createFirstBtn = document.getElementById('create-first-portfolio');
        if (createFirstBtn) {
            createFirstBtn.addEventListener('click', () => {
                const modal = new bootstrap.Modal(document.getElementById('createPortfolioModal'));
                modal.show();
            });
        }
    }
}

/**
 * Watchlist Manager Class
 */
class WatchlistManager {
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
            StockScanner.showNotification('Failed to initialize watchlist manager', 'error');
        }
    }
    
    async loadWatchlists() {
        try {
            this.watchlists = await StockScanner.apiCall('watchlist/list/');
            this.renderWatchlists();
        } catch (error) {
            console.error('Failed to load watchlists:', error);
            StockScanner.showNotification('Failed to load watchlists', 'error');
        }
    }
    
    renderWatchlists() {
        const container = document.getElementById('watchlists-container');
        if (!container) return;
        
        if (this.watchlists.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="empty-state">
                        <i class="fas fa-eye fa-3x mb-3"></i>
                        <h3>No Watchlists Yet</h3>
                        <p>Create your first watchlist or add from suggested stocks:</p>
                        <div class="suggested-stocks d-flex flex-wrap justify-content-center gap-2 mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('AAPL')">AAPL</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('MSFT')">MSFT</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('NVDA')">NVDA</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('AMZN')">AMZN</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('TSLA')">TSLA</button>
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.quickAddSuggested('GOOGL')">GOOGL</button>
                        </div>
                        <button class="btn btn-primary mt-3" id="create-first-watchlist">Create Watchlist</button>
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
                            <button class="btn btn-sm btn-outline-primary" onclick="watchlistManager.viewWatchlist(${watchlist.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="watchlistManager.exportWatchlist(${watchlist.id}, 'csv')">
                                <i class="fas fa-download"></i> CSV
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="watchlistManager.exportWatchlist(${watchlist.id}, 'json')">
                                <i class="fas fa-download"></i> JSON
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="watchlistManager.deleteWatchlist(${watchlist.id})">
                                <i class="fas fa-trash"></i>
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
                                ${StockScanner.formatPercentage(watchlist.average_performance || 0)}
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
    
    async createWatchlist() {
        const name = document.getElementById('watchlist-name').value;
        const description = document.getElementById('watchlist-description').value;
        
        if (!name.trim()) {
            StockScanner.showNotification('Watchlist name is required', 'error');
            return;
        }
        
        try {
            await StockScanner.apiCall('watchlist/create/', {
                method: 'POST',
                body: JSON.stringify({
                    name: name.trim(),
                    description: description.trim()
                })
            });
            
            StockScanner.showNotification('Watchlist created successfully', 'success');
            this.loadWatchlists();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createWatchlistModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('create-watchlist-form').reset();
            
        } catch (error) {
            console.error('Failed to create watchlist:', error);
            StockScanner.showNotification('Failed to create watchlist: ' + error.message, 'error');
        }
    }
    
    async addStock() {
        const watchlistId = document.getElementById('target-watchlist-id').value;
        const ticker = document.getElementById('stock-ticker-add').value.toUpperCase();
        const addedPrice = parseFloat(document.getElementById('added-price').value) || null;
        const targetPrice = parseFloat(document.getElementById('target-price').value) || null;
        const stopLoss = parseFloat(document.getElementById('stop-loss').value) || null;
        const notes = document.getElementById('stock-notes').value;
        const priceAlertEnabled = document.getElementById('price-alert-enabled').checked;
        const newsAlertEnabled = document.getElementById('news-alert-enabled').checked;
        
        if (!ticker) {
            StockScanner.showNotification('Stock ticker is required', 'error');
            return;
        }
        
        try {
            await StockScanner.apiCall('watchlist/add-stock/', {
                method: 'POST',
                body: JSON.stringify({
                    watchlist_id: parseInt(watchlistId),
                    stock_ticker: ticker,
                    added_price: addedPrice,
                    target_price: targetPrice,
                    stop_loss: stopLoss,
                    notes: notes.trim(),
                    price_alert_enabled: priceAlertEnabled,
                    news_alert_enabled: newsAlertEnabled
                })
            });
            
            StockScanner.showNotification('Stock added to watchlist successfully', 'success');
            this.loadWatchlists();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addStockModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('add-stock-form').reset();
            
        } catch (error) {
            console.error('Failed to add stock to watchlist:', error);
            StockScanner.showNotification('Failed to add stock: ' + error.message, 'error');
        }
    }
    
    quickAddSuggested(ticker) {
        // Create a default watchlist if none exists, then add ticker
        if (!this.watchlists || this.watchlists.length === 0) {
            this.createDefaultAndAdd(ticker);
            return;
        }
        const firstId = this.watchlists[0].id;
        this.addStockToWatchlist(firstId, ticker);
    }

    async createDefaultAndAdd(ticker) {
        try {
            const newWatch = await StockScanner.apiCall('watchlist/create/', {
                method: 'POST',
                body: JSON.stringify({ name: 'My Watchlist', description: 'Auto-created' })
            });
            await this.loadWatchlists();
            const targetId = newWatch?.id || (this.watchlists[0] && this.watchlists[0].id);
            if (targetId) {
                await this.addStockToWatchlist(targetId, ticker);
            }
        } catch (e) {
            console.error('Failed to create default watchlist:', e);
            StockScanner.showNotification('Failed to create watchlist', 'error');
        }
    }

    async addStockToWatchlist(watchlistId, ticker) {
        try {
            await StockScanner.apiCall('watchlist/add-stock/', {
                method: 'POST',
                body: JSON.stringify({
                    watchlist_id: parseInt(watchlistId),
                    ticker: ticker,
                    price_alert_enabled: false,
                    news_alert_enabled: true
                })
            });
            StockScanner.showNotification(`${ticker} added to watchlist`, 'success');
            await this.loadWatchlists();
        } catch (e) {
            console.error('Failed to add suggested:', e);
            StockScanner.showNotification('Failed to add suggested stock', 'error');
        }
    }

    async importWatchlist() {
        const activeTab = document.querySelector('#importWatchlistModal .nav-pills .active').id;
        const isCSV = activeTab === 'csv-import-tab';
        
        const fileInput = isCSV ? 
            document.getElementById('csv-watchlist-file') : 
            document.getElementById('json-watchlist-file');
        const file = fileInput.files[0];
        
        if (!file) {
            StockScanner.showNotification('Please select a file to import', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        if (isCSV) {
            const watchlistName = document.getElementById('import-watchlist-name-csv').value;
            if (!watchlistName.trim()) {
                StockScanner.showNotification('Watchlist name is required for CSV import', 'error');
                return;
            }
            formData.append('watchlist_name', watchlistName.trim());
        }
        
        try {
            const endpoint = isCSV ? 'watchlist/import/csv/' : 'watchlist/import/json/';
            const response = await fetch(StockScanner.apiUrl + endpoint, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-WP-Nonce': StockScanner.nonce,
                    'Accept': 'application/json'
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Import failed');
            }
            
            StockScanner.showNotification('Watchlist imported successfully', 'success');
            this.loadWatchlists();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('importWatchlistModal'));
            modal.hide();
            
            // Reset forms
            document.getElementById('import-csv-watchlist-form').reset();
            document.getElementById('import-json-watchlist-form').reset();
            
        } catch (error) {
            console.error('Failed to import watchlist:', error);
            StockScanner.showNotification('Failed to import watchlist: ' + error.message, 'error');
        }
    }
    
    async exportWatchlist(watchlistId, format) {
        try {
            const response = await fetch(`${StockScanner.apiUrl}watchlist/${watchlistId}/export/${format}/`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'X-WP-Nonce': StockScanner.nonce
                }
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `watchlist_${watchlistId}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            StockScanner.showNotification(`Watchlist exported as ${format.toUpperCase()}`, 'success');
            
        } catch (error) {
            console.error('Failed to export watchlist:', error);
            StockScanner.showNotification('Failed to export watchlist', 'error');
        }
    }
    
    populateBulkWatchlistOptions() {
        const select = document.getElementById('bulk-target-watchlist');
        select.innerHTML = '<option value="">Select a watchlist...</option>';
        
        this.watchlists.forEach(watchlist => {
            const option = document.createElement('option');
            option.value = watchlist.id;
            option.textContent = watchlist.name;
            select.appendChild(option);
        });
    }
    
    async bulkAddStocks() {
        const watchlistId = document.getElementById('bulk-target-watchlist').value;
        const tickersText = document.getElementById('bulk-stock-tickers').value;
        const priceAlerts = document.getElementById('bulk-price-alerts').checked;
        const newsAlerts = document.getElementById('bulk-news-alerts').checked;
        
        if (!watchlistId || !tickersText.trim()) {
            StockScanner.showNotification('Please select a watchlist and enter stock tickers', 'error');
            return;
        }
        
        const tickers = tickersText.split(/[,\n]/).map(t => t.trim().toUpperCase()).filter(t => t);
        
        if (tickers.length === 0) {
            StockScanner.showNotification('No valid stock tickers found', 'error');
            return;
        }
        
        let successCount = 0;
        let failCount = 0;
        
        for (const ticker of tickers) {
            try {
                await StockScanner.apiCall('watchlist/add-stock/', {
                    method: 'POST',
                    body: JSON.stringify({
                        watchlist_id: parseInt(watchlistId),
                        stock_ticker: ticker,
                        price_alert_enabled: priceAlerts,
                        news_alert_enabled: newsAlerts
                    })
                });
                successCount++;
            } catch (error) {
                console.error(`Failed to add ${ticker}:`, error);
                failCount++;
            }
        }
        
        StockScanner.showNotification(
            `Bulk add completed: ${successCount} added, ${failCount} failed`, 
            failCount > 0 ? 'warning' : 'success'
        );
        
        this.loadWatchlists();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('bulkAddModal'));
        modal.hide();
        
        // Reset form
        document.getElementById('bulk-add-form').reset();
    }
    
    changeView(viewType) {
        const container = document.getElementById('watchlists-container');
        container.className = `row mt-3 view-${viewType}`;
        this.renderWatchlists();
    }
    
    sortWatchlists(sortBy) {
        const sortedWatchlists = [...this.watchlists].sort((a, b) => {
            switch (sortBy) {
                case 'performance':
                    return (b.average_performance || 0) - (a.average_performance || 0);
                case 'items':
                    return (b.items_count || 0) - (a.items_count || 0);
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'created':
                default:
                    return new Date(b.created_at) - new Date(a.created_at);
            }
        });
        
        this.watchlists = sortedWatchlists;
        this.renderWatchlists();
    }
    
    async searchStocks(query, containerId) {
        if (query.length < 2) return;
        
        try {
            const results = await StockScanner.apiCall(`stocks/search/?q=${encodeURIComponent(query)}`);
            this.displayStockSearchResults(results, containerId);
        } catch (error) {
            console.error('Stock search failed:', error);
        }
    }
    
    displayStockSearchResults(results, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = '<div class="search-result">No stocks found</div>';
            return;
        }
        
        container.innerHTML = results.slice(0, 5).map(stock => `
            <div class="search-result" onclick="watchlistManager.selectStock('${stock.ticker}', '${stock.name}', '${containerId}')">
                <strong>${stock.ticker}</strong> - ${stock.name}
                ${stock.current_price ? `<span class="price">${StockScanner.formatCurrency(stock.current_price)}</span>` : ''}
            </div>
        `).join('');
    }
    
    selectStock(ticker, name, containerId) {
        document.getElementById('stock-ticker-add').value = ticker;
        document.getElementById(containerId).innerHTML = '';
        
        // Auto-fill current price if available
        this.fetchCurrentPrice(ticker);
    }
    
    async fetchCurrentPrice(ticker) {
        try {
            const data = await StockScanner.apiCall(`stocks/${ticker}/`);
            if (data.current_price) {
                document.getElementById('added-price').value = data.current_price;
            }
        } catch (error) {
            console.error('Failed to fetch current price:', error);
        }
    }
    
    useCurrentPrice() {
        const ticker = document.getElementById('stock-ticker-add').value;
        if (ticker) {
            this.fetchCurrentPrice(ticker);
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
            if (!document.getElementById('watchlists-container')) return;
            
            await this.loadWatchlists();
        } catch (error) {
            console.error('Price update failed:', error);
        }
    }
    
    setupEventListeners() {
        // Set up event listeners for forms and buttons
        const createFirstBtn = document.getElementById('create-first-watchlist');
        if (createFirstBtn) {
            createFirstBtn.addEventListener('click', () => {
                const modal = new bootstrap.Modal(document.getElementById('createWatchlistModal'));
                modal.show();
            });
        }
    }
}

/**
 * News Manager Class
 */
class NewsManager {
    constructor() {
        this.newsItems = [];
        this.preferences = {};
        this.currentTab = 'for-you';
        this.readLaterItems = new Set();
    }
    
    async init() {
        try {
            await this.loadPreferences();
            await this.loadPersonalizedFeed();
            this.setupEventListeners();
            this.startAutoRefresh();
        } catch (error) {
            console.error('News Manager initialization failed:', error);
            StockScanner.showNotification('Failed to initialize news manager', 'error');
        }
    }
    
    async loadPersonalizedFeed() {
        try {
            const params = new URLSearchParams({
                limit: 20,
                category: document.getElementById('news-category')?.value || ''
            });
            
            this.newsItems = await StockScanner.apiCall(`news/feed/?${params}`);
            this.renderNewsFeed();
        } catch (error) {
            console.error('Failed to load news feed:', error);
            StockScanner.showNotification('Failed to load news feed', 'error');
        }
    }
    
    renderNewsFeed() {
        const container = document.getElementById('for-you-feed');
        if (!container) return;
        
        if (this.newsItems.length === 0) {
            container.innerHTML = `
                <div class="empty-state text-center py-5">
                    <i class="fas fa-newspaper fa-3x mb-3"></i>
                    <h3>No News Available</h3>
                    <p>Check back later for personalized news updates</p>
                    <button class="btn btn-primary" onclick="newsManager.syncPortfolioStocks()">
                        Sync with Portfolio
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.newsItems.map(article => `
            <article class="news-item" data-news-id="${article.id}">
                <div class="news-content">
                    <div class="news-header">
                        <h5 class="news-title">
                            <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                                ${article.title}
                            </a>
                        </h5>
                        <div class="news-meta">
                            <span class="news-source">${article.source}</span>
                            <span class="news-date">${new Date(article.published_at).toLocaleDateString()}</span>
                            <span class="relevance-score">
                                Relevance: ${parseFloat(article.relevance_score).toFixed(1)}/10
                            </span>
                        </div>
                    </div>
                    
                    <div class="news-body">
                        <p class="news-summary">${article.summary || article.content.substring(0, 200) + '...'}</p>
                        ${article.related_stocks && article.related_stocks.length > 0 ? `
                            <div class="related-stocks">
                                <strong>Related Stocks:</strong>
                                ${article.related_stocks.map(ticker => `<span class="stock-ticker">${ticker}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="news-footer">
                        <div class="news-category">
                            <span class="badge bg-secondary">${article.category}</span>
                        </div>
                        <div class="news-actions">
                            <button class="btn btn-sm btn-outline-primary bookmark-btn" 
                                    onclick="newsManager.toggleBookmark(${article.id})">
                                <i class="fas fa-bookmark"></i>
                                ${this.readLaterItems.has(article.id) ? 'Saved' : 'Save'}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary share-btn" 
                                    onclick="newsManager.shareArticle(${article.id})">
                                <i class="fas fa-share"></i> Share
                            </button>
                            <button class="btn btn-sm btn-outline-info" 
                                    onclick="newsManager.viewArticle(${article.id})">
                                <i class="fas fa-eye"></i> View
                            </button>
                        </div>
                    </div>
                </div>
            </article>
        `).join('');
    }
    
    async loadPreferences() {
        try {
            // Load from localStorage first, then API
            const stored = localStorage.getItem('news_preferences');
            if (stored) {
                this.preferences = JSON.parse(stored);
            }
            
            // This would load from the API in a real implementation
            // const preferences = await StockScanner.apiCall('news/preferences/');
            // this.preferences = { ...this.preferences, ...preferences };
        } catch (error) {
            console.error('Failed to load news preferences:', error);
        }
    }
    
    async savePreferences() {
        const preferences = {
            followed_stocks: document.getElementById('followed-stocks').value.split(',').map(s => s.trim()).filter(s => s),
            followed_sectors: document.getElementById('followed-sectors').value.split(',').map(s => s.trim()).filter(s => s),
            preferred_categories: Array.from(document.querySelectorAll('.preferred-categories input:checked')).map(cb => cb.value),
            news_frequency: document.getElementById('news-frequency').value,
            auto_sync_portfolio: document.getElementById('auto-sync-portfolio').checked,
            exclude_low_relevance: document.getElementById('exclude-low-relevance').checked,
            prioritize_holdings: document.getElementById('prioritize-holdings').checked
        };
        
        try {
            await StockScanner.apiCall('news/preferences/', {
                method: 'POST',
                body: JSON.stringify(preferences)
            });
            
            this.preferences = preferences;
            localStorage.setItem('news_preferences', JSON.stringify(preferences));
            
            StockScanner.showNotification('News preferences saved successfully', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newsPreferencesModal'));
            modal.hide();
            
            // Refresh news feed
            this.refreshNews();
            
        } catch (error) {
            console.error('Failed to save news preferences:', error);
            StockScanner.showNotification('Failed to save preferences: ' + error.message, 'error');
        }
    }
    
    async syncPortfolioStocks() {
        try {
            await StockScanner.apiCall('news/sync-portfolio/', {
                method: 'POST'
            });
            
            StockScanner.showNotification('Portfolio stocks synced successfully', 'success');
            this.refreshNews();
        } catch (error) {
            console.error('Failed to sync portfolio stocks:', error);
            StockScanner.showNotification('Failed to sync portfolio stocks', 'error');
        }
    }
    
    async loadAnalytics() {
        try {
            const analytics = await StockScanner.apiCall('news/analytics/');
            this.renderAnalytics(analytics);
        } catch (error) {
            console.error('Failed to load news analytics:', error);
            StockScanner.showNotification('Failed to load news analytics', 'error');
        }
    }
    
    renderAnalytics(analytics) {
        const container = document.getElementById('news-analytics-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="analytics-overview">
                <h6>News Consumption Analytics</h6>
                <div class="row">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Articles Read</label>
                            <span class="value">${analytics.articles_read || 0}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Articles Clicked</label>
                            <span class="value">${analytics.articles_clicked || 0}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Avg Relevance</label>
                            <span class="value">${(analytics.average_relevance || 0).toFixed(1)}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <label>Saved Articles</label>
                            <span class="value">${this.readLaterItems.size}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="category-breakdown">
                <h6>Reading by Category</h6>
                ${analytics.by_category ? Object.entries(analytics.by_category).map(([category, count]) => `
                    <div class="category-stat">
                        <span class="category-name">${category}</span>
                        <span class="category-count">${count} articles</span>
                    </div>
                `).join('') : '<p>No category data available</p>'}
            </div>
        `;
    }
    
    filterByCategory(category) {
        // Re-load feed with category filter
        this.loadPersonalizedFeed();
    }
    
    sortNews(sortBy) {
        const sortedNews = [...this.newsItems].sort((a, b) => {
            switch (sortBy) {
                case 'date':
                    return new Date(b.published_at) - new Date(a.published_at);
                case 'popularity':
                    return (b.popularity_score || 0) - (a.popularity_score || 0);
                case 'relevance':
                default:
                    return (b.relevance_score || 0) - (a.relevance_score || 0);
            }
        });
        
        this.newsItems = sortedNews;
        this.renderNewsFeed();
    }
    
    filterByTimeframe(timeframe) {
        const now = new Date();
        let cutoffDate;
        
        switch (timeframe) {
            case '24h':
                cutoffDate = new Date(now - 24 * 60 * 60 * 1000);
                break;
            case '3d':
                cutoffDate = new Date(now - 3 * 24 * 60 * 60 * 1000);
                break;
            case '1w':
                cutoffDate = new Date(now - 7 * 24 * 60 * 60 * 1000);
                break;
            case '1m':
                cutoffDate = new Date(now - 30 * 24 * 60 * 60 * 1000);
                break;
            default:
                cutoffDate = new Date(0);
        }
        
        this.newsItems = this.newsItems.filter(article => 
            new Date(article.published_at) >= cutoffDate
        );
        this.renderNewsFeed();
    }
    
    async loadTabContent(tabId) {
        this.currentTab = tabId.replace('#', '');
        
        switch (this.currentTab) {
            case 'portfolio-news':
                await this.loadPortfolioNews();
                break;
            case 'watchlist-news':
                await this.loadWatchlistNews();
                break;
            case 'trending-news':
                await this.loadTrendingNews();
                break;
            case 'read-later':
                this.loadReadLaterNews();
                break;
            default:
                await this.loadPersonalizedFeed();
        }
    }
    
    async loadPortfolioNews() {
        // Implementation for portfolio-specific news
        // This would call an API endpoint for portfolio-related news
    }
    
    async loadWatchlistNews() {
        // Implementation for watchlist-specific news
        // This would call an API endpoint for watchlist-related news
    }
    
    async loadTrendingNews() {
        // Implementation for trending news
        // This would call an API endpoint for trending news
    }
    
    loadReadLaterNews() {
        const savedArticles = this.newsItems.filter(article => 
            this.readLaterItems.has(article.id)
        );
        
        const container = document.getElementById('read-later-feed');
        if (!container) return;
        
        if (savedArticles.length === 0) {
            container.innerHTML = `
                <div class="empty-state text-center py-5">
                    <i class="fas fa-bookmark fa-3x mb-3"></i>
                    <h3>No Saved Articles</h3>
                    <p>Save articles to read them later</p>
                </div>
            `;
            return;
        }
        
        // Render saved articles (similar to main feed)
        container.innerHTML = savedArticles.map(article => `
            <article class="news-item saved" data-news-id="${article.id}">
                <!-- Similar structure to main news items -->
            </article>
        `).join('');
    }
    
    async markAsRead(newsId) {
        try {
            await StockScanner.apiCall('news/mark-read/', {
                method: 'POST',
                body: JSON.stringify({ news_id: newsId })
            });
        } catch (error) {
            console.error('Failed to mark news as read:', error);
        }
    }
    
    async markAsClicked(newsId) {
        try {
            await StockScanner.apiCall('news/mark-clicked/', {
                method: 'POST',
                body: JSON.stringify({ news_id: newsId })
            });
        } catch (error) {
            console.error('Failed to mark news as clicked:', error);
        }
    }
    
    toggleBookmark(newsId) {
        if (this.readLaterItems.has(newsId)) {
            this.readLaterItems.delete(newsId);
        } else {
            this.readLaterItems.add(newsId);
        }
        
        // Update the button text
        const button = document.querySelector(`[data-news-id="${newsId}"] .bookmark-btn`);
        if (button) {
            button.innerHTML = this.readLaterItems.has(newsId) ? 
                '<i class="fas fa-bookmark"></i> Saved' : 
                '<i class="fas fa-bookmark"></i> Save';
        }
        
        // Update the counter
        document.getElementById('read-later-count').textContent = this.readLaterItems.size;
        
        // Save to localStorage
        localStorage.setItem('read_later_items', JSON.stringify([...this.readLaterItems]));
    }
    
    shareArticle(newsId) {
        const article = this.newsItems.find(item => item.id === newsId);
        if (!article) return;
        
        if (navigator.share) {
            navigator.share({
                title: article.title,
                url: article.url,
                text: article.summary || article.content.substring(0, 200) + '...'
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(article.url);
            StockScanner.showNotification('Article URL copied to clipboard', 'success');
        }
    }
    
    viewArticle(newsId) {
        const article = this.newsItems.find(item => item.id === newsId);
        if (!article) return;
        
        // Mark as read and clicked
        this.markAsRead(newsId);
        this.markAsClicked(newsId);
        
        // Open in new tab
        window.open(article.url, '_blank', 'noopener,noreferrer');
    }
    
    refreshNews() {
        this.loadPersonalizedFeed();
    }
    
    autoRefreshNews() {
        // Only refresh if user is actively viewing the page
        if (!document.hidden) {
            this.loadPersonalizedFeed();
        }
    }
    
    loadMoreNews() {
        // Implementation for pagination
        // This would load additional news items
    }
    
    trackScrollBehavior() {
        // Track user reading behavior for analytics
        // This could be used to improve personalization
    }
    
    startAutoRefresh() {
        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.autoRefreshNews();
        }, 300000);
    }
    
    setupEventListeners() {
        // Load saved read later items
        const savedItems = localStorage.getItem('read_later_items');
        if (savedItems) {
            this.readLaterItems = new Set(JSON.parse(savedItems));
            document.getElementById('read-later-count').textContent = this.readLaterItems.size;
        }
    }
}

// Theme toggle and keyboard shortcuts
(function(){
  if (typeof window === 'undefined') return;

  const STORAGE_KEY = 'rts_theme';
  function applyTheme(theme){
    const html = document.documentElement;
    if (theme === 'dark') html.setAttribute('data-theme','dark');
    else html.removeAttribute('data-theme');
  }
  function initTheme(){
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') applyTheme(saved);
    else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) applyTheme('dark');
  }
  function toggleTheme(){
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const next = isDark ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }
  window.toggleTheme = toggleTheme;
  initTheme();

  // Common keyboard shortcuts
  let pendingG = false;
  function navigate(path){ try { window.location.href = path; } catch(e){} }
  function focusSearch(){
    const search = document.querySelector('input[type="search"], .search-input, #stock-symbol, #news-symbol');
    if (search) { search.focus(); search.select?.(); }
  }
  document.addEventListener('keydown', (e)=>{
    // Ignore when typing in inputs/textarea or when modifiers change intent
    const tag = (e.target && e.target.tagName || '').toLowerCase();
    const typing = tag === 'input' || tag === 'textarea' || e.isComposing;
    if (!e.ctrlKey && !e.metaKey && !e.altKey) {
      if (!typing && e.key.toLowerCase() === 'g') {
        pendingG = true;
        setTimeout(()=>{ pendingG = false; }, 800);
        return;
      }
      if (pendingG) {
        if (e.key.toLowerCase() === 'd') { e.preventDefault(); navigate('/dashboard/'); pendingG = false; return; }
        if (e.key.toLowerCase() === 's') { e.preventDefault(); navigate('/stock-screener/'); pendingG = false; return; }
        if (e.key.toLowerCase() === 'w') { e.preventDefault(); navigate('/watchlist/'); pendingG = false; return; }
        if (e.key.toLowerCase() === 'n') { e.preventDefault(); navigate('/stock-news/'); pendingG = false; return; }
      }
      if (!typing && e.key === '/') { e.preventDefault(); focusSearch(); return; }
      if (e.shiftKey && e.key === '?') { e.preventDefault(); navigate('/shortcuts/'); return; }
      if (!typing && (e.key.toLowerCase() === 'k' || e.key.toLowerCase() === 'j')) {
        // Basic list navigation (optional enhancement)
        const list = document.querySelector('.news-feed, #results-tbody');
        if (list) {
          const items = list.querySelectorAll('.news-article, tr');
          const active = list.querySelector('.active-item');
          let idx = Array.from(items).indexOf(active);
          idx = idx < 0 ? 0 : idx + (e.key.toLowerCase() === 'j' ? 1 : -1);
          idx = Math.max(0, Math.min(items.length-1, idx));
          items.forEach(el=>el.classList.remove('active-item'));
          const target = items[idx];
          target?.classList.add('active-item');
          target?.scrollIntoView({ block: 'nearest' });
        }
      }
    }
  });
})();

// Global instances
let portfolioManager, watchlistManager, newsManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers based on current page
    const path = window.location.pathname;
    
    if (path.includes('/portfolio/') || document.getElementById('portfolios-grid')) {
        portfolioManager = new PortfolioManager();
        window.portfolioManager = portfolioManager; // Make globally available
    }
    
    if (path.includes('/watchlist/') || document.getElementById('watchlists-container')) {
        watchlistManager = new WatchlistManager();
        window.watchlistManager = watchlistManager; // Make globally available
    }
    
    if (path.includes('/personalized-news/') || document.getElementById('for-you-feed')) {
        newsManager = new NewsManager();
        window.newsManager = newsManager; // Make globally available
    }
});

// Notification CSS (add to head if not already present)
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            max-width: 500px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        }
        
        .notification-info {
            background: #3b82f6;
            color: white;
        }
        
        .notification-success {
            background: #10b981;
            color: white;
        }
        
        .notification-warning {
            background: #f59e0b;
            color: white;
        }
        
        .notification-error {
            background: #ef4444;
            color: white;
        }
        
        .notification-content {
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: inherit;
            font-size: 18px;
            cursor: pointer;
            margin-left: 12px;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
}