/**
 * Enhanced Dashboard functionality with real-time updates
 */

class StockScannerDashboard {
    constructor() {
        this.realTimeManager = null;
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.portfolioData = null;
        this.watchlistData = null;
        
        this.init();
    }

    init() {
        this.initializeRealTimeUpdates();
        this.loadDashboardData();
        this.bindEvents();
        this.startPeriodicUpdates();
        
        console.log('Enhanced Dashboard initialized');
    }

    initializeRealTimeUpdates() {
        if (window.StockScannerAPI && window.StockScannerAPI.RealTime) {
            this.realTimeManager = window.StockScannerAPI.RealTime;
        }
    }

    async loadDashboardData() {
        try {
            this.showLoading();
            
            // Load portfolio data
            await this.loadPortfolioData();
            
            // Load watchlist data
            await this.loadWatchlistData();
            
            // Load market overview
            await this.loadMarketOverview();
            
            // Load news feed
            await this.loadNewsFeed();
            
            this.hideLoading();
        } catch (error) {
            console.error('Dashboard data loading failed:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadPortfolioData() {
        try {
            const response = await StockScannerAPI.Portfolio.getPortfolio();
            
            if (response.success && response.portfolio) {
                this.portfolioData = response.portfolio;
                this.renderPortfolioSummary(response.portfolio);
                this.initPortfolioChart(response.portfolio);
                
                // Subscribe to real-time updates for portfolio holdings
                if (this.realTimeManager && response.portfolio.holdings) {
                    const tickers = response.portfolio.holdings.map(h => h.ticker);
                    this.realTimeManager.startUpdates(tickers, (data) => {
                        this.updatePortfolioRealTime(data);
                    });
                }
            } else {
                this.renderEmptyPortfolio();
            }
        } catch (error) {
            console.error('Portfolio loading error:', error);
            this.renderPortfolioError();
        }
    }

    async loadWatchlistData() {
        try {
            const response = await StockScannerAPI.Watchlist.getWatchlist();
            
            if (response.success && response.watchlist) {
                this.watchlistData = response.watchlist;
                this.renderWatchlistPreview(response.watchlist);
                
                // Subscribe to real-time updates for watchlist items
                if (this.realTimeManager && response.watchlist.items) {
                    const tickers = response.watchlist.items.map(item => item.ticker);
                    this.realTimeManager.startUpdates(tickers, (data) => {
                        this.updateWatchlistRealTime(data);
                    });
                }
            } else {
                this.renderEmptyWatchlist();
            }
        } catch (error) {
            console.error('Watchlist loading error:', error);
            this.renderWatchlistError();
        }
    }

    async loadMarketOverview() {
        try {
            const response = await StockScannerAPI.Stock.getMarketOverview();
            
            if (response.success && response.market_overview) {
                this.renderMarketOverview(response.market_overview);
            }
        } catch (error) {
            console.error('Market overview loading error:', error);
        }
    }

    async loadNewsFeed() {
        try {
            const response = await StockScannerAPI.News.getPersonalizedNews(5);
            
            if (response.success && response.data) {
                this.renderNewsFeed(response.data);
            }
        } catch (error) {
            console.error('News feed loading error:', error);
        }
    }

    renderPortfolioSummary(portfolio) {
        const container = document.getElementById('portfolio-summary');
        if (!container) return;

        const summary = portfolio.summary;
        const performance = portfolio.performance;

        const totalValueClass = summary.total_gain_loss >= 0 ? 'text-success' : 'text-danger';
        const totalGainLossClass = summary.total_gain_loss >= 0 ? 'text-success' : 'text-danger';

        container.innerHTML = `
            <div class="portfolio-stats grid grid-cols-2 gap-4 mb-6">
                <div class="stat-card">
                    <div class="stat-label">Total Value</div>
                    <div class="stat-value ${totalValueClass}">
                        ${StockScannerAPI.Utils.formatCurrency(summary.total_value)}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Return</div>
                    <div class="stat-value ${totalGainLossClass}">
                        ${StockScannerAPI.Utils.formatCurrency(summary.total_gain_loss)}
                        <span class="stat-subvalue">
                            (${StockScannerAPI.Utils.formatPercentage(summary.total_gain_loss_percent)})
                        </span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Holdings</div>
                    <div class="stat-value">${summary.holdings_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Invested</div>
                    <div class="stat-value">
                        ${StockScannerAPI.Utils.formatCurrency(summary.total_cost)}
                    </div>
                </div>
            </div>
            
            <div class="portfolio-holdings">
                <h4 class="holdings-title">Top Holdings</h4>
                <div class="holdings-list">
                    ${this.renderTopHoldings(portfolio.holdings)}
                </div>
            </div>
        `;
    }

    renderTopHoldings(holdings) {
        if (!holdings || holdings.length === 0) {
            return '<p class="no-holdings">No holdings found</p>';
        }

        // Sort by current value and take top 5
        const topHoldings = holdings
            .sort((a, b) => b.current_value - a.current_value)
            .slice(0, 5);

        return topHoldings.map(holding => {
            const changeClass = holding.gain_loss >= 0 ? 'text-success' : 'text-danger';
            
            return `
                <div class="holding-item flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                    <div class="holding-info">
                        <div class="holding-ticker font-mono font-semibold">${holding.ticker}</div>
                        <div class="holding-shares text-sm text-gray-600">
                            ${holding.shares} shares @ ${StockScannerAPI.Utils.formatCurrency(holding.average_cost)}
                        </div>
                    </div>
                    <div class="holding-performance text-right">
                        <div class="holding-value font-semibold">
                            ${StockScannerAPI.Utils.formatCurrency(holding.current_value)}
                        </div>
                        <div class="holding-change text-sm ${changeClass}">
                            ${StockScannerAPI.Utils.formatCurrency(holding.gain_loss)} 
                            (${StockScannerAPI.Utils.formatPercentage(holding.gain_loss_percent)})
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderWatchlistPreview(watchlist) {
        const container = document.getElementById('watchlist-preview');
        if (!container) return;

        if (!watchlist.items || watchlist.items.length === 0) {
            this.renderEmptyWatchlist();
            return;
        }

        // Take first 5 items
        const previewItems = watchlist.items.slice(0, 5);

        container.innerHTML = `
            <div class="watchlist-items">
                ${previewItems.map(item => this.renderWatchlistItem(item)).join('')}
            </div>
        `;
    }

    renderWatchlistItem(item) {
        const changeClass = item.stock_data.price_change >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <div class="watchlist-item flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg" data-ticker="${item.ticker}">
                <div class="item-info">
                    <div class="item-ticker font-mono font-semibold">${item.ticker}</div>
                    <div class="item-company text-sm text-gray-600">
                        ${item.stock_data.company_name || item.ticker}
                    </div>
                </div>
                <div class="item-price text-right">
                    <div class="current-price font-semibold">
                        ${StockScannerAPI.Utils.formatCurrency(item.stock_data.current_price)}
                    </div>
                    <div class="price-change text-sm ${changeClass}">
                        ${StockScannerAPI.Utils.formatCurrency(item.stock_data.price_change)}
                        (${StockScannerAPI.Utils.formatPercentage(item.stock_data.price_change_percent)})
                    </div>
                </div>
            </div>
        `;
    }

    renderMarketOverview(marketData) {
        const container = document.getElementById('market-overview');
        if (!container) return;

        container.innerHTML = `
            <div class="market-stats grid grid-cols-2 gap-4">
                <div class="market-stat">
                    <div class="stat-label">Market Status</div>
                    <div class="stat-value ${marketData.is_open ? 'text-success' : 'text-warning'}">
                        ${marketData.is_open ? 'Open' : 'Closed'}
                    </div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">S&P 500</div>
                    <div class="stat-value">
                        ${StockScannerAPI.Utils.formatNumber(marketData.sp500 || 4200)}
                        <span class="stat-change text-success">+0.5%</span>
                    </div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">Active Stocks</div>
                    <div class="stat-value">
                        ${StockScannerAPI.Utils.formatNumber(marketData.active_stocks || 8500)}
                    </div>
                </div>
                <div class="market-stat">
                    <div class="stat-label">Volume</div>
                    <div class="stat-value">
                        ${StockScannerAPI.Utils.formatNumber(marketData.total_volume || 2500000000)}
                    </div>
                </div>
            </div>
        `;
    }

    renderNewsFeed(articles) {
        const container = document.getElementById('news-feed');
        if (!container) return;

        if (!articles || articles.length === 0) {
            container.innerHTML = '<p class="no-news">No news available</p>';
            return;
        }

        container.innerHTML = articles.map(article => `
            <div class="news-item p-3 hover:bg-gray-50 rounded-lg">
                <h5 class="news-title font-medium mb-1">
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="hover:text-blue-600">
                        ${article.title}
                    </a>
                </h5>
                <div class="news-meta text-sm text-gray-600">
                    <span class="news-source">${article.source}</span>
                    <span class="news-separator"> • </span>
                    <span class="news-time">${this.formatTimeAgo(article.published_at)}</span>
                    ${article.related_stocks ? 
                        `<span class="news-separator"> • </span>
                         <span class="news-stocks">${article.related_stocks.slice(0, 2).join(', ')}</span>` 
                        : ''}
                </div>
            </div>
        `).join('');
    }

    initPortfolioChart(portfolio) {
        const chartContainer = document.getElementById('portfolio-chart');
        if (!chartContainer) return;

        // Create allocation chart
        const ctx = chartContainer.getContext('2d');
        
        if (this.charts.portfolioChart) {
            this.charts.portfolioChart.destroy();
        }

        const allocation = portfolio.allocation.by_stock.slice(0, 8); // Top 8 holdings
        
        this.charts.portfolioChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: allocation.map(item => item.ticker),
                datasets: [{
                    data: allocation.map(item => item.percentage),
                    backgroundColor: [
                        '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
                        '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    updatePortfolioRealTime(data) {
        if (!this.portfolioData || !this.portfolioData.holdings) return;

        let hasUpdates = false;

        // Update holdings with new prices
        this.portfolioData.holdings.forEach(holding => {
            if (data[holding.ticker]) {
                const newData = data[holding.ticker];
                const oldPrice = holding.current_price;
                const newPrice = newData.current_price;

                if (Math.abs(oldPrice - newPrice) > 0.01) {
                    holding.current_price = newPrice;
                    holding.current_value = newPrice * holding.shares;
                    holding.gain_loss = holding.current_value - holding.total_cost;
                    holding.gain_loss_percent = holding.total_cost > 0 ? 
                        (holding.gain_loss / holding.total_cost) * 100 : 0;
                    
                    hasUpdates = true;
                }
            }
        });

        if (hasUpdates) {
            // Recalculate portfolio summary
            this.portfolioData.summary = this.calculatePortfolioSummary(this.portfolioData.holdings);
            
            // Re-render portfolio summary
            this.renderPortfolioSummary(this.portfolioData);
            
            // Add visual indication of update
            this.flashUpdate('portfolio-summary');
        }
    }

    updateWatchlistRealTime(data) {
        if (!this.watchlistData || !this.watchlistData.items) return;

        let hasUpdates = false;

        this.watchlistData.items.forEach(item => {
            if (data[item.ticker]) {
                const newData = data[item.ticker];
                const oldPrice = item.stock_data.current_price;
                const newPrice = newData.current_price;

                if (Math.abs(oldPrice - newPrice) > 0.01) {
                    item.stock_data = { ...item.stock_data, ...newData };
                    hasUpdates = true;

                    // Update specific watchlist item in DOM
                    this.updateWatchlistItemDOM(item.ticker, newData);
                }
            }
        });

        if (hasUpdates) {
            this.flashUpdate('watchlist-preview');
        }
    }

    updateWatchlistItemDOM(ticker, newData) {
        const itemElement = document.querySelector(`[data-ticker="${ticker}"]`);
        if (!itemElement) return;

        const priceElement = itemElement.querySelector('.current-price');
        const changeElement = itemElement.querySelector('.price-change');

        if (priceElement) {
            priceElement.textContent = StockScannerAPI.Utils.formatCurrency(newData.current_price);
        }

        if (changeElement) {
            const changeClass = newData.price_change >= 0 ? 'text-success' : 'text-danger';
            changeElement.className = `price-change text-sm ${changeClass}`;
            changeElement.innerHTML = `
                ${StockScannerAPI.Utils.formatCurrency(newData.price_change)}
                (${StockScannerAPI.Utils.formatPercentage(newData.change_percent)})
            `;
        }
    }

    flashUpdate(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.classList.add('flash-update');
        setTimeout(() => {
            element.classList.remove('flash-update');
        }, 1000);
    }

    calculatePortfolioSummary(holdings) {
        if (!holdings || holdings.length === 0) {
            return {
                total_value: 0,
                total_cost: 0,
                total_gain_loss: 0,
                total_gain_loss_percent: 0,
                holdings_count: 0
            };
        }

        const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
        const totalCost = holdings.reduce((sum, h) => sum + h.total_cost, 0);
        const totalGainLoss = totalValue - totalCost;
        const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;

        return {
            total_value: totalValue,
            total_cost: totalCost,
            total_gain_loss: totalGainLoss,
            total_gain_loss_percent: totalGainLossPercent,
            holdings_count: holdings.length
        };
    }

    startPeriodicUpdates() {
        // Update dashboard data every 5 minutes
        setInterval(() => {
            this.loadMarketOverview();
            this.loadNewsFeed();
        }, 5 * 60 * 1000);
    }

    bindEvents() {
        // Refresh dashboard
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-action') && 
                e.target.getAttribute('data-action') === 'refresh-dashboard') {
                this.loadDashboardData();
            }
        });

        // Add stock modal
        this.bindAddStockModal();
    }

    bindAddStockModal() {
        // Add to portfolio
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('add-to-portfolio-btn')) {
                const ticker = e.target.getAttribute('data-ticker');
                if (ticker) {
                    this.showAddToPortfolioModal(ticker);
                }
            }
        });

        // Add to watchlist
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('add-to-watchlist-btn')) {
                const ticker = e.target.getAttribute('data-ticker');
                if (ticker) {
                    try {
                        const result = await StockScannerAPI.Watchlist.addToWatchlist(ticker);
                        StockScannerAPI.Toast.show(`${ticker} added to watchlist!`, 'success');
                        this.loadWatchlistData();
                    } catch (error) {
                        StockScannerAPI.Toast.show('Failed to add to watchlist', 'error');
                    }
                }
            }
        });
    }

    showAddToPortfolioModal(ticker) {
        // Create and show modal for adding to portfolio
        const modal = document.createElement('div');
        modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="modal-content bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 class="text-lg font-semibold mb-4">Add ${ticker} to Portfolio</h3>
                <form id="add-portfolio-form">
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Number of Shares</label>
                        <input type="number" name="shares" step="0.0001" min="0.0001" required 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Cost per Share</label>
                        <input type="number" name="cost_basis" step="0.01" min="0.01" required 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-6">
                        <label class="block text-sm font-medium mb-2">Purchase Date</label>
                        <input type="date" name="purchase_date" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="flex justify-end space-x-3">
                        <button type="button" class="modal-close px-4 py-2 text-gray-600 hover:text-gray-800">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            Add to Portfolio
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle form submission
        modal.querySelector('#add-portfolio-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const shares = parseFloat(formData.get('shares'));
            const costBasis = parseFloat(formData.get('cost_basis'));
            const purchaseDate = formData.get('purchase_date') || null;

            try {
                const result = await StockScannerAPI.Portfolio.addToPortfolio(ticker, shares, costBasis);
                StockScannerAPI.Toast.show(`${ticker} added to portfolio!`, 'success');
                modal.remove();
                this.loadPortfolioData();
            } catch (error) {
                StockScannerAPI.Toast.show('Failed to add to portfolio', 'error');
            }
        });

        // Close modal
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('modal-close')) {
                modal.remove();
            }
        });
    }

    renderEmptyPortfolio() {
        const container = document.getElementById('portfolio-summary');
        if (!container) return;

        container.innerHTML = `
            <div class="empty-portfolio text-center py-8">
                <div class="empty-icon text-4xl mb-4">📊</div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">No Portfolio Holdings</h4>
                <p class="text-gray-600 mb-4">Start building your portfolio by adding some stocks.</p>
                <button class="btn btn-primary" onclick="window.location.href='/stock-lookup/'">
                    Find Stocks
                </button>
            </div>
        `;
    }

    renderEmptyWatchlist() {
        const container = document.getElementById('watchlist-preview');
        if (!container) return;

        container.innerHTML = `
            <div class="empty-watchlist text-center py-8">
                <div class="empty-icon text-4xl mb-4">👁️</div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">No Watchlist Items</h4>
                <p class="text-gray-600 mb-4">Add stocks to your watchlist to track them.</p>
                <button class="btn btn-primary" onclick="window.location.href='/stock-lookup/'">
                    Add Stocks
                </button>
            </div>
        `;
    }

    renderPortfolioError() {
        const container = document.getElementById('portfolio-summary');
        if (!container) return;

        container.innerHTML = `
            <div class="portfolio-error text-center py-8">
                <div class="error-icon text-4xl mb-4">⚠️</div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">Unable to Load Portfolio</h4>
                <p class="text-gray-600 mb-4">There was an error loading your portfolio data.</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    Try Again
                </button>
            </div>
        `;
    }

    renderWatchlistError() {
        const container = document.getElementById('watchlist-preview');
        if (!container) return;

        container.innerHTML = `
            <div class="watchlist-error text-center py-8">
                <div class="error-icon text-4xl mb-4">⚠️</div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">Unable to Load Watchlist</h4>
                <p class="text-gray-600">There was an error loading your watchlist.</p>
            </div>
        `;
    }

    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));

        if (diffInMinutes < 60) {
            return `${diffInMinutes}m ago`;
        } else if (diffInMinutes < 1440) {
            return `${Math.floor(diffInMinutes / 60)}h ago`;
        } else {
            return `${Math.floor(diffInMinutes / 1440)}d ago`;
        }
    }

    showLoading() {
        StockScannerApp.showLoading('Loading dashboard data...');
    }

    hideLoading() {
        StockScannerApp.hideLoading();
    }

    showError(message) {
        StockScannerAPI.Toast.show(message, 'error');
    }
}

// Export for global use
window.StockScannerDashboard = StockScannerDashboard;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.body.classList.contains('page-template-page-dashboard')) {
        new StockScannerDashboard();
    }
});