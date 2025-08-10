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
            <!-- Tabs for categories and personalized feed -->
            <ul class="nav nav-tabs" id="news-tabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="personalized-tab" data-bs-toggle="tab" data-bs-target="#personalized" type="button" role="tab">For You</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="business-tab" data-bs-toggle="tab" data-bs-target="#business" type="button" role="tab">Business</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="technology-tab" data-bs-toggle="tab" data-bs-target="#technology" type="button" role="tab">Technology</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="markets-tab" data-bs-toggle="tab" data-bs-target="#markets" type="button" role="tab">Markets</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="earnings-tab" data-bs-toggle="tab" data-bs-target="#earnings" type="button" role="tab">Earnings</button>
                </li>
            </ul>

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
                    <div class="breaking-news-text" id="breaking-news-text">Loading latest breaking news...</div>
                </div>
            </div>

            <!-- Tabbed News Feeds -->
            <div class="tab-content" id="news-tab-content">
                <div class="tab-pane fade show active" id="personalized" role="tabpanel">
                    <div class="news-feed" id="personalized-feed"></div>
                </div>
                <div class="tab-pane fade" id="business" role="tabpanel">
                    <div class="news-feed" id="business-feed"></div>
                </div>
                <div class="tab-pane fade" id="technology" role="tabpanel">
                    <div class="news-feed" id="technology-feed"></div>
                </div>
                <div class="tab-pane fade" id="markets" role="tabpanel">
                    <div class="news-feed" id="markets-feed"></div>
                </div>
                <div class="tab-pane fade" id="earnings" role="tabpanel">
                    <div class="news-feed" id="earnings-feed"></div>
                </div>
            </div>

            <!-- Controls -->
            <div class="news-feed-section">
                <div class="news-header">
                    <h2>📈 Latest News</h2>
                    <button id="refresh-news" class="btn btn-outline">🔄 Refresh</button>
                </div>
                <div class="loading-indicator" id="news-loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading latest news...</p>
                </div>
                <div class="load-more-section">
                    <button id="load-more-news" class="btn btn-secondary">Load More News</button>
                </div>
            </div>

            <!-- Trending Topics -->
            <div class="trending-section">
                <h3>🔥 Trending Topics</h3>
                <div id="trending-topics" class="trending-topics"></div>
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
  const feeds = {
    'personalized': document.getElementById('personalized-feed'),
    'business': document.getElementById('business-feed'),
    'technology': document.getElementById('technology-feed'),
    'markets': document.getElementById('markets-feed'),
    'earnings': document.getElementById('earnings-feed')
  };

  const newsLoading = document.getElementById('news-loading');

  function renderArticles(container, items) {
    container.innerHTML = '';
    items.forEach(item => {
      const el = document.createElement('div');
      el.className = 'news-article';
      el.innerHTML = `
        <div class="article-header"><span class="article-category">${item.category}</span><span class="article-time">${item.time}</span></div>
        <h3 class="article-title">${item.title}</h3>
        <p class="article-summary">${item.summary}</p>
        <div class="article-footer"><span class="article-source">📰 ${item.source}</span><div class="article-symbols">${(item.symbols||[]).map(s=>`<span class='symbol-tag'>${s}</span>`).join('')}</div></div>
      `;
      container.appendChild(el);
    });
  }

  function mock(category) {
    const base = ['business','technology','markets','earnings'];
    const cat = category === 'personalized' ? base[Math.floor(Math.random()*base.length)] : category;
    const templates = [
      { title: 'Market Opens Higher on Optimism', summary: 'Stocks rally amid positive macro data and earnings beats.' },
      { title: 'Analysts Upgrade Major Tech Names', summary: 'Upgrades drive momentum in large-cap tech leaders.' },
      { title: 'Energy Stocks Gain on Supply Shift', summary: 'Commodity trends boost energy sector performance.' },
    ];
    const sources = ['Reuters','Bloomberg','MarketWatch','CNBC'];
    const symbols = ['AAPL','MSFT','NVDA','AMZN','TSLA','GOOGL'];
    return Array.from({length: 6}, (_, i) => {
      const t = templates[i % templates.length];
      return {
        category: cat,
        time: new Date(Date.now() - Math.random()*86400000).toLocaleString(),
        title: t.title,
        summary: t.summary,
        source: sources[Math.floor(Math.random()*sources.length)],
        symbols: symbols.slice(0, Math.floor(Math.random()*3)+1)
      };
    });
  }

  function loadFeed(key, clear=true) {
    if (!feeds[key]) return;
    newsLoading.style.display = 'block';
    setTimeout(()=>{
      renderArticles(feeds[key], mock(key));
      newsLoading.style.display = 'none';
    }, 700);
  }

  // Initial loads
  Object.keys(feeds).forEach(k=>loadFeed(k));

  document.getElementById('refresh-news').addEventListener('click', ()=>{
    const active = document.querySelector('#news-tabs .nav-link.active');
    const target = active?.getAttribute('data-bs-target')?.substring(1) || 'personalized';
    loadFeed(target, true);
  });

  document.querySelectorAll('#news-tabs .nav-link').forEach(btn=>{
    btn.addEventListener('shown.bs.tab', (e)=>{
      const target = e.target.getAttribute('data-bs-target').substring(1);
      loadFeed(target, false);
    });
  });
});
</script>

<?php get_footer(); ?>