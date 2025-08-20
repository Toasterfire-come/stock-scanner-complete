/**
 * Stock Scanner Pro - Watchlist Management Functionality
 */

(function() {
    'use strict';

    const Watchlist = {
        items: [],
        currentView: 'grid',
        currentFilter: '',
        currentSort: 'ticker',
        refreshInterval: null,

        init: function() {
            this.loadWatchlistData();
            this.bindEvents();
            this.startAutoRefresh();
        },

        // Load watchlist data
        loadWatchlistData: function() {
            const container = document.getElementById('watchlist-grid');
            if (container) {
                StockScannerAPI.Utils.showLoading(container, 'Loading watchlist...');
            }
            
            StockScannerAPI.Watchlist.getWatchlist()
                .then(data => {
                    if (data && data.success && data.watchlist) {
                        this.items = data.watchlist.items;
                        this.renderWatchlist(data.watchlist.items);
                        this.updateCategoryFilter(data.watchlist.categories);
                    } else {
                        this.showEmptyState();
                    }
                })
                .catch(error => {
                    console.error('Watchlist load error:', error);
                    this.showErrorState();
                })
                .finally(() => {
                    if (container) {
                        StockScannerAPI.Utils.hideLoading(container);
                    }
                });
        },

        // Render watchlist items
        renderWatchlist: function(items) {
            if (!items || items.length === 0) {
                this.showEmptyState();
                return;
            }

            if (this.currentView === 'grid') {
                this.renderGridView(items);
            } else {
                this.renderListView(items);
            }

            // Hide empty state
            const emptyState = document.getElementById('watchlist-empty');
            if (emptyState) {
                emptyState.style.display = 'none';
            }
        },

        // Render grid view
        renderGridView: function(items) {
            const container = document.getElementById('watchlist-grid');
            if (!container) return;

            container.style.display = 'grid';
            
            let html = '';
            items.forEach(item => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(item.price_change || 0);
                const categoryColor = this.getCategoryColor(item.category);
                
                html += `
                    <div class="watchlist-item-card" data-item-id="${item.id}" data-ticker="${item.ticker}">
                        <div class="watchlist-card-header">
                            <div class="stock-info">
                                <div class="stock-symbol">${item.ticker}</div>
                                <div class="stock-company">${item.stock_data?.company_name || item.ticker}</div>
                            </div>
                            <div class="category-badge" style="background-color: ${categoryColor}">
                                ${item.category || 'default'}
                            </div>
                        </div>
                        
                        <div class="watchlist-card-body">
                            <div class="price-info">
                                <div class="current-price">
                                    ${StockScannerAPI.Utils.formatCurrency(item.current_price || 0)}
                                </div>
                                <div class="price-change ${changeClass}">
                                    ${StockScannerAPI.Utils.formatCurrency(item.price_change || 0)} 
                                    (${StockScannerAPI.Utils.formatPercentage(item.price_change_percent || 0)})
                                </div>
                            </div>
                            
                            ${item.alerts && item.alerts.length > 0 ? `
                                <div class="alerts-indicator">
                                    <i class="fas fa-bell text-warning"></i>
                                    <span>${item.alerts.length} alert${item.alerts.length > 1 ? 's' : ''}</span>
                                </div>
                            ` : ''}
                            
                            ${item.notes ? `
                                <div class="item-notes">
                                    <i class="fas fa-sticky-note mr-2"></i>
                                    ${item.notes.substring(0, 50)}${item.notes.length > 50 ? '...' : ''}
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="watchlist-card-actions">
                            <button class="card-action-btn view-details" title="View Details" data-ticker="${item.ticker}">
                                <i class="fas fa-chart-line"></i>
                            </button>
                            <button class="card-action-btn add-to-portfolio" title="Add to Portfolio" data-ticker="${item.ticker}">
                                <i class="fas fa-plus"></i>
                            </button>
                            <button class="card-action-btn edit-item" title="Edit" data-item-id="${item.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="card-action-btn danger remove-item" title="Remove" data-item-id="${item.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        // Render list view
        renderListView: function(items) {
            const listContainer = document.getElementById('watchlist-list');
            const tbody = document.getElementById('watchlist-tbody');
            
            if (!listContainer || !tbody) return;

            listContainer.style.display = 'block';
            
            let html = '';
            items.forEach(item => {
                const changeClass = StockScannerAPI.Utils.getPriceChangeClass(item.price_change || 0);
                const categoryColor = this.getCategoryColor(item.category);
                
                html += `
                    <tr class="watchlist-row" data-item-id="${item.id}" data-ticker="${item.ticker}">
                        <td>
                            <div class="stock-symbol">
                                <strong>${item.ticker}</strong>
                            </div>
                        </td>
                        <td>
                            <div class="company-name">
                                ${item.stock_data?.company_name || item.ticker}
                            </div>
                        </td>
                        <td>
                            <span class="category-badge-small" style="background-color: ${categoryColor}">
                                ${item.category || 'default'}
                            </span>
                        </td>
                        <td class="text-right">
                            ${StockScannerAPI.Utils.formatCurrency(item.current_price || 0)}
                        </td>
                        <td class="text-right ${changeClass}">
                            ${StockScannerAPI.Utils.formatCurrency(item.price_change || 0)}
                        </td>
                        <td class="text-right ${changeClass}">
                            ${StockScannerAPI.Utils.formatPercentage(item.price_change_percent || 0)}
                        </td>
                        <td class="text-right">
                            ${StockScannerAPI.Utils.formatNumber(item.stock_data?.volume || 0)}
                        </td>
                        <td>
                            <div class="notes-cell" title="${item.notes || ''}">
                                ${item.notes ? item.notes.substring(0, 30) + (item.notes.length > 30 ? '...' : '') : ''}
                                ${item.alerts && item.alerts.length > 0 ? `<i class="fas fa-bell text-warning ml-2" title="${item.alerts.length} alert(s)"></i>` : ''}
                            </div>
                        </td>
                        <td class="text-center">
                            <div class="watchlist-actions">
                                <button class="watchlist-action-btn view-details" title="View Details" data-ticker="${item.ticker}">
                                    <i class="fas fa-chart-line"></i>
                                </button>
                                <button class="watchlist-action-btn add-to-portfolio" title="Add to Portfolio" data-ticker="${item.ticker}">
                                    <i class="fas fa-plus"></i>
                                </button>
                                <button class="watchlist-action-btn edit-item" title="Edit" data-item-id="${item.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="watchlist-action-btn danger remove-item" title="Remove" data-item-id="${item.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        },

        // Show empty state
        showEmptyState: function() {
            const emptyState = document.getElementById('watchlist-empty');
            const gridContainer = document.getElementById('watchlist-grid');
            const listContainer = document.getElementById('watchlist-list');
            
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            if (gridContainer) {
                gridContainer.innerHTML = '';
            }
            if (listContainer) {
                listContainer.style.display = 'none';
            }
        },

        // Show error state
        showErrorState: function() {
            const container = document.getElementById('watchlist-grid');
            if (!container) return;

            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle error-icon"></i>
                    <h4>Failed to Load Watchlist</h4>
                    <p>Please try refreshing the page or check your connection.</p>
                    <button class="btn btn-primary error-retry" onclick="StockScannerWatchlist.loadWatchlistData()">
                        <i class="fas fa-retry mr-2"></i>
                        Try Again
                    </button>
                </div>
            `;
        },

        // Update category filter options
        updateCategoryFilter: function(categories) {
            const filterSelect = document.getElementById('category-filter');
            if (!filterSelect || !categories) return;

            const currentValue = filterSelect.value;
            let html = '<option value="">All Categories</option>';
            
            categories.forEach(category => {
                html += `<option value="${category}">${category}</option>`;
            });
            
            filterSelect.innerHTML = html;
            filterSelect.value = currentValue;
        },

        // Get category color
        getCategoryColor: function(category) {
            const colors = {
                'default': '#6b7280',
                'growth': '#10b981',
                'dividend': '#3b82f6',
                'tech': '#8b5cf6',
                'healthcare': '#ec4899',
                'finance': '#f59e0b'
            };
            return colors[category] || colors['default'];
        },

        // Add stock to watchlist
        addToWatchlist: function(ticker, notes = '', category = 'default') {
            return StockScannerAPI.Watchlist.addToWatchlist(ticker, notes, category)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Stock added to watchlist successfully!', 'success');
                        this.loadWatchlistData(); // Reload watchlist data
                        return data;
                    } else {
                        throw new Error(data?.error || 'Failed to add stock to watchlist');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to add stock to watchlist', 'error');
                    throw error;
                });
        },

        // Remove stock from watchlist
        removeFromWatchlist: function(itemId) {
            return StockScannerAPI.Watchlist.removeFromWatchlist(itemId)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Stock removed from watchlist successfully!', 'success');
                        this.loadWatchlistData(); // Reload watchlist data
                        return data;
                    } else {
                        throw new Error(data?.error || 'Failed to remove stock from watchlist');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to remove stock from watchlist', 'error');
                    throw error;
                });
        },

        // Filter watchlist items
        filterItems: function(category) {
            this.currentFilter = category;
            let filteredItems = this.items;

            if (category) {
                filteredItems = this.items.filter(item => item.category === category);
            }

            this.renderWatchlist(filteredItems);
        },

        // Sort watchlist items
        sortItems: function(sortBy) {
            this.currentSort = sortBy;
            let sortedItems = [...this.items];

            sortedItems.sort((a, b) => {
                switch (sortBy) {
                    case 'ticker':
                        return a.ticker.localeCompare(b.ticker);
                    case 'company_name':
                        return (a.stock_data?.company_name || a.ticker).localeCompare(b.stock_data?.company_name || b.ticker);
                    case 'current_price':
                        return (b.current_price || 0) - (a.current_price || 0);
                    case 'change_percent':
                        return (b.price_change_percent || 0) - (a.price_change_percent || 0);
                    case 'added_date':
                        return new Date(b.created_at) - new Date(a.created_at);
                    default:
                        return 0;
                }
            });

            this.renderWatchlist(sortedItems);
        },

        // Switch view mode
        switchView: function(viewMode) {
            this.currentView = viewMode;
            
            const gridContainer = document.getElementById('watchlist-grid');
            const listContainer = document.getElementById('watchlist-list');
            
            if (viewMode === 'grid') {
                if (gridContainer) gridContainer.style.display = 'grid';
                if (listContainer) listContainer.style.display = 'none';
                this.renderGridView(this.items);
            } else {
                if (gridContainer) gridContainer.style.display = 'none';
                if (listContainer) listContainer.style.display = 'block';
                this.renderListView(this.items);
            }
        },

        // Start auto-refresh
        startAutoRefresh: function() {
            // Refresh every 5 minutes
            this.refreshInterval = setInterval(() => {
                this.loadWatchlistData();
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
            // Add to watchlist button
            document.addEventListener('click', (e) => {
                if (e.target.matches('#add-to-watchlist-btn') || 
                    e.target.closest('#add-to-watchlist-btn') ||
                    e.target.matches('#add-first-stock-btn') ||
                    e.target.closest('#add-first-stock-btn')) {
                    this.showAddToWatchlistModal();
                }
            });

            // Refresh watchlist button
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-action="refresh-watchlist"]') || 
                    e.target.closest('[data-action="refresh-watchlist"]')) {
                    e.preventDefault();
                    this.loadWatchlistData();
                    StockScannerAPI.Toast.show('Watchlist refreshed', 'success');
                }
            });

            // View mode buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.view-mode-btn')) {
                    const viewMode = e.target.dataset.view;
                    const buttons = document.querySelectorAll('.view-mode-btn');
                    
                    buttons.forEach(btn => btn.classList.remove('active'));
                    e.target.classList.add('active');
                    
                    this.switchView(viewMode);
                }
            });

            // Category filter
            const categoryFilter = document.getElementById('category-filter');
            if (categoryFilter) {
                categoryFilter.addEventListener('change', (e) => {
                    this.filterItems(e.target.value);
                });
            }

            // Sort dropdown
            const sortSelect = document.getElementById('sort-watchlist');
            if (sortSelect) {
                sortSelect.addEventListener('change', (e) => {
                    this.sortItems(e.target.value);
                });
            }

            // Item actions
            document.addEventListener('click', (e) => {
                const viewBtn = e.target.closest('.view-details');
                const addBtn = e.target.closest('.add-to-portfolio');
                const editBtn = e.target.closest('.edit-item');
                const removeBtn = e.target.closest('.remove-item');

                if (viewBtn) {
                    const ticker = viewBtn.dataset.ticker;
                    window.location.href = `/stock-lookup/?ticker=${ticker}`;
                } else if (addBtn) {
                    const ticker = addBtn.dataset.ticker;
                    this.showAddToPortfolioModal(ticker);
                } else if (editBtn) {
                    const itemId = editBtn.dataset.itemId;
                    this.showEditItemModal(itemId);
                } else if (removeBtn) {
                    const itemId = removeBtn.dataset.itemId;
                    this.confirmRemoveItem(itemId);
                }
            });

            // Watchlist item cards click
            document.addEventListener('click', (e) => {
                const card = e.target.closest('.watchlist-item-card');
                if (card && !e.target.closest('.watchlist-card-actions')) {
                    const ticker = card.dataset.ticker;
                    this.showStockDetailsModal(ticker);
                }
            });

            // Create alert checkbox
            document.addEventListener('change', (e) => {
                if (e.target.matches('#create-alert-checkbox')) {
                    const alertSection = document.getElementById('price-alert-section');
                    if (alertSection) {
                        alertSection.style.display = e.target.checked ? 'block' : 'none';
                    }
                }
            });
        },

        // Show add to watchlist modal
        showAddToWatchlistModal: function() {
            const modal = document.getElementById('addToWatchlistModal');
            if (!modal) return;

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('add-to-watchlist-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitAddToWatchlist();
            };
        },

        // Submit add to watchlist form
        submitAddToWatchlist: function() {
            const ticker = document.getElementById('watchlist-ticker-input').value.trim().toUpperCase();
            const category = document.getElementById('watchlist-category-input').value;
            const notes = document.getElementById('watchlist-notes-input').value;
            const createAlert = document.getElementById('create-alert-checkbox').checked;

            if (!ticker) {
                StockScannerAPI.Toast.show('Stock symbol is required', 'error');
                return;
            }

            this.addToWatchlist(ticker, notes, category)
                .then(() => {
                    // Handle alert creation if requested
                    if (createAlert) {
                        const targetPrice = parseFloat(document.getElementById('alert-target-price').value);
                        const condition = document.getElementById('alert-condition').value;
                        
                        if (targetPrice && targetPrice > 0) {
                            this.createPriceAlert(ticker, targetPrice, condition);
                        }
                    }

                    const modal = bootstrap.Modal.getInstance(document.getElementById('addToWatchlistModal'));
                    modal.hide();
                    // Reset form
                    document.getElementById('add-to-watchlist-form').reset();
                    document.getElementById('price-alert-section').style.display = 'none';
                })
                .catch(error => {
                    // Error already handled in addToWatchlist method
                });
        },

        // Show edit item modal
        showEditItemModal: function(itemId) {
            const item = this.items.find(i => i.id == itemId);
            if (!item) return;

            const modal = document.getElementById('editWatchlistModal');
            if (!modal) return;

            // Populate form with item data
            document.getElementById('edit-watchlist-id').value = item.id;
            document.getElementById('edit-watchlist-ticker').value = item.ticker;
            document.getElementById('edit-watchlist-category').value = item.category || 'default';
            document.getElementById('edit-watchlist-notes').value = item.notes || '';

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Handle form submission
            const form = document.getElementById('edit-watchlist-form');
            form.onsubmit = (e) => {
                e.preventDefault();
                this.submitEditItem();
            };

            // Handle delete button
            const deleteBtn = document.getElementById('delete-watchlist-btn');
            deleteBtn.onclick = () => {
                this.confirmRemoveItem(item.id);
                bootstrapModal.hide();
            };
        },

        // Submit edit item form
        submitEditItem: function() {
            const itemId = document.getElementById('edit-watchlist-id').value;
            const category = document.getElementById('edit-watchlist-category').value;
            const notes = document.getElementById('edit-watchlist-notes').value;

            StockScannerAPI.Watchlist.updateWatchlistItem(itemId, notes, category)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Watchlist item updated successfully!', 'success');
                        const modal = bootstrap.Modal.getInstance(document.getElementById('editWatchlistModal'));
                        modal.hide();
                        this.loadWatchlistData();
                    } else {
                        throw new Error(data?.error || 'Failed to update watchlist item');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show(error.message || 'Failed to update watchlist item', 'error');
                });
        },

        // Show stock details modal
        showStockDetailsModal: function(ticker) {
            const modal = document.getElementById('stockDetailsModal');
            if (!modal) return;

            document.getElementById('stock-details-title').textContent = `${ticker} - Stock Details`;
            
            const content = document.getElementById('stock-details-content');
            content.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Load stock details
            StockScannerAPI.Stock.getStock(ticker)
                .then(data => {
                    if (data && data.success && data.data) {
                        this.renderStockDetailsModal(content, data.data);
                    } else {
                        content.innerHTML = '<p class="text-center text-muted">Stock details not available</p>';
                    }
                })
                .catch(error => {
                    content.innerHTML = '<p class="text-center text-danger">Failed to load stock details</p>';
                });
        },

        // Render stock details modal content
        renderStockDetailsModal: function(container, stockData) {
            const changeClass = StockScannerAPI.Utils.getPriceChangeClass(stockData.price_change || 0);
            
            const html = `
                <div class="stock-details-modal-content">
                    <div class="stock-header-modal">
                        <div class="stock-title">
                            <h4>${stockData.ticker}</h4>
                            <p class="text-muted">${stockData.company_name || stockData.ticker}</p>
                        </div>
                        <div class="stock-price-modal">
                            <div class="current-price">${StockScannerAPI.Utils.formatCurrency(stockData.current_price || 0)}</div>
                            <div class="price-change ${changeClass}">
                                ${StockScannerAPI.Utils.formatCurrency(stockData.price_change || 0)} 
                                (${StockScannerAPI.Utils.formatPercentage(stockData.price_change_percent || 0)})
                            </div>
                        </div>
                    </div>
                    
                    <div class="stock-stats-modal mt-4">
                        <div class="row">
                            <div class="col-6">
                                <div class="stat-item-modal">
                                    <span class="stat-label">Volume</span>
                                    <span class="stat-value">${StockScannerAPI.Utils.formatNumber(stockData.volume || 0)}</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="stat-item-modal">
                                    <span class="stat-label">Market Cap</span>
                                    <span class="stat-value">${StockScannerAPI.Utils.formatCurrency(stockData.market_cap || 0)}</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="stat-item-modal">
                                    <span class="stat-label">P/E Ratio</span>
                                    <span class="stat-value">${stockData.pe_ratio || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="stat-item-modal">
                                    <span class="stat-label">Day Range</span>
                                    <span class="stat-value">
                                        ${StockScannerAPI.Utils.formatCurrency(stockData.day_low || 0)} - 
                                        ${StockScannerAPI.Utils.formatCurrency(stockData.day_high || 0)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        },

        // Show add to portfolio modal
        showAddToPortfolioModal: function(ticker) {
            // This would integrate with the portfolio module
            StockScannerAPI.Toast.show(`Add ${ticker} to portfolio feature coming soon!`, 'info');
        },

        // Create price alert
        createPriceAlert: function(ticker, targetPrice, condition) {
            StockScannerAPI.Watchlist.createPriceAlert(ticker, targetPrice, condition)
                .then(data => {
                    if (data && data.success) {
                        StockScannerAPI.Toast.show('Price alert created successfully!', 'success');
                    } else {
                        StockScannerAPI.Toast.show(data?.error || 'Failed to create price alert', 'warning');
                    }
                })
                .catch(error => {
                    StockScannerAPI.Toast.show('Failed to create price alert', 'error');
                });
        },

        // Confirm remove item
        confirmRemoveItem: function(itemId) {
            const item = this.items.find(i => i.id == itemId);
            if (!item) return;

            if (confirm(`Are you sure you want to remove ${item.ticker} from your watchlist?`)) {
                this.removeFromWatchlist(itemId);
            }
        }
    };

    // Export to global scope
    window.StockScannerWatchlist = Watchlist;

    // Auto-initialize if on watchlist page
    document.addEventListener('DOMContentLoaded', function() {
        if (document.body.classList.contains('page-template-page-watchlist')) {
            Watchlist.init();
        }
    });

})();