<?php
/**
 * Template Name: Stock Lookup
 * 
 * Stock search and detailed stock information page
 *
 * @package StockScannerPro
 */

get_header(); 

// Get ticker from URL parameter if provided
$ticker = isset($_GET['ticker']) ? sanitize_text_field($_GET['ticker']) : '';
?>

<div class="container mx-auto px-4 py-8">
    
    <!-- Page Header -->
    <div class="page-header mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Stock Lookup</h1>
        <p class="text-xl text-gray-600">Search and analyze any stock</p>
    </div>

    <!-- Search Form -->
    <div class="search-section mb-8">
        <div class="max-w-2xl mx-auto">
            <div class="bg-white rounded-lg border border-gray-200 p-6">
                <form id="stock-search-form" class="flex gap-4">
                    <div class="flex-1">
                        <label for="stock-ticker" class="block text-sm font-medium text-gray-700 mb-2">
                            Stock Ticker Symbol
                        </label>
                        <input type="text" 
                               id="stock-ticker" 
                               name="ticker"
                               class="form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               placeholder="Enter ticker (e.g., AAPL, MSFT, GOOGL)"
                               value="<?php echo esc_attr($ticker); ?>"
                               autocomplete="off">
                        <div id="search-suggestions" class="search-suggestions hidden mt-2"></div>
                    </div>
                    <div class="flex-shrink-0">
                        <label class="block text-sm font-medium text-gray-700 mb-2">&nbsp;</label>
                        <button type="submit" 
                                class="btn btn-primary px-6 py-3 h-full">
                            <i class="fas fa-search mr-2"></i>
                            Search
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Popular Stocks -->
    <div class="popular-stocks mb-8">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">Popular Stocks</h2>
        <div class="flex flex-wrap gap-2">
            <?php
            $popular_tickers = array('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX');
            foreach ($popular_tickers as $popular_ticker) :
            ?>
                <button class="popular-ticker-btn btn btn-outline-secondary btn-sm" 
                        data-ticker="<?php echo esc_attr($popular_ticker); ?>">
                    <?php echo esc_html($popular_ticker); ?>
                </button>
            <?php endforeach; ?>
        </div>
    </div>

    <!-- Stock Details Container -->
    <div id="stock-details" class="stock-details hidden">
        
        <!-- Stock Header -->
        <div id="stock-header" class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div class="stock-info">
                    <h2 id="stock-title" class="text-2xl font-bold text-gray-900">-</h2>
                    <p id="stock-company" class="text-lg text-gray-600">-</p>
                </div>
                
                <div class="stock-price-info text-right">
                    <div id="stock-current-price" class="text-3xl font-bold font-mono text-gray-900">$0.00</div>
                    <div id="stock-price-change" class="text-lg font-mono">$0.00 (0.00%)</div>
                    <div id="stock-last-updated" class="text-sm text-gray-500">-</div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="stock-actions mt-6 flex flex-wrap gap-3">
                <button id="add-to-watchlist-btn" class="btn btn-outline-primary">
                    <i class="fas fa-eye mr-2"></i>
                    Add to Watchlist
                </button>
                <button id="add-to-portfolio-btn" class="btn btn-outline-primary">
                    <i class="fas fa-plus mr-2"></i>
                    Add to Portfolio
                </button>
                <button id="create-alert-btn" class="btn btn-outline-primary">
                    <i class="fas fa-bell mr-2"></i>
                    Create Alert
                </button>
                <button id="share-stock-btn" class="btn btn-outline-secondary">
                    <i class="fas fa-share mr-2"></i>
                    Share
                </button>
            </div>
        </div>

        <!-- Stock Chart -->
        <div class="stock-chart-container mb-6">
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">Price Chart</h3>
                    <div class="chart-controls">
                        <div class="chart-period-selector">
                            <button class="chart-period-btn active" data-period="1d">1D</button>
                            <button class="chart-period-btn" data-period="5d">5D</button>
                            <button class="chart-period-btn" data-period="1m">1M</button>
                            <button class="chart-period-btn" data-period="3m">3M</button>
                            <button class="chart-period-btn" data-period="6m">6M</button>
                            <button class="chart-period-btn" data-period="1y">1Y</button>
                        </div>
                    </div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="stock-price-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Stock Statistics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            
            <!-- Key Statistics -->
            <div class="bg-white rounded-lg border border-gray-200 p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Key Statistics</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Market Cap</div>
                        <div id="stat-market-cap" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">P/E Ratio</div>
                        <div id="stat-pe-ratio" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Volume</div>
                        <div id="stat-volume" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">52W High</div>
                        <div id="stat-52w-high" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">52W Low</div>
                        <div id="stat-52w-low" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Dividend Yield</div>
                        <div id="stat-dividend-yield" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                </div>
            </div>

            <!-- Trading Info -->
            <div class="bg-white rounded-lg border border-gray-200 p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Trading Information</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Day's Range</div>
                        <div id="stat-day-range" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Avg Volume</div>
                        <div id="stat-avg-volume" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Bid</div>
                        <div id="stat-bid" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Ask</div>
                        <div id="stat-ask" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">EPS</div>
                        <div id="stat-eps" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label text-sm text-gray-600">Book Value</div>
                        <div id="stat-book-value" class="stat-value text-lg font-mono font-semibold">-</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Related News -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Related News</h3>
            <div id="stock-news" class="news-feed">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- No Results Message -->
    <div id="no-results" class="no-results hidden text-center py-12">
        <div class="text-6xl mb-4">📈</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Start by searching for a stock</h3>
        <p class="text-gray-600">Enter a ticker symbol above to get detailed stock information</p>
    </div>

    <!-- Error Message -->
    <div id="error-message" class="error-message hidden bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div class="text-red-600 text-2xl mb-2">⚠️</div>
        <h3 class="text-lg font-semibold text-red-900 mb-1">Stock Not Found</h3>
        <p class="text-red-700">Please check the ticker symbol and try again.</p>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initStockLookup();
});

