<?php
/**
 * Template Name: Market Overview
 * 
 * The template for displaying comprehensive market data and analysis
 */

get_header(); 
?>

<div class="market-overview-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-chart-area"></i>
                Market Overview
            </h1>
            <p class="page-subtitle">Real-time market data, indices performance, and comprehensive market analysis</p>
            
            <div class="market-status-banner" id="marketStatus">
                <div class="status-indicator">
                    <span class="status-light open" id="statusLight"></span>
                    <span class="status-text" id="statusText">Market Open</span>
                </div>
                <div class="market-time">
                    <i class="fas fa-clock"></i>
                    Eastern Time: <span id="currentTime">Loading...</span>
                </div>
                <div class="next-session" id="nextSession">
                    Next: Pre-market opens at 4:00 AM ET
                </div>
            </div>
        </div>
    </div>

    <div class="market-content">
        <div class="container">
            <!-- Major Indices -->
            <div class="indices-section">
                <div class="section-header">
                    <h2>Major Indices</h2>
                    <div class="refresh-control">
                        <span class="last-updated" id="lastUpdated">Last updated: --</span>
                        <button class="btn btn-outline btn-sm" id="refreshIndices">
                            <i class="fas fa-sync-alt"></i>
                            Refresh
                        </button>
                    </div>
                </div>
                
                <div class="indices-grid" id="indicesGrid">
                    <div class="loading-spinner">Loading market data...</div>
                </div>
            </div>

            <!-- Market Movers -->
            <div class="movers-section">
                <div class="section-header">
                    <h2>Market Movers</h2>
                    <div class="movers-tabs">
                        <button class="tab-btn active" data-tab="gainers">Top Gainers</button>
                        <button class="tab-btn" data-tab="losers">Top Losers</button>
                        <button class="tab-btn" data-tab="active">Most Active</button>
                    </div>
                </div>
                
                <div class="movers-content" id="moversContent">
                    <div class="loading-spinner">Loading market movers...</div>
                </div>
            </div>

            <!-- Market Sectors -->
            <div class="sectors-section">
                <div class="section-header">
                    <h2>Sector Performance</h2>
                    <div class="view-toggle">
                        <button class="view-btn active" data-view="heat">
                            <i class="fas fa-th"></i>
                            Heat Map
                        </button>
                        <button class="view-btn" data-view="list">
                            <i class="fas fa-list"></i>
                            List View
                        </button>
                    </div>
                </div>
                
                <div class="sectors-content" id="sectorsContent">
                    <div class="loading-spinner">Loading sector data...</div>
                </div>
            </div>

            <!-- Market News & Analysis -->
            <div class="news-analysis-section">
                <div class="section-header">
                    <h2>Market News & Analysis</h2>
                    <a href="/stock-news/" class="btn btn-outline btn-sm">
                        View All News
                        <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
                
                <div class="news-grid" id="newsGrid">
                    <div class="loading-spinner">Loading market news...</div>
                </div>
            </div>

            <!-- Market Statistics -->
            <div class="stats-section">
                <div class="section-header">
                    <h2>Market Statistics</h2>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value" id="advancingStocks">--</div>
                            <div class="stat-label">Advancing</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon declining">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value" id="decliningStocks">--</div>
                            <div class="stat-label">Declining</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon neutral">
                            <i class="fas fa-minus"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value" id="unchangedStocks">--</div>
                            <div class="stat-label">Unchanged</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-chart-bar"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value" id="totalVolume">--</div>
                            <div class="stat-label">Total Volume</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fear & Greed Index -->
            <div class="fear-greed-section">
                <div class="section-header">
                    <h2>Fear & Greed Index</h2>
                    <div class="info-tooltip" title="The Fear & Greed Index measures market sentiment on a scale of 0-100">
                        <i class="fas fa-info-circle"></i>
                    </div>
                </div>
                
                <div class="fear-greed-content">
                    <div class="fear-greed-meter">
                        <div class="meter-container">
                            <div class="meter-circle">
                                <div class="meter-fill" id="meterFill"></div>
                                <div class="meter-center">
                                    <span class="meter-value" id="fearGreedValue">50</span>
                                    <span class="meter-label" id="fearGreedLabel">Neutral</span>
                                </div>
                            </div>
                        </div>
                        <div class="meter-scale">
                            <div class="scale-item extreme-fear">
                                <span class="scale-value">0</span>
                                <span class="scale-label">Extreme Fear</span>
                            </div>
                            <div class="scale-item fear">
                                <span class="scale-value">25</span>
                                <span class="scale-label">Fear</span>
                            </div>
                            <div class="scale-item neutral">
                                <span class="scale-value">50</span>
                                <span class="scale-label">Neutral</span>
                            </div>
                            <div class="scale-item greed">
                                <span class="scale-value">75</span>
                                <span class="scale-label">Greed</span>
                            </div>
                            <div class="scale-item extreme-greed">
                                <span class="scale-value">100</span>
                                <span class="scale-label">Extreme Greed</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="fear-greed-factors">
                        <h3>Contributing Factors</h3>
                        <div class="factors-list" id="factorsList">
                            <div class="loading-spinner">Loading factors...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.market-overview-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 2rem 0;
}

