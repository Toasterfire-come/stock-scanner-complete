<?php
/**
 * Template Name: Search
 * 
 * Symbol search with autocomplete, quote card, fundamentals, and historical data
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Search Stocks', 'retail-trade-scanner'),
    'page_description' => __('Search for stocks, get quotes, and analyze fundamentals and historical data', 'retail-trade-scanner'),
    'page_class' => 'search-page',
    'header_actions' => array(
        array(
            'text' => __('Add to Watchlist', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'watchlist',
            'id' => 'add-to-watchlist',
            'disabled' => true
        ),
        array(
            'text' => __('Set Alert', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'alerts',
            'id' => 'set-alert',
            'disabled' => true
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="search-layout">
    <!-- Search Section -->
    <section class="search-section">
        <div class="search-container card glass-card">
            <div class="search-header">
                <h2><?php esc_html_e('Search for Stocks', 'retail-trade-scanner'); ?></h2>
                <p class="search-description">
                    <?php esc_html_e('Enter a stock symbol or company name to get detailed information, quotes, and analysis.', 'retail-trade-scanner'); ?>
                </p>
            </div>
            
            <div class="search-form">
                <div class="search-input-container">
                    <div class="search-input-wrapper">
                        <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20', 'class' => 'search-icon']); ?>
                        <input type="text" 
                               id="stock-search" 
                               class="search-input" 
                               placeholder="<?php esc_attr_e('Enter symbol (e.g., AAPL) or company name', 'retail-trade-scanner'); ?>"
                               autocomplete="off">
                        <button class="search-clear-btn hidden" id="clear-search">
                            <?php echo rts_get_icon('x', ['width' => '16', 'height' => '16']); ?>
                        </button>
                    </div>
                    <button class="search-submit-btn" id="search-submit">
                        <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
                        <span><?php esc_html_e('Search', 'retail-trade-scanner'); ?></span>
                    </button>
                </div>
                
                <!-- Autocomplete Results -->
                <div class="autocomplete-results hidden" id="autocomplete-results">
                    <div class="autocomplete-list"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Results Section -->
    <section class="search-results-section hidden" id="search-results">
        <!-- Stock Quote Card -->
        <div class="stock-quote-card card glass-card">
            <div class="quote-header">
                <div class="stock-identity">
                    <h1 class="stock-symbol" id="stock-symbol">--</h1>
                    <h2 class="company-name" id="company-name">--</h2>
                    <div class="stock-metadata">
                        <span class="market-status" id="market-status">--</span>
                        <span class="exchange" id="exchange">--</span>
                    </div>
                </div>
                <div class="stock-actions">
                    <button class="btn btn-ghost btn-icon" title="<?php esc_attr_e('Refresh', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('refresh', ['width' => '20', 'height' => '20']); ?>
                    </button>
                    <button class="btn btn-ghost btn-icon" title="<?php esc_attr_e('Share', 'retail-trade-scanner'); ?>">
                        <?php echo rts_get_icon('share', ['width' => '20', 'height' => '20']); ?>
                    </button>
                </div>
            </div>
            
            <div class="quote-content">
                <div class="price-section">
                    <div class="current-price">
                        <span class="price-value" id="current-price">$--</span>
                        <div class="price-change">
                            <span class="change-value" id="price-change">$-- (--)</span>
                            <span class="change-time" id="change-time">--</span>
                        </div>
                    </div>
                    
                    <div class="price-metrics">
                        <div class="metric">
                            <span class="metric-label"><?php esc_html_e('Previous Close', 'retail-trade-scanner'); ?></span>
                            <span class="metric-value" id="prev-close">$--</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label"><?php esc_html_e('Day Range', 'retail-trade-scanner'); ?></span>
                            <span class="metric-value" id="day-range">$-- - $--</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label"><?php esc_html_e('Volume', 'retail-trade-scanner'); ?></span>
                            <span class="metric-value" id="volume">--</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label"><?php esc_html_e('Market Cap', 'retail-trade-scanner'); ?></span>
                            <span class="metric-value" id="market-cap">--</span>
                        </div>
                    </div>
                </div>
                
                <!-- Mini Chart -->
                <div class="mini-chart-container">
                    <?php
                    get_template_part('template-parts/components/chart-shell', null, array(
                        'id' => 'quote-mini-chart',
                        'title' => '',
                        'type' => 'line',
                        'height' => '200px',
                        'loading' => true,
                        'show_controls' => false,
                        'variant' => 'mini'
                    ));
                    ?>
                </div>
            </div>
        </div>

        <!-- Analysis Tabs -->
        <div class="analysis-tabs-container card">
            <?php
            get_template_part('template-parts/components/tabs', null, array(
                'id' => 'analysis-tabs',
                'tabs' => array(
                    array(
                        'id' => 'overview',
                        'label' => __('Overview', 'retail-trade-scanner'),
                        'icon' => 'info',
                        'active' => true
                    ),
                    array(
                        'id' => 'fundamentals',
                        'label' => __('Fundamentals', 'retail-trade-scanner'),
                        'icon' => 'chart-bar'
                    ),
                    array(
                        'id' => 'technical',
                        'label' => __('Technical', 'retail-trade-scanner'),
                        'icon' => 'trending-up'
                    ),
                    array(
                        'id' => 'historical',
                        'label' => __('Historical', 'retail-trade-scanner'),
                        'icon' => 'calendar'
                    ),
                    array(
                        'id' => 'news',
                        'label' => __('News', 'retail-trade-scanner'),
                        'icon' => 'news'
                    )
                )
            ));
            ?>
            
            <!-- Tab Panels -->
            <div class="tab-panels">
                <!-- Overview Panel -->
                <div class="tab-panel active" id="panel-overview">
                    <div class="overview-grid grid grid-3">
                        <div class="overview-section">
                            <h3><?php esc_html_e('Key Statistics', 'retail-trade-scanner'); ?></h3>
                            <div class="stats-list">
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('52 Week Range', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="week-52-range">$-- - $--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('P/E Ratio', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="pe-ratio">--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Dividend Yield', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="dividend-yield">--%</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Beta', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="beta">--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('EPS', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="eps">$--</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="overview-section">
                            <h3><?php esc_html_e('Trading Info', 'retail-trade-scanner'); ?></h3>
                            <div class="stats-list">
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Avg Volume', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="avg-volume">--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Open', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="open-price">$--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('High', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="high-price">$--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Low', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="low-price">$--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label"><?php esc_html_e('Shares Outstanding', 'retail-trade-scanner'); ?></span>
                                    <span class="stat-value" id="shares-outstanding">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="overview-section">
                            <h3><?php esc_html_e('Company Profile', 'retail-trade-scanner'); ?></h3>
                            <div class="company-info">
                                <div class="company-description" id="company-description">
                                    <div class="skeleton" style="width: 100%; height: 60px;"></div>
                                </div>
                                <div class="company-details">
                                    <div class="detail-item">
                                        <span class="detail-label"><?php esc_html_e('Sector', 'retail-trade-scanner'); ?></span>
                                        <span class="detail-value" id="sector">--</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label"><?php esc_html_e('Industry', 'retail-trade-scanner'); ?></span>
                                        <span class="detail-value" id="industry">--</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label"><?php esc_html_e('Employees', 'retail-trade-scanner'); ?></span>
                                        <span class="detail-value" id="employees">--</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Fundamentals Panel -->
                <div class="tab-panel" id="panel-fundamentals">
                    <div class="fundamentals-grid grid grid-2">
                        <div class="fundamentals-section">
                            <h3><?php esc_html_e('Valuation Metrics', 'retail-trade-scanner'); ?></h3>
                            <?php
                            get_template_part('template-parts/components/table', null, array(
                                'id' => 'valuation-table',
                                'headers' => array(
                                    'metric' => __('Metric', 'retail-trade-scanner'),
                                    'value' => __('Value', 'retail-trade-scanner'),
                                    'industry_avg' => __('Industry Avg', 'retail-trade-scanner')
                                ),
                                'data' => array(
                                    array('metric' => 'P/E Ratio', 'value' => '--', 'industry_avg' => '--'),
                                    array('metric' => 'PEG Ratio', 'value' => '--', 'industry_avg' => '--'),
                                    array('metric' => 'Price/Book', 'value' => '--', 'industry_avg' => '--'),
                                    array('metric' => 'Price/Sales', 'value' => '--', 'industry_avg' => '--'),
                                    array('metric' => 'EV/Revenue', 'value' => '--', 'industry_avg' => '--')
                                ),
                                'compact' => true
                            ));
                            ?>
                        </div>
                        
                        <div class="fundamentals-section">
                            <h3><?php esc_html_e('Financial Health', 'retail-trade-scanner'); ?></h3>
                            <?php
                            get_template_part('template-parts/components/table', null, array(
                                'id' => 'financial-table',
                                'headers' => array(
                                    'metric' => __('Metric', 'retail-trade-scanner'),
                                    'value' => __('Value', 'retail-trade-scanner'),
                                    'benchmark' => __('Benchmark', 'retail-trade-scanner')
                                ),
                                'data' => array(
                                    array('metric' => 'Debt/Equity', 'value' => '--', 'benchmark' => '--'),
                                    array('metric' => 'Current Ratio', 'value' => '--', 'benchmark' => '--'),
                                    array('metric' => 'ROE', 'value' => '--', 'benchmark' => '--'),
                                    array('metric' => 'ROA', 'value' => '--', 'benchmark' => '--'),
                                    array('metric' => 'Profit Margin', 'value' => '--', 'benchmark' => '--')
                                ),
                                'compact' => true
                            ));
                            ?>
                        </div>
                    </div>
                </div>

                <!-- Technical Panel -->
                <div class="tab-panel" id="panel-technical">
                    <div class="technical-analysis">
                        <div class="technical-indicators">
                            <h3><?php esc_html_e('Technical Indicators', 'retail-trade-scanner'); ?></h3>
                            <div class="indicators-grid grid grid-3">
                                <div class="indicator-card">
                                    <h4><?php esc_html_e('RSI (14)', 'retail-trade-scanner'); ?></h4>
                                    <div class="indicator-value" id="rsi-value">--</div>
                                    <div class="indicator-signal" id="rsi-signal">--</div>
                                </div>
                                <div class="indicator-card">
                                    <h4><?php esc_html_e('MACD', 'retail-trade-scanner'); ?></h4>
                                    <div class="indicator-value" id="macd-value">--</div>
                                    <div class="indicator-signal" id="macd-signal">--</div>
                                </div>
                                <div class="indicator-card">
                                    <h4><?php esc_html_e('Moving Averages', 'retail-trade-scanner'); ?></h4>
                                    <div class="ma-list">
                                        <div class="ma-item">
                                            <span>SMA 20: <span id="sma-20">--</span></span>
                                        </div>
                                        <div class="ma-item">
                                            <span>SMA 50: <span id="sma-50">--</span></span>
                                        </div>
                                        <div class="ma-item">
                                            <span>SMA 200: <span id="sma-200">--</span></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="technical-chart">
                            <h3><?php esc_html_e('Price Chart with Indicators', 'retail-trade-scanner'); ?></h3>
                            <?php
                            get_template_part('template-parts/components/chart-shell', null, array(
                                'id' => 'technical-chart',
                                'title' => '',
                                'type' => 'candlestick',
                                'height' => '400px',
                                'loading' => true,
                                'show_controls' => true,
                                'variant' => 'technical'
                            ));
                            ?>
                        </div>
                    </div>
                </div>

                <!-- Historical Panel -->
                <div class="tab-panel" id="panel-historical">
                    <div class="historical-data">
                        <div class="historical-controls">
                            <div class="date-range-picker">
                                <label for="start-date"><?php esc_html_e('From:', 'retail-trade-scanner'); ?></label>
                                <input type="date" id="start-date" class="form-input">
                                
                                <label for="end-date"><?php esc_html_e('To:', 'retail-trade-scanner'); ?></label>
                                <input type="date" id="end-date" class="form-input">
                                
                                <button class="btn btn-primary" id="load-historical">
                                    <?php esc_html_e('Load Data', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                        </div>
                        
                        <div class="historical-table-container">
                            <?php
                            get_template_part('template-parts/components/table', null, array(
                                'id' => 'historical-table',
                                'headers' => array(
                                    'date' => __('Date', 'retail-trade-scanner'),
                                    'open' => __('Open', 'retail-trade-scanner'),
                                    'high' => __('High', 'retail-trade-scanner'),
                                    'low' => __('Low', 'retail-trade-scanner'),
                                    'close' => __('Close', 'retail-trade-scanner'),
                                    'volume' => __('Volume', 'retail-trade-scanner')
                                ),
                                'data' => array(),
                                'sortable' => true,
                                'pagination' => true,
                                'loading' => true
                            ));
                            ?>
                        </div>
                    </div>
                </div>

                <!-- News Panel -->
                <div class="tab-panel" id="panel-news">
                    <div class="stock-news">
                        <div class="news-filters">
                            <div class="news-filter-controls">
                                <select class="form-select news-source-filter">
                                    <option value="all"><?php esc_html_e('All Sources', 'retail-trade-scanner'); ?></option>
                                    <option value="reuters">Reuters</option>
                                    <option value="bloomberg">Bloomberg</option>
                                    <option value="marketwatch">MarketWatch</option>
                                </select>
                                
                                <select class="form-select news-time-filter">
                                    <option value="today"><?php esc_html_e('Today', 'retail-trade-scanner'); ?></option>
                                    <option value="week"><?php esc_html_e('This Week', 'retail-trade-scanner'); ?></option>
                                    <option value="month"><?php esc_html_e('This Month', 'retail-trade-scanner'); ?></option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="news-list" id="stock-news-list">
                            <!-- Dynamic content loaded via JavaScript -->
                            <div class="news-skeleton">
                                <div class="skeleton" style="width: 100%; height: 20px;"></div>
                                <div class="skeleton" style="width: 80%; height: 16px; margin-top: 8px;"></div>
                                <div class="skeleton" style="width: 120px; height: 14px; margin-top: 8px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</div>

<!-- Search JavaScript -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('stock-search');
    const searchSubmit = document.getElementById('search-submit');
    const clearButton = document.getElementById('clear-search');
    const autocompleteResults = document.getElementById('autocomplete-results');
    const searchResults = document.getElementById('search-results');
    
    let searchTimeout;
    let currentSymbol = null;
    
    // Search input event handlers
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length > 0) {
            clearButton.classList.remove('hidden');
            
            // Debounce autocomplete search
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performAutocomplete(query);
            }, 300);
        } else {
            clearButton.classList.add('hidden');
            hideAutocomplete();
        }
    });
    
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch(this.value.trim());
        }
    });
    
    searchSubmit.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });
    
    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        this.classList.add('hidden');
        hideAutocomplete();
        hideResults();
    });
    
    // Click outside to hide autocomplete
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-form')) {
            hideAutocomplete();
        }
    });
    
    function performAutocomplete(query) {
        // Simulate API autocomplete
        const mockResults = [
            { symbol: 'AAPL', name: 'Apple Inc.' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.' },
            { symbol: 'MSFT', name: 'Microsoft Corporation' },
            { symbol: 'AMZN', name: 'Amazon.com Inc.' },
            { symbol: 'TSLA', name: 'Tesla Inc.' }
        ].filter(stock => 
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        );
        
        showAutocomplete(mockResults);
    }
    
    function showAutocomplete(results) {
        const listElement = autocompleteResults.querySelector('.autocomplete-list');
        
        if (results.length > 0) {
            listElement.innerHTML = results.map(stock => `
                <div class="autocomplete-item" data-symbol="${stock.symbol}">
                    <div class="autocomplete-symbol">${stock.symbol}</div>
                    <div class="autocomplete-name">${stock.name}</div>
                </div>
            `).join('');
            
            // Add click handlers
            listElement.querySelectorAll('.autocomplete-item').forEach(item => {
                item.addEventListener('click', function() {
                    const symbol = this.dataset.symbol;
                    searchInput.value = symbol;
                    hideAutocomplete();
                    performSearch(symbol);
                });
            });
            
            autocompleteResults.classList.remove('hidden');
        } else {
            hideAutocomplete();
        }
    }
    
    function hideAutocomplete() {
        autocompleteResults.classList.add('hidden');
    }
    
    function performSearch(query) {
        if (!query) return;
        
        hideAutocomplete();
        showLoading();
        
        // Simulate API call
        setTimeout(() => {
            loadStockData(query.toUpperCase());
        }, 1500);
    }
    
    function showLoading() {
        searchResults.classList.remove('hidden');
        currentSymbol = searchInput.value.toUpperCase();
        
        // Show loading state
        showSkeletons();
        
        // Enable action buttons
        const addToWatchlistBtn = document.getElementById('add-to-watchlist');
        const setAlertBtn = document.getElementById('set-alert');
        if (addToWatchlistBtn) addToWatchlistBtn.disabled = false;
        if (setAlertBtn) setAlertBtn.disabled = false;
    }
    
    function loadStockData(symbol) {
        // Mock stock data
        const mockData = {
            symbol: symbol,
            name: getCompanyName(symbol),
            price: (Math.random() * 200 + 50).toFixed(2),
            change: ((Math.random() - 0.5) * 10).toFixed(2),
            changePercent: ((Math.random() - 0.5) * 5).toFixed(2),
            volume: formatNumber(Math.random() * 50000000 + 10000000),
            marketCap: formatNumber(Math.random() * 1000000000000 + 100000000000),
            exchange: 'NASDAQ',
            marketStatus: 'Closed'
        };
        
        updateQuoteCard(mockData);
        loadTabData(symbol);
        hideSkeletons();
        
        RTS.showSuccess(`Loaded data for ${symbol}`);
    }
    
    function updateQuoteCard(data) {
        document.getElementById('stock-symbol').textContent = data.symbol;
        document.getElementById('company-name').textContent = data.name;
        document.getElementById('market-status').textContent = data.marketStatus;
        document.getElementById('exchange').textContent = data.exchange;
        document.getElementById('current-price').textContent = `$${data.price}`;
        
        const changeElement = document.getElementById('price-change');
        const changeValue = parseFloat(data.change);
        changeElement.textContent = `$${data.change} (${data.changePercent}%)`;
        changeElement.className = `change-value ${changeValue >= 0 ? 'text-success' : 'text-danger'}`;
        
        document.getElementById('volume').textContent = data.volume;
        document.getElementById('market-cap').textContent = data.marketCap;
        document.getElementById('change-time').textContent = new Date().toLocaleTimeString();
    }
    
    function loadTabData(symbol) {
        // Load data for different tabs
        loadOverviewData(symbol);
        loadFundamentalsData(symbol);
        loadTechnicalData(symbol);
        loadNewsData(symbol);
    }
    
    function loadOverviewData(symbol) {
        // Mock overview data
        setTimeout(() => {
            document.getElementById('week-52-range').textContent = '$85.23 - $198.45';
            document.getElementById('pe-ratio').textContent = '28.5';
            document.getElementById('dividend-yield').textContent = '2.1%';
            document.getElementById('beta').textContent = '1.25';
            document.getElementById('eps').textContent = '$6.78';
            document.getElementById('avg-volume').textContent = '52.3M';
            document.getElementById('open-price').textContent = `$${(Math.random() * 200 + 50).toFixed(2)}`;
            document.getElementById('high-price').textContent = `$${(Math.random() * 200 + 50).toFixed(2)}`;
            document.getElementById('low-price').textContent = `$${(Math.random() * 200 + 50).toFixed(2)}`;
            document.getElementById('shares-outstanding').textContent = '15.7B';
            
            // Company profile
            const companyDescription = document.getElementById('company-description');
            companyDescription.innerHTML = `
                <p>A leading technology company that designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.</p>
            `;
            
            document.getElementById('sector').textContent = 'Technology';
            document.getElementById('industry').textContent = 'Consumer Electronics';
            document.getElementById('employees').textContent = '164,000';
        }, 500);
    }
    
    function loadFundamentalsData(symbol) {
        // This would populate the fundamentals tables with real data
        console.log('Loading fundamentals for', symbol);
    }
    
    function loadTechnicalData(symbol) {
        // Mock technical indicators
        setTimeout(() => {
            document.getElementById('rsi-value').textContent = '67.2';
            document.getElementById('rsi-signal').textContent = 'Overbought';
            document.getElementById('macd-value').textContent = '2.45';
            document.getElementById('macd-signal').textContent = 'Bullish';
            document.getElementById('sma-20').textContent = '$182.45';
            document.getElementById('sma-50').textContent = '$175.30';
            document.getElementById('sma-200').textContent = '$165.80';
        }, 800);
    }
    
    function loadNewsData(symbol) {
        const newsList = document.getElementById('stock-news-list');
        
        setTimeout(() => {
            newsList.innerHTML = `
                <div class="news-item">
                    <h4 class="news-title">${symbol} Reports Strong Q4 Earnings</h4>
                    <p class="news-excerpt">The company exceeded analyst expectations with revenue growth of 12% year-over-year...</p>
                    <div class="news-meta">
                        <span class="news-source">Reuters</span>
                        <span class="news-time">2 hours ago</span>
                    </div>
                </div>
                <div class="news-item">
                    <h4 class="news-title">Analyst Upgrades ${symbol} to Buy Rating</h4>
                    <p class="news-excerpt">Investment firm raises price target based on strong fundamentals and market position...</p>
                    <div class="news-meta">
                        <span class="news-source">Bloomberg</span>
                        <span class="news-time">4 hours ago</span>
                    </div>
                </div>
            `;
        }, 1000);
    }
    
    function showSkeletons() {
        document.querySelectorAll('.skeleton').forEach(skeleton => {
            skeleton.style.display = 'block';
        });
    }
    
    function hideSkeletons() {
        document.querySelectorAll('.skeleton').forEach(skeleton => {
            skeleton.style.display = 'none';
        });
    }
    
    function hideResults() {
        searchResults.classList.add('hidden');
        const addToWatchlistBtn = document.getElementById('add-to-watchlist');
        const setAlertBtn = document.getElementById('set-alert');
        if (addToWatchlistBtn) addToWatchlistBtn.disabled = true;
        if (setAlertBtn) setAlertBtn.disabled = true;
    }
    
    function getCompanyName(symbol) {
        const companies = {
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.'
        };
        return companies[symbol] || `${symbol} Corporation`;
    }
    
    function formatNumber(num) {
        if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
        if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toString();
    }
});
</script>

<style>
/* Search-specific styles */
.search-section {
    margin-bottom: var(--spacing-2xl);
}

