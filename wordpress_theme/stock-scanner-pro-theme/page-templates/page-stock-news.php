<?php
/**
 * Template Name: Stock News Page
 * Individual page for stock news feed functionality
 */

get_header(); ?>

<div class="stock-news-page">
    <div class="container">
        <div class="page-header">
            <h1>📰 Stock Market News</h1>
            <p class="page-description">Stay updated with the latest financial news and market analysis</p>
        </div>

        <div class="news-container">
            <!-- News Filters -->
            <div class="news-filters-section">
                <div class="filters-card">
                    <h3>🔍 Filter News</h3>
                    <div class="filter-controls">
                        <div class="filter-group">
                            <label for="news-category">Category:</label>
                            <select id="news-category">
                                <option value="all">All News</option>
                                <option value="general">General Market</option>
                                <option value="earnings">Earnings</option>
                                <option value="mergers">M&A</option>
                                <option value="ipo">IPOs</option>
                                <option value="crypto">Cryptocurrency</option>
                                <option value="commodities">Commodities</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label for="news-symbol">Stock Symbol:</label>
                            <input type="text" id="news-symbol" placeholder="e.g., AAPL, GOOGL" maxlength="10" />
                        </div>
                        
                        <div class="filter-group">
                            <label for="news-timeframe">Timeframe:</label>
                            <select id="news-timeframe">
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                            </select>
                        </div>
                        
                        <button id="apply-filters" class="btn btn-primary">Apply Filters</button>
                        <button id="clear-filters" class="btn btn-secondary">Clear</button>
                    </div>
                </div>
            </div>

            <!-- Breaking News Banner -->
            <div class="breaking-news-section">
                <div class="breaking-news-banner">
                    <span class="breaking-label">🔴 BREAKING</span>
                    <div class="breaking-news-text" id="breaking-news-text">
                        Loading latest breaking news...
                    </div>
                </div>
            </div>

            <!-- News Feed -->
            <div class="news-feed-section">
                <div class="news-header">
                    <h2>📈 Latest News</h2>
                    <button id="refresh-news" class="btn btn-outline">🔄 Refresh</button>
                </div>
                
                <div class="loading-indicator" id="news-loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading latest news...</p>
                </div>
                
                <div id="news-feed" class="news-feed">
                    <!-- News articles will be loaded here -->
                </div>
                
                <div class="load-more-section">
                    <button id="load-more-news" class="btn btn-secondary">Load More News</button>
                </div>
            </div>

            <!-- Trending Topics -->
            <div class="trending-section">
                <h3>🔥 Trending Topics</h3>
                <div id="trending-topics" class="trending-topics">
                    <!-- Trending topics will be loaded here -->
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.stock-news-page {
    padding: 40px 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-header h1 {
    color: #2271b1;
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.page-description {
    color: #646970;
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
}

.news-container {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    gap: 30px;
}

.filters-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
}

.filters-card h3 {
    margin: 0 0 20px 0;
    color: #1d2327;
    font-size: 1.3rem;
}

.filter-controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    align-items: end;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-group label {
    font-weight: 600;
    color: #1d2327;
    font-size: 0.9rem;
}

.filter-group select,
.filter-group input {
    padding: 10px 12px;
    border: 2px solid #e1e1e1;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: border-color 0.3s ease;
}

.filter-group select:focus,
.filter-group input:focus {
    outline: none;
    border-color: #2271b1;
}

.breaking-news-banner {
    background: linear-gradient(90deg, #d63638 0%, #b91c1c 100%);
    color: white;
    padding: 15px 25px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 4px 12px rgba(214, 54, 56, 0.3);
    animation: pulse-breaking 2s infinite;
}

@keyframes pulse-breaking {
    0%, 100% { box-shadow: 0 4px 12px rgba(214, 54, 56, 0.3); }
    50% { box-shadow: 0 6px 20px rgba(214, 54, 56, 0.5); }
}

.breaking-label {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: bold;
    white-space: nowrap;
}

.breaking-news-text {
    flex: 1;
    font-weight: 500;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.news-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.news-header h2 {
    margin: 0;
    color: #1d2327;
    font-size: 1.5rem;
}

.news-feed {
    display: grid;
    gap: 20px;
}

.news-article {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    transition: all 0.3s ease;
    cursor: pointer;
}

.news-article:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.article-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
}

.article-category {
    background: #f0f6ff;
    color: #2271b1;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.article-time {
    color: #646970;
    font-size: 0.9rem;
}

.article-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1d2327;
    margin: 0 0 10px 0;
    line-height: 1.4;
}

.article-summary {
    color: #646970;
    line-height: 1.6;
    margin-bottom: 15px;
}

.article-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
}

