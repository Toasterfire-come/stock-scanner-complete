<?php
/**
 * Template Name: Market Overview
 * 
 * Comprehensive market overview with charts, heatmaps, and statistics
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    
    <!-- Page Header -->
    <div class="page-header mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Market Overview</h1>
        <p class="text-xl text-gray-600">Real-time market data and analysis</p>
    </div>

    <!-- Market Status -->
    <div class="market-status-section mb-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="market-stat-card bg-white rounded-lg border border-gray-200 p-6 text-center">
                <div class="market-stat-icon text-3xl mb-2">📈</div>
                <div id="total-stocks" class="market-stat-value text-2xl font-bold font-mono text-gray-900">-</div>
                <div class="market-stat-label text-sm text-gray-600">Total Stocks</div>
            </div>
            
            <div class="market-stat-card bg-white rounded-lg border border-gray-200 p-6 text-center">
                <div class="market-stat-icon text-3xl mb-2">🟢</div>
                <div id="gainers-count" class="market-stat-value text-2xl font-bold font-mono text-green-600">-</div>
                <div class="market-stat-label text-sm text-gray-600">Gainers</div>
            </div>
            
            <div class="market-stat-card bg-white rounded-lg border border-gray-200 p-6 text-center">
                <div class="market-stat-icon text-3xl mb-2">🔴</div>
                <div id="losers-count" class="market-stat-value text-2xl font-bold font-mono text-red-600">-</div>
                <div class="market-stat-label text-sm text-gray-600">Losers</div>
            </div>
            
            <div class="market-stat-card bg-white rounded-lg border border-gray-200 p-6 text-center">
                <div class="market-stat-icon text-3xl mb-2">➖</div>
                <div id="unchanged-count" class="market-stat-value text-2xl font-bold font-mono text-gray-600">-</div>
                <div class="market-stat-label text-sm text-gray-600">Unchanged</div>
            </div>
        </div>
    </div>

    <!-- Market Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        <!-- Market Trend Chart -->
        <div class="chart-container">
            <div class="chart-header">
                <h2 class="chart-title">Market Trend</h2>
                <div class="chart-controls">
                    <div class="chart-period-selector">
                        <button class="chart-period-btn active" data-period="1d">1D</button>
                        <button class="chart-period-btn" data-period="1w">1W</button>
                        <button class="chart-period-btn" data-period="1m">1M</button>
                        <button class="chart-period-btn" data-period="3m">3M</button>
                        <button class="chart-period-btn" data-period="1y">1Y</button>
                    </div>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas id="market-trend-chart"></canvas>
            </div>
        </div>

        <!-- Top Performers -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Top Performers</h2>
            
            <!-- Top Gainers -->
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-800 mb-3">🚀 Top Gainers</h3>
                <div id="top-gainers" class="space-y-2">
                    <!-- Populated by JavaScript -->
                </div>
            </div>

            <!-- Top Losers -->
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-800 mb-3">📉 Top Losers</h3>
                <div id="top-losers" class="space-y-2">
                    <!-- Populated by JavaScript -->
                </div>
            </div>

            <!-- Most Active -->
            <div>
                <h3 class="text-lg font-medium text-gray-800 mb-3">🔥 Most Active</h3>
                <div id="most-active" class="space-y-2">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <!-- Market Heatmap -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Market Heatmap</h2>
            <div class="heatmap-controls flex gap-2">
                <select id="heatmap-category" class="form-select">
                    <option value="all">All Stocks</option>
                    <option value="large_cap">Large Cap</option>
                    <option value="mid_cap">Mid Cap</option>
                    <option value="small_cap">Small Cap</option>
                </select>
                <select id="heatmap-metric" class="form-select">
                    <option value="change_percent">Price Change %</option>
                    <option value="volume">Volume</option>
                    <option value="market_cap">Market Cap</option>
                </select>
            </div>
        </div>
        <div id="market-heatmap" class="market-heatmap">
            <!-- Populated by JavaScript -->
        </div>
    </div>

    <!-- Sector Performance -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Sector Performance</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Technology</div>
                <div class="sector-change text-lg font-mono font-semibold text-green-600">+2.45%</div>
            </div>
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Healthcare</div>
                <div class="sector-change text-lg font-mono font-semibold text-green-600">+1.23%</div>
            </div>
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Financials</div>
                <div class="sector-change text-lg font-mono font-semibold text-red-600">-0.87%</div>
            </div>
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Energy</div>
                <div class="sector-change text-lg font-mono font-semibold text-red-600">-1.45%</div>
            </div>
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Consumer Goods</div>
                <div class="sector-change text-lg font-mono font-semibold text-green-600">+0.76%</div>
            </div>
            <div class="sector-item p-4 bg-gray-50 rounded-lg">
                <div class="sector-name font-medium text-gray-900">Real Estate</div>
                <div class="sector-change text-lg font-mono font-semibold text-gray-600">+0.12%</div>
            </div>
        </div>
    </div>

    <!-- Market News -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900">Market News</h2>
            <a href="<?php echo esc_url(get_permalink(get_page_by_path('stock-news'))); ?>" 
               class="text-blue-600 hover:text-blue-700 font-medium">
                View All News →
            </a>
        </div>
        <div id="market-news-feed" class="news-feed">
            <!-- Populated by JavaScript -->
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeMarketOverview();
});

function initializeMarketOverview() {
    // Load market statistics
    loadMarketStats();
    
    // Initialize market trend chart
    initMarketTrendChart();
    
    // Load top performers
    loadTopPerformers();
    
    // Initialize heatmap
    initMarketHeatmap();
    
    // Load market news
    loadMarketNews();
    
    // Set up auto-refresh every 30 seconds
    setInterval(refreshMarketData, 30000);
}

function loadMarketStats() {
    StockScannerAPI.Stock.getMarketOverview()
        .then(data => {
            if (data.success && data.market_overview) {
                const stats = data.market_overview;
                document.getElementById('total-stocks').textContent = stats.total_stocks || 0;
                document.getElementById('gainers-count').textContent = stats.gainers || 0;
                document.getElementById('losers-count').textContent = stats.losers || 0;
                document.getElementById('unchanged-count').textContent = stats.unchanged || 0;
            }
        })
        .catch(error => {
            console.error('Failed to load market stats:', error);
        });
}

function initMarketTrendChart() {
    const ctx = document.getElementById('market-trend-chart');
    if (!ctx) return;
    
    // Sample data - in production, this would come from the API
    const chartData = {
        labels: ['9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00'],
        datasets: [{
            label: 'Market Index',
            data: [100, 101.2, 100.8, 102.1, 101.9, 103.2, 102.8, 103.9, 104.2, 103.8, 104.5, 105.1, 104.8, 105.3],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };

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
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                }
            }
        }
    };

    new Chart(ctx, config);
}

function loadTopPerformers() {
    StockScannerAPI.Stock.getTrending(15)
        .then(data => {
            if (data.success && data.data) {
                renderTopPerformers(data.data);
            }
        })
        .catch(error => {
            console.error('Failed to load top performers:', error);
        });
}

function renderTopPerformers(stocks) {
    if (!stocks || stocks.length === 0) return;
    
    // Sort by change percent
    const gainers = stocks.filter(s => (s.change_percent || 0) > 0)
                         .sort((a, b) => (b.change_percent || 0) - (a.change_percent || 0))
                         .slice(0, 5);
    
    const losers = stocks.filter(s => (s.change_percent || 0) < 0)
                        .sort((a, b) => (a.change_percent || 0) - (b.change_percent || 0))
                        .slice(0, 5);
    
    const mostActive = stocks.filter(s => s.volume > 0)
                           .sort((a, b) => (b.volume || 0) - (a.volume || 0))
                           .slice(0, 5);
    
    // Render gainers
    const gainersHtml = gainers.map(stock => createPerformerItem(stock)).join('');
    document.getElementById('top-gainers').innerHTML = gainersHtml;
    
    // Render losers
    const losersHtml = losers.map(stock => createPerformerItem(stock)).join('');
    document.getElementById('top-losers').innerHTML = losersHtml;
    
    // Render most active
    const activeHtml = mostActive.map(stock => createPerformerItem(stock, true)).join('');
    document.getElementById('most-active').innerHTML = activeHtml;
}

function createPerformerItem(stock, showVolume = false) {
    const change = stock.change_percent || 0;
    const changeClass = change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-600';
    
    return `
        <div class="performer-item flex items-center justify-between p-2 hover:bg-gray-50 rounded">
            <div>
                <div class="font-mono font-semibold text-sm">${stock.ticker}</div>
                <div class="text-xs text-gray-600 truncate" style="max-width: 120px;">
                    ${stock.company_name || stock.name || stock.ticker}
                </div>
            </div>
            <div class="text-right">
                <div class="font-mono text-sm">${StockScannerAPI.Utils.formatCurrency(stock.current_price)}</div>
                <div class="text-xs ${changeClass}">
                    ${showVolume ? 
                        StockScannerAPI.Utils.formatNumber(stock.volume) + ' vol' :
                        StockScannerAPI.Utils.formatPercentage(change)
                    }
                </div>
            </div>
        </div>
    `;
}

function initMarketHeatmap() {
    loadHeatmapData('all', 'change_percent');
    
    // Event listeners for heatmap controls
    document.getElementById('heatmap-category').addEventListener('change', function() {
        const category = this.value;
        const metric = document.getElementById('heatmap-metric').value;
        loadHeatmapData(category, metric);
    });
    
    document.getElementById('heatmap-metric').addEventListener('change', function() {
        const metric = this.value;
        const category = document.getElementById('heatmap-category').value;
        loadHeatmapData(category, metric);
    });
}

function loadHeatmapData(category, metric) {
    const filters = {
        limit: 50,
        category: category === 'all' ? '' : category,
        sort_by: metric,
        sort_order: 'desc'
    };
    
    StockScannerAPI.Stock.getStocks(filters)
        .then(data => {
            if (data.success && data.data) {
                renderHeatmap(data.data, metric);
            }
        })
        .catch(error => {
            console.error('Failed to load heatmap data:', error);
        });
}

function renderHeatmap(stocks, metric) {
    const heatmapContainer = document.getElementById('market-heatmap');
    if (!heatmapContainer || !stocks || stocks.length === 0) return;
    
    let html = '';
    
    stocks.forEach(stock => {
        const value = stock[metric] || 0;
        const size = getHeatmapCellSize(stock.market_cap || 0);
        const colorClass = getHeatmapColorClass(metric === 'change_percent' ? value : 0);
        
        html += `
            <div class="heatmap-cell ${size} ${colorClass}" 
                 data-ticker="${stock.ticker}"
                 title="${stock.company_name || stock.ticker}: ${formatHeatmapValue(value, metric)}">
                <div class="heatmap-ticker">${stock.ticker}</div>
                <div class="heatmap-change">${formatHeatmapValue(value, metric)}</div>
            </div>
        `;
    });
    
    heatmapContainer.innerHTML = html;
}

function getHeatmapCellSize(marketCap) {
    if (marketCap >= 200000000000) return 'size-xl';
    if (marketCap >= 10000000000) return 'size-lg';
    if (marketCap >= 2000000000) return 'size-md';
    if (marketCap >= 300000000) return 'size-sm';
    return 'size-xs';
}

function getHeatmapColorClass(changePercent) {
    if (changePercent >= 5) return 'bg-green-600 text-white';
    if (changePercent >= 2) return 'bg-green-400 text-white';
    if (changePercent >= 0.5) return 'bg-green-200 text-green-900';
    if (changePercent > -0.5) return 'bg-gray-100 text-gray-900';
    if (changePercent > -2) return 'bg-red-200 text-red-900';
    if (changePercent > -5) return 'bg-red-400 text-white';
    return 'bg-red-600 text-white';
}

function formatHeatmapValue(value, metric) {
    switch (metric) {
        case 'change_percent':
            return StockScannerAPI.Utils.formatPercentage(value);
        case 'volume':
            return StockScannerAPI.Utils.formatNumber(value);
        case 'market_cap':
            return StockScannerAPI.Utils.formatNumber(value);
        default:
            return value.toString();
    }
}

function loadMarketNews() {
    StockScannerAPI.News.getNews(5)
        .then(data => {
            if (data.success && data.data) {
                renderMarketNews(data.data);
            }
        })
        .catch(error => {
            console.error('Failed to load market news:', error);
        });
}

function renderMarketNews(articles) {
    const container = document.getElementById('market-news-feed');
    if (!container || !articles || articles.length === 0) return;
    
    let html = '';
    
    articles.forEach(article => {
        const publishedAt = new Date(article.published_at).toLocaleDateString();
        const sentiment = article.sentiment_score > 0.1 ? 'positive' : 
                         article.sentiment_score < -0.1 ? 'negative' : 'neutral';
        
        html += `
            <div class="news-item">
                <div class="news-item-content">
                    <h3 class="news-item-title">
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                            ${article.title}
                        </a>
                    </h3>
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
    
    container.innerHTML = html;
}

function refreshMarketData() {
    loadMarketStats();
    loadTopPerformers();
}
</script>

<?php get_footer(); ?>