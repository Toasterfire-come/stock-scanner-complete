<?php
/**
 * Template Name: Portfolio Management
 * 
 * Portfolio management with holdings, performance, and analytics
 *
 * @package StockScannerPro
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="portfolio-container">
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="container">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">Portfolio</h1>
                    <p class="text-gray-600 mt-2">Manage your investment portfolio</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-primary" id="add-stock-btn">
                        <i class="fas fa-plus mr-2"></i>
                        Add Stock
                    </button>
                    <button class="btn btn-outline-primary btn-sm" data-action="refresh-portfolio">
                        <i class="fas fa-sync-alt mr-2"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Portfolio Summary -->
        <div class="portfolio-summary-section mb-8">
            <div class="summary-cards-grid">
                <div class="summary-card">
                    <div class="summary-card-content">
                        <div class="summary-value" id="total-portfolio-value">$0.00</div>
                        <div class="summary-label">Total Value</div>
                    </div>
                    <div class="summary-icon">
                        <i class="fas fa-wallet text-primary"></i>
                    </div>
                </div>

                <div class="summary-card">
                    <div class="summary-card-content">
                        <div class="summary-value" id="total-return">$0.00</div>
                        <div class="summary-label">Total Return</div>
                        <div class="summary-change" id="total-return-percent">0.00%</div>
                    </div>
                    <div class="summary-icon">
                        <i class="fas fa-chart-line text-success"></i>
                    </div>
                </div>

                <div class="summary-card">
                    <div class="summary-card-content">
                        <div class="summary-value" id="day-change">$0.00</div>
                        <div class="summary-label">Today's Change</div>
                        <div class="summary-change" id="day-change-percent">0.00%</div>
                    </div>
                    <div class="summary-icon">
                        <i class="fas fa-calendar-day text-info"></i>
                    </div>
                </div>

                <div class="summary-card">
                    <div class="summary-card-content">
                        <div class="summary-value" id="holdings-count">0</div>
                        <div class="summary-label">Holdings</div>
                    </div>
                    <div class="summary-icon">
                        <i class="fas fa-layer-group text-purple"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Portfolio Performance Chart -->
        <div class="portfolio-chart-section mb-8">
            <div class="chart-card">
                <div class="chart-card-header">
                    <h3 class="chart-title">Portfolio Performance</h3>
                    <div class="chart-controls">
                        <div class="timeframe-buttons">
                            <button class="timeframe-btn active" data-period="1mo">1M</button>
                            <button class="timeframe-btn" data-period="3mo">3M</button>
                            <button class="timeframe-btn" data-period="6mo">6M</button>
                            <button class="timeframe-btn" data-period="1y">1Y</button>
                            <button class="timeframe-btn" data-period="all">All</button>
                        </div>
                    </div>
                </div>
                <div class="chart-card-body">
                    <canvas id="portfolio-performance-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Holdings Table -->
        <div class="holdings-section mb-8">
            <div class="holdings-card">
                <div class="holdings-card-header">
                    <h3 class="holdings-title">Holdings</h3>
                    <div class="holdings-controls">
                        <div class="sort-dropdown">
                            <select id="sort-holdings" class="form-select">
                                <option value="ticker">Symbol</option>
                                <option value="company_name">Company</option>
                                <option value="current_value">Current Value</option>
                                <option value="return_percent">Return %</option>
                                <option value="day_change_percent">Day Change %</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="holdings-card-body">
                    <div class="holdings-table-container">
                        <table class="holdings-table" id="holdings-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Company</th>
                                    <th class="text-right">Shares</th>
                                    <th class="text-right">Avg Cost</th>
                                    <th class="text-right">Current Price</th>
                                    <th class="text-right">Market Value</th>
                                    <th class="text-right">Gain/Loss</th>
                                    <th class="text-right">Return %</th>
                                    <th class="text-right">Day Change</th>
                                    <th class="text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="holdings-tbody">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Portfolio Analytics -->
        <div class="portfolio-analytics-section">
            <div class="analytics-grid">
                <!-- Allocation Chart -->
                <div class="allocation-card">
                    <div class="allocation-card-header">
                        <h3 class="allocation-title">Asset Allocation</h3>
                    </div>
                    <div class="allocation-card-body">
                        <canvas id="allocation-chart"></canvas>
                    </div>
                </div>

                <!-- Performance Metrics -->
                <div class="metrics-card">
                    <div class="metrics-card-header">
                        <h3 class="metrics-title">Performance Metrics</h3>
                    </div>
                    <div class="metrics-card-body" id="performance-metrics">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add Stock Modal -->
<div class="modal fade" id="addStockModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add Stock to Portfolio</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="add-stock-form">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="stock-ticker" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="stock-ticker" placeholder="e.g., AAPL" required>
                        <div id="ticker-suggestions" class="suggestions-dropdown"></div>
                    </div>
                    <div class="mb-3">
                        <label for="stock-shares" class="form-label">Number of Shares</label>
                        <input type="number" class="form-control" id="stock-shares" step="0.01" min="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="stock-cost-basis" class="form-label">Cost Basis per Share</label>
                        <input type="number" class="form-control" id="stock-cost-basis" step="0.01" min="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="stock-purchase-date" class="form-label">Purchase Date</label>
                        <input type="date" class="form-control" id="stock-purchase-date" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add Stock</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Edit Holding Modal -->
<div class="modal fade" id="editHoldingModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Holding</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="edit-holding-form">
                <div class="modal-body">
                    <input type="hidden" id="edit-holding-id">
                    <div class="mb-3">
                        <label for="edit-stock-ticker" class="form-label">Stock Symbol</label>
                        <input type="text" class="form-control" id="edit-stock-ticker" readonly>
                    </div>
                    <div class="mb-3">
                        <label for="edit-stock-shares" class="form-label">Number of Shares</label>
                        <input type="number" class="form-control" id="edit-stock-shares" step="0.01" min="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit-stock-cost-basis" class="form-label">Cost Basis per Share</label>
                        <input type="number" class="form-control" id="edit-stock-cost-basis" step="0.01" min="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit-stock-purchase-date" class="form-label">Purchase Date</label>
                        <input type="date" class="form-control" id="edit-stock-purchase-date" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger" id="delete-holding-btn">Delete Holding</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Holding</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
// Initialize portfolio when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerPortfolio !== 'undefined') {
        StockScannerPortfolio.init();
    }
});
</script>

<?php get_footer(); ?>