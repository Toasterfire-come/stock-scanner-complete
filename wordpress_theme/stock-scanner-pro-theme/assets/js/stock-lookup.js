/**
 * Stock Scanner Pro - Stock Lookup Functionality
 */

(function() {
    'use strict';

    const StockLookup = {
        currentTicker: null,
        searchTimeout: null,
        priceChart: null,

        init: function() {
            this.initSearchForm();
            this.initTabs();
            this.initModals();
            this.bindEvents();
            this.loadPopularStocks();
        },

        // Initialize search form
        initSearchForm: function() {
            const form = document.getElementById('stock-search-form');
            const input = document.getElementById('stock-search-input');
            
            if (!form || !input) return;

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const ticker = input.value.trim().toUpperCase();
                if (ticker) {
                    this.searchStock(ticker);
                }
            });

            // Auto-suggest on input
            input.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                this.handleSearchSuggestions(query);
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('#stock-search-form')) {
                    this.hideSuggestions();
                }
            });
        },

        // Handle search suggestions
        handleSearchSuggestions: function(query) {
            clearTimeout(this.searchTimeout);
            
            if (query.length < 1) {
                this.hideSuggestions();
                return;
            }

            this.searchTimeout = setTimeout(() => {
                this.fetchSearchSuggestions(query);
            }, 300);
        },

        // Fetch search suggestions
        fetchSearchSuggestions: function(query) {
            const suggestionsContainer = document.getElementById('search-suggestions');
            if (!suggestionsContainer) return;

            StockScannerAPI.Stock.searchStocks(query, 10)
                .then(data => {
                    this.renderSearchSuggestions(suggestionsContainer, data);
                })
                .catch(error => {
                    console.error('Search suggestions error:', error);
                    this.hideSuggestions();
                });
        },

        // Render search suggestions
        renderSearchSuggestions: function(container, data) {
            if (!data || !data.results || data.results.length === 0) {
                this.hideSuggestions();
                return;
            }

            let html = '';
            data.results.slice(0, 8).forEach(stock => {
                html += `
                    <div class="suggestion-item" data-ticker="${stock.ticker}">
                        <div class="suggestion-info">
                            <div class="suggestion-ticker">${stock.ticker}</div>
                            <div class="suggestion-company">${stock.company_name || stock.name || stock.ticker}</div>
                        </div>
                        <div class="suggestion-price">
                            ${stock.current_price ? StockScannerAPI.Utils.formatCurrency(stock.current_price) : ''}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
            container.style.display = 'block';
        },

        // Hide search suggestions
        hideSuggestions: function() {
            const suggestionsContainer = document.getElementById('search-suggestions');
            if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
                suggestionsContainer.innerHTML = '';
            }
        },

        // Search for stock
        searchStock: function(ticker) {
            const validTicker = StockScannerAPI.Utils.validateTicker(ticker);
            if (!validTicker) {
                StockScannerAPI.Toast.show('Invalid ticker symbol', 'error');
                return;
            }

            this.currentTicker = validTicker;
            this.hideSuggestions();
            this.showStockDetails();
            this.loadStockData(validTicker);
        },

        // Show stock details section
        showStockDetails: function() {
            const section = document.getElementById('stock-details-section');
            if (section) {
                section.style.display = 'block';
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        },

        // Load stock data
        loadStockData: function(ticker) {
            const headerContainer = document.getElementById('stock-header');
            const actionsContainer = document.getElementById('stock-actions');
            const statsContainer = document.getElementById('key-statistics');
            
            if (headerContainer) {
                StockScannerAPI.Utils.showLoading(headerContainer, 'Loading stock data...');
            }

            StockScannerAPI.Stock.getStock(ticker)
                .then(data => {
                    if (data && data.success && data.data) {
                        const stockData = data.data;
                        this.renderStockHeader(headerContainer, stockData);
                        this.renderStockActions(actionsContainer, stockData);
                        this.renderKeyStatistics(statsContainer, stockData);
                        this.initPriceChart(stockData);
                        this.loadStockNews(ticker);
                        this.loadFinancialData(ticker);
                    } else {
                        StockScannerAPI.Utils.showError(headerContainer, 'Stock not found or data unavailable');
                    }
                })
                .catch(error => {
                    console.error('Stock data error:', error);
                    StockScannerAPI.Utils.showError(headerContainer, 'Failed to load stock data');
                })
                .finally(() => {
                    if (headerContainer) {
                        StockScannerAPI.Utils.hideLoading(headerContainer);
                    }
                });
        },

        // Render stock header
        renderStockHeader: function(container, stockData) {
            if (!container || !stockData) return;

            const change = stockData.price_change_today || 0;
            const changePercent = stockData.price_change_percent || 0;
            const changeClass = StockScannerAPI.Utils.getPriceChangeClass(change);

            const html = `
                <div class="stock-header-content">
                    <div class="stock-title">
                        <h2 class="stock-ticker">${stockData.ticker}</h2>
                        <div class="stock-company">${stockData.company_name || stockData.name || stockData.ticker}</div>
                    </div>
                    <div class="stock-price-info">
                        <div class="current-price">${StockScannerAPI.Utils.formatCurrency(stockData.current_price || stockData.price)}</div>
                        <div class="price-change ${changeClass}">
                            ${StockScannerAPI.Utils.formatCurrency(change)} 
                            (${StockScannerAPI.Utils.formatPercentage(changePercent)})
                        </div>
                        <div class="market-status">
                            <span class="status-indicator ${stockData.market_open ? 'open' : 'closed'}"></span>
                            Market ${stockData.market_open ? 'Open' : 'Closed'}
                        </div>
                    </div>
                </div>
            `;

            container.innerHTML = html;
        },

        // Render stock actions
        renderStockActions: function(container, stockData) {
            if (!container || !stockData) return;

            const html = `
                <div class="stock-actions-buttons">
                    <button class="action-btn btn-primary" id="add-to-portfolio-btn" data-ticker="${stockData.ticker}">
                        <i class="fas fa-plus mr-2"></i>
                        Add to Portfolio
                    </button>
                    <button class="action-btn btn-outline-primary" id="add-to-watchlist-btn" data-ticker="${stockData.ticker}">
                        <i class="fas fa-eye mr-2"></i>
                        Add to Watchlist
                    </button>
                    <button class="action-btn btn-outline-secondary" id="create-alert-btn" data-ticker="${stockData.ticker}">
                        <i class="fas fa-bell mr-2"></i>
                        Create Alert
                    </button>
                    <button class="action-btn btn-outline-secondary" id="share-stock-btn" data-ticker="${stockData.ticker}">
                        <i class="fas fa-share mr-2"></i>
                        Share
                    </button>
                </div>
            `;

            container.innerHTML = html;
        },

        // Render key statistics
        renderKeyStatistics: function(container, stockData) {
            if (!container || !stockData) return;

            const stats = [
                { label: 'Market Cap', value: StockScannerAPI.Utils.formatCurrency(stockData.market_cap || 0) },
                { label: 'P/E Ratio', value: stockData.pe_ratio || 'N/A' },
                { label: '52W High', value: StockScannerAPI.Utils.formatCurrency(stockData.week_52_high || 0) },
                { label: '52W Low', value: StockScannerAPI.Utils.formatCurrency(stockData.week_52_low || 0) },
                { label: 'Volume', value: StockScannerAPI.Utils.formatNumber(stockData.volume || 0) },
                { label: 'Avg Volume', value: StockScannerAPI.Utils.formatNumber(stockData.avg_volume || 0) },
                { label: 'Dividend Yield', value: stockData.dividend_yield ? `${stockData.dividend_yield}%` : 'N/A' },
                { label: 'Beta', value: stockData.beta || 'N/A' }
            ];

            let html = '<div class="key-stats-grid">';
            stats.forEach(stat => {
                html += `
                    <div class="stat-item">
                        <div class="stat-label">${stat.label}</div>
                        <div class="stat-value">${stat.value}</div>
                    </div>
                `;
            });
            html += '</div>';

            container.innerHTML = html;
        },

        // Initialize price chart
        initPriceChart: function(stockData) {
            const canvas = document.getElementById('price-chart');
            if (!canvas) return;

            // Destroy existing chart
            if (this.priceChart) {
                this.priceChart.destroy();
            }

            const ctx = canvas.getContext('2d');
            
            // Mock price data - in real implementation, this would come from API
            const priceData = this.generateMockPriceData(stockData);

            this.priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: priceData.labels,
                    datasets: [{
                        label: `${stockData.ticker} Price`,
                        data: priceData.prices,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        y: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return StockScannerAPI.Utils.formatCurrency(value);
                                }
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
        },

        // Generate mock price data
        generateMockPriceData: function(stockData) {
            const currentPrice = stockData.current_price || 100;
            const labels = [];
            const prices = [];
            const dataPoints = 30;

            for (let i = dataPoints; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString());
                
                // Generate realistic price variation
                const variation = (Math.random() - 0.5) * 0.1; // ±5% variation
                const price = currentPrice * (1 + variation * (i / dataPoints));
                prices.push(Math.max(price, currentPrice * 0.8)); // Minimum 80% of current price
            }

            return { labels, prices };
        },

        // Load stock news
        loadStockNews: function(ticker) {
            const container = document.getElementById('stock-news');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading news...');

            StockScannerAPI.News.getStockNews(ticker, 10)
                .then(data => {
                    this.renderStockNews(container, data);
                })
                .catch(error => {
                    console.error('Stock news error:', error);
                    StockScannerAPI.Utils.showError(container, 'Failed to load news');
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading(container);
                });
        },

        // Render stock news
        renderStockNews: function(container, data) {
            if (!data || !data.results || data.results.length === 0) {
                container.innerHTML = '<p class="text-muted">No news articles found for this stock.</p>';
                return;
            }

            let html = '';
            data.results.forEach(article => {
                const publishedAt = new Date(article.published_at).toLocaleDateString();
                
                html += `
                    <div class="news-article">
                        <h4 class="news-title">
                            <a href="${article.url}" target="_blank" rel="noopener">${article.title}</a>
                        </h4>
                        <div class="news-meta">
                            <span class="news-source">${article.source}</span>
                            <span class="news-date">${publishedAt}</span>
                            ${article.sentiment_score ? 
                                `<span class="news-sentiment ${article.sentiment_score > 0 ? 'positive' : article.sentiment_score < 0 ? 'negative' : 'neutral'}">
                                    ${article.sentiment_score > 0 ? 'Positive' : article.sentiment_score < 0 ? 'Negative' : 'Neutral'}
                                </span>` : ''
                            }
                        </div>
                        ${article.summary ? `<p class="news-summary">${article.summary}</p>` : ''}
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Load financial data
        loadFinancialData: function(ticker) {
            const container = document.getElementById('financial-data');
            if (!container) return;

            StockScannerAPI.Utils.showLoading(container, 'Loading financial data...');

            // Mock financial data
            setTimeout(() => {
                const financials = {
                    revenue: 274500000000,
                    netIncome: 57400000000,
                    totalAssets: 381200000000,
                    totalDebt: 131440000000,
                    shareholderEquity: 138000000000,
                    operatingCashFlow: 80700000000
                };

                const html = `
                    <div class="financial-metrics">
                        <div class="financial-metric">
                            <div class="metric-label">Revenue (TTM)</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.revenue)}</div>
                        </div>
                        <div class="financial-metric">
                            <div class="metric-label">Net Income (TTM)</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.netIncome)}</div>
                        </div>
                        <div class="financial-metric">
                            <div class="metric-label">Total Assets</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.totalAssets)}</div>
                        </div>
                        <div class="financial-metric">
                            <div class="metric-label">Total Debt</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.totalDebt)}</div>
                        </div>
                        <div class="financial-metric">
                            <div class="metric-label">Shareholder Equity</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.shareholderEquity)}</div>
                        </div>
                        <div class="financial-metric">
                            <div class="metric-label">Operating Cash Flow</div>
                            <div class="metric-value">${StockScannerAPI.Utils.formatCurrency(financials.operatingCashFlow)}</div>
                        </div>
                    </div>
                `;

                container.innerHTML = html;
                StockScannerAPI.Utils.hideLoading(container);
            }, 1500);
        },

        // Load popular stocks
        loadPopularStocks: function() {
            const container = document.getElementById('popular-stocks');
            if (!container) return;

            StockScannerAPI.Stock.getTrending(12)
                .then(data => {
                    this.renderPopularStocks(container, data);
                })
                .catch(error => {
                    console.error('Popular stocks error:', error);
                    container.innerHTML = '<p class="text-muted">Failed to load popular stocks</p>';
                });
        },

        // Render popular stocks
        renderPopularStocks: function(container, data) {
            if (!data || !data.results || data.results.length === 0) {
                container.innerHTML = '<p class="text-muted">No popular stocks data available</p>';
                return;
            }

            let html = '';
            data.results.forEach(stock => {
                const change = stock.price_change_today || 0;
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(change);
                
                html += `
                    <div class="popular-stock-card" data-ticker="${stock.ticker}">
                        <div class="stock-symbol">${stock.ticker}</div>
                        <div class="stock-price">${StockScannerAPI.Utils.formatCurrency(stock.current_price || stock.price)}</div>
                        <div class="stock-change ${changeClass}">
                            ${StockScannerAPI.Utils.formatPercentage(stock.price_change_percent || stock.change_percent)}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Initialize tabs
        initTabs: function() {
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const targetTab = button.dataset.tab;
                    
                    // Remove active class from all tabs and contents
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));
                    
                    // Add active class to clicked tab and corresponding content
                    button.classList.add('active');
                    const targetContent = document.getElementById(`${targetTab}-tab`);
                    if (targetContent) {
                        targetContent.classList.add('active');
                    }
                });
            });
        },

        // Initialize modals
        initModals: function() {
            // Add to portfolio modal handling
            document.addEventListener('click', (e) => {
                if (e.target.matches('#add-to-portfolio-btn') || 
                    e.target.closest('#add-to-portfolio-btn')) {
                    const ticker = e.target.dataset.ticker || e.target.closest('[data-ticker]')?.dataset.ticker;
                    if (ticker) {
                        this.showAddToPortfolioModal(ticker);
                    }
                }
            });

            // Add to watchlist modal handling
            document.addEventListener('click', (e) => {
                if (e.target.matches('#add-to-watchlist-btn') || 
                    e.target.closest('#add-to-watchlist-btn')) {
                    const ticker = e.target.dataset.ticker || e.target.closest('[data-ticker]')?.dataset.ticker;
                    if (ticker) {
                        this.showAddToWatchlistModal(ticker);
                    }
                }
            });
        },

        // Show add to portfolio modal
        showAddToPortfolioModal: function(ticker) {
            const modal = document.getElementById('addToPortfolioModal');
            if (!modal) return;

            document.getElementById('portfolio-ticker').value = ticker;
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('add-to-portfolio-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitAddToPortfolio();
            };
        },

        // Show add to watchlist modal
        showAddToWatchlistModal: function(ticker) {
            const modal = document.getElementById('addToWatchlistModal');
            if (!modal) return;

            document.getElementById('watchlist-ticker').value = ticker;
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('add-to-watchlist-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitAddToWatchlist();
            };
        },

        // Submit add to portfolio
        submitAddToPortfolio: function() {
            const ticker = document.getElementById('portfolio-ticker').value;
            const shares = parseFloat(document.getElementById('portfolio-shares').value);
            const costBasis = parseFloat(document.getElementById('portfolio-cost-basis').value);
            const purchaseDate = document.getElementById('portfolio-purchase-date').value;

            if (!ticker || !shares || !costBasis) {
                StockScannerAPI.Toast.show('Please fill in all required fields', 'error');
                return;
            }

            StockScannerAPI.Portfolio.addToPortfolio(ticker, shares, costBasis, purchaseDate)
                .then(data => {
                    StockScannerAPI.Toast.show('Stock added to portfolio successfully!', 'success');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addToPortfolioModal'));
                    modal.hide();
                })
                .catch(error => {
                    console.error('Add to portfolio error:', error);
                    StockScannerAPI.Toast.show('Failed to add stock to portfolio', 'error');
                });
        },

        // Submit add to watchlist
        submitAddToWatchlist: function() {
            const ticker = document.getElementById('watchlist-ticker').value;
            const category = document.getElementById('watchlist-category').value;
            const notes = document.getElementById('watchlist-notes').value;

            if (!ticker) {
                StockScannerAPI.Toast.show('Stock symbol is required', 'error');
                return;
            }

            StockScannerAPI.Watchlist.addToWatchlist(ticker, notes, category)
                .then(data => {
                    StockScannerAPI.Toast.show('Stock added to watchlist successfully!', 'success');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addToWatchlistModal'));
                    modal.hide();
                })
                .catch(error => {
                    console.error('Add to watchlist error:', error);
                    StockScannerAPI.Toast.show('Failed to add stock to watchlist', 'error');
                });
        },

        // Bind event handlers
        bindEvents: function() {
            // Chart timeframe buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.timeframe-btn')) {
                    const period = e.target.dataset.period;
                    const buttons = document.querySelectorAll('.timeframe-btn');
                    
                    buttons.forEach(btn => btn.classList.remove('active'));
                    e.target.classList.add('active');
                    
                    // Update chart for the selected period
                    if (this.currentTicker) {
                        this.updateChartPeriod(period);
                    }
                }
            });

            // Suggestion clicks
            document.addEventListener('click', (e) => {
                const suggestion = e.target.closest('.suggestion-item');
                if (suggestion) {
                    const ticker = suggestion.dataset.ticker;
                    document.getElementById('stock-search-input').value = ticker;
                    this.searchStock(ticker);
                }
            });

            // Popular stock clicks
            document.addEventListener('click', (e) => {
                const popularStock = e.target.closest('.popular-stock-card');
                if (popularStock) {
                    const ticker = popularStock.dataset.ticker;
                    document.getElementById('stock-search-input').value = ticker;
                    this.searchStock(ticker);
                }
            });
        },

        // Update chart period
        updateChartPeriod: function(period) {
            if (!this.priceChart || !this.currentTicker) return;

            // In real implementation, this would fetch new data for the period
            StockScannerAPI.Toast.show(`Loading ${period} chart data...`, 'info');
        }
    };

    // Export to global scope
    window.StockScannerLookup = StockLookup;

    // Auto-initialize if on stock lookup page
    document.addEventListener('DOMContentLoaded', function() {
        if (document.body.classList.contains('page-template-page-stock-lookup')) {
            StockLookup.init();
        }
    });

})();