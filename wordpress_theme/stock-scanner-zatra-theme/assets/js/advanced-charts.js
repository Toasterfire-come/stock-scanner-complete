/**
 * Advanced Interactive Charts System - Backend Database Integration
 * Professional-grade chart visualizations with backend data only
 */

class AdvancedChartSystem {
    constructor() {
        this.charts = new Map();
        this.dataCache = new Map();
        this.updateIntervals = new Map();
        this.observedCharts = new Set();
        this.themes = {
            light: {
                background: '#ffffff',
                text: '#333333',
                grid: '#e1e5e9',
                positive: '#10b981',
                negative: '#ef4444',
                neutral: '#6b7280'
            },
            dark: {
                background: '#1a1a1a',
                text: '#ffffff',
                grid: '#374151',
                positive: '#34d399',
                negative: '#f87171',
                neutral: '#9ca3af'
            }
        };
        this.currentTheme = localStorage.getItem('chart-theme') || 'light';
        this.apiEndpoints = {
            stockData: '/wp-json/stock-scanner/v1/stock-data/',
            marketData: '/wp-json/stock-scanner/v1/market-data/',
            historicalData: '/wp-json/stock-scanner/v1/historical-data/',
            realTimeData: '/wp-json/stock-scanner/v1/realtime-data/'
        };
        this.init();
    }

    init() {
        this.setupChartDefaults();
        this.createChartControls();
        this.bindEvents();
        this.setupIntersectionObserver();
        this.setupPerformanceMonitoring();
        this.loadThemePreference();
    }

    setupChartDefaults() {
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.interaction.intersect = false;
        Chart.defaults.interaction.mode = 'index';
        Chart.defaults.animation.duration = 750;
        Chart.defaults.animation.easing = 'easeInOutQuart';
    }

