<?php
/**
 * Template Name: Stock Screener
 * 
 * The template for displaying stock screening and filtering functionality
 */

get_header(); 
?>

<div class="stock-screener-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-filter"></i>
                Stock Screener
            </h1>
            <p class="page-subtitle">Find stocks that match your investment criteria with our advanced screening tools</p>
        </div>
    </div>

    <div class="screener-content">
        <div class="container">
            <div class="screener-layout">
                <!-- Filters Sidebar -->
                <div class="filters-sidebar">
                    <div class="filters-header">
                        <h3>Screening Filters</h3>
                        <div class="filter-actions">
                            <button class="btn btn-outline btn-sm" id="saveScreen">
                                <i class="fas fa-save"></i>
                                Save
                            </button>
                            <button class="btn btn-secondary btn-sm" id="resetFilters">
                                <i class="fas fa-undo"></i>
                                Reset
                            </button>
                        </div>
                    </div>

                    <div class="filters-content">
                        <!-- Market Cap Filter -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-building"></i> Market Cap</h4>
                            </div>
                            <div class="filter-options">
                                <label class="checkbox-label">
                                    <input type="checkbox" name="market_cap" value="mega" checked>
                                    <span class="checkmark"></span>
                                    Mega Cap ($200B+)
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="market_cap" value="large" checked>
                                    <span class="checkmark"></span>
                                    Large Cap ($10B-$200B)
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="market_cap" value="mid" checked>
                                    <span class="checkmark"></span>
                                    Mid Cap ($2B-$10B)
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="market_cap" value="small">
                                    <span class="checkmark"></span>
                                    Small Cap ($300M-$2B)
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="market_cap" value="micro">
                                    <span class="checkmark"></span>
                                    Micro Cap (Under $300M)
                                </label>
                            </div>
                        </div>

                        <!-- Price Range Filter -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-dollar-sign"></i> Price Range</h4>
                            </div>
                            <div class="range-inputs">
                                <div class="input-group">
                                    <label>Min Price</label>
                                    <input type="number" id="minPrice" placeholder="0" min="0" step="0.01" class="form-input">
                                </div>
                                <div class="input-group">
                                    <label>Max Price</label>
                                    <input type="number" id="maxPrice" placeholder="1000" min="0" step="0.01" class="form-input">
                                </div>
                            </div>
                        </div>

                        <!-- Volume Filter -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-chart-bar"></i> Volume</h4>
                            </div>
                            <div class="range-inputs">
                                <div class="input-group">
                                    <label>Min Volume</label>
                                    <select id="minVolume" class="form-select">
                                        <option value="">Any Volume</option>
                                        <option value="50000">50K+</option>
                                        <option value="100000">100K+</option>
                                        <option value="500000">500K+</option>
                                        <option value="1000000">1M+</option>
                                        <option value="5000000">5M+</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Technical Indicators -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-chart-line"></i> Technical</h4>
                            </div>
                            <div class="range-inputs">
                                <div class="input-group">
                                    <label>P/E Ratio</label>
                                    <div class="range-group">
                                        <input type="number" id="minPE" placeholder="Min" class="form-input">
                                        <span class="range-separator">to</span>
                                        <input type="number" id="maxPE" placeholder="Max" class="form-input">
                                    </div>
                                </div>
                                <div class="input-group">
                                    <label>P/B Ratio</label>
                                    <div class="range-group">
                                        <input type="number" id="minPB" placeholder="Min" step="0.1" class="form-input">
                                        <span class="range-separator">to</span>
                                        <input type="number" id="maxPB" placeholder="Max" step="0.1" class="form-input">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Performance Filter -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-percentage"></i> Performance</h4>
                            </div>
                            <div class="range-inputs">
                                <div class="input-group">
                                    <label>1-Day Change %</label>
                                    <div class="range-group">
                                        <input type="number" id="min1Day" placeholder="Min" step="0.1" class="form-input">
                                        <span class="range-separator">to</span>
                                        <input type="number" id="max1Day" placeholder="Max" step="0.1" class="form-input">
                                    </div>
                                </div>
                                <div class="input-group">
                                    <label>YTD Change %</label>
                                    <div class="range-group">
                                        <input type="number" id="minYTD" placeholder="Min" step="0.1" class="form-input">
                                        <span class="range-separator">to</span>
                                        <input type="number" id="maxYTD" placeholder="Max" step="0.1" class="form-input">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Sector Filter -->
                        <div class="filter-section">
                            <div class="filter-header">
                                <h4><i class="fas fa-industry"></i> Sector</h4>
                            </div>
                            <div class="filter-options">
                                <select id="sectorFilter" class="form-select">
                                    <option value="">All Sectors</option>
                                    <option value="technology">Technology</option>
                                    <option value="healthcare">Healthcare</option>
                                    <option value="financial">Financial</option>
                                    <option value="consumer">Consumer</option>
                                    <option value="energy">Energy</option>
                                    <option value="industrial">Industrial</option>
                                    <option value="materials">Materials</option>
                                    <option value="utilities">Utilities</option>
                                    <option value="real-estate">Real Estate</option>
                                    <option value="telecommunications">Telecommunications</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="filter-actions-bottom">
                        <button class="btn btn-primary btn-block" id="applyFilters">
                            <i class="fas fa-search"></i>
                            Apply Filters
                        </button>
                    </div>
                </div>

                <!-- Results Section -->
                <div class="results-section">
                    <div class="results-header">
                        <div class="results-info">
                            <h3>Screening Results</h3>
                            <span class="results-count" id="resultsCount">0 stocks found</span>
                        </div>
                        <div class="results-controls">
                            <div class="view-options">
                                <button class="view-btn active" data-view="table">
                                    <i class="fas fa-table"></i>
                                </button>
                                <button class="view-btn" data-view="grid">
                                    <i class="fas fa-th"></i>
                                </button>
                            </div>
                            <select id="sortBy" class="form-select">
                                <option value="symbol">Symbol</option>
                                <option value="price">Price</option>
                                <option value="change">% Change</option>
                                <option value="volume">Volume</option>
                                <option value="market_cap">Market Cap</option>
                            </select>
                            <button class="btn btn-outline" id="exportResults">
                                <i class="fas fa-download"></i>
                                Export
                            </button>
                        </div>
                    </div>

                    <div class="results-content">
                        <div class="loading-indicator" id="loadingIndicator">
                            <i class="fas fa-spinner fa-spin"></i>
                            Screening stocks...
                        </div>

                        <div class="results-table" id="resultsTable" style="display: none;">
                            <div class="table-header">
                                <div class="header-cell">Symbol</div>
                                <div class="header-cell">Company</div>
                                <div class="header-cell">Price</div>
                                <div class="header-cell">Change</div>
                                <div class="header-cell">% Change</div>
                                <div class="header-cell">Volume</div>
                                <div class="header-cell">Market Cap</div>
                                <div class="header-cell">P/E</div>
                                <div class="header-cell">Actions</div>
                            </div>
                            <div class="table-body" id="resultsBody">
                                <!-- Results will be populated here -->
                            </div>
                        </div>

                        <div class="no-results" id="noResults" style="display: none;">
                            <div class="no-results-icon">
                                <i class="fas fa-search"></i>
                            </div>
                            <h3>No stocks match your criteria</h3>
                            <p>Try adjusting your filters to see more results</p>
                            <button class="btn btn-primary" onclick="document.getElementById('resetFilters').click()">
                                Reset Filters
                            </button>
                        </div>
                    </div>

                    <div class="pagination" id="pagination" style="display: none;">
                        <button class="btn btn-outline" id="prevPage" disabled>
                            <i class="fas fa-chevron-left"></i>
                            Previous
                        </button>
                        <span class="page-info" id="pageInfo">Page 1 of 1</span>
                        <button class="btn btn-outline" id="nextPage" disabled>
                            Next
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.stock-screener-container {
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

.screener-content {
    padding: 2rem 0;
}

.screener-layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 2rem;
    align-items: start;
}

