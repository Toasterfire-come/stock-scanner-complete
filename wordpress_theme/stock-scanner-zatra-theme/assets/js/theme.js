/**
 * Stock Scanner Pro - Zatra Theme JavaScript
 * Handles all frontend interactions and data display
 */

const StockScannerTheme = {
    // Configuration
    config: {
        ajaxUrl: stockScannerAjax?.ajaxurl || '/wp-admin/admin-ajax.php',
        nonce: stockScannerAjax?.nonce || '',
        themeUrl: stockScannerAjax?.theme_url || '',
        refreshInterval: 30000, // 30 seconds
        chartUpdateInterval: 60000, // 1 minute
    },

    // Cache for data
    cache: new Map(),
    
    // Active intervals
    intervals: new Map(),

    // Initialize the theme
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAjax();
        this.startRealTimeUpdates();
        this.initializeCharts();
        this.initializeTooltips();
        this.initializeLazyLoading();
        
        console.log('Stock Scanner Theme initialized');
    },

    // Setup event listeners
    setupEventListeners() {
        // Mobile menu toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('.mobile-menu-toggle')) {
                this.toggleMobileMenu();
            }
        });

        // Stock search functionality
        const searchInputs = document.querySelectorAll('.stock-search-input');
        searchInputs.forEach(input => {
            input.addEventListener('input', this.debounce((e) => {
                this.handleStockSearch(e.target.value);
            }, 300));
        });

        // Watchlist actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-watchlist')) {
                const symbol = e.target.dataset.symbol;
                this.addToWatchlist(symbol);
            }
            
            if (e.target.matches('.remove-from-watchlist')) {
                const symbol = e.target.dataset.symbol;
                this.removeFromWatchlist(symbol);
            }
        });

        // Data refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-data')) {
                const dataType = e.target.dataset.type;
                this.refreshData(dataType);
            }
        });

        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tab-btn')) {
                this.switchTab(e.target);
            }
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.ajax-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
    },

    // Initialize components
    initializeComponents() {
        this.initializeDataTables();
        this.initializeChartContainers();
        this.initializeNotifications();
        this.initializeModals();
    },

    // Initialize data tables
    initializeDataTables() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            const tableType = table.dataset.type;
            this.loadTableData(table, tableType);
        });
    },

    // Initialize chart containers
    initializeChartContainers() {
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            const chartType = container.dataset.type;
            const symbol = container.dataset.symbol;
            const range = container.dataset.range || '1W';
            
            if (symbol) {
                this.loadChartData(container, symbol, range);
            }
        });
    },

    // Load table data with proper formatting
    async loadTableData(table, tableType) {
        const loadingIndicator = table.querySelector('.loading-indicator');
        const tableBody = table.querySelector('.table-body');
        const emptyState = table.querySelector('.empty-state');

        try {
            // Show loading state
            if (loadingIndicator) loadingIndicator.style.display = 'flex';
            if (tableBody) tableBody.style.display = 'none';
            if (emptyState) emptyState.style.display = 'none';

            let data;
            switch (tableType) {
                case 'watchlist':
                    data = await this.getFormattedWatchlistData();
                    break;
                case 'portfolio':
                    data = await this.getFormattedPortfolioData();
                    break;
                case 'market':
                    data = await this.getFormattedMarketData();
                    break;
                default:
                    throw new Error(`Unknown table type: ${tableType}`);
            }

            // Hide loading state
            if (loadingIndicator) loadingIndicator.style.display = 'none';

            if (data && data.length > 0) {
                this.populateTable(table, data, tableType);
                if (tableBody) tableBody.style.display = 'block';
            } else {
                if (emptyState) emptyState.style.display = 'flex';
            }

        } catch (error) {
            console.error(`Error loading ${tableType} data:`, error);
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (emptyState) {
                emptyState.style.display = 'flex';
                const emptyMessage = emptyState.querySelector('.empty-message');
                if (emptyMessage) {
                    emptyMessage.textContent = `Error loading ${tableType} data: ${error.message}`;
                }
            }
        }
    },

    // Populate table with formatted data
    populateTable(table, data, tableType) {
        const tableBody = table.querySelector('.table-body');
        if (!tableBody) return;

        let html = '';
        
        switch (tableType) {
            case 'watchlist':
                html = this.generateWatchlistRows(data);
                break;
            case 'portfolio':
                html = this.generatePortfolioRows(data.holdings || []);
                this.updatePortfolioSummary(data);
                break;
            case 'market':
                html = this.generateMarketRows(data.indices || []);
                this.updateMarketStats(data);
                break;
        }

        tableBody.innerHTML = html;
        
        // Update table metadata
        const rowCount = table.querySelector('.row-count');
        if (rowCount) {
            const count = Array.isArray(data) ? data.length : (data.holdings?.length || data.indices?.length || 0);
            rowCount.textContent = `${count} items`;
        }
    },

    // Generate watchlist table rows
    generateWatchlistRows(watchlistData) {
        return watchlistData.map(stock => `
            <div class="table-row" data-symbol="${stock.symbol}">
                <div class="table-cell symbol-cell">
                    <strong>${stock.symbol}</strong>
                    <small>${stock.name}</small>
                </div>
                <div class="table-cell price-cell">${stock.price}</div>
                <div class="table-cell change-cell">${stock.change}</div>
                <div class="table-cell percent-cell">${stock.change_percent}</div>
                <div class="table-cell volume-cell">${stock.volume}</div>
                <div class="table-cell actions-cell">
                    <button class="action-btn view-chart" data-symbol="${stock.symbol}" title="View Chart">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button class="action-btn remove-from-watchlist" data-symbol="${stock.symbol}" title="Remove">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },

    // Generate portfolio table rows
    generatePortfolioRows(holdings) {
        return holdings.map(holding => `
            <div class="table-row" data-symbol="${holding.symbol}">
                <div class="table-cell symbol-cell">
                    <strong>${holding.symbol}</strong>
                    <small>${holding.name}</small>
                </div>
                <div class="table-cell shares-cell">${holding.shares}</div>
                <div class="table-cell cost-cell">${holding.avg_cost}</div>
                <div class="table-cell price-cell">${holding.current_price}</div>
                <div class="table-cell value-cell">${holding.market_value}</div>
                <div class="table-cell gain-cell">${holding.gain_loss}</div>
                <div class="table-cell percent-cell">${holding.gain_loss_percent}</div>
                <div class="table-cell actions-cell">
                    <button class="action-btn view-chart" data-symbol="${holding.symbol}" title="View Chart">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button class="action-btn edit-holding" data-symbol="${holding.symbol}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },

    // Generate market indices rows
    generateMarketRows(indices) {
        return indices.map(index => `
            <div class="table-row" data-symbol="${index.symbol}">
                <div class="table-cell symbol-cell">
                    <strong>${index.symbol}</strong>
                    <small>${index.name}</small>
                </div>
                <div class="table-cell price-cell">${index.price}</div>
                <div class="table-cell change-cell">${index.change}</div>
                <div class="table-cell percent-cell">${index.change_percent}</div>
                <div class="table-cell actions-cell">
                    <button class="action-btn view-chart" data-symbol="${index.symbol}" title="View Chart">
                        <i class="fas fa-chart-line"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },

    // Update portfolio summary
    updatePortfolioSummary(portfolioData) {
        const summaryElements = {
            'total-value': portfolioData.total_value,
            'total-cost': portfolioData.total_cost,
            'total-gain-loss': portfolioData.total_gain_loss,
            'total-gain-loss-percent': portfolioData.total_gain_loss_percent,
            'last-updated': portfolioData.last_updated
        };

        Object.entries(summaryElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = value;
                
                // Add color coding for gain/loss
                if (id.includes('gain-loss') && portfolioData.raw_total_gain_loss !== undefined) {
                    element.className = portfolioData.raw_total_gain_loss >= 0 ? 'positive' : 'negative';
                }
            }
        });
    },

    // Update market statistics
    updateMarketStats(marketData) {
        const statsElements = {
            'advancing-stocks': marketData.advancing,
            'declining-stocks': marketData.declining,
            'unchanged-stocks': marketData.unchanged,
            'market-status': marketData.market_status,
            'last-updated': marketData.last_updated
        };

        Object.entries(statsElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    },

    // Load chart data with proper formatting
    async loadChartData(container, symbol, range = '1W') {
        try {
            const canvas = container.querySelector('canvas');
            if (!canvas) return;

            // Use the advanced charts system if available
            if (window.AdvancedCharts) {
                await window.AdvancedCharts.createAdvancedStockChart(canvas.id, symbol, {
                    timeRange: range,
                    type: container.dataset.chartType || 'line'
                });
                return;
            }

            // Fallback to basic chart
            const data = await this.getFormattedHistoricalData(symbol, range);
            this.createBasicChart(canvas, data);

        } catch (error) {
            console.error(`Error loading chart for ${symbol}:`, error);
            this.showChartError(container, error.message);
        }
    },

    // Create basic chart fallback
    createBasicChart(canvas, data) {
        const ctx = canvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.symbol,
                    data: data.prices,
                    borderColor: data.trend >= 0 ? '#10b981' : '#ef4444',
                    backgroundColor: data.trend >= 0 ? '#10b98120' : '#ef444420',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: (value) => '$' + value.toFixed(2)
                        }
                    }
                }
            }
        });
    },

    // Show chart error
    showChartError(container, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chart-error';
        errorDiv.innerHTML = `
            <div class="error-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="error-message">Error loading chart: ${message}</div>
            <button class="retry-btn" onclick="location.reload()">Retry</button>
        `;
        
        container.innerHTML = '';
        container.appendChild(errorDiv);
    },

    // API Methods for formatted data
    async getFormattedStockData(symbol) {
        const cacheKey = `stock_${symbol}`;
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 60000) { // 1 minute cache
                return cached.data;
            }
        }

        const response = await this.makeAjaxRequest('get_formatted_stock_data', { symbol });
        
        if (response.success) {
            this.cache.set(cacheKey, {
                data: response.data,
                timestamp: Date.now()
            });
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch stock data');
    },

    async getFormattedHistoricalData(symbol, range = '1W') {
        const cacheKey = `historical_${symbol}_${range}`;
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 300000) { // 5 minute cache
                return cached.data;
            }
        }

        const response = await this.makeAjaxRequest('get_formatted_historical_data', { symbol, range });
        
        if (response.success) {
            this.cache.set(cacheKey, {
                data: response.data,
                timestamp: Date.now()
            });
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch historical data');
    },

    async getFormattedPortfolioData() {
        const response = await this.makeAjaxRequest('get_formatted_portfolio_data');
        
        if (response.success) {
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch portfolio data');
    },

    async getFormattedMarketData() {
        const cacheKey = 'market_data';
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 60000) { // 1 minute cache
                return cached.data;
            }
        }

        const response = await this.makeAjaxRequest('get_formatted_market_data');
        
        if (response.success) {
            this.cache.set(cacheKey, {
                data: response.data,
                timestamp: Date.now()
            });
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch market data');
    },

    async getFormattedWatchlistData() {
        const response = await this.makeAjaxRequest('get_formatted_watchlist_data');
        
        if (response.success) {
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch watchlist data');
    },

    async getFormattedNewsData(category = 'general', limit = 20) {
        const response = await this.makeAjaxRequest('get_formatted_news_data', { category, limit });
        
        if (response.success) {
            return response.data;
        }
        
        throw new Error(response.data || 'Failed to fetch news data');
    },

    // AJAX helper method
    async makeAjaxRequest(action, data = {}) {
        const formData = new FormData();
        formData.append('action', action);
        formData.append('nonce', this.config.nonce);
        
        Object.entries(data).forEach(([key, value]) => {
            formData.append(key, value);
        });

        const response = await fetch(this.config.ajaxUrl, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    // Stock search functionality
    async handleStockSearch(query) {
        if (query.length < 1) {
            this.hideSuggestions();
            return;
        }

        try {
            // For now, show basic suggestions
            // In a real implementation, this would search the backend
            const suggestions = this.generateStockSuggestions(query);
            this.showSuggestions(suggestions);
        } catch (error) {
            console.error('Error searching stocks:', error);
        }
    },

    // Generate stock suggestions (placeholder)
    generateStockSuggestions(query) {
        const commonStocks = [
            { symbol: 'AAPL', name: 'Apple Inc.' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.' },
            { symbol: 'MSFT', name: 'Microsoft Corporation' },
            { symbol: 'AMZN', name: 'Amazon.com Inc.' },
            { symbol: 'TSLA', name: 'Tesla Inc.' },
            { symbol: 'META', name: 'Meta Platforms Inc.' },
            { symbol: 'NVDA', name: 'NVIDIA Corporation' },
            { symbol: 'NFLX', name: 'Netflix Inc.' }
        ];

        return commonStocks.filter(stock => 
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);
    },

    // Show search suggestions
    showSuggestions(suggestions) {
        const suggestionsList = document.querySelector('.search-suggestions');
        if (!suggestionsList) return;

        if (suggestions.length === 0) {
            suggestionsList.style.display = 'none';
            return;
        }

        suggestionsList.innerHTML = suggestions.map(stock => `
            <div class="suggestion-item" data-symbol="${stock.symbol}">
                <strong>${stock.symbol}</strong>
                <span>${stock.name}</span>
            </div>
        `).join('');

        suggestionsList.style.display = 'block';

        // Add click handlers
        suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const symbol = item.dataset.symbol;
                this.selectStock(symbol);
                this.hideSuggestions();
            });
        });
    },

    // Hide search suggestions
    hideSuggestions() {
        const suggestionsList = document.querySelector('.search-suggestions');
        if (suggestionsList) {
            suggestionsList.style.display = 'none';
        }
    },

    // Select stock from suggestions
    selectStock(symbol) {
        const searchInput = document.querySelector('.stock-search-input');
        if (searchInput) {
            searchInput.value = symbol;
            // Trigger search or navigation
            this.searchStock(symbol);
        }
    },

    // Search for specific stock
    async searchStock(symbol) {
        try {
            const stockData = await this.getFormattedStockData(symbol);
            this.displayStockData(stockData);
        } catch (error) {
            console.error('Error fetching stock data:', error);
            this.showNotification('Error fetching stock data: ' + error.message, 'error');
        }
    },

    // Display stock data
    displayStockData(stockData) {
        const stockDisplay = document.querySelector('.stock-display');
        if (!stockDisplay) return;

        stockDisplay.innerHTML = `
            <div class="stock-header">
                <h2>${stockData.symbol}</h2>
                <p>${stockData.name}</p>
            </div>
            <div class="stock-metrics">
                <div class="metric">
                    <label>Price</label>
                    <value>${stockData.price}</value>
                </div>
                <div class="metric">
                    <label>Change</label>
                    <value>${stockData.change_percent}</value>
                </div>
                <div class="metric">
                    <label>Volume</label>
                    <value>${stockData.volume}</value>
                </div>
                <div class="metric">
                    <label>Market Cap</label>
                    <value>${stockData.market_cap}</value>
                </div>
            </div>
        `;

        stockDisplay.style.display = 'block';
    },

    // Watchlist management
    async addToWatchlist(symbol) {
        try {
            const response = await fetch('/wp-json/stock-scanner/v1/watchlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': this.config.nonce
                },
                body: JSON.stringify({ symbol })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${symbol} added to watchlist`, 'success');
                this.refreshWatchlist();
            } else {
                throw new Error(result.message || 'Failed to add to watchlist');
            }
        } catch (error) {
            console.error('Error adding to watchlist:', error);
            this.showNotification('Error adding to watchlist: ' + error.message, 'error');
        }
    },

    async removeFromWatchlist(symbol) {
        try {
            const response = await fetch(`/wp-json/stock-scanner/v1/watchlist?symbol=${symbol}`, {
                method: 'DELETE',
                headers: {
                    'X-WP-Nonce': this.config.nonce
                }
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${symbol} removed from watchlist`, 'success');
                this.refreshWatchlist();
            } else {
                throw new Error(result.message || 'Failed to remove from watchlist');
            }
        } catch (error) {
            console.error('Error removing from watchlist:', error);
            this.showNotification('Error removing from watchlist: ' + error.message, 'error');
        }
    },

    // Refresh watchlist data
    async refreshWatchlist() {
        const watchlistTable = document.querySelector('.data-table[data-type="watchlist"]');
        if (watchlistTable) {
            await this.loadTableData(watchlistTable, 'watchlist');
        }
    },

    // Refresh data by type
    async refreshData(dataType) {
        const tables = document.querySelectorAll(`.data-table[data-type="${dataType}"]`);
        tables.forEach(table => {
            this.loadTableData(table, dataType);
        });

        const charts = document.querySelectorAll(`.chart-container[data-type="${dataType}"]`);
        charts.forEach(container => {
            const symbol = container.dataset.symbol;
            const range = container.dataset.range || '1W';
            if (symbol) {
                this.loadChartData(container, symbol, range);
            }
        });

        this.showNotification(`${dataType} data refreshed`, 'success');
    },

    // Real-time updates
    startRealTimeUpdates() {
        // Update market data every 30 seconds
        this.intervals.set('market', setInterval(() => {
            this.refreshData('market');
        }, this.config.refreshInterval));

        // Update charts every minute
        this.intervals.set('charts', setInterval(() => {
            const chartContainers = document.querySelectorAll('.chart-container[data-symbol]');
            chartContainers.forEach(container => {
                const symbol = container.dataset.symbol;
                const range = container.dataset.range || '1W';
                this.loadChartData(container, symbol, range);
            });
        }, this.config.chartUpdateInterval));
    },

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Mobile menu toggle
    toggleMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.toggle('active');
        }
    },

    // Tab switching
    switchTab(tabButton) {
        const tabGroup = tabButton.closest('.tab-group');
        if (!tabGroup) return;

        // Update tab buttons
        tabGroup.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        tabButton.classList.add('active');

        // Update tab content
        const targetTab = tabButton.dataset.tab;
        const tabContent = tabGroup.querySelector('.tab-content');
        if (tabContent) {
            tabContent.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            const targetPane = tabContent.querySelector(`[data-tab="${targetTab}"]`);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        }
    },

    // Initialize other components
    setupAjax() {
        // Set up CSRF token for all AJAX requests
        const token = document.querySelector('meta[name="csrf-token"]');
        if (token) {
            this.config.csrfToken = token.getAttribute('content');
        }
    },

    initializeCharts() {
        // Initialize Chart.js defaults
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            Chart.defaults.responsive = true;
            Chart.defaults.maintainAspectRatio = false;
        }
    },

    initializeTooltips() {
        // Initialize tooltips for elements with title attributes
        const tooltipElements = document.querySelectorAll('[title]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    },

    initializeLazyLoading() {
        // Initialize lazy loading for images and charts
        if ('IntersectionObserver' in window) {
            const lazyElements = document.querySelectorAll('.lazy-load');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadLazyElement(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            });

            lazyElements.forEach(element => observer.observe(element));
        }
    },

    initializeNotifications() {
        // Set up notification container
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    },

    initializeModals() {
        // Set up modal functionality
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-trigger')) {
                const modalId = e.target.dataset.modal;
                this.openModal(modalId);
            }
            
            if (e.target.matches('.modal-close') || e.target.matches('.modal-backdrop')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });
    },

    // Notification system
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        container.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    },

    // Tooltip methods
    showTooltip(event) {
        const element = event.target;
        const title = element.getAttribute('title');
        if (!title) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = title;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';

        element.removeAttribute('title');
        element.dataset.originalTitle = title;
    },

    hideTooltip(event) {
        const element = event.target;
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }

        if (element.dataset.originalTitle) {
            element.setAttribute('title', element.dataset.originalTitle);
            delete element.dataset.originalTitle;
        }
    },

    // Lazy loading
    loadLazyElement(element) {
        if (element.dataset.src) {
            element.src = element.dataset.src;
            element.classList.remove('lazy-load');
        }
        
        if (element.classList.contains('lazy-chart')) {
            const symbol = element.dataset.symbol;
            const range = element.dataset.range;
            if (symbol) {
                this.loadChartData(element.closest('.chart-container'), symbol, range);
            }
        }
    },

    // Modal methods
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    },

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }
    },

    // Form handling
    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const action = form.dataset.action;
        
        if (!action) {
            console.error('Form missing data-action attribute');
            return;
        }

        try {
            const response = await this.makeAjaxRequest(action, Object.fromEntries(formData));
            
            if (response.success) {
                this.showNotification('Form submitted successfully', 'success');
                form.reset();
            } else {
                throw new Error(response.data || 'Form submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Error submitting form: ' + error.message, 'error');
        }
    },

    // Cleanup method
    destroy() {
        // Clear all intervals
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals.clear();
        
        // Clear cache
        this.cache.clear();
        
        console.log('Stock Scanner Theme destroyed');
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    StockScannerTheme.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    StockScannerTheme.destroy();
});

// Export for global access
window.StockScannerTheme = StockScannerTheme;