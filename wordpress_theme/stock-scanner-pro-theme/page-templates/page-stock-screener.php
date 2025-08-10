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
                <div class="filter-section" id="market-cap-filters">
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
                    <div class="range-inputs" style="display: grid; gap: var(--space-3);">
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
                    <div class="range-inputs" style="display: grid; gap: var(--space-3);">
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
                    <div class="performance-filters" style="display: grid; gap: var(--space-3);">
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
                        <select id="sector-filter" multiple style="height: 120px;">
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
                <div class="filter-actions" style="display: grid; gap: var(--space-3); margin-top: var(--space-5);">
                    <button id="apply-screen" class="btn btn-primary">🔍 Screen Stocks</button>
                    <button id="export-results" class="btn btn-outline">📤 Export Results</button>
                </div>
            </div>

            <!-- Results Panel -->
            <div class="results-panel">
                <div class="results-header">
                    <h2>📋 Screening Results</h2>
                    <div class="results-info" style="display: flex; justify-content: space-between; align-items: center; gap: var(--space-4);">
                        <span id="results-count">0 stocks found</span>
                        <div class="sort-controls" style="display: flex; align-items: center; gap: var(--space-2);">
                            <label style="margin: 0;">Sort by:</label>
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
                <div class="results-table-container" style="overflow-x: auto;">
                    <table id="results-table" class="screening-results table">
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
                <div class="pagination-controls" style="display: flex; justify-content: center; align-items: center; margin-top: var(--space-5);">
                    <button id="prev-page" class="btn btn-secondary">← Previous</button>
                    <span id="page-info" style="margin: 0 var(--space-4);">Page 1 of 1</span>
                    <button id="next-page" class="btn btn-secondary">Next →</button>
                </div>
            </div>
        </div>

        <!-- Saved Screens Section -->
        <div class="card p-6 mt-6">
            <h3>💾 Saved Screens</h3>
            <div id="saved-screens" class="saved-screens-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-4); margin-top: var(--space-4);">
                <!-- Saved screens will be loaded here -->
            </div>
        </div>
    </div>
</div>

<style>
/* Additional styles for screener page specific to unified theme */
.checkbox-group {
    display: grid;
    gap: var(--space-2);
}

.checkbox-group label {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: 400;
    cursor: pointer;
    padding: var(--space-2);
    border-radius: var(--radius-sm);
    transition: background-color 0.2s ease;
}

.checkbox-group label:hover {
    background: #f8fafc;
}

.checkbox-group input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.input-group label {
    display: block;
    margin-bottom: var(--space-2);
    color: var(--color-text);
    font-weight: 600;
}

.symbol-cell {
    color: var(--color-primary);
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
}

.symbol-cell:hover {
    text-decoration: underline;
}

.action-buttons {
    display: flex;
    gap: var(--space-2);
}

.btn-small {
    padding: var(--space-1) var(--space-2);
    font-size: 0.875rem;
    min-width: auto;
}

.saved-screen-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    cursor: pointer;
}

.saved-screen-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.saved-screen-card h4 {
    color: var(--color-text);
    margin: 0 0 var(--space-2) 0;
    font-size: 1.125rem;
}

.saved-screen-card p {
    color: var(--color-text-muted);
    margin: 0 0 var(--space-1) 0;
    font-size: 0.875rem;
}

.card-actions {
    display: flex;
    gap: var(--space-2);
    margin-top: var(--space-3);
}

