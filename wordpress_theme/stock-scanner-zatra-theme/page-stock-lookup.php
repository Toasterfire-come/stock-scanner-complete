<?php
/**
 * Template Name: Stock Lookup
 * 
 * The template for displaying stock lookup functionality
 */

get_header(); 
?>

<div class="stock-lookup-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-search"></i>
                Stock Lookup
            </h1>
            <p class="page-subtitle">Search for real-time stock quotes and detailed financial information</p>
        </div>
    </div>

    <div class="lookup-content">
        <div class="container">
            <!-- Search Section -->
            <div class="search-section">
                <div class="search-container">
                    <form class="stock-search-form" id="stockSearchForm">
                        <div class="search-input-group">
                            <input type="text" 
                                   name="symbol" 
                                   id="stockSymbol" 
                                   placeholder="Enter stock symbol (e.g., AAPL, GOOGL, TSLA)" 
                                   class="search-input" 
                                   autocomplete="off">
                            <button type="submit" class="search-btn">
                                <i class="fas fa-search"></i>
                                Search
                            </button>
                        </div>
                        <div class="search-suggestions" id="searchSuggestions"></div>
                    </form>
                </div>
            </div>

            <!-- Loading Indicator -->
            <div class="loading-indicator" id="loadingIndicator" style="display: none;">
                <i class="fas fa-spinner fa-spin"></i>
                Searching for stock data...
            </div>

            <!-- Search Results -->
            <div class="search-results" id="searchResults"></div>

            <!-- Popular Stocks Section -->
            <div class="popular-stocks-section">
                <h2>Popular Stocks</h2>
                <div class="popular-stocks-grid" id="popularStocks">
                    <div class="loading-spinner">Loading popular stocks...</div>
                </div>
            </div>

            <!-- Market Indices -->
            <div class="market-indices-section">
                <h2>Major Market Indices</h2>
                <div class="indices-grid" id="marketIndices">
                    <div class="loading-spinner">Loading market indices...</div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.stock-lookup-container {
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
    margin: 1rem 0 0 0;
}

.lookup-content {
    padding: 3rem 0;
}

.search-section {
    margin-bottom: 3rem;
}

.search-container {
    max-width: 600px;
    margin: 0 auto;
    position: relative;
}

.search-input-group {
    display: flex;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    overflow: hidden;
}

.search-input {
    flex: 1;
    padding: 1.5rem;
    border: none;
    font-size: 1.1rem;
    outline: none;
}

.search-btn {
    background: #3685fb;
    color: white;
    border: none;
    padding: 1.5rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: background 0.2s;
}

.search-btn:hover {
    background: #2563eb;
}

.search-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    max-height: 300px;
    overflow-y: auto;
    z-index: 10;
    display: none;
}

.suggestion-item {
    padding: 1rem 1.5rem;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
}

.suggestion-item:hover {
    background: #f8f9fa;
}

.suggestion-item:last-child {
    border-bottom: none;
}

.loading-indicator {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 1.1rem;
}

.search-results {
    margin-bottom: 3rem;
}

.stock-result-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
    margin-bottom: 2rem;
}

.stock-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 2rem;
}

.stock-title {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.stock-name h2 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
}

.stock-company {
    color: rgba(255,255,255,0.8);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

.stock-price-info {
    text-align: right;
}

.current-price {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}

.price-change {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.positive { color: #10b981; }
.negative { color: #ef4444; }

.stock-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}

.action-btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.1);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
}

.action-btn:hover {
    background: rgba(255,255,255,0.2);
}

.stock-details {
    padding: 2rem;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.detail-item {
    text-align: center;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.detail-label {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.detail-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
}

.stock-chart-container {
    margin-top: 2rem;
    height: 400px;
}

.popular-stocks-section,
.market-indices-section {
    margin-bottom: 3rem;
}

.popular-stocks-section h2,
.market-indices-section h2 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a1a1a;
}

.popular-stocks-grid,
.indices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.stock-card,
.index-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
    cursor: pointer;
}

.stock-card:hover,
.index-card:hover {
    transform: translateY(-2px);
}

.stock-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.stock-symbol {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
}

.stock-name-small {
    color: #666;
    font-size: 0.9rem;
}

.stock-price-small {
    text-align: right;
}

.price {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
}

.change {
    font-size: 0.9rem;
    font-weight: 500;
}

.loading-spinner {
    text-align: center;
    color: #666;
    padding: 3rem;
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
    }
    
    .search-input-group {
        flex-direction: column;
    }
    
    .search-btn {
        border-radius: 0 0 12px 12px;
    }
    
    .stock-title {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .stock-price-info {
        text-align: left;
    }
    
    .details-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
    
    .popular-stocks-grid,
    .indices-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeStockLookup();
    loadPopularStocks();
    loadMarketIndices();
});

