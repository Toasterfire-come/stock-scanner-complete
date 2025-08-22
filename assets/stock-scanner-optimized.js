/**
 * Optimized Stock Scanner Frontend
 * Efficient loading, caching, and performance optimization
 */

class OptimizedStockScanner {
    constructor() {
        this.apiBase = '/api/';
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        this.loadingStates = new Set();
        this.requestQueue = new Map();
        this.maxConcurrentRequests = 3;
        this.activeRequests = 0;
        
        this.init();
    }
    
    init() {
        // Initialize with performance optimizations
        this.setupEventDelegation();
        this.setupIntersectionObserver();
        this.setupRequestDeduplication();
        this.preloadCriticalData();
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
    }
    
    // ================== CACHING SYSTEM ==================
    
    getCacheKey(url, params = {}) {
        const paramString = Object.keys(params).sort()
            .map(key => `${key}=${params[key]}`)
            .join('&');
        return `${url}?${paramString}`;
    }
    
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        this.cache.delete(key);
        return null;
    }
    
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
        
        // Prevent cache from growing too large
        if (this.cache.size > 100) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
    }
    
    // ================== OPTIMIZED API CALLS ==================
    
    async makeRequest(url, options = {}) {
        const cacheKey = this.getCacheKey(url, options.params || {});
        
        // Check cache first
        const cached = this.getFromCache(cacheKey);
        if (cached && !options.bypassCache) {
            return cached;
        }
        
        // Deduplicate concurrent requests
        if (this.requestQueue.has(cacheKey)) {
            return this.requestQueue.get(cacheKey);
        }
        
        // Rate limiting
        if (this.activeRequests >= this.maxConcurrentRequests) {
            await this.waitForRequestSlot();
        }
        
        this.activeRequests++;
        
        const requestPromise = this.executeRequest(url, options)
            .then(data => {
                this.setCache(cacheKey, data);
                return data;
            })
            .finally(() => {
                this.activeRequests--;
                this.requestQueue.delete(cacheKey);
            });
        
        this.requestQueue.set(cacheKey, requestPromise);
        return requestPromise;
    }
    
    async executeRequest(url, options) {
        const response = await fetch(this.apiBase + url, {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            body: options.body ? JSON.stringify(options.body) : undefined
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async waitForRequestSlot() {
        return new Promise(resolve => {
            const checkSlot = () => {
                if (this.activeRequests < this.maxConcurrentRequests) {
                    resolve();
                } else {
                    setTimeout(checkSlot, 100);
                }
            };
            checkSlot();
        });
    }
    
    // ================== LAZY LOADING ==================
    
    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadElement(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        // Observe all lazy-load elements
        document.querySelectorAll('[data-lazy-load]').forEach(el => {
            this.observer.observe(el);
        });
    }
    
    async loadElement(element) {
        const loadType = element.dataset.lazyLoad;
        const loadingClass = 'loading';
        
        if (this.loadingStates.has(element)) return;
        
        this.loadingStates.add(element);
        element.classList.add(loadingClass);
        
        try {
            switch (loadType) {
                case 'portfolio':
                    await this.loadPortfolioData(element);
                    break;
                case 'market-analysis':
                    await this.loadMarketAnalysis(element);
                    break;
                case 'stock-screener':
                    await this.loadStockScreener(element);
                    break;
                case 'watchlist':
                    await this.loadWatchlist(element);
                    break;
                case 'earnings':
                    await this.loadEarningsCalendar(element);
                    break;
                default:
                    console.warn(`Unknown lazy load type: ${loadType}`);
            }
        } catch (error) {
            this.showError(element, error.message);
        } finally {
            element.classList.remove(loadingClass);
            this.loadingStates.delete(element);
        }
    }
    
    // ================== PORTFOLIO FUNCTIONALITY ==================
    
    async loadPortfolioData(element) {
        const data = await this.makeRequest('portfolio/');
        
        if (data.success) {
            element.innerHTML = this.renderPortfolios(data.portfolios);
            this.setupPortfolioEvents(element);
        }
    }
    
    renderPortfolios(portfolios) {
        if (!portfolios.length) {
            return `
                <div class="empty-state">
                    <h3>No Portfolios Yet</h3>
                    <p>Create your first portfolio to start tracking investments</p>
                    <button class="btn btn-primary" data-action="create-portfolio">
                        Create Portfolio
                    </button>
                </div>
            `;
        }
        
        return `
            <div class="portfolio-grid">
                ${portfolios.map(portfolio => `
                    <div class="portfolio-card" data-portfolio-id="${portfolio.id}">
                        <div class="portfolio-header">
                            <h3>${this.escapeHtml(portfolio.name)}</h3>
                            <span class="portfolio-value">$${this.formatNumber(portfolio.total_value)}</span>
                        </div>
                        <div class="portfolio-stats">
                            <div class="stat">
                                <span class="label">Gain/Loss:</span>
                                <span class="value ${portfolio.total_gain_loss >= 0 ? 'positive' : 'negative'}">
                                    ${portfolio.total_gain_loss >= 0 ? '+' : ''}$${this.formatNumber(portfolio.total_gain_loss)}
                                    (${portfolio.total_gain_loss_percent.toFixed(2)}%)
                                </span>
                            </div>
                            <div class="stat">
                                <span class="label">Holdings:</span>
                                <span class="value">${portfolio.holdings_count}</span>
                            </div>
                        </div>
                        <div class="portfolio-actions">
                            <button class="btn btn-sm btn-outline" data-action="view-portfolio" data-id="${portfolio.id}">
                                View Details
                            </button>
                            <button class="btn btn-sm btn-primary" data-action="add-holding" data-id="${portfolio.id}">
                                Add Stock
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // ================== MARKET ANALYSIS FUNCTIONALITY ==================
    
    async loadMarketAnalysis(element) {
        const analysisType = element.dataset.analysisType || '';
        const data = await this.makeRequest('market-analysis/', {
            params: { type: analysisType }
        });
        
        if (data.success) {
            element.innerHTML = this.renderMarketAnalysis(data.analyses);
            this.setupAnalysisEvents(element);
        }
    }
    
    renderMarketAnalysis(analyses) {
        return `
            <div class="analysis-list">
                ${analyses.map(analysis => `
                    <article class="analysis-card ${analysis.is_premium ? 'premium' : ''}" 
                             data-analysis-id="${analysis.id}">
                        <div class="analysis-header">
                            <h3>${this.escapeHtml(analysis.title)}</h3>
                            <div class="analysis-meta">
                                <span class="type">${analysis.analysis_type_display}</span>
                                ${analysis.is_premium ? '<span class="premium-badge">Premium</span>' : ''}
                                <span class="views">${analysis.views} views</span>
                            </div>
                        </div>
                        <div class="analysis-content">
                            <p>${this.escapeHtml(analysis.content)}</p>
                            ${analysis.tickers.length ? `
                                <div class="tickers">
                                    ${analysis.tickers.map(ticker => 
                                        `<span class="ticker-tag">${ticker}</span>`
                                    ).join('')}
                                </div>
                            ` : ''}
                        </div>
                        <div class="analysis-footer">
                            <span class="author">By ${analysis.author}</span>
                            <span class="date">${this.formatDate(analysis.created_at)}</span>
                            <button class="btn btn-sm btn-outline" data-action="read-analysis" data-id="${analysis.id}">
                                Read More
                            </button>
                        </div>
                    </article>
                `).join('')}
            </div>
        `;
    }
    
    // ================== STOCK SCREENER FUNCTIONALITY ==================
    
    async loadStockScreener(element) {
        element.innerHTML = this.renderScreenerForm();
        this.setupScreenerEvents(element);
    }
    
    renderScreenerForm() {
        return `
            <div class="screener-container">
                <form class="screener-form" data-action="screen-stocks">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="min-price">Min Price ($)</label>
                            <input type="number" id="min-price" name="min_price" step="0.01" min="0">
                        </div>
                        <div class="form-group">
                            <label for="max-price">Max Price ($)</label>
                            <input type="number" id="max-price" name="max_price" step="0.01">
                        </div>
                        <div class="form-group">
                            <label for="min-volume">Min Volume</label>
                            <input type="number" id="min-volume" name="min_volume" min="0">
                        </div>
                        <div class="form-group">
                            <label for="sector">Sector</label>
                            <select id="sector" name="sector">
                                <option value="">All Sectors</option>
                                <option value="technology">Technology</option>
                                <option value="healthcare">Healthcare</option>
                                <option value="financial">Financial</option>
                                <option value="energy">Energy</option>
                                <option value="consumer">Consumer</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Screen Stocks</button>
                </form>
                <div class="screener-results" id="screener-results"></div>
            </div>
        `;
    }
    
    async performStockScreen(formData) {
        const resultsContainer = document.getElementById('screener-results');
        resultsContainer.innerHTML = '<div class="loading">Screening stocks...</div>';
        
        try {
            const data = await this.makeRequest('stock-screener/', {
                params: Object.fromEntries(formData)
            });
            
            if (data.success) {
                resultsContainer.innerHTML = this.renderScreenerResults(data.results);
            }
        } catch (error) {
            resultsContainer.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    }
    
    renderScreenerResults(results) {
        if (!results.length) {
            return '<div class="empty-state">No stocks match your criteria</div>';
        }
        
        return `
            <div class="screener-results-table">
                <table class="responsive-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Company</th>
                            <th>Price</th>
                            <th>Volume</th>
                            <th>Market Cap</th>
                            <th>P/E Ratio</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(stock => `
                            <tr data-ticker="${stock.ticker}">
                                <td><strong>${stock.ticker}</strong></td>
                                <td>${this.escapeHtml(stock.company_name)}</td>
                                <td>$${this.formatNumber(stock.price)}</td>
                                <td>${this.formatNumber(stock.volume)}</td>
                                <td>${this.formatMarketCap(stock.market_cap)}</td>
                                <td>${stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline" data-action="add-to-watchlist" data-ticker="${stock.ticker}">
                                        Add to Watchlist
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // ================== EVENT HANDLING ==================
    
    setupEventDelegation() {
        document.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (!action) return;
            
            e.preventDefault();
            this.handleAction(action, e.target, e);
        });
        
        document.addEventListener('submit', (e) => {
            const action = e.target.dataset.action;
            if (!action) return;
            
            e.preventDefault();
            this.handleFormSubmit(action, e.target, e);
        });
    }
    
    async handleAction(action, element, event) {
        try {
            switch (action) {
                case 'create-portfolio':
                    await this.createPortfolio();
                    break;
                case 'view-portfolio':
                    await this.viewPortfolio(element.dataset.id);
                    break;
                case 'add-holding':
                    await this.addHolding(element.dataset.id);
                    break;
                case 'add-to-watchlist':
                    await this.addToWatchlist(element.dataset.ticker);
                    break;
                case 'read-analysis':
                    await this.readAnalysis(element.dataset.id);
                    break;
                default:
                    console.warn(`Unknown action: ${action}`);
            }
        } catch (error) {
            this.showNotification('Error: ' + error.message, 'error');
        }
    }
    
    async handleFormSubmit(action, form, event) {
        const formData = new FormData(form);
        
        try {
            switch (action) {
                case 'screen-stocks':
                    await this.performStockScreen(formData);
                    break;
                case 'contact-form':
                    await this.submitContactForm(formData);
                    break;
                default:
                    console.warn(`Unknown form action: ${action}`);
            }
        } catch (error) {
            this.showNotification('Error: ' + error.message, 'error');
        }
    }
    
    // ================== UTILITY FUNCTIONS ==================
    
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    formatMarketCap(marketCap) {
        if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
        if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
        if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
        return `$${this.formatNumber(marketCap)}`;
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    showError(element, message) {
        element.innerHTML = `<div class="error">Error: ${this.escapeHtml(message)}</div>`;
    }
    
    // ================== PRELOADING ==================
    
    async preloadCriticalData() {
        // Preload analytics data for homepage
        if (document.body.classList.contains('home')) {
            this.makeRequest('analytics/public/');
        }
        
        // Preload user data if logged in
        if (document.body.classList.contains('logged-in')) {
            this.makeRequest('member-dashboard/');
        }
    }
    
    // ================== CLEANUP ==================
    
    cleanup() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.cache.clear();
        this.requestQueue.clear();
        this.loadingStates.clear();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.stockScanner = new OptimizedStockScanner();
    });
} else {
    window.stockScanner = new OptimizedStockScanner();
}