let currentChart = null;

function initStockLookup() {
    // Bind form submission
    document.getElementById('stock-search-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const ticker = document.getElementById('stock-ticker').value.trim().toUpperCase();
        if (ticker) {
            searchStock(ticker);
        }
    });

    // Popular ticker buttons
    document.querySelectorAll('.popular-ticker-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const ticker = this.dataset.ticker;
            document.getElementById('stock-ticker').value = ticker;
            searchStock(ticker);
        });
    });

    // Live search suggestions
    let searchTimeout;
    document.getElementById('stock-ticker').addEventListener('input', function() {
        const query = this.value.trim();
        clearTimeout(searchTimeout);
        
        if (query.length >= 1) {
            searchTimeout = setTimeout(() => showSearchSuggestions(query), 300);
        } else {
            hideSearchSuggestions();
        }
    });

    // Chart period buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('chart-period-btn')) {
            document.querySelectorAll('.chart-period-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            
            const currentTicker = getCurrentTicker();
            if (currentTicker) {
                updateChart(currentTicker, e.target.dataset.period);
            }
        }
    });

    // Action buttons
    bindActionButtons();

    // Auto-search if ticker provided in URL
    const urlTicker = '<?php echo esc_js($ticker); ?>';
    if (urlTicker) {
        searchStock(urlTicker);
    }
}

function showSearchSuggestions(query) {
    StockScannerAPI.Stock.searchStocks(query, 5)
        .then(data => {
            if (data.success && data.results && data.results.length > 0) {
                renderSearchSuggestions(data.results);
            } else {
                hideSearchSuggestions();
            }
        })
        .catch(error => {
            console.error('Search suggestions error:', error);
            hideSearchSuggestions();
        });
}

