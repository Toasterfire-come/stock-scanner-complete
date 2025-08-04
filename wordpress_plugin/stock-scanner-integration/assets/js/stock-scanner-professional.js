/**
 * Stock Scanner Professional - Main JavaScript
 * Version: 3.0.0
 * 
 * Comprehensive functionality for professional stock scanning with:
 * - Real-time stock data updates
 * - Professional membership management
 * - Interactive widgets and charts
 * - WordPress admin console integration
 */

(function($) {
    'use strict';

    /**
     * Main Stock Scanner Professional Class
     */
    window.StockScannerPro = {
        
        // Configuration
        config: {
            updateInterval: 30000, // 30 seconds
            maxRetries: 3,
            retryDelay: 2000,
            animationDuration: 300,
            chartColors: {
                positive: '#00a32a',
                negative: '#d63638',
                neutral: '#646970',
                background: '#f0f0f1'
            }
        },
        
        // State management
        state: {
            activeWidgets: new Map(),
            updateTimers: new Map(),
            membershipLevel: 0,
            apiCallsToday: 0,
            apiLimit: 15
        },
        
        // Cache for API responses
        cache: new Map(),
        
        /**
         * Initialize the plugin
         */
        init() {
            this.loadUserData();
            this.initializeWidgets();
            this.bindEvents();
            this.startPeriodicUpdates();
            this.initializeCharts();
            this.setupMembershipComponents();
            
            console.log('Stock Scanner Professional initialized');
        },
        
        /**
         * Load user membership data
         */
        async loadUserData() {
            if (!stockScannerPro.isLoggedIn) {
                return;
            }
            
            try {
                const response = await this.apiCall('get_user_data');
                if (response.success) {
                    this.state.membershipLevel = response.data.membership_level || 0;
                    this.state.apiCallsToday = response.data.api_calls_today || 0;
                    this.state.apiLimit = response.data.api_limit || 15;
                    
                    this.updateMembershipDisplay();
                }
            } catch (error) {
                console.error('Failed to load user data:', error);
            }
        },
        
        /**
         * Initialize all stock widgets on the page
         */
        initializeWidgets() {
            $('.stock-scanner-widget').each((index, element) => {
                this.initializeWidget($(element));
            });
        },
        
        /**
         * Initialize individual stock widget
         */
        initializeWidget($widget) {
            const symbol = $widget.data('symbol');
            if (!symbol) {
                console.warn('Stock widget missing symbol');
                return;
            }
            
            // Register widget
            this.state.activeWidgets.set(symbol, {
                $element: $widget,
                lastUpdate: null,
                retryCount: 0
            });
            
            // Load initial data
            this.updateStockData(symbol);
            
            // Setup refresh button
            $widget.find('.stock-widget-refresh').on('click', () => {
                this.refreshStock(symbol);
            });
        },
        
        /**
         * Bind global events
         */
        bindEvents() {
            // Membership plan selection
            $(document).on('click', '.membership-plan-button', (e) => {
                this.handleMembershipUpgrade($(e.currentTarget));
            });
            
            // Stock search
            $(document).on('submit', '.stock-search-form', (e) => {
                e.preventDefault();
                this.handleStockSearch($(e.currentTarget));
            });
            
            // Watchlist management
            $(document).on('click', '.add-to-watchlist', (e) => {
                e.preventDefault();
                this.addToWatchlist($(e.currentTarget).data('symbol'));
            });
            
            $(document).on('click', '.remove-from-watchlist', (e) => {
                e.preventDefault();
                this.removeFromWatchlist($(e.currentTarget).data('symbol'));
            });
            
            // Real-time toggle
            $(document).on('change', '.realtime-toggle', (e) => {
                this.toggleRealTimeUpdates($(e.currentTarget).is(':checked'));
            });
            
            // Window visibility change
            $(document).on('visibilitychange', () => {
                if (document.hidden) {
                    this.pauseUpdates();
                } else {
                    this.resumeUpdates();
                }
            });
        },
        
        /**
         * Update stock data for a specific symbol
         */
        async updateStockData(symbol) {
            const widget = this.state.activeWidgets.get(symbol);
            if (!widget) {
                return;
            }
            
            const $widget = widget.$element;
            
            try {
                // Check cache first
                const cached = this.getFromCache(symbol);
                if (cached && Date.now() - cached.timestamp < 60000) { // 1 minute cache
                    this.displayStockData(symbol, cached.data);
                    return;
                }
                
                // Show loading state
                this.setWidgetLoading($widget, true);
                
                // Check API limits
                if (!this.canMakeApiCall()) {
                    this.showUpgradePrompt($widget);
                    return;
                }
                
                // Make API call
                const response = await this.apiCall('get_stock_data', { symbol });
                
                if (response.success) {
                    this.displayStockData(symbol, response.data);
                    this.addToCache(symbol, response.data);
                    this.incrementApiCalls();
                    widget.retryCount = 0;
                } else {
                    throw new Error(response.data?.message || 'Failed to fetch stock data');
                }
                
            } catch (error) {
                console.error(`Error updating stock data for ${symbol}:`, error);
                this.handleStockDataError(symbol, error);
            } finally {
                this.setWidgetLoading($widget, false);
            }
        },
        
        /**
         * Display stock data in widget
         */
        displayStockData(symbol, data) {
            const widget = this.state.activeWidgets.get(symbol);
            if (!widget) {
                return;
            }
            
            const $widget = widget.$element;
            
            // Update price
            const $currentPrice = $widget.find('.stock-price-current');
            $currentPrice.text(this.formatPrice(data.price));
            
            // Update change
            const $change = $widget.find('.stock-price-change');
            const changeValue = parseFloat(data.change);
            const changePercent = parseFloat(data.change_percent);
            
            $change.removeClass('positive negative');
            $change.addClass(changeValue >= 0 ? 'positive' : 'negative');
            $change.text(`${changeValue >= 0 ? '+' : ''}${changeValue.toFixed(2)} (${changePercent.toFixed(2)}%)`);
            
            // Update details
            this.updateStockDetails($widget, data);
            
            // Update chart if present
            if ($widget.find('.stock-chart').length > 0) {
                this.updateStockChart(symbol, data);
            }
            
            // Update timestamp
            widget.lastUpdate = Date.now();
            
            // Add animation
            $widget.addClass('updated');
            setTimeout(() => {
                $widget.removeClass('updated');
            }, this.config.animationDuration);
        },
        
        /**
         * Update stock details section
         */
        updateStockDetails($widget, data) {
            const details = [
                { label: 'Volume', value: this.formatNumber(data.volume) },
                { label: 'Market Cap', value: this.formatCurrency(data.market_cap) },
                { label: 'P/E Ratio', value: data.pe_ratio || 'N/A' },
                { label: '52W High', value: this.formatPrice(data.week_52_high) },
                { label: '52W Low', value: this.formatPrice(data.week_52_low) },
                { label: 'Avg Volume', value: this.formatNumber(data.avg_volume) }
            ];
            
            const $details = $widget.find('.stock-widget-details');
            $details.empty();
            
            details.forEach(detail => {
                if (detail.value && detail.value !== 'N/A' && detail.value !== '0') {
                    $details.append(`
                        <div class="stock-detail-item">
                            <span class="stock-detail-label">${detail.label}:</span>
                            <span class="stock-detail-value">${detail.value}</span>
                        </div>
                    `);
                }
            });
        },
        
        /**
         * Handle stock data errors
         */
        handleStockDataError(symbol, error) {
            const widget = this.state.activeWidgets.get(symbol);
            if (!widget) {
                return;
            }
            
            widget.retryCount++;
            
            if (widget.retryCount < this.config.maxRetries) {
                // Retry after delay
                setTimeout(() => {
                    this.updateStockData(symbol);
                }, this.config.retryDelay * widget.retryCount);
            } else {
                // Show error state
                const $widget = widget.$element;
                $widget.find('.stock-data').html(`
                    <div class="stock-error">
                        <p>Unable to load data for ${symbol}</p>
                        <button class="btn btn-secondary btn-small" onclick="StockScannerPro.refreshStock('${symbol}')">
                            Try Again
                        </button>
                    </div>
                `);
            }
        },
        
        /**
         * Refresh stock data manually
         */
        refreshStock(symbol) {
            const widget = this.state.activeWidgets.get(symbol);
            if (widget) {
                widget.retryCount = 0;
                this.removeFromCache(symbol);
                this.updateStockData(symbol);
            }
        },
        
        /**
         * Start periodic updates
         */
        startPeriodicUpdates() {
            this.state.updateTimers.set('main', setInterval(() => {
                if (!document.hidden) {
                    this.updateAllWidgets();
                }
            }, this.config.updateInterval));
        },
        
        /**
         * Update all active widgets
         */
        updateAllWidgets() {
            this.state.activeWidgets.forEach((widget, symbol) => {
                this.updateStockData(symbol);
            });
        },
        
        /**
         * Pause updates (when tab is hidden)
         */
        pauseUpdates() {
            this.state.updateTimers.forEach((timer, key) => {
                clearInterval(timer);
            });
            this.state.updateTimers.clear();
        },
        
        /**
         * Resume updates
         */
        resumeUpdates() {
            this.startPeriodicUpdates();
        },
        
        /**
         * Toggle real-time updates
         */
        toggleRealTimeUpdates(enabled) {
            if (enabled) {
                this.config.updateInterval = 5000; // 5 seconds
            } else {
                this.config.updateInterval = 30000; // 30 seconds
            }
            
            this.pauseUpdates();
            this.resumeUpdates();
        },
        
        /**
         * Initialize charts
         */
        initializeCharts() {
            $('.stock-chart canvas').each((index, canvas) => {
                const $canvas = $(canvas);
                const symbol = $canvas.closest('.stock-scanner-widget').data('symbol');
                
                if (symbol) {
                    this.createStockChart(symbol, canvas);
                }
            });
        },
        
        /**
         * Create stock chart
         */
        createStockChart(symbol, canvas) {
            // Chart implementation would go here
            // For now, we'll create a placeholder
            const ctx = canvas.getContext('2d');
            
            // Simple placeholder chart
            ctx.fillStyle = this.config.chartColors.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = this.config.chartColors.neutral;
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Chart loading...', canvas.width / 2, canvas.height / 2);
        },
        
        /**
         * Update stock chart
         */
        updateStockChart(symbol, data) {
            // Chart update implementation would go here
            console.log(`Updating chart for ${symbol}`, data);
        },
        
        /**
         * Setup membership components
         */
        setupMembershipComponents() {
            this.updateMembershipDisplay();
            this.initializeMembershipPlans();
        },
        
        /**
         * Update membership status display
         */
        updateMembershipDisplay() {
            const membershipNames = ['Free', 'Free', 'Bronze', 'Silver', 'Gold'];
            const membershipName = membershipNames[this.state.membershipLevel] || 'Free';
            
            $('.membership-status-badge').removeClass('free bronze silver gold');
            $('.membership-status-badge').addClass(membershipName.toLowerCase());
            $('.membership-status-badge').text(membershipName);
            
            // Update usage display
            $('.api-usage-current').text(this.state.apiCallsToday);
            $('.api-usage-limit').text(this.state.apiLimit);
            
            const usagePercent = (this.state.apiCallsToday / this.state.apiLimit) * 100;
            $('.api-usage-bar').css('width', `${Math.min(usagePercent, 100)}%`);
            
            if (usagePercent > 80) {
                $('.api-usage-bar').addClass('warning');
            }
        },
        
        /**
         * Initialize membership plans
         */
        initializeMembershipPlans() {
            $('.membership-plan').each((index, element) => {
                const $plan = $(element);
                const level = $plan.data('level');
                
                if (level === this.state.membershipLevel) {
                    $plan.addClass('current-plan');
                    $plan.find('.membership-plan-button').text('Current Plan').prop('disabled', true);
                }
            });
        },
        
        /**
         * Handle membership upgrade
         */
        handleMembershipUpgrade($button) {
            const $plan = $button.closest('.membership-plan');
            const level = $plan.data('level');
            const planName = $plan.find('.membership-plan-name').text();
            
            if (level <= this.state.membershipLevel) {
                return;
            }
            
            // Show confirmation modal
            this.showUpgradeModal(level, planName);
        },
        
        /**
         * Show upgrade modal
         */
        showUpgradeModal(level, planName) {
            const modal = `
                <div class="stock-scanner-modal-overlay">
                    <div class="stock-scanner-modal">
                        <div class="modal-header">
                            <h3>Upgrade to ${planName}</h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <p>You're about to upgrade to the ${planName} plan.</p>
                            <p>This will give you access to enhanced features and higher API limits.</p>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary modal-cancel">Cancel</button>
                            <button class="btn btn-primary modal-confirm" data-level="${level}">
                                Upgrade Now
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            $('body').append(modal);
            
            // Bind events
            $('.modal-close, .modal-cancel').on('click', () => {
                $('.stock-scanner-modal-overlay').remove();
            });
            
            $('.modal-confirm').on('click', (e) => {
                const upgradeLevel = $(e.currentTarget).data('level');
                this.processUpgrade(upgradeLevel);
            });
        },
        
        /**
         * Process membership upgrade
         */
        async processUpgrade(level) {
            try {
                $('.modal-confirm').prop('disabled', true).text('Processing...');
                
                const response = await this.apiCall('process_upgrade', { level });
                
                if (response.success) {
                    window.location.href = response.data.checkout_url;
                } else {
                    throw new Error(response.data.message || 'Upgrade failed');
                }
                
            } catch (error) {
                console.error('Upgrade error:', error);
                this.showNotification('Upgrade failed. Please try again.', 'error');
            } finally {
                $('.stock-scanner-modal-overlay').remove();
            }
        },
        
        /**
         * Handle stock search
         */
        async handleStockSearch($form) {
            const query = $form.find('input[name="search"]').val().trim();
            if (!query) {
                return;
            }
            
            const $results = $form.find('.search-results');
            $results.html('<div class="loading">Searching...</div>');
            
            try {
                const response = await this.apiCall('search_stocks', { query });
                
                if (response.success) {
                    this.displaySearchResults($results, response.data.results);
                } else {
                    throw new Error(response.data.message || 'Search failed');
                }
                
            } catch (error) {
                console.error('Search error:', error);
                $results.html('<div class="error">Search failed. Please try again.</div>');
            }
        },
        
        /**
         * Display search results
         */
        displaySearchResults($container, results) {
            if (results.length === 0) {
                $container.html('<div class="no-results">No stocks found.</div>');
                return;
            }
            
            const resultsHtml = results.map(stock => `
                <div class="search-result-item">
                    <div class="stock-info">
                        <strong>${stock.symbol}</strong>
                        <span>${stock.name}</span>
                    </div>
                    <div class="stock-actions">
                        <button class="btn btn-primary btn-small" onclick="StockScannerPro.addStockWidget('${stock.symbol}')">
                            Add Widget
                        </button>
                        <button class="btn btn-secondary btn-small add-to-watchlist" data-symbol="${stock.symbol}">
                            Watch
                        </button>
                    </div>
                </div>
            `).join('');
            
            $container.html(resultsHtml);
        },
        
        /**
         * Add stock widget dynamically
         */
        addStockWidget(symbol) {
            const widgetHtml = `
                <div class="stock-scanner-widget" data-symbol="${symbol}">
                    <div class="stock-widget-header">
                        <h3 class="stock-widget-title">${symbol}</h3>
                        <button class="stock-widget-refresh">Refresh</button>
                    </div>
                    <div class="stock-widget-price">
                        <span class="stock-price-current">Loading...</span>
                        <span class="stock-price-change"></span>
                    </div>
                    <div class="stock-widget-details"></div>
                </div>
            `;
            
            $('.stock-widgets-container').append(widgetHtml);
            
            const $newWidget = $(`.stock-scanner-widget[data-symbol="${symbol}"]`).last();
            this.initializeWidget($newWidget);
        },
        
        /**
         * Watchlist management
         */
        async addToWatchlist(symbol) {
            try {
                const response = await this.apiCall('add_to_watchlist', { symbol });
                
                if (response.success) {
                    this.showNotification(`${symbol} added to watchlist`, 'success');
                    this.updateWatchlistDisplay();
                } else {
                    throw new Error(response.data.message || 'Failed to add to watchlist');
                }
                
            } catch (error) {
                console.error('Watchlist error:', error);
                this.showNotification('Failed to add to watchlist', 'error');
            }
        },
        
        async removeFromWatchlist(symbol) {
            try {
                const response = await this.apiCall('remove_from_watchlist', { symbol });
                
                if (response.success) {
                    this.showNotification(`${symbol} removed from watchlist`, 'success');
                    this.updateWatchlistDisplay();
                } else {
                    throw new Error(response.data.message || 'Failed to remove from watchlist');
                }
                
            } catch (error) {
                console.error('Watchlist error:', error);
                this.showNotification('Failed to remove from watchlist', 'error');
            }
        },
        
        /**
         * Update watchlist display
         */
        updateWatchlistDisplay() {
            // This would update the watchlist UI
            console.log('Updating watchlist display');
        },
        
        /**
         * Utility functions
         */
        
        /**
         * Make API call
         */
        async apiCall(action, data = {}) {
            return $.ajax({
                url: stockScannerPro.ajaxUrl,
                method: 'POST',
                data: {
                    action: 'stock_scanner_' + action,
                    nonce: stockScannerPro.nonce,
                    ...data
                }
            });
        },
        
        /**
         * Check if API call can be made
         */
        canMakeApiCall() {
            return this.state.apiCallsToday < this.state.apiLimit;
        },
        
        /**
         * Increment API call count
         */
        incrementApiCalls() {
            this.state.apiCallsToday++;
            this.updateMembershipDisplay();
        },
        
        /**
         * Show upgrade prompt
         */
        showUpgradePrompt($widget) {
            $widget.find('.stock-data').html(`
                <div class="upgrade-prompt">
                    <h4>Upgrade Required</h4>
                    <p>You've reached your daily limit of ${this.state.apiLimit} API calls.</p>
                    <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                </div>
            `);
        },
        
        /**
         * Set widget loading state
         */
        setWidgetLoading($widget, loading) {
            if (loading) {
                $widget.addClass('loading');
                $widget.find('.stock-widget-refresh').prop('disabled', true);
            } else {
                $widget.removeClass('loading');
                $widget.find('.stock-widget-refresh').prop('disabled', false);
            }
        },
        
        /**
         * Cache management
         */
        addToCache(symbol, data) {
            this.cache.set(symbol, {
                data: data,
                timestamp: Date.now()
            });
        },
        
        getFromCache(symbol) {
            return this.cache.get(symbol);
        },
        
        removeFromCache(symbol) {
            this.cache.delete(symbol);
        },
        
        /**
         * Show notification
         */
        showNotification(message, type = 'info') {
            const notification = `
                <div class="stock-scanner-notification ${type}">
                    ${message}
                    <button class="notification-close">&times;</button>
                </div>
            `;
            
            $('body').append(notification);
            
            setTimeout(() => {
                $('.stock-scanner-notification').fadeOut(() => {
                    $(this).remove();
                });
            }, 5000);
            
            $('.notification-close').on('click', function() {
                $(this).parent().fadeOut(() => {
                    $(this).remove();
                });
            });
        },
        
        /**
         * Format functions
         */
        formatPrice(price) {
            return parseFloat(price).toFixed(2);
        },
        
        formatCurrency(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                notation: 'compact',
                maximumFractionDigits: 1
            }).format(amount);
        },
        
        formatNumber(number) {
            return new Intl.NumberFormat('en-US', {
                notation: 'compact',
                maximumFractionDigits: 1
            }).format(number);
        }
    };
    
    /**
     * Initialize when document is ready
     */
    $(document).ready(function() {
        // Only initialize on Stock Scanner pages
        if (typeof stockScannerPro !== 'undefined') {
            StockScannerPro.init();
        }
    });
    
})(jQuery);