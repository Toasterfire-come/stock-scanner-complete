/**
 * Stock Scanner Pro - Market Overview Functionality
 */

(function() {
    'use strict';

    const MarketOverview = {
        init: function() {
            this.loadMarketStatistics();
            this.loadMarketIndices();
            this.loadTopMovers();
            this.loadMostActive();
            this.loadSectorPerformance();
            this.initMarketHeatmap();
            this.bindEvents();
            this.initRefreshTimer();
        },

        // Load market statistics
        loadMarketStatistics: function() {
            const container = document.getElementById('market-statistics');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading market statistics...');

            StockScannerAPI.Stock.getMarketOverview()
                .then(data => {
                    this.renderMarketStatistics(container, data);
                })
                .catch(error => {
                    console.error('Market statistics error:', error);
                    StockScannerAPI.Utils.showError(container, 'Failed to load market statistics');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading(container);
                });
        },

        // Render market statistics
        renderMarketStatistics: function(container, data) {
            if (!data || !data.market_overview) {
                container.innerHTML = '<p class="text-muted">Market statistics unavailable</p>';
                return;
            }

            const stats = data.market_overview;
            const html = `
                <div class="market-stat-card">
                    <div class="stat-value">${stats.total_stocks || 0}</div>
                    <div class="stat-label">Total Stocks</div>
                    <div class="stat-icon"><i class="fas fa-chart-bar"></i></div>
                </div>
                <div class="market-stat-card positive">
                    <div class="stat-value">${stats.gainers || 0}</div>
                    <div class="stat-label">Gainers</div>
                    <div class="stat-icon"><i class="fas fa-arrow-up"></i></div>
                </div>
                <div class="market-stat-card negative">
                    <div class="stat-value">${stats.losers || 0}</div>
                    <div class="stat-label">Losers</div>
                    <div class="stat-icon"><i class="fas fa-arrow-down"></i></div>
                </div>
                <div class="market-stat-card neutral">
                    <div class="stat-value">${stats.unchanged || 0}</div>
                    <div class="stat-label">Unchanged</div>
                    <div class="stat-icon"><i class="fas fa-minus"></i></div>
                </div>
                <div class="market-stat-card">
                    <div class="stat-value">${StockScannerAPI.Utils.formatNumber(stats.total_volume || 0)}</div>
                    <div class="stat-label">Total Volume</div>
                    <div class="stat-icon"><i class="fas fa-exchange-alt"></i></div>
                </div>
                <div class="market-stat-card">
                    <div class="stat-value">${StockScannerAPI.Utils.formatCurrency(stats.market_cap || 0)}</div>
                    <div class="stat-label">Market Cap</div>
                    <div class="stat-icon"><i class="fas fa-coins"></i></div>
                </div>
            `;

            container.innerHTML = html;
        },

        // Load market indices
        loadMarketIndices: function() {
            const container = document.getElementById('market-indices');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading market indices...');

            // Mock data for major indices - in real implementation, this would come from API
            const indices = [
                { symbol: 'SPY', name: 'S&P 500', price: 445.67, change: 2.34, changePercent: 0.53 },
                { symbol: 'QQQ', name: 'NASDAQ-100', price: 378.92, change: -1.45, changePercent: -0.38 },
                { symbol: 'DIA', name: 'Dow Jones', price: 346.78, change: 0.89, changePercent: 0.26 },
                { symbol: 'IWM', name: 'Russell 2000', price: 198.45, change: -0.67, changePercent: -0.34 }
            ];

            setTimeout(() => {
                this.renderMarketIndices(container, indices);
                StockScannerAPI.Utils.hideLoading(container);
            }, 1000);
        },

        // Render market indices
        renderMarketIndices: function(container, indices) {
            let html = '';
            
            indices.forEach(index => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(index.change);
                
                html += `
                    <div class="index-card" data-ticker="${index.symbol}">
                        <div class="index-header">
                            <h4 class="index-symbol">${index.symbol}</h4>
                            <span class="index-name">${index.name}</span>
                        </div>
                        <div class="index-price">
                            <div class="current-price">${StockScannerAPI.Utils.formatCurrency(index.price)}</div>
                            <div class="price-change ${changeClass}">
                                ${StockScannerAPI.Utils.formatCurrency(index.change)} 
                                (${StockScannerAPI.Utils.formatPercentage(index.changePercent)})
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Load top movers
        loadTopMovers: function() {
            const gainersContainer = document.getElementById('top-gainers');
            const losersContainer = document.getElementById('top-losers');
            
            if (!gainersContainer && !losersContainer) return;

            if (gainersContainer) {
                StockScannerAPI.Utils.showLoading(gainersContainer, 'Loading top gainers...');
            }
            if (losersContainer) {
                StockScannerAPI.Utils.showLoading(losersContainer, 'Loading top losers...');
            }

            StockScannerAPI.Stock.getStocks({ sort_by: 'price_change_percent', sort_order: 'desc', limit: 10 })
                .then(data => {
                    if (data && data.results) {
                        const gainers = data.results.filter(stock => stock.price_change_percent > 0).slice(0, 5);
                        const losers = data.results.filter(stock => stock.price_change_percent < 0).slice(-5).reverse();
                        
                        if (gainersContainer) {
                            this.renderTopMovers(gainersContainer, gainers, 'gainers');
                        }
                        if (losersContainer) {
                            this.renderTopMovers(losersContainer, losers, 'losers');
                        }
                    }
                })
                .catch(error => {
                    console.error('Top movers error:', error);
                    if (gainersContainer) {
                        StockScannerAPI.Utils.showError(gainersContainer, 'Failed to load top gainers');
                    }
                    if (losersContainer) {
                        StockScannerAPI.Utils.showError(losersContainer, 'Failed to load top losers');
                    }
                })
                .finally(() => {
                    if (gainersContainer) {
                        StockScannerAPI.Utils.hideLoading(gainersContainer);
                    }
                    if (losersContainer) {
                        StockScannerAPI.Utils.hideLoading(losersContainer);
                    }
                });
        },

        // Render top movers
        renderTopMovers: function(container, stocks, type) {
            if (!stocks || stocks.length === 0) {
                container.innerHTML = `<p class="text-muted">No ${type} data available</p>`;
                return;
            }

            let html = '';
            stocks.forEach((stock, index) => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(stock.price_change_today || stock.change);
                
                html += `
                    <div class="mover-item" data-ticker="${stock.ticker}">
                        <div class="mover-rank">${index + 1}</div>
                        <div class="mover-info">
                            <div class="mover-ticker">${stock.ticker}</div>
                            <div class="mover-company">${stock.company_name || stock.name || stock.ticker}</div>
                        </div>
                        <div class="mover-price">
                            <div class="current-price">${StockScannerAPI.Utils.formatCurrency(stock.current_price || stock.price)}</div>
                            <div class="price-change ${changeClass}">
                                ${StockScannerAPI.Utils.formatPercentage(stock.price_change_percent || stock.change_percent)}
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Load most active stocks
        loadMostActive: function() {
            const container = document.getElementById('most-active');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading most active stocks...');

            StockScannerAPI.Stock.getStocks({ sort_by: 'volume', sort_order: 'desc', limit: 20 })
                .then(data => {
                    this.renderMostActive(container, data);
                })
                .catch(error => {
                    console.error('Most active stocks error:', error);
                    StockScannerAPI.Utils.showError(container, 'Failed to load most active stocks');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading(container);
                });
        },

        // Render most active stocks
        renderMostActive: function(container, data) {
            if (!data || !data.results || data.results.length === 0) {
                container.innerHTML = '<p class="text-muted">No active stocks data available</p>';
                return;
            }

            let html = '';
            data.results.slice(0, 12).forEach(stock => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(stock.price_change_today || stock.change);
                
                html += `
                    <div class="active-stock-card" data-ticker="${stock.ticker}">
                        <div class="stock-header">
                            <div class="stock-symbol">${stock.ticker}</div>
                            <div class="stock-price">${StockScannerAPI.Utils.formatCurrency(stock.current_price || stock.price)}</div>
                        </div>
                        <div class="stock-change ${changeClass}">
                            ${StockScannerAPI.Utils.formatCurrency(stock.price_change_today || stock.change)} 
                            (${StockScannerAPI.Utils.formatPercentage(stock.price_change_percent || stock.change_percent)})
                        </div>
                        <div class="stock-volume">
                            Volume: ${StockScannerAPI.Utils.formatNumber(stock.volume || 0)}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Load sector performance
        loadSectorPerformance: function() {
            const container = document.getElementById('sector-performance');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading sector performance...');

            // Mock sector data - in real implementation, this would come from API
            const sectors = [
                { name: 'Technology', change: 1.25, stocks: 45 },
                { name: 'Healthcare', change: 0.87, stocks: 32 },
                { name: 'Financial', change: -0.34, stocks: 28 },
                { name: 'Energy', change: -1.56, stocks: 18 },
                { name: 'Consumer Discretionary', change: 0.45, stocks: 35 },
                { name: 'Industrials', change: 0.23, stocks: 24 },
                { name: 'Materials', change: -0.78, stocks: 15 },
                { name: 'Utilities', change: 0.12, stocks: 12 }
            ];

            setTimeout(() => {
                this.renderSectorPerformance(container, sectors);
                StockScannerAPI.Utils.hideLoading(container);
            }, 1500);
        },

        // Render sector performance
        renderSectorPerformance: function(container, sectors) {
            let html = '';
            
            sectors.forEach(sector => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(sector.change);
                
                html += `
                    <div class="sector-card">
                        <div class="sector-name">${sector.name}</div>
                        <div class="sector-stats">
                            <div class="sector-change ${changeClass}">
                                ${StockScannerAPI.Utils.formatPercentage(sector.change)}
                            </div>
                            <div class="sector-stocks">${sector.stocks} stocks</div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Initialize market heatmap
        initMarketHeatmap: function() {
            const container = document.getElementById('market-heatmap');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading market heatmap...');

            // Placeholder for heatmap - would integrate with actual heatmap library
            setTimeout(() => {
                container.innerHTML = `
                    <div class="heatmap-placeholder">
                        <div class="heatmap-message">
                            <i class="fas fa-th text-4xl mb-4"></i>
                            <h4>Market Heatmap</h4>
                            <p>Interactive heatmap visualization will be displayed here</p>
                        </div>
                    </div>
                `;
                StockScannerAPI.Utils.hideLoading(container);
            }, 2000);
        },

        // Initialize auto-refresh timer
        initRefreshTimer: function() {
            // Refresh market data every 5 minutes
            setInterval(() => {
                this.refreshMarketData();
            }, 300000);
        },

        // Refresh all market data
        refreshMarketData: function() {
            this.loadMarketStatistics();
            this.loadMarketIndices();
            this.loadTopMovers();
            this.loadMostActive();
            this.loadSectorPerformance();
        },

        // Bind event handlers
        bindEvents: function() {
            // Refresh button
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-action="refresh-market-data"]') || 
                    e.target.closest('[data-action="refresh-market-data"]')) {
                    e.preventDefault();
                    this.refreshMarketData();
                    StockScannerAPI.Toast.show('Market data refreshed', 'success');
                }
            });

            // Stock/Index click handlers
            document.addEventListener('click', (e) => {
                const stockCard = e.target.closest('[data-ticker]');
                if (stockCard) {
                    const ticker = stockCard.dataset.ticker;
                    if (ticker) {
                        window.location.href = `/stock-lookup/?ticker=${ticker}`;
                    }
                }
            });

            // Error retry buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.error-retry')) {
                    const container = e.target.closest('[id]');
                    const containerId = container?.id;
                    
                    switch (containerId) {
                        case 'market-statistics':
                            this.loadMarketStatistics();
                            break;
                        case 'market-indices':
                            this.loadMarketIndices();
                            break;
                        case 'top-gainers':
                        case 'top-losers':
                            this.loadTopMovers();
                            break;
                        case 'most-active':
                            this.loadMostActive();
                            break;
                        case 'sector-performance':
                            this.loadSectorPerformance();
                            break;
                        case 'market-heatmap':
                            this.initMarketHeatmap();
                            break;
                    }
                }
            });
        }
    };

    // Export to global scope
    window.StockScannerMarketOverview = MarketOverview;

    // Auto-initialize if on market overview page
    document.addEventListener('DOMContentLoaded', function() {
        if (document.body.classList.contains('page-template-page-market-overview')) {
            MarketOverview.init();
        }
    });

})();