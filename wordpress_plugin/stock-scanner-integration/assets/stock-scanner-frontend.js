/**
 * Stock Scanner Frontend Integration
 * Handles email signups, stock filtering, detailed lookup, and news display
 * Full backend integration with Django API
 */

class StockScannerFrontend {
    constructor() {
        this.apiBase = '/api/';
        this.init();
    }

    init() {
        this.initEmailSignup();
        this.initStockFilter();
        this.initStockLookup();
        this.initNewsDisplay();
        this.initScrollAnimations();
        this.initMobileMenu();
        this.initTaxCalculator();
    }

    // 1. EMAIL SIGNUP FUNCTIONALITY
    initEmailSignup() {
        // Create email signup forms on relevant pages
        this.createEmailSignupForms();
        
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('email-signup-form')) {
                e.preventDefault();
                this.handleEmailSignup(e.target);
            }
        });
    }

    createEmailSignupForms() {
        const emailPages = ['email-stock-lists', 'popular-stock-lists', 'all-stock-lists'];
        const currentPage = document.body.classList;
        
        emailPages.forEach(page => {
            if (document.body.classList.contains(`page-${page}`)) {
                this.insertEmailSignupForm(page);
            }
        });
    }

    insertEmailSignupForm(pageType) {
        const formHTML = `
            <div class="card email-signup-card animate-fade-in">
                <div class="card-header">
                    <h4 class="card-title">📧 Subscribe to Stock Alerts</h4>
                    <p class="card-subtitle">Get notified of market opportunities in real-time</p>
                </div>
                <div class="card-body">
                    <form class="email-signup-form" data-category="${pageType}">
                        <div class="d-flex gap-md flex-wrap">
                            <div class="form-group flex-grow-1">
                                <input type="email" class="form-control" name="email" placeholder="Enter your email address" required>
                            </div>
                            <div class="form-group">
                                <select class="form-control form-select" name="category">
                                    <option value="popular">Popular Lists</option>
                                    <option value="all">All Lists</option>
                                    <option value="earnings">Earnings Alerts</option>
                                    <option value="breakouts">Breakout Stocks</option>
                                    <option value="dividends">Dividend Stocks</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <button type="submit" class="btn btn-primary">
                                    <span>Subscribe</span>
                                </button>
                            </div>
                        </div>
                        <div class="form-text">
                            📊 Join 50,000+ traders getting real-time alerts. Unsubscribe anytime.
                        </div>
                        <div class="signup-message"></div>
                    </form>
                </div>
            </div>
        `;

        // Insert after the page header
        const pageHeader = document.querySelector('.page-header');
        if (pageHeader) {
            pageHeader.insertAdjacentHTML('afterend', formHTML);
        }
    }

    async handleEmailSignup(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const messageDiv = form.querySelector('.signup-message');
        
        // Loading state
        submitBtn.innerHTML = '<span class="animate-spin">⏳</span> Subscribing...';
        submitBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}email-signup/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: formData.get('email'),
                    category: formData.get('category')
                })
            });

            const data = await response.json();

            if (data.success) {
                messageDiv.innerHTML = `
                    <div class="alert alert-success animate-fade-in">
                        ✅ ${data.message}
                    </div>
                `;
                form.reset();
            } else {
                throw new Error(data.message);
            }

        } catch (error) {
            messageDiv.innerHTML = `
                <div class="alert alert-error animate-fade-in">
                    ❌ ${error.message || 'Signup failed. Please try again.'}
                </div>
            `;
        } finally {
            submitBtn.innerHTML = '<span>Subscribe</span>';
            submitBtn.disabled = false;
        }
    }

    // 2. STOCK FILTER FUNCTIONALITY
    initStockFilter() {
        this.createStockFilterInterface();
        
        // Handle filter changes
        document.addEventListener('change', (e) => {
            if (e.target.closest('.stock-filter-form')) {
                this.handleStockFilter();
            }
        });

        document.addEventListener('input', (e) => {
            if (e.target.closest('.stock-filter-form')) {
                this.debounce(() => this.handleStockFilter(), 500)();
            }
        });
    }

    createStockFilterInterface() {
        if (document.body.classList.contains('page-filter-and-scrapper-pages') || 
            document.body.classList.contains('page-stock-search')) {
            this.insertStockFilterForm();
        }
    }

    insertStockFilterForm() {
        const filterHTML = `
            <div class="card stock-filter-card">
                <div class="card-header">
                    <h4 class="card-title">🔍 Advanced Stock Filter</h4>
                    <p class="card-subtitle">Filter stocks by price, volume, market cap, and more</p>
                </div>
                <div class="card-body">
                    <form class="stock-filter-form">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label class="form-label">Price Range</label>
                                    <div class="d-flex gap-sm">
                                        <input type="number" class="form-control" name="min_price" placeholder="Min $" step="0.01">
                                        <input type="number" class="form-control" name="max_price" placeholder="Max $" step="0.01">
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label class="form-label">Volume Range</label>
                                    <div class="d-flex gap-sm">
                                        <input type="number" class="form-control" name="min_volume" placeholder="Min Volume">
                                        <input type="number" class="form-control" name="max_volume" placeholder="Max Volume">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label class="form-label">Market Cap Range</label>
                                    <div class="d-flex gap-sm">
                                        <input type="number" class="form-control" name="min_market_cap" placeholder="Min Market Cap">
                                        <input type="number" class="form-control" name="max_market_cap" placeholder="Max Market Cap">
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label class="form-label">P/E Ratio Range</label>
                                    <div class="d-flex gap-sm">
                                        <input type="number" class="form-control" name="min_pe" placeholder="Min P/E" step="0.1">
                                        <input type="number" class="form-control" name="max_pe" placeholder="Max P/E" step="0.1">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="form-label">Sector</label>
                                    <input type="text" class="form-control" name="sector" placeholder="e.g., Technology">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="form-label">Sort By</label>
                                    <select class="form-control form-select" name="sort_by">
                                        <option value="current_price">Price</option>
                                        <option value="volume_today">Volume</option>
                                        <option value="market_cap">Market Cap</option>
                                        <option value="pe_ratio">P/E Ratio</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="form-label">Order</label>
                                    <select class="form-control form-select" name="sort_order">
                                        <option value="desc">High to Low</option>
                                        <option value="asc">Low to High</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <button type="button" class="btn btn-primary" onclick="stockScanner.handleStockFilter()">
                                <span>🔍 Filter Stocks</span>
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="stockScanner.clearStockFilter()">
                                <span>Clear Filters</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <div id="filter-results" class="filter-results"></div>
        `;

        const pageHeader = document.querySelector('.page-header');
        if (pageHeader) {
            pageHeader.insertAdjacentHTML('afterend', filterHTML);
        }
    }

    async handleStockFilter() {
        const form = document.querySelector('.stock-filter-form');
        const resultsDiv = document.getElementById('filter-results');
        
        if (!form || !resultsDiv) return;

        const formData = new FormData(form);
        const params = new URLSearchParams();
        
        // Build query parameters
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                params.append(key, value);
            }
        }

        // Show loading
        resultsDiv.innerHTML = `
            <div class="card loading">
                <div class="card-body text-center">
                    <div class="animate-spin">⏳</div>
                    <p>Filtering stocks...</p>
                </div>
            </div>
        `;

        try {
            const response = await fetch(`${this.apiBase}stocks/filter/?${params}`);
            const data = await response.json();

            if (data.success) {
                this.displayFilterResults(data.stocks, data.count, data.filters_applied);
            } else {
                throw new Error(data.message);
            }

        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="card-body text-center text-danger">
                        ❌ ${error.message || 'Failed to filter stocks'}
                    </div>
                </div>
            `;
        }
    }

    displayFilterResults(stocks, count, filters) {
        const resultsDiv = document.getElementById('filter-results');
        
        if (stocks.length === 0) {
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="card-body text-center">
                        <h4>📭 No Stocks Found</h4>
                        <p>Try adjusting your filter criteria.</p>
                    </div>
                </div>
            `;
            return;
        }

        const stocksHTML = stocks.map((stock, index) => `
            <div class="card stock-card animate-fade-in animate-delay-${Math.min(index + 1, 5)}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="card-title">${stock.ticker}</h5>
                            <p class="card-subtitle">${stock.company_name}</p>
                        </div>
                        <div class="text-right">
                            <div class="stock-price">$${stock.current_price}</div>
                            <div class="stock-volume">${this.formatNumber(stock.volume_today)} vol</div>
                        </div>
                    </div>
                    <div class="stock-metrics">
                        ${stock.market_cap ? `<span class="metric">MC: ${this.formatMarketCap(stock.market_cap)}</span>` : ''}
                        ${stock.pe_ratio ? `<span class="metric">P/E: ${stock.pe_ratio.toFixed(2)}</span>` : ''}
                        ${stock.dvav ? `<span class="metric">DVAV: ${stock.dvav.toFixed(2)}</span>` : ''}
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary" onclick="stockScanner.showStockDetails('${stock.ticker}')">
                            View Details
                        </button>
                        <small class="text-muted">${stock.last_update ? new Date(stock.last_update).toLocaleDateString() : ''}</small>
                    </div>
                </div>
            </div>
        `).join('');

        resultsDiv.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h4 class="card-title">📊 Filter Results</h4>
                    <p class="card-subtitle">Found ${count} stocks matching your criteria</p>
                </div>
            </div>
            <div class="stock-grid">
                ${stocksHTML}
            </div>
        `;
    }

    clearStockFilter() {
        document.querySelector('.stock-filter-form').reset();
        document.getElementById('filter-results').innerHTML = '';
    }

    // 3. DETAILED STOCK LOOKUP
    initStockLookup() {
        this.createStockLookupInterface();
        
        // Handle lookup submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('stock-lookup-form')) {
                e.preventDefault();
                this.handleStockLookup(e.target);
            }
        });
    }

    createStockLookupInterface() {
        // Add lookup form to relevant pages
        if (document.body.classList.contains('page-stock-search') || 
            document.body.classList.contains('page-personalized-stock-finder')) {
            this.insertStockLookupForm();
        }
    }

    insertStockLookupForm() {
        const lookupHTML = `
            <div class="card stock-lookup-card">
                <div class="card-header">
                    <h4 class="card-title">🔎 Stock Lookup</h4>
                    <p class="card-subtitle">Get comprehensive data for any stock ticker</p>
                </div>
                <div class="card-body">
                    <form class="stock-lookup-form">
                        <div class="d-flex gap-md">
                            <div class="form-group flex-grow-1">
                                <input type="text" class="form-control" name="ticker" placeholder="Enter stock ticker (e.g., AAPL, MSFT)" required style="text-transform: uppercase;">
                            </div>
                            <div class="form-group">
                                <button type="submit" class="btn btn-primary">
                                    <span>Lookup Stock</span>
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div id="lookup-results" class="lookup-results"></div>
        `;

        const pageContent = document.querySelector('.site-main .container');
        if (pageContent) {
            pageContent.insertAdjacentHTML('afterbegin', lookupHTML);
        }
    }

    async handleStockLookup(form) {
        const formData = new FormData(form);
        const ticker = formData.get('ticker').toUpperCase().trim();
        const submitBtn = form.querySelector('button[type="submit"]');
        const resultsDiv = document.getElementById('lookup-results');

        if (!ticker) return;

        // Loading state
        submitBtn.innerHTML = '<span class="animate-spin">⏳</span> Looking up...';
        submitBtn.disabled = true;

        resultsDiv.innerHTML = `
            <div class="card loading">
                <div class="card-body text-center">
                    <div class="animate-spin" style="font-size: 2rem;">📈</div>
                    <p>Fetching comprehensive data for ${ticker}...</p>
                </div>
            </div>
        `;

        try {
            const response = await fetch(`${this.apiBase}stocks/lookup/${ticker}/`);
            const result = await response.json();

            if (result.success) {
                this.displayStockDetails(result.data);
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="card-body text-center text-danger">
                        ❌ ${error.message || 'Failed to lookup stock'}
                    </div>
                </div>
            `;
        } finally {
            submitBtn.innerHTML = '<span>Lookup Stock</span>';
            submitBtn.disabled = false;
        }
    }

    displayStockDetails(stock) {
        const resultsDiv = document.getElementById('lookup-results');
        
        const detailsHTML = `
            <div class="stock-details-container animate-fade-in">
                <div class="card stock-header-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h2 class="stock-symbol">${stock.ticker}</h2>
                                <p class="stock-company">${stock.company_name}</p>
                                <p class="stock-sector">${stock.sector} • ${stock.industry}</p>
                            </div>
                            <div class="text-right">
                                <div class="stock-price-large">$${stock.current_price}</div>
                                <div class="stock-change">
                                    ${stock.previous_close ? 
                                        `${stock.current_price > stock.previous_close ? '📈' : '📉'} 
                                         ${((stock.current_price - stock.previous_close) / stock.previous_close * 100).toFixed(2)}%` 
                                        : ''}
                                </div>
                            </div>
                        </div>
                        ${stock.website ? `<a href="${stock.website}" target="_blank" class="btn btn-outline btn-sm">🌐 Company Website</a>` : ''}
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">📊 Price Data</h4>
                            </div>
                            <div class="card-body">
                                <div class="metrics-grid">
                                    <div class="metric-item">
                                        <span class="metric-label">Open</span>
                                        <span class="metric-value">$${stock.open || 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Day High</span>
                                        <span class="metric-value">$${stock.day_high || 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Day Low</span>
                                        <span class="metric-value">$${stock.day_low || 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">52W High</span>
                                        <span class="metric-value">$${stock.fifty_two_week_high || 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">52W Low</span>
                                        <span class="metric-value">$${stock.fifty_two_week_low || 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">50D Avg</span>
                                        <span class="metric-value">$${stock.fifty_day_average || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">📈 Market Data</h4>
                            </div>
                            <div class="card-body">
                                <div class="metrics-grid">
                                    <div class="metric-item">
                                        <span class="metric-label">Market Cap</span>
                                        <span class="metric-value">${this.formatMarketCap(stock.market_cap)}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Volume</span>
                                        <span class="metric-value">${this.formatNumber(stock.volume)}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Avg Volume</span>
                                        <span class="metric-value">${this.formatNumber(stock.avg_volume)}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">P/E Ratio</span>
                                        <span class="metric-value">${stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Beta</span>
                                        <span class="metric-value">${stock.beta ? stock.beta.toFixed(2) : 'N/A'}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Dividend Yield</span>
                                        <span class="metric-value">${stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                ${stock.description ? `
                <div class="card">
                    <div class="card-header">
                        <h4 class="card-title">ℹ️ Company Description</h4>
                    </div>
                    <div class="card-body">
                        <p>${stock.description.substring(0, 500)}${stock.description.length > 500 ? '...' : ''}</p>
                    </div>
                </div>
                ` : ''}

                ${stock.price_history && stock.price_history.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h4 class="card-title">📊 Recent Price History</h4>
                    </div>
                    <div class="card-body">
                        <div class="price-history-grid">
                            ${stock.price_history.map(day => `
                                <div class="price-history-item">
                                    <div class="date">${new Date(day.date).toLocaleDateString()}</div>
                                    <div class="ohlc">
                                        <span>O: $${day.open}</span>
                                        <span>H: $${day.high}</span>
                                        <span>L: $${day.low}</span>
                                        <span>C: $${day.close}</span>
                                    </div>
                                    <div class="volume">${this.formatNumber(day.volume)} vol</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;

        resultsDiv.innerHTML = detailsHTML;
    }

    showStockDetails(ticker) {
        // Create a temporary form and submit it
        const tempForm = document.createElement('form');
        tempForm.className = 'stock-lookup-form';
        tempForm.innerHTML = `<input type="hidden" name="ticker" value="${ticker}">`;
        this.handleStockLookup(tempForm);
    }

    // 4. NEWS DISPLAY FUNCTIONALITY
    initNewsDisplay() {
        if (document.body.classList.contains('page-news-scrapper')) {
            this.createNewsInterface();
            this.loadNews();
        }
    }

    createNewsInterface() {
        const newsHTML = `
            <div class="card news-controls-card">
                <div class="card-body">
                    <div class="d-flex gap-md flex-wrap align-items-center">
                        <div class="form-group">
                            <select class="form-control form-select" id="news-category">
                                <option value="market">Market News</option>
                                <option value="earnings">Earnings</option>
                                <option value="analysis">Analysis</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <input type="text" class="form-control" id="news-ticker" placeholder="Filter by ticker (optional)">
                        </div>
                        <div class="form-group">
                            <button class="btn btn-primary" onclick="stockScanner.loadNews()">
                                <span>🔄 Refresh News</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div id="news-container" class="news-container"></div>
            <div id="important-stocks" class="important-stocks-section"></div>
        `;

        const pageHeader = document.querySelector('.page-header');
        if (pageHeader) {
            pageHeader.insertAdjacentHTML('afterend', newsHTML);
        }
    }

    async loadNews() {
        const category = document.getElementById('news-category')?.value || 'market';
        const ticker = document.getElementById('news-ticker')?.value || '';
        const newsContainer = document.getElementById('news-container');
        const stocksContainer = document.getElementById('important-stocks');

        if (!newsContainer) return;

        // Show loading
        newsContainer.innerHTML = `
            <div class="card loading">
                <div class="card-body text-center">
                    <div class="animate-spin" style="font-size: 2rem;">📰</div>
                    <p>Loading latest financial news...</p>
                </div>
            </div>
        `;

        try {
            const params = new URLSearchParams({ category });
            if (ticker) params.append('ticker', ticker);

            const response = await fetch(`${this.apiBase}news/?${params}`);
            const data = await response.json();

            if (data.success) {
                this.displayNews(data.news, data.important_stocks);
            } else {
                throw new Error(data.message);
            }

        } catch (error) {
            newsContainer.innerHTML = `
                <div class="card">
                    <div class="card-body text-center text-danger">
                        ❌ ${error.message || 'Failed to load news'}
                    </div>
                </div>
            `;
        }
    }

    displayNews(articles, importantStocks) {
        const newsContainer = document.getElementById('news-container');
        const stocksContainer = document.getElementById('important-stocks');

        // Display news articles
        if (articles.length === 0) {
            newsContainer.innerHTML = `
                <div class="card">
                    <div class="card-body text-center">
                        <h4>📭 No News Found</h4>
                        <p>No recent news articles available.</p>
                    </div>
                </div>
            `;
        } else {
            const newsHTML = articles.map((article, index) => `
                <div class="card news-article animate-fade-in animate-delay-${Math.min(index + 1, 5)}">
                    <div class="card-body">
                        <div class="d-flex gap-lg">
                            ${article.thumbnail ? `
                                <div class="news-thumbnail">
                                    <img src="${article.thumbnail}" alt="News thumbnail" style="width: 100px; height: 70px; object-fit: cover; border-radius: 8px;">
                                </div>
                            ` : ''}
                            <div class="news-content flex-grow-1">
                                <h5 class="card-title">
                                    ${article.url && article.url !== '#' ? 
                                        `<a href="${article.url}" target="_blank">${article.title}</a>` : 
                                        article.title}
                                </h5>
                                <p class="card-subtitle">${article.summary}</p>
                                <div class="news-meta">
                                    <span class="news-publisher">📰 ${article.publisher}</span>
                                    <span class="news-time">🕒 ${this.formatTimeAgo(article.publish_time)}</span>
                                    ${article.related_ticker ? `<span class="news-ticker">📊 ${article.related_ticker}</span>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            newsContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h4 class="card-title">📰 Latest Financial News</h4>
                        <p class="card-subtitle">${articles.length} recent articles</p>
                    </div>
                </div>
                ${newsHTML}
            `;
        }

        // Display important stocks
        if (importantStocks && importantStocks.length > 0 && stocksContainer) {
            const stocksHTML = importantStocks.map(stock => `
                <div class="card stock-highlight">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6>${stock.ticker}</h6>
                                <small>${stock.company_name}</small>
                            </div>
                            <div class="text-right">
                                <div class="stock-price">$${stock.current_price}</div>
                                <small>${this.formatNumber(stock.volume_today)} vol</small>
                            </div>
                        </div>
                        ${stock.note ? `<div class="stock-note">${stock.note}</div>` : ''}
                    </div>
                </div>
            `).join('');

            stocksContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h4 class="card-title">🔥 Trending Stocks</h4>
                        <p class="card-subtitle">High volume stocks to watch</p>
                    </div>
                </div>
                <div class="stocks-grid">
                    ${stocksHTML}
                </div>
            `;
        }
    }

    // UTILITY FUNCTIONS
    formatNumber(num) {
        if (!num) return 'N/A';
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toLocaleString();
    }

    formatMarketCap(cap) {
        if (!cap) return 'N/A';
        if (cap >= 1e12) return '$' + (cap / 1e12).toFixed(1) + 'T';
        if (cap >= 1e9) return '$' + (cap / 1e9).toFixed(1) + 'B';
        if (cap >= 1e6) return '$' + (cap / 1e6).toFixed(1) + 'M';
        return '$' + cap.toLocaleString();
    }

    formatTimeAgo(timestamp) {
        if (!timestamp) return 'Unknown';
        const now = Date.now() / 1000;
        const diff = now - timestamp;
        
        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
        return Math.floor(diff / 86400) + 'd ago';
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

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
    }

    // ADDITIONAL UI ENHANCEMENTS
    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, observerOptions);

        // Observe all cards
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }

    initMobileMenu() {
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const mainNav = document.querySelector('.main-navigation');

        if (mobileToggle && mainNav) {
            mobileToggle.addEventListener('click', () => {
                mobileToggle.classList.toggle('active');
                mainNav.classList.toggle('active');
            });
        }

        // Header scroll effect
        let lastScroll = 0;
        const header = document.querySelector('.site-header');
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                header?.classList.add('scrolled');
            } else {
                header?.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }

    // Sales Tax Display Functions
    initTaxCalculator() {
        // Add tax calculator to checkout pages
        if (document.body.classList.contains('page-membership-checkout')) {
            this.addTaxCalculatorToCheckout();
        }
    }

    addTaxCalculatorToCheckout() {
        const checkoutForm = document.querySelector('#pmpro_form, .checkout-form');
        if (checkoutForm) {
            this.detectLocationAndShowTax();
        }
    }

    async detectLocationAndShowTax() {
        try {
            // Get user's location
            const response = await fetch('http://ipapi.co/json/');
            const location = await response.json();
            
            if (location.country_code === 'US') {
                this.displayTaxInfo(location.region_code, location.region);
            }
        } catch (error) {
            console.log('Could not detect location for tax calculation');
        }
    }

    displayTaxInfo(stateCode, stateName) {
        const taxRates = {
            'AL': 4.00, 'AK': 0.00, 'AZ': 5.60, 'AR': 6.50, 'CA': 7.25, 'CO': 2.90,
            'CT': 6.35, 'DE': 0.00, 'FL': 6.00, 'GA': 4.00, 'HI': 4.00, 'ID': 6.00,
            'IL': 6.25, 'IN': 7.00, 'IA': 6.00, 'KS': 6.50, 'KY': 6.00, 'LA': 4.45,
            'ME': 5.50, 'MD': 6.00, 'MA': 6.25, 'MI': 6.00, 'MN': 6.875, 'MS': 7.00,
            'MO': 4.225, 'MT': 0.00, 'NE': 5.50, 'NV': 6.85, 'NH': 0.00, 'NJ': 6.625,
            'NM': 5.125, 'NY': 8.00, 'NC': 4.75, 'ND': 5.00, 'OH': 5.75, 'OK': 4.50,
            'OR': 0.00, 'PA': 6.00, 'RI': 7.00, 'SC': 6.00, 'SD': 4.50, 'TN': 7.00,
            'TX': 6.25, 'UT': 5.95, 'VT': 6.00, 'VA': 5.30, 'WA': 6.50, 'WV': 6.00,
            'WI': 5.00, 'WY': 4.00, 'DC': 6.00
        };

        const taxRate = taxRates[stateCode] || 6.00;
        
        if (taxRate > 0) {
            const taxNotice = `
                <div class="tax-notice card" style="margin: var(--spacing-lg) 0; background: #f8f9fa; border-left: 4px solid var(--info);">
                    <div class="card-body">
                        <h5>💰 Sales Tax Notice</h5>
                        <p><strong>Location:</strong> ${stateName} (${stateCode})</p>
                        <p><strong>Tax Rate:</strong> ${taxRate}%</p>
                        <p class="text-muted">Sales tax will be automatically calculated and added to your total at checkout.</p>
                    </div>
                </div>
            `;
            
            const checkoutContainer = document.querySelector('.checkout-container, #pmpro_form');
            if (checkoutContainer) {
                checkoutContainer.insertAdjacentHTML('afterbegin', taxNotice);
            }
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.stockScanner = new StockScannerFrontend();
});

