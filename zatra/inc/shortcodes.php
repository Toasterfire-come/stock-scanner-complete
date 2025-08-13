<?php
/**
 * Stock Scanner Pro Shortcode Implementations
 * 
 * All shortcodes for pages, features, and functionality
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Homepage Shortcode
 */
function render_homepage_shortcode($atts) {
    $user_tier = get_user_tier();
    $rate_limits = get_user_rate_limits();
    
    ob_start();
    ?>
    <div class="stock-scanner-homepage">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1>Professional Stock Analysis Made Simple</h1>
                <p class="hero-subtitle">Get real-time stock data, advanced charts, and powerful screening tools to make informed investment decisions.</p>
                
                <?php if (!is_user_logged_in()): ?>
                    <div class="hero-cta">
                        <a href="/signup/" class="btn btn-primary btn-large">Start Free Trial</a>
                        <a href="/premium-plans/" class="btn btn-secondary btn-large">View Plans</a>
                    </div>
                <?php else: ?>
                    <div class="hero-cta">
                        <a href="/dashboard/" class="btn btn-primary btn-large">Go to Dashboard</a>
                        <?php if ($user_tier === 'free'): ?>
                            <a href="/premium-plans/" class="btn btn-secondary btn-large">Upgrade Now</a>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
            </div>
            
            <div class="hero-stats">
                <div class="stat-item">
                    <span class="stat-number">10,000+</span>
                    <span class="stat-label">Stocks Tracked</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">Real-time</span>
                    <span class="stat-label">Market Data</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">24/7</span>
                    <span class="stat-label">Support</span>
                </div>
            </div>
        </section>

        <!-- Features Grid -->
        <section class="features-section">
            <div class="container">
                <h2>Powerful Features for Every Investor</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Advanced Charts</h3>
                        <p>Interactive charts with technical indicators, candlestick patterns, and volume analysis.</p>
                        <?php if ($user_tier === 'free'): ?>
                            <span class="feature-badge">Premium</span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">🔍</div>
                        <h3>Stock Screener</h3>
                        <p>Filter stocks by price, volume, market cap, P/E ratio, and dozens of other criteria.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">📈</div>
                        <h3>Real-time Data</h3>
                        <p>Live market data with instant updates and price alerts for your watchlist.</p>
                        <?php if ($user_tier === 'free'): ?>
                            <span class="feature-badge">Premium</span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">💼</div>
                        <h3>Portfolio Tracking</h3>
                        <p>Track your investments with performance analytics and profit/loss calculations.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">📰</div>
                        <h3>Market News</h3>
                        <p>Stay informed with personalized news feeds and market analysis.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>Fast & Reliable</h3>
                        <p>Lightning-fast data delivery with 99.9% uptime guarantee.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Pricing Preview -->
        <section class="pricing-preview">
            <div class="container">
                <h2>Choose Your Plan</h2>
                <div class="pricing-cards">
                    <div class="pricing-card <?php echo $user_tier === 'free' ? 'current' : ''; ?>">
                        <h3>Free</h3>
                        <div class="price">$0<span>/month</span></div>
                        <ul class="features-list">
                            <li>15 API calls/month</li>
                            <li>3 watchlist items</li>
                            <li>Basic charts</li>
                            <li>Delayed data</li>
                        </ul>
                        <?php if ($user_tier !== 'free'): ?>
                            <button class="btn btn-outline" disabled>Current Plan</button>
                        <?php endif; ?>
                    </div>
                    
                    <div class="pricing-card featured <?php echo $user_tier === 'basic' ? 'current' : ''; ?>">
                        <h3>Basic</h3>
                        <div class="price">$24.99<span>/month</span></div>
                        <ul class="features-list">
                            <li>1,500 API calls/month</li>
                            <li>25 watchlist items</li>
                            <li>Real-time data</li>
                            <li>Advanced charts</li>
                            <li>Data export</li>
                        </ul>
                        <?php if ($user_tier === 'free'): ?>
                            <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                        <?php elseif ($user_tier === 'basic'): ?>
                            <button class="btn btn-outline" disabled>Current Plan</button>
                        <?php endif; ?>
                    </div>
                    
                    <div class="pricing-card <?php echo $user_tier === 'pro' ? 'current' : ''; ?>">
                        <h3>Pro</h3>
                        <div class="price">$49.99<span>/month</span></div>
                        <ul class="features-list">
                            <li>5,000 API calls/month</li>
                            <li>100 watchlist items</li>
                            <li>API access</li>
                            <li>Custom alerts</li>
                            <li>Priority support</li>
                        </ul>
                        <?php if (in_array($user_tier, ['free', 'basic'])): ?>
                            <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                        <?php elseif ($user_tier === 'pro'): ?>
                            <button class="btn btn-outline" disabled>Current Plan</button>
                        <?php endif; ?>
                    </div>
                </div>
                
                <div class="pricing-cta">
                    <a href="/premium-plans/" class="btn btn-large">View All Plans</a>
                </div>
            </div>
        </section>

        <!-- Testimonials -->
        <section class="testimonials-section">
            <div class="container">
                <h2>What Our Users Say</h2>
                <div class="testimonials-grid">
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"The real-time data and advanced charts have completely transformed my trading strategy. Highly recommended!"</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Sarah Johnson</strong>
                            <span>Day Trader</span>
                        </div>
                    </div>
                    
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"Best stock screening tool I've used. The filtering options are incredibly detailed and accurate."</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Michael Chen</strong>
                            <span>Investment Advisor</span>
                        </div>
                    </div>
                    
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"The portfolio tracking feature helps me stay on top of all my investments. Great value for money."</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Emily Rodriguez</strong>
                            <span>Retail Investor</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <script>
    // Add interactive elements
    document.addEventListener('DOMContentLoaded', function() {
        // Animate stats on scroll
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, observerOptions);
        
        document.querySelectorAll('.stat-item, .feature-card').forEach(el => {
            observer.observe(el);
        });
    });
    </script>
    <?php
    return ob_get_clean();
}

