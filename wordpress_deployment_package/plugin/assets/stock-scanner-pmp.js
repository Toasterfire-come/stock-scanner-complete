/**
 * Stock Scanner PMP Integration JavaScript
 * Handles stock data loading with membership protection
 */

jQuery(document).ready(function($) {
    'use strict';
    
    // Configuration from WordPress
    const config = window.stockScannerPMP || {};
    const djangoAPI = config.django_api_url || '';
    const userLevel = config.user_level || 0;
    const userFeatures = config.features || [];
    
    /**
     * Stock data loader with membership protection
     */
    class StockDataLoader {
        constructor() {
            this.cache = new Map();
            this.rateLimiter = new Map();
            this.init();
        }
        
        init() {
            this.bindEvents();
            this.loadStockData();
            this.setupAutoRefresh();
        }
        
        bindEvents() {
            // Handle protected stock data elements
            $('.stock-data').each((index, element) => {
                this.loadSingleStock($(element));
            });
            
            // Handle tool buttons in member dashboard
            $('.tool-button').on('click', (e) => {
                e.preventDefault();
                this.handleToolClick($(e.target));
            });
            
            // Handle stock search with membership limits
            $('#stock-search-form').on('submit', (e) => {
                e.preventDefault();
                this.handleStockSearch($(e.target));
            });
            
            // Handle upgrade buttons
            $('.upgrade-button').on('click', (e) => {
                this.trackUpgradeClick($(e.target));
            });
        }
        
        /**
         * Load stock data for protected elements
         */
        loadStockData() {
            $('.stock-data').each((index, element) => {
                const $element = $(element);
                const ticker = $element.data('ticker');
                const format = $element.data('format') || 'basic';
                
                if (ticker) {
                    this.fetchStockData(ticker, format)
                        .then(data => this.renderStockData($element, data))
                        .catch(error => this.renderError($element, error));
                }
            });
        }
        
        /**
         * Load single stock with caching
         */
        async loadSingleStock($element) {
            const ticker = $element.data('ticker');
            const format = $element.data('format') || 'basic';
            
            if (!ticker) return;
            
            try {
                const data = await this.fetchStockData(ticker, format);
                this.renderStockData($element, data);
            } catch (error) {
                this.renderError($element, error);
            }
        }
        
        /**
         * Fetch stock data from Django API
         */
        async fetchStockData(ticker, format = 'basic') {
            // Check cache first
            const cacheKey = `${ticker}_${format}`;
            if (this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                if (Date.now() - cached.timestamp < 120000) { // 2 minutes
                    return cached.data;
                }
            }
            
            // Check rate limits
            if (this.isRateLimited()) {
                throw new Error('Rate limit exceeded. Please wait before making more requests.');
            }
            
            // Determine API endpoint based on user level
            const endpoint = this.getAPIEndpoint();
            const url = `${djangoAPI}${endpoint}${ticker}/`;
            
            // Add user token for authentication
            const token = this.getUserToken();
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Token': token
                }
            });
            
            if (!response.ok) {
                if (response.status === 403) {
                    throw new Error('upgrade_required');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                if (data.subscription && !data.subscription.has_access) {
                    throw new Error('upgrade_required');
                }
                throw new Error(data.error || 'Unknown error');
            }
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
            
            // Update rate limiter
            this.updateRateLimit();
            
            return data;
        }
        
        /**
         * Get appropriate API endpoint based on user level
         */
        getAPIEndpoint() {
            if (userLevel >= 1) {
                return 'api/protected/stocks/';
            }
            return 'api/stocks/';
        }
        
        /**
         * Get user token for API authentication
         */
        getUserToken() {
            // This would normally be generated server-side
            return btoa(`${userLevel}:${Date.now()}`);
        }
        
        /**
         * Check if user is rate limited
         */
        isRateLimited() {
            const now = Date.now();
            const userLimits = this.getUserLimits();
            
            if (userLimits.api_calls_per_hour === -1) {
                return false; // Unlimited
            }
            
            // Clean old entries
            this.rateLimiter.forEach((timestamp, key) => {
                if (now - timestamp > 3600000) { // 1 hour
                    this.rateLimiter.delete(key);
                }
            });
            
            return this.rateLimiter.size >= userLimits.api_calls_per_hour;
        }
        
        /**
         * Update rate limiter
         */
        updateRateLimit() {
            this.rateLimiter.set(Date.now(), Date.now());
        }
        
        /**
         * Get user limits based on membership level
         */
        getUserLimits() {
            const limits = {
                0: { stock_limit: 10, api_calls_per_hour: 20 },
                1: { stock_limit: 50, api_calls_per_hour: 100 },
                2: { stock_limit: 200, api_calls_per_hour: 500 },
                3: { stock_limit: -1, api_calls_per_hour: -1 }
            };
            
            return limits[userLevel] || limits[0];
        }
        
        /**
         * Render stock data in element
         */
        renderStockData($element, data) {
            const stockData = data.data;
            const subscription = data.subscription || {};
            
            const changeClass = stockData.price_change_today >= 0 ? 'positive' : 'negative';
            const changeSymbol = stockData.price_change_today >= 0 ? '▲' : '▼';
            
            let html = `
                <div class="stock-display ${changeClass}">
                    <div class="stock-header">
                        <span class="ticker">${stockData.ticker}</span>
                        <span class="company">${stockData.company_name}</span>
                    </div>
                    <div class="stock-price">
                        <span class="price">$${parseFloat(stockData.current_price).toFixed(2)}</span>
                        <span class="change">
                            ${changeSymbol} ${Math.abs(stockData.price_change_today).toFixed(2)}
                            (${stockData.price_change_percent}%)
                        </span>
                    </div>
            `;
            
            // Add additional data based on subscription level
            if (subscription.level !== 'free') {
                html += `
                    <div class="stock-details">
                        <div class="detail-item">
                            <span class="label">Volume:</span>
                            <span class="value">${parseInt(stockData.volume_today).toLocaleString()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Market Cap:</span>
                            <span class="value">$${this.formatMarketCap(stockData.market_cap)}</span>
                        </div>
                `;
                
                // Premium features
                if (subscription.level === 'premium' || subscription.level === 'pro') {
                    html += `
                        <div class="detail-item">
                            <span class="label">DVAV:</span>
                            <span class="value">${stockData.dvav}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Rating:</span>
                            <span class="value rating-${stockData.technical_rating.toLowerCase()}">${stockData.technical_rating}</span>
                        </div>
                    `;
                }
                
                html += '</div>';
            }
            
            html += `
                    <div class="stock-footer">
                        <span class="last-update">Updated: ${new Date(stockData.last_update).toLocaleTimeString()}</span>
                        <span class="membership-badge">${subscription.level || 'free'}</span>
                    </div>
                </div>
            `;
            
            $element.html(html);
        }
        
        /**
         * Render error message
         */
        renderError($element, error) {
            let html;
            
            if (error.message === 'upgrade_required') {
                html = `
                    <div class="stock-upgrade-notice">
                        <div class="upgrade-icon">🔒</div>
                        <div class="upgrade-content">
                            <h4>Membership Required</h4>
                            <p>Upgrade your membership to access real-time stock data.</p>
                            <a href="/membership-levels/" class="upgrade-button">Upgrade Now</a>
                        </div>
                    </div>
                `;
            } else {
                html = `
                    <div class="stock-error">
                        <span class="error-icon">⚠️</span>
                        <span class="error-message">${error.message}</span>
                    </div>
                `;
            }
            
            $element.html(html);
        }
        
        /**
         * Format market cap for display
         */
        formatMarketCap(marketCap) {
            if (marketCap >= 1000000000000) {
                return (marketCap / 1000000000000).toFixed(1) + 'T';
            } else if (marketCap >= 1000000000) {
                return (marketCap / 1000000000).toFixed(1) + 'B';
            } else if (marketCap >= 1000000) {
                return (marketCap / 1000000).toFixed(1) + 'M';
            }
            return marketCap.toString();
        }
        
        /**
         * Handle tool button clicks in member dashboard
         */
        handleToolClick($button) {
            const tool = $button.data('tool');
            
            // Check if user has access to this tool
            if (!this.hasFeatureAccess(tool)) {
                this.showUpgradeModal(tool);
                return;
            }
            
            // Handle different tools
            switch (tool) {
                case 'search':
                    this.openStockSearch();
                    break;
                case 'watchlist':
                    this.openWatchlist();
                    break;
                case 'alerts':
                    this.openAlerts();
                    break;
                case 'portfolio':
                    this.openPortfolio();
                    break;
            }
        }
        
        /**
         * Check if user has access to a feature
         */
        hasFeatureAccess(feature) {
            const featureMap = {
                'search': 'basic_prices',
                'watchlist': 'basic_prices',
                'alerts': 'alerts',
                'portfolio': 'portfolio_tracking'
            };
            
            const requiredFeature = featureMap[feature];
            return userFeatures.includes(requiredFeature);
        }
        
        /**
         * Show upgrade modal
         */
        showUpgradeModal(feature) {
            const modal = `
                <div class="stock-scanner-modal">
                    <div class="modal-content">
                        <h3>Upgrade Required</h3>
                        <p>The ${feature} feature requires a higher membership level.</p>
                        <div class="modal-buttons">
                            <a href="/membership-levels/" class="upgrade-button">View Plans</a>
                            <button class="close-modal">Close</button>
                        </div>
                    </div>
                </div>
            `;
            
            $('body').append(modal);
            
            $('.close-modal, .stock-scanner-modal').on('click', function(e) {
                if (e.target === this) {
                    $('.stock-scanner-modal').remove();
                }
            });
        }
        
        /**
         * Handle stock search with membership limits
         */
        handleStockSearch($form) {
            const query = $form.find('input[name="q"]').val();
            const userLimits = this.getUserLimits();
            
            // Check search limits
            if (this.searchCount >= userLimits.stock_limit && userLimits.stock_limit !== -1) {
                this.showUpgradeModal('search limit exceeded');
                return;
            }
            
            // Perform search
            this.performSearch(query);
        }
        
        /**
         * Perform stock search
         */
        async performSearch(query) {
            try {
                const url = `${djangoAPI}api/stocks/search/?q=${encodeURIComponent(query)}`;
                const token = this.getUserToken();
                
                const response = await fetch(url, {
                    headers: {
                        'X-WP-Token': token
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.renderSearchResults(data.data);
                    this.searchCount = (this.searchCount || 0) + 1;
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        }
        
        /**
         * Render search results
         */
        renderSearchResults(results) {
            const $container = $('#search-results');
            
            if (results.length === 0) {
                $container.html('<p>No stocks found matching your search.</p>');
                return;
            }
            
            let html = '<div class="search-results-grid">';
            
            results.forEach(stock => {
                html += `
                    <div class="search-result-item">
                        <div class="stock-info">
                            <span class="ticker">${stock.ticker}</span>
                            <span class="company">${stock.company_name}</span>
                        </div>
                        <div class="stock-price">
                            $${parseFloat(stock.current_price).toFixed(2)}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            $container.html(html);
        }
        
        /**
         * Setup auto-refresh for stock data
         */
        setupAutoRefresh() {
            // Refresh based on membership level
            const refreshInterval = this.getRefreshInterval();
            
            if (refreshInterval > 0) {
                setInterval(() => {
                    this.loadStockData();
                }, refreshInterval);
            }
        }
        
        /**
         * Get refresh interval based on membership
         */
        getRefreshInterval() {
            const intervals = {
                0: 300000, // Free: 5 minutes
                1: 120000, // Basic: 2 minutes
                2: 60000,  // Premium: 1 minute
                3: 30000   // Pro: 30 seconds
            };
            
            return intervals[userLevel] || intervals[0];
        }
        
        /**
         * Track upgrade button clicks for analytics
         */
        trackUpgradeClick($button) {
            // Send analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'upgrade_click', {
                    'event_category': 'membership',
                    'event_label': 'stock_scanner',
                    'current_level': userLevel
                });
            }
        }
        
        // Open different tools (placeholder functions)
        openStockSearch() { console.log('Opening stock search...'); }
        openWatchlist() { console.log('Opening watchlist...'); }
        openAlerts() { console.log('Opening alerts...'); }
        openPortfolio() { console.log('Opening portfolio...'); }
    }
    
    // Initialize the stock data loader
    const stockLoader = new StockDataLoader();
    
    // Make it globally available
    window.stockScannerLoader = stockLoader;
    
    // Handle dynamic content loading
    $(document).on('DOMNodeInserted', function(e) {
        const $target = $(e.target);
        if ($target.hasClass('stock-data') && !$target.data('loaded')) {
            $target.data('loaded', true);
            stockLoader.loadSingleStock($target);
        }
    });
});