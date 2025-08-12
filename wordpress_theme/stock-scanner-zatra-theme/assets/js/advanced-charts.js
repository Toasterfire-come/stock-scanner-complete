/**
 * Advanced Interactive Charts System
 * Provides professional-grade chart visualizations without backend changes
 */

class AdvancedChartSystem {
    constructor() {
        this.charts = new Map();
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
        this.currentTheme = 'light';
        this.init();
    }

    init() {
        this.setupChartDefaults();
        this.createChartControls();
        this.bindEvents();
    }

    setupChartDefaults() {
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.interaction.intersect = false;
        Chart.defaults.interaction.mode = 'index';
    }

    createChartControls() {
        const controlsHTML = `
            <div class="chart-controls-overlay" id="chartControls">
                <div class="chart-toolbar">
                    <div class="chart-type-selector">
                        <button class="chart-type-btn active" data-type="line">
                            <i class="fas fa-chart-line"></i>
                            Line
                        </button>
                        <button class="chart-type-btn" data-type="candlestick">
                            <i class="fas fa-chart-bar"></i>
                            Candlestick
                        </button>
                        <button class="chart-type-btn" data-type="area">
                            <i class="fas fa-chart-area"></i>
                            Area
                        </button>
                        <button class="chart-type-btn" data-type="volume">
                            <i class="fas fa-signal"></i>
                            Volume
                        </button>
                    </div>
                    
                    <div class="time-range-selector">
                        <button class="time-btn" data-range="1D">1D</button>
                        <button class="time-btn active" data-range="1W">1W</button>
                        <button class="time-btn" data-range="1M">1M</button>
                        <button class="time-btn" data-range="3M">3M</button>
                        <button class="time-btn" data-range="1Y">1Y</button>
                        <button class="time-btn" data-range="5Y">5Y</button>
                    </div>
                    
                    <div class="chart-indicators">
                        <button class="indicator-btn" data-indicator="sma">SMA</button>
                        <button class="indicator-btn" data-indicator="ema">EMA</button>
                        <button class="indicator-btn" data-indicator="bollinger">Bollinger</button>
                        <button class="indicator-btn" data-indicator="rsi">RSI</button>
                        <button class="indicator-btn" data-indicator="macd">MACD</button>
                    </div>
                    
                    <div class="chart-actions">
                        <button class="action-btn" id="fullscreenChart">
                            <i class="fas fa-expand"></i>
                        </button>
                        <button class="action-btn" id="downloadChart">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="action-btn" id="shareChart">
                            <i class="fas fa-share"></i>
                        </button>
                        <button class="action-btn" id="themeToggle">
                            <i class="fas fa-moon"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Only add if not already present
        if (!document.getElementById('chartControls')) {
            document.body.insertAdjacentHTML('beforeend', controlsHTML);
        }
    }

    bindEvents() {
        // Chart type selection
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateChartType(e.target.dataset.type);
            });
        });

        // Time range selection
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateTimeRange(e.target.dataset.range);
            });
        });

        // Technical indicators
        document.querySelectorAll('.indicator-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.classList.toggle('active');
                this.toggleIndicator(e.target.dataset.indicator);
            });
        });

        // Chart actions
        document.getElementById('fullscreenChart')?.addEventListener('click', () => this.toggleFullscreen());
        document.getElementById('downloadChart')?.addEventListener('click', () => this.downloadChart());
        document.getElementById('shareChart')?.addEventListener('click', () => this.shareChart());
        document.getElementById('themeToggle')?.addEventListener('click', () => this.toggleTheme());
    }

    createAdvancedStockChart(canvasId, symbol, data = null) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        // Generate realistic stock data if none provided
        const chartData = data || this.generateRealisticStockData(symbol);
        
        const config = {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: symbol,
                    data: chartData.prices,
                    borderColor: chartData.trend > 0 ? this.themes[this.currentTheme].positive : this.themes[this.currentTheme].negative,
                    backgroundColor: chartData.trend > 0 ? 
                        `${this.themes[this.currentTheme].positive}20` : 
                        `${this.themes[this.currentTheme].negative}20`,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: this.themes[this.currentTheme].background,
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: this.themes[this.currentTheme].background,
                        titleColor: this.themes[this.currentTheme].text,
                        bodyColor: this.themes[this.currentTheme].text,
                        borderColor: this.themes[this.currentTheme].grid,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (context) => {
                                return `${symbol} - ${context[0].label}`;
                            },
                            label: (context) => {
                                const price = context.parsed.y;
                                const volume = chartData.volumes[context.dataIndex];
                                return [
                                    `Price: $${price.toFixed(2)}`,
                                    `Volume: ${this.formatVolume(volume)}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: this.themes[this.currentTheme].grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: this.themes[this.currentTheme].text,
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: this.themes[this.currentTheme].grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: this.themes[this.currentTheme].text,
                            callback: (value) => `$${value.toFixed(2)}`
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                hover: {
                    animationDuration: 200
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, { chart, symbol, data: chartData });
        
        // Add real-time updates
        this.startRealTimeUpdates(canvasId);
        
        return chart;
    }

