<?php
/**
 * Template Name: Watchlist
 * 
 * Complete watchlist management with categories and alerts
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
                <h1 class="text-4xl font-bold text-gray-900 mb-2">My Watchlist</h1>
                <p class="text-xl text-gray-600">Track stocks you're interested in</p>
            </div>
            <div class="watchlist-actions mt-4 md:mt-0 flex gap-3">
                <button id="add-stock-btn" class="btn btn-primary">
                    <i class="fas fa-plus mr-2"></i>
                    Add Stock
                </button>
                <button id="create-alert-btn" class="btn btn-outline-primary">
                    <i class="fas fa-bell mr-2"></i>
                    Create Alert
                </button>
                <button id="export-watchlist-btn" class="btn btn-outline-secondary">
                    <i class="fas fa-download mr-2"></i>
                    Export
                </button>
            </div>
        </div>
    </div>

    <!-- Watchlist Overview -->
    <div class="watchlist-overview grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Total Stocks</h3>
                <i class="fas fa-list text-2xl text-blue-600"></i>
            </div>
            <div id="total-stocks" class="text-3xl font-bold text-gray-900">0</div>
            <div class="text-sm text-gray-600 mt-2">In watchlist</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Gainers</h3>
                <i class="fas fa-arrow-up text-2xl text-green-600"></i>
            </div>
            <div id="gainers-count" class="text-3xl font-bold text-green-600">0</div>
            <div class="text-sm text-gray-600 mt-2">Positive today</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Losers</h3>
                <i class="fas fa-arrow-down text-2xl text-red-600"></i>
            </div>
            <div id="losers-count" class="text-3xl font-bold text-red-600">0</div>
            <div class="text-sm text-gray-600 mt-2">Negative today</div>
        </div>

        <div class="overview-card bg-white rounded-lg p-6 shadow-lg border">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">Active Alerts</h3>
                <i class="fas fa-bell text-2xl text-orange-600"></i>
            </div>
            <div id="active-alerts" class="text-3xl font-bold text-gray-900">0</div>
            <div class="text-sm text-gray-600 mt-2">Price alerts set</div>
        </div>
    </div>

    <!-- Categories and Filters -->
    <div class="filters-section bg-white rounded-lg p-6 shadow-lg border mb-8">
        <div class="flex flex-col md:flex-row md:items-center gap-4">
            <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Category</label>
                <select id="category-filter" class="form-select w-full md:w-48">
                    <option value="all">All Categories</option>
                    <!-- Populated by JavaScript -->
                </select>
            </div>
            
            <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-2">Search Stocks</label>
                <input type="text" id="stock-search" placeholder="Search by ticker or name..." 
                       class="form-input w-full">
            </div>
            
            <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                <select id="sort-by" class="form-select w-full md:w-48">
                    <option value="ticker">Ticker</option>
                    <option value="change_percent">Performance</option>
                    <option value="current_price">Price</option>
                    <option value="created_at">Date Added</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Watchlist Grid -->
    <div id="watchlist-container" class="watchlist-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Populated by JavaScript -->
    </div>

    <!-- Loading State -->
    <div id="watchlist-loading" class="loading-state hidden text-center py-12">
        <div class="spinner mx-auto mb-4"></div>
        <p class="text-gray-600">Loading your watchlist...</p>
    </div>

    <!-- Empty State -->
    <div id="empty-watchlist" class="empty-state hidden text-center py-16">
        <div class="empty-icon text-6xl mb-6">👁️</div>
        <h3 class="text-2xl font-semibold text-gray-900 mb-4">Your Watchlist is Empty</h3>
        <p class="text-gray-600 mb-8 max-w-md mx-auto">
            Start tracking stocks that interest you. Add them to your watchlist to monitor their performance.
        </p>
        <button class="btn btn-primary btn-lg" onclick="document.getElementById('add-stock-btn').click()">
            <i class="fas fa-plus mr-2"></i>
            Add Your First Stock
        </button>
    </div>

    <!-- Add Stock Modal -->
    <div id="add-stock-modal" class="modal hidden fixed inset-0 bg-black bg-opacity-50 z-50">
        <div class="modal-dialog flex items-center justify-center min-h-screen p-4">
            <div class="modal-content bg-white rounded-lg shadow-xl max-w-md w-full">
                <div class="modal-header p-6 border-b">
                    <h3 class="text-xl font-semibold text-gray-900">Add Stock to Watchlist</h3>
                    <button class="modal-close absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <form id="add-stock-form" class="p-6">
                    <div class="form-group mb-4">
                        <label class="form-label">Stock Ticker</label>
                        <input type="text" name="ticker" id="modal-ticker" required
                               class="form-input" placeholder="e.g., AAPL" maxlength="5">
                        <div id="ticker-suggestions" class="suggestions-dropdown hidden"></div>
                    </div>
                    
                    <div class="form-group mb-4">
                        <label class="form-label">Category</label>
                        <select name="category" id="modal-category" class="form-select">
                            <option value="default">Default</option>
                            <option value="growth">Growth Stocks</option>
                            <option value="dividend">Dividend Stocks</option>
                            <option value="tech">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                            <option value="energy">Energy</option>
                        </select>
                    </div>
                    
                    <div class="form-group mb-6">
                        <label class="form-label">Notes (Optional)</label>
                        <textarea name="notes" rows="3" class="form-input" 
                                  placeholder="Why are you watching this stock?"></textarea>
                    </div>
                    
                    <div class="form-actions flex justify-end space-x-3">
                        <button type="button" class="modal-close btn btn-outline-secondary">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus mr-2"></i>
                            Add to Watchlist
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Create Alert Modal -->
    <div id="create-alert-modal" class="modal hidden fixed inset-0 bg-black bg-opacity-50 z-50">
        <div class="modal-dialog flex items-center justify-center min-h-screen p-4">
            <div class="modal-content bg-white rounded-lg shadow-xl max-w-md w-full">
                <div class="modal-header p-6 border-b">
                    <h3 class="text-xl font-semibold text-gray-900">Create Price Alert</h3>
                    <button class="modal-close absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <form id="create-alert-form" class="p-6">
                    <div class="form-group mb-4">
                        <label class="form-label">Stock Ticker</label>
                        <select name="ticker" id="alert-ticker" required class="form-select">
                            <option value="">Select a stock from your watchlist</option>
                            <!-- Populated by JavaScript -->
                        </select>
                    </div>
                    
                    <div class="form-group mb-4">
                        <label class="form-label">Alert Condition</label>
                        <select name="condition" required class="form-select">
                            <option value="above">Price goes above</option>
                            <option value="below">Price goes below</option>
                        </select>
                    </div>
                    
                    <div class="form-group mb-4">
                        <label class="form-label">Target Price</label>
                        <input type="number" name="target_price" step="0.01" min="0.01" required
                               class="form-input" placeholder="e.g., 150.00">
                    </div>
                    
                    <div class="form-group mb-6">
                        <label class="form-label">Email Notification</label>
                        <input type="email" name="email" class="form-input" 
                               value="<?php echo wp_get_current_user()->user_email; ?>"
                               placeholder="your@email.com">
                    </div>
                    
                    <div class="form-actions flex justify-end space-x-3">
                        <button type="button" class="modal-close btn btn-outline-secondary">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-bell mr-2"></i>
                            Create Alert
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    new WatchlistManager();
});

class WatchlistManager {
    constructor() {
        this.watchlist = null;
        this.filteredItems = [];
        this.currentFilter = 'all';
        this.currentSort = 'ticker';
        this.searchQuery = '';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadWatchlistData();
        
        console.log('Watchlist Manager initialized');
    }
    
    async loadWatchlistData() {
        try {
            this.showLoading();
            
            const response = await StockScannerAPI.Watchlist.getWatchlist();
            
            if (response.success && response.watchlist) {
                this.watchlist = response.watchlist;
                this.renderWatchlist();
                this.initializeFilters();
                
                // Start real-time updates
                if (this.watchlist.items && this.watchlist.items.length > 0) {
                    const tickers = this.watchlist.items.map(item => item.ticker);
                    StockScannerAPI.RealTime.startUpdates(tickers, (data) => {
                        this.updateRealTimeData(data);
                    });
                }
            } else {
                this.showEmptyState();
            }
            
            this.hideLoading();
        } catch (error) {
            console.error('Watchlist loading error:', error);
            this.showError('Failed to load watchlist data');
            this.hideLoading();
        }
    }
    
    renderWatchlist() {
        if (!this.watchlist || !this.watchlist.items || this.watchlist.items.length === 0) {
            this.showEmptyState();
            return;
        }
        
        this.renderOverview();
        this.applyFiltersAndSort();
        this.renderWatchlistGrid();
        this.hideEmptyState();
    }
    
    renderOverview() {
        if (!this.watchlist.items) return;
        
        const items = this.watchlist.items;
        const totalStocks = items.length;
        const gainers = items.filter(item => item.stock_data?.price_change > 0).length;
        const losers = items.filter(item => item.stock_data?.price_change < 0).length;
        
        document.getElementById('total-stocks').textContent = totalStocks;
        document.getElementById('gainers-count').textContent = gainers;
        document.getElementById('losers-count').textContent = losers;
        
        // TODO: Get active alerts count from API
        document.getElementById('active-alerts').textContent = '0';
    }
    
    initializeFilters() {
        // Populate category filter
        const categories = ['all', ...this.watchlist.categories];
        const categoryFilter = document.getElementById('category-filter');
        
        categoryFilter.innerHTML = categories.map(cat => 
            `<option value="${cat}">${cat === 'all' ? 'All Categories' : this.capitalize(cat)}</option>`
        ).join('');
        
        // Populate alert ticker dropdown
        const alertTicker = document.getElementById('alert-ticker');
        alertTicker.innerHTML = '<option value="">Select a stock from your watchlist</option>' +
            this.watchlist.items.map(item => 
                `<option value="${item.ticker}">${item.ticker} - ${item.stock_data?.company_name || item.ticker}</option>`
            ).join('');
    }
    
    applyFiltersAndSort() {
        let items = [...this.watchlist.items];
        
        // Apply category filter
        if (this.currentFilter !== 'all') {
            items = items.filter(item => item.category === this.currentFilter);
        }
        
        // Apply search filter
        if (this.searchQuery) {
            items = items.filter(item => 
                item.ticker.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                (item.stock_data?.company_name || '').toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        }
        
        // Apply sort
        items.sort((a, b) => {
            let aValue, bValue;
            
            switch (this.currentSort) {
                case 'ticker':
                    aValue = a.ticker;
                    bValue = b.ticker;
                    break;
                case 'change_percent':
                    aValue = a.stock_data?.price_change_percent || 0;
                    bValue = b.stock_data?.price_change_percent || 0;
                    return bValue - aValue; // Descending for performance
                case 'current_price':
                    aValue = a.stock_data?.current_price || 0;
                    bValue = b.stock_data?.current_price || 0;
                    return bValue - aValue; // Descending for price
                case 'created_at':
                    aValue = new Date(a.created_at);
                    bValue = new Date(b.created_at);
                    return bValue - aValue; // Most recent first
                default:
                    return 0;
            }
            
            if (typeof aValue === 'string') {
                return aValue.localeCompare(bValue);
            }
            return aValue - bValue;
        });
        
        this.filteredItems = items;
    }
    
    renderWatchlistGrid() {
        const container = document.getElementById('watchlist-container');
        if (!container) return;
        
        if (this.filteredItems.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="text-4xl mb-4">🔍</div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">No stocks found</h3>
                    <p class="text-gray-600">Try adjusting your filters or search terms.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.filteredItems.map(item => this.renderWatchlistCard(item)).join('');
    }
    
    renderWatchlistCard(item) {
        const stockData = item.stock_data || {};
        const change = stockData.price_change || 0;
        const changePercent = stockData.price_change_percent || 0;
        const changeClass = change >= 0 ? 'text-green-600' : 'text-red-600';
        const bgClass = change >= 0 ? 'bg-green-50' : 'bg-red-50';
        
        return `
            <div class="watchlist-card bg-white rounded-lg shadow-lg border hover:shadow-xl transition-shadow" data-ticker="${item.ticker}">
                <div class="card-header p-4 border-b ${bgClass}">
                    <div class="flex items-center justify-between">
                        <div>
                            <h4 class="text-lg font-bold font-mono">${item.ticker}</h4>
                            <p class="text-sm text-gray-600 truncate">${stockData.company_name || item.ticker}</p>
                        </div>
                        <div class="text-right">
                            <div class="text-xl font-bold font-mono">${StockScannerAPI.Utils.formatCurrency(stockData.current_price || 0)}</div>
                            <div class="text-sm ${changeClass}">
                                ${StockScannerAPI.Utils.formatCurrency(change)} (${StockScannerAPI.Utils.formatPercentage(changePercent)})
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card-body p-4">
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <span class="text-xs text-gray-500 uppercase tracking-wide">Volume</span>
                            <div class="font-mono text-sm">${StockScannerAPI.Utils.formatNumber(stockData.volume || 0)}</div>
                        </div>
                        <div>
                            <span class="text-xs text-gray-500 uppercase tracking-wide">Market Cap</span>
                            <div class="font-mono text-sm">${StockScannerAPI.Utils.formatNumber(stockData.market_cap || 0)}</div>
                        </div>
                    </div>
                    
                    <div class="category-tag mb-4">
                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                            ${this.capitalize(item.category)}
                        </span>
                    </div>
                    
                    ${item.notes ? `
                        <div class="notes mb-4">
                            <span class="text-xs text-gray-500 uppercase tracking-wide">Notes</span>
                            <p class="text-sm text-gray-700 mt-1">${item.notes}</p>
                        </div>
                    ` : ''}
                    
                    <div class="card-actions flex justify-between items-center">
                        <span class="text-xs text-gray-500">
                            Added ${this.formatDate(item.created_at)}
                        </span>
                        <div class="flex space-x-2">
                            <button class="btn btn-sm btn-outline-primary add-to-portfolio-btn" 
                                    data-ticker="${item.ticker}" title="Add to Portfolio">
                                <i class="fas fa-plus"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning create-alert-btn" 
                                    data-ticker="${item.ticker}" title="Create Alert">
                                <i class="fas fa-bell"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger remove-stock-btn" 
                                    data-item-id="${item.id}" title="Remove from Watchlist">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Add stock button
        document.getElementById('add-stock-btn')?.addEventListener('click', () => {
            this.showAddStockModal();
        });
        
        // Create alert button
        document.getElementById('create-alert-btn')?.addEventListener('click', () => {
            this.showCreateAlertModal();
        });
        
        // Filter controls
        document.getElementById('category-filter')?.addEventListener('change', (e) => {
            this.currentFilter = e.target.value;
            this.applyFiltersAndSort();
            this.renderWatchlistGrid();
        });
        
        document.getElementById('sort-by')?.addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.applyFiltersAndSort();
            this.renderWatchlistGrid();
        });
        
        document.getElementById('stock-search')?.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            this.applyFiltersAndSort();
            this.renderWatchlistGrid();
        });
        
        // Form submissions
        document.getElementById('add-stock-form')?.addEventListener('submit', (e) => {
            this.handleAddStock(e);
        });
        
        document.getElementById('create-alert-form')?.addEventListener('submit', (e) => {
            this.handleCreateAlert(e);
        });
        
        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') || e.target.classList.contains('modal-close')) {
                this.closeModals();
            }
        });
        
        // Card action buttons (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-stock-btn')) {
                const itemId = e.target.closest('.remove-stock-btn').dataset.itemId;
                this.removeStock(itemId);
            } else if (e.target.closest('.add-to-portfolio-btn')) {
                const ticker = e.target.closest('.add-to-portfolio-btn').dataset.ticker;
                this.addToPortfolio(ticker);
            } else if (e.target.closest('.create-alert-btn')) {
                const ticker = e.target.closest('.create-alert-btn').dataset.ticker;
                this.showCreateAlertModal(ticker);
            }
        });
    }
    
    showAddStockModal() {
        document.getElementById('add-stock-modal').classList.remove('hidden');
        document.getElementById('modal-ticker').focus();
    }
    
    showCreateAlertModal(ticker = '') {
        document.getElementById('create-alert-modal').classList.remove('hidden');
        if (ticker) {
            document.getElementById('alert-ticker').value = ticker;
        }
    }
    
    closeModals() {
        document.getElementById('add-stock-modal').classList.add('hidden');
        document.getElementById('create-alert-modal').classList.add('hidden');
        document.getElementById('add-stock-form').reset();
        document.getElementById('create-alert-form').reset();
    }
    
    async handleAddStock(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const ticker = formData.get('ticker').toUpperCase();
        const category = formData.get('category');
        const notes = formData.get('notes');
        
        try {
            const result = await StockScannerAPI.Watchlist.addToWatchlist(ticker, notes, category);
            
            StockScannerAPI.Toast.show(`${ticker} added to watchlist!`, 'success');
            this.closeModals();
            this.loadWatchlistData();
        } catch (error) {
            console.error('Add stock error:', error);
            StockScannerAPI.Toast.show('Failed to add stock to watchlist', 'error');
        }
    }
    
    async handleCreateAlert(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const ticker = formData.get('ticker');
        const condition = formData.get('condition');
        const targetPrice = parseFloat(formData.get('target_price'));
        const email = formData.get('email');
        
        try {
            const result = await StockScannerAPI.Alerts.createAlert(ticker, targetPrice, condition, email);
            
            StockScannerAPI.Toast.show(`Price alert created for ${ticker}!`, 'success');
            this.closeModals();
        } catch (error) {
            console.error('Create alert error:', error);
            StockScannerAPI.Toast.show('Failed to create price alert', 'error');
        }
    }
    
    async removeStock(itemId) {
        if (!confirm('Are you sure you want to remove this stock from your watchlist?')) {
            return;
        }
        
        try {
            await StockScannerAPI.Watchlist.removeFromWatchlist(itemId);
            StockScannerAPI.Toast.show('Stock removed from watchlist', 'success');
            this.loadWatchlistData();
        } catch (error) {
            console.error('Remove stock error:', error);
            StockScannerAPI.Toast.show('Failed to remove stock', 'error');
        }
    }
    
    showLoading() {
        document.getElementById('watchlist-loading').classList.remove('hidden');
        document.getElementById('watchlist-container').classList.add('hidden');
        document.getElementById('empty-watchlist').classList.add('hidden');
    }
    
    hideLoading() {
        document.getElementById('watchlist-loading').classList.add('hidden');
        document.getElementById('watchlist-container').classList.remove('hidden');
    }
    
    showEmptyState() {
        document.getElementById('empty-watchlist').classList.remove('hidden');
        document.getElementById('watchlist-container').classList.add('hidden');
    }
    
    hideEmptyState() {
        document.getElementById('empty-watchlist').classList.add('hidden');
    }
    
    showError(message) {
        StockScannerAPI.Toast.show(message, 'error');
    }
    
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
}
</script>

<?php get_footer(); ?>