.search-container {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}

.search-header h2 {
    margin-bottom: var(--spacing-sm);
}

.search-description {
    color: var(--gray-600);
    margin-bottom: var(--spacing-xl);
}

.search-input-container {
    display: flex;
    gap: var(--spacing-md);
    align-items: stretch;
}

.search-input-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: var(--spacing-md);
    color: var(--gray-400);
    z-index: 1;
}

.search-input {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-md) var(--spacing-md) calc(var(--spacing-md) * 3);
    font-size: var(--text-lg);
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-xl);
    background: var(--surface-raised);
    transition: all var(--transition-fast) var(--easing-standard);
}

.search-input:focus {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

.search-clear-btn {
    position: absolute;
    right: var(--spacing-md);
    background: none;
    border: none;
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-sm);
    color: var(--gray-400);
    transition: color var(--transition-fast);
}

.search-clear-btn:hover {
    color: var(--gray-600);
}

.search-submit-btn {
    padding: var(--spacing-md) var(--spacing-xl);
    background: var(--primary-500);
    color: white;
    border: none;
    border-radius: var(--radius-xl);
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.search-submit-btn:hover {
    background: var(--primary-600);
    transform: translateY(-1px);
}

.autocomplete-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    z-index: 100;
    margin-top: var(--spacing-xs);
}

