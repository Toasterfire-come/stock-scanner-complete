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