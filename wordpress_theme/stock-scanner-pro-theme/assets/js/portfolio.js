/**
 * Stock Scanner Pro - Portfolio Management Functionality
 */

(function() {
    'use strict';

    const Portfolio = {
        holdings: [],
        portfolioChart: null,
        allocationChart: null,
        refreshInterval: null,

        init: function() {
            this.loadPortfolioData();
            this.initCharts();
            this.bindEvents();
            this.startAutoRefresh();
        },

        // Load portfolio data
        loadPortfolioData: function() {
            StockScannerAPI.Utils.showLoading(document.getElementById('holdings-tbody'), 'Loading portfolio...');
            
            StockScannerAPI.Portfolio.getPortfolio()
                .then(data => {
                    if (data && data.success && data.portfolio) {
                        this.holdings = data.portfolio.holdings;
                        this.updatePortfolioSummary(data.portfolio.summary);
                        this.renderHoldings(data.portfolio.holdings);
                        this.updateAllocationChart(data.portfolio.allocation);
                        this.updatePerformanceMetrics(data.portfolio.performance);
                        this.updatePortfolioChart(data.portfolio.performance);
                    } else {
                        this.showEmptyState();
                    }
                })
                .catch(error => {
                    console.error('Portfolio load error:', error);
                    this.showErrorState();
                })
                .finally(() => {
                    StockScannerAPI.Utils.hideLoading(document.getElementById('holdings-tbody'));
                });
        },

        // Update portfolio summary cards
        updatePortfolioSummary: function(summary) {
            if (!summary) return;

            const totalValueEl = document.getElementById('total-portfolio-value');
            const totalReturnEl = document.getElementById('total-return');
            const totalReturnPercentEl = document.getElementById('total-return-percent');
            const dayChangeEl = document.getElementById('day-change');
            const dayChangePercentEl = document.getElementById('day-change-percent');
            const holdingsCountEl = document.getElementById('holdings-count');

            if (totalValueEl) {
                totalValueEl.textContent = StockScannerAPI.Utils.formatCurrency(summary.total_value || 0);
            }

            if (totalReturnEl) {
                const change = summary.total_gain_loss || 0;
                totalReturnEl.textContent = StockScannerAPI.Utils.formatCurrency(change);
                totalReturnEl.className = 'summary-value ' + StockScannerAPI.Utils.getPriceChangeClass(change);
            }

            if (totalReturnPercentEl) {
                const changePercent = summary.total_gain_loss_percent || 0;
                totalReturnPercentEl.textContent = StockScannerAPI.Utils.formatPercentage(changePercent);
                totalReturnPercentEl.className = 'summary-change ' + StockScannerAPI.Utils.getPriceChangeClass(changePercent);
            }

            if (dayChangeEl) {
                // This would come from today's portfolio change data
                const dayChange = 0; // Placeholder
                dayChangeEl.textContent = StockScannerAPI.Utils.formatCurrency(dayChange);
                dayChangeEl.className = 'summary-value ' + StockScannerAPI.Utils.getPriceChangeClass(dayChange);
            }

            if (holdingsCountEl) {
                holdingsCountEl.textContent = summary.holdings_count || 0;
            }
        },

        // Render holdings table
        renderHoldings: function(holdings) {
            const tbody = document.getElementById('holdings-tbody');
            if (!tbody) return;

            if (!holdings || holdings.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="text-center py-8">
                            <div class="empty-state">
                                <i class="fas fa-wallet empty-state-icon"></i>
                                <h4>No Holdings Found</h4>
                                <p>Add stocks to your portfolio to start tracking performance.</p>
                                <button class="btn btn-primary" id="add-first-stock-btn">
                                    <i class="fas fa-plus mr-2"></i>
                                    Add Your First Stock
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }

            let html = '';
            holdings.forEach((holding, index) => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(holding.gain_loss || 0);
                const dayChangeClass = StockScannerAPI.Utils.getPriceChangeClass(holding.stock_data?.price_change || 0);
                
                html += `
                    <tr data-holding-id="${holding.id}" class="holding-row">
                        <td>
                            <div class="stock-symbol">
                                <strong>${holding.ticker}</strong>
                            </div>
                        </td>
                        <td>
                            <div class="company-name">
                                ${holding.stock_data?.company_name || holding.ticker}
                            </div>
                        </td>
                        <td class="text-right">
                            ${StockScannerAPI.Utils.formatNumber(holding.shares, 4)}
                        </td>
                        <td class="text-right">
                            ${StockScannerAPI.Utils.formatCurrency(holding.average_cost)}
                        </td>
                        <td class="text-right">
                            ${StockScannerAPI.Utils.formatCurrency(holding.current_price)}
                        </td>
                        <td class="text-right">
                            <strong>${StockScannerAPI.Utils.formatCurrency(holding.current_value)}</strong>
                        </td>
                        <td class="text-right ${changeClass}">
                            ${StockScannerAPI.Utils.formatCurrency(holding.gain_loss)}
                        </td>
                        <td class="text-right ${changeClass}">
                            ${StockScannerAPI.Utils.formatPercentage(holding.gain_loss_percent)}
                        </td>
                        <td class="text-right ${dayChangeClass}">
                            ${StockScannerAPI.Utils.formatPercentage(holding.stock_data?.price_change_percent || 0)}
                        </td>
                        <td class="text-center">
                            <div class="holding-actions">
                                <button class="holding-action-btn edit-holding" title="Edit Holding" data-holding-id="${holding.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="holding-action-btn view-details" title="View Details" data-ticker="${holding.ticker}">
                                    <i class="fas fa-chart-line"></i>
                                </button>
                                <button class="holding-action-btn danger remove-holding" title="Remove Holding" data-holding-id="${holding.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        },

        // Initialize charts
        initCharts: function() {
            this.initPortfolioChart();
            this.initAllocationChart();
        },

        // Initialize portfolio performance chart
        initPortfolioChart: function() {
            const canvas = document.getElementById('portfolio-performance-chart');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            
            this.portfolioChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Portfolio Value',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
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
                        x: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        y: {
                            display: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return StockScannerAPI.Utils.formatCurrency(value);
                                }
                            }
                        }
                    }
                }
            });
        },

        // Initialize allocation chart
        initAllocationChart: function() {
            const canvas = document.getElementById('allocation-chart');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            
            this.allocationChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
                            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },

        // Update allocation chart
        updateAllocationChart: function(allocation) {
            if (!this.allocationChart || !allocation || !allocation.by_stock) return;

            const labels = [];
            const data = [];

            allocation.by_stock.forEach(item => {
                labels.push(item.ticker);
                data.push(item.percentage);
            });

            this.allocationChart.data.labels = labels;
            this.allocationChart.data.datasets[0].data = data;
            this.allocationChart.update();
        },

        // Update portfolio performance chart
        updatePortfolioChart: function(performance) {
            if (!this.portfolioChart) return;

            // Generate mock historical data for now
            const labels = [];
            const data = [];
            const currentValue = performance?.current_value || 10000;

            for (let i = 30; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString());
                
                // Generate realistic portfolio value
                const variation = (Math.random() - 0.5) * 0.1;
                const value = currentValue * (1 + variation * (i / 30));
                data.push(Math.max(value, currentValue * 0.8));
            }

            this.portfolioChart.data.labels = labels;
            this.portfolioChart.data.datasets[0].data = data;
            this.portfolioChart.update();
        },

        // Update performance metrics
        updatePerformanceMetrics: function(performance) {
            const container = document.getElementById('performance-metrics');
            if (!container || !performance) return;

            const metrics = [
                { label: 'Total Return', value: StockScannerAPI.Utils.formatCurrency(performance.total_return || 0), class: StockScannerAPI.Utils.getPriceChangeClass(performance.total_return || 0) },
                { label: 'Return %', value: StockScannerAPI.Utils.formatPercentage(performance.total_return_percent || 0), class: StockScannerAPI.Utils.getPriceChangeClass(performance.total_return_percent || 0) },
                { label: 'Invested Amount', value: StockScannerAPI.Utils.formatCurrency(performance.invested_amount || 0), class: '' },
                { label: 'Current Value', value: StockScannerAPI.Utils.formatCurrency(performance.current_value || 0), class: '' },
                { label: 'Average Return', value: StockScannerAPI.Utils.formatPercentage(performance.average_return || 0), class: StockScannerAPI.Utils.getPriceChangeClass(performance.average_return || 0) },
                { label: 'Volatility', value: StockScannerAPI.Utils.formatPercentage(performance.volatility || 0), class: '' }
            ];

            let html = '<div class="performance-metrics">';
            metrics.forEach(metric => {
                html += `
                    <div class="metric-item">
                        <div class="metric-label">${metric.label}</div>
                        <div class="metric-value ${metric.class}">${metric.value}</div>
                    </div>
                `;
            });
            html += '</div>';

            container.innerHTML = html;
        },

        // Show empty state
        showEmptyState: function() {
            const tbody = document.getElementById('holdings-tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="text-center py-8">
                            <div class="portfolio-empty-state">
                                <i class="fas fa-wallet empty-state-icon"></i>
                                <h3 class="empty-state-title">Your Portfolio is Empty</h3>
                                <p class="empty-state-description">Start building your portfolio by adding stocks you own.</p>
                                <button class="btn btn-primary" id="add-first-stock-btn">
                                    <i class="fas fa-plus mr-2"></i>
                                    Add Your First Stock
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }
        },

        // Show error state
        showErrorState: function() {
            const tbody = document.getElementById('holdings-tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="text-center py-8">
                            <div class="error-state">
                                <i class="fas fa-exclamation-triangle error-icon"></i>
                                <h4>Failed to Load Portfolio</h4>
                                <p>Please try refreshing the page or check your connection.</p>
                                <button class="btn btn-primary error-retry" onclick="StockScannerPortfolio.loadPortfolioData()">
                                    <i class="fas fa-retry mr-2"></i>
                                    Try Again
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }
        },

        // Add stock to portfolio
        addStock: function(ticker, shares, costBasis, purchaseDate) {
            return StockScannerAPI.Portfolio.addToPortfolio(ticker, shares, costBasis, purchaseDate)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Stock added to portfolio successfully!', 'success');
                        this.loadPortfolioData(); // Reload portfolio data
                        return data;
                    } else {
                        throw new Error(data?.error || 'Failed to add stock to portfolio');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to add stock to portfolio', 'error');
                    throw error;
                });
        },

        // Remove stock from portfolio
        removeStock: function(holdingId) {
            return StockScannerAPI.Portfolio.removeFromPortfolio(holdingId)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Stock removed from portfolio successfully!', 'success');
                        this.loadPortfolioData(); // Reload portfolio data
                        return data;
                    } else {
                        throw new Error(data?.error || 'Failed to remove stock from portfolio');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to remove stock from portfolio', 'error');
                    throw error;
                });
        },

        // Start auto-refresh
        startAutoRefresh: function() {
            // Refresh every 5 minutes
            this.refreshInterval = setInterval(() => {
                this.loadPortfolioData();
            }, 300000);
        },

        // Stop auto-refresh
        stopAutoRefresh: function() {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }
        },

        // Bind event handlers
        bindEvents: function() {
            // Add stock button
            document.addEventListener('click', (e) => {
                if (e.target.matches('#add-stock-btn') || 
                    e.target.closest('#add-stock-btn') ||
                    e.target.matches('#add-first-stock-btn') ||
                    e.target.closest('#add-first-stock-btn')) {
                    this.showAddStockModal();
                }
            });

            // Refresh portfolio button
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-action="refresh-portfolio"]') || 
                    e.target.closest('[data-action="refresh-portfolio"]')) {
                    e.preventDefault();
                    this.loadPortfolioData();
                    StockScannerAPI.Toast.show('Portfolio data refreshed', 'success');
                }
            });

            // Holding actions
            document.addEventListener('click', (e) => {
                const editBtn = e.target.closest('.edit-holding');
                const removeBtn = e.target.closest('.remove-holding');
                const viewBtn = e.target.closest('.view-details');

                if (editBtn) {
                    const holdingId = editBtn.dataset.holdingId;
                    this.showEditHoldingModal(holdingId);
                } else if (removeBtn) {
                    const holdingId = removeBtn.dataset.holdingId;
                    this.confirmRemoveHolding(holdingId);
                } else if (viewBtn) {
                    const ticker = viewBtn.dataset.ticker;
                    window.location.href = `/stock-lookup/?ticker=${ticker}`;
                }
            });

            // Sort holdings
            const sortSelect = document.getElementById('sort-holdings');
            if (sortSelect) {
                sortSelect.addEventListener('change', (e) => {
                    this.sortHoldings(e.target.value);
                });
            }

            // Chart timeframe buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.timeframe-btn')) {
                    const period = e.target.dataset.period;
                    const buttons = document.querySelectorAll('.timeframe-btn');
                    
                    buttons.forEach(btn => btn.classList.remove('active'));
                    e.target.classList.add('active');
                    
                    // Update chart for the selected period
                    this.updateChartPeriod(period);
                }
            });
        },

        // Show add stock modal
        showAddStockModal: function() {
            const modal = document.getElementById('addStockModal');
            if (!modal) return;

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('add-stock-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitAddStock();
            };
        },

        // Submit add stock form
        submitAddStock: function() {
            const ticker = document.getElementById('stock-ticker').value.trim().toUpperCase();
            const shares = parseFloat(document.getElementById('stock-shares').value);
            const costBasis = parseFloat(document.getElementById('stock-cost-basis').value);
            const purchaseDate = document.getElementById('stock-purchase-date').value;

            if (!ticker || !shares || !costBasis) {
                StockScannerAPI.Toast.show('Please fill in all required fields', 'error');
                return;
            }

            this.addStock(ticker, shares, costBasis, purchaseDate)
                .then(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addStockModal'));
                    modal.hide();
                    // Reset form
                    document.getElementById('add-stock-form').reset();
                })
                .catch(error => {
                    // Error already handled in addStock method
                });
        },

        // Show edit holding modal
        showEditHoldingModal: function(holdingId) {
            const holding = this.holdings.find(h => h.id == holdingId);
            if (!holding) return;

            const modal = document.getElementById('editHoldingModal');
            if (!modal) return;

            // Populate form with holding data
            document.getElementById('edit-holding-id').value = holding.id;
            document.getElementById('edit-stock-ticker').value = holding.ticker;
            document.getElementById('edit-stock-shares').value = holding.shares;
            document.getElementById('edit-stock-cost-basis').value = holding.average_cost;
            document.getElementById('edit-stock-purchase-date').value = holding.purchase_date?.split(' ')[0] || '';

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('edit-holding-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitEditHolding();
            };

            // Handle delete button
            const deleteBtn = document.getElementById('delete-holding-btn');
            deleteBtn.onclick = () => {
                this.confirmRemoveHolding(holding.id);
                bootstrapModal.hide();
            };
        },

        // Submit edit holding form
        submitEditHolding: function() {
            const holdingId = document.getElementById('edit-holding-id').value;
            const shares = parseFloat(document.getElementById('edit-stock-shares').value);
            const costBasis = parseFloat(document.getElementById('edit-stock-cost-basis').value);
            const purchaseDate = document.getElementById('edit-stock-purchase-date').value;

            if (!shares || !costBasis) {
                StockScannerAPI.Toast.show('Please fill in all required fields', 'error');
                return;
            }

            // Update holding via API
            StockScannerAPI.Portfolio.updateHolding(holdingId, shares, costBasis, purchaseDate)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Holding updated successfully!', 'success');
                        const modal = bootstrap.Modal.getInstance(document.getElementById('editHoldingModal'));
                        modal.hide();
                        this.loadPortfolioData();
                    } else {
                        throw new Error(data?.error || 'Failed to update holding');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to update holding', 'error');
                });
        },

        // Confirm remove holding
        confirmRemoveHolding: function(holdingId) {
            const holding = this.holdings.find(h => h.id == holdingId);
            if (!holding) return;

            if (confirm(`Are you sure you want to remove ${holding.ticker} from your portfolio?`)) {
                this.removeStock(holdingId);
            }
        },

        // Sort holdings
        sortHoldings: function(sortBy) {
            const tbody = document.getElementById('holdings-tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            rows.sort((a, b) => {
                const aData = this.holdings.find(h => h.id == a.dataset.holdingId);
                const bData = this.holdings.find(h => h.id == b.dataset.holdingId);

                if (!aData || !bData) return 0;

                switch (sortBy) {
                    case 'ticker':
                        return aData.ticker.localeCompare(bData.ticker);
                    case 'company_name':
                        return (aData.stock_data?.company_name || aData.ticker).localeCompare(bData.stock_data?.company_name || bData.ticker);
                    case 'current_value':
                        return (bData.current_value || 0) - (aData.current_value || 0);
                    case 'return_percent':
                        return (bData.gain_loss_percent || 0) - (aData.gain_loss_percent || 0);
                    case 'day_change_percent':
                        return (bData.stock_data?.price_change_percent || 0) - (aData.stock_data?.price_change_percent || 0);
                    default:
                        return 0;
                }
            });

            // Reorder DOM elements
            rows.forEach(row => tbody.appendChild(row));
        },

        // Update chart period
        updateChartPeriod: function(period) {
            // In real implementation, this would fetch new data for the period
            StockScannerAPI.Toast.show(`Loading ${period} portfolio data...`, 'info');
        }
    };

    // Export to global scope
    window.StockScannerPortfolio = Portfolio;

    // Auto-initialize if on portfolio page
    document.addEventListener('DOMContentLoaded', function() {
        if (document.body.classList.contains('page-template-page-portfolio')) {
            Portfolio.init();
        }
    });

})();