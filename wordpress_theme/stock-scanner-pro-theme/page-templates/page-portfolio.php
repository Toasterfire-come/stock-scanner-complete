<?php
/**
 * Template Name: Portfolio
 * 
 * Complete portfolio management with performance analytics
 *
 * @package StockScannerPro
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
                <h1 class="text-4xl font-bold text-gray-900 mb-2">My Portfolio</h1>
                <p class="text-xl text-gray-600">Track your investments and performance</p>
            </div>
            <div class="portfolio-actions mt-4 md:mt-0 flex gap-3">
                <button id="add-holding-btn" class="btn btn-primary">
                    <i class="fas fa-plus mr-2"></i>
                    Add Holding
                </button>
                <button id="export-portfolio-btn" class="btn btn-outline-primary">
                    <i class="fas fa-download mr-2"></i>
                    Export
                </button>
                <button id="refresh-portfolio-btn" class="btn btn-outline-secondary">
                    <i class="fas fa-sync-alt mr-2"></i>
                    Refresh
                </button>
            </div>
        </div>
    </div>

    <!-- Portfolio Overview -->
    <div class="portfolio-overview grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Total Value</h3>
                <i class="fas fa-wallet text-2xl text-blue-600"></i>
            </div>
            <div id="total-value" class="text-3xl font-bold text-gray-900 font-mono">$0.00</div>
            <div id="total-change" class="text-sm mt-2">$0.00 (0.00%)</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Today's P&L</h3>
                <i class="fas fa-chart-line text-2xl text-green-600"></i>
            </div>
            <div id="daily-pnl" class="text-3xl font-bold text-gray-900 font-mono">$0.00</div>
            <div id="daily-pnl-percent" class="text-sm mt-2">0.00%</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Holdings</h3>
                <i class="fas fa-list text-2xl text-purple-600"></i>
            </div>
            <div id="holdings-count" class="text-3xl font-bold text-gray-900">0</div>
            <div class="text-sm text-gray-600 mt-2">Active positions</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Diversity Score</h3>
                <i class="fas fa-balance-scale text-2xl text-orange-600"></i>
            </div>
            <div id="diversity-score" class="text-3xl font-bold text-gray-900">0</div>
            <div class="text-sm text-gray-600 mt-2">Portfolio balance</div>
        </div>
    </div>

    <!-- Portfolio Performance Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        
        <!-- Performance Chart -->
        <div class="chart-container">
            <div class="chart-header">
                <h3 class="chart-title">Portfolio Performance</h3>
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
                <canvas id="portfolio-performance-chart"></canvas>
            </div>
        </div>

        <!-- Allocation Chart -->
        <div class="chart-container">
            <div class="chart-header">
                <h3 class="chart-title">Asset Allocation</h3>
                <div class="chart-controls">
                    <select id="allocation-view" class="form-select">
                        <option value="holdings">By Holdings</option>
                        <option value="sectors">By Sectors</option>
                        <option value="market_cap">By Market Cap</option>
                    </select>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas id="portfolio-allocation-chart"></canvas>
            </div>
        </div>
    </div>

    <!-- Holdings Table -->
    <div class="holdings-section bg-white rounded-lg shadow-lg border">
        <div class="holdings-header p-6 border-b">
            <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">Holdings</h3>
                <div class="holdings-controls flex gap-3">
                    <input type="text" id="holdings-search" placeholder="Search holdings..." 
                           class="form-input w-64">
                    <select id="holdings-sort" class="form-select">
                        <option value="ticker">Ticker</option>
                        <option value="value">Market Value</option>
                        <option value="gain_loss">Gain/Loss</option>
                        <option value="gain_loss_percent">Gain/Loss %</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="holdings-table-container">
            <div id="holdings-table" class="holdings-table">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- Performance Analytics -->
    <div class="analytics-section mt-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Risk Metrics -->
            <div class="analytics-card bg-white rounded-lg p-6 shadow-lg border">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h4>
                <div class="metrics-list space-y-3">
                    <div class="metric-item flex justify-between">
                        <span class="text-gray-600">Volatility</span>
                        <span id="volatility" class="font-mono font-semibold">0.00%</span>
                    </div>
                    <div class="metric-item flex justify-between">
                        <span class="text-gray-600">Sharpe Ratio</span>
                        <span id="sharpe-ratio" class="font-mono font-semibold">0.00</span>
                    </div>
                    <div class="metric-item flex justify-between">
                        <span class="text-gray-600">Beta</span>
                        <span id="beta" class="font-mono font-semibold">0.00</span>
                    </div>
                    <div class="metric-item flex justify-between">
                        <span class="text-gray-600">Max Drawdown</span>
                        <span id="max-drawdown" class="font-mono font-semibold">0.00%</span>
                    </div>
                </div>
            </div>

            <!-- Top Performers -->
            <div class="analytics-card bg-white rounded-lg p-6 shadow-lg border">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Top Performers</h4>
                <div id="top-performers" class="performers-list">
                    <!-- Populated by JavaScript -->
                </div>
            </div>

            <!-- Worst Performers -->
            <div class="analytics-card bg-white rounded-lg p-6 shadow-lg border">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Worst Performers</h4>
                <div id="worst-performers" class="performers-list">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <!-- Loading State -->
    <div id="portfolio-loading" class="loading-state hidden fixed inset-0 bg-black bg-opacity-50 z-50">
        <div class="flex items-center justify-center min-h-screen">
            <div class="loading-spinner bg-white rounded-lg p-8 shadow-xl">
                <div class="flex items-center space-x-3">
                    <div class="spinner"></div>
                    <span class="text-gray-900 font-medium">Loading portfolio data...</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Holding Modal -->
    <div id="add-holding-modal" class="modal hidden fixed inset-0 bg-black bg-opacity-50 z-50">
        <div class="modal-dialog flex items-center justify-center min-h-screen p-4">
            <div class="modal-content bg-white rounded-lg shadow-xl max-w-md w-full">
                <div class="modal-header p-6 border-b">
                    <h3 class="text-xl font-semibold text-gray-900">Add Stock to Portfolio</h3>
                    <button class="modal-close absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <form id="add-holding-form" class="p-6">
                    <div class="form-group mb-4">
                        <label class="form-label">Stock Ticker</label>
                        <input type="text" name="ticker" id="modal-ticker" required
                               class="form-input" placeholder="e.g., AAPL" maxlength="5">
                        <div id="ticker-suggestions" class="suggestions-dropdown hidden"></div>
                    </div>
                    
                    <div class="form-group mb-4">
                        <label class="form-label">Number of Shares</label>
                        <input type="number" name="shares" step="0.0001" min="0.0001" required
                               class="form-input" placeholder="e.g., 100">
                    </div>
                    
                    <div class="form-group mb-4">
                        <label class="form-label">Cost per Share</label>
                        <input type="number" name="cost_basis" step="0.01" min="0.01" required
                               class="form-input" placeholder="e.g., 150.00">
                    </div>
                    
                    <div class="form-group mb-6">
                        <label class="form-label">Purchase Date</label>
                        <input type="date" name="purchase_date" class="form-input">
                    </div>
                    
                    <div class="form-actions flex justify-end space-x-3">
                        <button type="button" class="modal-close btn btn-outline-secondary">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus mr-2"></i>
                            Add to Portfolio
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    new PortfolioManager();
});

class PortfolioManager {
    constructor() {
        this.portfolio = null;
        this.charts = {};
        this.sortField = 'ticker';
        this.sortDirection = 'asc';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadPortfolioData();
        
        console.log('Portfolio Manager initialized');
    }
    
    async loadPortfolioData() {
        try {
            this.showLoading();
            
            const response = await StockScannerAPI.Portfolio.getPortfolio();
            
            if (response.success && response.portfolio) {
                this.portfolio = response.portfolio;
                this.renderPortfolio();
                this.initializeCharts();
                
                // Start real-time updates if holdings exist
                if (this.portfolio.holdings && this.portfolio.holdings.length > 0) {
                    const tickers = this.portfolio.holdings.map(h => h.ticker);
                    StockScannerAPI.RealTime.startUpdates(tickers, (data) => {
                        this.updateRealTimeData(data);
                    });
                }
            } else {
                this.renderEmptyPortfolio();
            }
            
            this.hideLoading();
        } catch (error) {
            console.error('Portfolio loading error:', error);
            this.showError('Failed to load portfolio data');
            this.hideLoading();
        }
    }
    
    renderPortfolio() {
        if (!this.portfolio) return;
        
        this.renderOverview();
        this.renderHoldingsTable();
        this.renderAnalytics();
    }
    
    renderOverview() {
        const summary = this.portfolio.summary;
        
        // Total Value
        document.getElementById('total-value').textContent = 
            StockScannerAPI.Utils.formatCurrency(summary.total_value);
        
        // Total Change
        const totalChangeEl = document.getElementById('total-change');
        const changeClass = summary.total_gain_loss >= 0 ? 'text-success' : 'text-danger';
        totalChangeEl.className = `text-sm mt-2 ${changeClass}`;
        totalChangeEl.textContent = `${StockScannerAPI.Utils.formatCurrency(summary.total_gain_loss)} (${StockScannerAPI.Utils.formatPercentage(summary.total_gain_loss_percent)})`;
        
        // Holdings Count
        document.getElementById('holdings-count').textContent = summary.holdings_count;
        
        // Calculate and display other metrics
        this.updatePerformanceMetrics();
    }
    
    renderHoldingsTable() {
        const container = document.getElementById('holdings-table');
        if (!container) return;
        
        if (!this.portfolio.holdings || this.portfolio.holdings.length === 0) {
            container.innerHTML = `
                <div class="empty-holdings text-center py-12">
                    <div class="empty-icon text-6xl mb-4">📊</div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">No Holdings Yet</h3>
                    <p class="text-gray-600 mb-6">Start building your portfolio by adding some stocks.</p>
                    <button class="btn btn-primary" onclick="document.getElementById('add-holding-btn').click()">
                        <i class="fas fa-plus mr-2"></i>
                        Add Your First Stock
                    </button>
                </div>
            `;
            return;
        }
        
        // Sort holdings
        const sortedHoldings = [...this.portfolio.holdings].sort((a, b) => {
            const aValue = a[this.sortField] || 0;
            const bValue = b[this.sortField] || 0;
            
            if (this.sortDirection === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });
        
        const tableHTML = `
            <div class="holdings-table-header grid grid-cols-8 gap-4 p-4 bg-gray-50 font-semibold text-gray-700 border-b">
                <div class="col-span-2">Stock</div>
                <div class="text-right">Shares</div>
                <div class="text-right">Avg Cost</div>
                <div class="text-right">Current Price</div>
                <div class="text-right">Market Value</div>
                <div class="text-right">Gain/Loss</div>
                <div class="text-center">Actions</div>
            </div>
            <div class="holdings-table-body">
                ${sortedHoldings.map(holding => this.renderHoldingRow(holding)).join('')}
            </div>
        `;
        
        container.innerHTML = tableHTML;
    }
    
    renderHoldingRow(holding) {
        const changeClass = holding.gain_loss >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <div class="holding-row grid grid-cols-8 gap-4 p-4 border-b hover:bg-gray-50 items-center" data-ticker="${holding.ticker}">
                <div class="col-span-2">
                    <div class="font-mono font-semibold">${holding.ticker}</div>
                    <div class="text-sm text-gray-600">${holding.stock_data?.company_name || holding.ticker}</div>
                </div>
                <div class="text-right font-mono">${holding.shares}</div>
                <div class="text-right font-mono">${StockScannerAPI.Utils.formatCurrency(holding.average_cost)}</div>
                <div class="text-right font-mono">${StockScannerAPI.Utils.formatCurrency(holding.current_price)}</div>
                <div class="text-right font-mono font-semibold">${StockScannerAPI.Utils.formatCurrency(holding.current_value)}</div>
                <div class="text-right font-mono ${changeClass}">
                    <div>${StockScannerAPI.Utils.formatCurrency(holding.gain_loss)}</div>
                    <div class="text-sm">${StockScannerAPI.Utils.formatPercentage(holding.gain_loss_percent)}</div>
                </div>
                <div class="text-center">
                    <button class="btn btn-sm btn-outline-danger remove-holding-btn" data-holding-id="${holding.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Add holding button
        document.getElementById('add-holding-btn')?.addEventListener('click', () => {
            this.showAddHoldingModal();
        });
        
        // Refresh button
        document.getElementById('refresh-portfolio-btn')?.addEventListener('click', () => {
            this.loadPortfolioData();
        });
        
        // Export button
        document.getElementById('export-portfolio-btn')?.addEventListener('click', () => {
            this.exportPortfolio();
        });
        
        // Add holding form
        document.getElementById('add-holding-form')?.addEventListener('submit', (e) => {
            this.handleAddHolding(e);
        });
        
        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') || e.target.classList.contains('modal-close')) {
                this.closeModal();
            }
        });
        
        // Remove holding buttons (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-holding-btn')) {
                const holdingId = e.target.closest('.remove-holding-btn').dataset.holdingId;
                this.removeHolding(holdingId);
            }
        });
        
        // Ticker search suggestions
        document.getElementById('modal-ticker')?.addEventListener('input', (e) => {
            this.handleTickerSearch(e);
        });
        
        // Sort controls
        document.getElementById('holdings-sort')?.addEventListener('change', (e) => {
            this.sortField = e.target.value;
            this.renderHoldingsTable();
        });
    }
    
    showAddHoldingModal() {
        document.getElementById('add-holding-modal').classList.remove('hidden');
        document.getElementById('modal-ticker').focus();
    }
    
    closeModal() {
        document.getElementById('add-holding-modal').classList.add('hidden');
        document.getElementById('add-holding-form').reset();
    }
    
    async handleAddHolding(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const ticker = formData.get('ticker').toUpperCase();
        const shares = parseFloat(formData.get('shares'));
        const costBasis = parseFloat(formData.get('cost_basis'));
        const purchaseDate = formData.get('purchase_date') || null;
        
        try {
            const result = await StockScannerAPI.Portfolio.addToPortfolio(ticker, shares, costBasis, purchaseDate);
            
            StockScannerAPI.Toast.show(`${ticker} added to portfolio!`, 'success');
            this.closeModal();
            this.loadPortfolioData();
        } catch (error) {
            console.error('Add holding error:', error);
            StockScannerAPI.Toast.show('Failed to add stock to portfolio', 'error');
        }
    }
    
    async removeHolding(holdingId) {
        if (!confirm('Are you sure you want to remove this holding from your portfolio?')) {
            return;
        }
        
        try {
            await StockScannerAPI.Portfolio.removeFromPortfolio(holdingId);
            StockScannerAPI.Toast.show('Holding removed from portfolio', 'success');
            this.loadPortfolioData();
        } catch (error) {
            console.error('Remove holding error:', error);
            StockScannerAPI.Toast.show('Failed to remove holding', 'error');
        }
    }
    
    showLoading() {
        document.getElementById('portfolio-loading').classList.remove('hidden');
    }
    
    hideLoading() {
        document.getElementById('portfolio-loading').classList.add('hidden');
    }
    
    showError(message) {
        StockScannerAPI.Toast.show(message, 'error');
    }
    
    renderEmptyPortfolio() {
        const container = document.getElementById('holdings-table');
        if (container) {
            this.renderHoldingsTable(); // This will show the empty state
        }
    }
}
</script>

<style>
.form-label {
    display: block;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
}

.form-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    transition: border-color 0.15s ease-in-out;
}

.form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-select {
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    background-color: white;
    font-size: 0.875rem;
}

.suggestions-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 10;
    max-height: 200px;
    overflow-y: auto;
}
</style>

<?php get_footer(); ?>