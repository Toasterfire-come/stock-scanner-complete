/**
 * Stock Scanner JavaScript
 * Handles API integration and dynamic content updates
 */

jQuery(document).ready(function($) {
    
    // Configuration
    const API_URL = stockScannerAjax.api_url;
    const AJAX_URL = stockScannerAjax.ajaxurl;
    const NONCE = stockScannerAjax.nonce;
    
    // Cache for API responses
    const cache = {
        stocks: null,
        news: null,
        lastUpdate: null
    };
    
    // Initialize the application
    function init() {
        loadStockTicker();
        loadNewsFeed();
        loadMarketSummary();
        
        // Auto-refresh every 30 seconds
        setInterval(function() {
            loadStockTicker();
            loadNewsFeed();
            loadMarketSummary();
        }, 30000);
    }
    
    // Load stock ticker data
    function loadStockTicker() {
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_stocks',
                nonce: NONCE,
                limit: 10,
                category: 'gainers'
            },
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateStockTicker(response.data.data);
                    cache.stocks = response.data.data;
                }
            },
            error: function() {
                console.log('Failed to load stock data');
            }
        });
    }
    
    // Update stock ticker display
    function updateStockTicker(stocks) {
        const tickerContent = $('.ticker-scroll');
        let tickerHtml = '';
        
        stocks.forEach(function(stock) {
            const changeClass = stock.change_percent >= 0 ? 'positive' : 'negative';
            const changeSymbol = stock.change_percent >= 0 ? '+' : '';
            
            tickerHtml += `
                <span class="ticker-item ${changeClass}">
                    ${stock.ticker} $${stock.current_price} 
                    <span class="change">${changeSymbol}${stock.change_percent}%</span>
                </span>
            `;
        });
        
        tickerContent.html(tickerHtml);
        
        // Animate ticker scroll
        animateTicker();
    }
    
    // Animate ticker scrolling
    function animateTicker() {
        const tickerScroll = $('.ticker-scroll');
        const tickerContent = tickerScroll.find('.ticker-item');
        const scrollWidth = tickerContent.outerWidth(true) * tickerContent.length;
        
        tickerScroll.css('width', scrollWidth + 'px');
        
        tickerScroll.animate({
            scrollLeft: scrollWidth
        }, 20000, 'linear', function() {
            tickerScroll.scrollLeft(0);
            animateTicker();
        });
    }
    
    // Load news feed
    function loadNewsFeed() {
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_news',
                nonce: NONCE,
                limit: 5
            },
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateNewsFeed(response.data.data);
                    cache.news = response.data.data;
                }
            },
            error: function() {
                console.log('Failed to load news data');
            }
        });
    }
    
    // Update news feed display
    function updateNewsFeed(news) {
        const newsContent = $('.news-content');
        let newsHtml = '';
        
        news.forEach(function(article) {
            const sentimentClass = getSentimentClass(article.sentiment_grade);
            const impactClass = getImpactClass(article.impact_score);
            
            newsHtml += `
                <article class="news-item ${sentimentClass} ${impactClass}">
                    <div class="news-header">
                        <h3 class="news-title">
                            <a href="${article.url}" target="_blank">${article.title}</a>
                        </h3>
                        <div class="news-meta">
                            <span class="sentiment-grade">${article.sentiment_grade}</span>
                            <span class="impact-score">Impact: ${article.impact_score}/10</span>
                            <span class="published-date">${formatDate(article.published_at)}</span>
                        </div>
                    </div>
                    <div class="news-summary">${article.summary}</div>
                    ${article.mentioned_tickers ? `<div class="mentioned-tickers">Mentioned: ${article.mentioned_tickers}</div>` : ''}
                </article>
            `;
        });
        
        newsContent.html(newsHtml);
        $('.news-loading').hide();
        newsContent.show();
    }
    
    // Load market summary
    function loadMarketSummary() {
        // For now, use sample data - replace with actual API call
        const marketData = {
            'S&P 500': { value: '4,567.89', change: '+1.23%' },
            'NASDAQ': { value: '14,234.56', change: '+0.87%' },
            'DOW': { value: '34,567.12', change: '+0.45%' }
        };
        
        updateMarketSummary(marketData);
    }
    
    // Update market summary display
    function updateMarketSummary(marketData) {
        $('#sp500-value').html(`${marketData['S&P 500'].value} <span class="change positive">${marketData['S&P 500'].change}</span>`);
        $('#nasdaq-value').html(`${marketData['NASDAQ'].value} <span class="change positive">${marketData['NASDAQ'].change}</span>`);
        $('#dow-value').html(`${marketData['DOW'].value} <span class="change positive">${marketData['DOW'].change}</span>`);
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
    
    function getImpactClass(score) {
        if (score >= 8) return 'impact-high';
        if (score >= 5) return 'impact-medium';
        return 'impact-low';
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    // Stock ticker shortcode functionality
    $('.stock-ticker').each(function() {
        const $ticker = $(this);
        const limit = $ticker.data('limit') || 10;
        const category = $ticker.data('category') || '';
        const showChanges = $ticker.data('show-changes') === 'true';
        
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_stocks',
                nonce: NONCE,
                limit: limit,
                category: category
            },
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateTickerWidget($ticker, response.data.data, showChanges);
                }
            }
        });
    });
    
    // News shortcode functionality
    $('.stock-news').each(function() {
        const $news = $(this);
        const limit = $news.data('limit') || 5;
        const showSentiment = $news.data('show-sentiment') === 'true';
        
        $.ajax({
            url: AJAX_URL,
            type: 'POST',
            data: {
                action: 'get_news',
                nonce: NONCE,
                limit: limit
            },
            success: function(response) {
                if (response.success && response.data && response.data.data) {
                    updateNewsWidget($news, response.data.data, showSentiment);
                }
            }
        });
    });
    
    // Update ticker widget
    function updateTickerWidget($widget, stocks, showChanges) {
        const $content = $widget.find('.ticker-content');
        let html = '<div class="ticker-widget">';
        
        stocks.forEach(function(stock) {
            const changeClass = stock.change_percent >= 0 ? 'positive' : 'negative';
            const changeSymbol = stock.change_percent >= 0 ? '+' : '';
            
            html += `
                <div class="ticker-widget-item ${changeClass}">
                    <span class="ticker-symbol">${stock.ticker}</span>
                    <span class="ticker-price">$${stock.current_price}</span>
                    ${showChanges ? `<span class="ticker-change">${changeSymbol}${stock.change_percent}%</span>` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        $content.html(html);
        $widget.find('.ticker-loading').hide();
        $content.show();
    }
    
    // Update news widget
    function updateNewsWidget($widget, news, showSentiment) {
        const $content = $widget.find('.news-content');
        let html = '<div class="news-widget">';
        
        news.forEach(function(article) {
            const sentimentClass = showSentiment ? getSentimentClass(article.sentiment_grade) : '';
            
            html += `
                <div class="news-widget-item ${sentimentClass}">
                    <h4 class="news-widget-title">
                        <a href="${article.url}" target="_blank">${article.title}</a>
                    </h4>
                    <div class="news-widget-meta">
                        ${showSentiment ? `<span class="sentiment-badge">${article.sentiment_grade}</span>` : ''}
                        <span class="news-date">${formatDate(article.published_at)}</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        $content.html(html);
        $widget.find('.news-loading').hide();
        $content.show();
    }
    
    // Initialize the application
    init();
    
});