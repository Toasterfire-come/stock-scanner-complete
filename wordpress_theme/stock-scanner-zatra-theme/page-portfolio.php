<?php
/**
 * Template Name: Portfolio
 * 
 * The template for displaying portfolio tracking and analytics
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="portfolio-container">
    <div class="page-header">
        <div class="container">
            <div class="header-content">
                <div class="header-left">
                    <h1 class="page-title">
                        <i class="fas fa-briefcase"></i>
                        My Portfolio
                    </h1>
                    <p class="page-subtitle">Track your investments and analyze performance</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" id="addHoldingBtn">
                        <i class="fas fa-plus"></i>
                        Add Holding
                    </button>
                    <button class="btn btn-secondary" id="exportBtn">
                        <i class="fas fa-download"></i>
                        Export
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="portfolio-content">
        <div class="container">
            <!-- Portfolio Summary -->
            <div class="portfolio-summary">
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="card-icon">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="card-content">
                            <div class="card-value" id="totalValue">$0.00</div>
                            <div class="card-label">Total Value</div>
                            <div class="card-change positive" id="totalChange">+$0.00 (0.00%)</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="card-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="card-content">
                            <div class="card-value" id="todayChange">$0.00</div>
                            <div class="card-label">Today's Change</div>
                            <div class="card-change" id="todayChangePercent">0.00%</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="card-icon">
                            <i class="fas fa-coins"></i>
                        </div>
                        <div class="card-content">
                            <div class="card-value" id="totalCost">$0.00</div>
                            <div class="card-label">Total Cost Basis</div>
                            <div class="card-change neutral" id="averageCost">Avg: $0.00</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="card-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="card-content">
                            <div class="card-value" id="totalReturn">0.00%</div>
                            <div class="card-label">Total Return</div>
                            <div class="card-change" id="annualizedReturn">Annual: 0.00%</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Portfolio Chart -->
            <div class="portfolio-chart-section">
                <div class="chart-header">
                    <h3>Portfolio Performance</h3>
                    <div class="chart-controls">
                        <button class="chart-period active" data-period="1D">1D</button>
                        <button class="chart-period" data-period="1W">1W</button>
                        <button class="chart-period" data-period="1M">1M</button>
                        <button class="chart-period" data-period="3M">3M</button>
                        <button class="chart-period" data-period="1Y">1Y</button>
                        <button class="chart-period" data-period="ALL">ALL</button>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="portfolioChart" width="800" height="400"></canvas>
                </div>
            </div>

            <!-- Holdings Table -->
            <div class="holdings-section">
                <div class="section-header">
                    <h3>Holdings</h3>
                    <div class="holdings-controls">
                        <input type="text" id="holdingsSearch" placeholder="Search holdings..." class="search-input">
                        <select id="holdingsSort" class="sort-select">
                            <option value="symbol">Symbol</option>
                            <option value="value">Market Value</option>
                            <option value="change">Today's Change</option>
                            <option value="return">Total Return</option>
                        </select>
                    </div>
                </div>

                <div class="holdings-table-container">
                    <div class="loading-indicator" id="holdingsLoading">
                        <i class="fas fa-spinner fa-spin"></i>
                        Loading holdings...
                    </div>

                    <div class="holdings-table" id="holdingsTable" style="display: none;">
                        <div class="table-header">
                            <div class="header-cell symbol">Symbol</div>
                            <div class="header-cell shares">Shares</div>
                            <div class="header-cell price">Price</div>
                            <div class="header-cell value">Market Value</div>
                            <div class="header-cell cost">Cost Basis</div>
                            <div class="header-cell change">Today's Change</div>
                            <div class="header-cell return">Total Return</div>
                            <div class="header-cell allocation">Allocation</div>
                            <div class="header-cell actions">Actions</div>
                        </div>
                        <div class="table-body" id="holdingsBody">
                            <!-- Holdings will be populated here -->
                        </div>
                    </div>

                    <div class="empty-portfolio" id="emptyPortfolio" style="display: none;">
                        <div class="empty-icon">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <h3>Your portfolio is empty</h3>
                        <p>Start building your portfolio by adding your first stock holding</p>
                        <button class="btn btn-primary" onclick="document.getElementById('addHoldingBtn').click()">
                            <i class="fas fa-plus"></i>
                            Add Your First Holding
                        </button>
                    </div>
                </div>
            </div>

            <!-- Allocation Chart -->
            <div class="allocation-section">
                <h3>Asset Allocation</h3>
                <div class="allocation-content">
                    <div class="allocation-chart">
                        <canvas id="allocationChart" width="400" height="400"></canvas>
                    </div>
                    <div class="allocation-legend" id="allocationLegend">
                        <!-- Legend items will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add Holding Modal -->
<div class="modal" id="addHoldingModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Add Holding</h3>
            <button class="modal-close" id="modalClose">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <form id="addHoldingForm">
                <div class="form-group">
                    <label for="stockSymbol">Stock Symbol</label>
                    <input type="text" id="stockSymbol" placeholder="e.g., AAPL" class="form-input" required>
                    <div class="stock-suggestions" id="stockSuggestions"></div>
                </div>
                
                <div class="form-group">
                    <label for="shares">Number of Shares</label>
                    <input type="number" id="shares" placeholder="0" class="form-input" step="0.001" min="0" required>
                </div>
                
                <div class="form-group">
                    <label for="purchasePrice">Purchase Price per Share</label>
                    <input type="number" id="purchasePrice" placeholder="0.00" class="form-input" step="0.01" min="0" required>
                </div>
                
                <div class="form-group">
                    <label for="purchaseDate">Purchase Date</label>
                    <input type="date" id="purchaseDate" class="form-input" required>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancelBtn">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-plus"></i>
                        Add Holding
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
.portfolio-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 2rem 0;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0.5rem 0 0 0;
}

.header-actions {
    display: flex;
    gap: 1rem;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
    text-decoration: none;
}

.btn-primary {
    background: rgba(255,255,255,0.2);
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
}

.btn-primary:hover {
    background: rgba(255,255,255,0.3);
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
}

.btn-secondary:hover {
    background: rgba(255,255,255,0.1);
}

.portfolio-content {
    padding: 2rem 0;
}

.portfolio-summary {
    margin-bottom: 2rem;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.summary-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.card-icon {
    background: #3685fb;
    color: white;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.card-content {
    flex: 1;
}

.card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.card-label {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.card-change {
    font-size: 0.9rem;
    font-weight: 600;
}

.card-change.positive { color: #10b981; }
.card-change.negative { color: #ef4444; }
.card-change.neutral { color: #6b7280; }

.portfolio-chart-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.chart-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.chart-controls {
    display: flex;
    gap: 0.5rem;
}

.chart-period {
    padding: 0.5rem 1rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
}

.chart-period:hover,
.chart-period.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.chart-container {
    height: 400px;
    position: relative;
}

.holdings-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.holdings-controls {
    display: flex;
    gap: 1rem;
}

.search-input {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    outline: none;
}

.search-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.sort-select {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    outline: none;
}

.holdings-table-container {
    min-height: 200px;
}

.loading-indicator {
    text-align: center;
    padding: 3rem;
    color: #666;
    font-size: 1.1rem;
}

.holdings-table {
    width: 100%;
}

.table-header {
    background: #f8f9fa;
    display: grid;
    grid-template-columns: 100px 80px 100px 120px 120px 120px 120px 100px 100px;
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

.holding-row {
    display: grid;
    grid-template-columns: 100px 80px 100px 120px 120px 120px 120px 100px 100px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
    transition: background 0.2s;
    font-size: 0.9rem;
}

.holding-row:hover {
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

.price-cell, .value-cell, .cost-cell {
    font-weight: 600;
    color: #1a1a1a;
}

.change-cell, .return-cell {
    font-weight: 600;
}

.change-cell.positive, .return-cell.positive { color: #10b981; }
.change-cell.negative, .return-cell.negative { color: #ef4444; }

.allocation-cell {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.allocation-bar {
    flex: 1;
    height: 6px;
    background: #e1e5e9;
    border-radius: 3px;
    overflow: hidden;
}

.allocation-fill {
    height: 100%;
    background: #3685fb;
    transition: width 0.3s ease;
}

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

.action-btn.remove:hover {
    color: #ef4444;
}

.empty-portfolio {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
}

.empty-icon {
    font-size: 4rem;
    color: #ddd;
    margin-bottom: 1rem;
}

.empty-portfolio h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.empty-portfolio p {
    margin: 0 0 2rem 0;
}

.allocation-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.allocation-section h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.allocation-content {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    align-items: center;
}

.allocation-chart {
    position: relative;
    height: 400px;
}

.allocation-legend {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.legend-color {
    width: 20px;
    height: 20px;
    border-radius: 4px;
}

.legend-info {
    flex: 1;
}

.legend-symbol {
    font-weight: 700;
    color: #333;
}

.legend-percentage {
    color: #666;
    font-size: 0.9rem;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    justify-content: center;
    align-items: center;
}

.modal.active {
    display: flex;
}

.modal-content {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e1e5e9;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    color: #666;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
}

.modal-close:hover {
    background: #f0f0f0;
}

.modal-body {
    padding: 1.5rem;
}

.form-group {
    margin-bottom: 1.5rem;
    position: relative;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
}

.form-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    box-sizing: border-box;
}

.form-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.stock-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #e1e5e9;
    border-top: none;
    border-radius: 0 0 8px 8px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10;
    display: none;
}

.suggestion-item {
    padding: 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
}

.suggestion-item:hover {
    background: #f8f9fa;
}

.suggestion-item:last-child {
    border-bottom: none;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

@media (max-width: 1200px) {
    .allocation-content {
        grid-template-columns: 1fr;
        text-align: center;
    }
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .summary-cards {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }
    
    .chart-controls {
        flex-wrap: wrap;
    }
    
    .holdings-controls {
        flex-direction: column;
    }
    
    .table-header,
    .holding-row {
        grid-template-columns: repeat(4, 1fr);
        font-size: 0.8rem;
    }
    
    .header-cell:nth-child(n+5),
    .holding-row > *:nth-child(n+5) {
        display: none;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializePortfolio();
    loadPortfolioData();
    setupEventListeners();
});

function initializePortfolio() {
    const addHoldingBtn = document.getElementById('addHoldingBtn');
    const modal = document.getElementById('addHoldingModal');
    const modalClose = document.getElementById('modalClose');
    const cancelBtn = document.getElementById('cancelBtn');
    
    addHoldingBtn.addEventListener('click', () => modal.classList.add('active'));
    modalClose.addEventListener('click', () => modal.classList.remove('active'));
    cancelBtn.addEventListener('click', () => modal.classList.remove('active'));
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    // Set default date to today
    document.getElementById('purchaseDate').valueAsDate = new Date();
}

function setupEventListeners() {
    // Chart period buttons
    document.querySelectorAll('.chart-period').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.chart-period').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updatePortfolioChart(this.dataset.period);
        });
    });
    
    // Add holding form
    document.getElementById('addHoldingForm').addEventListener('submit', handleAddHolding);
    
    // Stock symbol suggestions
    document.getElementById('stockSymbol').addEventListener('input', showStockSuggestions);
    
    // Search and sort
    document.getElementById('holdingsSearch').addEventListener('input', filterHoldings);
    document.getElementById('holdingsSort').addEventListener('change', sortHoldings);
    
    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportPortfolio);
}

function loadPortfolioData() {
    const loadingIndicator = document.getElementById('holdingsLoading');
    const holdingsTable = document.getElementById('holdingsTable');
    const emptyPortfolio = document.getElementById('emptyPortfolio');
    
    loadingIndicator.style.display = 'block';
    holdingsTable.style.display = 'none';
    emptyPortfolio.style.display = 'none';
    
    // Simulate loading delay
    getPortfolioData()
        .then(portfolioData => {
            const holdings = Array.isArray(portfolioData.holdings) ? portfolioData.holdings : [];
            if (holdings.length === 0) {
                loadingIndicator.style.display = 'none';
                emptyPortfolio.style.display = 'block';
            } else {
                updatePortfolioSummary(portfolioData);
                displayHoldings(holdings);
                updateAllocationChart(holdings);
                updatePortfolioChart('1D');
                loadingIndicator.style.display = 'none';
                holdingsTable.style.display = 'block';
            }
        })
        .catch(err => {
            console.error('Portfolio error:', err);
            loadingIndicator.style.display = 'none';
            emptyPortfolio.style.display = 'block';
        });
}

function getPortfolioData() {
    const params = new URLSearchParams();
    params.append('action', 'get_formatted_portfolio_data');
    params.append('nonce', (window.stockScannerAjax && stockScannerAjax.nonce) || '');
    return fetch((window.stockScannerAjax && stockScannerAjax.ajaxurl) || '/wp-admin/admin-ajax.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params
    })
    .then(res => res.json())
    .then(res => {
        if (!res || !res.success) throw new Error(res && res.data ? res.data : 'Failed to load portfolio');
        return res.data || {};
    });
}

function updatePortfolioSummary(data) {
    document.getElementById('totalValue').textContent = '$' + data.totalValue.toLocaleString('en-US', {minimumFractionDigits: 2});
    document.getElementById('totalCost').textContent = '$' + data.totalCost.toLocaleString('en-US', {minimumFractionDigits: 2});
    
    const todayChangeElement = document.getElementById('todayChange');
    const todayChangePercentElement = document.getElementById('todayChangePercent');
    todayChangeElement.textContent = (data.todayChange >= 0 ? '+$' : '-$') + Math.abs(data.todayChange).toLocaleString('en-US', {minimumFractionDigits: 2});
    
    const todayChangePercent = (data.todayChange / (data.totalValue - data.todayChange)) * 100;
    todayChangePercentElement.textContent = (todayChangePercent >= 0 ? '+' : '') + todayChangePercent.toFixed(2) + '%';
    todayChangePercentElement.className = 'card-change ' + (todayChangePercent >= 0 ? 'positive' : 'negative');
    
    const totalReturnElement = document.getElementById('totalReturn');
    totalReturnElement.textContent = data.totalReturn.toFixed(2) + '%';
    totalReturnElement.className = 'card-value ' + (data.totalReturn >= 0 ? 'positive' : 'negative');
    
    const totalChangeAmount = data.totalValue - data.totalCost;
    const totalChangePercent = (totalChangeAmount / data.totalCost) * 100;
    const totalChangeElement = document.getElementById('totalChange');
    totalChangeElement.textContent = (totalChangeAmount >= 0 ? '+$' : '-$') + Math.abs(totalChangeAmount).toLocaleString('en-US', {minimumFractionDigits: 2}) + 
                                   ' (' + (totalChangePercent >= 0 ? '+' : '') + totalChangePercent.toFixed(2) + '%)';
    totalChangeElement.className = 'card-change ' + (totalChangeAmount >= 0 ? 'positive' : 'negative');
}

function displayHoldings(holdings) {
    const tbody = document.getElementById('holdingsBody');
    
    tbody.innerHTML = holdings.map(holding => {
        const todayChangeClass = holding.todayChange >= 0 ? 'positive' : 'negative';
        const todayChangeSymbol = holding.todayChange >= 0 ? '+' : '';
        const returnClass = holding.totalReturn >= 0 ? 'positive' : 'negative';
        const returnSymbol = holding.totalReturn >= 0 ? '+' : '';
        
        return `
            <div class="holding-row">
                <div class="symbol-cell" onclick="viewStock('${holding.symbol}')">${holding.symbol}</div>
                <div class="shares-cell">${holding.shares}</div>
                <div class="price-cell">$${holding.currentPrice.toFixed(2)}</div>
                <div class="value-cell">$${holding.marketValue.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                <div class="cost-cell">$${holding.costBasis.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                <div class="change-cell ${todayChangeClass}">
                    ${todayChangeSymbol}$${Math.abs(holding.todayChange).toFixed(2)} (${todayChangeSymbol}${holding.todayChangePercent.toFixed(2)}%)
                </div>
                <div class="return-cell ${returnClass}">
                    ${returnSymbol}${holding.totalReturn.toFixed(2)}%
                </div>
                <div class="allocation-cell">
                    <span>${holding.allocation.toFixed(1)}%</span>
                    <div class="allocation-bar">
                        <div class="allocation-fill" style="width: ${holding.allocation}%"></div>
                    </div>
                </div>
                <div class="actions-cell">
                    <button class="action-btn" onclick="editHolding('${holding.symbol}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn remove" onclick="removeHolding('${holding.symbol}')" title="Remove">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updatePortfolioChart(period) {
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    
    // Generate sample data based on period
    const data = generateChartData(period);
    
    // Destroy existing chart if it exists
    if (window.portfolioChart) {
        window.portfolioChart.destroy();
    }
    
    window.portfolioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Portfolio Value',
                data: data.values,
                borderColor: '#3685fb',
                backgroundColor: 'rgba(54, 133, 251, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateAllocationChart(holdings) {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    
    const colors = ['#3685fb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'];
    
    const data = holdings.map(holding => holding.allocation);
    const labels = holdings.map(holding => holding.symbol);
    
    if (window.allocationChart) {
        window.allocationChart.destroy();
    }
    
    window.allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, holdings.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Update legend
    updateAllocationLegend(holdings, colors);
}

function updateAllocationLegend(holdings, colors) {
    const legend = document.getElementById('allocationLegend');
    
    legend.innerHTML = holdings.map((holding, index) => `
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${colors[index]}"></div>
            <div class="legend-info">
                <div class="legend-symbol">${holding.symbol}</div>
                <div class="legend-percentage">${holding.allocation.toFixed(1)}% • $${holding.marketValue.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
            </div>
        </div>
    `).join('');
}

function generateChartData(period) {
    // Generate sample portfolio performance data
    const baseValue = 125430.67;
    const points = period === '1D' ? 24 : period === '1W' ? 7 : period === '1M' ? 30 : period === '3M' ? 90 : 365;
    
    const labels = [];
    const values = [];
    
    for (let i = 0; i < points; i++) {
        if (period === '1D') {
            labels.push(i + ':00');
        } else {
            const date = new Date();
            date.setDate(date.getDate() - (points - i));
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        const variation = (Math.random() - 0.5) * 5000;
        values.push(baseValue + variation);
    }
    
    return { labels, values };
}

function showStockSuggestions() {
    // Implementation similar to other pages
    console.log('Showing stock suggestions...');
}

function handleAddHolding(e) {
    e.preventDefault();
    console.log('Adding holding...');
    
    // Close modal and refresh
    document.getElementById('addHoldingModal').classList.remove('active');
    document.getElementById('addHoldingForm').reset();
    
    showNotification('Holding added successfully!', 'success');
    setTimeout(loadPortfolioData, 500);
}

function editHolding(symbol) {
    console.log('Editing holding:', symbol);
}

function removeHolding(symbol) {
    if (confirm(`Remove ${symbol} from your portfolio?`)) {
        console.log('Removing holding:', symbol);
        showNotification(`${symbol} removed from portfolio!`, 'info');
        setTimeout(loadPortfolioData, 500);
    }
}

function viewStock(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
}

function filterHoldings() {
    // Implementation for filtering holdings
    console.log('Filtering holdings...');
}

function sortHoldings() {
    // Implementation for sorting holdings
    console.log('Sorting holdings...');
}

function exportPortfolio() {
    console.log('Exporting portfolio...');
    showNotification('Portfolio export coming soon!', 'info');
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