// Additional styles for the frontend components
const additionalCSS = `
<style>
.stock-grid, .stocks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
    margin: var(--spacing-xl) 0;
}

.stock-card, .stock-highlight {
    transition: all var(--transition-normal);
}

.stock-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-xl);
}

.stock-price, .stock-price-large {
    font-weight: 700;
    color: var(--success);
    font-family: var(--font-mono);
}

.stock-price-large {
    font-size: 2rem;
}

.stock-metrics {
    display: flex;
    gap: var(--spacing-md);
    margin: var(--spacing-md) 0;
    flex-wrap: wrap;
}

.metric {
    background: var(--light-gray);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
}

.metric-item {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--medium-gray);
}

.metric-label {
    color: var(--text-muted);
    font-size: 0.9rem;
}

.metric-value {
    font-weight: 600;
    color: var(--text-primary);
    font-family: var(--font-mono);
}

.news-article {
    margin-bottom: var(--spacing-lg);
}

.news-meta {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-sm);
    flex-wrap: wrap;
}

.news-meta span {
    font-size: 0.85rem;
    color: var(--text-muted);
    background: var(--light-gray);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
}

.price-history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
}

.price-history-item {
    background: var(--light-gray);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    text-align: center;
}

.ohlc {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    margin: var(--spacing-sm) 0;
    font-family: var(--font-mono);
}

.alert {
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    margin: var(--spacing-md) 0;
}

.alert-success {
    background: rgba(72, 187, 120, 0.1);
    border: 1px solid var(--success);
    color: var(--success);
}

.alert-error {
    background: rgba(245, 101, 101, 0.1);
    border: 1px solid var(--danger);
    color: var(--danger);
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -var(--spacing-sm);
}

.col-md-6, .col-md-4 {
    padding: 0 var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.col-md-6 { flex: 0 0 50%; }
.col-md-4 { flex: 0 0 33.333333%; }

@media (max-width: 768px) {
    .col-md-6, .col-md-4 { flex: 0 0 100%; }
    .stock-grid, .stocks-grid { grid-template-columns: 1fr; }
    .metrics-grid { grid-template-columns: 1fr; }
    .price-history-grid { grid-template-columns: 1fr; }
    .ohlc { flex-direction: column; gap: var(--spacing-xs); }
}
</style>
`;

// Inject additional CSS
document.head.insertAdjacentHTML('beforeend', additionalCSS);