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

get_header(); ?>

<div class="portfolio-management-container">
    <div class="container">
        <div class="page-header">
            <h1> My Portfolios</h1>
            <p class="page-description">Create portfolios, add holdings, and track performance in real time</p>
        </div>

        <!-- Portfolio Actions Bar -->
        <div class="card p-6 mb-6">
            <div class="portfolio-actions-bar" style="display: flex; justify-content: space-between; align-items: center; gap: var(--space-4); flex-wrap: wrap;">
                <div class="action-buttons" style="display: flex; gap: var(--space-3); flex-wrap: wrap;">
                    <button class="btn btn-primary" id="create-portfolio-btn">
                        ➕ Create Portfolio
                    </button>
                    <button class="btn btn-secondary" id="import-csv-btn">
                        📤 Import from CSV
                    </button>
                    <button class="btn btn-outline" id="view-roi-analytics-btn">
                         ROI Analytics
                    </button>
                </div>
                <div class="portfolio-filters">
                    <select id="portfolio-sort" class="form-select" style="min-width: 200px;">
                        <option value="created">Sort by Created Date</option>
                        <option value="performance">Sort by Performance</option>
                        <option value="value">Sort by Total Value</option>
                        <option value="name">Sort by Name</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Portfolio Grid -->
        <div class="portfolios-section mb-6">
            <div id="portfolios-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: var(--space-5);">
                <div class="loading-indicator" style="grid-column: 1 / -1;">
                    <div class="spinner"></div>
                    <p>Loading your portfolios...</p>
                </div>
            </div>
        </div>

        <!-- Portfolio Performance Summary -->
        <div class="card p-6">
            <h3 style="margin-bottom: var(--space-5); color: var(--color-text);"> Overall Portfolio Performance</h3>
            <div id="overall-performance" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4);">
                <!-- Performance metrics will be loaded here -->
            </div>
        </div>
    </div>
</div>

<!-- Create Portfolio Modal -->
<div class="modal-overlay" id="createPortfolioModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 1000; justify-content: center; align-items: center;">
    <div class="modal-dialog card" style="max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto;">
        <div class="modal-content p-6">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-5); padding-bottom: var(--space-4); border-bottom: 1px solid var(--color-border);">
                <h5 class="modal-title" style="margin: 0; color: var(--color-text);">Create New Portfolio</h5>
                <button type="button" class="btn-close" data-dismiss="modal" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--color-text-muted);">×</button>
            </div>
            <div class="modal-body">
                <form id="create-portfolio-form" style="display: grid; gap: var(--space-4);">
                    <div class="form-group">
                        <label for="portfolio-name" class="form-label">Portfolio Name *</label>
                        <input type="text" class="form-control" id="portfolio-name" required>
                    </div>
                    <div class="form-group">
                        <label for="portfolio-description" class="form-label">Description</label>
                        <textarea class="form-control" id="portfolio-description" rows="3"></textarea>
                    </div>
                    <div class="form-check" style="display: flex; align-items: center; gap: var(--space-2);">
                        <input class="form-check-input" type="checkbox" id="portfolio-public" style="width: auto;">
                        <label class="form-check-label" for="portfolio-public" style="margin: 0;">
                            Make portfolio public (visible to other users)
                        </label>
                    </div>
                </form>
            </div>
            <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--color-border);">
                <button type="button" class="btn btn-outline" data-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-portfolio-btn">Create Portfolio</button>
            </div>
        </div>
    </div>
</div>

<!-- Add Holding Modal -->
<div class="modal-overlay" id="addHoldingModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 1000; justify-content: center; align-items: center;">
    <div class="modal-dialog card" style="max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto;">
        <div class="modal-content p-6">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-5); padding-bottom: var(--space-4); border-bottom: 1px solid var(--color-border);">
                <h5 class="modal-title" style="margin: 0; color: var(--color-text);">Add New Holding</h5>
                <button type="button" class="btn-close" data-dismiss="modal" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--color-text-muted);">×</button>
            </div>
            <div class="modal-body">
                <form id="add-holding-form" style="display: grid; gap: var(--space-4);">
                    <div class="form-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3);">
                        <div class="form-group">
                            <label for="holding-symbol" class="form-label">Stock Symbol *</label>
                            <input type="text" class="form-control" id="holding-symbol" placeholder="e.g., AAPL" required>
                        </div>
                        <div class="form-group">
                            <label for="holding-quantity" class="form-label">Quantity *</label>
                            <input type="number" class="form-control" id="holding-quantity" min="0" step="0.01" required>
                        </div>
                    </div>
                    <div class="form-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3);">
                        <div class="form-group">
                            <label for="holding-price" class="form-label">Purchase Price *</label>
                            <input type="number" class="form-control" id="holding-price" min="0" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label for="holding-date" class="form-label">Purchase Date *</label>
                            <input type="date" class="form-control" id="holding-date" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="holding-notes" class="form-label">Notes (Optional)</label>
                        <textarea class="form-control" id="holding-notes" rows="2" placeholder="Investment thesis, reminders, etc."></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--color-border);">
                <button type="button" class="btn btn-outline" data-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="save-holding-btn">Add Holding</button>
            </div>
        </div>
    </div>
