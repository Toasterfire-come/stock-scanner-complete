<?php
/**
 * Template Name: Market Overview
 * 
 * Complete market data with heatmaps and sector analysis
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
                <h1 class="text-4xl font-bold text-gray-900 mb-2">Market Overview</h1>
                <p class="text-xl text-gray-600">Real-time market data and sector analysis</p>
            </div>
            <div class="market-status flex items-center gap-4 mt-4 md:mt-0">
                <div id="market-status-indicator" class="flex items-center gap-2">
                    <div class="status-dot w-3 h-3 rounded-full bg-gray-400"></div>
                    <span id="market-status-text" class="font-medium text-gray-600">Loading...</span>
                </div>
                <div class="last-updated text-sm text-gray-500">
                    Updated: <span id="last-update-time">--</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Market Indices -->
    <div class="market-indices grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="index-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">S&P 500</h3>
                <i class="fas fa-chart-line text-2xl text-blue-600"></i>
            </div>
            <div id="sp500-price" class="text-3xl font-bold font-mono text-gray-900">--</div>
            <div id="sp500-change" class="text-sm mt-2">-- (--)</div>
        </div>

        <div class="index-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">NASDAQ</h3>
                <i class="fas fa-chart-line text-2xl text-green-600"></i>
            </div>
            <div id="nasdaq-price" class="text-3xl font-bold font-mono text-gray-900">--</div>
            <div id="nasdaq-change" class="text-sm mt-2">-- (--)</div>
        </div>

        <div class="index-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Dow Jones</h3>
                <i class="fas fa-chart-line text-2xl text-purple-600"></i>
            </div>
            <div id="dow-price" class="text-3xl font-bold font-mono text-gray-900">--</div>
            <div id="dow-change" class="text-sm mt-2">-- (--)</div>
        </div>
    </div>

    <!-- Market Stats -->
    <div class="market-stats grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        <div class="stat-card bg-white rounded-lg p-4 shadow border text-center">
            <div class="stat-icon text-2xl mb-2">📈</div>
            <div class="stat-label text-sm text-gray-600 mb-1">Advancing</div>
            <div id="advancing-stocks" class="stat-value text-xl font-bold text-green-600">--</div>
        </div>
        
        <div class="stat-card bg-white rounded-lg p-4 shadow border text-center">
            <div class="stat-icon text-2xl mb-2">📉</div>
            <div class="stat-label text-sm text-gray-600 mb-1">Declining</div>
            <div id="declining-stocks" class="stat-value text-xl font-bold text-red-600">--</div>
        </div>
        
        <div class="stat-card bg-white rounded-lg p-4 shadow border text-center">
            <div class="stat-icon text-2xl mb-2">📊</div>
            <div class="stat-label text-sm text-gray-600 mb-1">Volume</div>
            <div id="total-volume" class="stat-value text-xl font-bold text-gray-900">--</div>
        </div>
        
        <div class="stat-card bg-white rounded-lg p-4 shadow border text-center">
            <div class="stat-icon text-2xl mb-2">🔥</div>
            <div class="stat-label text-sm text-gray-600 mb-1">New Highs</div>
            <div id="new-highs" class="stat-value text-xl font-bold text-blue-600">--</div>
        </div>
    </div>

    <!-- Market Heatmap and Top Movers -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        <!-- Market Heatmap -->
        <div class="heatmap-section">
            <div class="section-header mb-4">
                <h3 class="text-xl font-semibold text-gray-900">Sector Performance</h3>
                <p class="text-sm text-gray-600">Today's sector performance heatmap</p>
            </div>
            <div class="heatmap-container bg-white rounded-lg p-6 shadow-lg border">
                <div id="sector-heatmap" class="heatmap-grid grid grid-cols-3 gap-2">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>

        <!-- Top Movers -->
        <div class="movers-section">
            <div class="section-header mb-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-xl font-semibold text-gray-900">Top Movers</h3>
                    <div class="mover-tabs">
                        <button class="tab-btn active" data-tab="gainers">Gainers</button>
                        <button class="tab-btn" data-tab="losers">Losers</button>
                        <button class="tab-btn" data-tab="volume">Volume</button>
                    </div>
                </div>
            </div>
            <div class="movers-container bg-white rounded-lg p-6 shadow-lg border">
                <div id="gainers-list" class="mover-list">
                    <!-- Populated by JavaScript -->
                </div>
                <div id="losers-list" class="mover-list hidden">
                    <!-- Populated by JavaScript -->
                </div>
                <div id="volume-list" class="mover-list hidden">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <!-- News Feed -->
    <div class="news-section">
        <div class="section-header mb-6">
            <h3 class="text-2xl font-semibold text-gray-900">Market News</h3>
            <p class="text-gray-600">Latest market developments and analysis</p>
        </div>
        <div class="news-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div id="news-feed" class="col-span-full">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>

</div>

<script>
class MarketOverviewManager {
    constructor() {
        this.marketData = null;
        this.updateInterval = 30000; // 30 seconds
        this.activeTab = 'gainers';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadMarketData();
        this.startPeriodicUpdates();
        
        console.log('Market Overview initialized');
    }
    
    async loadMarketData() {
        try {
            // Load market indices
            await this.loadMarketIndices();
            
            // Load market stats
            await this.loadMarketStats();
            
            // Load sector performance
            await this.loadSectorPerformance();
            
            // Load top movers
            await this.loadTopMovers();
            
            // Load market news
            await this.loadMarketNews();
            
            // Update last update time
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Market data loading error:', error);
            this.showError('Failed to load market data');
        }
    }
    
    async loadMarketIndices() {
        // Simulate API calls - replace with actual API integration
        const indices = {
            'SPY': { price: 4200.50, change: 15.25, changePercent: 0.36 },
            'QQQ': { price: 350.75, change: -2.10, changePercent: -0.59 },
            'DIA': { price: 338.90, change: 5.80, changePercent: 1.74 }
        };
        
        this.updateIndexDisplay('sp500', indices.SPY);
        this.updateIndexDisplay('nasdaq', indices.QQQ);
        this.updateIndexDisplay('dow', indices.DIA);
    }
    
    updateIndexDisplay(indexId, data) {
        const priceElement = document.getElementById(`${indexId}-price`);
        const changeElement = document.getElementById(`${indexId}-change`);
        
        if (priceElement && changeElement) {
            priceElement.textContent = StockScannerAPI.Utils.formatNumber(data.price);
            
            const changeClass = data.change >= 0 ? 'text-green-600' : 'text-red-600';
            changeElement.className = `text-sm mt-2 ${changeClass}`;
            changeElement.textContent = `${StockScannerAPI.Utils.formatCurrency(data.change)} (${StockScannerAPI.Utils.formatPercentage(data.changePercent)})`;
        }
    }
    
    async loadMarketStats() {
        // Simulate market stats
        const stats = {
            advancing: 1245,
            declining: 892,
            volume: 2547893000,
            newHighs: 87
        };
        
        document.getElementById('advancing-stocks').textContent = stats.advancing.toLocaleString();
        document.getElementById('declining-stocks').textContent = stats.declining.toLocaleString();
        document.getElementById('total-volume').textContent = StockScannerAPI.Utils.formatNumber(stats.volume);
        document.getElementById('new-highs').textContent = stats.newHighs;
    }
    
    async loadSectorPerformance() {
        const sectors = [
            { name: 'Technology', performance: 2.5, color: 'bg-green-500' },
            { name: 'Healthcare', performance: 1.8, color: 'bg-green-400' },
            { name: 'Finance', performance: -0.5, color: 'bg-red-400' },
            { name: 'Energy', performance: 3.2, color: 'bg-green-600' },
            { name: 'Consumer', performance: 0.8, color: 'bg-green-200' },
            { name: 'Industrials', performance: -1.2, color: 'bg-red-500' },
            { name: 'Materials', performance: 1.1, color: 'bg-green-300' },
            { name: 'Utilities', performance: -0.3, color: 'bg-red-300' },
            { name: 'Real Estate', performance: 0.4, color: 'bg-green-100' }
        ];
        
        const heatmapContainer = document.getElementById('sector-heatmap');
        heatmapContainer.innerHTML = sectors.map(sector => `
            <div class="heatmap-cell ${sector.color} text-white p-4 rounded-lg text-center">
                <div class="sector-name font-semibold text-sm mb-1">${sector.name}</div>
                <div class="sector-performance font-mono text-lg">${sector.performance >= 0 ? '+' : ''}${sector.performance}%</div>
            </div>
        `).join('');
    }
    
    async loadTopMovers() {
        const movers = {
            gainers: [
                { ticker: 'NVDA', price: 485.50, change: 25.30, changePercent: 5.5 },
                { ticker: 'AMD', price: 125.75, change: 8.90, changePercent: 7.6 },
                { ticker: 'TSLA', price: 245.20, change: 15.50, changePercent: 6.8 },
                { ticker: 'AMZN', price: 155.90, change: 7.25, changePercent: 4.9 },
                { ticker: 'GOOGL', price: 140.80, change: 6.15, changePercent: 4.6 }
            ],
            losers: [
                { ticker: 'META', price: 318.40, change: -12.60, changePercent: -3.8 },
                { ticker: 'NFLX', price: 398.20, change: -18.90, changePercent: -4.5 },
                { ticker: 'PYPL', price: 68.50, change: -5.20, changePercent: -7.1 },
                { ticker: 'SNAP', price: 9.85, change: -0.95, changePercent: -8.8 },
                { ticker: 'UBER', price: 45.30, change: -2.80, changePercent: -5.8 }
            ],
            volume: [
                { ticker: 'AAPL', price: 178.50, volume: 89500000 },
                { ticker: 'SPY', price: 420.50, volume: 67200000 },
                { ticker: 'QQQ', price: 350.75, volume: 45800000 },
                { ticker: 'TSLA', price: 245.20, volume: 38900000 },
                { ticker: 'NVDA', price: 485.50, volume: 32100000 }
            ]
        };
        
        this.renderMovers('gainers', movers.gainers, true);
        this.renderMovers('losers', movers.losers, true);
        this.renderMovers('volume', movers.volume, false);
    }
    
    renderMovers(type, data, showChange) {
        const container = document.getElementById(`${type}-list`);
        
        container.innerHTML = data.map(item => `
            <div class="mover-item flex items-center justify-between p-3 border-b hover:bg-gray-50">
                <div class="mover-info">
                    <div class="ticker font-mono font-semibold">${item.ticker}</div>
                    <div class="price font-mono text-sm text-gray-600">$${item.price?.toFixed(2) || '--'}</div>
                </div>
                <div class="mover-data text-right">
                    ${showChange ? `
                        <div class="change font-mono ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}">
                            ${item.change >= 0 ? '+' : ''}${item.change?.toFixed(2)}
                        </div>
                        <div class="change-percent text-sm ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}">
                            ${item.changePercent >= 0 ? '+' : ''}${item.changePercent?.toFixed(2)}%
                        </div>
                    ` : `
                        <div class="volume font-mono text-sm">
                            ${StockScannerAPI.Utils.formatNumber(item.volume)}
                        </div>
                    `}
                </div>
            </div>
        `).join('');
    }
    
    async loadMarketNews() {
        const news = [
            {
                title: "Fed Signals Potential Rate Cuts Amid Economic Uncertainty",
                summary: "Federal Reserve officials hint at possible interest rate reductions...",
                source: "MarketWatch",
                time: "2 hours ago",
                url: "#"
            },
            {
                title: "Tech Stocks Rally on Strong Earnings Reports",
                summary: "Major technology companies exceed expectations...",
                source: "Reuters",
                time: "4 hours ago", 
                url: "#"
            },
            {
                title: "Oil Prices Surge on Supply Concerns",
                summary: "Crude oil futures jump as geopolitical tensions rise...",
                source: "Bloomberg",
                time: "6 hours ago",
                url: "#"
            }
        ];
        
        const newsContainer = document.getElementById('news-feed');
        newsContainer.innerHTML = news.map(article => `
            <div class="news-article bg-white rounded-lg p-6 shadow border hover:shadow-lg transition-shadow">
                <h4 class="news-title font-semibold text-gray-900 mb-2">
                    <a href="${article.url}" class="hover:text-blue-600">${article.title}</a>
                </h4>
                <p class="news-summary text-gray-600 text-sm mb-3">${article.summary}</p>
                <div class="news-meta flex items-center justify-between text-xs text-gray-500">
                    <span class="news-source">${article.source}</span>
                    <span class="news-time">${article.time}</span>
                </div>
            </div>
        `).join('');
    }
    
    bindEvents() {
        // Tab switching for top movers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            }
        });
        
        // Refresh data button (if added)
        document.addEventListener('click', (e) => {
            if (e.target.id === 'refresh-market-data') {
                this.loadMarketData();
            }
        });
    }
    
    switchTab(tab) {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        
        // Show/hide mover lists
        document.querySelectorAll('.mover-list').forEach(list => {
            list.classList.add('hidden');
        });
        document.getElementById(`${tab}-list`).classList.remove('hidden');
        
        this.activeTab = tab;
    }
    
    startPeriodicUpdates() {
        setInterval(() => {
            this.loadMarketData();
        }, this.updateInterval);
    }
    
    updateLastUpdateTime() {
        const now = new Date();
        document.getElementById('last-update-time').textContent = 
            now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
    }
    
    showError(message) {
        StockScannerAPI.Toast.show(message, 'error');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    new MarketOverviewManager();
});
</script>

<style>
.tab-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    background: white;
    color: #6b7280;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:first-child {
    border-radius: 0.375rem 0 0 0.375rem;
}

.tab-btn:last-child {
    border-radius: 0 0.375rem 0.375rem 0;
    border-left: none;
}

.tab-btn:not(:first-child):not(:last-child) {
    border-left: none;
}

.tab-btn.active {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
}

.tab-btn:hover:not(.active) {
    background: #f3f4f6;
}

.heatmap-cell {
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.news-article {
    margin-bottom: 1rem;
}

.status-dot.market-open {
    background-color: #10b981;
}

.status-dot.market-closed {
    background-color: #ef4444;
}
</style>

<?php get_footer(); ?>