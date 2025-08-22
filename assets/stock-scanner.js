/**
 * Stock Scanner WordPress Integration JavaScript
 * Handles frontend interactions and API calls
 */

const stockScanner = {
    
    init: function() {
        this.bindEvents();
        this.loadInitialData();
    },
    
    bindEvents: function() {
        // Auto-refresh stock data every 30 seconds
        setInterval(() => {
            this.refreshAllStocks();
        }, 30000);
        
        // Handle click events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('refresh-btn')) {
                const widget = e.target.closest('.stock-scanner-widget');
                const symbol = widget.dataset.symbol;
                this.refreshStock(symbol);
            }
        });
    },
    
    loadInitialData: function() {
        const widgets = document.querySelectorAll('.stock-scanner-widget');
        widgets.forEach(widget => {
            const symbol = widget.dataset.symbol;
            this.loadStockData(symbol, widget);
        });
    },
    
    refreshStock: function(symbol) {
        const widget = document.querySelector(`[data-symbol="${symbol}"]`);
        if (widget) {
            this.loadStockData(symbol, widget);
        }
    },
    
    refreshAllStocks: function() {
        const widgets = document.querySelectorAll('.stock-scanner-widget');
        widgets.forEach(widget => {
            const symbol = widget.dataset.symbol;
            this.loadStockData(symbol, widget);
        });
    },
    
    loadStockData: function(symbol, widget) {
        const loadingEl = widget.querySelector('.loading');
        const priceEl = widget.querySelector('.stock-price');
        const detailsEl = widget.querySelector('.stock-details');
        
        // Show loading state
        loadingEl.style.display = 'block';
        priceEl.style.display = 'none';
        if (detailsEl) detailsEl.style.display = 'none';
        
        // Make AJAX request
        jQuery.post(stock_scanner_ajax.ajax_url, {
            action: 'get_stock_data',
            symbol: symbol,
            nonce: stock_scanner_ajax.nonce
        })
        .done((response) => {
            if (response.success) {
                this.updateStockWidget(widget, response.data);
            } else {
                this.showError(widget, response.data.message || 'Failed to load stock data');
                
                // If it's a paywall error, show upgrade options
                if (response.data.usage) {
                    this.showPaywallMessage(widget, response.data);
                }
            }
        })
        .fail(() => {
            this.showError(widget, 'Network error occurred');
        })
        .always(() => {
            loadingEl.style.display = 'none';
        });
    },
    
    updateStockWidget: function(widget, data) {
        const priceEl = widget.querySelector('.stock-price');
        const detailsEl = widget.querySelector('.stock-details');
        
        // Update price information
        if (priceEl) {
            const priceSpan = priceEl.querySelector('.price');
            const changeSpan = priceEl.querySelector('.change');
            
            if (priceSpan && data.price) {
                priceSpan.textContent = `$${data.price.toFixed(2)}`;
            }
            
            if (changeSpan && data.change !== undefined) {
                const changeValue = data.change;
                const changePercent = data.change_percent || 0;
                
                changeSpan.textContent = `${changeValue >= 0 ? '+' : ''}${changeValue.toFixed(2)} (${changePercent.toFixed(2)}%)`;
                changeSpan.className = `change ${changeValue >= 0 ? 'positive' : 'negative'}`;
            }
            
            priceEl.style.display = 'block';
        }
        
        // Update details
        if (detailsEl && data.details) {
            const volumeEl = detailsEl.querySelector('.volume');
            const marketCapEl = detailsEl.querySelector('.market-cap');
            
            if (volumeEl && data.details.volume) {
                volumeEl.textContent = this.formatNumber(data.details.volume);
            }
            
            if (marketCapEl && data.details.market_cap) {
                marketCapEl.textContent = this.formatCurrency(data.details.market_cap);
            }
            
            detailsEl.style.display = 'block';
        }
        
        // Update chart if present
        if (data.chart_data) {
            this.updateChart(widget, data.chart_data);
        }
        
        // Update timestamp
        this.updateTimestamp(widget);
    },
    
    updateChart: function(widget, chartData) {
        const chartCanvas = widget.querySelector('canvas');
        if (!chartCanvas || !window.Chart) return;
        
        const ctx = chartCanvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (chartCanvas.chart) {
            chartCanvas.chart.destroy();
        }
        
        // Create new chart
        chartCanvas.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    label: 'Price',
                    data: chartData.prices || [],
                    borderColor: '#007cba',
                    backgroundColor: 'rgba(0, 124, 186, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    },
    
    showError: function(widget, message) {
        const loadingEl = widget.querySelector('.loading');
        loadingEl.innerHTML = `<div class="error">⚠️ ${message}</div>`;
        loadingEl.style.display = 'block';
    },
    
    showPaywallMessage: function(widget, errorData) {
        const { usage, limit } = errorData;
        
        const paywallHtml = `
            <div class="stock-scanner-paywall">
                <div class="paywall-message">
                    <h4>🚀 Upgrade for More Stock Data</h4>
                    <p>You've used <strong>${usage.monthly}</strong> out of <strong>${limit}</strong> stocks this month.</p>
                    <div class="upgrade-options">
                        <a href="/membership-checkout/?level=2" class="btn btn-premium">Upgrade to Premium</a>
                        <a href="/membership-checkout/?level=3" class="btn btn-professional">Go Professional</a>
                    </div>
                </div>
            </div>
        `;
        
        widget.innerHTML = paywallHtml;
    },
    
    updateTimestamp: function(widget) {
        let timestampEl = widget.querySelector('.last-updated');
        
        if (!timestampEl) {
            timestampEl = document.createElement('div');
            timestampEl.className = 'last-updated';
            widget.appendChild(timestampEl);
        }
        
        const now = new Date();
        timestampEl.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    },
    
    formatNumber: function(num) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    },
    
    formatCurrency: function(amount) {
        if (amount >= 1e12) {
            return '$' + (amount / 1e12).toFixed(1) + 'T';
        } else if (amount >= 1e9) {
            return '$' + (amount / 1e9).toFixed(1) + 'B';
        } else if (amount >= 1e6) {
            return '$' + (amount / 1e6).toFixed(1) + 'M';
        }
        return '$' + amount.toLocaleString();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    stockScanner.init();
});

// Global function for manual refresh
window.stockScanner = stockScanner;