function initializeStockLookup() {
    const form = document.getElementById('stockSearchForm');
    const input = document.getElementById('stockSymbol');
    const suggestions = document.getElementById('searchSuggestions');
    
    form.addEventListener('submit', handleStockSearch);
    input.addEventListener('input', handleSearchInput);
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            suggestions.style.display = 'none';
        }
    });
}

function handleStockSearch(e) {
    e.preventDefault();
    const symbol = document.getElementById('stockSymbol').value.trim().toUpperCase();
    
    if (!symbol) return;
    
    searchStock(symbol);
}

function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    if (query.length >= 2) {
        showSearchSuggestions(query);
    } else {
        hideSearchSuggestions();
    }
}

function showSearchSuggestions(query) {
    // Simulate stock suggestions
    const suggestions = [
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
        { symbol: 'TSLA', name: 'Tesla Inc.' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.' }
    ].filter(stock => 
        stock.symbol.includes(query.toUpperCase()) || 
        stock.name.toLowerCase().includes(query.toLowerCase())
    );
    
    const suggestionsContainer = document.getElementById('searchSuggestions');
    
    if (suggestions.length > 0) {
        suggestionsContainer.innerHTML = suggestions.map(stock => `
            <div class="suggestion-item" onclick="selectSuggestion('${stock.symbol}')">
                <strong>${stock.symbol}</strong> - ${stock.name}
            </div>
        `).join('');
        suggestionsContainer.style.display = 'block';
    } else {
        hideSearchSuggestions();
    }
}

function hideSearchSuggestions() {
    document.getElementById('searchSuggestions').style.display = 'none';
}

function selectSuggestion(symbol) {
    document.getElementById('stockSymbol').value = symbol;
    hideSearchSuggestions();
    searchStock(symbol);
}

function searchStock(symbol) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('searchResults');
    
    loadingIndicator.style.display = 'block';
    resultsContainer.innerHTML = '';
    
    // Simulate API call
    setTimeout(() => {
        loadingIndicator.style.display = 'none';
        displayStockResult(symbol);
    }, 1500);
}