.article-source {
    font-size: 0.9rem;
    color: #646970;
    font-weight: 500;
}

.article-symbols {
    display: flex;
    gap: 8px;
}

.symbol-tag {
    background: #f0f0f0;
    color: #646970;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 500;
}

.trending-topics {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.trending-topic {
    background: white;
    color: #2271b1;
    border: 2px solid #e1e1e1;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.trending-topic:hover {
    background: #2271b1;
    color: white;
    transform: translateY(-1px);
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

.btn-primary {
    background: #2271b1;
    color: white;
}

.btn-primary:hover {
    background: #135e96;
    transform: translateY(-1px);
}

.btn-secondary {
    background: #646970;
    color: white;
}

.btn-secondary:hover {
    background: #50575e;
}

.btn-outline {
    background: transparent;
    color: #2271b1;
    border: 2px solid #2271b1;
}

.btn-outline:hover {
    background: #2271b1;
    color: white;
}

.loading-indicator {
    text-align: center;
    padding: 40px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #2271b1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.load-more-section {
    text-align: center;
    margin-top: 30px;
}

@media (max-width: 768px) {
    .filter-controls {
        grid-template-columns: 1fr;
    }
    
    .news-header {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }
    
    .breaking-news-banner {
        flex-direction: column;
        text-align: center;
        gap: 10px;
    }
    
    .breaking-news-text {
        white-space: normal;
    }
    
    .article-header {
        flex-direction: column;
        gap: 10px;
    }
    
    .article-footer {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const newsCategory = document.getElementById('news-category');
    const newsSymbol = document.getElementById('news-symbol');
    const newsTimeframe = document.getElementById('news-timeframe');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const refreshNewsBtn = document.getElementById('refresh-news');
    const loadMoreBtn = document.getElementById('load-more-news');
    const newsFeed = document.getElementById('news-feed');
    const newsLoading = document.getElementById('news-loading');
    const breakingNewsText = document.getElementById('breaking-news-text');
    const trendingTopics = document.getElementById('trending-topics');

    let currentPage = 1;
    let isLoading = false;

    // Event listeners
    applyFiltersBtn.addEventListener('click', function() {
        currentPage = 1;
        loadNews(true);
    });

    clearFiltersBtn.addEventListener('click', function() {
        newsCategory.value = 'all';
        newsSymbol.value = '';
        newsTimeframe.value = 'today';
        currentPage = 1;
        loadNews(true);
    });

    refreshNewsBtn.addEventListener('click', function() {
        currentPage = 1;
        loadNews(true);
        loadBreakingNews();
        loadTrendingTopics();
    });

    loadMoreBtn.addEventListener('click', function() {
        currentPage++;
        loadNews(false);
    });

    // Load initial data
    loadNews(true);
    loadBreakingNews();
    loadTrendingTopics();

    function loadNews(clearExisting = false) {
        if (isLoading) return;
        
        isLoading = true;
        newsLoading.style.display = 'block';
        
        if (clearExisting) {
            newsFeed.innerHTML = '';
        }

        // Simulate API call with mock data
        setTimeout(() => {
            const mockNews = generateMockNews();
            displayNews(mockNews, clearExisting);
            newsLoading.style.display = 'none';
            isLoading = false;
        }, 1000);
    }

    function generateMockNews() {
        const categories = ['general', 'earnings', 'mergers', 'ipo', 'crypto', 'commodities'];
        const symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX'];
        const sources = ['Reuters', 'Bloomberg', 'MarketWatch', 'CNBC', 'Financial Times', 'Wall Street Journal'];
        
        const newsTemplates = [
            {
                title: "Tech Giants Show Strong Q4 Performance Despite Market Volatility",
                summary: "Major technology companies reported better-than-expected earnings, driving market optimism despite ongoing economic uncertainties."
            },
            {
                title: "Federal Reserve Signals Potential Rate Changes in Upcoming Meeting",
                summary: "Market analysts anticipate significant monetary policy decisions that could impact investment strategies across all sectors."
            },
            {
                title: "Breakthrough AI Technology Drives Semiconductor Stock Rally",
                summary: "Advanced artificial intelligence applications are creating new opportunities in the semiconductor industry, boosting related stock prices."
            },
            {
                title: "Energy Sector Sees Major Investment Shift Toward Renewables",
                summary: "Traditional energy companies are pivoting toward sustainable solutions, attracting significant institutional investment."
            },
            {
                title: "Healthcare Innovation Sparks Biotech Stock Surge",
                summary: "Revolutionary medical treatments and drug developments are driving unprecedented growth in biotechnology investments."
            }
        ];

        return Array.from({length: 8}, (_, i) => {
            const template = newsTemplates[i % newsTemplates.length];
            const category = categories[Math.floor(Math.random() * categories.length)];
            const relatedSymbols = symbols.slice(0, Math.floor(Math.random() * 3) + 1);
            const source = sources[Math.floor(Math.random() * sources.length)];
            
            return {
                id: Date.now() + i,
                title: template.title,
                summary: template.summary,
                category: category,
                symbols: relatedSymbols,
                source: source,
                time: new Date(Date.now() - Math.random() * 86400000).toLocaleString(),
                url: '#'
            };
        });
    }

    function displayNews(newsItems, clearExisting) {
        if (clearExisting) {
            newsFeed.innerHTML = '';
        }

        newsItems.forEach(item => {
            const articleElement = createNewsArticle(item);
            newsFeed.appendChild(articleElement);
        });
    }

    function createNewsArticle(item) {
        const article = document.createElement('div');
        article.className = 'news-article';
        article.onclick = () => openNewsArticle(item);
        
        article.innerHTML = `
            <div class="article-header">
                <span class="article-category">${item.category}</span>
                <span class="article-time">${item.time}</span>
            </div>
            <h3 class="article-title">${item.title}</h3>
            <p class="article-summary">${item.summary}</p>
            <div class="article-footer">
                <span class="article-source">📰 ${item.source}</span>
                <div class="article-symbols">
                    ${item.symbols.map(symbol => `<span class="symbol-tag">${symbol}</span>`).join('')}
                </div>
            </div>
        `;
        
        return article;
    }

    function openNewsArticle(item) {
        // In a real implementation, this would open the full article
        alert(`Opening article: ${item.title}\n\nThis would typically open the full article or redirect to the source.`);
    }

    function loadBreakingNews() {
        // Simulate breaking news
        const breakingNews = [
            "Market opens higher following positive economic data release",
            "Major tech acquisition announced, shares surge in pre-market trading",
            "Federal Reserve minutes reveal key insights into future policy direction",
            "Breakthrough drug approval sends biotech stocks soaring",
            "Energy sector rally continues amid supply chain improvements"
        ];
        
        const randomNews = breakingNews[Math.floor(Math.random() * breakingNews.length)];
        breakingNewsText.textContent = randomNews;
    }

    function loadTrendingTopics() {
        const topics = [
            'Artificial Intelligence', 'Electric Vehicles', 'Renewable Energy', 'Biotechnology',
            'Cryptocurrency', 'Supply Chain', 'Inflation', 'Interest Rates', 'Tech Earnings',
            'Market Volatility', 'ESG Investing', 'Digital Transformation'
        ];
        
        trendingTopics.innerHTML = topics.map(topic => 
            `<span class="trending-topic" onclick="searchNewsByTopic('${topic}')">${topic}</span>`
        ).join('');
    }

    window.searchNewsByTopic = function(topic) {
        newsSymbol.value = '';
        newsCategory.value = 'all';
        // In a real implementation, this would filter news by topic
        alert(`Searching news for: ${topic}`);
        loadNews(true);
    };

    // Auto-refresh breaking news every 30 seconds
    setInterval(loadBreakingNews, 30000);
});
</script>

<?php get_footer(); ?>