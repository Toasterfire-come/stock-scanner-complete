<?php
/**
 * Template Name: Stock Scanner Pro - Dashboard
 * 
 * Professional dashboard with Zatra theme styling
 */

// Redirect to login if not logged in
if (!is_user_logged_in()) {
    wp_redirect('/login/');
    exit;
}

get_header(); ?>

<main id="main" class="wp-block-group alignfull is-layout-constrained wp-block-group-is-layout-constrained" style="margin-top:0">
    
    <div class="wp-block-group__inner-container">
        <div class="container">
            <div class="stock-scanner-dashboard">
                
                <!-- Dashboard Header -->
                <div class="dashboard-header">
                    <div class="dashboard-title">
                        <h1 class="wp-block-heading has-large-font-size">Dashboard</h1>
                        <p class="has-text-color has-custom-color-2-color">Welcome back, <?php echo wp_get_current_user()->display_name; ?>!</p>
                    </div>
                    
                    <div class="user-info">
                        <?php 
                        $user_tier = get_user_tier();
                        $rate_limits = get_user_rate_limits();
                        ?>
                        <span class="user-tier tier-<?php echo $user_tier; ?>"><?php echo ucfirst($user_tier); ?> Plan</span>
                        <div class="api-usage">
                            <span class="usage-label">API Calls This Month:</span>
                            <span class="usage-count" id="api-usage-count">Loading...</span>
                            <span class="usage-limit">/ <?php echo $rate_limits['api_calls_per_month']; ?></span>
                        </div>
                    </div>
                </div>

                <!-- Dashboard Grid -->
                <div class="dashboard-grid">
                    
                    <!-- Quick Actions -->
                    <div class="dashboard-card quick-actions">
                        <h3>Quick Actions</h3>
                        <div class="action-buttons">
                            <a href="/stock-lookup/" class="action-btn">
                                <i class="fas fa-search"></i>
                                <span>Stock Lookup</span>
                            </a>
                            <a href="/stock-screener/" class="action-btn">
                                <i class="fas fa-filter"></i>
                                <span>Screen Stocks</span>
                            </a>
                            <a href="/watchlist/" class="action-btn">
                                <i class="fas fa-star"></i>
                                <span>My Watchlist</span>
                            </a>
                            <a href="/portfolio/" class="action-btn">
                                <i class="fas fa-briefcase"></i>
                                <span>Portfolio</span>
                            </a>
                        </div>
                    </div>

                    <!-- Market Overview -->
                    <div class="dashboard-card market-overview">
                        <h3>Market Overview</h3>
                        <div class="market-indices" id="market-indices">
                            <div class="index-item">
                                <span class="index-name">S&P 500</span>
                                <span class="index-value">Loading...</span>
                                <span class="index-change">--</span>
                            </div>
                            <div class="index-item">
                                <span class="index-name">NASDAQ</span>
                                <span class="index-value">Loading...</span>
                                <span class="index-change">--</span>
                            </div>
                            <div class="index-item">
                                <span class="index-name">DOW</span>
                                <span class="index-value">Loading...</span>
                                <span class="index-change">--</span>
                            </div>
                        </div>
                    </div>

                    <!-- Watchlist Preview -->
                    <div class="dashboard-card watchlist-preview">
                        <h3>My Watchlist</h3>
                        <div class="watchlist-items" id="watchlist-preview">
                            <div class="loading">Loading watchlist...</div>
                        </div>
                        <a href="/watchlist/" class="view-all-link">View All</a>
                    </div>

                    <!-- Recent News -->
                    <div class="dashboard-card recent-news">
                        <h3>Market News</h3>
                        <div class="news-items" id="recent-news">
                            <div class="loading">Loading news...</div>
                        </div>
                        <a href="/stock-news/" class="view-all-link">View All News</a>
                    </div>

                    <!-- Performance Chart or Upgrade Prompt -->
                    <?php if ($rate_limits['advanced_charts']): ?>
                        <div class="dashboard-card performance-chart">
                            <h3>Portfolio Performance</h3>
                            <div class="chart-container">
                                <canvas id="performance-chart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    <?php else: ?>
                        <div class="dashboard-card upgrade-prompt">
                            <div class="home-icon-wrap home-icon-wrap-1">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <h3>Advanced Charts</h3>
                            <p>Upgrade to access advanced portfolio performance charts and technical indicators.</p>
                            <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                        </div>
                    <?php endif; ?>

                    <!-- Account Summary -->
                    <div class="dashboard-card account-summary">
                        <h3>Account Summary</h3>
                        <div class="summary-stats">
                            <div class="summary-item">
                                <span class="summary-label">Plan</span>
                                <span class="summary-value"><?php echo ucfirst($user_tier); ?></span>
                            </div>
                            <div class="summary-item">
                                <span class="summary-label">Member Since</span>
                                <span class="summary-value"><?php echo date('M Y', strtotime(wp_get_current_user()->user_registered)); ?></span>
                            </div>
                            <div class="summary-item">
                                <span class="summary-label">API Limit</span>
                                <span class="summary-value"><?php echo $rate_limits['api_calls_per_month'] == 999999 ? 'Unlimited' : number_format($rate_limits['api_calls_per_month']); ?></span>
                            </div>
                        </div>
                        <div class="account-actions">
                            <a href="/account/" class="btn btn-outline btn-small">Manage Account</a>
                            <?php if ($user_tier === 'free'): ?>
                                <a href="/premium-plans/" class="btn btn-primary btn-small">Upgrade</a>
                            <?php endif; ?>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>

