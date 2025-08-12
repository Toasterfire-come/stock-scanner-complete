<?php
/**
 * Template Name: Dashboard
 * 
 * The template for displaying the user dashboard
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="dashboard-container">
    <div class="dashboard-header">
        <div class="container">
            <h1 class="dashboard-title">
                <i class="fas fa-chart-line"></i>
                Dashboard
            </h1>
            <p class="dashboard-subtitle">Welcome back, <?php echo esc_html(wp_get_current_user()->display_name); ?>!</p>
        </div>
    </div>

    <div class="dashboard-content">
        <div class="container">
            <!-- Quick Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-wallet"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value" id="portfolio-value">Loading...</div>
                        <div class="stat-label">Portfolio Value</div>
                        <div class="stat-change positive" id="portfolio-change">+0.00%</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value" id="day-change">Loading...</div>
                        <div class="stat-label">Day's Change</div>
                        <div class="stat-change" id="day-change-percent">0.00%</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-eye"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value" id="watchlist-count">Loading...</div>
                        <div class="stat-label">Watchlist Items</div>
                        <div class="stat-change neutral">Active</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value" id="best-performer">Loading...</div>
                        <div class="stat-label">Best Performer</div>
                        <div class="stat-change positive" id="best-performer-change">+0.00%</div>
                    </div>
                </div>
            </div>

            <!-- Main Dashboard Grid -->
            <div class="dashboard-grid">
                <!-- Portfolio Overview -->
                <div class="dashboard-widget portfolio-widget">
                    <div class="widget-header">
                        <h3>Portfolio Overview</h3>
                        <a href="/portfolio/" class="view-all-btn">View All</a>
                    </div>
                    <div class="widget-content">
                        <div class="portfolio-chart-container">
                            <canvas id="portfolioChart" width="400" height="200"></canvas>
                        </div>
                        <div class="portfolio-holdings" id="portfolio-holdings">
                            <div class="loading-spinner">Loading portfolio...</div>
                        </div>
                    </div>
                </div>

                <!-- Watchlist Widget -->
                <div class="dashboard-widget watchlist-widget">
                    <div class="widget-header">
                        <h3>Your Watchlist</h3>
                        <a href="/watchlist/" class="view-all-btn">Manage</a>
                    </div>
                    <div class="widget-content">
                        <div class="watchlist-items" id="watchlist-items">
                            <div class="loading-spinner">Loading watchlist...</div>
                        </div>
                    </div>
                </div>

                <!-- Market Overview -->
                <div class="dashboard-widget market-widget">
                    <div class="widget-header">
                        <h3>Market Overview</h3>
                        <a href="/market-overview/" class="view-all-btn">View All</a>
                    </div>
                    <div class="widget-content">
                        <div class="market-indices" id="market-indices">
                            <div class="loading-spinner">Loading market data...</div>
                        </div>
                    </div>
                </div>

                <!-- Recent News -->
                <div class="dashboard-widget news-widget">
                    <div class="widget-header">
                        <h3>Market News</h3>
                        <a href="/stock-news/" class="view-all-btn">Read More</a>
                    </div>
                    <div class="widget-content">
                        <div class="news-feed" id="news-feed">
                            <div class="loading-spinner">Loading news...</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="quick-actions">
                <h3>Quick Actions</h3>
                <div class="action-buttons">
                    <a href="/stock-lookup/" class="action-btn">
                        <i class="fas fa-search"></i>
                        Stock Lookup
                    </a>
                    <a href="/stock-screener/" class="action-btn">
                        <i class="fas fa-filter"></i>
                        Stock Screener
                    </a>
                    <a href="/portfolio/" class="action-btn">
                        <i class="fas fa-briefcase"></i>
                        Portfolio
                    </a>
                    <a href="/premium-plans/" class="action-btn premium-btn">
                        <i class="fas fa-crown"></i>
                        Upgrade to Premium
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.dashboard-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.dashboard-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 2rem 0;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.dashboard-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0.5rem 0 0 0;
}

.dashboard-content {
    padding: 2rem 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
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
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a1a;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
    margin: 0.25rem 0;
}

.stat-change {
    font-size: 0.9rem;
    font-weight: 600;
}

.stat-change.positive { color: #10b981; }
.stat-change.negative { color: #ef4444; }
.stat-change.neutral { color: #6b7280; }

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.dashboard-widget {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.widget-header {
    padding: 1.5rem 1.5rem 0 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.widget-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.view-all-btn {
    color: #3685fb;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
}

.widget-content {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
}

.loading-spinner {
    text-align: center;
    color: #666;
    padding: 2rem;
}

.quick-actions {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.quick-actions h3 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.action-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    color: #1a1a1a;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
}

.action-btn:hover {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.premium-btn {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    border-color: #f59e0b;
}

.premium-btn:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        grid-template-columns: 1fr;
    }
    
    .dashboard-title {
        font-size: 2rem;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard data
    loadDashboardData();
    
    // Set up real-time updates
    setInterval(loadDashboardData, 60000); // Update every minute
});

function loadDashboardData() {
    // Load portfolio data
    loadPortfolioData();
    
    // Load watchlist data
    loadWatchlistData();
    
    // Load market data
    loadMarketData();
    
    // Load news data
    loadNewsData();
}

function loadPortfolioData() {
    // This would make an AJAX call to get portfolio data from the backend
    // For now, we'll use placeholder data
    const portfolioData = {
        value: '$125,430.67',
        change: '+2,340.56',
        changePercent: '+1.90%',
        holdings: [
            { symbol: 'AAPL', name: 'Apple Inc.', shares: 100, value: '$17,500', change: '+2.3%' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 50, value: '$13,750', change: '-0.8%' },
            { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 75, value: '$25,125', change: '+1.5%' }
        ]
    };
    
    // Update portfolio stats
    document.getElementById('portfolio-value').textContent = portfolioData.value;
    document.getElementById('day-change').textContent = portfolioData.change;
    document.getElementById('day-change-percent').textContent = portfolioData.changePercent;
    document.getElementById('day-change-percent').className = 'stat-change ' + 
        (portfolioData.change.startsWith('+') ? 'positive' : 'negative');
    
    // Update portfolio holdings
    const holdingsContainer = document.getElementById('portfolio-holdings');
    holdingsContainer.innerHTML = portfolioData.holdings.map(stock => `
        <div class="holding-item">
            <div class="holding-info">
                <strong>${stock.symbol}</strong>
                <span>${stock.name}</span>
            </div>
            <div class="holding-value">
                <div>${stock.value}</div>
                <div class="change ${stock.change.startsWith('+') ? 'positive' : 'negative'}">${stock.change}</div>
            </div>
        </div>
    `).join('');
}

function loadWatchlistData() {
    // Load watchlist from backend
    const watchlistData = [
        { symbol: 'TSLA', name: 'Tesla Inc.', price: '$245.67', change: '+3.2%' },
        { symbol: 'NVDA', name: 'NVIDIA Corp.', price: '$892.34', change: '+5.7%' },
        { symbol: 'AMD', name: 'Advanced Micro Devices', price: '$142.89', change: '-1.2%' }
    ];
    
    document.getElementById('watchlist-count').textContent = watchlistData.length;
    
    const watchlistContainer = document.getElementById('watchlist-items');
    watchlistContainer.innerHTML = watchlistData.map(stock => `
        <div class="watchlist-item">
            <div class="stock-info">
                <strong>${stock.symbol}</strong>
                <span>${stock.name}</span>
            </div>
            <div class="stock-price">
                <div>${stock.price}</div>
                <div class="change ${stock.change.startsWith('+') ? 'positive' : 'negative'}">${stock.change}</div>
            </div>
        </div>
    `).join('');
}

function loadMarketData() {
    // Load market indices
    const marketData = [
        { name: 'S&P 500', value: '4,567.23', change: '+1.2%' },
        { name: 'NASDAQ', value: '14,234.56', change: '+2.1%' },
        { name: 'DOW', value: '34,567.89', change: '+0.8%' }
    ];
    
    const marketContainer = document.getElementById('market-indices');
    marketContainer.innerHTML = marketData.map(index => `
        <div class="market-item">
            <div class="index-name">${index.name}</div>
            <div class="index-value">${index.value}</div>
            <div class="change ${index.change.startsWith('+') ? 'positive' : 'negative'}">${index.change}</div>
        </div>
    `).join('');
}

function loadNewsData() {
    // Load recent news
    const newsData = [
        { title: 'Market Rally Continues as Tech Stocks Surge', time: '2 hours ago' },
        { title: 'Federal Reserve Announces Interest Rate Decision', time: '4 hours ago' },
        { title: 'Earnings Season Kicks Off with Strong Results', time: '6 hours ago' }
    ];
    
    const newsContainer = document.getElementById('news-feed');
    newsContainer.innerHTML = newsData.map(news => `
        <div class="news-item">
            <div class="news-title">${news.title}</div>
            <div class="news-time">${news.time}</div>
        </div>
    `).join('');
}
</script>

<?php get_footer(); ?>