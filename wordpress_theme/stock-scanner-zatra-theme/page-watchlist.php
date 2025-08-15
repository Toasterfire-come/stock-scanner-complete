<?php
/**
 * Template Name: Watchlist
 * 
 * The template for displaying and managing user watchlists
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="watchlist-container">
    <div class="page-header">
        <div class="container">
            <div class="header-content">
                <div class="header-left">
                    <h1 class="page-title">
                        <i class="fas fa-eye"></i>
                        My Watchlist
                    </h1>
                    <p class="page-subtitle">Track and monitor your favorite stocks</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" id="addStockBtn">
                        <i class="fas fa-plus"></i>
                        Add Stock
                    </button>
                    <button class="btn btn-secondary" id="refreshBtn">
                        <i class="fas fa-sync-alt"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="watchlist-content">
        <div class="container">
            <!-- Quick Stats -->
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-icon">
                        <i class="fas fa-list"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value" id="totalStocks">0</div>
                        <div class="stat-label">Total Stocks</div>
                    </div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">
                        <i class="fas fa-arrow-up"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value positive" id="gainers">0</div>
                        <div class="stat-label">Gainers</div>
                    </div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">
                        <i class="fas fa-arrow-down"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value negative" id="losers">0</div>
                        <div class="stat-label">Losers</div>
                    </div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value" id="lastUpdate">--:--</div>
                        <div class="stat-label">Last Update</div>
                    </div>
                </div>
            </div>

            <!-- Filter and Sort Controls -->
            <div class="controls-section">
                <div class="search-filter">
                    <input type="text" id="searchInput" placeholder="Search your watchlist..." class="search-input">
                    <i class="fas fa-search search-icon"></i>
                </div>
                <div class="sort-controls">
                    <label for="sortSelect">Sort by:</label>
                    <select id="sortSelect" class="sort-select">
                        <option value="symbol">Symbol</option>
                        <option value="name">Name</option>
                        <option value="price">Price</option>
                        <option value="change">Change</option>
                        <option value="volume">Volume</option>
                    </select>
                    <button id="sortOrder" class="sort-order-btn" data-order="asc">
                        <i class="fas fa-sort-up"></i>
                    </button>
                </div>
            </div>

            <!-- Watchlist Table -->
            <div class="watchlist-table-container">
                <div class="loading-indicator" id="loadingIndicator">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading your watchlist...
                </div>
                
                <div class="watchlist-table" id="watchlistTable" style="display: none;">
                    <div class="table-header">
                        <div class="header-cell symbol">Symbol</div>
                        <div class="header-cell name">Company</div>
                        <div class="header-cell price">Price</div>
                        <div class="header-cell change">Change</div>
                        <div class="header-cell volume">Volume</div>
                        <div class="header-cell actions">Actions</div>
                    </div>
                    <div class="table-body" id="watchlistBody">
                        <!-- Watchlist items will be populated here -->
                    </div>
                </div>

                <div class="empty-watchlist" id="emptyWatchlist" style="display: none;">
                    <div class="empty-icon">
                        <i class="fas fa-eye-slash"></i>
                    </div>
                    <h3>Your watchlist is empty</h3>
                    <p>Start adding stocks to track their performance</p>
                    <button class="btn btn-primary" onclick="document.getElementById('addStockBtn').click()">
                        <i class="fas fa-plus"></i>
                        Add Your First Stock
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add Stock Modal -->
<div class="modal" id="addStockModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Add Stock to Watchlist</h3>
            <button class="modal-close" id="modalClose">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <form id="addStockForm">
                <div class="form-group">
                    <label for="stockSymbolInput">Stock Symbol</label>
                    <input type="text" id="stockSymbolInput" placeholder="e.g., AAPL, GOOGL, TSLA" class="form-input" autocomplete="off">
                    <div class="suggestions-container" id="symbolSuggestions"></div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancelBtn">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="addBtn">
                        <i class="fas fa-plus"></i>
                        Add Stock
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
.watchlist-container {
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

.watchlist-content {
    padding: 2rem 0;
}

.stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-item {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.stat-icon {
    background: #3685fb;
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
}

.stat-value.positive { color: #10b981; }
.stat-value.negative { color: #ef4444; }

.stat-label {
    color: #666;
    font-size: 0.9rem;
}

.controls-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}

.search-filter {
    position: relative;
    flex: 1;
    max-width: 400px;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
}

.search-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
}

.sort-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.sort-select {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    outline: none;
}

.sort-order-btn {
    background: #f8f9fa;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    padding: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}

.sort-order-btn:hover {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.watchlist-table-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}

.loading-indicator {
    text-align: center;
    padding: 3rem;
    color: #666;
    font-size: 1.1rem;
}

.watchlist-table {
    width: 100%;
}

.table-header {
    background: #f8f9fa;
    display: grid;
    grid-template-columns: 100px 1fr 120px 120px 120px 100px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #e1e5e9;
    font-weight: 600;
    color: #333;
}

.table-body {
    max-height: 600px;
    overflow-y: auto;
}

.watchlist-row {
    display: grid;
    grid-template-columns: 100px 1fr 120px 120px 120px 100px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
    transition: background 0.2s;
}

.watchlist-row:hover {
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

.name-cell {
    color: #666;
    font-size: 0.9rem;
}

.price-cell {
    font-weight: 600;
    color: #1a1a1a;
}

.change-cell {
    font-weight: 600;
}

.change-cell.positive { color: #10b981; }
.change-cell.negative { color: #ef4444; }

.volume-cell {
    color: #666;
    font-size: 0.9rem;
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

.empty-watchlist {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
}

.empty-icon {
    font-size: 4rem;
    color: #ddd;
    margin-bottom: 1rem;
}

.empty-watchlist h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.empty-watchlist p {
    margin: 0 0 2rem 0;
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

.suggestions-container {
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

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .stats-row {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
    
    .controls-section {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .table-header,
    .watchlist-row {
        grid-template-columns: 80px 1fr 80px 80px;
        font-size: 0.9rem;
    }
    
    .volume-cell,
    .header-cell.volume {
        display: none;
    }
    
    .actions-cell,
    .header-cell.actions {
        display: none;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeWatchlist();
    loadWatchlist();
    setupEventListeners();
    
    // Start real-time updates
    setInterval(updatePrices, 30000); // Update every 30 seconds
});

function initializeWatchlist() {
    const addStockBtn = document.getElementById('addStockBtn');
    const modal = document.getElementById('addStockModal');
    const modalClose = document.getElementById('modalClose');
    const cancelBtn = document.getElementById('cancelBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    addStockBtn.addEventListener('click', () => modal.classList.add('active'));
    modalClose.addEventListener('click', () => modal.classList.remove('active'));
    cancelBtn.addEventListener('click', () => modal.classList.remove('active'));
    refreshBtn.addEventListener('click', loadWatchlist);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const sortOrderBtn = document.getElementById('sortOrder');
    const addStockForm = document.getElementById('addStockForm');
    const stockSymbolInput = document.getElementById('stockSymbolInput');
    
    searchInput.addEventListener('input', filterWatchlist);
    sortSelect.addEventListener('change', sortWatchlist);
    sortOrderBtn.addEventListener('click', toggleSortOrder);
    addStockForm.addEventListener('submit', handleAddStock);
    stockSymbolInput.addEventListener('input', showStockSuggestions);
}

function loadWatchlist() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const watchlistTable = document.getElementById('watchlistTable');
    const emptyWatchlist = document.getElementById('emptyWatchlist');
    
    loadingIndicator.style.display = 'block';
    watchlistTable.style.display = 'none';
    emptyWatchlist.style.display = 'none';
    
    // Simulate loading delay
    getWatchlistData()
        .then(watchlistData => {
            if (watchlistData.length === 0) {
                loadingIndicator.style.display = 'none';
                emptyWatchlist.style.display = 'block';
                updateStats(watchlistData);
            } else {
                displayWatchlist(watchlistData);
                updateStats(watchlistData);
                loadingIndicator.style.display = 'none';
                watchlistTable.style.display = 'block';
            }
        })
        .catch(err => {
            console.error('Watchlist error:', err);
            loadingIndicator.style.display = 'none';
            emptyWatchlist.style.display = 'block';
        });
}

function getWatchlistData() {
    const params = new URLSearchParams();
    params.append('action', 'get_formatted_watchlist_data');
    params.append('nonce', (window.stockScannerAjax && stockScannerAjax.nonce) || '');
    return fetch((window.stockScannerAjax && stockScannerAjax.ajaxurl) || '/wp-admin/admin-ajax.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params
    })
    .then(res => res.json())
    .then(res => {
        if (!res || !res.success) throw new Error(res && res.data ? res.data : 'Failed to load watchlist');
        return Array.isArray(res.data) ? res.data : [];
    });
}

function displayWatchlist(data) {
    const tbody = document.getElementById('watchlistBody');
    
    tbody.innerHTML = data.map(stock => {
        const changeClass = stock.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = stock.change >= 0 ? '+' : '';
        
        return `
            <div class="watchlist-row">
                <div class="symbol-cell" onclick="viewStock('${stock.symbol}')">${stock.symbol}</div>
                <div class="name-cell">${stock.name}</div>
                <div class="price-cell">$${stock.price.toFixed(2)}</div>
                <div class="change-cell ${changeClass}">
                    ${changeSymbol}$${stock.change.toFixed(2)} (${changeSymbol}${stock.changePercent.toFixed(2)}%)
                </div>
                <div class="volume-cell">${formatVolume(stock.volume)}</div>
                <div class="actions-cell">
                    <button class="action-btn" onclick="viewStock('${stock.symbol}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn remove" onclick="removeStock('${stock.symbol}')" title="Remove">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updateStats(data) {
    const totalStocks = data.length;
    const gainers = data.filter(stock => stock.change > 0).length;
    const losers = data.filter(stock => stock.change < 0).length;
    const now = new Date();
    
    document.getElementById('totalStocks').textContent = totalStocks;
    document.getElementById('gainers').textContent = gainers;
    document.getElementById('losers').textContent = losers;
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
}

function filterWatchlist() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('.watchlist-row');
    
    rows.forEach(row => {
        const symbol = row.querySelector('.symbol-cell').textContent.toLowerCase();
        const name = row.querySelector('.name-cell').textContent.toLowerCase();
        
        if (symbol.includes(searchTerm) || name.includes(searchTerm)) {
            row.style.display = 'grid';
        } else {
            row.style.display = 'none';
        }
    });
}

function sortWatchlist() {
    // Implementation for sorting would go here
    console.log('Sorting watchlist...');
}

function toggleSortOrder() {
    const btn = document.getElementById('sortOrder');
    const currentOrder = btn.dataset.order;
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    
    btn.dataset.order = newOrder;
    btn.innerHTML = newOrder === 'asc' ? '<i class="fas fa-sort-up"></i>' : '<i class="fas fa-sort-down"></i>';
    
    sortWatchlist();
}

function showStockSuggestions() {
    const input = document.getElementById('stockSymbolInput');
    const suggestions = document.getElementById('symbolSuggestions');
    const query = input.value.trim();
    
    if (query.length >= 2) {
        const stocks = [
            { symbol: 'AAPL', name: 'Apple Inc.' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.' },
            { symbol: 'MSFT', name: 'Microsoft Corporation' },
            { symbol: 'TSLA', name: 'Tesla Inc.' },
            { symbol: 'AMZN', name: 'Amazon.com Inc.' },
            { symbol: 'NVDA', name: 'NVIDIA Corporation' },
            { symbol: 'META', name: 'Meta Platforms Inc.' },
            { symbol: 'NFLX', name: 'Netflix Inc.' }
        ].filter(stock => 
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        );
        
        if (stocks.length > 0) {
            suggestions.innerHTML = stocks.map(stock => `
                <div class="suggestion-item" onclick="selectStock('${stock.symbol}')">
                    <strong>${stock.symbol}</strong> - ${stock.name}
                </div>
            `).join('');
            suggestions.style.display = 'block';
        } else {
            suggestions.style.display = 'none';
        }
    } else {
        suggestions.style.display = 'none';
    }
}

function selectStock(symbol) {
    document.getElementById('stockSymbolInput').value = symbol;
    document.getElementById('symbolSuggestions').style.display = 'none';
}

function handleAddStock(e) {
    e.preventDefault();
    const symbol = document.getElementById('stockSymbolInput').value.trim().toUpperCase();
    
    if (!symbol) return;
    
    // Simulate adding stock
    console.log('Adding stock:', symbol);
    
    // Close modal and refresh watchlist
    document.getElementById('addStockModal').classList.remove('active');
    document.getElementById('stockSymbolInput').value = '';
    
    // Show success message
    showNotification(`${symbol} added to your watchlist!`, 'success');
    
    // Refresh watchlist
    setTimeout(loadWatchlist, 500);
}

function removeStock(symbol) {
    if (confirm(`Remove ${symbol} from your watchlist?`)) {
        console.log('Removing stock:', symbol);
        showNotification(`${symbol} removed from your watchlist!`, 'info');
        setTimeout(loadWatchlist, 500);
    }
}

function viewStock(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
}

function updatePrices() {
    // Simulate real-time price updates
    console.log('Updating prices...');
    
    // In a real app, this would fetch updated prices from the backend
    // and update the displayed values
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add styles
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
    
    // Add close button styles
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
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}
</script>

<?php get_footer(); ?>