.filters-sidebar {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: sticky;
    top: 2rem;
    max-height: calc(100vh - 4rem);
    overflow-y: auto;
}

.filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e1e5e9;
}

.filters-header h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.filter-actions {
    display: flex;
    gap: 0.5rem;
}

.filter-section {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.filter-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.filter-header {
    margin-bottom: 1rem;
}

.filter-header h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.filter-header i {
    color: #3685fb;
}

.filter-options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #666;
    padding: 0.25rem 0;
}

.checkbox-label input[type="checkbox"] {
    display: none;
}

.checkmark {
    width: 18px;
    height: 18px;
    border: 2px solid #e1e5e9;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
    background: #3685fb;
    border-color: #3685fb;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.range-inputs {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.input-group label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #555;
}

.range-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.range-separator {
    color: #888;
    font-size: 0.9rem;
}

.form-input,
.form-select {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.filter-actions-bottom {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e1e5e9;
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

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover {
    background: #4b5563;
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

.btn-block {
    width: 100%;
    justify-content: center;
}

.results-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e1e5e9;
}

.results-info h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.25rem 0;
}

.results-count {
    font-size: 0.9rem;
    color: #666;
}

.results-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.view-options {
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

.results-content {
    min-height: 400px;
    position: relative;
}

.loading-indicator {
    text-align: center;
    padding: 4rem;
    color: #666;
    font-size: 1.1rem;
}

.results-table {
    width: 100%;
}

.table-header {
    background: #f8f9fa;
    display: grid;
    grid-template-columns: 80px 1fr 100px 100px 100px 120px 120px 80px 120px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #e1e5e9;
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
}

.table-body {
    max-height: 600px;
    overflow-y: auto;
}

.result-row {
    display: grid;
    grid-template-columns: 80px 1fr 100px 100px 100px 120px 120px 80px 120px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
    transition: background 0.2s;
    font-size: 0.9rem;
}

.result-row:hover {
    background: #f8f9fa;
}

.symbol-cell {
    font-weight: 700;
    color: #3685fb;
    cursor: pointer;
}

.symbol-cell:hover {
    text-decoration: underline;
}

.company-cell {
    color: #333;
    font-weight: 500;
}

.price-cell {
    font-weight: 600;
    color: #1a1a1a;
}

.change-cell {
    font-weight: 600;
}

.change-cell.positive { color: #10b981; }
.change-cell.negative { color: #ef4444; }

.actions-cell {
    display: flex;
    gap: 0.5rem;
}

.action-btn {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.2s;
}

.action-btn:hover {
    background: #f0f0f0;
    color: #3685fb;
}

.no-results {
    text-align: center;
    padding: 4rem;
    color: #666;
}

.no-results-icon {
    font-size: 4rem;
    color: #ddd;
    margin-bottom: 1rem;
}

.no-results h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.no-results p {
    margin: 0 0 2rem 0;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e1e5e9;
}

.page-info {
    font-size: 0.9rem;
    color: #666;
}

@media (max-width: 1024px) {
    .screener-layout {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .filters-sidebar {
        position: static;
        max-height: none;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .results-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .results-controls {
        justify-content: space-between;
    }
    
    .table-header,
    .result-row {
        grid-template-columns: repeat(4, 1fr);
        font-size: 0.8rem;
    }
    
    .header-cell:nth-child(n+5),
    .result-row > *:nth-child(n+5) {
        display: none;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeScreener();
    loadInitialResults();
});

let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

function initializeScreener() {
    // Filter controls
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
    document.getElementById('saveScreen').addEventListener('click', saveScreen);
    
    // View controls
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            toggleView(this.dataset.view);
        });
    });
    
    // Sort control
    document.getElementById('sortBy').addEventListener('change', handleSort);
    
    // Export control
    document.getElementById('exportResults').addEventListener('click', exportResults);
    
    // Pagination
    document.getElementById('prevPage').addEventListener('click', () => changePage(currentPage - 1));
    document.getElementById('nextPage').addEventListener('click', () => changePage(currentPage + 1));
}

function applyFilters() {
    showLoading();
    
    // Collect filter values
    currentFilters = {
        market_cap: Array.from(document.querySelectorAll('input[name="market_cap"]:checked')).map(cb => cb.value),
        min_price: document.getElementById('minPrice').value,
        max_price: document.getElementById('maxPrice').value,
        min_volume: document.getElementById('minVolume').value,
        min_pe: document.getElementById('minPE').value,
        max_pe: document.getElementById('maxPE').value,
        min_pb: document.getElementById('minPB').value,
        max_pb: document.getElementById('maxPB').value,
        min_1day: document.getElementById('min1Day').value,
        max_1day: document.getElementById('max1Day').value,
        min_ytd: document.getElementById('minYTD').value,
        max_ytd: document.getElementById('maxYTD').value,
        sector: document.getElementById('sectorFilter').value
    };
    
    // Simulate API call
    setTimeout(() => {
        const results = generateMockResults();
        displayResults(results);
        hideLoading();
    }, 1500);
}

function resetFilters() {
    // Reset all form inputs
    document.querySelectorAll('.filters-sidebar input').forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = input.name === 'market_cap' && ['mega', 'large', 'mid'].includes(input.value);
        } else {
            input.value = '';
        }
    });
    
    document.querySelectorAll('.filters-sidebar select').forEach(select => {
        select.value = '';
    });
    
    // Apply filters automatically
    applyFilters();
}

