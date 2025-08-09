<?php
/**
 * Template Name: Enhanced Watchlist
 * Description: Advanced watchlist management with import/export and performance tracking
 */

// Security check - require user authentication
if (!is_user_logged_in()) {
    wp_redirect(wp_registration_url());
    exit;
}

get_header(); ?>

<div class="enhanced-watchlist-container">
    <div class="container-fluid">
        <div class="row">
            <!-- Page Header -->
            <div class="col-12">
                <div class="page-header">
                    <h1 class="page-title">
                        <i class="fas fa-eye"></i> Enhanced Watchlist
                    </h1>
                    <p class="page-description">
                        Create unlimited watchlists with import/export, performance tracking, and advanced alerts
                    </p>
                </div>
            </div>
        </div>

        <!-- Watchlist Actions Bar -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="watchlist-actions-bar">
                    <button class="btn btn-primary" id="create-watchlist-btn">
                        <i class="fas fa-plus"></i> Create Watchlist
                    </button>
                    <button class="btn btn-success" id="import-watchlist-btn">
                        <i class="fas fa-upload"></i> Import Watchlist
                    </button>
                    <button class="btn btn-warning" id="bulk-add-stocks-btn">
                        <i class="fas fa-layer-group"></i> Bulk Add Stocks
                    </button>
                    <div class="watchlist-filters">
                        <select id="watchlist-view" class="form-select">
                            <option value="grid">Grid View</option>
                            <option value="list">List View</option>
                            <option value="performance">Performance View</option>
                        </select>
                        <select id="watchlist-sort" class="form-select">
                            <option value="created">Sort by Created Date</option>
                            <option value="performance">Sort by Performance</option>
                            <option value="items">Sort by Item Count</option>
                            <option value="name">Sort by Name</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Watchlist Tabs -->
        <div class="row">
            <div class="col-12">
                <ul class="nav nav-tabs" id="watchlist-tabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="all-watchlists-tab" data-bs-toggle="tab" 
                                data-bs-target="#all-watchlists" type="button" role="tab">
                            <i class="fas fa-list"></i> All Watchlists
                        </button>
                    </li>
                    <!-- Additional tabs will be added dynamically -->
                </ul>
            </div>
        </div>

        <!-- Watchlist Content -->
        <div class="tab-content" id="watchlist-tab-content">
            <div class="tab-pane fade show active" id="all-watchlists" role="tabpanel">
                <div class="row mt-3" id="watchlists-container">
                    <!-- Watchlists will be loaded here via JavaScript -->
                    <div class="col-12">
                        <div class="loading-spinner text-center">
                            <i class="fas fa-spinner fa-spin fa-2x"></i>
                            <p>Loading your watchlists...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Summary -->
        <div class="row mt-5">
            <div class="col-12">
                <div class="performance-summary-card">
                    <h3><i class="fas fa-chart-line"></i> Watchlist Performance Summary</h3>
                    <div class="row" id="watchlist-performance-summary">
                        <!-- Performance metrics will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Create Watchlist Modal -->
<div class="modal fade" id="createWatchlistModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Create New Watchlist</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="create-watchlist-form">
                    <div class="mb-3">
                        <label for="watchlist-name" class="form-label">Watchlist Name *</label>
                        <input type="text" class="form-control" id="watchlist-name" required>
                    </div>
                    <div class="mb-3">
                        <label for="watchlist-description" class="form-label">Description</label>
                        <textarea class="form-control" id="watchlist-description" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-watchlist-btn">Create Watchlist</button>
            </div>
        </div>
    </div>
</div>

<!-- Add Stock to Watchlist Modal -->
<div class="modal fade" id="addStockModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add Stock to Watchlist</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="add-stock-form">
                    <input type="hidden" id="target-watchlist-id">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="stock-ticker-add" class="form-label">Stock Ticker *</label>
                                <input type="text" class="form-control" id="stock-ticker-add" placeholder="e.g., AAPL" required>
                                <div class="stock-search-results" id="stock-search-results-add"></div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="added-price" class="form-label">Price When Added</label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" id="added-price" step="0.01" min="0.01">
                                    <button class="btn btn-outline-secondary" type="button" id="use-current-price">Use Current</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="target-price" class="form-label">Target Price</label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" id="target-price" step="0.01" min="0.01">
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="stop-loss" class="form-label">Stop Loss</label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" id="stop-loss" step="0.01" min="0.01">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="stock-notes" class="form-label">Notes</label>
                        <textarea class="form-control" id="stock-notes" rows="3" placeholder="Your analysis or reasoning..."></textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="price-alert-enabled">
                                <label class="form-check-label" for="price-alert-enabled">
                                    Enable Price Alerts
                                </label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="news-alert-enabled">
                                <label class="form-check-label" for="news-alert-enabled">
                                    Enable News Alerts
                                </label>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-stock-btn">Add Stock</button>
            </div>
        </div>
    </div>
</div>