.market-status-banner {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
    max-width: 800px;
    margin: 0 auto;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.status-light {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s infinite;
}

.status-light.closed {
    background: #ef4444;
    animation: none;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-text {
    font-weight: 600;
    font-size: 1.1rem;
}

.market-time {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
}

.next-session {
    font-size: 0.9rem;
    opacity: 0.8;
}

.market-content {
    padding: 3rem 0;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.refresh-control {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.last-updated {
    font-size: 0.9rem;
    color: #666;
}

.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
}

.btn-outline {
    background: transparent;
    color: #666;
    border: 1px solid #e1e5e9;
}

.btn-outline:hover {
    background: #f8f9fa;
    border-color: #3685fb;
    color: #3685fb;
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.8rem;
}

.indices-section,
.movers-section,
.sectors-section,
.news-analysis-section,
.stats-section,
.fear-greed-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.indices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.index-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    transition: transform 0.2s;
}

.index-card:hover {
    transform: translateY(-2px);
}

.index-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.index-symbol {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
}

.index-name {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.25rem;
}

.index-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
}

.index-change {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.index-change.positive { color: #10b981; }
.index-change.negative { color: #ef4444; }

.index-chart {
    height: 60px;
    margin-top: 1rem;
}

.movers-tabs {
    display: flex;
    gap: 0.5rem;
}

.tab-btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}

.tab-btn:hover,
.tab-btn.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.movers-content {
    margin-top: 1.5rem;
}

.movers-table {
    display: grid;
    grid-template-columns: 1fr 100px 120px 120px 120px;
    gap: 1rem;
}

.movers-header {
    display: contents;
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
}

.movers-header > div {
    padding: 1rem 0.5rem;
    border-bottom: 2px solid #e1e5e9;
}

.mover-row {
    display: contents;
    font-size: 0.9rem;
}

.mover-row > div {
    padding: 1rem 0.5rem;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    align-items: center;
}

.mover-symbol {
    font-weight: 700;
    color: #3685fb;
    cursor: pointer;
}

.mover-symbol:hover {
    text-decoration: underline;
}

.mover-company {
    color: #666;
    font-size: 0.8rem;
    margin-top: 0.25rem;
}

.mover-price {
    font-weight: 600;
    color: #1a1a1a;
}

.mover-change {
    font-weight: 600;
}

.mover-change.positive { color: #10b981; }
.mover-change.negative { color: #ef4444; }

.view-toggle {
    display: flex;
    gap: 0.25rem;
}

.view-btn {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    border-radius: 4px;
}

.view-btn:hover,
.view-btn.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.sectors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.sector-card {
    border-radius: 8px;
    padding: 1rem;
    color: white;
    position: relative;
    overflow: hidden;
}

.sector-name {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.sector-change {
    font-size: 1.25rem;
    font-weight: 700;
}

.news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.news-card {
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    padding: 1rem;
    transition: transform 0.2s;
    cursor: pointer;
}

.news-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.news-title {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

.news-summary {
    color: #666;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 0.75rem;
}

.news-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: #888;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #10b981;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.stat-icon.declining {
    background: #ef4444;
}

.stat-icon.neutral {
    background: #6b7280;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
}

.fear-greed-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
}

.meter-container {
    text-align: center;
}

.meter-circle {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(
        from 0deg,
        #ef4444 0deg 72deg,
        #f59e0b 72deg 144deg,
        #6b7280 144deg 216deg,
        #10b981 216deg 288deg,
        #059669 288deg 360deg
    );
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 2rem;
    position: relative;
}

.meter-fill {
    position: absolute;
    width: 160px;
    height: 160px;
    background: white;
    border-radius: 50%;
}

.meter-center {
    position: relative;
    z-index: 1;
    text-align: center;
}

.meter-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
}

.meter-label {
    display: block;
    font-size: 1rem;
    color: #666;
    margin-top: 0.25rem;
}

.meter-scale {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
}

.scale-item {
    text-align: center;
    flex: 1;
}

.scale-value {
    display: block;
    font-weight: 600;
    color: #333;
}

.scale-label {
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-top: 0.25rem;
}

.fear-greed-factors h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 1rem 0;
}

.factors-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.factor-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 6px;
}

.factor-name {
    color: #333;
    font-weight: 500;
}

.factor-value {
    font-weight: 600;
}

.factor-value.positive { color: #10b981; }
.factor-value.negative { color: #ef4444; }
.factor-value.neutral { color: #6b7280; }

.loading-spinner {
    text-align: center;
    padding: 3rem;
    color: #666;
    font-size: 1.1rem;
}

.info-tooltip {
    cursor: help;
    color: #666;
}

@media (max-width: 1024px) {
    .fear-greed-content {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .market-status-banner {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .section-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .movers-tabs {
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .movers-table {
        grid-template-columns: 1fr 80px 100px;
        font-size: 0.8rem;
    }
    
    .movers-table .mover-row > div:nth-child(4),
    .movers-table .movers-header > div:nth-child(4),
    .movers-table .mover-row > div:nth-child(5),
    .movers-table .movers-header > div:nth-child(5) {
        display: none;
    }
    
    .meter-circle {
        width: 150px;
        height: 150px;
    }
    
    .meter-fill {
        width: 120px;
        height: 120px;
    }
    
    .meter-value {
        font-size: 1.5rem;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeMarketOverview();
    loadMarketData();
    updateClock();
    setInterval(updateClock, 1000);
});

function initializeMarketOverview() {
    // Refresh button
    document.getElementById('refreshIndices').addEventListener('click', loadMarketData);
    
    // Movers tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadMoversData(this.dataset.tab);
        });
    });
    
    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            toggleSectorsView(this.dataset.view);
        });
    });
}