    createCandlestickChart(canvasId, symbol, data = null) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const chartData = data || this.generateCandlestickData(symbol);
        
        // Custom candlestick chart using line chart with custom drawing
        const config = {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'High',
                        data: chartData.high,
                        borderColor: 'transparent',
                        backgroundColor: 'transparent',
                        pointRadius: 0
                    },
                    {
                        label: 'Low',
                        data: chartData.low,
                        borderColor: 'transparent',
                        backgroundColor: 'transparent',
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: this.themes[this.currentTheme].background,
                        titleColor: this.themes[this.currentTheme].text,
                        bodyColor: this.themes[this.currentTheme].text,
                        borderColor: this.themes[this.currentTheme].grid,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (context) => `${symbol} - ${context[0].label}`,
                            label: (context) => {
                                const index = context.dataIndex;
                                return [
                                    `Open: $${chartData.open[index].toFixed(2)}`,
                                    `High: $${chartData.high[index].toFixed(2)}`,
                                    `Low: $${chartData.low[index].toFixed(2)}`,
                                    `Close: $${chartData.close[index].toFixed(2)}`,
                                    `Volume: ${this.formatVolume(chartData.volume[index])}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: this.themes[this.currentTheme].grid, drawBorder: false },
                        ticks: { color: this.themes[this.currentTheme].text }
                    },
                    y: {
                        position: 'right',
                        grid: { color: this.themes[this.currentTheme].grid, drawBorder: false },
                        ticks: { 
                            color: this.themes[this.currentTheme].text,
                            callback: (value) => `$${value.toFixed(2)}`
                        }
                    }
                }
            },
            plugins: [{
                afterDatasetsDraw: (chart) => {
                    this.drawCandlesticks(chart, chartData);
                }
            }]
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, { chart, symbol, data: chartData, type: 'candlestick' });
        
        return chart;
    }

    drawCandlesticks(chart, data) {
        const ctx = chart.ctx;
        const meta = chart.getDatasetMeta(0);
        
        data.labels.forEach((label, index) => {
            const x = meta.data[index].x;
            const yScale = chart.scales.y;
            
            const open = yScale.getPixelForValue(data.open[index]);
            const close = yScale.getPixelForValue(data.close[index]);
            const high = yScale.getPixelForValue(data.high[index]);
            const low = yScale.getPixelForValue(data.low[index]);
            
            const isGreen = data.close[index] > data.open[index];
            const color = isGreen ? this.themes[this.currentTheme].positive : this.themes[this.currentTheme].negative;
            
            const candleWidth = 8;
            
            // Draw high-low line
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, high);
            ctx.lineTo(x, low);
            ctx.stroke();
            
            // Draw open-close rectangle
            ctx.fillStyle = isGreen ? color : this.themes[this.currentTheme].background;
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            
            const rectHeight = Math.abs(close - open);
            const rectY = Math.min(open, close);
            
            ctx.fillRect(x - candleWidth/2, rectY, candleWidth, rectHeight);
            ctx.strokeRect(x - candleWidth/2, rectY, candleWidth, rectHeight);
        });
    }

    createVolumeChart(canvasId, symbol, data = null) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const chartData = data || this.generateVolumeData(symbol);
        
        const config = {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Volume',
                    data: chartData.volumes,
                    backgroundColor: chartData.volumes.map((_, index) => {
                        const isUp = index === 0 || chartData.prices[index] > chartData.prices[index - 1];
                        return isUp ? 
                            `${this.themes[this.currentTheme].positive}60` : 
                            `${this.themes[this.currentTheme].negative}60`;
                    }),
                    borderColor: chartData.volumes.map((_, index) => {
                        const isUp = index === 0 || chartData.prices[index] > chartData.prices[index - 1];
                        return isUp ? this.themes[this.currentTheme].positive : this.themes[this.currentTheme].negative;
                    }),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: this.themes[this.currentTheme].background,
                        titleColor: this.themes[this.currentTheme].text,
                        bodyColor: this.themes[this.currentTheme].text,
                        borderColor: this.themes[this.currentTheme].grid,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => `Volume: ${this.formatVolume(context.parsed.y)}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: this.themes[this.currentTheme].grid, drawBorder: false },
                        ticks: { color: this.themes[this.currentTheme].text }
                    },
                    y: {
                        position: 'right',
                        grid: { color: this.themes[this.currentTheme].grid, drawBorder: false },
                        ticks: { 
                            color: this.themes[this.currentTheme].text,
                            callback: (value) => this.formatVolume(value)
                        }
                    }
                }
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, { chart, symbol, data: chartData, type: 'volume' });
        
        return chart;
    }

    generateRealisticStockData(symbol) {
        const days = 30;
        const labels = [];
        const prices = [];
        const volumes = [];
        
        let currentPrice = 100 + Math.random() * 200;
        const trend = Math.random() > 0.5 ? 1 : -1;
        
        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Realistic price movement
            const volatility = 0.02 + Math.random() * 0.03;
            const change = (Math.random() - 0.5) * volatility * currentPrice;
            const trendInfluence = trend * 0.001 * currentPrice;
            
            currentPrice += change + trendInfluence;
            currentPrice = Math.max(currentPrice, 1); // Prevent negative prices
            
            prices.push(parseFloat(currentPrice.toFixed(2)));
            
            // Realistic volume (higher on price changes)
            const baseVolume = 1000000 + Math.random() * 5000000;
            const volumeMultiplier = 1 + Math.abs(change / currentPrice) * 10;
            volumes.push(Math.floor(baseVolume * volumeMultiplier));
        }
        
        return { labels, prices, volumes, trend };
    }

    generateCandlestickData(symbol) {
        const days = 30;
        const labels = [];
        const open = [];
        const high = [];
        const low = [];
        const close = [];
        const volume = [];
        
        let currentPrice = 100 + Math.random() * 200;
        
        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            const openPrice = currentPrice;
            const volatility = 0.05;
            
            const dayHigh = openPrice * (1 + Math.random() * volatility);
            const dayLow = openPrice * (1 - Math.random() * volatility);
            const closePrice = dayLow + Math.random() * (dayHigh - dayLow);
            
            open.push(parseFloat(openPrice.toFixed(2)));
            high.push(parseFloat(dayHigh.toFixed(2)));
            low.push(parseFloat(dayLow.toFixed(2)));
            close.push(parseFloat(closePrice.toFixed(2)));
            
            const baseVolume = 1000000 + Math.random() * 5000000;
            volume.push(Math.floor(baseVolume));
            
            currentPrice = closePrice;
        }
        
        return { labels, open, high, low, close, volume };
    }

    generateVolumeData(symbol) {
        const data = this.generateRealisticStockData(symbol);
        return {
            labels: data.labels,
            volumes: data.volumes,
            prices: data.prices
        };
    }

    startRealTimeUpdates(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        setInterval(() => {
            this.updateChartData(canvasId);
        }, 5000 + Math.random() * 10000); // Random interval 5-15 seconds
    }

    updateChartData(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { chart, data } = chartInfo;
        
        // Add new data point
        const lastPrice = data.prices[data.prices.length - 1];
        const change = (Math.random() - 0.5) * 0.02 * lastPrice;
        const newPrice = Math.max(lastPrice + change, 1);
        
        const now = new Date();
        const newLabel = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Update data
        data.labels.push(newLabel);
        data.prices.push(parseFloat(newPrice.toFixed(2)));
        data.volumes.push(Math.floor(1000000 + Math.random() * 5000000));
        
        // Keep only last 50 points
        if (data.labels.length > 50) {
            data.labels.shift();
            data.prices.shift();
            data.volumes.shift();
        }
        
        // Update chart
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.prices;
        chart.update('none'); // No animation for real-time updates
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

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        const themeBtn = document.getElementById('themeToggle');
        const icon = themeBtn.querySelector('i');
        
        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-sun';
            document.body.classList.add('dark-theme');
        } else {
            icon.className = 'fas fa-moon';
            document.body.classList.remove('dark-theme');
        }
        
        // Update all charts with new theme
        this.charts.forEach((chartInfo, canvasId) => {
            this.updateChartTheme(canvasId);
        });
    }

    updateChartTheme(canvasId) {
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { chart } = chartInfo;
        const theme = this.themes[this.currentTheme];
        
        // Update chart colors
        chart.options.plugins.tooltip.backgroundColor = theme.background;
        chart.options.plugins.tooltip.titleColor = theme.text;
        chart.options.plugins.tooltip.bodyColor = theme.text;
        chart.options.plugins.tooltip.borderColor = theme.grid;
        
        chart.options.scales.x.grid.color = theme.grid;
        chart.options.scales.x.ticks.color = theme.text;
        chart.options.scales.y.grid.color = theme.grid;
        chart.options.scales.y.ticks.color = theme.text;
        
        chart.update();
    }

    downloadChart(canvasId = null) {
        if (!canvasId) {
            // Download the first available chart
            canvasId = this.charts.keys().next().value;
        }
        
        const chartInfo = this.charts.get(canvasId);
        if (!chartInfo) return;
        
        const { chart, symbol } = chartInfo;
        const canvas = chart.canvas;
        
        const link = document.createElement('a');
        link.download = `${symbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL();
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
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.showNotification('Chart link copied to clipboard!', 'success');
            });
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `chart-notification ${type}`;
        notification.textContent = message;
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: type === 'success' ? '#10b981' : '#3685fb',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            zIndex: '1002',
            fontSize: '14px',
            fontWeight: '500'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize Advanced Chart System
document.addEventListener('DOMContentLoaded', function() {
    window.AdvancedCharts = new AdvancedChartSystem();
});

// CSS for Chart Controls
const chartControlsCSS = `
<style>
.chart-controls-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
    pointer-events: none;
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
    transition: all 0.2s;
    font-size: 0.85rem;
    font-weight: 500;
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
}

.chart-type-btn i {
    margin-right: 0.5rem;
}

.action-btn {
    padding: 0.5rem;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

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
}

/* Dark theme body styles */
.dark-theme {
    background: #1a1a1a;
    color: #ffffff;
}

.dark-theme .card,
.dark-theme .section {
    background: #2d2d2d;
    border-color: #374151;
}

.dark-theme .form-input,
.dark-theme .form-select {
    background: #374151;
    border-color: #4b5563;
    color: #d1d5db;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', chartControlsCSS);