</main>

<style>
/* Dashboard-specific styles that complement Zatra theme */
.dashboard-title h1 {
    margin-bottom: 8px;
}

.dashboard-title p {
    margin: 0;
    font-size: 16px;
}

.index-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color);
}

.index-item:last-child {
    border-bottom: none;
}

.index-name {
    font-weight: 600;
    color: var(--text-color);
}

.index-value {
    font-family: var(--font-primary);
    font-weight: 600;
}

.index-change.positive {
    color: var(--success-color);
}

.index-change.negative {
    color: #ff6b6b;
}

.watchlist-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
}

.watchlist-item:last-child {
    border-bottom: none;
}

.stock-symbol {
    font-weight: 600;
    color: var(--primary-color);
}

.stock-price {
    font-family: var(--font-primary);
    font-weight: 600;
}

.stock-change.positive {
    color: var(--success-color);
}

.stock-change.negative {
    color: #ff6b6b;
}

.news-item {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
}

.news-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.news-item h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    line-height: 1.4;
}

.news-item h4 a {
    color: var(--text-color);
    text-decoration: none;
}

.news-item h4 a:hover {
    color: var(--primary-color);
}

.news-summary {
    font-size: 12px;
    color: var(--light-text);
    margin: 0 0 4px 0;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.news-time {
    font-size: 11px;
    color: var(--light-text);
}

.view-all-link {
    display: block;
    text-align: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
    font-size: 14px;
    color: var(--primary-color);
    text-decoration: none;
}

.view-all-link:hover {
    color: var(--accent-color);
}

.loading {
    text-align: center;
    color: var(--light-text);
    font-style: italic;
    padding: 20px 0;
}

.empty-state {
    text-align: center;
    color: var(--light-text);
    padding: 20px 0;
}

.empty-state a {
    color: var(--primary-color);
}

.summary-stats {
    margin-bottom: 20px;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
}

.summary-item:last-child {
    border-bottom: none;
}

.summary-label {
    font-size: 14px;
    color: var(--light-text);
}

.summary-value {
    font-weight: 600;
    color: var(--text-color);
}

.account-actions {
    display: flex;
    gap: 12px;
}

.btn-small {
    padding: 8px 16px;
    font-size: 14px;
    min-height: 36px;
}

.upgrade-prompt {
    text-align: center;
}

.upgrade-prompt .home-icon-wrap {
    margin: 0 auto 20px;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard data
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

function loadDashboardData() {
    // Load API usage
    fetch(stockScannerAjax.backend_url + 'user/api-usage/', {
        headers: {
            'X-WP-Nonce': stockScannerAjax.nonce
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.current_usage) {
            document.getElementById('api-usage-count').textContent = data.current_usage.this_month || 0;
        }
    })
    .catch(error => {
        console.error('Error loading API usage:', error);
        document.getElementById('api-usage-count').textContent = '0';
    });

    // Load market data
    fetch(stockScannerAjax.backend_url + 'market-stats/', {
        headers: {
            'X-WP-Nonce': stockScannerAjax.nonce
        }
    })
    .then(response => response.json())
    .then(data => {
        updateMarketIndices(data);
    })
    .catch(error => {
        console.error('Error loading market data:', error);
        updateMarketIndices(null);
    });

    // Load watchlist preview
    fetch(stockScannerAjax.backend_url + 'watchlist/', {
        headers: {
            'X-WP-Nonce': stockScannerAjax.nonce
        }
    })
    .then(response => response.json())
    .then(data => {
        updateWatchlistPreview(data);
    })
    .catch(error => {
        console.error('Error loading watchlist:', error);
        updateWatchlistPreview(null);
    });

    // Load recent news
    fetch(stockScannerAjax.backend_url + 'news/', {
        headers: {
            'X-WP-Nonce': stockScannerAjax.nonce
        }
    })
    .then(response => response.json())
    .then(data => {
        updateRecentNews(data);
    })
    .catch(error => {
        console.error('Error loading news:', error);
        updateRecentNews(null);
    });
}

function updateMarketIndices(data) {
    const container = document.getElementById('market-indices');
    
    if (data && data.indices) {
        let html = '';
        data.indices.forEach(index => {
            const changeClass = index.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="index-item">
                    <span class="index-name">${index.name}</span>
                    <span class="index-value">${index.value}</span>
                    <span class="index-change ${changeClass}">${index.change >= 0 ? '+' : ''}${index.change}%</span>
                </div>
            `;
        });
        container.innerHTML = html;
    } else {
        // Sample data for demonstration
        container.innerHTML = `
            <div class="index-item">
                <span class="index-name">S&P 500</span>
                <span class="index-value">4,567.89</span>
                <span class="index-change positive">+0.75%</span>
            </div>
            <div class="index-item">
                <span class="index-name">NASDAQ</span>
                <span class="index-value">14,234.56</span>
                <span class="index-change positive">+1.23%</span>
            </div>
            <div class="index-item">
                <span class="index-name">DOW</span>
                <span class="index-value">35,678.90</span>
                <span class="index-change negative">-0.45%</span>
            </div>
        `;
    }
}

function updateWatchlistPreview(data) {
    const container = document.getElementById('watchlist-preview');
    
    if (data && data.results && data.results.length > 0) {
        let html = '';
        data.results.slice(0, 5).forEach(stock => {
            const changeClass = stock.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="watchlist-item">
                    <span class="stock-symbol">${stock.ticker}</span>
                    <span class="stock-price">$${stock.current_price}</span>
                    <span class="stock-change ${changeClass}">${stock.change >= 0 ? '+' : ''}${stock.change}%</span>
                </div>
            `;
        });
        container.innerHTML = html;
    } else {
        container.innerHTML = '<div class="empty-state">No stocks in watchlist. <a href="/stock-lookup/">Add some stocks</a></div>';
    }
}

function updateRecentNews(data) {
    const container = document.getElementById('recent-news');
    
    if (data && data.results && data.results.length > 0) {
        let html = '';
        data.results.slice(0, 3).forEach(article => {
            html += `
                <div class="news-item">
                    <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
                    <p class="news-summary">${article.summary || article.description || 'No summary available.'}</p>
                    <span class="news-time">${new Date(article.published_at).toLocaleDateString()}</span>
                </div>
            `;
        });
        container.innerHTML = html;
    } else {
        // Sample news for demonstration
        container.innerHTML = `
            <div class="news-item">
                <h4><a href="#" target="_blank">Market Opens Higher on Strong Earnings</a></h4>
                <p class="news-summary">Major indices climb as tech companies report better-than-expected quarterly results...</p>
                <span class="news-time">${new Date().toLocaleDateString()}</span>
            </div>
            <div class="news-item">
                <h4><a href="#" target="_blank">Fed Signals Potential Rate Changes</a></h4>
                <p class="news-summary">Federal Reserve officials hint at policy adjustments in upcoming meetings...</p>
                <span class="news-time">${new Date().toLocaleDateString()}</span>
            </div>
        `;
    }
}

<?php if ($rate_limits['advanced_charts']): ?>
// Initialize performance chart for premium users
const ctx = document.getElementById('performance-chart').getContext('2d');
const performanceChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Portfolio Value',
            data: [10000, 10500, 10200, 11000, 11500, 12000],
            borderColor: '#3685fb',
            backgroundColor: 'rgba(54, 133, 251, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: '#e1e5e9'
                }
            },
            x: {
                grid: {
                    color: '#e1e5e9'
                }
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    }
});
<?php endif; ?>
</script>

<?php get_footer(); ?>