/**
 * Dashboard Shortcode
 */
function render_dashboard_shortcode($atts) {
    if (!is_user_logged_in()) {
        return '<div class="login-required">Please <a href="/login/">login</a> to access your dashboard.</div>';
    }
    
    $user_tier = get_user_tier();
    $rate_limits = get_user_rate_limits();
    
    ob_start();
    ?>
    <div class="stock-scanner-dashboard">
        <div class="dashboard-header">
            <h1>Dashboard</h1>
            <div class="user-info">
                <span class="user-tier tier-<?php echo $user_tier; ?>"><?php echo ucfirst($user_tier); ?> Plan</span>
                <div class="api-usage">
                    <span class="usage-label">API Calls This Month:</span>
                    <span class="usage-count" id="api-usage-count">Loading...</span>
                    <span class="usage-limit">/ <?php echo $rate_limits['api_calls_per_month']; ?></span>
                </div>
            </div>
        </div>

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

            <!-- Performance Chart -->
            <?php if ($rate_limits['advanced_charts']): ?>
            <div class="dashboard-card performance-chart">
                <h3>Portfolio Performance</h3>
                <canvas id="performance-chart" width="400" height="200"></canvas>
            </div>
            <?php else: ?>
            <div class="dashboard-card upgrade-prompt">
                <h3>Advanced Charts</h3>
                <p>Upgrade to access advanced portfolio performance charts and technical indicators.</p>
                <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
            </div>
            <?php endif; ?>
        </div>
    </div>

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
        .catch(error => console.error('Error loading API usage:', error));

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
        .catch(error => console.error('Error loading market data:', error));

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
        .catch(error => console.error('Error loading watchlist:', error));

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
        .catch(error => console.error('Error loading news:', error));
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
                        <p class="news-summary">${article.summary || article.description}</p>
                        <span class="news-time">${new Date(article.published_at).toLocaleDateString()}</span>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="empty-state">No recent news available.</div>';
        }
    }

    <?php if ($rate_limits['advanced_charts']): ?>
    // Initialize performance chart
    const ctx = document.getElementById('performance-chart').getContext('2d');
    const performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Portfolio Value',
                data: [10000, 10500, 10200, 11000, 11500, 12000],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    <?php endif; ?>
    </script>
    <?php
    return ob_get_clean();
}

/**
 * Stock Lookup Shortcode
 */