.autocomplete-item {
    padding: var(--spacing-md);
    cursor: pointer;
    border-bottom: 1px solid var(--gray-100);
    transition: background var(--transition-fast);
}

.autocomplete-item:last-child {
    border-bottom: none;
}

.autocomplete-item:hover {
    background: var(--gray-50);
}

.autocomplete-symbol {
    font-weight: 600;
    color: var(--primary-600);
}

.autocomplete-name {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.search-form {
    position: relative;
}

/* Stock Quote Card */
.stock-quote-card {
    margin-bottom: var(--spacing-xl);
}

.quote-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-xl);
}

.stock-identity .stock-symbol {
    font-size: var(--text-4xl);
    font-weight: 700;
    margin: 0;
    color: var(--primary-600);
}

.stock-identity .company-name {
    font-size: var(--text-xl);
    color: var(--gray-700);
    margin: var(--spacing-xs) 0 var(--spacing-sm);
}

.stock-metadata {
    display: flex;
    gap: var(--spacing-md);
    font-size: var(--text-sm);
    color: var(--gray-500);
}

.stock-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.quote-content {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: var(--spacing-xl);
}

.current-price .price-value {
    font-size: var(--text-4xl);
    font-weight: 700;
    margin-right: var(--spacing-md);
}

.price-change {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.change-value {
    font-size: var(--text-xl);
    font-weight: 600;
}

.change-time {
    font-size: var(--text-sm);
    color: var(--gray-500);
}

.price-metrics {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-lg);
    margin-top: var(--spacing-xl);
}

