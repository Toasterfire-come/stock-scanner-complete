/**
 * Stock Scanner Pro - Dashboard Functionality
 */

(function($) {
    'use strict';

    const Dashboard = {
        init: function() {
            this.initPortfolioSummary();
            this.initWatchlist();
            this.initMarketOverview();
            this.initNewsFeed();
            this.initQuickActions();
            this.initRefreshTimer();
            this.bindEvents();
        },

        // Initialize portfolio summary widget
        initPortfolioSummary: function() {
            const $container = $('#portfolio-summary');
            if ($container.length === 0) return;

            StockScannerAPI.Utils.showLoading($container);

            StockScannerAPI.Portfolio.getPortfolio()
                .then(data => {
                    this.renderPortfolioSummary($container, data);
                })
                .catch(error => {
                    console.error('Portfolio error:', error);
                    StockScannerAPI.Utils.showError($container, 'Failed to load portfolio data');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading($container);
                });
        },

        // Render portfolio summary
        renderPortfolioSummary: function($container, data) {
            if (!data || !data.success) {
                $container.html('<p class="text-muted">No portfolio data available</p>');
                return;
            }

            const portfolio = data.data || {};
            const totalValue = portfolio.total_value || 0;
            const totalReturn = portfolio.total_return || 0;
            const totalReturnPercent = portfolio.total_return_percent || 0;
            const holdingsCount = portfolio.holdings_count || 0;

            const html = `
                <div class="portfolio-summary">
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">${StockScannerAPI.Utils.formatCurrency(totalValue)}</div>
                        <div class="portfolio-metric-label">Total Value</div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value ${StockScannerAPI.Utils.getPriceChangeClass(totalReturn)}">
                            ${StockScannerAPI.Utils.formatCurrency(totalReturn)}
                        </div>
                        <div class="portfolio-metric-label">Total Return</div>
                        <div class="portfolio-metric-change ${StockScannerAPI.Utils.getPriceChangeClass(totalReturn)}">
                            ${StockScannerAPI.Utils.formatPercentage(totalReturnPercent)}
                        </div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">${holdingsCount}</div>
                        <div class="portfolio-metric-label">Holdings</div>
                    </div>
                    <div class="portfolio-metric">
                        <div class="portfolio-metric-value">
                            ${portfolio.top_performer ? portfolio.top_performer.ticker : 'N/A'}
                        </div>
                        <div class="portfolio-metric-label">Top Performer</div>
                        ${portfolio.top_performer ? 
                            `<div class="portfolio-metric-change text-success">
                                ${StockScannerAPI.Utils.formatPercentage(portfolio.top_performer.return_percent)}
                            </div>` : ''
                        }
                    </div>
                </div>
            `;

            $container.html(html);
        },

        // Initialize watchlist widget
        initWatchlist: function() {
            const $container = $('#watchlist-preview');
            if ($container.length === 0) return;

            StockScannerAPI.Utils.showLoading($container);

            StockScannerAPI.Watchlist.getWatchlist()
                .then(data => {
                    this.renderWatchlist($container, data);
                })
                .catch(error => {
                    console.error('Watchlist error:', error);
                    StockScannerAPI.Utils.showError($container, 'Failed to load watchlist');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading($container);
                });
        },

        // Render watchlist
        renderWatchlist: function($container, data) {
            if (!data || !data.success || !data.data || data.data.length === 0) {
                $container.html('<p class="text-muted">No watchlist items found</p>');
                return;
            }

            const items = data.data.slice(0, 5); // Show only first 5 items
            let html = '<div class="watchlist-items">';

            items.forEach(item => {
                const change = item.price_change_today || 0;
                const changePercent = item.change_percent || 0;

                html += `
                    <div class="watchlist-item" data-ticker="${item.ticker}">
                        <div class="watchlist-item-info">
                            <h4 class="watchlist-item-ticker">${item.ticker}</h4>
                            <p class="watchlist-item-company">${item.company_name || item.name || item.ticker}</p>
                        </div>
                        <div class="watchlist-item-price">
                            <div class="watchlist-item-current-price stock-price">
                                ${StockScannerAPI.Utils.formatCurrency(item.current_price)}
                            </div>
                            <div class="watchlist-item-change stock-change ${StockScannerAPI.Utils.getPriceChangeClass(change)}">
                                ${StockScannerAPI.Utils.formatCurrency(change)} (${StockScannerAPI.Utils.formatPercentage(changePercent)})
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            
            if (data.data.length > 5) {
                html += `<div class="text-center mt-4">
                    <a href="/watchlist" class="btn btn-outline-primary btn-sm">View All ${data.data.length} Items</a>
                </div>`;
            }

            $container.html(html);
        },

        // Initialize market overview
        initMarketOverview: function() {
            const $container = $('#market-overview');
            if ($container.length === 0) return;

            StockScannerAPI.Utils.showLoading($container);

            StockScannerAPI.Stock.getMarketOverview()
                .then(data => {
                    this.renderMarketOverview($container, data);
                })
                .catch(error => {
                    console.error('Market overview error:', error);
                    StockScannerAPI.Utils.showError($container, 'Failed to load market data');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading($container);
                });
        },

        // Render market overview
        renderMarketOverview: function($container, data) {
            if (!data || !data.success) {
                $container.html('<p class="text-muted">Market data unavailable</p>');
                return;
            }

            const overview = data.market_overview || {};
            const topPerformers = data.top_performers || {};

            let html = `
                <div class="market-overview-stats">
                    <div class="market-stat">
                        <div class="market-stat-label">Total Stocks</div>
                        <div class="market-stat-value">${overview.total_stocks || 0}</div>
                    </div>
                    <div class="market-stat">
                        <div class="market-stat-label">Gainers</div>
                        <div class="market-stat-value text-success">${overview.gainers || 0}</div>
                    </div>
                    <div class="market-stat">
                        <div class="market-stat-label">Losers</div>
                        <div class="market-stat-value text-danger">${overview.losers || 0}</div>
                    </div>
                    <div class="market-stat">
                        <div class="market-stat-label">Unchanged</div>
                        <div class="market-stat-value">${overview.unchanged || 0}</div>
                    </div>
                </div>
            `;

            // Top performer
            if (topPerformers.top_gainer) {
                const gainer = topPerformers.top_gainer;
                html += `
                    <div class="top-performer">
                        <h5>Top Gainer</h5>
                        <div class="performer-item">
                            <strong>${gainer.ticker}</strong> - ${gainer.company_name || gainer.ticker}
                            <span class="text-success">${StockScannerAPI.Utils.formatPercentage(gainer.price_change_percent)}</span>
                        </div>
                    </div>
                `;
            }

            $container.html(html);
        },

        // Initialize news feed
        initNewsMedia: function() {
            const $container = $('#news-feed');
            if ($container.length === 0) return;

            StockScannerAPI.Utils.showLoading($container);

            StockScannerAPI.News.getPersonalizedNews(5)
                .then(data => {
                    this.renderNewsFeed($container, data);
                })
                .catch(error => {
                    console.error('News feed error:', error);
                    // Fallback to general news
                    return StockScannerAPI.News.getNews(5);
                })
                .then(data => {
                    if (data) this.renderNewsFeed($container, data);
                })
                .catch(error => {
                    console.error('News feed fallback error:', error);
                    StockScannerAPI.Utils.showError($container, 'Failed to load news');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading($container);
                });
        },

        // Render news feed
        renderNewsFeed: function($container, data) {
            if (!data || !data.success || !data.data || data.data.length === 0) {
                $container.html('<p class="text-muted">No news articles found</p>');
                return;
            }

            let html = '<div class="news-feed">';

            data.data.forEach(article => {
                const publishedAt = new Date(article.published_at).toLocaleDateString();
                const sentiment = article.sentiment_score > 0.1 ? 'positive' : 
                                 article.sentiment_score < -0.1 ? 'negative' : 'neutral';

                html += `
                    <div class="news-item">
                        <div class="news-item-content">
                            <h6 class="news-item-title">
                                <a href="${article.url}" target="_blank">${article.title}</a>
                            </h6>
                            <div class="news-item-meta">
                                <span>${article.source}</span>
                                <span>${publishedAt}</span>
                                ${article.related_stocks ? 
                                    `<span>Related: ${article.related_stocks.slice(0, 3).join(', ')}</span>` : ''
                                }
                                <span class="news-item-sentiment ${sentiment}">${sentiment}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            $container.html(html);
        },

        // Initialize quick actions
        initQuickActions: function() {
            const $container = $('#quick-actions');
            if ($container.length === 0) return;

            const html = `
                <div class="quick-actions">
                    <a href="/stock-lookup" class="quick-action-btn">
                        <i class="fas fa-search quick-action-icon"></i>
                        Look Up Stock
                    </a>
                    <a href="/portfolio" class="quick-action-btn">
                        <i class="fas fa-chart-line quick-action-icon"></i>
                        Manage Portfolio
                    </a>
                    <a href="/watchlist" class="quick-action-btn">
                        <i class="fas fa-eye quick-action-icon"></i>
                        View Watchlist
                    </a>
                    <button class="quick-action-btn" id="create-alert-btn">
                        <i class="fas fa-bell quick-action-icon"></i>
                        Create Alert
                    </button>
                </div>
            `;

            $container.html(html);
        },

        // Initialize auto-refresh timer
        initRefreshTimer: function() {
            // Refresh dashboard data every 2 minutes
            setInterval(() => {
                this.refreshData();
            }, 120000);
        },

        // Refresh all dashboard data
        refreshData: function() {
            this.initPortfolioSummary();
            this.initWatchlist();
            this.initMarketOverview();
        },

        // Bind event handlers
        bindEvents: function() {
            // Refresh button
            $(document).on('click', '[data-action="refresh-dashboard"]', (e) => {
                e.preventDefault();
                this.refreshData();
                StockScannerAPI.Toast.show('Dashboard refreshed', 'success');
            });

            // Quick stock lookup
            $(document).on('submit', '#quick-stock-search', (e) => {
                e.preventDefault();
                const ticker = $(e.target).find('input[name="ticker"]').val().trim();
                if (ticker) {
                    window.location.href = `/stock-lookup/?ticker=${encodeURIComponent(ticker)}`;
                }
            });

            // Create alert modal
            $(document).on('click', '#create-alert-btn', () => {
                this.showCreateAlertModal();
            });

            // Watchlist item click
            $(document).on('click', '.watchlist-item', function() {
                const ticker = $(this).data('ticker');
                if (ticker) {
                    window.location.href = `/stock-lookup/?ticker=${ticker}`;
                }
            });

            // Error retry buttons
            $(document).on('click', '.error-retry', (e) => {
                const $container = $(e.target).closest('[id]');
                const containerId = $container.attr('id');
                
                switch (containerId) {
                    case 'portfolio-summary':
                        this.initPortfolioSummary();
                        break;
                    case 'watchlist-preview':
                        this.initWatchlist();
                        break;
                    case 'market-overview':
                        this.initMarketOverview();
                        break;
                    case 'news-feed':
                        this.initNewsFeed();
                        break;
                }
            });
        },

        // Show create alert modal
        showCreateAlertModal: function() {
            const modalHtml = `
                <div class="modal fade" id="createAlertModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Create Price Alert</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="create-alert-form">
                                    <div class="mb-3">
                                        <label for="alert-ticker" class="form-label">Stock Ticker</label>
                                        <input type="text" class="form-control" id="alert-ticker" placeholder="e.g., AAPL" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="alert-price" class="form-label">Target Price</label>
                                        <input type="number" class="form-control" id="alert-price" step="0.01" placeholder="0.00" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="alert-condition" class="form-label">Condition</label>
                                        <select class="form-select" id="alert-condition" required>
                                            <option value="">Select condition</option>
                                            <option value="above">Price rises above</option>
                                            <option value="below">Price falls below</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="alert-email" class="form-label">Email Address</label>
                                        <input type="email" class="form-control" id="alert-email" placeholder="your@email.com" required>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="save-alert-btn">Create Alert</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal
            $('#createAlertModal').remove();
            
            // Add modal to page
            $('body').append(modalHtml);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('createAlertModal'));
            modal.show();

            // Handle form submission
            $('#save-alert-btn').on('click', () => {
                this.submitCreateAlert();
            });
        },

        // Submit create alert form
        submitCreateAlert: function() {
            const ticker = $('#alert-ticker').val().trim().toUpperCase();
            const price = parseFloat($('#alert-price').val());
            const condition = $('#alert-condition').val();
            const email = $('#alert-email').val().trim();

            if (!ticker || !price || !condition || !email) {
                StockScannerAPI.Toast.show('Please fill in all fields', 'error');
                return;
            }

            const validTicker = StockScannerAPI.Utils.validateTicker(ticker);
            if (!validTicker) {
                StockScannerAPI.Toast.show('Invalid ticker symbol', 'error');
                return;
            }

            $('#save-alert-btn').prop('disabled', true).text('Creating...');

            StockScannerAPI.Alerts.createAlert(validTicker, price, condition, email)
                .then(data => {
                    StockScannerAPI.Toast.show('Alert created successfully!', 'success');
                    $('#createAlertModal').modal('hide');
                })
                .catch(error => {
                    console.error('Create alert error:', error);
                    StockScannerAPI.Toast.show('Failed to create alert', 'error');
                })
                .finally(() => {
                    $('#save-alert-btn').prop('disabled', false).text('Create Alert');
                });
        }
    };

    // Initialize dashboard when document is ready
    $(document).ready(function() {
        if ($('body').hasClass('page-template-page-dashboard')) {
            Dashboard.init();
        }
    });

    // Export to global scope
    window.StockScannerDashboard = Dashboard;

})(jQuery);