function saveScreen() {
    showNotification('Screening criteria saved successfully!', 'success');
}

function loadInitialResults() {
    showLoading();
    
    // Load default results
    setTimeout(() => {
        const results = generateMockResults();
        displayResults(results);
        hideLoading();
    }, 1000);
}

function generateMockResults() {
    const mockStocks = [
        { symbol: 'AAPL', company: 'Apple Inc.', price: 175.43, change: 2.15, changePercent: 1.24, volume: 58742000, marketCap: '2.8T', pe: 28.5 },
        { symbol: 'MSFT', company: 'Microsoft Corp.', price: 334.89, change: -1.23, changePercent: -0.37, volume: 32156000, marketCap: '2.5T', pe: 32.1 },
        { symbol: 'GOOGL', company: 'Alphabet Inc.', price: 2734.52, change: 15.67, changePercent: 0.58, volume: 1234000, marketCap: '1.7T', pe: 24.8 },
        { symbol: 'AMZN', company: 'Amazon.com Inc.', price: 3234.12, change: -8.45, changePercent: -0.26, volume: 2845000, marketCap: '1.6T', pe: 42.3 },
        { symbol: 'TSLA', company: 'Tesla Inc.', price: 234.56, change: 12.34, changePercent: 5.56, volume: 87654000, marketCap: '745B', pe: 65.2 }
    ];
    
    return mockStocks;
}