.metric {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--gray-100);
}

.metric-label {
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.metric-value {
    font-weight: 600;
    color: var(--gray-900);
}

/* Analysis Tabs */
.analysis-tabs-container {
    margin-bottom: var(--spacing-xl);
}

.tab-panel {
    padding: var(--spacing-xl);
}

.overview-grid {
    gap: var(--spacing-2xl);
}

.overview-section h3 {
    margin-bottom: var(--spacing-lg);
    color: var(--gray-800);
}

.stats-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--gray-100);
}

.stat-label {
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.stat-value {
    font-weight: 600;
    color: var(--gray-900);
}

.company-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.company-description {
    color: var(--gray-700);
    line-height: 1.6;
}

.company-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.detail-item {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-xs) 0;
    border-bottom: 1px solid var(--gray-100);
}

.detail-label {
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.detail-value {
    font-weight: 500;
    color: var(--gray-900);
}

/* Technical Analysis */
.technical-analysis {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2xl);
}

.indicators-grid {
    gap: var(--spacing-lg);
}

.indicator-card {
    background: var(--gray-50);
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    text-align: center;
}

.indicator-card h4 {
    margin: 0 0 var(--spacing-sm);
    color: var(--gray-700);
    font-size: var(--text-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.indicator-value {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--primary-600);
    margin-bottom: var(--spacing-xs);
}

.indicator-signal {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.ma-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
}

/* Historical Data */
.historical-controls {
    margin-bottom: var(--spacing-xl);
}

.date-range-picker {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    flex-wrap: wrap;
}

.date-range-picker label {
    font-weight: 600;
    color: var(--gray-700);
}

.date-range-picker input {
    max-width: 150px;
}

/* News */
.news-filters {
    margin-bottom: var(--spacing-xl);
}

.news-filter-controls {
    display: flex;
    gap: var(--spacing-md);
}

.news-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.news-item {
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast);
}

.news-item:hover {
    box-shadow: var(--shadow-md);
}

.news-title {
    margin: 0 0 var(--spacing-sm);
    font-size: var(--text-lg);
    color: var(--gray-900);
}

.news-excerpt {
    color: var(--gray-700);
    margin: 0 0 var(--spacing-md);
    line-height: 1.5;
}

.news-meta {
    display: flex;
    gap: var(--spacing-md);
    font-size: var(--text-sm);
    color: var(--gray-500);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .search-input-container {
        flex-direction: column;
    }
    
    .quote-content {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }
    
    .price-metrics {
        grid-template-columns: 1fr;
    }
    
    .overview-grid {
        grid-template-columns: 1fr;
    }
    
    .indicators-grid {
        grid-template-columns: 1fr;
    }
    
    .date-range-picker {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>