function loadMarketData() {
    loadIndicesData();
    loadMoversData('gainers');
    loadSectorsData();
    loadNewsData();
    loadStatsData();
    loadFearGreedData();
    
    // Update last updated time
    document.getElementById('lastUpdated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
}

function loadIndicesData() {
    const indicesGrid = document.getElementById('indicesGrid');
    
    setTimeout(() => {
        const indices = [
            { symbol: 'S&P 500', name: 'Standard & Poor\'s 500', value: 4756.50, change: 23.45, changePercent: 0.49 },
            { symbol: 'NASDAQ', name: 'NASDAQ Composite', value: 15024.71, change: -45.32, changePercent: -0.30 },
            { symbol: 'DOW', name: 'Dow Jones Industrial Average', value: 35432.23, change: 156.78, changePercent: 0.44 },
            { symbol: 'RUSSELL 2000', name: 'Russell 2000 Index', value: 2234.56, change: -12.34, changePercent: -0.55 }
        ];
        
        indicesGrid.innerHTML = indices.map(index => {
            const changeClass = index.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = index.change >= 0 ? '+' : '';
            
            return `
                <div class="index-card">
                    <div class="index-header">
                        <div>
                            <div class="index-symbol">${index.symbol}</div>
                            <div class="index-name">${index.name}</div>
                        </div>
                    </div>
                    <div class="index-value">${index.value.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                    <div class="index-change ${changeClass}">
                        <i class="fas fa-arrow-${index.change >= 0 ? 'up' : 'down'}"></i>
                        ${changeSymbol}${Math.abs(index.change).toFixed(2)} (${changeSymbol}${index.changePercent.toFixed(2)}%)
                    </div>
                    <div class="index-chart">
                        <canvas id="chart-${index.symbol.replace(/\s+/g, '')}" width="200" height="60"></canvas>
                    </div>
                </div>
            `;
        }).join('');
        
        // Create mini charts
        indices.forEach(index => {
            createMiniChart(`chart-${index.symbol.replace(/\s+/g, '')}`, index.change >= 0);
        });
    }, 800);
}

function createMiniChart(canvasId, isPositive) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const data = generateMiniChartData();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                borderColor: isPositive ? '#10b981' : '#ef4444',
                backgroundColor: isPositive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            elements: {
                point: { radius: 0 }
            }
        }
    });
}

