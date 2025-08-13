<?php
/**
 * Template Name: Stock Scanner Pro - Stock Lookup
 * 
 * Professional stock lookup page with Zatra theme styling
 */

get_header(); ?>

<main id="main" class="wp-block-group alignfull is-layout-constrained wp-block-group-is-layout-constrained" style="margin-top:0">
    
    <div class="wp-block-group__inner-container">
        <div class="container">
            <div class="stock-lookup-tool">
                
                <!-- Lookup Header -->
                <div class="lookup-header">
                    <h1 class="wp-block-heading has-text-align-center has-huge-font-size">Stock Lookup</h1>
                    <p class="has-text-align-center has-medium-font-size">Search for any stock and get detailed analysis, charts, and key metrics</p>
                </div>

                <!-- Search Container -->
                <div class="search-container">
                    <div class="search-box">
                        <input type="text" id="stock-search" placeholder="Enter stock symbol (e.g., AAPL, MSFT, TSLA)" class="search-input">
                        <button id="search-btn" class="btn btn-primary">
                            <i class="fas fa-search"></i> Search
                        </button>
                    </div>
                    <div id="search-suggestions" class="search-suggestions"></div>
                </div>

                <!-- Loading Indicator -->
                <div id="loading-indicator" class="loading-indicator" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading stock data...</p>
                </div>

                <!-- Error Message -->
                <div id="error-message" class="error-message" style="display: none;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span id="error-text">Stock not found. Please check the symbol and try again.</span>
                </div>

                <!-- Stock Result -->
                <div id="stock-result" class="stock-result" style="display: none;">
                    
                    <!-- Stock Header -->
                    <div class="stock-header">
                        <div class="stock-info">
                            <h2 id="stock-name">Apple Inc.</h2>
                            <div class="stock-meta">
                                <span id="stock-symbol" class="stock-symbol">AAPL</span>
                                <span id="stock-exchange" class="stock-exchange">NASDAQ</span>
                            </div>
                        </div>
                        
                        <div class="stock-price">
                            <span id="current-price" class="current-price">$150.25</span>
                            <div class="price-changes">
                                <span id="price-change" class="price-change positive">+2.45</span>
                                <span id="change-percent" class="change-percent positive">(+1.66%)</span>
                            </div>
                        </div>
                        
                        <div class="stock-actions">
                            <?php if (is_user_logged_in()): ?>
                                <button id="add-to-watchlist" class="btn btn-secondary">
                                    <i class="fas fa-star"></i> Add to Watchlist
                                </button>
                                <button id="add-to-portfolio" class="btn btn-outline">
                                    <i class="fas fa-briefcase"></i> Add to Portfolio
                                </button>
                            <?php else: ?>
                                <a href="/login/" class="btn btn-primary">Login to Save</a>
                            <?php endif; ?>
                        </div>
                    </div>

                    <!-- Stock Details -->
                    <div class="stock-details">
                        <div class="details-grid">
                            
                            <!-- Price Chart -->
                            <div class="detail-card chart-card">
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

                            <!-- Key Statistics -->
                            <div class="detail-card">
                                <h3>Key Statistics</h3>
                                <div id="key-stats" class="stats-grid">
                                    <div class="stat-item">
                                        <span class="stat-label">Market Cap</span>
                                        <span class="stat-value">$2.45T</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">P/E Ratio</span>
                                        <span class="stat-value">28.5</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Volume</span>
                                        <span class="stat-value">45.2M</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">52W High</span>
                                        <span class="stat-value">$182.94</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">52W Low</span>
                                        <span class="stat-value">$124.17</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Dividend Yield</span>
                                        <span class="stat-value">0.50%</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Company Profile -->
                            <div class="detail-card">
                                <h3>Company Profile</h3>
                                <div id="company-profile">
                                    <p class="company-description">
                                        Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.
                                    </p>
                                    <div class="company-details">
                                        <div class="company-detail">
                                            <span class="detail-label">Industry:</span>
                                            <span class="detail-value">Consumer Electronics</span>
                                        </div>
                                        <div class="company-detail">
                                            <span class="detail-label">Sector:</span>
                                            <span class="detail-value">Technology</span>
                                        </div>
                                        <div class="company-detail">
                                            <span class="detail-label">Employees:</span>
                                            <span class="detail-value">164,000</span>
                                        </div>
                                        <div class="company-detail">
                                            <span class="detail-label">Founded:</span>
                                            <span class="detail-value">1976</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Recent News -->
                            <div class="detail-card">
                                <h3>Recent News</h3>
                                <div id="stock-news">
                                    <div class="loading">Loading news...</div>
                                </div>
                            </div>

                            <!-- Technical Indicators (Premium Feature) -->
                            <?php if (get_user_rate_limits()['advanced_charts']): ?>
                                <div class="detail-card">
                                    <h3>Technical Indicators</h3>
                                    <div class="technical-indicators">
                                        <div class="indicator-item">
                                            <span class="indicator-name">RSI (14)</span>
                                            <span class="indicator-value">65.2</span>
                                            <span class="indicator-signal neutral">Neutral</span>
                                        </div>
                                        <div class="indicator-item">
                                            <span class="indicator-name">MACD</span>
                                            <span class="indicator-value">1.25</span>
                                            <span class="indicator-signal bullish">Bullish</span>
                                        </div>
                                        <div class="indicator-item">
                                            <span class="indicator-name">SMA (50)</span>
                                            <span class="indicator-value">$148.75</span>
                                            <span class="indicator-signal bullish">Above</span>
                                        </div>
                                        <div class="indicator-item">
                                            <span class="indicator-name">SMA (200)</span>
                                            <span class="indicator-value">$145.20</span>
                                            <span class="indicator-signal bullish">Above</span>
                                        </div>
                                    </div>
                                </div>
                            <?php else: ?>
                                <div class="detail-card upgrade-prompt">
                                    <div class="home-icon-wrap home-icon-wrap-1">
                                        <i class="fas fa-chart-line"></i>
                                    </div>
                                    <h3>Technical Indicators</h3>
                                    <p>Upgrade to access advanced technical indicators like RSI, MACD, and moving averages.</p>
                                    <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                                </div>
                            <?php endif; ?>

                        </div>
                    </div>
                </div>

                <!-- Popular Stocks -->
                <div class="popular-stocks">
                    <h2 class="wp-block-heading has-text-align-center has-large-font-size">Popular Stocks</h2>
                    <div class="popular-grid">
                        <?php 
                        $popular_stocks = array(
                            array('symbol' => 'AAPL', 'name' => 'Apple Inc.', 'price' => '$150.25', 'change' => '+1.66%', 'positive' => true),
                            array('symbol' => 'MSFT', 'name' => 'Microsoft Corp.', 'price' => '$335.50', 'change' => '+0.85%', 'positive' => true),
                            array('symbol' => 'GOOGL', 'name' => 'Alphabet Inc.', 'price' => '$2,750.00', 'change' => '-0.45%', 'positive' => false),
                            array('symbol' => 'AMZN', 'name' => 'Amazon.com Inc.', 'price' => '$3,200.00', 'change' => '+2.15%', 'positive' => true),
                            array('symbol' => 'TSLA', 'name' => 'Tesla Inc.', 'price' => '$850.75', 'change' => '-1.25%', 'positive' => false),
                            array('symbol' => 'META', 'name' => 'Meta Platforms', 'price' => '$325.40', 'change' => '+3.20%', 'positive' => true)
                        );
                        
                        foreach ($popular_stocks as $stock): 
                            $change_class = $stock['positive'] ? 'positive' : 'negative';
                        ?>
                            <div class="popular-stock-item" data-symbol="<?php echo $stock['symbol']; ?>">
                                <div class="stock-symbol"><?php echo $stock['symbol']; ?></div>
                                <div class="stock-name"><?php echo $stock['name']; ?></div>
                                <div class="stock-price"><?php echo $stock['price']; ?></div>
                                <div class="stock-change <?php echo $change_class; ?>"><?php echo $stock['change']; ?></div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>

            </div>
        </div>
    </div>

