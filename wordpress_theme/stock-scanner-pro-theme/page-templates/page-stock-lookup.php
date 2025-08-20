<?php
/**
 * Template Name: Stock Lookup
 * 
 * Advanced stock search and analysis page
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="stock-lookup-container">
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="container">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">Stock Lookup</h1>
                    <p class="text-gray-600 mt-2">Search and analyze stocks with real-time data</p>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Search Section -->
        <div class="search-section mb-8">
            <div class="search-card">
                <form id="stock-search-form" class="stock-search-form">
                    <div class="search-input-group">
                        <input 
                            type="text" 
                            id="stock-search-input" 
                            name="ticker" 
                            placeholder="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)"
                            class="search-input"
                            autocomplete="off"
                            required
                        >
                        <button type="submit" class="search-btn">
                            <i class="fas fa-search"></i>
                            Search
                        </button>
                    </div>
                    <div id="search-suggestions" class="search-suggestions">
                        <!-- Populated by JavaScript -->
                    </div>
                </form>
            </div>
        </div>

        <!-- Stock Details Section -->
        <div id="stock-details-section" class="stock-details-section" style="display: none;">
            <!-- Stock Header -->
            <div id="stock-header" class="stock-header mb-6">
                <!-- Populated by JavaScript -->
            </div>

            <!-- Stock Actions -->
            <div id="stock-actions" class="stock-actions mb-6">
                <!-- Populated by JavaScript -->
            </div>

            <!-- Stock Data Grid -->
            <div class="stock-data-grid mb-8">
                <!-- Price Chart -->
                <div class="stock-chart-card">
                    <div class="card-header">
                        <h3 class="card-title">Price Chart</h3>
                        <div class="chart-controls">
                            <div class="timeframe-buttons">
                                <button class="timeframe-btn active" data-period="1d">1D</button>
                                <button class="timeframe-btn" data-period="5d">5D</button>
                                <button class="timeframe-btn" data-period="1mo">1M</button>
                                <button class="timeframe-btn" data-period="3mo">3M</button>
                                <button class="timeframe-btn" data-period="6mo">6M</button>
                                <button class="timeframe-btn" data-period="1y">1Y</button>
                                <button class="timeframe-btn" data-period="5y">5Y</button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="price-chart" class="price-chart"></canvas>
                    </div>
                </div>

                <!-- Key Statistics -->
                <div class="key-stats-card">
                    <div class="card-header">
                        <h3 class="card-title">Key Statistics</h3>
                    </div>
                    <div id="key-statistics" class="card-body">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Additional Info Tabs -->
            <div class="info-tabs-section mb-8">
                <div class="tabs-nav">
                    <button class="tab-btn active" data-tab="financials">
                        <i class="fas fa-chart-bar mr-2"></i>
                        Financials
                    </button>
                    <button class="tab-btn" data-tab="news">
                        <i class="fas fa-newspaper mr-2"></i>
                        News
                    </button>
                    <button class="tab-btn" data-tab="analysis">
                        <i class="fas fa-analytics mr-2"></i>
                        Analysis
                    </button>
                    <button class="tab-btn" data-tab="similar">
                        <i class="fas fa-users mr-2"></i>
                        Similar Stocks
                    </button>
                </div>

                <div class="tabs-content">
                    <!-- Financials Tab -->
                    <div id="financials-tab" class="tab-content active">
                        <div id="financial-data" class="financial-data">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>

                    <!-- News Tab -->
                    <div id="news-tab" class="tab-content">
                        <div id="stock-news" class="stock-news">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>

                    <!-- Analysis Tab -->
                    <div id="analysis-tab" class="tab-content">
                        <div id="stock-analysis" class="stock-analysis">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>

                    <!-- Similar Stocks Tab -->
                    <div id="similar-tab" class="tab-content">
                        <div id="similar-stocks" class="similar-stocks">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Popular Searches -->
        <div class="popular-searches-section">
            <h2 class="section-title mb-4">Popular Searches</h2>
            <div id="popular-stocks" class="popular-stocks-grid">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>
</div>

<!-- Add to Portfolio Modal -->
<div class="modal fade" id="addToPortfolioModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add to Portfolio</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="add-to-portfolio-form">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="portfolio-ticker" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="portfolio-ticker" readonly>
                    </div>
                    <div class="mb-3">
                        <label for="portfolio-shares" class="form-label">Number of Shares</label>
                        <input type="number" class="form-control" id="portfolio-shares" step="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="portfolio-cost-basis" class="form-label">Cost Basis per Share</label>
                        <input type="number" class="form-control" id="portfolio-cost-basis" step="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="portfolio-purchase-date" class="form-label">Purchase Date</label>
                        <input type="date" class="form-control" id="portfolio-purchase-date">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add to Portfolio</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Add to Watchlist Modal -->
<div class="modal fade" id="addToWatchlistModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add to Watchlist</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="add-to-watchlist-form">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="watchlist-ticker" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="watchlist-ticker" readonly>
                    </div>
                    <div class="mb-3">
                        <label for="watchlist-category" class="form-label">Category</label>
                        <select class="form-select" id="watchlist-category">
                            <option value="default">Default</option>
                            <option value="growth">Growth</option>
                            <option value="dividend">Dividend</option>
                            <option value="tech">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="watchlist-notes" class="form-label">Notes</label>
                        <textarea class="form-control" id="watchlist-notes" rows="3" placeholder="Optional notes about this stock"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add to Watchlist</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
// Initialize stock lookup when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerLookup !== 'undefined') {
        StockScannerLookup.init();
    }
    
    // Check if ticker is provided in URL
    const urlParams = new URLSearchParams(window.location.search);
    const ticker = urlParams.get('ticker');
    if (ticker) {
        document.getElementById('stock-search-input').value = ticker;
        document.getElementById('stock-search-form').dispatchEvent(new Event('submit'));
    }
});
</script>

<?php get_footer(); ?>