function displayStockResult(symbol) {
    // Simulate stock data
    const stockData = {
        symbol: symbol,
        name: getCompanyName(symbol),
        price: (Math.random() * 500 + 50).toFixed(2),
        change: (Math.random() * 20 - 10).toFixed(2),
        changePercent: (Math.random() * 10 - 5).toFixed(2),
        volume: Math.floor(Math.random() * 10000000),
        marketCap: (Math.random() * 2000 + 100).toFixed(1) + 'B',
        peRatio: (Math.random() * 50 + 5).toFixed(2),
        dayHigh: (Math.random() * 500 + 50).toFixed(2),
        dayLow: (Math.random() * 500 + 50).toFixed(2),
        fiftyTwoWeekHigh: (Math.random() * 600 + 100).toFixed(2),
        fiftyTwoWeekLow: (Math.random() * 200 + 20).toFixed(2)
    };
    
    const changeClass = parseFloat(stockData.change) >= 0 ? 'positive' : 'negative';
    const changeSymbol = parseFloat(stockData.change) >= 0 ? '+' : '';
    
    const resultHTML = `
        <div class="stock-result-card">
            <div class="stock-header">
                <div class="stock-title">
                    <div class="stock-name">
                        <h2>${stockData.symbol}</h2>
                        <div class="stock-company">${stockData.name}</div>
                    </div>
                    <div class="stock-price-info">
                        <div class="current-price">$${stockData.price}</div>
                        <div class="price-change ${changeClass}">
                            ${changeSymbol}$${stockData.change} (${changeSymbol}${stockData.changePercent}%)
                        </div>
                    </div>
                </div>
                <div class="stock-actions">
                    <button class="action-btn add-to-watchlist" data-symbol="${stockData.symbol}">
                        <i class="fas fa-plus"></i> Add to Watchlist
                    </button>
                    <a href="/portfolio/" class="action-btn">
                        <i class="fas fa-briefcase"></i> View Portfolio
                    </a>
                </div>
            </div>
            <div class="stock-details">
                <div class="details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Volume</div>
                        <div class="detail-value">${stockData.volume.toLocaleString()}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Market Cap</div>
                        <div class="detail-value">$${stockData.marketCap}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">P/E Ratio</div>
                        <div class="detail-value">${stockData.peRatio}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Day High</div>
                        <div class="detail-value">$${stockData.dayHigh}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Day Low</div>
                        <div class="detail-value">$${stockData.dayLow}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">52W High</div>
                        <div class="detail-value">$${stockData.fiftyTwoWeekHigh}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">52W Low</div>
                        <div class="detail-value">$${stockData.fiftyTwoWeekLow}</div>
                    </div>
                </div>
                <div class="stock-chart-container">
                    <canvas id="stockChart-${stockData.symbol}" class="stock-chart" data-symbol="${stockData.symbol}"></canvas>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('searchResults').innerHTML = resultHTML;
    
    // Initialize chart for this stock
    if (typeof Chart !== 'undefined') {
        createStockChart(`stockChart-${stockData.symbol}`, stockData.symbol);
    }
}

function createStockChart(canvasId, symbol) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Generate sample data
    const labels = [];
    const data = [];
    const basePrice = Math.random() * 500 + 50;
    
    for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        const variation = (Math.random() - 0.5) * 20;
        data.push((basePrice + variation).toFixed(2));
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: symbol,
                data: data,
                borderColor: '#3685fb',
                backgroundColor: 'rgba(54, 133, 251, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
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
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function loadPopularStocks() {
    const popularStocks = [
        { symbol: 'AAPL', name: 'Apple Inc.', price: 175.43, change: 2.35 },
        { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 2734.89, change: -15.67 },
        { symbol: 'MSFT', name: 'Microsoft Corp.', price: 334.85, change: 3.21 },
        { symbol: 'TSLA', name: 'Tesla Inc.', price: 245.67, change: 12.45 },
        { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 3156.78, change: -8.90 },
        { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 892.34, change: 25.67 }
    ];
    
    const container = document.getElementById('popularStocks');
    container.innerHTML = popularStocks.map(stock => {
        const changeClass = stock.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = stock.change >= 0 ? '+' : '';
        const changePercent = ((stock.change / stock.price) * 100).toFixed(2);
        
        return `
            <div class="stock-card" onclick="searchStock('${stock.symbol}')">
                <div class="stock-info">
                    <div>
                        <div class="stock-symbol">${stock.symbol}</div>
                        <div class="stock-name-small">${stock.name}</div>
                    </div>
                    <div class="stock-price-small">
                        <div class="price">$${stock.price.toFixed(2)}</div>
                        <div class="change ${changeClass}">
                            ${changeSymbol}${stock.change.toFixed(2)} (${changeSymbol}${changePercent}%)
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function loadMarketIndices() {
    const indices = [
        { name: 'S&P 500', symbol: 'SPX', value: 4567.23, change: 12.45 },
        { name: 'NASDAQ', symbol: 'IXIC', value: 14234.56, change: -23.67 },
        { name: 'Dow Jones', symbol: 'DJI', value: 34567.89, change: 45.12 }
    ];
    
    const container = document.getElementById('marketIndices');
    container.innerHTML = indices.map(index => {
        const changeClass = index.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = index.change >= 0 ? '+' : '';
        const changePercent = ((index.change / index.value) * 100).toFixed(2);
        
        return `
            <div class="index-card">
                <div class="stock-info">
                    <div>
                        <div class="stock-symbol">${index.name}</div>
                        <div class="stock-name-small">${index.symbol}</div>
                    </div>
                    <div class="stock-price-small">
                        <div class="price">${index.value.toLocaleString()}</div>
                        <div class="change ${changeClass}">
                            ${changeSymbol}${index.change.toFixed(2)} (${changeSymbol}${changePercent}%)
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function getCompanyName(symbol) {
    const companies = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'TSLA': 'Tesla Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corporation',
        'META': 'Meta Platforms Inc.',
        'NFLX': 'Netflix Inc.',
        'AMD': 'Advanced Micro Devices Inc.'
    };
    
    return companies[symbol] || `${symbol} Corporation`;
}
</script>

<?php get_footer(); ?>