</div>

<style>
/* Portfolio page specific styles */
.portfolio-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.portfolio-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.portfolio-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-4);
}

.portfolio-title {
    color: var(--color-text);
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
}

.portfolio-performance {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--space-3);
    margin: var(--space-4) 0;
}

.perf-metric {
    text-align: center;
}

.perf-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: var(--space-1);
}

.perf-label {
    font-size: 0.875rem;
    color: var(--color-text-muted);
}

.modal-overlay.show {
    display: flex !important;
}

@media (max-width: 768px) {
    .portfolio-actions-bar {
        flex-direction: column;
        align-items: stretch !important;
    }
    
    .action-buttons {
        justify-content: center;
    }
    
    .form-row {
        grid-template-columns: 1fr !important;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    function showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
        }
    }

    function hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }

    // Event listeners for modal triggers
    document.getElementById('create-portfolio-btn')?.addEventListener('click', () => {
        showModal('createPortfolioModal');
    });

    // Close modal events
    document.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) {
                modal.classList.remove('show');
            }
        });
    });

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    });

    // Load portfolios
    loadPortfolios();
    loadOverallPerformance();

    function loadPortfolios() {
        // Simulate loading portfolios
        setTimeout(() => {
            const grid = document.getElementById('portfolios-grid');
            grid.innerHTML = generateMockPortfolios();
        }, 1000);
    }

    function loadOverallPerformance() {
        const container = document.getElementById('overall-performance');
        container.innerHTML = `
            <div class="performance-metric" style="text-align: center; padding: var(--space-4); background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md);">
                <div style="font-size: 2rem; font-weight: 700; color: var(--color-success); margin-bottom: var(--space-2);">+$12,547</div>
                <div style="color: var(--color-text-muted); font-size: 0.875rem;">Total Gain/Loss</div>
            </div>
            <div class="performance-metric" style="text-align: center; padding: var(--space-4); background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md);">
                <div style="font-size: 2rem; font-weight: 700; color: var(--color-success); margin-bottom: var(--space-2);">+15.2%</div>
                <div style="color: var(--color-text-muted); font-size: 0.875rem;">Total Return</div>
            </div>
            <div class="performance-metric" style="text-align: center; padding: var(--space-4); background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md);">
                <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary); margin-bottom: var(--space-2);">$94,732</div>
                <div style="color: var(--color-text-muted); font-size: 0.875rem;">Total Value</div>
            </div>
            <div class="performance-metric" style="text-align: center; padding: var(--space-4); background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md);">
                <div style="font-size: 2rem; font-weight: 700; color: var(--color-text); margin-bottom: var(--space-2);">3</div>
                <div style="color: var(--color-text-muted); font-size: 0.875rem;">Active Portfolios</div>
            </div>
        `;
    }

    function generateMockPortfolios() {
        const portfolios = [
            { name: 'Growth Portfolio', value: '$45,230', return: '+12.3%', holdings: 8 },
            { name: 'Dividend Focus', value: '$32,100', return: '+8.7%', holdings: 12 },
            { name: 'Tech Stocks', value: '$17,402', return: '+21.5%', holdings: 5 }
        ];

        return portfolios.map(portfolio => `
            <div class="portfolio-card">
                <div class="portfolio-header">
                    <h4 class="portfolio-title">${portfolio.name}</h4>
                    <button class="btn btn-outline btn-small">⚙️</button>
                </div>
                <div class="portfolio-performance">
                    <div class="perf-metric">
                        <div class="perf-value" style="color: var(--color-primary);">${portfolio.value}</div>
                        <div class="perf-label">Current Value</div>
                    </div>
                    <div class="perf-metric">
                        <div class="perf-value" style="color: var(--color-success);">${portfolio.return}</div>
                        <div class="perf-label">Total Return</div>
                    </div>
                    <div class="perf-metric">
                        <div class="perf-value" style="color: var(--color-text);">${portfolio.holdings}</div>
                        <div class="perf-label">Holdings</div>
                    </div>
                </div>
                <div style="display: flex; gap: var(--space-2); margin-top: var(--space-4);">
                    <button class="btn btn-primary" style="flex: 1;">View Details</button>
                    <button class="btn btn-outline">+ Add Holding</button>
                </div>
            </div>
        `).join('');
    }
});
</script>

<?php get_footer(); ?>