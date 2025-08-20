<?php
/**
 * Template Name: Watchlist Management
 * 
 * User watchlist with categories, notes, and price alerts
 *
 * @package StockScannerPro
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="watchlist-container">
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="container">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">Watchlist</h1>
                    <p class="text-gray-600 mt-2">Track and monitor your favorite stocks</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-primary" id="add-to-watchlist-btn">
                        <i class="fas fa-plus mr-2"></i>
                        Add Stock
                    </button>
                    <button class="btn btn-outline-primary btn-sm" data-action="refresh-watchlist">
                        <i class="fas fa-sync-alt mr-2"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Watchlist Controls -->
        <div class="watchlist-controls mb-6">
            <div class="controls-row">
                <!-- Category Filter -->
                <div class="filter-group">
                    <label for="category-filter" class="filter-label">Category:</label>
                    <select id="category-filter" class="form-select">
                        <option value="">All Categories</option>
                        <option value="default">Default</option>
                        <option value="growth">Growth</option>
                        <option value="dividend">Dividend</option>
                        <option value="tech">Technology</option>
                        <option value="healthcare">Healthcare</option>
                        <option value="finance">Finance</option>
                    </select>
                </div>

                <!-- Sort Options -->
                <div class="filter-group">
                    <label for="sort-watchlist" class="filter-label">Sort by:</label>
                    <select id="sort-watchlist" class="form-select">
                        <option value="ticker">Symbol</option>
                        <option value="company_name">Company</option>
                        <option value="current_price">Current Price</option>
                        <option value="change_percent">% Change</option>
                        <option value="added_date">Date Added</option>
                    </select>
                </div>

                <!-- View Mode -->
                <div class="view-mode-group">
                    <button class="view-mode-btn active" data-view="grid" title="Grid View">
                        <i class="fas fa-th-large"></i>
                    </button>
                    <button class="view-mode-btn" data-view="list" title="List View">
                        <i class="fas fa-list"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Watchlist Items -->
        <div class="watchlist-items-section">
            <div id="watchlist-grid" class="watchlist-grid">
                <!-- Populated by JavaScript -->
            </div>
            
            <div id="watchlist-list" class="watchlist-list" style="display: none;">
                <div class="watchlist-table-container">
                    <table class="watchlist-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Company</th>
                                <th>Category</th>
                                <th class="text-right">Price</th>
                                <th class="text-right">Change</th>
                                <th class="text-right">% Change</th>
                                <th class="text-right">Volume</th>
                                <th>Notes</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="watchlist-tbody">
                            <!-- Populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Empty State -->
            <div id="watchlist-empty" class="empty-state" style="display: none;">
                <div class="empty-state-content">
                    <i class="fas fa-eye empty-state-icon"></i>
                    <h3 class="empty-state-title">No Stocks in Watchlist</h3>
                    <p class="empty-state-description">Add stocks to your watchlist to track their performance and receive alerts.</p>
                    <button class="btn btn-primary" id="add-first-stock-btn">
                        <i class="fas fa-plus mr-2"></i>
                        Add Your First Stock
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add to Watchlist Modal -->
<div class="modal fade" id="addToWatchlistModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add to Watchlist</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="add-to-watchlist-form">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="watchlist-ticker-input" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="watchlist-ticker-input" placeholder="e.g., AAPL" required>
                        <div id="watchlist-ticker-suggestions" class="suggestions-dropdown"></div>
                    </div>
                    <div class="mb-3">
                        <label for="watchlist-category-input" class="form-label">Category</label>
                        <select class="form-select" id="watchlist-category-input">
                            <option value="default">Default</option>
                            <option value="growth">Growth</option>
                            <option value="dividend">Dividend</option>
                            <option value="tech">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="watchlist-notes-input" class="form-label">Notes</label>
                        <textarea class="form-control" id="watchlist-notes-input" rows="3" placeholder="Optional notes about this stock"></textarea>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="create-alert-checkbox">
                            <label class="form-check-label" for="create-alert-checkbox">
                                Create price alert
                            </label>
                        </div>
                    </div>
                    <div id="price-alert-section" style="display: none;">
                        <div class="mb-3">
                            <label for="alert-target-price" class="form-label">Target Price</label>
                            <input type="number" class="form-control" id="alert-target-price" step="0.01">
                        </div>
                        <div class="mb-3">
                            <label for="alert-condition" class="form-label">Alert Condition</label>
                            <select class="form-select" id="alert-condition">
                                <option value="above">Price rises above</option>
                                <option value="below">Price falls below</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add to Watchlist</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Edit Watchlist Item Modal -->
<div class="modal fade" id="editWatchlistModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Watchlist Item</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="edit-watchlist-form">
                <div class="modal-body">
                    <input type="hidden" id="edit-watchlist-id">
                    <div class="mb-3">
                        <label for="edit-watchlist-ticker" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="edit-watchlist-ticker" readonly>
                    </div>
                    <div class="mb-3">
                        <label for="edit-watchlist-category" class="form-label">Category</label>
                        <select class="form-select" id="edit-watchlist-category">
                            <option value="default">Default</option>
                            <option value="growth">Growth</option>
                            <option value="dividend">Dividend</option>
                            <option value="tech">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="edit-watchlist-notes" class="form-label">Notes</label>
                        <textarea class="form-control" id="edit-watchlist-notes" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger" id="delete-watchlist-btn">Remove from Watchlist</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Item</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Stock Details Modal -->
<div class="modal fade" id="stockDetailsModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="stock-details-title">Stock Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="stock-details-content">
                <!-- Populated by JavaScript -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" id="view-full-analysis-btn">View Full Analysis</button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize watchlist when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerWatchlist !== 'undefined') {
        StockScannerWatchlist.init();
    }
});
</script>

<?php get_footer(); ?>