<!-- Import Watchlist Modal -->
<div class="modal fade" id="importWatchlistModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Import Watchlist</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="import-format-tabs">
                    <ul class="nav nav-pills mb-3" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="csv-import-tab" data-bs-toggle="pill" 
                                    data-bs-target="#csv-import" type="button" role="tab">
                                CSV Import
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="json-import-tab" data-bs-toggle="pill" 
                                    data-bs-target="#json-import" type="button" role="tab">
                                JSON Import
                            </button>
                        </li>
                    </ul>
                </div>
                
                <div class="tab-content">
                    <!-- CSV Import -->
                    <div class="tab-pane fade show active" id="csv-import" role="tabpanel">
                        <div class="import-instructions mb-4">
                            <h6>CSV Format Requirements:</h6>
                            <p>Your CSV file should include the following columns:</p>
                            <code>ticker,added_price,notes,target_price,stop_loss,price_alert_enabled,news_alert_enabled</code>
                        </div>
                        <form id="import-csv-watchlist-form">
                            <div class="mb-3">
                                <label for="import-watchlist-name-csv" class="form-label">Watchlist Name *</label>
                                <input type="text" class="form-control" id="import-watchlist-name-csv" required>
                            </div>
                            <div class="mb-3">
                                <label for="csv-watchlist-file" class="form-label">CSV File *</label>
                                <input type="file" class="form-control" id="csv-watchlist-file" accept=".csv" required>
                            </div>
                        </form>
                    </div>
                    
                    <!-- JSON Import -->
                    <div class="tab-pane fade" id="json-import" role="tabpanel">
                        <div class="import-instructions mb-4">
                            <h6>JSON Format:</h6>
                            <p>Upload a JSON file exported from another watchlist system</p>
                        </div>
                        <form id="import-json-watchlist-form">
                            <div class="mb-3">
                                <label for="json-watchlist-file" class="form-label">JSON File *</label>
                                <input type="file" class="form-control" id="json-watchlist-file" accept=".json" required>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="import-preview" id="import-watchlist-preview" style="display: none;">
                    <h6>Import Preview</h6>
                    <div class="preview-content"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-success" id="import-watchlist-btn-submit">Import Watchlist</button>
            </div>
        </div>
    </div>
</div>

<!-- Bulk Add Stocks Modal -->
<div class="modal fade" id="bulkAddModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Bulk Add Stocks</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="bulk-add-form">
                    <div class="mb-3">
                        <label for="bulk-target-watchlist" class="form-label">Target Watchlist *</label>
                        <select class="form-select" id="bulk-target-watchlist" required>
                            <option value="">Select a watchlist...</option>
                            <!-- Watchlist options will be populated here -->
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="bulk-stock-tickers" class="form-label">Stock Tickers *</label>
                        <textarea class="form-control" id="bulk-stock-tickers" rows="5" 
                                  placeholder="Enter stock tickers separated by commas or new lines&#10;Example: AAPL, MSFT, GOOGL, TSLA" required></textarea>
                    </div>
                    <div class="bulk-options">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="bulk-price-alerts">
                            <label class="form-check-label" for="bulk-price-alerts">
                                Enable price alerts for all stocks
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="bulk-news-alerts">
                            <label class="form-check-label" for="bulk-news-alerts">
                                Enable news alerts for all stocks
                            </label>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="bulk-add-submit-btn">Add Stocks</button>
            </div>
        </div>
    </div>
</div>

<!-- Watchlist Detail Modal -->
<div class="modal fade" id="watchlistDetailModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="watchlist-detail-title">Watchlist Details</h5>
                <div class="modal-header-actions">
                    <button type="button" class="btn btn-sm btn-outline-primary" id="export-csv-btn">
                        <i class="fas fa-download"></i> Export CSV
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-success" id="export-json-btn">
                        <i class="fas fa-download"></i> Export JSON
                    </button>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="watchlist-detail-content">
                    <!-- Watchlist details will be loaded here -->
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" id="add-stock-to-watchlist">Add Stock</button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize Enhanced Watchlist functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Watchlist Manager
    const watchlistManager = new WatchlistManager();
    watchlistManager.init();
    
    // Load user watchlists
    watchlistManager.loadWatchlists();
    
    // Set up event listeners
    document.getElementById('create-watchlist-btn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('createWatchlistModal'));
        modal.show();
    });
    
    document.getElementById('import-watchlist-btn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('importWatchlistModal'));
        modal.show();
    });
    
    document.getElementById('bulk-add-stocks-btn').addEventListener('click', function() {
        watchlistManager.populateBulkWatchlistOptions();
        const modal = new bootstrap.Modal(document.getElementById('bulkAddModal'));
        modal.show();
    });
    
    // View and sorting
    document.getElementById('watchlist-view').addEventListener('change', function() {
        watchlistManager.changeView(this.value);
    });
    
    document.getElementById('watchlist-sort').addEventListener('change', function() {
        watchlistManager.sortWatchlists(this.value);
    });
    
    // Form submissions
    document.getElementById('save-watchlist-btn').addEventListener('click', function() {
        watchlistManager.createWatchlist();
    });
    
    document.getElementById('save-stock-btn').addEventListener('click', function() {
        watchlistManager.addStock();
    });
    
    document.getElementById('import-watchlist-btn-submit').addEventListener('click', function() {
        watchlistManager.importWatchlist();
    });
    
    document.getElementById('bulk-add-submit-btn').addEventListener('click', function() {
        watchlistManager.bulkAddStocks();
    });
    
    // File upload previews
    document.getElementById('csv-watchlist-file').addEventListener('change', function() {
        watchlistManager.previewCSVImport(this.files[0]);
    });
    
    document.getElementById('json-watchlist-file').addEventListener('change', function() {
        watchlistManager.previewJSONImport(this.files[0]);
    });
    
    // Stock ticker search
    document.getElementById('stock-ticker-add').addEventListener('input', function() {
        watchlistManager.searchStocks(this.value, 'stock-search-results-add');
    });
    
    // Use current price button
    document.getElementById('use-current-price').addEventListener('click', function() {
        watchlistManager.useCurrentPrice();
    });
    
    // Real-time price updates
    setInterval(function() {
        watchlistManager.updatePrices();
    }, 30000); // Update every 30 seconds
    
    // Auto-save watchlist tabs preferences
    document.addEventListener('shown.bs.tab', function(e) {
        localStorage.setItem('activeWatchlistTab', e.target.id);
    });
});
</script>

<?php get_footer(); ?>