function generateMiniChartData() {
    const labels = [];
    const values = [];
    const baseValue = 100;
    
    for (let i = 0; i < 20; i++) {
        labels.push(i);
        values.push(baseValue + (Math.random() - 0.5) * 10);
    }
    
    return { labels, values };
}

function loadMoversData(type) {
    const moversContent = document.getElementById('moversContent');
    
    moversContent.innerHTML = '<div class="loading-spinner">Loading market movers...</div>';
    
    setTimeout(() => {
        const movers = generateMoversData(type);
        
        moversContent.innerHTML = `
            <div class="movers-table">
                <div class="movers-header">
                    <div>Symbol</div>
                    <div>Price</div>
                    <div>Change</div>
                    <div>% Change</div>
                    <div>Volume</div>
                </div>
                ${movers.map(mover => {
                    const changeClass = mover.change >= 0 ? 'positive' : 'negative';
                    const changeSymbol = mover.change >= 0 ? '+' : '';
                    
                    return `
                        <div class="mover-row">
                            <div>
                                <div class="mover-symbol" onclick="viewStock('${mover.symbol}')">${mover.symbol}</div>
                                <div class="mover-company">${mover.company}</div>
                            </div>
                            <div class="mover-price">$${mover.price.toFixed(2)}</div>
                            <div class="mover-change ${changeClass}">${changeSymbol}${mover.change.toFixed(2)}</div>
                            <div class="mover-change ${changeClass}">${changeSymbol}${mover.changePercent.toFixed(2)}%</div>
                            <div class="mover-volume">${formatVolume(mover.volume)}</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }, 600);
}

function generateMoversData(type) {
    const stocks = [
        { symbol: 'TSLA', company: 'Tesla Inc.', price: 234.56, volume: 87654000 },
        { symbol: 'NVDA', company: 'NVIDIA Corp.', price: 456.78, volume: 45678000 },
        { symbol: 'AMD', company: 'Advanced Micro Devices', price: 123.45, volume: 34567000 },
        { symbol: 'AAPL', company: 'Apple Inc.', price: 175.43, volume: 58742000 },
        { symbol: 'MSFT', company: 'Microsoft Corp.', price: 334.89, volume: 32156000 }
    ];
    
    return stocks.map(stock => ({
        ...stock,
        change: type === 'gainers' ? Math.random() * 20 + 5 : 
                type === 'losers' ? -(Math.random() * 15 + 3) : 
                (Math.random() - 0.5) * 10,
        changePercent: type === 'gainers' ? Math.random() * 8 + 2 : 
                      type === 'losers' ? -(Math.random() * 6 + 1) : 
                      (Math.random() - 0.5) * 4
    }));
}

function loadSectorsData() {
    const sectorsContent = document.getElementById('sectorsContent');
    
    setTimeout(() => {
        const sectors = [
            { name: 'Technology', change: 2.34 },
            { name: 'Healthcare', change: 1.45 },
            { name: 'Financial', change: -0.87 },
            { name: 'Consumer Discretionary', change: 1.67 },
            { name: 'Energy', change: -2.13 },
            { name: 'Industrial', change: 0.92 },
            { name: 'Materials', change: -1.34 },
            { name: 'Utilities', change: 0.45 },
            { name: 'Real Estate', change: -0.23 },
            { name: 'Telecommunications', change: 0.78 }
        ];
        
        sectorsContent.innerHTML = `
            <div class="sectors-grid">
                ${sectors.map(sector => {
                    const changeClass = sector.change >= 0 ? 'positive' : 'negative';
                    const bgColor = sector.change >= 0 ? 
                        `rgba(16, 185, 129, ${Math.abs(sector.change) * 0.3 + 0.4})` : 
                        `rgba(239, 68, 68, ${Math.abs(sector.change) * 0.3 + 0.4})`;
                    
                    return `
                        <div class="sector-card" style="background: ${bgColor}">
                            <div class="sector-name">${sector.name}</div>
                            <div class="sector-change">${sector.change >= 0 ? '+' : ''}${sector.change.toFixed(2)}%</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }, 1000);
}