function displayResults(results) {
    const resultsBody = document.getElementById('resultsBody');
    const resultsCount = document.getElementById('resultsCount');
    const resultsTable = document.getElementById('resultsTable');
    const noResults = document.getElementById('noResults');
    
    resultsCount.textContent = `${results.length} stocks found`;
    
    if (results.length === 0) {
        resultsTable.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    resultsTable.style.display = 'block';
    noResults.style.display = 'none';
    
    resultsBody.innerHTML = results.map(stock => {
        const changeClass = stock.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = stock.change >= 0 ? '+' : '';
        
        return `
            <div class="result-row">
                <div class="symbol-cell" onclick="viewStock('${stock.symbol}')">${stock.symbol}</div>
                <div class="company-cell">${stock.company}</div>
                <div class="price-cell">$${stock.price.toFixed(2)}</div>
                <div class="change-cell ${changeClass}">${changeSymbol}${stock.change.toFixed(2)}</div>
                <div class="change-cell ${changeClass}">${changeSymbol}${stock.changePercent.toFixed(2)}%</div>
                <div class="volume-cell">${formatVolume(stock.volume)}</div>
                <div class="market-cap-cell">${stock.marketCap}</div>
                <div class="pe-cell">${stock.pe}</div>
                <div class="actions-cell">
                    <button class="action-btn" onclick="addToWatchlist('${stock.symbol}')" title="Add to Watchlist">
                        <i class="fas fa-star"></i>
                    </button>
                    <button class="action-btn" onclick="viewDetails('${stock.symbol}')" title="View Details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
}

function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsTable').style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function toggleView(view) {
    // Implementation for grid vs table view
    console.log('Switching to', view, 'view');
}

function handleSort() {
    const sortBy = document.getElementById('sortBy').value;
    console.log('Sorting by:', sortBy);
    showNotification('Results sorted by ' + sortBy, 'info');
}

function exportResults() {
    showNotification('Export functionality coming soon!', 'info');
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    applyFilters();
}

function viewStock(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
}

function addToWatchlist(symbol) {
    showNotification(`${symbol} added to watchlist!`, 'success');
}

function viewDetails(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3685fb',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
        zIndex: '1001',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        minWidth: '300px'
    });
    
    const closeBtn = notification.querySelector('button');
    Object.assign(closeBtn.style, {
        background: 'none',
        border: 'none',
        color: 'white',
        fontSize: '1.25rem',
        cursor: 'pointer',
        padding: '0'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}
</script>

<?php get_footer(); ?>