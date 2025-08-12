<?php
/**
 * Template Name: Stock News
 * 
 * The template for displaying stock market news
 */

get_header(); 
?>

<div class="stock-news-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-newspaper"></i>
                Stock Market News
            </h1>
            <p class="page-subtitle">Stay updated with the latest market developments and financial insights</p>
        </div>
    </div>

    <div class="news-content">
        <div class="container">
            <!-- News Filters -->
            <div class="news-filters">
                <div class="filter-tabs">
                    <button class="filter-tab active" data-category="all">All News</button>
                    <button class="filter-tab" data-category="breaking">Breaking</button>
                    <button class="filter-tab" data-category="markets">Markets</button>
                    <button class="filter-tab" data-category="earnings">Earnings</button>
                    <button class="filter-tab" data-category="crypto">Crypto</button>
                    <button class="filter-tab" data-category="analysis">Analysis</button>
                </div>
                
                <div class="filter-controls">
                    <input type="text" id="newsSearch" placeholder="Search news..." class="search-input">
                    <select id="sourceFilter" class="source-filter">
                        <option value="all">All Sources</option>
                        <option value="reuters">Reuters</option>
                        <option value="bloomberg">Bloomberg</option>
                        <option value="marketwatch">MarketWatch</option>
                        <option value="cnbc">CNBC</option>
                    </select>
                </div>
            </div>

            <!-- Featured News -->
            <div class="featured-news">
                <h2>Featured Stories</h2>
                <div class="featured-grid" id="featuredNews">
                    <div class="loading-spinner">Loading featured news...</div>
                </div>
            </div>

            <!-- News Feed -->
            <div class="news-feed">
                <div class="news-header">
                    <h2>Latest News</h2>
                    <div class="view-options">
                        <button class="view-btn active" data-view="list">
                            <i class="fas fa-list"></i>
                        </button>
                        <button class="view-btn" data-view="grid">
                            <i class="fas fa-th"></i>
                        </button>
                    </div>
                </div>
                
                <div class="news-list" id="newsList">
                    <div class="loading-spinner">Loading news...</div>
                </div>
                
                <div class="load-more-container">
                    <button class="btn btn-primary" id="loadMoreBtn">
                        Load More News
                    </button>
                </div>
            </div>

            <!-- Market Pulse -->
            <div class="market-pulse">
                <h2>Market Pulse</h2>
                <div class="pulse-grid">
                    <div class="pulse-card">
                        <h3>Market Sentiment</h3>
                        <div class="sentiment-meter">
                            <div class="sentiment-bar">
                                <div class="sentiment-fill" style="width: 65%"></div>
                            </div>
                            <span class="sentiment-label">Bullish (65%)</span>
                        </div>
                    </div>
                    
                    <div class="pulse-card">
                        <h3>Fear & Greed Index</h3>
                        <div class="fear-greed-meter">
                            <div class="meter-circle">
                                <span class="meter-value">72</span>
                            </div>
                            <span class="meter-label">Greed</span>
                        </div>
                    </div>
                    
                    <div class="pulse-card">
                        <h3>Top Movers</h3>
                        <div class="movers-list">
                            <div class="mover-item">
                                <span class="symbol">TSLA</span>
                                <span class="change positive">+5.2%</span>
                            </div>
                            <div class="mover-item">
                                <span class="symbol">NVDA</span>
                                <span class="change positive">+3.8%</span>
                            </div>
                            <div class="mover-item">
                                <span class="symbol">META</span>
                                <span class="change negative">-2.1%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.stock-news-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 0 0;
}

.news-content {
    padding: 2rem 0;
}

.news-filters {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}

.filter-tabs {
    display: flex;
    gap: 0.5rem;
}

.filter-tab {
    padding: 0.75rem 1.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}

.filter-tab:hover,
.filter-tab.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.filter-controls {
    display: flex;
    gap: 1rem;
}

.search-input {
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    outline: none;
    min-width: 200px;
}

.search-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.source-filter {
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    outline: none;
}

.featured-news {
    margin-bottom: 3rem;
}

.featured-news h2 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 1.5rem 0;
    color: #1a1a1a;
}

.featured-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

.featured-main {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    background: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.featured-image {
    width: 100%;
    height: 300px;
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 4rem;
}

.featured-content {
    padding: 1.5rem;
}

.featured-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
    line-height: 1.3;
}

.featured-summary {
    color: #666;
    line-height: 1.6;
    margin: 0 0 1rem 0;
}

.featured-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    color: #888;
}

.featured-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.sidebar-story {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.2s;
}

.sidebar-story:hover {
    transform: translateY(-2px);
}

.sidebar-title {
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
    line-height: 1.4;
    font-size: 0.95rem;
}

.sidebar-meta {
    font-size: 0.8rem;
    color: #888;
}

.news-feed {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.news-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.news-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    color: #1a1a1a;
}

