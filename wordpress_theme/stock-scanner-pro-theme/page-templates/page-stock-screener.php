<?php
/**
 * Template Name: Stock Screener Page
 * Individual page for stock screening and filtering functionality
 */

get_header(); ?>

<div class="stock-screener-page">
    <div class="container">
        <div class="page-header">
            <h1>🔍 Stock Screener</h1>
            <p class="page-description">Find stocks that match your investment criteria with our advanced screening tools</p>
        </div>

        <div class="screener-container">
            <!-- Screening Filters Panel -->
            <div class="filters-panel">
                <div class="panel-header">
                    <h2>📊 Screening Filters</h2>
                    <div class="panel-actions">
                        <button id="save-screen" class="btn btn-outline">💾 Save Screen</button>
                        <button id="reset-filters" class="btn btn-secondary">🔄 Reset</button>
                    </div>
                </div>

                <!-- Market Cap Filters -->
                <div class="filter-section">
                    <h3>💰 Market Capitalization</h3>
                    <div class="filter-group">
                        <div class="checkbox-group">
                            <label><input type="checkbox" value="mega" checked> Mega Cap ($200B+)</label>
                            <label><input type="checkbox" value="large" checked> Large Cap ($10B-$200B)</label>
                            <label><input type="checkbox" value="mid" checked> Mid Cap ($2B-$10B)</label>
                            <label><input type="checkbox" value="small" checked> Small Cap ($300M-$2B)</label>
                            <label><input type="checkbox" value="micro"> Micro Cap (Under $300M)</label>
                        </div>
                    </div>
                </div>

                <!-- Price Filters -->
                <div class="filter-section">
                    <h3>💵 Price Range</h3>
                    <div class="range-inputs">
                        <div class="input-group">
                            <label>Min Price:</label>
                            <input type="number" id="min-price" placeholder="0" min="0" step="0.01">
                        </div>
                        <div class="input-group">
                            <label>Max Price:</label>
                            <input type="number" id="max-price" placeholder="1000" min="0" step="0.01">
                        </div>
                    </div>
                </div>

                <!-- Volume Filters -->
                <div class="filter-section">
                    <h3>📈 Volume</h3>
                    <div class="range-inputs">
                        <div class="input-group">
                            <label>Min Volume:</label>
                            <input type="number" id="min-volume" placeholder="100000" min="0">
                        </div>
                        <div class="input-group">
                            <label>Avg Volume (30d):</label>
                            <select id="volume-filter">
                                <option value="">Any</option>
                                <option value="100k">Over 100K</option>
                                <option value="500k">Over 500K</option>
                                <option value="1m">Over 1M</option>
                                <option value="5m">Over 5M</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Performance Filters -->
                <div class="filter-section">
                    <h3>📊 Performance</h3>
                    <div class="performance-filters">
                        <div class="input-group">
                            <label>1-Day Change (%):</label>
                            <select id="day-change">
                                <option value="">Any</option>
                                <option value="up5">Up 5%+</option>
                                <option value="up2">Up 2%+</option>
                                <option value="down2">Down 2%+</option>
                                <option value="down5">Down 5%+</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label>52-Week Performance:</label>
                            <select id="year-performance">
                                <option value="">Any</option>
                                <option value="high">Near 52W High</option>
                                <option value="low">Near 52W Low</option>
                                <option value="up20">Up 20%+ YTD</option>
                                <option value="down20">Down 20%+ YTD</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Sector Filters -->
                <div class="filter-section">
                    <h3>🏢 Sectors & Industries</h3>
                    <div class="sector-filters">
                        <select id="sector-filter" multiple>
                            <option value="technology">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="financial">Financial</option>
                            <option value="consumer">Consumer</option>
                            <option value="industrial">Industrial</option>
                            <option value="energy">Energy</option>
                            <option value="materials">Materials</option>
                            <option value="utilities">Utilities</option>
                            <option value="realestate">Real Estate</option>
                            <option value="communication">Communication</option>
                        </select>
                    </div>
                </div>

                <!-- Technical Indicators -->
                <div class="filter-section">
                    <h3>📉 Technical Indicators</h3>
                    <div class="technical-filters">
                        <div class="checkbox-group">
                            <label><input type="checkbox" value="above_sma20"> Above 20-day SMA</label>
                            <label><input type="checkbox" value="above_sma50"> Above 50-day SMA</label>
                            <label><input type="checkbox" value="above_sma200"> Above 200-day SMA</label>
                            <label><input type="checkbox" value="golden_cross"> Golden Cross Pattern</label>
                            <label><input type="checkbox" value="oversold_rsi"> Oversold RSI (&lt;30)</label>
                            <label><input type="checkbox" value="overbought_rsi"> Overbought RSI (&gt;70)</label>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="filter-actions">
                    <button id="apply-screen" class="btn btn-primary btn-large">🔍 Screen Stocks</button>
                    <button id="export-results" class="btn btn-outline">📤 Export Results</button>
                </div>
            </div>

            <!-- Results Panel -->
            <?php echo do_shortcode('[stock_screener_tool]'); ?>
            <div class="results-panel">
                <div class="results-header">
                    <h2>📋 Screening Results</h2>
                    <div class="results-info">
                        <span id="results-count">0 stocks found</span>
                        <div class="sort-controls">
                            <label>Sort by:</label>
                            <select id="sort-by">
                                <option value="symbol">Symbol</option>
                                <option value="price">Price</option>
                                <option value="change">% Change</option>
                                <option value="volume">Volume</option>
                                <option value="market_cap">Market Cap</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Loading Indicator -->
                <div class="loading-indicator" id="screening-loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Screening stocks...</p>
                </div>

                <!-- Results Table -->
                <div class="results-table-container">
                    <table id="results-table" class="screening-results">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Company</th>
                                <th>Price</th>
                                <th>Change</th>
                                <th>% Change</th>
                                <th>Volume</th>
                                <th>Market Cap</th>
                                <th>Sector</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="results-tbody">
                            <!-- Results will be populated here -->
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div class="pagination-controls">
                    <button id="prev-page" class="btn btn-secondary">← Previous</button>
                    <span id="page-info">Page 1 of 1</span>
                    <button id="next-page" class="btn btn-secondary">Next →</button>
                </div>
            </div>
        </div>

        <!-- Saved Screens Section -->
        <div class="saved-screens-section">
            <h3>💾 Saved Screens</h3>
            <div id="saved-screens" class="saved-screens-grid">
                <!-- Saved screens will be loaded here -->
            </div>
        </div>
    </div>