</main>

<style>
/* Stock Lookup specific styles */
.search-input {
    font-size: 18px;
    padding: 16px 20px;
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius);
    background: white;
    transition: all 0.3s ease;
}

.search-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
    outline: none;
}

.chart-card {
    grid-column: span 2;
}

.company-detail {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
}

.company-detail:last-child {
    border-bottom: none;
}

.detail-label {
    font-weight: 500;
    color: var(--light-text);
}

.detail-value {
    font-weight: 600;
    color: var(--text-color);
}

.technical-indicators {
    display: grid;
    gap: 16px;
}

.indicator-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--light-background);
    border-radius: var(--border-radius);
}

.indicator-name {
    font-weight: 500;
    color: var(--text-color);
}

.indicator-value {
    font-family: var(--font-primary);
    font-weight: 600;
}

.indicator-signal {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.indicator-signal.bullish {
    background: #e8f5e8;
    color: var(--success-color);
}

.indicator-signal.bearish {
    background: #ffeaea;
    color: #ff6b6b;
}

.indicator-signal.neutral {
    background: #f0f0f0;
    color: var(--light-text);
}

.popular-stocks {
    margin-top: 80px;
    padding: 60px 0;
    background: var(--light-background);
    border-radius: var(--border-radius-large);
}

.popular-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.popular-stock-item {
    background: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}

.popular-stock-item:hover {
    transform: translateY(-4px);
    box-shadow: 0px 15px 30px rgb(0 0 0 / 15%);
}

.popular-stock-item .stock-symbol {
    font-size: 18px;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 4px;
}

.popular-stock-item .stock-name {
    font-size: 12px;
    color: var(--light-text);
    margin-bottom: 8px;
}

.popular-stock-item .stock-price {
    font-size: 16px;
    font-weight: 600;
    font-family: var(--font-primary);
    margin-bottom: 4px;
}

.popular-stock-item .stock-change {
    font-size: 14px;
    font-weight: 500;
}

@media (max-width: 768px) {
    .chart-card {
        grid-column: span 1;
    }
    
    .popular-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 480px) {
    .search-box {
        flex-direction: column;
        gap: 12px;
    }
    
    .popular-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Handle popular stock clicks
    document.querySelectorAll('.popular-stock-item').forEach(item => {
        item.addEventListener('click', function() {
            const symbol = this.dataset.symbol;
            document.getElementById('stock-search').value = symbol;
            handleSearchSubmit();
            
            // Scroll to results
            document.getElementById('stock-result').scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
    
    // Auto-focus search input
    document.getElementById('stock-search').focus();
});
</script>

<?php get_footer(); ?>