<?php
/**
 * Template Name: Stock Lookup Page
 * Individual page for stock quote lookup functionality
 */

get_header(); ?>

<div class="stock-lookup-page">
    <div class="container">
        <div class="page-header">
            <h1>Stock Quote Lookup</h1>
            <p class="page-description">Get real-time stock quotes, prices, and basic company information</p>
        </div>

        <div class="stock-lookup-container">
            <!-- Quick Lookup Section -->
            <div class="lookup-section">
                <div class="lookup-form-card">
                    <h2>🔍 Quick Stock Quote</h2>
                    <div class="lookup-form">
                        <div class="input-group">
                            <input type="text" id="stock-symbol" placeholder="Enter stock symbol (e.g., AAPL, GOOGL, TSLA)" maxlength="10" />
                            <button id="get-stock-quote" class="btn btn-primary">Get Quote</button>
                        </div>
                        <div class="popular-stocks">
                            <span>Popular: </span>
                            <button class="stock-chip" data-symbol="AAPL">AAPL</button>
                            <button class="stock-chip" data-symbol="GOOGL">GOOGL</button>
                            <button class="stock-chip" data-symbol="TSLA">TSLA</button>
                            <button class="stock-chip" data-symbol="MSFT">MSFT</button>
                            <button class="stock-chip" data-symbol="AMZN">AMZN</button>
                            <button class="stock-chip" data-symbol="NVDA">NVDA</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div class="results-section">
                <div id="stock-result" class="stock-result-card" style="display: none;">
                    <!-- Stock quote results will be displayed here -->
                </div>
                
                <div class="loading-indicator" id="loading-indicator" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading stock data...</p>
                </div>
            </div>

            <!-- Recent Lookups -->
            <div class="recent-lookups-section">
                <h3>📊 Recent Lookups</h3>
                <div id="recent-lookups" class="recent-lookups-grid">
                    <!-- Recent lookups will be populated here -->
                </div>
            </div>

            <!-- Usage Stats -->
            <?php if (is_user_logged_in()): ?>
            <div class="usage-stats-section">
                <h3>📈 Your API Usage</h3>
                <div id="usage-stats" class="usage-stats-card">
                    <!-- Usage stats will be loaded here -->
                </div>
            </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const stockSymbolInput = document.getElementById('stock-symbol');
    const getQuoteBtn = document.getElementById('get-stock-quote');
    const stockResult = document.getElementById('stock-result');
    const loadingIndicator = document.getElementById('loading-indicator');
    const stockChips = document.querySelectorAll('.stock-chip');

    // Check for symbol parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const symbolParam = urlParams.get('symbol');
    if (symbolParam) {
        const symbol = symbolParam.trim().toUpperCase();
        stockSymbolInput.value = symbol;
        getStockQuote(symbol);
    }

    // Handle stock chip clicks
    stockChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const symbol = this.dataset.symbol;
            stockSymbolInput.value = symbol;
            getStockQuote(symbol);
        });
    });

    // Handle enter key press
    stockSymbolInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const symbol = this.value.trim().toUpperCase();
            if (symbol) {
                getStockQuote(symbol);
            }
        }
    });

    // Handle get quote button click
    getQuoteBtn.addEventListener('click', function() {
        const symbol = stockSymbolInput.value.trim().toUpperCase();
        if (symbol) {
            getStockQuote(symbol);
        } else {
            alert('Please enter a stock symbol');
        }
    });

    function getStockQuote(symbol) {
        // Show loading
        stockResult.style.display = 'none';
        loadingIndicator.style.display = 'block';
        getQuoteBtn.disabled = true;
        getQuoteBtn.textContent = 'Loading...';

        // Make AJAX request
        fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                action: 'stock_scanner_get_quote',
                symbol: symbol,
                nonce: '<?php echo wp_create_nonce('stock_scanner_theme_nonce'); ?>'
            })
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            getQuoteBtn.disabled = false;
            getQuoteBtn.textContent = 'Get Quote';

            if (data.success) {
                displayStockResult(data.data);
                addToRecentLookups(symbol, data.data);
                updateUsageStats();
            } else {
                displayError(data.data || 'Failed to fetch stock data');
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            getQuoteBtn.disabled = false;
            getQuoteBtn.textContent = 'Get Quote';
            displayError('Network error occurred');
        });
    }

    function displayStockResult(data) {
        const changeClass = parseFloat(data.change) >= 0 ? 'positive' : 'negative';
        const changeIcon = parseFloat(data.change) >= 0 ? '↗' : '↘';
        
        stockResult.innerHTML = `
            <div class="stock-quote-header">
                <h3>${data.symbol}</h3>
                <div class="quote-timestamp">Updated: ${new Date(data.timestamp).toLocaleString()}</div>
            </div>
            <div class="stock-quote-data">
                <div class="main-price">
                    <span class="price">$${data.price}</span>
                    <div class="change-info ${changeClass}">
                        <span class="change">${changeIcon} $${data.change}</span>
                        <span class="change-percent">(${data.change_percent}%)</span>
                    </div>
                </div>
                <div class="stock-details">
                    <div class="detail-item">
                        <span class="label">Volume:</span>
                        <span class="value">${data.volume}</span>
                    </div>
                </div>
            </div>
            <div class="quote-actions">
                <button class="btn btn-secondary add-to-watchlist" data-symbol="${data.symbol}">
                    ⭐ Add to Watchlist
                </button>
                <button class="btn btn-outline view-chart" data-symbol="${data.symbol}">
                    📊 View Chart
                </button>
            </div>
        `;
        
        stockResult.style.display = 'block';
        
        // Add event listeners for action buttons
        const addToWatchlistBtn = stockResult.querySelector('.add-to-watchlist');
        const viewChartBtn = stockResult.querySelector('.view-chart');
        
        if (addToWatchlistBtn) {
            addToWatchlistBtn.addEventListener('click', function() {
                addToWatchlist(data.symbol);
            });
        }
        
        if (viewChartBtn) {
            viewChartBtn.addEventListener('click', function() {
                window.location.href = `/technical-analysis/?symbol=${data.symbol}`;
            });
        }
    }

    function displayError(message) {
        stockResult.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
            </div>
        `;
        stockResult.style.display = 'block';
    }

    function addToRecentLookups(symbol, data) {
        // Add to local storage for recent lookups
        let recentLookups = JSON.parse(localStorage.getItem('recentStockLookups') || '[]');
        
        // Remove if already exists
        recentLookups = recentLookups.filter(item => item.symbol !== symbol);
        
        // Add to beginning
        recentLookups.unshift({
            symbol: symbol,
            price: data.price,
            change: data.change,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 6
        recentLookups = recentLookups.slice(0, 6);
        
        localStorage.setItem('recentStockLookups', JSON.stringify(recentLookups));
        displayRecentLookups();
    }

    function displayRecentLookups() {
        const recentLookups = JSON.parse(localStorage.getItem('recentStockLookups') || '[]');
        const container = document.getElementById('recent-lookups');
        
        if (recentLookups.length === 0) {
            container.innerHTML = '<p>No recent lookups</p>';
            return;
        }
        
        container.innerHTML = recentLookups.map(item => `
            <div class="recent-lookup-item" onclick="getStockQuote('${item.symbol}')">
                <div class="symbol">${item.symbol}</div>
                <div class="price">$${item.price}</div>
                <div class="change ${parseFloat(item.change) >= 0 ? 'positive' : 'negative'}">
                    ${item.change}
                </div>
            </div>
        `).join('');
    }

    function updateUsageStats() {
        <?php if (is_user_logged_in()): ?>
        fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                action: 'get_usage_stats',
                nonce: '<?php echo wp_create_nonce('stock_scanner_theme_nonce'); ?>'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const usageStats = document.getElementById('usage-stats');
                if (usageStats) {
                    usageStats.innerHTML = `
                        <div class="usage-grid">
                            <div class="usage-item">
                                <span class="usage-number">${data.data.monthly_calls}</span>
                                <span class="usage-label">This Month</span>
                            </div>
                            <div class="usage-item">
                                <span class="usage-number">${data.data.daily_calls}</span>
                                <span class="usage-label">Today</span>
                            </div>
                            <div class="usage-item">
                                <span class="usage-number">${data.data.monthly_limit === -1 ? '∞' : data.data.monthly_limit}</span>
                                <span class="usage-label">Monthly Limit</span>
                            </div>
                        </div>
                    `;
                }
            }
        });
        <?php endif; ?>
    }

    function addToWatchlist(symbol) {
        <?php if (is_user_logged_in()): ?>
        fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                action: 'add_to_watchlist',
                symbol: symbol,
                nonce: '<?php echo wp_create_nonce('stock_scanner_theme_nonce'); ?>'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`${symbol} added to your watchlist!`);
            } else {
                alert('Failed to add to watchlist');
            }
        });
        <?php else: ?>
        alert('Please log in to add stocks to your watchlist');
        <?php endif; ?>
    }

    // Load recent lookups on page load
    displayRecentLookups();
    
    <?php if (is_user_logged_in()): ?>
    // Load usage stats
    updateUsageStats();
    <?php endif; ?>
});
</script>

<style>
.stock-quote-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e1e1e1;
}

.stock-quote-header h3 {
    margin: 0;
    font-size: 1.5rem;
    color: #1d2327;
}

.quote-timestamp {
    color: #646970;
    font-size: 0.9rem;
}

.main-price {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

.price {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1d2327;
}

.change-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.change-info.positive {
    color: #00a32a;
}

.change-info.negative {
    color: #d63638;
}

.change {
    font-size: 1.1rem;
    font-weight: 600;
}

.change-percent {
    font-size: 0.9rem;
}

.stock-details {
    margin-bottom: 20px;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.label {
    color: #646970;
    font-weight: 500;
}

.value {
    color: #1d2327;
    font-weight: 600;
}

.quote-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn-secondary {
    background: #646970;
    color: white;
}

.btn-secondary:hover {
    background: #50575e;
}

.btn-outline {
    background: transparent;
    color: #2271b1;
    border: 2px solid #2271b1;
}

.btn-outline:hover {
    background: #2271b1;
    color: white;
}

.error-message {
    text-align: center;
    padding: 40px;
}

.error-message h3 {
    color: #d63638;
    margin-bottom: 15px;
}

.usage-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 20px;
}

.usage-item {
    text-align: center;
}

.usage-number {
    display: block;
    font-size: 1.8rem;
    font-weight: bold;
    color: #2271b1;
    margin-bottom: 5px;
}

.usage-label {
    color: #646970;
    font-size: 0.9rem;
}

.recent-lookup-item .symbol {
    font-weight: bold;
    color: #1d2327;
    margin-bottom: 5px;
}

.recent-lookup-item .price {
    color: #646970;
    margin-bottom: 3px;
}

.recent-lookup-item .change.positive {
    color: #00a32a;
}

.recent-lookup-item .change.negative {
    color: #d63638;
}
</style>

<?php get_footer(); ?>