</div>

<style>
.stock-screener-page {
    padding: 40px 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-header h1 {
    color: #2271b1;
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.page-description {
    color: #646970;
    font-size: 1.1rem;
    max-width: 700px;
    margin: 0 auto;
}

.screener-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 30px;
}

.filters-panel {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    height: fit-content;
    position: sticky;
    top: 20px;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;
}

.panel-header h2 {
    margin: 0;
    color: #1d2327;
    font-size: 1.3rem;
}

.panel-actions {
    display: flex;
    gap: 10px;
}

.filter-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f0f0f0;
}

.filter-section:last-child {
    border-bottom: none;
}

.filter-section h3 {
    color: #1d2327;
    font-size: 1.1rem;
    margin: 0 0 15px 0;
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.checkbox-group label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #646970;
    cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
    margin: 0;
}

.range-inputs {
    display: grid;
    gap: 15px;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.input-group label {
    font-weight: 600;
    color: #1d2327;
    font-size: 0.9rem;
}

.input-group input,
.input-group select {
    padding: 8px 10px;
    border: 2px solid #e1e1e1;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: border-color 0.3s ease;
}

.input-group input:focus,
.input-group select:focus {
    outline: none;
    border-color: #2271b1;
}

.sector-filters select {
    width: 100%;
    height: 120px;
    padding: 8px;
    border: 2px solid #e1e1e1;
    border-radius: 4px;
}

.filter-actions {
    margin-top: 25px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.btn-large {
    padding: 15px 25px;
    font-size: 1rem;
}

.results-panel {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;
}

.results-header h2 {
    margin: 0;
    color: #1d2327;
    font-size: 1.3rem;
}

.results-info {
    display: flex;
    align-items: center;
    gap: 20px;
}

#results-count {
    color: #646970;
    font-weight: 500;
}

.sort-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.sort-controls label {
    font-weight: 500;
    color: #646970;
}

.sort-controls select {
    padding: 6px 10px;
    border: 1px solid #e1e1e1;
    border-radius: 4px;
}

.results-table-container {
    overflow-x: auto;
    margin-bottom: 20px;
}

.screening-results {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.screening-results th,
.screening-results td {
    padding: 12px 8px;
    text-align: left;
    border-bottom: 1px solid #e1e1e1;
}

.screening-results th {
    background: #f8f9fa;
    font-weight: 600;
    color: #1d2327;
    position: sticky;
    top: 0;
}

.screening-results tbody tr:hover {
    background: #f8f9fa;
}

.symbol-cell {
    font-weight: 600;
    color: #2271b1;
    cursor: pointer;
}

.symbol-cell:hover {
    text-decoration: underline;
}

.change-positive {
    color: #00a32a;
    font-weight: 600;
}

.change-negative {
    color: #d63638;
    font-weight: 600;
}

.action-buttons {
    display: flex;
    gap: 5px;
}

.btn-small {
    padding: 4px 8px;
    font-size: 0.8rem;
    border-radius: 3px;
}

.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 20px;
}

.saved-screens-section {
    max-width: 1400px;
    margin: 40px auto 0;
}

.saved-screens-section h3 {
    color: #1d2327;
    font-size: 1.3rem;
    margin-bottom: 20px;
}

.saved-screens-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.saved-screen-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    cursor: pointer;
    transition: all 0.3s ease;
}