    setupIntersectionObserver() {
        this.chartObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const canvasId = entry.target.id;
                if (entry.isIntersecting) {
                    this.observedCharts.add(canvasId);
                    this.loadChartData(canvasId);
                } else {
                    this.observedCharts.delete(canvasId);
                    this.pauseChartUpdates(canvasId);
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });
    }

    setupPerformanceMonitoring() {
        this.performanceMetrics = {
            chartRenderTimes: [],
            dataFetchTimes: [],
            memoryUsage: []
        };
        
        // Monitor memory usage every 30 seconds
        setInterval(() => {
            if (performance.memory) {
                this.performanceMetrics.memoryUsage.push({
                    timestamp: Date.now(),
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize
                });
                
                // Keep only last 100 measurements
                if (this.performanceMetrics.memoryUsage.length > 100) {
                    this.performanceMetrics.memoryUsage.shift();
                }
            }
        }, 30000);
    }

    createChartControls() {
        const controlsHTML = `
            <div class="chart-controls-overlay" id="chartControls" style="display: none;">
                <div class="chart-toolbar">
                    <div class="chart-type-selector">
                        <button class="chart-type-btn active" data-type="line" title="Line Chart">
                            <i class="fas fa-chart-line"></i>
                            <span>Line</span>
                        </button>
                        <button class="chart-type-btn" data-type="candlestick" title="Candlestick Chart">
                            <i class="fas fa-chart-bar"></i>
                            <span>Candlestick</span>
                        </button>
                        <button class="chart-type-btn" data-type="area" title="Area Chart">
                            <i class="fas fa-chart-area"></i>
                            <span>Area</span>
                        </button>
                        <button class="chart-type-btn" data-type="volume" title="Volume Chart">
                            <i class="fas fa-signal"></i>
                            <span>Volume</span>
                        </button>
                    </div>
                    
                    <div class="time-range-selector">
                        <button class="time-btn" data-range="1D" title="1 Day">1D</button>
                        <button class="time-btn active" data-range="1W" title="1 Week">1W</button>
                        <button class="time-btn" data-range="1M" title="1 Month">1M</button>
                        <button class="time-btn" data-range="3M" title="3 Months">3M</button>
                        <button class="time-btn" data-range="1Y" title="1 Year">1Y</button>
                        <button class="time-btn" data-range="5Y" title="5 Years">5Y</button>
                    </div>
                    
                    <div class="chart-indicators">
                        <button class="indicator-btn" data-indicator="sma" title="Simple Moving Average">SMA</button>
                        <button class="indicator-btn" data-indicator="ema" title="Exponential Moving Average">EMA</button>
                        <button class="indicator-btn" data-indicator="bollinger" title="Bollinger Bands">Bollinger</button>
                        <button class="indicator-btn" data-indicator="rsi" title="Relative Strength Index">RSI</button>
                        <button class="indicator-btn" data-indicator="macd" title="MACD">MACD</button>
                    </div>
                    
                    <div class="chart-actions">
                        <button class="action-btn" id="fullscreenChart" title="Fullscreen">
                            <i class="fas fa-expand"></i>
                        </button>
                        <button class="action-btn" id="downloadChart" title="Download Chart">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="action-btn" id="shareChart" title="Share Chart">
                            <i class="fas fa-share"></i>
                        </button>
                        <button class="action-btn" id="themeToggle" title="Toggle Theme">
                            <i class="fas fa-moon"></i>
                        </button>
                        <button class="action-btn" id="refreshChart" title="Refresh Data">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        if (!document.getElementById('chartControls')) {
            document.body.insertAdjacentHTML('beforeend', controlsHTML);
        }
    }

    bindEvents() {
        // Chart type selection
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', this.debounce((e) => {
                document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
                e.target.closest('.chart-type-btn').classList.add('active');
                this.updateChartType(e.target.closest('.chart-type-btn').dataset.type);
            }, 300));
        });

        // Time range selection
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', this.debounce((e) => {
                document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateTimeRange(e.target.dataset.range);
            }, 300));
        });

        // Technical indicators
        document.querySelectorAll('.indicator-btn').forEach(btn => {
            btn.addEventListener('click', this.debounce((e) => {
                e.target.classList.toggle('active');
                this.toggleIndicator(e.target.dataset.indicator);
            }, 300));
        });

        // Chart actions
        document.getElementById('fullscreenChart')?.addEventListener('click', () => this.toggleFullscreen());
        document.getElementById('downloadChart')?.addEventListener('click', () => this.downloadChart());
        document.getElementById('shareChart')?.addEventListener('click', () => this.shareChart());
        document.getElementById('themeToggle')?.addEventListener('click', () => this.toggleTheme());
        document.getElementById('refreshChart')?.addEventListener('click', () => this.refreshAllCharts());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'd':
                        e.preventDefault();
                        this.downloadChart();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.toggleFullscreen();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshAllCharts();
                        break;
                }
            }
        });
    }

    // Performance optimization: Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Lazy loading: Only create charts when visible
    observeChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (canvas && this.chartObserver) {
            this.chartObserver.observe(canvas);
        }
    }

    async createAdvancedStockChart(canvasId, symbol, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`Canvas with ID ${canvasId} not found`);
            return null;
        }

        // Show loading state
        this.showChartLoading(canvasId);

        try {
            // Fetch data from backend database
            const chartData = await this.fetchStockData(symbol, options.timeRange || '1W');
            
            if (!chartData || !chartData.success) {
                this.showChartError(canvasId, 'Failed to load stock data');
                return null;
            }

            const ctx = canvas.getContext('2d');
            const config = this.buildChartConfig(symbol, chartData.data, options);
            
            // Performance monitoring
            const renderStart = performance.now();
            const chart = new Chart(ctx, config);
            const renderTime = performance.now() - renderStart;
            
            this.performanceMetrics.chartRenderTimes.push({
                canvasId,
                symbol,
                renderTime,
                timestamp: Date.now()
            });

            // Store chart reference
            this.charts.set(canvasId, { 
                chart, 
                symbol, 
                data: chartData.data,
                options,
                lastUpdate: Date.now()
            });
            
            // Cache data for performance
            this.dataCache.set(`${symbol}_${options.timeRange || '1W'}`, {
                data: chartData.data,
                timestamp: Date.now(),
                ttl: 300000 // 5 minutes
            });

            // Setup real-time updates only for visible charts
            if (this.observedCharts.has(canvasId)) {
                this.startRealTimeUpdates(canvasId);
            }

            this.hideChartLoading(canvasId);
            return chart;

        } catch (error) {
            console.error('Error creating chart:', error);
            this.showChartError(canvasId, 'Error loading chart data');
            return null;
        }
    }

    buildChartConfig(symbol, data, options) {
        const theme = this.themes[this.currentTheme];
        const isPositive = data.trend > 0;
        
        return {
            type: options.type || 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: symbol,
                    data: data.prices,
                    borderColor: isPositive ? theme.positive : theme.negative,
                    backgroundColor: isPositive ? 
                        `${theme.positive}20` : 
                        `${theme.negative}20`,
                    borderWidth: 2,
                    fill: options.type === 'area',
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: theme.background,
                    pointHoverBorderWidth: 2,
                    // Performance optimization: Skip points when zoomed out
                    pointSkip: data.labels.length > 100 ? 2 : 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: theme.background,
                        titleColor: theme.text,
                        bodyColor: theme.text,
                        borderColor: theme.grid,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (context) => `${symbol} - ${context[0].label}`,
                            label: (context) => {
                                const price = context.parsed.y;
                                const volume = data.volumes?.[context.dataIndex];
                                const result = [`Price: $${price.toFixed(2)}`];
                                if (volume) {
                                    result.push(`Volume: ${this.formatVolume(volume)}`);
                                }
                                return result;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: theme.grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.text,
                            maxTicksLimit: 8,
                            // Performance: Skip labels when too many
                            callback: function(value, index) {
                                if (this.getLabelForValue(value).length > 50 && index % 2 !== 0) {
                                    return '';
                                }
                                return this.getLabelForValue(value);
                            }
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: theme.grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.text,
                            callback: (value) => `$${value.toFixed(2)}`
                        }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                hover: {
                    animationDuration: 200
                },
                // Performance optimizations
                parsing: false,
                normalized: true,
                spanGaps: true
            }
        };
    }

    async fetchStockData(symbol, timeRange = '1W') {
        // Check cache first
        const cacheKey = `${symbol}_${timeRange}`;
        const cached = this.dataCache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < cached.ttl) {
            return { success: true, data: cached.data };
        }

        const fetchStart = performance.now();
        
        try {
            const response = await fetch(`${this.apiEndpoints.historicalData}${symbol}?range=${timeRange}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': stockScannerAjax?.nonce || ''
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const fetchTime = performance.now() - fetchStart;
            
            this.performanceMetrics.dataFetchTimes.push({
                symbol,
                timeRange,
                fetchTime,
                timestamp: Date.now()
            });

            // Cache the data
            this.dataCache.set(cacheKey, {
                data: data,
                timestamp: Date.now(),
                ttl: 300000 // 5 minutes
            });

            return { success: true, data: data };

        } catch (error) {
            console.error('Error fetching stock data:', error);
            return { success: false, error: error.message };
        }
    }

    async fetchRealTimeData(symbol) {
        try {
            const response = await fetch(`${this.apiEndpoints.realTimeData}${symbol}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': stockScannerAjax?.nonce || ''
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            console.error('Error fetching real-time data:', error);
            return null;
        }
    }

    startRealTimeUpdates(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;

        // Clear existing interval
        if (this.updateIntervals.has(canvasId)) {
            clearInterval(this.updateIntervals.get(canvasId));
        }

        // Only update if chart is visible
        const interval = setInterval(async () => {
            if (this.observedCharts.has(canvasId)) {
                await this.updateChartData(canvasId);
            }
        }, 30000); // Update every 30 seconds

        this.updateIntervals.set(canvasId, interval);
    }

    pauseChartUpdates(canvasId) {
        if (this.updateIntervals.has(canvasId)) {
            clearInterval(this.updateIntervals.get(canvasId));
            this.updateIntervals.delete(canvasId);
        }
    }

    async updateChartData(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;

        const { chart, symbol } = chartInfo;
        
        try {
            const realTimeData = await this.fetchRealTimeData(symbol);
            
            if (realTimeData && realTimeData.success) {
                // Update chart with new data point
                const newData = realTimeData.data;
                
                chart.data.labels.push(newData.timestamp);
                chart.data.datasets[0].data.push(newData.price);
                
                // Keep only last 100 data points for performance
                if (chart.data.labels.length > 100) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }
                
                // Update without animation for real-time feel
                chart.update('none');
                
                // Update last update timestamp
                chartInfo.lastUpdate = Date.now();
            }
        } catch (error) {
            console.error('Error updating chart data:', error);
        }
    }

    showChartLoading(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const container = canvas.parentElement;
        let loader = container.querySelector('.chart-loader');
        
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'chart-loader';
            loader.innerHTML = `
                <div class="loader-spinner"></div>
                <div class="loader-text">Loading chart data...</div>
            `;
            container.appendChild(loader);
        }
        
        loader.style.display = 'flex';
        canvas.style.opacity = '0.3';
    }

    hideChartLoading(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const container = canvas.parentElement;
        const loader = container.querySelector('.chart-loader');
        
        if (loader) {
            loader.style.display = 'none';
        }
        
        canvas.style.opacity = '1';
    }

    showChartError(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const container = canvas.parentElement;
        let error = container.querySelector('.chart-error');
        
        if (!error) {
            error = document.createElement('div');
            error.className = 'chart-error';
            container.appendChild(error);
        }
        
        error.innerHTML = `
            <div class="error-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="error-message">${message}</div>
            <button class="error-retry" onclick="window.AdvancedCharts.retryChart('${canvasId}')">
                Retry
            </button>
        `;
        
        error.style.display = 'flex';
        canvas.style.display = 'none';
    }

    async retryChart(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (chartInfo) {
            const { symbol, options } = chartInfo;
            
            // Hide error and show canvas
            const canvas = document.getElementById(canvasId);
            const container = canvas.parentElement;
            const error = container.querySelector('.chart-error');
            
            if (error) error.style.display = 'none';
            canvas.style.display = 'block';
            
            // Recreate chart
            await this.createAdvancedStockChart(canvasId, symbol, options);
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('chart-theme', this.currentTheme);
        
        const themeBtn = document.getElementById('themeToggle');
        const icon = themeBtn?.querySelector('i');
        
        if (icon) {
            if (this.currentTheme === 'dark') {
                icon.className = 'fas fa-sun';
                document.body.classList.add('dark-theme');
            } else {
                icon.className = 'fas fa-moon';
                document.body.classList.remove('dark-theme');
            }
        }
        
        // Update all charts with new theme
        this.charts.forEach((chartInfo, canvasId) => {
            this.updateChartTheme(canvasId);
        });
    }

    loadThemePreference() {
        if (this.currentTheme === 'dark') {
            document.body.classList.add('dark-theme');
            const icon = document.querySelector('#themeToggle i');
            if (icon) icon.className = 'fas fa-sun';
        }
    }

    updateChartTheme(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { chart } = chartInfo;
        const theme = this.themes[this.currentTheme];
        
        // Update chart colors
        if (chart.options.plugins?.tooltip) {
            chart.options.plugins.tooltip.backgroundColor = theme.background;
            chart.options.plugins.tooltip.titleColor = theme.text;
            chart.options.plugins.tooltip.bodyColor = theme.text;
            chart.options.plugins.tooltip.borderColor = theme.grid;
        }
        
        if (chart.options.scales?.x?.grid) {
            chart.options.scales.x.grid.color = theme.grid;
            chart.options.scales.x.ticks.color = theme.text;
        }
        
        if (chart.options.scales?.y?.grid) {
            chart.options.scales.y.grid.color = theme.grid;
            chart.options.scales.y.ticks.color = theme.text;
        }
        
        chart.update();
    }

    async refreshAllCharts() {
        const refreshPromises = [];
        
        this.charts.forEach((chartInfo, canvasId) => {
            const { symbol, options } = chartInfo;
            
            // Clear cache for this symbol
            const cacheKey = `${symbol}_${options.timeRange || '1W'}`;
            this.dataCache.delete(cacheKey);
            
            // Refresh chart data
            refreshPromises.push(this.updateChartData(canvasId));
        });
        
        try {
            await Promise.all(refreshPromises);
            this.showNotification('All charts refreshed successfully!', 'success');
        } catch (error) {
            this.showNotification('Error refreshing charts', 'error');
        }
    }

    formatVolume(volume) {
        if (volume >= 1000000000) {
            return (volume / 1000000000).toFixed(1) + 'B';
        } else if (volume >= 1000000) {
            return (volume / 1000000).toFixed(1) + 'M';
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(1) + 'K';
        }
        return volume.toLocaleString();
    }

    downloadChart(canvasId = null) {
        if (!canvasId) {
            canvasId = this.charts.keys().next().value;
        }
        
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { chart, symbol } = chartInfo;
        const canvas = chart.canvas;
        
        const link = document.createElement('a');
        link.download = `${symbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL('image/png', 1.0);
        link.click();
    }

    shareChart(canvasId = null) {
        if (!canvasId) {
            canvasId = this.charts.keys().next().value;
        }
        
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { symbol } = chartInfo;
        
        if (navigator.share) {
            navigator.share({
                title: `${symbol} Stock Chart`,
                text: `Check out this ${symbol} stock chart from Stock Scanner Pro`,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.showNotification('Chart link copied to clipboard!', 'success');
            });
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `chart-notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" class="notification-close">&times;</button>
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
            zIndex: '1002',
            fontSize: '14px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            maxWidth: '400px'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Performance monitoring methods
    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            cacheSize: this.dataCache.size,
            activeCharts: this.charts.size,
            observedCharts: this.observedCharts.size
        };
    }

    // Cleanup method for memory management
    cleanup() {
        // Clear all intervals
        this.updateIntervals.forEach(interval => clearInterval(interval));
        this.updateIntervals.clear();
        
        // Destroy all charts
        this.charts.forEach(chartInfo => {
            if (chartInfo.chart) {
                chartInfo.chart.destroy();
            }
        });
        this.charts.clear();
        
        // Clear cache
        this.dataCache.clear();
        
        // Disconnect observer
        if (this.chartObserver) {
            this.chartObserver.disconnect();
        }
        
        this.observedCharts.clear();
    }
}

// Initialize Advanced Chart System
document.addEventListener('DOMContentLoaded', function() {
    window.AdvancedCharts = new AdvancedChartSystem();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (window.AdvancedCharts) {
            window.AdvancedCharts.cleanup();
        }
    });
});

// Enhanced CSS for Chart System
const chartSystemCSS = `
<style>
.chart-controls-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
    pointer-events: none;
    transition: opacity 0.3s ease;
}

.chart-toolbar {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #e1e5e9;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    pointer-events: auto;
    flex-wrap: wrap;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.dark-theme .chart-toolbar {
    background: rgba(26, 26, 26, 0.95);
    border-bottom-color: #374151;
}

.chart-type-selector,
.time-range-selector,
.chart-indicators,
.chart-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.chart-type-btn,
.time-btn,
.indicator-btn,
.action-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.85rem;
    font-weight: 500;
    position: relative;
    overflow: hidden;
}

.chart-type-btn span {
    margin-left: 0.5rem;
}

.dark-theme .chart-type-btn,
.dark-theme .time-btn,
.dark-theme .indicator-btn,
.dark-theme .action-btn {
    background: #374151;
    border-color: #4b5563;
    color: #d1d5db;
}

.chart-type-btn:hover,
.time-btn:hover,
.indicator-btn:hover,
.action-btn:hover {
    background: #f8f9fa;
    border-color: #3685fb;
    color: #3685fb;
    transform: translateY(-1px);
}

.dark-theme .chart-type-btn:hover,
.dark-theme .time-btn:hover,
.dark-theme .indicator-btn:hover,
.dark-theme .action-btn:hover {
    background: #4b5563;
    border-color: #60a5fa;
    color: #60a5fa;
}

.chart-type-btn.active,
.time-btn.active,
.indicator-btn.active {
    background: #3685fb;
    border-color: #3685fb;
    color: white;
    box-shadow: 0 2px 8px rgba(54, 133, 251, 0.3);
}

.action-btn {
    padding: 0.5rem;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Chart Loading States */
.chart-loader {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.9);
    z-index: 10;
}

.dark-theme .chart-loader {
    background: rgba(26, 26, 26, 0.9);
}

.loader-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e1e5e9;
    border-top: 3px solid #3685fb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

.loader-text {
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
}

.dark-theme .loader-text {
    color: #d1d5db;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Chart Error States */
.chart-error {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.95);
    z-index: 10;
    padding: 2rem;
    text-align: center;
}

.dark-theme .chart-error {
    background: rgba(26, 26, 26, 0.95);
}

.error-icon {
    font-size: 3rem;
    color: #ef4444;
    margin-bottom: 1rem;
}

.error-message {
    color: #666;
    font-size: 1rem;
    margin-bottom: 1.5rem;
    max-width: 300px;
}

.dark-theme .error-message {
    color: #d1d5db;
}

.error-retry {
    padding: 0.75rem 1.5rem;
    background: #3685fb;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
}

.error-retry:hover {
    background: #2563eb;
}

/* Notification Styles */
.chart-notification {
    animation: slideIn 0.3s ease-out;
}

.notification-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .chart-toolbar {
        padding: 0.75rem 1rem;
        gap: 1rem;
    }
    
    .chart-type-selector,
    .time-range-selector,
    .chart-indicators {
        flex-wrap: wrap;
    }
    
    .chart-type-btn,
    .time-btn,
    .indicator-btn {
        padding: 0.375rem 0.75rem;
        font-size: 0.8rem;
    }
    
    .chart-type-btn span {
        display: none;
    }
}

/* Performance optimizations */
.chart-container {
    contain: layout style paint;
    will-change: transform;
}

.chart-container canvas {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: optimize-contrast;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', chartSystemCSS);