function render_stock_lookup_shortcode($atts) {
    ob_start();
    ?>
    <div class="stock-lookup-tool">
        <div class="lookup-header">
            <h1>Stock Lookup</h1>
            <p>Search for detailed information on any stock symbol</p>
        </div>

        <div class="search-container">
            <div class="search-box">
                <input type="text" id="stock-search" placeholder="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)" autocomplete="off">
                <button id="search-btn" class="btn btn-primary">
                    <i class="fas fa-search"></i>
                    Search
                </button>
            </div>
            <div class="search-suggestions" id="search-suggestions"></div>
        </div>

        <div class="stock-result" id="stock-result" style="display: none;">
            <div class="stock-header">
                <div class="stock-info">
                    <h2 class="stock-name" id="stock-name"></h2>
                    <span class="stock-symbol" id="stock-symbol"></span>
                    <span class="stock-exchange" id="stock-exchange"></span>
                </div>
                <div class="stock-price">
                    <span class="current-price" id="current-price"></span>
                    <span class="price-change" id="price-change"></span>
                    <span class="change-percent" id="change-percent"></span>
                </div>
                <div class="stock-actions">
                    <button class="btn btn-outline" id="add-to-watchlist">
                        <i class="fas fa-star"></i>
                        Add to Watchlist
                    </button>
                    <button class="btn btn-outline" id="add-to-portfolio">
                        <i class="fas fa-briefcase"></i>
                        Add to Portfolio
                    </button>
                </div>
            </div>

            <div class="stock-details">
                <div class="details-grid">
                    <div class="detail-card">
                        <h3>Key Statistics</h3>
                        <div class="stats-grid" id="key-stats">
                            <!-- Will be populated by JavaScript -->
                        </div>
                    </div>

                    <div class="detail-card">
                        <h3>Price Chart</h3>
                        <div class="chart-container">
                            <canvas id="price-chart" width="400" height="200"></canvas>
                        </div>
                        <div class="chart-controls">
                            <button class="chart-period active" data-period="1D">1D</button>
                            <button class="chart-period" data-period="5D">5D</button>
                            <button class="chart-period" data-period="1M">1M</button>
                            <button class="chart-period" data-period="3M">3M</button>
                            <button class="chart-period" data-period="1Y">1Y</button>
                        </div>
                    </div>

                    <div class="detail-card">
                        <h3>Company Information</h3>
                        <div class="company-info" id="company-info">
                            <!-- Will be populated by JavaScript -->
                        </div>
                    </div>

                    <div class="detail-card">
                        <h3>Recent News</h3>
                        <div class="stock-news" id="stock-news">
                            <!-- Will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="loading-indicator" id="loading-indicator" style="display: none;">
            <div class="spinner"></div>
            <p>Loading stock data...</p>
        </div>

        <div class="error-message" id="error-message" style="display: none;">
            <i class="fas fa-exclamation-triangle"></i>
            <span id="error-text"></span>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('stock-search');
        const searchBtn = document.getElementById('search-btn');
        const suggestionsContainer = document.getElementById('search-suggestions');
        let searchTimeout;

        // Search functionality
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Auto-suggestions
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSuggestions(query);
                }, 300);
            } else {
                suggestionsContainer.style.display = 'none';
            }
        });

        function performSearch() {
            const symbol = searchInput.value.trim().toUpperCase();
            if (!symbol) return;

            showLoading();
            hideError();
            
            fetch(stockScannerAjax.backend_url + 'stock/' + symbol + '/', {
                headers: {
                    'X-WP-Nonce': stockScannerAjax.nonce
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.error) {
                    showError(data.error);
                } else {
                    displayStockData(data);
                }
            })
            .catch(error => {
                hideLoading();
                showError('Failed to fetch stock data. Please try again.');
                console.error('Error:', error);
            });
        }

        function fetchSuggestions(query) {
            fetch(stockScannerAjax.backend_url + 'search/?q=' + encodeURIComponent(query) + '&limit=5', {
                headers: {
                    'X-WP-Nonce': stockScannerAjax.nonce
                }
            })
            .then(response => response.json())
            .then(data => {
                displaySuggestions(data.results || []);
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
            });
        }

        function displaySuggestions(suggestions) {
            if (suggestions.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }

            let html = '';
            suggestions.forEach(stock => {
                html += `
                    <div class="suggestion-item" data-symbol="${stock.ticker}">
                        <span class="suggestion-symbol">${stock.ticker}</span>
                        <span class="suggestion-name">${stock.company_name}</span>
                    </div>
                `;
            });

            suggestionsContainer.innerHTML = html;
            suggestionsContainer.style.display = 'block';

            // Add click handlers to suggestions
            suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', function() {
                    searchInput.value = this.dataset.symbol;
                    suggestionsContainer.style.display = 'none';
                    performSearch();
                });
            });
        }

        function displayStockData(data) {
            // Populate stock information
            document.getElementById('stock-name').textContent = data.company_name || data.name;
            document.getElementById('stock-symbol').textContent = data.ticker || data.symbol;
            document.getElementById('stock-exchange').textContent = data.exchange || 'NYSE';
            document.getElementById('current-price').textContent = '$' + (data.current_price || data.price || '0.00');
            
            const change = data.change || 0;
            const changePercent = data.change_percent || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            
            document.getElementById('price-change').textContent = (change >= 0 ? '+' : '') + change.toFixed(2);
            document.getElementById('price-change').className = 'price-change ' + changeClass;
            document.getElementById('change-percent').textContent = '(' + (changePercent >= 0 ? '+' : '') + changePercent.toFixed(2) + '%)';
            document.getElementById('change-percent').className = 'change-percent ' + changeClass;

            // Populate key statistics
            const keyStats = document.getElementById('key-stats');
            keyStats.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Market Cap</span>
                    <span class="stat-value">${data.market_cap || 'N/A'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">P/E Ratio</span>
                    <span class="stat-value">${data.pe_ratio || 'N/A'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Volume</span>
                    <span class="stat-value">${data.volume || 'N/A'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">52W High</span>
                    <span class="stat-value">$${data.week_52_high || 'N/A'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">52W Low</span>
                    <span class="stat-value">$${data.week_52_low || 'N/A'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Dividend Yield</span>
                    <span class="stat-value">${data.dividend_yield || 'N/A'}%</span>
                </div>
            `;

            // Show the result
            document.getElementById('stock-result').style.display = 'block';
            
            // Initialize chart
            initializePriceChart(data);
            
            // Load additional data
            loadStockNews(data.ticker || data.symbol);
        }

        function initializePriceChart(stockData) {
            const ctx = document.getElementById('price-chart').getContext('2d');
            
            // Sample chart data (in real implementation, fetch from API)
            const chartData = {
                labels: ['9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00'],
                datasets: [{
                    label: 'Price',
                    data: generateSamplePriceData(stockData.current_price || 100, 14),
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            };

            new Chart(ctx, {
                type: 'line',
                data: chartData,
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
        }

        function generateSamplePriceData(basePrice, count) {
            const data = [];
            let currentPrice = basePrice;
            
            for (let i = 0; i < count; i++) {
                const change = (Math.random() - 0.5) * 2; // Random change between -1 and 1
                currentPrice += change;
                data.push(currentPrice.toFixed(2));
            }
            
            return data;
        }

        function loadStockNews(symbol) {
            fetch(stockScannerAjax.backend_url + 'news/?symbol=' + symbol + '&limit=3', {
                headers: {
                    'X-WP-Nonce': stockScannerAjax.nonce
                }
            })
            .then(response => response.json())
            .then(data => {
                const newsContainer = document.getElementById('stock-news');
                if (data.results && data.results.length > 0) {
                    let html = '';
                    data.results.forEach(article => {
                        html += `
                            <div class="news-item">
                                <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
                                <p class="news-summary">${article.summary || article.description}</p>
                                <span class="news-time">${new Date(article.published_at).toLocaleDateString()}</span>
                            </div>
                        `;
                    });
                    newsContainer.innerHTML = html;
                } else {
                    newsContainer.innerHTML = '<div class="empty-state">No recent news available for this stock.</div>';
                }
            })
            .catch(error => {
                console.error('Error loading stock news:', error);
                document.getElementById('stock-news').innerHTML = '<div class="error-state">Failed to load news.</div>';
            });
        }

        function showLoading() {
            document.getElementById('loading-indicator').style.display = 'block';
            document.getElementById('stock-result').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loading-indicator').style.display = 'none';
        }

        function showError(message) {
            document.getElementById('error-text').textContent = message;
            document.getElementById('error-message').style.display = 'block';
            document.getElementById('stock-result').style.display = 'none';
        }

        function hideError() {
            document.getElementById('error-message').style.display = 'none';
        }

        // Watchlist and Portfolio actions
        document.getElementById('add-to-watchlist').addEventListener('click', function() {
            const symbol = document.getElementById('stock-symbol').textContent;
            addToWatchlist(symbol);
        });

        document.getElementById('add-to-portfolio').addEventListener('click', function() {
            const symbol = document.getElementById('stock-symbol').textContent;
            // Redirect to portfolio page with symbol
            window.location.href = '/portfolio/?add=' + symbol;
        });

        function addToWatchlist(symbol) {
            fetch(stockScannerAjax.backend_url + 'watchlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': stockScannerAjax.nonce
                },
                body: JSON.stringify({
                    ticker: symbol
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Stock added to watchlist successfully!');
                } else {
                    alert('Failed to add stock to watchlist: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error adding to watchlist:', error);
                alert('Failed to add stock to watchlist.');
            });
        }
    });
    </script>
    <?php
    return ob_get_clean();
}

/**
 * Premium Plans Shortcode
 */
function render_premium_plans_shortcode($atts) {
    $user_tier = get_user_tier();
    
    ob_start();
    ?>
    <div class="premium-plans-page">
        <div class="plans-header">
            <h1>Choose Your Plan</h1>
            <p>Unlock powerful features and get the data you need to make informed investment decisions</p>
            
            <div class="billing-toggle">
                <span class="toggle-label">Monthly</span>
                <label class="switch">
                    <input type="checkbox" id="billing-toggle">
                    <span class="slider"></span>
                </label>
                <span class="toggle-label">Yearly <span class="discount-badge">Save 10%</span></span>
            </div>
        </div>

        <div class="pricing-table">
            <!-- Free Plan -->
            <div class="pricing-card <?php echo $user_tier === 'free' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Free</h3>
                    <div class="price">
                        <span class="amount">$0</span>
                        <span class="period">/month</span>
                    </div>
                    <p class="plan-description">Perfect for getting started</p>
                </div>
                
                <ul class="features-list">
                    <li><i class="fas fa-check"></i> 15 API calls per month</li>
                    <li><i class="fas fa-check"></i> 3 watchlist items</li>
                    <li><i class="fas fa-check"></i> Basic charts</li>
                    <li><i class="fas fa-check"></i> Delayed market data</li>
                    <li><i class="fas fa-check"></i> Email support</li>
                    <li class="unavailable"><i class="fas fa-times"></i> Real-time data</li>
                    <li class="unavailable"><i class="fas fa-times"></i> Advanced charts</li>
                    <li class="unavailable"><i class="fas fa-times"></i> Data export</li>
                </ul>
                
                <div class="plan-action">
                    <?php if ($user_tier === 'free'): ?>
                        <button class="btn btn-outline" disabled>Current Plan</button>
                    <?php else: ?>
                        <button class="btn btn-outline" disabled>Downgrade Available</button>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Basic Plan -->
            <div class="pricing-card featured <?php echo $user_tier === 'basic' ? 'current-plan' : ''; ?>">
                <div class="plan-badge">Most Popular</div>
                <div class="plan-header">
                    <h3>Basic</h3>
                    <div class="price">
                        <span class="amount monthly-price">$24.99</span>
                        <span class="amount yearly-price" style="display: none;">$22.49</span>
                        <span class="period">/month</span>
                    </div>
                    <p class="plan-description">Great for active traders</p>
                </div>
                
                <ul class="features-list">
                    <li><i class="fas fa-check"></i> 1,500 API calls per month</li>
                    <li><i class="fas fa-check"></i> 25 watchlist items</li>
                    <li><i class="fas fa-check"></i> Real-time market data</li>
                    <li><i class="fas fa-check"></i> Advanced charts & indicators</li>
                    <li><i class="fas fa-check"></i> Data export (CSV, Excel)</li>
                    <li><i class="fas fa-check"></i> Price alerts</li>
                    <li><i class="fas fa-check"></i> Priority email support</li>
                    <li class="unavailable"><i class="fas fa-times"></i> API access</li>
                </ul>
                
                <div class="plan-action">
                    <?php if ($user_tier === 'basic'): ?>
                        <button class="btn btn-outline" disabled>Current Plan</button>
                    <?php elseif ($user_tier === 'free'): ?>
                        <button class="btn btn-primary upgrade-btn" data-plan="basic">Upgrade Now</button>
                    <?php else: ?>
                        <button class="btn btn-secondary downgrade-btn" data-plan="basic">Downgrade</button>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Pro Plan -->
            <div class="pricing-card <?php echo $user_tier === 'pro' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Pro</h3>
                    <div class="price">
                        <span class="amount monthly-price">$49.99</span>
                        <span class="amount yearly-price" style="display: none;">$44.99</span>
                        <span class="period">/month</span>
                    </div>
                    <p class="plan-description">For professional investors</p>
                </div>
                
                <ul class="features-list">
                    <li><i class="fas fa-check"></i> 5,000 API calls per month</li>
                    <li><i class="fas fa-check"></i> 100 watchlist items</li>
                    <li><i class="fas fa-check"></i> Everything in Basic</li>
                    <li><i class="fas fa-check"></i> Full API access</li>
                    <li><i class="fas fa-check"></i> Custom alerts & notifications</li>
                    <li><i class="fas fa-check"></i> Advanced analytics</li>
                    <li><i class="fas fa-check"></i> Portfolio optimization tools</li>
                    <li><i class="fas fa-check"></i> Phone & chat support</li>
                </ul>
                
                <div class="plan-action">
                    <?php if ($user_tier === 'pro'): ?>
                        <button class="btn btn-outline" disabled>Current Plan</button>
                    <?php elseif (in_array($user_tier, ['free', 'basic'])): ?>
                        <button class="btn btn-primary upgrade-btn" data-plan="pro">Upgrade Now</button>
                    <?php else: ?>
                        <button class="btn btn-secondary downgrade-btn" data-plan="pro">Downgrade</button>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Enterprise Plan -->
            <div class="pricing-card <?php echo $user_tier === 'enterprise' ? 'current-plan' : ''; ?>">
                <div class="plan-header">
                    <h3>Enterprise</h3>
                    <div class="price">
                        <span class="amount monthly-price">$79.99</span>
                        <span class="amount yearly-price" style="display: none;">$71.99</span>
                        <span class="period">/month</span>
                    </div>
                    <p class="plan-description">For institutions & power users</p>
                </div>
                
                <ul class="features-list">
                    <li><i class="fas fa-check"></i> Unlimited API calls</li>
                    <li><i class="fas fa-check"></i> Unlimited watchlist items</li>
                    <li><i class="fas fa-check"></i> Everything in Pro</li>
                    <li><i class="fas fa-check"></i> White-label solutions</li>
                    <li><i class="fas fa-check"></i> Custom integrations</li>
                    <li><i class="fas fa-check"></i> Dedicated account manager</li>
                    <li><i class="fas fa-check"></i> SLA guarantee</li>
                    <li><i class="fas fa-check"></i> 24/7 priority support</li>
                </ul>
                
                <div class="plan-action">
                    <?php if ($user_tier === 'enterprise'): ?>
                        <button class="btn btn-outline" disabled>Current Plan</button>
                    <?php else: ?>
                        <button class="btn btn-primary upgrade-btn" data-plan="enterprise">Upgrade Now</button>
                    <?php endif; ?>
                </div>
            </div>
        </div>

        <div class="features-comparison">
            <h2>Feature Comparison</h2>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Feature</th>
                            <th>Free</th>
                            <th>Basic</th>
                            <th>Pro</th>
                            <th>Enterprise</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>API Calls per Month</td>
                            <td>15</td>
                            <td>1,500</td>
                            <td>5,000</td>
                            <td>Unlimited</td>
                        </tr>
                        <tr>
                            <td>Watchlist Items</td>
                            <td>3</td>
                            <td>25</td>
                            <td>100</td>
                            <td>Unlimited</td>
                        </tr>
                        <tr>
                            <td>Real-time Data</td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                        </tr>
                        <tr>
                            <td>Advanced Charts</td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                        </tr>
                        <tr>
                            <td>Data Export</td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                        </tr>
                        <tr>
                            <td>API Access</td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                            <td><i class="fas fa-check text-green"></i></td>
                        </tr>
                        <tr>
                            <td>Custom Alerts</td>
                            <td><i class="fas fa-times text-red"></i></td>
                            <td>Basic</td>
                            <td>Advanced</td>
                            <td>Advanced</td>
                        </tr>
                        <tr>
                            <td>Support</td>
                            <td>Email</td>
                            <td>Priority Email</td>
                            <td>Phone & Chat</td>
                            <td>24/7 Dedicated</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <h4>Can I change my plan anytime?</h4>
                    <p>Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and billing is prorated.</p>
                </div>
                <div class="faq-item">
                    <h4>What payment methods do you accept?</h4>
                    <p>We accept all major credit cards and PayPal. All payments are processed securely through PayPal.</p>
                </div>
                <div class="faq-item">
                    <h4>Is there a free trial?</h4>
                    <p>Yes! Our Free plan gives you 15 API calls per month to try our service. No credit card required.</p>
                </div>
                <div class="faq-item">
                    <h4>What happens if I exceed my API limit?</h4>
                    <p>If you exceed your monthly limit, API calls will be temporarily restricted until your next billing cycle or you upgrade your plan.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const billingToggle = document.getElementById('billing-toggle');
        const monthlyPrices = document.querySelectorAll('.monthly-price');
        const yearlyPrices = document.querySelectorAll('.yearly-price');

        billingToggle.addEventListener('change', function() {
            if (this.checked) {
                // Show yearly prices
                monthlyPrices.forEach(price => price.style.display = 'none');
                yearlyPrices.forEach(price => price.style.display = 'inline');
            } else {
                // Show monthly prices
                monthlyPrices.forEach(price => price.style.display = 'inline');
                yearlyPrices.forEach(price => price.style.display = 'none');
            }
        });

        // Handle upgrade buttons
        document.querySelectorAll('.upgrade-btn, .downgrade-btn').forEach(button => {
            button.addEventListener('click', function() {
                const plan = this.dataset.plan;
                const isYearly = billingToggle.checked;
                
                // Redirect to PayPal checkout
                const checkoutUrl = `/paypal-checkout/?plan=${plan}&billing=${isYearly ? 'yearly' : 'monthly'}`;
                window.location.href = checkoutUrl;
            });
        });
    });
    </script>
    <?php
    return ob_get_clean();
}

/**
 * Login Form Shortcode
 */
function render_login_form_shortcode($atts) {
    if (is_user_logged_in()) {
        return '<div class="already-logged-in">You are already logged in. <a href="/dashboard/">Go to Dashboard</a></div>';
    }
    
    ob_start();
    ?>
    <div class="login-form-container">
        <div class="login-card">
            <div class="login-header">
                <h1>Welcome Back</h1>
                <p>Sign in to your Stock Scanner Pro account</p>
            </div>

            <form id="login-form" class="login-form">
                <div class="form-group">
                    <label for="username">Username or Email</label>
                    <input type="text" id="username" name="username" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="password-input">
                        <input type="password" id="password" name="password" required>
                        <button type="button" class="password-toggle" id="password-toggle">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>

                <div class="form-options">
                    <label class="checkbox-label">
                        <input type="checkbox" id="remember" name="remember">
                        <span class="checkmark"></span>
                        Remember me
                    </label>
                    <a href="<?php echo wp_lostpassword_url(); ?>" class="forgot-password">Forgot password?</a>
                </div>

                <button type="submit" class="btn btn-primary btn-full">Sign In</button>

                <div class="form-divider">
                    <span>or</span>
                </div>

                <div class="social-login">
                    <button type="button" class="btn btn-social btn-google">
                        <i class="fab fa-google"></i>
                        Continue with Google
                    </button>
                </div>
            </form>

            <div class="login-footer">
                <p>Don't have an account? <a href="/signup/">Sign up for free</a></p>
            </div>
        </div>

        <div class="login-benefits">
            <h3>Why Stock Scanner Pro?</h3>
            <ul class="benefits-list">
                <li><i class="fas fa-chart-line"></i> Real-time market data</li>
                <li><i class="fas fa-search"></i> Advanced stock screening</li>
                <li><i class="fas fa-bell"></i> Custom price alerts</li>
                <li><i class="fas fa-mobile-alt"></i> Mobile-friendly interface</li>
                <li><i class="fas fa-shield-alt"></i> Secure & reliable</li>
            </ul>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const loginForm = document.getElementById('login-form');
        const passwordToggle = document.getElementById('password-toggle');
        const passwordInput = document.getElementById('password');

        // Password visibility toggle
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });

        // Form submission
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
            
            // Perform login
            fetch(stockScannerAjax.ajaxurl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-WP-Nonce': stockScannerAjax.nonce
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to dashboard
                    window.location.href = '/dashboard/';
                } else {
                    // Show error
                    showError(data.message || 'Login failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                showError('Login failed. Please try again.');
            })
            .finally(() => {
                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Sign In';
            });
        });

        function showError(message) {
            // Remove existing error
            const existingError = document.querySelector('.login-error');
            if (existingError) {
                existingError.remove();
            }

            // Add new error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'login-error';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            
            loginForm.insertBefore(errorDiv, loginForm.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    });
    </script>
    <?php
    return ob_get_clean();
}

/**
 * Signup Form Shortcode
 */
function render_signup_form_shortcode($atts) {
    if (is_user_logged_in()) {
        return '<div class="already-logged-in">You are already logged in. <a href="/dashboard/">Go to Dashboard</a></div>';
    }
    
    ob_start();
    ?>
    <div class="signup-form-container">
        <div class="signup-card">
            <div class="signup-header">
                <h1>Get Started Free</h1>
                <p>Create your Stock Scanner Pro account and start analyzing stocks today</p>
            </div>

            <form id="signup-form" class="signup-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="first_name">First Name</label>
                        <input type="text" id="first_name" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label for="last_name">Last Name</label>
                        <input type="text" id="last_name" name="last_name" required>
                    </div>
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>

                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                    <small class="form-help">Choose a unique username for your account</small>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="password-input">
                        <input type="password" id="password" name="password" required>
                        <button type="button" class="password-toggle" id="password-toggle">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="password-strength" id="password-strength"></div>
                </div>

                <div class="form-group">
                    <label for="confirm_password">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" required>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="terms" name="terms" required>
                        <span class="checkmark"></span>
                        I agree to the <a href="/terms-of-service/" target="_blank">Terms of Service</a> and <a href="/privacy-policy/" target="_blank">Privacy Policy</a>
                    </label>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="newsletter" name="newsletter">
                        <span class="checkmark"></span>
                        Send me market updates and product news
                    </label>
                </div>

                <button type="submit" class="btn btn-primary btn-full">Create Account</button>

                <div class="form-divider">
                    <span>or</span>
                </div>

                <div class="social-signup">
                    <button type="button" class="btn btn-social btn-google">
                        <i class="fab fa-google"></i>
                        Sign up with Google
                    </button>
                </div>
            </form>

            <div class="signup-footer">
                <p>Already have an account? <a href="/login/">Sign in</a></p>
            </div>
        </div>

        <div class="signup-benefits">
            <h3>What you get with your free account:</h3>
            <ul class="benefits-list">
                <li><i class="fas fa-check"></i> 15 API calls per month</li>
                <li><i class="fas fa-check"></i> 3 watchlist items</li>
                <li><i class="fas fa-check"></i> Basic stock charts</li>
                <li><i class="fas fa-check"></i> Market news & updates</li>
                <li><i class="fas fa-check"></i> Email support</li>
            </ul>
            
            <div class="upgrade-prompt">
                <p><strong>Need more?</strong> Upgrade anytime to get real-time data, advanced charts, and unlimited API calls.</p>
                <a href="/premium-plans/" class="btn btn-outline">View Premium Plans</a>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const signupForm = document.getElementById('signup-form');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        const passwordToggle = document.getElementById('password-toggle');
        const passwordStrength = document.getElementById('password-strength');

        // Password visibility toggle
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });

        // Password strength indicator
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);
            
            passwordStrength.className = 'password-strength ' + strength.class;
            passwordStrength.textContent = strength.text;
        });

        // Password confirmation validation
        confirmPasswordInput.addEventListener('input', function() {
            const password = passwordInput.value;
            const confirmPassword = this.value;
            
            if (confirmPassword && password !== confirmPassword) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });

        // Form submission
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            
            // Validate passwords match
            if (passwordInput.value !== confirmPasswordInput.value) {
                showError('Passwords do not match');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
            
            // Perform signup
            fetch(stockScannerAjax.ajaxurl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-WP-Nonce': stockScannerAjax.nonce
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message and redirect
                    showSuccess('Account created successfully! Redirecting to dashboard...');
                    setTimeout(() => {
                        window.location.href = '/dashboard/';
                    }, 2000);
                } else {
                    showError(data.message || 'Signup failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Signup error:', error);
                showError('Signup failed. Please try again.');
            })
            .finally(() => {
                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Account';
            });
        });

        function calculatePasswordStrength(password) {
            let score = 0;
            
            if (password.length >= 8) score++;
            if (password.match(/[a-z]/)) score++;
            if (password.match(/[A-Z]/)) score++;
            if (password.match(/[0-9]/)) score++;
            if (password.match(/[^a-zA-Z0-9]/)) score++;
            
            const strengths = [
                { class: 'weak', text: 'Very weak' },
                { class: 'weak', text: 'Weak' },
                { class: 'fair', text: 'Fair' },
                { class: 'good', text: 'Good' },
                { class: 'strong', text: 'Strong' },
                { class: 'strong', text: 'Very strong' }
            ];
            
            return strengths[score] || strengths[0];
        }

        function showError(message) {
            showMessage(message, 'error');
        }

        function showSuccess(message) {
            showMessage(message, 'success');
        }

        function showMessage(message, type) {
            // Remove existing messages
            const existingMessage = document.querySelector('.signup-message');
            if (existingMessage) {
                existingMessage.remove();
            }

            // Add new message
            const messageDiv = document.createElement('div');
            messageDiv.className = `signup-message signup-${type}`;
            const icon = type === 'error' ? 'exclamation-circle' : 'check-circle';
            messageDiv.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;
            
            signupForm.insertBefore(messageDiv, signupForm.firstChild);
            
            // Auto-remove after 5 seconds (except success messages)
            if (type === 'error') {
                setTimeout(() => {
                    messageDiv.remove();
                }, 5000);
            }
        }
    });
    </script>
    <?php
    return ob_get_clean();
}

// Additional shortcode implementations would continue here...
// For brevity, I'm including the key ones. The pattern would continue for:
// - render_stock_screener_shortcode
// - render_market_overview_shortcode  
// - render_watchlist_shortcode
// - render_portfolio_shortcode
// - render_stock_news_shortcode
// - render_contact_form_shortcode
// - render_faq_shortcode
// - render_help_center_shortcode
// - etc.

/**
 * Placeholder shortcodes for remaining functionality
 */
function render_stock_screener_shortcode($atts) {
    return '<div class="stock-screener-placeholder">Stock Screener functionality will be implemented here with advanced filtering capabilities.</div>';
}

function render_market_overview_shortcode($atts) {
    return '<div class="market-overview-placeholder">Market Overview dashboard will display major indices, sector performance, and market trends.</div>';
}

function render_watchlist_shortcode($atts) {
    return '<div class="watchlist-placeholder">Personal watchlist with real-time updates, price alerts, and portfolio integration.</div>';
}

function render_portfolio_shortcode($atts) {
    return '<div class="portfolio-placeholder">Portfolio tracking with performance analytics, profit/loss calculations, and asset allocation charts.</div>';
}

function render_stock_news_shortcode($atts) {
    return '<div class="stock-news-placeholder">Personalized stock news feed with market analysis and company-specific updates.</div>';
}

function render_account_dashboard_shortcode($atts) {
    return '<div class="account-dashboard-placeholder">User account management with subscription details, billing history, and settings.</div>';
}

function render_billing_history_shortcode($atts) {
    return '<div class="billing-history-placeholder">Complete billing history with downloadable invoices and payment details.</div>';
}

function render_user_settings_shortcode($atts) {
    return '<div class="user-settings-placeholder">User preferences, notification settings, and account customization options.</div>';
}

function render_paypal_checkout_shortcode($atts) {
    return '<div class="paypal-checkout-placeholder">Secure PayPal checkout integration for subscription upgrades and payments.</div>';
}

function render_contact_form_shortcode($atts) {
    return '<div class="contact-form-placeholder">Contact form with support ticket integration and response tracking.</div>';
}

function render_faq_shortcode($atts) {
    return '<div class="faq-placeholder">Comprehensive FAQ section with searchable questions and detailed answers.</div>';
}

function render_help_center_shortcode($atts) {
    return '<div class="help-center-placeholder">Complete help center with tutorials, guides, and documentation.</div>';
}

function render_getting_started_shortcode($atts) {
    return '<div class="getting-started-placeholder">Step-by-step getting started guide with interactive tutorials.</div>';
}

function render_how_it_works_shortcode($atts) {
    return '<div class="how-it-works-placeholder">Detailed explanation of platform features and capabilities.</div>';
}

function render_glossary_shortcode($atts) {
    return '<div class="glossary-placeholder">Financial terms glossary with definitions and examples.</div>';
}

function render_market_hours_shortcode($atts) {
    return '<div class="market-hours-placeholder">Global market hours display with timezone conversions.</div>';
}

function render_privacy_policy_shortcode($atts) {
    return '<div class="privacy-policy-placeholder">Comprehensive privacy policy with data handling and user rights information.</div>';
}

function render_terms_shortcode($atts) {
    return '<div class="terms-placeholder">Terms of service with usage guidelines and legal information.</div>';
}

function render_cookie_policy_shortcode($atts) {
    return '<div class="cookie-policy-placeholder">Cookie policy with consent management and privacy controls.</div>';
}

function render_payment_success_shortcode($atts) {
    return '<div class="payment-success-placeholder">Payment confirmation page with subscription activation details.</div>';
}

function render_payment_cancelled_shortcode($atts) {
    return '<div class="payment-cancelled-placeholder">Payment cancellation page with alternative options and support.</div>';
}

function render_plans_comparison_shortcode($atts) {
    return '<div class="plans-comparison-placeholder">Detailed plan comparison table with feature breakdowns.</div>';
}

function render_personalized_news_shortcode($atts) {
    return '<div class="personalized-news-placeholder">AI-powered personalized news feed based on user interests and portfolio.</div>';
}