function loadNewsData() {
    const newsGrid = document.getElementById('newsGrid');
    
    setTimeout(() => {
        const news = [
            {
                title: 'Federal Reserve Signals Potential Rate Changes',
                summary: 'The Federal Reserve indicated possible adjustments to interest rates in the coming months...',
                source: 'Reuters',
                time: '2 hours ago'
            },
            {
                title: 'Tech Stocks Rally on Strong Earnings',
                summary: 'Major technology companies reported better-than-expected quarterly results...',
                source: 'Bloomberg',
                time: '3 hours ago'
            },
            {
                title: 'Oil Prices Surge on Supply Concerns',
                summary: 'Crude oil prices jumped as supply chain disruptions continue to impact global markets...',
                source: 'MarketWatch',
                time: '4 hours ago'
            }
        ];
        
        newsGrid.innerHTML = news.map(article => `
            <div class="news-card">
                <div class="news-title">${article.title}</div>
                <div class="news-summary">${article.summary}</div>
                <div class="news-meta">
                    <span class="news-source">${article.source}</span>
                    <span class="news-time">${article.time}</span>
                </div>
            </div>
        `).join('');
    }, 1200);
}

function loadStatsData() {
    setTimeout(() => {
        document.getElementById('advancingStocks').textContent = '2,847';
        document.getElementById('decliningStocks').textContent = '1,523';
        document.getElementById('unchangedStocks').textContent = '234';
        document.getElementById('totalVolume').textContent = '4.2B';
    }, 900);
}

function loadFearGreedData() {
    const factorsList = document.getElementById('factorsList');
    
    setTimeout(() => {
        const fearGreedValue = 68;
        const label = fearGreedValue < 25 ? 'Extreme Fear' :
                     fearGreedValue < 45 ? 'Fear' :
                     fearGreedValue < 55 ? 'Neutral' :
                     fearGreedValue < 75 ? 'Greed' : 'Extreme Greed';
        
        document.getElementById('fearGreedValue').textContent = fearGreedValue;
        document.getElementById('fearGreedLabel').textContent = label;
        
        const factors = [
            { name: 'Stock Price Momentum', value: 72, trend: 'positive' },
            { name: 'Stock Price Strength', value: 64, trend: 'positive' },
            { name: 'Stock Price Breadth', value: 58, trend: 'positive' },
            { name: 'Put/Call Ratio', value: 45, trend: 'neutral' },
            { name: 'Market Volatility', value: 34, trend: 'negative' },
            { name: 'Safe Haven Demand', value: 42, trend: 'neutral' },
            { name: 'Junk Bond Demand', value: 71, trend: 'positive' }
        ];
        
        factorsList.innerHTML = factors.map(factor => `
            <div class="factor-item">
                <span class="factor-name">${factor.name}</span>
                <span class="factor-value ${factor.trend}">${factor.value}</span>
            </div>
        `).join('');
    }, 1500);
}

function toggleSectorsView(view) {
    // Implementation for different sector views
    console.log('Switching to', view, 'view');
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour12: true,
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit'
    });
    
    document.getElementById('currentTime').textContent = timeString;
    
    // Update market status based on time
    const hour = now.getHours();
    const isMarketOpen = hour >= 9 && hour < 16; // Simplified market hours
    
    const statusLight = document.getElementById('statusLight');
    const statusText = document.getElementById('statusText');
    
    if (isMarketOpen) {
        statusLight.className = 'status-light open';
        statusText.textContent = 'Market Open';
    } else {
        statusLight.className = 'status-light closed';
        statusText.textContent = 'Market Closed';
    }
}

function viewStock(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
}
</script>

<?php get_footer(); ?>