.view-options {
    display: flex;
    gap: 0.5rem;
}

.view-btn {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
}

.view-btn:hover,
.view-btn.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.news-list {
    min-height: 200px;
}

.news-item {
    display: flex;
    gap: 1rem;
    padding: 1.5rem 0;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
}

.news-item:hover {
    background: #f8f9fa;
    margin: 0 -1.5rem;
    padding: 1.5rem;
    border-radius: 8px;
}

.news-item:last-child {
    border-bottom: none;
}

.news-thumbnail {
    width: 120px;
    height: 80px;
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.news-info {
    flex: 1;
}

.news-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
    line-height: 1.4;
    cursor: pointer;
}

.news-title:hover {
    color: #3685fb;
}

.news-excerpt {
    color: #666;
    line-height: 1.5;
    margin: 0 0 0.75rem 0;
    font-size: 0.95rem;
}

.news-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: #888;
}

.news-source {
    font-weight: 500;
}

.load-more-container {
    text-align: center;
    margin-top: 2rem;
}

.btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-block;
}

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(54, 133, 251, 0.3);
}

.market-pulse {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.market-pulse h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 1.5rem 0;
    color: #1a1a1a;
}

.pulse-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.pulse-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
}

.pulse-card h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: #333;
}

.sentiment-meter {
    text-align: center;
}

.sentiment-bar {
    width: 100%;
    height: 8px;
    background: #e1e5e9;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.sentiment-fill {
    height: 100%;
    background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
    transition: width 0.3s ease;
}

.sentiment-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #10b981;
}

.fear-greed-meter {
    text-align: center;
}

.meter-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, #ef4444 0deg, #f59e0b 72deg, #10b981 144deg, #f59e0b 216deg, #ef4444 288deg, #ef4444 360deg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.5rem auto;
    position: relative;
}

.meter-circle::before {
    content: '';
    position: absolute;
    width: 60px;
    height: 60px;
    background: white;
    border-radius: 50%;
}

.meter-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #333;
    position: relative;
    z-index: 1;
}

.meter-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #f59e0b;
}

.movers-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.mover-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: white;
    border-radius: 6px;
}

.symbol {
    font-weight: 700;
    color: #333;
}

.change {
    font-weight: 600;
    font-size: 0.9rem;
}

.change.positive { color: #10b981; }
.change.negative { color: #ef4444; }

.loading-spinner {
    text-align: center;
    color: #666;
    padding: 3rem;
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .news-filters {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .filter-tabs {
        overflow-x: auto;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
    }
    
    .filter-controls {
        flex-direction: column;
    }
    
    .featured-grid {
        grid-template-columns: 1fr;
    }
    
    .news-item {
        flex-direction: column;
    }
    
    .news-thumbnail {
        width: 100%;
        height: 150px;
    }
    
    .pulse-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeNewsPage();
    loadFeaturedNews();
    loadNewsFeed();
});

function initializeNewsPage() {
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            filterNewsByCategory(this.dataset.category);
        });
    });
    
    // Search functionality
    document.getElementById('newsSearch').addEventListener('input', handleNewsSearch);
    
    // Source filter
    document.getElementById('sourceFilter').addEventListener('change', handleSourceFilter);
    
    // View options
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            toggleView(this.dataset.view);
        });
    });
    
    // Load more button
    document.getElementById('loadMoreBtn').addEventListener('click', loadMoreNews);
}

function loadFeaturedNews() {
    const featuredContainer = document.getElementById('featuredNews');
    
    setTimeout(() => {
        const featuredHTML = `
            <div class="featured-main">
                <div class="featured-image">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="featured-content">
                    <h3 class="featured-title">Market Rally Continues as Tech Stocks Surge to New Highs</h3>
                    <p class="featured-summary">Technology stocks led a broad market rally today, with the NASDAQ hitting record highs as investors remained optimistic about earnings season. Major tech companies showed strong performance...</p>
                    <div class="featured-meta">
                        <span class="featured-source">MarketWatch</span>
                        <span class="featured-time">2 hours ago</span>
                    </div>
                </div>
            </div>
            <div class="featured-sidebar">
                <div class="sidebar-story">
                    <h4 class="sidebar-title">Federal Reserve Signals Potential Rate Changes in Coming Months</h4>
                    <div class="sidebar-meta">Reuters • 1 hour ago</div>
                </div>
                <div class="sidebar-story">
                    <h4 class="sidebar-title">Earnings Season Kicks Off with Strong Bank Results</h4>
                    <div class="sidebar-meta">Bloomberg • 3 hours ago</div>
                </div>
                <div class="sidebar-story">
                    <h4 class="sidebar-title">Cryptocurrency Market Shows Signs of Recovery</h4>
                    <div class="sidebar-meta">CNBC • 4 hours ago</div>
                </div>
                <div class="sidebar-story">
                    <h4 class="sidebar-title">Oil Prices Rise on Supply Concerns</h4>
                    <div class="sidebar-meta">MarketWatch • 5 hours ago</div>
                </div>
            </div>
        `;
        
        featuredContainer.innerHTML = featuredHTML;
    }, 1000);
}