function renderSearchSuggestions(results) {
    const container = document.getElementById('search-suggestions');
    
    let html = '<div class="suggestions-list bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">';
    
    results.forEach(stock => {
        html += `
            <div class="suggestion-item p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                 onclick="selectSuggestion('${stock.ticker}')">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="font-mono font-semibold text-sm">${stock.ticker}</div>
                        <div class="text-xs text-gray-600 truncate" style="max-width: 200px;">
                            ${stock.company_name || stock.ticker}
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="font-mono text-sm">${StockScannerAPI.Utils.formatCurrency(stock.current_price)}</div>
                        <div class="text-xs ${StockScannerAPI.Utils.getPriceChangeClass(stock.change_percent)}">
                            ${StockScannerAPI.Utils.formatPercentage(stock.change_percent)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    container.innerHTML = html;
    container.classList.remove('hidden');
}

function selectSuggestion(ticker) {
    document.getElementById('stock-ticker').value = ticker;
    hideSearchSuggestions();
    searchStock(ticker);
}

function hideSearchSuggestions() {
    document.getElementById('search-suggestions').classList.add('hidden');
}

function searchStock(ticker) {
    if (!ticker) return;
    
    // Show loading
    showLoading();
    hideAllSections();
    
    // Update URL without reloading page
    const url = new URL(window.location);
    url.searchParams.set('ticker', ticker);
    window.history.pushState({}, '', url);
    
    StockScannerAPI.Stock.getStock(ticker)
        .then(data => {
            if (data.success && data.data) {
                displayStockData(data.data);
                loadStockNews(ticker);
                updateChart(ticker, '1d');
            } else {
                showErrorMessage();
            }
        })
        .catch(error => {
            console.error('Stock search error:', error);
            showErrorMessage();
        })
        .finally(() => {
            hideLoading();
        });
}

function displayStockData(stock) {
    // Stock header
    document.getElementById('stock-title').textContent = stock.ticker || 'N/A';
    document.getElementById('stock-company').textContent = stock.company_name || stock.name || stock.ticker;
    document.getElementById('stock-current-price').textContent = StockScannerAPI.Utils.formatCurrency(stock.current_price);
    
    const change = stock.price_change_today || 0;
    const changePercent = stock.change_percent || 0;
    const changeElement = document.getElementById('stock-price-change');
    changeElement.textContent = `${StockScannerAPI.Utils.formatCurrency(change)} (${StockScannerAPI.Utils.formatPercentage(changePercent)})`;
    changeElement.className = 'text-lg font-mono ' + StockScannerAPI.Utils.getPriceChangeClass(change);
    
    const lastUpdated = stock.last_updated ? new Date(stock.last_updated).toLocaleString() : 'N/A';
    document.getElementById('stock-last-updated').textContent = `Last updated: ${lastUpdated}`;
    
    // Statistics
    document.getElementById('stat-market-cap').textContent = StockScannerAPI.Utils.formatNumber(stock.market_cap) || 'N/A';
    document.getElementById('stat-pe-ratio').textContent = stock.pe_ratio ? parseFloat(stock.pe_ratio).toFixed(2) : 'N/A';
    document.getElementById('stat-volume').textContent = StockScannerAPI.Utils.formatNumber(stock.volume) || 'N/A';
    document.getElementById('stat-52w-high').textContent = StockScannerAPI.Utils.formatCurrency(stock.week_52_high) || 'N/A';
    document.getElementById('stat-52w-low').textContent = StockScannerAPI.Utils.formatCurrency(stock.week_52_low) || 'N/A';
    document.getElementById('stat-dividend-yield').textContent = stock.dividend_yield ? StockScannerAPI.Utils.formatPercentage(stock.dividend_yield) : 'N/A';
    
    // Trading info
    const dayRange = stock.days_low && stock.days_high ? 
        `${StockScannerAPI.Utils.formatCurrency(stock.days_low)} - ${StockScannerAPI.Utils.formatCurrency(stock.days_high)}` : 'N/A';
    document.getElementById('stat-day-range').textContent = dayRange;
    document.getElementById('stat-avg-volume').textContent = StockScannerAPI.Utils.formatNumber(stock.avg_volume_3mon) || 'N/A';
    document.getElementById('stat-bid').textContent = StockScannerAPI.Utils.formatCurrency(stock.bid_price) || 'N/A';
    document.getElementById('stat-ask').textContent = StockScannerAPI.Utils.formatCurrency(stock.ask_price) || 'N/A';
    document.getElementById('stat-eps').textContent = stock.earnings_per_share ? StockScannerAPI.Utils.formatCurrency(stock.earnings_per_share) : 'N/A';
    document.getElementById('stat-book-value').textContent = StockScannerAPI.Utils.formatCurrency(stock.book_value) || 'N/A';
    
    // Show stock details
    document.getElementById('stock-details').classList.remove('hidden');
}

function loadStockNews(ticker) {
    StockScannerAPI.News.getStockNews(ticker, 5)
        .then(data => {
            if (data.success && data.data && data.data.length > 0) {
                renderStockNews(data.data);
            } else {
                document.getElementById('stock-news').innerHTML = '<p class="text-gray-600">No recent news found for this stock.</p>';
            }
        })
        .catch(error => {
            console.error('Stock news error:', error);
            document.getElementById('stock-news').innerHTML = '<p class="text-gray-600">Unable to load news.</p>';
        });
}

function renderStockNews(articles) {
    let html = '';
    
    articles.forEach(article => {
        const publishedAt = new Date(article.published_at).toLocaleDateString();
        const sentiment = article.sentiment_score > 0.1 ? 'positive' : 
                         article.sentiment_score < -0.1 ? 'negative' : 'neutral';
        
        html += `
            <div class="news-item">
                <div class="news-item-content">
                    <h4 class="news-item-title">
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                            ${article.title}
                        </a>
                    </h4>
                    <div class="news-item-meta">
                        <span>${article.source}</span>
                        <span>${publishedAt}</span>
                        <span class="news-item-sentiment ${sentiment}">${sentiment}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    document.getElementById('stock-news').innerHTML = html;
}

function updateChart(ticker, period) {
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Generate sample chart data (in production, this would come from the API)
    const chartData = generateChartData(ticker, period);
    
    const ctx = document.getElementById('stock-price-chart');
    if (!ctx) return;
    
    const config = {
        type: 'line',
        data: chartData,
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
                    ticks: {
                        maxRotation: 0
                    }
                },
                y: {
                    display: true,
                    position: 'right',
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    currentChart = new Chart(ctx, config);
}

function generateChartData(ticker, period) {
    // Sample data generation - replace with actual API call
    const dataPoints = period === '1d' ? 24 : period === '5d' ? 5 : 30;
    const labels = [];
    const data = [];
    const basePrice = Math.random() * 200 + 50;
    
    for (let i = 0; i < dataPoints; i++) {
        if (period === '1d') {
            labels.push(new Date(Date.now() - (dataPoints - i) * 3600000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        } else {
            labels.push(new Date(Date.now() - (dataPoints - i) * 86400000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        const variation = (Math.random() - 0.5) * 10;
        data.push(Math.max(0.01, basePrice + variation));
    }
    
    return {
        labels: labels,
        datasets: [{
            label: ticker + ' Price',
            data: data,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };
}

function bindActionButtons() {
    // Add to Watchlist
    document.getElementById('add-to-watchlist-btn').addEventListener('click', function() {
        const ticker = getCurrentTicker();
        if (ticker) {
            addToWatchlist(ticker);
        }
    });

    // Add to Portfolio
    document.getElementById('add-to-portfolio-btn').addEventListener('click', function() {
        const ticker = getCurrentTicker();
        if (ticker) {
            showAddToPortfolioModal(ticker);
        }
    });

    // Create Alert
    document.getElementById('create-alert-btn').addEventListener('click', function() {
        const ticker = getCurrentTicker();
        if (ticker) {
            showCreateAlertModal(ticker);
        }
    });

    // Share Stock
    document.getElementById('share-stock-btn').addEventListener('click', function() {
        if (navigator.share) {
            navigator.share({
                title: getCurrentTicker(),
                url: window.location.href
            });
        } else {
            // Fallback: copy link
            navigator.clipboard.writeText(window.location.href);
            StockScannerAPI.Toast.show('Link copied to clipboard!', 'success');
        }
    });
}

function addToWatchlist(ticker) {
    StockScannerAPI.Watchlist.addToWatchlist(ticker)
        .then(data => {
            StockScannerAPI.Toast.show(`${ticker} added to watchlist!`, 'success');
        })
        .catch(error => {
            console.error('Add to watchlist error:', error);
            StockScannerAPI.Toast.show('Failed to add to watchlist', 'error');
        });
}

function getCurrentTicker() {
    return document.getElementById('stock-ticker').value.trim().toUpperCase();
}

function showLoading() {
    StockScannerApp.showLoading('Loading stock data...');
}

function hideLoading() {
    StockScannerApp.hideLoading();
}

function showErrorMessage() {
    hideAllSections();
    document.getElementById('error-message').classList.remove('hidden');
}

function hideAllSections() {
    document.getElementById('stock-details').classList.add('hidden');
    document.getElementById('no-results').classList.add('hidden');
    document.getElementById('error-message').classList.add('hidden');
}

// Show "Add to Portfolio" modal
function showAddToPortfolioModal(ticker) {
    // Implementation would show a modal for adding to portfolio
    StockScannerAPI.Toast.show('Add to Portfolio feature coming soon!', 'info');
}

// Show "Create Alert" modal  
function showCreateAlertModal(ticker) {
    // Implementation would show a modal for creating alerts
    StockScannerAPI.Toast.show('Create Alert feature coming soon!', 'info');
}
</script>

<?php get_footer(); ?>