.saved-screen-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    font-size: 0.9rem;
}

.btn-primary {
    background: #2271b1;
    color: white;
}

.btn-primary:hover {
    background: #135e96;
    transform: translateY(-1px);
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

.loading-indicator {
    text-align: center;
    padding: 60px 20px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #2271b1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
    .screener-container {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .filters-panel {
        position: static;
    }
    
    .results-info {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }
}

@media (max-width: 768px) {
    .panel-header {
        flex-direction: column;
        gap: 15px;
    }
    
    .panel-actions {
        width: 100%;
    }
    
    .results-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }
    
    .pagination-controls {
        flex-direction: column;
        gap: 10px;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const applyScreenBtn = document.getElementById('apply-screen');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const exportResultsBtn = document.getElementById('export-results');
    const saveScreenBtn = document.getElementById('save-screen');
    const sortBySelect = document.getElementById('sort-by');
    const resultsCount = document.getElementById('results-count');
    const resultsTbody = document.getElementById('results-tbody');
    const screeningLoading = document.getElementById('screening-loading');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');

    let currentPage = 1;
    let totalPages = 1;
    let currentResults = [];
    let isScreening = false;

    // Event Listeners
    applyScreenBtn.addEventListener('click', performScreening);
    resetFiltersBtn.addEventListener('click', resetAllFilters);
    exportResultsBtn.addEventListener('click', exportResults);
    saveScreenBtn.addEventListener('click', saveCurrentScreen);
    sortBySelect.addEventListener('change', sortResults);
    prevPageBtn.addEventListener('click', () => changePage(currentPage - 1));
    nextPageBtn.addEventListener('click', () => changePage(currentPage + 1));

    // Load initial data
    loadSavedScreens();

    function performScreening() {
        if (isScreening) return;
        
        isScreening = true;
        screeningLoading.style.display = 'block';
        resultsTbody.innerHTML = '';
        applyScreenBtn.disabled = true;
        applyScreenBtn.textContent = '🔍 Screening...';

        // Collect filter criteria
        const filters = collectFilters();
        
        // Simulate API call
        setTimeout(() => {
            const mockResults = generateMockResults(filters);
            displayResults(mockResults);
            screeningLoading.style.display = 'none';
            isScreening = false;
            applyScreenBtn.disabled = false;
            applyScreenBtn.textContent = '🔍 Screen Stocks';
        }, 2000);
    }

    function collectFilters() {
        // Collect all filter values
        const marketCaps = Array.from(document.querySelectorAll('input[value]:checked'))
            .map(cb => cb.value);
        
        return {
            marketCaps: marketCaps,
            minPrice: document.getElementById('min-price').value,
            maxPrice: document.getElementById('max-price').value,
            minVolume: document.getElementById('min-volume').value,
            volumeFilter: document.getElementById('volume-filter').value,
            dayChange: document.getElementById('day-change').value,
            yearPerformance: document.getElementById('year-performance').value,
            sectors: Array.from(document.getElementById('sector-filter').selectedOptions)
                .map(option => option.value),
            technicals: Array.from(document.querySelectorAll('.technical-filters input:checked'))
                .map(cb => cb.value)
        };
    }

    function generateMockResults(filters) {
        const stocks = [
            { symbol: 'AAPL', company: 'Apple Inc.', price: 175.43, change: 2.15, changePercent: 1.24, volume: '52.3M', marketCap: '2.8T', sector: 'Technology' },
            { symbol: 'GOOGL', company: 'Alphabet Inc.', price: 138.21, change: -1.45, changePercent: -1.04, volume: '25.7M', marketCap: '1.7T', sector: 'Technology' },
            { symbol: 'TSLA', company: 'Tesla Inc.', price: 248.50, change: 8.32, changePercent: 3.46, volume: '95.2M', marketCap: '789B', sector: 'Consumer' },
            { symbol: 'MSFT', company: 'Microsoft Corp.', price: 378.85, change: 4.67, changePercent: 1.25, volume: '28.4M', marketCap: '2.8T', sector: 'Technology' },
            { symbol: 'AMZN', company: 'Amazon.com Inc.', price: 146.80, change: -2.30, changePercent: -1.54, volume: '41.6M', marketCap: '1.5T', sector: 'Consumer' },
            { symbol: 'NVDA', company: 'NVIDIA Corp.', price: 875.28, change: 15.42, changePercent: 1.79, volume: '38.9M', marketCap: '2.2T', sector: 'Technology' },
            { symbol: 'META', company: 'Meta Platforms', price: 484.20, change: -6.75, changePercent: -1.37, volume: '18.3M', marketCap: '1.2T', sector: 'Technology' },
            { symbol: 'JPM', company: 'JPMorgan Chase', price: 165.42, change: 1.28, changePercent: 0.78, volume: '12.8M', marketCap: '485B', sector: 'Financial' },
            { symbol: 'JNJ', company: 'Johnson & Johnson', price: 158.90, change: 0.85, changePercent: 0.54, volume: '8.2M', marketCap: '418B', sector: 'Healthcare' },
            { symbol: 'V', company: 'Visa Inc.', price: 267.35, change: 3.20, changePercent: 1.21, volume: '6.4M', marketCap: '565B', sector: 'Financial' }
        ];

        // Apply basic filtering (simplified)
        let filteredStocks = stocks.filter(stock => {
            if (filters.minPrice && stock.price < parseFloat(filters.minPrice)) return false;
            if (filters.maxPrice && stock.price > parseFloat(filters.maxPrice)) return false;
            if (filters.sectors.length > 0 && !filters.sectors.includes(stock.sector.toLowerCase())) return false;
            return true;
        });

        return filteredStocks;
    }

    function displayResults(results) {
        currentResults = results;
        resultsCount.textContent = `${results.length} stocks found`;
        
        resultsTbody.innerHTML = '';
        
        results.forEach(stock => {
            const row = createResultRow(stock);
            resultsTbody.appendChild(row);
        });

        updatePagination();
    }

    function createResultRow(stock) {
        const row = document.createElement('tr');
        const changeClass = stock.change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = stock.change >= 0 ? '↗' : '↘';
        
        row.innerHTML = `
            <td><span class="symbol-cell" onclick="viewStock('${stock.symbol}')">${stock.symbol}</span></td>
            <td>${stock.company}</td>
            <td>$${stock.price.toFixed(2)}</td>
            <td class="${changeClass}">${changeIcon} $${Math.abs(stock.change).toFixed(2)}</td>
            <td class="${changeClass}">${stock.changePercent.toFixed(2)}%</td>
            <td>${stock.volume}</td>
            <td>${stock.marketCap}</td>
            <td>${stock.sector}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-small" onclick="addToWatchlist('${stock.symbol}')">⭐</button>
                    <button class="btn btn-outline btn-small" onclick="viewChart('${stock.symbol}')">📊</button>
                </div>
            </td>
        `;
        
        return row;
    }

    function resetAllFilters() {
        // Reset all form inputs
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = cb.value === 'mega' || cb.value === 'large' || cb.value === 'mid' || cb.value === 'small';
        });
        document.querySelectorAll('input[type="number"]').forEach(input => input.value = '');
        document.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
        
        // Clear results
        resultsTbody.innerHTML = '';
        resultsCount.textContent = '0 stocks found';
    }

    function sortResults() {
        const sortBy = sortBySelect.value;
        
        currentResults.sort((a, b) => {
            switch(sortBy) {
                case 'symbol':
                    return a.symbol.localeCompare(b.symbol);
                case 'price':
                    return b.price - a.price;
                case 'change':
                    return b.changePercent - a.changePercent;
                case 'volume':
                    return parseFloat(b.volume.replace('M', '')) - parseFloat(a.volume.replace('M', ''));
                default:
                    return 0;
            }
        });
        
        displayResults(currentResults);
    }

    function exportResults() {
        if (currentResults.length === 0) {
            alert('No results to export');
            return;
        }
        
        // In a real implementation, this would generate and download a CSV file
        alert(`Exporting ${currentResults.length} stocks to CSV file...`);
    }

    function saveCurrentScreen() {
        const screenName = prompt('Enter a name for this screen:');
        if (!screenName) return;
        
        const filters = collectFilters();
        const savedScreens = JSON.parse(localStorage.getItem('savedScreens') || '[]');
        
        savedScreens.push({
            name: screenName,
            filters: filters,
            created: new Date().toISOString(),
            resultCount: currentResults.length
        });
        
        localStorage.setItem('savedScreens', JSON.stringify(savedScreens));
        loadSavedScreens();
        alert(`Screen "${screenName}" saved successfully!`);
    }

    function loadSavedScreens() {
        const savedScreens = JSON.parse(localStorage.getItem('savedScreens') || '[]');
        const container = document.getElementById('saved-screens');
        
        if (savedScreens.length === 0) {
            container.innerHTML = '<p>No saved screens yet. Create and save your first screen!</p>';
            return;
        }
        
        container.innerHTML = savedScreens.map(screen => `
            <div class="saved-screen-card" onclick="loadSavedScreen('${screen.name}')">
                <h4>${screen.name}</h4>
                <p>Created: ${new Date(screen.created).toLocaleDateString()}</p>
                <p>Results: ${screen.resultCount} stocks</p>
                <div class="card-actions">
                    <button class="btn btn-primary btn-small">Load Screen</button>
                    <button class="btn btn-outline btn-small" onclick="deleteSavedScreen('${screen.name}', event)">Delete</button>
                </div>
            </div>
        `).join('');
    }

    function changePage(page) {
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        updatePagination();
    }

    function updatePagination() {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages;
    }

    // Global functions for onclick handlers
    window.viewStock = function(symbol) {
        window.location.href = `/stock-lookup/?symbol=${symbol}`;
    };

    window.addToWatchlist = function(symbol) {
        <?php if (is_user_logged_in()): ?>
        alert(`${symbol} added to your watchlist!`);
        <?php else: ?>
        alert('Please log in to add stocks to your watchlist');
        <?php endif; ?>
    };

    window.viewChart = function(symbol) {
        window.location.href = `/technical-analysis/?symbol=${symbol}`;
    };

    window.loadSavedScreen = function(screenName) {
        const savedScreens = JSON.parse(localStorage.getItem('savedScreens') || '[]');
        const screen = savedScreens.find(s => s.name === screenName);
        if (!screen) return;
        
        // Apply saved filters
        // This would restore all filter values from screen.filters
        alert(`Loading saved screen: ${screenName}`);
    };

    window.deleteSavedScreen = function(screenName, event) {
        event.stopPropagation();
        if (!confirm(`Delete saved screen "${screenName}"?`)) return;
        
        let savedScreens = JSON.parse(localStorage.getItem('savedScreens') || '[]');
        savedScreens = savedScreens.filter(s => s.name !== screenName);
        localStorage.setItem('savedScreens', JSON.stringify(savedScreens));
        loadSavedScreens();
    };
});
</script>

<?php get_footer(); ?>