function loadNewsFeed() {
    const newsContainer = document.getElementById('newsList');
    
    setTimeout(() => {
        const newsItems = [
            {
                title: "Apple Reports Strong Q4 Earnings Despite Supply Chain Challenges",
                excerpt: "Apple exceeded analyst expectations with quarterly revenue of $117.2 billion, driven by strong iPhone sales and services growth...",
                source: "Reuters",
                time: "30 minutes ago",
                category: "earnings"
            },
            {
                title: "Tesla Stock Jumps 8% on Production Milestone Announcement",
                excerpt: "Tesla shares surged in after-hours trading following the company's announcement of reaching its production targets ahead of schedule...",
                source: "Bloomberg",
                time: "1 hour ago",
                category: "markets"
            },
            {
                title: "Federal Reserve Minutes Reveal Split on Interest Rate Policy",
                excerpt: "The latest Federal Reserve meeting minutes show division among policymakers regarding the pace of future interest rate adjustments...",
                source: "CNBC",
                time: "2 hours ago",
                category: "breaking"
            },
            {
                title: "Microsoft's Azure Revenue Growth Slows But Beats Estimates",
                excerpt: "Microsoft reported cloud revenue growth of 22%, slightly below the previous quarter but still exceeding Wall Street expectations...",
                source: "MarketWatch",
                time: "3 hours ago",
                category: "earnings"
            },
            {
                title: "Bitcoin Breaks $45,000 as Institutional Adoption Continues",
                excerpt: "Bitcoin reached a new multi-month high as more institutional investors enter the cryptocurrency market...",
                source: "CoinDesk",
                time: "4 hours ago",
                category: "crypto"
            }
        ];
        
        const newsHTML = newsItems.map(item => `
            <div class="news-item" data-category="${item.category}">
                <div class="news-thumbnail">
                    <i class="fas fa-newspaper"></i>
                </div>
                <div class="news-info">
                    <h3 class="news-title">${item.title}</h3>
                    <p class="news-excerpt">${item.excerpt}</p>
                    <div class="news-meta">
                        <span class="news-source">${item.source}</span>
                        <span class="news-time">${item.time}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        newsContainer.innerHTML = newsHTML;
    }, 1500);
}

function filterNewsByCategory(category) {
    const newsItems = document.querySelectorAll('.news-item');
    
    newsItems.forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function handleNewsSearch() {
    const searchTerm = document.getElementById('newsSearch').value.toLowerCase();
    const newsItems = document.querySelectorAll('.news-item');
    
    newsItems.forEach(item => {
        const title = item.querySelector('.news-title').textContent.toLowerCase();
        const excerpt = item.querySelector('.news-excerpt').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || excerpt.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function handleSourceFilter() {
    const selectedSource = document.getElementById('sourceFilter').value;
    const newsItems = document.querySelectorAll('.news-item');
    
    newsItems.forEach(item => {
        const source = item.querySelector('.news-source').textContent.toLowerCase();
        
        if (selectedSource === 'all' || source.includes(selectedSource.toLowerCase())) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function toggleView(view) {
    const newsList = document.getElementById('newsList');
    
    if (view === 'grid') {
        newsList.style.display = 'grid';
        newsList.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
        newsList.style.gap = '1.5rem';
        
        // Modify news items for grid view
        document.querySelectorAll('.news-item').forEach(item => {
            item.style.flexDirection = 'column';
            item.style.background = '#f8f9fa';
            item.style.borderRadius = '8px';
            item.style.padding = '1rem';
            item.style.border = 'none';
        });
    } else {
        newsList.style.display = 'block';
        newsList.style.gridTemplateColumns = 'none';
        
        // Reset news items for list view
        document.querySelectorAll('.news-item').forEach(item => {
            item.style.flexDirection = 'row';
            item.style.background = 'transparent';
            item.style.borderRadius = '0';
            item.style.padding = '1.5rem 0';
            item.style.borderBottom = '1px solid #f0f0f0';
        });
    }
}

function loadMoreNews() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    loadMoreBtn.textContent = 'Loading...';
    loadMoreBtn.disabled = true;
    
    // Simulate loading more news
    setTimeout(() => {
        loadMoreBtn.textContent = 'Load More News';
        loadMoreBtn.disabled = false;
        
        showNotification('More news loaded successfully!', 'success');
    }, 2000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
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
        zIndex: '1001',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        minWidth: '300px'
    });
    
    const closeBtn = notification.querySelector('button');
    Object.assign(closeBtn.style, {
        background: 'none',
        border: 'none',
        color: 'white',
        fontSize: '1.25rem',
        cursor: 'pointer',
        padding: '0'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}
</script>

<?php get_footer(); ?>