@media (max-width: 768px) {
    .results-info {
        flex-direction: column;
        align-items: stretch !important;
        gap: var(--space-3) !important;
    }
    
    .sort-controls {
        justify-content: space-between !important;
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
        
        // Build API URL with filters
        const backendUrl = '<?php echo get_backend_api_url('stocks/'); ?>';
        const params = new URLSearchParams();
        
        // Add filters to API request
        if (filters.minPrice) params.append('min_price', filters.minPrice);
        if (filters.maxPrice) params.append('max_price', filters.maxPrice);
        if (filters.minVolume) params.append('min_volume', filters.minVolume);
        if (filters.sectors && filters.sectors.length > 0) {
            // Note: Django API may not have sector filtering, we'll add it to results filter
        }
        
        params.append('limit', '100');
        params.append('sort_by', 'market_cap');
        params.append('sort_order', 'desc');
        
        // Make API call to Django backend
        fetch(`${backendUrl}?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            screeningLoading.style.display = 'none';
            isScreening = false;
            applyScreenBtn.disabled = false;
            applyScreenBtn.textContent = '🔍 Screen Stocks';
            
            if (data.results && data.results.length > 0) {
                // Apply client-side sector filtering if needed
                let results = data.results;
                if (filters.sectors && filters.sectors.length > 0) {
                    results = results.filter(stock => 
                        filters.sectors.some(sector => 
                            (stock.sector || '').toLowerCase().includes(sector.toLowerCase())
                        )
                    );
                }
                
                // Apply performance filters
                if (filters.dayChange) {
                    const threshold = parseFloat(filters.dayChange);
                    results = results.filter(stock => {
                        const change = parseFloat(stock.change_percent || 0);
                        return Math.abs(change) >= threshold;
                    });
                }
                
                displayResults(results);
            } else {
                resultsTbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #666;">No stocks found matching your criteria</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            screeningLoading.style.display = 'none';
            isScreening = false;
            applyScreenBtn.disabled = false;
            applyScreenBtn.textContent = '🔍 Screen Stocks';
            
            // Show fallback sample data when backend is unavailable
            const fallbackResults = [
                { ticker: 'AAPL', name: 'Apple Inc.', current_price: 175.43, price_change_today: 2.15, change_percent: 1.24, volume: 52300000, market_cap: 2800000000000, sector: 'Technology' },
                { ticker: 'GOOGL', name: 'Alphabet Inc.', current_price: 138.21, price_change_today: -1.45, change_percent: -1.04, volume: 25700000, market_cap: 1700000000000, sector: 'Technology' },
                { ticker: 'TSLA', name: 'Tesla Inc.', current_price: 248.50, price_change_today: 8.32, change_percent: 3.46, volume: 95200000, market_cap: 789000000000, sector: 'Consumer' },
                { ticker: 'MSFT', name: 'Microsoft Corp.', current_price: 378.85, price_change_today: 4.67, change_percent: 1.25, volume: 28400000, market_cap: 2800000000000, sector: 'Technology' },
                { ticker: 'NVDA', name: 'NVIDIA Corp.', current_price: 875.28, price_change_today: 15.42, change_percent: 1.79, volume: 38900000, market_cap: 2200000000000, sector: 'Technology' }
            ];
            
            // Apply basic client-side filtering to fallback data
            let filteredResults = fallbackResults;
            if (filters.minPrice) {
                filteredResults = filteredResults.filter(stock => stock.current_price >= parseFloat(filters.minPrice));
            }
            if (filters.maxPrice) {
                filteredResults = filteredResults.filter(stock => stock.current_price <= parseFloat(filters.maxPrice));
            }
            
            if (filteredResults.length > 0) {
                displayResults(filteredResults);
                // Add notice about sample data
                const notice = document.createElement('div');
                notice.style.cssText = 'background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center;';
                notice.textContent = 'Backend unavailable - showing sample data. Please try again later for real-time data.';
                resultsTbody.parentNode.insertBefore(notice, resultsTbody.parentNode.firstChild);
            } else {
                resultsTbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #666;">No sample data available matching your criteria</td></tr>';
            }
        });
    }

    function collectFilters() {
        // Collect all filter values
        const marketCaps = Array.from(document.querySelectorAll('#market-cap-filters input[type="checkbox"]:checked'))
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
            { symbol: 'V', company: 'Visa Inc.', price: 267.35, change: 3.20, changePercent: 1.21, volume: '6.4M', marketCap: '565B', sector: 'Financial' },
            { symbol: 'PG', company: 'Procter & Gamble', price: 152.80, change: 0.45, changePercent: 0.30, volume: '5.8M', marketCap: '365B', sector: 'Consumer' },
            { symbol: 'HD', company: 'Home Depot', price: 325.67, change: -2.15, changePercent: -0.66, volume: '4.2M', marketCap: '340B', sector: 'Consumer' },
            { symbol: 'BAC', company: 'Bank of America', price: 34.52, change: 0.78, changePercent: 2.31, volume: '45.1M', marketCap: '285B', sector: 'Financial' },
            { symbol: 'XOM', company: 'Exxon Mobil', price: 98.45, change: 2.85, changePercent: 2.98, volume: '18.7M', marketCap: '415B', sector: 'Energy' },
            { symbol: 'CVX', company: 'Chevron Corp.', price: 142.78, change: 1.92, changePercent: 1.36, volume: '12.4M', marketCap: '275B', sector: 'Energy' }
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
        
        // Handle Django API data format
        const symbol = stock.ticker || stock.symbol;
        const company = stock.name || stock.company_name || stock.company || symbol;
        const price = parseFloat(stock.current_price || stock.price || 0);
        const change = parseFloat(stock.price_change_today || stock.change || 0);
        const changePercent = parseFloat(stock.change_percent || stock.changePercent || 0);
        const volume = formatVolume(stock.volume || 0);
        const marketCap = formatMarketCap(stock.market_cap || 0);
        const sector = stock.sector || 'N/A';
        
        const changeClass = change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = change >= 0 ? '↗' : '↘';
        
        row.innerHTML = `
            <td><span class="symbol-cell" onclick="viewStock('${symbol}')" title="Click to view ${symbol} details">${symbol}</span></td>
            <td>${company}</td>
            <td>$${price.toFixed(2)}</td>
            <td class="${changeClass}">${changeIcon} $${Math.abs(change).toFixed(2)}</td>
            <td class="${changeClass}">${changePercent.toFixed(2)}%</td>
            <td>${volume}</td>
            <td>${marketCap}</td>
            <td>${sector}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-small" onclick="addToWatchlist('${symbol}')" title="Add to watchlist">Add</button>
                    <button class="btn btn-outline btn-small" onclick="viewStock('${symbol}')" title="View details">View</button>
                </div>
            </td>
        `;
        
        return row;
    }
    
    function formatVolume(volume) {
        if (!volume) return 'N/A';
        const vol = parseInt(volume);
        if (vol >= 1000000) {
            return (vol / 1000000).toFixed(1) + 'M';
        } else if (vol >= 1000) {
            return (vol / 1000).toFixed(1) + 'K';
        }
        return vol.toString();
    }
    
    function formatMarketCap(marketCap) {
        if (!marketCap) return 'N/A';
        const cap = parseFloat(marketCap);
        if (cap >= 1000000000000) {
            return (cap / 1000000000000).toFixed(1) + 'T';
        } else if (cap >= 1000000000) {
            return (cap / 1000000000).toFixed(1) + 'B';
        } else if (cap >= 1000000) {
            return (cap / 1000000).toFixed(1) + 'M';
        }
        return cap.toString();
    }

    function resetAllFilters() {
        // Reset all form inputs
        document.querySelectorAll('.filters-panel input[type="checkbox"]').forEach(cb => {
            cb.checked = cb.value === 'mega' || cb.value === 'large' || cb.value === 'mid' || cb.value === 'small';
        });
        document.querySelectorAll('.filters-panel input[type="number"]').forEach(input => input.value = '');
        document.querySelectorAll('.filters-panel select').forEach(select => select.selectedIndex = 0);
        
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
            container.innerHTML = '<p style="color: var(--color-text-muted); text-align: center; grid-column: 1 / -1;">No saved screens yet. Create and save your first screen!</p>';
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