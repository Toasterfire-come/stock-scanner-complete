/**
 * Stock Scanner Plugin JavaScript
 * Handles remote API integration for hosted WordPress sites
 */

jQuery(document).ready(function($) {
    
    // Configuration
    const AJAX_URL = stockScannerAjax.ajaxurl;
    const NONCE = stockScannerAjax.nonce;
    const CACHE_DURATION = stockScannerAjax.cache_duration || 300;
    
    // Cache for local storage
    const cache = {
        stocks: {},
        news: {},
        market: {}
    };
    
    // Initialize all widgets
    function initWidgets() {
        initStockTickers();
        initNewsWidgets();
        initMarketSummaries();
    }
    
    // Initialize stock ticker widgets
    function initStockTickers() {
        $('.stock-ticker-widget').each(function() {
            const $widget = $(this);
            const widgetId = $widget.attr('id');
            const limit = $widget.data('limit') || 10;
            const category = $widget.data('category') || '';
            const showChanges = $widget.data('show-changes') === 'true';
            const autoRefresh = $widget.data('auto-refresh') === 'true';
            const refreshInterval = ($widget.data('refresh-interval') || 30) * 1000;
            
            // Load initial data
            loadStockData($widget, limit, category, showChanges);
            
            // Set up auto-refresh
            if (autoRefresh) {
                setInterval(function() {
                    loadStockData($widget, limit, category, showChanges);
                }, refreshInterval);
            }
            
            // Set up retry button
            $widget.find('.retry-btn').on('click', function() {
                loadStockData($widget, limit, category, showChanges);
            });
        });
    }
    
    // Initialize news widgets
    function initNewsWidgets() {
        $('.stock-news-widget').each(function() {
            const $widget = $(this);
            const widgetId = $widget.attr('id');
            const limit = $widget.data('limit') || 5;
            const showSentiment = $widget.data('show-sentiment') === 'true';
            const autoRefresh = $widget.data('auto-refresh') === 'true';
            const refreshInterval = ($widget.data('refresh-interval') || 60) * 1000;
            
            // Load initial data
            loadNewsData($widget, limit, showSentiment);
            
            // Set up auto-refresh
            if (autoRefresh) {
                setInterval(function() {
                    loadNewsData($widget, limit, showSentiment);
                }, refreshInterval);
            }
            
            // Set up retry button
            $widget.find('.retry-btn').on('click', function() {
                loadNewsData($widget, limit, showSentiment);
            });
        });
    }
    
    // Initialize market summary widgets
    function initMarketSummaries() {
        $('.market-summary-widget').each(function() {
            const $widget = $(this);
            const widgetId = $widget.attr('id');
            const showChanges = $widget.data('show-changes') === 'true';
            const autoRefresh = $widget.data('auto-refresh') === 'true';
            const refreshInterval = ($widget.data('refresh-interval') || 60) * 1000;
            
            // Load initial data
            loadMarketData($widget, showChanges);
            
            // Set up auto-refresh
            if (autoRefresh) {
                setInterval(function() {
                    loadMarketData($widget, showChanges);
                }, refreshInterval);
            }
            
            // Set up retry button
            $widget.find('.retry-btn').on('click', function() {
                loadMarketData($widget, showChanges);
            });
        });
    }
    
    // Load stock data
    function loadStockData($widget, limit, category, showChanges) {
        const $loading = $widget.find('.ticker-loading');
        const $content = $widget.find('.ticker-content');
        const $error = $widget.find('.ticker-error');
        
        // Show loading
        $loading.show();
        $content.hide();
        $error.hide();
        
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_stocks',
                nonce: NONCE,
                limit: limit,
                category: category
            },
            timeout: 10000,
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateStockTicker($widget, response.data.data, showChanges);
                    updateLastUpdated($widget, new Date());
                    $loading.hide();
                    $content.show();
                } else {
                    showError($widget, 'No stock data available');
                }
            },
            error: function(xhr, status, error) {
                console.error('Stock data error:', error);
                showError($widget, 'Failed to load stock data');
            }
        });
    }
    
    // Load news data
    function loadNewsData($widget, limit, showSentiment) {
        const $loading = $widget.find('.news-loading');
        const $content = $widget.find('.news-content');
        const $error = $widget.find('.news-error');
        
        // Show loading
        $loading.show();
        $content.hide();
        $error.hide();
        
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_news',
                nonce: NONCE,
                limit: limit,
                show_sentiment: showSentiment
            },
            timeout: 10000,
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateNewsWidget($widget, response.data.data, showSentiment);
                    updateLastUpdated($widget, new Date());
                    $loading.hide();
                    $content.show();
                } else {
                    showError($widget, 'No news available');
                }
            },
            error: function(xhr, status, error) {
                console.error('News data error:', error);
                showError($widget, 'Failed to load news');
            }
        });
    }
    
    // Load market data
    function loadMarketData($widget, showChanges) {
        const $loading = $widget.find('.summary-loading');
        const $content = $widget.find('.summary-content');
        const $error = $widget.find('.summary-error');
        
        // Show loading
        $loading.show();
        $content.hide();
        $error.hide();
        
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_market_summary',
                nonce: NONCE
            },
            timeout: 10000,
            success: function(response) {
                if (response.success && response.data) {
                    updateMarketSummary($widget, response.data, showChanges);
                    updateLastUpdated($widget, new Date());
                    $loading.hide();
                    $content.show();
                } else {
                    showError($widget, 'No market data available');
                }
            },
            error: function(xhr, status, error) {
                console.error('Market data error:', error);
                showError($widget, 'Failed to load market data');
            }
        });
    }
    
    // Update stock ticker display
    function updateStockTicker($widget, stocks, showChanges) {
        const $items = $widget.find('.ticker-items');
        let html = '';
        
        stocks.forEach(function(stock) {
            const changeClass = stock.change_percent >= 0 ? 'positive' : 'negative';
            const changeSymbol = stock.change_percent >= 0 ? '+' : '';
            
            html += `
                <div class="ticker-item ${changeClass}">
                    <span class="ticker-symbol">${stock.ticker}</span>
                    <span class="ticker-price">$${stock.current_price}</span>
                    ${showChanges ? `<span class="ticker-change">${changeSymbol}${stock.change_percent}%</span>` : ''}
                </div>
            `;
        });
        
        $items.html(html);
    }
    
    // Update news widget display
    function updateNewsWidget($widget, news, showSentiment) {
        const $items = $widget.find('.news-items');
        let html = '';
        
        news.forEach(function(article) {
            const sentimentClass = showSentiment ? getSentimentClass(article.sentiment_grade) : '';
            
            html += `
                <div class="news-item ${sentimentClass}">
                    <div class="news-header">
                        <h4 class="news-title">
                            <a href="${article.url}" target="_blank">${article.title}</a>
                        </h4>
                        <div class="news-meta">
                            ${showSentiment ? `<span class="sentiment-badge">${article.sentiment_grade}</span>` : ''}
                            <span class="news-date">${formatDate(article.published_at)}</span>
                        </div>
                    </div>
                    <div class="news-summary">${article.summary}</div>
                    ${article.mentioned_tickers ? `<div class="mentioned-tickers">Mentioned: ${article.mentioned_tickers}</div>` : ''}
                </div>
            `;
        });
        
        $items.html(html);
    }
    
    // Update market summary display
    function updateMarketSummary($widget, marketData, showChanges) {
        const $items = $widget.find('.summary-items');
        let html = '';
        
        Object.keys(marketData).forEach(function(index) {
            const data = marketData[index];
            const changeClass = data.change && data.change.includes('+') ? 'positive' : 'negative';
            
            html += `
                <div class="market-item">
                    <span class="market-label">${index}</span>
                    <span class="market-value">
                        ${data.value}
                        ${showChanges && data.change ? `<span class="market-change ${changeClass}">${data.change}</span>` : ''}
                    </span>
                </div>
            `;
        });
        
        $items.html(html);
    }
    
    // Show error message
    function showError($widget, message) {
        const $loading = $widget.find('.ticker-loading, .news-loading, .summary-loading');
        const $error = $widget.find('.ticker-error, .news-error, .summary-error');
        
        $loading.hide();
        $error.find('p').text(message);
        $error.show();
    }
    
    // Update last updated timestamp
    function updateLastUpdated($widget, date) {
        const $lastUpdated = $widget.find('.last-updated');
        const timeString = date.toLocaleTimeString();
        $lastUpdated.text(`Last updated: ${timeString}`);
    }
    
    // Helper functions
    function getSentimentClass(grade) {
        const classes = {
            'A': 'sentiment-excellent',
            'B': 'sentiment-good',
            'C': 'sentiment-neutral',
            'D': 'sentiment-poor',
            'F': 'sentiment-bad'
        };
        return classes[grade] || 'sentiment-neutral';
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    // Admin page functionality
    if ($('#test-api-btn').length) {
        $('#test-api-btn').on('click', function() {
            const $btn = $(this);
            const $result = $('#test-result');
            
            $btn.prop('disabled', true).text('Testing...');
            $result.html('');
            
            // Test stock API
            $.ajax({
                url: AJAX_URL,
                type: 'POST',
                data: {
                    action: 'get_stocks',
                    nonce: NONCE,
                    limit: 1
                },
                timeout: 10000,
                success: function(response) {
                    if (response.success) {
                        $result.html('<div class="notice notice-success"><p>✅ API connection successful!</p></div>');
                    } else {
                        $result.html('<div class="notice notice-error"><p>❌ API connection failed: ' + response.data + '</p></div>');
                    }
                },
                error: function(xhr, status, error) {
                    $result.html('<div class="notice notice-error"><p>❌ API connection failed: ' + error + '</p></div>');
                },
                complete: function() {
                    $btn.prop('disabled', false).text('Test Connection');
                }
            });
        });
    }
    
    // Initialize widgets
    initWidgets();
    
    // Global error handling
    $(document).ajaxError(function(event, xhr, settings, error) {
        console.error('AJAX Error:', error);
    });
    
});