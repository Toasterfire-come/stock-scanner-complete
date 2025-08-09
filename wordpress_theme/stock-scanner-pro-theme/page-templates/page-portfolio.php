<?php
/**
 * Template Name: Portfolio Management
 * Description: Complete portfolio management interface with performance analytics
 */

// Security check - require user authentication
if (!is_user_logged_in()) {
    wp_redirect(wp_registration_url());
    exit;
}

g et_header(); ?>

<div class="portfolio-management-container">
    <div class="container">
        <div class="page-header">
            <h1>📈 My Portfolios</h1>
            <p class="page-description">Create portfolios, add holdings, and track performance in real time</p>
        </div>

        <!-- Portfolio Actions Bar -->
        <div class="portfolio-actions-bar panel">
            <button class="btn btn-primary" id="create-portfolio-btn">
                <i class="fas fa-plus"></i> Create Portfolio
            </button>
            <button class="btn btn-secondary" id="import-csv-btn">
                <i class="fas fa-upload"></i> Import from CSV
            </button>
            <button class="btn btn-outline" id="view-roi-analytics-btn">
                <i class="fas fa-chart-line"></i> ROI Analytics
            </button>
            <div class="portfolio-filters">
                <select id="portfolio-sort" class="form-select">
                    <option value="created">Sort by Created Date</option>
                    <option value="performance">Sort by Performance</option>
                    <option value="value">Sort by Total Value</option>
                    <option value="name">Sort by Name</option>
                </select>
            </div>
        </div>

        <!-- Portfolio Grid -->
        <div class="row" id="portfolios-grid">
            <div class="col-12">
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <p>Loading your portfolios...</p>
                </div>
            </div>
        </div>

        <!-- Portfolio Performance Summary -->
        <div class="mt-6">
            <div class="performance-summary-card card">
                <h3>Overall Portfolio Performance</h3>
                <div class="row" id="overall-performance"></div>
            </div>
        </div>
    </div>
</div>

<!-- Create Portfolio Modal -->
<div class="modal fade" id="createPortfolioModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Create New Portfolio</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="create-portfolio-form">
                    <div class="mb-3">
                        <label for="portfolio-name" class="form-label">Portfolio Name *</label>
                        <input type="text" class="form-control" id="portfolio-name" required>
                    </div>
                    <div class="mb-3">
                        <label for="portfolio-description" class="form-label">Description</label>
                        <textarea class="form-control" id="portfolio-description" rows="3"></textarea>
                    </div>
                    <div class="mb-3 form-check">
                        <input class="form-check-input" type="checkbox" id="portfolio-public">
                        <label class="form-check-label" for="portfolio-public">
                            Make portfolio public (visible to other users)
                        </label>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-portfolio-btn">Create Portfolio</button>
            </div>
        </div>
    </div>
</div>

<!-- Add Holding Modal -->
<div class="modal fade" id="addHoldingModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add Stock Holding</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="add-holding-form">
                    <input type="hidden" id="holding-portfolio-id">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="stock-ticker" class="form-label">Stock Ticker *</label>
                                <input type="text" class="form-control" id="stock-ticker" placeholder="e.g., AAPL" required>
                                <div class="stock-search-results" id="stock-search-results"></div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="shares-amount" class="form-label">Number of Shares *</label>
                                <input type="number" class="form-control" id="shares-amount" step="0.0001" min="0.0001" required>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="average-cost" class="form-label">Average Cost per Share *</label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" id="average-cost" step="0.01" min="0.01" required>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="current-price" class="form-label">Current Price (optional)</label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" id="current-price" step="0.01" min="0.01">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="alert-source" class="form-label">Alert Source (if applicable)</label>
                        <select class="form-select" id="alert-source">
                            <option value="">Manual Entry</option>
                        </select>
                    </div>
                    <div class="holding-preview" id="holding-preview" style="display: none;">
                        <h6>Holding Preview</h6>
                        <div class="preview-details"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-holding-btn">Add Holding</button>
            </div>
        </div>
    </div>
</div>

<!-- Import CSV Modal -->
<div class="modal fade" id="importCsvModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Import Portfolio from CSV</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="import-instructions mb-4">
                    <h6>CSV Format Requirements:</h6>
                    <p>Your CSV file should include the following columns:</p>
                    <code>ticker,shares,average_cost,current_price</code>
                    <p class="mt-2">Example:</p>
                    <code>AAPL,100,150.00,165.00<br>MSFT,50,200.00,210.00</code>
                </div>
                <form id="import-csv-form">
                    <div class="mb-3">
                        <label for="import-portfolio-name" class="form-label">Portfolio Name *</label>
                        <input type="text" class="form-control" id="import-portfolio-name" required>
                    </div>
                    <div class="mb-3">
                        <label for="csv-file" class="form-label">CSV File *</label>
                        <input type="file" class="form-control" id="csv-file" accept=".csv" required>
                    </div>
                    <div class="import-preview" id="import-preview" style="display: none;">
                        <h6>Import Preview</h6>
                        <div class="preview-table"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-secondary" id="import-csv-btn-submit">Import Portfolio</button>
            </div>
        </div>
    </div>
</div>

<!-- ROI Analytics Modal -->
<div class="modal fade" id="roiAnalyticsModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Alert-Based ROI Analytics</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="roi-analytics-content"></div>
            </div>
        </div>
    </div>
</div>

<!-- Portfolio Detail Modal -->
<div class="modal fade" id="portfolioDetailModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="portfolio-detail-title">Portfolio Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="portfolio-detail-content"></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" id="add-holding-to-portfolio">Add Holding</button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize Portfolio Management functionality
document.addEventListener('DOMContentLoaded', function() {
    const portfolioManager = new PortfolioManager();
    portfolioManager.init();

    document.getElementById('create-portfolio-btn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('createPortfolioModal'));
        modal.show();
    });

    document.getElementById('import-csv-btn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('importCsvModal'));
        modal.show();
    });

    document.getElementById('view-roi-analytics-btn').addEventListener('click', function() {
        portfolioManager.loadROIAnalytics();
        const modal = new bootstrap.Modal(document.getElementById('roiAnalyticsModal'));
        modal.show();
    });

    document.getElementById('portfolio-sort').addEventListener('change', function() {
        portfolioManager.sortPortfolios(this.value);
    });

    document.getElementById('save-portfolio-btn').addEventListener('click', function() {
        portfolioManager.createPortfolio();
    });

    document.getElementById('save-holding-btn').addEventListener('click', function() {
        portfolioManager.addHolding();
    });
});
</script>

<?php get_footer(); ?>